---
feature: fix-profile-writes
serves: docs/specs/learner-profile.md
design: "Follows ADR-0006 — protocol prose constrains LLM behavior"
status: done
date: 2026-04-22
---
# Plan: Constrain Profile Writes in Challenger + Reviewer Protocols

E2E tests revealed that the challenger and reviewer protocols don't
explicitly constrain which profile fields the LLM may write. The LLM
hallucinated `challenge_log` and `review_patterns` fields that violate
the schema's `additionalProperties: false`.

Fix: add explicit "Profile Update" sections to both protocols listing
the exact fields the LLM may modify, matching the schema.

## Tasks

- [x] T1: Add profile write constraints to `protocols/challenger.md` → `src/sensei/engine/protocols/challenger.md`
- [x] T2: Add profile write constraints to `protocols/reviewer.md` → `src/sensei/engine/protocols/reviewer.md`
- [x] T3: Run full test suite → verify (depends: T1, T2)

## Acceptance Criteria

- [x] AC1: Challenger and reviewer E2E tests pass (LLM no longer adds extra fields)
- [x] AC2: Protocol prose explicitly names the allowed profile fields
- [x] AC3: Full test suite green
