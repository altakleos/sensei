---
status: done
---
# Plan: P1 CLI Hardening — Upgrade Safety, Verify Completeness, Deprecated API

**Scope**: 4 fixes — 1 script, 3 CLI command improvements
**Design**: Follows existing patterns; no new abstractions

## Context

Gap analysis P1 items. These improve upgrade reliability and verify completeness.

## Tasks

### Fix 4: Replace deprecated `datetime.utcnow()` in mutate_graph.py

**File**: `src/sensei/engine/scripts/mutate_graph.py`
- Line 7: add `timezone` to `from datetime import datetime` → `from datetime import datetime, timezone`
- Line 200: replace `datetime.utcnow().strftime(...)` → `datetime.now(tz=timezone.utc).strftime(...)`

**Test impact**: None — existing tests pass `--now` explicitly, never hit the default branch.

### Fix 5: Upgrade refreshes AGENTS.md and shims

**File**: `src/sensei/cli.py`, `upgrade` function (L349–385)
**Change**: After `_install_run_script(sensei_dir)` (L381), add the same AGENTS.md + shim refresh block that `init` uses (L262–268):

```python
    # Refresh AGENTS.md + tool shims to match new engine version.
    agents_template = sensei_dir / "templates" / "AGENTS.md"
    if agents_template.exists():
        (target / "AGENTS.md").write_text(
            agents_template.read_text(encoding="utf-8"), encoding="utf-8"
        )
    for rel_path, content in _SHIMS.items():
        _write_shim(target, rel_path, content)
```

Note: Unlike `init`, we guard with `if agents_template.exists()` for robustness — the template should always exist after `_atomic_replace_engine`, but defensive coding.

**Test**: Add `test_upgrade_refreshes_agents_and_shims` — verify AGENTS.md content matches template after upgrade, verify at least one shim file is refreshed.

### Fix 6: Reject version downgrades in upgrade

**File**: `src/sensei/cli.py`, `upgrade` function
**Change**: After reading `old_version` (L361), before the equality check (L362), add a downgrade guard.

Since the project uses PEP 440 pre-release versions (`0.1.0a25`), we need `packaging.version.Version` for correct comparison. Stdlib tuple parsing breaks on `a25` suffixes.

- Add `packaging` to `pyproject.toml` dependencies: `"packaging>=23.0"`
- In `upgrade`, after reading `old_version`:

```python
    from packaging.version import Version, InvalidVersion
    try:
        old_ver = Version(old_version)
        new_ver = Version(__version__)
    except InvalidVersion:
        old_ver = None  # unknown version, allow upgrade
        new_ver = None

    if old_ver and new_ver and new_ver < old_ver:
        raise click.ClickException(
            f"Installed version ({__version__}) is older than current engine ({old_version}). "
            f"Downgrade is not supported — install a newer version or use 'init --force'."
        )
```

**Test**: Add `test_upgrade_rejects_downgrade` — set `.sensei-version` to a higher version, confirm upgrade fails with appropriate error.

### Fix 7: Expand verify to check goals, AGENTS.md, shims, hints

**File**: `src/sensei/cli.py`, `verify` function (L388–478)
**Changes** — add 4 new checks after the existing config check:

**Check 6: Goal file validation**
```python
    # Check 6: goal files
    goals_dir = target / "learner" / "goals"
    if goals_dir.is_dir():
        from sensei.engine.scripts.check_goal import validate_goal
        for goal_path in sorted(goals_dir.glob("*.yaml")):
            try:
                goal_data = yaml.safe_load(goal_path.read_text(encoding="utf-8"))
            except yaml.YAMLError as exc:
                errors.append(f"{goal_path.name}: invalid YAML — {exc}")
                continue
            if not isinstance(goal_data, dict):
                errors.append(f"{goal_path.name}: not a YAML mapping")
                continue
            status, goal_errors = validate_goal(goal_data)
            for e in goal_errors:
                errors.append(f"{goal_path.name}: {e}")
```

**Check 7: AGENTS.md exists**
```python
    if not (target / "AGENTS.md").exists():
        errors.append("missing: AGENTS.md")
```

**Check 8: Shim files exist**
```python
    for rel_path in _SHIMS:
        if not (target / rel_path).exists():
            errors.append(f"missing: {rel_path}")
```

**Check 9: Hints registry schema** (if file exists)
```python
    hints_path = target / "learner" / "hints" / "hints.yaml"
    if hints_path.exists():
        hints_schema_path = sensei_dir / "schemas" / "hints.yaml.schema.json"
        if hints_schema_path.exists():
            # validate against schema (same pattern as session-notes check)
```

**Tests**: Add tests for each new check — goal validation errors surfaced, missing AGENTS.md detected, missing shim detected, invalid hints.yaml detected.

## Verification

- `make gate` passes
- New tests cover all 4 fixes
- `sensei verify` on a valid instance still prints OK
- `sensei upgrade` on a downgrade scenario prints error and exits non-zero

## Out of Scope

- Extracting mastery levels to shared module (P2)
- Init transactionality (P2 #8)
- E2E tests (P3)
