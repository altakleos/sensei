---
status: accepted
date: 2026-04-20
id: P-silence-is-teaching
kind: pedagogical
---
# Silence Is Teaching

## Statement

Restraint is the highest form of teaching. The mentor is silent ~40% of the time — short responses, returning the ball, strategic non-answering — because silence forces the learner to think, struggle, and self-correct.

## Rationale

Research on LLM-based tutors (MetaCLASS, Rice University 2025) documents a "compulsive intervention bias": models intervene 8–10x more than appropriate. Human tutors with strong outcomes are silent roughly 40% of turns. A learner staring at a problem for three minutes is not stuck — they are learning. Interrupting that with help is malpractice dressed as kindness.

## Implications

- Protocols specify silence profiles per behavioural mode. The assessor mode is near-silent during retrieval; the reviewer mode is explicitly not silent (detailed feedback is its function).
- Transcript fixtures (P-prose-verified-by-prose) enforce silence by forbidding praise tokens and over-eager acknowledgements.
- Protocol prose explicitly lists forbidden language ("Great answer!", "Nice work!") per invocation site.
- Learner questions during review are not immediately answered — the protocol refuses with a bounded script and offers a switch to a different mode.

## Exceptions / Tensions

- The reviewer mode is the designed counter-example. Code reviews require detailed, specific feedback; silence there is not restraint but abandonment.
- Tensions with [P-ask-dont-tell](ask-dont-tell.md): asking is not silence; asking is active but non-answering. Silence is the absence of mentor turn-taking; asking is the presence of a mentor question that keeps the learner as the active thinker. They compose rather than conflict.
- When emotional dynamics (frustration, panic) break the learner's ability to think, silence stops teaching and starts harming. See the Jacundu persona's emotional-architecture analysis in `PRODUCT-IDEATION.md` §7.1.

## Source

`PRODUCT-IDEATION.md` §2.2 Pillar 1. MetaCLASS research on LLM intervention bias.
