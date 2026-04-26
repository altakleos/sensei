---
feature: question-density-metric
serves: docs/specs/behavioral-modes.md
design: "No new design doc — pattern instantiation of the existing silence_ratio metric (shipped per `silence-ratio-and-missing-dogfood.md`). Same shape: helper script in `src/sensei/engine/scripts/`, optional fixture-yaml `question_density: {min, max}` band consumed by `tests/transcripts/test_fixtures.py`, calibration comments naming each protocol's expected shape. No ADR (no architectural decision — second metric in an established family)."
status: done
date: 2026-04-26
---
# Plan: Question-Density Metric for Tier-1 Fixtures

The 2026-04-25 follow-up audit's Risk #4 named three quantitative metrics that would close the "principles-over-state-machines is asserted, not measured" gap (audit § 9 row 4). One metric — `silence_ratio` — was already in production across all 10 fixtures by v0.1.0a19. This plan adds the second: **question-density** = `mentor_questions / mentor_turns`.

Question-density complements silence_ratio: silence_ratio measures *how much* the mentor talks; question-density measures *what shape* the talk takes. A regression where a Socratic protocol (tutor, assess, challenger) drops from "asks every turn" to "explains every turn" would not necessarily move silence_ratio — the mentor talks the same amount — but would crater question-density. The new metric catches that class of drift.

The third metric named by the audit (`assessor-exception adherence count`) is deliberately deferred to a separate session because it requires an enumerated definition of "teaching language" patterns, which is a thornier authoring problem than this metric's per-turn `?` count.

## Design choices

- **What is a question?** A mentor sentence that ends in `?`. Heuristic: any `?` followed by whitespace or end-of-string. Captures `"Why does this work?"` and `"What's next? Move on."` (counts the first `?`). Ignores `?` inside code fences or quoted strings — same scope rule silence_ratio's word counter uses.
- **What is "density"?** `total_mentor_questions / total_mentor_turns` (float). A pure-Socratic mode shows ≥ 1.0 (each turn ends with at least one question). Lecture mode shows near 0. Multi-question turns are honoured (a single turn ending `"Why? What if?"` counts as 2).
- **Why per-turn (not per-word)?** Per-turn is interpretable as "how often does a mentor turn invite a learner response?" Per-word would smear high-density turns into long narrative turns that happen to contain one question. Per-turn matches the existing silence-profile vocabulary in `engine.md` § Invariants ("Tutor ~40% silent" framing).
- **No ADR.** Same pattern as silence_ratio (which had no ADR — it shipped via `silence-ratio-and-missing-dogfood.md`). Per AGENTS.md: "Second metric in an established family" doesn't warrant a new architectural decision record.

## Per-protocol expected ranges (calibrated during T4)

These are *intent-level* rough expectations; T4 measures actual values from the shipped dogfood transcripts and sets bands with margin:

| Protocol | Expected density | Rationale |
|---|---|---|
| `assess` | high (≥0.8) | Probing IS the protocol; teaching is forbidden |
| `tutor` | medium-high (≥0.4) | Teach by asking, but not every turn |
| `challenger` | high (≥0.7) | Provoke, don't tell |
| `review` | medium-high (≥0.4) | Recall via questions |
| `cross_goal_review` | high (≥0.6) | Pure Q&A across topics |
| `goal` | medium (≥0.3) | Clarify via questions, but also names rubric |
| `reviewer` | low (≤0.4) | Feedback is the deliverable; questions optional |
| `hints` | low (≤0.3) | Narrative triage, mentor reports |
| `status` | very low (≤0.2) | Reports state; rarely asks |
| `performance_training` | variable | Stage-dependent; will set after measurement |

Calibration sets `min` for question-heavy protocols (catches regression toward lecture) and `max` for narrative protocols (catches regression toward over-questioning that breaks the protocol's character).

## Tasks

- [x] T1 — Author `src/sensei/engine/scripts/question_density.py`. Library entry: `compute_question_density(text: str) -> float`. CLI entry: `python -m sensei.engine.scripts.question_density --transcript <path>` printing JSON `{mentor_turns, mentor_questions, question_density}`. Mirror `silence_ratio.py`'s overall shape — `[MENTOR]` / `[LEARNER]` turn extraction (re-use `compute_turn_stats` if convenient or duplicate the helper), `_strip_frontmatter`, fenced-code-block awareness for `?` counting. Module docstring names the heuristic ("any `?` followed by whitespace or end-of-string, outside fenced code blocks") and points at the silence_ratio sibling for the broader fixture-metric story.
- [x] T2 — Add `tests/scripts/test_question_density.py`. ~10-12 cases mirroring `test_silence_ratio.py`: zero-question transcript → 0.0; one question per turn → 1.0; multi-question turn → counts each; learner questions → ignored; questions inside code fences → ignored; questions inside YAML frontmatter → ignored; unknown encoding / missing file → exit 1.
- [x] T3 — Register `scripts/question_density.py` in `src/sensei/engine/manifest.yaml` (under the existing `scripts/` block, alphabetic position between `mutate_graph.py` and `resume_planner.py`). `tests/ci/test_engine_manifest.py` re-validates that every shipped script is registered.
- [x] T4 — **Calibration pass.** With T1 in place, run `compute_question_density` against each `<protocol>.dogfood.md` transcript and record the observed value. For each protocol:
  - Choose a band (`min` and/or `max`) that's the observed value ± a margin big enough to absorb single-LLM-run variance but tight enough to catch a real regression. Default margin: ±0.25 for high-density protocols, +0.30 ceiling for low-density protocols. Document the calibration in a per-fixture comment matching the silence_ratio comment style ("Calibrated against `<protocol>.dogfood.md` (observed N.NN). Catches the regression where ...").
  - High-density protocols (assess, challenger, tutor, review, cross_goal_review): set `min` only; ceiling unbounded.
  - Low-density protocols (reviewer, hints, status, goal): set `max` only; floor unbounded.
  - Mixed (`performance_training`, others if observation surprises): set both `min` and `max` with documented rationale.
- [x] T5 — Extend `tests/transcripts/test_fixtures.py` to consume `question_density: {min, max}` from the fixture frontmatter, mirroring the silence_ratio block. Same shape: import `compute_question_density`, evaluate against the dogfood transcript, assert against `min` / `max` with a clear failure message naming the observed value.
- [x] T6 — Add `question_density:` blocks to all 10 fixture files (`tests/transcripts/<protocol>.md`) under each fixture's existing `silence_ratio:` block. Use the bands T4 produced. Each block carries a one-line comment naming the observed value and the regression mode the band catches.
- [x] T7 — One-line `[Unreleased]` § Added entry in `CHANGELOG.md` announcing the new metric — mirrors how the v0.1.0a19 entry announced silence_ratio. Per `docs/specs/release-communication.md`, contributor-facing test infrastructure that becomes a release-gate signal warrants a CHANGELOG line.
- [x] T8 — One-paragraph note in `docs/design/transcript-fixtures.md` § Fixture schema (or wherever silence_ratio is documented) introducing `question_density` as the second quantitative metric, alongside silence_ratio. Cross-reference this plan.
- [x] T9 — Run the full local pipeline: `.venv/bin/pytest && .venv/bin/ruff check . && .venv/bin/mypy && python ci/check_foundations.py && python ci/check_links.py && python ci/check_links.py --root src/sensei/engine && python ci/check_changelog_links.py && python ci/check_plan_completion.py`. All green, including the 10 newly-banded fixture cases.
- [x] T10 — Add row to `docs/plans/README.md` § Shipped index.
- [x] T11 — Commit message: `feat: question-density metric for Tier-1 fixtures`. Body cites this plan, names the helper + tests + manifest entry + 10 fixture bands, and references the silence_ratio sibling.

## Acceptance Criteria

- [x] AC1 — `src/sensei/engine/scripts/question_density.py` exists; library function `compute_question_density(text: str) -> float` is importable.
- [x] AC2 — `python -m sensei.engine.scripts.question_density --transcript tests/transcripts/assess.dogfood.md` exits 0 and prints a JSON object with the three named keys.
- [x] AC3 — `tests/scripts/test_question_density.py` has at least 10 test functions and passes.
- [x] AC4 — `src/sensei/engine/manifest.yaml` lists `scripts/question_density.py` under the scripts block; `tests/ci/test_engine_manifest.py` passes.
- [x] AC5 — All 10 `tests/transcripts/<protocol>.md` fixtures have a `question_density:` block under their existing `silence_ratio:` block, each with a one-line calibration comment.
- [x] AC6 — `tests/transcripts/test_fixtures.py` consumes the new field; `tests/transcripts/test_fixtures.py::test_transcript_fixture` cases pass against all dogfood transcripts.
- [x] AC7 — `[Unreleased]` § Added in `CHANGELOG.md` contains the announcement entry; `python ci/check_changelog_links.py` passes.
- [x] AC8 — Full local pipeline (T9) passes with coverage ≥ 92%.
- [x] AC9 — `git diff --stat` touches only: this plan, `docs/plans/README.md`, the new `question_density.py` + its tests, `manifest.yaml`, the 10 fixture files, `test_fixtures.py`, `CHANGELOG.md`, `docs/design/transcript-fixtures.md`. No other files.

## Out of Scope

- **Assessor-exception adherence counter** (the third metric the audit named). Requires an enumerated regex set for "teaching language" — a separate authoring problem worth its own session.
- **Backfill silence_ratio bands.** Already done across all 10 fixtures (v0.1.0a19 work). The audit's claim that silence_ratio was "defined for some protocols only" was stale.
- **A new fixture for `calibration-anchors`.** That spec is now `accepted` (per `65f19f0`) but has no implementation yet; fixtures land alongside the first implementation work, not now.
- **Updating `engine.md` § Invariants prose** to reference question-density alongside the existing silence-profile language. Engine prose creep is a real cost; the test-side enforcement is sufficient signal for this metric. Revisit if a future session adds two more metrics.
- **`--from` / `--to` flags on the helper for measuring partial transcripts.** The full-transcript measurement is what the fixtures consume; partial-range measurement is YAGNI.

## Risk and reversal

- **Calibration variance.** Real-LLM dogfood is one sample. Bands set tight to a one-sample observation can flake when the dogfood is re-captured. Mitigation: T4 documents margin per protocol; defaults are wide (±0.25 for high-density, +0.30 for low-density). The maintainer can tighten later as more dogfood samples accumulate.
- **Reversal**: revert the commit. No persistent state, no schema migration, no engine bundle integrity beyond a manifest entry that the inverse `test_engine_manifest` test re-validates on revert.
