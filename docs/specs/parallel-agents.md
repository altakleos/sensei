---
status: draft
date: 2026-04-20
serves: []
realizes: []
stressed_by: []
---
# Parallel Agent Execution

## Intent

Sensei's development process supports multiple LLM agents implementing different plans simultaneously. Each agent operates in filesystem isolation so that one agent's git operations, uncommitted changes, and branch state never interfere with another agent's work. The isolation mechanism is transparent to agents — each agent sees a normal git repository and follows the standard boot chain (AGENTS.md → engine.md → protocols).

## Invariants

1. **Filesystem isolation.** Each agent operates in its own working directory with its own branch. Changes in one agent's workspace are invisible to other agents until explicitly integrated.

2. **Commit attribution.** Each agent's commits contain only the files that agent modified. No agent commits work performed by another agent.

3. **Boot chain integrity.** Every agent workspace contains the full project context (AGENTS.md, engine.md, specs, designs, plans). An agent in an isolated workspace behaves identically to an agent in the main checkout.

4. **Sequential integration.** After parallel agents complete, their work integrates into the target branch one branch at a time, with verification between each integration step. Cross-reference integrity (check_foundations.py, test suite) is validated after each merge.

5. **Workspace containment.** All agent workspaces reside within the project directory structure. Parallel execution does not create artifacts outside the project root.

6. **Conflict-free by design.** Plans declared as parallelizable have disjoint write sets — no two parallel plans modify the same file. Shared accumulation files (CHANGELOG.md) are handled during integration, not during parallel execution.

7. **Agent-agnostic.** The isolation mechanism works with any LLM agent that operates on a filesystem and uses git (Claude Code, Cursor, Kiro, Copilot, Aider). No agent-specific modifications are required.

8. **Graceful degradation.** If isolation is not set up, agents still function correctly in sequential mode. Parallel execution is opt-in, not required.

## Rationale

Currently, two agents cannot implement different plans simultaneously because they share a single working directory. One agent's branch creation changes the other's HEAD. Uncommitted changes from one agent appear in the other's git status. Neither agent can reliably determine which changes are theirs to commit. This blocks the declared inter-plan parallelism (Plans 2, 3, 4 can run in parallel) from being executed.

Research (CAID, CMU 2026) demonstrates that filesystem isolation via git worktrees produces 63.3% task completion vs 55.5% with instruction-only isolation — confirming that physical isolation is necessary, not just helpful.

## Out of Scope

- Intra-plan task parallelism (splitting one plan across multiple agents)
- Automated orchestration (a process that spawns and monitors agents)
- Inter-agent communication during execution
- Conflict resolution automation (semantic conflicts require human judgment)
- Agent-specific tool integrations (Claude Code --worktree flag, Cursor /worktree command)

## Decisions

None yet — ADR to follow.
