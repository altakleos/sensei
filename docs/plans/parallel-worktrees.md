---
feature: parallel-worktrees
serves: (operational — unblocks parallel agent execution of Plans 2, 3, 4)
design: (N/A — git workflow, not a product feature)
status: planned
date: 2026-04-20
---
# Plan: Parallel Agent Worktrees

## Problem

Plans 2 (curriculum-engine), 3 (interaction-model), and 4 (deep-frontiers-principles) can run in parallel, but a single git checkout means:
- One agent creating a branch moves the other agent's HEAD
- Uncommitted changes from one agent appear in the other's `git status`
- Neither agent knows what's theirs to commit

## Solution

Git worktrees: one worktree per plan, each on its own branch, sharing the same `.git` object store. No copies, no forks, instant setup.

## Tasks

- [ ] T1: Create `scripts/worktree-setup.sh` — takes a plan name, creates a branch from `main`, adds a worktree under `../<repo>-<plan>/`. Idempotent (skip if worktree exists). → `scripts/worktree-setup.sh`
- [ ] T2: Create `scripts/worktree-teardown.sh` — takes a plan name, merges its branch into `main` (fast-forward only; abort on conflict for manual resolution), removes the worktree, deletes the branch. → `scripts/worktree-teardown.sh`
- [ ] T3: Create `docs/operations/parallel-agents.md` — brief workflow doc: setup, point each agent at its worktree directory, merge back. Includes the exact commands for the 3-plan case. → `docs/operations/parallel-agents.md`
- [ ] T4: Dry-run — execute `worktree-setup.sh` for all three plans, verify each worktree is on the correct branch and has a clean working tree, then tear down one to verify the merge path works.

## Acceptance Criteria

- [ ] AC1: Running `worktree-setup.sh curriculum-engine` creates `../sensei-curriculum-engine/` on branch `plan/curriculum-engine` from current `main`
- [ ] AC2: Running `worktree-setup.sh` for all three plans produces three independent working directories that share the same git object store
- [ ] AC3: A commit in one worktree does not appear in `git status` of another
- [ ] AC4: `worktree-teardown.sh curriculum-engine` fast-forward merges the branch into `main` and removes the worktree
- [ ] AC5: `docs/operations/parallel-agents.md` exists and documents the full workflow
