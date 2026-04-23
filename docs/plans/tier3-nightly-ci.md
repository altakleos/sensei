---
feature: tier3-nightly-ci
serves: docs/specs/release-process.md
design: "Follows existing CI workflow pattern + agent_runner abstraction"
status: done
date: 2026-04-22
---
# Plan: Tier-3 Nightly E2E CI Workflow

GitHub Actions workflow that runs the Tier-2 E2E tests on a nightly
schedule against Kiro CLI. Uses the agent_runner abstraction. Cost-capped
by running only on schedule (not on every PR).

## Tasks

- [x] T1: Create `.github/workflows/e2e-nightly.yml` → `.github/workflows/e2e-nightly.yml`
- [x] T2: Update `docs/operations/release-playbook.md` — document Tier-3 → `docs/operations/release-playbook.md`
- [x] T3: Update `tests/transcripts/README.md` — update Tier-3 status from deferred → active → `tests/transcripts/README.md`
- [x] T4: Run full test suite → verify (depends: T1, T2, T3)
- [x] T5: Mark plan done, add to plans index (depends: T4)

## Acceptance Criteria

- [x] AC1: Workflow runs on cron schedule (nightly) and manual dispatch
- [x] AC2: Workflow uses SENSEI_E2E=1 + kiro-cli for E2E tests
- [x] AC3: Workflow has a cost cap (timeout per test, total timeout)
- [x] AC4: Tier-3 status updated in test documentation
- [x] AC5: Full test suite green
