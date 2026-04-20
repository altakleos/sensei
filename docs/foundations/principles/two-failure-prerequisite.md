---
status: accepted
date: 2026-04-20
id: P-two-failure-prerequisite
kind: pedagogical
---
# Two Failures Mean a Missing Prerequisite

## Statement

After two failed attempts at the same concept, the problem is deeper than explanation style — it is a gap in the foundation. The mentor stops explaining and diagnoses the missing prerequisite.

## Rationale

The tension between "try different modalities" and Math Academy's insight that "one good explanation plus prerequisites outperforms many explanations" resolves at the count of two. One failure is normal — the learner may need a different angle. Two failures signal that no angle will work because the prerequisite knowledge is absent. A third explanation wastes time and erodes trust; diagnosis is the only productive move.

This aligns with the prerequisite-graph architecture (ADR-0006 v2 scope): when a learner fails twice, the system traverses the prerequisite graph to find the gap rather than generating another surface-level explanation.

## Implications

- Protocols track per-concept failure count within a session. At count=2, the protocol shifts from explanation to prerequisite diagnosis.
- Prerequisite diagnosis uses recognition probes: "Have you seen X before?" / "What happens when Y?" — quick checks that reveal whether the foundation is absent or merely rusty.
- The distinction between "rusty" (fast relearning, partial recognition, responds to brief cues) and "never learned" (no recognition, no partial recall) determines the remediation path: review for rusty, teach-from-scratch for never-learned.
- This principle overrides [P-productive-failure](productive-failure.md) at the two-failure boundary: productive failure is valuable for the first attempt, but a third attempt at the same concept without prerequisite repair is unproductive failure.

## Exceptions / Tensions

- For genuinely novel concepts with no prerequisite chain (e.g., a new programming language's syntax), two failures may indicate the explanation is bad, not that prerequisites are missing. The mentor should distinguish "concept with prerequisites" from "atomic fact" before applying this principle.
- Tensions with [P-ask-dont-tell](ask-dont-tell.md): after two failures, the mentor may need to *tell* (explain the prerequisite directly) rather than ask. The Socratic stance yields to the diagnostic stance when the learner lacks the knowledge to answer questions about the prerequisite.
- Tensions with [P-productive-failure](productive-failure.md): productive failure says "let them struggle." This principle says "two struggles is enough." They compose via the count threshold — struggle is productive until it isn't.

## Source

Technical Principle (original, §3.8 — The Two-Failure Principle). Math Academy's finding on explanation quality vs. prerequisite completeness (see `docs/research/synthesis/accelerated-performance.md`). The "rusty vs never-learned" detection framework from `src/sensei/engine/scripts/classify_confidence.py`.
