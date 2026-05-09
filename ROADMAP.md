# ROADMAP

## Scientific goal

Build a mechanism-traceable bridge between electrochemical degradation mechanisms and ECM-level diagnostic observables.

## Phase B: DFN parameter perturbation -> ECM observable mapping

Perturbation dimensions:

1. Solid diffusion coefficient decrease: D_s,n / D_s,p
2. Exchange-current density decrease: j0
3. Contact resistance increase
4. LLI-equivalent stoichiometry shift
5. LAM-equivalent active material volume fraction decrease

Observable outputs:

- C/3 capacity
- Energy efficiency / round-trip efficiency
- HPPC Ri(SOC)
- tau1/tau2(SOC) from biexponential relaxation fitting
- dV/dt features
- normalized V-Q curves

## Phase B execution structure

Day 1:
- Repository structure
- Baseline Chen2020 C/3 simulation
- One-SOC HPPC baseline smoke test

Day 2:
- Baseline 5-SOC HPPC
- Extraction pipeline

Day 3:
- Tier 0 perturbation sanity scan

Day 4-7:
- Full 21-case Phase B scan

## Phase C: isolated mechanism cycling

Branches:

1. SEI-only cycling
2. Plating-stress isolated branch

Phase C starts only after Phase B fingerprint extraction is stable.

## Acceptance criteria for Day 1

- Repository structure exists
- PyBaMM environment is installable
- Baseline Chen2020 C/3 simulation runs
- One-SOC HPPC baseline simulation runs
- Ri extraction returns finite value
- First git commit created
