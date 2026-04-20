---
feature: research-and-closure
serves: (decomposition — PRODUCT-IDEATION.md §8/§9/§10 + full deprecation)
design: (N/A — absorption + cross-reference migration + deletion)
status: planned
date: 2026-04-20
---
# Plan: Research, Closure & Deletion of PRODUCT-IDEATION.md

Absorbs ALL remaining content from `PRODUCT-IDEATION.md`, migrates all 78 cross-references, and deletes the file. Plan 5 of 5 — runs AFTER Plans 1–4 complete (all destination artifacts exist).

**Depends on:** Plans 1–4 (behavioral-architecture, curriculum-engine, interaction-model, deep-frontiers-principles).

## Pre-Analysis: What Remains After Plans 1–4

Plans 1–4 absorb §2.4, §3, §4, §5 content into principles, specs, design docs, and ADRs. What's left:
- **§8 research findings** (~20 unabsorbed) — need homes in synthesis docs or artifact Rationale sections
- **§9 resolved questions** (12 unabsorbed) — need homes in implementing artifacts' Rationale sections
- **§1 minor gaps** (Core Flow code block, "automatic progress tracking" property)
- **§7.1 minor gaps** (first-move script, push-vs-comfort diagnostic, mode-to-week mapping)
- **78 cross-references** across 32 files pointing at PRODUCT-IDEATION.md
- **§10** — pointer table, fully covered by RESEARCH-BIBLIOGRAPHY.md. No action needed.
- **§6.2** — already absorbed into learner-profile spec (v1 captured, rest explicitly deferred). No action needed.

**RESEARCH-BIBLIOGRAPHY.md: KEEP.** It's a standalone 58-source reference catalog with independent value. Only its one PRODUCT-IDEATION.md provenance note needs updating.

## Phase 1 — §8 Research Synthesis Absorption (single commit)

Create 4 themed synthesis docs in `docs/research/synthesis/` to house the ~20 unabsorbed findings. These bridge the raw bibliography and the spec/principle layer.

- [ ] T1: `docs/research/synthesis/learning-science.md` — forward testing effect, forethought phase g=1.613, sleep-dependent consolidation details. Frontmatter: `feeds: [P-forgetting-curve-is-curriculum, P-metacognition-is-the-multiplier]`. → `docs/research/synthesis/learning-science.md`
- [ ] T2: `docs/research/synthesis/competitive-landscape.md` — GenMentor/DeepTutor positioning, Karpathy local-files validation, developer tool landscape (Exercism, CodeCrafters). Dated snapshot. → `docs/research/synthesis/competitive-landscape.md`
- [ ] T3: `docs/research/synthesis/adaptive-personalization.md` — 40/50/10 policy, 5-level graduated hinting, hint dependency ratio, 3-4 prerequisite limit, task selection LLM>expert-systems. Frontmatter: `feeds: [P-know-the-learner, curriculum-graph, goal-lifecycle]`. → `docs/research/synthesis/adaptive-personalization.md`
- [ ] T4: `docs/research/synthesis/accelerated-performance.md` — Performance Prep Stack (6 steps), Three-Mode taxonomy (reindex/new/performance), Stress Inoculation Training, rapid diagnostic 4-20 questions, rusty-vs-never-learned detection signals, prerequisite graph 60-80% pruning, behavior coaching 30>60min, motivation-first design. Frontmatter: `feeds: [performance-training, assessment-protocol, behavioral-modes]`. → `docs/research/synthesis/accelerated-performance.md`
- [ ] T5: Update existing principles' Source fields to cite synthesis docs where relevant (forgetting-curve → learning-science.md, mastery-before-progress → accelerated-performance.md, etc.). → various `docs/foundations/principles/*.md`
- [ ] T6: `docs/research/synthesis/README.md` — index explaining the synthesis layer's role between bibliography and specs. → `docs/research/synthesis/README.md`

## Phase 2 — §9 Resolved Questions + §1/§7.1 Gaps (single commit)

Absorb remaining orphaned content into destination artifacts' Rationale/Implications sections.

- [ ] T7: Absorb 12 unabsorbed §9 resolved questions into their implementing artifacts' Rationale sections. Mapping: metacognition-invisible → P-metacognition-is-the-multiplier; time-pressured-mode → behavioral-modes spec; coach-behaviors → P-metacognition-is-the-multiplier; curriculum-DAG-visible → curriculum-graph spec; cross-goal-transfer → cross-goal-intelligence spec; proactive-suggestions → P-learner-is-not-the-goal; mode-bleed-testing → behavioral-modes spec; mastery-visible → learner-profile spec; performance-stack-integration → performance-training spec; init-asking → goal-lifecycle spec; uncertain-targets → goal-lifecycle spec; FIRe-accuracy → curriculum-graph spec. → various specs and principles
- [ ] T8: Absorb §1 gaps: Core Flow code block → vision.md § Identity; "automatic progress tracking" → learner-profile spec § Invariants. Absorb §7.1 gaps: first-move script → behavioral-modes spec; push-vs-comfort diagnostic → behavioral-modes design doc; mode-to-week mapping → performance-training spec. → `docs/foundations/vision.md`, `docs/specs/learner-profile.md`, `docs/specs/behavioral-modes.md`, `docs/design/behavioral-modes.md`, `docs/specs/performance-training.md`

## Phase 3 — Cross-Reference Migration (single commit)

Migrate all 78 references across 32 files. Zero references to PRODUCT-IDEATION.md must remain.

- [ ] T9: Foundation principles (8 files) — replace Source section `PRODUCT-IDEATION.md §X.Y` citations with "Pedagogical Pillar N (original)" + research citations. Replace inline §X.Y references with cross-links to decomposed artifacts. → `docs/foundations/principles/*.md`
- [ ] T10: `docs/specs/review-protocol.md` — replace §3.3→mentor-relationship principle, §3.10→silence-is-teaching principle, §8.1→forgetting-curve principle, §8.4→adaptive-personalization synthesis. → `docs/specs/review-protocol.md`
- [ ] T11: `docs/specs/learner-profile.md` — replace §3.6→review-protocol invariants, §6.2→"original ideation (git history)", §8.1→forgetting-curve principle. → `docs/specs/learner-profile.md`
- [ ] T12: ADR-0006 References — replace §3.6/§8.1/§8.5/§8.6 with decomposed artifact links. ADR body is immutable; References are navigational metadata. → `docs/decisions/0006-hybrid-runtime-architecture.md`
- [ ] T13: `src/sensei/engine/engine.md` — replace §3.6 source citation with review-protocol spec. → `src/sensei/engine/engine.md`
- [ ] T14: `docs/foundations/vision.md` — remove "Full ideation backdrop" reference. vision.md IS the canonical vision now. → `docs/foundations/vision.md`
- [ ] T15: `docs/foundations/personas/jacundu.md` — replace Source §7.1 with "Original use-case analysis (preserved in git history). This persona is now the canonical artifact." → `docs/foundations/personas/jacundu.md`
- [ ] T16: Python docstrings — `classify_confidence.py` replace §8.5 with "per ADR-0006 § V1 scope"; `decay.py` replace §8.1 with "per P-forgetting-curve-is-curriculum, ADR-0006". → `src/sensei/engine/scripts/classify_confidence.py`, `src/sensei/engine/scripts/decay.py`

**Note:** Plan files are historical records — do NOT update their PRODUCT-IDEATION.md references. ADR Context sections (0001, 0012) are immutable — do NOT update.

## Phase 4 — Top-Level Docs + Deletion (single commit)

- [ ] T17: Update `AGENTS.md` — remove PRODUCT-IDEATION.md from project layout tree, replace "pre-decomposition record" constraint with: "The product vision has been decomposed into `docs/foundations/` and `docs/specs/`. `RESEARCH-BIBLIOGRAPHY.md` is the curated research catalog." Update References section. → `AGENTS.md`
- [ ] T18: Update `README.md` — replace PRODUCT-IDEATION.md link with `docs/foundations/vision.md`. Update status line from "ideation + scaffolding" to reflect current state. → `README.md`
- [ ] T19: Update `RESEARCH-BIBLIOGRAPHY.md` — replace "synthesized into PRODUCT-IDEATION.md" with "synthesized into the original ideation document and subsequently decomposed into `docs/foundations/` and `docs/specs/`." → `RESEARCH-BIBLIOGRAPHY.md`
- [ ] T20: **Delete `PRODUCT-IDEATION.md`.** Git history preserves it. → `git rm PRODUCT-IDEATION.md`

## Phase 5 — Verification (single commit)

- [ ] T21: `grep -r "PRODUCT-IDEATION" .` — must return 0 hits outside of plan files (which are historical). → verify
- [ ] T22: Run `ci/check_foundations.py` — confirm 0 errors. → verify
- [ ] T23: Full test suite green. → verify
- [ ] T24: Append Unreleased entry to `CHANGELOG.md` — "Fully decomposed and deleted PRODUCT-IDEATION.md. All content absorbed into foundation principles, specs, design docs, ADRs, and research synthesis docs. RESEARCH-BIBLIOGRAPHY.md retained as standalone reference catalog." → `CHANGELOG.md`

## Acceptance Criteria

- [ ] AC1: 4 research synthesis docs exist in `docs/research/synthesis/`.
- [ ] AC2: All 12 unabsorbed §9 resolved questions appear in destination artifacts' Rationale sections.
- [ ] AC3: `grep -r "PRODUCT-IDEATION" .` returns 0 hits outside plan files.
- [ ] AC4: `PRODUCT-IDEATION.md` does not exist in the working tree.
- [ ] AC5: `AGENTS.md` and `README.md` no longer reference PRODUCT-IDEATION.md.
- [ ] AC6: `ci/check_foundations.py` passes with 0 errors.
- [ ] AC7: Full test suite green.
- [ ] AC8: CHANGELOG.md `[Unreleased]` describes the change.
- [ ] AC9: RESEARCH-BIBLIOGRAPHY.md exists and its one provenance note is updated.

## Out of Scope

- Deleting RESEARCH-BIBLIOGRAPHY.md — it's a standalone reference catalog with independent value.
- Updating plan files' historical references — plans are permanent records.
- Editing ADR Context sections — ADRs are immutable once accepted.

## Notes

**Why synthesis docs instead of bloating principles:** Principles are stances, not evidence dumps. Research findings belong in a dedicated layer that principles cite in their Source field and specs cite in their Rationale field. This preserves the provenance chain: bibliography → synthesis → principle/spec.

**Why delete instead of archive:** The SDD model should fully absorb source documents. Keeping a "fully-decomposed" monolith creates a gravitational pull — people read it instead of the decomposed artifacts, and it drifts out of sync. Git history is the archive. The working tree should contain only living artifacts.

**ADR References are navigational metadata:** ADR body text (Context, Decision, Consequences) is immutable. References sections serve navigation and are updated when targets move — same as updating a hyperlink when a page moves.
