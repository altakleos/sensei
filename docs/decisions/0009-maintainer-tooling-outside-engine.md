---
status: accepted
date: 2026-04-20
weight: lite
protocols: [release]
---
# ADR-0009: Maintainer Tooling Lives Outside the Engine Bundle

## Decision

Scripts that are invoked only at release or CI time — never by protocols at runtime in a user instance — live at `ci/` in the repo root. They are NOT part of the engine bundle (`src/sensei/engine/scripts/`) and are therefore NOT copied into `.sensei/` by `sensei init`.

The first such tool is `ci/check_package_contents.py`, the release-time wheel validator introduced by the release-workflow design.

## Why

`sensei init` copies the entire `src/sensei/engine/` tree into every learner instance. Placing maintainer tooling in that tree means every user gets wheel-inspection scripts, release validators, and other CI-only code they cannot run and should not read. Separating maintainer-side tools from runtime helpers keeps the engine bundle purely runtime-relevant and makes the boundary legible without needing per-file documentation ("this one, but not that one").

## Alternative

Place `check_package_contents.py` alongside runtime helpers under `src/sensei/engine/scripts/`. This is the pattern used by the sibling Sprue project. Rejected for Sensei because Sensei's distribution model copies the whole bundle to every user; unlike Sprue, there is no legitimate reason for a learner's instance to ship with release infrastructure.
