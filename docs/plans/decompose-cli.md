---
status: done
design: "Follows ADR-0006"
---

# Plan: Decompose cli.py into focused modules

## Problem

`cli.py` is a 601-LOC monolith containing 4 CLI commands, engine
management logic, shim generation, and validation — all in one file.
As commands grow, this becomes harder to navigate and test in isolation.

## Analysis

The dependency graph is a clean DAG with no circular dependencies:

```
constants ← engine_mgmt ← {init, upgrade}
constants ← shim_gen    ← {init, upgrade, verify(read-only)}
engine_scripts           ← {status, upgrade, verify}
```

## Solution

Extract three modules alongside cli.py. Keep cli.py as the thin
Click command layer that delegates to extracted modules.

### New modules

| Module | Extracted from | LOC | Contents |
|--------|---------------|-----|----------|
| `_engine.py` | cli.py L62–175 | ~114 | `_engine_source`, `_fsync_dir`, `_atomic_replace_engine`, `_install_run_script` |
| `_shims.py` | cli.py L35–52, L161–164 | ~25 | `_SHIMS` dict, `_write_shim` |
| `_verify.py` | cli.py L455–601 | ~147 | `verify` command body extracted as `run_verify(target, verbose)` |

### What stays in cli.py

- Click group and command decorators (`main`, `init`, `status`, `upgrade`, `verify`)
- Command-specific constants (`_LEARNER_ID_RE`, `_LEARNER_CONFIG_YAML`, `_STARTER_PROFILE_HEADER`)
- The `init` command body (97 LOC — uses init-only constants, not worth extracting)
- The `status` command body (91 LOC — simple, self-contained)
- The `upgrade` command body (62 LOC — small)
- The `verify` Click decorator (thin wrapper calling `_verify.run_verify`)

### Import structure

```
cli.py
  ├── from sensei._engine import _engine_source, _atomic_replace_engine, _install_run_script
  ├── from sensei._shims import SHIMS, write_shim
  └── from sensei._verify import run_verify (lazy, inside verify command)

_engine.py
  ├── stdlib only (shutil, os, stat, pathlib)
  └── import sensei (for __file__ resolution)

_shims.py
  └── stdlib only (pathlib)

_verify.py
  ├── from sensei._shims import SHIMS
  └── lazy: sensei.engine.scripts.{check_profile, config, check_goal}
```

No circular imports. `_engine.py` and `_shims.py` are leaf modules.

### Naming convention

Leading underscore (`_engine.py`, `_shims.py`, `_verify.py`) signals
these are internal modules, not public API. Drop the leading underscore
from extracted symbols (e.g., `_engine_source` → `engine_source` since
the module-level underscore already signals privacy).

### Files touched

| File | Change |
|------|--------|
| `src/sensei/_engine.py` | New — engine management functions |
| `src/sensei/_shims.py` | New — shim dict and writer |
| `src/sensei/_verify.py` | New — verify command logic |
| `src/sensei/cli.py` | Remove extracted code, add imports |
| `tests/test_cli.py` | Update any direct imports if needed |

### What does NOT change

- Public API: `sensei.cli:main` entry point unchanged
- CLI behavior: all 4 commands work identically
- Engine scripts: untouched
- Test behavior: all tests pass with same assertions

## Acceptance criteria

1. `cli.py` is under 300 LOC
2. Three new modules exist with clear single responsibilities
3. No circular imports
4. `pytest` passes (704+ tests, 92%+ coverage)
5. `ruff check src/` passes
6. `mypy --strict src/` passes (or no regressions)
7. `sensei init`, `sensei status`, `sensei upgrade`, `sensei verify` all work

## Risks

- **Import ordering**: Lazy imports in command bodies must stay lazy to
  avoid import-time side effects. The extraction preserves this.
- **Test coupling**: Some tests may import private symbols from cli.py
  directly. These need updating to import from the new modules.
