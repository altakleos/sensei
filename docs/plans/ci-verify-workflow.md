---
feature: ci-verify-workflow
serves: (no spec yet — release-playbook aspirational "CI green on main" gate)
design: (no design doc — small orthogonal infrastructure)
status: done
date: 2026-04-20
---
# Plan: GitHub Actions Verify Workflow

> **Retroactive reconstruction** for commit `55bf996`.

## Tasks

- [x] T1: Create `.github/workflows/verify.yml` running `pytest` on push and pull_request to `main` across Python 3.10, 3.11, 3.12, 3.13 with `fail-fast: false` → `.github/workflows/verify.yml`

## Acceptance Criteria

- [x] AC1: Workflow triggers on push and PR to `main`
- [x] AC2: Matrix covers all four supported Python versions
- [x] AC3: `fail-fast: false` so one failing version does not abort the others
- [x] AC4: First run on `main` completes green — verified as 20s green run `24651837626`

## Follow-up Work (not covered by this plan)

- `release.yml` workflow with PyPI OIDC trusted publisher — pending operational admin work and a separate plan.
- A formal `docs/specs/continuous-integration.md` capturing what CI guarantees, if/when CI scope grows beyond pytest.

## Outcome

Shipped in commit `55bf996` (1 file, 29 insertions).
