---
feature: first-protocol-review
serves: (spec to be written as T1)
design: (design to be written as T2)
status: planned
date: 2026-04-20
---
# Plan: First Protocol — `review.md`

The first real protocol. Exercises four of the five v1 helpers (`check_profile`, `decay`, `classify_confidence`, `mastery_check`) end-to-end in a concrete user-facing flow: at the start of a session, Sensei offers targeted review of topics whose freshness has dropped below the stale threshold, records the learner's responses, and updates the profile before moving on.

This plan is deliberately front-loaded with a spec and design task because `review.md` makes the first pedagogical guarantees that must survive future protocols.

## Open Questions

Resolved:
1. **What does "review" guarantee?** → **(a) Retrieval-only.** Spec captures the full invariants; see `docs/specs/review-protocol.md`.
4. **Seed profile during init — in this plan or separate?** → Shipped standalone ahead of this plan (commit `59decfb`).

Resolved during T2 design:
2. **Single protocol vs split** → single `review.md` owns the full cycle. No sub-protocol at v1.
3. **Question-generation helper** → prose-only at v1. LLM generates retrieval questions per the design's shape guidelines.

## Tasks

### Phase 0 — Prerequisite

- [x] T0: Update `sensei init` to seed a minimal valid `profile.yaml` (schema_version 0, empty expertise_map, learner_id from `--learner-id` flag defaulting to `learner`) → `src/sensei/cli.py`, `tests/test_init.py`
  - *Split out and shipped as a standalone change ahead of the rest of this plan (43/43 tests passing).*

### Phase 1 — Specify

- [x] T1: Spec `docs/specs/review-protocol.md` — retrieval-only; stale-first; one topic at a time; no reteach inside review; single-writer post-question; learner-exit-anytime → `docs/specs/review-protocol.md`

### Phase 2 — Design

- [x] T2: Design `docs/design/review-protocol.md` — nine-step orchestration, helper invocation contract, v1 update rule (last_seen/attempts/correct only; mastery/confidence deferred), error-handling table, config references (half_life_days, stale_threshold), silence profile, engine dispatch update (depends: T1) → `docs/design/review-protocol.md`

### Phase 3 — Implement the protocol

- [x] T3: `src/sensei/engine/protocols/review.md` — full prose-as-code with nine numbered steps, shell-subprocess helper invocations, stop-signal list, silence profile binding, error-handling table (depends: T2) → `src/sensei/engine/protocols/review.md`
- [x] T3b: Populate `defaults.yaml` with `memory.half_life_days: 7.0` and `memory.stale_threshold: 0.5` → `src/sensei/engine/defaults.yaml`
- [~] T4: **Not needed.** T2 design resolved the question-generation concern as "prose-only at v1"; no helper shipped. Deferred until a protocol actually needs deterministic question templating.

### Phase 4 — Verify

- [x] T5: Orchestration integration tests — synthesize profiles with varying freshness, drive helpers in protocol sequence, assert stale-first ranking, tie-break behaviour, v1 update rule preserves cross-field invariant, all four quadrants produce valid updates (8 tests) → `tests/scripts/test_review_protocol.py`
  - *Does not test LLM prose interpretation. Behavioural correctness of the protocol itself requires dogfood testing with a real LLM agent.*
- [x] T6: Update `engine.md` dispatch — review signals route to `protocols/review.md` (accepted); code-review intent re-assigned to future `protocols/review-code.md` → `src/sensei/engine/engine.md`

## Acceptance Criteria

- [ ] AC1: `docs/specs/review-protocol.md` and `docs/design/review-protocol.md` exist and cross-link
- [ ] AC2: `src/sensei/engine/protocols/review.md` exists, loads cleanly in Claude Code reading `AGENTS.md`, and the dispatch in `engine.md` reflects it
- [ ] AC3: Integration tests synthesize a profile and simulate a review session, asserting stale-first ordering and correct write-back
- [ ] AC4: `sensei init` seeds a valid `profile.yaml` that passes `sensei verify` (or `python scripts/check_profile.py`) immediately after `init`
- [ ] AC5: `sensei verify` and CI remain green (43+/43+ tests)
- [ ] AC6: Manual dogfood — open a test instance in Claude Code, boot via `AGENTS.md`, request review, observe that the protocol actually fires through the helpers

## Out of Scope

- Any mutation of goal state (goal folders) — this protocol is profile-only.
- FSRS-based scheduling. Decay arithmetic only per the v1 helper inventory.
- Multi-topic simultaneous review. One topic at a time; loop if user wants more.
- Affect detection and conversational pacing beyond what the protocol prose encodes directly.

## Notes

This is the moment Sensei stops being scaffolding and becomes product. Expect the spec and design phases to take longer than the implementation itself — that's a feature, not a bug.
