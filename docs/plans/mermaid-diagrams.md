---
feature: mermaid-diagrams
serves: (documentation enhancement — no feature spec)
design: (convention in docs/development-process.md § Diagrams)
status: done
date: 2026-04-20
---
# Plan: Mermaid Diagram Enhancement Pass

Add mermaid diagrams across the documentation where they significantly improve clarity. Prioritized by impact — HIGH items first (content genuinely hard to understand without a visual), MEDIUM items in a second pass.

## Phase 1 — Specs (HIGH priority, single commit)

Specs define product guarantees. Diagrams here help contributors and LLM agents understand what the system must do.

- [x] T1: `docs/specs/curriculum-graph.md` — `stateDiagram-v2` showing 5 node states (collapsed, expanded, spawned, active, completed) and valid transitions between them. → after Invariants: Five node states
- [x] T2: `docs/specs/curriculum-graph.md` — `flowchart TD` showing frontier computation: prerequisites completed → node eligible → activation. → after Invariants: Frontier
- [x] T3: `docs/specs/goal-lifecycle.md` — `flowchart TD` showing the Generate→Probe→Reshape cycle: goal expressed → draft generated → first lesson IS assessment → probe → reshape. → after Invariants
- [x] T4: `docs/specs/assessment-protocol.md` — `flowchart LR` showing diagnostic vs summative as two parallel tracks: different triggers, modes, scoring methods, outputs. → after Intent
- [x] T5: `docs/specs/assessment-protocol.md` — `flowchart TD` showing the two-failure decision tree: fail 1 → different angle → fail 2 → prerequisite diagnosis → recognition probes → rusty (review) vs never-learned (teach). → after Invariant (g)
- [x] T6: `docs/specs/performance-training.md` — `flowchart LR` showing the 6-stage stack: learn → automate → verbalize → time pressure → simulated evaluation → full mock, with mode overlays per stage. → after Invariants
- [x] T7: `docs/specs/review-protocol.md` — `flowchart TD` showing the review session flow: compute stale → rank → pose → classify → write → validate → next/end. No-reteach branch visible. → after Invariants
- [x] T8: `docs/specs/learner-profile.md` — `stateDiagram-v2` showing mastery levels: none → shaky → developing → solid → mastered (with demotion arrows since monotonicity is not enforced). → after Invariants: Mastery is ordered

## Phase 2 — Design docs + engine (HIGH priority, single commit)

Design docs explain HOW. Diagrams here show architecture and orchestration.

- [x] T9: `docs/design/release-workflow.md` — `flowchart LR` showing 3-job pipeline: verify → build-and-check → publish, with OIDC gate and environment approval. → after Architecture
- [x] T10: `docs/design/learner-profile-state.md` — `stateDiagram-v2` showing mastery enum + TopicState lifecycle with validator gates. → after Fields section
- [x] T11: `docs/design/folder-structure.md` — `flowchart TD` showing .sensei/ (engine-owned) vs learner/ (learner-owned) vs shim files, with ownership annotations. → after Layout section
- [x] T12: `docs/design/transcript-fixtures.md` — `flowchart TD` showing two-tier verification: fixtures + dogfood → conftest loader → Tier-1 (lexical, CI) / Tier-2 (LLM-as-judge, local). → after Architecture
- [x] T13: `src/sensei/engine/engine.md` — `flowchart TD` showing boot chain: AGENTS.md → engine.md → dispatch → protocols → helpers. → after the boot chain description
- [x] T14: `src/sensei/engine/protocols/review.md` — `flowchart TD` showing 9-step loop with error branches (invalid profile → end, no stale → end, learner exits → end). → after Purpose section
- [x] T15: `src/sensei/engine/protocols/modes/assessor.md` — `quadrantChart` or simple 2×2 grid showing confidence × correctness quadrant (mastered/learning/gap/misconception). → after the quadrant model description

## Phase 3 — ADRs (HIGH priority, single commit)

ADRs record decisions. Diagrams here make the architecture concrete.

- [x] T16: `docs/decisions/0002-agent-bootstrap.md` — `flowchart LR` showing boot chain: AGENTS.md → engine.md → protocols → scripts/prompts/schemas. → after Decision
- [x] T17: `docs/decisions/0004-sensei-distribution-model.md` — `flowchart TD` showing: pip install (wheel) → sensei init (copy to .sensei/ + learner/ + shims) → sensei upgrade (overwrite .sensei/ only). → after Decision
- [x] T18: `docs/decisions/0006-hybrid-runtime-architecture.md` — `flowchart TD` showing: Protocols (LLM) ↔ shell subprocess ↔ Scripts (CPython), with v1 helpers listed. → after Decision
- [x] T19: `docs/decisions/0012-foundations-layer.md` — `flowchart TD` showing foundations above the 6-layer stack with serves/realizes/stressed_by linkage arrows. → after Shape section
- [x] T20: `docs/decisions/0013-context-composition.md` — `flowchart TD` showing focused loading: base personality (full) + active mode (full) + 3 others (summary only). → after Decision
- [x] T21: `docs/decisions/0014-principles-over-state-machines.md` — `flowchart TD` showing three-layer architecture: Layer 1 (deterministic) → Layer 2 (principle-driven LLM) → Layer 3 (multi-agent coordination). → after Decision
- [x] T22: `docs/decisions/0015-unified-goal-pipeline.md` — `flowchart LR` showing 4-stage pipeline: triage → resolve → generate DAG → adapt. → after Decision

## Phase 4 — Principles + research (HIGH + MEDIUM, single commit)

Principles and research synthesis docs where a visual clarifies a concept.

- [x] T23: `docs/foundations/principles/two-failure-prerequisite.md` — `flowchart TD` showing the decision tree: fail 1 → different angle → fail 2 → diagnose → recognition probes → rusty vs never-learned. → after Implications
- [x] T24: `docs/foundations/principles/emotion-cognition-are-one.md` — `stateDiagram-v2` showing degradation chain: confusion → frustration → boredom → disengagement, with intervention point at confusion→frustration boundary. → after Implications: degradation chain
- [x] T25: `docs/research/synthesis/accelerated-performance.md` — `flowchart LR` showing Performance Prep Stack: learn → automate → verbalize → time pressure → simulated eval → full mock. → after Performance Training Model section
- [x] T26: `docs/research/synthesis/accelerated-performance.md` — `flowchart TD` showing FIRe dual graphs: prerequisite graph (forward, gates) + encompassing graph (backward, credit flow). → after FIRe section
- [x] T27: `docs/sensei-implementation.md` — `flowchart TD` showing implementation artifacts (protocols/config/helpers) feeding into verification types (assertions/rules/runner/transcript fixtures). → after the Implementation + Verification table

## Phase 5 — Verification (single commit)

- [x] T28: Verify all mermaid blocks render correctly on GitHub (push to branch, check preview). → verify
- [x] T29: Run `ci/check_foundations.py` — confirm 0 errors. → verify
- [x] T30: Full test suite green. → verify
- [x] T31: Append Unreleased entry to `CHANGELOG.md`. → `CHANGELOG.md`

## Acceptance Criteria

- [x] AC1: All 27 diagrams render correctly in GitHub markdown preview.
- [x] AC2: Every diagram has an anchor comment (`<!-- Diagram: illustrates §X -->`) and a numbered caption.
- [x] AC3: No diagram exceeds 15 nodes (complexity ceiling per convention).
- [x] AC4: `ci/check_foundations.py` passes with 0 errors.
- [x] AC5: Full test suite green.
- [x] AC6: CHANGELOG.md `[Unreleased]` describes the enhancement.

## Out of Scope

- CI validation of mermaid syntax (future — could use `@mermaid-js/mermaid-cli`).
- MEDIUM-priority diagrams not listed above (can be added opportunistically when those files are next edited).
- Diagrams in plan files (historical records, not living docs).

## Notes

**Why not all 48 opportunities?** The 27 tasks above cover all HIGH-priority items plus the MEDIUM items that are in files likely to be read frequently. The remaining ~21 MEDIUM items are nice-to-have and can be added when those files are next touched for other reasons.

**Diagram reuse:** Some concepts appear in multiple files (e.g., the two-failure tree in both the principle and the assessment spec). Each gets its own diagram — they serve different audiences (the principle explains WHY, the spec defines WHAT). Slight differences in framing are expected.
