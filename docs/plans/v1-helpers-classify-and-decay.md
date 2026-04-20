---
feature: v1-helpers-classify-and-decay
serves: (implements ADR-0006 v1 helper inventory, items 3 and 4)
design: docs/decisions/0006-hybrid-runtime-architecture.md
status: done
date: 2026-04-20
---
# Plan: First Two ADR-0006 V1 Helpers

> **Retroactive reconstruction** for commit `5735e36`.

Ships the two ADR-0006 v1 helpers that require no schema decisions — pure arithmetic/classification. Validates the hybrid-runtime invocation pattern end-to-end before tackling profile-dependent helpers (`check_profile`, `mastery_check`).

## Tasks

- [x] T1: Implement `classify_confidence.py` mapping (confidence, correctness) to the 4-quadrant label from PRODUCT-IDEATION.md §8.5 → `src/sensei/engine/scripts/classify_confidence.py`
- [x] T2: Implement `decay.py` exponential-forgetting freshness arithmetic (freshness = 2^(-elapsed/half_life)) with configurable stale threshold → `src/sensei/engine/scripts/decay.py`
- [x] T3: Unit tests for library + CLI + subprocess paths for both helpers → `tests/scripts/test_classify_confidence.py`, `tests/scripts/test_decay.py`
- [x] T4: `tests/scripts/__init__.py` to make the directory a package

## Acceptance Criteria

- [x] AC1: Each helper emits a single JSON line to stdout on success
- [x] AC2: Each helper is importable as a library AND runnable as a CLI
- [x] AC3: A subprocess-invocation test passes for each (verifies the pattern protocols will use)
- [x] AC4: Input validation raises `ValueError` with a helpful message
- [x] AC5: All tests pass locally and under CI verify.yml matrix

## Outcome

Shipped in commit `5735e36` (5 files, 352 insertions). Suite grew from 3 to 19 passing tests. CI went green on first run.
