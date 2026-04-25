---
feature: ruff-cleanup
serves: docs/specs/release-process.md
design: "Pure-formatting cleanup; no architectural change. No design doc needed."
status: done
date: 2026-04-25
---
# Plan: Reconcile Ruff Lint Errors on Main

`ruff check src/ tests/ ci/` reports 37 errors on the current `main`. CI runs `ruff check .` on every PR (`.github/workflows/verify.yml:32`). Either main is briefly red and recent merges bypassed CI, or local-vs-CI configurations diverge. Either way the state should be reconciled.

Breakdown:
- **32 × E501** line-too-long across 15 files (mostly test files in `tests/scripts/`)
- **5 × E402** module-level imports below conditional `sys.path` insertion (e.g., `tests/e2e/capture_dogfood.py:28-29`)
- **1 × F841** unused local variable in `tests/e2e/test_mastery_calibration_e2e.py`
- **1 × F401** unused `re` import (auto-fixable with `--fix`)

This change is pure formatting + small import re-orderings. No behavioral effect.

## Tasks

- [x] T1: Auto-apply `ruff check --fix` for the 1 safe fix (F401 unused `re` import). Verify with diff that the fix removed only an unused import line and nothing else.
- [x] T2: Manually break the 32 E501 lines. Strategy:
  - Production code (`src/sensei/engine/scripts/global_knowledge.py:40,134`, `mastery_check.py:75`, `mutate_graph.py:244`): split function signatures across lines, break long f-strings.
  - Test files: prefer line continuations on assertion strings or extract intermediate variables; do not introduce conditional logic.
- [x] T3: Resolve the 5 E402 violations:
  - `tests/e2e/capture_dogfood.py:28-29`, `tests/e2e/test_goal_lifecycle_e2e.py`, `tests/e2e/test_mastery_calibration_e2e.py`, `tests/scripts/test_global_knowledge.py`, `tests/test_mutate_graph.py:275` — add `# noqa: E402` with a trailing comment naming the reason (sys.path bootstrap, test-grouping comment, etc.) when the placement is intentional. Do **not** rewrite the sys.path-prepend pattern; that's a deliberate idiom in these tests.
- [x] T4: Resolve the 1 F841 in `tests/e2e/test_mastery_calibration_e2e.py`. If the variable is captured for diff-vs-after assertions, prefix `_` (`_before_profile`) to mark intentional retention; if truly unused, delete. Inspect the test before deciding.
- [x] T5: Apply `ruff check --fix --unsafe-fixes` ONLY to evaluate whether the 2 hidden fixes are safe; do NOT commit them blindly. Report what they would do; if non-behavioral, apply them. Otherwise skip.
- [x] T6: Run `ruff check src/ tests/ ci/` and confirm zero errors. Run full pytest suite (`pytest`) to confirm no regressions from the line-breaks or import re-orderings.
- [x] T7: No CHANGELOG entry — refactors and internal lint cleanups are explicitly excluded by `AGENTS.md:111`.

## Acceptance Criteria

- [x] AC1: `ruff check src/ tests/ ci/` exits 0.
- [x] AC2: `pytest` passes (no behavioral regression from the cleanup).
- [x] AC3: No production-code logic changed — diffs are limited to whitespace, import order, line-continuations, and the noqa comments justified in T3/T4.

## Out of Scope

- Tightening `ruff` rules in `pyproject.toml` — pure cleanup only; rule changes warrant their own ADR-lite.
- Migrating sys.path-bootstrap idioms in tests to a conftest fixture — separate concern.
- Auto-formatter (`ruff format`) adoption — pyproject currently configures `ruff lint` only; format adoption is a different decision.
