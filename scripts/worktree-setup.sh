#!/usr/bin/env bash
set -euo pipefail

# Parallel Agent Worktree Setup
# Creates isolated git worktrees for parallel plan execution.
# Usage: scripts/worktree-setup.sh <plan-name> [plan-name ...]

if [ $# -eq 0 ]; then
  echo "Usage: scripts/worktree-setup.sh <plan-name> [plan-name ...]"
  echo "Example: scripts/worktree-setup.sh curriculum-engine interaction-model deep-frontiers"
  exit 1
fi

# Abort if working directory is dirty
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "ERROR: Working directory has uncommitted changes. Commit or stash first."
  exit 1
fi

BASE=$(git rev-parse --short HEAD)
echo "Creating worktrees from $(git branch --show-current) @ $BASE"
echo ""

for PLAN in "$@"; do
  WORKTREE=".worktrees/$PLAN"
  BRANCH="plan/$PLAN"

  if [ -d "$WORKTREE" ]; then
    echo "SKIP: $WORKTREE already exists (branch: $BRANCH)"
    continue
  fi

  # Create branch if it doesn't exist
  if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    echo "WARN: Branch $BRANCH already exists, using it"
    git worktree add "$WORKTREE" "$BRANCH"
  else
    git worktree add "$WORKTREE" -b "$BRANCH"
  fi

  # Install dependencies if pyproject.toml exists
  if [ -f "$WORKTREE/pyproject.toml" ]; then
    (cd "$WORKTREE" && pip install -e . -q 2>/dev/null) || true
  fi

  echo "  OK: $WORKTREE -> branch $BRANCH"
done

echo ""
echo "=== Agent Workspaces Ready ==="
echo ""
for PLAN in "$@"; do
  WORKTREE="$(cd . && pwd)/.worktrees/$PLAN"
  echo "  Agent: open $WORKTREE"
  echo "         branch: plan/$PLAN"
  echo ""
done
echo "When done, run: scripts/worktree-teardown.sh $*"
