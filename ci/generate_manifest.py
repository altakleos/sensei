"""Regenerate src/sensei/engine/manifest.yaml with SHA-256 checksums.

Usage:
    python ci/generate_manifest.py
"""

from __future__ import annotations

import hashlib
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ENGINE_DIR = _REPO_ROOT / "src" / "sensei" / "engine"
_MANIFEST_PATH = _ENGINE_DIR / "manifest.yaml"

_EXCLUDED_NAMES = {"__init__.py", "manifest.yaml", "run.sh"}
_EXCLUDED_BASENAMES = {"README.md"}
_EXCLUDED_DIRS = {"__pycache__"}

_HEADER = """\
# Sensei engine bundle manifest. Enumerates every file that must be present
# for `sensei verify` to report OK, with SHA-256 checksums for content
# integrity verification.
#
# Regenerate with: python ci/generate_manifest.py

schema_version: 2

required:
"""

# Directory groups in display order, with comment headers matching the
# current manifest style.  "." means top-level files.
_GROUPS: list[tuple[str, str]] = [
    (".", "  # Top-level"),
    ("templates", "  # Templates"),
    ("protocols", "  # Protocols (top-level)"),
    ("protocols/modes", "  # Behavioral mode files"),
    ("schemas", "  # Schemas"),
    ("scripts", "  # Helper scripts"),
]


def _collect_files() -> list[tuple[str, str]]:
    """Return sorted (rel_path, sha256) for every manifest-eligible file."""
    entries: list[tuple[str, str]] = []
    for path in _ENGINE_DIR.rglob("*"):
        if not path.is_file():
            continue
        if any(part in _EXCLUDED_DIRS for part in path.parts):
            continue
        if path.name in _EXCLUDED_NAMES or path.name in _EXCLUDED_BASENAMES:
            continue
        rel = path.relative_to(_ENGINE_DIR).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append((rel, digest))
    entries.sort()
    return entries


def _group_key(rel: str) -> str:
    """Return the directory group key for a relative path."""
    parts = rel.split("/")
    if len(parts) == 1:
        return "."
    return "/".join(parts[:-1])


def generate() -> str:
    entries = _collect_files()
    grouped: dict[str, list[tuple[str, str]]] = {}
    for rel, digest in entries:
        key = _group_key(rel)
        grouped.setdefault(key, []).append((rel, digest))

    lines = [_HEADER]
    first = True
    for group_key, comment in _GROUPS:
        items = grouped.get(group_key, [])
        if not items:
            continue
        if not first:
            lines.append("")
        lines.append(comment)
        for rel, digest in items:
            lines.append(f"  - path: {rel}")
            lines.append(f"    sha256: {digest}")
        first = False

    return "\n".join(lines) + "\n"


def main() -> None:
    content = generate()
    _MANIFEST_PATH.write_text(content, encoding="utf-8")
    print(f"Wrote {_MANIFEST_PATH}")


if __name__ == "__main__":
    main()
