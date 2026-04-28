---
protocol: goal
actor: MENTOR
turn_format: bracket
forbidden_phrases:
  - "Here's a hint"
  - "Don't worry"
  - "Good try"
  - "Let me help"
required_one_of:
  - '(?i)rubric'
  - '(?i)scoring'
  - '(?i)you have \\d+ minutes'
---
# Fidelity fixture: simulated-evaluation-realism

Stage 5 assessor overlay applies evaluation realism — no hints,
rubric disclosed, clock visible.

Migrated from sensei fixture `performance_training.md::simulated-evaluation-realism`.
