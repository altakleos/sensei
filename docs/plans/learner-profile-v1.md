---
feature: learner-profile-v1
serves: docs/specs/learner-profile.md
design: docs/design/learner-profile-state.md
status: done
date: 2026-04-20
---
# Plan: Learner Profile V1 — Spec, Schema, Validator, Mastery Gate

> **Retroactive reconstruction** for commit `d763021`.

First feature to exit scaffolding and make real product decisions. Defines what Sensei tracks at v1, ships a JSON Schema, and implements two of the five ADR-0006 v1 helpers (`check_profile` + `mastery_check`).

## Scope

Per the clarifying question decision: **minimal profile** — `expertise_map` only (topic → mastery/confidence/last_seen/attempts/correct). No `learning_style`, `pace`, `weaknesses`, or `engagement` at v1. Each deferred dimension will earn its own spec when a protocol needs it.

## Tasks

- [x] T1: Spec — invariants: ordered mastery enum, unit-float confidence, ISO-8601 UTC timestamps, schema-versioned, absence-means-none, monotonicity-not-enforced → `docs/specs/learner-profile.md`
- [x] T2: Design — yaml shape, field semantics, slug convention (`^[a-z][a-z0-9-]*$`), validator contract, mastery-check contract (depends: T1) → `docs/design/learner-profile-state.md`
- [x] T3: JSON Schema realizing T1/T2 with `patternProperties` for topic slugs (depends: T2) → `src/sensei/engine/schemas/profile.schema.json`
- [x] T4: `check_profile.py` — JSON Schema validation + cross-field check (`correct <= attempts`), exit 0/1/2 for ok/schema/cross-field (depends: T3) → `src/sensei/engine/scripts/check_profile.py`
- [x] T5: `mastery_check.py` — enum-ordered gate; absent topic = mastery `none`; exit 0/1/3 for pass/invalid/fail (depends: T4) → `src/sensei/engine/scripts/mastery_check.py`
- [x] T6: Unit tests for T4 and T5 covering library + CLI + subprocess paths → `tests/scripts/test_check_profile.py`, `tests/scripts/test_mastery_check.py`
- [x] T7: Add `jsonschema>=4.18` to runtime deps → `pyproject.toml`
- [x] T8: Index updates → `docs/specs/README.md`, `docs/design/README.md`, `src/sensei/engine/schemas/README.md`

## Acceptance Criteria

- [x] AC1: Spec and design cross-link and both reference ADR-0006
- [x] AC2: A minimal valid profile (schema_version 0, learner_id, empty expertise_map) passes the validator
- [x] AC3: Every invariant in the spec has a negative test (invalid mastery level, confidence out of range, bad slug, cross-field violation, missing required field, wrong schema_version)
- [x] AC4: `mastery_check` with an absent topic exits 3 and reports `current_mastery: none`
- [x] AC5: Protocol-style subprocess invocation works for both helpers
- [x] AC6: Full suite remains green (42/42)
- [x] AC7: CI verify.yml passes on the feature commit

## Deferred (separate plans)

- Numeric confidence threshold in mastery_check (e.g., `--min-confidence 0.9` for the 90% threshold in §3.6).
- Schema validators for other state files (`knowledge-state.yaml`, `curriculum.yaml`, `progress.yaml`) — each needs its own spec first.
- Seeding a minimal `profile.yaml` during `sensei init` — separate plan.

## Outcome

Shipped in commit `d763021` (11 files, 711 insertions). 23 new tests; total suite now 42 passing. First feature with a full spec→design→schema→implementation→verification chain.
