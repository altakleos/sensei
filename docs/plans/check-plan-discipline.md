---
feature: check-plan-discipline
serves: docs/specs/release-process.md
design: "Pattern instantiation of existing ci/check_*.py linter family. No new mechanism."
status: done
date: 2026-04-25
---
# Plan: Lint Plan-Completion Discipline

`docs/development-process.md:107-112` is unambiguous: a plan with `status: done` must have every task `- [x]` (shipped) or `- [~]` (deferred with NOTE). Two current plans violate this:

- `docs/plans/expand-trigger.md` — six tasks (T1–T6) marked `- [ ]` despite `status: done`. Verification: commit `21f1f84 feat: expand trigger`, granularity-check prose present in `src/sensei/engine/protocols/tutor.md`, `src/sensei/engine/protocols/assess.md:178` mentions decompose, `defaults.yaml` carries `max_decompose_children`, `docs/specs/README.md:14` lists the spec, and CHANGELOG `[0.1.0a18]` records the entry. **All eight tasks shipped.**
- `docs/plans/real-dogfood-capture.md` — five tasks (T1–T5) all marked `- [ ]` plus four ACs unticked despite `status: done`. Verification: commits `7de6fa8 feat: add multi-turn dogfood capture harness`, `6a5539c test: replace synthetic dogfood seeds with real LLM captures`, `4ea8bdf docs: mark real-dogfood-capture plan as done`. The capture harness exists at `tests/e2e/capture_dogfood.py`; the three real `.dogfood.md` transcripts ship under `tests/transcripts/`. **All five tasks shipped.**

The fix is two-part: tick the boxes for what shipped, then add `ci/check_plan_completion.py` (instantiation of the existing `ci/check_foundations.py` and `ci/check_links.py` pattern) to `verify.yml` so this never recurs.

## Tasks

- [x] T1: `docs/plans/expand-trigger.md` — change every `- [x] **<n>.` to `- [x] **<n>.` for tasks 1–6 (tasks 7–8 already ticked). Frontmatter `status: done` already correct.
- [x] T2: `docs/plans/real-dogfood-capture.md` — change every `- [x] T<n>` to `- [x] T<n>` (T1–T5) and every `- [x] AC<n>` to `- [x] AC<n>` (AC1–AC4). Frontmatter `status: done` already correct.
- [x] T3: Create `ci/check_plan_completion.py`:
  - Walk `docs/plans/*.md`.
  - For each plan with `status: done` (frontmatter), parse the body for top-level checkboxes (`- [ ]`, `- [x]`, `- [~]`). Lines indented as sub-bullets are not top-level tasks and are ignored.
  - Fail (exit 1) if any unticked `- [ ]` line is found in a `done` plan, listing each violator as `path:line: <task summary>`.
  - Treat `- [~]` as explicitly-deferred (acceptable on a `done` plan).
  - Skip plans whose frontmatter `status` is anything other than `done` (`planned`, `in-progress`, missing).
  - Provide `--quiet` for green-path silence and verbose default output that matches `ci/check_foundations.py`'s style.
- [x] T4: Add `tests/ci/test_check_plan_completion.py`:
  - Use `tmp_path` fixtures with synthetic plan files.
  - Cover: `done`+all-ticked → exit 0; `done`+unticked task → exit 1 with the violating `path:line` in stdout; `done`+`[~]` deferred → exit 0; `planned`+unticked → exit 0 (only `done` plans are policed); missing-frontmatter file → exit 0 (skip silently); sub-bullet `- [ ]` under a parent `- [x]` is not flagged.
  - Add a smoke test that runs the validator against the real `docs/plans/` and expects exit 0 (post-T1+T2 fix).
- [x] T5: `.github/workflows/verify.yml` — append a new step after the existing foundations/links linter steps:
  ```yaml
  - name: Lint plan completion
    run: python ci/check_plan_completion.py
  ```
- [x] T6: `docs/development-process.md` — add a one-line pointer in § "Checkbox convention" noting that `ci/check_plan_completion.py` enforces the rule. Single sentence; no rule-text duplication.
- [x] T7: No CHANGELOG entry — internal CI lint addition is in the docs-only/internal-test exclusion at `AGENTS.md:111`.

## Acceptance Criteria

- [x] AC1: `python ci/check_plan_completion.py` exits 0 against the current `docs/plans/` after T1+T2 fixes.
- [x] AC2: `pytest tests/ci/test_check_plan_completion.py` passes (≥6 cases per T4).
- [x] AC3: Reverting either expand-trigger.md or real-dogfood-capture.md to its broken state (status=done + unticked task) makes `ci/check_plan_completion.py` exit 1 (verified locally; not committed). Demonstrates the lint actually catches the violation it was built for.
- [x] AC4: Full `pytest && ruff check . && mypy && python ci/check_plan_completion.py` all pass.

## Out of Scope

- Auditing every plan in `docs/plans/` for hidden violations beyond the two named — the new lint will catch any I missed once T5 runs in CI.
- Auto-ticking based on git-log heuristics — explicit human review (T1, T2) is the contract; auto-tick reintroduces the silent-skip risk.
- Enforcing the `- [~]` NOTE-block requirement — that's a stricter rule the development-process.md describes ("with a NOTE: explaining why"); a separate plan if/when warranted.
