# Release Playbook

Operational procedures for releasing Sensei and handling incidents.

The release mechanism and its invariants are documented in the spec [`docs/specs/release-process.md`](../specs/release-process.md), the design [`docs/design/release-workflow.md`](../design/release-workflow.md), and the placement of maintainer tooling in [ADR-0009](../decisions/0009-maintainer-tooling-outside-engine.md). This playbook is the operational runbook maintainers follow to execute those mechanisms.

**Prerequisites before the first real release:** PyPI project registration, PyPI trusted-publisher configuration, GitHub Environment `pypi` setup, and capturing the environment ID below. See `docs/plans/release-workflow.md` § Prerequisites for the exact steps.

## Pre-release gate (manual)

Before tagging any release, run the Tier-2 behavioural E2E on your workstation. CI cannot run this — the LLM CLI tools and auth credentials are workstation-only. The tests auto-detect `claude` or `kiro-cli` on PATH (preferring Claude when both are available). Override with `SENSEI_E2E_TOOL=claude` or `SENSEI_E2E_TOOL=kiro`.

**Agent-driven releases.** If an LLM agent (the same one driving this playbook) is operating inside a Claude Code session — `which claude` returns a path *and* `CLAUDECODE=1` is set in the environment — the agent IS on the maintainer's workstation for purposes of this gate. The agent should run the gate end-to-end (Option B, OAuth flow) without escalating a cost-permission ask: the maintainer's authority to cut a release implies authority to spend the OAuth quota the gate consumes (~$2–4 per release per [ADR-0027](../decisions/0027-tier2-gate-expansion.md)). Mention the spend in the post-run summary, not as a pre-run gate. Genuinely irreversible actions — PyPI publish, force-push to `main`, deleting a published tag — still require explicit confirmation; Tier-2 spend is a budgeted cost, not an irreversible action.

Activate the project venv first — `pyproject.toml` sets `addopts = "--cov=..."`, which requires `pytest-cov` from the dev extras. Without the venv, the system `pytest` will reject `--cov=*` and `--no-cov` alike.

The same discipline applies to **all** local pre-merge gates, not just pytest. CI installs ruff and mypy from the project's dev extras (`pip install -e '.[dev]'`); a system-wide `ruff` or `mypy` on `PATH` may report different lint rules or type errors than CI does, leading to "looks broken locally, merges green in CI" (or the more dangerous inverse). Use `.venv/bin/<tool>` for ruff, mypy, and pytest; `python ci/check_*.py` is fine to run from the system Python because the validators have no version-sensitive dependencies.

```bash
source .venv/bin/activate   # or ./.venv/bin/pytest ... if you prefer not to activate

# The seven-test gate (per ADR-0027). Listing tests explicitly so the
# six nightly-only e2e tests don't fire on the maintainer's workstation.
GATE_TESTS=(
  tests/e2e/test_goal_protocol_e2e.py
  tests/e2e/test_assess_protocol_e2e.py
  tests/e2e/test_hints_protocol_e2e.py
  tests/e2e/test_tutor_protocol_e2e.py
  tests/e2e/test_review_protocol_e2e.py
  tests/e2e/test_reviewer_protocol_e2e.py
  tests/e2e/test_challenger_protocol_e2e.py
)

# Option A (API key):
ANTHROPIC_API_KEY=sk-ant-... pytest "${GATE_TESTS[@]}" -v --no-cov

# Option B (OAuth Claude Code user):
SENSEI_E2E=1 pytest "${GATE_TESTS[@]}" -v --no-cov

# Option C (Kiro CLI):
SENSEI_E2E=1 pytest "${GATE_TESTS[@]}" -v --no-cov
```

`--no-cov` is required because `pytest-cov` would otherwise fail the threshold on a single-test invocation whose coverage surface is tiny.

Expected: all seven Tier-2 tests pass — the headless LLM agent (Claude Code or Kiro) reads `AGENTS.md`, dispatches to the named protocol, and emits the expected artifact:

- `test_goal_protocol_produces_schema_valid_goal` — dispatches to `goal`, writes a schema-valid goal file to `learner/goals/`.
- `test_assess_protocol_updates_profile_with_attempts` — dispatches to `assess`, increments `attempts` and `correct` in `learner/profile.yaml` for a pre-seeded topic.
- `test_hints_protocol_drains_inbox_and_populates_registry` — dispatches to `hints` triage on a pre-seeded inbox, registers entries into `learner/hints/hints.yaml` and drains `learner/inbox/`.
- `test_tutor_protocol_updates_profile_after_teaching` — dispatches to `tutor`, runs one explain → probe → classify → update cycle on a pre-seeded untaught topic; profile's `attempts` field bumps and the file still validates.
- `test_review_protocol_updates_stale_topic_timestamp` — dispatches to `review`, picks up a stale topic per the spaced-repetition queue and refreshes its `last_seen` timestamp.
- `test_reviewer_protocol_reviews_solution_and_updates_profile` — dispatches to `reviewer` against a submitted solution; profile is updated with the review's verdict.
- `test_challenger_protocol_pushes_limits_and_updates_profile` — dispatches to `challenger`; learner's profile reflects the productive-failure interaction.

Each run takes ~60–120s on a cold Claude Code cache; seven tests is ~12–14 minutes total (per [ADR-0027](../decisions/0027-tier2-gate-expansion.md), expanded from the previous 3-test / ~5-minute gate to close the breadth gap surfaced in the 2026-04-25 follow-up audit). A red result means either a protocol prose regression or a schema drift. **Do not tag** until the gate is green.

Skip only with an explicit CHANGELOG note recording why (e.g. upstream Claude Code outage).

Capture the gate's output (or a summary plus the transcript sha256) to `docs/operations/releases/<tag>.md` per the template at [`docs/operations/releases/README.md`](releases/README.md). Commit alongside the release tag. Without this artifact, "did the gate run?" is unverifiable after the fact — the maintainer who could miss running the gate is the same one trusted to confirm it ran.

## Tier-3 Nightly E2E

The `e2e-nightly` GitHub Actions workflow runs all E2E tests on a daily schedule (06:00 UTC). Results appear in the Actions tab. The workflow can also be triggered manually via `workflow_dispatch` with an optional `tool` input (`auto`/`claude`/`kiro`).

**Required secret:** `ANTHROPIC_API_KEY` in the repository's Actions secrets. Without it, the Claude Code install step is skipped and `agent_runner` auto-detection finds no tool — tests skip gracefully.

**Cost cap:** 30-minute job timeout + 300s per-test timeout via `pytest --timeout`. At ~2 minutes per test, a full run takes ~6–18 minutes of API time depending on test count.

## Normal Release

1. Ensure `main` is green (CI verified across Python 3.10–3.13).
2. Tag a semver release from `main`:
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```
3. The `release.yml` workflow triggers. It:
   - Runs the full verify gate (pytest + smoke test + wheel build + package-contents check)
   - Pauses on the `pypi` GitHub Environment for your manual approval
   - On approval, publishes wheel + sdist to PyPI via OIDC trusted publishing
4. Verify the release is live:
   ```bash
   pip index versions sensei-tutor
   ```
5. Create a GitHub Release. Body is the `CHANGELOG.md` section for `vX.Y.Z` verbatim plus a `pip install sensei-tutor==X.Y.Z` install hint. Per [docs/specs/release-communication.md](../specs/release-communication.md), the changelog is the canonical "what changed" artifact; the Release is a derived view.

**Tag patterns the workflow matches:** `v1.2.3`, `v0.1.0-alpha`, `v0.1.0-rc.1`, `v0.1.0a1`, `v0.1.0b2`.

## Pre-release (alpha / beta / rc)

Same flow as normal release with a prerelease suffix:

```bash
git tag v0.2.0-alpha
git push origin v0.2.0-alpha
```

Users must pass `--pre` to pip to install prereleases:

```bash
pip install sensei-tutor --pre
```

## Yanking a Bad Release

A **yank** hides a release from `pip install sensei-tutor` (without a pinned version) but leaves it installable for anyone who pinned to that specific version. Yank when a release has a correctness bug but is not actively harmful.

1. Log in to PyPI: https://pypi.org/manage/project/sensei-tutor/releases/
2. Find the release, click **Options → Yank**
3. Enter a short reason (shown to users who pinned to the yanked version)
4. Confirm
5. Amend `CHANGELOG.md` in a follow-up commit: append `**Yanked:** <reason, link to fix version>` under the yanked release's heading. Per `docs/specs/release-communication.md`, the entry itself is **never deleted** — yanking hides the version from unpinned installs, so anyone who pinned it deserves to find an explanation in the changelog.

**When to yank vs delete:** Always yank first. Delete only if the release contains secrets or malicious code (deletion is permanent and breaks anyone with a pinned version). PyPI does not allow re-uploading a deleted version.

## Issuing a Patch

After yanking (or instead of yanking for quick fixes):

1. Fix on `main` via a normal PR (follow the layer stack in `AGENTS.md`).
2. Bump the version in `src/sensei/__init__.py`:
   ```python
   __version__ = "0.1.2"  # was 0.1.1
   ```
3. Commit, tag, push — same flow as Normal Release.
4. If the previous release was yanked, optionally update the yank message to point at the fix version.

## Incident Response

### Release workflow failed before publish

The `verify` job failed. Fix the failure, push a new commit to main, delete the bad tag, re-tag:

```bash
git tag -d v0.1.1                 # delete local
git push origin :v0.1.1           # delete remote
# ... fix and push to main ...
git tag v0.1.1
git push origin v0.1.1
```

### Release workflow failed at publish step

- Check the Actions UI for the specific error.
- Common causes:
  - PyPI trusted publisher not configured → configure at https://pypi.org/manage/account/publishing/ and re-run the workflow
  - Environment `pypi` not approved → click **Review deployments** in the Actions UI
  - Version already exists on PyPI → PyPI forbids re-uploading the same version; bump and re-tag
- The workflow is idempotent: re-running after a transient failure is safe because PyPI refuses duplicate uploads rather than creating conflicts.

### Corrupt wheel discovered in production

1. **Yank immediately** (see Yanking a Bad Release above).
2. Fix, bump version, release as a patch.
3. Announce on the GitHub Release page for the yanked version — link to the fix.

### PyPI account compromised

1. Reset PyPI password and 2FA from a clean device.
2. Review trusted publishers: https://pypi.org/manage/project/sensei-tutor/settings/publishing/ — remove any unfamiliar entries.
3. Review PyPI account activity for unauthorized publishes. Yank anything unauthorized.
4. Rotate any GitHub personal access tokens.
5. Open a GitHub issue or security advisory to disclose.

## Upgrade Cleanup

`sensei upgrade` should sweep stale `.sensei.old.*` and `tmp*` directories from a prior interrupted run on every invocation. No manual cleanup is needed after a SIGKILL'd upgrade — the next `sensei upgrade` run (including an "already up to date" no-op) reclaims them automatically.

*Implemented in v0.1.0a10. The cleanup runs automatically on every `sensei upgrade` invocation.*

## Rollback: Users on a Bad Version

A user who installed a bad release can downgrade:

```bash
pip install 'sensei-tutor==0.1.0' --force-reinstall --pre
```

Their `.sensei/` directory was left untouched by the bad CLI (per upgrade atomicity, ADR-0004), so their instance content is intact. If they ran `sensei upgrade` mid-flight on a broken version, the atomic-swap guarantees the previous `.sensei/` is preserved.

## Pre-release Checklist

Before tagging:

- [ ] CI green on `main`
- [ ] `CHANGELOG.md` `## [Unreleased]` section promoted to `vX.Y.Z` with today's date (per [docs/specs/release-communication.md](../specs/release-communication.md) — `ci/check_package_contents.py` rejects the build if this is missing)
- [ ] `CHANGELOG.md` reference-link tail updated for the new tag — add `[X.Y.Z]: …compare/v<prev>...vX.Y.Z` and bump `[Unreleased]:` to compare from `vX.Y.Z...HEAD` (`ci/check_changelog_links.py` enforces)
- [ ] Version bumped in `src/sensei/__init__.py`
- [ ] `docs/plans/` has no `status: in-progress` plans that should block
- [ ] Local pre-merge gates pass — run **from the project venv** (`.venv/bin/pytest && .venv/bin/ruff check . && .venv/bin/mypy && python ci/check_foundations.py && python ci/check_links.py && python ci/check_plan_completion.py`). System-wide `ruff`/`mypy`/`pytest` may disagree with CI; the venv version is the source of truth.
- [ ] Tier-2 E2E run captured to `docs/operations/releases/v<X.Y.Z>.md` per the template at [`docs/operations/releases/README.md`](releases/README.md). **CI-enforced** by `ci/check_release_audit.py` in `release.yml`'s `build-and-check` job (per [ADR-0024](../decisions/0024-release-audit-log-required.md)) — a missing or malformed log file fails the build before publish.
- [ ] `python -m build && python ci/check_package_contents.py --wheel dist/*.whl --tag vX.Y.Z` passes
- [ ] GitHub Environment `pypi` reviewers still exist and are reachable

## Approving PyPI Publish from the Terminal

The `pypi` GitHub Environment is configured with a `required_reviewers` protection rule. After every release tag push, the `publish` job pauses until the maintainer explicitly approves the deployment — this is the human approval gate that `docs/specs/release-process.md` requires. Per [ADR-0026](../decisions/0026-publish-gate-manual-approval.md), the maintainer's `gh api` approval call below is the canonical step that satisfies the spec invariant.

```bash
# Find the run ID for the release
gh run list --workflow=release.yml --limit 3

# Confirm the deployment is waiting (returns a non-empty list)
gh api repos/altakleos/sensei/actions/runs/<RUN_ID>/pending_deployments

# Resolve the pypi environment's numeric id by name (don't hardcode it —
# recreating the environment changes the id, but the name `pypi` is stable).
ENV_ID=$(gh api repos/altakleos/sensei/environments/pypi --jq '.id')

# Approve
gh api repos/altakleos/sensei/actions/runs/<RUN_ID>/pending_deployments \
  --method POST \
  --field "environment_ids[]=$ENV_ID" \
  --field 'state=approved' \
  --field 'comment=Ship it'
```

GitHub-environment ids are stable across runs but tied to GitHub-account state — recreating the `pypi` environment (account migration, accidental delete + recreate, security rotation) changes the id. Resolving by the environment name is therefore the canonical pattern; the hardcoded literal that appears in [ADR-0026](../decisions/0026-publish-gate-manual-approval.md)'s body was the v0.1.0a20-empirical witness and is preserved there as historical record (ADR bodies are immutable). If `gh api repos/altakleos/sensei/environments/pypi` returns 404, the environment was deleted or renamed — re-run [`docs/plans/release-workflow.md`](../plans/release-workflow.md) § Prerequisites to recreate it.

You can also approve through the GitHub UI: open the workflow run, click **Review deployments**, check the `pypi` environment, click **Approve and deploy**.

### Historical note (superseded)

[ADR-0020](../decisions/0020-release-self-bypass.md) previously claimed that `prevent_self_review: false` plus a self-pushed tag caused the gate to auto-bypass without pausing. Empirical behaviour during the v0.1.0a20 release (and the GH Environment configuration probed at the same time) showed the gate does pause and `gh api` approval is required. ADR-0020 is `superseded` by ADR-0026; the v0.1.0a9 anecdote in the original ADR text is preserved there as archaeology, not as current behaviour.

If a future maintainer wants the gate to *actually* auto-bypass for self-pushed tags, the configuration paths to consider are: removing the `required_reviewers` rule entirely, switching to a deploy-bot reviewer that auto-approves on tag push, or accepting the speed bump as-is. ADR-0026 chose the third option.

## References

- Release process spec: [docs/specs/release-process.md](../specs/release-process.md)
- Release communication spec: [docs/specs/release-communication.md](../specs/release-communication.md)
- Release workflow design: [docs/design/release-workflow.md](../design/release-workflow.md)
- Release plan (prerequisites + acceptance criteria): [docs/plans/release-workflow.md](../plans/release-workflow.md)
- Distribution ADR: [docs/decisions/0004-sensei-distribution-model.md](../decisions/0004-sensei-distribution-model.md)
- Maintainer-tooling location ADR: [docs/decisions/0009-maintainer-tooling-outside-engine.md](../decisions/0009-maintainer-tooling-outside-engine.md)
- Release workflow file: [.github/workflows/release.yml](../../.github/workflows/release.yml)
- Package-contents validator: [ci/check_package_contents.py](../../ci/check_package_contents.py)
- PyPI yank documentation: https://pypi.org/help/#yanked
