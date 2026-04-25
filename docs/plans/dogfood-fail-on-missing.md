---
feature: dogfood-fail-on-missing
serves: docs/specs/behavioral-modes.md
design: "Pattern instantiation of the existing transcript-fixture verification mechanism (ADR-0011). No new mechanism — converts a soft skip into a hard fail. Out-of-scope follow-up named in docs/plans/silence-ratio-and-missing-dogfood.md § Out of Scope is now in scope."
status: done
date: 2026-04-25
---
# Plan: `tests/transcripts/test_fixtures.py` — Fail on Missing Dogfood

`tests/transcripts/test_fixtures.py:24–29` currently calls `pytest.skip()` when a fixture's `.dogfood.md` companion is missing. This was intentional during the silence-ratio rollout (CHANGELOG v0.1.0a19) when not every protocol had a real-LLM capture yet — skipping kept CI green while the dogfood backfill was in progress. Per `docs/plans/silence-ratio-and-missing-dogfood.md` § Out of Scope:

> Removing `pytest.skip()` for missing dogfood. After this plan, no protocol is missing dogfood — but turning skip-on-missing into fail-on-missing is a follow-up for a separate small PR.

That moment is now. Verified 2026-04-25 against post-merge `main`: zero transcript-fixture skips today; all 14 pytest skips come from workstation-only Tier-2 E2E (`ANTHROPIC_API_KEY`/`SENSEI_E2E` gating). Converting skip → fail is pure footgun-sealing — a future protocol that ships without dogfood will fail loudly rather than silently bypass verification.

## Targets and Verified Evidence

| # | Target | Evidence (verified 2026-04-25) |
|---|---|---|
| 1 | `tests/transcripts/test_fixtures.py:24–29` calls `pytest.skip()` on missing dogfood | Read confirms exact lines; the skip path is dead today (no protocol triggers it). |
| 2 | All 11 protocols have committed dogfood transcripts | `fd "\.dogfood\.md$" tests/transcripts/` returns 11 files. |
| 3 | The deferred follow-up is explicitly scheduled | `docs/plans/silence-ratio-and-missing-dogfood.md:89` names it as out-of-scope-for-that-PR-but-the-next-one. |

## Approach

Two-line change in `test_fixtures.py`: replace `pytest.skip(...)` with `pytest.fail(...)` carrying the same diagnostic message (so a maintainer adding a new protocol fixture without its dogfood gets an actionable error pointing at the cadence doc). No other code touched.

A test for the new behaviour is straightforward: a parametrised case with a fixture that points at a non-existent `.dogfood.md` should now produce a failure, not a skip. But — adding a test that deliberately fails would require carving out a separate test runner and is more surface than the change deserves. The existing 11 dogfood-paired fixtures plus the conftest.py loader's behaviour are sufficient evidence that the change is correct; a follow-up would be the moment a real protocol regression catches it.

## Tasks

- [x] T1 — `tests/transcripts/test_fixtures.py:24–29`: replace the `pytest.skip(...)` call with `pytest.fail(...)`. Keep the message body identical so maintainers see the same diagnostic, just with a different verdict. Update the message preamble from "cannot be evaluated until a session is captured" to "must be captured before this fixture lands" — the contract is now eager, not lazy.
- [x] T2 — `docs/design/transcript-fixtures.md` § Cadence: update if it documents the skip-on-missing contract. Single-paragraph edit max. Skip the task if the section already accommodates fail-on-missing.
- [x] T3 — Run full local pipeline via `.venv/bin/`. All green (zero new skips, zero new failures expected since all protocols have dogfood).
- [x] T4 — Commit on `test/dogfood-fail-on-missing` branch with message `test: fail (not skip) when a transcript fixture lacks dogfood capture`. Open PR.

## Acceptance Criteria

- [x] AC1 — `grep -n "pytest.skip" tests/transcripts/test_fixtures.py` returns no matches.
- [x] AC2 — `grep -n "pytest.fail" tests/transcripts/test_fixtures.py` returns one match in the dogfood-missing branch.
- [x] AC3 — `.venv/bin/pytest tests/transcripts/ -q --no-cov` reports the same number of passes as before this plan, with **zero** transcript-fixture skips.
- [x] AC4 — `.venv/bin/pytest -q --no-cov` reports 14 skipped (workstation-only E2E only — unchanged from the pre-change baseline).
- [x] AC5 — `git diff --stat` shows changes only in `tests/transcripts/test_fixtures.py`, this plan, and (if needed) `docs/design/transcript-fixtures.md`.

## Out of Scope

- Adding a test that exercises the new `pytest.fail()` branch. Carving out a unit test that deliberately fails to validate that a future regression would fail-loudly is out of scope; the runtime change is two lines and the existing fixture inventory exercises the path.
- A CHANGELOG entry. Per AGENTS.md, "Refactors, internal tests, and docs-only edits don't need a changelog entry" — this is a test-only change.
- Adjusting the design doc's "Cadence" section if it already accommodates eager dogfood capture (most likely the case).
