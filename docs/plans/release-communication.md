---
feature: release-communication
serves: docs/specs/release-communication.md
design: (thin — described inline in this plan)
status: planned
date: 2026-04-20
---
# Plan: Release Communication

Lands the invariants in `docs/specs/release-communication.md`. Seeds `CHANGELOG.md`, teaches `ci/check_package_contents.py` to enforce per-version changelog entries, bundles the file in the sdist, and updates the operational playbook to reflect that communication is now spec-driven.

## Tasks

### Phase 1 — Implementation

- [ ] T1: Create `CHANGELOG.md` at repo root in Keep a Changelog 1.1 format. Include `## [Unreleased]` section. Seed a `## [0.1.0a1] — 2026-04-20` entry from the existing GitHub Release body (condensed). → `CHANGELOG.md`
- [ ] T2: Extend `pyproject.toml` sdist include to carry `CHANGELOG.md`. Wheel remains excluded (per spec — changelogs inside wheels are non-standard and collide with bundle-integrity invariant). → `pyproject.toml`
- [ ] T3: Extend `ci/check_package_contents.py` — new `CHANGELOG_REQUIRED_ENTRY` check. Parse `CHANGELOG.md` from the sdist (not the wheel — the wheel doesn't carry it; tests read from disk relative to the validator invocation), assert a `## [<version>] — <YYYY-MM-DD>` heading exists for the tag's version. New exit code `4` = `changelog_missing_entry`. Updates the JSON report shape to include `changelog_status`. → `ci/check_package_contents.py`
- [ ] T4: Extend `tests/ci/test_check_package_contents.py` to cover: changelog entry present (happy path), changelog file missing entirely, changelog present but entry for the tag missing, changelog entry malformed (e.g., date missing), an `## [Unreleased]` heading counts as "not a released entry." → `tests/ci/test_check_package_contents.py`
- [ ] T5: Update `docs/operations/release-playbook.md`:
  - Pre-release checklist `CHANGELOG.md updated (if maintained)` → `CHANGELOG.md [Unreleased] section promoted to vX.Y.Z with today's date (per docs/specs/release-communication.md)`.
  - Normal Release step 5 "Create a GitHub Release on the tag with notes" → "Create a GitHub Release; body is the `CHANGELOG.md` section for vX.Y.Z verbatim plus `pip install sensei-tutor==X.Y.Z`."
  - Add a Yank step: "amend `CHANGELOG.md` in a follow-up commit with `**Yanked:** <reason, link to fix version>`. Never delete the entry."
  - Add pointer to `docs/specs/release-communication.md` in the References section.
  → `docs/operations/release-playbook.md`
- [ ] T6: Add a one-paragraph note to `AGENTS.md` recommending Conventional Commits (as loose convention, not enforced) and telling contributors to append user-visible changes to `## [Unreleased]` in the same commit that introduces them. → `AGENTS.md`

### Phase 2 — Verify

- [ ] T7: `pytest` full suite green including new changelog checks.
- [ ] T8: Local wheel + sdist build — confirm `CHANGELOG.md` appears in the sdist but NOT in the wheel. Run `python ci/check_package_contents.py --wheel dist/*.whl --tag v0.1.0a1` against a wheel matched by the existing seeded changelog entry; expect status `ok`.
- [ ] T9: Smoke — bump version to a throwaway `v0.1.0a99` in a local branch, rebuild, run the validator; expect exit 4 (`changelog_missing_entry`). Do NOT commit or tag the throwaway bump.

## Acceptance Criteria

- [ ] AC1: `CHANGELOG.md` exists, passes a manual Keep-a-Changelog format read, has `## [Unreleased]` and `## [0.1.0a1] — 2026-04-20`.
- [ ] AC2: `pyproject.toml` sdist include lists `CHANGELOG.md`; wheel target does not force-include it.
- [ ] AC3: `ci/check_package_contents.py` exits 4 when the tag's version has no dated entry; exits 0 for a valid full pipeline on `v0.1.0a1`.
- [ ] AC4: `tests/ci/test_check_package_contents.py` covers changelog-missing-entry, malformed-entry, and unreleased-only scenarios.
- [ ] AC5: Playbook's pre-release checklist enforces the Unreleased → version promotion; playbook Yank section documents the amendment rule; References point to the new spec.
- [ ] AC6: `AGENTS.md` mentions Conventional Commits preference and the "append to Unreleased" rule.
- [ ] AC7: Suite count grows by ≥3 tests.

## Out of Scope

- Conventional Commits enforcement (commitlint, CI gate). Convention-only.
- `git-cliff` / `semantic-release` / Changie / towncrier adoption.
- Automated PyPI long-description regeneration.
- Bundling `CHANGELOG.md` in the wheel.
- Backfilling changelog entries for versions prior to `0.1.0a1` (there are none).

## Notes

**Why the changelog is read from disk, not the sdist, in the validator:** the `build-and-check` CI job runs against the wheel. The sdist contains `CHANGELOG.md`; the wheel does not. Checking a file that lives only in the sdist from a wheel validator is awkward. Simpler: the validator reads `CHANGELOG.md` from the working directory relative to the repo root. At release time that file is always the one being shipped in the sdist. If the sdist and the on-disk file ever diverge (they shouldn't — hatchling bundles from disk), that's its own bug worth catching separately.
