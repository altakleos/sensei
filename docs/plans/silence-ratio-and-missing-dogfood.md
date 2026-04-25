---
feature: silence-ratio-and-missing-dogfood
serves: docs/specs/behavioral-modes.md
design: "Pattern instantiation of existing transcript-fixture mechanism (ADR-0011) + new deterministic helper following the scripts-compute-protocols-judge boundary (ADR-0006)."
status: planned
date: 2026-04-25
---
# Plan: Silence-Ratio Helper + Dogfood Capture for the Five Missing Protocols

The project analysis surfaced two related gaps in the prose-as-code semantic-verification surface:

1. **Silence-is-teaching is unmeasured.** `engine.md:213` codifies per-mode silence profiles ("Tutor ~40% silent; Assessor silent while learner works; Challenger silent for productive failure; Reviewer NOT silent") and `docs/foundations/principles/silence-is-teaching.md` raises silence to a load-bearing principle. **No fixture or script measures it.** The closest enforcement is permitted-utterance regex in `tests/transcripts/assess.md` — a forbidden/allowed list, not a quantitative bound.

2. **Five protocols ship without dogfood transcripts.** `tests/transcripts/` has dogfood for `assess`, `review`, `hints`, `performance_training`, `cross_goal_review`. The remaining five — **tutor, goal, challenger, reviewer, status** — have no real-LLM corpus, so their lexical fixtures are skipped at CI time (per `test_fixtures.py:22-26`). `tutor` is the default mode every session opens in; behavioral regressions there are uncaught today.

Bundled because each new dogfood capture in #2 should land already covered by the silence-ratio assertion from #1 — single review surface, two atomic commits.

## Approach

**Commit 1 — silence_ratio helper + bands on existing fixtures.**
- New deterministic script `src/sensei/engine/scripts/silence_ratio.py`. Inputs: a dogfood transcript path. Outputs: JSON `{mentor_words, learner_words, mentor_word_share, mentor_turns, learner_turns}`. Word count uses `re.findall(r"\w+", text)` so punctuation and whitespace don't skew.
- Extend `tests/transcripts/test_fixtures.py` to honour an optional `silence_ratio: {min: <float>, max: <float>}` field per fixture entry. Computed from the dogfood transcript via `silence_ratio.py`'s exported `compute_word_share(text) -> float`. Hard assertion: fail if the mentor word-share falls outside the band.
- Add `silence_ratio:` bands to existing fixtures where the protocol's silence profile is non-trivial:
  - `assess.md` — mentor word-share `<= 0.30` (assessor exception; mostly silent)
  - `review.md` — mentor word-share `<= 0.45` (mentor announces topic + asks; not chatty)
  - `performance_training.md` — context-dependent; widen to `<= 0.55` for the captured drill scenarios
  - `hints.md` — `<= 0.55` (mentor narrates a triage)
  - `cross_goal_review.md` — `<= 0.45`
  Bands are a **starting calibration** based on the actual existing dogfood content. If T3 (initial run) shows real transcripts blow them, I'll widen rather than tighten — the goal is to catch regressions, not pin a number that a future protocol revision can't move.

**Commit 2 — dogfood capture for the five missing protocols.**
- Extend `tests/e2e/capture_dogfood.py`:
  - Add `tutor`, `goal`, `challenger`, `reviewer`, `status` to the `PROTOCOLS` tuple.
  - Add seeding helpers (`_seed_tutor`, `_seed_goal`, etc.) modelled on the existing `_seed_assess` / `_seed_review` patterns.
  - Add per-protocol prompt templates that drive the LLM into the protocol's dispatch path.
- Run `python tests/e2e/capture_dogfood.py --protocol tutor goal challenger reviewer status` to write the five `.dogfood.md` files. Uses the project's existing `agent_runner.py` wrapper around `claude` (already verified working in this environment).
- Author lexical fixtures for the five protocols (`tests/transcripts/{tutor,goal,challenger,reviewer,status}.md`):
  - Forbidden-phrase lists drawn from `personality.md` (e.g. "Great question!", "Nice work!", praise tokens).
  - `required_one_of` patterns specific to each protocol (e.g. for `goal`, an ask about target depth or three unknowns).
  - `silence_ratio:` bands per the engine.md profile:
    - tutor: `0.30–0.70` (mid; mentor teaches but with ~40% silence target)
    - assessor mode is covered by `assess.md` — `goal` protocol is conversational, so `0.30–0.65`
    - challenger: `0.20–0.55` (silent for productive failure)
    - reviewer: `0.30–0.75` (NOT silent; floor enforces presence)
    - status: `0.40–0.80` (status is mentor reporting; higher floor expected)

## Tasks

### Commit 1 — silence_ratio helper + existing-fixture coverage

- [ ] T1: `src/sensei/engine/scripts/silence_ratio.py` — pure-Python helper. CLI entry: `silence_ratio.py --transcript <path>`. Library entry: `compute_word_share(text: str) -> float`, `compute_turn_stats(text: str) -> dict`. Reuses the `[MENTOR]`/`[LEARNER]` line-marker convention already established by `tests/transcripts/conftest.py:extract_mentor_turns`. Exit 0 + JSON to stdout on success; exit 1 + error JSON on missing/empty file.
- [ ] T2: Register `scripts/silence_ratio.py` in `src/sensei/engine/manifest.yaml` under `required:`.
- [ ] T3: `tests/scripts/test_silence_ratio.py` — happy path (synthetic transcript), edge cases (no mentor turns, no learner turns, empty file, frontmatter present), CLI smoke via `main(argv)`. Verify the existing 5 dogfood transcripts produce values that fall inside the bands chosen below — if any blow the band, widen the band, don't tighten the protocol.
- [ ] T4: `tests/transcripts/test_fixtures.py` — extend the per-case assertion to honour a `silence_ratio: {min: ..., max: ...}` fixture field. Skip the silence assertion if the field is absent (backward-compatible; existing fixtures without bands keep working unchanged). Compute via `silence_ratio.compute_word_share(dogfood_text)`.
- [ ] T5: `tests/transcripts/assess.md` — add `silence_ratio: {max: 0.30}` to the per-fixture entries where the silence-is-teaching invariant is load-bearing (assessor exception fixtures). Set as **a wide starting calibration** — the goal is to catch regressions, not to hold any specific number sacred. Run T3's verification step against the actual `assess.dogfood.md`; if the real ratio is outside `[0, 0.30]`, widen to a value 0.05 above the observed.
- [ ] T6: `tests/transcripts/review.md` — add `silence_ratio: {max: 0.45}` per the review protocol's "ask, don't lecture" stance. Same calibration rule as T5.
- [ ] T7: `tests/transcripts/performance_training.md`, `hints.md`, `cross_goal_review.md` — add silence_ratio bands (`max: 0.55`, `max: 0.55`, `max: 0.45` respectively) following the same calibration rule.
- [ ] T8: `docs/development-process.md` — add a one-line pointer in the "Verification" subsection noting that fixture-level silence-ratio assertions exist (single sentence, no rule-text duplication).
- [ ] T9: Run full pipeline (`pytest && ruff check . && mypy && python ci/check_*.py`). Commit as: `feat: silence_ratio helper + per-fixture silence bands`.

### Commit 2 — dogfood capture for tutor/goal/challenger/reviewer/status

- [ ] T10: `tests/e2e/capture_dogfood.py` — add `tutor`, `goal`, `challenger`, `reviewer`, `status` to `PROTOCOLS`. Add `_seed_tutor`, `_seed_goal`, `_seed_challenger`, `_seed_reviewer`, `_seed_status` helpers following the established pattern. Add prompt templates for each — multi-turn for protocols that need multiple exchanges (tutor is multi-turn; status is single-turn).
- [ ] T11: Run `python tests/e2e/capture_dogfood.py --protocol tutor goal challenger reviewer status` from this environment. Inspect the generated `.dogfood.md` files for sanity (no ANSI noise, plausible mentor speech, both turn types present). If any capture is malformed, fix `_extract_mentor_text` regexes and re-run that protocol.
- [ ] T12: Author `tests/transcripts/{tutor,goal,challenger,reviewer,status}.md` with:
  - Frontmatter naming the protocol and one or more `fixtures:` entries.
  - `forbidden_phrases:` from `personality.md` baseline (Great question, Nice work, Excellent, apologetic softeners, emoji codepoints).
  - `required_one_of:` patterns specific to each protocol (e.g. goal asks the three-unknowns; status reports counts).
  - `silence_ratio:` bands per the per-protocol values listed in the Approach section above. **Calibrate after capture**: if the captured transcript blows the band, widen rather than tighten.
- [ ] T13: `CHANGELOG.md` — append under `## [Unreleased]` → `### Added`:
  > Silence-is-teaching is now a measured invariant. New `scripts/silence_ratio.py` computes mentor word-share from any dogfood transcript; transcript fixtures support an optional `silence_ratio: {min, max}` band that fails CI if the mentor talks too much (or too little, for non-silent modes). Dogfood transcripts captured for `tutor`, `goal`, `challenger`, `reviewer`, `status` — all five had been skipped at CI time pending real-LLM coverage. Tier-1 lexical fixtures (forbidden phrases + required-one-of regex) authored against the captures.
- [ ] T14: Run full pipeline. Commit as: `feat: dogfood capture for tutor/goal/challenger/reviewer/status protocols`.

## Acceptance Criteria

- [ ] AC1: `python -m sensei.engine.scripts.silence_ratio --transcript tests/transcripts/assess.dogfood.md` exits 0 and prints a JSON object with the four expected keys.
- [ ] AC2: `pytest tests/scripts/test_silence_ratio.py` — all cases pass (≥6 per T3).
- [ ] AC3: `pytest tests/transcripts/` — every fixture case runs (none skipped). All five new protocol fixtures (T12) load and assert against their dogfood transcripts.
- [ ] AC4: `python ci/check_plan_completion.py && python ci/check_links.py && ruff check . && mypy && pytest` — all green.
- [ ] AC5: Negative-case demonstration (verified locally; not committed): manually edit one dogfood `[MENTOR]` turn to be 5× longer; the silence-ratio fixture for that protocol fails with the offending observed ratio in the error message.
- [ ] AC6: Five new `<protocol>.dogfood.md` files exist under `tests/transcripts/` and contain at least one `[MENTOR]` and one `[LEARNER]` turn each.

## Out of Scope

- An LLM-as-judge tier-2 verifier. The lexical + ratio combo is the cheap-and-honest layer; an LLM judge can come in a separate spec when it's worth the complexity.
- Per-mode silence bands at the engine level (e.g. a `silence_target` field in `defaults.yaml`). Could fold there later, but the per-fixture YAML keeps calibration close to the transcript that proves the band, which is the right scope for v1.
- Updating the existing transcripts to make silence-ratio greener — bands are calibrated *to* what real-LLM captures actually do, not the other way around.
- Capturing dogfood for the four behavioral mode files in `protocols/modes/`. Those are loaded as overlays onto the active protocol; they're already exercised when the parent protocol is captured. Separate scope if a mode-specific transcript becomes warranted.
- Removing `pytest.skip()` for missing dogfood. After this plan, no protocol is missing dogfood — but turning skip-on-missing into fail-on-missing is a follow-up for a separate small PR.
