---
feature: performance-training-v2
serves: docs/specs/performance-training.md
design: docs/design/performance-training.md
status: in-progress
date: 2026-04-22
---
# Plan: Performance Training V2 (Stages 5–6)

## Tasks

- [ ] T1: Add stage 5-6 thresholds to defaults.yaml
- [ ] T2: Update goal.schema.json — stage maximum from 6 (already set) — verify
- [ ] T3: Replace stage 5-6 stubs in performance-training.md protocol with full definitions
- [ ] T4: Replace Assessor overlay stub with full V2 content
- [ ] T5: Update stage progression table to include stage 4→5 and 5→6 transitions
- [ ] T6: Add transcript fixture entries for stage 5-6 behavior
- [ ] T7: Add schema tests for stage 5-6 values
- [ ] T8: Run full test suite — verify green
- [ ] T9: Update plans/README.md index

## Acceptance Criteria

- [ ] AC1: Stage 5 (simulated evaluation) fully defined with Assessor + Challenger overlays
- [ ] AC2: Stage 6 (full mock) fully defined with Assessor + Reviewer overlays
- [ ] AC3: Stage progression rules cover all 6 stages
- [ ] AC4: Assessor overlay no longer stubbed
- [ ] AC5: Tests pass, schema validates stages 1-6
