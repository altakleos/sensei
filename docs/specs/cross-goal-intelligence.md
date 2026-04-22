---
status: accepted
date: 2026-04-20
realizes:
  - P-transfer-is-the-goal
  - P-learner-is-not-the-goal
  - P-know-the-learner
  - P-forgetting-curve-is-curriculum
stressed_by:
  - persona-jacundu
fixtures:
  - tests/scripts/test_global_knowledge.py
  - tests/scripts/test_goal_priority.py
  - tests/test_cross_goal.py
---
# Cross-Goal Intelligence

## Intent

When a learner pursues multiple goals, knowledge and effort do not stay siloed. Foundational concepts learned in one goal transfer to another — even when the two goals name the concept differently. Spaced repetition schedules across goals compete for the same limited session time. Goals are paused and resumed, and the time away causes decay that must be accounted for on re-entry. Cross-goal intelligence coordinates across goal boundaries to produce a coherent learning experience rather than isolated parallel tracks.

The core challenge is semantic: two goals may teach the same underlying concept under different names. A "data structures" goal teaches "hash maps" while a "systems programming" goal teaches "hash table performance." These are the same foundational knowledge. Cross-goal intelligence recognizes this overlap and ensures that learning in one goal transfers appropriately to the other.

## Invariants

- **Foundational concepts live in a global knowledge state.** When a learner demonstrates mastery of a concept (e.g., "hash maps") in one goal, that evidence is recorded globally, not just within the goal's curriculum graph. Other goals that depend on the same concept can read this global state to skip redundant calibration. However, individual goals can require re-demonstration in their specific context — knowing hash maps in a data-structures goal does not automatically satisfy a systems-programming goal that needs hash map performance analysis. The global knowledge state is the learner profile's expertise map, which is already goal-spanning — not a separate data store.
- **Spaced repetition is coordinated globally.** Review scheduling considers all active goals when selecting which stale topics to surface. A topic that is stale in two goals is reviewed once, not twice. The review protocol reads from the global knowledge state, not from per-goal state, when determining freshness.
- **Priority and time allocation respect learner intent.** When multiple goals compete for session time, Sensei allocates based on learner-expressed priority, goal urgency (time-bounded goals take precedence as deadlines approach), and decay risk (goals with many near-stale topics get review time before topics cross the stale threshold).
- **Pause and resume are decay-aware.** When a learner pauses a goal and later resumes, the re-entry point accounts for time elapsed. Topics that were completed before the pause have decayed; the curriculum frontier is recomputed with current freshness values. Re-entry begins with targeted review of the most-decayed topics, not with the next topic in the pre-pause sequence.
- **Concept evidence survives goal retirement.** When a goal is retired or deleted, the concept evidence it contributed to the global knowledge state persists. The learner's demonstrated mastery of a concept does not disappear because the goal that surfaced it is no longer active. Other goals that share the concept continue to benefit from the evidence.
- **Curriculum nodes carry concept tags.** Each node in a curriculum graph is tagged with abstract concepts that identify the underlying knowledge independent of goal-specific framing. "Hash maps" in a data-structures goal and "hash table performance" in a systems-programming goal both carry a shared concept tag. Concept tags name the transferable knowledge, not the goal-specific application.
- **Concept tags are assigned at curriculum generation time.** Tags are determined when the curriculum is created, not applied retroactively to existing nodes. This ensures every node enters the system with its cross-goal identity already established.
- **Concept mastery in one goal is evidence, not proof, in another.** When a learner demonstrates mastery of a concept in one goal, that mastery provides evidence of competence in the same concept under other goals. It does not automatically satisfy those goals' requirements. Each goal retains the right to probe application-level mastery in its own context.
- **Review scheduling considers concept overlap across goals.** A concept reviewed in one goal counts toward review obligations for the same concept in other goals. A learner who reviews "recursion" in their algorithms goal does not face a separate review of the same concept in their functional-programming goal. The review is concept-aware, not slug-aware.
- **Concept transfer is bidirectional.** Evidence flows in both directions. Mastery demonstrated in any goal contributes to the global concept state. No goal is privileged as the "source" of concept knowledge.

## Rationale

**Foundational concepts transfer across goals, but goals can require re-demonstration.** The resolved §9 question on cross-goal knowledge transfer established this dual model. A global knowledge state avoids the absurdity of re-teaching hash maps from scratch when the learner starts a second goal. But context matters: knowing a concept abstractly is different from applying it under specific constraints. Goals retain the right to probe application-level mastery even when the global state says the concept is known. This balances efficiency (don't re-teach what's known) with rigor (don't assume transfer is automatic).

**Global coordination prevents redundant review.** Without coordination, a learner with three goals that all depend on "recursion" would be asked to review recursion three times per review cycle. This is wasteful and annoying. Global review coordination collapses these into one retrieval opportunity, with the result propagated to all goals that depend on the concept.

**Decay-aware re-entry respects the forgetting curve.** A naive resume would pick up where the learner left off, ignoring that weeks of inactivity have eroded previously completed topics. The forgetting-curve pillar requires that Sensei treat time away as a first-class signal. Re-entry review is not punishment for pausing — it is the same evidence-based care that the review protocol provides during active learning.

**Concept tags solve the semantic gap.** Slug-level deduplication (matching identical topic names across goals) catches only exact overlaps. Real knowledge transfer is semantic: "binary search" and "divide-and-conquer search" are the same concept; "TCP" in a networking goal and "reliable delivery" in a distributed-systems goal share foundational knowledge. Concept tags provide a shared vocabulary that transcends goal-specific naming. This is informed by Math Academy's approach to fractional implicit repetition (FIRe), where practicing an advanced topic gives partial credit to its prerequisites — the same principle applied across goal boundaries rather than within a single knowledge graph.

**Evidence, not proof, respects context-dependent mastery.** Transfer research consistently shows that knowing a concept in one context does not guarantee fluency in another. A learner who masters recursion through functional programming may still struggle with recursive backtracking in an algorithms context. The "evidence, not proof" model lets Sensei skip redundant foundational teaching while preserving each goal's right to verify application-level competence. This embodies P-transfer-is-the-goal: the goal is transfer, but transfer must be verified, not assumed.

**Tags at generation time, not retroactively.** Assigning concept tags during curriculum generation ensures consistency. Retroactive tagging would require re-analyzing existing curricula whenever a new goal is added, creating fragile dependencies between goals that were designed independently. Generation-time tagging makes each curriculum self-contained while still participating in cross-goal intelligence.

Concept tag matching is inherently approximate. Different LLMs generating curricula for different goals may produce different tags for the same underlying knowledge ("hash-maps" vs "hash-tables" vs "associative-arrays"). The system degrades gracefully in both directions: false negatives (missed concept matches) produce slightly redundant review, which is safe; false positives (incorrect matches) could skip needed instruction, but this risk is bounded by the evidence-not-proof invariant — goals can always require re-demonstration in their specific context. Semantic reconciliation of concept tags occurs at review time, not at generation time, so tags from different models coexist without retroactive modification.

Note: P-learner-is-not-the-goal currently marks cross-goal transfer as deferred at v1. That deferral is superseded by this spec's promotion to v1 scope.

## Out of Scope

- **Goal merging.** Two goals that converge in scope are not automatically merged. The learner must explicitly redefine their goals.
- **Cross-learner intelligence.** Knowledge transfer across different learners is out of scope. Each learner's global state is private.
- **Automated goal suggestion based on cross-goal patterns.** Proactive suggestions are a separate concern (§9 resolved: suggest once, don't repeat if ignored).
- **Session scheduling UI.** How the learner communicates time availability or goal priority is a UX concern, not a cross-goal intelligence concern.
- **Fractional credit propagation.** Math Academy's FIRe model computes precise fractional weights for how much an advanced topic exercises each prerequisite. This level of granularity requires handcrafted encompassing weights across the full knowledge graph and is not v1 scope.
- **Concept tag taxonomy management.** A curated, centralized taxonomy of all possible concept tags is not maintained. Tags emerge from curriculum generation and are matched semantically, not from a controlled vocabulary.
- **Concept tag format standardization.** Whether tags use a controlled vocabulary, slug format, or free text is a design decision. The spec requires only that tags identify transferable knowledge and can be matched across goals.

## Specs Requiring Amendment

Accepting this spec requires updating the following accepted specs:

- **goal-lifecycle-transitions.md** — the "at most one active goal" constraint must be reconciled with multi-goal coordination. Multiple goals must be simultaneously active for cross-goal intelligence to function. The constraint likely means "at most one focused goal" (receiving new instruction) while others remain active for review.
- **review-protocol.md** — remove "Cross-goal intelligence" from Out of Scope. Review becomes cross-goal-aware per this spec's invariants.
- **assessment-protocol.md** — remove "Cross-goal assessment coordination" from Out of Scope. Assessment reads global concept state per the evidence-not-proof invariant.
- **curriculum-graph.md** — nodes must support concept tags as a property. The current node model (5 states, DAG structure) does not mention tags.
- **learner-profile.md** — remove "multi-goal coordination" from Out of Scope. The profile's expertise map becomes the global knowledge state.

## Decisions

- [ADR-0006: Hybrid Runtime](../decisions/0006-hybrid-runtime-architecture.md) — deterministic helpers that compute decay and freshness across goals

## References

- Original ideation §9 (resolved) — cross-goal knowledge transfer: global knowledge state for foundational concepts, goals can require re-demonstration
- Original ideation §9 (resolved) — proactive goal suggestions: suggest once when patterns emerge
- `docs/specs/curriculum-graph.md` — per-goal DAG structure that cross-goal intelligence reads across
- `docs/specs/goal-lifecycle.md` — goal creation and evolution that produces the goals being coordinated
- `docs/foundations/principles/know-the-learner.md` — the meta-pillar; cross-goal intelligence is "know the learner" applied across goal boundaries
- `docs/foundations/principles/forgetting-curve-is-curriculum.md` — decay-aware re-entry is the forgetting curve applied to paused goals
- `docs/foundations/principles/transfer-is-the-goal.md` — concept tags exist because transfer, not topic completion, is the measure of learning
- `docs/foundations/principles/learner-is-not-the-goal.md` — cross-goal intelligence serves the learner's growth, not the goal's completion metrics
- [Interleaving](interleaving.md) — depends on concept tags from this spec for cross-goal interleaving.
