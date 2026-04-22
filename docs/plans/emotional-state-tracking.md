---
feature: emotional-state-tracking
serves: docs/specs/emotional-state-tracking.md
design: docs/design/emotional-state-tracking.md
status: in-progress
date: 2026-04-22
---
# Plan: Emotional State Tracking

## Tasks

- [ ] T1: Add `emotional_state` to `profile.schema.json`, bump `schema_version` to 1 (~15 min)
- [ ] T2: Add migration function `_migrate_profile_0_to_1` in `migrate.py`, update `CURRENT_PROFILE_VERSION` (~10 min)
- [ ] T3: Add `emotional_state` config section to `defaults.yaml` (~2 min)
- [ ] T4: Add emotional state tracking instructions to `personality.md` (~5 min)
- [ ] T5: Connect overwhelm heuristic to emotional_state writes in `tutor.md` (~5 min)
- [ ] T6: Add affect-aware session decisions to `assess.md` (~5 min)
- [ ] T7: Add affect-aware pacing to `review.md` (~5 min)
- [ ] T8: Update schema validation tests and add migration test (~10 min)

## Acceptance Criteria

- [ ] AC1: Profile schema validates `emotional_state` with 3 enum dimensions + `updated_at`
- [ ] AC2: Schema version bumped from 0 to 1
- [ ] AC3: Migration adds all-`unknown` emotional_state to v0 profiles
- [ ] AC4: `defaults.yaml` has `staleness_minutes` and `degradation_intervention_threshold`
- [ ] AC5: Four protocols updated with minimal affect-aware instructions
- [ ] AC6: All tests pass, CI green
