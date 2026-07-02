# control-certificate -- wedge #10

A **stability/feasibility-claim -> proof packet**. Grounded in dogfood passes
0112 (Lyapunov stability certificate) and 0113 (constrained-MPC feasibility),
scoped in by the operator's robotics and cybernetics lane. Cybernetics is the
program's thesis in feedback-loop vocabulary; this wedge makes the loop's
central promise -- "this controller is stable" -- carry re-checkable proof.

A `system` (plant + regime) claims a declared `certificate` (`lyapunov`,
`ranking-function`, `contraction-metric`, or `mpc-feasibility`), proven by
witnessed `conditions` (each a real residual within tolerance) **and**
falsified by a required `negative_fixture` that **must violate** the
certificate.

## The load-bearing gates

`_gates.py` enforces three rules:

1. The `negative_fixture` provably violates the certificate
   (`violates_certificate == true` **and** `residual > tolerance`). A
   stability "check" that cannot fail on a known-unstable system has no
   discriminating power -- **a verifier that cannot fail on a known-bad input
   is not a verifier.**
2. **Kind completeness**: a certificate kind must witness all of its defining
   conditions (`lyapunov` needs `positive-definite` + `decrease`;
   `mpc-feasibility` needs `recursive-feasibility` + `constraint-satisfaction`;
   `ranking-function` needs `well-founded` + `decrease`; `contraction-metric`
   needs `contraction`). A kind without its conditions witnessed is an
   assertion, not a certificate.
3. **Sim-to-real boundary**: `hardware_validity_claim` requires a hardware (or
   hybrid) regime AND hardware evidence references. Verified in simulation is
   never presented as verified on hardware.

The verdict is `MATCH` iff every witnessed condition holds within tolerance,
`DRIFT` if any fails, `UNVERIFIABLE` if nothing was witnessed.

Decrease is not constancy: a conserved quantity belongs to the `conservation`
wedge (#9); this wedge covers directional conditions (a potential strictly
decreases, a feasible set stays reachable). Domain-general: controller
stability, program termination via ranking functions, iterative-solver
convergence, MPC feasibility.

## Use

```bash
telos-proof control-certificate --input claim.json --claim "..." --scope "..." --out ./artifacts
# or: python -m proof_surface.control_certificate --input claim.json ...
```

`claim.json`: `{sources, system, certificate, witnesses, negative_fixture,
sim_to_real[, uncertainty]}`. Emits `packet.json`, `report.md`, crucible
`thesis`/`measurements`, an optional peer assessment, and a content-addressed
`bundle.json`.
