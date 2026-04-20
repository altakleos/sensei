---
status: accepted
date: 2026-04-20
realizes:
  - P-know-the-learner
  - P-forgetting-curve-is-curriculum
stressed_by:
  - persona-jacundu
---
# Cross-Goal Intelligence

## Intent

When a learner pursues multiple goals, knowledge and effort do not stay siloed. Foundational concepts learned in one goal transfer to another. Spaced repetition schedules across goals compete for the same limited session time. Goals are paused and resumed, and the time away causes decay that must be accounted for on re-entry. Cross-goal intelligence is the set of mechanisms that coordinate across goal boundaries to produce a coherent learning experience rather than isolated parallel tracks.

This spec is deferred (status: accepted) because the v1 product operates goal-by-goal. The mechanisms described here become necessary when multi-goal learners are common enough that siloed operation produces visible incoherence — redundant review of the same concept under two goals, or a paused goal resuming as if no time passed.

## Invariants

- **Foundational concepts live in a global knowledge state.** When a learner demonstrates mastery of a concept (e.g., "hash maps") in one goal, that evidence is recorded globally, not just within the goal's curriculum graph. Other goals that depend on the same concept can read this global state to skip redundant calibration. However, individual goals can require re-demonstration in their specific context — knowing hash maps in a data-structures goal does not automatically satisfy a systems-programming goal that needs hash map performance analysis.
- **Spaced repetition is coordinated globally.** Review scheduling considers all active goals when selecting which stale topics to surface. A topic that is stale in two goals is reviewed once, not twice. The review protocol reads from the global knowledge state, not from per-goal state, when determining freshness.
- **Priority and time allocation respect learner intent.** When multiple goals compete for session time, Sensei allocates based on learner-expressed priority, goal urgency (time-bounded goals take precedence as deadlines approach), and decay risk (goals with many near-stale topics get review time before topics cross the stale threshold).
- **Pause and resume are decay-aware.** When a learner pauses a goal and later resumes, the re-entry point accounts for time elapsed. Topics that were completed before the pause have decayed; the curriculum frontier is recomputed with current freshness values. Re-entry begins with targeted review of the most-decayed topics, not with the next topic in the pre-pause sequence.

## Rationale

**Foundational concepts transfer across goals, but goals can require re-demonstration.** The resolved §9 question on cross-goal knowledge transfer established this dual model. A global knowledge state avoids the absurdity of re-teaching hash maps from scratch when the learner starts a second goal. But context matters: knowing a concept abstractly is different from applying it under specific constraints. Goals retain the right to probe application-level mastery even when the global state says the concept is known. This balances efficiency (don't re-teach what's known) with rigor (don't assume transfer is automatic).

**Global coordination prevents redundant review.** Without coordination, a learner with three goals that all depend on "recursion" would be asked to review recursion three times per review cycle. This is wasteful and annoying. Global review coordination collapses these into one retrieval opportunity, with the result propagated to all goals that depend on the concept.

**Decay-aware re-entry respects the forgetting curve.** A naive resume would pick up where the learner left off, ignoring that weeks of inactivity have eroded previously completed topics. The forgetting-curve pillar requires that Sensei treat time away as a first-class signal. Re-entry review is not punishment for pausing — it is the same evidence-based care that the review protocol provides during active learning.

## Out of Scope

- **Goal merging.** Two goals that converge in scope are not automatically merged. The learner must explicitly redefine their goals.
- **Cross-learner intelligence.** Knowledge transfer across different learners is out of scope. Each learner's global state is private.
- **Automated goal suggestion based on cross-goal patterns.** Proactive suggestions are a separate concern (§9 resolved: suggest once, don't repeat if ignored).
- **Session scheduling UI.** How the learner communicates time availability or goal priority is a UX concern, not a cross-goal intelligence concern.

## Decisions

- [ADR-0006: Hybrid Runtime](../decisions/0006-hybrid-runtime-architecture.md) — deterministic helpers that compute decay and freshness across goals

## References

- Original ideation §9 (resolved) — cross-goal knowledge transfer: global knowledge state for foundational concepts, goals can require re-demonstration
- Original ideation §9 (resolved) — proactive goal suggestions: suggest once when patterns emerge
- `docs/specs/curriculum-graph.md` — per-goal DAG structure that cross-goal intelligence reads across
- `docs/specs/goal-lifecycle.md` — goal creation and evolution that produces the goals being coordinated
- `docs/foundations/principles/know-the-learner.md` — the meta-pillar; cross-goal intelligence is "know the learner" applied across goal boundaries
- `docs/foundations/principles/forgetting-curve-is-curriculum.md` — decay-aware re-entry is the forgetting curve applied to paused goals
