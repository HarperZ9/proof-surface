"""Framework evidence adapters: wrap incumbents as evidence inputs.

Each importer maps a framework export (MLflow run, W&B artifact, SLSA / in-toto
provenance, ...) into a common EvidenceImport: the source refs it can attest, and
-- crucially -- an explicit ``missing_binding`` naming the Telos proof-layer fields
that CANNOT be inferred from the raw export (authority, workspace state,
verification verdicts, decision). That declared gap is the answer to "how is this
not <incumbent> with a new UI?". Stdlib-only.
"""

from __future__ import annotations

import re
from typing import Any

_HEX64 = re.compile(r"[0-9a-f]{64}\Z")

# Telos proof-layer fields no runtime/experiment/supply-chain export supplies.
NON_INFERABLE = [
    "authority_receipts",
    "workspace_state",
    "verification_verdicts",
    "decision_summary",
]


def _is_hex64(value: Any) -> bool:
    return isinstance(value, str) and bool(_HEX64.fullmatch(value))


def _evidence_import(
    source: str,
    *,
    evidence_inputs: list[str],
    sources: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "source": source,
        "evidence_inputs": evidence_inputs,
        "sources": sources,
        "missing_binding": list(NON_INFERABLE),
    }


def import_mlflow_run(run: dict[str, Any]) -> dict[str, Any]:
    """MLflow run -> evidence import (params/metrics/tags/artifact_uri)."""
    info = run.get("info", {}) or {}
    data = run.get("data", {}) or {}
    sources = [{"ref": f"mlflow:run:{info.get('run_id', '')}"}]
    for metric in data.get("metrics", []) or []:
        if isinstance(metric, dict):
            sources.append(
                {"ref": f"mlflow:metric:{metric.get('key')}={metric.get('value')}"}
            )
    return _evidence_import(
        "mlflow",
        evidence_inputs=["params", "metrics", "tags", "artifact_uri"],
        sources=sources,
    )


def import_wandb_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    """Weights & Biases artifact -> evidence import (name/version/digest)."""
    source = {"ref": f"wandb:artifact:{artifact.get('name', '')}"}
    digest = artifact.get("digest")
    if _is_hex64(digest):
        source["sha256"] = digest
    return _evidence_import(
        "wandb",
        evidence_inputs=["name", "version", "digest", "metadata"],
        sources=[source],
    )


def import_slsa_provenance(provenance: dict[str, Any]) -> dict[str, Any]:
    """SLSA / in-toto provenance -> evidence import (subjects with digests)."""
    sources = []
    for subject in provenance.get("subject", []) or []:
        if not isinstance(subject, dict):
            continue
        entry = {"ref": f"slsa:subject:{subject.get('name', '')}"}
        sha = (subject.get("digest") or {}).get("sha256")
        if _is_hex64(sha):
            entry["sha256"] = sha
        sources.append(entry)
    return _evidence_import(
        "slsa",
        evidence_inputs=["subject", "predicate.builder", "predicate.buildType"],
        sources=sources,
    )
