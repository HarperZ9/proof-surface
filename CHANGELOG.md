# Changelog

## 2026-07-01 - Flagship receipt kinds on the organ bundle spine

- Extended the closed `RECEIPT_KINDS` set of the `organ-receipt-bundle` contract
  with the five flagship kinds: `crucible-assessment`, `forum-route`,
  `index-context-envelope`, `gather-corpus`, `learn-receipt`. The JSON schema
  enum was updated in lockstep and a test pins the two artifacts together.
- Added a cross-tool conformance test module proving a mixed bundle (one entry
  of every flagship kind plus an existing organ kind, synthetic sha256 digests)
  validates with the stdlib-only validator, and that an entry claiming an
  unknown `receipt_kind` is still rejected: the set is extended, not opened.
- `ORGAN_BUNDLE_VERSION` stays `0.1`; validation behavior for existing kinds is
  unchanged.

## 2026-07-01 - 0.2.0 - Family hardening (post-integration)

- Typed `failure_labels` (the shared `_failure` vocabulary) are now accepted by
  ALL nine wedges, not just `agent_action`, per the rl-scaling receipt-spine note.
- `research_claim` gained a first-class `REFUTED` promotion rung and a refutation
  gate: a standing counterexample (a `refuted` attempt or `formal.counterexample_found`)
  forces `REFUTED` and outranks passing checks; a PASSED kernel replay with
  unresolved `sorry` holes is rejected.
- `eval_attempt` gained an auditability gate: a `correct` outcome with a latent
  (unavailable) reasoning trace and no `replay_ref` has no audit surface and is
  not scored `MATCH`.
- `_compute_lease` was promoted to the shared spine and wired onto `rollout_receipt`
  (paid GPU / cluster compute as an accountable external write); rollout now also
  enforces `$.verdicts.overall == $.verifier.verdict`.
- The negative-fixture conformance gate ("a verifier that cannot fail is not a
  verifier") now covers all nine wedges.

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
