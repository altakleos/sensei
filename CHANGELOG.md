# Changelog

All notable user-visible changes to Sensei (distributed as `sensei-tutor` on PyPI) are recorded in this file.

The format is based on [Keep a Changelog 1.1](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Policy lives in [`docs/specs/release-communication.md`](docs/specs/release-communication.md).

## [Unreleased]

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

>>>>>>> plan/cross-goal
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
