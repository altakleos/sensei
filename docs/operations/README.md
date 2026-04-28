# Operations

Runbooks for operational tasks in this repo. Read the relevant file before running the task — each is self-contained.

| Runbook | Use when |
|---|---|
| [`release-playbook.md`](release-playbook.md) | Cutting a release. Includes the pre-release Tier-2 E2E gate (goal + assess + hints protocols against headless Claude Code), yank procedure, and the manual-approval step required by the `pypi` GitHub Environment per ADR-0026. |
| [`parallel-agents.md`](parallel-agents.md) | Running multiple LLM agents in parallel on independent branches via git worktrees. References the `scripts/worktree-setup.sh` + `scripts/worktree-teardown.sh` helpers. |
| [`context-budget.md`](context-budget.md) | Auditing the token cost of the Sensei boot chain per session. Tier-A / Tier-B / Tier-C breakdown, agent compatibility matrix, re-measurement one-liner. |
| [`shim-validation.md`](shim-validation.md) | Behavioral validation of each tool-specific shim (Cursor, Copilot, Windsurf, Cline, Roo, AI Assistant). Run when claiming a new tool is ✅ Verified. |
| [`backup-recovery.md`](backup-recovery.md) | Backing up and restoring learner data. What to protect, how to recover from corruption, what `sensei upgrade` already handles. |
| [`branch-protection.md`](branch-protection.md) | Recommended GitHub branch protection and tag protection rules for `main`. |

Not every-session reading. Each is load-bearing when its task comes up, and the referring file is the canonical source — don't reconstruct the procedure from memory.
