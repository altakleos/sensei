---
feature: scripts-relative-imports
serves: "bug fix — engine scripts fail in user instances when system Python lacks matching sensei-tutor version"
design: "No new design doc — mechanical import rewrite preserving observable behaviour. Follows existing private-helper module convention (_atomic.py, _iso.py, _states.py)."
status: done
date: 2026-04-27
---
# Plan: Convert Engine Script Imports to Relative (sys.path-based)

## Problem

All 18 intra-package imports across 12 engine scripts use absolute imports:

```python
from sensei.engine.scripts._states import DONE_STATES, EXCLUDED_STATES
```

These scripts are copied into user instances by `sensei init` (at `.sensei/scripts/`).
When an LLM agent runs `python3 .sensei/scripts/frontier.py`, the system Python
must have the matching `sensei-tutor` package installed — otherwise the import fails
with `ModuleNotFoundError`. This breaks the core design promise that instances are
self-contained.

Reported in the field: user upgraded via `pipx` + `sensei upgrade`, but the agent's
`python3` resolved to a different environment that lacked `_states.py`.

## Fix

Insert a `sys.path` guard at the top of each script that adds the script's own
directory to `sys.path`, then use bare imports:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _states import DONE_STATES, EXCLUDED_STATES
```

This works both when run standalone (`python3 .sensei/scripts/frontier.py`) and
when imported as a package in tests (`from sensei.engine.scripts.frontier import ...`),
because `sys.path.insert` is idempotent and the bare name resolves from the
script's own directory first.

## Why not `from ._states import ...`?

Relative package imports (`from .X import Y`) require the file to be loaded as
part of a package (`-m sensei.engine.scripts.frontier` or imported). They fail
with `ImportError: attempted relative import with no known parent package` when
run as `python3 frontier.py`. Since agents invoke scripts directly, relative
package imports don't work.

## Scope

12 files, 18 import lines. No behavioural change. No CLI change. No schema change.

| File | Lines | Imports |
|------|-------|---------|
| frontier.py | 29 | `_states` |
| mutate_graph.py | 32–33 | `_atomic`, `_states` |
| decay.py | 27 | `_iso` |
| hint_decay.py | 33 | `_iso` |
| goal_priority.py | 36–37 | `_iso`, `decay` |
| review_scheduler.py | 34–35 | `_iso`, `decay` |
| resume_planner.py | 34–36 | `_iso`, `decay`, `frontier` |
| mastery_check.py | 31 | `check_profile` |
| check_profile.py | 70 | `migrate` |
| migrate.py | 28 | `_atomic` |
| teaching_density.py | 54 | `silence_ratio` |
| question_density.py | 50 | `silence_ratio` |

## Tasks

- [ ] T1 — Rewrite all 18 absolute imports to bare imports with `sys.path` guard in each of the 12 files.
- [ ] T2 — Verify all existing tests pass (`make gate` or `pytest`).
- [ ] T3 — Verify scripts run standalone: `python3 src/sensei/engine/scripts/frontier.py --help` works without `sensei-tutor` on `PYTHONPATH`.
- [ ] T4 — Update CHANGELOG.md under `## [Unreleased]`.
