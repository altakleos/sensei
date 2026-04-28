---
feature: fix-gaps-2-6
serves: gap analysis audit 2026-04-28
status: done
date: 2026-04-28
---
# Plan: Fix Gap Analysis Issues #2–6

## Context

A comprehensive audit on 2026-04-28 identified 25 issues. This plan addresses
issues #2–6 (the P0/P1 non-code-change items):

- **#2** `hints.yaml.schema.json` exists but is never validated at runtime
- **#3** `session-notes.schema.json` exists but is never validated at runtime
- **#4** CHANGELOG `[Unreleased]` section is misplaced (below `[0.2.0a3]`)
- **#5** Plans README index is missing 16 plan entries
- **#6** 5 CI scripts have no corresponding tests

## Tasks

### Issue #4 — CHANGELOG fix (trivial)

- [x] T1: Move `## [Unreleased]` from line 47 to line 7 (above `## [0.2.0a3]`) → `CHANGELOG.md`

### Issue #5 — Plans README index (trivial, mechanical)

- [x] T2: Add 16 missing plan rows to the Shipped table in `docs/plans/README.md`

### Issue #2 — Hints schema validation

- [x] T3: Create `src/sensei/engine/scripts/check_hints.py` following the `check_profile.py` / `check_goal.py` pattern: argparse CLI, JSON Schema via `Draft202012Validator`, JSON stdout, exit 0/1 → `src/sensei/engine/scripts/check_hints.py`
- [x] T4: Add `check_hints` to `run.sh` allowlist → `src/sensei/engine/run.sh`
- [x] T5: Add `check_hints.py` to `manifest.yaml` with SHA-256 checksum → `src/sensei/engine/manifest.yaml`
- [x] T6: Create `tests/scripts/test_check_hints.py` with valid, invalid, and edge-case fixtures → `tests/scripts/test_check_hints.py`

### Issue #3 — Session-notes schema validation

- [x] T7: Create `src/sensei/engine/scripts/check_session_notes.py` following the same pattern → `src/sensei/engine/scripts/check_session_notes.py`
- [x] T8: Add `check_session_notes` to `run.sh` allowlist → `src/sensei/engine/run.sh`
- [x] T9: Add `check_session_notes.py` to `manifest.yaml` with SHA-256 checksum → `src/sensei/engine/manifest.yaml`
- [x] T10: Create `tests/scripts/test_check_session_notes.py` → `tests/scripts/test_check_session_notes.py`

### Issue #6 — CI script tests

- [x] T11: Create `tests/ci/test_check_deps.py` — test unpinned detection, duplicate detection, clean project → `tests/ci/test_check_deps.py`
- [x] T12: Create `tests/ci/test_check_security_patterns.py` — test each anti-pattern category, clean project → `tests/ci/test_check_security_patterns.py`
- [x] T13: Create `tests/ci/test_check_test_quality.py` — test trivial body detection, clean tests → `tests/ci/test_check_test_quality.py`
- [x] T14: Create `tests/ci/test_release_preflight.py` — test version mismatch, tag format, passing preflight → `tests/ci/test_release_preflight.py`
- [x] T15: Create `tests/ci/test_generate_manifest.py` — test manifest generation, checksum correctness → `tests/ci/test_generate_manifest.py`

## Acceptance Criteria

- [x] AC1: `python -m sensei.engine.scripts.check_hints --help` works; validates a valid hints.yaml exits 0; rejects invalid hints.yaml exits 1
- [x] AC2: `python -m sensei.engine.scripts.check_session_notes --help` works; validates a valid session-notes.yaml exits 0; rejects invalid exits 1
- [x] AC3: CHANGELOG `[Unreleased]` is the first version section (above `[0.2.0a3]`)
- [x] AC4: `docs/plans/README.md` lists all 90 plan files on disk
- [x] AC5: All 5 new CI test files pass (`pytest tests/ci/test_check_deps.py tests/ci/test_check_security_patterns.py tests/ci/test_check_test_quality.py tests/ci/test_release_preflight.py tests/ci/test_generate_manifest.py`)
- [x] AC6: `make gate` passes (lint, typecheck, tests, validators)
- [x] AC7: Both new validator scripts are in `run.sh` allowlist and `manifest.yaml`

## Documentation Impact

None — these are internal quality fixes. No user-facing behavior changes.
