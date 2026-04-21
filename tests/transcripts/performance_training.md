---
protocol: goal
spec: docs/specs/performance-training.md
status: golden
date: 2026-04-21
fixtures:
  - name: phase-activates
    what_it_pins: |
      When a learner with solid mastery says they have a performance event,
      the performance phase activates. The mentor must confirm activation
      and reference stage 1. The phase is entered, not suggested.
    forbidden_phrases:
      - "Would you like to"
      - "Do you want me to"
      - "I can help you prepare"
      - "Let me know if"
    required_all_of:
      - "[Pp]erformance training is active"
      - "[Ss]tage 1"
  - name: format-aware-framing
    what_it_pins: |
      In stage 1, the Tutor overlay frames material in the shape the
      performance format demands. The mentor must reference the event
      format (interview, exam, certification) when teaching, not teach
      in generic form.
    required_one_of:
      - "interview"
      - "exam"
      - "certification"
  - name: no-time-pressure-stage-1
    what_it_pins: |
      Stage 1 has no time pressure. The mentor must not introduce clock
      references, time limits, or pacing pressure during stage 1.
    forbidden_phrases:
      - "minutes left"
      - "time is up"
      - "hurry"
      - "clock is ticking"
      - "you have 5 minutes"
      - "speed up"
---

# Performance Training — Transcript Fixtures

Tier-1 lexical assertions for performance-phase activation and stage-1
behavior (spec invariants 1–4 of `docs/specs/performance-training.md`).
Pairs with `performance_training.dogfood.md` — a captured session where a
learner with solid mastery on an active goal says "I have an interview in
two weeks" and the performance phase activates at stage 1.

## Fixture: phase-activates

Details in frontmatter.

## Fixture: format-aware-framing

Details in frontmatter.

## Fixture: no-time-pressure-stage-1

Details in frontmatter.
