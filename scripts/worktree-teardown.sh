#!/usr/bin/env bash
set -euo pipefail

# Parallel Agent Worktree Teardown
# Merges agent branches sequentially with verification, then cleans up.
# Usage: scripts/worktree-teardown.sh <plan-name> [plan-name ...]
# Merge order = argument order. Recommend: smallest changes first.

if [ $# -eq 0 ]; then
  echo "Usage: scripts/worktree-teardown.sh <plan-name> [plan-name ...]"
  echo "Merge order = argument order. Smallest changes first recommended."
  exit 1
fi

for PLAN in "$@"; do
  BRANCH="plan/$PLAN"
  WORKTREE=".worktrees/$PLAN"

  echo "--- Merging $BRANCH ---"

  # Merge
  if ! git merge "$BRANCH" --no-edit 2>/dev/null; then
    echo ""
    echo "CONFLICT merging $BRANCH. Conflicting files:"
    git diff --name-only --diff-filter=U
    echo ""
    echo "HINT: For CHANGELOG.md conflicts, keep all entries under [Unreleased]."
    echo "Resolve conflicts, then run: git merge --continue"
    echo "Remaining worktrees left intact for manual teardown."
    exit 1
  fi

  # Verify — find pytest in venv or PATH
  echo "  Verifying..."
  PYTEST=""
  if [ -f ".venv/bin/pytest" ]; then
    PYTEST=".venv/bin/pytest"
  elif command -v pytest &>/dev/null; then
    PYTEST="pytest"
  fi

  if [ -n "$PYTEST" ]; then
    if ! $PYTEST -q 2>/dev/null; then
      echo "ERROR: Tests failed after merging $BRANCH."
      echo "Fix the issue, commit, then re-run teardown for remaining plans."
      exit 1
    fi
  else
    echo "  WARN: pytest not found, skipping test verification"
  fi

  if [ -f "ci/check_foundations.py" ]; then
    PYTHON="python3"
    [ -f ".venv/bin/python" ] && PYTHON=".venv/bin/python"
    if ! $PYTHON ci/check_foundations.py 2>/dev/null; then
      echo "ERROR: check_foundations.py failed after merging $BRANCH."
      echo "Fix cross-reference issues, commit, then re-run for remaining plans."
      exit 1
    fi
  fi

  # Cleanup
  if [ -d "$WORKTREE" ]; then
    git worktree remove "$WORKTREE"
  fi
  git branch -d "$BRANCH" 2>/dev/null || true

  echo "  OK: $BRANCH merged and cleaned up"
  echo ""
done

echo "=== All plans integrated successfully ==="
