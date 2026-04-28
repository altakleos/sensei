---
protocol: goal
actor: MENTOR
turn_format: bracket
forbidden_phrases:
  - "Would you like to"
  - "Do you want me to"
  - "I can help you prepare"
  - "Let me know if"
required_all_of:
  - '[Pp]erformance training is active'
  - '[Ss]tage 1'
word_share:
  max: 0.95
pattern_density:
  - pattern: '(?<!\?)\?(?=\s|$|[.!?,;])'
    strip_code_fences: true
    max: 1.0
---
# Fidelity fixture: phase-activates

When a learner with solid mastery says they have a performance event,
the performance phase activates. The mentor must confirm activation
and reference stage 1. The phase is entered, not suggested.

Migrated from sensei fixture `performance_training.md::phase-activates`.
