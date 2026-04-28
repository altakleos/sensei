---
protocol: review
actor: MENTOR
turn_format: bracket
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
word_share:
  max: 0.75
pattern_density:
  - pattern: '(?<!\?)\?(?=\s|$|[.!?,;])'
    strip_code_fences: true
    min: 0.3
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
# Fidelity fixture: silence-profile

Step 8 permits only `Got it.` / `Okay.` / `Recorded.` / `Next.` as
acknowledgements. Praise and softening phrases are forbidden; the
dogfood transcript must contain at least one permitted
acknowledgement.

Migrated from sensei fixture `review.md::silence-profile`.
