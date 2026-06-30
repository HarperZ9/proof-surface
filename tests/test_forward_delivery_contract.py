from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SECRET_ASSIGNMENT = re.compile(
    r"""
    (?<![A-Za-z0-9_])
    ["']?
    (?P<name>
        api[_-]?key|
        api[_-]?token|
        access[_-]?token|
        auth[_-]?token|
        client[_-]?secret|
        password|
        passwd|
        secret|
        token
    )
    ["']?
    \s*(?:=|:)\s*
    ["']?
    (?P<value>[A-Za-z0-9][A-Za-z0-9._~+/=-]{15,})
    ["']?
    """,
    re.IGNORECASE | re.VERBOSE,
)
PLACEHOLDER_TERMS = ("placeholder", "example", "sample", "dummy", "redacted", "<")


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_public_and_developer_delivery_files_exist() -> None:
    required = [
        "README.md",
        "USAGE.md",
        "CHANGELOG.md",
        "AUTHORS.md",
        "CONTRIBUTING.md",
        "LICENSE",
        "AGENTS.md",
        ".github/FUNDING.yml",
        ".github/workflows/ci.yml",
        "docs/brand/proof-surface-hero.png",
        "project-docs/specs/SPEC-proof-surface-forward-delivery.md",
    ]

    assert [path for path in required if not (ROOT / path).is_file()] == []


def test_readme_serves_public_and_developer_audiences() -> None:
    text = read("README.md")

    for heading in ["## Try it", "## Why it matters", "## For developers"]:
        assert heading in text
    assert "docs/brand/proof-surface-hero.png" in text
    assert "validate evidence packets" in text.lower()
    assert "USAGE.md" in text
    assert "CHANGELOG.md" in text
    assert 'python -m pip install -e ".[test]"' in text
    assert "python -m pytest" in text


def test_changelog_records_current_delivery_status() -> None:
    text = read("CHANGELOG.md")

    assert "Forward Delivery Contract" in text
    assert "SPEC-proof-surface-forward-delivery.md" in text
    assert "validators" in text


def test_docs_do_not_use_credential_shaped_assignments() -> None:
    docs = ["README.md", "USAGE.md", "CHANGELOG.md", "AGENTS.md"]
    findings: list[str] = []

    for path in docs:
        text = read(path)
        for match in SECRET_ASSIGNMENT.finditer(text):
            value = match.group("value").lower()
            if not any(term in value for term in PLACEHOLDER_TERMS):
                line = text[: match.start()].count("\n") + 1
                findings.append(f"{path}:{line}")

    assert findings == []
