---
protocol: challenger
spec: docs/specs/behavioral-modes.md
status: golden
date: 2026-04-25
fixtures:
  - name: no-praise-tokens
    what_it_pins: |
      personality.md baseline — challenger mode is uniquely susceptible
      to praise-laden softening when the problem is hard ("Great attempt!").
      Forbidden across the board.
    forbidden_phrases:
      - "Great attempt"
      - "Great try"
      - "Nice work"
      - "Well done"
      - "Excellent"
      - "Awesome"
      - "Fantastic"
      - "Don't worry"
      - "It's okay if"
  - name: poses-problem-not-solution
    what_it_pins: |
      The challenger overlay's job is to pose harder problems and remain
      silent while the learner produces an attempt — productive failure.
      At least one mentor turn must contain a problem-shaped phrase
      (constraints, success criteria, or a request for the learner's
      attempt) rather than a worked solution.
    required_one_of:
      - "(?i)constraint"
      - "(?i)success criteria"
      - "(?i)return"
      - "(?i)algorithm"
      - "(?i)complexity"
      - "(?i)attempt"
      - "(?i)pseudocode"
      - "(?i)go\\."
  - name: no-solution-leak
    what_it_pins: |
      Challenger must not hand the learner the answer mid-problem. The
      transcript must not contain phrases that pre-spoil the algorithm
      ("the answer is", "the trick is to", "use a hash map and").
    forbidden_phrases:
      - "the answer is"
      - "the trick is"
      - "the solution is"
      - "Here's how to solve it"
      - "I'll show you the answer"
    silence_ratio:
      # Calibrated against challenger.dogfood.md (observed 0.48). The
      # challenger mode is intentionally near-balanced — mentor poses,
      # learner reasons at length. Ceiling 0.65 catches a regression
      # where the challenger walks through the solution itself.
      max: 0.65
---

# Challenger Protocol — Transcript Fixtures

Tier-1 lexical assertions for `src/sensei/engine/protocols/challenger.md`
and the challenger behavioral mode. Pairs with `challenger.dogfood.md` —
a captured session where a learner with mastered foundational topics
asks the mentor to make the work harder.

## Fixture: no-praise-tokens

Details in frontmatter.

## Fixture: poses-problem-not-solution

Details in frontmatter.

## Fixture: no-solution-leak

Details in frontmatter.
