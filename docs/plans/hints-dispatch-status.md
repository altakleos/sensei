---
feature: hints-dispatch-status
serves: docs/specs/hints.md
design: "Pure dispatch-table label correction in engine.md. No new mechanism, no behavior change, no spec change. Pattern instantiation of the existing dispatch-table convention where every other protocol is labelled `accepted`."
status: done
date: 2026-04-25
---
# Plan: Promote `protocols/hints.md` to `accepted` in `engine.md` Dispatch Table

The 2026-04-25 audit Move #3 (part 2): correct `engine.md:198` where `protocols/hints.md` is the only protocol still labelled `draft` in the dispatch table. Every other protocol is `accepted`. Spec, protocol prose, transcript fixtures, dogfood capture, and E2E test all assert the protocol is shipped — only the dispatch-table label is stale.

## Targets and Verified Evidence

| # | Target | Evidence (re-verified 2026-04-25 against post-merge `main`) |
|---|---|---|
| 1 | `engine.md:198` labels hints `draft` | `grep -n "hints\.md" src/sensei/engine/engine.md` returns `198: ... | protocols/hints.md | draft |`. |
| 2 | Spec is `accepted` | `head -3 docs/specs/hints.md` shows `status: accepted`. |
| 3 | Protocol prose declares itself executable | `head -3 src/sensei/engine/protocols/hints.md` shows `# Hints Triage Protocol — Executable` + the `prose-as-code` admonition. |
| 4 | Verification artifacts ship | `tests/transcripts/hints.md`, `tests/transcripts/hints.dogfood.md`, `tests/e2e/test_hints_protocol_e2e.py` all exist on `main`. |
| 5 | The label is historically stale, not deliberate | `git log -p src/sensei/engine/engine.md` shows `protocols/hints.md | draft` was the original label at introduction (well before the spec was promoted to `accepted`); subsequent commits added other protocols to the table without touching this row. |

## Approach

Single-line edit to `engine.md:198`: `draft` → `accepted`. No spec change (spec is already `accepted`), no ADR (no decision is being made — a stale label is being aligned with reality), no protocol-prose change beyond the table cell.

This is borderline-trivial under AGENTS.md ("renaming a local variable" / "deleting code the caller can prove is unreachable" sit at the same scale), but the edit lands inside protocol prose (`engine.md` is the kernel) and AGENTS.md explicitly counts protocol-prose changes as non-trivial. Plan-first respected; the plan is short to match the change.

## Tasks

- [x] T1 — `src/sensei/engine/engine.md:198`: change the status cell from `draft` to `accepted`. No other change to the table row or surrounding prose.
- [x] T2 — Run full local pipeline via `.venv/bin/`. All green. (Expected — no schema, no test, no protocol-execution change.)
- [x] T3 — Commit on `docs/hints-dispatch-status` branch with message `docs: promote protocols/hints.md to accepted in dispatch table`. Open PR.

## Acceptance Criteria

- [x] AC1 — `grep -n "protocols/hints.md" src/sensei/engine/engine.md` shows the row labelled `accepted`.
- [x] AC2 — `grep -n "draft" src/sensei/engine/engine.md` returns no matches in the dispatch table region (lines ~186–205).
- [x] AC3 — `.venv/bin/pytest && .venv/bin/ruff check . && .venv/bin/mypy && python ci/check_*.py` all green.
- [x] AC4 — `git diff --stat` shows changes only in `src/sensei/engine/engine.md` and this plan.

## Out of Scope

- Any change to the protocol prose itself. The protocol is already executable per its own header.
- Any change to the hints spec. Already `accepted`.
- Any CHANGELOG entry. Per AGENTS.md, "Refactors, internal tests, and docs-only edits don't need a changelog entry."
