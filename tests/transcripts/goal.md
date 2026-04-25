---
protocol: goal
spec: docs/specs/goal-lifecycle.md
status: golden
date: 2026-04-25
fixtures:
  - name: no-praise-tokens
    what_it_pins: |
      personality.md baseline — applies to every protocol including goal
      setting.
    forbidden_phrases:
      - "Great question"
      - "Great choice"
      - "Nice goal"
      - "Excellent"
      - "Awesome"
      - "Fantastic"
      - "I'm so excited"
      - "I love this"
  - name: probes-not-templates
    what_it_pins: |
      The goal protocol elicits the three-unknowns or target-depth (or
      both) from the conversation rather than handing the learner a
      pre-baked plan. At least one mentor turn must either (a) ask a
      probing question or (b) reflect captured state ("8 weeks", "L6",
      "saved", "depth") — i.e. the mentor demonstrates uptake before
      committing to scope.
    required_one_of:
      - "\\?"
      - "(?i)goal saved"
      - "(?i)target depth"
      - "(?i)8 weeks"
      - "(?i)l6"
      - "(?i)prior"
      - "(?i)constraint"
    silence_ratio:
      # Calibrated against goal.dogfood.md (observed 0.72). The goal
      # protocol is mentor-heavy in the rubric-and-probe phase but the
      # learner contributes substantively in clarification turns. Ceiling
      # 0.85 catches a regression where goal-setting devolves into a
      # mentor monologue with no learner input.
      max: 0.85
---

# Goal Protocol — Transcript Fixtures

Tier-1 lexical assertions for `src/sensei/engine/protocols/goal.md`.
Pairs with `goal.dogfood.md` — a captured session where a learner with
no prior expertise opens with a multi-week interview prep goal and the
mentor probes for the three-unknowns / target-depth.

## Fixture: no-praise-tokens

Details in frontmatter.

## Fixture: probes-not-templates

Details in frontmatter.
