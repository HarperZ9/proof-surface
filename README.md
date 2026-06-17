# proof-surface

The shared, stdlib-only contract family for accountability/provenance tooling.
One source of truth for three small validators that previously lived as
copy-pasted duplicates across several repos.

## Contracts

| Contract | Validator | What it is |
| --- | --- | --- |
| **proof-surface packet** (`v0.1`) | `validate_packet` | A neutral evidence/index packet that producers emit and a proof-index consumes. |
| **work-record receipt** (`v0.1`) | `validate_work_record` | A verifiable record of agent work that flows **outward** for review: the structural inverse of an authorization-suppression "prefire". |
| **witness receipt** | `validate_witness_receipt` | Consumer-side validator that **mirrors** EMET's published witness-receipt shape and closed verdict lattice. |

## Design stance

- **Accountability, not authority.** Every validator rejects authority-shaped
  content. Verdicts are confined to closed lattices; nothing here ever emits
  `TRUSTED`/`APPROVED`/`AUTHORIZED`.
- **The work-record receipt is hard-pinned against drift.** `additionalProperties`
  is false at every level, a recursive guard rejects the prefire capsule/meta
  field names by name (they are neutral-sounding and slip a lexical denylist),
  decision fields are closed enums, and `direction` is fixed to `output-only`:
  a work record is emitted, never read back as inbound model/session state.
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
