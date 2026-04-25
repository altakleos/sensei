---
feature: real-dogfood-capture
serves: docs/design/transcript-fixtures.md
design: "Follows ADR-0011"
status: done
date: 2026-04-22
---
# Plan: Real Dogfood Capture

Replace the three synthetic-seed `.dogfood.md` transcripts (hints, assess, review)
with real LLM-captured sessions, fulfilling the obligation documented in
`docs/design/transcript-fixtures.md § Cadence`.

## Approach

Build a multi-turn capture script that:
1. Scaffolds a sensei environment (reusing E2E patterns)
2. Seeds profile + goal state appropriate for each protocol
3. Sends a learner prompt → captures mentor response → sends follow-up → captures again
4. Formats the exchange as `[MENTOR]/[LEARNER]` turn-marked dogfood markdown
5. Writes `.dogfood.md` with real frontmatter (agent, model, status: captured)
6. Validates against existing fixture invariants

## Tasks

- [x] T1: Create `tests/e2e/capture_dogfood.py` — multi-turn capture harness
  - Reuse `agent_runner.run_agent()` for LLM invocation
  - Reuse E2E scaffold pattern (sensei init + seed profile + seed goal)
  - Implement multi-turn loop: send prompt, capture response, send follow-up
  - Post-process raw LLM output into `[MENTOR]/[LEARNER]` format
  - Write `.dogfood.md` with proper frontmatter
  - Support `--protocol hints|assess|review|all` flag
  - Support `--dry-run` to show what would be captured without writing

- [x] T2: Define capture scenarios for each protocol
  - **hints**: Seed inbox with 4 items (matching existing fixture expectations), prompt mentor to triage
  - **assess**: Seed profile with a topic ready for assessment, prompt mentor to assess, provide a learner answer
  - **review**: Seed profile with stale topics, prompt mentor to review, provide learner answers

- [x] T3: Run capture against real LLM, replace synthetic seeds
  - Execute `capture_dogfood.py --protocol all`
  - Replace `tests/transcripts/hints.dogfood.md`
  - Replace `tests/transcripts/assess.dogfood.md`
  - Replace `tests/transcripts/review.dogfood.md`

- [x] T4: Validate — all transcript fixture tests pass
  - `pytest tests/transcripts/ -v`
  - If any fixture fails, diagnose: is it the LLM output or the fixture calibration?

- [x] T5: Full verification — `pytest` + `ruff` + `mypy`

## Acceptance Criteria

- [x] AC1: All three `.dogfood.md` files have `status: captured` and a real agent/model
- [x] AC2: `pytest tests/transcripts/` passes with the real transcripts
- [x] AC3: Full test suite passes (`pytest`)
- [x] AC4: capture_dogfood.py is a reusable script for future release cadence captures
