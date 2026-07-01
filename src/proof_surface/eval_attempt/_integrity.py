"""Eval integrity: a benchmark result is meaningless if the answer leaked.

Harvest of dogfood pass 0085 (arc_agi eval cluster). The load-bearing honesty
gate: a `correct` outcome is contamination, not a pass, when the attempt had
ground-truth access. The same no-overreach-without-disclosure family as the
visual calibration boundary and the optimization dependency boundary.
"""

from __future__ import annotations

from typing import Any

from .._validate import Issue


def validate_integrity(result: Any, boundaries: Any, issues: list[Issue]) -> None:
    outcome = result.get("outcome") if isinstance(result, dict) else None
    had_ground_truth = (
        boundaries.get("had_ground_truth") if isinstance(boundaries, dict) else None
    )
    if outcome == "correct" and had_ground_truth is True:
        issues.append(
            Issue(
                "$.boundaries",
                "a 'correct' outcome is contamination, not a pass, when the attempt "
                "had ground-truth access (had_ground_truth=true)",
            )
        )
