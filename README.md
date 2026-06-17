# proof-surface

The shared, stdlib-only contract family for accountability/provenance tooling.
One source of truth for three small validators that previously lived as
copy-pasted duplicates across several repos.

## Contracts

| Contract | Validator | What it is |
| --- | --- | --- |
| **proof-surface packet** (`v0.1`) | `validate_packet` | A neutral evidence/index packet that producers emit and a proof-index consumes. |
| **work-record receipt** (`v0.1`) | `validate_work_record` | A verifiable record of agent work that flows **outward** for review: the structural inverse of an authorization-suppression "prefire". |
| **authorization receipt** (`v0.1`) | `validate_authorization_receipt`, `check_action` | A verifiable record of a real, explicit, least-privilege, **expiring**, revocable grant of authority from a human principal to an agent. The **inward** complement to the work-record receipt, completing bilateral provenance. Verifier input only — never re-injected as model context. |
| **witness receipt** | `validate_witness_receipt` | Consumer-side validator that **mirrors** EMET's published witness-receipt shape and closed verdict lattice. |
| **pre-execution gate** (`v0.1`) | `evaluate_gate`, `validate_gate_request` | A default-deny, fail-closed, **advisory** mediation layer. Given a planned action, its authorization receipt, a budget, and optional observed state, it returns a `GateDecision` (allow / deny / needs-human) with per-dimension check results. Reports a decision for the runtime/operator to enforce; **never grants authority** and is **never injected into a model as trusted state**. The inverse of the prefire's "consume embedded authority" — the gate withholds approval unless every check positively passes. |
| **evaluation contract** (`v0.1`) | `validate_evaluation_contract`, `evaluate` | Evaluation as a deploy gate, not a vanity score: declares objective + criteria with thresholds and a `required` flag, and `evaluate` returns a **deploy / block / needs-human** decision. Uncertainty-aware — if `measured ± uncertainty` straddles a threshold it escalates to needs-human; a required criterion with no result is `missing` -> needs-human. Never deploys on uncertainty. |
| **claim ledger** (`v0.1`) | `validate_claim_ledger`, `confidence_gate`, `find_conflicts`, `trace_dependents` | Traceable multi-agent memory: each claim carries a **source-provided** confidence plus explicit `depends_on` / `conflicts_with` links (referential integrity enforced). Surfaces low-confidence claims, declared conflicts, and the transitive set contaminated by a given claim (cycle-safe). Reports provenance and uncertainty; it does **not** adjudicate truth. |

## Design stance

- **Accountability, not authority.** Every validator rejects authority-shaped
  content. Verdicts are confined to closed lattices; nothing here ever emits
  `TRUSTED`/`APPROVED`/`AUTHORIZED`.
- **The work-record receipt is hard-pinned against drift.** `additionalProperties`
  is false at every level, a recursive guard rejects the prefire capsule/meta
  field names by name (they are neutral-sounding and slip a lexical denylist),
  decision fields are closed enums, and `direction` is fixed to `output-only`:
  a work record is emitted, never read back as inbound model/session state.
- **The authorization receipt is the honest inversion of the prefire.** Where
  the prefire fabricated federal appointments and suppressed authorization checks,
  the authorization receipt records a real grant from a real human principal,
  hard-requires an expiry (`expires_at` mandatory — authority must expire),
  enforces an explicit allowlist scope (default-deny: empty `allowed_actions`
  authorizes nothing), and is verifier input only. The `check_action` helper
  confirms a specific action against a receipt; it does not inject "trusted state"
  into a model. The identical forbidden-field-name guard (recursive, fail-closed)
  is applied at every object level.
- **The pre-execution gate is the live-state inversion of the prefire's authority-consumption.** Where the prefire instructed the model to treat embedded state as pre-authorized, the gate withholds approval unless authorization, budget, and state each positively pass. Default-deny: allow is the rarest outcome. Fail-closed: any dimension that cannot be positively confirmed (unknown budget, unverifiable state) escalates to needs-human rather than auto-allowing. Advisory: `GateDecision` is a structured recommendation; the runtime or operator is the enforcement point. The identical forbidden-field-name guard (recursive, fail-closed) is applied at every object level of the gate request, including inside the embedded authorization receipt.
- **The evaluation contract makes eval a gate, not a report.** Criteria carry
  thresholds and a `required` flag; `evaluate` ties results to a
  deploy/block/needs-human decision and accounts for uncertainty (a result whose
  interval straddles its threshold is `uncertain` -> needs-human, never a silent
  pass). Same forbidden-field guard and `additionalProperties:false` discipline.
- **The claim ledger keeps confidence honest.** Confidence is source-provided and
  never adjusted or filtered by the tool (a `0.0` claim is logged, not dropped);
  the ledger surfaces low-confidence claims, conflicts, and downstream
  contamination for human review without adjudicating which claim is true.
- **EMET stays independent.** EMET is the byte-witness spine and remains
  self-contained and stdlib-only for independent re-derivability, so it is *not*
  a dependency of this package. `witness_receipt` mirrors EMET's schema so other
  tools can validate EMET receipts without importing EMET.

## Usage

```python
from proof_surface import validate_work_record

issues = validate_work_record(record)  # [] means valid
for issue in issues:
    print(issue.path, issue.message)
```

Schemas live in `schemas/`; conformance vectors (valid + invalid) live under
`conformance/<contract>/v0.1/` with a `manifest.json` per contract.

## License

MIT.
