---
feature: shared-turn-parser-public-api
serves: docs/specs/release-process.md
design: "No design doc — pure refactor. Promotes the existing private `_split_into_turns` helper in `src/sensei/engine/scripts/silence_ratio.py` to a public name (`split_into_turns`); updates the two cross-module consumers (`question_density.py`, `teaching_density.py`) to import the public name; adds a direct test pinning the public-API contract. No new mechanism, no schema change, no protocol prose change. ADR not warranted (mechanical hygiene)."
status: done
date: 2026-04-26
---
# Plan: Promote `_split_into_turns` to a Public API

When `question_density.py` (commit `7d76e6c`) and `teaching_density.py` (commit `f26c64e`) shipped, both modules imported `_split_into_turns` from `silence_ratio.py` — an underscore-prefixed name conventionally signalling "private to its own module." With three consumers now sharing the canonical `[MENTOR]`/`[LEARNER]` turn parser, the underscore-prefix is no longer accurate: the function IS the public turn-extraction API for the Tier-1 quantitative-band family, and importing it across modules with `_` prefix carries a "this is a smell" comment in both downstream modules.

This plan promotes the symbol to its public name (`split_into_turns`), updates the two consumers, and pins the public-API contract with a direct test in `test_silence_ratio.py` (currently the function is exercised only indirectly via `compute_turn_stats` tests). The cross-module-sharing comments in `question_density.py` and `teaching_density.py` simplify accordingly.

## Tasks

- [x] T1 — Rename `_split_into_turns` → `split_into_turns` in `src/sensei/engine/scripts/silence_ratio.py`. Update the one internal caller (`compute_turn_stats`). Module docstring's "Library entry points" list grows the new public name.
- [x] T2 — Update `src/sensei/engine/scripts/question_density.py`: import `split_into_turns` (not `_split_into_turns`); simplify the cross-module-sharing comment from "Importing the private helper keeps the parser single-source… at the cost of a one-character-off-the-style convention" to a one-liner pointing at the now-public API.
- [x] T3 — Update `src/sensei/engine/scripts/teaching_density.py`: same as T2 — import the public name; trim the redundant cross-module-sharing comment.
- [x] T4 — Add at least 2 new direct cases in `tests/scripts/test_silence_ratio.py` exercising `split_into_turns` (one happy-path: `[MENTOR] hi\n[LEARNER] yes\n` → ``(["hi"], ["yes"])``; one frontmatter-and-multiline: confirms strip + multi-line accumulation. The existing `compute_turn_stats` tests transitively cover the rest, but pinning the public surface directly is the load-bearing change of this refactor.
- [x] T5 — Run the full local pipeline from the project venv: `.venv/bin/pytest && .venv/bin/ruff check . && .venv/bin/mypy && python ci/check_foundations.py && python ci/check_links.py && python ci/check_links.py --root src/sensei/engine && python ci/check_changelog_links.py && python ci/check_plan_completion.py`. All must stay green; this plan is rename + import update, no behaviour change.
- [x] T6 — Add row to `docs/plans/README.md` § Shipped index.
- [x] T7 — Commit message: `refactor: promote _split_into_turns to public split_into_turns`. Body cites this plan, names the three modules touched, and notes the absence of a CHANGELOG entry (internal refactor).

## Acceptance Criteria

- [x] AC1 — `grep -n "def split_into_turns\b" src/sensei/engine/scripts/silence_ratio.py` returns one match (the public definition); `grep -n "def _split_into_turns" src/sensei/engine/scripts/` returns zero matches across the package.
- [x] AC2 — `grep -n "import split_into_turns\|from .* import .* split_into_turns" src/sensei/engine/scripts/question_density.py src/sensei/engine/scripts/teaching_density.py` returns at least one match per file (no leading underscore).
- [x] AC3 — `grep -n "_split_into_turns" src/sensei/engine/scripts/` returns zero matches across the entire package (no stale references).
- [x] AC4 — `tests/scripts/test_silence_ratio.py` includes at least 2 new test functions whose names contain `split_into_turns`.
- [x] AC5 — Full local pipeline (T5) passes with coverage ≥ 92%.
- [x] AC6 — `git diff --stat` touches only: this plan, `docs/plans/README.md`, `src/sensei/engine/scripts/silence_ratio.py`, `src/sensei/engine/scripts/question_density.py`, `src/sensei/engine/scripts/teaching_density.py`, `tests/scripts/test_silence_ratio.py`. No other files.

## Out of Scope

- **Promoting `_strip_frontmatter` to public.** Used only internally by `split_into_turns`; no cross-module consumer requests it. If a future helper does, that's the moment to flip it.
- **CHANGELOG entry.** AGENTS.md: refactors don't need a changelog entry. The user-visible release flow and the engine bundle's behavioural surface are unchanged; only an internal symbol gets a name without an underscore.
- **A new ADR.** Pure mechanical hygiene — not a decision about architecture.
- **Backward-compat alias** (`_split_into_turns = split_into_turns`). All three consumers live in this repo and are updated in the same commit; no outside callers exist. Keeping the alias would obscure the rename and invite future drift.

## Risk and reversal

- **Test-import skew.** `test_silence_ratio.py` doesn't currently import `_split_into_turns` directly (per the file's existing contents); only the new T4 test cases import the public name. If any other test file in `tests/scripts/` imports the underscore-prefixed name (it shouldn't — checked), the rename would surface that at pytest collection. AC3 catches any stale references.
- **Reversal**: revert the commit. Pure rename; no persistent state, no schema migration.
