---
feature: calibration-anchors-promotion
serves: docs/specs/calibration-anchors.md
design: "No design doc — this plan promotes a spec from draft to accepted (status frontmatter flip + README index update). No mechanism, no schema change, no protocol prose change. Pattern instantiation of the existing spec-promotion convention. Folds in a sibling stale-index repair for `cross-goal-intelligence.md` and `interleaving.md` whose spec files are already `accepted` but whose README rows still say `draft`."
status: done
date: 2026-04-25
---
# Plan: Promote `calibration-anchors.md` from Draft to Accepted

`docs/specs/calibration-anchors.md` has been `status: draft` since 2026-04-24 (commit `4b0c8c5`). The 2026-04-25 follow-up audit named it as the only currently-`draft` spec and asked: ship or close. This plan ships — promotes the spec to `accepted` — for four reasons:

1. **The schema seam is already in production.** v0.1.0a19's `anchor_type` enum on the hints registry (`src/sensei/engine/schemas/hints.yaml.schema.json:75-79`) is the spec's forward-compat investment. Closing the spec would require a v0.1.0a21 `Removed` CHANGELOG entry rolling that field back — destructive and asymmetric.
2. **The spec is detailed and self-consistent.** ~140 lines of intent + 9 invariants + trust hierarchy + goal-archetype table + ipsative-vs-criterion split + out-of-scope. Three personas stress-test it (`tomas`, `jacundu`, `nkechi`); three principles realize it (`P-curriculum-is-hypothesis`, `P-know-the-learner`, `P-mastery-before-progress`). It cross-references three accepted ADRs (0006, 0014, 0019) without contradiction.
3. **Promotion is intent-level, not implementation-level.** Per AGENTS.md "Required: Spec Before Design," accepting a spec commits the contract, not a release timeline. The maintainer can sequence implementation work whenever it makes sense.
4. **`status: draft` for >24h with no clear path is the audit smell** (per `docs/specs/README.md` template's spec-promotion convention). The cleanup is to either accept or close; accept is cheaper here.

While editing the spec index, the plan also corrects two pre-existing index drifts: `cross-goal-intelligence.md` and `interleaving.md` have `status: accepted` in their spec files (verified via `grep -n "^status:"`) but their `docs/specs/README.md` rows still say `draft`. Same class of bug as the `engine.md:298` link drift fixed in commit `77b5a7a` — same fix shape (text correction so the index matches reality).

## Tasks

- [x] T1 — Flip `docs/specs/calibration-anchors.md` frontmatter `status: draft` → `status: accepted`. Update the `fixtures_deferred:` rationale from "Draft spec. Fixtures follow accepted spec + implementation." to "Accepted spec; no implementation plan filed yet. Fixtures land alongside the first implementation work — see `protocols/goal.md` § Step 4 (curriculum generation) and `protocols/assess.md` for likely consumption sites." This keeps the field per the spec-template convention while making the new rationale honest about state.
- [x] T2 — Update `docs/specs/README.md` index — flip the `Calibration Anchors` row from `draft` to `accepted`.
- [x] T3 — Update `docs/specs/README.md` index — flip `Cross-Goal Intelligence` and `Interleaving` rows from `draft` to `accepted` (the spec files have already been `accepted` since 2026-04-22; only the index is stale).
- [x] T4 — Add a one-line entry to `CHANGELOG.md` `[Unreleased]` § Changed: announce the promotion. Mirrors the v0.1.0a19 entry that announced the draft. Per `docs/specs/release-communication.md`, contract-level changes that affect contributor expectations get a CHANGELOG line even when no runtime behaviour changes.
- [x] T5 — Add row to `docs/plans/README.md` § Shipped index.
- [x] T6 — Run the full local pipeline from the project venv: `.venv/bin/pytest && .venv/bin/ruff check . && .venv/bin/mypy && python ci/check_foundations.py && python ci/check_links.py && python ci/check_links.py --root src/sensei/engine && python ci/check_changelog_links.py && python ci/check_plan_completion.py`. All must stay green. `check_foundations.py` re-validates the `realizes` / `stressed_by` slugs on the now-accepted spec; that's the load-bearing assertion for promotion.
- [x] T7 — Commit message: `docs: accept calibration-anchors spec; repair specs/README index drift`. Body cites this plan and lists the index repairs.

## Acceptance Criteria

- [x] AC1 — `grep -n "^status:" docs/specs/calibration-anchors.md` returns `status: accepted`.
- [x] AC2 — `grep -n "fixtures_deferred:" docs/specs/calibration-anchors.md` returns one line with the updated rationale (no longer mentions "Draft spec").
- [x] AC3 — `grep -nE "^\| \[(Calibration Anchors|Cross-Goal Intelligence|Interleaving)\]" docs/specs/README.md` returns three lines, each ending in `| accepted |`.
- [x] AC4 — `CHANGELOG.md` `[Unreleased]` § Changed contains a one-line entry referencing the promotion and `docs/specs/calibration-anchors.md`.
- [x] AC5 — `python ci/check_foundations.py` passes (validates the spec's `realizes:` and `stressed_by:` slugs against `docs/foundations/`).
- [x] AC6 — Full local pipeline (T6) passes.
- [x] AC7 — `git diff --stat` touches only: this plan, `docs/plans/README.md`, `docs/specs/calibration-anchors.md`, `docs/specs/README.md`, `CHANGELOG.md`. No other files.

## Out of Scope

- **A design doc, ADR, or implementation plan for calibration anchors.** Promotion to `accepted` is a contract commitment, not an implementation start. The first implementation work will file its own plan.
- **Rolling back the `anchor_type` field on `hints.yaml.schema.json`.** That seam already shipped in v0.1.0a19 and is consistent with the now-accepted spec.
- **Editing other `draft` artifacts.** No other specs are draft as of this commit. Design docs and ADRs aren't surveyed by this plan.
- **A new ADR.** Promotion is a status flip on an existing intent doc; no new decision is being recorded.

## Risk and reversal

If the maintainer decides post-acceptance that the spec is wrong, the convention is to write a superseding spec (or close with a `superseded` status if no replacement is needed) — not to revert this commit. Spec promotion is reversible-by-supersession, mirroring the ADR pattern.
