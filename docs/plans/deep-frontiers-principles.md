---
feature: deep-frontiers-principles
serves: (decomposition — PRODUCT-IDEATION.md §2.4 into foundation principles)
design: (N/A — foundation principles, not feature specs)
status: planned
date: 2026-04-20
---
# Plan: Deep Frontiers Principles — PRODUCT-IDEATION §2.4 Decomposition

Migrates the four Deep Frontiers subsections from `PRODUCT-IDEATION.md` §2.4 into foundation principles. Plan 4 of 5 in the full PRODUCT-IDEATION decomposition.

**Depends on:** Plan 1 (`behavioral-architecture`) — these principles refine how behavioral modes operate. Independent of Plans 2 and 3.

**Why now (not earlier):** The foundations-layer plan explicitly deferred §2.4: "migrate once the first-wave pillar set is exercised in a feature." That condition is met — the review-protocol spec exercises multiple pillars. The deep frontiers are research-dense pedagogical stances that future protocol specs need to cite.

## Pre-Analysis

| §2.4 | Content                    | Destination                                              |
|-------|----------------------------|----------------------------------------------------------|
| 2.4.1 | Metacognition             | **NEW principle** → `P-metacognition-is-the-multiplier`  |
| 2.4.2 | Emotional Dynamics        | **NEW principle** → `P-emotion-cognition-are-one`        |
| 2.4.3 | Transfer                  | **NEW principle** → `P-transfer-is-the-goal`             |
| 2.4.4 | Personalization Paradox   | **Update** → P-know-the-learner (already partially absorbed) |

## Phase 1 — Three new principles (single commit)

- [ ] T1: `docs/foundations/principles/metacognition-is-the-multiplier.md` — kind: pedagogical. Statement: teaching the learner to plan, monitor, calibrate, and seek help strategically accelerates all future learning. Metacognitive skills are the multiplier on every other pedagogical investment. The forethought phase has the highest measured AI impact (g=1.613). Captures §2.4.1. → `docs/foundations/principles/metacognition-is-the-multiplier.md`
- [ ] T2: `docs/foundations/principles/emotion-cognition-are-one.md` — kind: pedagogical. Statement: confusion correlates with deep learning more than any other emotion, but has a shelf life. Motivation requires autonomy, competence, and relatedness (SDT), not rewards. Emotional state is learning infrastructure, not a side effect to manage. Captures §2.4.2. → `docs/foundations/principles/emotion-cognition-are-one.md`
- [ ] T3: `docs/foundations/principles/transfer-is-the-goal.md` — kind: pedagogical. Statement: learning that doesn't transfer is inert knowledge. Comparison is the cognitive engine of transfer. Vary surface features, require discrimination, prompt self-explanation, interleave across domains. What feels like good learning often produces poor transfer. Captures §2.4.3. → `docs/foundations/principles/transfer-is-the-goal.md`

## Phase 2 — Update P-know-the-learner + wiring (single commit)

- [ ] T4: Update `docs/foundations/principles/know-the-learner.md` — absorb remaining §2.4.4 content: expertise reversal effect detail, Kirschner vs Kapur resolution via sequencing, filter bubble risk, negotiated adaptivity. Add to Implications or Exceptions-and-Tensions sections. → `docs/foundations/principles/know-the-learner.md`
- [ ] T5: Run `ci/check_foundations.py` — confirm 0 errors. New principles will show as orphan warnings (no spec references them yet); that's expected and correct. → verify
- [ ] T6: Full test suite green. → verify
- [ ] T7: Append Unreleased entry to `CHANGELOG.md`. → `CHANGELOG.md`

## Acceptance Criteria

- [ ] AC1: Three new principles exist with status: accepted — `P-metacognition-is-the-multiplier`, `P-emotion-cognition-are-one`, `P-transfer-is-the-goal`.
- [ ] AC2: `P-know-the-learner` updated with §2.4.4 content (expertise reversal, negotiated adaptivity).
- [ ] AC3: `ci/check_foundations.py` passes with 0 errors (orphan warnings expected and acceptable).
- [ ] AC4: CHANGELOG.md `[Unreleased]` describes the change.

## Out of Scope

- Specs that realize these principles — those come when protocols are built that need them (e.g., a metacognition protocol would `realizes: [P-metacognition-is-the-multiplier]`).
- Affect detection mechanisms (§2.4.2 mentions it) — deferred per ADR-0006 v2 scope.
