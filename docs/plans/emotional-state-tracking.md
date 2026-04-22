---
feature: emotional-state-tracking
serves: docs/specs/emotional-state-tracking.md
design: docs/design/emotional-state-tracking.md
status: done
date: 2026-04-22
---
# Plan: Emotional State Tracking

## Tasks

- [x] T1: Add `emotional_state` to `profile.schema.json`, bump `schema_version` to 1 (~15 min)
- [x] T2: Add migration function `_migrate_profile_0_to_1` in `migrate.py`, update `CURRENT_PROFILE_VERSION` (~10 min)
- [x] T3: Add `emotional_state` config section to `defaults.yaml` (~2 min)
- [x] T4: Add emotional state tracking instructions to `personality.md` (~5 min)
- [x] T5: Connect overwhelm heuristic to emotional_state writes in `tutor.md` (~5 min)
- [x] T6: Add affect-aware session decisions to `assess.md` (~5 min)
- [x] T7: Add affect-aware pacing to `review.md` (~5 min)
- [x] T8: Update schema validation tests and add migration test (~10 min)

## Acceptance Criteria

- [x] AC1: Profile schema validates `emotional_state` with 3 enum dimensions + `updated_at`
- [x] AC2: Schema version bumped from 0 to 1
- [x] AC3: Migration adds all-`unknown` emotional_state to v0 profiles
- [x] AC4: `defaults.yaml` has `staleness_minutes` and `degradation_intervention_threshold`
- [x] AC5: Four protocols updated with minimal affect-aware instructions
- [x] AC6: All tests pass, CI green
