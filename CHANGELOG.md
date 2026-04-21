# Changelog

All notable user-visible changes to Sensei (distributed as `sensei-tutor` on PyPI) are recorded in this file.

The format is based on [Keep a Changelog 1.1](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Policy lives in [`docs/specs/release-communication.md`](docs/specs/release-communication.md).

## [Unreleased]

- test: convert `tests/test_frontier.py` and `tests/test_mutate_graph.py` from subprocess-only invocations to direct `main(argv) + capsys` calls (keeping one subprocess smoke per file as an ADR-0006 CLI-entry regression guard). Coverage jumps from 63% to 81% — the gap was a pytest-cov measurement artifact, not a testing gap. `--cov-fail-under` ratcheted from 60 → 80.
- fix: `hint_decay.py` now returns exit code 1 cleanly on missing hints file or YAML parse errors (previously propagated `FileNotFoundError` / raised uncaught). Aligns with every other engine script's `is_file() + return 1` pattern.
- refactor: `migrate.main()` signature normalized to `main(argv: list[str] | None = None) -> int` — matches every other engine script, enables direct `main(...)` testing without subprocess. `__main__` block wraps with `sys.exit(main())`. No caller change (`sensei upgrade` uses `migrate_instance()` directly, not `main()`).
- test: convert `tests/test_hint_decay.py` CLI test and extend `tests/test_migrate.py` with direct `main(argv) + capsys` coverage plus error-path tests (missing file, corrupt YAML, parser-required flags). Coverage jumps from 81% to 85%; `hint_decay.py` 69 → 92%, `migrate.py` 42 → 78%. `--cov-fail-under` ratcheted from 80 → 83.
- test: second Tier-2 behavioural E2E — `tests/e2e/test_assess_protocol_e2e.py` invokes headless Claude Code to run the `assess` protocol against a pre-seeded profile (topic at `developing` mastery) and asserts Step 5 ran: `attempts` and `correct` incremented, `last_seen` updated, profile still validates against `profile.schema.json`. Single-turn `-p` mode is simulated via a fixture that supplies both the assessment request and the learner's stipulated correct answer. Complements the `goal` E2E — one data point was an anecdote, two is a pattern. Release playbook updated to reference both tests as the pre-release gate (~3–5 min total, real combined run measured ~4 min); `tests/transcripts/README.md` Tier-2 row updated to plural.
- test: round-3 coverage ratchet — new error-path tests for `sensei status`, `sensei upgrade`, `sensei verify`, and the `_engine_source` / `_atomic_replace_engine` helpers in `tests/test_cli.py`. Covers status's stale-topic detection, verify's FAIL output for missing files / invalid YAML / schema-validation failures, the "prior run crashed between swap steps" recovery branch, and the `_engine_source` missing-bundle guard. `cli.py` jumps from 67% to 96%; overall coverage 85% → 91%. `--cov-fail-under` ratcheted from 83 → 89.
- security: `sensei init --learner-id` now strictly validates the value against `^[A-Za-z0-9_-]{1,64}$` and rejects anything else with a clear error. Previously the value was interpolated verbatim into `instance/profile.yaml` via `string.Template.substitute`, which left a local YAML-injection surface (`--learner-id $'foo\\nexpertise_map: {pwn: {mastery: mastered}}'` could seed an arbitrary profile). The profile is now serialised via `yaml.safe_dump(dict(...))`, not string templating. Inputs with whitespace, braces, dots, slashes, quotes, or other metacharacters now error out at parse time — normal names and handles ("alice", "learner-01", "ab_cd") still work. The `--learner-id` value eventually ends up in LLM prompts, so this also removes a prompt-steering vector.
- docs: add `SECURITY.md` at repo root — supported-versions table (latest `0.1.x` only during alpha), private disclosure channel (GitHub Security Advisories), response-time targets for the solo maintainer, and an explicit in-scope / out-of-scope threat model that carves prompt-injection-via-learner-content and LLM-output-correctness *out* of scope. Matches the single-user product scope in `docs/foundations/vision.md`.
- refactor: `sensei init` now reads the AGENTS.md boot document from `src/sensei/engine/templates/AGENTS.md` in the bundle instead of a hardcoded `_AGENTS_MD` constant in `cli.py`. Eliminates the drift risk between the CLI source and the engine (AGENTS.md references `engine.md`, `protocols/`, and `defaults.yaml` — changes to the bundle now naturally pull along the boot doc). `sensei verify` gains the template path in its expected-files list; `ci/check_package_contents.py` now requires `sensei/engine/templates/AGENTS.md` in every shipped wheel. No behaviour change at init time — the written `AGENTS.md` is byte-identical to before.
- docs: retroactively mark ADR-0017 (file-drop ingestion), ADR-0018 (curriculum boosting over rewriting), and ADR-0019 (universal inbox) as `provisional` — all three govern hints/curriculum-boosting behaviour that has unit-test coverage but no transcript fixture or Tier-2 E2E validating live LLM execution. Each ADR gains a provisional-rationale callout pointing at the review trigger. Per ADR-0011 and the `provisional` status convention documented in `docs/decisions/README.md`.
- docs: add `docs/operations/context-budget.md` — measured token cost of the Sensei boot chain per session. Tier A (always-loaded baseline) is ~4,400–4,600 tokens; dispatched protocols add 760–3,700 tokens, with `goal.md` as the outlier at ~3,700. Peak scenario (goal creation with schema in context) sits near 9,200 tokens before conversation history. Tested-on matrix names the agents that comfortably fit (Claude Code, Kiro, Cursor, Windsurf, Copilot Chat on GPT-4o) and flags the < 16K-context category as risky. Includes a re-measurement snippet and a follow-up TODO to automate the measurement into a CI gate against a Tier-A ceiling.

## [0.1.0a9] — 2026-04-21

- fix: atomic writes in migrate and mutate_graph — profile.yaml and goal files can no longer be corrupted by interrupted writes (refs ADR-0004 atomicity contract)
- fix: protocol prose now matches script CLIs — `goal.md`, `tutor.md`, `hints.md`, and `challenger.md` had subprocess invocations with wrong flag names and positional verbs that would cause LLM-executed commands to fail (e.g., `mutate_graph.py collapse --topic` → `--operation collapse --node`, `hint_decay.py --registry` → `--hints-file` with required `--expire-threshold` and `--expire-after-days`). New CI linter (`tests/ci/test_protocol_script_consistency.py`) imports each script, captures its argparse, and validates every protocol invocation against it.
- fix: `sensei upgrade` and `sensei init --force` swap the `.sensei/` engine bundle atomically via a copy-to-temp + aside + rename-in-place sequence. A failed copy or interrupted swap no longer destroys the learner's existing `.sensei/`, and a crash mid-swap is recovered on the next invocation (honors the atomicity contract in `docs/operations/release-playbook.md` and ADR-0004).
- fix: `goal_priority.py` now honors `instance/config.yaml` overrides of `memory.half_life_days` and `memory.stale_threshold` via new `--half-life-days` and `--stale-threshold` CLI flags (previously hardcoded to 7.0 and 0.5, so learner overrides silently did not apply to goal ranking). `engine.md` session-start invocation updated to pass the config values.
- refactor: `sensei status` now imports `freshness_score` from `decay.py` instead of reimplementing `2**(-elapsed/half_life)` inline, eliminating drift risk across call sites that share the exponential-decay formula.
- test: synthetic seed transcript at `tests/transcripts/assess.dogfood.md` unblocks the four previously-skipped `assess` fixtures (assessor-silence, no-teaching-during-assessment, gate-result-reported, two-failure-diagnosis). Covers all three protocol branches — pass, one-more, and two-failure prerequisite diagnosis — in one file. Marked `status: seed` per the `review.dogfood.md` precedent; replace with a real captured session at the next release per `docs/design/transcript-fixtures.md` § Cadence.
- fix: cleanup — CLI module docstring no longer calls `status`/`upgrade`/`verify` "stubs" (all three are fully implemented); removed an unresolved `>>>>>>> plan/cross-goal` merge marker from the 0.1.0a4 section; `hint_decay.py` imports PyYAML unconditionally like every other engine script (PyYAML is a hard dependency).
- test: new coverage for cross-goal intelligence — `tests/scripts/test_global_knowledge.py` exercises the mastery-level threshold (`solid` and above are "known globally") and the CLI error paths; `tests/scripts/test_goal_priority.py` directly guards the a6 regression by asserting `paused`/`completed`/`abandoned` goals never appear in rankings, plus priority ordering, decay-risk scoring, and `--half-life-days` override honoring. `tests/test_schema_validation.py` round-trips valid/invalid profile + goal fixtures against the JSON schemas and checks that `migrate_profile` output still validates (guards the a6 goal-shape regression class).
- chore: pytest-cov wired into the verify gate (`pytest>=7`, `pytest-cov>=5`). Coverage floor set at 60% as the measured v0.1.0a9 baseline; `frontier.py` and `mutate_graph.py` read low because their tests invoke the scripts via subprocess, which pytest-cov cannot observe. Follow-up: convert those tests to direct `main(argv)` calls and ratchet the floor upward.
- test: Tier-2 behavioural E2E for the `goal` protocol (`tests/e2e/test_goal_protocol_e2e.py`). Scaffolds a fresh instance, invokes headless Claude Code (`claude -p --permission-mode acceptEdits`), and asserts the emitted `instance/goals/*.yaml` validates against `goal.schema.json`. Runs as a manual pre-release gate (see `docs/operations/release-playbook.md`); skipped in default CI when `claude` is missing or neither `ANTHROPIC_API_KEY` nor `SENSEI_E2E` is set. Tier structure documented in `tests/transcripts/README.md` per ADR-0011.
- docs: vision and README narrow the overclaimed "any LLM agent" / "agent-agnostic" language to "agent-portable by design" and name Claude Code and Kiro as the dogfood-validated agents. Shims for Cursor, Copilot, Windsurf, Cline, Roo, and AI Assistant remain in place awaiting further validation. Aider dropped from vision prose (no Aider shim exists today).
- docs: `docs/decisions/README.md` now documents the `provisional` ADR status for decisions that govern still-`draft` protocols or design properties no fixture has yet validated. Existing ADRs unchanged; authors of new ADRs should prefer `provisional` in those cases.
- chore: `ci/check_foundations.py` now warns (non-blocking) when a spec declares `realizes:` or `serves:` but names neither `fixtures:` nor `fixtures_deferred:`. Twelve existing specs currently emit this warning and will be backfilled incrementally. Warning is scheduled to hard-fail after two releases to match ADR-0011's "prose verified by prose" discipline.
- docs: `docs/specs/README.md` spec template grows `fixtures:` and `fixtures_deferred:` fields plus a short section explaining the fixture-naming convention. Couples new decisions to verification evidence per ADR-0011 and the v0.1.0a9 methodology gate.

## [0.1.0a8] — 2026-04-20

### Fixed

- Tutor mode: after posing a question, treat the learner's next message as their answer (not a meta-request).

## [0.1.0a7] — 2026-04-20

### Fixed

- Goal protocol Step 4: corrected YAML format to match actual schema (nodes as map, not list; correct field names).
- Goal protocol: "spawned" is the correct state for not-yet-started topics (not "pending").
- Added dependency guidance to engine.md for pipx/system-Python environments.

## [0.1.0a6] — 2026-04-20

### Fixed

- `goal_priority.py`: paused goals no longer appear in priority rankings (only active goals ranked).
- `sensei init`: now creates `instance/goals/` directory for goal state files.
- `test_e2e_smoke.py`: uses `sys.executable` and `shutil.which` instead of hardcoded `.venv/` paths (fixes CI).

## [0.1.0a5] — 2026-04-20

### Added

- Reviewer protocol (`protocols/reviewer.md`): structured code/solution review with three-tier feedback (what works, issues, key learning), self-assessment calibration, and iterative revision support.
- Challenger protocol (`protocols/challenger.md`): structured challenge sequences with difficulty calibration, challenge-type selection from the disruption toolkit, observe→calibrate loop, and profile-tracked weakness patterns.
- Cross-goal intelligence: `global_knowledge.py` (skip already-mastered topics across goals) and `goal_priority.py` (rank goals by priority, decay risk, and recency for session start).

## [0.1.0a4] — 2026-04-20

### Added

- Cross-goal intelligence: `scripts/global_knowledge.py` (checks if a topic is mastered globally across goals), `scripts/goal_priority.py` (ranks active goals by priority + decay risk + recency). Goal protocol gains decay-aware re-entry (Step 2.5) and global knowledge skip (Step 6). Engine auto-selects highest-priority goal at session start.
- Goal lifecycle transitions: pause, resume, abandon, and automatic completion. Goals persist across transitions with full progress preservation.
- Schema migration in `sensei upgrade`: detects profile schema version mismatches and applies forward migrations automatically.
- Tutor protocol (`protocols/tutor.md`): the pedagogical engine governing multi-turn teaching via explain→probe→reshape cycles, with explanation strategies by topic type, formative micro-assessment, two-failure prerequisite diagnosis, and mid-session triggers for review weaving and hint integration.

## [0.1.0a3] — 2026-04-20

### Added

- Curriculum graph implementation: `scripts/frontier.py` (frontier computation with hints-based priority boosting) and `scripts/mutate_graph.py` (5 validated graph operations — activate, complete, collapse, spawn, expand — with cycle detection). Curriculum tunables in `defaults.yaml`.
- Status protocol (`protocols/status.md`): conversational progress reporting synthesizing profile mastery, curriculum state, hint freshness, and review staleness into a 5–8 sentence narrative.
- Parallel agent execution: spec, design, ADR-0016, and shell scripts (`scripts/worktree-setup.sh`, `scripts/worktree-teardown.sh`) for git worktree-based isolation enabling multiple LLM agents to implement plans simultaneously.
- Branching and PR convention added to `docs/development-process.md`. All changes now land on main through a branch and pull request.

## [0.1.0a2] — 2026-04-20

### Added

- Parallel agent execution: spec, design, ADR-0016, and shell scripts for git worktree-based isolation enabling multiple LLM agents to implement plans simultaneously
- Release-communication spec (`docs/specs/release-communication.md`) and this `CHANGELOG.md`. Every future release must ship with a dated entry here; `ci/check_package_contents.py` enforces the presence of an entry for the tag being released.
- Behavioural verification layer (`tests/transcripts/`) with a pytest loader for transcript fixtures and the first fixture file (`review.md`). Per [ADR-0011](docs/decisions/0011-transcript-fixtures.md).
- `docs/foundations/` — new cross-cutting-concerns layer per [ADR-0012](docs/decisions/0012-foundations-layer.md). Contains `vision.md`, 14 principles (6 technical migrated from `sensei-implementation.md` + 7 pedagogical pillars + one mentor-relationship principle), and the Jacundu persona. Specs gain optional `serves:` / `realizes:` / `stressed_by:` frontmatter; `ci/check_foundations.py` is a hard-fail CI gate that catches broken references.
- `docs/development-process.md` gains a project-agnostic "Foundations" section describing the layer as source material above the six-layer stack.
- Full decomposition of `PRODUCT-IDEATION.md` into SDD artifacts (Plans 1–5): 7 new foundation principles, 6 new feature specs, 3 new design docs, 3 new ADRs (0013–0015), and 4 research synthesis docs. The original ideation document is deleted (preserved in git history).
- `docs/research/` reorganized into a 3-tier structure: `bibliography.md` (58 annotated citations), `reports/` (deep investigative reports), `synthesis/` (curated findings with `[Bibliography #N]` provenance citations).
- Behavioral modes runtime: `protocols/personality.md` (base personality, always loaded) + four mode authoring files (`protocols/modes/{tutor,assessor,challenger,reviewer}.md`). Engine kernel (`engine.md`) rewritten with full composition instructions and transition rules.
- Assessment protocol (`protocols/assess.md`): summative mastery gating with deterministic scoring via `mastery_check.py`, two-failure prerequisite diagnosis, assessor exception enforcement.
- 27 mermaid diagrams across specs, design docs, ADRs, and principles. Diagram convention added to `development-process.md`.
- mypy --strict + ruff added to CI pipeline. All source passes both.
- 15 new tests (127 total): CLI commands, config loader, YAML error paths.
- Goal lifecycle: `protocols/goal.md` (6-step protocol: parse goal → triage three unknowns → generate curriculum DAG → validate → begin teaching), `schemas/goal.schema.json`, `scripts/check_goal.py` (DAG cycle detection, single-active-node enforcement, prerequisite resolution).
- `sensei status` enhanced: shows learner ID, topic count, mastery distribution, and stale topics due for review.
- `sensei verify` implemented: checks 18 expected engine files + profile schema validation. Reports specific missing files on failure.
- `sensei upgrade` implemented: replaces `.sensei/` engine bundle from installed package, preserves `instance/` data. Detects same-version noop.
- `sensei init` now creates `instance/goals/` directory for goal state files.
- Assessment transcript fixture (`tests/transcripts/assess.md`) with 4 test cases.
- Hints ingestion protocol + hint_decay.py for curriculum hint processing.

### Fixed

- `cli.py`: learner-id with `{` or `}` no longer crashes (switched from `str.format()` to `string.Template`).
- `config.py`: invalid YAML now raises `ValueError` with clear message instead of silent `{}` or crash.
- `check_foundations.py`: Windows line endings no longer break frontmatter parsing; malformed YAML handled gracefully.
- `decay.py`: `import math` moved to top level (PEP 8).
- `engine.md`: status updated from "scaffolding stub" to reflect active protocols.

### Notes

- The behavioral modes and assessment protocol are runtime prose-as-code — they change how an LLM agent behaves when reading the `.sensei/` bundle. Users installing `pip install sensei-tutor` and running `sensei init` will get the full four-mode mentor system.

## [0.1.0a1] — 2026-04-20

First public alpha. An architecture-validation release — not suitable for real learners yet.

### Added

- **SDD doc layering** — `docs/{specs,design,decisions,plans,operations}` with a project-agnostic `development-process.md` and ADRs 0001–0010.
- **Engine bundle** at `src/sensei/engine/` — `engine.md` kernel with a dispatch table, `defaults.yaml` tunables, placeholder directories for `protocols/`, `scripts/`, `prompts/`, `schemas/`, `profiles/`.
- **First prose-as-code protocol**: `protocols/review.md`. Retrieval-only spaced-repetition review — stale-first selection, one topic at a time, no reteach inside review, post-response profile update only.
- **V1 deterministic helpers** per [ADR-0006](docs/decisions/0006-hybrid-runtime-architecture.md): `config.py` (deep-merge loader), `classify_confidence.py` (4-quadrant classifier), `decay.py` (exponential-forgetting freshness), `check_profile.py` (JSON Schema + cross-field validator), `mastery_check.py` (enum-ordered gate).
- **Learner profile schema** at `schemas/profile.schema.json` — `expertise_map` with per-topic mastery enum, confidence, `last_seen`, attempts/correct counters.
- **CLI** — `sensei init <target>` scaffolds a complete instance with `AGENTS.md` plus eight tool-specific shims (Claude Code, Cursor, Kiro, Copilot, Windsurf, Cline, Roo Code, JetBrains AI) so the boot chain works across agents that do not natively read `AGENTS.md`.
- **CI + release pipeline** — GitHub Actions `verify.yml` (pytest matrix Python 3.10–3.13) and `release.yml` (three jobs with OIDC trusted publishing and a human-approval gate on the `pypi` environment).
- **`ci/check_package_contents.py`** wheel validator — asserts engine-bundle integrity, rejects instance-content leaks, enforces tag ↔ `__version__` concordance.

### Known limitations

- `sensei status`, `sensei upgrade`, and `sensei verify` are stubs. Only `sensei init` is functional.
- The review protocol writes only `last_seen` / `attempts` / `correct`. Mastery and confidence calibration are deferred to a future protocol per [ADR-0008](docs/decisions/0008-review-writes-audit-fields-only.md).
- FSRS scheduling, FIRe fractional credit propagation, per-learner speed calibration, and affect detection are deferred to a v2 ADR per [ADR-0006](docs/decisions/0006-hybrid-runtime-architecture.md).
- Protocol behavioural verification — whether an LLM actually follows the nine numbered steps — is currently manual-only. Automated behavioural testing is scoped as the next feature.

[Unreleased]: https://github.com/altakleos/sensei/compare/v0.1.0a1...HEAD
[0.1.0a1]: https://github.com/altakleos/sensei/releases/tag/v0.1.0a1
