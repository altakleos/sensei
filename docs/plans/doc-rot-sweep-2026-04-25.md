---
feature: doc-rot-sweep-2026-04-25
serves: docs/specs/release-communication.md
design: "No design doc — pure documentation correction. No new mechanism, no new spec, no protocol prose change. Pattern instantiation of existing CHANGELOG / instance-template surfaces."
status: done
date: 2026-04-25
---
# Plan: Doc-Rot Sweep — 2026-04-25 Audit Findings (Corrected)

The 2026-04-25 repo audit surfaced documentation surfaces that contradict the current state of the codebase. An earlier draft of this plan included a sixth target (a "Known limitations" block in `README.md`) that turned out to be a context-bleed error — the cited content actually lives in the v0.1.0a1 historical CHANGELOG section, which is immutable per Keep-a-Changelog convention. That target has been dropped. The remaining five targets are independently re-verified below.

No code behavior changes. No spec or protocol prose changes. Bundled because the review cost dominates and each edit shares the same risk profile (false claims read by contributors and LLM agents).

## Targets and Re-Verified Evidence (2026-04-25)

| # | File | Line(s) | Current claim | Verified-current evidence it is false |
|---|---|---|---|---|
| 1 | `src/sensei/engine/defaults.yaml` | 2 | "Status: scaffolding. No real tunables yet — sections are placeholders for future work." | `head -3` confirms the comment is still present (re-checked 2026-04-25). `grep -c "^[a-z_]+:"` returns 10 top-level keys — `schema_version`, `mentor`, `learner`, `curriculum`, `memory`, `hints`, `cross_goal`, `interleaving`, `session_notes`, `performance_training` — all populated with real values, all schema-validated by `defaults.schema.json` per CHANGELOG v0.1.0a19. |
| 2 | `src/sensei/engine/templates/AGENTS.md` | 13 | "Never teach during assessment (ADR forthcoming — mentor behavioral invariants)." | Re-checked: line 13 still reads exactly that. ADR-0006 is `accepted` since 2026-04-20 (`docs/decisions/0006-hybrid-runtime-architecture.md:1–4`). `docs/specs/assessment-protocol.md` is `accepted` and exists. |
| 3 | `src/sensei/engine/templates/AGENTS.md` | 21 | "`.sensei/README.md` — engine contents overview (if present)" | Re-checked: line 21 still reads exactly that. `manifest.yaml` does not list `README.md` at the engine top level; the engine has subdirectory READMEs only (`profiles/`, `prompts/`, `protocols/`, `schemas/`). The "if present" hedge papers over a missing file no plan has scheduled. |
| 4 | `AGENTS.md` (source-repo) | 3 | "see `src/sensei/cli.py` → `_AGENTS_MD`" (with link to that path) | Re-checked: `grep -n "_AGENTS_MD" src/sensei/cli.py` returns zero matches. The instance-side document is in `src/sensei/engine/templates/AGENTS.md` and is loaded at `cli.py:251–255` via `agents_template = sensei_dir / "templates" / "AGENTS.md"`. |
| 5 | `CHANGELOG.md` | 309 (Unreleased) and missing entries between 309 and 310 | `[Unreleased]` compares from `v0.1.0a15...HEAD`; no compare-links exist for `[0.1.0a16]`, `[0.1.0a17]`, `[0.1.0a18]`, `[0.1.0a19]`. | Re-checked: `grep -nE "^\[(Unreleased\|0\.1\.0a)" CHANGELOG.md` confirms the link tail goes `[Unreleased] → [0.1.0a15] → [0.1.0a14] → ...` with the four most-recent releases skipped. Heading entries for a16/a17/a18/a19 exist on lines 9, 25, 36, 54. |

## Approach

Single squashable commit. Each edit is a literal text replacement; no logic, no API, no protocol, no schema. CI gates that run today (`pytest`, `ruff`, `mypy`, `ci/check_foundations.py`, `ci/check_links.py`, `ci/check_plan_completion.py`) must remain green; no new dependencies or hooks.

For target #3 there are two acceptable resolutions:
- **(A) Drop the line.** Cheapest, matches reality. Chosen as the default in T3 below.
- **(B) Ship `engine/README.md`** and register it in `manifest.yaml`. Out of scope here — that is a content-creation task, not a doc-rot fix. If the user prefers (B), this plan should be deferred and rewritten.

For target #5, new compare-links must follow the existing format exactly (`https://github.com/altakleos/sensei/compare/<from>...<to>`) so that future contributors don't introduce drift in URL shape. The four new lines are inserted between the existing `[Unreleased]:` line (which itself gets bumped to compare from `v0.1.0a19...HEAD`) and the existing `[0.1.0a15]:` line, in descending-version order to match the existing tail.

## Tasks

- [x] T1 — `src/sensei/engine/defaults.yaml:2`: replace the "scaffolding / placeholders for future work" header with one sentence pointing readers at `defaults.schema.json` as the authoritative shape and `learner/config.yaml` as the override surface. No semantic change to any tunable.
- [x] T2 — `src/sensei/engine/templates/AGENTS.md:13`: replace "Never teach during assessment (ADR forthcoming — mentor behavioral invariants)." with "Never teach during assessment — see `docs/specs/assessment-protocol.md` § Invariants and ADR-0006." Other two bullets unchanged.
- [x] T3 — `src/sensei/engine/templates/AGENTS.md:21`: drop the `.sensei/README.md` reference line. Leave the `.sensei/engine.md` reference. (Resolution A from § Approach.)
- [x] T4 — `AGENTS.md:3`: change the `src/sensei/cli.py` link + `_AGENTS_MD` symbol reference to a link pointing at `src/sensei/engine/templates/AGENTS.md` (the actual current path). Keep the surrounding sentence shape.
- [x] T5 — `CHANGELOG.md`: update line 309 (`[Unreleased]:`) to compare from `v0.1.0a19...HEAD`. Insert four new compare-link lines immediately after, in descending order: `[0.1.0a19]: ...compare/v0.1.0a18...v0.1.0a19`, `[0.1.0a18]: ...compare/v0.1.0a17...v0.1.0a18`, `[0.1.0a17]: ...compare/v0.1.0a16...v0.1.0a17`, `[0.1.0a16]: ...compare/v0.1.0a15...v0.1.0a16`. URLs follow the existing `https://github.com/altakleos/sensei/compare/<from>...<to>` shape.
- [x] T6 — Run the full local pipeline: `pytest && ruff check . && mypy && python ci/check_foundations.py && python ci/check_links.py && python ci/check_plan_completion.py`. All must stay green. (Expected: green — none of these edits affect Python source, schemas, foundations slugs, link targets, or plan checkboxes.)
- [x] T7 — Commit message: `docs: sweep stale doc surfaces flagged in 2026-04-25 audit`. Body cites this plan path and lists the five targets.

## Acceptance Criteria

- [x] AC1 — `grep -n "scaffolding\|placeholders for future work" src/sensei/engine/defaults.yaml` returns no match.
- [x] AC2 — `grep -n "ADR forthcoming" src/sensei/engine/templates/AGENTS.md` returns no matches.
- [x] AC3 — `grep -n "\.sensei/README\.md" src/sensei/engine/templates/AGENTS.md` returns no matches.
- [x] AC4 — `grep -n "_AGENTS_MD" AGENTS.md` returns no matches.
- [x] AC5 — `grep -nE "^\[0\.1\.0a(16|17|18|19)\]:" CHANGELOG.md` returns four lines, each with a well-formed compare URL. `grep -n "^\[Unreleased\]:" CHANGELOG.md` shows `v0.1.0a19...HEAD`.
- [x] AC6 — Full CI suite (T6) passes locally.
- [x] AC7 — `git diff --stat` shows changes only in: `docs/plans/doc-rot-sweep-2026-04-25.md` (this plan), `src/sensei/engine/defaults.yaml`, `src/sensei/engine/templates/AGENTS.md`, `AGENTS.md`, `CHANGELOG.md`. No other files modified.

## Out of Scope

- Adding `engine/README.md` (target #3, resolution B). Treated as a separate content task if the user prefers it.
- Adding `ci/check_changelog_links.py` or any other new CI gate (Move #2 from the audit). Separate plan.
- Tightening `defaults.schema.json` to mark inner tunables `required` (Move #3 from the audit). Separate plan.
- Resolving the `protocols/hints.md` status drift in `engine.md:198` (Move #3 from the audit). Separate plan because it touches protocol prose, which warrants spec/ADR consideration this sweep deliberately avoids.
- Any change to `README.md`. The audit's earlier "Known limitations" finding for the README was a context-bleed error; the README is current. CHANGELOG historical sections (e.g. `[0.1.0a1]`'s "Known limitations") are immutable per Keep-a-Changelog convention.
- Any change to test fixtures, transcripts, or the engine bundle's behavioural surface.
- Any CHANGELOG entry under `[Unreleased]`. This plan ships docs-only edits per AGENTS.md "Refactors, internal tests, and docs-only edits don't need a changelog entry."
