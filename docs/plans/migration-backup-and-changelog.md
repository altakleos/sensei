---
status: done
design: "Follows ADR-0004"
---

# Plan: Add backup/rollback to migration and fix CHANGELOG

## Problem 1: Migration has no backup/rollback (#3)

`migrate_instance()` migrates profile.yaml then iterates goal files
sequentially. Each file write is individually atomic (via `atomic_write_text`),
but there is no transaction boundary across files. If profile migrates
successfully but the 3rd goal file fails, you get mixed schema versions
on disk with no recovery path.

## Problem 2: CHANGELOG is empty (#5)

8+ commits since v0.2.0a2 with an empty `[Unreleased]` section.

## Solution

### Change 1: Backup before migration in migrate_instance()

Before migrating any files, copy the entire `learner/` directory to
`learner/.backup/`. On success, remove the backup. On any failure,
restore from backup.

```python
def migrate_instance(learner_dir: Path) -> list[str]:
    backup_dir = learner_dir / ".backup"
    # Back up files that migration will touch
    _backup_targets(learner_dir, backup_dir)
    try:
        results = _do_migrate(learner_dir)
    except Exception:
        _restore_backup(learner_dir, backup_dir)
        raise
    # Success — remove backup
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    return results
```

The backup is lightweight — only copy files that migration actually touches
(profile.yaml + goals/*.yaml), not the entire learner directory.

### Change 2: CHANGELOG entries

Add entries for all user-visible changes since v0.2.0a2.

### Files touched

| File | Change |
|------|--------|
| `src/sensei/engine/scripts/migrate.py` | Add backup/restore around migration |
| `tests/test_migrate.py` | Add test for partial failure + rollback |
| `CHANGELOG.md` | Fill [Unreleased] section |

## Acceptance criteria

1. Partial migration failure restores all files to pre-migration state
2. Successful migration removes the backup
3. New test simulates partial failure and verifies rollback
4. CHANGELOG [Unreleased] has entries for all user-visible changes
5. `pytest` passes, coverage maintained
