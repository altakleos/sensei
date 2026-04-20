---
status: accepted
date: 2026-04-20
id: P-know-the-learner
kind: pedagogical
---
# Know the Learner, Not Just the Subject

## Statement

Adaptation to the individual is not a feature of the product — it is the entire point. Two learners studying the same topic need completely different approaches.

## Rationale

One learner thinks in code examples; the other needs the abstract concept first. One rushes and makes careless errors; the other overthinks and never starts. A mentor that treats them identically fails both. This goes beyond "learning styles" — it is about detecting frustration before it becomes disengagement, noticing that *this* learner always struggles with *this* type of mistake, understanding that *this* one needs to build something real to stay motivated while *that* one needs theoretical grounding first.

Per `PRODUCT-IDEATION.md` §7.1's meta-insight, this is the *meta-pillar* that governs how all other principles apply. The same system with the same principles behaves completely differently for a senior engineer re-entering interview preparation than for a fresh graduate — not because the principles change, but because knowing the learner is what tells the mentor which dial to turn for this person right now.

## Implications

- The learner profile (`docs/specs/learner-profile.md`) is first-class state, not a cached inference. It is the authority every pedagogical decision consults.
- Adaptation operates across sessions via the persistent profile, not just within a session via context window.
- Personas (`docs/foundations/personas/`) are design stressors — their role is to ensure the other principles bend correctly under different learner shapes.
- Cross-goal intelligence: knowledge the learner has built in one goal transfers as context into any new goal, not re-gathered.

## Exceptions / Tensions

- Filter-bubble risk: always matching a learner's preferred modality produces a narrow, fragile understanding. "Anti-personalization" is occasionally the right move — force the wrong modality specifically because it forces deeper processing. See `PRODUCT-IDEATION.md` §2.4.4 (Personalization Paradox).
- This is the principle that *constrains* the others rather than competing with them. When two pillars conflict for a specific learner, the tiebreak is: what does knowing *this* learner tell us?

## Source

`PRODUCT-IDEATION.md` §2.2 Pillar 7 and §7.1 (meta-pillar insight). Self-Determination Theory (Ryan & Deci) on individual variation in motivational needs.
