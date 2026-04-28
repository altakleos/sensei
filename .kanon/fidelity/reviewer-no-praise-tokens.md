---
protocol: reviewer
actor: MENTOR
turn_format: bracket
forbidden_phrases:
  - "Looks great"
  - "Great code"
  - "Great work"
  - "Nice work"
  - "Well done"
  - "Excellent"
  - "Looks good to me"
  - "LGTM"
  - "Awesome"
  - "Fantastic"
---
# Fidelity fixture: no-praise-tokens

personality.md baseline. Code review is uniquely susceptible to
false-positive praise ("Looks great overall!") that softens real
defects.

Migrated from sensei fixture `reviewer.md::no-praise-tokens`.
