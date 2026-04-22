---
feature: metacognitive-tracking
serves: docs/specs/metacognitive-tracking.md
design: docs/design/metacognitive-tracking.md
status: done
date: 2026-04-22
---
# Plan: Metacognitive State Tracking

## Tasks

- [x] T1: Add `metacognitive_state` to `profile.schema.json`, bump `schema_version` to 2 (~10 min)
- [x] T2: Add migration function `_migrate_profile_1_to_2` in `migrate.py`, update `CURRENT_PROFILE_VERSION` (~10 min)
- [x] T3: Add `metacognitive_state` config section to `defaults.yaml` (~2 min)
- [x] T4: Add metacognitive state tracking instructions to `personality.md` (~3 min)
- [x] T5: Add calibration update instruction to `assess.md` (~3 min)
- [x] T6: Extend forethought prompt in `tutor.md` with planning_tendency check (~3 min)
- [x] T7: Add help-seeking observation to `modes/reviewer.md` (~3 min)
- [x] T8: Create `calibration_tracker.py` script (~10 min)
- [x] T9: Add schema validation tests, migration test, and calibration tracker tests (~15 min)

## Acceptance Criteria

- [x] AC1: Profile schema validates `metacognitive_state` with calibration_accuracy (float|null), planning_tendency (enum), help_seeking (enum), updated_at
- [x] AC2: Schema version bumped from 1 to 2
- [x] AC3: Migration adds all-unknown/null metacognitive_state to v1 profiles
- [x] AC4: `defaults.yaml` has `staleness_days` and `fading_threshold`
- [x] AC5: Four protocols updated with minimal metacognitive-aware instructions
- [x] AC6: `calibration_tracker.py` computes calibration_accuracy from profile data
- [x] AC7: All tests pass
