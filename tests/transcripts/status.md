---
protocol: status
spec: docs/specs/behavioral-modes.md
status: golden
date: 2026-04-25
fixtures:
  - name: no-praise-tokens
    what_it_pins: |
      personality.md baseline — even a status report is forbidden from
      praise tokens or congratulatory framing.
    forbidden_phrases:
      - "Great progress"
      - "Awesome work"
      - "Nice job"
      - "Excellent"
      - "You're doing great"
      - "Keep up the great work"
      - "Fantastic"
      - "I'm proud"
  - name: structured-report
    what_it_pins: |
      Status surfaces concrete state. At least one mentor turn must
      contain an evidence signal — counts, mastery level names, freshness
      language, or topic identifiers from the seeded profile.
    required_one_of:
      - "(?i)mastered"
      - "(?i)solid"
      - "(?i)developing"
      - "(?i)stale"
      - "(?i)rusty"
      - "(?i)topic-[abc]"
      - "(?i)\\d+ of \\d+"
      - "(?i)\\d+/\\d+"
    silence_ratio:
      # Calibrated against status.dogfood.md (observed 0.93). Status is
      # mentor-reporting-by-design — the learner asks one short question.
      # Floor 0.50 catches the regression where status returns nothing
      # substantive (mentor brevity below 50% would mean the report
      # itself is missing).
      min: 0.50
---

# Status Protocol — Transcript Fixtures

Tier-1 lexical assertions for `src/sensei/engine/protocols/status.md`.
Pairs with `status.dogfood.md` — a captured session where a learner
asks "How am I doing?" against a seeded profile with mixed mastery
levels (mastered, solid, developing) and a stale topic.

## Fixture: no-praise-tokens

Details in frontmatter.

## Fixture: structured-report

Details in frontmatter.
