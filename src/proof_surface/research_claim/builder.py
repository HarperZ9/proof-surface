"""Assemble a research-claim proof packet with a re-derivable verdict.

Each verification check's categorical status maps to a crucible measurement:
pass -> deviation 0 (MATCH), fail -> deviation 1 (DRIFT), unverifiable -> deviation
None (UNVERIFIABLE, fail-closed). A failed or unverifiable run still yields a valid
packet that preserves the sources, attempts, and evidence.
"""

from __future__ import annotations

from typing import Any

from .._decision import derive_decision_summary
from .._verdict import combine_overall, verdict_for_measurement
from .packet import PACKET_VERSION

_TOLERANCE = 0.5


def _check_measurement(status: str) -> tuple[float | None, float]:
    if status == "pass":
        return 0.0, _TOLERANCE
    if status == "fail":
        return 1.0, _TOLERANCE
    return None, _TOLERANCE  # unverifiable / unknown -> fail-closed


def build_research_claim_packet(
    *,
    statement: str,
    sources: list[dict[str, Any]],
    attempts: list[dict[str, Any]],
    checks: list[dict[str, Any]],
    claim: str,
    scope: str,
    packet_id: str,
    uncertainty: list[str] | None = None,
    promotion: str | None = None,
    formal: dict[str, Any] | None = None,
) -> dict[str, Any]:
    per_check: list[dict[str, Any]] = []
    statuses: list[str] = []
    norm_checks: list[dict[str, Any]] = []
    for c in checks:
        deviation, tolerance = _check_measurement(c.get("status", ""))
        status = verdict_for_measurement(deviation, tolerance)
        statuses.append(status)
        per_check.append({"checker": c["checker"], "status": status})
        entry = {
            "checker": c["checker"],
            "status": c["status"],
            "evidence": list(c.get("evidence") or []),
        }
        if c.get("notes"):
            entry["notes"] = c["notes"]
        norm_checks.append(entry)

    overall = combine_overall(statuses)
    resolved_promotion = promotion or (
        "CRUCIBLE_MATCH" if overall == "MATCH" else "UNVERIFIABLE"
    )

    return {
        "version": PACKET_VERSION,
        "packet_id": packet_id,
        "claim": claim,
        "scope": scope,
        "statement": statement,
        "sources": [dict(s) for s in sources],
        "attempts": [dict(a) for a in attempts],
        "checks": norm_checks,
        "verdicts": {"overall": overall, "per_check": per_check},
        "promotion": resolved_promotion,
        "uncertainty": list(uncertainty or []),
        "decision_summary": derive_decision_summary(
            overall,
            missing_evidence=list(uncertainty or [])
            if overall == "UNVERIFIABLE"
            else None,
        ),
        **({"formal": formal} if formal is not None else {}),
    }


def to_crucible_inputs(packet: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Emit crucible's (thesis, measurements) file contract for re-derivation."""
    claims = []
    rows = []
    for c in packet.get("checks", []):
        deviation, tolerance = _check_measurement(c.get("status", ""))
        text = f"The statement holds under the {c['checker']} check."
        claims.append(
            {"text": text, "falsification": "the check status is not 'pass'."}
        )
        rows.append(
            {
                "claim": text,
                "deviation": deviation,
                "tolerance": tolerance,
                "method": c["checker"],
                "evidence": list(c.get("evidence") or []),
            }
        )
    thesis = {
        "title": f"Research-claim proof packet {packet.get('packet_id', '')}",
        "disposition": "publishable",
        "claims": claims,
    }
    return thesis, {"measurements": rows}
