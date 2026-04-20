---
feature: parallel-worktrees
serves: docs/specs/parallel-agents.md
design: docs/design/parallel-agents.md
status: done
date: 2026-04-20
---
# Plan: Parallel Agent Worktrees

## Tasks

- [ ] **T1:** Add `.worktrees/` to `.gitignore` → `.gitignore`
  Append `.worktrees/` to the existing .gitignore file.

- [ ] **T2:** Create `scripts/worktree-setup.sh` → `scripts/worktree-setup.sh`
  Bash script (~50 lines) that:
  - Accepts one or more plan names as arguments
  - Validates working directory is clean (abort if dirty)
  - For each plan name: creates branch `plan/<name>` from current HEAD, creates worktree at `.worktrees/<name>/`
  - Runs `pip install -e .` in each worktree (if pyproject.toml exists)
  - Prints summary: directory paths and branch names for each agent
  - Idempotent: skips existing worktrees with a message
  - Make executable (chmod +x)

- [ ] **T3:** Create `scripts/worktree-teardown.sh` → `scripts/worktree-teardown.sh` (depends: T2)
  Bash script (~50 lines) that:
  - Accepts one or more plan names as arguments (merge order = argument order)
  - For each plan: merges `plan/<name>` into current branch (ff preferred, --no-ff fallback)
  - After each merge: runs `pytest` and `python ci/check_foundations.py`
  - If merge conflicts: aborts, prints conflicting files, prints resolution hint for CHANGELOG.md pattern
  - If verification fails: aborts, prints failure output
  - On success: removes worktree (`git worktree remove`), deletes branch (`git branch -d`)
  - Make executable (chmod +x)

- [ ] **T4:** Create workflow runbook → `docs/operations/parallel-agents.md` (depends: T2, T3)
  Step-by-step human workflow (~40 lines):
  - When to use (plans declared as parallelizable)
  - Setup: exact commands for the Plans 2/3/4 case
  - During execution: what to tell each agent, how to monitor
  - Integration: merge order recommendation (smallest first), CHANGELOG conflict resolution pattern
  - Cleanup: what happens automatically vs manually
  - Troubleshooting: common issues and fixes

- [ ] **T5:** Verify end-to-end → verify (depends: T2, T3)
  - Run `scripts/worktree-setup.sh curriculum-engine interaction-model deep-frontiers`
  - Confirm 3 worktrees exist at `.worktrees/`
  - Make a trivial commit in one worktree, confirm it's invisible from another
  - Run `scripts/worktree-teardown.sh deep-frontiers` on one to verify merge path
  - Clean up remaining worktrees
  - Full test suite green

- [ ] **T6:** Update `docs/specs/README.md` and `docs/design/README.md` indexes → `docs/specs/README.md`, `docs/design/README.md` (depends: T1)
  Add rows for the new spec and design doc.

- [ ] **T7:** Append Unreleased entry to CHANGELOG.md → `CHANGELOG.md` (depends: T5)

## Acceptance Criteria

- [ ] **AC1:** `scripts/worktree-setup.sh plan-a plan-b` creates `.worktrees/plan-a/` and `.worktrees/plan-b/` with correct branches
- [ ] **AC2:** Changes committed in one worktree are invisible from another worktree's `git status`
- [ ] **AC3:** `scripts/worktree-teardown.sh plan-a` merges, verifies, removes worktree, and deletes branch
- [ ] **AC4:** Teardown aborts cleanly on merge conflict (worktree preserved for manual resolution)
- [ ] **AC5:** `.worktrees/` is gitignored (does not appear in `git status`)
- [ ] **AC6:** Workflow runbook is followable by someone with no prior context
- [ ] **AC7:** Full test suite green
