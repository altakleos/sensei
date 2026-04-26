# Contributing to Sensei

This is the Sensei source repository. The product is `sensei-tutor` on PyPI; this repo is where it is built and governed.

## Governance

Sensei follows Spec-Driven Development. Before making any non-trivial change, read [`AGENTS.md`](AGENTS.md) — the contributor boot document. It routes you to the SDD method, the layer stack (specs → design → ADRs → plans → implementation → verification), and the plan-before-build / spec-before-design rules.

Short version: **for any change that touches more than one file, adds a dependency, alters a public surface, or warrants a CHANGELOG entry, write a plan in `docs/plans/<slug>.md` first and wait for approval.** See [`AGENTS.md` § Required: Plan Before Build](AGENTS.md).

## Setup

```bash
git clone https://github.com/altakleos/sensei.git
cd sensei
make setup
make gate
```

`make setup` creates `.venv/` and installs the package editably with dev extras. `make gate` runs the full local pre-merge bundle (lint + typecheck + tests + validators) — the same gates CI runs.

You need Python 3.10 or newer. The PyPI install path (`pip install sensei-tutor`) is for end users, not contributors; contributors install editably from a clone.

## Daily loop

```bash
make test     # run pytest after every change
make lint     # ruff
make gate     # full local bundle before opening a PR
```

If `make test` is too slow, target a single file: `.venv/bin/pytest tests/path/to/test_file.py -v`.

## PR convention

Branches are slash-prefixed by change type: `feat/<slug>`, `fix/<slug>`, `docs/<slug>`, `refactor/<slug>`, `chore/<slug>`. PR titles follow the same prefix. Plans land as the first commit on a feature branch. See [`docs/development-process.md` § Branching and Integration](docs/development-process.md).

## What goes where

| Surface | Lives in | Governed by |
|---|---|---|
| CLI / package source | `src/sensei/` | ADR-0004 |
| Engine bundle (prose protocols, scripts, schemas) | `src/sensei/engine/` | ADR-0006, manifest.yaml |
| Tests | `tests/` (unit, e2e, ci, transcripts) | ADR-0011, pyproject.toml |
| CI gates | `ci/check_*.py` | release-process spec |
| Specs / Design / ADRs / Plans | `docs/` | development-process.md |

For more, read [`AGENTS.md`](AGENTS.md) and follow its boot chain.
