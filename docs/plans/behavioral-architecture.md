---
feature: behavioral-architecture
serves: (decomposition — PRODUCT-IDEATION.md §3 into SDD artifacts)
design: (produced by this plan — no pre-existing design doc)
status: done
date: 2026-04-20
---
# Plan: Behavioral Architecture — PRODUCT-IDEATION §3 Decomposition

Decomposes `PRODUCT-IDEATION.md` §3 (Architecture, §3.1–3.11) into proper SDD artifacts: foundation principles, feature specs, design docs, and ADRs. This is Plan 1 of 5 in the full PRODUCT-IDEATION decomposition; all other plans depend on it.

## Pre-Analysis: Where Each Subsection Lands

| §    | Subsection                    | Destination                                        |
|------|-------------------------------|----------------------------------------------------|
| 3.1  | Principles Over Rules         | Already captured → ADR-0006 + P-prose-is-code      |
| 3.2  | One Mentor                    | Already captured → P-mentor-relationship            |
| 3.3  | Four Behavioral Modes         | **NEW spec** → `behavioral-modes.md`               |
| 3.4  | Organic Transitions           | Absorbed → behavioral-modes spec invariants         |
| 3.5  | Principles Not Mode-Switching | **NEW principle** → `P-principles-not-modes`        |
| 3.6  | Assessor Exception            | Absorbed → behavioral-modes + review-protocol       |
| 3.7  | Diagnostic vs Summative       | **NEW spec** → `assessment-protocol.md`             |
| 3.8  | Two-Failure Principle         | **NEW principle** → `P-two-failure-prerequisite`    |
| 3.9  | Performance Gap               | **NEW spec** → `performance-training.md` (v2 draft)|
| 3.10 | Silence Across Modes          | Absorbed → P-silence-is-teaching + behavioral-modes |
| 3.11 | Adaptive Behaviors            | Absorbed → learner-profile + behavioral-modes       |

## Phase 1 — Foundation principles (single commit)

Two new principles with no dependencies on unwritten artifacts. Can land immediately.

- [ ] T1: `docs/foundations/principles/principles-not-modes.md` — kind: technical. Statement: behavioral modes are a design-time authoring abstraction, not a runtime abstraction. What loads into the LLM is a composed set of principles with active emphasis, not four separate mode definitions. Captures §3.5's prompt-attention-dilution guidance (base personality + active emphasis + brief summaries). → `docs/foundations/principles/principles-not-modes.md`
- [ ] T2: `docs/foundations/principles/two-failure-prerequisite.md` — kind: pedagogical. Statement: after two failed attempts at the same concept, diagnose the missing prerequisite instead of trying a third explanation. Resolves the tension between modality variation and Math Academy's insight (one good explanation + prerequisites > many explanations). Captures §3.8. → `docs/foundations/principles/two-failure-prerequisite.md`

## Phase 2 — Behavioral modes spec + design (single commit)

The primary new spec. Absorbs §3.3, §3.4, §3.6 (assessor exception as invariant), §3.10 (silence profiles), and §3.11 (profile-driven adaptation).

- [ ] T3: `docs/specs/behavioral-modes.md` — spec defining the four behavioral profiles (tutor, assessor, challenger, reviewer) as manifestations of one mentor personality. Key invariants: (a) modes emerge from principles, not explicit switches; (b) transitions are system-driven and invisible to the learner; (c) each mode has a defined silence profile; (d) forbidden language patterns per mode (no "Great question!" in tutor, no teaching in assessor); (e) assessor uses deterministic scoring, never LLM reasoning for mastery; (f) profile signals drive adaptive mode responses (§3.11 table); (g) include "First Session" subsection for crisis-state learners (honest assessment with dignity — use §7.1's first-move script as exemplar); (h) include "Verification" subsection defining mode-bleed testing (automated behavioral tests for hard rules, confusion signals for soft boundaries); (i) Rationale must state: time pressure is not a mode, it's a signal that modifies how principles apply; (j) Overview must include the four informal role analogies (teacher/examiner/sparring-partner/code-reviewer from §2.3) as human-readable framing. Frontmatter: `realizes: [P-mentor-relationship, P-silence-is-teaching, P-principles-not-modes]`, `stressed_by: [persona-jacundu]`. → `docs/specs/behavioral-modes.md`
- [ ] T4: `docs/design/behavioral-modes.md` — design doc covering: (a) how the engine composes per-mode authoring files into one principle set at runtime (base personality + active emphasis + brief summaries per §3.5); (b) transition trigger table (learner asks question → tutor, submits code → reviewer, etc. per §3.4); (c) the signal→response adaptation table from §3.11 mapped to mode-specific behaviors, including the push-vs-comfort diagnostic from §7.1 ("Is the emotion blocking learning or protecting identity?"); (d) the assessor exception enforcement mechanism (subprocess to mastery_check.py per ADR-0006). → `docs/design/behavioral-modes.md`
- [ ] T5: ADR: Context Composition Strategy — records the decision that the engine composes one unified principle set from per-mode authoring files, loading active mode's full content + brief summaries of others, rather than loading all four simultaneously. Motivated by prompt attention dilution (§3.5). → `docs/decisions/0013-context-composition.md`
- [ ] T6: Update `docs/decisions/README.md` — add ADR-0013 row. → `docs/decisions/README.md`

## Phase 3 — Assessment protocol spec (single commit)

Depends on behavioral-modes spec (references assessor mode definition).

- [ ] T7: `docs/specs/assessment-protocol.md` — spec defining two distinct assessment types. Diagnostic: inline probing within tutor mode, includes "rusty vs never-learned" detection via recognition probes and relearning speed. Summative: mastery gate at topic boundaries, invokes assessor mode, deterministic scoring via mastery_check.py, 90% threshold. Key invariants: (a) diagnostic and summative are never conflated; (b) summative uses deterministic scoring, never LLM reasoning; (c) summative results write to learner profile; diagnostic results inform but don't gate; (d) the assessor exception (no teaching during summative) is absolute. Frontmatter: `realizes: [P-mastery-before-progress, P-scripts-compute-protocols-judge, P-two-failure-prerequisite]`, `stressed_by: [persona-jacundu]`. → `docs/specs/assessment-protocol.md`

## Phase 4 — Performance training spec (single commit, v2 draft)

Depends on behavioral-modes spec (modifies mode behaviors).

- [ ] T8: `docs/specs/performance-training.md` — status: **draft** (not accepted — this is a v2 feature). Spec defining the Performance Preparation Stack (learn → automate → verbalize → time pressure → simulated evaluation → full mock) as a cross-cutting journey phase that modifies all four modes. Key invariants: (a) performance training is a phase, not a fifth mode; (b) the six-stage stack is ordered and progressive; (c) each stage modifies existing mode behaviors rather than replacing them (Tutor→time awareness, Challenger→interview pressure, Assessor→evaluation conditions); (d) entry requires sufficient mastery across relevant curriculum. Rationale must state: performance training is a cross-cutting journey phase, not a fifth mode or separate agent (§9 resolved question). Include §7.1's three-week arc as the canonical example of mode-emphasis shifting across a goal lifecycle (tutor-heavy → challenger-heavy → assessor/reviewer-heavy). Frontmatter: `realizes: [P-mentor-relationship, P-mastery-before-progress]`, `stressed_by: [persona-jacundu]`. → `docs/specs/performance-training.md`

## Phase 5 — Backreference wiring + verification (single commit)

- [ ] T9: Create `docs/decisions/0014-principles-over-state-machines.md` — NEW ADR recording the decision to use principle-driven LLM pedagogy over deterministic state machines. Context: full evidence table from §3.1 (StratL narrow finding, PedagogicalRL-Thinking +134%, LearnLM +31%, Harvard RCT 2x, GPT-5.2 0% leakage, Khanmigo 700K users). Decision: three-layer architecture (Layer 1: deterministic code/yaml, Layer 2: principle-driven LLM, Layer 3: multi-agent coordination). Consequences: enables the product model — principle-based context files ship in a pip package and make any frontier LLM a good tutor. Cross-references ADR-0006 (runtime split). → `docs/decisions/0014-principles-over-state-machines.md`
- [ ] T10: Update `docs/decisions/README.md` — add ADR-0014 row. → `docs/decisions/README.md`
- [ ] T11: Verify §3.2 coverage — confirm P-mentor-relationship covers the four context-trigger examples from §3.2 (learner asks question → teaching, submits code → review, suspects overconfidence → assessment, demonstrates mastery → challenge). Add to Implications if missing. → `docs/foundations/principles/mentor-relationship.md`
- [ ] T12: Update existing specs with new `realizes:` references where the behavioral-modes spec creates new linkable principles. Specifically: review-protocol.md gains `P-principles-not-modes` if appropriate. → `docs/specs/review-protocol.md`
- [ ] T13: Run `ci/check_foundations.py` — confirm 0 errors. New principles may show as orphan warnings until Phase 2 specs land; that's expected. → verify
- [ ] T14: Full test suite green. → verify
- [ ] T15: Append Unreleased entry to `CHANGELOG.md` covering the behavioral-architecture decomposition. → `CHANGELOG.md`

## Acceptance Criteria

- [ ] AC1: Two new foundation principles exist: `P-principles-not-modes` (technical) and `P-two-failure-prerequisite` (pedagogical), both with `status: accepted`.
- [ ] AC2: `docs/specs/behavioral-modes.md` exists with status: accepted, covering the four modes, transitions, silence profiles, forbidden language, assessor exception, and adaptive behaviors.
- [ ] AC3: `docs/design/behavioral-modes.md` exists covering composition strategy, transition triggers, and signal→response table.
- [ ] AC4: ADR-0013 (context composition) exists and is indexed.
- [ ] AC5: `docs/specs/assessment-protocol.md` exists with status: accepted, distinguishing diagnostic from summative assessment.
- [ ] AC6: `docs/specs/performance-training.md` exists with status: draft (v2 feature).
- [ ] AC7: `ci/check_foundations.py` passes with 0 errors on the full repo.
- [ ] AC8: Full test suite green.
- [ ] AC9: CHANGELOG.md `[Unreleased]` describes the change.

## Out of Scope

- Implementing behavioral mode protocols (`.sensei/protocols/tutor.md`, etc.) — that's implementation work after the spec is accepted.
- Implementing the assessment protocol — separate implementation plan after the spec is accepted.
- Performance training implementation — v2, deferred.
- §4 (Interaction Model), §5 (Curriculum), §2.4 (Deep Frontiers) — separate plans.

## Notes

**Why §3.9 lands as a draft spec, not accepted:** The ideation itself flags that the Performance Preparation Stack "doesn't map cleanly" to the four modes. It's a v2 feature that needs design iteration. Drafting the spec now captures the intent; accepting it waits until the behavioral modes are implemented and the interaction patterns are proven.

**Why no separate design doc for assessment-protocol:** The assessment protocol's mechanism is straightforward — it composes the existing mastery_check.py helper (ADR-0006) with the behavioral-modes transition system. A design doc would largely restate the spec invariants. If implementation reveals complexity, a design doc can be added then.

**Why §3.6 is absorbed rather than getting its own artifact:** The assessor exception is an invariant of two existing artifacts (review-protocol spec, behavioral-modes spec) and one existing ADR (ADR-0006). Creating a standalone artifact would duplicate content across four places. The principle is: the exception is enforced where it matters, not described in a fifth location.
