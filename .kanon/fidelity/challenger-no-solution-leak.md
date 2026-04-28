---
protocol: challenger
actor: MENTOR
turn_format: bracket
forbidden_phrases:
  - "the answer is"
  - "the trick is"
  - "the solution is"
  - "Here's how to solve it"
  - "I'll show you the answer"
word_share:
  max: 0.65
pattern_density:
  - pattern: '(?<!\?)\?(?=\s|$|[.!?,;])'
    strip_code_fences: true
    min: 1.0
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
# Fidelity fixture: no-solution-leak

Challenger must not hand the learner the answer mid-problem. The
transcript must not contain phrases that pre-spoil the algorithm
("the answer is", "the trick is to", "use a hash map and").

Migrated from sensei fixture `challenger.md::no-solution-leak`.
