"""Tests for the authorization-receipt contract.

Mirrors the style of test_work_record.py exactly.  Every assertion is
meaningful; no "it didn't crash" tests.

Contract invariants exercised here:
  * Forbidden-field guard -- recursive, fail-closed, same set as work-record.
  * Required expiry -- expires_at is mandatory; authority must expire.
  * Default-deny scope -- empty allowed_actions authorizes nothing.
  * check_action helper -- out-of-scope denied, in-scope allowed, revoked denied,
    expired denied.
  * additionalProperties:false at root and every nested object.
  * Conformance manifest -- every fixture must match its declared expected result.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from proof_surface import authorization_receipt as ar
from proof_surface import validate_authorization_receipt

CONF = Path(__file__).resolve().parents[1] / "conformance" / "authorization-receipt" / "v0.1"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _valid() -> dict:
    return json.loads((CONF / "valid" / "minimal.receipt.json").read_text(encoding="utf-8"))


def _now_str(offset_seconds: int = 0) -> str:
    dt = datetime.now(tz=timezone.utc) + timedelta(seconds=offset_seconds)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _receipt(
    *,
    actions: list[str] | None = None,
    targets: list[str] | None = None,
    revoked: bool = False,
    granted_offset: int = -3600,
    expires_offset: int = 3600,
) -> dict:
    """Build a minimal syntactically valid receipt for check_action tests."""
    return {
        "authorization_version": "0.1",
        "receipt_id": "ar-test-fixture",
        "kind": "authorization-grant",
        "principal": {"id": "user:alice@example.com"},
        "agent": {"id": "agent:test"},
        "intent": "Test fixture for check_action.",
        "scope": {
            "allowed_actions": actions if actions is not None else ["read_file"],
            "allowed_targets": targets if targets is not None else [],
        },
        "granted_at": _now_str(granted_offset),
        "expires_at": _now_str(expires_offset),
        "revoked": revoked,
    }


# ---------------------------------------------------------------------------
# Structural validation -- happy path
# ---------------------------------------------------------------------------


def test_minimal_valid_receipt_passes():
    assert validate_authorization_receipt(_valid()) == []


# ---------------------------------------------------------------------------
# Forbidden-field guard
# ---------------------------------------------------------------------------


def test_forbidden_field_rejected_at_root():
    data = _valid()
    data["federal_appointment"] = {"state": "embedded"}
    issues = validate_authorization_receipt(data)
    assert any("forbidden" in i.message for i in issues)


def test_every_prefire_key_is_forbidden():
    for key in ar.FORBIDDEN_FIELDS:
        data = _valid()
        data[key] = "x"
        issues = validate_authorization_receipt(data)
        assert any(
            i.path == f"$.{key}" and "forbidden" in i.message for i in issues
        ), f"key {key!r} not blocked"


def test_forbidden_field_rejected_when_nested_in_scope():
    data = _valid()
    data["scope"]["authorization_context_mode"] = "consume_verified_native_state"
    issues = validate_authorization_receipt(data)
    assert any(
        i.path.endswith("authorization_context_mode") and "forbidden" in i.message
        for i in issues
    )


def test_forbidden_field_rejected_when_nested_in_principal():
    data = _valid()
    data["principal"]["prefire"] = True
    issues = validate_authorization_receipt(data)
    assert any(
        i.path.endswith("prefire") and "forbidden" in i.message for i in issues
    )


# ---------------------------------------------------------------------------
# Required-expiry enforcement
# ---------------------------------------------------------------------------


def test_missing_expires_at_rejected():
    data = _valid()
    del data["expires_at"]
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.expires_at" for i in issues)


def test_expires_at_before_granted_at_rejected():
    data = _valid()
    data["granted_at"] = "2026-06-17T10:00:00Z"
    data["expires_at"] = "2026-06-17T09:00:00Z"
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.expires_at" for i in issues)


def test_expires_at_equal_to_granted_at_rejected():
    data = _valid()
    data["granted_at"] = "2026-06-17T10:00:00Z"
    data["expires_at"] = "2026-06-17T10:00:00Z"
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.expires_at" for i in issues)


def test_expires_at_without_timezone_rejected():
    data = _valid()
    data["expires_at"] = "2026-06-17T23:59:59"
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.expires_at" for i in issues)


# ---------------------------------------------------------------------------
# additionalProperties:false enforcement
# ---------------------------------------------------------------------------


def test_unknown_root_field_rejected():
    data = _valid()
    data["extra_authority"] = "full_access"
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.extra_authority" for i in issues)


def test_unknown_scope_field_rejected():
    data = _valid()
    data["scope"]["wildcard"] = "*"
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.scope.wildcard" for i in issues)


def test_unknown_principal_field_rejected():
    data = _valid()
    data["principal"]["clearance_level"] = "top_secret"
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.principal.clearance_level" for i in issues)


def test_unknown_agent_field_rejected():
    data = _valid()
    data["agent"]["trusted"] = True
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.agent.trusted" for i in issues)


# ---------------------------------------------------------------------------
# Scope shape -- default-deny
# ---------------------------------------------------------------------------


def test_scope_allowed_actions_must_be_array():
    data = _valid()
    data["scope"]["allowed_actions"] = "read_file"
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.scope.allowed_actions" for i in issues)


def test_scope_allowed_targets_must_be_array():
    data = _valid()
    data["scope"]["allowed_targets"] = "any"
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.scope.allowed_targets" for i in issues)


def test_scope_max_actions_must_be_non_negative():
    data = _valid()
    data["scope"]["max_actions"] = -1
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.scope.max_actions" for i in issues)


def test_scope_max_actions_bool_rejected():
    data = _valid()
    data["scope"]["max_actions"] = True
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.scope.max_actions" for i in issues)


# ---------------------------------------------------------------------------
# Required-field checks
# ---------------------------------------------------------------------------


def test_missing_principal_id_rejected():
    data = _valid()
    del data["principal"]["id"]
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.principal.id" for i in issues)


def test_empty_principal_id_rejected():
    data = _valid()
    data["principal"]["id"] = "   "
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.principal.id" for i in issues)


def test_missing_agent_id_rejected():
    data = _valid()
    del data["agent"]["id"]
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.agent.id" for i in issues)


def test_missing_intent_rejected():
    data = _valid()
    del data["intent"]
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.intent" for i in issues)


def test_revoked_must_be_bool():
    data = _valid()
    data["revoked"] = "no"
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.revoked" for i in issues)


def test_kind_must_be_authorization_grant():
    data = _valid()
    data["kind"] = "authorization-suppression"
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.kind" for i in issues)


def test_authorization_version_const():
    data = _valid()
    data["authorization_version"] = "2.0"
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.authorization_version" for i in issues)


def test_notes_must_be_string_when_present():
    data = _valid()
    data["notes"] = 42
    issues = validate_authorization_receipt(data)
    assert any(i.path == "$.notes" for i in issues)


# ---------------------------------------------------------------------------
# check_action -- default-deny and positive-allow
# ---------------------------------------------------------------------------


def test_check_action_in_scope_allowed():
    receipt = _receipt(actions=["read_file"], targets=[])
    result = ar.check_action(receipt, "read_file", "some/path.txt")
    assert result is None, f"expected None (allowed), got {result}"


def test_check_action_out_of_scope_denied():
    receipt = _receipt(actions=["read_file"], targets=[])
    result = ar.check_action(receipt, "write_file", "some/path.txt")
    assert result is not None
    assert "not in allowed_actions" in result.message


def test_check_action_target_restricted_allowed():
    receipt = _receipt(actions=["read_file"], targets=["C:/dev/public/proof-surface/conformance/"])
    result = ar.check_action(receipt, "read_file", "C:/dev/public/proof-surface/conformance/")
    assert result is None


def test_check_action_target_restricted_denied():
    receipt = _receipt(actions=["read_file"], targets=["C:/dev/public/proof-surface/conformance/"])
    result = ar.check_action(receipt, "read_file", "C:/dev/secret/")
    assert result is not None
    assert "not in allowed_targets" in result.message


def test_check_action_empty_allowed_actions_denies_everything():
    receipt = _receipt(actions=[], targets=[])
    result = ar.check_action(receipt, "read_file", "any/path")
    assert result is not None
    assert "no actions" in result.message or "default-deny" in result.message


def test_check_action_revoked_denies():
    receipt = _receipt(revoked=True)
    result = ar.check_action(receipt, "read_file", "any/path")
    assert result is not None
    assert "revoked" in result.message


def test_check_action_expired_denies():
    receipt = _receipt(granted_offset=-7200, expires_offset=-3600)
    result = ar.check_action(receipt, "read_file", "any/path")
    assert result is not None
    assert "expired" in result.message


def test_check_action_not_yet_active_denies():
    receipt = _receipt(granted_offset=3600, expires_offset=7200)
    result = ar.check_action(receipt, "read_file", "any/path")
    assert result is not None
    assert "not yet" in result.message


def test_check_action_invalid_receipt_denies():
    receipt = {"authorization_version": "0.1"}  # structurally broken
    result = ar.check_action(receipt, "read_file", "any/path")
    assert result is not None
    assert "invalid" in result.message


# ---------------------------------------------------------------------------
# Conformance manifest
# ---------------------------------------------------------------------------


def test_conformance_fixtures_match_manifest():
    manifest = json.loads((CONF / "manifest.json").read_text(encoding="utf-8"))
    for fixture in manifest["fixtures"]:
        data = json.loads((CONF / fixture["path"]).read_text(encoding="utf-8"))
        issues = validate_authorization_receipt(data)
        if fixture["expected"] == "valid":
            assert issues == [], f"{fixture['path']} should be valid: {issues}"
        else:
            assert issues, f"{fixture['path']} should be invalid but got no issues"
