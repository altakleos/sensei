---
status: done
design: "Follows ADR-0006, ADR-0022"
---

# Plan: Eliminate `sys.path.insert` hack from engine scripts

## Problem

14 of 24 engine scripts contain a `sys.path.insert(0, ...)` hack to enable
bare sibling imports (e.g., `from _iso import parse_iso`) when invoked as
standalone files by `run.sh`. This:

- Defeats mypy strict mode (20 `# type: ignore[import-not-found]` suppressions)
- Duplicates boilerplate across 14 files
- 5 of the 14 files don't even use private helpers — their hack is dead code

The hack exists because `run.sh` invokes scripts as direct files
(`python3 scripts/decay.py`), not as modules. Tests and cli.py use normal
package imports and are unaffected.

## Solution

Move the path setup from each script into `run.sh` via `PYTHONPATH`. This is
the single point of entry for standalone execution, so it's the right place
to configure the import environment.

### Changes

**1. `src/sensei/engine/run.sh`** — set `PYTHONPATH` before exec:

```sh
export PYTHONPATH="$SCRIPT_DIR/scripts:${PYTHONPATH:-}"
exec "$PYTHON" "$SCRIPT_DIR/scripts/$@"
```

Both the primary path (from `.python_path`) and the fallback (`python3`)
get the same `PYTHONPATH`.

**2. 14 engine scripts** — remove the hack (3 lines each):

Remove:
```python
sys.path.insert(0, str(Path(__file__).resolve().parent))
```

Remove the `# type: ignore[import-not-found]` comment from each bare import.

Remove `from pathlib import Path` if it becomes unused after the removal
(check each file — some use `Path` elsewhere).

Remove `import sys` if it becomes unused after the removal (check each
file — some use `sys.argv` or `sys.exit` elsewhere).

**3. 5 dead-code files** (mastery_check, check_profile, check_goal,
question_density, teaching_density) — remove the hack even though they
have no bare sibling imports. They don't need it and never did.

### Files touched

| File | Change |
|------|--------|
| `src/sensei/engine/run.sh` | Add `PYTHONPATH` export |
| `src/sensei/engine/scripts/decay.py` | Remove hack + type-ignore |
| `src/sensei/engine/scripts/frontier.py` | Remove hack + type-ignore |
| `src/sensei/engine/scripts/mastery_check.py` | Remove hack (dead code) |
| `src/sensei/engine/scripts/hint_decay.py` | Remove hack + type-ignore |
| `src/sensei/engine/scripts/pacing.py` | Remove hack + type-ignore |
| `src/sensei/engine/scripts/migrate.py` | Remove hack + type-ignore |
| `src/sensei/engine/scripts/check_profile.py` | Remove hack (dead code) |
| `src/sensei/engine/scripts/review_scheduler.py` | Remove hack + type-ignore |
| `src/sensei/engine/scripts/mutate_graph.py` | Remove hack + type-ignore |
| `src/sensei/engine/scripts/check_goal.py` | Remove hack (dead code) |
| `src/sensei/engine/scripts/resume_planner.py` | Remove hack + type-ignore |
| `src/sensei/engine/scripts/goal_priority.py` | Remove hack + type-ignore |
| `src/sensei/engine/scripts/question_density.py` | Remove hack (dead code) |
| `src/sensei/engine/scripts/teaching_density.py` | Remove hack (dead code) |

Total: 15 files (1 shell script + 14 Python scripts).

### What does NOT change

- cli.py — already uses package imports, unaffected
- Tests — already use package imports, unaffected
- `__init__.py` — stays empty
- `_atomic.py`, `_iso.py`, `_states.py` — untouched
- `config.py` and the 5 scripts without the hack — untouched

## Acceptance criteria

1. `sys.path.insert` appears in zero engine scripts
2. `type: ignore[import-not-found]` appears in zero engine scripts
3. `pytest` passes (698+ tests, 92%+ coverage)
4. `ruff check src/ tests/` passes
5. `mypy --strict src/` passes (or improves — fewer suppressions)
6. Manual: `run.sh decay.py --last-seen 2026-04-01T00:00:00Z --half-life-days 7 --now 2026-04-20T00:00:00Z` works from a scaffolded instance
7. `sensei verify` passes on a scaffolded instance

## Risks

- **Upgrade path**: Existing user instances have the old `run.sh`. `sensei upgrade`
  replaces engine files atomically, so the new `run.sh` and cleaned scripts
  arrive together. No migration needed — the old scripts with the hack still
  work if a user hasn't upgraded.
- **Non-sh shells**: `PYTHONPATH` is POSIX standard. `run.sh` already requires
  `/bin/sh`. No risk.
