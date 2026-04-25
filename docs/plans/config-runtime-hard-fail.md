---
feature: config-runtime-hard-fail
serves: docs/specs/learner-profile.md
design: "Pattern instantiation of ADR-0023 (verify-time schema strictness). No new mechanism — same validator, same schema, flipped default. ADR-0025 (lite) records the gate change."
status: done
date: 2026-04-25
---
# Plan: Runtime Config Validation Hard-Fails by Default

`src/sensei/engine/scripts/config.py:41–71` (`_soft_validate`) prints `WARN: config: ...` to stderr on schema errors and returns the merged config anyway. Every protocol invocation (via subprocess) calls `load_config`. A learner who edits `learner/config.yaml` badly and never runs `sensei verify` gets a stderr line that scrolls off; the engine silently substitutes hardcoded script defaults — exactly the silent-misconfiguration mode ADR-0023 fixed at the *verify* gate but not at *runtime*.

This plan promotes the runtime path to hard-fail by default, with a `SENSEI_CONFIG_SOFT_FAIL=1` env-var opt-out reserved for engine-repair / dev / CI-smoke scenarios. ADR-0025 (lite) records the gate change.

**Redirected mid-flight.** An earlier draft of this plan also tightened `defaults.schema.json` `learner` mapping from `additionalProperties: true` to `additionalProperties: false` (the audit's "subtlest landmine #1"). On implementation, this conflicted directly with `tests/ci/test_defaults_schema.py:test_learner_section_remains_open`, which ADR-0023 added to deliberately preserve the open `learner.*` surface for forward-compat. ADR-0023 stands; the schema tightening is dropped from this plan. ADR-0025 only changes runtime strictness, not the schema's permissive learner block.

## Context

- **Spec:** `docs/specs/learner-profile.md` already declares the configuration contract. No spec change needed — this is a runtime-strictness adjustment to a previously-soft check.
- **Caller surface (probed):** the only caller of `load_config` in `src/` is `src/sensei/cli.py:496` inside `sensei verify`. Engine helper scripts receive their tunables via CLI flags from protocol-side subprocess invocations, not via direct imports of `config.py`. Blast radius for the gate change is therefore narrow: the CLI-internal path inside `verify`, and the test surface in `tests/scripts/test_config.py`.
- **Test scaffolding:** `sensei init` (cli.py:215–245) writes a valid empty `learner/config.yaml` plus `.sensei/defaults.yaml`. Empty learner config deep-merged on top of valid defaults validates cleanly. No existing test fixture is expected to break; if one does, that signals a real fixture bug, not test-noise.
- **Design-skip rationale:** see frontmatter `design:` field. ADR-0025 (lite) is the load-bearing artifact; `defaults.schema.json` change is a one-line tightening backed by the existing `defaults.yaml` shape (`learner: {}`).

## Tasks

- [x] T1: Write ADR-0025 → `docs/decisions/0025-runtime-config-hard-fail.md` (lite shape: Decision / Why / Alternative). Update `docs/decisions/README.md` index row.
- [x] T2: Define `ConfigValidationError(ValueError)` in `src/sensei/engine/scripts/config.py` and rename `_soft_validate` → `_validate`. New behaviour:
  - On schema errors: collect the formatted error list. If `os.environ.get("SENSEI_CONFIG_SOFT_FAIL") == "1"`, print each error to stderr prefixed with `WARN: config: ...` and return the merged dict (today's behaviour). Otherwise, raise `ConfigValidationError` with the joined error list as the message.
  - Same `try: import jsonschema; except ImportError: return` short-circuit (verify still owns the canonical strict gate; `load_config` defers when jsonschema isn't installed). (depends: T1.)
- [~] T3: ~~Tighten `defaults.schema.json` `learner.additionalProperties` to `false`.~~ **Dropped.** Conflicts with `tests/ci/test_defaults_schema.py:test_learner_section_remains_open` per ADR-0023's deliberate forward-compat reservation. The audit's "subtlest landmine #1" remains open as a known limitation; closing it requires its own ADR superseding ADR-0023, which is out of scope here.
- [x] T4: Update `sensei verify` (`src/sensei/cli.py:488–504`) to catch `ConfigValidationError` from `load_config` and append each line to the `errors` list. Without this, verify's structured FAIL report would be replaced by an uncaught exception traceback when the merged config is bad. (depends: T2.)
- [x] T5: Extend `tests/scripts/test_config.py`:
  - Happy path unchanged — empty learner override + valid defaults loads cleanly.
  - Non-dict overlay (e.g. `memory: 5`) is whole-key-replaced by `_deep_merge` and surfaces as a schema type error → `ConfigValidationError` by default. (Note: `memory: {}` does NOT trigger this — recursive deep-merge fills inner keys from defaults; the failure mode lives at the schema layer per ADR-0023, not at the merge layer.)
  - Type error (e.g. `memory.half_life_days: "seven"`) raises by default.
  - Unknown top-level key raises by default.
  - Same bad config with `SENSEI_CONFIG_SOFT_FAIL=1` (use `monkeypatch.setenv`) returns merged dict and prints `WARN: config:` to stderr (capture via `capsys`).
  - Truthy-but-not-`1` env value (e.g. `"true"`) does NOT downgrade — only the literal `"1"` opts out.
  - Clean config with `SENSEI_CONFIG_SOFT_FAIL=1` emits no WARN.
  - Use `monkeypatch.delenv` to ensure default is hard-fail (don't rely on shell state). (depends: T2.)
- [x] T6: Verify `sensei verify` against a deliberately-bad `learner/config.yaml` end-to-end via a CLI test (extend `tests/test_cli.py` rather than re-spin a verify-specific harness). Asserts the FAIL report names the offending dotpath and exits 1. (depends: T4.)
- [x] T7: Append `CHANGELOG.md` `## [Unreleased]` entry under `### Changed` describing the runtime gate change and the schema tightening, citing ADR-0025. Single line. (depends: T1.)
- [x] T8: Add a row to `docs/plans/README.md` index for this plan. (depends: nothing; runs at the very end so the plan filename is already in place.)

## Acceptance Criteria

- [x] AC1: `.venv/bin/pytest --no-cov` passes locally; total count grows by the new tests in T5+T6 (~5–6 new passing); no existing tests regress.
- [x] AC2: `.venv/bin/pytest` passes the project's existing `--cov-fail-under=92` gate; coverage on the modified `config.py` is ≥ 92%.
- [x] AC3: `.venv/bin/ruff check .` and `.venv/bin/mypy` are clean.
- [x] AC4: `python ci/check_foundations.py`, `check_links.py`, `check_changelog_links.py`, `check_plan_completion.py`, `check_release_audit.py --tag <unrelated>` all behave as before (the change does not touch CI gate code paths).
- [x] AC5: `python -c "from pathlib import Path; from sensei.engine.scripts.config import load_config; load_config(Path('src/sensei/engine'), Path('/tmp'))"` succeeds (defaults alone validate); the same call against a tampered `learner/config.yaml` raises `ConfigValidationError`.
- [x] AC6: `SENSEI_CONFIG_SOFT_FAIL=1 python -c "..."` against a bad config returns the merged dict and emits `WARN:` lines to stderr.
- [x] AC7: ADR-0025 indexed in `docs/decisions/README.md` in number order; ADR shape ≤ 12 body lines.
- [~] AC8: ~~`defaults.schema.json` `learner` block carries `additionalProperties: false`.~~ Dropped with T3.

## Out of Scope

- Migrating `learner: {}` to a populated-with-real-defaults shape. ADR-0025 only changes strictness; the *content* of the learner section remains "reserved for future expansion."
- Adding a `sensei doctor` or `--dry-run` mode. The opt-out is via env var only; no new CLI surface.
- Touching ADR-0023 or its plan. ADR-0025 supplements it, not supersedes.
- Changing `_deep_merge` semantics. Whole-key replacement at non-dict overlay boundaries is intentional per ADR-0023; the validator catches the resulting shape, not the merge logic.

## Notes

- The env-var opt-out exists so a maintainer debugging a broken schema file or a partially-migrated instance is not locked out of the engine. Treat its use in production as a defect signal: every WARN stream is a future-tense bug report.
- After this lands, the soft-fail prose in `docs/operations/release-playbook.md` and `src/sensei/engine/scripts/config.py`'s `_soft_validate` docstring need a sweep — both currently read "soft-warn ... `sensei verify` is the strict gate." Post-change, the runtime path is *also* strict by default; keep the verify gate prose accurate but drop the "only the verify gate is strict" framing.
