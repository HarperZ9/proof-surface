"""Reviewer-facing Markdown report for a competition-attempt proof packet."""

from __future__ import annotations

from typing import Any

from .._boundary import render_boundary
from .._decision import render_decision_summary


def render_report(packet: dict[str, Any]) -> str:
    verdicts = packet.get("verdicts") or {}
    overall = verdicts.get("overall", "UNVERIFIABLE")
    challenge = packet.get("challenge") or {}
    judge_repo = challenge.get("judge_repo") or {}
    attempt = packet.get("attempt") or {}
    extraction = packet.get("answer_extraction") or {}
    calls = attempt.get("external_model_calls")
    lines = [
        f"# Competition-Attempt Proof Packet `{packet.get('packet_id', '')}`",
        "",
        f"**Verdict: {overall}** -- {packet.get('claim', '')}",
        "",
        f"- **Scope:** {packet.get('scope', '')}",
        f"- **Challenge:** {challenge.get('challenge_ref')} "
        f"(stage: {challenge.get('stage')})",
        f"- **Judge repo (source-pinned):** {judge_repo.get('repo_ref')} at "
        f"`{str(judge_repo.get('head_sha'))[:12]}`, "
        f"{judge_repo.get('observed_files')} file(s), files digest "
        f"`{str(judge_repo.get('files_digest'))[:16]}...`",
        f"- **Attempt:** {attempt.get('attempt_id')} on {attempt.get('model_ref')}"
        + (
            f" -- external model calls: {calls}"
            + (
                f" (receipt: {attempt.get('provider_receipt_ref')})"
                if attempt.get("provider_receipt_ref")
                else ""
            )
            if calls is not None
            else " -- hosted-model usage undisclosed"
        ),
        f"- **Answer extraction:** {extraction.get('method')} from "
        f"{extraction.get('extracted_ref')} "
        f"(injection_checked: {extraction.get('injection_checked')})",
        f"- **Cited layers:** "
        f"{', '.join(verdicts.get('cited_layers') or []) or 'none'}",
    ]
    lines.extend(render_decision_summary(packet.get("decision_summary")))
    lines.extend(["", "## Certificate layers", ""])
    lines.append("| Layer | Status | Passing | Evidence / probe |")
    lines.append("| --- | --- | --- | --- |")
    for layer in packet.get("certificate_layers") or []:
        if not isinstance(layer, dict):
            continue
        evidence = layer.get("evidence_ref") or layer.get("probe_evidence") or ""
        passing = layer.get("passing")
        lines.append(
            f"| {layer.get('layer')} | {layer.get('status')} "
            f"| {'-' if passing is None else passing} | {evidence} |"
        )
    lines.extend(
        [
            "",
            "_The verdict may only cite layers that EXECUTED; an "
            "UNAVAILABLE_FENCED layer must cite the probe that proved the "
            "fence, and MATCH is only derivable from an executed, passing "
            "judge verdict._",
        ]
    )
    lines.extend(render_boundary())
    return "\n".join(lines)
