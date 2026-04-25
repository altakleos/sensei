---
feature: tier2-gate-expansion
serves: docs/specs/release-process.md
design: "ADR-only — ADR-0027 (lite) records the cadence/coverage trade-off. Pattern instantiation of the existing release-playbook § Pre-release gate; no new mechanism, no schema change, no Python change. Implementation is prose-side: extend the test list from 3 to 7 and update timing/cost commentary accordingly."
status: done
date: 2026-04-25
---
# Plan: Expand Pre-Release Tier-2 Gate from 3 to 7 Protocols

The 2026-04-25 follow-up audit's top recommendation: close the gap ADR-0024 created but did not fill. The workstation-only Tier-2 gate's audit log is now mandatory, but the gate itself only covers `goal` + `assess` + `hints` (3-of-11 protocols). Behavioral regressions in `tutor` / `review` / `reviewer` / `challenger` reach learners as silent quality drops between releases — exactly the failure mode the gate is supposed to prevent.

This plan expands the pre-release gate to **7 tests covering the 7 protocols a learner exercises in a normal session**: the existing `goal` / `assess` / `hints` triage plus `tutor`, `review`, `reviewer`, `challenger`. The remaining six nightly tests (`mode_transition`, `mastery_calibration`, `goal_lifecycle`, `decompose_trigger`, `insert_trigger`, `skip_trigger`) stay in Tier-3 nightly — they're interaction-pattern tests that overlap with the protocol-level gate, and including them would compound cost without proportional unique coverage.

ADR-0027 (lite) records the cadence/coverage trade-off so a future maintainer reading this six months from now sees the choice as a deliberate one, not as the answer that happened to land first.

## Trade-off

| Dimension | Before (3 tests) | After (7 tests) |
|---|---|---|
| Coverage | 3/13 e2e tests, 3/11 protocols (~27%) | 7/13 e2e tests, 7/11 protocols (~64%) |
| Wall time | ~5:23 (cold cache, v0.1.0a20 measurement) | ~12-14 min projected (linear scaling) |
| OAuth cost (Option B) | ~$1-3 | ~$2-4 |
| Drift caught | goal-creation, assess-probe, hints-pipeline | + tutor teaching drift, reviewer code-review drift, review stale-topic ranking, challenger productive-failure |

The six nightly-only tests overlap with gated protocol tests — e.g., `goal_lifecycle` exercises pause/resume and decay paths that `goal` already invokes; `mode_transition` exercises the same protocol prose as the four mode-named tests. Including them in the gate would compound cost without uniquely covering a protocol.

## Tasks

- [x] T1 — Author ADR-0027 → `docs/decisions/0027-tier2-gate-expansion.md` (lite shape: Decision / Why / Alternative). Decision: pre-release Tier-2 gate covers `tests/e2e/test_{goal,assess,hints,tutor,review,reviewer,challenger}_protocol_e2e.py`. Why: ADR-0024 closed the audit-trail gap; this closes the coverage-breadth gap, which is the actual binding constraint per the 2026-04-25 follow-up audit. Alternative: keep 3 forever and lean on nightly Tier-3 — rejected because nightly green-status freshness is unenforced and a same-day-after-breakage release ships uncaught.
- [x] T2 — Update `docs/decisions/README.md` index — add the ADR-0027 row in number order.
- [x] T3 — Update `docs/operations/release-playbook.md` § Pre-release gate:
  - Test list 3 bullets → 7 bullets, each with the same one-line shape as existing entries: `test_tutor_protocol_e2e.py`, `test_review_protocol_e2e.py`, `test_reviewer_protocol_e2e.py`, `test_challenger_protocol_e2e.py` added.
  - Update the sample `pytest tests/e2e/...` invocation block to invoke the seven test files explicitly (matches what `v0.1.0a20.md` did for three).
  - Update timing prose: "~60-120s per test on cold cache; seven tests is ~12-14 minutes total" (was "three tests is ~4-6 minutes").
  - Update Option B cost note: "~$2-4 per release" (was "~$1-3").
  - Add one sentence pointing at ADR-0027 for the cadence/coverage rationale.
- [x] T4 — Update `docs/operations/releases/README.md` template body to list the seven test bullets (was three) under "Tests covered (per release-playbook § Pre-release gate)". Reference ADR-0027 alongside ADR-0024 in the preamble.
- [x] T5 — Run the full local pipeline from the project venv: `.venv/bin/pytest && .venv/bin/ruff check . && .venv/bin/mypy && python ci/check_foundations.py && python ci/check_links.py && python ci/check_links.py --root src/sensei/engine && python ci/check_changelog_links.py && python ci/check_plan_completion.py`. All must stay green; this plan touches no code, so no test outcome changes.
- [x] T6 — Add row to `docs/plans/README.md` § Shipped index.
- [x] T7 — Commit message: `docs: expand pre-release Tier-2 gate from 3 to 7 protocols (ADR-0027)`. Body cites this plan, ADR-0027, and lists the changed files.

## Acceptance Criteria

- [x] AC1 — `docs/decisions/0027-tier2-gate-expansion.md` exists, ADR-lite shape (≤ 12 body lines), references ADR-0024 and the 2026-04-25 follow-up audit.
- [x] AC2 — `docs/decisions/README.md` shows ADR-0027 with status `accepted (lite)`.
- [x] AC3 — `grep -cE "test_(tutor|review|reviewer|challenger|goal|assess|hints)_protocol_e2e\.py" docs/operations/release-playbook.md` returns at least 7 matches.
- [x] AC4 — `grep -cE "test_(tutor|review|reviewer|challenger|goal|assess|hints)_protocol_e2e\.py" docs/operations/releases/README.md` returns at least 7 matches.
- [x] AC5 — `docs/operations/release-playbook.md` § Pre-release gate prose mentions ~12-14 min wall time and ~$2-4 OAuth cost.
- [x] AC6 — Full local pipeline (T5) passes.
- [x] AC7 — `git diff --stat` touches only: this plan, `docs/plans/README.md`, the new ADR-0027, `docs/decisions/README.md`, `docs/operations/release-playbook.md`, `docs/operations/releases/README.md`. No code change.

## Out of Scope

- **CI-enforcing the 7-test coverage in `ci/check_release_audit.py`.** Strong follow-up — would parse the audit-log body and assert all 7 test functions are listed, completing the ADR-0024 pattern at the breadth dimension. Adds Python + tests; doubled effort for what is otherwise a docs/ADR change. Filed separately if the user wants it. Until then the playbook is the source of truth and the maintainer is the enforcement, same posture as before this plan for the existing 3 tests.
- The six nightly-only tests (`mode_transition`, `mastery_calibration`, `goal_lifecycle`, `decompose_trigger`, `insert_trigger`, `skip_trigger`). They stay in Tier-3 nightly per the trade-off table.
- Any change to `release.yml` or `e2e-nightly.yml`. Tier-2 is workstation-only (existing constraint); Tier-3 cadence is unchanged.
- Quantitative protocol-adherence metrics (`silence_ratio` bands, question-density, assessor-exception adherence count) across all 11 dogfood fixtures. Separate plan — that's the audit's L-effort recommendation.
- CHANGELOG entry. AGENTS.md: docs-only / process changes don't need one. The user-visible release flow (push tag → wait briefly → wheel on PyPI) is unchanged; only the maintainer-side gate's coverage breadth changes.
