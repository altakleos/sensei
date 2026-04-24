---
status: accepted
date: 2026-04-24
realizes:
  - P-curriculum-is-hypothesis
  - P-know-the-learner
stressed_by:
  - persona-tomas
  - persona-nkechi
fixtures_deferred: "Depth is a protocol-level concept consumed by LLM judgment, not scripts. Verified by dogfooding."
---

# Target Depth

## Intent

When a learner states a goal, the mentor infers how deep the learner needs to go and records it. This depth signal shapes curriculum generation — an overview goal produces broader, shallower nodes while an expertise goal produces narrower, deeper ones. Without an explicit depth signal, two goals in the same domain (e.g., "pass a Python interview" vs "become a Python expert") may generate curricula at the same granularity, failing to reflect the learner's actual needs.

## Invariants

- The mentor MUST infer `target_depth` from the learner's goal statement. It MUST NOT ask the learner to choose a depth level — this is not intake.
- `target_depth` MUST be one of `exposure`, `functional`, or `deep`. Default is `functional` when depth cannot be inferred.
- Each depth level is defined by what the learner will be able to DO, not by keyword patterns. The protocol provides examples to illustrate judgment, not rules to match.
  - `exposure` — recognize concepts, read others' work, have informed conversations.
  - `functional` — build, apply, and solve real problems independently.
  - `deep` — reason about edge cases, make architectural decisions, teach others.
- `target_depth` is a hypothesis, like the curriculum itself. If interaction reveals the learner needs more or less depth than initially inferred, the mentor updates it.
- `target_depth` is consumed by protocol prose (the LLM's curriculum generation judgment), not by Python scripts. No script reads or branches on this field.
- `target_depth` lives in `three_unknowns` alongside `prior_state`, `target_state`, and `constraints`.

## Rationale

The goal protocol already extracts a "depth signal" (goal.md Step 1) but discards it — it is never stored or consumed downstream. This means two goals sharing a topic domain can produce identical curricula despite having different depth requirements. The learner experiences this as the mentor "forgetting" what level they need.

Formalizing depth as a stored field gives the LLM an explicit reference when generating the curriculum. The field is consumed by protocol prose, not scripts, keeping it consistent with scripts-compute-protocols-judge: the LLM judges how depth shapes the curriculum; scripts compute the DAG mechanics.

Three levels (not two, not four) because: the LLM must infer depth from a single sentence, and three levels have clear semantic boundaries mapped to Bloom's taxonomy tiers (Remember/Understand, Apply/Analyze, Evaluate/Create). A boolean (deep vs not-deep) loses the exposure/functional distinction. Four levels create ambiguous boundaries the LLM resolves inconsistently.

## Out of Scope

- **Depth-aware script behavior.** No changes to `global_knowledge.py`, `mastery_check.py`, `review_scheduler.py`, or any other script. Depth is a protocol concept, not a computation input. The existing `require_redemonstration` flag handles per-node mastery verification.
- **Depth profiles in config.** No `depth_profiles` section in `defaults.yaml`. The existing `initial_size_min/max` and `prior_knowledge_percentile` ranges are sufficient. The LLM uses depth as a soft bias within those ranges.
- **Challenger auto-routing by depth.** The challenger protocol's existing entry conditions are sufficient. Depth does not override the tutor→assessor→challenger progression.
- **Per-node depth.** Depth is a goal-level property. The decompose mutation handles node-level granularity at runtime.

## Decisions

- [ADR-0006: Hybrid Runtime — Scripts Compute, Protocols Judge](../decisions/0006-hybrid-runtime-architecture.md) — depth is consumed by protocol prose, not scripts.
- [ADR-0014: Principles Over State Machines](../decisions/0014-principles-over-state-machines.md) — depth influences behavior through LLM judgment, not label-driven routing.
- [ADR-0015: Unified Goal-Processing Pipeline](../decisions/0015-unified-goal-pipeline.md) — depth is part of the goal's three_unknowns, processed in the same pipeline as prior_state and target_state.
