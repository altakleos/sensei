---
feature: e2e-review-protocol
serves: docs/specs/review-protocol.md
design: "Follows existing E2E test pattern + agent_runner abstraction"
status: in-progress
date: 2026-04-22
---
# Plan: Review Protocol E2E Test

Tier-2 E2E test for the review protocol. Seeds a profile with topics at
varying freshness, triggers review, asserts the LLM picks stale topics
and updates profile timestamps.

## Tasks

- [ ] T1: Create `tests/e2e/test_review_protocol_e2e.py` → `tests/e2e/test_review_protocol_e2e.py`
  - Scaffold a fresh instance via `sensei init`
  - Seed `learner/profile.yaml` with 3+ topics: one stale (last_seen 10 days ago), one fresh (today), one medium (3 days ago)
  - Create a goal file in `learner/goals/` so the review protocol has curriculum context
  - Build prompt: read the fixture scenario, ask the agent to run a review session
  - Run via `run_agent()` from `agent_runner.py`
  - Assert: `last_seen` on the stale topic is updated (newer than before)
  - Assert: profile still validates against schema
  - Assert: agent stdout mentions the stale topic (retrieval-first selection)
- [ ] T2: Run full test suite — confirm green → verify (depends: T1)
- [ ] T3: Mark plan done, add to plans index → `docs/plans/README.md` (depends: T2)

## Acceptance Criteria

- [ ] AC1: E2E test passes with both Claude and Kiro (via agent_runner)
- [ ] AC2: Test seeds realistic profile state and verifies review updates it
- [ ] AC3: Test skips cleanly when no LLM tool is available
- [ ] AC4: Full test suite green
