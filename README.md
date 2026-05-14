# PyBaMM Aging Bridge

PyBaMM Aging Bridge is a mechanism-to-observable modeling project for lithium-ion battery aging diagnostics.

The project investigates how DFN-level electrochemical perturbations manifest as ECM-level diagnostic observables, including:

- short-window internal resistance `Ri`
- CDEFG-style HPPC voltage points
- relaxation time descriptors `tau1 / tau2`
- voltage recovery morphology
- contact overpotential
- SOC-dependent diagnostic fingerprints

The core objective is to establish a traceable bridge:

    DFN-level physical perturbation
    -> simulated HPPC response
    -> CDEFG / Ri / relaxation extraction
    -> ECM-level observable fingerprint
    -> aging diagnostic interpretation

---

## Motivation

Battery aging is not directly observable in practical systems. In most engineering workflows, degradation has to be inferred from measurable signals such as voltage response, pulse resistance, relaxation behavior, capacity, or energy efficiency.

A key risk is that different physical mechanisms can produce superficially similar observables. For example, an increase in short-window resistance may originate from charge-transfer degradation, contact resistance growth, temperature effects, or other coupled mechanisms.

This project therefore asks:

    Which electrochemical perturbation produces which observable diagnostic fingerprint?

The project does not start from an assumed SOH value. Instead, it perturbs interpretable DFN-level physical pathways and audits how they appear in observable HPPC-derived descriptors.

---

## Methodological Principle

This repository follows an audit-first modeling workflow.

Each notebook defines:

- its objective
- its workflow
- its expected outputs
- its interpretation boundary
- a final closure summarizing what was and was not established

The central rule is:

    Parameter perturbation is not itself a conclusion.
    Only observable drift under a controlled extraction protocol can support an interpretation.

---

## Model and Protocol

Current baseline:

- Model: PyBaMM DFN
- Parameter set: Chen2020
- Thermal setting: default isothermal
- Default temperature: 25 °C
- HPPC pulse: 1C discharge pulse for 10 s
- Relaxation: 600 s
- Main SOC points: 10%, 30%, 50%, 70%, 90%

PyBaMM current convention is explicitly tracked:

    PyBaMM convention:
    +I = discharge
    -I = charge

---

## Observable Extraction

The project uses a CDEFG-style HPPC extraction workflow.

For each pulse:

| Point | Meaning |
|---|---|
| C | pre-pulse baseline voltage |
| D | short-time voltage response after pulse start |
| E | end-of-pulse voltage |
| F | short-time recovery after current interruption |
| G | long-time recovered voltage |

Extracted observables include:

- `Ri_CD`
- `Ri_EF`
- `tau1 / tau2` from biexponential relaxation fitting
- 60 s and 300 s fitting-window tau descriptors
- relaxation residuals
- contact overpotential
- normalized remaining polarization

Important methodological note:

    tau1 / tau2 are observation-window-dependent descriptors,
    not unique physical constants.

---

## Perturbation Families

The current project focuses on four controlled perturbation families.

| Family | DFN-level perturbation | Intended physical meaning |
|---|---|---|
| `Ds_p` | positive particle diffusivity decrease | positive solid diffusion limitation |
| `j0_n` | negative exchange-current density decrease | negative-electrode charge-transfer degradation |
| `j0_p` | positive exchange-current density decrease | positive-electrode kinetic degradation |
| `contact_R` | contact resistance increase | pure ohmic / external contact resistance |

---

## Key Results

### 1. Corrected Tier-0 Fingerprints

After enabling the PyBaMM model option:

    {"contact resistance": "true"}

the corrected Tier-0 scan showed distinct fingerprints:

| Perturbation | Main response | Interpretation |
|---|---|---|
| `Ds_p ×0.5` | `tau2` increases, `Ri` nearly unchanged | diffusion-sensitive relaxation fingerprint |
| `j0_n ×0.5` | `Ri` increases strongly, `tau2` nearly unchanged | negative-electrode kinetic fingerprint |
| `j0_p ×0.5` | `Ri` increases moderately, `tau2` nearly unchanged | positive-electrode kinetic fingerprint |
| `contact_R = 5 mΩ` | `Ri` increases by exactly 5 mΩ, tau unchanged | pure ohmic/contact fingerprint |

---

### 2. Perturbation-Level Scan at SOC = 50%

At SOC = 50%, perturbation strength mapped monotonically into observable drift.

Key findings:

- decreasing `D_s,p` monotonically increased `tau2`
- decreasing `j0,n` monotonically increased `Ri`
- decreasing `j0,p` also increased `Ri`, but more weakly than `j0,n`
- increasing contact resistance produced a strictly linear ohmic response

This established that the selected fingerprints are not isolated one-point artifacts.

---

## Representative Figures

### Corrected Tier-0 mechanism fingerprint summary

This figure summarizes how different DFN-level perturbations project into ECM-level observables.

![Corrected Tier-0 mechanism fingerprint summary](docs/figures/corrected_tier0_mechanism_fingerprint_summary.png)

---

### SOC-resolved Ri-sensitive fingerprints

This figure shows how Ri-sensitive perturbations behave across SOC. The contact-resistance fingerprint remains SOC-invariant, while exchange-current perturbations remain sign-stable with mechanism-specific magnitude.

![SOC-resolved Ri-sensitive fingerprints](docs/figures/multi_soc_Ri_sensitive_fingerprints.png)

---

### SOC-resolved diffusion-sensitive tau2 fingerprint

This figure shows that positive solid diffusivity reduction produces a tau2 increase across all SOC points, but the magnitude is state-dependent.

![SOC-resolved diffusion-sensitive tau2 fingerprint](docs/figures/multi_soc_Ds_p_tau2_fingerprint.png)


---

### 3. Temperature Entry Audit

The Chen2020 parameter set uses:

    Reference temperature = 298.15 K
    Ambient temperature   = 298.15 K
    Initial temperature   = 298.15 K

The default model is:

    thermal = isothermal
    surface temperature = ambient

Temperature-sensitive callable parameters include:

- negative electrode exchange-current density
- positive electrode exchange-current density
- electrolyte diffusivity
- electrolyte conductivity

A small 10 / 25 / 45 °C audit showed:

- `Ri` changes strongly with temperature
- `tau2` descriptors remain nearly unchanged under the current configuration

This means temperature must be treated as an independent operating-condition layer in future work.

---

### 3b. Temperature-Representative Fingerprint Check

A representative scan at SOC = 50% tested whether mechanism fingerprints remain identifiable across:

- 10 °C
- 25 °C
- 45 °C

Main findings:

- `Ds_p ×0.5` remains identifiable through `tau2` increase across all tested temperatures.
- `j0_n ×0.5` remains identifiable through Ri increase with mild magnitude variation.
- `j0_p ×0.5` remains identifiable but weakens at higher temperature.
- `contact_R = 5 mΩ` remains temperature-invariant, producing exactly +5 mΩ Ri shift and 25 mV contact overpotential.

![Temperature-resolved Ri-sensitive fingerprints](docs/figures/temperature_resolved_Ri_sensitive_fingerprints.png)

![Temperature-resolved diffusion-sensitive tau2 fingerprint](docs/figures/temperature_resolved_Ds_p_tau2_fingerprint.png)


---

### 4. Multi-SOC Fingerprint Stability

A multi-SOC scan across 10%, 30%, 50%, 70%, and 90% SOC showed that fingerprint stability has two levels:

    sign stability:
    whether the observable changes in the same direction across SOC

    magnitude stability:
    whether the size of the change remains similar across SOC

Summary:

| Fingerprint family | SOC behavior |
|---|---|
| baseline | Ri and tau2 are SOC-dependent |
| `Ds_p ×0.5` | sign-stable, magnitude state-dependent |
| `j0_n ×0.5` | sign-stable, magnitude relatively stable |
| `j0_p ×0.5` | sign-stable, weaker but stable |
| `contact_R = 5 mΩ` | SOC-invariant |

This supports the interpretation that mechanism fingerprints are not simply present or absent. Their direction and magnitude must be evaluated separately.

---

## Interpretation Rules

Current diagnostic interpretation rules:

| Observable pattern | Supported interpretation |
|---|---|
| `Ri ↑`, `tau2 ≈ constant` | kinetic / charge-transfer or ohmic pathway |
| `tau2 ↑`, `Ri ≈ constant` | diffusion-sensitive relaxation limitation |
| constant `Ri` offset across SOC with `I·R` consistency | contact resistance pathway |
| baseline `Ri` or `tau` changes with SOC | same-SOC baseline comparison is mandatory |
| `Ri` changes strongly with temperature | temperature effect must be separated from degradation mechanisms |

---


## SEI-only Metric Registry v0.1

Notebook 15 extends the SEI-only aging fingerprint analysis into a broader diagnostic metric registry.

The goal is to move beyond a narrow `Ri / tau1 / tau2` audit and classify SEI-only aging using multiple observable layers.

### Implemented metric layers

| Layer | Status | Main metrics |
|---|---|---|
| degradation state | active | SEI thickness, LLI, lithium lost, side-reaction capacity loss |
| external capacity RPT | active | RPT discharge capacity, capacity retention, capacity fade |
| multi-window resistance | active | Ri_0.1s, Ri_1s, Ri_10s, recovery Ri |
| fitted relaxation | active | tau1_60s, tau1_300s, tau2_60s, tau2_300s |
| non-parametric relaxation | active | tau_FG_eff, t95, t99, tau_tail, recovery area |
| voltage recovery / pseudo-OCV | feasibility | finite-rest Uinf and recovery amplitude |
| OCV / ICA / DVA | deferred | requires low-rate or quasi-equilibrium voltage curve |
| thermal | deferred | requires non-isothermal model branch |

### Main SEI-only classification

Using Metric Registry v0.1, the SEI-only fingerprint is classified as:

    capacity / LLI dominant mixed signature

The dominant layer is the capacity / LLI degradation-state layer.

The secondary layer is a weak but monotonic multi-window Ri component.

The fitted and non-parametric relaxation descriptors are useful audit layers, but they do not form the dominant SEI-only fingerprint under the present proof-of-concept protocol.

### Representative SEI Metric Registry figures

External capacity RPT:

![SEI Metric Registry capacity RPT drift](docs/figures/sei_metric_registry_capacity_rpt_drift.png)

Capacity retention:

![SEI Metric Registry capacity retention](docs/figures/sei_metric_registry_capacity_retention.png)

LLI and side-reaction capacity loss:

![SEI Metric Registry LLI and capacity loss](docs/figures/sei_metric_registry_LLI_capacity_loss.png)

Multi-window resistance drift:

![SEI Metric Registry multi-window Ri drift](docs/figures/sei_metric_registry_multi_window_Ri_drift.png)

Fitted tau descriptor drift:

![SEI Metric Registry fitted tau drift](docs/figures/sei_metric_registry_fitted_tau_drift.png)

Non-parametric relaxation descriptor drift:

![SEI Metric Registry non-parametric relaxation drift](docs/figures/sei_metric_registry_nonparam_relaxation_drift.png)

### Methodological boundary

The capacity RPT and HPPC/RPT branches are diagnostic only.

They are not used as starting points for subsequent aging.

The RPT conditioning is nominal-capacity based and approximate.

Voltage-recovery metrics are finite-rest recovery descriptors, not strict OCV-SOC measurements.

Thermal metrics remain deferred under the current isothermal model configuration.


## Notebook Index

| Notebook | Purpose |
|---|---|
| `01_baseline_chen2020_c3_smoke.ipynb` | baseline C/3 DFN smoke test |
| `02_baseline_hppc_one_soc_smoke.ipynb` | one-SOC HPPC extraction chain |
| `03_tier0_mechanism_sanity_scan.ipynb` | initial Tier-0 perturbation sanity scan |
| `04_tier0_contact_resistance_audit.ipynb` | contact-resistance option audit |
| `05_corrected_tier0_fingerprint_scan.ipynb` | corrected Tier-0 fingerprint scan |
| `06_phaseB_level_scan_soc50.ipynb` | SOC=50% perturbation-level scan |
| `07_temperature_model_audit.ipynb` | temperature entry-point audit |
| `08_multi_soc_fingerprint_scan.ipynb` | multi-SOC fingerprint stability scan |
| `09_fingerprint_map_summary.ipynb` | consolidated fingerprint map and interpretation rules |

---

## Current Scope Boundary

This repository does not yet claim:

- full aging simulation
- SOH trajectory prediction
- validated SEI or plating aging behavior
- transferability across chemistries
- thermal-aging coupling
- experimental validation of the simulated fingerprints

Current conclusions are bounded by:

- Chen2020 DFN for controlled perturbation fingerprint mapping,
- OKane2022 DFN for degradation-enabled SEI-only aging branches,
- selected perturbation families
- HPPC-style 1C 10 s discharge pulse
- 600 s relaxation
- default isothermal 25 °C condition unless explicitly varied
- selected SOC points

---

## Next Steps

Planned next stages:

1. Add representative figures to README.
2. Extend fingerprint checks to selected temperature-mechanism interactions.
3. Add controlled aging mechanism branches:
   - SEI-only
   - plating-stress isolation
4. Later: compare simulated fingerprints with experimental HPPC aging observables.

---

## Project Status

Current status:

    Phase A: infrastructure and HPPC observable extraction — complete
    Phase B-0: corrected Tier-0 fingerprints — complete
    Phase B-1: SOC=50% perturbation-level scan — complete
    Phase B-2: temperature entry audit — complete
    Phase B-3: multi-SOC fingerprint stability scan — complete
    Phase B-4: fingerprint map summary — complete
    Next: repository presentation cleanup and representative figures


## Fixed-endpoint pseudo-OCV audit

Notebook 16 adds a fixed-endpoint pseudo-OCV feasibility audit for the SEI-only aging branch. The protocol uses full-charge preconditioning, followed by a C/3 discharge to the same loaded terminal-voltage endpoint, `Ukl = 3.70 V`, and a fixed 60 min rest.

The audit shows that the fixed-endpoint protocol is technically clean: the loaded-voltage endpoint error is negligible and the rest-duration quality check passes. Under SEI-only aging, the same loaded terminal-voltage endpoint is reached after less discharged capacity. From 0 to 20 cycles, `Q_to_Ukl` decreases by approximately `0.01068 Ah`, while the nominal endpoint SOC shifts upward by approximately `0.214 percentage points`.

The finite-rest voltage descriptor remains weak. `U00_after_fixed_rest` shifts by approximately `+0.407 mV`, while the recovery amplitude remains essentially neutral. Therefore, the fixed-endpoint pseudo-OCV layer is classified as a feasibility-level auxiliary diagnostic layer, not as a strict OCV-SOC or ICA/DVA diagnostic.

Representative outputs:

- `docs/figures/fixed_endpoint_pseudo_ocv_Q_to_Ukl_drift.png`
- `docs/figures/fixed_endpoint_pseudo_ocv_endpoint_soc_drift.png`
- `docs/figures/fixed_endpoint_pseudo_ocv_U00_after_rest_drift_mV.png`
- `docs/figures/fixed_endpoint_pseudo_ocv_recovery_features.png`
- `docs/tables/fixed_endpoint_pseudo_ocv_quality_audit.csv`
- `docs/tables/fixed_endpoint_pseudo_ocv_drift_table.csv`
- `docs/tables/fixed_endpoint_pseudo_ocv_classification_table_clean.csv`
- `docs/tables/fixed_endpoint_pseudo_ocv_metric_table.csv`


## Strict OCV / ICA / DVA feasibility audit

Notebook 17 adds a dedicated low-rate OCV-like diagnostic branch for the SEI-only aging workflow. The protocol starts from the pre-diagnostic full-charge-rest checkpoint state generated by the aging protocol and then performs a C/25 discharge to 2.5 V followed by a 60 min rest.

A selected-segment audit is required because PyBaMM `starting_solution` carries the preceding aging history into the diagnostic solution. The final diagnostic discharge segment is therefore selected explicitly as the last discharge segment with `0.15 A <= I_mean <= 0.25 A` and duration greater than 1000 min.

The selected C/25 diagnostic segments pass the audit across all checkpoints. The low-rate discharge capacity decreases from `5.100624 Ah` at 0 cycles to `5.085432 Ah` at 20 cycles, corresponding to approximately `0.2978 %` capacity fade.

The start-state audit passes with a C/25 diagnostic start-voltage spread of approximately `5.407 mV`, below the 10 mV feasibility threshold. This supports feasibility-level OCV-like analysis, while early-Q derivative interpretation remains conservative.

The V(Q) quality audit passes for all checkpoints. ICA and DVA derivative features are technically extractable from the smoothed low-rate V(Q) curves. The dominant ICA peak appears around `Q ≈ 0.48–0.49 Ah`, while DVA shows stronger endpoint sensitivity near the low-voltage cutoff.

This branch is classified as a feasibility-level strict OCV / ICA / DVA audit. It does not yet prove strict thermodynamic OCV or mechanism-unique ICA/DVA fingerprints.

Representative outputs:

- `docs/figures/strict_ocv_like_VQ_overlay.png`
- `docs/figures/strict_ocv_like_deltaV_vs_Q.png`
- `docs/figures/strict_ocv_ica_overlay.png`
- `docs/figures/strict_ocv_dva_overlay.png`
- `docs/tables/strict_ocv_ica_dva_quality_audit.csv`
- `docs/tables/strict_ocv_ica_dva_curve_summary.csv`
- `docs/tables/strict_ocv_ica_dva_start_state_audit.csv`
- `docs/tables/strict_ocv_ica_dva_feature_table.csv`
- `docs/tables/strict_ocv_ica_dva_classification_table.csv`
- `docs/tables/strict_ocv_ica_dva_output_inventory.csv`


## Slow-rate OCV-like validation audit

Notebook 18 audits whether the C/25 OCV-like voltage-curve descriptors from Notebook 17 remain structurally stable when the diagnostic discharge rate is reduced to C/50.

The audit compares two SEI-only aging checkpoints, 0 cycles and 20 cycles, under two diagnostic rates: C/25 and C/50. The selected diagnostic segments pass the rate-specific audit. C/25 branches show mean current ≈ 0.2 A and duration ≈ 1525–1530 min, while C/50 branches show mean current ≈ 0.1 A and duration ≈ 3053–3062 min.

All V(Q) curves pass the quality audit. C/50 produces a systematic voltage elevation relative to C/25, consistent with lower polarization at lower diagnostic current. The mean C50–C25 voltage offset is approximately +6.1 to +6.2 mV, with p95 absolute difference ≈ 8.51 mV and endpoint-sensitive maximum differences of approximately 14–16 mV.

ICA and DVA features are extractable at both diagnostic rates. ICA peak position shows rate sensitivity, with C50–C25 peak-Q shifts of approximately +0.0463 Ah at 0 cycles and −0.0168 Ah at 20 cycles. DVA median magnitude remains highly stable, with relative changes below 0.3%.

Project-level classification:

`C/25 OCV-like diagnostic branch = partially supported`

C/25 remains adequate for practical OCV-like feasibility analysis, but derivative-level interpretation remains protocol-sensitive. The result supports C/25 as an engineering-practical diagnostic branch, but not as strict thermodynamic OCV.

Representative outputs:

- `docs/figures/slow_rate_ocv_validation_VQ_overlay.png`
- `docs/figures/slow_rate_ocv_validation_deltaV_rate_effect.png`
- `docs/figures/slow_rate_ocv_validation_ica_overlay.png`
- `docs/figures/slow_rate_ocv_validation_dva_overlay.png`
- `docs/tables/slow_rate_ocv_validation_selected_segment_audit.csv`
- `docs/tables/slow_rate_ocv_validation_curve_summary.csv`
- `docs/tables/slow_rate_ocv_validation_quality_audit.csv`
- `docs/tables/slow_rate_ocv_validation_rate_effect_audit.csv`
- `docs/tables/slow_rate_ocv_validation_feature_table.csv`
- `docs/tables/slow_rate_ocv_validation_feature_rate_audit.csv`
- `docs/tables/slow_rate_ocv_validation_classification_table.csv`
- `docs/tables/slow_rate_ocv_validation_output_inventory.csv`


## GITT-like finite-rest OCV reconstruction audit

Notebook 19 audits whether a coarse GITT-like pulse-rest diagnostic protocol can reconstruct finite-rest OCV-like voltage points from the SEI-only aging branch.

The protocol uses repeated C/10 discharge pulses followed by 60 min rest periods. Each diagnostic branch contains 16 pulse-rest pairs. Each pulse discharges approximately 0.25 Ah, producing a reconstructed finite-rest OCV-like curve over a cumulative discharge window of approximately 4.0 Ah.

The selected pulse-rest sequences pass the segment-level audit at both 0-cycle and 20-cycle checkpoints:

- mean pulse current ≈ 0.5 A,
- pulse duration = 30 min,
- rest duration = 60 min,
- cumulative reconstructed Q-window ≈ 4.0 Ah.

The finite-rest reconstruction quality audit passes. Rest-end voltage points are smooth and monotonic with cumulative discharged capacity. Pulse charge is highly consistent, and rest recovery amplitude remains positive for all pulse-rest pairs.

The 20-cycle curve is slightly lower than the 0-cycle reference over the reconstructed Q-window:

- mean ΔU(20 cycles − 0 cycles) ≈ −1.974 mV,
- median ΔU ≈ −2.054 mV,
- maximum absolute voltage drift ≈ 3.026 mV.

Rest-recovery amplitude changes are very weak, with mean Δrecovery ≈ −0.115 mV and maximum absolute recovery shift ≈ 0.630 mV.

Project-level classification:

`GITT-like finite-rest OCV reconstruction = feasibility supported`

The protocol can reconstruct smooth and monotonic finite-rest OCV-like points in the SEI-only aging branch. It provides a weak voltage-drift descriptor, but strict thermodynamic OCV remains unproven.

Representative outputs:

- `docs/figures/gitt_like_ocv_reconstruction_overlay.png`
- `docs/figures/gitt_like_ocv_deltaU_vs_Q.png`
- `docs/figures/gitt_like_ocv_recovery_amplitude.png`
- `docs/tables/gitt_like_ocv_segment_audit.csv`
- `docs/tables/gitt_like_ocv_selected_sequence_audit.csv`
- `docs/tables/gitt_like_ocv_reconstruction_point_table.csv`
- `docs/tables/gitt_like_ocv_quality_audit.csv`
- `docs/tables/gitt_like_ocv_0_vs_20_comparison_table.csv`
- `docs/tables/gitt_like_ocv_classification_table.csv`
- `docs/tables/gitt_like_ocv_output_inventory.csv`


## Stronger SEI-only aging checkpoint audit

Notebook 20 extends the SEI-only aging branch from 20 cycles to stronger checkpoints at 50 and 100 cycles.

The degradation mechanism is unchanged: OKane2022 with solvent-diffusion-limited SEI only, with plating, LAM, particle mechanics, SEI porosity change, and thermal coupling disabled.

The audit confirms that all available degradation-state metrics increase monotonically from 0 to 100 cycles:

- SEI thickness increases from approximately 5.01 nm to 18.66 nm.
- LLI increases from approximately 0.00009% to 0.1687%.
- total lithium lost increases from approximately 2.65e-7 mol to 4.79e-4 mol.
- SEI capacity loss increases from approximately 0.000007 Ah to 0.01284 Ah.

Relative to the 20-cycle checkpoint, the 100-cycle checkpoint amplifies all available degradation-state metrics by approximately 3.06×.

Project-level classification:

`50/100-cycle SEI-only aging checkpoints = supported`

The stronger checkpoints are suitable for downstream diagnostic audits. However, this notebook does not yet establish a mechanism-unique SEI diagnostic fingerprint; it only confirms monotonic and amplified SEI-only aging severity.

Representative outputs:

- `docs/figures/stronger_sei_aging_degradation_state.png`
- `docs/figures/stronger_sei_aging_capacity_loss.png`
- `docs/tables/stronger_sei_aging_state_table.csv`
- `docs/tables/stronger_sei_aging_monotonicity_audit.csv`
- `docs/tables/stronger_sei_aging_classification_table.csv`


## Stronger SEI diagnostic branch audit

Notebook 21 audits whether the stronger 0/20/50/100-cycle SEI-only checkpoints produce clearer downstream diagnostic observables.

Three diagnostic layers are evaluated:

1. capacity RPT / external capacity check,
2. C/25 OCV-like V(Q),
3. GITT-like finite-rest OCV reconstruction.

Capacity RPT provides the clearest downstream observable. The external discharge capacity decreases monotonically from `5.049518 Ah` at 0 cycles to `5.025803 Ah` at 100 cycles. At 100 cycles, the capacity fade is approximately `0.4696 %`, corresponding to a capacity loss of approximately `0.023715 Ah`. The capacity-loss trend links strongly to SEI-state degradation metrics, with correlation coefficients of approximately `0.93`.

C/25 OCV-like V(Q) is technically valid and aging-sensitive, but full-window interpretation is endpoint-amplified. The full-window 100-cycle mean voltage drift is approximately `−5.626 mV`, with p95 `|ΔU| ≈ 20.186 mV` and max `|ΔU| ≈ 115.120 mV`. After central-window control over `Q = 0.20–4.50 Ah`, the 100-cycle mean drift is reduced to approximately `−2.694 mV`, with p95 `|ΔU| ≈ 6.251 mV`. The endpoint-amplification flag is true.

GITT-like finite-rest reconstruction is technically clean and less endpoint-amplified, but the voltage signal remains weak. At 100 cycles, the finite-rest mean voltage drift is approximately `−2.280 mV`, with p95 `|ΔU| ≈ 4.145 mV`. Rest recovery amplitude remains an auxiliary descriptor, with a 100-cycle mean shift of approximately `−0.182 mV`.

Project-level classification:

`SEI-only stronger-checkpoint diagnostics = capacity-dominant, voltage-secondary`

Stronger SEI-only aging is clearly observable in external capacity RPT and degradation-state variables. C/25 and GITT-like voltage descriptors show monotonic aging-linked drift, but their interpretation remains secondary: C/25 is endpoint-amplified, while GITT-like finite-rest drift is cleaner but weak. Mechanism uniqueness remains unproven.

Representative outputs:

- `docs/figures/stronger_sei_diag_capacity_retention.png`
- `docs/figures/stronger_sei_diag_capacity_vs_degradation.png`
- `docs/figures/stronger_sei_diag_c25_VQ_overlay.png`
- `docs/figures/stronger_sei_diag_c25_deltaU_vs_Q.png`
- `docs/figures/stronger_sei_diag_gitt_reconstruction_overlay.png`
- `docs/figures/stronger_sei_diag_gitt_deltaU_vs_Q.png`
- `docs/figures/stronger_sei_diag_gitt_recovery_amplitude.png`
- `docs/tables/stronger_sei_diag_capacity_rpt_table.csv`
- `docs/tables/stronger_sei_diag_c25_revised_classification_table.csv`
- `docs/tables/stronger_sei_diag_gitt_classification_table.csv`
- `docs/tables/stronger_sei_diag_output_inventory.csv`


## Aging-evidence and fitting-target rejection rules

The project uses the following audit rules to decide whether a diagnostic feature is suitable as primary aging evidence or as a primary fitting target for aging-model parameterization.

A feature is **not recommended as a primary aging evidence / fitting target** if any of the following conditions apply:

1. **Signal-to-smoothing-range ratio < 1**  
   The aging-induced feature change is smaller than the variability caused by smoothing-window selection.

2. **Monotonic fraction across smoothing < 0.75**  
   The feature does not preserve a monotonic aging trend across different smoothing windows.

3. **Signal appears only in the endpoint region**  
   The feature is likely affected by cutoff-boundary amplification, usable-capacity shifts, or endpoint curvature.

4. **Strong preprocessing dependence**  
   The feature changes substantially with smoothing, interpolation, common-Q grid selection, or endpoint truncation.

5. **Weak physical linkage to degradation-state variables**  
   The feature is not consistently linked to SEI thickness, LLI, lithium loss, SEI capacity loss, or other degradation-state variables.

6. **Mechanism non-uniqueness**  
   The feature can plausibly be produced by multiple mechanisms, such as SEI growth, lithium plating, LAM, or resistance growth.

7. **Signal magnitude below protocol sensitivity**  
   The feature drift is smaller than the sensitivity introduced by the diagnostic protocol itself.

Current project interpretation:

- **Capacity RPT** is the recommended primary measurement-level fitting target for SEI-only aging.
- **GITT-like finite-rest voltage points** and **C/25 central-window V(Q)** are secondary voltage-shape constraints.
- **C/25 endpoint/full-window drift** is a boundary diagnostic only, because it is endpoint-amplified.
- **ICA/DVA derivative features** remain auxiliary audit descriptors under stronger SEI-only aging and are not recommended as primary fitting targets.


## Resistance-growth fingerprint audit

Notebook 23 audits whether pure contact / ohmic resistance growth produces a diagnostic fingerprint that is separable from SEI-only aging.

A controlled contact-resistance perturbation was applied using the OKane2022 DFN with contact resistance enabled. The imposed contact-resistance levels were:

- 0 mΩ
- 2 mΩ
- 5 mΩ
- 10 mΩ

The HPPC-like Ri(t) branch was performed at approximately 50.5% SOC using:

- initial SOC = 1.0
- C/3 discharge for 90 min
- 60 min rest
- 1C discharge pulse for 10 s
- 600 s relaxation

The imposed contact resistance was recovered almost exactly as an additive shift across all pulse-resistance windows:

- `Ri_0.05s`
- `Ri_0.1s`
- `Ri_1s`
- `Ri_10s`
- `Ri_recovery_0.1s`
- `Ri_recovery_1s`

The maximum additive error across Ri windows was approximately `1.18e-10 mΩ`, effectively numerical zero.

Raw recovery amplitude increased with contact resistance because it contains the instantaneous ohmic jump `I · R_contact`. After post-ohmic correction starting at `t_off + 0.1 s`, the relaxation descriptors became invariant across contact resistance:

- post-ohmic recovery amplitude ≈ `26.3136 mV`
- post-ohmic `tau_FG_eff` ≈ `25.5 s`
- post-ohmic `t95` ≈ `171.1 s`
- post-ohmic `t99` ≈ `409.1 s`
- post-ohmic `tau_tail` ≈ `72.077 s`

Capacity RPT showed only a weak usable-capacity boundary effect. At 10 mΩ contact resistance, capacity retention was approximately `99.9242%`, corresponding to an apparent capacity loss of `0.003828 Ah`.

Project-level classification:

`contact / ohmic resistance growth = Ri(t)-dominant fingerprint`

Pure contact resistance growth is separable from SEI-only aging. It should be parameterized primarily using multi-window pulse resistance targets, not capacity fade or derivative-voltage features.

Representative outputs:

- `docs/figures/resistance_growth_multi_window_Ri.png`
- `docs/figures/resistance_growth_raw_vs_corrected_relaxation.png`
- `docs/figures/resistance_growth_capacity_retention.png`
- `docs/tables/mechanism_fingerprint_registry_v0_2.csv`
- `docs/tables/resistance_growth_hppc_descriptor_table.csv`
- `docs/tables/resistance_growth_corrected_relaxation_descriptor_table.csv`
- `docs/tables/resistance_growth_ri_additive_error_summary.csv`
- `docs/tables/resistance_growth_corrected_relaxation_invariance_audit.csv`
- `docs/tables/resistance_growth_capacity_rpt_table.csv`
- `docs/tables/resistance_growth_fingerprint_summary_v0_2.csv`
- `docs/tables/resistance_growth_classification_table.csv`


## LAM fingerprint audit

Notebook 24 audits controlled LAM = Loss of Active Material（活性材料损失） as a mechanism-contrast branch.

Two LAM branches were evaluated by scaling active material volume fraction:

- NE-LAM = Negative Electrode Loss of Active Material（负极活性材料损失）
- PE-LAM = Positive Electrode Loss of Active Material（正极活性材料损失）

LAM levels:

- 5%
- 10%
- 20%

The audit used Mechanism Fingerprint Registry v0.2 and evaluated:

- Capacity RPT = Reference Performance Test（容量基准性能测试）
- C/25 OCV-like V(Q)（C/25 近似 OCV 电压曲线）
- central-window voltage drift（中央窗口电压漂移）
- ICA/DVA central features（中央窗口微分电压特征）
- endpoint / boundary behavior（端点 / 边界行为）
- fitting-target hierarchy（拟合目标层级）

Key findings:

- NE-LAM is capacity-dominant and boundary-sensitive.
- PE-LAM is voltage-shape / DVA-dominant and less endpoint-confounded.
- LAM produces stronger voltage-shape fingerprints than SEI-only aging.
- DVA central features become candidate fitting targets under LAM, especially PE-LAM.
- ICA peak features remain mostly unreliable as primary fitting targets.

Capacity RPT response:

- NE-LAM 5% / 10% / 20% capacity retention ≈ 95.09% / 90.18% / 80.31%.
- PE-LAM 5% / 10% / 20% capacity retention ≈ 99.85% / 99.68% / 97.33%.

C/25 central-window V(Q):

- PE-LAM 5% / 10% / 20% central mean ΔU ≈ −14.63 / −30.43 / −66.42 mV.
- PE-LAM endpoint amplification flag = False.
- NE-LAM 10% and 20% show endpoint amplification and require boundary-control interpretation.

DVA central features:

- NE-LAM 10% / 20% DVA_median central signal-to-smoothing ratio ≈ 2.77 / 4.27.
- PE-LAM 5% / 10% / 20% DVA_median central ratio ≈ 3.16 / 13.39 / 10.36.
- Direction consistency = 1.0.

Project-level classification:

`LAM fingerprint = capacity- and voltage-shape-sensitive, DVA-informative`

NE-LAM is best described as:

`capacity-dominant + boundary-sensitive`

PE-LAM is best described as:

`voltage-shape / DVA-dominant`

Representative outputs:

- `docs/figures/lam_fingerprint_c25_VQ_overlay.png`
- `docs/figures/lam_fingerprint_c25_deltaU_vs_Q.png`
- `docs/figures/lam_fingerprint_capacity_retention.png`
- `docs/figures/lam_fingerprint_ica_overlay.png`
- `docs/figures/lam_fingerprint_dva_overlay.png`
- `docs/tables/lam_fingerprint_branch_summary.csv`
- `docs/tables/lam_fingerprint_summary_v0_2.csv`
- `docs/tables/lam_fingerprint_classification_table.csv`


## Plating entry observability audit

Notebook 25 audits lithium plating（析锂）entry observability in the PyBaMM aging-bridge workflow.

The first model attempt showed an important option boundary: OKane2022 partially reversible plating（部分可逆析锂）depends on SEI thickness through dead-lithium decay, so `SEI = none` caused a division-by-zero failure. The corrected setup uses an SEI background:

- SEI = solvent-diffusion limited
- lithium plating = partially reversible
- lithium plating porosity change = false
- LAM and particle mechanics disabled
- isothermal model

The protocol starts at low SOC and applies a stress-charge branch:

- initial SOC = 0.05
- charge to 4.2 V at stress charge rate
- hold at 4.2 V until C/20
- rest for 60 min
- C/3 discharge to 2.5 V
- rest for 60 min

Audited conditions:

- no_plating_25C_1C
- plating_25C_1C
- plating_10C_1C
- plating_10C_2C
- matched controls: no_plating_10C_1C and no_plating_10C_2C

Direct negative-electrode plating variables were available and extractable. Matched no-plating controls were clean, while all plating-enabled cases showed direct plating signals.

Direct plating indicators increased with stress:

- loss of capacity to plating: ≈ 0.0445 Ah at 25°C/1C, ≈ 0.0728 Ah at 10°C/1C, ≈ 0.0954 Ah at 10°C/2C
- maximum plating current density: ≈ 0.031, 0.058, and 0.139 A/m² respectively

Matched post-stress discharge-capacity differences were much smaller:

- 25C_1C: −0.002763 Ah, approximately −0.0555%
- 10C_1C: −0.007530 Ah, approximately −0.1543%
- 10C_2C: −0.010112 Ah, approximately −0.2073%

This confirms that direct plating-variable peaks must not be interpreted as final irreversible capacity loss under partially reversible plating.

A charge-segment audit clarified protocol interpretation:

- 1C stress-charge segments reached approximately −5 A
- 2C stress-charge segments reached approximately −10 A
- final discharge-capacity checks were performed at common C/3, approximately +1.6667 A

Project-level classification:

`plating entry observability = supported`

`full plating fingerprint = deferred`

Representative outputs:

- `docs/figures/plating_entry_capacity_loss_to_plating.png`
- `docs/figures/plating_entry_current_density.png`
- `docs/figures/plating_entry_discharge_capacity.png`
- `docs/figures/plating_entry_matched_capacity_difference.png`
- `docs/figures/plating_entry_direct_vs_matched_capacity_effect.png`
- `docs/figures/plating_entry_charge_segment_current_audit.png`
- `docs/tables/plating_entry_observability_compact.csv`
- `docs/tables/plating_entry_matched_plating_effect_audit.csv`
- `docs/tables/plating_entry_revised_classification_table.csv`


## Plating full-fingerprint Phase A audit

Notebook 26 closes Phase A of the lithium plating（析锂）full-fingerprint audit.

The notebook was intentionally scoped to Phase A after HPPC Phase B repeatedly killed the Jupyter kernel under:

- DFN model,
- SEI-background partially reversible plating,
- `starting_solution`,
- dense HPPC sampling.

Therefore, Notebook 26 should not be interpreted as a completed full plating fingerprint.

Phase A completed:

- post-stress state generation,
- direct plating-state observability,
- Capacity RPT = Reference Performance Test（容量基准性能测试） from post-stress states,
- matched capacity-effect audit,
- Phase A visualization,
- execution-resource boundary classification.

Key Phase A results:

- matched no-plating controls remained clean;
- plating-enabled branches showed direct plating signals;
- max direct plating capacity variable ≈ `0.095446 Ah`;
- max plating current density ≈ `0.138783 A/m²`;
- max matched discharge-capacity effect ≈ `0.010112 Ah`.

Classification:

`plating full-fingerprint Phase A = supported`

`full plating fingerprint = deferred`

HPPC Ri(t)（时间窗内阻） and corrected relaxation descriptors（修正后恢复描述符） under plating must be moved to a process-isolated workflow rather than executed inside Jupyter.

Representative outputs:

- `docs/figures/plating_full_phaseA_direct_plating_capacity.png`
- `docs/figures/plating_full_phaseA_matched_capacity_effect.png`
- `docs/figures/plating_full_phaseA_direct_vs_capacity_effect.png`
- `docs/tables/plating_full_branch_contract.csv`
- `docs/tables/plating_full_post_stress_observability_table.csv`
- `docs/tables/plating_full_capacity_table.csv`
- `docs/tables/plating_full_matched_capacity_audit.csv`
- `docs/tables/plating_full_phaseA_classification_table.csv`
- `docs/tables/plating_full_phaseA_output_inventory.csv`


## Plating HPPC process-isolated audit

Notebook 26B completes the HPPC Ri(t)（时间窗内阻）and corrected relaxation（修正后恢复描述符）layer that was deferred from Notebook 26.

Notebook 26 showed that in-notebook PyBaMM execution with DFN + SEI-background plating + `starting_solution` + dense HPPC sampling repeatedly killed the Jupyter kernel. Notebook 26B therefore moved HPPC execution into isolated external Python processes.

External runner:

- `scripts/run_plating_hppc_condition.py`

Each condition was executed in a separate process and wrote descriptor CSV outputs. This solved the Jupyter kernel-death boundary.

Key results:

- all 6 matched HPPC conditions produced descriptor and segment-audit CSV files;
- absolute Ri(t) is strongly temperature-sensitive;
- matched plating-minus-control Ri(t) shifts are weak / near-zero;
- maximum absolute matched Ri(t) delta ≈ `0.120 mΩ`;
- corrected relaxation changes are also weak;
- maximum corrected recovery-amplitude delta < `0.3 mV`;
- maximum corrected t95 delta ≈ `3.3 s`.

Classification:

`plating HPPC layer = process-isolated audit completed; Ri(t) / corrected relaxation weak`

Interpretation:

Direct plating variables are observable under the SEI-background partially reversible plating branch, but HPPC Ri(t) and corrected relaxation are not primary fitting-target layers for this plating branch under the tested stress range.

Representative outputs:

- `docs/figures/plating_26B_hppc_Ri_absolute.png`
- `docs/figures/plating_26B_hppc_matched_Ri_shift.png`
- `docs/figures/plating_26B_hppc_corrected_relaxation_shift.png`
- `docs/tables/plating_26B_hppc_descriptor_table.csv`
- `docs/tables/plating_26B_matched_hppc_audit.csv`
- `docs/tables/plating_26B_classification_table.csv`

