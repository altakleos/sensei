---
feature: verify-bundle-completeness
serves: docs/specs/release-process.md
design: "Follows ADR-0004 — bundle integrity is a release-gate property; no new mechanism, single-file enumeration change."
status: done
date: 2026-04-25
---
# Plan: `sensei verify` Bundle Completeness

`sensei verify`'s hardcoded `expected` list at `src/sensei/cli.py:416-437` checks 8 of 15 protocol files, 5 of 14 helper scripts, and 2 of 4 schemas. A maintainer could delete `protocols/tutor.md`, `protocols/hints.md`, `scripts/review_scheduler.py`, or `schemas/goal.schema.json` and `verify` would still report OK — defeating the release-gate purpose.

The fix replaces the hardcoded list with a small **manifest file** shipped inside the engine bundle. Manifest enumeration (rather than wildcard scan-the-target) keeps the contract explicit and detectable: a missing entry in either the manifest or the filesystem becomes a verify failure.

## Tasks

- [x] T1: Add `src/sensei/engine/manifest.yaml` enumerating every required bundle file. Format:
  ```yaml
  schema_version: 1
  required:
    - engine.md
    - defaults.yaml
    - protocols/...
    - scripts/...
    - schemas/...
    - templates/AGENTS.md
  ```
  Source the list by running `fd -t f . src/sensei/engine/` and excluding only `__pycache__/`, `__init__.py` (Python packaging artefact, not a runtime asset), `*/README.md` (developer docs, not engine code), `run.sh` (renamed to `run` at install time and tested separately).
- [x] T2: `src/sensei/cli.py` — replace the hardcoded `expected` block (lines 416-437) with a `_load_manifest(sensei_dir) -> list[str]` helper that reads `.sensei/manifest.yaml` and returns the `required:` list. Preserve `.sensei-version` as a separate runtime-generated check (it isn't shipped in the bundle, so it isn't in the manifest). On `manifest.yaml` parse failure or missing manifest, surface a verify error rather than silently skipping the bundle check.
- [x] T3: `tests/test_cli.py` — add `test_verify_reports_missing_protocol_file_<name>` parametrised over a representative sample (one top-level protocol, one mode protocol, one script, one schema) covering files **not** in the previous hardcoded list, ensuring the new manifest catches them. Also add a test that delete-then-verify catches a missing `manifest.yaml`.
- [x] T4: `tests/ci/test_check_package_contents.py` — extend (or add a sibling test) that asserts every `*.md`/`*.py`/`*.json`/`*.yaml` file under `src/sensei/engine/` (excluding the documented exclusion set) appears in `manifest.yaml`. This is the inverse check: anything that ships must be enumerated. Otherwise contributors can add a new protocol file and forget to register it.
- [x] T5: `src/sensei/engine/templates/AGENTS.md` and the contributor `AGENTS.md` — note the manifest file in the project layout block.
- [x] T6: `CHANGELOG.md` — append under `## [Unreleased]` → `### Fixed`:
  > `sensei verify` now checks the full engine bundle via a shipped manifest. Previous releases checked only a subset of protocols/scripts/schemas; a maintainer-deleted `hints.md`, `tutor.md`, `reviewer.md`, `status.md`, `performance-training.md`, `challenger.md`, or several helper scripts could pass verify silently.

## Acceptance Criteria

- [x] AC1: `sensei verify` reports failure when ANY file under `src/sensei/engine/` (excluding the documented exclusion set) is missing from a freshly-initialised instance. Verified by T3.
- [x] AC2: `sensei verify` reports failure when a new protocol/script/schema is added to the bundle but not registered in `manifest.yaml`. Verified by T4.
- [x] AC3: `sensei verify` continues to report OK on a clean instance (no regression). Verified by existing `test_verify_exits_zero`.
- [x] AC4: `pytest -v && ruff check . && mypy` all pass.

## Out of Scope

- Migrating the manifest to JSON Schema — YAML mapping with a `required:` list is sufficient.
- Auto-generating the manifest from a directory walk at build time — explicit enumeration is the contract; auto-generation reintroduces the silent-add hole.
- Per-file content checksums — bundle integrity (existence) is the v1 goal; tampering detection is out of scope.

