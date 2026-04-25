---
feature: defaults-schema-required-keys
serves: docs/specs/release-process.md
design: "Schema-only tightening of an existing validator (defaults.schema.json + sensei verify path). No new mechanism. Pattern instantiation of the schema-validation contract introduced at v0.1.0a19."
status: done
date: 2026-04-25
---
# Plan: Mark `defaults.yaml` Inner Tunables as `required` in the Schema

The 2026-04-25 audit Move #3 (part 1): close a soft-failure mode in `defaults.schema.json`. The schema currently asserts `additionalProperties: false` on every nested mapping but does not declare any of the inner tunables as `required`. A learner override of `memory: {}` in `learner/config.yaml` would silently drop both `half_life_days` and `stale_threshold` from the merged config, leaving `goal_priority.py` and the review pipeline to fall through to hardcoded script defaults — exactly the silent-misconfiguration class that v0.1.0a19's CHANGELOG entry promised to catch ("rejects typos, wrong types, and out-of-range tunables").

## Targets and Verified Evidence

| # | Target | Evidence (re-verified 2026-04-25 post-merge) |
|---|---|---|
| 1 | Top-level `required` is only `["schema_version"]` | `python3 -c "import json; print(json.load(open('src/sensei/engine/schemas/defaults.schema.json'))['required'])"` returns `['schema_version']`. |
| 2 | All nine nested mappings have no `required` list | Inspection: `mentor`, `learner`, `curriculum`, `memory`, `hints`, `cross_goal`, `interleaving`, `session_notes`, `performance_training` all return `(none)`. |
| 3 | The deep-merge loader (`scripts/config.py`) treats partial overrides as additive | Confirmed by reading the loader in PR #25 history; learner-side `memory: {}` overrides the engine's `memory:` block whole-key-replace style. |

## Approach

This is a **behavioral change to the validation contract**: a learner config that today passes `sensei verify` will fail tomorrow if it overrode an inner mapping without listing every required key. That is the right outcome — silent defaults-fall-through is exactly what the schema-validation feature was added to prevent — but it warrants an **ADR-lite** because:

- Concrete trigger: changes a default that alters out-of-box behaviour for any user who has used a partial-mapping override.
- Concrete trigger: moves something from allowed (silent fall-through) to blocked (verify failure).

Per `docs/decisions/README.md` § ADR-lite triggers, both triggers fire. ADR-lite is mandatory.

The list of "required" keys must match exactly the keys engine code or protocol prose reads from the merged config. Source of truth is `engine.md`'s configuration section (`engine.md:276–289`) plus the `defaults.yaml` body. Any tunable named in either is required.

## Tasks

- [x] T1 — Investigation pass: walk `engine.md:276–289` and the protocols (`grep -rE "config\.(memory|hints|cross_goal|interleaving|session_notes|performance_training)\." src/sensei/engine/protocols/`) to enumerate every config dotpath actually read at runtime. Produce a checklist; cross-reference against `defaults.yaml` keys.
- [x] T2 — `docs/decisions/0023-defaults-schema-required-keys.md` (ADR-lite): one-paragraph rationale per the ADR-lite template (`docs/decisions/README.md:67–81`). Decision: required-key arrays added to nested mappings. Why: silent fall-through defeats the verify gate. Alternative: leave as-is and document the soft contract.
- [x] T3 — `src/sensei/engine/schemas/defaults.schema.json`: add `required: [...]` to each of the nine nested mappings. Keys are the union of (a) keys named in `engine.md` Configuration section and (b) keys with non-empty defaults in `defaults.yaml`.
- [x] T4 — `tests/ci/test_defaults_schema.py`: add cases for (a) full defaults.yaml passes; (b) `memory: {}` override fails with a specific `required` error citing both missing keys; (c) `cross_goal: {}` override fails citing all four required keys; (d) partial-with-some-keys override fails citing the missing one.
- [x] T5 — `CHANGELOG.md` `[Unreleased]` → `### Changed`: one-line entry — "`sensei verify` now rejects partial nested overrides in `learner/config.yaml` that drop required tunables (e.g. `memory: {}`). Previously these silently fell through to hardcoded script defaults."
- [x] T6 — Run full local pipeline via `.venv/bin/`. All green.
- [x] T7 — Commit on `feat/defaults-schema-required-keys` branch; open PR.

## Acceptance Criteria

- [x] AC1 — `defaults.schema.json` validates the existing `defaults.yaml` (after merge) without error.
- [x] AC2 — Negative cases T4(b)/T4(c)/T4(d) fail with specific `required` errors.
- [x] AC3 — `python ci/check_defaults_schema.py` (or whatever the existing test entrypoint is) reports OK on `main`.
- [x] AC4 — ADR-0023 file exists, references `defaults.schema.json` and the v0.1.0a19 schema-validated tunables CHANGELOG entry.
- [x] AC5 — CHANGELOG `[Unreleased] / Changed` line landed.
- [x] AC6 — `.venv/bin/pytest && .venv/bin/ruff check . && .venv/bin/mypy && python ci/check_*.py` all green.

## Out of Scope

- Re-architecting the deep-merge loader to do soft-merge of partial mappings instead of whole-key-replace. That would be a behavior change to `scripts/config.py` and warrants its own plan + likely a full ADR.
- Adding new tunables. This plan only formalizes the contract for existing ones.
- Tightening the schema for the `learner: {}` reserved-for-expansion top-level key (still `additionalProperties: true` per the schema). It has no inner contract today.
