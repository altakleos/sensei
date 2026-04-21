---
feature: goal-lifecycle-transitions
serves: docs/specs/goal-lifecycle-transitions.md
design: "Follows goal-lifecycle spec pattern + ADR-0006 (hybrid runtime)"
status: done
date: 2026-04-21
---
# Plan: Goal Lifecycle Transitions

> **Retroactive reconstruction** — this plan documents work already shipped in v0.1.0a4.

Adds pause, resume, abandon, and complete transitions to the goal lifecycle. Goals move through `active → paused → active` (resume), `active → abandoned`, or `active → completed` (automatic on curriculum completion). At most one goal may be active at a time.

## Tasks

- [x] T1: Add `paused`, `abandoned`, `completed` to goal status enum in `goal.schema.json` → `src/sensei/engine/schemas/goal.schema.json`
- [x] T2: Add `paused_at`, `resumed_at` timestamp fields to goal schema → `src/sensei/engine/schemas/goal.schema.json` (depends: T1)
- [x] T3: Add § Lifecycle Transitions to `protocols/goal.md` with transition rules → `src/sensei/engine/protocols/goal.md` (depends: T2)
- [x] T4: Enforce at-most-one-active-goal in goal protocol prose → `src/sensei/engine/protocols/goal.md` (depends: T3)
- [x] T5: Add automatic completion detection (all nodes collapsed or completed) → `src/sensei/engine/protocols/goal.md` (depends: T3)
- [x] T6: Add schema validation tests for new status values → `tests/scripts/test_check_goal.py` (depends: T1)
- [x] T7: Add schema round-trip tests → `tests/test_schema_validation.py` (depends: T2)

## Acceptance Criteria

- [x] AC1: Goal schema accepts all 4 statuses (`active`, `paused`, `abandoned`, `completed`)
- [x] AC2: Pausing preserves all curriculum and profile data
- [x] AC3: Resume recomputes frontier with current freshness
- [x] AC4: At most one active goal enforced by protocol
