---
status: accepted
weight: lite
date: 2026-04-25
protocols: []
---
# ADR-0024: Release Audit Log Is a CI-Enforced Gate

**Decision:** `release.yml`'s `build-and-check` job fails when `docs/operations/releases/<tag>.md` is missing, has malformed frontmatter, reports a non-zero `exit_code`, or omits any required field (`tag`, `date`, `tester`, `tool`, `tool_version`, `exit_code`, `transcript_hash`). Enforcement lives in a new sibling validator, `ci/check_release_audit.py`, wired in immediately after `check_package_contents.py`. Pre-template releases (`v0.1.0a1`–`v0.1.0a19`) are out of scope; the gate fires from the next tag forward.

**Why:** Commit cfd354c landed the audit-log template, but `release.yml` did not require the file to exist before publishing — a maintainer who skipped both the workstation-only Tier-2 gate and its log produced an unobservably-broken release. ADR-0020 (self-bypass for solo maintainer) accepts the no-second-reviewer trade-off at the publish step; the analogous gap one step earlier (the gate itself) had no committed artifact. CI-checking the artifact closes that loop without re-opening ADR-0020 — the bypass still stands, but its evidence trail is now machine-checked.

**Alternative:** Leave the audit log advisory and rely on the maintainer's pre-release checklist. Rejected because the same maintainer who could miss running the Tier-2 gate is the one trusted to confirm it ran; an honor-system artifact closes nothing the checklist did not already promise. Extending `ci/check_package_contents.py` instead of adding a sibling validator was also considered and rejected — the wheel-contents check and the audit-log check have different concerns (bundle integrity vs. release-evidence trail) and different failure modes; collapsing them obscures both.
