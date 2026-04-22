---
feature: interleaving
serves: docs/specs/interleaving.md
design: docs/design/interleaving.md
status: planned
date: 2025-07-14
---
# Plan: Interleaving

## Tasks

- [ ] T1: Add `interleaving` config section to `defaults.yaml` → `src/sensei/engine/defaults.yaml`
- [ ] T2: Add interleaving post-sort to `review_scheduler.py` — `--interleave`, `--interleave-intensity`, `--topic-areas` args + `interleave_topics` function → `src/sensei/engine/scripts/review_scheduler.py`
- [ ] T3: Add interleaving instructions to `review.md` Step 2 (~5 lines) → `src/sensei/engine/protocols/review.md`
- [ ] T4: Add interleaving tests — round-robin, intensity blending, min_mastery threshold, CLI flags → `tests/scripts/test_review_scheduler.py`

## Acceptance Criteria

- [ ] AC1: `defaults.yaml` has `interleaving.enabled`, `interleaving.intensity`, `interleaving.min_mastery`
- [ ] AC2: `review_scheduler.py` accepts `--interleave`, `--interleave-intensity`, `--topic-areas` and applies round-robin reorder
- [ ] AC3: Topics below `min_mastery` are excluded from interleaving (blocked practice)
- [ ] AC4: Intensity 0.0 preserves original stale-first order; intensity 1.0 fully interleaves
- [ ] AC5: `review.md` instructs protocol to derive areas and pass `--interleave --topic-areas` to scheduler
- [ ] AC6: Review protocol does NOT label topics with their area (discriminative contrast)
- [ ] AC7: All existing tests pass, new interleaving tests pass
- [ ] AC8: Coverage stays above 89%
