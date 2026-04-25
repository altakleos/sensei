---
feature: release-audit-enforcement
serves: docs/specs/release-process.md
design: "Pattern instantiation of existing ci/check_*.py linter family (check_package_contents, check_foundations, check_links, check_plan_completion, check_changelog_links). No new mechanism — adds one tag-keyed file-existence + frontmatter-shape validator wired into release.yml's build-and-check job. Single concern (release-gate auditability). ADR-0024 (lite) records the gate change."
status: done
date: 2026-04-25
---
# Plan: Release Audit-Log Enforcement

The Tier-2 behavioural E2E pre-release gate runs on the maintainer's workstation only. Commit cfd354c landed `docs/operations/releases/<tag>.md` as the audit-trail template, but `release.yml` does not require the file to exist before publishing — a maintainer who skips the gate **and** the log produces an unobservably-broken release. This plan adds machine-checked enforcement so the audit log becomes a release-gate property, not policy.

The change does not relax the human-approval invariant accepted by ADR-0020 (self-bypass for solo maintainer); it strengthens the *evidence trail* for the gate the maintainer is trusted to run. ADR-0020's trade-off (no second human reviewer) becomes safer once the workstation-only gate's outcome is committed and CI-verified before publish.

## Context

- Spec: [`docs/specs/release-process.md`](../specs/release-process.md). The invariant "Pre-release behavioural gate must be observable after the fact" is implicit in the spec's audit-trail expectation; the plan tightens enforcement, no spec amendment needed.
- Template: [`docs/operations/releases/README.md`](../operations/releases/README.md) — required frontmatter fields are `tag`, `date`, `tester`, `tool`, `tool_version`, `exit_code`, `transcript_hash`.
- Existing pattern: `ci/check_package_contents.py` is a tag-keyed validator already wired into `release.yml`'s `build-and-check` job; the new check follows the same shape.
- Decision-doc: ADR-0024 (lite) — records the gate change per `docs/development-process.md` § ADR-lite triggers (changes a human approval gate).

## Tasks

- [x] T1: Write ADR-0024 → `docs/decisions/0024-release-audit-log-required.md`. ADR-lite shape (Decision / Why / Alternative). Update `docs/decisions/README.md` index row for 0024. (depends: nothing — produces the design-skip target.)
- [x] T2: Implement validator → `ci/check_release_audit.py`. CLI: `python ci/check_release_audit.py --tag vX.Y.Z`. Assertions:
  - `docs/operations/releases/<tag>.md` exists and is readable.
  - YAML frontmatter parses and is a mapping.
  - Required fields present and non-empty: `tag`, `date`, `tester`, `tool`, `tool_version`, `exit_code`, `transcript_hash`.
  - `tag` field equals the `--tag` argument (catches copy-paste of last release's log).
  - `exit_code` is integer `0`.
  - `transcript_hash` is either a 64-char lowercase hex string OR the literal `"n/a"` (template allows the latter when stdout was discarded).
  - `tool` is one of `claude`, `kiro`, or a free-form non-empty string starting with `other:` to keep ADR-0003 conformance auditable while permitting future tools.
  - Exit 0 on success; exit 1 with a list of failed assertions on failure.
- [x] T3: Tests → `tests/ci/test_check_release_audit.py`. Cover: missing file; malformed YAML frontmatter; non-mapping frontmatter; missing each required field; mismatched `tag`; non-zero `exit_code`; bad `transcript_hash` (wrong length, uppercase, non-hex); unknown `tool`; happy path with `transcript_hash` as hex; happy path with `transcript_hash: "n/a"`. Use `tmp_path` and a small fixture template; mirror the structure of `tests/ci/test_check_package_contents.py`. (depends: T2.)
- [x] T4: Wire into `release.yml` → `.github/workflows/release.yml`. Add a `Validate release audit log` step in the `build-and-check` job, immediately after `Validate wheel contents against tag`, running `python ci/check_release_audit.py --tag "${GITHUB_REF_NAME}"`. The job already has the repo checked out; no new dependencies. (depends: T2.)
- [x] T5: Update `docs/operations/release-playbook.md` § Pre-release Checklist — promote the existing "Tier-2 E2E run captured to docs/operations/releases/v<X.Y.Z>.md" bullet from advisory to enforced; add a one-liner pointing at `ci/check_release_audit.py`. (depends: T2.)
- [x] T6: Update `docs/operations/releases/README.md` Index section — replace the "(empty — first entry lands with the next release)" line with a brief note that the file is now CI-enforced from `vX.Y.Z` onward (where X.Y.Z is the next tag after merge). (depends: T1.)
- [x] T7: Append `CHANGELOG.md` `## [Unreleased]` entry under `### Added` describing the new gate; reference ADR-0024. Keep one line. (depends: T1.)

## Acceptance Criteria

- [x] AC1: `python ci/check_release_audit.py --tag v0.1.0a20` exits 1 today (no audit log exists for the next planned tag), and exits 0 once a conformant log file lands.
- [x] AC2: `pytest tests/ci/test_check_release_audit.py -v` passes with all assertions from T3 covered; coverage on `ci/check_release_audit.py` is ≥ 92% (matches the project's `--cov-fail-under` floor).
- [x] AC3: `.venv/bin/ruff check ci/check_release_audit.py tests/ci/test_check_release_audit.py` and `.venv/bin/mypy` are clean.
- [x] AC4: `release.yml`'s `build-and-check` job fails when the audit log is missing or malformed; verified by reading the diff (no live release dry-run on `main`).
- [x] AC5: `python ci/check_changelog_links.py` and `python ci/check_links.py` and `python ci/check_plan_completion.py` and `python ci/check_foundations.py` all stay green after the changes.
- [x] AC6: ADR-0024 appears in `docs/decisions/README.md` index in number order; ADR text is ≤ 12 lines below frontmatter (ADR-lite shape).
- [x] AC7: `git grep -nE 'docs/operations/releases/<tag>\\.md' docs/` shows the playbook and audit-log README both reference the enforcer's existence.

## Out of Scope

- Backfilling audit logs for `v0.1.0a1`–`v0.1.0a19`. `releases/README.md:5` already records that pre-template releases have no recorded output to backfill from.
- Changing the workstation-only nature of the Tier-2 gate. CI still cannot run the gate; this plan only enforces the *artifact* of having run it.
- Re-opening ADR-0020. The self-bypass remains; this plan strengthens its evidence trail without modifying the bypass itself.
- Changing `ci/check_package_contents.py`. The new check is a sibling, not an extension, to keep concerns separable.

## Notes

- The validator is a single tag-keyed function; complexity is comparable to `ci/check_changelog_links.py` (~150 lines including tests).
- After merge but before the next release tag, T5–T6 documentation will reference a CI gate that has fired zero times. That is acceptable — the first real exercise is the next release cut.
