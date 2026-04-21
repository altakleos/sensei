---
feature: curriculum-engine
serves: (decomposition — PRODUCT-IDEATION.md §5 + §4.4 into SDD artifacts)
design: (produced by this plan — no pre-existing design doc)
status: done
date: 2026-04-20
---
# Plan: Curriculum Engine — PRODUCT-IDEATION §5 + §4.4 Decomposition

Decomposes `PRODUCT-IDEATION.md` §5 (Curriculum Architecture, §5.1–5.7) and §4.4 (Cross-Goal Intelligence) into SDD artifacts. Plan 2 of 5 in the full PRODUCT-IDEATION decomposition.

**Depends on:** Plan 1 (`behavioral-architecture`) — the behavioral modes spec defines how the curriculum interacts with modes (assessor gates mastery, challenger activates on confirmation).

## Pre-Analysis: Merge Map

Several subsections are the same concern and merge into one artifact:

| Merge Group                      | Source Subsections              | Resulting Artifact                                  |
|----------------------------------|---------------------------------|-----------------------------------------------------|
| Curriculum-is-hypothesis principle | §5.1 + §5.2 (stance portion)  | `P-curriculum-is-hypothesis` (pedagogical)          |
| Goal Lifecycle spec              | §5.2 (pipeline) + §5.3 + §5.4 + §5.6 | `docs/specs/goal-lifecycle.md`              |
| Curriculum Graph spec            | §5.5 + §5.7                    | `docs/specs/curriculum-graph.md`                    |
| Cross-Goal Intelligence spec    | §4.4                            | `docs/specs/cross-goal-intelligence.md` (deferred)  |

## Phase 1 — Foundation principle + ADR (single commit)

- [x] T1: `docs/foundations/principles/curriculum-is-hypothesis.md` — kind: pedagogical. Statement: a curriculum is a hypothesis, not a plan. Generated immediately as a biased draft, validated through teaching (not questionnaires), reshaped continuously by evidence from learner performance. Accuracy at generation time is less important than responsiveness to interaction. Captures §5.1 core insight + §5.2 stance. → `docs/foundations/principles/curriculum-is-hypothesis.md`
- [x] T2: ADR: Unified Goal Pipeline — records the decision that Sensei uses one goal-processing pipeline with type-sensitive parameters rather than per-goal-type strategies. The three-unknowns framework (prior state, target state, constraints) is universal; type differences manifest as which unknown is hardest to resolve. Captures §5.4. → `docs/decisions/NNNN-unified-goal-pipeline.md`
- [x] T3: Update `docs/decisions/README.md` — add new ADR row. → `docs/decisions/README.md`

## Phase 2 — Curriculum graph spec (single commit)

The data-structure contract. No dependency on goal-lifecycle (the graph exists independently of how goals are managed).

- [x] T4: `docs/specs/curriculum-graph.md` — spec defining the curriculum as a DAG of topics with typed node states and a dynamic frontier. Key invariants: (a) the graph is a DAG (no cycles); (b) node states: collapsed, expanded, spawned, active, completed; (c) the frontier is computed dynamically from node states + dependencies; (d) graph mutations are incremental, never full regeneration ("evolve don't regenerate"); (e) validation effort scales with uncertainty — well-defined domains tolerate ~80% accuracy, vague targets require more probing (§5.7). Frontmatter: `realizes: [P-curriculum-is-hypothesis, P-forgetting-curve-is-curriculum]`. → `docs/specs/curriculum-graph.md`

## Phase 3 — Goal lifecycle spec (single commit)

Depends on curriculum-graph spec (populates the graph) and learner-profile spec (reads prior state).

- [x] T5: `docs/specs/goal-lifecycle.md` — spec defining how learning goals are created, triaged, calibrated, and evolved. Key invariants: (a) goals are created through conversation, never CLI flags or forms; (b) the first interaction with a new goal IS the assessment — no separate onboarding phase (§5.6 cold start); (c) a draft curriculum is generated immediately, biased toward the 70th-percentile learner (§5.2); (d) all goals decompose into three unknowns: prior state, target state, constraints (§5.3); (e) one pipeline, type-sensitive parameters (§5.4 per ADR). Frontmatter: `realizes: [P-curriculum-is-hypothesis, P-know-the-learner]`, `stressed_by: [persona-jacundu]`. → `docs/specs/goal-lifecycle.md`

## Phase 4 — Cross-goal intelligence spec + wiring (single commit)

- [x] T6: `docs/specs/cross-goal-intelligence.md` — status: **draft** (deferred — depends on goal-lifecycle implementation). Spec defining knowledge transfer across goals, global spaced repetition coordination, priority/time allocation, and pause/resume with decay-aware re-entry. Captures §4.4. Frontmatter: `realizes: [P-know-the-learner, P-forgetting-curve-is-curriculum]`, `stressed_by: [persona-jacundu]`. → `docs/specs/cross-goal-intelligence.md`
- [x] T7: Run `ci/check_foundations.py` — confirm 0 errors. → verify
- [x] T8: Full test suite green. → verify
- [x] T9: Append Unreleased entry to `CHANGELOG.md`. → `CHANGELOG.md`

## Acceptance Criteria

- [x] AC1: `P-curriculum-is-hypothesis` principle exists with status: accepted.
- [x] AC2: ADR for unified goal pipeline exists and is indexed.
- [x] AC3: `docs/specs/curriculum-graph.md` exists with status: accepted.
- [x] AC4: `docs/specs/goal-lifecycle.md` exists with status: accepted.
- [x] AC5: `docs/specs/cross-goal-intelligence.md` exists with status: draft.
- [x] AC6: `ci/check_foundations.py` passes with 0 errors.
- [x] AC7: CHANGELOG.md `[Unreleased]` describes the change.

## Out of Scope

- Implementing the curriculum graph data structure or goal lifecycle pipeline — separate implementation plans.
- Knowledge graph design (FIRe, dual graphs, prerequisite limits from §8.6) — deferred to a design doc when curriculum-graph implementation begins. ADR-0006 already scopes FIRe to v2.
- §4.1, §4.2, §4.3, §4.5 — covered by Plan 3 (interaction-model).
