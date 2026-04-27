---
feature: release-v0.1.0a22
serves: docs/specs/release-process.md
design: "Pattern instantiation of docs/operations/release-playbook.md, exercising the v0.1.0a21 → v0.1.0a22 path. Same pipeline as v0.1.0a21 (full ADR-0024 + ADR-0027 + ADR-0028 trio + dynamic env-id resolution). The new ADR-immutability gate (CI step added in PR #44) is in scope here for the FIRST time on a release pipeline run — its push-mode invocation (HEAD only, no merge-base) will fire on the release commit itself; the commit edits no ADRs, so the gate will report OK. No new mechanism."
status: in-progress
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
- [ ] T2 — Bump `src/sensei/__init__.py`: `__version__ = "0.1.0a21"` → `"0.1.0a22"`.
- [ ] T3 — Promote `## [Unreleased]` → `## [0.1.0a22] — 2026-04-27`. Add a fresh empty `## [Unreleased]` heading above it.
- [ ] T4 — Update CHANGELOG compare-link tail: bump `[Unreleased]:` to compare from `v0.1.0a22...HEAD`; insert `[0.1.0a22]: https://github.com/altakleos/sensei/compare/v0.1.0a21...v0.1.0a22` immediately below.
- [ ] T5 — Run pre-release Tier-2 gate (7 tests, ~12-14 min, ~$2-4 OAuth via Option B per the agent-driven clause). Capture pytest stdout for the audit log; compute sha256 of the captured stdout for the `transcript_hash` frontmatter field. The full command is the `GATE_TESTS=( … )` array from `release-playbook.md:24–32` plus `SENSEI_E2E=1 .venv/bin/pytest "${GATE_TESTS[@]}" -v --no-cov`.
- [ ] T6 — Author `docs/operations/releases/v0.1.0a22.md` per the template at `docs/operations/releases/README.md`. Frontmatter: `tag: v0.1.0a22`, `date: 2026-04-27`, `tester: makutaku`, `tool: claude`, `tool_version: <captured from `claude --version`>`, `exit_code: 0`, `transcript_hash: <sha256 of T5's stdout>`. Body MUST list all seven test file paths from `REQUIRED_GATE_TESTS` (ADR-0028 breadth check enforces this).
- [ ] T7 — Run the full local pipeline as a final pre-tag check via `make gate` (which now invokes all six validators including the new `check_adr_immutability.py`) plus `python ci/check_release_audit.py --tag v0.1.0a22`. The audit-log validator MUST pass against the new file.
- [ ] T8 — Add row to `docs/plans/README.md` § Shipped index.
- [ ] T9 — Stage + commit T2–T8 with message `chore: release v0.1.0a22`. Body lists the [Unreleased] → [0.1.0a22] promotion, the two user-facing entries, the Tier-2 gate's seven-test outcome, and references the audit log file. Push to `origin/main` (release commits land directly on main per the v0.1.0a21 + v0.1.0a17 + v0.1.0a13 precedent — release.yml is the gate, not PR review).
- [ ] T10 — **STOP for confirmation.** Surface the commit SHA and `[0.1.0a22]` CHANGELOG section to the user. Tag only after explicit confirmation. On confirmation: `git tag v0.1.0a22 && git push origin v0.1.0a22`.
- [ ] T11 — Watch the release.yml workflow via `gh run watch`. Verify: pytest matrix (py3.10–3.13) green, build-and-check job green (which runs `check_release_audit.py` against the new audit log per ADR-0024 + ADR-0028 — the load-bearing gate of this release), and the publish job pausing at the `pypi` environment for manual approval per ADR-0026.
- [ ] T12 — **STOP for IRREVERSIBLE confirmation.** Once the publish job pauses, surface the run ID + run URL and the `gh api` approval recipe. Do NOT issue the `state=approved` POST without explicit user authorisation per the playbook ("Genuinely irreversible actions — PyPI publish… still require explicit confirmation").
- [ ] T13 — On user authorisation: resolve `ENV_ID` via `gh api repos/altakleos/sensei/environments/pypi --jq '.id'` (per ADR-0026 / commit `b006a6d`), then `gh api repos/altakleos/sensei/actions/runs/<RUN_ID>/pending_deployments --method POST --field "environment_ids[]=$ENV_ID" --field state=approved --field "comment=Ship it"`. Workflow advances and publishes.
- [ ] T14 — Verify the published artifact: `pip index versions sensei-tutor` should list 0.1.0a22.
- [ ] T15 — Create a GitHub Release for v0.1.0a22 per the playbook (body = the `[0.1.0a22]` CHANGELOG section verbatim + `pip install sensei-tutor==0.1.0a22 --pre` install hint).

## Acceptance Criteria

- [ ] AC1 — `src/sensei/__init__.py` reports `__version__ = "0.1.0a22"`.
- [ ] AC2 — `CHANGELOG.md` has the `[0.1.0a22]` heading dated 2026-04-27 + a new empty `[Unreleased]` heading above it; the `[0.1.0a22]` block contains exactly the two user-facing Added entries that were under `[Unreleased]` at plan-filing time (no PR #43 / #45 entries — per T1's skip).
- [ ] AC3 — `CHANGELOG.md` compare-link tail has `[0.1.0a22]: ...compare/v0.1.0a21...v0.1.0a22` and `[Unreleased]: ...compare/v0.1.0a22...HEAD`.
- [ ] AC4 — `docs/operations/releases/v0.1.0a22.md` exists; frontmatter conforms to the template; body lists all seven test file paths from `REQUIRED_GATE_TESTS`.
- [ ] AC5 — Tier-2 gate (T5) ran clean: 7 passed, 0 failed, exit 0; the audit log captures the run.
- [ ] AC6 — Full local pipeline (T7) green: `make gate` (lint + typecheck + tests + 6 validators including `check_adr_immutability.py`) and `python ci/check_release_audit.py --tag v0.1.0a22` both exit 0.
- [ ] AC7 — Tag `v0.1.0a22` pushed; `release.yml` triggers.
- [ ] AC8 — `release.yml` verify job passes across py3.10–3.13; build-and-check job passes (audit log + breadth gates green).
- [ ] AC9 — Publish job pauses at the `pypi` GitHub Environment per ADR-0026.
- [ ] AC10 — On explicit user authorisation, the `gh api` approval call returns success; workflow advances; `sensei-tutor==0.1.0a22` appears on PyPI.
- [ ] AC11 — GitHub Release for v0.1.0a22 created.

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
