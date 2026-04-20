---
feature: release-workflow
serves: docs/specs/release-process.md
design: docs/design/release-workflow.md
status: planned
date: 2026-04-20
---
# Plan: Release Workflow

Implements the `release-process` spec via the mechanism in `design/release-workflow.md`. Lands the infrastructure for publishing Sensei to PyPI; does not cut an actual release (the first real release earns its own plan).

## Tasks

### Phase 1 — Implementation

- [x] T1: Write `ci/check_package_contents.py` — wheel validator. Checks required files, required directories, forbidden path prefixes, and version concordance between `sensei/__init__.py` and the supplied `--tag`. Exit codes 0/1/2/3 per design. Single JSON report to stdout. → `ci/check_package_contents.py`
- [x] T2: Unit tests for T1 using synthetic wheel fixtures built on-the-fly — happy path, each missing-required-file case (parameterized), each forbidden-path case, version-mismatch case (34 tests) → `tests/ci/test_check_package_contents.py`
- [x] T3: Write `.github/workflows/release.yml` — three jobs (`verify` matrix, `build-and-check`, `publish`). Tag trigger per design. `pypi` environment on the publish job with `id-token: write`. `pypa/gh-action-pypi-publish` action → `.github/workflows/release.yml`
- [x] T4: Remove the aspirational preamble from `docs/operations/release-playbook.md`; add cross-links to the new spec, design, and ADR-0009; update the `check-package-contents.py` path reference from `src/sensei/engine/scripts/` to `ci/` → `docs/operations/release-playbook.md`

### Phase 2 — Verify

- [x] T5: Unit tests from T2 pass locally (34 new tests; suite 85/85).
- [x] T6: `pytest` full suite green including the new CI-validator tests.
- [x] T7: Local wheel build + smoke-check — `python -m build` clean (no duplicate-name warnings), `python ci/check_package_contents.py --wheel dist/*.whl --tag v0.0.0` returns status `ok`. Also dropped the redundant `[tool.hatch.build.targets.wheel.force-include]` from `pyproject.toml` that had been causing the warnings.
- [x] T8: End-to-end exercise — first real tag `v0.1.0a1` pushed. First publish attempt failed with `invalid-publisher` (PyPI pending-publisher not yet registered); after registering, `gh run rerun --failed` succeeded on second approval. Release live at https://pypi.org/project/sensei-tutor/0.1.0a1/ and https://github.com/altakleos/sensei/releases/tag/v0.1.0a1. Clean-venv `pip install sensei-tutor==0.1.0a1 --pre` + `sensei init` verified the published wheel scaffolds correctly and the seeded profile validates.

## Acceptance Criteria

- [ ] AC1: `ci/check_package_contents.py` handles all four documented exit conditions with unit tests for each.
- [ ] AC2: `tests/ci/test_check_package_contents.py` exercises happy path, every missing-required-file variant, every forbidden-path variant, and the version-mismatch case against synthetic wheels built in the test.
- [ ] AC3: `.github/workflows/release.yml` has exactly three jobs with explicit `needs` dependency; `publish` uses `pypa/gh-action-pypi-publish@release/v1` with `permissions.id-token: write`; references the `pypi` environment.
- [ ] AC4: The tag filter matches every semver and prerelease form listed in the design; does not match arbitrary tags like `release-2026-04`.
- [ ] AC5: `docs/operations/release-playbook.md` no longer contains the aspirational-status preamble. It references the spec, design, and ADR-0009.
- [ ] AC6: `verify.yml` still passes on `main` after this plan lands (no regressions in existing tests).
- [ ] AC7: Suite count grows by at least 6 tests (happy + 3 failure categories × 1+ case each, conservatively).

## Prerequisites (maintainer, outside this plan)

These are the items the maintainer must handle manually on PyPI and GitHub before the first real release can cut. T8 is blocked on all four.

1. Register `sensei-tutor` on PyPI (the first publish can use the trusted-publisher pending-project flow without a pre-existing project). Distribution name per ADR-0010.
2. Configure the PyPI trusted publisher for project `sensei-tutor`: repository `altakleos/sensei`, workflow `release.yml`, environment `pypi`.
3. Create the GitHub Environment `pypi` with a required reviewer and the deployment-tag restriction set to pattern `v*` (NOT a branch rule on `main` — the workflow is triggered by tag push, so the triggering ref is the tag).
4. Capture the environment ID in `docs/operations/release-playbook.md` (currently placeholder `<TBD>`).

## Out of Scope

- Cutting `v0.1.0` or any other real release. Ships infrastructure only.
- Sigstore / PEP 740 attestation signing — deferred per spec.
- Changelog automation — deferred per spec.
- Reusable-workflow coupling between `release.yml` and `verify.yml`. Design's Notes explicitly chose duplication.
- Post-release announcement automation.

## Notes

T4 (playbook update) could have been a separate trivial commit, but bundling with the workflow landing keeps the "release infrastructure goes live" moment atomic.
