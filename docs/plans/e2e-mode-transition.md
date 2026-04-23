---
feature: e2e-mode-transition
serves: docs/specs/behavioral-modes.md
design: "Follows existing E2E test pattern + stipulated multi-turn prompt"
status: in-progress
date: 2026-04-22
---
# Plan: Multi-Turn Mode Transition E2E Test

First multi-turn E2E test. Verifies that the mentor transitions between
modes during a conversation — the core product differentiator. Uses a
single prompt with stipulated learner responses (same technique as the
assess E2E) to simulate a multi-turn session.

## Tasks

- [ ] T1: Create `tests/e2e/test_mode_transition_e2e.py` → `tests/e2e/test_mode_transition_e2e.py`
  - Scaffold instance, seed profile with topic at mastery `developing`, attempts 2
  - Seed goal with the topic as active
  - Build a multi-turn stipulated prompt:
    - Turn 1: "Teach me about [topic]" (triggers tutor)
    - Turn 2: Stipulated correct answer (tutor probes, learner answers well)
    - Turn 3: Stipulated second correct answer (should trigger mode shift)
    - Ask agent to update profile after each interaction and stop after 3 turns
  - Assert: attempts >= 4 (seed 2 + at least 2 interactions)
  - Assert: profile validates against schema
  - Assert: mastery progressed from `developing` (evidence of assessment/challenge)
- [ ] T2: Run full test suite — confirm green → verify (depends: T1)
- [ ] T3: Mark plan done, add to plans index (depends: T2)

## Acceptance Criteria

- [ ] AC1: E2E test passes with Kiro (via agent_runner)
- [ ] AC2: Profile shows evidence of multi-turn interaction (attempts >= 4)
- [ ] AC3: Test skips cleanly when no LLM tool is available
- [ ] AC4: Full test suite green
