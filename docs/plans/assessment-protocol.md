---
feature: assessment-protocol
serves: docs/specs/assessment-protocol.md
design: "Follows ADR-0006 (hybrid runtime) + docs/design/behavioral-modes.md (mode composition)"
status: done
date: 2026-04-21
---
# Plan: Assessment Protocol (retroactive)

Retroactive reconstruction — this plan documents work already shipped in v0.1.0a2.

The assessment protocol composes existing mechanisms (mastery_check.py, classify_confidence.py, behavioral-modes transition system) without introducing new architecture. Design doc skipped per § When to Skip a Design Doc: pattern instantiation (ADR-0006 helper invocation), single-concern (assessor mode boundary), spec carries reasoning (diagnostic/summative split, two-failure rule), plan exists (this file).

## Tasks

- [x] T1: Write assessment-protocol spec → `docs/specs/assessment-protocol.md`
- [x] T2: Write assess protocol prose → `src/sensei/engine/protocols/assess.md`
- [x] T3: Wire mastery_check.py into assess protocol (subprocess, exit code gating)
- [x] T4: Wire classify_confidence.py into assess protocol (4-quadrant classification)
- [x] T5: Implement two-failure prerequisite diagnosis branching in protocol
- [x] T6: Write transcript fixture → `tests/transcripts/assess.md`
- [x] T7: Write synthetic dogfood session → `tests/transcripts/assess.dogfood.md`

## Acceptance Criteria

- [x] AC1: Deterministic scoring via mastery_check.py (no LLM judgment on pass/fail)
- [x] AC2: Two-failure prerequisite diagnosis routes to tutor protocol
- [x] AC3: Assessor exception enforced (no teaching during assessment)
- [x] AC4: Transcript fixtures pass
