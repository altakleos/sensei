"""Tests for src/sensei/engine/manifest.yaml.

The engine manifest is the contract for `sensei verify`: every file shipped
inside the engine bundle must be registered, otherwise verify cannot detect
its absence on a learner instance. This test enumerates the on-disk bundle
and asserts the manifest is exhaustive.

If you add a new protocol/script/schema to the engine bundle, add it to
manifest.yaml in the same commit — these tests will fail otherwise.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ENGINE_DIR = _REPO_ROOT / "src" / "sensei" / "engine"
_MANIFEST_PATH = _ENGINE_DIR / "manifest.yaml"

# Files in the bundle that are deliberately not engine assets and therefore
# not registered in the manifest. Matches the exclusion set documented in
# manifest.yaml's header.
_EXCLUDED_NAMES = {"__init__.py", "manifest.yaml", "run.sh"}
_EXCLUDED_BASENAMES = {"README.md"}
_EXCLUDED_DIRS = {"__pycache__"}


def _shipped_files() -> set[str]:
    """Return the relative-to-engine paths of every file currently in the bundle,
    minus the documented exclusion set."""
    out: set[str] = set()
    for path in _ENGINE_DIR.rglob("*"):
        if not path.is_file():
            continue
        if any(part in _EXCLUDED_DIRS for part in path.parts):
            continue
        if path.name in _EXCLUDED_NAMES:
            continue
        if path.name in _EXCLUDED_BASENAMES:
            continue
        out.add(path.relative_to(_ENGINE_DIR).as_posix())
    return out


def _manifest_data() -> dict:
    data = yaml.safe_load(_MANIFEST_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "manifest.yaml must be a YAML mapping"
    return data


def _manifest_required() -> list[dict]:
    data = _manifest_data()
    required = data.get("required")
    assert isinstance(required, list), "manifest.yaml: 'required' must be a list"
    assert all(isinstance(r, dict) for r in required), "manifest entries must be dicts"
    return required


def _manifest_paths() -> list[str]:
    return [e["path"] for e in _manifest_required()]


def test_manifest_exists() -> None:
    assert _MANIFEST_PATH.is_file(), f"manifest not found at {_MANIFEST_PATH}"


def test_manifest_is_well_formed() -> None:
    """Schema_version present, required is a non-empty list of dicts."""
    data = _manifest_data()
    assert data.get("schema_version") == 2
    required = data.get("required")
    assert isinstance(required, list) and required, "required list is empty or wrong type"
    for entry in required:
        assert isinstance(entry, dict), f"expected dict, got {type(entry).__name__}"
        assert "path" in entry, f"entry missing 'path': {entry}"
        assert "sha256" in entry, f"entry missing 'sha256': {entry}"


def test_every_shipped_file_is_registered() -> None:
    """Inverse-coverage check: anything under src/sensei/engine/ that ships
    must appear in manifest.yaml. Catches contributors adding a new protocol
    file but forgetting to register it."""
    shipped = _shipped_files()
    registered = set(_manifest_paths())
    unregistered = sorted(shipped - registered)
    assert not unregistered, (
        "The following engine files ship but are not registered in "
        "manifest.yaml. Add them to the 'required:' list:\n  - "
        + "\n  - ".join(unregistered)
    )


def test_no_manifest_entries_point_at_missing_files() -> None:
    """Forward-coverage check: every manifest entry resolves to a real file
    in the engine bundle. Catches typos and stale entries left after a
    rename or deletion."""
    missing = [rel for rel in _manifest_paths() if not (_ENGINE_DIR / rel).is_file()]
    assert not missing, (
        "manifest.yaml lists entries that do not exist in the bundle:\n  - "
        + "\n  - ".join(missing)
    )


def test_checksums_match_file_contents() -> None:
    """Verify that committed SHA-256 hashes match actual file contents.
    Catches stale hashes after file edits without regenerating the manifest."""
    mismatches: list[str] = []
    for entry in _manifest_required():
        rel = entry["path"]
        expected = entry["sha256"]
        actual = hashlib.sha256((_ENGINE_DIR / rel).read_bytes()).hexdigest()
        if actual != expected:
            mismatches.append(f"{rel}: expected {expected[:12]}… got {actual[:12]}…")
    assert not mismatches, (
        "Checksum mismatches — regenerate with: python ci/generate_manifest.py\n  - "
        + "\n  - ".join(mismatches)
    )


@pytest.mark.parametrize(
    "rel",
    [
        # Sentinel files that the previous hardcoded verify list was missing.
        # These must be in the manifest from now on.
        "protocols/tutor.md",
        "protocols/hints.md",
        "protocols/challenger.md",
        "protocols/reviewer.md",
        "protocols/status.md",
        "protocols/performance-training.md",
        "schemas/goal.schema.json",
        "schemas/hints.yaml.schema.json",
        "scripts/review_scheduler.py",
        "scripts/goal_priority.py",
    ],
)
def test_manifest_contains_previously_unchecked_files(rel: str) -> None:
    """Regression: pin the specific files that the v0.1.0a18 hardcoded list
    omitted, so we cannot accidentally drop them again."""
    assert rel in _manifest_paths(), (
        f"{rel} must be registered in manifest.yaml — it was previously "
        "missing from the hardcoded verify list."
    )
