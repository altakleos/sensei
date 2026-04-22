---
feature: e2e-challenger-reviewer
serves: docs/specs/behavioral-modes.md
design: "Follows existing E2E test pattern + agent_runner abstraction"
status: done
date: 2026-04-22
---
# Plan: Challenger + Reviewer Protocol E2E Tests

Tier-2 E2E tests for the two remaining protocols. Completes E2E coverage
of all six core protocols (goal, assess, review, hints, tutor, challenger,
reviewer).

## Tasks

### Challenger E2E

- [x] T1: Create `tests/e2e/test_challenger_protocol_e2e.py` → `tests/e2e/test_challenger_protocol_e2e.py`
  - Scaffold instance, seed profile with a topic at mastery `solid` (challenger targets mastered topics)
  - Seed goal with the topic as a completed node
  - Prompt: "Challenge me on [topic]. Push my limits."
  - Provide a stipulated answer that demonstrates understanding
  - Assert: agent exited 0, profile validates, topic attempts incremented

### Reviewer E2E

- [x] T2: Create `tests/e2e/test_reviewer_protocol_e2e.py` → `tests/e2e/test_reviewer_protocol_e2e.py`
  - Scaffold instance, seed profile with a topic at mastery `developing`
  - Seed goal with the topic as an active node
  - Prompt: "Review my solution: [provide a code snippet]. Give me feedback."
  - Assert: agent exited 0, profile validates, topic attempts incremented

### Finalize

- [x] T3: Run full test suite — confirm green → verify (depends: T1, T2)
- [x] T4: Mark plan done, add to plans index → `docs/plans/README.md` (depends: T3)

## Acceptance Criteria

- [x] AC1: Both E2E tests pass with Kiro (via agent_runner)
- [x] AC2: Tests skip cleanly when no LLM tool is available
- [x] AC3: Full test suite green
