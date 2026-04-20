---
status: accepted
date: 2026-04-20
id: P-curriculum-is-hypothesis
kind: pedagogical
---
# Curriculum Is Hypothesis

## Statement

A curriculum is a hypothesis, not a plan. It is generated immediately as a biased draft, validated through teaching — not questionnaires — and reshaped continuously by evidence from learner performance. Accuracy at generation time is less important than responsiveness to interaction.

## Rationale

The traditional model treats curriculum as a fixed artifact: design it carefully, validate it with experts, then deliver it. This fails in adaptive tutoring because the information needed to build a good curriculum — what the learner knows, what "done" means to them, how they learn — can only be revealed through interaction, not upfront elicitation.

Sensei's model inverts this. A draft curriculum is generated immediately upon hearing the goal, biased toward the 70th-percentile learner for that domain. This draft is intentionally imprecise but usefully wrong: reacting to a concrete draft is 10× easier than answering abstract questions about yourself. The first lesson IS the assessment — the learner's performance on early topics reveals prior knowledge, misconceptions, and pace far more reliably than self-report ever could.

The curriculum then evolves incrementally. Nodes collapse when the learner demonstrates mastery, expand when granularity is needed, and spawn when gaps are discovered that the original graph missed. The graph is never regenerated wholesale — that would be disorienting. It is reshaped by evidence, one interaction at a time.

This stance dissolves the cold-start problem. There is no onboarding phase, no intake questionnaire, no "tell me about yourself" preamble. The mentor listens to the goal, generates a hypothesis, and starts teaching. Calibration happens through performance, not conversation about performance.

## Implications

- Curriculum generation happens at goal creation, not after an assessment phase. There is no separate onboarding step.
- The generated curriculum accepts ~80% accuracy as sufficient for well-defined domains. Errors are expected and self-correct through interaction.
- Curriculum mutations are incremental (collapse, expand, spawn) — never full regeneration.
- Validation effort scales with uncertainty: well-defined domains tolerate imprecision; vague targets require more probing before the hypothesis stabilizes.
- Protocols must treat the curriculum as mutable state, not a fixed reference. Any protocol that reads the curriculum must tolerate that it has changed since last read.

## Exceptions / Tensions

- Tensions with quality expectations: stakeholders accustomed to expert-curated curricula may perceive an 80%-accurate generated graph as sloppy. Resolution: accuracy is a property of the steady state, not the initial state. The hypothesis converges through use.
- Tensions with [P-mastery-before-progress](mastery-before-progress.md): if the curriculum hypothesis is wrong about prerequisites, the learner may be asked to demonstrate mastery of a topic that shouldn't be on their path. Resolution: mastery checks on incorrectly placed topics naturally trigger collapse or restructuring — the error is self-correcting.
- For domains where the learner has near-zero prior knowledge, the 70th-percentile bias may overshoot badly. The first few interactions will produce rapid downward calibration, which is acceptable but may feel discouraging. Protocols should interpret early struggle as calibration signal, not learner failure.

## Source

Technical Principle (original). Curriculum as constraint satisfaction (§5.1), Generate → Probe → Reshape model (§5.2), cold start dissolves when first lesson is assessment (§5.6), accuracy risk scales with domain certainty (§5.7). See `docs/specs/goal-lifecycle.md` and `docs/specs/curriculum-graph.md` for the decomposed specifications.
