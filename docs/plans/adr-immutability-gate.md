---
feature: adr-immutability-gate
serves: docs/development-process.md § ADRs (immutability invariant)
design: "No new design doc — verification gate for an existing process invariant (`development-process.md:82`: 'ADRs are immutable once accepted. To reverse a decision, write a new ADR that supersedes it'). Same shape as `ci/check_plan_completion.py` (walk markdown files, parse frontmatter, assert structural invariant against the working tree and git history). The skip-conditions in `development-process.md § When to Skip a Design Doc` apply: pattern instantiation of an existing CI-validator pattern; single-concern; the invariant the gate enforces is named in the spec layer; this plan covers the file-level breakdown. No ADR — the rule already exists in the method doc; this only adds mechanical enforcement, which is the point of the validators-close-the-loop principle."
status: done
date: 2026-04-26
---
# Plan: CI Gate for ADR Immutability

The 2026-04-26 audit (Recommendation #5, Risk #3) named ADR mutability as the only convention-only invariant in the SDD method without a mechanical guard. `AGENTS.md` and `docs/development-process.md:82` both state "ADRs are immutable once accepted." `git log --diff-filter=M docs/decisions/*.md` shows seven accepted ADRs have had body content modified after acceptance:

- ADR-0006 — modified 3× (most recently `bcd2a7a docs: update stale v2 deferral language for shipped features`)
- ADRs 0017 / 0018 / 0019 / 0020 / 0012 / 0004 — modified 2× each

Two of these classes are *legitimate* under the existing process:
1. **Status transitions** — `provisional → accepted`, `accepted → superseded` (frontmatter-only; the FSM is documented in `development-process.md § Status values`).
2. **Adding a `superseded-by:` annotation** — frontmatter-only; the rule explicitly anticipates this.

The third class — *body-text edits to accepted ADRs* — is the one the audit flagged. The fix is a CI gate that distinguishes legitimate frontmatter-FSM changes from illegitimate body changes, and fails the build when a body change happens without an explicit, audit-traceable opt-out.

## Design choices

- **Diff-based, not snapshot-based.** The gate compares each PR's working-tree ADR contents against the same files at the merge base (or, in `verify.yml`'s push-to-main case, the previous commit on `main`). It does not maintain a separate snapshot file — that would itself be a target for silent edits.
- **What's locked vs. what's free.**
  - **Frontmatter:** mutable. `status` may transition through the FSM (`provisional → accepted | superseded`, `accepted → superseded`); `date` may be updated only on a status transition; `superseded-by:` may be added when status becomes `superseded`. Other frontmatter additions (e.g., `protocols:`) are tolerated because the schema is loose.
  - **Body (everything below the closing `---`):** **immutable** once status reached `accepted` or `accepted (lite)`, with the explicit-opt-out below.
- **Explicit opt-out: commit-message trailer.** A maintainer can edit a frozen ADR body by adding a trailer to the commit message: `Allow-ADR-edit: NNNN — <reason>`. The gate parses the most-recent commit touching the ADR; if the trailer cites the ADR's number with a non-empty reason, the body diff is allowed. The trailer becomes the audit log. Multiple ADRs in one commit need a comma-separated list: `Allow-ADR-edit: 0006, 0017 — typo sweep`.
- **Special-case: appending to `## Historical Note`.** If the diff is purely additive at the bottom of the file under a heading matching `^##+\s+Historical Note` (case-insensitive), it is allowed without a trailer. This pattern matches what ADR-0020 + the playbook-historical-note hunk in `release-playbook.md:223–227` already do — preserving archaeology while making it visible.
- **The gate runs on every PR and every push to main**, via `verify.yml`. Failure is hard, not warn — promote-from-warn is not needed because the gate fires only on a clear contract violation.
- **Provisional ADRs are exempt** — body edits to `provisional` ADRs are allowed (the status itself implies mutability). This matches `development-process.md`: "provisional — accepted on current evidence, flagged for review when verification evidence lands."

## Algorithm sketch

For each `docs/decisions/NNNN-*.md` modified in the diff between `HEAD` and the comparison base:

1. Load old contents (`git show <base>:<path>`) and new contents (working tree).
2. Parse YAML frontmatter from both.
3. If old `status` is **not** in `{accepted, accepted (lite)}`: skip — ADR is provisional or being created. Allowed.
4. If old `status` is `accepted` and new `status` is `superseded` *and* the only body change is appending a `## Historical Note` section *or* there is no body change at all: allowed.
5. Strip frontmatter from both old and new; compare body bytes.
   - **Equal:** allowed (frontmatter-only change).
   - **Different:** check the commit message of the most-recent commit touching this file (`git log -1 --format=%B -- <path>`). If it contains an `Allow-ADR-edit:` trailer that names this ADR's number with a non-empty reason: allowed. Otherwise: **fail**.
6. After all files processed, if any file failed: print structured error per file (path, ADR number, what changed, hint to add `Allow-ADR-edit:` trailer or write a superseding ADR), exit 1.

The gate is implemented as `ci/check_adr_immutability.py` with a function-level entry point so the test suite can invoke it on synthetic ADR fixtures without a real git repo.

## Tasks

- [x] T1 — Authored `ci/check_adr_immutability.py` (~250 lines). Library entry: `check_adr_immutability(repo_root: Path, base_ref: str | None = None, head: str = "HEAD") -> tuple[int, list[str]]`. CLI entry honours `--base-ref`, `--head`, `--repo`. Algorithm per the sketch. The default base-ref is `None` (push-mode: HEAD only) rather than `origin/main` so the gate works on local checkouts without a configured remote; PR mode opts in via the workflow snippet in T3.
- [x] T2 — Authored `tests/ci/test_check_adr_immutability.py` with 16 cases covering:
  - frontmatter-only change to an accepted ADR — allowed
  - body change to a provisional ADR — allowed
  - body change to an accepted ADR without trailer — **fail**
  - body change with valid `Allow-ADR-edit: NNNN — reason` trailer — allowed
  - body change with `Allow-ADR-edit:` trailer naming a different ADR — fail
  - body change with empty reason after the dash — fail
  - status transition `accepted → superseded` with `superseded-by:` annotation only — allowed
  - status transition with appended `## Historical Note` — allowed
  - new ADR (not in base) — allowed (fresh authorship, no immutability constraint)
  - deleted ADR — fail (immutability includes existence)
  - multiple ADRs in one commit, single trailer covering both — allowed
  - multi-file diff with mixed legal/illegal changes — illegal entries enumerated, exit 1
  - CLI happy path on a real-repo invocation against `HEAD~1`
  - CLI failure exit code = 1 with stderr lines describing each violation
  - The fixture builds tiny synthetic ADRs in a `tmp_path` with `subprocess.run(["git", "init"], …)` — `tests/ci/test_check_adr_immutability.py` becomes the second test file in `tests/ci/` to use a synthetic git repo (the first is `test_check_release_audit.py` per the existing pattern).
- [x] T3 — Added the gate to `.github/workflows/verify.yml` after the `Lint plan completion` step. Implementation chose an event-aware shell branch rather than a single static `--base-ref`: pull-request runs use `--base-ref "origin/${{ github.base_ref }}"` to walk the PR's commit range; push-to-main runs use the push-mode default (HEAD only). The default `actions/checkout@v5` fetch-depth of 1 is too shallow even for a HEAD~ lookup, so `fetch-depth: 0` was added to the checkout step. (One extra step in the existing matrix-of-4 job rather than a separate job; the per-run cost of fetching the full history of a ~150-commit repo is negligible.)
- [x] T4 — Updated `docs/operations/release-playbook.md § Pre-release Checklist`: appended `&& python ci/check_adr_immutability.py` to the existing local-gates one-liner. No structural change.
- [x] T5 — Updated `docs/development-process.md § ADRs` immediately after the immutability sentence at line 82: a one-paragraph addition naming the gate, the three exceptions, the trailer convention (em-dash / en-dash / ASCII hyphen / colon all accepted; comma-separated ADR numbers covered), and a pointer to this plan.
- [x] T6 — Retroactive verdicts (recorded; no history rewriting):

  | SHA | Subject | Gate verdict | Class |
  |---|---|---|---|
  | `bcd2a7a` | docs: update stale v2 deferral language for shipped features | **FAIL** on ADR-0006 | Real body edit; would have been blocked. The "stale v2 deferral language" sweep should have either superseded ADR-0006 or carried `Allow-ADR-edit: 0006 — sweep stale v2 deferrals after the features shipped`. |
  | `b77dfa3` | docs: promote ADR-0020 and ADR-0021 from provisional to accepted | OK | Frontmatter-only status flip. |
  | `5f4a269` | docs: ADR-0020 — release self-bypass for solo maintainer (provisional) | OK | New ADR creation. |
  | `ccb9b45` | docs: graduate ADR-0017/-0018/-0019 from provisional to accepted | OK | Frontmatter-only status flip on three files. |
  | `22e086b` | docs: mark ADR-0017, -0018, -0019 as provisional | **FAIL** on ADR-0017/0018/0019 | Real body edits — the commit added "provisional-rationale callouts pointing at the review trigger" alongside the status downgrade. Would have needed `Allow-ADR-edit: 0017, 0018, 0019 — annotate provisional-status reason` (and arguably should have superseded each instead, since the body claim being added is a substantive "why the original review trigger remains pending" note). |
  | `3ea1d64` | docs: accept hints spec + 3 ADRs (file-drop, boosting, universal inbox) | OK | New ADR creation in the same commit as a spec acceptance. |
  | `048dbfc` | docs: ADR-0026 supersedes ADR-0020 (publish gate is manual approval) | OK | New ADR-0026 creation + frontmatter-only `superseded-by` annotation on ADR-0020. |

  Two of seven commits are real body-edit violations under the new gate (`bcd2a7a` and `22e086b`); the other five are legitimate operations the gate correctly allows. The two violations remain on `main` as historical record. No retro-amendment is performed — immutability is forward-looking and the trailer mechanism becomes available to future maintainers.
- [x] T7 — Completed in follow-up branch `chore/makefile-adr-validator` after PR #42 (contributor-onboarding-makefile) and PR #44 (adr-immutability-gate) both landed on main. Single-line append to `Makefile § validators`: `$(PY) ci/check_adr_immutability.py`. `make validators` now runs all six gates locally; `make gate` propagates. Originally marked `[~]` deferred because this branch's parent (main pre-#42) had no Makefile to extend.
- [x] T8 — `[Unreleased]` § Added entry in `CHANGELOG.md` announces the gate, the three exceptions, and the trailer convention.
- [x] T9 — Add row to `docs/plans/README.md § Shipped` index.
- [x] T10 — Commit on `feat/adr-immutability-gate` branch with message `feat: ci/check_adr_immutability.py — enforce ADR-body immutability`. Body cites this plan, names AGENTS.md / `development-process.md` § ADRs as the spec authority, and notes the trailer convention.

## Acceptance Criteria

- [x] AC1 — `ci/check_adr_immutability.py` exists; importable; CLI honours `--base-ref`, `--head`, and `--repo`. Default base-ref is `None` (push-mode); PR mode opts in.
- [x] AC2 — `tests/ci/test_check_adr_immutability.py` has 16 cases; all pass on first run.
- [x] AC3 — `.github/workflows/verify.yml` invokes the gate after `Lint plan completion`; failure fails the job. `fetch-depth: 0` added to the checkout step so HEAD~ is reachable.
- [x] AC4 — `docs/operations/release-playbook.md § Pre-release Checklist` includes `python ci/check_adr_immutability.py` in the local-gates one-liner.
- [x] AC5 — `docs/development-process.md § ADRs` cross-links to the gate and names the three exceptions.
- [x] AC6 — Retroactive verdict (T6) recorded inline; no history rewrites; two real violations among seven historical commits documented.
- [x] AC7 — `[Unreleased]` § Added in `CHANGELOG.md` announces the gate.
- [x] AC8 — Full local gate passes; the new check on push-mode HEAD reports OK because the only commit on this branch is the gate commit itself, which adds new tests/CI but does not modify any accepted ADR.
- [x] AC9 — `git diff --stat` on the original PR (#44) touched only: this plan, `docs/plans/README.md`, `ci/check_adr_immutability.py` (new), `tests/ci/test_check_adr_immutability.py` (new), `.github/workflows/verify.yml`, `docs/operations/release-playbook.md`, `docs/development-process.md`, `CHANGELOG.md`. The Makefile-validators line was added in the follow-up branch `chore/makefile-adr-validator` once PR #42 had landed (T7 above).

## Out of Scope

- **Locking ADR *frontmatter* fields besides status/date/superseded-by.** The schema is loose by design; locking it would over-constrain future ADR authoring. The body is the load-bearing surface.
- **Auto-generating superseding-ADR scaffolds.** A future helper could prompt "ADR-NNNN is locked — generate ADR-MMMM?" but that's productivity tooling, not enforcement.
- **Retroactively fixing the seven flagged commits.** ADR immutability is a forward-looking guard; rewriting history would itself violate the immutability spirit. T6 produces a verdict log only.
- **Enforcing immutability on plans, design docs, or specs.** Plans are by-design completion records; design docs may evolve with implementation; specs are mutable but governed by their own SDD process. ADRs are the only artifact class with a written immutability invariant.
- **Pre-commit hook integration.** Out of scope. The gate fires in CI; a pre-commit hook is a separate convenience layer addressed (or not) by the contributor-onboarding plan.

## Risk and reversal

- **Risk: false-positive on a status-only frontmatter change.** Mitigation: the algorithm explicitly compares *body* bytes after stripping the frontmatter; status flips alone produce identical bodies.
- **Risk: maintainer hits the gate on a legitimate typo fix and feels the trailer is heavyweight.** Mitigation: the trailer is one line; the alternative (writing a superseding ADR for a typo) is heavier, which is intentional — it forces a moment of consideration. If false-positives recur, a follow-up plan can extend the special-case list (e.g., link-rot fixes where only the URL changes inside an inline-code-quoted markdown link, with the visible text unchanged).
- **Risk: the merge-base computation fails on a force-push or rebased branch.** Mitigation: T1 falls back to `HEAD~1` when `origin/main` lookup fails; failure prints a hint rather than a stack trace.
- **Reversal:** revert the commit. The gate is additive; reversing leaves the existing convention-only state.
