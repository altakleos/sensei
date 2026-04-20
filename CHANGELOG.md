# Changelog

All notable user-visible changes to Sensei (distributed as `sensei-tutor` on PyPI) are recorded in this file.

The format is based on [Keep a Changelog 1.1](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Policy lives in [`docs/specs/release-communication.md`](docs/specs/release-communication.md).

## [Unreleased]

### Added

- Release-communication spec (`docs/specs/release-communication.md`) and this `CHANGELOG.md`. Every future release must ship with a dated entry here; `ci/check_package_contents.py` enforces the presence of an entry for the tag being released.
- Behavioural verification layer (`tests/transcripts/`) with a pytest loader for transcript fixtures and the first fixture file (`review.md`). Per [ADR-0011](docs/decisions/0011-transcript-fixtures.md).
- `docs/foundations/` — new cross-cutting-concerns layer per [ADR-0012](docs/decisions/0012-foundations-layer.md). Contains `vision.md`, 14 principles (6 technical migrated from `sensei-implementation.md` + 7 pedagogical pillars + one mentor-relationship principle), and the Jacundu persona. Specs gain optional `serves:` / `realizes:` / `stressed_by:` frontmatter; `ci/check_foundations.py` is a hard-fail CI gate that catches broken references.
- `docs/development-process.md` gains a project-agnostic "Foundations" section describing the layer as source material above the six-layer stack.
- Full decomposition of `PRODUCT-IDEATION.md` into SDD artifacts (Plans 1–5): 7 new foundation principles, 6 new feature specs, 3 new design docs, 3 new ADRs (0013–0015), and 4 research synthesis docs. The original ideation document is deleted (preserved in git history).
- `docs/research/` reorganized into a 3-tier structure: `bibliography.md` (58 annotated citations), `reports/` (deep investigative reports), `synthesis/` (curated findings with `[Bibliography #N]` provenance citations).

### Notes

- No user-visible CLI or runtime behaviour changes in this Unreleased cycle yet; the above are documentation-layer expansions and verification infrastructure. Users installing `pip install sensei-tutor` see no functional difference.

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
