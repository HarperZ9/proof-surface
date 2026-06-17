import json
from pathlib import Path

from proof_surface import validate_witness_receipt

CONF = Path(__file__).resolve().parents[1] / "conformance" / "witness-receipt" / "v0.1"


def _valid() -> dict:
    return json.loads((CONF / "valid" / "minimal.receipt.json").read_text(encoding="utf-8"))


def test_valid_receipt_passes():
    assert validate_witness_receipt(_valid()) == []


def test_forbidden_verdict_rejected():
    data = _valid()
    data["verdict"] = "APPROVED"
    assert any(issue.path == "$.verdict" for issue in validate_witness_receipt(data))


def test_authority_token_in_notes_rejected():
    data = _valid()
    data["notes"] = "This artifact is APPROVED for release."
    assert any("authority token" in issue.message for issue in validate_witness_receipt(data))


def test_bad_subject_sha_rejected():
    data = _valid()
    data["subject"][0]["digest"]["sha256"] = "nope"
    assert any(issue.path.endswith("sha256") for issue in validate_witness_receipt(data))


def test_unknown_root_field_rejected():
    data = _valid()
    data["extra"] = 1
    assert validate_witness_receipt(data)


def test_conformance_fixtures_match_manifest():
    manifest = json.loads((CONF / "manifest.json").read_text(encoding="utf-8"))
    for fixture in manifest["fixtures"]:
        data = json.loads((CONF / fixture["path"]).read_text(encoding="utf-8"))
        issues = validate_witness_receipt(data)
        if fixture["expected"] == "valid":
            assert issues == [], f"{fixture['path']} should be valid: {issues}"
        else:
            assert issues, f"{fixture['path']} should be invalid"
