# Cross-mechanism Status Table v0.1

## Big picture

This project has progressed from a single-mechanism SEI-only audit into a mechanism-to-observable fingerprint framework for lithium-ion battery aging diagnostics.

The objective is not simply to check whether a metric changes with degradation. The core question is:

> Which observable features should be used as fitting targets for which aging mechanisms?

This supports an industry-oriented workflow for measurement-based aging-model parameterization and HV battery-system validation.

---

## Cross-mechanism status table

| Mechanism | Main notebooks | Dominant fingerprint | Primary fitting targets | Secondary / auxiliary targets | Rejection / boundary flags | Current status |
|---|---:|---|---|---|---|---|
| SEI-only aging | 20, 21, 22 | Capacity-dominant | Capacity RPT | GITT-like finite-rest voltage; C/25 central-window V(Q) | ICA/DVA features are mostly unsuitable as primary targets; C/25 full-window drift is endpoint-amplified | Closed |
| Contact / ohmic resistance growth | 23 | Ri(t)-dominant | Ri_0.05s, Ri_0.1s, Ri_1s, Ri_10s, recovery-side Ri | Corrected post-ohmic relaxation as invariance audit | Raw recovery amplitude and raw recovery area are ohmic-jump-confounded and should not be used as primary relaxation evidence | Closed |
| NE-LAM | 24 | Capacity-dominant and boundary-sensitive | Capacity RPT | C/25 central-window V(Q); DVA_median central | NE-LAM 10% and 20% show endpoint amplification; NE-LAM 20% should be treated as a stress / boundary case | Closed |
| PE-LAM | 24 | Voltage-shape / DVA-dominant | C/25 central-window V(Q); DVA_median central | Capacity RPT as auxiliary / secondary target | ICA peak features remain mostly smoothing-sensitive; no dominant endpoint amplification observed for PE-LAM in the tested range | Closed |
| Lithium plating entry | 25 | Direct plating-variable observability | Direct plating variables: loss of capacity to plating, plating current density, plated lithium thickness | Matched post-stress discharge capacity | Direct plating-variable peak is not equal to final irreversible capacity loss; matched no-plating controls are mandatory | Entry supported |
| Lithium plating Phase A | 26 | Post-stress direct plating state + matched capacity effect | Direct plating-state variables | Matched capacity effect | Full plating fingerprint not complete; HPPC layer triggered an execution-resource boundary inside Jupyter | Phase A closed |
| Lithium plating HPPC | 26B | Direct plating observable, but HPPC weak | None as primary target under the tested stress range | Ri(t) and corrected relaxation as auxiliary audit descriptors only | Matched Ri(t) delta is near-zero; corrected relaxation response is weak; not resistance-growth-like | Process-isolated audit closed |

---

## Cross-mechanism evidence hierarchy

| Evidence layer | SEI-only | Contact / ohmic resistance | LAM | Lithium plating |
|---|---|---|---|---|
| Capacity RPT | Strong primary target | Weak boundary effect | Strong for NE-LAM; weak to moderate for PE-LAM | Matched effect measurable but small |
| Ri(t) / multi-window resistance | Not primary in the current branch | Strongest primary fingerprint | Not audited in the LAM notebook | Weak / near-zero under the tested plating stress |
| Corrected relaxation | Secondary / weak | Invariant after ohmic correction | Not audited | Weak / near-zero under the tested plating stress |
| C/25 central-window V(Q) | Secondary; moderate | Not a main target | Strong, especially for PE-LAM | Not yet audited after 26B |
| GITT-like finite-rest voltage | Secondary; clean but weak | Not a main target | Not audited in Notebook 24 | Not yet audited |
| ICA/DVA central features | Mostly auxiliary / rejected as primary | Not a main target | DVA central features become candidate targets | Not yet audited |
| Endpoint / boundary behavior | Important confounder | Weak cutoff effect | Strong for high-severity NE-LAM | Important but insufficient alone |
| Direct mechanism variables | SEI state variables available | Imposed contact resistance known | Imposed LAM known | Direct plating variables observable |

---

## Current synthesis

The current mechanism-separation logic is:

```text
SEI-only:
capacity-first

Contact / ohmic resistance:
Ri(t)-first

LAM:
capacity + V(Q) + DVA

Lithium plating:
direct plating variables first;
HPPC weak under the tested range;
full V(Q) / ICA-DVA fingerprint still open
```

Core conclusion:

> Different aging mechanisms should not be interpreted using a single universal aging indicator. SEI-only aging is best represented by Capacity RPT, contact / ohmic resistance by multi-window Ri(t), LAM by voltage-shape and DVA features, and lithium plating by direct plating variables plus matched controls.

---

## Mechanism-specific fitting-target hierarchy

| Mechanism | Best current fitting targets |
|---|---|
| SEI-only aging | Capacity RPT |
| Contact / ohmic resistance growth | Multi-window Ri(t) |
| NE-LAM | Capacity RPT + boundary-controlled V(Q) |
| PE-LAM | C/25 central-window V(Q) + DVA_median central |
| Lithium plating | Direct plating variables + matched capacity audit; HPPC auxiliary only under the tested range |

---

## Feature qualification rules

A diagnostic feature should not be used as primary aging evidence or as a primary fitting target if any of the following apply:

1. Signal-to-smoothing-range ratio < 1.
2. Monotonic fraction across smoothing < 0.75.
3. Signal appears only in the endpoint region.
4. Feature depends strongly on preprocessing, smoothing, interpolation, common-Q selection, or endpoint truncation.
5. Feature is weakly linked to degradation-state variables.
6. Feature is mechanism-non-unique and can be produced by multiple aging pathways.
7. Signal magnitude is below diagnostic-protocol sensitivity.

These rules prevent artifact-driven model fitting and are mandatory for all future mechanism-fingerprint notebooks.

---

## Current rejection boundaries

The following interpretations are not supported:

- ICA/DVA should not be treated as a universal primary aging indicator.
- Endpoint drift should not be directly interpreted as a true mechanism-specific change without boundary control.
- Direct plating-variable peaks should not be equated with final irreversible capacity loss.
- Lithium plating should not be interpreted as resistance-growth-like based on the current HPPC results.
- Weak SEI-only DVA response should not be used to reject DVA as a method in general.
- Raw recovery amplitude in the contact-resistance branch should not be interpreted as slow relaxation growth.

---

## Project-level conclusion

The current project-level conclusions are:

1. SEI-only aging is primarily capacity-driven.
2. Contact / ohmic resistance growth is primarily expressed as a window-invariant Ri(t) shift.
3. LAM, especially PE-LAM, activates voltage-shape and DVA central features.
4. Lithium plating is directly observable through plating-state variables, but HPPC Ri(t) and corrected relaxation remain weak under the tested stress range.
5. Feature qualification rules must remain the basis for all future mechanism-contrast branches.

---

## Recommended next step

The next recommended notebook is:

`27_cross_mechanism_fingerprint_synthesis.ipynb`

Suggested goals:

1. Merge current evidence from SEI-only, contact / ohmic resistance, LAM, and lithium plating.
2. Generate a unified mechanism fingerprint matrix.
3. Mark each observable as primary, secondary, auxiliary, rejected, or deferred.
4. Identify which mechanisms are closed and which require additional diagnostic layers.
5. Produce an industry-neutral portfolio-level summary of the aging-model parameterization framework.
