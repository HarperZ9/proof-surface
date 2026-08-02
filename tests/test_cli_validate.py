from __future__ import annotations

import json
from pathlib import Path

from proof_surface.cli import main


ROOT = Path(__file__).resolve().parents[1]


def test_validate_cli_accepts_tadr_bundle(capsys) -> None:
    path = (
        ROOT
        / "conformance"
        / "organ-receipt-bundle"
        / "v0.1"
        / "valid"
        / "tadr-kinds.bundle.json"
    )

    assert main(["validate", str(path)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["verdict"] == "MATCH"
    assert result["contract"] == "organ-receipt-bundle/v0.1"


def test_validate_cli_rejects_zero_digest(capsys) -> None:
    path = (
        ROOT
        / "conformance"
        / "organ-receipt-bundle"
        / "v0.1"
        / "invalid"
        / "tadr-zero-digest.bundle.json"
    )

    assert main(["validate", str(path)]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["verdict"] == "UNVERIFIABLE"
    assert result["issues"][0]["path"] == "$.entries[0].payload_sha256"


def test_validate_cli_accepts_authorization_v0_2(capsys) -> None:
    path = (
        ROOT
        / "conformance"
        / "authorization-receipt"
        / "v0.2"
        / "valid"
        / "minimal.receipt.json"
    )

    assert main(["validate", str(path)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["verdict"] == "MATCH"
    assert result["contract"] == "authorization-receipt/v0.2"


def test_validate_cli_fails_closed_on_unknown_contract(tmp_path, capsys) -> None:
    path = tmp_path / "unknown.json"
    path.write_text('{"schema":"unknown/v1"}', encoding="utf-8")

    assert main(["validate", str(path)]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["verdict"] == "UNVERIFIABLE"
    assert result["reason"] == "unknown_contract"
