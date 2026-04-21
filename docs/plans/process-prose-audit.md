---
feature: process-prose-audit
serves: docs/development-process.md
design: "N/A — documentation-only refactoring, no new mechanism"
status: done
date: 2026-04-21
---
# Plan: Development Process Prose-as-Code Audit

Systematic fix of all findings from the four-reviewer audit (discoverability,
clarity, organization, contradictions). Goal: a fresh LLM session can find,
understand, and correctly follow every process rule without ambiguity.

## Tasks

### Phase 1 — Stale content & broken references (mechanical)

- [x] T1: Fix AGENTS.md stale ADR count ("0001–0005" → "0001–0019") → `AGENTS.md`
- [x] T2: Fix AGENTS.md stale project layout tree (update descriptions to match reality) → `AGENTS.md`
- [x] T3: Fix plan-before-branch paradox (swap steps 4/5 in "New Feature: Full Stack") → `docs/development-process.md`
- [x] T4: Fix script names in sensei-implementation.md (hyphens → underscores) → `docs/sensei-implementation.md`
- [x] T5: Remove dangling §3.6/§8.5 references → `docs/sensei-implementation.md`
- [x] T6: Update status from "scaffolding" to reflect shipped reality → `docs/sensei-implementation.md`
- [x] T7: Mark `memory/rules.yaml` as planned (not yet implemented) in verification table → `docs/sensei-implementation.md`
- [x] T8: Add 5 orphaned plans to plans/README.md index → `docs/plans/README.md`

### Phase 2 — Migrate process concepts from READMEs to development-process.md

- [x] T9: Add document authority hierarchy to development-process.md → `docs/development-process.md`
- [x] T10: Migrate checkbox convention from plans/README.md to development-process.md § Plans, leave pointer in README → `docs/development-process.md`, `docs/plans/README.md`
- [x] T11: Migrate ADR status vocabulary + provisional preference from decisions/README.md to development-process.md § ADRs, leave pointer in README → `docs/development-process.md`, `docs/decisions/README.md`
- [x] T12: Migrate fixture-naming convention from specs/README.md to development-process.md § When to Write a Spec, leave pointer in README → `docs/development-process.md`, `docs/specs/README.md`
- [x] T13: Migrate kind decision heuristic + CI enforcement from foundations/README.md to development-process.md § Foundations, leave pointer in README → `docs/development-process.md`, `docs/foundations/README.md`
- [x] T14: Add ADR template to decisions/README.md (consistent with specs/plans/design READMEs) → `docs/decisions/README.md`

### Phase 3 — Fix stale summaries in development-process.md

- [x] T15: Update spec frontmatter summary (2 fields → 7) → `docs/development-process.md`
- [x] T16: Update design doc section names to match template → `docs/development-process.md`
- [x] T17: Add ADR-lite tie-breaker rule ("when in doubt, default to full ADR") → `docs/development-process.md`

### Phase 4 — Improve clarity (definitions, examples, boot chain)

- [x] T18: Add worked examples for workflow routing (feature / behavioral / bug fix) → `docs/development-process.md`
- [x] T19: Add glossary of undefined terms (behavioral change, component boundary, spec invariant) → `docs/development-process.md`
- [x] T20: Fix boot chain in AGENTS.md — add foundations/vision.md as step 0 → `AGENTS.md`
- [x] T21: Add operations link to development-process.md References → `docs/development-process.md`
- [x] T22: Fix changelog granularity — align AGENTS.md with spec ("same PR or commit") → `AGENTS.md`

### Phase 5 — Resolve contradictions

- [x] T23: Add ADR-lite for release approval self-bypass (resolve spec vs playbook contradiction) → `docs/decisions/0020-release-self-bypass.md`, `docs/decisions/README.md`

## Acceptance Criteria

- [x] AC1: A fresh LLM session reading only the boot chain can find rules for every common action (feature, plan, ADR, spec, commit, release, skip design doc)
- [x] AC2: No process concept is defined ONLY in a README — all are in development-process.md with README pointers
- [x] AC3: All file references in sensei-implementation.md match actual filenames on disk
- [x] AC4: development-process.md summaries match their canonical templates
- [x] AC5: The three workflow paths have worked examples
- [x] AC6: Document authority hierarchy is stated
- [x] AC7: CI passes (pytest + ruff + mypy + check_foundations)
