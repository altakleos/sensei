---
status: provisional
weight: lite
date: 2026-04-21
protocols: []
---
# ADR-0020: Release Self-Bypass for Solo Maintainer

**Decision:** The release-process spec's human-approval invariant is satisfied by GitHub Environment protection rules, even when the sole required reviewer is also the tag pusher and `prevent_self_review` is `false`. In a solo-maintainer project, the maintainer's act of pushing a release tag after completing the pre-release checklist constitutes the approval step.

**Why:** The spec invariant ("Automatic, un-gated publishes are not permitted") was written assuming a multi-reviewer team. With a single maintainer, requiring a second human creates a process bottleneck with no safety gain — the same person would review and approve. The GitHub Environment config (`required_reviewers: [maintainer]`, `prevent_self_review: false`) is intentional, not an oversight. The pre-release checklist in the release playbook provides the verification gate.

**Alternative:** Require a second reviewer for all releases. Rejected because the project currently has a single maintainer, and blocking releases on external availability adds latency without adding safety. When the project gains a second maintainer, this ADR should be revisited.
