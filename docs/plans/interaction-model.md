---
feature: interaction-model
serves: (decomposition — PRODUCT-IDEATION.md §4 + §6.1 into SDD artifacts)
design: (produced by this plan — no pre-existing design doc)
status: done
date: 2026-04-20
---
# Plan: Interaction Model — PRODUCT-IDEATION §4 + §6.1 Decomposition

Decomposes `PRODUCT-IDEATION.md` §4 (Interaction Model, §4.1–4.5) and §6.1 (Folder Structure) into SDD artifacts. Plan 3 of 5 in the full PRODUCT-IDEATION decomposition.

**Depends on:** Plan 1 (`behavioral-architecture`) — the interaction model needs to know how modes and transitions work.
**Soft dependency on:** Plan 2 (`curriculum-engine`) — goal folders are curriculum artifacts, but the folder structure can be designed with curriculum as a known-but-not-yet-specified consumer.

## Pre-Analysis: Most of §4 Is Already Captured

| §    | Subsection              | Status                                                    |
|------|-------------------------|-----------------------------------------------------------|
| 4.1  | Minimal CLI             | Already realised → `cli.py` + ADR-0004                   |
| 4.2  | Conversation-First      | Already captured → `vision.md` Key Properties             |
| 4.3  | Learner Is Not the Goal | **NEW principle** → `P-learner-is-not-the-goal` (product) |
| 4.4  | Cross-Goal Intelligence | Covered by Plan 2 → `cross-goal-intelligence.md`         |
| 4.5  | Full Portability        | Already captured → ADR-0004 + `vision.md`                 |
| 6.1  | Folder Structure        | No standalone artifact — emergent from component specs    |

## Phase 1 — Foundation principle (single commit)

- [x] T1: `docs/foundations/principles/learner-is-not-the-goal.md` — kind: product. Statement: the learner is a persistent identity; goals are transient workspaces. The profile lives above goals, knowledge transfers across them, and goals can be created, paused, and retired without affecting the learner's identity or accumulated knowledge. This constrains the folder structure, the profile spec, and every future goal-management spec. Captures §4.3. → `docs/foundations/principles/learner-is-not-the-goal.md`

## Phase 2 — Verify existing coverage + folder structure rationale (single commit)

- [x] T2: Verify §4.1 coverage — confirm `cli.py` implements the "minimal CLI" contract (init scaffolds, everything else is conversation). No new artifact needed; add a §4.1 citation to ADR-0004 References if missing. → verify
- [x] T3: Verify §4.2 coverage — confirm `vision.md` Key Properties captures "conversation-first." If the specific phrasing "no artificial separation between setup and learning" is missing, add it. → `docs/foundations/vision.md`
- [x] T4: Verify §4.5 coverage — confirm ADR-0004 + `vision.md` capture full portability (git-trackable, Dropbox-syncable, copy to new laptop). No new artifact needed. → verify
- [x] T5: `docs/design/folder-structure.md` — design doc capturing the rationale for the canonical folder layout that `sensei init` creates. Documents the divergences between §6.1's aspirational sketch and the actual implementation (e.g., `learner/profile.yaml` not `.sensei/profile.yaml`). Documents where future components will land (goal workspaces, agent mode files) without specifying them. This is a design rationale doc, not a spec — the folder structure is an emergent property of component specs. → `docs/design/folder-structure.md`

## Phase 3 — Wiring + verification (single commit)

- [x] T6: Wire `P-learner-is-not-the-goal` into existing specs — add to `realizes:` on `learner-profile.md` (the profile is root-level, not per-goal). → `docs/specs/learner-profile.md`
- [x] T7: Run `ci/check_foundations.py` — confirm 0 errors. → verify
- [x] T8: Full test suite green. → verify
- [x] T9: Append Unreleased entry to `CHANGELOG.md`. → `CHANGELOG.md`

## Acceptance Criteria

- [x] AC1: `P-learner-is-not-the-goal` principle exists with status: accepted.
- [x] AC2: `docs/design/folder-structure.md` exists documenting the canonical layout and §6.1 divergences.
- [x] AC3: §4.1, §4.2, §4.5 verified as already captured — no new artifacts, citations added where missing.
- [x] AC4: `ci/check_foundations.py` passes with 0 errors.
- [x] AC5: CHANGELOG.md `[Unreleased]` describes the change.

## Out of Scope

- CLI enhancements (e.g., `sensei status` showing goal progress) — separate spec when needed.
- Goal workspace folder structure — deferred to Plan 2's goal-lifecycle implementation.
- §4.4 (Cross-Goal Intelligence) — covered by Plan 2.
