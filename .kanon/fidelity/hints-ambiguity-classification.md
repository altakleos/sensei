---
protocol: hints
actor: MENTOR
turn_format: bracket
required_one_of:
  - 'not sure'
  - 'unclassif'
  - 'unclear'
  - 'flagged for review'
  - 'need.* clarif'
  - 'What.*about\?'
  - '\?$'
---
# Fidelity fixture: ambiguity-classification

ADR-0019's universal-inbox-with-LLM-triage bet has a known gap: genuinely
unclassifiable content. The protocol must either ask the learner to
clarify OR explicitly flag the item as unresolved — never silently drop.

Migrated from sensei fixture `hints.md::ambiguity-classification`.
