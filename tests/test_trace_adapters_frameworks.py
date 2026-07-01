"""Framework evidence adapters: wrap incumbents, declare the non-inferable gap."""

from __future__ import annotations

from proof_surface.trace_adapters import (
    NON_INFERABLE,
    import_mlflow_run,
    import_slsa_provenance,
    import_wandb_artifact,
)

_HEX = "a" * 64


def test_mlflow_run_yields_sources_and_declares_missing_binding():
    ev = import_mlflow_run(
        {"info": {"run_id": "r1"}, "data": {"metrics": [{"key": "acc", "value": 0.9}]}}
    )
    assert ev["source"] == "mlflow"
    refs = [s["ref"] for s in ev["sources"]]
    assert "mlflow:run:r1" in refs
    assert any("acc" in r for r in refs)
    assert ev["missing_binding"] == NON_INFERABLE
    assert "authority_receipts" in ev["missing_binding"]


def test_wandb_artifact_binds_a_hex_digest():
    ev = import_wandb_artifact({"name": "model", "version": "v3", "digest": _HEX})
    assert ev["sources"][0]["sha256"] == _HEX
    assert ev["missing_binding"] == NON_INFERABLE


def test_slsa_provenance_binds_subject_digests():
    ev = import_slsa_provenance(
        {"subject": [{"name": "artifact.tar", "digest": {"sha256": _HEX}}]}
    )
    assert ev["sources"][0]["ref"] == "slsa:subject:artifact.tar"
    assert ev["sources"][0]["sha256"] == _HEX
    assert ev["missing_binding"] == NON_INFERABLE


def test_missing_binding_names_the_proof_layer_fields():
    # The declared gap is the differentiator: incumbents do not supply these.
    for field in ("authority_receipts", "workspace_state", "verification_verdicts"):
        assert field in NON_INFERABLE
