# Release Playbook

Operational procedures for releasing Sensei and handling incidents.

The release mechanism and its invariants are documented in the spec [`docs/specs/release-process.md`](../specs/release-process.md), the design [`docs/design/release-workflow.md`](../design/release-workflow.md), and the placement of maintainer tooling in [ADR-0009](../decisions/0009-maintainer-tooling-outside-engine.md). This playbook is the operational runbook maintainers follow to execute those mechanisms.

**Prerequisites before the first real release:** PyPI project registration, PyPI trusted-publisher configuration, GitHub Environment `pypi` setup, and capturing the environment ID below. See `docs/plans/release-workflow.md` § Prerequisites for the exact steps.

## Pre-release gate (manual)

Before tagging any release, run the Tier-2 behavioural E2E on your workstation. CI cannot run this — the LLM CLI tools and auth credentials are workstation-only. The tests auto-detect `claude` or `kiro-cli` on PATH (preferring Claude when both are available). Override with `SENSEI_E2E_TOOL=claude` or `SENSEI_E2E_TOOL=kiro`.

**Agent-driven releases.** If an LLM agent (the same one driving this playbook) is operating inside a Claude Code session — `which claude` returns a path *and* `CLAUDECODE=1` is set in the environment — the agent IS on the maintainer's workstation for purposes of this gate. The agent should run the gate end-to-end (Option B, OAuth flow) without escalating a cost-permission ask: the maintainer's authority to cut a release implies authority to spend the OAuth quota the gate consumes (~$1–3 per release). Mention the spend in the post-run summary, not as a pre-run gate. Genuinely irreversible actions — PyPI publish, force-push to `main`, deleting a published tag — still require explicit confirmation; Tier-2 spend is a budgeted cost, not an irreversible action.

Activate the project venv first — `pyproject.toml` sets `addopts = "--cov=..."`, which requires `pytest-cov` from the dev extras. Without the venv, the system `pytest` will reject `--cov=*` and `--no-cov` alike.

The same discipline applies to **all** local pre-merge gates, not just pytest. CI installs ruff and mypy from the project's dev extras (`pip install -e '.[dev]'`); a system-wide `ruff` or `mypy` on `PATH` may report different lint rules or type errors than CI does, leading to "looks broken locally, merges green in CI" (or the more dangerous inverse). Use `.venv/bin/<tool>` for ruff, mypy, and pytest; `python ci/check_*.py` is fine to run from the system Python because the validators have no version-sensitive dependencies.

```bash
source .venv/bin/activate   # or ./.venv/bin/pytest ... if you prefer not to activate

# Option A (API key):
ANTHROPIC_API_KEY=sk-ant-... pytest tests/e2e/ -v --no-cov

# Option B (OAuth Claude Code user):
SENSEI_E2E=1 pytest tests/e2e/ -v --no-cov

# Option C (Kiro CLI):
SENSEI_E2E=1 pytest tests/e2e/ -v --no-cov
```

`--no-cov` is required because `pytest-cov` would otherwise fail the threshold on a single-test invocation whose coverage surface is tiny.

Expected: all three Tier-2 tests pass — the headless LLM agent (Claude Code or Kiro) reads `AGENTS.md`, dispatches to the named protocol, and emits the expected artifact:

- `test_goal_protocol_produces_schema_valid_goal` — dispatches to `goal`, writes a schema-valid goal file to `learner/goals/`.
- `test_assess_protocol_updates_profile_with_attempts` — dispatches to `assess`, increments `attempts` and `correct` in `learner/profile.yaml` for a pre-seeded topic.
- `test_hints_protocol_drains_inbox_and_populates_registry` — dispatches to `hints` triage on a pre-seeded inbox, registers entries into `learner/hints/hints.yaml` and drains `learner/inbox/`.

Each run takes ~60–120s on a cold Claude Code cache; three tests is ~4–6 minutes total. A red result means either a protocol prose regression or a schema drift. **Do not tag** until the gate is green.

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

The `pypi` GitHub Environment is configured with a `required_reviewers` protection rule. For a **solo-maintainer release** the gate currently **self-bypasses** and the publish step runs without pausing. See § "Self-bypass caveat" below before assuming the approval command is necessary.

```bash
# Find the run ID for the release
gh run list --workflow=release.yml --limit 3

# Check pending deployment (confirms it's waiting)
gh api repos/altakleos/sensei/actions/runs/<RUN_ID>/pending_deployments

# Approve (only reachable when the gate actually pauses — see caveat below)
gh api repos/altakleos/sensei/actions/runs/<RUN_ID>/pending_deployments \
  --method POST \
  --field 'environment_ids[]=14342694313' \
  --field 'state=approved' \
  --field 'comment=Ship it'
```

The environment ID `14342694313` is stable — the `pypi` environment in `altakleos/sensei`. Only the run ID changes per release.

### Self-bypass caveat

The `pypi` environment's `required_reviewers` rule lists exactly one reviewer (`makutaku`) and has `prevent_self_review: false`. GitHub Environments auto-approve a deployment when the initiator is also the sole reviewer and self-review is allowed — so when the maintainer pushes a release tag from their own credentials, the `publish` job runs immediately without pausing, and `pending_deployments` returns an empty list.

Discovered during the v0.1.0a9 release: the entire release workflow (verify matrix + build + publish) completed in 1m9s with zero manual approval step. PyPI received the artifact as designed.

This is not a defect — it is how the environment is configured. If you want the gate to be a real pause for self-triggered releases, choose one of:

1. **Add a co-reviewer** to the `pypi` environment (teammate, bot account, or personal secondary account).
2. **Set `prevent_self_review: true`** in the environment's required-reviewers protection rule. Your own tag pushes will then pause for a second reviewer to approve.
3. **Set `can_admins_bypass: false`** on the environment to prevent admin bypass as well, if you want the rule to apply even to org-admin actions.

Until one of the above is configured, treat the documented approval flow above as applicable only to deployments triggered by someone other than the sole reviewer (e.g. a future contributor's release push), or as a dry-run reference.

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
