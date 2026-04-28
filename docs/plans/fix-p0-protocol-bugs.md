---
status: complete
---
# Plan: Fix P0 Protocol & Script Bugs

**Scope**: 3 bugs — prose fix, path fix, ordinal fix
**Design**: Follows existing patterns; no new abstractions

## Context

Gap analysis found 3 bugs that cause incorrect LLM behavior at runtime:

1. **assess.md references undefined config key** — `config.assessment.mastery_threshold` doesn't exist; the real key is `config.curriculum.mastery_threshold`
2. **4 protocols reference a non-existent file path** — `learner/goals/<goal>/curriculum.yaml` doesn't exist; goal data lives in `learner/goals/<slug>.yaml`
3. **Mastery ordinal divergence** — `review_scheduler.py` uses a 3-level scale (`shaky/solid/deep`) with different numeric values than the canonical 5-level scale used by `global_knowledge.py` and `mastery_check.py`

All three are prose-as-code or script bugs — no CLI changes, no schema changes, no new features.

## Tasks

### Bug 1: Fix config key reference in assess.md

**File**: `src/sensei/engine/protocols/assess.md` line 15
**Change**: `config.assessment.mastery_threshold` → `config.curriculum.mastery_threshold`
**Scope**: 1 line, 1 file

### Bug 2: Fix curriculum file path references

**Files** (11 replacements total):
- `src/sensei/engine/protocols/tutor.md` — lines 12, 28, 69, 98, 117, 127 (6 occurrences)
- `src/sensei/engine/protocols/challenger.md` — line 12 (1 occurrence)
- `src/sensei/engine/protocols/reviewer.md` — line 12 (1 occurrence)
- `src/sensei/engine/protocols/status.md` — lines 14, 31, 38 (3 occurrences)

**Change**: All variations of `learner/goals/<goal>/curriculum.yaml` → `learner/goals/<slug>.yaml`

Note: The exact placeholder varies (`<goal>`, `<active-goal>`, etc.) — each must be replaced with the corresponding `<slug>` form matching `goal.md`'s convention.

### Bug 3: Align mastery ordinals in review_scheduler.py

**File**: `src/sensei/engine/scripts/review_scheduler.py` lines 43–46
**Change**: Replace `_MASTERY_ORDINALS = {"shaky": 0.2, "solid": 0.6, "deep": 0.9}` with the canonical 5-level scale from `global_knowledge.py`:
```python
_MASTERY_ORDINALS: dict[str, float] = {
    "none": 0.0,
    "shaky": 0.25,
    "developing": 0.5,
    "solid": 0.75,
    "mastered": 1.0,
}
```

**Test impact**: `tests/scripts/test_review_scheduler.py` likely has assertions against the old ordinal values — must be updated to match.

### Verification

- `make gate` passes (lint + typecheck + test + validators)
- Grep confirms zero remaining `curriculum.yaml` references in protocols/
- Grep confirms zero remaining `assessment.mastery_threshold` references
- `review_scheduler.py` ordinals match `global_knowledge.py` exactly

## Out of Scope

- Extracting mastery levels to a shared `_levels.py` module (good idea, separate PR)
- Updating engine.md Script Registry (observation #20, P3)
- Any CLI changes
