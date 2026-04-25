---
protocol: tutor
spec: docs/specs/behavioral-modes.md
status: golden
date: 2026-04-25
fixtures:
  - name: no-praise-tokens
    what_it_pins: |
      personality.md forbids praise tokens, exclamation softeners, and
      apologetic openers. The tutor must convey approval through next-step
      direction, not adjective inflation.
    forbidden_phrases:
      - "Great question"
      - "Great job"
      - "Nice work"
      - "Well done"
      - "Excellent"
      - "Good question"
      - "Awesome"
      - "Fantastic"
      - "I'm sorry"
      - "Apologies"
  - name: socratic-not-monologue
    what_it_pins: |
      The tutor protocol's Socratic stance — the mentor probes the learner's
      mental model before explaining. At least one mentor turn must contain
      a question (`?`) or a verb-phrased imperative that asks for learner
      reasoning ("tell me", "trace", "consider").
    required_one_of:
      - "\\?"
      - "(?i)tell me"
      - "(?i)trace"
      - "(?i)consider"
      - "(?i)reason out"
      - "(?i)what (do|would) you"
    silence_ratio:
      # Calibrated against tutor.dogfood.md (observed 0.53). Ceiling 0.70
      # catches a regression where the tutor stops probing and starts
      # lecturing — that pattern pushes mentor word-share into the 0.85+
      # range typical of teaching-mode transcripts.
      max: 0.70
---

# Tutor Protocol — Transcript Fixtures

Tier-1 lexical assertions for `src/sensei/engine/protocols/tutor.md` and the
default behavioral mode at session start. Pairs with `tutor.dogfood.md` —
a captured session where a learner with `mastery: none` on `ownership`
asks the mentor to teach.

## Fixture: no-praise-tokens

Details in frontmatter.

## Fixture: socratic-not-monologue

Details in frontmatter.
