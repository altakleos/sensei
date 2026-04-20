# Parallel Agent Execution — Runbook

How to run multiple LLM agents implementing different plans simultaneously.

## When to Use

When the plan index (`docs/plans/README.md`) declares plans as parallelizable:
```
Plans 2, 3, 4 can run in parallel
```

## Setup

```bash
scripts/worktree-setup.sh curriculum-engine interaction-model deep-frontiers
```

This creates:
- `.worktrees/curriculum-engine/` on branch `plan/curriculum-engine`
- `.worktrees/interaction-model/` on branch `plan/interaction-model`
- `.worktrees/deep-frontiers/` on branch `plan/deep-frontiers`

## Launch Agents

Open each worktree directory in a separate LLM agent session:

| Agent Session | Directory | Instruction |
|---------------|-----------|-------------|
| Terminal 1 | `.worktrees/curriculum-engine/` | "Execute docs/plans/curriculum-engine.md" |
| Terminal 2 | `.worktrees/interaction-model/` | "Execute docs/plans/interaction-model.md" |
| Terminal 3 | `.worktrees/deep-frontiers/` | "Execute docs/plans/deep-frontiers-principles.md" |

Each agent sees a normal git repo. No special instructions needed.

## Integration

When all agents finish, merge back (smallest changes first):

```bash
scripts/worktree-teardown.sh deep-frontiers interaction-model curriculum-engine
```

The script merges each branch sequentially, running tests after each merge.

### CHANGELOG.md Conflicts

All plans append to `## [Unreleased]`. Git cannot auto-merge appends to the same section. Resolution: keep all entries. This takes 30 seconds per conflict.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Working directory has uncommitted changes" | Commit or stash before setup |
| Worktree already exists | Script skips it; remove manually with `git worktree remove .worktrees/<name>` |
| Merge conflict during teardown | Resolve manually, `git merge --continue`, re-run teardown for remaining plans |
| Tests fail after merge | Fix the issue in the main checkout, commit, re-run teardown |
| Agent can't find dependencies | Run `pip install -e .` inside the worktree directory |
