---
status: done
design: "Follows ADR-0006"
---

# Plan: Declare kanon-kit as a dev dependency

## Problem

`kanon-kit` is used by `make gate` and CI but is not declared in
`pyproject.toml`. Contributors following CONTRIBUTING.md (`make setup` →
`make gate`) hit a command-not-found error. CI works around this with a
separate `pip install kanon-kit` on the same line.

## Solution

1. Add `kanon-kit==0.2.0a7` to `[project.optional-dependencies] dev`
2. Simplify CI verify.yml line 31 from `pip install -e '.[dev]' kanon-kit`
   to `pip install -e '.[dev]'`

## Files touched

| File | Change |
|------|--------|
| `pyproject.toml` | Add `kanon-kit==0.2.0a7` to dev extras |
| `.github/workflows/verify.yml` | Remove redundant `kanon-kit` from pip install |

## Acceptance criteria

1. `kanon-kit` appears in `pyproject.toml` dev extras with pinned version
2. `uv sync --all-extras` installs kanon-kit
3. `make gate` succeeds (kanon verify . works)
4. CI verify.yml no longer has the separate kanon-kit install
