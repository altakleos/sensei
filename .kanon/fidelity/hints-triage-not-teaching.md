---
protocol: hints
actor: MENTOR
turn_format: bracket
forbidden_phrases:
  - "Let me explain"
  - "Here's why"
  - "To help you understand"
  - "Actually,"
  - "The answer is"
  - "What you need to know is"
  - "Think about"
word_share:
  max: 0.95
pattern_density:
  - pattern: '(?<!\?)\?(?=\s|$|[.!?,;])'
    strip_code_fences: true
    max: 1.5
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
# Fidelity fixture: triage-not-teaching

During hints triage the mentor classifies and summarises; it does NOT
teach, explain, or elaborate on the content of individual hints. Teaching
leakage during triage violates the behavioural-modes spec — triage is an
administrative operation, not a tutor interaction.

Migrated from sensei fixture `hints.md::triage-not-teaching`.
