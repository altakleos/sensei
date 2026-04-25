---
feature: engine-bundle-link-gate
serves: docs/specs/release-process.md
design: "No design doc — pure CI extension + four single-line text corrections. Pattern instantiation of the existing ci/check_links.py validator: same code, second invocation against the engine-bundle root. No new mechanism, no schema change, no protocol prose semantics change."
status: done
date: 2026-04-25
---
# Plan: Engine-Bundle Link Gate + 2026-04-25 Audit Drift Fixes

The 2026-04-25 follow-up audit (post-v0.1.0a20) surfaced four documentation surfaces that drift from current state. The most consequential pair sits *inside the wheel* — `src/sensei/engine/engine.md:298` and `src/sensei/engine/protocols/performance-training.md:125` both link `0020-phase-overlay-composition.md`, but the actual ADR is `0021-phase-overlay-composition.md` (ADR-0020 is the now-superseded `release-self-bypass`). Every `sensei init` propagates the broken citation into the learner's `.sensei/`.

The class of bug exists because `ci/check_links.py` defaults to scanning `docs/` only (`_DEFAULT_ROOT = _REPO_ROOT / "docs"` at `ci/check_links.py:45`). The engine bundle ships its own markdown corpus that no link gate touches.

This plan (a) fixes the four drifts and (b) extends the gate so the class of bug fails CI next time.

## Targets

| # | File | Line | Current | Corrected |
|---|---|---|---|---|
| 1 | `src/sensei/engine/engine.md` | 298 | `0020-phase-overlay-composition.md` | `0021-phase-overlay-composition.md` |
| 2 | `src/sensei/engine/protocols/performance-training.md` | 125 | `docs/decisions/0020-phase-overlay-composition.md` | `docs/decisions/0021-phase-overlay-composition.md` |
| 3 | `tests/transcripts/conftest.py` | 8 | "Missing dogfood transcripts produce `pytest.skip`, never a failing case." | One sentence noting that `test_fixtures.py` now `pytest.fail`s instead — matches commit `202b680`. |
| 4 | `docs/operations/README.md` | 7 | "...and the self-bypass caveat on the `pypi` GitHub Environment for solo-maintainer releases." | "...and the manual-approval step required by the `pypi` GitHub Environment per ADR-0026." |

## Approach

Single squashable commit. The CI extension is a one-line addition to `verify.yml` that re-invokes the existing validator with `--root src/sensei/engine`; no Python change. The four text fixes are literal replacements with no semantic logic change.

For target #2, the change is a single character (`0` → `1`) inside a code-fenced reference path; protocol prose semantics are unchanged because the citation points to the same conceptual ADR (phase-overlay composition).

## Tasks

- [x] T1 — Fix the two engine-bundle ADR-link typos (#1, #2). Single character change each (`0020` → `0021`); no surrounding prose changes. Files: `src/sensei/engine/engine.md`, `src/sensei/engine/protocols/performance-training.md`.
- [x] T2 — Update `tests/transcripts/conftest.py:8` docstring to match `test_fixtures.py:24-29`'s actual `pytest.fail` behaviour (#3). One sentence.
- [x] T3 — Update `docs/operations/README.md:7` to drop "self-bypass caveat" phrasing post-ADR-0026 (#4). One sentence.
- [x] T4 — Extend `.github/workflows/verify.yml`'s "Lint markdown links" step (or add a sibling step) to scan the engine bundle as well as `docs/`. New invocation: `python ci/check_links.py --root src/sensei/engine`. The validator already supports `--root` (`ci/check_links.py:111-115`); no Python change required.
- [x] T5 — Run the full local pipeline from the project venv: `.venv/bin/pytest && .venv/bin/ruff check . && .venv/bin/mypy && python ci/check_foundations.py && python ci/check_links.py && python ci/check_links.py --root src/sensei/engine && python ci/check_changelog_links.py && python ci/check_plan_completion.py`. All must stay green; the new engine-bundle invocation must be green AFTER T1+T2 (and would have been red before — that demonstrates the gate is load-bearing).
- [x] T6 — Add row to `docs/plans/README.md` § Shipped index.
- [x] T7 — Commit message: `chore: extend link gate to engine bundle + fix 2026-04-25 audit drifts`. Body cites this plan path and lists the four target files.

## Acceptance Criteria

- [x] AC1 — `grep -rn "0020-phase-overlay" src/sensei/engine/` returns zero matches.
- [x] AC2 — `grep -n "pytest.skip\|never a failing case" tests/transcripts/conftest.py` returns zero matches.
- [x] AC3 — `grep -n "self-bypass" docs/operations/README.md` returns zero matches.
- [x] AC4 — `python ci/check_links.py --root src/sensei/engine` exits 0.
- [x] AC5 — `.github/workflows/verify.yml` invokes `ci/check_links.py` against `src/sensei/engine` (in addition to the existing default-root invocation).
- [x] AC6 — Full local pipeline (T5) passes.
- [x] AC7 — `git diff --stat` touches only: this plan, `docs/plans/README.md`, the four target files in #1–#4, and `.github/workflows/verify.yml`. No change to `ci/check_links.py` itself.

## Out of Scope

- The Tier-2 coverage expansion from 3 to 7 protocols (audit recommendation #1) — separate, larger plan with its own ADR-lite.
- Resolving ADR-0023's `learner.additionalProperties: true` reservation (audit Risk #2) — needs ADR superseding 0023, deliberately deferred until a typed extension forces the choice.
- Promoting `docs/specs/calibration-anchors.md` from `draft` (audit recommendation #6).
- The top-level `inbox/` relocation (audit recommendation #7).
- Backfilling `silence_ratio` bands across all dogfood fixtures (audit Risk #4).
- Any CHANGELOG entry. AGENTS.md: "docs-only edits don't need a changelog entry." The `verify.yml` change is a CI-only addition with no user-visible behaviour change.
