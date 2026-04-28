---
protocol: goal
actor: MENTOR
turn_format: bracket
required_one_of:
  - '\?'
  - '(?i)goal saved'
  - '(?i)target depth'
  - '(?i)8 weeks'
  - '(?i)l6'
  - '(?i)prior'
  - '(?i)constraint'
word_share:
  max: 0.85
pattern_density:
  - pattern: '(?<!\?)\?(?=\s|$|[.!?,;])'
    strip_code_fences: true
    min: 0.5
    max: 4.0
---
# Fidelity fixture: probes-not-templates

The goal protocol elicits the three-unknowns or target-depth (or
both) from the conversation rather than handing the learner a
pre-baked plan. At least one mentor turn must either (a) ask a
probing question or (b) reflect captured state ("8 weeks", "L6",
"saved", "depth") — i.e. the mentor demonstrates uptake before
committing to scope.

Migrated from sensei fixture `goal.md::probes-not-templates`.
