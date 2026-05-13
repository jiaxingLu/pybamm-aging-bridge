# Project Summary — PyBaMM Aging Bridge

## One-line description

PyBaMM Aging Bridge is a mechanism-to-observable modeling project that maps DFN-level electrochemical perturbations to ECM-level HPPC diagnostic fingerprints.

## Research motivation

Battery aging is difficult to observe directly in practical systems. In engineering applications, aging-related changes are usually inferred from measurable signals such as pulse resistance, voltage relaxation, capacity, energy efficiency, or temperature-dependent behavior.

A central ambiguity is that different degradation mechanisms can produce similar observable symptoms. For example, an increase in short-window resistance may result from charge-transfer degradation, contact resistance growth, temperature effects, or other coupled mechanisms.

This project addresses that ambiguity by asking:

    Which electrochemical perturbation produces which observable diagnostic fingerprint?

## Core methodology

The project follows a mechanism-to-observable workflow:

    DFN-level physical perturbation
    -> simulated HPPC response
    -> CDEFG / Ri / relaxation extraction
    -> ECM-level observable fingerprint
    -> diagnostic interpretation rule

Instead of assuming an SOH value directly, the project perturbs interpretable physical pathways in a PyBaMM DFN model and audits how these perturbations appear in engineering-level observables.

## Model and protocol

Current baseline configuration:

- Model: PyBaMM DFN
- Parameter set: Chen2020
- Thermal setting: default isothermal
- Default temperature: 25 °C
- Pulse protocol: 1C discharge pulse for 10 s
- Relaxation: 600 s
- SOC points: 10%, 30%, 50%, 70%, 90%

The analysis explicitly tracks PyBaMM current convention:

    +I = discharge
    -I = charge

## Observable extraction

The project uses a CDEFG-style HPPC extraction workflow.

For each pulse:

| Point | Meaning |
|---|---|
| C | pre-pulse baseline voltage |
| D | short-time voltage response after pulse start |
| E | end-of-pulse voltage |
| F | short-time recovery after current interruption |
| G | long-time recovered voltage |

Extracted observables:

- Ri_CD
- Ri_EF
- tau1 / tau2 from biexponential relaxation fitting
- 60 s and 300 s tau descriptors
- relaxation morphology
- contact overpotential
- normalized remaining polarization

Important methodological point:

    tau1 / tau2 are observation-window-dependent descriptors,
    not unique physical constants.

## Perturbation families

The current study focuses on four controlled perturbation families:

| Family | Perturbation | Physical meaning |
|---|---|---|
| Ds_p | positive particle diffusivity decrease | positive solid diffusion limitation |
| j0_n | negative exchange-current density decrease | negative-electrode charge-transfer degradation |
| j0_p | positive exchange-current density decrease | positive-electrode kinetic degradation |
| contact_R | contact resistance increase | pure ohmic / external contact resistance |

## Main findings

### 1. Diffusion-sensitive fingerprint

Reducing positive particle diffusivity produces:

- tau2 increase,
- slower relaxation recovery,
- nearly unchanged short-window Ri.

Interpretation:

    tau2 increases while Ri remains nearly unchanged
    -> diffusion-sensitive relaxation limitation

This fingerprint is sign-stable across SOC, but its magnitude is SOC-dependent.

### 2. Negative-electrode kinetic fingerprint

Reducing negative electrode exchange-current density produces:

- strong Ri increase,
- nearly unchanged tau2.

Interpretation:

    Ri increases strongly while tau2 remains close to baseline
    -> negative-electrode charge-transfer / kinetic limitation

This fingerprint is sign-stable and magnitude-stable across the tested SOC range.

### 3. Positive-electrode kinetic fingerprint

Reducing positive electrode exchange-current density produces:

- moderate Ri increase,
- nearly unchanged tau2.

Interpretation:

    Ri increases moderately while tau2 remains close to baseline
    -> positive-electrode kinetic limitation

This fingerprint is weaker than the negative-electrode kinetic fingerprint under the present protocol.

### 4. Contact-resistance fingerprint

Increasing contact resistance produces:

- exact Ri increase equal to the imposed contact resistance,
- contact overpotential consistent with I·R,
- unchanged tau descriptors.

Interpretation:

    constant Ri offset across SOC + I·R consistency + unchanged tau
    -> pure ohmic/contact resistance contribution

This fingerprint is SOC-invariant under the present protocol.

## Temperature audit

A small 10 / 25 / 45 °C audit showed that temperature is an active operating-condition layer.

Under the current Chen2020 isothermal workflow:

- Ri changes strongly with temperature,
- tau2 descriptors remain nearly unchanged,
- temperature enters primarily through exchange-current density and electrolyte transport functions.

Therefore, temperature effects must be separated from degradation-mechanism perturbations in future scans.

## Key methodological result

Mechanism fingerprints are not simply present or absent. They have two layers:

1. Sign stability:
   whether an observable changes in the same direction across SOC.

2. Magnitude stability:
   whether the size of that change remains similar across SOC.

For example:

- contact resistance is both sign-stable and magnitude-stable;
- j0_n is sign-stable and relatively magnitude-stable;
- Ds_p is sign-stable but magnitude state-dependent.


## Temperature-representative fingerprint check

A representative temperature scan was performed at SOC = 50% using:

- 10 °C
- 25 °C
- 45 °C

The tested perturbation cases were:

- baseline
- Ds_p_x0p5
- j0_n_x0p5
- j0_p_x0p5
- contact_R_5mOhm

Main observations:

1. Baseline Ri decreases strongly as temperature increases.
2. Ds_p_x0p5 remains identifiable through tau2 increase across all tested temperatures.
3. j0_n_x0p5 remains identifiable through Ri increase, with mild magnitude variation.
4. j0_p_x0p5 remains sign-stable but weakens at higher temperature.
5. contact_R_5mOhm remains exactly temperature-invariant, with +5 mΩ Ri shift and 25 mV contact overpotential.

This extends the fingerprint framework from SOC-aware interpretation to SOC- and temperature-aware diagnostic interpretation.



## SEI-only Metric Registry v0.1 update

The SEI-only branch has been extended from an internal-degradation and Ri/tau audit into a broader Metric Registry v0.1 framework.

Implemented diagnostic layers include:

1. degradation-state variables,
2. external capacity RPT,
3. multi-window resistance,
4. fitted tau1/tau2 descriptors,
5. non-parametric relaxation descriptors,
6. voltage-recovery / pseudo-OCV feasibility metrics.

The following layers are registered but deferred:

- strict OCV-SOC curve,
- ICA / DVA features,
- fixed-endpoint pseudo-OCV after same Ukl,
- thermal / heat-generation indicators.

### Main SEI-only result

Under the current proof-of-concept protocol, SEI-only aging is classified as:

    capacity / LLI dominant mixed signature

The strongest evidence comes from:

- monotonic SEI thickness growth,
- monotonic LLI growth,
- monotonic side-reaction capacity loss,
- external capacity RPT fade.

At the final 20-cycle checkpoint, the capacity RPT showed:

- capacity retention of approximately 99.746%,
- capacity fade of approximately 0.254%,
- capacity loss of approximately 0.0128 Ah relative to the 0-cycle RPT.

The multi-window resistance layer showed weak but monotonic drift, with final changes on the order of approximately 0.2–0.3 mΩ.

The fitted tau1/tau2 and non-parametric relaxation descriptors were successfully extracted, but they remained secondary audit layers rather than dominant fingerprints.

### Voltage-recovery and OCV boundary

Finite-rest HPPC recovery descriptors, such as Uinf and recovery amplitude, were extracted as feasibility-level voltage-recovery features.

These are not strict OCV-SOC measurements.

A strict OCV / ICA / DVA analysis requires a dedicated low-rate or quasi-equilibrium voltage-curve protocol.


## Interpretation boundary

This project does not yet claim:

- full aging simulation,
- SOH trajectory prediction,
- validated SEI or plating behavior,
- transferability across chemistries,
- thermal-aging coupling,
- experimental validation of all simulated fingerprints.

The current conclusions are bounded by:

- Chen2020 DFN for controlled perturbation fingerprint mapping,
- OKane2022 DFN for degradation-enabled SEI-only aging branches,
- selected perturbation families,
- default isothermal 25 °C unless otherwise stated,
- HPPC-style 1C 10 s discharge pulse,
- 600 s relaxation,
- selected SOC points.

## Current status

Completed:

- baseline DFN HPPC extraction chain,
- corrected Tier-0 fingerprint scan,
- SOC=50% perturbation-level scan,
- temperature entry audit,
- multi-SOC fingerprint stability scan,
- consolidated fingerprint map,
- README with representative figures and tables.

Next possible directions:

1. multi-temperature representative fingerprint checks,
2. SEI-only aging branch,
3. plating-stress isolation branch,
4. comparison with experimental HPPC aging observables.


## Notebook 16 — Fixed-endpoint pseudo-OCV feasibility audit

Notebook 16 extends the SEI-only diagnostic framework with a fixed-endpoint pseudo-OCV audit. The diagnostic protocol consists of full-charge preconditioning, C/3 discharge to a fixed loaded terminal-voltage endpoint (`Ukl = 3.70 V`), and a fixed 60 min rest before evaluating finite-rest voltage recovery features.

### Main findings

- The protocol quality check passes: the fixed loaded-voltage endpoint is reached with negligible error, and the 60 min rest duration is consistent across checkpoints.
- `Q_to_Ukl` decreases from `2.307087 Ah` at 0 cycles to `2.296406 Ah` at 20 cycles, corresponding to a drift of approximately `-0.010680 Ah`.
- The nominal SOC at the fixed loaded-voltage endpoint shifts upward by approximately `+0.214 percentage points`.
- `U00_after_fixed_rest` changes weakly by approximately `+0.407 mV`.
- The recovery amplitude changes by only approximately `-0.0097 mV`, which is interpreted as essentially neutral.

### Interpretation boundary

This layer must be interpreted as **fixed-endpoint pseudo-OCV**, not as strict OCV. The endpoint is defined under load by a fixed terminal voltage, and the voltage recovery is evaluated after a finite rest duration. Therefore, `U00_after_fixed_rest` is a finite-rest voltage-recovery descriptor, not a thermodynamic OCV-SOC point.

The main diagnostic signal is not a strong OCV shift. Instead, the relevant observation is that under SEI-only aging, the same loaded terminal-voltage endpoint is reached after less discharged capacity. This makes the layer useful as an auxiliary feasibility-level descriptor, while strict OCV / ICA / DVA remains deferred to a dedicated low-rate or quasi-equilibrium protocol.

### Classification

`fixed-endpoint pseudo-OCV = feasibility-level auxiliary diagnostic layer`

Dominant evidence:

- clear `Q_to_Ukl` drift,
- small endpoint nominal-SOC shift,
- weak finite-rest voltage shift,
- neutral recovery-amplitude response.

This result complements the Metric Registry v0.1 by adding a voltage-curve / finite-rest descriptor layer, but it does not replace a dedicated strict OCV / ICA / DVA audit.

### Representative files

Figures:

- `docs/figures/fixed_endpoint_pseudo_ocv_Q_to_Ukl_drift.png`
- `docs/figures/fixed_endpoint_pseudo_ocv_endpoint_soc_drift.png`
- `docs/figures/fixed_endpoint_pseudo_ocv_U00_after_rest_drift_mV.png`
- `docs/figures/fixed_endpoint_pseudo_ocv_recovery_features.png`

Tables:

- `docs/tables/fixed_endpoint_pseudo_ocv_quality_audit.csv`
- `docs/tables/fixed_endpoint_pseudo_ocv_drift_table.csv`
- `docs/tables/fixed_endpoint_pseudo_ocv_classification_table_clean.csv`
- `docs/tables/fixed_endpoint_pseudo_ocv_metric_table.csv`


## Notebook 17 — Strict OCV / ICA / DVA feasibility audit

Notebook 17 establishes a dedicated low-rate OCV-like diagnostic branch for the SEI-only aging workflow.

The first implementation attempt used repeated full-charge preconditioning before the low-rate diagnostic branch. PyBaMM warnings showed that some preconditioning steps were infeasible or skipped because the aging checkpoints already ended in a full-charge-rest state. The protocol was therefore corrected to a diagnostic-only branch:

- start from the pre-diagnostic full-charge-rest aging checkpoint,
- use `initial_soc = 1.0` for the 0-cycle reference,
- perform C/25 discharge to 2.5 V,
- finish with a 60 min rest.

### Segment-selection audit

A selected-segment audit was required because PyBaMM `starting_solution` carries previous aging history into the diagnostic solution. The final C/25 diagnostic discharge segment was selected explicitly as the last discharge segment satisfying:

`0.15 A <= I_mean <= 0.25 A` and `duration > 1000 min`.

The selected diagnostic segments passed the audit:

- mean current ≈ 0.2 A,
- duration ≈ 1525–1530 min,
- final voltage ≈ 2.5 V,
- low-rate discharge capacity ≈ 5.085–5.101 Ah.

### Main findings

The low-rate discharge capacity decreased from `5.100624 Ah` at 0 cycles to `5.085432 Ah` at 20 cycles, corresponding to approximately `0.2978 %` capacity fade.

The start-state audit passed. The C/25 diagnostic start-voltage spread was approximately `5.407 mV`, below the 10 mV feasibility threshold. This is acceptable for feasibility-level OCV-like analysis, but early-Q derivative features should be interpreted conservatively.

The V(Q) quality audit passed for all checkpoints:

- Q was monotonic,
- each curve contained more than 1500 points,
- voltage span was approximately 1.68–1.69 V,
- local voltage-increase fractions remained below 0.2%.

The OCV-like V(Q) curves are technically extractable and largely overlap across aging checkpoints. The ΔU(Q) comparison relative to the 0-cycle reference shows weak negative voltage drift over much of the common Q-window and stronger endpoint sensitivity near the low-voltage cutoff.

ICA and DVA features were technically extractable from the smoothed low-rate V(Q) curves.

For ICA, the dominant peak appears near `Q ≈ 0.48–0.49 Ah`. From 0 to 20 cycles, the peak magnitude changed from approximately `22.998 Ah/V` to `22.449 Ah/V`, while the peak position shifted from approximately `0.479 Ah` to `0.491 Ah`.

For DVA, the median magnitude remained nearly unchanged at approximately `0.1775 V/Ah`, while the endpoint-sensitive DVA peak increased from approximately `2.425 V/Ah` to `2.735 V/Ah`.

### Interpretation boundary

This notebook establishes technical feasibility, not a fully validated thermodynamic OCV or mechanism-resolved ICA/DVA diagnostic.

The C/25 discharge branch should be described as an OCV-like or quasi-equilibrium voltage-curve diagnostic. It should not be called strict thermodynamic OCV unless relaxation effects are further quantified or a slower/GITT-like protocol is introduced.

ICA and DVA are derivative features extracted from a smoothed low-rate V(Q) curve. Their existence confirms that derivative-based voltage-curve descriptors are technically obtainable in the SEI-only branch. Their mechanistic interpretation remains deferred.

### Classification

`strict OCV / ICA / DVA branch = feasibility-level diagnostic branch`

Supported:

- C/25 low-rate diagnostic discharge produces smooth OCV-like V(Q) curves.
- Low-rate capacity fade is directly observable.
- ICA and DVA curves are technically extractable after smoothing and quality audit.
- ICA/DVA should be classified as audit-level derivative descriptors.
- Endpoint-region DVA drift is visible but must be interpreted conservatively.

Not supported:

- strict thermodynamic OCV,
- mechanism-unique ICA/DVA fingerprints,
- separation of SEI-only voltage-curve drift from all possible electrode-specific aging signatures,
- validation against experimental aging data.

### Representative files

Figures:

- `docs/figures/strict_ocv_like_VQ_overlay.png`
- `docs/figures/strict_ocv_like_deltaV_vs_Q.png`
- `docs/figures/strict_ocv_ica_overlay.png`
- `docs/figures/strict_ocv_dva_overlay.png`

Tables:

- `docs/tables/strict_ocv_ica_dva_quality_audit.csv`
- `docs/tables/strict_ocv_ica_dva_curve_summary.csv`
- `docs/tables/strict_ocv_ica_dva_start_state_audit.csv`
- `docs/tables/strict_ocv_ica_dva_feature_table.csv`
- `docs/tables/strict_ocv_ica_dva_classification_table.csv`
- `docs/tables/strict_ocv_ica_dva_output_inventory.csv`


## Notebook 18 — Slow-rate OCV-like validation audit

Notebook 18 stress-tests the C/25 OCV-like diagnostic branch established in Notebook 17 by comparing it against a slower C/50 diagnostic branch.

### Study design

The audit compares two SEI-only aging checkpoints:

- 0 cycles
- 20 cycles

Two diagnostic rates are evaluated:

- C/25
- C/50

The aging mechanism, model configuration, checkpoint construction, and segment-selection logic remain aligned with Notebook 17. The only intentional variable is diagnostic discharge rate.

### Main findings

The selected diagnostic segments passed the rate-specific audit. C/25 branches show mean current ≈ 0.2 A and duration ≈ 1525–1530 min. C/50 branches show mean current ≈ 0.1 A and duration ≈ 3053–3062 min.

All V(Q) curves passed the quality audit. C/50 produces a systematically higher terminal voltage than C/25, consistent with reduced ohmic and polarization losses at lower diagnostic current.

The common-Q rate-effect audit shows:

- mean C50–C25 voltage offset ≈ +6.1 to +6.2 mV,
- p95 absolute C50–C25 difference ≈ 8.51 mV,
- maximum absolute C50–C25 difference ≈ 14–16 mV near the low-voltage endpoint.

The main V(Q) structure is broadly stable between C/25 and C/50, while endpoint regions remain rate-sensitive.

ICA features are extractable at both rates. The dominant ICA peak remains present, but its peak position shows non-negligible rate sensitivity:

- 0 cycles: C50–C25 ICA peak-Q shift ≈ +0.0463 Ah,
- 20 cycles: C50–C25 ICA peak-Q shift ≈ −0.0168 Ah.

DVA median magnitude is highly stable between C/25 and C/50, with relative changes below 0.3%. Endpoint-sensitive DVA peaks still require conservative interpretation.

### Interpretation boundary

Notebook 18 supports the practical use of C/25 as an OCV-like feasibility diagnostic branch, but only with qualified interpretation.

C/25 is adequate for extracting smooth V(Q), ΔU(Q), ICA, and DVA descriptors at the audit level. However, comparison with C/50 shows that derivative features are not fully protocol-invariant. ICA peak position remains sensitive to diagnostic rate and should not be overinterpreted as a strict thermodynamic OCV feature.

### Classification

`C/25 OCV-like diagnostic branch = partially supported`

Project-level wording:

> C/25 is adequate for practical OCV-like feasibility analysis, but derivative-level interpretation remains protocol-sensitive.

### Representative files

Figures:

- `docs/figures/slow_rate_ocv_validation_VQ_overlay.png`
- `docs/figures/slow_rate_ocv_validation_deltaV_rate_effect.png`
- `docs/figures/slow_rate_ocv_validation_ica_overlay.png`
- `docs/figures/slow_rate_ocv_validation_dva_overlay.png`

Tables:

- `docs/tables/slow_rate_ocv_validation_selected_segment_audit.csv`
- `docs/tables/slow_rate_ocv_validation_curve_summary.csv`
- `docs/tables/slow_rate_ocv_validation_quality_audit.csv`
- `docs/tables/slow_rate_ocv_validation_rate_effect_audit.csv`
- `docs/tables/slow_rate_ocv_validation_feature_table.csv`
- `docs/tables/slow_rate_ocv_validation_feature_rate_audit.csv`
- `docs/tables/slow_rate_ocv_validation_classification_table.csv`
- `docs/tables/slow_rate_ocv_validation_output_inventory.csv`

