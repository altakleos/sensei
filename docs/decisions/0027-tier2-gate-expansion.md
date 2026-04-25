---
status: accepted
weight: lite
date: 2026-04-25
protocols: []
---
# ADR-0027: Pre-Release Tier-2 Gate Covers Seven Protocols

**Decision:** The workstation-only Tier-2 E2E gate documented in `docs/operations/release-playbook.md` § Pre-release gate covers seven test files exercising seven protocols: `tests/e2e/test_{goal,assess,hints,tutor,review,reviewer,challenger}_protocol_e2e.py`. The remaining six nightly tests (`mode_transition`, `mastery_calibration`, `goal_lifecycle`, `decompose_trigger`, `insert_trigger`, `skip_trigger`) stay in the Tier-3 nightly job (`e2e-nightly.yml`). Wall-time budget rises from ~5 minutes to ~12-14 minutes; OAuth cost (Option B) from ~$1-3 to ~$2-4 per release.

**Why:** The 2026-04-25 follow-up audit named the 3-protocol gate as the next weakest link once ADR-0024 made the audit log mandatory: the artifact is now machine-checked but the gate's breadth covers only ~27% of the protocols a learner exercises in a normal session. ADR-0024's pattern was "machine-check the artifact, trust the maintainer for breadth"; the failure mode is that a single maintainer cutting daily releases cannot reliably extrapolate behavioral health from three tests. Expanding to seven captures the four conversational protocols (`tutor`, `review`, `reviewer`, `challenger`) that drive the bulk of a session's behavioural surface. The six excluded tests are interaction-pattern tests that overlap with the gated protocol tests — `goal_lifecycle` exercises decay paths `goal` already invokes; `mode_transition` exercises the same prose as the four mode-named tests — so including them would compound cost without uniquely covering a protocol.

**Alternative:** Keep the gate at three protocols and rely on the Tier-3 nightly workflow for breadth. Rejected because nightly green-status freshness is unenforced — a same-day release after a same-day breakage on a non-gated protocol ships uncaught. The audit-log gate requires `transcript_hash` proof that the *gate* ran, not that nightly was green; tying release to nightly would require a new dependency between two GitHub Actions workflows that today are independent. Cheaper to widen the gate the maintainer already runs.
