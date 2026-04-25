---
feature: tier3-hygiene
serves: docs/specs/release-process.md
design: "Pure documentation hygiene. No design doc needed."
status: done
date: 2026-04-25
---
# Plan: Tier 3 Doc Hygiene

Two stale/cosmetic items surfaced by the project analysis. Each is independently trivial; bundling because they're the same concern (contributor-facing doc accuracy).

## Tasks

- [x] T1: `AGENTS.md:49` — replace stale `(297 tests — unit, integration, transcript fixtures, E2E)` with a number-free description (`unit, integration, transcript fixtures, E2E`). The exact count drifts; the categorization is what a contributor needs.
- [x] T2: `docs/plans/README.md:39-42` — repair four collapsed table rows where two plan entries share one row (the `done ||` joiner pattern that put two `| plan | description | done |` triplets on a single line). Split each onto its own row so the table renders correctly.

## Acceptance Criteria

- [x] AC1: `AGENTS.md` line 49 carries no specific test count.
- [x] AC2: `docs/plans/README.md` table has one entry per row in the "Shipped" section.
- [x] AC3: `python ci/check_links.py` exits 0 (no link breakage from the README edits).
- [x] AC4: No CHANGELOG entry — docs-only edit per AGENTS.md:111.

## Out of Scope

- Validating the 6 unverified LLM shims (Cursor, Copilot, Windsurf, Cline, Roo, AI Assistant) — that's real engineering work needing its own plan.
- Restructuring the plan index (e.g., grouping by milestone) — separate concern.
