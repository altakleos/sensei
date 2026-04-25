# Release Audit Trail

Per-release log files capturing the Tier-2 behavioural E2E pre-release gate output. The gate runs on the maintainer's workstation only — see [`docs/operations/release-playbook.md`](../release-playbook.md) § Pre-release gate. Without a committed artifact, "did the gate run?" is a question only the maintainer can answer, and the same maintainer who could miss running the gate is the one being trusted to confirm it ran. These files close that loop.

The audit trail is forward-looking. v0.1.0a19 and earlier releases predate this directory and have no log file — no recorded Tier-2 output exists to backfill from.

## File Naming

`<tag>.md`, e.g. `v0.1.0a20.md`. One file per shipped tag. Files are committed to `main` alongside or shortly after the release tag.

## Template

Copy this when cutting a release:

```markdown
---
tag: vX.Y.Z
date: YYYY-MM-DD
tester: <github-handle>
tool: claude | kiro | (other)
tool_version: <version-string-from-CLI-or-API>
exit_code: 0
transcript_hash: <sha256 of pytest stdout, or "n/a" if discarded>
---
# Release vX.Y.Z — Tier-2 E2E Audit Log

## Invocation

```bash
# Exact command run, including env vars
.venv/bin/pytest tests/e2e/ -v --no-cov
```

## Result

`N passed, M skipped` (or describe failure mode + recovery).

Tests covered (per release-playbook § Pre-release gate):

- `test_goal_protocol_produces_schema_valid_goal` — pass | fail
- `test_assess_protocol_updates_profile_with_attempts` — pass | fail
- `test_hints_protocol_drains_inbox_and_populates_registry` — pass | fail

## Notes

(Optional. Anything anomalous: flaky run, retry, manual intervention, transcript-fixture drift caught at this gate, time taken if substantially more than the documented ~4–6 minutes, etc.)
```

## Required Fields

| Field | Why |
|---|---|
| `tag` | Pins the artifact to a release. |
| `date` | When the gate actually ran (UTC date is fine — exact time not required). |
| `tester` | Sole-maintainer or future-co-maintainer ownership. |
| `tool` | The Tier-2 gate auto-detects `claude` vs `kiro-cli`; recording which actually ran is load-bearing for ADR-0003 conformance. |
| `tool_version` | Catches the case where a CLI silently shipped a behavioural regression between releases. |
| `exit_code` | The gate's verdict. `0` only. |
| `transcript_hash` | sha256 of the pytest stdout (or `n/a` if not captured). Lets a future investigator confirm the recorded output matches what was run. |

## Index

(empty — first entry lands with the next release)
