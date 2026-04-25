---
protocol: assessment
spec: docs/specs/assessment-protocol.md
status: golden
date: 2026-04-20
fixtures:
  - name: assessor-silence
    what_it_pins: |
      During summative assessment (Steps 2-6), the assessor speaks only to
      pose questions, acknowledge responses, and report the gate result.
      Praise, encouragement, and elaboration are forbidden.
    forbidden_phrases:
      - "Great"
      - "Nice work"
      - "Well done"
      - "Good job"
      - "Excellent"
      - "That's correct"
      - "You're doing well"
      - "Keep it up"
    required_one_of:
      - 'Got it\.'
      - 'Okay\.'
      - 'One more\.'
      - 'Let me see where you are'
    silence_ratio:
      # Calibrated against assess.dogfood.md (observed 0.66). Ceiling of
      # 0.80 catches a regression where the assessor starts teaching
      # (typical teaching-mode word-share is 0.85+).
      max: 0.80
  - name: no-teaching-during-assessment
    what_it_pins: |
      The assessor exception is absolute. During summative assessment, the
      mentor never teaches, hints, explains, or scaffolds. This is the
      hardest behavioral constraint in the system.
    forbidden_phrases:
      - "Let me explain"
      - "Here's a hint"
      - "Think about"
      - "Remember that"
      - "The answer is"
      - "Actually, "
      - "To help you"
      - "Consider"
      - "What if I told you"
  - name: gate-result-reported
    what_it_pins: |
      After the mastery gate runs, the mentor reports the result in one
      sentence. Pass = "You've demonstrated solid mastery of [topic]."
      Fail triggers either another question or prerequisite diagnosis.
    required_one_of:
      - "demonstrated.*mastery"
      - "Ready to move forward"
      - "Two misses"
      - "needs attention first"
      - 'One more\.'
  - name: two-failure-diagnosis
    what_it_pins: |
      After two failures at the same topic, the protocol shifts to
      prerequisite diagnosis rather than posing a third question. The
      mentor says "Two misses on [topic]. Let me check what's underneath."
    required_all_of:
      - "Two misses"
      - "underneath"
---

# Assessment Protocol — Dogfood Transcript

> Paste a real assessment session transcript below this line for CI verification.
> The transcript must contain `[MENTOR]` and `[LEARNER]` turn markers.
> See `tests/transcripts/conftest.py` for the loader.
