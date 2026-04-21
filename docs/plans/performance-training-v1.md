---
feature: performance-training-v1
serves: docs/specs/performance-training.md
design: docs/design/performance-training.md
status: done
date: 2026-04-21
---
# Plan: Performance Training V1 (Stages 1–4)

Implements the performance training phase overlay for stages 1–4 (learn → automate → verbalize → time pressure). The phase is a context-layer overlay on the existing four-mode model, not a fifth mode. Follows the single phase protocol composition from ADR-0020: one file (`protocols/performance-training.md`) loaded alongside the active mode when the phase is active for the current goal.

**V1 boundary:** stages 5–6 (simulated evaluation, full mock) are explicitly deferred to V2. The phase protocol stubs those stages as `[V2 — not yet active]`.

## Pre-Analysis: Component → File Mapping

| Component | File(s) | New or Modified |
|-----------|---------|-----------------|
| Config defaults | `src/sensei/engine/defaults.yaml` | modified |
| Goal schema | `src/sensei/engine/schemas/goal.schema.json` | modified |
| Phase protocol | `src/sensei/engine/protocols/performance-training.md` | **new** |
| Engine kernel | `src/sensei/engine/engine.md` | modified |
| Goal protocol | `src/sensei/engine/protocols/goal.md` | modified |
| Schema tests | `tests/scripts/test_check_goal.py` | modified |
| Transcript fixture | `tests/transcripts/performance_training.md` | **new** |
| Fixture test | `tests/transcripts/test_fixtures.py` | modified |

## Phase 1 — Config and Schema (foundation)

- [x] T1: Add `performance_training` section to `defaults.yaml` — `mastery_gate: solid` (minimum mastery level to enter phase, matching spec invariant 4), `stage_thresholds: { automate: 3, verbalize: 2, time_pressure: 3 }` (correct recalls / clear explanations / timed solves needed to advance). → `src/sensei/engine/defaults.yaml`
- [x] T2: Extend `goal.schema.json` — add optional `performance_training` object to the goal-level properties with fields: `active` (boolean, default false), `stage` (integer 1–6, current stage in the stack), `entered_at` (date-time or null, when phase was activated), `event_type` (enum: interview, exam, certification, or null), `event_date` (date-time or null, target performance event). Add a `$defs/PerformanceTraining` definition with `additionalProperties: false`. → `src/sensei/engine/schemas/goal.schema.json` (depends: T1)
- [x] T3: Update `check_goal.py` tests — add cases for the new `performance_training` schema fields: valid object, missing (optional), null sub-fields, stage out of range (should fail), active without entered_at (cross-field check if applicable). → `tests/scripts/test_check_goal.py` (depends: T2)
- [x] T4: Run full test suite — confirm existing tests pass with schema additions. → verify (depends: T3)

## Phase 2 — Phase Protocol (core artifact)

- [x] T5: Create `protocols/performance-training.md` — the single phase protocol file per ADR-0020. Structure:
  1. **Phase preamble** — entry conditions (mastery gate from `config.performance_training.mastery_gate`), current stage reference (from goal's `performance_training.stage`), general phase principles (performance ≠ learning, staged progression, no skipping).
  2. **Stage definitions** — for each of stages 1–4:
     - Stage 1 (Learn): Tutor frames material in performance-format shape. No time pressure. Format-aware understanding.
     - Stage 2 (Automate): Tutor drills pattern recognition; Challenger introduces minor variations. Fluent recall without deliberation.
     - Stage 3 (Verbalize): Challenger enforces thinking-aloud. Learner explains solutions aloud. Probes for clarity.
     - Stage 4 (Time pressure): Clock introduced. Challenger sets time constraints; Tutor adds pacing guidance. Familiar problems, new variable is speed.
     - Stages 5–6: stubbed as `[V2 — not yet active]`.
  3. **Per-mode overlay sections** — `## When Tutor is Active`, `## When Challenger is Active`, `## When Assessor is Active`, `## When Reviewer is Active`. Each section defines the behavioral deltas from spec invariant 3 (Tutor: time awareness cues, pacing guidance, format-specific framing; Challenger: interview-style pressure, format constraints, thinking-aloud requirements; Assessor: V2 stub; Reviewer: weak-spot targeting from phase attempts).
  4. **Stage progression rules** — how the engine determines when to advance (threshold checks against `config.performance_training.stage_thresholds`).
  → `src/sensei/engine/protocols/performance-training.md`

## Phase 3 — Engine Wiring

- [x] T6: Update `engine.md` § Session Start — Mode Composition — add Step 2.5 (or equivalent) documenting the phase overlay loading. When the current goal has `performance_training.active: true`, load `protocols/performance-training.md` in full as an additional context layer after the active mode. Composition becomes: `personality (full) + active mode (full) + inactive §Summaries + performance-training.md (full)`. Reference ADR-0020. → `src/sensei/engine/engine.md` (depends: T5)
- [x] T7: Update `engine.md` § Configuration — document the new `performance_training.*` config keys (`mastery_gate`, `stage_thresholds.*`) alongside existing config documentation. → `src/sensei/engine/engine.md` (depends: T1, T6)
- [x] T8: Update `engine.md` § Dispatch Table — add a row for performance-phase entry signals (e.g., "I have an interview coming up" / "Prepare me for the exam" / "Start performance training") dispatching to `protocols/goal.md` §Performance Phase Activation. → `src/sensei/engine/engine.md` (depends: T6)

## Phase 4 — Goal Protocol Integration

- [x] T9: Update `goal.md` — add a `## Performance Phase Activation` section. This section:
  1. Detects when the learner expresses a performance event (interview, exam, certification) or when mastery gate conditions are met.
  2. Runs `mastery_check.py` (or equivalent mastery assessment) against the goal's completed nodes to verify the learner meets the `config.performance_training.mastery_gate` threshold (default: `solid`).
  3. If gate is met: sets `performance_training.active: true`, `stage: 1`, `entered_at: <now>`, `event_type`, `event_date` in the goal YAML. Validates with `check_goal.py`. Informs the learner the performance phase is active.
  4. If gate is NOT met: explains what mastery gaps remain and continues normal learning. Does not activate the phase.
  → `src/sensei/engine/protocols/goal.md` (depends: T2, T5)
- [x] T10: Update `goal.md` — add a `## Performance Phase Stage Advancement` section documenting how stage transitions work within the goal protocol. When the phase protocol's stage progression rules indicate advancement, the goal protocol updates `performance_training.stage` in the goal YAML and re-validates. → `src/sensei/engine/protocols/goal.md` (depends: T9)

## Phase 5 — Tests and Verification

- [x] T11: Transcript fixture — a tier-1 lexical fixture for performance-phase behavior. Scenario: learner with an active goal at solid mastery says "I have an interview in two weeks"; fixture asserts the performance phase activates, stage 1 begins, and Tutor overlay behavior (format-aware framing) is present. → `tests/transcripts/performance_training.md`, `tests/transcripts/test_fixtures.py` (depends: T9)
- [x] T12: Schema validation tests — extend `test_check_goal.py` with a goal file that has `performance_training` populated, confirm `check_goal.py` accepts it. Also test: stage=7 rejected, active=true without entered_at behavior, event_type not in enum rejected. → `tests/scripts/test_check_goal.py` (depends: T2, T4)
- [x] T13: Run full test suite — confirm green. → verify (depends: T11, T12)

## Phase 6 — Finalize

- [x] T14: Update `docs/plans/README.md` — add this plan to the index table under the appropriate section. → `docs/plans/README.md` (depends: T13)
- [x] T15: Full test suite green, `sensei verify` passes. → verify (depends: T14)

---

## V1 STOPS HERE

Stages 5–6 (simulated evaluation, full mock) are **V2 scope**. They depend on:
- Mock interview protocol (not yet specified)
- Realistic scoring rubrics (not yet designed)
- Assessor's simulated-evaluation overlay (stubbed in V1 phase protocol as `[V2 — not yet active]`)

V2 work will be tracked in a separate `performance-training-v2` plan.

---

## Acceptance Criteria

- [x] AC1: **Spec invariant 1 (phase, not a mode)** — no new mode files created. `protocols/modes/` still contains exactly four files (tutor, challenger, assessor, reviewer). Performance training is a single overlay protocol file.
- [x] AC2: **Spec invariant 2 (ordered stages)** — the phase protocol defines stages 1–4 in order. Stage progression rules enforce sequential advancement (no skipping). Goal schema tracks `stage` as an integer.
- [x] AC3: **Spec invariant 3 (mode behavioral deltas)** — the phase protocol contains per-mode overlay sections (`When Tutor is Active`, `When Challenger is Active`, etc.) with the observable behavioral deltas specified in the spec: Tutor adds time awareness/pacing/format framing; Challenger adds interview pressure/format constraints/thinking-aloud; Reviewer targets execution gaps.
- [x] AC4: **Spec invariant 4 (mastery gate)** — `defaults.yaml` contains `performance_training.mastery_gate: solid`. Goal protocol checks mastery level before activating the phase. A learner below `solid` is not entered into performance training.
- [x] AC5: `goal.schema.json` accepts the `performance_training` object on goals; existing goal files without it remain valid (all fields optional/defaulted).
- [x] AC6: `engine.md` documents the phase overlay composition (when loaded, how composed) and the new config keys.
- [x] AC7: Transcript fixture validates performance-phase activation and stage-1 behavior.
- [x] AC8: Full test suite green, `sensei verify` passes.
