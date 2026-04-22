---
status: draft
date: 2025-07-14
realizes:
  - P-transfer-is-the-goal
  - P-forgetting-curve-is-curriculum
stressed_by:
  - persona-jacundu
fixtures_deferred: "awaiting implementation — no protocol performs interleaving yet"
---
# Interleaving

## Intent

Review sessions mix topics from different areas rather than presenting them in a single-topic sequence ordered only by staleness. Interleaving forces discriminative contrast — the learner must identify *which* concept or strategy applies before they can answer, rather than pattern-matching within a known category. This is the mechanism that converts retrieval practice from a retention tool into a transfer tool.

Without interleaving, a learner reviewing five stale topics from the same area answers each one in context: they know the category before they see the question. With interleaving, consecutive questions come from different areas, and the learner must first recognize the problem type. Meta-analyses find a moderate overall interleaving effect (g = 0.42; Brunmair & Richter, 2019, 59 studies), with individual classroom studies in mathematics showing larger effects on delayed tests (d = 0.79–0.83; Rohrer et al., 2015, 2020). The effect is strongest for procedural and problem-solving skills — precisely the domain Sensei operates in — and despite feeling harder during practice.

For the purposes of this spec, an *area* is a top-level branch of a curriculum DAG (within a single goal) or a distinct goal (across goals). For example, in a "system design" curriculum, "networking," "storage," and "distributed consensus" are separate areas. The grouping is structural (derived from the curriculum graph), not semantic. Interleaving alternates between areas at both levels.

## Invariants

- **Review sessions present topics from multiple areas.** When more than one area has stale topics, review alternates between areas rather than exhausting one area before moving to the next. A review session is not a single-topic sequence. Each retrieval prompt remains atomic — interleaving governs the order of single-topic prompts, not their composition. Within each area, stale-first ordering is preserved; interleaving alternates between areas but does not reorder topics within an area.
- **Interleaving applies during review and practice, not during initial instruction.** When the mentor is teaching a new topic for the first time, it uses blocked practice — focused, sustained engagement with one concept. Interleaving begins only after the learner has had initial exposure and the topic enters the review cycle. Block practice builds; interleaved practice transfers.
- **Interleaved items require discrimination.** The learner must identify which strategy, concept, or approach applies — interleaved retrieval prompts do not label their source topic or area. The pedagogical value of interleaving comes from this act of discrimination, not merely from variety.
- **Topics below a minimum mastery threshold are excluded from interleaving.** A topic the learner has barely encountered is not interleaved with mature topics. Novice-level topics receive blocked practice until they reach sufficient mastery to benefit from discriminative contrast rather than be overwhelmed by it. The minimum mastery threshold for interleaving eligibility is a configurable tunable, distinct from the summative assessment gate. It represents the point at which a topic has had enough initial exposure to benefit from discriminative contrast rather than continued blocked practice.
- **The degree of interleaving is configurable.** The learner or mentor can adjust how aggressively topics are mixed. At one extreme, review is fully interleaved across all eligible areas; at the other, it approaches the current stale-first single-area sequence. The default balances transfer benefit against cognitive load. The interleaving intensity is exposed as a tunable in the engine's configuration. At zero, review sequences topics by staleness alone (current behavior). At maximum, review fully alternates between all eligible areas.
- **Within-goal and cross-goal interleaving are both supported.** Topics from different areas within a single curriculum can be interleaved (within-goal), and topics from different active goals can be interleaved (cross-goal). Both levels produce discriminative contrast; cross-goal interleaving additionally surfaces connections the learner might not see when goals are reviewed in isolation. Within-goal interleaving operates independently and does not require cross-goal infrastructure. Cross-goal interleaving depends on the cross-goal-intelligence spec being accepted and the goal-lifecycle-transitions "at most one active goal" constraint being amended to permit multiple simultaneously active goals.
- **Mid-session teaching can weave in review of previously mastered concepts.** When the mentor is teaching new material and a previously mastered concept is contextually relevant, the mentor may pose a brief retrieval prompt for that concept before continuing instruction. This "review weaving" is opportunistic, not scheduled — it occurs when the teaching context creates a natural connection, not on a fixed cadence. This invariant codifies behavior already present in the tutor protocol's review-weaving trigger.

## Rationale

The forgetting-curve principle (P-forgetting-curve-is-curriculum) establishes that *when* to review is governed by decay. But decay-based scheduling says nothing about *what order* to present topics within a session. Stale-first selection solves priority; interleaving solves sequencing. They are complementary, not competing.

The transfer principle (P-transfer-is-the-goal) names interleaving as one of four behaviors the system must enact: "mix problem types and contexts rather than blocking by topic." Without interleaving, the system produces retention but not transfer — the learner can recall concepts when prompted by category but fails to recognize which concept applies in novel situations.

Rohrer et al. demonstrated that interleaved practice produces moderate-to-large effects compared to blocked practice — a meta-analysis of 59 studies found g = 0.42 overall (Brunmair & Richter, 2019), while pre-registered classroom trials in mathematics showed d = 0.83 on delayed tests (Rohrer et al., 2020). The mechanism is discriminative contrast: when problems from different categories are mixed, the learner must first identify the problem type before selecting a strategy. This identification step is precisely the skill that transfers to real-world application, where problems do not arrive pre-labeled.

Math Academy's implementation provides a practical insight: interleave *dissimilar* topics during initial learning (to prevent interference) but interleave *similar* topics during review (to force discrimination). This aligns with the invariant that initial instruction uses blocked practice while review uses interleaving.

FSRS and similar schedulers determine *when* each topic is due for review. Interleaving operates at a different layer — given a set of due topics, it determines the *order* in which they are presented within a session. These are independent concerns: the scheduler produces candidates, interleaving sequences them.

Students consistently perceive interleaved practice as harder and less effective than blocked practice, even when interleaving produces superior outcomes. The mentor must hold the line on interleaving despite learner discomfort, consistent with the transfer principle's acknowledgment that "practice that feels harder is actually working better."

## Out of Scope

- **The selection algorithm.** How interleaved items are chosen, grouped, or sequenced is a design and implementation concern. This spec guarantees that interleaving occurs, not how it is computed.
- **Cross-goal semantic transfer.** Recognizing that two goals share a foundational concept and coordinating mastery evidence across them is a separate concern (see `cross-goal-intelligence.md`). Interleaving may surface topics from multiple goals, but it does not reason about concept overlap or shared mastery.
- **Scheduler internals.** How the decay model, freshness computation, or review prioritization work is owned by the review protocol and its supporting design. Interleaving consumes the output of scheduling; it does not modify the scheduler.
- **Adaptive interleaving based on emotional state.** Adjusting interleaving intensity in response to detected frustration or disengagement is deferred. Interleaving at v1 does not adapt to affect.
- **Multi-topic questions.** A single retrieval prompt that requires synthesizing two topics simultaneously is a distinct pedagogical move from interleaving (which sequences single-topic prompts in mixed order). Multi-topic synthesis questions may build on interleaving but are not part of this spec.

## Specs Requiring Amendment

Accepting this spec requires updating the following:

- **review-protocol.md** — the stale-first ordering invariant must be reconciled with interleaved sequencing. Stale-first applies within each area; interleaving governs the order across areas. The "Multi-topic review questions" out-of-scope item should cross-reference this spec to distinguish multi-topic synthesis (still out of scope) from interleaved single-topic sequencing (now in scope).
- **curriculum-graph.md** — nodes must be associable with an area (top-level DAG branch). The current node model defines states and edges but has no area grouping.
- **P-forgetting-curve-is-curriculum** (principle) — currently states "Interleaving is a v2 concern." This spec promotes interleaving to v1. The principle's deferral note is superseded.

## Decisions

None yet.

## References

- [P-transfer-is-the-goal](../foundations/principles/transfer-is-the-goal.md) — names interleaving as one of four required transfer behaviors
- [P-forgetting-curve-is-curriculum](../foundations/principles/forgetting-curve-is-curriculum.md) — establishes decay-based scheduling that interleaving complements; deferred interleaving to v2 (now promoted)
- [Review Protocol spec](review-protocol.md) — currently lists "Multi-topic questions" as out of scope; interleaving modifies review's sequencing guarantees
- [Cross-Goal Intelligence spec](cross-goal-intelligence.md) — cross-goal interleaving depends on multi-goal coordination
- Brunmair, E. & Richter, T. (2019) — meta-analysis of 59 interleaving studies (g = 0.42 overall; *Psychological Bulletin*)
- Rohrer, D. et al. (2020) — pre-registered classroom RCT, 787 students (d = 0.83 on delayed test; *Journal of Educational Psychology*)
- Rohrer, D. et al. (2015) — classroom RCT, 126 students (d = 0.79 on delayed test; *Journal of Educational Psychology*)
- Math Academy — interleave dissimilar during learning, similar during review
