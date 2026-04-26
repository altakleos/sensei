---
protocol: reviewer
spec: docs/specs/behavioral-modes.md
status: golden
date: 2026-04-25
fixtures:
  - name: no-praise-tokens
    what_it_pins: |
      personality.md baseline. Code review is uniquely susceptible to
      false-positive praise ("Looks great overall!") that softens real
      defects.
    forbidden_phrases:
      - "Looks great"
      - "Great code"
      - "Great work"
      - "Nice work"
      - "Well done"
      - "Excellent"
      - "Looks good to me"
      - "LGTM"
      - "Awesome"
      - "Fantastic"
  - name: identifies-defect
    what_it_pins: |
      The reviewer mode's job is to surface defects, not to summarise.
      The dogfood transcript contains a real bug (linked-list reverse
      that destroys its traversal); the mentor must flag it. At least
      one mentor turn must contain a defect signal — explicit (`bug`,
      `issue`, `incorrect`, `breaks`, `wrong`) or operational (`crash`,
      `error`, `infinite loop`).
    required_one_of:
      - "(?i)bug"
      - "(?i)issue"
      - "(?i)incorrect"
      - "(?i)wrong"
      - "(?i)broken"
      - "(?i)breaks"
      - "(?i)destroys"
      - "(?i)corrupts"
      - "(?i)infinite loop"
      - "(?i)crash"
    silence_ratio:
      # Calibrated against reviewer.dogfood.md (observed 0.84). Reviewer
      # mode IS narrative by design — feedback is the deliverable. The
      # floor catches the regression where the mentor returns "looks
      # fine" with no actual review (mentor word-share would drop into
      # the brief-acknowledgement range, ~0.30 typical).
      min: 0.50
    question_density:
      # Calibrated against reviewer.dogfood.md (observed 0.500). Feedback
      # is the deliverable — the reviewer narrates findings, not probes.
      # Some clarifying questions are normal but heavy questioning would
      # mean the reviewer is doing the wrong job. Ceiling 1.5 catches
      # over-questioning regressions.
      max: 1.5
    teaching_density:
      # Calibrated against reviewer.dogfood.md (observed 0.000). Code
      # review surfaces defects — feedback, not teaching. A reviewer
      # that explains the correct fix in didactic prose has slipped
      # into tutor mode. Catches that drift.
      max: 0.0
---

# Reviewer Protocol — Transcript Fixtures

Tier-1 lexical assertions for `src/sensei/engine/protocols/reviewer.md`
and the reviewer behavioral mode. Pairs with `reviewer.dogfood.md` —
a captured session where a learner submits a buggy linked-list reverse
function for review.

## Fixture: no-praise-tokens

Details in frontmatter.

## Fixture: identifies-defect

Details in frontmatter.
