---
feature: dogfood-verification
serves: (no new spec — implements design/transcript-fixtures.md against existing protocol specs)
design: docs/design/transcript-fixtures.md
status: planned
date: 2026-04-20
---
# Plan: Dogfood Verification MVP

Lands the Tier-1 layer of the transcript-fixtures design: one fixtures file covering `review.md`'s invariants, the pytest loader, and one committed dogfood transcript. Tier-2 (LLM-as-judge) is explicitly deferred to a follow-up plan.

## Tasks

### Phase 1 — Loader

- [ ] T1: Create `tests/transcripts/__init__.py` (empty) → `tests/transcripts/__init__.py`
- [ ] T2: Create `tests/transcripts/conftest.py` — pytest collection hook that:
  - Discovers every `tests/transcripts/*.md` file that is NOT a `*.dogfood.md` companion.
  - For each fixture file, parses YAML frontmatter + `## Fixture: <name>` sections.
  - Pairs each fixtures file with its companion `<basename>.dogfood.md` (if present).
  - For each `## Fixture:` section, emits one parametrised pytest case.
  - When the companion dogfood is missing, `pytest.skip`s with a loud reason rather than failing.
  - Mentor-turn extraction: lines prefixed with `[MENTOR]` in the dogfood transcript are the mentor's output; other lines are ignored.
  - Assertions per fixture (as declared in frontmatter):
    - `forbidden_phrases`: string list; none may appear in any mentor turn (case-sensitive substring match).
    - `required_one_of`: optional regex list; if present, at least one regex must match at least one mentor turn.
    - `required_all_of`: optional regex list; every regex must match somewhere in the mentor turns.
  → `tests/transcripts/conftest.py`

### Phase 2 — First fixtures file

- [ ] T3: Create `tests/transcripts/review.md` covering the four drift modes named in ADR-0011's grounding:
  - **silence-profile** — forbidden: `Great`, `Nice work`, `Well done`, `You're doing well`, `Actually,`, `The correct answer`, `Let me explain`; required-one-of: `^Got it\.$`, `^Okay\.$`, `^Recorded\.$`, `^Next\.$`.
  - **no-reteach** — forbidden: `Let me explain`, `The correct answer is`, `Here's why`, `Actually,`; required-all-of: `I won't explain during review` (if the fixture session is one that should have hit the refusal branch — optional depending on the dogfood scenario).
  - **retrieval-only-question** — no multiple-choice markers (`\(a\)`, `\(b\)`, `^- \[[ xX]\]`), no priming markers (`Last time`, `Recall`, `Remember when`).
  - **sign-off** — required-all-of: `That's it for now\.`
  - Frontmatter links to `docs/specs/review-protocol.md` and the full invariant list.
  → `tests/transcripts/review.md`

### Phase 3 — Captured dogfood transcript

- [ ] T4: Capture one real LLM session driving the review protocol against a synthesised profile with two stale topics. Save verbatim to `tests/transcripts/review.dogfood.md` with `[LEARNER]` / `[MENTOR]` turn prefixes and frontmatter recording agent, model, and capture date. This is a one-time manual step the author does at implementation time; re-capture at each release per the design's cadence. → `tests/transcripts/review.dogfood.md`
- [ ] T5: Confirm the captured transcript passes every fixture — if it fails, either the LLM drifted (fix the protocol prose) or the fixture is over-strict (loosen). Iterate.

### Phase 4 — Verify

- [ ] T6: `pytest tests/transcripts/ -v` shows at least four parametrised cases passing against the committed dogfood transcript.
- [ ] T7: Delete `tests/transcripts/review.dogfood.md` locally and re-run pytest — all transcript cases should `SKIPPED` (not fail). Restore the transcript.
- [ ] T8: Full suite still green (92 → 96+).

### Phase 5 — Documentation wrap

- [ ] T9: Add a short README at `tests/transcripts/README.md` explaining how to author a fixtures file and how to capture a dogfood transcript. 15–30 lines. Points at design doc and ADR-0011 for the full story. → `tests/transcripts/README.md`

## Acceptance Criteria

- [ ] AC1: `tests/transcripts/conftest.py` implements the collection hook and the three assertion categories described in T2.
- [ ] AC2: Missing `.dogfood.md` → `pytest.skip`, never a failing case.
- [ ] AC3: `tests/transcripts/review.md` has at least four `## Fixture:` sections covering silence-profile, no-reteach, retrieval-only-question, and sign-off.
- [ ] AC4: A real dogfood transcript exists at `tests/transcripts/review.dogfood.md` and passes every fixture.
- [ ] AC5: Suite count grows by at least 4 (one parametrised case per fixture).
- [ ] AC6: Removing the dogfood transcript results in `SKIPPED`, not `FAILED`.
- [ ] AC7: `docs/sensei-implementation.md` Verification table references these artifacts (already done in the design commit).

## Out of Scope

- Tier-2 LLM-as-judge. Needs its own plan when operator-local tooling is worth building.
- Fixtures for other protocols (none exist yet). Each future engine protocol earns its own fixtures file in the same commit that lands the protocol.
- Scheduled CI runs of Tier-2. Deferred per design.
- `.flaky-log.md` machinery. Not needed until Tier-2 lands.
- Adding `tests/transcripts/` artifacts to the sdist include list or the wheel. They are test-only; they belong outside the distribution bundle per ADR-0009 (maintainer tooling outside engine).

## Notes

**T4 is an unusual task** — capturing a real LLM session is manual, requires an agent session, and is not reproducible from pytest alone. That is intentional and captured in the design. The plan records it as a task because a human (the maintainer) is the only executor who can complete it; tracking it here keeps the artifact honest about how it was produced.

**Why no spec?** Per ADR-0011, transcript fixtures implement existing spec invariants rather than declaring new product guarantees. The "what Sensei promises" for protocol behaviour lives in each protocol's spec (e.g., `docs/specs/review-protocol.md`); transcript fixtures verify those promises.
