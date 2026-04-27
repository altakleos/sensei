"""Changelog link validator for ``kanon verify``."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parent.parent / "check_changelog_links.py"


def _load():  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location("_ccl", _SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check(target: Path, errors: list[str], warnings: list[str]) -> None:
    changelog = target / "CHANGELOG.md"
    if not changelog.is_file():
        return
    errs = _load().lint(changelog)
    errors.extend(f"changelog-links: {e}" for e in errs)
