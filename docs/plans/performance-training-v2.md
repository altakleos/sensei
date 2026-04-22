---
feature: performance-training-v2
serves: docs/specs/performance-training.md
design: docs/design/performance-training.md
status: done
date: 2026-04-22
---
# Plan: Performance Training V2 (Stages 5–6)

## Tasks

- [x] T1: Add stage 5-6 thresholds to defaults.yaml
- [x] T2: Update goal.schema.json — stage maximum from 6 (already set) — verify
- [x] T3: Replace stage 5-6 stubs in performance-training.md protocol with full definitions
- [x] T4: Replace Assessor overlay stub with full V2 content
- [x] T5: Update stage progression table to include stage 4→5 and 5→6 transitions
- [x] T6: Add transcript fixture entries for stage 5-6 behavior
- [x] T7: Add schema tests for stage 5-6 values
- [x] T8: Run full test suite — verify green
- [x] T9: Update plans/README.md index

## Acceptance Criteria

- [x] AC1: Stage 5 (simulated evaluation) fully defined with Assessor + Challenger overlays
- [x] AC2: Stage 6 (full mock) fully defined with Assessor + Reviewer overlays
- [x] AC3: Stage progression rules cover all 6 stages
- [x] AC4: Assessor overlay no longer stubbed
- [x] AC5: Tests pass, schema validates stages 1-6
