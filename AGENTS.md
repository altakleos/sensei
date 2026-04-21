# AGENTS.md — Sensei Source Repository

You are operating the Sensei source repository. This is the upstream project, not a user's learning instance. For the instance-side boot document (what `sensei init` writes), see [`src/sensei/cli.py`](src/sensei/cli.py) → `_AGENTS_MD`.

## What Sensei Is

A pip-installable CLI that scaffolds a learning-environment folder. The user opens that folder with any LLM agent and the agent becomes an adaptive mentor guided by prose-as-code context files and a living learner profile. See [`docs/foundations/vision.md`](docs/foundations/vision.md) for the product vision.

## Contributor Boot Chain

1. Read [`docs/development-process.md`](docs/development-process.md) — the SDD method.
2. Read [`docs/sensei-implementation.md`](docs/sensei-implementation.md) — how this project instantiates Implementation and Verification.
3. Read [`docs/decisions/README.md`](docs/decisions/README.md) — what has already been decided.
4. Before making non-trivial changes, follow the flow in § "How Work Flows Through the Layers": spec → design → ADR → plan → implementation → verification.

## Project Layout

```
sensei/
├── AGENTS.md                 (this file — contributor entry point)
├── CLAUDE.md                 (Claude Code shim pointing at AGENTS.md)
├── docs/research/bibliography.md  (58 curated sources)
├── README.md                 (project readme)
├── pyproject.toml            (pip package metadata)
├── docs/
│   ├── development-process.md  (project-agnostic SDD reference)
│   ├── sensei-implementation.md
│   ├── specs/                  (product intent)
│   ├── design/                 (technical architecture)
│   ├── decisions/              (ADRs 0001–0005 so far)
│   ├── plans/                  (task breakdowns)
│   ├── operations/             (operational runbooks: release, worktrees, context budget)
│   └── research/               (promoted librarian reports)
├── src/sensei/
│   ├── __init__.py
│   ├── cli.py                  (click CLI: init/status/upgrade/verify)
│   └── engine/                 (the runtime bundle copied by `sensei init`)
│       ├── engine.md           (kernel + dispatch table — stub)
│       ├── defaults.yaml       (tunables — empty)
│       ├── protocols/          (prose-as-code — empty)
│       ├── scripts/config.py   (deep-merge config loader)
│       ├── prompts/
│       ├── schemas/
│       └── profiles/
└── tests/
    └── test_init.py            (smoke test for `sensei init`)
```

## Key Constraints

- `docs/development-process.md` is **project-agnostic**. Do not mention pedagogy, learner, mentor, tutor, curriculum, or Sensei the product in it. Sensei-specific material lives in `docs/sensei-implementation.md`.
- ADRs are immutable once accepted. To reverse one, write a superseding ADR.
- The product vision has been fully decomposed into docs/foundations/ (principles, personas, vision) and docs/specs/ (protocols, features). `docs/research/bibliography.md` is the curated research catalog.

## Contribution Conventions

- **Commit messages** — prefer [Conventional Commits](https://www.conventionalcommits.org/) prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`). Convention only, no CI gate.
- **Changelog** — append every user-visible change to `## [Unreleased]` in `CHANGELOG.md` in the same commit that introduces it. Don't batch at release time. Per [docs/specs/release-communication.md](docs/specs/release-communication.md). Refactors, internal tests, and docs-only edits don't need a changelog entry.
- **Version references** — always write pre-release versions in full (`v0.1.0a9` or `0.1.0a9`), never the bare suffix (`a9`). A bare suffix is a PEP 440 pre-release marker that attaches to any `X.Y.Z`, so "post-a9" or "a9 cut" is ambiguous across future releases (e.g. `v7.8.9a9` is also "a9"). Applies to prose, filenames, code comments, commit messages, and CHANGELOG entries. Inside a compound like `v0.1.0a9` the suffix is fine — the leading `v0.1.0` disambiguates.

## References

- [`docs/development-process.md`](docs/development-process.md) — the SDD method
- [`docs/sensei-implementation.md`](docs/sensei-implementation.md) — Sensei's instantiation
- [`docs/decisions/README.md`](docs/decisions/README.md) — ADR index
- [`docs/foundations/vision.md`](docs/foundations/vision.md) — product vision
- [`docs/operations/README.md`](docs/operations/README.md) — operational runbooks (release, worktrees, context budget)
