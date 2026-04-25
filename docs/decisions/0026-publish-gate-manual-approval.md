---
status: accepted
weight: lite
date: 2026-04-25
protocols: []
supersedes: 0020
---
# ADR-0026: Publish Gate Is a Manual Approval (Supersedes ADR-0020)

**Decision:** The `pypi` GitHub Environment's `required_reviewers` rule pauses the `publish` job until the maintainer explicitly approves via `gh api repos/altakleos/sensei/actions/runs/<RUN_ID>/pending_deployments --method POST --field 'environment_ids[]=14342694313' --field 'state=approved'` (or the GitHub UI equivalent). That approval call is the canonical step that satisfies the `release-process.md` spec invariant "Automatic, un-gated publishes are not permitted." ADR-0020's "self-bypass" interpretation is superseded.

**Why:** v0.1.0a20 was the first release fully driven through CI from a clean main with the agent-driven Tier-2 clause active. The publish job paused; `gh api .../pending_deployments` returned a non-empty list with `current_user_can_approve: true`; the workflow advanced only after an explicit `state=approved` POST. ADR-0020's claim — that `prevent_self_review: false` plus self-pushed tags auto-bypasses the rule — does not match this empirical behaviour. Either GitHub's environment-protection semantics changed since 2026-04-21 or ADR-0020's analysis was wrong from the start; either way, the docs must reconcile to observed reality. The spec invariant survives intact and is now more obviously satisfied: the gate genuinely pauses, the maintainer genuinely approves.

**Alternative:** Reconfigure the environment to actually auto-approve (e.g., remove the `required_reviewers` rule, or add a deploy-bot reviewer that auto-approves on tag push). Rejected because the current pause is a real speed bump — the maintainer reviews the run's previous-step output (Tier-2 audit-log gate, package-contents check, pytest matrix) before approving — and adds latency-only-not-safety risk if removed. Manual approval is fast (~5 seconds via `gh api`), aligns with how every other reviewer-protected GitHub Environment behaves, and removes the cognitive overhead of "is the bypass active or not?" that ADR-0020 carried.
