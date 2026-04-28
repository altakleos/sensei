---
protocol: reviewer
actor: MENTOR
turn_format: bracket
required_one_of:
  - '(?i)bug'
  - '(?i)issue'
  - '(?i)incorrect'
  - '(?i)wrong'
  - '(?i)broken'
  - '(?i)breaks'
  - '(?i)destroys'
  - '(?i)corrupts'
  - '(?i)infinite loop'
  - '(?i)crash'
word_share:
  min: 0.5
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
# Fidelity fixture: identifies-defect

The reviewer mode's job is to surface defects, not to summarise.
The dogfood transcript contains a real bug (linked-list reverse
that destroys its traversal); the mentor must flag it. At least
one mentor turn must contain a defect signal — explicit (`bug`,
`issue`, `incorrect`, `breaks`, `wrong`) or operational (`crash`,
`error`, `infinite loop`).

Migrated from sensei fixture `reviewer.md::identifies-defect`.
