---
status: done
design: "Follows ADR-0006"
---

# Plan: Fail CI when E2E tests silently skip

## Problem

Both CI workflows can report green with zero E2E tests actually executed:

1. **verify.yml** — collects e2e tests but always skips them (no tool on PATH).
   E2E tests inflate the "15 skipped" count, masking real skips.
2. **e2e-nightly.yml** — if `ANTHROPIC_API_KEY` secret is missing/expired,
   Claude CLI install is skipped, all 13 tests skip, pytest exits 0.

## Solution

### Change 1: verify.yml — exclude e2e tests

Add `--ignore=tests/e2e` to the pytest invocation. E2E tests should never
run in the PR/push workflow — they need an LLM tool and API key. Excluding
them removes false skips from the count and makes the skip count meaningful.

### Change 2: e2e-nightly.yml — fail on all-skip

Add a step after pytest that parses the JUnit XML output and fails if
zero tests actually passed. Use pytest's `--junit-xml` flag and a simple
grep/check.

```yaml
- name: Run E2E tests
  run: pytest tests/e2e/ -v --no-cov --junit-xml=e2e-results.xml

- name: Fail if no tests ran
  if: always()
  run: |
    if ! grep -q 'tests="[1-9]' e2e-results.xml 2>/dev/null; then
      echo "ERROR: Zero E2E tests ran. Check ANTHROPIC_API_KEY secret." >&2
      exit 1
    fi
```

### Change 3: pyproject.toml — exclude e2e from default test collection

Add `--ignore=tests/e2e` to `[tool.pytest.ini_options] addopts` so local
`pytest` runs also exclude e2e by default. Developers run e2e explicitly
with `pytest tests/e2e/`.

### Files touched

| File | Change |
|------|--------|
| `.github/workflows/verify.yml` | Add `--ignore=tests/e2e` to pytest |
| `.github/workflows/e2e-nightly.yml` | Add `--junit-xml` + fail-on-zero-ran step |
| `pyproject.toml` | Add `--ignore=tests/e2e` to addopts |

## Acceptance criteria

1. `pytest` (no args) does NOT collect tests/e2e/ files
2. `pytest tests/e2e/` still collects them (explicit override)
3. e2e-nightly has a step that fails if zero tests ran
4. All existing tests still pass
