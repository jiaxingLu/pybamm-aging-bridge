#!/usr/bin/env python3
"""
Process-isolated plating HPPC condition runner.

Purpose:
    Run one plating/no-plating HPPC condition in a standalone Python process,
    then write descriptor CSV files and exit. This avoids keeping large PyBaMM
    Solution objects inside Jupyter memory.

Usage:
    python scripts/run_plating_hppc_condition.py --condition no_plating_25C_1C
    python scripts/run_plating_hppc_condition.py --condition plating_10C_2C
"""

from __future__ import annotations

import argparse
import gc
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pybamm


# =============================================================================
# Paths
# =============================================================================

REPO = Path("/Users/louislu/projects/pybamm-aging-bridge")
DATA = REPO / "data"
OUTDIR = DATA / "plating_hppc_process_isolated"
OUTDIR.mkdir(parents=True, exist_ok=True)

CONTRACT_PATH = DATA / "plating_full_branch_contract.csv"


# =============================================================================
# Protocol constants
# =============================================================================

STRESS_PERIOD = "10 seconds"

HPPC_PRE_REST_STEPS = [
    "Discharge at C/3 for 90 minutes",
    "Rest for 60 minutes",
]
HPPC_PRE_REST_PERIOD = "10 seconds"

# Important:
# Add 2 s rest before the pulse so that the pulse-only solution has
# a local pre-pulse voltage reference U_C.
HPPC_PULSE_RELAX_STEPS = [
    "Rest for 2 seconds",
    "Discharge at 1C for 10 seconds",
    "Rest for 600 seconds",
]
HPPC_PULSE_RELAX_PERIOD = "0.1 seconds"

HPPC_PULSE_CURRENT_LO_A = 4.5
HPPC_PULSE_CURRENT_HI_A = 5.5
HPPC_PULSE_DURATION_LO_S = 8.0
HPPC_PULSE_DURATION_HI_S = 12.5

RI_TIME_WINDOWS_S = [0.05, 0.1, 1.0, 10.0]
RECOVERY_RI_WINDOWS_S = [0.1, 1.0]
RELAX_START_DELAY_S = 0.1


# =============================================================================
# Model and solver
# =============================================================================

def build_plating_model(plating_mode: str = "partially reversible", temperature_C: float = 25.0):
    """
    Build OKane2022 DFN with SEI-background lithium plating.

    Important:
    OKane2022 partially reversible plating depends on SEI thickness, so SEI
    must be enabled. SEI = none can cause division-by-zero in dead-lithium decay.
    """
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

    temperature_K = temperature_C + 273.15
    parameter_values.update(
        {
            "Ambient temperature [K]": temperature_K,
            "Initial temperature [K]": temperature_K,
        },
        check_already_exists=False,
    )

    return model, parameter_values


def make_solver():
    return pybamm.CasadiSolver(
        mode="safe",
        atol=1e-6,
        rtol=1e-6,
        dt_max=600,
    )


def make_plating_stress_state_protocol(stress_charge_rate: str = "1C"):
    return [
        f"Charge at {stress_charge_rate} until 4.2 V",
        "Hold at 4.2 V until C/20",
        "Rest for 60 minutes",
    ]


def run_experiment(row: pd.Series, steps: list[str], period: str, starting_solution=None):
    condition = row["condition"]
    plating_mode = row["plating_mode"]
    temperature_C = float(row["temperature_C"])
    initial_soc = float(row["initial_soc"])

    model, pv = build_plating_model(
        plating_mode=plating_mode,
        temperature_C=temperature_C,
    )

    experiment = pybamm.Experiment(steps, period=period)

    sim = pybamm.Simulation(
        model,
        parameter_values=pv,
        experiment=experiment,
        solver=make_solver(),
    )

    kwargs = {}
    if starting_solution is not None:
        kwargs["starting_solution"] = starting_solution
    else:
        kwargs["initial_soc"] = initial_soc

    print(
        f"[RUN] {condition} | plating={plating_mode} | "
        f"T={temperature_C} °C | period={period}"
    )

    t0 = time.perf_counter()
    sol = sim.solve(**kwargs)
    elapsed = time.perf_counter() - t0

    print(f"[OK] solved: {condition} | runtime={elapsed:.1f} s")
    return sol


def compact_last_state(sol):
    """
    Return only the final state of a PyBaMM Solution.

    This avoids passing full solution history through starting_solution, which
    can be unstable and memory-heavy for DFN + plating workflows.
    """
    if hasattr(sol, "last_state"):
        return sol.last_state
    raise RuntimeError("PyBaMM Solution has no last_state attribute.")


# =============================================================================
# Descriptor helpers
# =============================================================================

def trapezoid_integral(y, x):
    if hasattr(np, "trapezoid"):
        return np.trapezoid(y, x)
    return np.trapz(y, x)


def value_at_time(t, y, target_t):
    idx = int(np.argmin(np.abs(t - target_t)))
    return float(y[idx]), float(t[idx])


def summarize_current_segments(sol, condition: str, eps: float = 1e-5):
    """
    PyBaMM convention:
        +I = discharge
        -I = charge
    """
    t = np.asarray(sol["Time [s]"].entries, dtype=float)
    u = np.asarray(sol["Terminal voltage [V]"].entries, dtype=float)
    i = np.asarray(sol["Current [A]"].entries, dtype=float)

    state = np.where(i > eps, "discharge", np.where(i < -eps, "charge", "rest"))
    change_idx = np.r_[0, np.flatnonzero(state[1:] != state[:-1]) + 1, len(state)]

    rows = []

    for k in range(len(change_idx) - 1):
        a, b = change_idx[k], change_idx[k + 1]
        if b - a < 2:
            continue

        rows.append({
            "condition": condition,
            "segment_id": int(k),
            "segment_type": state[a],
            "idx_start": int(a),
            "idx_stop": int(b),
            "t_start_s": float(t[a]),
            "t_end_s": float(t[b - 1]),
            "duration_s": float(t[b - 1] - t[a]),
            "duration_min": float((t[b - 1] - t[a]) / 60),
            "U_start_V": float(u[a]),
            "U_end_V": float(u[b - 1]),
            "I_mean_A": float(np.mean(i[a:b])),
            "I_min_A": float(np.min(i[a:b])),
            "I_max_A": float(np.max(i[a:b])),
            "n_points": int(b - a),
        })

    return pd.DataFrame(rows)


def extract_hppc_descriptors(sol, row: pd.Series):
    condition = row["condition"]

    seg = summarize_current_segments(sol, condition)
    seg_path = OUTDIR / f"{condition}_segment_audit.csv"
    seg.to_csv(seg_path, index=False)
    print(f"[OK] saved: {seg_path}")

    pulse_candidates = seg[
        (seg["segment_type"] == "discharge")
        & (seg["I_mean_A"].between(HPPC_PULSE_CURRENT_LO_A, HPPC_PULSE_CURRENT_HI_A))
        & (seg["duration_s"].between(HPPC_PULSE_DURATION_LO_S, HPPC_PULSE_DURATION_HI_S))
    ].sort_values("t_start_s")

    if pulse_candidates.empty:
        print("[DEBUG] Segment audit:")
        print(seg)
        raise RuntimeError(f"No valid 1C 10 s HPPC pulse found for {condition}")

    pulse = pulse_candidates.iloc[-1]

    t = np.asarray(sol["Time [s]"].entries, dtype=float)
    u = np.asarray(sol["Terminal voltage [V]"].entries, dtype=float)
    i = np.asarray(sol["Current [A]"].entries, dtype=float)

    t_on = float(pulse["t_start_s"])
    t_off = float(pulse["t_end_s"])

    # Pre-pulse reference comes from the 2 s rest added before the pulse.
    U_C, t_C = value_at_time(t, u, t_on - 0.6)
    I_C, _ = value_at_time(t, i, t_on - 0.6)

    pulse_mask = (t >= t_on + 0.2) & (t <= t_off - 0.2)
    I_pulse = float(np.mean(i[pulse_mask]))
    deltaI_on = I_pulse - I_C

    out = {
        "pair": row["pair"],
        "condition": condition,
        "plating_mode": row["plating_mode"],
        "temperature_C": float(row["temperature_C"]),
        "stress_charge_rate": row["stress_charge_rate"],
        "role": row["role"],
        "t_on_s": t_on,
        "t_off_s": t_off,
        "U_C_V": U_C,
        "I_C_A": I_C,
        "I_pulse_A": I_pulse,
        "deltaI_on_A": deltaI_on,
    }

    # -------------------------------------------------------------------------
    # Pulse-on Ri(t)
    # -------------------------------------------------------------------------
    for w in RI_TIME_WINDOWS_S:
        target = t_on + min(w, t_off - t_on - 0.02)
        U_w, t_w = value_at_time(t, u, target)

        Ri_ohm = (U_C - U_w) / deltaI_on

        out[f"Ri_{w:g}s_mOhm"] = Ri_ohm * 1000
        out[f"U_at_{w:g}s_V"] = U_w
        out[f"t_at_{w:g}s_s"] = t_w

    # -------------------------------------------------------------------------
    # Recovery-side Ri
    # -------------------------------------------------------------------------
    U_E, _ = value_at_time(t, u, t_off - 0.02)
    I_E, _ = value_at_time(t, i, t_off - 0.02)

    out["U_E_V"] = U_E
    out["I_E_A"] = I_E

    for w in RECOVERY_RI_WINDOWS_S:
        U_rec, t_rec = value_at_time(t, u, t_off + w)
        I_rec, _ = value_at_time(t, i, t_off + w)

        deltaI_off = I_E - I_rec
        Ri_rec_ohm = (U_rec - U_E) / deltaI_off if abs(deltaI_off) > 1e-12 else np.nan

        out[f"Ri_recovery_{w:g}s_mOhm"] = Ri_rec_ohm * 1000
        out[f"U_recovery_{w:g}s_V"] = U_rec
        out[f"t_recovery_{w:g}s_s"] = t_rec

    # -------------------------------------------------------------------------
    # Raw relaxation descriptors
    # -------------------------------------------------------------------------
    rest_mask = (t >= t_off) & (t <= t_off + 600)
    t_rest = t[rest_mask] - t_off
    u_rest = u[rest_mask]

    U_off = float(u_rest[0])
    tail_mask = t_rest >= (t_rest.max() - 60)
    U_inf = float(np.mean(u_rest[tail_mask]))

    recovery_amp = U_inf - U_off

    out["U_off_V"] = U_off
    out["U_inf_600s_V"] = U_inf
    out["recovery_amplitude_mV"] = recovery_amp * 1000

    if recovery_amp > 1e-9:
        frac = (u_rest - U_off) / recovery_amp

        def first_time_to_fraction(frac_target):
            idxs = np.flatnonzero(frac >= frac_target)
            return float(t_rest[idxs[0]]) if len(idxs) else np.nan

        out["tau_FG_eff_s"] = first_time_to_fraction(1 - np.exp(-1))
        out["t95_s"] = first_time_to_fraction(0.95)
        out["t99_s"] = first_time_to_fraction(0.99)
        out["recovery_area_mV_s"] = float(
            trapezoid_integral((u_rest - U_off) * 1000, t_rest)
        )

        residual = U_inf - u_rest
        fit_mask = (
            (frac >= 0.50)
            & (frac <= 0.95)
            & (residual > 1e-8)
        )

        if fit_mask.sum() >= 5:
            x = t_rest[fit_mask]
            y = np.log(residual[fit_mask])
            slope, _ = np.polyfit(x, y, 1)
            out["tau_tail_s"] = float(-1 / slope) if slope < 0 else np.nan
        else:
            out["tau_tail_s"] = np.nan
    else:
        out["tau_FG_eff_s"] = np.nan
        out["t95_s"] = np.nan
        out["t99_s"] = np.nan
        out["recovery_area_mV_s"] = np.nan
        out["tau_tail_s"] = np.nan

    # -------------------------------------------------------------------------
    # Corrected post-ohmic relaxation descriptors
    # -------------------------------------------------------------------------
    t_start_corr = t_off + RELAX_START_DELAY_S
    rest_mask_corr = (t >= t_start_corr) & (t <= t_off + 600)
    t_corr = t[rest_mask_corr] - t_start_corr
    u_corr = u[rest_mask_corr]

    U_start_corr = float(u_corr[0])
    tail_mask_corr = t_corr >= (t_corr.max() - 60)
    U_inf_corr = float(np.mean(u_corr[tail_mask_corr]))

    amp_corr = U_inf_corr - U_start_corr

    out["post_ohmic_U_start_V"] = U_start_corr
    out["post_ohmic_U_inf_600s_V"] = U_inf_corr
    out["post_ohmic_recovery_amplitude_mV"] = amp_corr * 1000

    if amp_corr > 1e-9:
        frac_corr = (u_corr - U_start_corr) / amp_corr

        def first_time_to_fraction_corr(frac_target):
            idxs = np.flatnonzero(frac_corr >= frac_target)
            return float(t_corr[idxs[0]]) if len(idxs) else np.nan

        out["post_ohmic_tau_FG_eff_s"] = first_time_to_fraction_corr(1 - np.exp(-1))
        out["post_ohmic_t95_s"] = first_time_to_fraction_corr(0.95)
        out["post_ohmic_t99_s"] = first_time_to_fraction_corr(0.99)
        out["post_ohmic_recovery_area_mV_s"] = float(
            trapezoid_integral((u_corr - U_start_corr) * 1000, t_corr)
        )

        residual_corr = U_inf_corr - u_corr
        fit_mask_corr = (
            (frac_corr >= 0.50)
            & (frac_corr <= 0.95)
            & (residual_corr > 1e-8)
        )

        if fit_mask_corr.sum() >= 5:
            x = t_corr[fit_mask_corr]
            y = np.log(residual_corr[fit_mask_corr])
            slope, _ = np.polyfit(x, y, 1)
            out["post_ohmic_tau_tail_s"] = float(-1 / slope) if slope < 0 else np.nan
        else:
            out["post_ohmic_tau_tail_s"] = np.nan
    else:
        out["post_ohmic_tau_FG_eff_s"] = np.nan
        out["post_ohmic_t95_s"] = np.nan
        out["post_ohmic_t99_s"] = np.nan
        out["post_ohmic_recovery_area_mV_s"] = np.nan
        out["post_ohmic_tau_tail_s"] = np.nan

    return out


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", required=True)
    args = parser.parse_args()

    if not CONTRACT_PATH.exists():
        raise FileNotFoundError(f"Missing contract: {CONTRACT_PATH}")

    contract = pd.read_csv(CONTRACT_PATH)

    match = contract[contract["condition"] == args.condition]

    if match.empty:
        raise ValueError(
            f"Condition {args.condition!r} not found. "
            f"Available: {contract['condition'].tolist()}"
        )

    row = match.iloc[0]

    # 1) stress-state protocol
    stress_steps = make_plating_stress_state_protocol(row["stress_charge_rate"])

    post_stress = run_experiment(
        row=row,
        steps=stress_steps,
        period=STRESS_PERIOD,
        starting_solution=None,
    )

    post_stress_last = compact_last_state(post_stress)
    del post_stress
    gc.collect()

    # 2) coarse pre-HPPC discharge + rest
    pre_hppc = run_experiment(
        row=row,
        steps=HPPC_PRE_REST_STEPS,
        period=HPPC_PRE_REST_PERIOD,
        starting_solution=post_stress_last,
    )

    pre_hppc_last = compact_last_state(pre_hppc)
    del pre_hppc, post_stress_last
    gc.collect()

    # 3) dense pulse + relaxation
    hppc_sol = run_experiment(
        row=row,
        steps=HPPC_PULSE_RELAX_STEPS,
        period=HPPC_PULSE_RELAX_PERIOD,
        starting_solution=pre_hppc_last,
    )

    del pre_hppc_last
    gc.collect()

    descriptor = extract_hppc_descriptors(hppc_sol, row=row)

    descriptor_df = pd.DataFrame([descriptor])
    descriptor_path = OUTDIR / f"{args.condition}_hppc_descriptor.csv"
    descriptor_df.to_csv(descriptor_path, index=False)

    print(f"[OK] saved: {descriptor_path}")

    del hppc_sol
    gc.collect()

    print("[DONE]")


if __name__ == "__main__":
    main()
