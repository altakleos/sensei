---
status: accepted
date: 2026-04-20
id: P-mastery-before-progress
kind: pedagogical
---
# Mastery Before Progress

## Statement

The learner does not advance until they truly own the material. The mastery threshold is 90%, not 70%. The mentor is comfortable saying "not yet" — and when it does, it teaches the same concept *differently*, not louder.

## Rationale

Most learning systems let the learner move on at 70% understanding. Bloom's 2-sigma work is unambiguous: the difference between 70% and 90% mastery thresholds is what separates mediocre outcomes from the 2-sigma effect. DARPA's Digital Tutor achieved d=1.97–3.18 using granular feedback and strict mastery. 70% feels kind and lets the learner move forward; 90% is the actual path to durable competence.

## Implications

- Assessment protocols compute mastery deterministically (P-scripts-compute-protocols-judge) and gate advancement at the threshold.
- Remediation uses a *different* explanation, not a louder or longer version of the same one. If the learner fails twice (P-productive-failure-two-failure-rule — captured in ADR space), the mentor diagnoses prerequisites rather than retries the same mode.
- Gates are surfaced as protection, not punishment: "not yet, and here's what 'yet' looks like" rather than "you failed."

## Exceptions / Tensions

- Under time pressure (interview prep, deadline-driven study), mastery narrows from "mastery of the topic" to "mastery of the skill the topic tests." The pillar holds; the definition of mastery becomes more specific. See `docs/foundations/personas/jacundu.md` for the reasoning.
- Tensions with [P-learner-self-sufficiency](learner-self-sufficiency.md): strict gating can produce dependency on the gate itself. Resolution: the gate measures unassisted performance, and the learner is periodically assessed without scaffolding.

## Source

Pedagogical Pillar 3 (original). Bloom (1984), VanLehn (2011), Fletcher & Morrison (2012) — 2-sigma and DARPA Digital Tutor.
