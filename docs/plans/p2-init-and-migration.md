---
status: done
---
# Plan: P2 Remaining — Init Robustness + Migration Chain Tests

**Scope**: 2 fixes — init error recovery, migration chain test gap
**Design**: Follows existing patterns; no new abstractions

## Tasks

### Fix 8: Make init learner scaffolding recoverable on partial failure

The engine install is already atomic. The learner file writes are not — and making them fully transactional (all-or-nothing) would require a staging directory + rename swap, which is heavy for what's essentially a one-time scaffolding operation.

**Pragmatic approach**: Instead of full transactionality, make init **self-healing** — if it fails partway through, re-running `sensei init <target> --force` should complete the missing writes. The current `if not exists` guards already prevent overwriting existing files, but the problem is that `--force` only gates on `.sensei/` existence, not learner file completeness.

**Change**: Wrap the learner file writes in a try/except that catches OSError. On failure, emit a clear message telling the user to re-run with `--force`. The `--force` path already re-runs the full init including learner scaffolding, and the `if not exists` guards protect already-written files.

Additionally, the `.gitkeep` write (L239–241) is unconditional — add an `if not exists` guard for consistency.

**File**: `src/sensei/cli.py`, `init` function
**Test**: Add `test_init_partial_failure_recoverable` — monkeypatch a write to raise OSError mid-init, verify error message suggests `--force`, then run init with `--force` and verify all files present.

### Fix 15: Add goal v0→v2 migration chain test

The profile chain test exists (`test_profile_migration_v0_to_v2_end_to_end`). The goal equivalent is missing.

**File**: `tests/test_migrate.py`
**Change**: Add `test_goal_migration_v0_to_v2_end_to_end` — create a v0 goal with old-style node states (`collapsed`, `spawned`, `expanded`) and no `target_depth`, call `migrate_goal()`, assert schema_version==2, node states renamed, and `target_depth` added.

Note on session-notes and hints migrations: No migration functions exist for these file types yet (they're at schema_version 0 with no v1 defined). Writing tests for non-existent migrations is out of scope — the gap is that `migrate_instance` doesn't handle them, but that's a feature gap, not a test gap. When v1 migrations are added for these types, tests should be added alongside.

## Verification

- `make gate` passes
- New tests cover both fixes
