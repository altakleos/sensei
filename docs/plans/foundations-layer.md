---
feature: foundations-layer
serves: (method change — no per-feature spec)
design: (inline — captured in ADR-0012 and the new `docs/development-process.md` section)
status: done
date: 2026-04-20
---
# Plan: Foundations Layer + PRODUCT-IDEATION Phase-1 Decomposition

Ships the cross-cutting concerns layer per [ADR-0012](../decisions/0012-foundations-layer.md), plus the first wave of content migration from `PRODUCT-IDEATION.md` and `sensei-implementation.md`.

## Phase 1 — Method doc + scaffold (single commit)

- [ ] T1: Update `docs/development-process.md` — add a "Foundations" section before § "Specs". Project-agnostic content: defines the layer, names the sub-namespaces (vision, principles, personas), describes linkage-by-frontmatter (serves / realizes / stressed_by / stresses), describes migration-via-ADR-lite, and marks the layer optional-but-prescribed for projects without cross-cutting philosophy. Update the Relationships diagram to show `Foundations → Specs`. → `docs/development-process.md`
- [ ] T2: Create `docs/foundations/README.md` — index + linkage conventions + links to the linter + Sensei-specific principle decision guide ("kind: pedagogical vs technical vs product"). → `docs/foundations/README.md`
- [ ] T3: Create `docs/foundations/vision.md` — extracted from `PRODUCT-IDEATION.md` §1 + §2.1. Narrative prose; light frontmatter. → `docs/foundations/vision.md`

## Phase 2 — Linter (same commit as Phase 1 per ADR-0012 amendment)

- [ ] T4: `ci/check_foundations.py` — hard-fail validator. Asserts: (a) every `serves:` / `realizes:` / `stressed_by:` slug in any spec resolves to an existing `foundations/` file with matching type; (b) every `stresses:` slug in any persona resolves; (c) `kind:` values are in {pedagogical, technical, product}; (d) every accepted principle is referenced by at least one spec (warning, not error, for now — promotes to error after 3 feature PRs). Exit codes 0/1/2. → `ci/check_foundations.py`
- [ ] T5: `tests/ci/test_check_foundations.py` — unit tests. Synthetic foundation trees; each violation case covered. → `tests/ci/test_check_foundations.py`
- [ ] T6: Wire `check_foundations.py` into CI — either add to `verify.yml` matrix or invoke from a new dedicated step. Simpler: run unconditionally in `verify.yml`. → `.github/workflows/verify.yml`

## Phase 3 — Technical principles migration (single commit)

Migrate the six Load-Bearing Principles from `docs/sensei-implementation.md` into `docs/foundations/principles/`. Each becomes a TOGAF-style principle file with `kind: technical`. The `sensei-implementation.md` section becomes a pointer.

- [ ] T7: `docs/foundations/principles/prose-is-code.md`
- [ ] T8: `docs/foundations/principles/scripts-compute-protocols-judge.md`
- [ ] T9: `docs/foundations/principles/config-over-hardcoding.md`
- [ ] T10: `docs/foundations/principles/validators-close-the-loop.md`
- [ ] T11: `docs/foundations/principles/cross-link-dont-duplicate.md`
- [ ] T12: `docs/foundations/principles/prose-verified-by-prose.md`
- [ ] T13: Update `docs/sensei-implementation.md` — remove the Load-Bearing Principles section; replace with a one-paragraph pointer to `docs/foundations/principles/`. → `docs/sensei-implementation.md`

## Phase 4 — Pedagogical principles migration (single commit, 7 pillars + mentor relationship)

Extract the seven pillars from `PRODUCT-IDEATION.md` §2.2 and the mentor relationship from §2.3 into `docs/foundations/principles/` with `kind: pedagogical`.

- [ ] T14: `docs/foundations/principles/silence-is-teaching.md` (Pillar 1)
- [ ] T15: `docs/foundations/principles/ask-dont-tell.md` (Pillar 2)
- [ ] T16: `docs/foundations/principles/mastery-before-progress.md` (Pillar 3)
- [ ] T17: `docs/foundations/principles/productive-failure.md` (Pillar 4)
- [ ] T18: `docs/foundations/principles/forgetting-curve-is-curriculum.md` (Pillar 5)
- [ ] T19: `docs/foundations/principles/learner-self-sufficiency.md` (Pillar 6)
- [ ] T20: `docs/foundations/principles/know-the-learner.md` (Pillar 7)
- [ ] T21: `docs/foundations/principles/mentor-relationship.md` (§2.3 — demanding-but-caring mentor; four modes from principles)

## Phase 5 — Persona (single commit)

- [ ] T22: `docs/foundations/personas/jacundu.md` — extracted from `PRODUCT-IDEATION.md` §7.1 (senior SDE interview prep). Includes `stresses:` list pointing at current specs and principles; `owner: makutaku`.

## Phase 6 — Backreference wiring (single commit)

Apply `serves:` / `realizes:` / `stressed_by:` frontmatter to existing specs where the linkage is clear. Do not force-add links; only where the spec genuinely realises a principle or is stressed by the persona.

- [ ] T23: Update `docs/specs/review-protocol.md` — add `realizes: [P-silence-is-teaching, P-ask-dont-tell, P-mastery-before-progress, P-productive-failure, P-forgetting-curve-is-curriculum]` and `stressed_by: [persona-jacundu]`.
- [ ] T24: Update `docs/specs/learner-profile.md` — add `realizes: [P-know-the-learner]`, `stressed_by: [persona-jacundu]`.
- [ ] T25: Update `docs/specs/release-process.md` / `release-communication.md` — no natural principle linkage (these are infrastructure). Add `kind: infrastructure` spec-type frontmatter if convenient; skip otherwise.
- [ ] T26: Update `docs/specs/README.md` — template section gains optional `serves:`, `realizes:`, `stressed_by:` frontmatter fields.

## Phase 7 — Changelog + verify (single commit)

- [ ] T27: Append Unreleased entry to `CHANGELOG.md` covering the foundations-layer addition, principles migration, and new linter.
- [ ] T28: Full suite green (96+ tests → 96 + new linter tests).
- [ ] T29: Local smoke — confirm linter catches a synthetic broken `serves:` reference (negative test).

## Acceptance Criteria

- [ ] AC1: `docs/foundations/` exists with README, vision.md, principles/ (13 files: 6 technical + 7 pedagogical + mentor-relationship), personas/jacundu.md.
- [ ] AC2: `docs/sensei-implementation.md` no longer carries the Load-Bearing Principles section; it points at `docs/foundations/principles/`.
- [ ] AC3: `docs/development-process.md` describes Foundations as source material above the stack, project-agnostic language only.
- [ ] AC4: `ci/check_foundations.py` hard-fails on a broken reference; test suite covers each violation category.
- [ ] AC5: At least two existing specs (`review-protocol.md`, `learner-profile.md`) carry `realizes:` / `stressed_by:` frontmatter that resolves cleanly through the linter.
- [ ] AC6: Full suite green including new linter tests (target: 100+ tests).
- [ ] AC7: CHANGELOG.md `[Unreleased]` describes the change.

## Out of Scope (Phase 2+ decomposition, deferred)

- `PRODUCT-IDEATION.md` §3 (Architecture), §4 (Interaction Model), §5 (Curriculum), §6.1 (Folder Structure), §9 (Open Design Questions) — each needs its own plan.
- `§2.4 Deep Frontiers` — migrate to `foundations/principles/` (kind: pedagogical) once the first-wave pillar set is exercised in a feature.
- Policy-ADR enforcement validator (`check_policy_adr_coverage.py`) — deferred to a follow-up ADR once a second `protocols: [all]` ADR lands.
- Moving pre-existing ADRs (0006, 0009, 0011) to carry `scope: policy` frontmatter — trivial cleanup; fold into a later commit.

## Notes

**Why fold §9 resolved questions into destination artifacts rather than keep a separate log**: the user's explicit direction. Each resolved question is absorbed into the Rationale section of the spec, design, ADR, or principle that realises it, citing `PRODUCT-IDEATION.md §9 item N` in prose. Loss of standalone history is accepted because each resolved question was a design-driving input for exactly one downstream artifact.

**Why the linter is hard-fail from day 1**: user's explicit direction. A warning-first linter would silently tolerate broken references, which is exactly what `check_foundations.py` is meant to catch. Broken references are a 30-second fix; hard-failing keeps the invariant honest.

**Why ship all 7 pillars at once rather than 3 exemplars**: user's explicit direction, on the argument that the seven pillars are a cohesive set from `PRODUCT-IDEATION.md §2.2` and splitting weakens their meaning. The adversarial critic's concern (prove the shape before growth) is partially mitigated by the pre-lived experience with the 6 existing technical principles — the shape has been in sensei-implementation.md for weeks.
