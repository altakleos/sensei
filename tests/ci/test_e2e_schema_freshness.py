"""Verify E2E fixtures use current schema versions.

E2E test fixtures hardcode schema_version values. When migrate.py bumps
CURRENT_PROFILE_VERSION or CURRENT_GOAL_VERSION, these fixtures become
stale. This test catches the drift at CI time rather than at the next
nightly E2E run.
"""

from __future__ import annotations

import re
from pathlib import Path

from sensei.engine.scripts.migrate import CURRENT_GOAL_VERSION, CURRENT_PROFILE_VERSION

_E2E_DIR = Path(__file__).resolve().parents[2] / "tests" / "e2e"

# Schema versions that are valid across all file types.
# Profile and goal versions come from migrate.py; hints and session-notes
# are pinned at 0 in their JSON schemas (no migration system yet).
_VALID_VERSIONS = {CURRENT_PROFILE_VERSION, CURRENT_GOAL_VERSION, 0}


def _find_schema_versions(directory: Path) -> list[tuple[Path, int, int]]:
    """Return (file, line_number, version) for every schema_version literal."""
    results: list[tuple[Path, int, int]] = []
    pattern = re.compile(r"""["']schema_version["']\s*:\s*(\d+)""")
    for py_file in sorted(directory.glob("*.py")):
        for i, line in enumerate(py_file.read_text(encoding="utf-8").splitlines(), 1):
            m = pattern.search(line)
            if m:
                results.append((py_file, i, int(m.group(1))))
    return results


def test_e2e_fixtures_use_current_schema_versions() -> None:
    """Every schema_version in E2E fixtures matches a known current version."""
    if not _E2E_DIR.is_dir():
        return
    stale: list[str] = []
    for path, line, version in _find_schema_versions(_E2E_DIR):
        if version not in _VALID_VERSIONS:
            stale.append(f"{path.name}:{line} has schema_version {version}")
    assert not stale, (
        f"E2E fixtures have stale schema_version "
        f"(valid: {sorted(_VALID_VERSIONS)}):\n" + "\n".join(stale)
    )
