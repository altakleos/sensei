"""Tests for ci/check_test_quality.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "ci" / "check_test_quality.py"
assert _SCRIPT_PATH.is_file(), f"script not found: {_SCRIPT_PATH}"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_test_quality", _SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


mod = _load_module()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_proper_test_no_findings(tmp_path: Path) -> None:
    _write(
        tmp_path / "test_good.py",
        "def test_addition():\n    assert 1 + 1 == 2\n",
    )
    errors, warnings = mod._check_file(tmp_path / "test_good.py")
    assert errors == []


def test_pass_only_body_reported(tmp_path: Path) -> None:
    _write(
        tmp_path / "test_bad.py",
        "def test_placeholder():\n    pass\n",
    )
    errors, warnings = mod._check_file(tmp_path / "test_bad.py")
    assert len(errors) == 1
    assert "trivial" in errors[0]


def test_assert_true_only_reported(tmp_path: Path) -> None:
    _write(
        tmp_path / "test_bad.py",
        "def test_placeholder():\n    assert True\n",
    )
    errors, warnings = mod._check_file(tmp_path / "test_bad.py")
    assert len(errors) == 1
    assert "trivial" in errors[0]


def test_non_test_files_ignored(tmp_path: Path) -> None:
    _write(tmp_path / "helper.py", "def test_helper():\n    pass\n")
    files = mod._find_test_files(tmp_path)
    assert not any("helper.py" in str(f) for f in files)
