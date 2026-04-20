#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
REPO_NAME="$(basename "$REPO_ROOT")"
PARENT_DIR="$(dirname "$REPO_ROOT")"

usage() {
  echo "Usage: $0 [--merge|--cleanup] [-b BASE_BRANCH] agent:branch [agent:branch ...]"
  echo "  Each arg is agent_name:branch_name (e.g. kiro:feat/curriculum-engine)"
  echo "  --merge    Merge all agent branches back to base and remove worktrees"
  echo "  --cleanup  Remove worktrees without merging"
  echo "  -b BRANCH  Base branch (default: current branch)"
  exit 1
}

# Parse flags
MODE="create"; BASE=""
while [[ $# -gt 0 && "$1" == -* ]]; do
  case "$1" in
    --merge)   MODE="merge"; shift ;;
    --cleanup) MODE="cleanup"; shift ;;
    -b)        BASE="$2"; shift 2 ;;
    *)         usage ;;
  esac
done
[[ $# -eq 0 ]] && usage
BASE="${BASE:-$(git branch --show-current)}"

# Collect agent:branch pairs
declare -a AGENTS=() BRANCHES=() DIRS=()
for arg in "$@"; do
  [[ "$arg" == *:* ]] || { echo "Error: '$arg' must be agent:branch"; exit 1; }
  AGENTS+=("${arg%%:*}"); BRANCHES+=("${arg#*:}")
  DIRS+=("$PARENT_DIR/$REPO_NAME-${arg%%:*}")
done

do_cleanup() {
  for i in "${!DIRS[@]}"; do
    [[ -d "${DIRS[$i]}" ]] && git worktree remove --force "${DIRS[$i]}" && echo "Removed ${DIRS[$i]}"
  done
}

if [[ "$MODE" == "cleanup" ]]; then do_cleanup; exit 0; fi

if [[ "$MODE" == "merge" ]]; then
  git checkout "$BASE" 2>/dev/null || git switch "$BASE"
  for i in "${!BRANCHES[@]}"; do
    echo "Merging ${BRANCHES[$i]} into $BASE..."
    git merge --no-ff "${BRANCHES[$i]}" -m "merge: ${BRANCHES[$i]} into $BASE"
  done
  do_cleanup
  echo "Done. All branches merged into $BASE."
  exit 0
fi

# Create mode — check for dirty state
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Error: working directory is dirty. Commit or stash changes first." >&2; exit 1
fi

for i in "${!AGENTS[@]}"; do
  dir="${DIRS[$i]}"; branch="${BRANCHES[$i]}"
  if [[ -d "$dir" ]]; then echo "Skip: $dir already exists"; continue; fi
  if git show-ref --verify --quiet "refs/heads/$branch" 2>/dev/null; then
    git worktree add "$dir" "$branch"
  else
    git worktree add -b "$branch" "$dir" "$BASE"
  fi
done

echo ""
echo "=== Worktrees ready ==="
for i in "${!AGENTS[@]}"; do
  echo "  ${AGENTS[$i]} → ${DIRS[$i]}  (branch: ${BRANCHES[$i]})"
done
echo ""
echo "Open each directory in its own agent session."
echo "When done: $0 --merge -b $BASE $*"
