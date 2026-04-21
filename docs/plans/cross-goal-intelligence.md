---
feature: cross-goal-intelligence
serves: docs/specs/cross-goal-intelligence.md
design: "Follows ADR-0006"
status: done
date: 2026-04-21
---
# Plan: Cross-Goal Intelligence

Implements all four invariants from the cross-goal intelligence spec. Two invariants extend existing partial implementations (global knowledge state, priority/time allocation); two are entirely new (globally coordinated spaced repetition, decay-aware pause/resume). All new scripts follow the ADR-0006 hybrid runtime pattern: argparse CLI, stdin/stdout JSON, importable as library, subprocess-invocable by protocols.

## Pre-Analysis: Invariant → Implementation Mapping

| Invariant | Existing code | New work |
|-----------|--------------|----------|
| Global knowledge state | `global_knowledge.py` (check only) | Add `--goal` flag for per-goal re-demonstration override |
| Globally coordinated spaced repetition | — | New `review_scheduler.py` script; update `review.md` to read global state |
| Priority and time allocation | `goal_priority.py` (priority + decay risk) | Add deadline urgency term; new `session_allocator.py` for time budgets |
| Decay-aware pause/resume | — | New `resume_planner.py` script; update `goal.md` §Resume |

## Phase 1 — Schema Changes (foundation for all phases)

- [x] T1: Extend `goal.schema.json` — add optional `deadline` field (ISO-8601 date-time, nullable) to the goal object. The `priority`, `paused_at`, and `resumed_at` fields already exist. → `src/sensei/engine/schemas/goal.schema.json`
- [x] T2: Extend `goal.schema.json` — add optional `require_redemonstration` boolean field (default `false`) to `NodeState.properties` in `$defs` (note: `NodeState` has `additionalProperties: false`, so the field must be added inside `properties`). When `true`, the node requires in-context mastery proof even if the topic is globally known. → `src/sensei/engine/schemas/goal.schema.json` (depends: T1)
- [x] T3: Update `check_goal.py` tests to cover the new schema fields (deadline, require_redemonstration) — valid values, null values, missing (optional) values. → `tests/scripts/test_check_goal.py` (depends: T2)
- [x] T3a: Review `check_goal.py` `_check_cross_field()` — if `require_redemonstration` has any cross-field constraints (e.g., only meaningful on completed nodes), add validation logic and corresponding tests. If no cross-field constraints apply, document that in a code comment. → `src/sensei/engine/scripts/check_goal.py`, `tests/scripts/test_check_goal.py` (depends: T2)
- [x] T4: Run full test suite — confirm existing tests still pass with schema additions (all fields are optional with defaults, so no breakage expected). → verify (depends: T3)

## Phase 2 — Global Knowledge State: Per-Goal Re-Demonstration Override (Invariant 1)

- [x] T5: Extend `global_knowledge.py` — add optional `--goal` flag accepting a path to a goal YAML file. When provided, after the global check, also check whether the topic's node in that goal has `require_redemonstration: true`. If so, override `known` to `false` in the output and add `"redemonstration_required": true` to the JSON response. Without `--goal`, behavior is unchanged (backward compatible). → `src/sensei/engine/scripts/global_knowledge.py`
- [x] T6: Unit tests for the re-demonstration override — topic globally known but goal requires re-demonstration → `known: false`; topic globally known and goal does NOT require re-demonstration → `known: true`; `--goal` flag absent → existing behavior unchanged. → `tests/scripts/test_global_knowledge.py` (depends: T5)
- [x] T7: Update `test_cross_goal.py` `TestGlobalKnowledge` class — add integration-level test combining profile + goal file with re-demonstration flag. → `tests/test_cross_goal.py` (depends: T6)
- [x] T8: Run full test suite — confirm green. → verify (depends: T7)

## Phase 3 — Globally Coordinated Spaced Repetition (Invariant 2)

- [x] T9: Implement `review_scheduler.py` — new script that reads all active goal files + the learner profile, computes freshness for every completed topic across all goals using `decay.freshness_score`, deduplicates topics that appear in multiple goals (a topic stale in two goals produces one review item, not two), and outputs a ranked JSON list of review candidates sorted by freshness ascending. CLI: `--goals-dir`, `--profile`, `--half-life-days` (reads from existing `memory.half_life_days` in defaults.yaml), `--stale-threshold` (reads from existing `memory.stale_threshold`), `--now` (all following existing conventions from `goal_priority.py`). → `src/sensei/engine/scripts/review_scheduler.py`
- [x] T10: Unit tests for `review_scheduler.py` — (a) topic stale in two goals appears once in output; (b) deduplication picks the lowest freshness score; (c) topics from paused goals are included (they still decay); (d) topics from abandoned/completed goals are excluded; (e) non-completed nodes are excluded; (f) output sorted by freshness ascending; (g) missing goals-dir returns exit 1; (h) subprocess invocation test. → `tests/scripts/test_review_scheduler.py` (depends: T9)
- [x] T11: Update `review.md` Step 2 — replace the per-topic `decay.py` loop (the section that iterates over completed topics and calls `decay.py` per-topic to build a stale list) with a single `review_scheduler.py` invocation that reads across all active goals. The script's output replaces the manually-built stale list. Preserve the existing error handling pattern: if `review_scheduler.py` fails, fall back to treating all completed topics as candidates (matching the current per-call fallback: "if an invocation fails, treat that topic as not-stale"). → `src/sensei/engine/protocols/review.md` (depends: T9)
- [x] T12: Run full test suite — confirm green. → verify (depends: T11)

## Phase 4 — Priority and Time Allocation (Invariant 3)

- [x] T13: Extend `goal_priority.py` — add optional `--deadline-weight` float flag (default from `defaults.yaml`). For goals with a `deadline` field, compute a deadline urgency term: `deadline_weight * (1 / max(1, days_until_deadline))`. Add this to the existing score. Include `deadline` info in the `reason` string when it contributes. Also include paused goals in output with a `"status": "paused"` marker (they were previously filtered out; downstream consumers need them for session planning). **Note:** existing tests (`test_paused_goal_returns_none`, `test_main_skips_paused_goals_end_to_end`) assert paused goals are excluded — update them to expect the new inclusion behavior. → `src/sensei/engine/scripts/goal_priority.py`, `tests/scripts/test_goal_priority.py`
- [x] T14: Implement `session_allocator.py` — new script that takes the ranked goal list from `goal_priority.py` (via stdin JSON or `--goals-json` file) and a `--session-minutes` budget, then allocates minutes per goal proportional to score. Output: JSON with `allocations: [{slug, minutes, reason}]`. Minimum allocation is 5 minutes (goals below minimum are dropped with a note). → `src/sensei/engine/scripts/session_allocator.py`
- [x] T15: Unit tests for deadline urgency in `goal_priority.py` — (a) goal with imminent deadline scores higher than same-priority goal without; (b) goal with distant deadline gets minimal boost; (c) no deadline → no urgency term; (d) paused goals now appear in output with status marker. → `tests/scripts/test_goal_priority.py` (depends: T13)
- [x] T16: Unit tests for `session_allocator.py` — (a) single goal gets full budget; (b) two goals split proportionally; (c) goal below 5-minute minimum is dropped; (d) empty input → empty allocations; (e) subprocess invocation test. → `tests/scripts/test_session_allocator.py` (depends: T14)
- [x] T17: Run full test suite — confirm green. → verify (depends: T16)

## Phase 5 — Decay-Aware Pause/Resume (Invariant 4)

- [x] T18: Implement `resume_planner.py` — new script that takes a goal file path + profile path + config params, computes freshness for every completed node in the goal, identifies the most-decayed topics, recomputes the curriculum frontier (by importing `compute_frontier` from `frontier.py` as a library call — not subprocess — since resume_planner already has the goal data in memory), and outputs a JSON resume plan: `{stale_topics: [{slug, freshness, elapsed_days}], frontier: [slugs], recommended_action: "review_first" | "continue"}`. The `recommended_action` is `"review_first"` when any topic has freshness below the stale threshold, `"continue"` otherwise. → `src/sensei/engine/scripts/resume_planner.py`
- [x] T19: Unit tests for `resume_planner.py` — (a) goal paused 30 days → multiple stale topics, action=review_first; (b) goal paused 1 day → no stale topics, action=continue; (c) stale topics sorted by freshness ascending (most decayed first); (d) only completed nodes are checked for decay; (e) missing profile → exit 1; (f) subprocess invocation test. → `tests/scripts/test_resume_planner.py` (depends: T18)
- [x] T20: Update `goal.md` §Resume — replace the current per-topic `decay.py` loop (steps 4–6) with a single `resume_planner.py` invocation. Use the script's `recommended_action` to decide whether to offer review-first or continue. Update the `paused_at`/`resumed_at` timestamps in the goal file. Preserve the existing learner-choice flow ("continue where you left off, or review stale topics first?"). → `src/sensei/engine/protocols/goal.md` (depends: T18)
- [x] T21: Run full test suite — confirm green. → verify (depends: T20)

## Phase 6 — Configuration and Engine Wiring

- [x] T22: Update `defaults.yaml` — add `cross_goal` section with: `deadline_weight: 5.0` (urgency multiplier), `min_session_minutes: 5` (minimum per-goal allocation), `review_dedup: true` (enable cross-goal review deduplication). → `src/sensei/engine/defaults.yaml` (depends: T13, T14)
- [x] T23: Update `engine.md` dispatch table — add entries for the new scripts in the "Running Helper Scripts" section or equivalent. Document `review_scheduler.py`, `session_allocator.py`, and `resume_planner.py` with their CLI signatures. Update the "Session Start — Goal Selection" section to reference `session_allocator.py` for time budgeting after priority ranking. → `src/sensei/engine/engine.md` (depends: T22)
- [x] T23a: Update `status.md` — in the session-start flow, after the `goal_priority.py` invocation, add a `session_allocator.py` call to produce per-goal time budgets. The status protocol should present the allocations to the learner as a suggested session plan. → `src/sensei/engine/protocols/status.md` (depends: T14, T23)
- [x] T24: Update `engine.md` "Configuration" section — document the new `cross_goal.*` config keys alongside the existing `memory.*` keys. → `src/sensei/engine/engine.md` (depends: T23)
- [x] T25: Run full test suite — confirm green. → verify (depends: T24)

## Phase 7 — Integration Tests and Transcript Fixture

- [x] T26: Cross-goal integration test — multi-goal scenario exercising all four invariants end-to-end: create two goals sharing a common topic, verify global knowledge deduplication, verify review scheduling collapses duplicates, verify priority ranking with deadline, verify resume after pause produces a decay-aware plan. → `tests/test_cross_goal.py` (depends: T8, T12, T17, T21)
- [x] T27: Transcript fixture — a tier-1 lexical fixture for the cross-goal review deduplication scenario. A learner with two active goals sharing "recursion" requests review; the fixture asserts "recursion" appears once in the review queue, not twice. → `tests/transcripts/cross_goal_review.md`, `tests/transcripts/test_fixtures.py` (depends: T26)
- [x] T28: Run full test suite including transcript fixtures — confirm green. → verify (depends: T27)

## Phase 8 — Finalize

- [x] T29: Update `docs/plans/README.md` — add this plan to the index table. → `docs/plans/README.md` (depends: T28)
- [x] T30: Full test suite green, `sensei verify` passes, CI green. → verify (depends: T29)

## Acceptance Criteria

- [x] AC1: **Invariant 1 (global knowledge state)** — `global_knowledge.py --goal <path>` returns `known: false` for a topic that is globally mastered but whose goal node has `require_redemonstration: true`. Without `--goal`, existing behavior is unchanged.
- [x] AC2: **Invariant 2 (coordinated spaced repetition)** — `review_scheduler.py` given two goals that both depend on "recursion" (stale in both) produces exactly one review entry for "recursion", not two. `review.md` invokes this script instead of per-goal decay loops.
- [x] AC3: **Invariant 3 (priority and time allocation)** — `goal_priority.py` scores a goal with an imminent deadline higher than an identical goal without a deadline. `session_allocator.py` produces per-goal minute allocations proportional to score.
- [x] AC4: **Invariant 4 (decay-aware pause/resume)** — `resume_planner.py` given a goal paused 30 days ago produces a plan with `recommended_action: "review_first"` and stale topics sorted by freshness ascending. `goal.md` §Resume invokes this script.
- [x] AC5: All new scripts follow ADR-0006 pattern: argparse CLI, JSON stdout, importable as library, subprocess test passes.
- [x] AC6: `goal.schema.json` accepts `deadline` on goals and `require_redemonstration` on nodes; existing goal files remain valid.
- [x] AC7: `defaults.yaml` contains `cross_goal` section with documented tunables.
- [x] AC8: `engine.md` dispatch table and configuration section document all new scripts and config keys.
- [x] AC9: Integration test in `test_cross_goal.py` exercises all four invariants in a multi-goal scenario.
- [x] AC10: Transcript fixture validates cross-goal review deduplication.
- [x] AC11: Full test suite green, `sensei verify` passes.
