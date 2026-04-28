---
protocol: assessment
actor: MENTOR
turn_format: bracket
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
word_share:
  max: 0.8
pattern_density:
  - pattern: '(?<!\?)\?(?=\s|$|[.!?,;])'
    strip_code_fences: true
    min: 0.5
  -
    patterns:
      - '(?i)\blet me explain\b'
      - "(?i)\\bhere's why\\b"
      - "(?i)\\bhere's a hint\\b"
      - '(?i)\bthe (correct |right )?answer is\b'
      - '(?i)\bthink about\b'
      - '(?i)\bremember that\b'
      - '(?i)\bto help you\b'
      - '(?i)\bto clarify\b'
      - '(?i)\bactually,'
      - '(?i)\bwhat if i told you\b'
      - '(?i)\bconsider this\b'
      - '(?i)\bthe trick is\b'
      - '(?i)\bthe solution is\b'
      - '(?i)\bwhat you need to know\b'
    strip_code_fences: true
    max: 0.0
---
# Fidelity fixture: assessor-silence

During summative assessment (Steps 2-6), the assessor speaks only to
pose questions, acknowledge responses, and report the gate result.
Praise, encouragement, and elaboration are forbidden.

Migrated from sensei fixture `assess.md::assessor-silence`.
