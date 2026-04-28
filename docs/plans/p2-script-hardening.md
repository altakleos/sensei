---
status: complete
---
# Plan: P2 Batch — Script Hardening + Test Coverage Gaps

**Scope**: 6 fixes — 3 script hardening, 3 test coverage gaps
**Design**: Follows existing patterns; no new abstractions

## Tasks

### Fix 9: Add error handling to calibration_tracker.py

**File**: `src/sensei/engine/scripts/calibration_tracker.py`
**Change**: In `main()`, wrap YAML reading with file-exists check, try/except YAMLError, and isinstance check — same pattern as `check_profile.py`.

### Fix 10: Auto-migrate goals before validation in check_goal.py

**File**: `src/sensei/engine/scripts/check_goal.py`
**Change**: In `validate_goal()`, add migration call before schema validation — same pattern as `check_profile.py`'s `validate_profile()`:
```python
import contextlib
from migrate import migrate_goal
with contextlib.suppress(ValueError, KeyError):
    goal = migrate_goal(dict(goal))
```

### Fix 11: Add state precondition to mutate_graph.py _do_skip

**File**: `src/sensei/engine/scripts/mutate_graph.py`
**Change**: In `_do_skip()`, reject nodes in terminal states (completed, decomposed, skipped). Return error code 1 if node state is in `{"completed", "decomposed", "skipped"}`.

**Test impact**: `tests/scripts/test_mutate_graph.py` — add test that skip from completed/decomposed/skipped returns exit code 1.

### Fix 12: Add tests for _iso.py

**New file**: `tests/scripts/test_iso.py`
**Tests**: trailing Z → UTC, explicit offset preserved, naive → UTC, round-trip.

### Fix 13: Add tests for _states.py

**New file**: `tests/scripts/test_states.py`
**Tests**: membership assertions, DONE_STATES ⊂ EXCLUDED_STATES, frozenset type.

### Fix 14: Add hints.yaml.schema.json validation test

**File**: `tests/test_schema_validation.py`
**Change**: Add VALID_HINTS fixture, add to parametrize list, add negative tests.

## Verification

- `make gate` passes
- Coverage stays ≥ 92%
