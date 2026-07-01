"""Multi-branch solver comparison + dependency-boundary honesty.

Harvest of dogfood pass 0094 (consolidated QuantumOptimizationWorkflowReceipt).
Several solver branches are compared against the exact baseline; a branch whose
dependency is missing is marked NOT_EXECUTED_DEPENDENCY_MISSING -- a dependency
boundary, NOT implied coverage. The load-bearing honesty rule: a non-executed
branch may not claim an objective value.
"""

from __future__ import annotations

from typing import Any

from .._validate import Issue, reject_unknown, require_enum, require_text
from .._verdict import verdict_for_measurement

BRANCH_STATUSES = {"COMPLETED", "NOT_RUN", "FAILED", "NOT_EXECUTED_DEPENDENCY_MISSING"}
BASELINE_MATCHES = {"MATCH", "DRIFT", "UNVERIFIABLE"}
BRANCH_FIELDS = {
    "branch_id",
    "method",
    "status",
    "objective_value",
    "notes",
    "baseline_match",
}


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def derive_baseline_match(
    branch: dict[str, Any], baseline: dict[str, Any], tolerance: Any
) -> str:
    """Score a completed branch against the exact baseline; else it claims nothing."""
    if branch.get("status") != "COMPLETED":
        return "UNVERIFIABLE"
    value = branch.get("objective_value")
    baseline_value = (
        baseline.get("objective_value") if isinstance(baseline, dict) else None
    )
    if (
        not _is_number(value)
        or not _is_number(baseline_value)
        or not _is_number(tolerance)
    ):
        return "UNVERIFIABLE"
    return verdict_for_measurement(
        abs(float(value) - float(baseline_value)), float(tolerance)
    )


def validate_solver_branches(
    value: Any, issues: list[Issue], path: str = "$.solver_branches"
) -> None:
    """Validate the optional solver_branches list. Absent or None is valid."""
    if value is None:
        return
    if not isinstance(value, list):
        issues.append(Issue(path, "expected array"))
        return
    for index, item in enumerate(value):
        branch_path = f"{path}[{index}]"
        if not isinstance(item, dict):
            issues.append(Issue(branch_path, "expected object"))
            continue
        reject_unknown(item, branch_path, BRANCH_FIELDS, issues)
        require_text(item, "branch_id", issues, f"{branch_path}.branch_id")
        require_text(item, "method", issues, f"{branch_path}.method")
        require_enum(item, "status", BRANCH_STATUSES, issues, f"{branch_path}.status")
        _validate_value(item, branch_path, issues)
        notes = item.get("notes")
        if notes is not None and (not isinstance(notes, str) or not notes.strip()):
            issues.append(
                Issue(f"{branch_path}.notes", "expected non-empty string or null")
            )
        match = item.get("baseline_match")
        if match is not None and match not in BASELINE_MATCHES:
            issues.append(
                Issue(
                    f"{branch_path}.baseline_match",
                    "expected MATCH / DRIFT / UNVERIFIABLE or null",
                )
            )


def _validate_value(
    item: dict[str, Any], branch_path: str, issues: list[Issue]
) -> None:
    value = item.get("objective_value")
    if item.get("status") == "COMPLETED":
        if not _is_number(value):
            issues.append(
                Issue(
                    f"{branch_path}.objective_value",
                    "a COMPLETED branch must record a numeric objective_value",
                )
            )
    elif value is not None:
        issues.append(
            Issue(
                f"{branch_path}.objective_value",
                "a non-executed branch must not claim a value (dependency boundary, "
                "not implied coverage)",
            )
        )
