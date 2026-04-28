---
protocol: status
actor: MENTOR
turn_format: bracket
required_one_of:
  - '(?i)mastered'
  - '(?i)solid'
  - '(?i)developing'
  - '(?i)stale'
  - '(?i)rusty'
  - '(?i)topic-[abc]'
  - '(?i)\d+ of \d+'
  - '(?i)\d+/\d+'
word_share:
  min: 0.5
pattern_density:
  - pattern: '(?<!\?)\?(?=\s|$|[.!?,;])'
    strip_code_fences: true
    max: 2.0
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
# Fidelity fixture: structured-report

Status surfaces concrete state. At least one mentor turn must
contain an evidence signal — counts, mastery level names, freshness
language, or topic identifiers from the seeded profile.

Migrated from sensei fixture `status.md::structured-report`.
