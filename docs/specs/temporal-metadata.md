---
status: accepted
date: 2026-04-27
serves: [vision]
realizes: [P-forgetting-curve-is-curriculum, P-know-the-learner]
stressed_by: [persona-jacundu, persona-tomas]
fixtures_deferred: "Spec is draft; fixtures will be named once design and plan are accepted."
---
# Temporal Metadata on Topic Transitions

## Intent

When a learner completes a curriculum topic, Sensei records **when** it happened and begins tracking **how stable** that knowledge is. These two signals — completion timestamp and per-topic memory stability — let the mentor compute learning velocity, project deadline feasibility, and schedule reviews on personalised forgetting curves instead of a single global half-life.

## Invariants

- **Completion timestamp is captured.** When a curriculum node transitions to `completed`, the node acquires a `completed_at` field containing the ISO-8601 UTC timestamp of the transition. The field is absent (or null) on nodes that have never been completed.

- **Completion timestamp is immutable.** Once set, `completed_at` does not change — subsequent review, challenge, or assessment interactions update `last_seen` in the profile but never overwrite `completed_at` on the node.

- **Stability is initialised at completion.** When a topic is first completed, its profile entry acquires a `stability` field set to the configured initial value (default: the global `half_life_days`). This represents the estimated number of days before recall probability drops to 50%.

- **Stability adapts after retrieval.** Each successful retrieval (review or challenge where the learner demonstrates recall) increases `stability`. Each lapse (failure to recall a previously-completed topic) decreases it. The exact update rule is a design decision; the spec requires only that stability moves in the correct direction.

- **Decay uses per-topic stability when available.** The freshness calculation (`decay.py`) uses the topic's `stability` value as its half-life when present, falling back to the global `half_life_days` config when absent. Existing topics without `stability` continue to work unchanged.

- **Velocity is computable.** Given `completed_at` on nodes and `activated_at` (or the first `last_seen` as proxy), the system can derive time-to-mastery per topic. No spec is placed on how velocity is surfaced — only that the data to compute it exists.

- **Backward compatibility is preserved.** Both fields are optional with sensible defaults. Existing goal files and profiles without these fields remain valid. No schema version bump is required. `sensei upgrade` is not required to adopt — fields appear organically as the learner completes topics after upgrading.

## Rationale

Sensei's review scheduling runs on exponential decay with a single global half-life (`memory.half_life_days`, default 7). This means a topic the learner nailed in one session decays at the same rate as one they barely scraped through over three weeks. Every major spaced-repetition system (Anki/FSRS, SuperMemo SM-17+, Duolingo HLR) personalises decay per item — the research consensus is unambiguous (bibliography #14 FSRS, #41 MEMORIZE, #58 Math Academy FIRe).

The absence of `completed_at` also makes several promised features impossible:
- **Learning velocity** — "you're completing 1.5 topics/week" requires knowing when each was completed.
- **Deadline projection** — goal priority scoring (`goal_priority.py`) cannot project whether the learner is on-track without a velocity estimate.
- **Pacing visualisation** — the `status` command cannot show a timeline without completion dates.

The `last_seen` field is correct for what it measures (last retrieval), but it cannot serve double duty as a completion anchor because it is overwritten on every subsequent interaction.

## Out of Scope

- **Update formula for stability.** Whether stability follows SM-2 ease-factor rules, FSRS's DSR model, or a simpler multiplier is a design decision, not a spec concern. The spec requires only directional correctness (up on success, down on lapse).
- **`activated_at` timestamp.** Useful but derivable from the first `last_seen` entry. May be added later; not required for the velocity and stability use cases.
- **Time-on-task capture.** High value but high capture burden in a prose-as-code system with no timer infrastructure. Deferred.
- **Stability on non-completed topics.** Only completed topics enter the review cycle; stability on pending/active nodes has no consumer.
- **Surfacing velocity or pacing to the learner.** This spec guarantees the data exists; how it is displayed is a separate spec.

## Decisions

- None yet. Design doc will determine the stability update rule and where `completed_at` is written (protocol prose vs. `mutate_graph.py`).

## References

- [P-forgetting-curve-is-curriculum](../foundations/principles/forgetting-curve-is-curriculum.md) — "Memory decays predictably; the optimal time to review something is just before the learner would forget it."
- [P-know-the-learner](../foundations/principles/know-the-learner.md) — the learner profile must capture enough signal to adapt.
- Bibliography #14 (FSRS), #41 (MEMORIZE), #48 (PSI-KT), #58 (Math Academy FIRe) — all require per-item temporal metadata.
