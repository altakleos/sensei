---
feature: e2e-tutor-protocol
serves: docs/specs/behavioral-modes.md
design: "Follows existing E2E test pattern + agent_runner abstraction"
status: in-progress
date: 2026-04-22
---
# Plan: Tutor Protocol E2E Test

Tier-2 E2E test for the tutor protocol. Seeds a goal with an active topic,
triggers teaching, asserts the LLM enters tutor mode and updates the
learner profile with mastery/attempts data for the taught topic.

## Tasks

- [ ] T1: Create `tests/e2e/test_tutor_protocol_e2e.py` → `tests/e2e/test_tutor_protocol_e2e.py`
  - Scaffold a fresh instance via `sensei init`
  - Seed a goal with one active topic (e.g., 'binary-search') at `spawned` state
  - Seed profile with the topic at mastery `none`, attempts 0
  - Build prompt: ask the agent to teach the topic, provide a stipulated correct answer
  - Run via `run_agent()` from `agent_runner.py`
  - Assert: profile topic has attempts > 0 (teaching interaction occurred)
  - Assert: profile still validates against schema
- [ ] T2: Run full test suite — confirm green → verify (depends: T1)
- [ ] T3: Mark plan done, add to plans index → `docs/plans/README.md` (depends: T2)

## Acceptance Criteria

- [ ] AC1: E2E test passes with both Claude and Kiro (via agent_runner)
- [ ] AC2: Test verifies the tutor protocol updates the profile after teaching
- [ ] AC3: Test skips cleanly when no LLM tool is available
- [ ] AC4: Full test suite green
