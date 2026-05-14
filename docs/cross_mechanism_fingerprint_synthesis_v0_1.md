# Cross-mechanism Fingerprint Synthesis v0.1

## Scope

This document summarizes the current mechanism-to-observable fingerprint framework for lithium-ion battery aging diagnostics and measurement-based aging-model parameterization.

The synthesis consolidates completed audit notebooks into a unified evidence structure. It does not introduce new simulations or new mechanism evidence.

Mechanism families covered in this version:

- SEI-only aging
- Contact / ohmic resistance growth
- Negative-electrode loss of active material
- Positive-electrode loss of active material
- Lithium plating

## Main objective

The objective is to identify which observable features are suitable as fitting targets for different aging mechanisms.

A measurable feature is not automatically a valid fitting target. The current framework separates primary targets, secondary targets, auxiliary audit layers, rejected features, and deferred features.

## Mechanism-level target hierarchy

| Mechanism | Current fingerprint classification | Primary target layer |
|---|---|---|
| SEI-only aging | Capacity-dominant, voltage-secondary, derivative-auxiliary | Capacity RPT |
| Contact / ohmic resistance growth | Ri(t)-dominant | Multi-window Ri(t) |
| Negative-electrode loss of active material | Capacity-dominant and boundary-sensitive | Capacity RPT |
| Positive-electrode loss of active material | Voltage-shape and DVA-dominant | C/25 central-window V(Q), DVA central features |
| Lithium plating | Direct mechanism-state observability supported; external diagnostic fingerprint deferred | Direct plating-state variables |

## Interpretation by mechanism

### SEI-only aging

SEI-only aging is currently classified as capacity-dominant. Capacity RPT provides the clearest primary fitting target in the completed audits.

C/25 central-window V(Q) and GITT-like finite-rest voltage provide secondary information, but voltage interpretation must avoid endpoint-amplified regions. ICA and DVA features remain auxiliary or rejected as primary targets under the current evidence because their derivative-level response is sensitive to preprocessing or weaker than capacity-level evidence.

### Contact / ohmic resistance growth

Contact / ohmic resistance growth is classified as Ri(t)-dominant. Multi-window Ri(t) provides the primary fitting target.

Raw recovery amplitude and raw recovery area are not valid primary relaxation descriptors because they are confounded by the instantaneous ohmic voltage jump. Post-ohmic corrected relaxation descriptors remain largely invariant in the completed audit and should not be interpreted as primary evidence of slow relaxation growth.

### Loss of active material

Negative-electrode loss of active material is capacity-dominant and boundary-sensitive. Capacity RPT is the primary target, while central-window voltage and DVA features provide secondary support when endpoint amplification is controlled.

Positive-electrode loss of active material is voltage-shape and DVA-dominant within the tested range. C/25 central-window V(Q) and DVA central features are the strongest current fitting-target candidates. Capacity RPT remains secondary.

### Lithium plating

Lithium plating direct mechanism-state observability is supported in the current model-based audit. Direct plating-state variables show stress sensitivity and matched-control separation.

This does not close the external diagnostic fingerprint. Capacity RPT, Ri(t), and corrected relaxation descriptors remain auxiliary under the current evidence. C/25 central-window V(Q), GITT-like finite-rest voltage, ICA features, and DVA features remain deferred until future process-isolated diagnostic audits support or reject them.

## Feature rejection and downgrade logic

A feature should not be used as a primary fitting target if one or more of the following risks dominate:

- endpoint amplification
- smoothing sensitivity
- weak matched-control separation
- mechanism non-uniqueness
- ohmic-jump confounding
- protocol sensitivity
- model-state-only observability
- execution-resource boundary

These rules are intended to prevent artifact-driven fitting and to keep fitting targets physically interpretable.

## Current conclusion

The project has moved from isolated mechanism notebooks to a structured mechanism-to-observable fingerprint framework.

The current evidence supports the following hierarchy:

- SEI-only aging: capacity-first
- Contact / ohmic resistance growth: Ri(t)-first
- Negative-electrode loss of active material: capacity-first with boundary control
- Positive-electrode loss of active material: voltage-shape and DVA-first
- Lithium plating: direct mechanism-state observability supported, external diagnostic fingerprint deferred

## Current limitations

This synthesis is evidence-conservative. It does not claim that all aging mechanisms are uniquely identifiable from one observable.

Capacity fade, voltage-shape drift, resistance increase, and derivative features can be mechanism-non-unique. Mechanism-specific interpretation requires contrast branches, matched controls, and protocol-boundary checks.

Lithium plating remains the most important open branch for external diagnostic closure.

## Recommended next step

The next useful technical step is targeted closure of deferred lithium-plating external diagnostics under process-isolated execution. Priority diagnostic layers are:

1. C/25 central-window V(Q)
2. GITT-like finite-rest voltage
3. ICA central features
4. DVA central features

Broad simulation sweeps are not recommended before these deferred diagnostic layers are closed.
