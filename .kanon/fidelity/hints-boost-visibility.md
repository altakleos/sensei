---
protocol: hints
actor: MENTOR
turn_format: bracket
required_one_of:
  - 'boost'
  - 'prioritis'
  - 'priority'
  - 'ranked up'
  - 'moved .* (to the top|up)'
---
# Fidelity fixture: boost-visibility

ADR-0018 named "subtle influence" as the known risk of additive boosting:
if the LLM silently boosts curriculum priority without telling the
learner, they never discover why next session feels different. The mentor
MUST surface which topic(s) got boosted, or name the mechanism explicitly.

Migrated from sensei fixture `hints.md::boost-visibility`.
