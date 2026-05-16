#!/usr/bin/env python3
"""
Process-isolated lithium-plating external diagnostic Stage 1 runner.

Purpose:
    Run one stress condition in a standalone Python process and export
    post-stress state summaries plus model-internal plating-state audits.

Scope:
    Stage 1 only:
    initial_soc = 0.05
    -> charge to 4.2 V at stress rate
    -> CV hold to C/20
    -> rest 60 min
    -> discharge at C/3 to 2.5 V
    -> rest 60 min

This script does not run C/25 V(Q), GITT-like finite-rest voltage, ICA, or DVA.

Usage:
    python scripts/run_plating_external_stress_condition.py --condition no_plating_25C_1C
    python scripts/run_plating_external_stress_condition.py --condition plating_10C_2C
"""

from __future__ import annotations

import argparse
import gc
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd
import pybamm


# =============================================================================
# Paths
# =============================================================================

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data"
DOCS_TABLES = REPO / "docs" / "tables"

REGISTRY_PATH = DOCS_TABLES / "plating_external_diagnostic_condition_registry_v0_1.csv"

OUTDIR = DATA / "plating_external_stage1_stress"
OUTDIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Constants
# =============================================================================

INITIAL_SOC = 0.05
STRESS_PERIOD = "10 seconds"

DIRECT_PLATING_VARIABLES = [
    "Loss of capacity to negative lithium plating [A.h]",
    "Loss of lithium to negative lithium plating [mol]",
    "X-averaged negative lithium plating concentration [mol.m-3]",
    "X-averaged negative dead lithium concentration [mol.m-3]",
    "X-averaged negative lithium plating thickness [m]",
    "X-averaged negative dead lithium thickness [m]",
    "X-averaged negative electrode lithium plating interfacial current density [A.m-2]",
    "X-averaged negative electrode lithium plating reaction overpotential [V]",
    "Negative electrode lithium plating interfacial current density [A.m-2]",
    "Negative electrode lithium plating reaction overpotential [V]",
]


# =============================================================================
# Model, solver, and protocol
# =============================================================================

def build_model(plating_enabled: bool, temperature_C: float):
    """
    Build OKane2022 DFN with SEI background.

    For plating-enabled branches, partially reversible lithium plating is enabled.
    For control branches, lithium plating is disabled while keeping the same
    base chemistry and SEI background.
    """
    plating_mode = "partially reversible" if plating_enabled else "none"

    options = {
        "SEI": "solvent-diffusion limited",
        "SEI porosity change": "false",
        "lithium plating": plating_mode,
        "lithium plating porosity change": "false",
        "loss of active material": "none",
        "particle mechanics": "none",
        "thermal": "isothermal",
    }

    model = pybamm.lithium_ion.DFN(options=options)
    parameter_values = pybamm.ParameterValues("OKane2022")

    temperature_K = float(temperature_C) + 273.15
    parameter_values.update(
        {
            "Ambient temperature [K]": temperature_K,
            "Initial temperature [K]": temperature_K,
        },
        check_already_exists=False,
    )

    return model, parameter_values, plating_mode


def make_solver():
    return pybamm.CasadiSolver(
        mode="safe",
        atol=1e-6,
        rtol=1e-6,
        dt_max=600,
    )


def make_stage1_protocol(stress_charge_rate_C: float) -> list[str]:
    stress_rate = f"{float(stress_charge_rate_C):g}C"

    return [
        f"Charge at {stress_rate} until 4.2 V",
        "Hold at 4.2 V until C/20",
        "Rest for 60 minutes",
        "Discharge at C/3 until 2.5 V",
        "Rest for 60 minutes",
    ]


def run_stage1_solution(row: pd.Series):
    condition_id = row["condition_id"]
    plating_enabled = parse_bool(row["plating_enabled"])
    temperature_C = float(row["temperature_C"])
    stress_charge_rate_C = float(row["stress_charge_rate_C"])

    model, pv, plating_mode = build_model(
        plating_enabled=plating_enabled,
        temperature_C=temperature_C,
    )

    protocol = make_stage1_protocol(stress_charge_rate_C)
    experiment = pybamm.Experiment(protocol, period=STRESS_PERIOD)

    sim = pybamm.Simulation(
        model,
        parameter_values=pv,
        experiment=experiment,
        solver=make_solver(),
    )

    print(
        f"[RUN] {condition_id} | plating={plating_mode} | "
        f"T={temperature_C:g} °C | stress={stress_charge_rate_C:g}C"
    )

    t0 = time.perf_counter()
    sol = sim.solve(initial_soc=INITIAL_SOC)
    runtime_s = time.perf_counter() - t0

    print(f"[OK] solved: {condition_id} | runtime={runtime_s:.1f} s")

    metadata = {
        "condition_id": condition_id,
        "plating_enabled": plating_enabled,
        "plating_mode": plating_mode,
        "temperature_C": temperature_C,
        "stress_charge_rate_C": stress_charge_rate_C,
        "runtime_s": runtime_s,
        "initial_soc": INITIAL_SOC,
        "period": STRESS_PERIOD,
        "termination": str(getattr(sol, "termination", "")),
    }

    return sol, metadata


# =============================================================================
# Extraction helpers
# =============================================================================

def _as_float_array(values):
    arr = np.asarray(values, dtype=float)
    return arr


def _finite_flatten(arr):
    flat = np.asarray(arr, dtype=float).ravel()
    return flat[np.isfinite(flat)]


def _time_series_from_entries(entries):
    """
    Convert a PyBaMM variable entries array into a scalar time series.

    If entries are spatially resolved, average over all non-time axes.
    PyBaMM processed variables usually keep time as the last axis.
    """
    arr = _as_float_array(entries)

    if arr.ndim == 0:
        return np.array([float(arr)])

    if arr.ndim == 1:
        return arr

    reshaped = arr.reshape(-1, arr.shape[-1])
    return np.nanmean(reshaped, axis=0)


def trapezoid_integral(y, x):
    if hasattr(np, "trapezoid"):
        return np.trapezoid(y, x)
    return np.trapz(y, x)


def summarize_current_segments(sol, condition_id: str, eps: float = 1e-5) -> pd.DataFrame:
    """
    Segment the applied current trajectory.

    PyBaMM convention:
        +I = discharge
        -I = charge
    """
    t = _as_float_array(sol["Time [s]"].entries)
    u = _as_float_array(sol["Terminal voltage [V]"].entries)
    i = _as_float_array(sol["Current [A]"].entries)

    state = np.where(i > eps, "discharge", np.where(i < -eps, "charge", "rest"))
    change_idx = np.r_[0, np.flatnonzero(state[1:] != state[:-1]) + 1, len(state)]

    rows = []

    for k in range(len(change_idx) - 1):
        a, b = int(change_idx[k]), int(change_idx[k + 1])
        if b - a < 2:
            continue

        rows.append({
            "condition_id": condition_id,
            "segment_id": int(k),
            "segment_type": str(state[a]),
            "idx_start": a,
            "idx_stop": b,
            "t_start_s": float(t[a]),
            "t_end_s": float(t[b - 1]),
            "duration_s": float(t[b - 1] - t[a]),
            "duration_min": float((t[b - 1] - t[a]) / 60.0),
            "U_start_V": float(u[a]),
            "U_end_V": float(u[b - 1]),
            "I_mean_A": float(np.mean(i[a:b])),
            "I_min_A": float(np.min(i[a:b])),
            "I_max_A": float(np.max(i[a:b])),
            "n_points": int(b - a),
        })

    return pd.DataFrame(rows)


def summarize_stress_state(sol, metadata: dict, segment_df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize the full Stage 1 stress trajectory.

    Capacity convention:
        charge_Ah    = integral of -I over charge segments
        discharge_Ah = integral of +I over discharge segments
        throughput_Ah = charge_Ah + discharge_Ah
        net_charge_Ah = charge_Ah - discharge_Ah
    """
    condition_id = metadata["condition_id"]

    t = _as_float_array(sol["Time [s]"].entries)
    u = _as_float_array(sol["Terminal voltage [V]"].entries)
    i = _as_float_array(sol["Current [A]"].entries)

    t_h = t / 3600.0

    charge_current = np.where(i < 0, -i, 0.0)
    discharge_current = np.where(i > 0, i, 0.0)

    charge_Ah = float(trapezoid_integral(charge_current, t_h))
    discharge_Ah = float(trapezoid_integral(discharge_current, t_h))
    throughput_Ah = charge_Ah + discharge_Ah
    net_charge_Ah = charge_Ah - discharge_Ah

    n_charge_segments = int((segment_df["segment_type"] == "charge").sum()) if not segment_df.empty else 0
    n_discharge_segments = int((segment_df["segment_type"] == "discharge").sum()) if not segment_df.empty else 0
    n_rest_segments = int((segment_df["segment_type"] == "rest").sum()) if not segment_df.empty else 0

    row = {
        **metadata,
        "t_start_s": float(t[0]),
        "t_end_s": float(t[-1]),
        "duration_s": float(t[-1] - t[0]),
        "duration_min": float((t[-1] - t[0]) / 60.0),
        "U_start_V": float(u[0]),
        "U_end_V": float(u[-1]),
        "I_start_A": float(i[0]),
        "I_end_A": float(i[-1]),
        "U_min_V": float(np.min(u)),
        "U_max_V": float(np.max(u)),
        "I_min_A": float(np.min(i)),
        "I_max_A": float(np.max(i)),
        "charge_Ah": charge_Ah,
        "discharge_Ah": discharge_Ah,
        "throughput_Ah": throughput_Ah,
        "net_charge_Ah": net_charge_Ah,
        "n_charge_segments": n_charge_segments,
        "n_discharge_segments": n_discharge_segments,
        "n_rest_segments": n_rest_segments,
        "n_time_points": int(len(t)),
        "summary_status": "completed",
    }

    return pd.DataFrame([row])


def extract_direct_plating_audit(sol, metadata: dict) -> pd.DataFrame:
    """
    Extract model-internal plating-state variables if available.

    Missing variables are recorded as available=False rather than raising.
    This keeps no-plating control branches auditable.
    """
    rows = []
    condition_id = metadata["condition_id"]

    for var_name in DIRECT_PLATING_VARIABLES:
        row = {
            "condition_id": condition_id,
            "plating_enabled": metadata["plating_enabled"],
            "plating_mode": metadata["plating_mode"],
            "temperature_C": metadata["temperature_C"],
            "stress_charge_rate_C": metadata["stress_charge_rate_C"],
            "variable_name": var_name,
            "available": False,
            "initial_value": np.nan,
            "final_value": np.nan,
            "min_value": np.nan,
            "max_value": np.nan,
            "max_abs_value": np.nan,
            "unit_hint": "",
            "status": "missing_variable",
            "notes": "",
        }

        try:
            entries = sol[var_name].entries
            arr = _as_float_array(entries)
            flat = _finite_flatten(arr)

            if flat.size == 0:
                row["available"] = True
                row["status"] = "available_no_finite_values"
                row["notes"] = "Variable exists but contains no finite values."
            else:
                ts = _time_series_from_entries(arr)
                ts_finite = ts[np.isfinite(ts)]

                row["available"] = True
                row["initial_value"] = float(ts_finite[0]) if ts_finite.size else np.nan
                row["final_value"] = float(ts_finite[-1]) if ts_finite.size else np.nan
                row["min_value"] = float(np.nanmin(flat))
                row["max_value"] = float(np.nanmax(flat))
                row["max_abs_value"] = float(np.nanmax(np.abs(flat)))
                row["status"] = "available"

        except KeyError:
            row["notes"] = "Variable not present in this model / option set."
        except Exception as exc:
            row["status"] = "extraction_error"
            row["notes"] = repr(exc)

        rows.append(row)

    audit_df = pd.DataFrame(rows)

    # Simple condition-level signal summary for downstream checks.
    if audit_df["available"].any():
        max_abs_available = audit_df.loc[audit_df["available"], "max_abs_value"]
        if max_abs_available.notna().any() and float(max_abs_available.max()) > 0:
            condition_signal_status = "nonzero_internal_plating_variable_detected"
        else:
            condition_signal_status = "available_but_zero_or_near_zero"
    else:
        condition_signal_status = "no_direct_plating_variables_available"

    audit_df["condition_signal_status"] = condition_signal_status

    return audit_df


# =============================================================================
# IO and main
# =============================================================================

def parse_bool(value) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)) and not pd.isna(value):
        return bool(int(value))

    text = str(value).strip().lower()

    if text in {"true", "1", "yes", "y"}:
        return True

    if text in {"false", "0", "no", "n"}:
        return False

    raise ValueError(f"Cannot parse boolean value: {value!r}")


def load_condition_registry() -> pd.DataFrame:
    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(f"Missing registry: {REGISTRY_PATH}")

    registry = pd.read_csv(REGISTRY_PATH)

    required = {
        "condition_id",
        "plating_enabled",
        "temperature_C",
        "stress_charge_rate_C",
        "control_condition_id",
        "matched_pair_id",
    }

    missing = required - set(registry.columns)

    if missing:
        raise ValueError(f"Condition registry missing required columns: {missing}")

    return registry


def select_condition(registry: pd.DataFrame, condition_id: str) -> pd.Series:
    match = registry[registry["condition_id"] == condition_id]

    if match.empty:
        available = registry["condition_id"].tolist()
        raise ValueError(
            f"Condition {condition_id!r} not found. Available conditions: {available}"
        )

    return match.iloc[0]


def save_condition_outputs(condition_id: str, sol, metadata: dict):
    segment_df = summarize_current_segments(sol, condition_id)
    stress_summary_df = summarize_stress_state(sol, metadata, segment_df)
    direct_audit_df = extract_direct_plating_audit(sol, metadata)

    segment_path = OUTDIR / f"{condition_id}_segment_audit.csv"
    stress_summary_path = OUTDIR / f"{condition_id}_stress_state_summary.csv"
    direct_audit_path = OUTDIR / f"{condition_id}_direct_plating_audit.csv"

    segment_df.to_csv(segment_path, index=False)
    stress_summary_df.to_csv(stress_summary_path, index=False)
    direct_audit_df.to_csv(direct_audit_path, index=False)

    print(f"[OK] saved segment audit: {segment_path}")
    print(f"[OK] saved stress-state summary: {stress_summary_path}")
    print(f"[OK] saved direct plating audit: {direct_audit_path}")

    return {
        "segment_path": segment_path,
        "stress_summary_path": stress_summary_path,
        "direct_audit_path": direct_audit_path,
    }


def save_error(condition_id: str, exc: BaseException):
    error_path = OUTDIR / f"{condition_id}_error.csv"

    error_df = pd.DataFrame([
        {
            "condition_id": condition_id,
            "status": "execution_error",
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
            "failure_classification": "execution_boundary_not_scientific_negative",
        }
    ])

    error_df.to_csv(error_path, index=False)

    print(f"[ERROR] saved execution-boundary record: {error_path}")
    return error_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", required=False, help="Condition ID to run.")
    parser.add_argument("--list", action="store_true", help="List available conditions and exit.")
    parser.add_argument("--dry-run", action="store_true", help="Validate condition selection without running PyBaMM.")
    args = parser.parse_args()

    registry = load_condition_registry()

    if args.list:
        print("[AVAILABLE CONDITIONS]")
        for condition_id in registry["condition_id"].tolist():
            print(condition_id)
        return

    if not args.condition:
        raise ValueError("Please pass --condition or use --list.")

    row = select_condition(registry, args.condition)

    print("[CONDITION]")
    print(row.to_string())

    if args.dry_run:
        print("[OK] dry-run completed. No PyBaMM simulation executed.")
        return

    try:
        sol, metadata = run_stage1_solution(row)
        save_condition_outputs(args.condition, sol, metadata)

        del sol
        gc.collect()

        print("[DONE] Stage 1 stress condition completed.")

    except Exception as exc:
        save_error(args.condition, exc)
        raise


if __name__ == "__main__":
    main()
