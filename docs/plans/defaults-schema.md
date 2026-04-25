---
feature: defaults-schema
serves: docs/specs/release-process.md
design: "Pattern instantiation of the existing schemas/*.schema.json + cli.py validation pattern. No new mechanism."
status: done
date: 2026-04-25
---
# Plan: Schema-Validated `defaults.yaml`

`src/sensei/engine/defaults.yaml` is the canonical tunable surface — `mastery_threshold`, `half_life_days`, `mastery_gate`, etc. — but unlike `profile.yaml` and `goal.yaml` it has **no JSON schema**. Consequences observed during the project analysis:

- A typo in a tunable name (e.g. `memory.half_life_dais`) silently falls through to script-level hardcoded defaults; no error, no warning.
- A wrong type (`half_life_days: "seven"`) only surfaces when a script parses it, far from the source.
- New tunables can be added without an authoritative reference of what's allowed.

This plan adds `schemas/defaults.schema.json` modelled on `profile.schema.json`, validates it during `sensei verify`, and registers the schema in the engine manifest.

## Tasks

- [x] T1: Create `src/sensei/engine/schemas/defaults.schema.json` (Draft-2020-12, `additionalProperties: false` at every level). Cover every key currently in `defaults.yaml`:
  - `schema_version` (const 0 — bump on any field-semantics change)
  - `mentor.emotional_state.{staleness_minutes, degradation_intervention_threshold}`
  - `mentor.metacognitive_state.{staleness_days, fading_threshold}`
  - `learner` (empty object placeholder per current state)
  - `curriculum.{max_nodes, initial_size_min, initial_size_max, prior_knowledge_percentile, frontier_max, mastery_threshold, min_attempts, max_decompose_children}`
  - `curriculum.depth_profiles.{exposure, functional, deep}` each with the same numeric subset
  - `memory.{half_life_days, stale_threshold}`
  - `hints.{half_life_days, boost_weight, max_boost, cluster_threshold, expire_threshold, expire_after_days, relevance_floor}`
  - `cross_goal.{deadline_weight, min_session_minutes, review_dedup, concept_dedup}`
  - `interleaving.{enabled, intensity, min_mastery}`
  - `session_notes.{load_count, max_entries}`
  - `performance_training.mastery_gate` (enum: shaky, solid, deep, mastered)
  - `performance_training.stage_thresholds.{automate, verbalize, time_pressure, simulated_eval, full_mock}`
  - Numeric fields constrained to plausible ranges (e.g. `half_life_days: minimum 0.1`, `mastery_threshold: 0..1`, `intensity: 0..1`, `min_session_minutes: minimum 1`).
  - Each field carries a `description:` quoting the existing comment in `defaults.yaml`.
- [x] T2: Register `schemas/defaults.schema.json` in `src/sensei/engine/manifest.yaml` under `required:`.
- [x] T3: Extend `src/sensei/cli.py:verify` to validate `.sensei/defaults.yaml` against the schema (mirroring the existing session-notes validation block at `cli.py:460-478`). Report each violation with its JSON path.
- [x] T4: Extend `src/sensei/engine/scripts/config.py` (the deep-merge loader) to **optionally** validate the merged result if a schema is reachable. Soft-fail (warn to stderr, return the merged config anyway) — protocols depend on the loader, so a hard failure would brick the whole engine if a learner adds a typo. The hard gate lives in `sensei verify`.
- [x] T5: Add `tests/test_cli.py` cases:
  - Happy path: `sensei verify` passes on a clean instance.
  - Detect a tunable typo (e.g. write `memory.half_life_dais: 7` to `learner/config.yaml`, run verify, expect failure with the `memory` path).
  - Detect a wrong type (`memory.half_life_days: "seven"`, expect failure).
  - Detect an out-of-range value (`memory.stale_threshold: 1.5`, expect failure).
- [x] T6: Add `tests/ci/test_defaults_schema.py`:
  - Load `defaults.yaml` and assert it validates against `defaults.schema.json` (forward check — every shipped default is schema-valid).
  - Snapshot test: every top-level key in `defaults.yaml` appears in the schema's `properties` (catches new tunables that get added without schema updates).
- [x] T7: `CHANGELOG.md` — append under `## [Unreleased]` → `### Added`:
  > `defaults.yaml` is now JSON-Schema validated. `sensei verify` rejects typos, wrong types, and out-of-range tunables; previously these silently fell through to hardcoded script defaults.

## Acceptance Criteria

- [x] AC1: `python -m json.tool < src/sensei/engine/schemas/defaults.schema.json` parses without error (valid JSON).
- [x] AC2: `sensei verify` on a clean instance returns OK (no regression).
- [x] AC3: A learner config with a typo'd or out-of-range tunable causes `sensei verify` to exit 1 with a JSON-path-pointed error (verified by T5).
- [x] AC4: New tunable added to `defaults.yaml` without schema update fails `tests/ci/test_defaults_schema.py` (verified by writing a temporary key and confirming the snapshot test fires).
- [x] AC5: Full pipeline green: `pytest && ruff check . && mypy && python ci/check_*.py`.

## Out of Scope

- Strictly checking values match the comments in `defaults.yaml` (e.g. that `mastery_threshold: 0.9` actually corresponds to "minimum correct/attempts ratio") — that's a doc-rot prevention task, separate concern.
- A migration path for older `defaults.yaml` (would need `schema_version` bump). Not needed at v0 — a typo/range failure is just a verify failure today, not a migration trigger.
- Validating the *learner override* `learner/config.yaml` directly. The merged result is what scripts see; that's where validation lives. A separate spec could later constrain learner overrides to a stricter subset.
