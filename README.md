# PyBaMM Aging Bridge

PyBaMM Aging Bridge is a mechanism-to-observable modeling project focused on lithium-ion battery aging diagnostics.

The project investigates how electrochemical degradation mechanisms, including diffusion limitation, charge-transfer degradation, contact resistance growth, lithium inventory loss, and active material loss, manifest as observable ECM-level signatures such as Ri(SOC), relaxation time constants tau1/tau2, dV/dt behavior, energy efficiency, and voltage-charge trajectory deformation.

The core objective is to establish a traceable bridge between DFN-level physical perturbations and engineering-level battery diagnostics.

## Project logic

DFN physical perturbation  
→ simulated cell response  
→ HPPC / charge-discharge evaluation  
→ ECM-level observable extraction  
→ aging diagnostic fingerprint

## Core observables

- Capacity
- Energy efficiency / round-trip efficiency
- HPPC-derived Ri(SOC)
- Biexponential relaxation time constants tau1/tau2
- dV/dt features
- Normalized voltage-charge curves

## Phase B

DFN parameter perturbation to ECM observable mapping.

## Phase C

Isolated mechanism cycling for SEI and plating-stress branches.
