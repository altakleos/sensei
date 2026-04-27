---
feature: engine-state-constants
serves: "implementation refactor — no spec change (preserves observable behaviour)"
design: "No new design doc — DRY refactor of two `frozenset` constants (`_DONE_STATES`, `_EXCLUDED_STATES`) currently duplicated byte-for-byte at `src/sensei/engine/scripts/frontier.py:29–30` and `src/sensei/engine/scripts/mutate_graph.py:34–35`. Pattern follows existing private-helper modules `_atomic.py` and `_iso.py` (both manifest-registered, both consumed by multiple scripts). No ADR — refactor preserves observable behaviour and introduces no new architectural decision."
status: done
date: 2026-04-26
---
# Plan: Hoist Curriculum-State Constants into a Shared Module

The 2026-04-26 audit (Recommendation #2, Architecture Risk) named the only architectural-drift risk in the script layer: `_DONE_STATES = frozenset({"skipped", "completed"})` and `_EXCLUDED_STATES = frozenset({"skipped", "active", "completed", "decomposed"})` are defined verbatim in two files:

- `src/sensei/engine/scripts/frontier.py:29–30`
- `src/sensei/engine/scripts/mutate_graph.py:34–35`

Both files use these sets to decide *the same question* — "is this node eligible for the activation frontier?" If a future curriculum-mutation operation adds a new state (say, `paused` or `inserted-pending`) and only one of the two files is updated, the frontier and mutation logic disagree silently — `frontier.py` would consider a `paused` node eligible while `mutate_graph._is_on_frontier` would not (or vice versa). The eligibility predicate is a curriculum-graph invariant that should have one definition.

The fix is the smallest possible refactor: a new private helper module `_states.py` exporting the two constants; both files import from it.

## Design choices

- **Module name `_states.py` (leading underscore) follows the existing `_atomic.py` / `_iso.py` convention** for private helpers consumed by multiple engine scripts. Keeps the public/private boundary visible at import time.
- **Constants stay frozensets**, no behavioural change. The refactor must be byte-identical in observable behaviour.
- **Public attribute names without leading underscore:** export `DONE_STATES` and `EXCLUDED_STATES` (no underscore in the new module). The leading underscore at the call site (`from ._states import DONE_STATES as _DONE_STATES` would re-introduce the same constant locally) is unnecessary; just rename at import to `DONE_STATES`. Any downstream test that asserted on the *names* `_DONE_STATES` would be a private-API contract violation; this plan's smoke test confirms no such test exists.
- **Manifest entry required.** `manifest.yaml` enumerates every shipped engine file (per ADR-0024-adjacent integrity gate); `_states.py` lands as a registered entry next to the existing `_atomic.py` and `_iso.py` rows.
- **No public-API change.** No script's CLI, exit codes, JSON output shape, or imported symbols change. Only internal organisation.
- **No new dependency.** Pure Python.

## Tasks

- [x] T1 — Create `src/sensei/engine/scripts/_states.py`. Contents: module docstring (one paragraph naming the invariant — these are the two state-classification sets the curriculum-graph eligibility predicate depends on), `from __future__ import annotations`, then `DONE_STATES = frozenset({"skipped", "completed"})` and `EXCLUDED_STATES = frozenset({"skipped", "active", "completed", "decomposed"})`. ~30 lines including per-constant docstrings (slightly longer than the 15-line estimate because each constant earned a one-paragraph docstring naming its semantic role).
- [x] T2 — Update `src/sensei/engine/scripts/frontier.py:29–30`: replaced the two local `_DONE_STATES` / `_EXCLUDED_STATES` definitions with `from sensei.engine.scripts._states import DONE_STATES, EXCLUDED_STATES` (now at line 29). Both call sites in `compute_frontier` updated (lines 49, 52).
- [x] T3 — Update `src/sensei/engine/scripts/mutate_graph.py:34–35`: same replacement applied. Both call sites in `_is_on_frontier` updated (lines 39, 42 after the import line consolidated to line 33).
- [x] T4 — Added `scripts/_states.py` to `src/sensei/engine/manifest.yaml § required` between `_iso.py` and `calibration_tracker.py` (manifest line 51).
- [x] T5 — Ran `.venv/bin/pytest tests/test_frontier.py tests/test_mutate_graph.py tests/test_curriculum_integration.py -v`: 37 passed, no failures, no behavioural drift.
- [x] T6 — Full local gate green: `.venv/bin/ruff check .` "All checks passed!", `.venv/bin/mypy` "Success: no issues found in 32 source files" (was 31, +1 for `_states.py`), `.venv/bin/pytest` "673 passed, 14 skipped" with coverage 93.10% ≥ threshold 92% (small bump from 93.09% as the new module's three statements are fully covered indirectly through frontier/mutate_graph tests). `tests/ci/test_engine_manifest.py` 14 passed — every shipped engine file registered.
- [x] T7 — `grep -rn "_DONE_STATES\|_EXCLUDED_STATES" src/ tests/` returns zero matches; the leading-underscore names are extinct. The new module exports `DONE_STATES` / `EXCLUDED_STATES` (no underscore); the leading underscore was retained at the *module* level (`_states.py`) per the existing `_atomic.py` / `_iso.py` private-helper convention.
- [x] T8 — Add row to `docs/plans/README.md § Shipped` index.
- [x] T9 — Commit on `refactor/engine-state-constants` branch with message `refactor: hoist DONE_STATES/EXCLUDED_STATES into shared engine.scripts._states`. Body cites this plan and notes "no behavioural change; manifest entry added."

## Acceptance Criteria

- [x] AC1 — `src/sensei/engine/scripts/_states.py` exists and exports `DONE_STATES` (frozenset of `{"skipped", "completed"}`) and `EXCLUDED_STATES` (frozenset of `{"skipped", "active", "completed", "decomposed"}`).
- [x] AC2 — `src/sensei/engine/scripts/frontier.py` and `src/sensei/engine/scripts/mutate_graph.py` no longer define their own copies; both import from `_states`.
- [x] AC3 — `src/sensei/engine/manifest.yaml` lists `scripts/_states.py` (line 51).
- [x] AC4 — `tests/ci/test_engine_manifest.py` passes (14 passed).
- [x] AC5 — `tests/test_frontier.py`, `tests/test_mutate_graph.py`, `tests/test_curriculum_integration.py` all pass with no edits to test files (37 passed combined).
- [x] AC6 — Full local gate passes; coverage 93.10% ≥ 92%.
- [x] AC7 — `git diff --stat` touches only: this plan, `docs/plans/README.md`, `_states.py` (new), `frontier.py`, `mutate_graph.py`, `manifest.yaml`. No test edits, no public-API change.
- [x] AC8 — `grep "frozenset({\"skipped\", \"completed\"})" src/` matches only `_states.py`; `frontier.py` and `mutate_graph.py` no longer carry the literal.

## Out of Scope

- **Renaming the existing `_atomic.py` / `_iso.py` modules** to drop their underscore prefix. Convention is established; touching it is unrelated.
- **Adding more state-classification helpers** (e.g., `IN_PROGRESS_STATES`, `TERMINAL_STATES`). Add only what the audit identified as duplicated; speculative additions belong in a future plan when a real consumer needs them.
- **Updating any protocol prose** to reference the new constants by name. Protocol prose names states by string literal (`"skipped"`, `"completed"`), not by Python constant. The constants are an internal implementation detail.
- **A `_states.py` test file.** The constants are checked via the existing `frontier.py` / `mutate_graph.py` test suites that exercise the same predicates end-to-end. A standalone test would assert constant *values* — a tautology that does not strengthen verification.

## Risk and reversal

- **Risk: an LLM-generated patch (or an out-of-tree fork) imports the old `_DONE_STATES` private name.** Low likelihood — leading-underscore names are private-API by Python convention; nothing in this repo grep'd up references outside the two source files. Mitigation: T7's grep gate covers the in-repo case.
- **Reversal:** revert the commit. The refactor is byte-equivalent; reversing produces the original two-file duplication exactly.
