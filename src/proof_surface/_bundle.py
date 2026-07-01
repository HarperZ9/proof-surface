"""Portable proof bundle: a buyer-inspectable, content-addressed manifest.

After a domain CLI writes its artifacts, ``write_receipts`` scans them, records a
per-file sha256, and emits ``bundle.json`` with a deterministic ``bundle_hash``
over the file digests -- one manifest a reviewer can re-check without trusting the
tool. Stdlib-only.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BUNDLE_SCHEMA = "proof-surface-bundle/v0"
_ARTIFACTS = [
    "packet.json",
    "report.md",
    "crucible-thesis.json",
    "crucible-measurements.json",
]


def write_receipts(out_dir: str | Path, *, domain: str, packet_id: str) -> str:
    """Emit bundle.json manifest over the already-written artifacts; return the hash."""
    out = Path(out_dir)
    files = []
    for name in _ARTIFACTS:
        path = out / name
        if path.exists():
            files.append(
                {"name": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            )
    bundle_hash = hashlib.sha256(
        "".join(f"{f['name']}:{f['sha256']}\n" for f in files).encode("utf-8")
    ).hexdigest()
    bundle = {
        "schema": BUNDLE_SCHEMA,
        "domain": domain,
        "packet_id": packet_id,
        "bundle_hash": bundle_hash,
        "files": files,
    }
    (out / "bundle.json").write_text(
        json.dumps(bundle, indent=2) + "\n", encoding="utf-8"
    )
    return bundle_hash
