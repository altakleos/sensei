---
status: done
design: "Follows ADR-0004"
---

# Plan: Add SHA-256 checksums to engine manifest

## Problem

`sensei verify` checks that files listed in manifest.yaml exist, but never
validates their content. A corrupted or tampered script passes verification
as long as the file is present.

## Solution

### Manifest format change (schema_version 1 → 2)

Change `required` from a flat string list to a list of objects with
`path` and `sha256` fields:

```yaml
schema_version: 2
required:
  - path: engine.md
    sha256: abc123...
  - path: scripts/decay.py
    sha256: def456...
```

### New script: ci/generate_manifest.py

Walks `src/sensei/engine/`, computes SHA-256 for each file in the
manifest, and writes `manifest.yaml` with hashes. Run manually when
engine files change, output checked into git.

### Verify changes (_verify.py)

For schema_version 2: check existence AND compare SHA-256. For
schema_version 1 (old instances not yet upgraded): fall back to
existence-only checks with a warning.

### CI test update

`test_engine_manifest.py` updated to validate the new format and
verify that committed hashes match actual file contents.

### Files touched

| File | Change |
|------|--------|
| `src/sensei/engine/manifest.yaml` | Format v1 → v2 with SHA-256 hashes |
| `src/sensei/_verify.py` | Add SHA-256 verification for v2 manifests |
| `ci/generate_manifest.py` | New — generates manifest with hashes |
| `tests/ci/test_engine_manifest.py` | Update for new format + hash verification |

## Acceptance criteria

1. `manifest.yaml` schema_version is 2 with SHA-256 for all 45 files
2. `sensei verify` checks content hashes, not just existence
3. Tampered file detected by verify (new test)
4. `ci/generate_manifest.py` reproduces the committed manifest exactly
5. Old v1 manifests still work (existence-only + warning)
6. All tests pass, coverage maintained
