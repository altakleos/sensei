---
protocol: review
actor: MENTOR
turn_format: bracket
forbidden_phrases:
  - "review recursion again"
  - "recursion (again)"
  - "second review of recursion"
  - "already reviewed recursion"
required_one_of:
  - 'recursion'
word_share:
  max: 0.55
pattern_density:
  - pattern: '(?<!\?)\?(?=\s|$|[.!?,;])'
    strip_code_fences: true
    min: 0.2
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
# Fidelity fixture: dedup-recursion

Invariant 2 (globally coordinated spaced repetition): when two active
goals both depend on 'recursion' and it is stale, the review queue
must contain exactly one entry for 'recursion', not two. The mentor
must not ask the learner to review the same topic twice in one session.

Migrated from sensei fixture `cross_goal_review.md::dedup-recursion`.
