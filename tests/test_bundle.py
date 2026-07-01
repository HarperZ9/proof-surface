"""The portable proof bundle: a content-addressed, re-checkable manifest."""

from __future__ import annotations

import json

from proof_surface.agent_action.cli import main

_AUTH = {
    "authorization_version": "0.1",
    "receipt_id": "auth-1",
    "kind": "authorization-grant",
    "principal": {"id": "user:zain"},
    "agent": {"id": "agent:claude"},
    "intent": "write",
    "scope": {
        "allowed_actions": ["fs.write"],
        "allowed_targets": ["/work/config.json"],
    },
    "granted_at": "2020-01-01T00:00:00+00:00",
    "expires_at": "2999-01-01T00:00:00+00:00",
    "revoked": False,
}
_TRACE = {
    "trace_id": "t1",
    "service": "demo",
    "spans": [
        {
            "span_id": "s2",
            "parent_span_id": None,
            "name": "write",
            "kind": "client",
            "start_unix_ns": 0,
            "end_unix_ns": 1,
            "status": {"code": "ok", "message": ""},
            "attributes": {
                "actor.id": "user:zain",
                "tool.name": "fs",
                "action.kind": "fs.write",
                "action.target": "/work/config.json",
                "side_effect.class": "write",
                "content.sha256": "a" * 64,
                "after.sha256": "c" * 64,
            },
            "events": [],
        }
    ],
}


def _run(tmp_path, out_name):
    trace = tmp_path / "t.json"
    trace.write_text(json.dumps(_TRACE), encoding="utf-8")
    auth = tmp_path / "a.json"
    auth.write_text(json.dumps(_AUTH), encoding="utf-8")
    out = tmp_path / out_name
    rc = main(
        [
            "--trace",
            str(trace),
            "--authorization",
            str(auth),
            "--claim",
            "c",
            "--scope",
            "s",
            "--packet-id",
            "pkt-1",
            "--out",
            str(out),
        ]
    )
    assert rc == 0
    return json.loads((out / "bundle.json").read_text(encoding="utf-8"))


def test_bundle_manifest_lists_every_artifact_with_a_digest(tmp_path):
    bundle = _run(tmp_path, "out")
    assert bundle["domain"] == "agent-action"
    assert bundle["packet_id"] == "pkt-1"
    assert len(bundle["bundle_hash"]) == 64
    names = {f["name"] for f in bundle["files"]}
    assert names >= {
        "packet.json",
        "report.md",
        "crucible-thesis.json",
        "crucible-measurements.json",
    }
    for f in bundle["files"]:
        assert len(f["sha256"]) == 64


def test_bundle_hash_is_deterministic(tmp_path):
    a = _run(tmp_path, "out-a")
    b = _run(tmp_path, "out-b")
    assert a["bundle_hash"] == b["bundle_hash"]
