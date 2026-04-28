---
protocol: assessment
actor: MENTOR
turn_format: bracket
required_one_of:
  - 'demonstrated.*mastery'
  - 'Ready to move forward'
  - 'Two misses'
  - 'needs attention first'
  - 'One more\.'
---
# Fidelity fixture: gate-result-reported

After the mastery gate runs, the mentor reports the result in one
sentence. Pass = "You've demonstrated solid mastery of [topic]."
Fail triggers either another question or prerequisite diagnosis.

Migrated from sensei fixture `assess.md::gate-result-reported`.
