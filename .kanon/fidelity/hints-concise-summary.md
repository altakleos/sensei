---
protocol: hints
actor: MENTOR
turn_format: bracket
required_one_of:
  - 'processed \d+'
  - '\d+ hint'
  - 'archived'
  - 'boosted'
  - 'registered'
---
# Fidelity fixture: concise-summary

Per docs/specs/hints.md, the learner sees triage results as counts and
outcomes — not per-item commentary. After triage completes, the mentor
emits a short summary line.

Migrated from sensei fixture `hints.md::concise-summary`.
