"""Wheel contents validator (maintainer-side, CI only).

Asserts a built wheel satisfies the invariants in docs/specs/release-process.md:

- **Required files present.** The engine bundle ships complete.
- **Required directories non-empty.** `prompts/`, `schemas/`, `profiles/` each
  contain at least one entry.
- **No forbidden path prefixes.** User-instance content never leaks into the
  wheel.
- **Version concordance.** `sensei/__init__.py.__version__` matches the
  supplied `--tag` (leading `v` stripped). Literal string comparison — the
  release process requires the maintainer to keep them exactly in sync.

Exit codes:
    0 — all checks pass
    1 — one or more required files or directories missing
    2 — one or more forbidden paths present
    3 — version concordance failure (or version unreadable)

Prints a single JSON report to stdout regardless of exit code.

Invoked by `.github/workflows/release.yml` as the final gate before the
publish job runs.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any

REQUIRED_FILES: tuple[str, ...] = (
    "sensei/__init__.py",
    "sensei/engine/engine.md",
    "sensei/engine/defaults.yaml",
    "sensei/engine/protocols/README.md",
    "sensei/engine/protocols/review.md",
    "sensei/engine/scripts/config.py",
    "sensei/engine/scripts/check_profile.py",
    "sensei/engine/scripts/mastery_check.py",
    "sensei/engine/scripts/decay.py",
    "sensei/engine/scripts/classify_confidence.py",
    "sensei/engine/schemas/profile.schema.json",
)

REQUIRED_DIRS: tuple[str, ...] = (
    "sensei/engine/prompts/",
    "sensei/engine/schemas/",
    "sensei/engine/profiles/",
)

FORBIDDEN_PREFIXES: tuple[str, ...] = (
    "instance/",
    "wiki/",
    "raw/",
    "notebook/",
    "inbox/",
    "memory/",
    ".kiro/",
    ".cursor/",
    ".windsurf/",
    ".clinerules/",
    ".roo/",
    ".aiassistant/",
    ".github/",
)

FORBIDDEN_EXACT: tuple[str, ...] = (
    "AGENTS.md",
    "CLAUDE.md",
)

_VERSION_PATTERN = re.compile(r'^__version__\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)


def _strip_v(tag: str) -> str:
    return tag[1:] if tag.startswith("v") else tag


def _extract_version(init_content: str) -> str | None:
    m = _VERSION_PATTERN.search(init_content)
    return m.group(1) if m else None


def check_wheel(wheel_path: Path, tag: str) -> tuple[int, dict[str, Any]]:
    """Validate `wheel_path` against `tag`. Returns (exit_code, report)."""
    with zipfile.ZipFile(wheel_path) as z:
        names = z.namelist()
        try:
            init_content = z.read("sensei/__init__.py").decode("utf-8")
        except KeyError:
            init_content = ""
    name_set = set(names)

    missing_files = [f for f in REQUIRED_FILES if f not in name_set]
    missing_dirs = [d for d in REQUIRED_DIRS if not any(n.startswith(d) for n in names)]

    forbidden: list[str] = []
    for n in names:
        if any(n.startswith(p) for p in FORBIDDEN_PREFIXES) or n in FORBIDDEN_EXACT:
            forbidden.append(n)

    expected = _strip_v(tag)
    actual = _extract_version(init_content)

    report: dict[str, Any] = {
        "wheel": str(wheel_path),
        "tag": tag,
        "expected_version": expected,
        "actual_version": actual,
        "missing_files": missing_files,
        "missing_dirs": missing_dirs,
        "forbidden": forbidden,
    }

    if missing_files or missing_dirs:
        report["status"] = "missing"
        return 1, report
    if forbidden:
        report["status"] = "forbidden"
        return 2, report
    if actual != expected:
        report["status"] = "version_mismatch"
        return 3, report

    report["status"] = "ok"
    return 0, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--wheel", type=Path, required=True, help="Path to the built .whl file")
    parser.add_argument("--tag", required=True, help="Release tag, e.g. v0.1.0 or v0.1.0-alpha")
    args = parser.parse_args(argv)

    if not args.wheel.is_file():
        print(json.dumps({"status": "missing", "error": f"wheel not found: {args.wheel}"}))
        return 1

    rc, report = check_wheel(args.wheel, args.tag)
    print(json.dumps(report))
    return rc


if __name__ == "__main__":
    sys.exit(main())
