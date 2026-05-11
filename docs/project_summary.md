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
