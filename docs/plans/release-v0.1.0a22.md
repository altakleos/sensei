---
feature: release-v0.1.0a22
serves: docs/specs/release-process.md
design: "Pattern instantiation of docs/operations/release-playbook.md, exercising the v0.1.0a21 → v0.1.0a22 path. Same pipeline as v0.1.0a21 (full ADR-0024 + ADR-0027 + ADR-0028 trio + dynamic env-id resolution). The new ADR-immutability gate (CI step added in PR #44) is in scope here for the FIRST time on a release pipeline run — its push-mode invocation (HEAD only, no merge-base) will fire on the release commit itself; the commit edits no ADRs, so the gate will report OK. No new mechanism."
status: done
date: 2026-04-27
---
# Plan: Release v0.1.0a22

The `[Unreleased]` CHANGELOG section carries two substantive entries from the post-v0.1.0a21 work:

- **Contributor onboarding scaffolding** — top-level `Makefile` + `CONTRIBUTING.md` (PR #42, commit `73da673`)
- **ADR-immutability CI gate** — `ci/check_adr_immutability.py` enforced via `verify.yml` (PR #44, commit `911380f`)

A third change shipped on `main` since v0.1.0a21 — the script-layer constants refactor (`engine.scripts._states`, PR #43, commit `4b2dbc6`) — and a fourth — the Makefile-validators wiring follow-up (PR #45, commit `a29f009`) — are intentionally NOT in the user-facing CHANGELOG: the refactor preserves observable behaviour, and the Makefile-validators line is contributor-only mechanical wiring of the gate that PR #44 already announced. Per `release-communication.md` § "User-visible scope".

This release also exercises the **ADR-immutability gate** in CI for the first time on a release tag. The release commit edits no ADRs, so the gate reports OK in push-mode (HEAD only). If a future release commit ever touched an ADR (e.g., a status flip), the gate's exception list (frontmatter-only, Historical Note, trailer) would govern.

## CHANGELOG scope (maintainer decision, decision #2 at plan-approval time)

The `[0.1.0a22]` section retains ONLY the two existing user-facing `[Unreleased]` entries (Makefile/CONTRIBUTING + ADR-immutability gate). The script-constants refactor (PR #43) and the Makefile-validators wiring (PR #45) do NOT earn entries; they are non-user-visible per the spec. This narrows the precedent set by v0.1.0a20's ADR-0024 announcement and matches the v0.1.0a21 narrowing.

## Pre-flight verification (already done before filing this plan)

- `which claude` → `/home/rosantos/.local/bin/claude` ✓
- `CLAUDECODE=1` ✓
- → Per `release-playbook.md` § Pre-release gate "Agent-driven releases" clause, the agent drives the Tier-2 gate end-to-end via Option B (OAuth) without escalating cost-permission asks. Spend mentioned post-run.
- `gh auth status` — already validated this session via four successful PR pushes + four merges + one tag-less workflow watch.
- `__version__ = "0.1.0a21"` ✓ (current; bumps to `"0.1.0a22"`).

## Tasks

- [~] T1 — **Skipped (maintainer decision per the CHANGELOG-scope clause above):** no new entries added to `[Unreleased]` before promotion. CHANGELOG `[0.1.0a22]` carries only the two existing user-facing entries.
- [x] T2 — Bumped `src/sensei/__init__.py`: `__version__ = "0.1.0a21"` → `"0.1.0a22"`.
- [x] T3 — Promoted `## [Unreleased]` → `## [0.1.0a22] — 2026-04-27`; fresh empty `## [Unreleased]` heading above.
- [x] T4 — Updated CHANGELOG compare-link tail: `[Unreleased]:` now compares from `v0.1.0a22...HEAD`; `[0.1.0a22]: ...compare/v0.1.0a21...v0.1.0a22` inserted.
- [x] T5 — Pre-release Tier-2 gate ran clean: `7 passed in 666.11s (0:11:06)`, exit 0. Captured stdout sha256 = `8c7b95c6801875033adc06ec619846675e585fd87584652ae492969e5d23427f`. Run via SENSEI_E2E=1 (Option B, OAuth) per the agent-driven clause; spend ~$2-4.
- [x] T6 — Authored `docs/operations/releases/v0.1.0a22.md` with all seven test paths in body. `tool_version` captured from `claude --version` = `2.1.119 (Claude Code)`.
- [x] T7 — Full local pipeline green: `make gate` (lint + typecheck + tests + 6 validators including `check_adr_immutability.py`) and `python ci/check_release_audit.py --tag v0.1.0a22` (`release-audit: OK`) both exit 0.
- [x] T8 — Added row to `docs/plans/README.md` § Shipped index.
- [x] T9 — Committed `a58d317 chore: release v0.1.0a22` directly on main; pushed to `origin/main`.
- [x] T10 — Stopped for explicit user confirmation. On approval, tagged `v0.1.0a22` and pushed.
- [x] T11 — Watched `release.yml` run [#24973153525](https://github.com/altakleos/sensei/actions/runs/24973153525): pytest matrix (py3.10–3.13) all green, build-and-check passed (audit-log + breadth + package-contents + version concordance), publish job paused at the `pypi` GitHub Environment per ADR-0026.
- [x] T12 — Stopped for IRREVERSIBLE confirmation. User approved via the GitHub UI (publish job moved from `waiting` to `in_progress` without the agent's `gh api` call firing).
- [x] T13 — Approval landed via the GitHub Environment UI rather than the `gh api` recipe. Both paths converge on the same `pending_deployments` endpoint; the recipe is preserved in the playbook for terminal-only flows. The dynamic env-id resolver still verified working: `pypi` environment id = `14342694313` (matches the literal preserved in ADR-0026's body as historical record).
- [x] T14 — Verified on PyPI: direct JSON API confirms `latest: 0.1.0a22`, two artefacts shipped (`sensei_tutor-0.1.0a22-py3-none-any.whl` + `sensei_tutor-0.1.0a22.tar.gz`). `pip index versions` was CDN-stale at the moment of check; the JSON API was authoritative.
- [x] T15 — GitHub Release v0.1.0a22 created at https://github.com/altakleos/sensei/releases/tag/v0.1.0a22; body = the `[0.1.0a22]` CHANGELOG section verbatim + the `pip install sensei-tutor==0.1.0a22 --pre` install hint; flagged as `--prerelease`.

## Acceptance Criteria

- [x] AC1 — `src/sensei/__init__.py` reports `__version__ = "0.1.0a22"`.
- [x] AC2 — `CHANGELOG.md` has the `[0.1.0a22]` heading dated 2026-04-27 + a new empty `[Unreleased]` heading above it; the `[0.1.0a22]` block contains exactly the two user-facing Added entries that were under `[Unreleased]` at plan-filing time.
- [x] AC3 — `CHANGELOG.md` compare-link tail has `[0.1.0a22]: ...compare/v0.1.0a21...v0.1.0a22` and `[Unreleased]: ...compare/v0.1.0a22...HEAD`.
- [x] AC4 — `docs/operations/releases/v0.1.0a22.md` exists; frontmatter conforms to the template; body lists all seven test file paths.
- [x] AC5 — Tier-2 gate ran clean: 7 passed, 0 failed, exit 0; audit log captures the run.
- [x] AC6 — Full local pipeline green; `check_release_audit.py --tag v0.1.0a22` reports `release-audit: OK`.
- [x] AC7 — Tag `v0.1.0a22` pushed; `release.yml` triggered.
- [x] AC8 — `release.yml` verify job passed across py3.10–3.13; build-and-check job passed (audit-log + breadth gates green).
- [x] AC9 — Publish job paused at the `pypi` GitHub Environment per ADR-0026.
- [x] AC10 — User approval landed (via GitHub UI rather than `gh api`); workflow advanced; `sensei-tutor==0.1.0a22` is live on PyPI (verified via `https://pypi.org/pypi/sensei-tutor/json`).
- [x] AC11 — GitHub Release v0.1.0a22 created at https://github.com/altakleos/sensei/releases/tag/v0.1.0a22.

## Out of Scope

- **A non-aN bump** (v0.1.1, v0.1.0, etc.). Following the established alpha cadence; the GA exit-criteria spec (Recommendation #4 from the 2026-04-26 audit) is the prerequisite for that move and has not yet been written.
- **Yanking any prior release.** v0.1.0a21 stays on PyPI.
- **Re-running v0.1.0a21's release.** Idempotent at the workflow level; PyPI rejects duplicate uploads regardless.
- **A new ADR.** Pure pattern-instantiation of the existing release flow.
- **CHANGELOG entries for PR #43 (engine-state-constants) or PR #45 (Makefile-validators wiring).** Both are non-user-visible per `release-communication.md` § User-visible scope; explicitly skipped (decision #1).

## Risk and reversal

- **Pre-tag (T2–T9)**: each step reversible via `git revert <sha>`. Local pipeline + `make gate` is the gate; no remote artifact yet.
- **Post-tag, pre-publish (T10–T12)**: tag deletion via `git tag -d v0.1.0a22 && git push origin :v0.1.0a22` is possible but disruptive (cancels running CI). Acceptable if a problem surfaces between tag and publish.
- **Post-publish (T14+)**: PyPI does NOT allow deletion. Yank is the recovery path per the playbook § Yanking a Bad Release. **T13 is the irreversible step**; the explicit-confirmation gate at T12 exists precisely for this reason.
- **OAuth spend**: ~$2-4 per Tier-2 run. Already covered by the agent-driven clause; no separate ask.

## Notes

If T5 (Tier-2 gate) FAILS on any of the seven tests, this release is blocked. Per the playbook: "A red result means either a protocol prose regression or a schema drift. Do not tag until the gate is green." Surface the failure to the user; investigate before proceeding.

If T6 / T7 / T11 surface a `check_release_audit.py` failure (frontmatter mismatch, breadth gap, etc.) — that's the audit-log gate working as designed. Fix the audit log before re-running.

If T7 surfaces a `check_adr_immutability.py` failure on the release commit — that would be a surprise (the release commit shouldn't touch ADRs). Investigate immediately; the gate fires correctly only because something *was* edited.
