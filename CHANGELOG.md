# Changelog

## 2026-06-29 - Forward Delivery Contract

- Added `AGENTS.md`, `CHANGELOG.md`, a delivery regression test, and
  `project-docs/specs/SPEC-proof-surface-forward-delivery.md`.
- Updated CI to current Node 24-era GitHub Actions majors for Python setup and
  checkout.
- Added package repository, issues, and homepage metadata.
- Normalized forward-facing punctuation for public-surface scanner
  compatibility.
- Kept schemas, validators, conformance vectors, decision helpers, and verdict
  behavior unchanged.

## Current Status

- Runtime: Python 3.10+ with stdlib-only core validators.
- Surfaces: Python API, JSON schemas, conformance vectors, examples, and usage
  guide.
- Verification: pytest suite plus the root forward delivery contract.
