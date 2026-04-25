# Operations

Runbooks for operational tasks in this repo. Read the relevant file before running the task — each is self-contained.

| Runbook | Use when |
|---|---|
| [`release-playbook.md`](release-playbook.md) | Cutting a release. Includes the pre-release Tier-2 E2E gate (goal + assess + hints protocols against headless Claude Code), yank procedure, and the self-bypass caveat on the `pypi` GitHub Environment for solo-maintainer releases. |
| [`parallel-agents.md`](parallel-agents.md) | Running multiple LLM agents in parallel on independent branches via git worktrees. References the `scripts/worktree-setup.sh` + `scripts/worktree-teardown.sh` helpers. |
| [`context-budget.md`](context-budget.md) | Auditing the token cost of the Sensei boot chain per session. Tier-A / Tier-B / Tier-C breakdown, agent compatibility matrix, re-measurement one-liner. |
| [`shim-validation.md`](shim-validation.md) | Behavioral validation of each tool-specific shim (Cursor, Copilot, Windsurf, Cline, Roo, AI Assistant). Run when claiming a new tool is ✅ Verified. |

Not every-session reading. Each is load-bearing when its task comes up, and the referring file is the canonical source — don't reconstruct the procedure from memory.
