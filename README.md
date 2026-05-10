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

- Chen2020 DFN
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
