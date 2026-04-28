---
protocol: tutor
actor: MENTOR
turn_format: bracket
required_one_of:
  - '\?'
  - '(?i)tell me'
  - '(?i)trace'
  - '(?i)consider'
  - '(?i)reason out'
  - '(?i)what (do|would) you'
word_share:
  max: 0.7
pattern_density:
  - pattern: '(?<!\?)\?(?=\s|$|[.!?,;])'
    strip_code_fences: true
    min: 0.4
---
# Fidelity fixture: socratic-not-monologue

The tutor protocol's Socratic stance — the mentor probes the learner's
mental model before explaining. At least one mentor turn must contain
a question (`?`) or a verb-phrased imperative that asks for learner
reasoning ("tell me", "trace", "consider").

Migrated from sensei fixture `tutor.md::socratic-not-monologue`.
