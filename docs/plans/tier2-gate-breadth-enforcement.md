---
feature: tier2-gate-breadth-enforcement
serves: docs/specs/release-process.md
design: "ADR-only — ADR-0028 (lite) records the breadth-enforcement decision. Pattern instantiation of the existing ci/check_release_audit.py validator helpers (_validate_tool, _validate_transcript_hash) — adds a third helper that asserts all seven test file paths appear in the audit-log body. No new mechanism, no schema change, no release.yml invocation change."
status: done
date: 2026-04-25
---
# Plan: CI-Enforce the 7-Test Tier-2 Gate Breadth (ADR-0028)

ADR-0024 made the per-release audit log mandatory; ADR-0027 widened the gate to seven protocols. The `ci/check_release_audit.py` validator currently asserts that the artifact exists, parses, and reports `exit_code: 0` — but does **not** check that the named tests actually ran. A maintainer (human or agent) can still ship an audit log claiming "3 passed" while skipping the tutor/review/reviewer/challenger expansion — exactly the failure mode ADR-0027 was supposed to close.

This plan adds breadth enforcement: `ci/check_release_audit.py` asserts that the body of `docs/operations/releases/<tag>.md` mentions every test file path enumerated in ADR-0027 (seven `tests/e2e/test_*_protocol_e2e.py` paths). Honour-system → machine-checked. ADR-0028 (lite) records the decision and lists the seven paths so the source of truth lives in one place.

## Design choice: file paths, not function names

The validator searches the body for **file paths** (`tests/e2e/test_<protocol>_protocol_e2e.py`), not function names. Rationale: the seven file paths appear verbatim in the playbook's bash-array invocation block, which the maintainer copy-pastes into the audit log's `## Invocation` section — so the paths land in the body for free. Function names are also listed under `## Result`, but they're more brittle (a refactor that renames `test_goal_protocol_produces_schema_valid_goal` would break archaeology). Paths are stable.

## Forward-looking gate

`v0.1.0a20.md` predates ADR-0027 — it lists only 3 tests and would fail the new breadth check. ADR-0028 follows the same forward-looking pattern as ADR-0024: the gate fires from the **next** tag onward. `release.yml` only runs the validator against `GITHUB_REF_NAME` (the current tag), so the historical log is never re-validated by CI. A maintainer running `python ci/check_release_audit.py --tag v0.1.0a20` manually for archaeology will see the expected-failure mode (4 missing test paths) — that's the gate working as designed, not a regression.

## Tasks

- [x] T1 — Author ADR-0028 → `docs/decisions/0028-tier2-gate-breadth-enforcement.md` (lite shape: Decision / Why / Alternative). Decision: `ci/check_release_audit.py` fails when any of the seven test file paths from ADR-0027 are absent from the audit-log body. The seven paths are listed verbatim in the ADR so a future supersession reads the contract from one place. Why: ADR-0024 + ADR-0027 left a soft-failure mode where the gate's breadth was set in docs but not enforced in CI; this closes it without re-opening either prior ADR. Alternative: keep honour-system; rejected because the same maintainer who could miss running 7 tests is the one trusted to confirm 7 ran — same shape as the argument ADR-0024 used to enforce the artifact's existence.
- [x] T2 — Update `docs/decisions/README.md` index — add ADR-0028 row in number order.
- [x] T3 — Extend `ci/check_release_audit.py`:
  - Add module constant `REQUIRED_GATE_TESTS: tuple[str, ...]` with the seven `tests/e2e/test_*_protocol_e2e.py` paths.
  - Add helper `_validate_body_breadth(body: str) -> list[str]` returning one violation string per missing path.
  - Refactor `_split_frontmatter` (or `lint`) to also return the body text (after the closing `---\n` fence), so the lint function can pass it to `_validate_body_breadth`.
  - Wire the new check into `lint(audit_path, expected_tag)` after the existing field-level validations.
  - Update the module docstring's rules list to include the new check as numbered rule 8 (after the existing rules 1–7), with a one-line pointer at ADR-0028.
- [x] T4 — Extend `tests/ci/test_check_release_audit.py`:
  - `test_body_breadth_complete` — body lists all seven paths; no violation.
  - `test_body_breadth_missing_one` — body omits one path; one violation reported, naming the missing path.
  - `test_body_breadth_missing_all` — body has no test references; seven violations reported.
  - `test_legacy_three_test_log_fails_breadth` — body lists only the original three paths; reports the four expected violations (tutor/review/reviewer/challenger). Documents the forward-looking-gate intent.
  - Adjust any existing happy-path fixture that didn't include all seven paths so the existing tests remain green under the new check.
- [x] T5 — Run the full local pipeline from the project venv: `.venv/bin/pytest && .venv/bin/ruff check . && .venv/bin/mypy && python ci/check_foundations.py && python ci/check_links.py && python ci/check_links.py --root src/sensei/engine && python ci/check_changelog_links.py && python ci/check_plan_completion.py`. All must stay green.
- [x] T6 — Add row to `docs/plans/README.md` § Shipped index.
- [x] T7 — Commit message: `feat: ci/check_release_audit.py enforces 7-test gate breadth (ADR-0028)`. Body cites this plan, ADR-0028, ADR-0027, ADR-0024.

## Acceptance Criteria

- [x] AC1 — `docs/decisions/0028-tier2-gate-breadth-enforcement.md` exists, ADR-lite shape (≤ 14 body lines including the path list), references ADR-0024 and ADR-0027.
- [x] AC2 — `docs/decisions/README.md` shows ADR-0028 with status `accepted (lite)`.
- [x] AC3 — `grep -c "test_.*_protocol_e2e\.py" ci/check_release_audit.py` returns at least 7 (the constant lists all seven paths).
- [x] AC4 — `python ci/check_release_audit.py --tag v0.1.0a20` exits non-zero with violations naming the four absent test paths (tutor/review/reviewer/challenger) — demonstrates the gate working on the legacy log.
- [x] AC5 — `.venv/bin/pytest tests/ci/test_check_release_audit.py -v` passes including the four new cases.
- [x] AC6 — Full local pipeline (T5) passes.
- [x] AC7 — `git diff --stat` touches only: this plan, `docs/plans/README.md`, ADR-0028, `docs/decisions/README.md`, `ci/check_release_audit.py`, `tests/ci/test_check_release_audit.py`. No other code changes.

## Out of Scope

- **Backfilling `v0.1.0a20.md`** to mention the four newly-required test paths. Forward-looking gate per Forward-looking gate § above; rewriting historical logs would be lying about what actually ran (3 tests, not 7).
- **Function-name validation.** This plan validates file paths only; function-name verification would harden the check further but couples the validator to test-name stability. Filed as a possible future hardening if a function-name refactor ever leaves an audit log with stale references.
- **Re-running the validator against historical tags in CI.** `release.yml` continues to run only against `GITHUB_REF_NAME` (current tag); historical logs are not re-validated.
- Quantitative protocol-adherence metrics across dogfood fixtures (audit Risk #4). Separate plan.
- CHANGELOG entry. AGENTS.md: this is process / CI-internal hardening; no user-visible release-flow change. The maintainer's release sequence is unchanged.

## Diff Estimate

- `ci/check_release_audit.py`: +30-40 lines (constant + helper + lint wiring + docstring rule 8).
- `tests/ci/test_check_release_audit.py`: +50-80 lines (4 new cases + minor fixture updates).
- ADR-0028: ~14 body lines.
- Plan + index rows: ~75 lines this plan, ~2 lines elsewhere.

Net: ~180-220 LOC, M effort.
