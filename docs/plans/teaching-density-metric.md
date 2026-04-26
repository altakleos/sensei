---
feature: teaching-density-metric
serves: docs/specs/assessment-protocol.md
design: "No new design doc — third metric in the established Tier-1 quantitative-band family (silence_ratio + question_density). Same shape: helper script in `src/sensei/engine/scripts/`, optional fixture-yaml `teaching_density: {max}` band consumed by `tests/transcripts/test_fixtures.py`, calibration comments naming each protocol's expected ceiling. No ADR — pattern instantiation, not a new architectural decision."
status: done
date: 2026-04-26
---
# Plan: Teaching-Density Metric for Tier-1 Fixtures

The 2026-04-25 follow-up audit's Risk #4 named three quantitative metrics that would close the "principles-over-state-machines is asserted, not measured" gap. Two are now in production: `silence_ratio` (v0.1.0a19, all 10 fixtures) and `question_density` (commit `7d76e6c`, all 10 fixtures). This plan ships the third — **teaching-density** — and closes Risk #4.

The audit named the third metric "assessor-exception adherence count." Generalising one notch: the assessor exception (`engine.md` § Invariants: "during assessment, never teach") is the canonical case, but the same prohibition holds for `review` (no reteach), `challenger` (provoke, don't tell), `reviewer` (feedback ≠ teaching), `cross_goal_review` (Q&A, not teach), `status` (reports, not teaches), and `hints` (triage, not teaching). Each protocol's existing `forbidden_phrases` list already enumerates teaching-shaped phrases — but those lists are scattered, partially overlapping, and binary (one match = fail; the count is invisible). A unified taxonomy + density metric makes the "teaching pressure" a measurable, comparable signal across protocols.

`tutor` and `performance_training` (stage 1) are NOT teaching-prohibited; they omit the band.

## Design choices

- **Taxonomy lives in the helper, not per-fixture.** Mining the existing `assess` / `hints` / `review` `forbidden_phrases` lists for teaching-shaped patterns produces a ~14-entry canonical regex set: `let me explain`, `here's why`, `here's a hint`, `the (correct |right )?answer is`, `think about`, `remember that`, `to help you`, `to clarify`, `actually,`, `what if i told you`, `consider this`, `the trick is`, `the solution is`, `what you need to know`. Case-insensitive. Module constant `_TEACHING_PATTERNS`.
- **Density, not count.** `teaching_density = teaching_token_appearances / mentor_turns`. Mirrors `question_density` shape — per-turn rate, not absolute count. For protocols where teaching is forbidden, `max: 0.0` is the appropriate band; for `performance_training` stage 1 (where teaching IS the protocol but doesn't dominate per-turn), a higher ceiling like `max: 1.0` could apply if needed. `tutor` omits the band entirely.
- **Max only, no min.** A teaching-token floor is never useful — having no teaching language in a Socratic protocol is the desired outcome.
- **Existing `forbidden_phrases` stay.** This metric is additive. Removing the per-fixture lists would lose the named-phrase precision that the lists carry; the new metric provides a complementary cross-protocol signal.
- **No ADR.** Same pattern as silence_ratio (no ADR) and question_density (no ADR). Three metrics in the family is enough to call this an established pattern, not a new architectural decision.

## Per-protocol expected bands (set in T5 against measured values)

| Protocol | Teaching policy | Band |
|---|---|---|
| `assess` | Forbidden (assessor exception) | `max: 0.0` |
| `review` | Forbidden (no reteach) | `max: 0.0` |
| `challenger` | Forbidden (provoke, don't tell) | `max: 0.0` |
| `reviewer` | Forbidden (feedback ≠ teaching) | `max: 0.0` |
| `cross_goal_review` | Forbidden (Q&A, not teach) | `max: 0.0` |
| `status` | Forbidden (reports, not teaches) | `max: 0.0` |
| `hints` | Forbidden during triage | `max: 0.0` |
| `goal` | OMIT — see calibration note below | OMIT |
| `tutor` | Allowed (teaching is the protocol) | OMIT |
| `performance_training` | Allowed (stage 1 is instructional) | OMIT |

**Calibration note (2026-04-26).** T3 measurement against the shipped `goal.dogfood.md` produced density 1.500 (3 token matches across 2 mentor turns), all three confirmed false positives: two `the answer is` matches inside conditional system-design framing (`"if the answer is bad / if the answer is good"`) and one `think about` match inside a quoted hypothetical (`"We didn't think about abuse"`). The goal protocol's clarification language legitimately overlaps with teaching-token shapes in problem-framing and conditional analysis, so the band cannot be set without producing systematic noise. Omitting `goal` matches the same rationale that omits `tutor` and `performance_training` — protocols whose legitimate prose overlaps the taxonomy. The metric stays load-bearing on the seven protocols where teaching is genuinely forbidden.

Calibration in T3 measures actual teaching_density per dogfood transcript. If a "Forbidden" protocol's measured value is non-zero, that's a real fixture-level signal — it means the dogfood capture itself contains a violation that should be re-captured (or the band loosened with explicit rationale).

## Tasks

- [x] T1 — Author `src/sensei/engine/scripts/teaching_density.py`. Library entry: `compute_teaching_density(text: str) -> float`. CLI entry: `python -m sensei.engine.scripts.teaching_density --transcript <path>` printing JSON `{mentor_turns, teaching_token_count, teaching_density}`. Same shape as `question_density.py` — imports `_split_into_turns` from silence_ratio, strips fenced code blocks, applies the canonical `_TEACHING_PATTERNS` regex against each mentor turn (case-insensitive), sums matches, divides by mentor_turns. Module docstring lists the canonical taxonomy and points at the assessor exception in `engine.md` § Invariants.
- [x] T2 — Add `tests/scripts/test_teaching_density.py`. ~12-14 cases mirroring `test_question_density.py` shape: zero-token transcript → 0.0; one token per turn → 1.0; multi-token turn → counts each; learner teaching tokens → ignored; tokens in code fences → ignored; tokens in frontmatter → ignored; case-insensitive matching; specific patterns covered (`let me explain`, `the answer is`, `think about`, etc.); CLI happy path, missing file, no-mentor-turns, subprocess invocation.
- [x] T3 — **Calibration pass.** With T1 in place, run `compute_teaching_density` against each `<protocol>.dogfood.md` and record observed values. For each "Forbidden" protocol, the expected value is 0.0; if non-zero, surface that in the plan completion notes and either fix the dogfood or document the loosening.
- [x] T4 — Register `scripts/teaching_density.py` in `src/sensei/engine/manifest.yaml` (alphabetic position: after `silence_ratio.py`).
- [x] T5 — Extend `tests/transcripts/test_fixtures.py` to consume `teaching_density: {max}` from fixture frontmatter, mirroring the existing `silence_ratio` / `question_density` blocks. Same shape: import `compute_teaching_density`, evaluate, assert against `max` only.
- [x] T6 — Add `teaching_density:` blocks to 7 of the 10 fixture files (omit `tutor`, `performance_training`, AND `goal` — see calibration note). Each block carries a one-line comment naming the observed value (0.000 for all seven) and the regression mode the band catches.
- [x] T7 — One-line `[Unreleased]` § Added entry in `CHANGELOG.md` announcing the metric. Mirrors how question_density was announced.
- [x] T8 — Update `docs/design/transcript-fixtures.md` § Loader bullet 4 (the quantitative-metric paragraph added in commit `7d76e6c`) to enumerate all three metrics: silence_ratio + question_density + teaching_density.
- [x] T9 — Run the full local pipeline. All green, including the 8 newly-banded fixture cases.
- [x] T10 — Add row to `docs/plans/README.md` § Shipped index.
- [x] T11 — Commit message: `feat: teaching-density metric closes Tier-1 audit Risk #4`. Body cites this plan, names the helper + tests + 8 fixture bands, and notes Risk #4 is now closed (silence_ratio + question_density + teaching_density all in production).

## Acceptance Criteria

- [x] AC1 — `src/sensei/engine/scripts/teaching_density.py` exists; library function `compute_teaching_density(text: str) -> float` is importable.
- [x] AC2 — `python -m sensei.engine.scripts.teaching_density --transcript tests/transcripts/assess.dogfood.md` exits 0 and prints a JSON object with the three named keys.
- [x] AC3 — `tests/scripts/test_teaching_density.py` has at least 12 test functions and passes.
- [x] AC4 — `src/sensei/engine/manifest.yaml` lists `scripts/teaching_density.py`; `tests/ci/test_engine_manifest.py` passes.
- [x] AC5 — Seven fixtures (all except `tutor`, `performance_training`, and `goal` per the calibration note) have a `teaching_density:` block under their existing `question_density:` block, each with a one-line calibration comment.
- [x] AC6 — `tests/transcripts/test_fixtures.py` consumes the new field; all `tests/transcripts/test_fixtures.py::test_transcript_fixture` cases pass against shipped dogfood transcripts.
- [x] AC7 — `[Unreleased]` § Added in `CHANGELOG.md` contains the announcement entry.
- [x] AC8 — `docs/design/transcript-fixtures.md` enumerates all three quantitative metrics in the loader paragraph.
- [x] AC9 — Full local pipeline (T9) passes with coverage ≥ 92%.
- [x] AC10 — `git diff --stat` touches only: this plan, `docs/plans/README.md`, the new `teaching_density.py` + its tests, `manifest.yaml`, the 7 fixture files, `test_fixtures.py`, `CHANGELOG.md`, `docs/design/transcript-fixtures.md`. No other files.

## Out of Scope

- **Removing the existing `forbidden_phrases` lists** in `assess.md`, `hints.md`, `review.md`. The lists carry named-phrase precision (the no-reteach fixture catches `the right answer is` specifically) that the cross-protocol metric loses by aggregating. Both signals coexist; the new metric is additive.
- **Expanding the taxonomy beyond ~14 patterns.** The canonical set comes from mining existing forbidden_phrases. A future session can ratchet the list as more dogfood samples reveal regressions the current list misses.
- **A `teaching_density` band on `tutor` or `performance_training`.** Both are teaching-protocols by design; a band is meaningless. Future expansion could distinguish "good teaching" patterns from "bad teaching" but that's a much harder authoring problem.
- **Quantitative bands on `forbidden_phrases` themselves** (e.g., "max 2 violations allowed"). Binary fail-on-any is the right semantics for forbidden phrases — a regression that adds one violation is real.

## Risk and reversal

- **Calibration surprise.** A "Forbidden" protocol's dogfood may already contain a teaching-token (e.g., the LLM said "actually, " in a non-teaching context). T3 surfaces this; the plan-execution comment for that protocol will document whether the dogfood needs re-capture or the taxonomy needs refinement.
- **Taxonomy false-positives.** Phrases like `the answer is` could legitimately appear in non-teaching contexts ("So the answer is, you tell me"). The risk is a band fails on a non-regression. Mitigation: the calibration pass surfaces this immediately; bands can loosen on a per-fixture basis with explicit comment.
- **Reversal**: revert the commit. No persistent state, no schema migration. Manifest entry is one line.
