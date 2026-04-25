---
protocol: review
spec: docs/specs/review-protocol.md
status: golden
date: 2026-04-20
fixtures:
  - name: silence-profile
    what_it_pins: |
      Step 8 permits only `Got it.` / `Okay.` / `Recorded.` / `Next.` as
      acknowledgements. Praise and softening phrases are forbidden; the
      dogfood transcript must contain at least one permitted
      acknowledgement.
    forbidden_phrases:
      - "Great"
      - "Nice work"
      - "Well done"
      - "You're doing well"
      - "Fantastic"
      - "Awesome"
      - "That's correct"
      - "That's right"
    required_one_of:
      - '^Got it\.$'
      - '^Okay\.$'
      - '^Recorded\.$'
      - '^Next\.$'
    silence_ratio:
      # Calibrated against review.dogfood.md (observed 0.58). Ceiling 0.75
      # catches a regression where review starts re-teaching (which would
      # also trip the no-reteach forbidden_phrases below).
      max: 0.75
  - name: no-reteach
    what_it_pins: |
      Review never explains the correct answer inside the session. A
      reteach-on-miss would violate the retrieval-only spec invariant.
    forbidden_phrases:
      - "Let me explain"
      - "The correct answer is"
      - "Here's why"
      - "Actually, "
      - "To clarify"
      - "The right answer is"
  - name: retrieval-only-question
    what_it_pins: |
      Questions in step 5 must not prime the learner with framing or
      multiple choice. No "recall that", no "last time", no "(a) / (b)"
      style options.
    forbidden_phrases:
      - "Last time"
      - "Recall that"
      - "Remember when"
      - "Remember that"
      - "As you know"
  - name: sign-off
    what_it_pins: |
      Step 9 — the session must end with the prescribed sign-off exactly.
    required_all_of:
      - "That's it for now\\."
---

# Review protocol — transcript fixtures

Each `## Fixture:` in the frontmatter pins one cluster of invariants from
`docs/specs/review-protocol.md`. The fixtures file is paired with
`review.dogfood.md`, the captured session the loader runs these
assertions against.

## Fixture: silence-profile

Details in frontmatter.

## Fixture: no-reteach

Details in frontmatter.

## Fixture: retrieval-only-question

Details in frontmatter.

## Fixture: sign-off

Details in frontmatter.
