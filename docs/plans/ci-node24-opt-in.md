---
feature: ci-node24-opt-in
serves: docs/specs/release-process.md
design: "Pure CI hygiene. No design doc needed."
status: planned
date: 2026-04-25
---
# Plan: CI Forward-Compat — Opt Into Node 24 for JavaScript Actions

Every recent CI run carries an annotation on every `actions/setup-python@v5` step:

> Node.js 20 actions are deprecated. … Node.js 20 will be removed from the runner on September 16th, 2026. … To opt into Node.js 24 now, set the `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` environment variable on the runner or in your workflow file.

We have ~5 months of runway. Two paths exist:

1. **Wait for `actions/setup-python@v6`** (Node-24 native). Upstream hasn't released it. We'd notice and bump on release.
2. **Opt in now via env var.** Forces JavaScript actions to run on Node 24 today, surfacing any incompatibility immediately rather than the morning of September 16 when we'd lose CI.

This plan does (2) because the cost is one line per workflow and the upside is real: if any of our actions has a Node-24 incompatibility (e.g. `actions/checkout@v5`, `actions/setup-python@v5`, `actions/upload-artifact@v5`, `actions/download-artifact@v5`, `pypa/gh-action-pypi-publish@release/v1`), we want to know in April with months to react, not on a Wednesday morning when CI suddenly fails.

The change is reversible: if Node 24 breaks something, the env var is removed and we go back to Node 20 until upstream catches up.

## Tasks

- [ ] T1: `.github/workflows/verify.yml` — add a workflow-level `env:` block setting `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: "true"`.
- [ ] T2: `.github/workflows/release.yml` — same env block at workflow level.
- [ ] T3: `.github/workflows/e2e-nightly.yml` — same env block at workflow level.
- [ ] T4: No CHANGELOG entry — internal CI hygiene per AGENTS.md:111 (refactors and internal-test edits don't need entries).

## Acceptance Criteria

- [ ] AC1: All three workflow files declare `env: FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: "true"` at the top level (above `jobs:`).
- [ ] AC2: After merge, the next `verify` run on `main` is green AND the per-job logs no longer carry the Node-20 deprecation annotation (or, if they do, the annotation now reflects the Node-24-forced behavior — the issue is upstream pinning to a node, not us).
- [ ] AC3: No regression in test outcomes (verified by the same PR's CI run).

## Out of Scope

- Bumping individual action versions. All five actions used (`checkout@v5`, `setup-python@v5`, `upload-artifact@v5`, `download-artifact@v5`, `gh-action-pypi-publish@release/v1`) are already at the latest available stable major.
- Migrating away from JavaScript-based actions to Docker-based or composite actions (different node-version risk model). Out of scope.
- Auto-detecting and bumping action versions in CI (Dependabot territory). Already a Dependabot opportunity, separate concern.
- Setting `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true` (the *opposite* of this plan — that's the post-September-16 escape hatch if Node 24 breaks something we can't fix in time).
