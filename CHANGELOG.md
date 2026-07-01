# Changelog

## 2026-07-01 - 0.2.0 - Proof-packet wedge family

- Added nine domain proof-packet wedges, each a validator + builder + report +
  CLI sharing one spine (crucible-faithful verdict rule, required decision
  summary, non-promotion boundary, content-addressed bundle, neutrality guards):
  `agent_action`, `visual_measurement`, `research_claim`, `model_eval`,
  `optimization_workflow`, `rollout_receipt`, `eval_attempt`, `ai4science`,
  `conservation`. All route through the unified `telos-proof <domain>` CLI.
- Each wedge enforces a domain honesty gate (no physical-calibration overclaim,
  contamination rejection, dependency-boundary and penalty-surrogate and
  fixture-match-is-not-encoding-soundness checks, reject-unmeasured-discovery,
  a negative fixture that must break, and a sufficient-not-necessary boundary).
- Added `proof_surface.trace_adapters`: OpenTelemetry and LangSmith/Langfuse
  trace normalizers plus evidence importers for MLflow, W&B (artifacts + Weave),
  Braintrust, Arize Phoenix, promptfoo, Helicone, DVC, and SLSA/in-toto, each
  declaring the non-inferable proof-layer gap, with an enforced coverage registry.
- Harvested from the `telos/docs/research/dogfood` program (through pass 0111)
  and the `rl-scaling-receipt-spine` and `mycology-network-intelligence` notes.
- Bumped version to 0.2.0. Base contracts (packets, receipts, gates, ledgers,
  delegation chains, witness receipts) are unchanged and remain the stable core.

## 2026-06-29 - Forward Delivery Contract

- Added `AGENTS.md`, `CHANGELOG.md`, a delivery regression test, and
  `project-docs/specs/SPEC-proof-surface-forward-delivery.md`.
- Updated CI to current Node 24-era GitHub Actions majors for Python setup and
  checkout.
- Added package repository, issues, and homepage metadata.
- Normalized forward-facing punctuation for public-surface scanner
  compatibility.
- Kept schemas, validators, conformance vectors, decision helpers, and verdict
  behavior unchanged.

## Current Status

- Runtime: Python 3.10+ with stdlib-only core validators.
- Surfaces: Python API, JSON schemas, conformance vectors, examples, and usage
  guide.
- Verification: pytest suite plus the root forward delivery contract.
