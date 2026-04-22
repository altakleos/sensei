---
feature: metacognitive-tracking
serves: docs/specs/metacognitive-tracking.md
design: docs/design/metacognitive-tracking.md
status: in-progress
date: 2026-04-22
---
# Plan: Metacognitive State Tracking

## Tasks

- [ ] T1: Add `metacognitive_state` to `profile.schema.json`, bump `schema_version` to 2 (~10 min)
- [ ] T2: Add migration function `_migrate_profile_1_to_2` in `migrate.py`, update `CURRENT_PROFILE_VERSION` (~10 min)
- [ ] T3: Add `metacognitive_state` config section to `defaults.yaml` (~2 min)
- [ ] T4: Add metacognitive state tracking instructions to `personality.md` (~3 min)
- [ ] T5: Add calibration update instruction to `assess.md` (~3 min)
- [ ] T6: Extend forethought prompt in `tutor.md` with planning_tendency check (~3 min)
- [ ] T7: Add help-seeking observation to `modes/reviewer.md` (~3 min)
- [ ] T8: Create `calibration_tracker.py` script (~10 min)
- [ ] T9: Add schema validation tests, migration test, and calibration tracker tests (~15 min)

## Acceptance Criteria

- [ ] AC1: Profile schema validates `metacognitive_state` with calibration_accuracy (float|null), planning_tendency (enum), help_seeking (enum), updated_at
- [ ] AC2: Schema version bumped from 1 to 2
- [ ] AC3: Migration adds all-unknown/null metacognitive_state to v1 profiles
- [ ] AC4: `defaults.yaml` has `staleness_days` and `fading_threshold`
- [ ] AC5: Four protocols updated with minimal metacognitive-aware instructions
- [ ] AC6: `calibration_tracker.py` computes calibration_accuracy from profile data
- [ ] AC7: All tests pass
