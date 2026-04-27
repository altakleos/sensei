# Changelog

All notable user-visible changes to Sensei (distributed as `sensei-tutor` on PyPI) are recorded in this file.

The format is based on [Keep a Changelog 1.1](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Policy lives in [`docs/specs/release-communication.md`](docs/specs/release-communication.md).

## [Unreleased]

### Added
- Contributor onboarding scaffolding: top-level `Makefile` (`setup`, `test`, `lint`, `typecheck`, `validators`, `gate`, `clean`) and `CONTRIBUTING.md`. All Makefile targets shell out to `.venv/bin/<tool>` so local pre-merge checks match CI; `make gate` runs the full bundle. Closes the gap where `pytest` on a fresh clone failed because `pyproject.toml` mandates `--cov=…` and PEP 668 blocks system-pip from installing `pytest-cov` — the venv discipline that lived only inside `docs/operations/release-playbook.md` is now mechanised at the entry point. Per [`docs/plans/contributor-onboarding-makefile.md`](docs/plans/contributor-onboarding-makefile.md).
- ADR-immutability CI gate. New `ci/check_adr_immutability.py` enforces the long-standing process invariant that "ADRs are immutable once accepted" (`docs/development-process.md` § ADRs). Body edits to `accepted` / `accepted (lite)` ADRs fail the build unless the commit message carries an `Allow-ADR-edit: NNNN — <reason>` trailer or the diff is purely a `## Historical Note` append. Frontmatter-only status FSM transitions (provisional → accepted, accepted → superseded, plus `superseded-by:` annotations) are always allowed. Wired into `verify.yml`; runs in PR mode (BASE..HEAD) and push-to-main mode (HEAD only). Closes the only convention-only invariant in the SDD method without a mechanical guard, per the 2026-04-26 audit. Per [`docs/plans/adr-immutability-gate.md`](docs/plans/adr-immutability-gate.md).

## [0.1.0a21] — 2026-04-26

### Added
- Teaching-density metric for Tier-1 fixtures. New helper `src/sensei/engine/scripts/teaching_density.py` counts mentor appearances of a curated teaching-language taxonomy (`let me explain`, `the (correct/right) answer is`, `think about`, etc.) per mentor turn. Seven fixtures (assess, challenger, cross_goal_review, hints, review, reviewer, status) ship with `teaching_density: {max: 0.0}` bands enforcing the assessor-exception and no-reteach invariants from `engine.md` § Invariants. Closes the third (and final) quantitative metric named by the 2026-04-25 follow-up audit Risk #4 — the family is now silence_ratio + question_density + teaching_density. Per [`docs/plans/teaching-density-metric.md`](docs/plans/teaching-density-metric.md).
- Question-density metric for Tier-1 fixtures. New helper `src/sensei/engine/scripts/question_density.py` measures mentor questions per mentor turn; transcript fixtures may declare an optional `question_density: {min, max}` band that fails CI if a Socratic protocol regresses toward telling (low density) or a narrative protocol drifts toward interrogation (high density). All 10 dogfood fixtures shipped with calibrated bands. Complements `silence_ratio`: silence_ratio measures *how much* the mentor talks; question_density measures *what shape* the talk takes. Per [`docs/plans/question-density-metric.md`](docs/plans/question-density-metric.md).

### Changed
- Calibration anchors spec promoted from draft to accepted ([`docs/specs/calibration-anchors.md`](docs/specs/calibration-anchors.md)). The contract — two-phase seeding, trust hierarchy (learner materials > web > training data), per-topic success criteria, hints-pipeline integration via the existing `anchor_type` enum — is now stable; first implementation work will file its own plan. The `anchor_type` schema seam shipped in v0.1.0a19 is unchanged.

## [0.1.0a20] — 2026-04-25

### Added
- Release audit log is now CI-enforced. `ci/check_release_audit.py` runs in `release.yml`'s `build-and-check` job (after `check_package_contents.py`) and fails the build when `docs/operations/releases/<tag>.md` is missing, has malformed frontmatter, omits a required field, reports a non-zero `exit_code`, or carries an unrecognised `tool` value. Closes the gap that survived ADR-0020's self-bypass: the workstation-only Tier-2 gate now leaves a machine-checked artifact before publish. Per [ADR-0024](docs/decisions/0024-release-audit-log-required.md).

### Changed
- `sensei verify` now rejects partial nested overrides in `learner/config.yaml` that drop required tunables (e.g. `memory: {}`, `cross_goal: {}`). Previously these silently fell through to hardcoded script defaults — exactly the silent-misconfiguration mode the v0.1.0a19 schema-validation feature was meant to prevent. Per [ADR-0023](docs/decisions/0023-defaults-schema-required-keys.md).
- Runtime config validation is now hard-fail by default. `load_config()` raises `ConfigValidationError` instead of printing a `WARN:` line and continuing, so a bad `learner/config.yaml` cannot silently slip past a learner who does not run `sensei verify`. Set `SENSEI_CONFIG_SOFT_FAIL=1` to downgrade to the previous behaviour for engine-repair / dev / CI-smoke flows. Per [ADR-0025](docs/decisions/0025-runtime-config-hard-fail.md).

## [0.1.0a19] — 2026-04-25

### Added
- Target depth: goals now capture how deep the learner needs to go (`exposure`, `functional`, or `deep`). Inferred from the goal statement, shapes curriculum granularity. (spec: `docs/specs/target-depth.md`)
- Calibration anchors draft spec: defines how the mentor researches real-world standards to calibrate assessment — two-phase seeding (training data → inbox materials/web research), trust hierarchy (learner materials > web > training data), per-topic success criteria, and integration with the hints pipeline. Schema seam: `anchor_type` field added to hints registry. (spec: `docs/specs/calibration-anchors.md`)
- `defaults.yaml` is now JSON-Schema validated. `sensei verify` rejects typos, wrong types, and out-of-range tunables in the merged config (engine defaults + learner overrides); previously these silently fell through to hardcoded script defaults. The deep-merge loader (`config.py`) soft-warns to stderr at runtime so a single bad tunable cannot brick the engine; `sensei verify` is the strict gate. (plan: `docs/plans/defaults-schema.md`)
- Silence-is-teaching is now a measured invariant. New `scripts/silence_ratio.py` computes mentor word-share from any dogfood transcript; transcript fixtures support an optional `silence_ratio: {min, max}` band that fails CI if the mentor talks too much (or too little, for non-silent modes). Bands calibrated against shipped real-LLM captures. (plan: `docs/plans/silence-ratio-and-missing-dogfood.md`)
- Dogfood transcripts captured for `tutor`, `goal`, `challenger`, `reviewer`, `status` — all five had been skipped at CI time pending real-LLM coverage. Tier-1 lexical fixtures (forbidden phrases + required-one-of regex + silence-ratio bands) authored against the captures.
- Shim format validation: every generated tool shim (Claude Code, Kiro, Cursor, Copilot, Windsurf, Cline, Roo, AI Assistant) is now CI-asserted at scaffold time — Cursor's `.mdc` frontmatter, Windsurf's `trigger:`, Claude Code's `@AGENTS.md` import directive, and the plain-prose paths for the rest. Snapshot test pins `_SHIMS` so silent edits are caught. The new [`docs/operations/shim-validation.md`](docs/operations/shim-validation.md) provides a per-tool manual end-to-end runbook. README distinguishes "shim format validated" from "behavior verified". (plan: `docs/plans/shim-validation.md`)

### Changed
- Mastery calibration: the tutor now requires depth-aware multi-probe evidence before skipping a topic (1 probe for exposure, 2 for functional, 3 for deep). Mastery promotion is capped at one level per interaction — a single correct answer cannot jump from `none` to `solid`. `mastery_check.py` now supports `--min-attempts` and `--min-ratio` flags; the tutor gate requires 3+ attempts at 90%+ accuracy.

### Fixed
- `sensei verify` now checks the full engine bundle via a shipped `manifest.yaml`. Previous releases checked only a subset of protocols/scripts/schemas via a hardcoded list; a maintainer-deleted `hints.md`, top-level `tutor.md`, `challenger.md`, `reviewer.md`, `status.md`, `performance-training.md`, several helper scripts (e.g. `review_scheduler.py`, `goal_priority.py`), or `goal.schema.json` / `hints.yaml.schema.json` could pass verify silently. CI now also asserts the inverse: every shipped engine file must be registered in the manifest. (plan: `docs/plans/verify-bundle-completeness.md`)

## [0.1.0a18] — 2026-04-24

### Added
- Decompose trigger: protocol prose in tutor.md and assess.md that tells the mentor when to decompose a coarse curriculum node into finer-grained subtopics (spec: `docs/specs/expand-trigger.md`)
- E2E tests for all three mutation triggers (skip, insert, decompose) — previously none had E2E coverage

### Changed
- Renamed curriculum mutation operations for clarity: `collapse` → `skip`, `spawn` → `insert`, `expand` → `decompose`. The initial node state `spawned` is now split into `pending` (original curriculum node) and `inserted` (dynamically created gap-fill). Field `spawned_from` → `inserted_from`.
- Goal schema bumped from v0 to v1. `sensei upgrade` migrates existing goal files automatically.
- Config knob `max_expand_children` → `max_decompose_children`

## [0.1.0a17] — 2026-04-23

### Added

- **Dogfood capture harness** — `tests/e2e/capture_dogfood.py` scaffolds a Sensei instance, runs multi-turn LLM conversations, and writes `.dogfood.md` transcripts. Supports all 5 protocols (`--protocol hints|assess|review|performance_training|cross_goal_review|all`). Uses an answerer LLM in a clean directory for reliable correct answers.
- **Real LLM transcript captures** — all 5 dogfood transcripts (hints, assess, review, performance_training, cross_goal_review) replaced with real Kiro CLI captures. 19 transcript fixtures now have dogfood companions (was 12).
- **Tier-2 E2E tests** — challenger protocol, reviewer protocol, goal lifecycle (pause/resume with stale detection), multi-turn mode transition (3-turn stipulated session).
- **Tier-3 nightly E2E CI workflow** — runs full E2E suite on a schedule.

### Changed

- **Assessment protocol** — strengthened silence profile enforcement with inline violation examples, code-block templates for exact phrasing ("Got it. One more.", "Two misses on [topic]."), explicit forbidden-word list at classification step.
- **Challenger and reviewer protocols** — constrained profile writes to prevent unvalidated mutations.

### Fixed

- **Assess fixture patterns** — relaxed overly strict `^Got it\.$` anchored regexes to `Got it\.` substring matches. The protocol says "Got it. One more." as one phrase; the fixture shouldn't penalise the LLM for following the protocol correctly.

## [0.1.0a16] — 2026-04-22

### Added

- **Emotional state tracking** — learner profile now tracks emotional state (engagement, frustration, agency) as structured fields. Assessment and review protocols are affect-aware. Degradation chain (confusion → frustration → boredom → disengagement) monitored with configurable intervention thresholds.
- **Cross-goal concept tags** — curriculum nodes carry abstract concept tags assigned at generation time. Review scheduling deduplicates by concept overlap across goals, not just identical slugs. Mastery evidence transfers bidirectionally between goals sharing concepts (evidence, not proof).
- **Interleaving** — review sessions alternate topics between areas for discriminative contrast. Configurable intensity (0=blocked, 1=fully interleaved). Topics below minimum mastery threshold receive blocked practice. Within-goal and cross-goal interleaving both supported.
- **Metacognitive state tracking** — learner profile tracks calibration accuracy, planning tendency, and help-seeking pattern. Protocols adapt coaching intensity with fading scaffolding as metacognitive skills develop.

### Changed

- **Provenance traceability** — bibliography references added to principle Source sections, HTML provenance comments added to all protocol files, traceability matrix created at `docs/foundations/traceability.md`. README claim updated from "drawn from" to "informed by."

## [0.1.0a15] — 2026-04-22

### Added

- Performance training V2 — stages 5 (simulated evaluation) and 6 (full mock) complete the six-stage Performance Preparation Stack. Assessor overlay fully implemented with evaluation realism, rubric framing, and mock orchestration. Reviewer debrief after full mocks.
- Session notes — structured cross-session mentor memory. The mentor records observations (misconceptions, breakthroughs, effective strategies, emotional shifts) incrementally during sessions, with a prose summary and next-session seeds at session close. Stored in `learner/session-notes.yaml`, schema-validated, bounded at 50 entries. Engine loads the last 3 notes at session start for continuity.
- New schema: `session-notes.schema.json` with 4 observation types.
- `sensei init` creates `learner/session-notes.yaml`; `sensei verify` validates it.

## [0.1.0a14] — 2026-04-22

### Added

- `.sensei/run` shell wrapper for reliable script interpreter resolution. LLM agents now invoke `.sensei/run <script>.py` instead of bare `python3 .sensei/scripts/<script>.py`. The wrapper uses the Python that has `sensei-tutor` installed; falls back to `python3` if stale. (ADR-0022)
- Inline `ImportError` guards in all 12 engine scripts — actionable error messages instead of raw tracebacks when dependencies are missing.

### Changed

- All 42 script invocations across 9 engine files updated from `python .sensei/scripts/` to `.sensei/run`.
- `sensei init` now records `sys.executable` in `.sensei/.python_path` and installs the run wrapper.
- `sensei upgrade` refreshes `.sensei/.python_path` and the run wrapper.

## [0.1.0a13] — 2026-04-22

### Fixed

- `sensei upgrade` now triggers `instance/` → `learner/` rename for users upgrading from pre-v0.1.0a11 versions. Previously the migration guard only checked for `learner/` existence, so the rename was never invoked.

## [0.1.0a12] — 2026-04-22

### Added

- Markdown link validator (`ci/check_links.py`) — CI hard-fail on broken internal doc links. Five broken links repaired on introduction.
- Retroactive plan for assessment-protocol with design-doc skip declaration.

### Changed

- `development-process.md`: tightened plan-before-build from pointer to hard gate; tightened spec-before-design and verification-alongside-implementation rules.

### Fixed

- Hardened state-mutation paths: atomic writes, YAML error handling, and edge cases across `mutate_graph.py`, `migrate.py`, `frontier.py`, and other scripts.
- Medium-severity code review findings: improved error messages, input validation, and defensive checks across engine scripts.
- Low-severity hygiene: consistent `from __future__ import annotations`, minor cleanups.

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
- `mutate_graph.mutate` refactored into per-op helpers (`_do_activate`, `_do_complete`, `_do_skip`, `_do_insert`, `_do_decompose`) for readability. Public behaviour (exit codes, JSON output, error messages) is byte-identical.
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
- Goal protocol: "pending" is the correct state for not-yet-started topics.
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

- Curriculum graph implementation: `scripts/frontier.py` (frontier computation with hints-based priority boosting) and `scripts/mutate_graph.py` (5 validated graph operations — activate, complete, skip, insert, decompose — with cycle detection). Curriculum tunables in `defaults.yaml`.
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

[Unreleased]: https://github.com/altakleos/sensei/compare/v0.1.0a21...HEAD
[0.1.0a21]: https://github.com/altakleos/sensei/compare/v0.1.0a20...v0.1.0a21
[0.1.0a20]: https://github.com/altakleos/sensei/compare/v0.1.0a19...v0.1.0a20
[0.1.0a19]: https://github.com/altakleos/sensei/compare/v0.1.0a18...v0.1.0a19
[0.1.0a18]: https://github.com/altakleos/sensei/compare/v0.1.0a17...v0.1.0a18
[0.1.0a17]: https://github.com/altakleos/sensei/compare/v0.1.0a16...v0.1.0a17
[0.1.0a16]: https://github.com/altakleos/sensei/compare/v0.1.0a15...v0.1.0a16
[0.1.0a15]: https://github.com/altakleos/sensei/compare/v0.1.0a14...v0.1.0a15
[0.1.0a14]: https://github.com/altakleos/sensei/compare/v0.1.0a13...v0.1.0a14
[0.1.0a13]: https://github.com/altakleos/sensei/compare/v0.1.0a12...v0.1.0a13
[0.1.0a12]: https://github.com/altakleos/sensei/compare/v0.1.0a11...v0.1.0a12
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
