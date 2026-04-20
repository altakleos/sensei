---
status: accepted
date: 2026-04-20
---
# ADR-0016: Git Worktrees for Multi-Agent Filesystem Isolation

## Context

Sensei's development process declares inter-plan parallelism (Plans 2, 3, 4 can run in parallel after Plan 1). However, executing this parallelism is currently impossible because all LLM agents share a single git checkout. When two agents operate in the same working directory: (a) one agent's branch creation changes the other's HEAD, (b) uncommitted changes from one agent appear in the other's git status, (c) neither agent can determine which changes are theirs to commit.

The 2025-2026 LLM agent ecosystem has converged on git worktrees as the standard isolation mechanism (Claude Code --worktree flag, Cursor 3 /worktree command, CAID paper from CMU, Claudio, multiclaude, agent-worktree). Research (CAID, CMU March 2026) demonstrates that instruction-only isolation (telling agents not to touch certain files) actually hurts performance vs single-agent (55.5% vs 57.2%), while worktree isolation improves to 63.3%.

## Decision

Use git worktrees contained within the project directory at `.worktrees/` (gitignored) to provide filesystem isolation for parallel LLM agents. Each agent gets its own worktree on a dedicated branch (`plan/<name>`). Integration is sequential (one merge at a time) with verification gates between merges. Two shell scripts (`worktree-setup.sh`, `worktree-teardown.sh`) manage the lifecycle. The human orchestrator decides when to create worktrees, which plans to parallelize, and resolves any merge conflicts during integration.

## Alternatives Considered

1. **Separate git clones** (`git clone . ../sensei-agent-1`). Full isolation but: duplicates the entire .git history (wasteful for large repos), creates independent remotes requiring push/pull ceremony for integration, pollutes the parent directory, and branches created in one clone are not visible in others without fetching. Worktrees share the object store, making branches instantly visible for merging.

2. **Docker containers per agent.** Maximum isolation (separate filesystem, network, processes) but: massive overhead for a CLI project with pytest, requires Docker installation and configuration, credential forwarding for git, and LLM agent tools (Claude Code, Cursor, Kiro) are not designed to operate inside containers. Solves a problem (environment isolation) that doesn't exist here.

3. **Branch-only workflow (no filesystem isolation).** Each agent creates its own branch but shares the working directory. Does NOT solve the problem: `git checkout -b` changes HEAD for all processes sharing the directory, uncommitted changes are visible to all agents, and `git add .` captures files from other agents. This is the current broken state.

4. **Lock-based serialization.** Agents acquire a lock before committing, pull before commit. Kills parallelism entirely (agents block on each other). Doesn't solve the uncommitted-changes visibility problem. Incompatible with how LLM agents operate (they don't support external lock protocols).

5. **Worktrees in sibling directories** (`../sensei-agent-1/`). Functionally equivalent to the chosen approach but pollutes the parent directory. The community (Claude Code, Claudio, Giselle) has converged on worktrees inside the project (`.worktrees/`, `.claude/worktrees/`, `.claudio/worktrees/`) for containment.

## Consequences

- Plans declared as parallelizable can now be executed simultaneously by separate agents.
- Each worktree is a full working copy of tracked files, multiplying disk usage by the number of parallel agents. For Sensei (~small repo), this is negligible.
- Agents must not run concurrent git operations that modify shared metadata (refs, objects). The sequential integration workflow prevents this during the merge phase; during parallel execution, agents only commit to their own branches (safe).
- The `.worktrees/` directory must be added to `.gitignore`. Forgetting this causes worktree contents to appear as untracked files.
- Each worktree requires its own dependency installation (`pip install -e .`). The setup script handles this.
- The approach is tool-agnostic: any LLM agent that operates on a filesystem works in a worktree without modification.
- Future enhancement: if the pattern proves valuable, a `sensei parallel` CLI command could automate the workflow. For now, shell scripts are sufficient and transparent.
