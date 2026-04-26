---
protocol: review
spec: docs/specs/cross-goal-intelligence.md
status: golden
date: 2026-04-20
fixtures:
  - name: dedup-recursion
    what_it_pins: |
      Invariant 2 (globally coordinated spaced repetition): when two active
      goals both depend on 'recursion' and it is stale, the review queue
      must contain exactly one entry for 'recursion', not two. The mentor
      must not ask the learner to review the same topic twice in one session.
    forbidden_phrases:
      - "review recursion again"
      - "recursion (again)"
      - "second review of recursion"
      - "already reviewed recursion"
    required_one_of:
      - 'recursion'
    silence_ratio:
      # Calibrated against cross_goal_review.dogfood.md (observed 0.36).
      # Cross-goal review is Q&A — mentor asks, learner recalls. Ceiling
      # 0.55 catches the regression where the protocol starts narrating
      # the goal map instead of probing.
      max: 0.55
    question_density:
      # Calibrated against cross_goal_review.dogfood.md (observed 0.333).
      # Q&A protocol; some recall turns are statements ("you missed X")
      # that pull the average down below 1.0. Floor 0.2 catches the
      # regression where the protocol stops asking entirely (would be 0.0).
      min: 0.2
  - name: cross-goal-no-duplicate-queue
    what_it_pins: |
      The review queue presented to the learner must not list the same topic
      more than once, even when multiple goals share that topic. Duplicate
      entries would confuse the learner and waste session time.
    forbidden_phrases:
      - "recursion, recursion"
      - "recursion and recursion"
      - "recursion twice"
---

# Cross-Goal Review Deduplication — Transcript Fixtures

Tier-1 lexical assertions for cross-goal review deduplication (Invariant 2
of `docs/specs/cross-goal-intelligence.md`). Pairs with
`cross_goal_review.dogfood.md` — a captured session where a learner with
two active goals sharing "recursion" requests review.

## Fixture: dedup-recursion

Details in frontmatter.

## Fixture: cross-goal-no-duplicate-queue

Details in frontmatter.
