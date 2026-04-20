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

Still open (resolve before T2 design):
2. Single protocol that owns read-ask-classify-write, or split into `review.md` + `record-response.md`? Leaning: one protocol at v1.
3. Does review need a new helper to propose the retrieval question, or is that left to the LLM's discretion (prose guidance only)? Leaning: prose-only for v1; the question-generation problem is too open to pin down in a helper yet.

## Tasks

### Phase 0 — Prerequisite

- [x] T0: Update `sensei init` to seed a minimal valid `profile.yaml` (schema_version 0, empty expertise_map, learner_id from `--learner-id` flag defaulting to `learner`) → `src/sensei/cli.py`, `tests/test_init.py`
  - *Split out and shipped as a standalone change ahead of the rest of this plan (43/43 tests passing).*

### Phase 1 — Specify

- [x] T1: Spec `docs/specs/review-protocol.md` — retrieval-only; stale-first; one topic at a time; no reteach inside review; single-writer post-question; learner-exit-anytime → `docs/specs/review-protocol.md`

### Phase 2 — Design

- [ ] T2: Design `docs/design/review-protocol.md` — the orchestration prose, step numbering convention, helper invocation contract, error handling (profile invalid mid-session), silence profile per PRODUCT-IDEATION §3.10 (depends: T1) → `docs/design/review-protocol.md`

### Phase 3 — Implement the protocol

- [ ] T3: Write `src/sensei/engine/protocols/review.md` as prose-as-code (numbered steps, config references, shell invocations in fenced blocks, tone calibration) (depends: T2) → `src/sensei/engine/protocols/review.md`
- [ ] T4: If T2 surfaces a need: add a helper to pick the next-due topic from decay output (e.g., `scripts/next_due_topic.py`). Otherwise defer.

### Phase 4 — Verify

- [ ] T5: Acceptance tests — integration-ish: synthesize a profile with several topics at varying freshness, run the helpers in the sequence the protocol specifies, assert the expected behavioural properties (stale-first ordering, no reteach before retrieval, state write-back passes validation) → `tests/protocols/test_review.py`
- [ ] T6: Update `engine.md` dispatch table to reflect that `review.md` is the first populated entry (depends: T3) → `src/sensei/engine/engine.md`

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
