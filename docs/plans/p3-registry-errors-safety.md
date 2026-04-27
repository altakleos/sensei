# Plan: P3 Batch — Script Registry, Error Consistency, Decompose Safety, Init Guard

**Status**: complete
**Scope**: 5 fixes (items 19+20 merged, 21, 22, 24; item 23 is a non-issue)
**Design**: Follows existing patterns; no new abstractions

## Context

Item 23 (misplaced test file) is a non-issue — `test_review_protocol.py` is a protocol integration test, correctly named and placed. Dropping it.

Items 16–18 (E2E tests) require real LLM infrastructure and belong in the nightly CI workflow, not this batch.

## Tasks

### Fix 19+20: Complete engine.md Script Registry

**File**: `src/sensei/engine/engine.md`
**Change**: Expand the Script Registry section (L227–L271) to document all 20 public scripts. Organize into two subsections:

1. **Protocol Scripts** (invoked by LLM protocols) — 16 scripts: review_scheduler, session_allocator, resume_planner, goal_priority, mastery_check, calibration_tracker, check_goal, check_profile, classify_confidence, config, decay, frontier, global_knowledge, hint_decay, mutate_graph, pacing
2. **Utility Scripts** (CLI/test infrastructure, not protocol-invoked) — 4 scripts: migrate, question_density, silence_ratio, teaching_density

Each entry: script name, one-line purpose, invocation pattern. Keep it concise — the existing 3 entries are ~10 lines each, but most scripts need only 2–3 lines (name + purpose + basic invocation).

### Fix 21: Standardize error output in hint_decay.py and migrate.py

**Standard**: JSON to stdout (matching calibration_tracker.py, mutate_graph.py, and all other scripts).

**File 1**: `src/sensei/engine/scripts/hint_decay.py`
- Lines 74, 81, 85: Change `print("error: ...", file=sys.stderr)` → `print(json.dumps({"error": "..."}))`
- Line 32 (import guard): Leave as stderr — this is a missing-dependency guard that runs before json is available.

**File 2**: `src/sensei/engine/scripts/migrate.py`
- Wrap `migrate_file()` and `migrate_instance()` calls in `main()` with try/except ValueError, outputting JSON error to stdout.

### Fix 22: Add slug collision check to _do_decompose

**File**: `src/sensei/engine/scripts/mutate_graph.py`
**Change**: In `_do_decompose()`, before adding subgraph nodes (L122), check for collisions:
```python
for sub_slug in sub_nodes:
    if sub_slug in nodes and sub_slug != slug:
        return 1, ""
```

**Test**: Add `test_decompose_rejects_slug_collision` in `tests/test_mutate_graph.py`.

### Fix 24: Guard AGENTS.md overwrite on --force

**File**: `src/sensei/cli.py`, `init` function
**Change**: On non-force init, AGENTS.md is always written (new instance). On `--force` re-init, only write AGENTS.md if it doesn't exist or matches the previous template (i.e., hasn't been user-customized).

Simplest approach: add `if not exists` guard matching the learner file pattern. Users who want to refresh AGENTS.md can delete it and re-run, or use `sensei upgrade` (which already refreshes it unconditionally — that's the correct place for template updates).

```python
agents_md = target / "AGENTS.md"
if not agents_md.exists():
    agents_md.write_text(
        agents_template.read_text(encoding="utf-8"), encoding="utf-8"
    )
```

Same guard for shims — wrap in `if not exists` so `--force` doesn't clobber user customizations.

**Test**: Add `test_init_force_preserves_custom_agents_md` — init, modify AGENTS.md, init --force, verify custom content preserved.

Note: `upgrade` already refreshes AGENTS.md and shims unconditionally (Fix 5) — that's intentional since upgrade means "give me the new engine version's boot docs."

## Verification

- `make gate` passes
- New tests cover fixes 22 and 24
- Grep confirms all scripts documented in engine.md Script Registry
