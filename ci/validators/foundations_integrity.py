"""Foundations referential integrity validator for ``kanon verify``."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parent.parent / "check_foundations.py"


def _load():  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location("_cf", _SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check(target: Path, errors: list[str], warnings: list[str]) -> None:
    foundations = target / "docs" / "foundations"
    specs = target / "docs" / "specs"
    if not foundations.is_dir() or not specs.is_dir():
        return
    errs, warns = _load().check(foundations, specs)
    errors.extend(f"foundations: {e}" for e in errs)
    warnings.extend(f"foundations: {w}" for w in warns)
