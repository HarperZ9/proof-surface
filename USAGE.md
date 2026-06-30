# Using proof-surface

A practical guide to the public API. `proof-surface` is a **stdlib-only,
zero-dependency** library: every contract is a plain validator (returns a list
of `Issue`, empty meaning valid) plus, for the active contracts, a decision
helper that returns a closed-lattice verdict. Nothing here grants authority or
is meant to be fed back into a model as trusted state -- these are **verifier
inputs and reviewer-facing outputs**.

> The output blocks below were produced by running the calls against
> `proof_surface` 0.1.0 on CPython 3.12. Treat exact reason strings as
> illustrative -- assert on `decision` / `verdict` / `path`, not on prose.

## Install

From source (no runtime dependencies):

```bash
pip install .
```

Or run straight from a checkout without installing, by putting `src/` on the
path:

```bash
PYTHONPATH=src python your_script.py
```

The test extra pulls in `pytest` and `jsonschema`:

```bash
pip install ".[test]"
pytest
```

## The public surface at a glance

Everything is re-exported from the top-level `proof_surface` package.

| Contract | Validator (`-> list[Issue]`) | Decision / helper |
| --- | --- | --- |
| proof-surface packet | `validate_packet`, `validate_packet_file` | -- |
| work-record receipt | `validate_work_record`, `validate_work_record_file` | -- |
| authorization receipt | `validate_authorization_receipt`, `validate_authorization_receipt_file` | `check_action(receipt, action, target, *, now=None) -> Issue \| None` |
| witness receipt | `validate_witness_receipt`, `validate_witness_receipt_file` | -- |
| pre-execution gate | `validate_gate_request` | `evaluate_gate(request) -> GateDecision` |
| evaluation contract | `validate_evaluation_contract` | `evaluate(contract, results) -> EvalDecision` |
| claim ledger | `validate_claim_ledger` | `confidence_gate`, `find_conflicts`, `trace_dependents` |
| delegation chain | `validate_delegation_chain`, `validate_delegation_chain_file` | `verify_delegation(...) -> DelegationVerdict`; producer helpers `compute_binding`, `compute_chain_binding` |
| organ receipt bundle | `validate_organ_receipt_bundle`, `validate_organ_receipt_bundle_file` | compact interchange over sibling organ receipts |

`Issue` is a frozen dataclass with two fields: `Issue.path` (a JSONPath-ish
string like `"$.scope.allowed_actions"`) and `Issue.message`. **An empty list
means valid.**

```python
from proof_surface import Issue, validate_packet
```

---

## Example 1 -- validate a document

Every validator takes an already-parsed `dict` and returns `list[Issue]`. The
`*_file` variants take a `pathlib.Path`, load the JSON for you, and return the
same shape (a load/parse error comes back as a single `Issue` at `$`).

```python
from proof_surface import validate_claim_ledger

ledger = {
    "ledger_version": "0.1",
    "claims": [
        {
            "claim_id": "c1",
            "statement": "Accuracy on the held-out set is 92.3%.",
            "source": "agent:evaluator-v1",
            "confidence": 0.95,
            "evidence_refs": ["runs/metrics.json"],
            "depends_on": [],
            "conflicts_with": [],
        },
    ],
}

issues = validate_claim_ledger(ledger)
print(issues)
```

Expected output (valid document):

```
[]
```

If you misspell a field or drift past the allowlist, you get a precise path.
For example, adding an unknown top-level key `"foo": 1`:

```
[Issue(path='$.foo', message='unexpected field')]
```

---

## Example 2 -- authorization receipt + `check_action`

`check_action` returns `None` when the action is **allowed**, or an `Issue`
explaining the **denial**. It is default-deny: a structurally invalid receipt, a
revoked grant, an out-of-window timestamp, or an out-of-scope action all deny.
Pass an explicit `now` (an aware `datetime`) for reproducible checks.

```python
from datetime import datetime, timezone
from proof_surface import check_action, validate_authorization_receipt

receipt = {
    "authorization_version": "0.1",
    "receipt_id": "ar-demo",
    "kind": "authorization-grant",
    "principal": {"id": "user:alice@example.com", "role": "project-owner"},
    "agent": {"id": "agent:planner"},
    "intent": "Read repository files.",
    "scope": {
        "allowed_actions": ["read_file"],
        "allowed_targets": ["repo:proof-surface"],
    },
    "granted_at": "2026-06-17T00:00:00Z",
    "expires_at": "2026-06-19T00:00:00Z",
    "revoked": False,
}

now = datetime(2026, 6, 18, tzinfo=timezone.utc)

print(validate_authorization_receipt(receipt))
print(check_action(receipt, "read_file", "repo:proof-surface", now=now))
print(check_action(receipt, "delete_file", "repo:proof-surface", now=now))
```

Expected output:

```
[]
None
Issue(path='$.scope.allowed_actions', message="action denied: 'delete_file' not in allowed_actions")
```

The first line confirms the receipt is structurally valid, the second shows an
allowed action (`None`), and the third shows a denial because `delete_file` is
not in the allowlist.

---

## Example 3 -- pre-execution gate and evaluation contract

Both `evaluate_gate` and `evaluate` return a frozen decision object. The gate is
**default-deny / fail-closed**: `allow` only when every applicable check passes;
any check that cannot be positively confirmed becomes `unknown` and the decision
escalates to `needs-human`.
If a request declares a required `human_gap`, the gate likewise escalates until
external operator attestation, an evidence label, and an evidence digest are
present.

```python
from datetime import datetime, timezone
from proof_surface import evaluate_gate

now = datetime(2026, 6, 18, tzinfo=timezone.utc)
receipt = {
    "authorization_version": "0.1", "receipt_id": "ar-demo",
    "kind": "authorization-grant",
    "principal": {"id": "user:alice@example.com"}, "agent": {"id": "agent:planner"},
    "intent": "Read repository files.",
    "scope": {"allowed_actions": ["read_file"], "allowed_targets": ["repo:proof-surface"]},
    "granted_at": "2026-06-17T00:00:00Z", "expires_at": "2099-01-01T00:00:00Z",
    "revoked": False,
}

request = {
    "planned_action": {
        "action_kind": "read_file",
        "target": "repo:proof-surface",
        "estimated_cost": {"tokens": 100},
    },
    "authorization": receipt,
    "budget": {"remaining_tokens": 1000},
}

decision = evaluate_gate(request)
print(decision.decision, decision.checks)

# Drop the budget: estimated tokens with no remaining-budget figure cannot be
# confirmed, so the budget check is "unknown" and the gate escalates.
request_no_budget = {**request, "budget": {}}
print(evaluate_gate(request_no_budget).decision)
```

Expected output:

```
allow {'authorization': 'pass', 'budget': 'pass', 'state': 'not-applicable', 'human_gap': 'not-applicable'}
needs-human
```

The evaluation contract works the same way, but the decision lattice is
`deploy` / `block` / `needs-human`, and it is **uncertainty-aware**: a measured
value whose `± uncertainty` interval straddles the threshold is `uncertain` and
never silently deploys.

```python
from proof_surface import evaluate

contract = {
    "eval_version": "0.1",
    "contract_id": "ec-demo",
    "objective": "Gate deploy on accuracy and latency.",
    "criteria": [
        {"name": "accuracy", "metric": "accuracy_pct",
         "threshold": 90.0, "direction": ">=", "required": True},
        {"name": "p99_latency_ms", "metric": "p99_latency_ms",
         "threshold": 500.0, "direction": "<=", "required": True},
    ],
}

clear = [
    {"name": "accuracy", "measured": 92.3, "uncertainty": 0.5},
    {"name": "p99_latency_ms", "measured": 480.0, "uncertainty": 5.0},
]
print(evaluate(contract, clear).decision)

straddle = [
    {"name": "accuracy", "measured": 90.2, "uncertainty": 1.0},  # 89.2..91.2 straddles 90
    {"name": "p99_latency_ms", "measured": 480.0},
]
result = evaluate(contract, straddle)
print(result.decision, result.per_criterion)
```

Expected output:

```
deploy
needs-human {'accuracy': 'uncertain', 'p99_latency_ms': 'pass'}
```

---

## Example 4 -- delegation chain (build, validate, verify)

A delegation chain roots authority in a **real human** and attenuates scope down
every hop. Bindings are SHA-256 hash-chains; build them with the producer
helpers `compute_binding` (per hop) and `compute_chain_binding` (whole-chain
commitment), then `verify_delegation` re-derives them. The verdict lattice is
`VALID` / `DENIED` / `UNVERIFIABLE`; `effective_scope` and `effective_expiry`
are populated **only** on `VALID`.

```python
from datetime import datetime, timezone
from proof_surface import (
    compute_binding, compute_chain_binding,
    validate_delegation_chain, verify_delegation,
)

hop = {
    "from": {"id": "alice@example.com", "kind": "human"},
    "to": {"id": "agent:planner", "kind": "agent"},
    "scope": {
        "allowed_actions": ["read", "summarize"],
        "allowed_targets": ["repo:proof-surface"],
    },
    "granted_at": "2026-01-01T00:00:00Z",
    "expires_at": "2099-01-01T00:00:00Z",
    "revoked": False,
}
# The binding is computed over the hop WITHOUT its own "binding" key; the root
# hop uses prev_binding="".
hop["binding"] = compute_binding(hop, "")

chain = {
    "delegation_version": "0.1",
    "chain_id": "chain-demo",
    "hops": [hop],
    "chain_binding": compute_chain_binding("chain-demo", 1, hop["binding"]),
}

now = datetime(2026, 6, 18, tzinfo=timezone.utc)
print(validate_delegation_chain(chain))

ok = verify_delegation(chain, action="read", target="repo:proof-surface", now=now)
print(ok.verdict, ok.effective_scope)

bad = verify_delegation(chain, action="delete", target="repo:proof-surface", now=now)
print(bad.verdict)

# Demanding asymmetric-signature assurance with no verifier is honestly
# UNVERIFIABLE -- never a fabricated VALID.
print(verify_delegation(chain, require_signatures=True, now=now).verdict)
```

Expected output:

```
[]
VALID {'allowed_actions': ['read', 'summarize'], 'allowed_targets': ['repo:proof-surface'], 'any_target': False}
DENIED
UNVERIFIABLE
```

> **Integrity caveat (verbatim from the module).** The per-hop `binding` and the
> `chain_binding` are *keyless* SHA-256 hashes: they give self-consistent
> integrity and catch partial corruption and naive truncation/extension, but
> they are **not** tamper-evidence against an adversary who rewrites the whole
> document and recomputes every binding. For real anti-forgery, pin the
> out-of-band `chain_binding` via `pinned_chain_binding`, or verify an
> asymmetric signature per hop via `require_signatures=True` +
> `signature_verifier`.

---

## Conformance vectors

Each contract ships valid and invalid fixtures under
`conformance/<contract>/v0.1/` with a `manifest.json`. They are the canonical
"what a good/bad document looks like" reference and are exercised by the test
suite; read them alongside this guide when you need a concrete shape.
