"""Tests for ci/check_deps.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "ci" / "check_deps.py"
assert _SCRIPT_PATH.is_file(), f"script not found: {_SCRIPT_PATH}"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_deps", _SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


mod = _load_module()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# --- pyproject.toml tests ---


def test_pinned_deps_no_warnings(tmp_path: Path) -> None:
    _write(
        tmp_path / "pyproject.toml",
        '[project]\nname = "x"\ndependencies = [\n  "click==8.1.7",\n]\n',
    )
    findings = mod._check_pyproject_toml(tmp_path / "pyproject.toml")
    assert findings == []


def test_unpinned_dep_reported(tmp_path: Path) -> None:
    _write(
        tmp_path / "pyproject.toml",
        '[project]\nname = "x"\ndependencies = [\n  ">=8.0",\n]\n',
    )
    findings = mod._check_pyproject_toml(tmp_path / "pyproject.toml")
    assert len(findings) == 1
    assert findings[0]["rule"] == "unpinned-version"


def test_exact_pinned_dep_no_warning(tmp_path: Path) -> None:
    _write(
        tmp_path / "pyproject.toml",
        '[project]\nname = "x"\ndependencies = [\n  "requests==2.31.0",\n]\n',
    )
    findings = mod._check_pyproject_toml(tmp_path / "pyproject.toml")
    assert findings == []


# --- requirements.txt tests ---


def test_requirements_unpinned_range(tmp_path: Path) -> None:
    _write(tmp_path / "requirements.txt", "requests>=1.0\n")
    findings = mod._check_requirements_txt(tmp_path / "requirements.txt")
    assert len(findings) == 1
    assert findings[0]["rule"] == "unpinned-version"


def test_requirements_pinned_ok(tmp_path: Path) -> None:
    _write(tmp_path / "requirements.txt", "requests==2.31.0\n")
    findings = mod._check_requirements_txt(tmp_path / "requirements.txt")
    assert findings == []


# --- duplicate-purpose tests ---


def test_duplicate_purpose_reported(tmp_path: Path) -> None:
    _write(
        tmp_path / "requirements.txt",
        "requests==2.31.0\nhttpx==0.27.0\n",
    )
    findings = mod._check_duplicates(tmp_path)
    assert len(findings) == 1
    assert findings[0]["rule"] == "duplicate-purpose"
    assert "http" in findings[0]["message"].lower()
