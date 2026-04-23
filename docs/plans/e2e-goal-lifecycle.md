---
feature: e2e-goal-lifecycle
serves: docs/specs/goal-lifecycle-transitions.md
design: "Follows existing E2E test pattern + stipulated multi-step prompt"
status: in-progress
date: 2026-04-22
---
# Plan: Goal Lifecycle E2E Test — Pause + Resume

Tests the persistence contract: goal state survives across sessions.
Exercises pause/resume transitions and decay-aware re-entry via
resume_planner.py. Validates Tomás persona stress-test.

## Tasks

- [ ] T1: Create `tests/e2e/test_goal_lifecycle_e2e.py` → `tests/e2e/test_goal_lifecycle_e2e.py`
  - Scaffold instance, seed profile with 3 topics at varying mastery/freshness
  - Seed goal with all 3 topics (1 completed, 1 active, 1 spawned)
  - Stipulated prompt: pause the goal, then resume it
  - Between pause and resume, mutate timestamps to simulate time passing
  - Assert: goal file shows pause then active status
  - Assert: profile validates, agent identifies stale topics on resume
- [ ] T2: Run full test suite → verify (depends: T1)
- [ ] T3: Mark plan done, add to plans index (depends: T2)

## Acceptance Criteria

- [ ] AC1: E2E test passes with Kiro
- [ ] AC2: Goal file shows status transitions (active → paused → active)
- [ ] AC3: Test skips cleanly when no LLM tool is available
- [ ] AC4: Full test suite green
