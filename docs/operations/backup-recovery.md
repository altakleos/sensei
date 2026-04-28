# Backup and Recovery

How to protect and restore learner data in a Sensei instance.

## What to back up

All learner state lives under the instance's `learner/` directory:

```
learner/
├── profile.yaml          # mastery scores, engagement signals, misconception history
├── config.yaml           # user overrides for engine defaults (optional)
├── session-notes.yaml    # cross-session mentor observations
├── goals/                # one YAML file per learning goal (curriculum graph + state)
└── hints/
    ├── hints.yaml         # hint registry
    └── inbox/             # user-dropped materials
```

The `.sensei/` directory is the engine bundle — it can always be regenerated with `sensei upgrade`.

**Back up `learner/` only.** Everything else is reproducible.

## Backup

Copy the learner directory to any safe location:

```bash
cp -r ~/learning/learner ~/learning-backup-$(date +%Y%m%d)
```

Or use git — the instance folder works well as a personal repo:

```bash
cd ~/learning
git init
git add learner/
git commit -m "snapshot: $(date +%Y-%m-%d)"
```

## Recovery

### Restore from backup

```bash
# Replace corrupted learner data with backup
rm -rf ~/learning/learner
cp -r ~/learning-backup-20260428/learner ~/learning/learner

# Verify integrity
sensei verify ~/learning
```

### Rebuild engine from scratch

If `.sensei/` is corrupted but `learner/` is intact:

```bash
sensei upgrade ~/learning
sensei verify ~/learning
```

`sensei upgrade` performs an atomic engine swap — it backs up learner files before migration and restores them on partial failure (added in v0.2.0a3).

### Start fresh

```bash
rm -rf ~/learning/.sensei
sensei init ~/learning --force
```

This regenerates the engine bundle and shims. Learner data in `learner/` is preserved.

## What `sensei upgrade` already protects

Per ADR-0004, `sensei upgrade` performs an atomic engine replacement:

1. Backs up learner files that need migration
2. Runs schema migrations
3. Swaps the engine bundle atomically
4. On failure, restores the backup

This protects against upgrade-time corruption but not against manual edits, disk failures, or accidental deletion.

## Recommendations

- **Git-track your instance** if your learning history matters to you
- **Back up before manual YAML edits** — a typo in `profile.yaml` can break schema validation
- **Run `sensei verify` after any manual change** to catch problems early
