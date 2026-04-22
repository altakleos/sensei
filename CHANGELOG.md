# Changelog

All notable user-visible changes to Sensei (distributed as `sensei-tutor` on PyPI) are recorded in this file.

The format is based on [Keep a Changelog 1.1](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Policy lives in [`docs/specs/release-communication.md`](docs/specs/release-communication.md).

## [Unreleased]

### Added

- `ci/check_links.py` — maintainer-side validator that walks every `*.md` under `docs/` and fails CI on any relative markdown link that does not resolve to an existing file. Skips external URLs, same-file anchors, and fenced code blocks. Wired into `verify.yml` alongside the existing `check_foundations.py` step.

### Fixed

- Five broken relative links in docs repaired: `docs/foundations/principles/mentor-relationship.md` (behavioral-modes spec), `docs/design/folder-structure.md` (ADR-0004 filename drift), `docs/operations/parallel-agents.md` (ADR-0016 filename drift), `docs/specs/hints.md` (Jacundu persona filename), and `docs/research/bibliography.md` (self-referential `docs/research/` path).

- Atomic writes now fsync the containing directory on POSIX after `os.replace`, closing a gap where the rename's dirent update could be lost on power loss (ADR-0004 durability contract). Applies to both `atomic_write_text` (learner state files) and `_atomic_replace_engine` (each rename in the `.sensei/` swap).
- `sensei upgrade` now migrates learner data **before** swapping the engine bundle. A migration failure no longer leaves a new engine paired with old-format data — the old engine remains on disk and is still compatible with the unmigrated data.
- `migrate.py` writeback uses `yaml.safe_dump` instead of `yaml.dump`, preventing future migrations from emitting unsafe Python-tagged YAML that `safe_load` would then refuse to re-read.
- `review_scheduler.py` skips malformed goal YAML with a warning on stderr instead of crashing the cross-goal pipeline on a single corrupt file.
- `frontier.py` priority is now computed from alphabetical slug order instead of YAML insertion order, removing hidden coupling between `curriculum.yaml` key layout and teaching sequence.
- `sensei status` surfaces a `Warning:` line for topics with unparseable `last_seen` timestamps. Previously these were silently coerced to stale, masking profile corruption.
- `ci/check_foundations.py` now reports invalid YAML frontmatter as an error instead of silently treating it as absent frontmatter — a broken principle file could previously drop out of the foundations index unnoticed.
- `session_allocator.allocate_session` now distributes per-goal residue via largest-remainder apportionment, so session budgets are no longer under-allocated by up to N-1 minutes across N goals.

### Changed

- Migration function contract (`migrate.py`): functions registered in `PROFILE_MIGRATIONS` / `GOAL_MIGRATIONS` must be **pure** — accept a dict and return a new dict, without mutating the input. Guarantees that a partially-failed migration chain cannot leave the caller's dict half-transformed. Registries are empty today, so no external callers are affected.
- `_parse_iso` helper consolidated into `sensei.engine.scripts._iso.parse_iso`. Five scripts previously carried verbatim copies of the same five-line helper.
- Cycle detection in `mutate_graph._has_cycle` and `check_goal._check_cross_field` is now O(N+E) via a precomputed reverse-adjacency index (was O(N²) per dequeue).
- `profile.schema.json` enforces the `^[A-Za-z0-9_-]{1,64}$` pattern on `learner_id`, mirroring the CLI `--learner-id` validator so profiles written outside the CLI cannot smuggle YAML- or prompt-injecting characters.
- `mutate_graph.mutate` refactored into per-op helpers (`_do_activate`, `_do_complete`, `_do_collapse`, `_do_spawn`, `_do_expand`) for readability. Public behaviour (exit codes, JSON output, error messages) is byte-identical.
- `goal_priority._is_stale` now calls `decay.freshness_score` instead of reimplementing the exponential arithmetic inline.

### Tests

- On-disk round-trip of a registered non-identity migration (`test_migrate_file_runs_registered_migration_end_to_end`) seeds migration-scaffolding coverage ahead of the first real migration.
- `FORBIDDEN_PREFIXES` snapshot test locks the set of wheel-forbidden paths so silent removal of any prefix fails CI.

## [0.1.0a11] — 2026-04-21

### Added

- Performance training V1 — phase overlay protocol for stages 1–4 (concept → automate → verbalize → time pressure). New protocol, design doc, ADR-0021, schema extensions, config tunables, and transcript fixture.
- Cross-goal intelligence — all 4 spec invariants implemented: re-demonstration override, review deduplication, deadline-aware priority + session allocation, decay-aware resume. Five new scripts (`review_scheduler.py`, `session_allocator.py`, `resume_planner.py`, `goal_priority.py`, `global_knowledge.py`).
- Adaptive session opener — mentor bridges sessions with 2–3 sentences of context (goal, last topic, stale count), then immediately resumes teaching. No greeting filler, no status dumps.
- Fixture coverage promoted from CI warning to hard-fail. Specs declaring `realizes:`/`serves:` must now name `fixtures:` or `fixtures_deferred:`. All 12 specs already compliant.
- Design docs for cross-goal intelligence (pipeline topology) and goal-lifecycle (creation pipeline and script orchestration).
- ADR-0020: release self-bypass for solo maintainer (provisional).

### Changed

- `instance/` directory renamed to `learner/` across codebase — clearer semantics for the user-facing folder.
- Development process prose-as-code audit: 23 fixes across 11 files. Document authority hierarchy added, process concepts consolidated into `development-process.md`, stale summaries updated, boot chain improved, worked examples and glossary added.
- CHANGELOG v0.1.0a9 section reformatted to Keep a Changelog headers. Compare links added for a2–a10.

### Fixed

- 4 ruff lint errors resolved (E501 line length, I001 import sort).
- Garbled content at end of `sensei-implementation.md` removed.
- Script names in `sensei-implementation.md` corrected (hyphens → underscores to match actual filenames).
- Plan-before-branch step ordering paradox fixed in `development-process.md`.

## [0.1.0a10] — 2026-04-21

### Added

- Hints protocol E2E test (`tests/e2e/test_hints_protocol_e2e.py`) — seeds inbox, invokes hints triage, asserts hints.yaml populated.
- Frontier and mutate_graph tests converted from subprocess-only to direct `main(argv) + capsys` calls. Coverage 63% → 81%.

### Fixed

- `hint_decay.py`: returns exit code 1 cleanly on missing file or YAML parse errors (previously raised uncaught exceptions).

## [0.1.0a9] — 2026-04-21

### Fixed

- Atomic writes in migrate and mutate_graph — profile.yaml and goal files can no longer be corrupted by interrupted writes (refs ADR-0004 atomicity contract).
- Protocol prose now matches script CLIs — `goal.md`, `tutor.md`, `hints.md`, and `challenger.md` had subprocess invocations with wrong flag names and positional verbs that would cause LLM-executed commands to fail. New CI linter (`tests/ci/test_protocol_script_consistency.py`) validates every protocol invocation against its script's argparse.
- `sensei upgrade` and `sensei init --force` swap the `.sensei/` engine bundle atomically via a copy-to-temp + aside + rename-in-place sequence. A failed copy or interrupted swap no longer destroys the learner's existing `.sensei/`.
- `goal_priority.py` now honors `instance/config.yaml` overrides of `memory.half_life_days` and `memory.stale_threshold` via new CLI flags (previously hardcoded).
- Cleanup — CLI module docstring no longer calls `status`/`upgrade`/`verify` "stubs"; removed an unresolved merge marker from the v0.1.0a4 section; `hint_decay.py` imports PyYAML unconditionally.

### Changed

- `sensei status` now imports `freshness_score` from `decay.py` instead of reimplementing the formula inline, eliminating drift risk.
- Vision and README narrow "any LLM agent" language to "agent-portable by design" and name Claude Code and Kiro as dogfood-validated agents.

### Added

- Synthetic seed transcript at `tests/transcripts/assess.dogfood.md` unblocks the four previously-skipped `assess` fixtures. Marked `status: seed`; replace with a real captured session at the next release.
- Cross-goal intelligence test coverage — `test_global_knowledge.py`, `test_goal_priority.py`, `test_schema_validation.py`.
- pytest-cov wired into the verify gate. Coverage floor set at 60% as the v0.1.0a9 baseline.
- Tier-2 behavioural E2E for the `goal` protocol (`tests/e2e/test_goal_protocol_e2e.py`). Manual pre-release gate.
- `provisional` ADR status documented in `docs/decisions/README.md`.
- `ci/check_foundations.py` warns when specs with `realizes:` lack `fixtures:`. Scheduled to hard-fail after two releases.
- Spec template gains `fixtures:` and `fixtures_deferred:` fields per ADR-0011 methodology gate.

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

[Unreleased]: https://github.com/altakleos/sensei/compare/v0.1.0a11...HEAD
[0.1.0a11]: https://github.com/altakleos/sensei/compare/v0.1.0a10...v0.1.0a11
[0.1.0a10]: https://github.com/altakleos/sensei/compare/v0.1.0a9...v0.1.0a10
[0.1.0a9]: https://github.com/altakleos/sensei/compare/v0.1.0a8...v0.1.0a9
[0.1.0a8]: https://github.com/altakleos/sensei/compare/v0.1.0a7...v0.1.0a8
[0.1.0a7]: https://github.com/altakleos/sensei/compare/v0.1.0a6...v0.1.0a7
[0.1.0a6]: https://github.com/altakleos/sensei/compare/v0.1.0a5...v0.1.0a6
[0.1.0a5]: https://github.com/altakleos/sensei/compare/v0.1.0a4...v0.1.0a5
[0.1.0a4]: https://github.com/altakleos/sensei/compare/v0.1.0a3...v0.1.0a4
[0.1.0a3]: https://github.com/altakleos/sensei/compare/v0.1.0a2...v0.1.0a3
[0.1.0a2]: https://github.com/altakleos/sensei/compare/v0.1.0a1...v0.1.0a2
[0.1.0a1]: https://github.com/altakleos/sensei/releases/tag/v0.1.0a1
