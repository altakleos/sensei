---
feature: adopt-sdd-from-sprue
serves: (meta — this adoption predates any spec)
design: (meta)
status: done
date: 2026-04-20
---
# Plan: Adopt Sprue's SDD Architecture for Sensei

> **Retroactive reconstruction.** This plan was not committed before its implementation (commit `e512082`). It is reconstructed after the fact to preserve the historical record and to honour `docs/development-process.md`. All tasks are marked done.

## Tasks

### Phase A — Docs scaffold

- [x] A1: Create `docs/development-process.md` — project-agnostic SDD reference derived from sprue → `docs/development-process.md`
- [x] A2: Create `docs/sensei-implementation.md` — stub instantiation doc → `docs/sensei-implementation.md`
- [x] A3–A6: README.md for `docs/{specs,design,decisions,plans}/` → each directory
- [x] A7: Create `docs/operations/` with `.gitkeep` → `docs/operations/.gitkeep`

### Phase B — Foundational ADRs

- [x] B1: ADR-0001 SDD adoption → `docs/decisions/0001-spec-driven-development-process.md`
- [x] B2: ADR-0002 Agent bootstrap → `docs/decisions/0002-agent-bootstrap.md`
- [x] B3: ADR-0003 Tool-specific agent hooks → `docs/decisions/0003-tool-specific-agent-hooks.md` (depends: B2)
- [x] B4: ADR-0004 Distribution model → `docs/decisions/0004-sensei-distribution-model.md` (depends: B2)
- [x] B5: ADR-0005 ADR-lite format → `docs/decisions/0005-adr-lite-format.md`

### Phase C — Engine bundle scaffold

- [x] C1: `src/sensei/__init__.py` with `__version__`
- [x] C2: `src/sensei/engine/engine.md` kernel stub (depends: B2)
- [x] C3: `src/sensei/engine/defaults.yaml` with empty sections
- [x] C4: Placeholder READMEs for `protocols/`, `prompts/`, `schemas/`, `profiles/`
- [x] C5: `src/sensei/engine/scripts/{__init__.py,config.py}` deep-merge loader

### Phase D — pip CLI skeleton

- [x] D1: `pyproject.toml` with hatchling, click, pyyaml, entry point
- [x] D2: `src/sensei/cli.py` with click app (init/status/upgrade/verify) (depends: C2, C3, B3, B4)
- [x] D3: `tests/test_init.py` smoke test (depends: D2)

### Phase E — Root-level files

- [x] E1: Project-root `AGENTS.md` (depends: B2, C2)
- [x] E2: `CLAUDE.md` shim (depends: E1)
- [x] E3: `README.md`
- [x] E4: Update `.gitignore` for dist/, build/, egg-info/

## Acceptance Criteria

- [x] AC1: `docs/` tree populated per target layout
- [x] AC2: ADRs 0001–0005 exist with valid frontmatter, cross-linked
- [x] AC3: `pip install -e .` succeeds
- [x] AC4: `sensei init` creates `.sensei/` + 8 tool shims
- [x] AC5: `sensei.__version__` imports as `0.0.0`
- [x] AC6: smoke tests pass (3/3)
- [x] AC7: `PRODUCT-IDEATION.md`, `RESEARCH-BIBLIOGRAPHY.md`, `docs/research/*` untouched
- [x] AC8: Engine bundle is scaffolding-only (no protocol logic)
- [x] AC9: `docs/development-process.md` contains zero Sensei-specific references

## Outcome

Shipped in commit `e512082` (29 files, 1,123 insertions).
