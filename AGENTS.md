# AGENTS.md — Sensei Source Repository

You are operating the Sensei source repository. This is the upstream project, not a user's learning instance. For the instance-side boot document (what `sensei init` writes), see [`src/sensei/cli.py`](src/sensei/cli.py) → `_AGENTS_MD`.

## What Sensei Is

A pip-installable CLI that scaffolds a learning-environment folder. The user opens that folder with any LLM agent and the agent becomes an adaptive mentor guided by prose-as-code context files and a living learner profile. See [`PRODUCT-IDEATION.md`](PRODUCT-IDEATION.md) for the full product vision.

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
├── PRODUCT-IDEATION.md       (product vision — pre-decomposition monolith)
├── RESEARCH-BIBLIOGRAPHY.md  (58 curated sources)
├── README.md                 (project readme)
├── pyproject.toml            (pip package metadata)
├── docs/
│   ├── development-process.md  (project-agnostic SDD reference)
│   ├── sensei-implementation.md
│   ├── specs/                  (product intent)
│   ├── design/                 (technical architecture)
│   ├── decisions/              (ADRs 0001–0005 so far)
│   ├── plans/                  (task breakdowns)
│   ├── operations/             (runbooks — empty for now)
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
- `PRODUCT-IDEATION.md` and `RESEARCH-BIBLIOGRAPHY.md` are the pre-decomposition record. Do not edit them casually — they will be broken into specs and design docs in a dedicated pass.

## References

- [`docs/development-process.md`](docs/development-process.md) — the SDD method
- [`docs/sensei-implementation.md`](docs/sensei-implementation.md) — Sensei's instantiation
- [`docs/decisions/README.md`](docs/decisions/README.md) — ADR index
- [`PRODUCT-IDEATION.md`](PRODUCT-IDEATION.md) — product vision
