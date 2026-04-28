---
status: done
design: "Follows ADR-0006, ADR-0022"
---

# Plan: Harden run.sh and sensei init against path-based attacks

## Problem

Three related security gaps in the script execution and init paths:

1. **run.sh passes `$@` unsanitized to `exec`** — no allowlist on script
   names. A prompt-injected LLM could pass crafted arguments.
2. **`sensei init` does not check for symlinks** — a symlink planted at the
   target before init runs could redirect file writes to arbitrary locations.
3. **`.python_path` is a trust anchor with no validation** — run.sh reads a
   path from this file and `exec`s it. No check that it's an absolute path
   to a real Python interpreter.

## Solution

### Change 1: Script-name allowlist in run.sh

Extract the script name from `$1`, validate it against a hardcoded allowlist
of the 19 scripts that have `__main__` guards. Reject anything else before
reaching `exec`.

```sh
# Allowlist of valid script targets (files with __main__ guards).
SCRIPT="$1"
case "$SCRIPT" in
  calibration_tracker.py|check_goal.py|check_profile.py|\
  classify_confidence.py|decay.py|frontier.py|\
  global_knowledge.py|goal_priority.py|hint_decay.py|\
  mastery_check.py|migrate.py|mutate_graph.py|\
  pacing.py|question_density.py|resume_planner.py|\
  review_scheduler.py|session_allocator.py|silence_ratio.py|\
  teaching_density.py) ;;
  *) echo "ERROR: unknown script: $SCRIPT" >&2; exit 1 ;;
esac
shift
```

Then pass `"$SCRIPT"` and `"$@"` (remaining args) to exec:
```sh
exec "$PYTHON" "$SCRIPT_DIR/scripts/$SCRIPT" "$@"
```

### Change 2: Validate `.python_path` in run.sh

After reading the file, check that the value is an absolute path before
using it:

```sh
PYTHON=$(cat "$PYTHON_PATH_FILE")
case "$PYTHON" in
  /*) ;;  # absolute path — OK
  *) echo "ERROR: .python_path must be an absolute path, got: $PYTHON" >&2; exit 1 ;;
esac
```

The existing `-x` check already verifies it's executable.

### Change 3: Symlink rejection in sensei init

After `target = target.resolve()`, before `target.mkdir()`, check that
neither the target nor the `.sensei` subdirectory is a symlink:

```python
if target.is_symlink():
    raise click.ClickException(
        f"Target path is a symlink: {target}. "
        f"Refusing to write through symlinks for security."
    )
sensei_dir = target / ".sensei"
if sensei_dir.is_symlink():
    raise click.ClickException(
        f".sensei is a symlink: {sensei_dir}. "
        f"Refusing to write through symlinks for security."
    )
```

Note: `target.resolve()` already follows symlinks, so `target.is_symlink()`
will be False after resolve. The check must happen BEFORE resolve on the
original argument. Reorder: check first, resolve second.

### Files touched

| File | Change |
|------|--------|
| `src/sensei/engine/run.sh` | Allowlist + .python_path validation |
| `src/sensei/cli.py` | Symlink check before resolve in init |

### What does NOT change

- Engine scripts — untouched
- Tests that don't test init or run.sh — untouched
- Upgrade path — new run.sh arrives via `sensei upgrade`

## Acceptance criteria

1. `run.sh` rejects script names not in the allowlist (exit 1, stderr message)
2. `run.sh` rejects non-absolute `.python_path` values (exit 1, stderr message)
3. `sensei init` rejects symlink targets with a clear error
4. `sensei init` rejects symlink `.sensei` directories with a clear error
5. `pytest` passes (698+ tests, 92%+ coverage)
6. `ruff check src/` passes
7. New tests cover the symlink rejection path

## Risks

- **Allowlist maintenance**: When a new script is added, run.sh must be
  updated. Mitigated by: scripts are added rarely, and a missing entry
  produces a clear error message that points to the fix.
- **Existing instances**: Old run.sh has no allowlist. `sensei upgrade`
  replaces it atomically. No migration needed.
