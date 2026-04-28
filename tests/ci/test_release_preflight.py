"""Tests for ci/release-preflight.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "ci" / "release-preflight.py"
assert _SCRIPT_PATH.is_file(), f"script not found: {_SCRIPT_PATH}"


def _load_preflight():
    spec = importlib.util.spec_from_file_location("release_preflight", _SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


pfn = _load_preflight()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# -- _find_version tests --


def test_find_version_matches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(tmp_path / "src" / "pkg" / "__init__.py", '__version__ = "1.2.3"\n')
    monkeypatch.chdir(tmp_path)
    assert pfn._find_version() == "1.2.3"


def test_find_version_returns_none_when_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "src").mkdir()
    monkeypatch.chdir(tmp_path)
    assert pfn._find_version() is None


# -- main() integration tests (mock subprocess._check to isolate pure logic) --


def _setup_and_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    tag: str,
    version: str | None,
    changelog: str,
) -> int:
    """Scaffold a fake project, run main(), return exit code."""
    if version is not None:
        _write(tmp_path / "src" / "pkg" / "__init__.py", f'__version__ = "{version}"\n')
    else:
        (tmp_path / "src").mkdir(exist_ok=True)
    _write(tmp_path / "CHANGELOG.md", changelog)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["release-preflight.py", "--tag", tag])
    with patch.object(pfn, "_check", return_value=True), pytest.raises(SystemExit) as exc_info:
        pfn.main()
    return exc_info.value.code


def test_version_match_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rc = _setup_and_run(tmp_path, monkeypatch, "v1.2.3", "1.2.3", "## 1.2.3\n- stuff\n")
    assert rc == 0


def test_version_mismatch_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rc = _setup_and_run(tmp_path, monkeypatch, "v1.2.3", "9.9.9", "## 1.2.3\n- stuff\n")
    assert rc == 1


def test_invalid_tag_format_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A tag without a version number causes version_match to fail."""
    rc = _setup_and_run(tmp_path, monkeypatch, "vnotaversion", "1.2.3", "## notaversion\n")
    assert rc == 1


def test_changelog_entry_present_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rc = _setup_and_run(tmp_path, monkeypatch, "v2.0.0", "2.0.0", "## 2.0.0\n- big release\n")
    assert rc == 0


def test_changelog_missing_entry_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rc = _setup_and_run(tmp_path, monkeypatch, "v2.0.0", "2.0.0", "## 1.0.0\n- old release\n")
    assert rc == 1
