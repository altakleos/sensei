# Contributing to Sensei

Read [`AGENTS.md`](AGENTS.md) — the canonical contributor boot document. It covers the SDD method, plan-before-build rules, and project layout.

## Setup

```bash
git clone https://github.com/altakleos/sensei.git
cd sensei
make setup
make gate
```

`make setup` creates `.venv/` and installs the package editably with dev extras. `make gate` runs the full local pre-merge bundle (lint + typecheck + tests + validators). You need Python 3.10 or newer.

## Daily loop

```bash
make test     # pytest after every change
make lint     # ruff
make gate     # full bundle before opening a PR
```
