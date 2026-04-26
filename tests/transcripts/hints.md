---
protocol: hints
spec: docs/specs/hints.md
status: golden
date: 2026-04-21
fixtures:
  - name: triage-not-teaching
    what_it_pins: |
      During hints triage the mentor classifies and summarises; it does NOT
      teach, explain, or elaborate on the content of individual hints. Teaching
      leakage during triage violates the behavioural-modes spec — triage is an
      administrative operation, not a tutor interaction.
    forbidden_phrases:
      - "Let me explain"
      - "Here's why"
      - "To help you understand"
      - "Actually,"
      - "The answer is"
      - "What you need to know is"
      - "Think about"
    silence_ratio:
      # Calibrated against hints.dogfood.md (observed 0.84). Hints triage is
      # narrative by design — mentor lists items and outcomes — so the
      # ceiling sits well above the typical chat ratio. Catches the case
      # where triage devolves into per-item teaching (would push 0.95+).
      max: 0.95
    question_density:
      # Calibrated against hints.dogfood.md (observed 0.500). Triage is
      # narrative; some clarifying questions are normal but the protocol
      # should not interrogate. Ceiling 1.5 catches the regression where
      # triage devolves into per-item Q&A.
      max: 1.5
    teaching_density:
      # Calibrated against hints.dogfood.md (observed 0.000). Triage is
      # an administrative operation, not a tutor interaction — teaching
      # leakage during triage violates the behavioural-modes spec.
      # Complements the triage-not-teaching forbidden_phrases list above.
      max: 0.0
  - name: concise-summary
    what_it_pins: |
      Per docs/specs/hints.md, the learner sees triage results as counts and
      outcomes — not per-item commentary. After triage completes, the mentor
      emits a short summary line.
    required_one_of:
      - 'processed \d+'
      - '\d+ hint'
      - 'archived'
      - 'boosted'
      - 'registered'
  - name: boost-visibility
    what_it_pins: |
      ADR-0018 named "subtle influence" as the known risk of additive boosting:
      if the LLM silently boosts curriculum priority without telling the
      learner, they never discover why next session feels different. The mentor
      MUST surface which topic(s) got boosted, or name the mechanism explicitly.
    required_one_of:
      - 'boost'
      - 'prioritis'
      - 'priority'
      - 'ranked up'
      - 'moved .* (to the top|up)'
  - name: ambiguity-classification
    what_it_pins: |
      ADR-0019's universal-inbox-with-LLM-triage bet has a known gap: genuinely
      unclassifiable content. The protocol must either ask the learner to
      clarify OR explicitly flag the item as unresolved — never silently drop.
    required_one_of:
      - 'not sure'
      - 'unclassif'
      - 'unclear'
      - 'flagged for review'
      - 'need.* clarif'
      - 'What.*about\?'
      - '\?$'
---

# Hints Triage Protocol — Fixtures

Tier-1 lexical assertions for `src/sensei/engine/protocols/hints.md`. Pairs with `hints.dogfood.md` (synthetic seed at v0.1.0a9; real captured session owed at the next release per `docs/design/transcript-fixtures.md` § Cadence).

The invariants pinned here close the review triggers for ADR-0017 (file-drop ingestion), ADR-0018 (curriculum boosting — specifically the "subtle influence" consequence), and ADR-0019 (universal inbox — the classify-at-triage bet). Seeing all four fixtures pass against a coherent hints session is what graduates those ADRs from `provisional` back to `accepted`.
