"""Conservation gate: a check must be able to fail on a known-bad input.

Harvest of dogfood passes 0105/0106/0107. The load-bearing honesty rule: a
conservation packet must carry a negative fixture that PROVABLY breaks the
declared invariant (drift beyond tolerance). A "check" whose negative fixture
does not break has no discriminating power -- a verifier that can't fail is not
a verifier.
"""

from __future__ import annotations

from typing import Any

from .._validate import Issue, reject_unknown, require_text

NEGATIVE_FIXTURE_FIELDS = {"description", "drift", "tolerance", "breaks_invariant"}


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_negative_fixture(value: Any, issues: list[Issue]) -> None:
    """A required negative fixture that must genuinely break the invariant."""
    path = "$.negative_fixture"
    if not isinstance(value, dict):
        issues.append(Issue(path, "expected object (a required breaking fixture)"))
        return
    reject_unknown(value, path, NEGATIVE_FIXTURE_FIELDS, issues)
    require_text(value, "description", issues, f"{path}.description")
    drift = value.get("drift")
    tolerance = value.get("tolerance")
    if not _is_number(drift) or drift < 0:
        issues.append(Issue(f"{path}.drift", "expected a non-negative number"))
    if not _is_number(tolerance) or tolerance <= 0:
        issues.append(Issue(f"{path}.tolerance", "expected a number > 0"))
    if value.get("breaks_invariant") is not True:
        issues.append(
            Issue(
                f"{path}.breaks_invariant",
                "expected true -- a conservation check must include a negative fixture "
                "that provably breaks the invariant (else it has no discriminating power)",
            )
        )
    elif _is_number(drift) and _is_number(tolerance) and drift <= tolerance:
        issues.append(
            Issue(
                path,
                "breaks_invariant is true but drift is within tolerance -- the negative "
                "fixture does not actually break the invariant",
            )
        )
