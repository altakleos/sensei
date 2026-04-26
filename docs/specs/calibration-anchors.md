---
status: accepted
date: 2026-04-24
realizes:
  - P-curriculum-is-hypothesis
  - P-know-the-learner
  - P-mastery-before-progress
stressed_by:
  - persona-tomas
  - persona-jacundu
  - persona-nkechi
fixtures_deferred: "Accepted spec; no implementation plan filed yet. Fixtures land alongside the first implementation work — see protocols/goal.md § Step 4 (curriculum generation) and protocols/assess.md for likely consumption sites."
---

# Calibration Anchors

## Intent

When a learner sets a goal, the mentor calibrates its assessment against a researched understanding of what mastery looks like in that goal's context. Without calibration, the mentor relies on unconstrained LLM judgment to decide what "solid at load balancing for system design interviews" means — producing assessments that may be too shallow, too deep, or misaligned with the real-world standard the learner is preparing for.

Calibration anchors give the mentor an explicit, auditable reference for what "done" looks like per topic, where that reference came from, and how confident the mentor is in it. The learner can inspect, challenge, and override the anchor at any time.

## The Three Calibration Problems This Solves

1. **Per-topic success criteria** — what should the learner be able to do/explain/solve for this topic to be "done" in this goal's context? The anchor defines this as behavioral criteria (what the learner can DO), not content checklists.

2. **Assessment calibration** — are the probes the LLM generates at the right difficulty for the goal? The anchor provides exemplar probes at the target difficulty, which the assessor uses as calibration references (not verbatim question banks).

3. **Evidence threshold** — how much evidence at the right difficulty before advancing? The anchor specifies per-topic evidence expectations informed by the goal's real-world context (e.g., "interviewers ask 2-3 follow-ups per topic").

## Two-Phase Calibration

### Phase 1 — Seed at goal creation (non-blocking)

When the mentor generates the curriculum (goal.md Step 4), it also seeds a calibration anchor from its training knowledge. This is the LLM synthesizing what it already knows about the domain's standards — not web research, not a delay. The learner is learning within 2 turns (invariant preserved).

The seed anchor contains:
- A success profile for the goal overall (what "ready" looks like)
- Per-topic success criteria at the goal's `target_depth` level
- Exemplar probe templates at the target difficulty
- Per-topic evidence expectations
- Source confidence: `training_knowledge` (honest about provenance)

### Phase 2 — Progressive refinement (three triggers)

1. **Learner provides materials** — materials dropped into the inbox that match the goal get classified as calibration anchors (not just hints) when they represent a reference standard (book chapters, exam guides, rubrics, syllabi). These refine the anchor with higher-confidence data.

2. **Web research** (optional, when the LLM has tool-use web access) — the mentor researches on-demand when it detects the seed anchor is thin for a specific topic it's about to teach or assess. Just-in-time per topic, not front-loaded.

3. **Mentor self-correction** — when learner performance contradicts the anchor's expectations (e.g., anchor says "basic topic" but the learner struggles), the mentor annotates the anchor with observed difficulty.

## Trust Hierarchy

When multiple calibration sources exist, precedence is:

1. **Learner-provided materials** — highest trust. The learner knows their target context. An actual rubric from their target company is ground truth.
2. **Web research** — medium trust. More current and specific than training data, but quality varies. Provenance recorded.
3. **LLM training data** — baseline. The Bayesian prior that gets updated by evidence.

Within the same tier, more recent supersedes older. Conflicts between tiers are resolved by the hierarchy. Conflicts within a tier are surfaced to the learner.

## Invariants

- The calibration anchor MUST be seeded at goal creation time from training knowledge. The learner MUST NOT wait for research before the first lesson.
- The anchor is a **hypothesis about the standard**, not the standard itself. It is treated with the same epistemic humility as the curriculum.
- The anchor MUST be auditable. The learner can read the anchor file at any time and see: what criteria the mentor is using, where each criterion came from, and the confidence level.
- The anchor MUST be surfaceable. When the learner asks "what are you calibrating against?" or "how do you know this is the right bar?", the mentor reads and summarizes the anchor.
- Learner-provided materials MUST take precedence over mentor-researched or training-derived anchors.
- The anchor constrains the **target state** (what "done" looks like), not the **path** (how to get there). The curriculum graph still mutates freely via skip/insert/decompose.
- Web research is OPTIONAL. The system MUST degrade gracefully when the LLM has no web access — the seed from training knowledge is always available.
- Anchor changes MUST be surfaced to the learner. No silent recalibration.
- For goals without external standards (curiosity-driven, exposure-depth), the anchor uses ipsative calibration (the learner's own prior performance), not external standards.

## Anchor File Structure

Each goal gets a companion anchor file:

```
learner/goals/
├── system-design-interviews.yaml          # goal file
├── system-design-interviews.anchor.yaml   # calibration anchor
```

The anchor contains:
- `success_profile` — what "ready" looks like for this goal overall
- `topic_anchors` — per-topic success criteria, exemplar probes, and evidence expectations (keyed by curriculum node slug)
- `provenance` — append-only log of what informed the calibration and when

The anchor is consumed by protocol prose (the LLM reads it during assessment and teaching). No Python script reads or branches on anchor contents. This follows the scripts-compute-protocols-judge boundary — the anchor is a judgment input, not a computation input.

The one exception: `topic_anchors[slug].evidence_threshold.min_probes` parameterizes the `--min-attempts` flag that `mastery_check.py` already supports. The anchor doesn't change the script; it changes how the protocol invokes the script.

## Integration with the Hints Pipeline

The hints system (ADR-0019) already triages inbox materials, scores relevance, and registers them. Calibration anchoring extends this with a classification step:

- When triaging an inbox item, the mentor classifies it as `hint` (interest signal — current behavior) or `anchor` (calibration reference — new behavior).
- `anchor` classification is appropriate when the material represents a reference standard: book chapters, exam guides, rubrics, syllabi, structured roadmaps from authoritative sources.
- `hint` classification remains the default for casual materials: tweets, blog posts, article links, notes.
- The `anchor_type` field on hint registry entries records this classification.
- When an anchor is registered, the mentor compares its topic coverage against the current curriculum and the existing calibration anchor, and proposes refinements.

## Goal-Type Awareness

Not all goals benefit from external calibration:

| Goal archetype | External calibration? | Anchor source |
|---|---|---|
| Interview prep, certification, exam | Yes — the standard is externally defined | Rubrics, blueprints, scoring criteria |
| Expertise with professional context | Light — industry expectations, not exam content | Role expectations, canonical references |
| Curiosity-driven, exposure-depth | No — the learner defines "done" | Ipsative (learner's own prior performance) |

The mentor infers the goal archetype from `expressed_as`, `target_depth`, and `three_unknowns.constraints`. This is LLM judgment, not a lookup table.

## Out of Scope

- **Anchor schema validation via Python script.** The anchor file is protocol-consumed, not script-consumed. No `check_anchor.py` in v1.
- **Cross-goal anchor sharing.** Each goal has its own anchor. A shared calibration library is a v2 concern.
- **Automatic authority classification of inbox materials.** The mentor asks the learner when classification is ambiguous.
- **Anchor-calibrated assessment question generation.** v1 anchors influence the mentor's judgment about difficulty and criteria. They do not template-generate questions.

## Decisions

- [ADR-0006: Hybrid Runtime — Scripts Compute, Protocols Judge](../decisions/0006-hybrid-runtime-architecture.md) — the anchor is consumed by protocol prose, not scripts (except parameterizing `--min-attempts`).
- [ADR-0019: Universal Inbox over Typed Drop Zones](../decisions/0019-universal-inbox.md) — the inbox remains universal; `anchor_type` extends the hint registry, not the inbox structure.
- [ADR-0014: Principles Over State Machines](../decisions/0014-principles-over-state-machines.md) — goal-type awareness is LLM judgment, not a state machine.

## References

- P-curriculum-is-hypothesis — the anchor is a hypothesis about the standard, corrected by evidence.
- P-know-the-learner — learner-provided materials take precedence because the learner knows their context.
- P-mastery-before-progress — the anchor defines what mastery means per topic, making the 90% threshold meaningful.
- P-metacognition-is-the-multiplier — the anchor is visible to the learner, enabling self-calibration.
- `docs/specs/hints.md` — the hints pipeline that calibration anchoring extends.
- `docs/specs/target-depth.md` — target_depth determines whether external calibration is appropriate.
- Koedinger, Corbett & Perfetti (2012), "The Knowledge-Learning-Instruction Framework" — criterion-referenced assessment anchored to real-world standards.
- Bloom (1984), "The 2 Sigma Problem" — mastery learning with criterion-referenced thresholds.
