"""Tests for ci/check_package_contents.py.

Builds synthetic wheels on-the-fly with zipfile and runs the validator
against each. Does not invoke the real pip-built wheel — keeps tests
fast and deterministic.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import zipfile
from pathlib import Path
from typing import Iterable

import pytest


_REPO_ROOT = Path(__file__).resolve().parents[2]
_VALIDATOR_PATH = _REPO_ROOT / "ci" / "check_package_contents.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location("check_package_contents", _VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


cpc = _load_validator()


def _good_files(version: str = "0.0.0") -> dict[str, str | bytes]:
    """Return the minimal file-set the validator accepts as a passing wheel."""
    return {
        "sensei/__init__.py": f'__version__ = "{version}"\n',
        "sensei/engine/engine.md": "# engine\n",
        "sensei/engine/defaults.yaml": "schema_version: 0\n",
        "sensei/engine/protocols/README.md": "# protocols\n",
        "sensei/engine/protocols/review.md": "# review\n",
        "sensei/engine/scripts/config.py": "# config\n",
        "sensei/engine/scripts/check_profile.py": "# check_profile\n",
        "sensei/engine/scripts/mastery_check.py": "# mastery_check\n",
        "sensei/engine/scripts/decay.py": "# decay\n",
        "sensei/engine/scripts/classify_confidence.py": "# classify\n",
        "sensei/engine/schemas/profile.schema.json": "{}",
        "sensei/engine/prompts/README.md": "# prompts\n",
        "sensei/engine/profiles/README.md": "# profiles\n",
        "sensei-0.0.0.dist-info/METADATA": "Name: sensei\n",
    }


def _make_wheel(tmp_path: Path, files: dict[str, str | bytes], name: str = "sensei-0.0.0-py3-none-any.whl") -> Path:
    wheel = tmp_path / name
    with zipfile.ZipFile(wheel, "w") as z:
        for path, content in files.items():
            if isinstance(content, str):
                content = content.encode("utf-8")
            z.writestr(path, content)
    return wheel


def _invoke(wheel: Path, tag: str) -> tuple[int, dict]:
    rc = cpc.main(["--wheel", str(wheel), "--tag", tag])
    return rc, {}  # main already printed; for structured output use check_wheel


def test_happy_path(tmp_path: Path) -> None:
    wheel = _make_wheel(tmp_path, _good_files())
    rc, report = cpc.check_wheel(wheel, "v0.0.0")
    assert rc == 0, report
    assert report["status"] == "ok"


@pytest.mark.parametrize(
    "removed",
    [
        "sensei/__init__.py",
        "sensei/engine/engine.md",
        "sensei/engine/defaults.yaml",
        "sensei/engine/protocols/review.md",
        "sensei/engine/scripts/config.py",
        "sensei/engine/scripts/check_profile.py",
        "sensei/engine/scripts/mastery_check.py",
        "sensei/engine/scripts/decay.py",
        "sensei/engine/scripts/classify_confidence.py",
        "sensei/engine/schemas/profile.schema.json",
    ],
)
def test_missing_required_file(tmp_path: Path, removed: str) -> None:
    files = _good_files()
    files.pop(removed)
    wheel = _make_wheel(tmp_path, files)
    rc, report = cpc.check_wheel(wheel, "v0.0.0")
    assert rc == 1, report
    assert report["status"] == "missing"
    assert removed in report["missing_files"]


@pytest.mark.parametrize(
    "empty_dir_marker,expected_missing",
    [
        ("sensei/engine/prompts/README.md", "sensei/engine/prompts/"),
        ("sensei/engine/profiles/README.md", "sensei/engine/profiles/"),
    ],
)
def test_required_directory_empty(tmp_path: Path, empty_dir_marker: str, expected_missing: str) -> None:
    files = _good_files()
    files.pop(empty_dir_marker)
    wheel = _make_wheel(tmp_path, files)
    rc, report = cpc.check_wheel(wheel, "v0.0.0")
    assert rc == 1, report
    assert expected_missing in report["missing_dirs"]


@pytest.mark.parametrize(
    "forbidden_path",
    [
        "instance/profile.yaml",
        "wiki/index.md",
        "raw/source.txt",
        "notebook/notes.md",
        "inbox/incoming.md",
        "memory/rules.yaml",
        ".kiro/steering/sensei.md",
        ".cursor/rules/sensei.mdc",
        ".windsurf/rules/sensei.md",
        ".clinerules/sensei.md",
        ".roo/rules/sensei.md",
        ".aiassistant/rules/sensei.md",
        ".github/copilot-instructions.md",
        "AGENTS.md",
        "CLAUDE.md",
    ],
)
def test_forbidden_path(tmp_path: Path, forbidden_path: str) -> None:
    files = _good_files()
    files[forbidden_path] = "leaked\n"
    wheel = _make_wheel(tmp_path, files)
    rc, report = cpc.check_wheel(wheel, "v0.0.0")
    assert rc == 2, report
    assert report["status"] == "forbidden"
    assert forbidden_path in report["forbidden"]


def test_version_mismatch(tmp_path: Path) -> None:
    files = _good_files(version="0.0.0")
    wheel = _make_wheel(tmp_path, files)
    rc, report = cpc.check_wheel(wheel, "v0.1.0")
    assert rc == 3, report
    assert report["status"] == "version_mismatch"
    assert report["expected_version"] == "0.1.0"
    assert report["actual_version"] == "0.0.0"


def test_version_matches_prerelease_literally(tmp_path: Path) -> None:
    files = _good_files(version="0.1.0-alpha")
    wheel = _make_wheel(tmp_path, files)
    rc, report = cpc.check_wheel(wheel, "v0.1.0-alpha")
    assert rc == 0, report


def test_version_missing_is_mismatch(tmp_path: Path) -> None:
    files = _good_files()
    files["sensei/__init__.py"] = "# no version here\n"
    wheel = _make_wheel(tmp_path, files)
    rc, report = cpc.check_wheel(wheel, "v0.1.0")
    assert rc == 3, report
    assert report["status"] == "version_mismatch"
    assert report["actual_version"] is None


def test_wheel_not_found_exits_1() -> None:
    rc = cpc.main(["--wheel", "/tmp/definitely-not-a-wheel.whl", "--tag", "v0.0.0"])
    assert rc == 1


def test_main_emits_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    wheel = _make_wheel(tmp_path, _good_files())
    rc = cpc.main(["--wheel", str(wheel), "--tag", "v0.0.0"])
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["status"] == "ok"
    assert parsed["tag"] == "v0.0.0"
    assert parsed["expected_version"] == "0.0.0"
    assert parsed["actual_version"] == "0.0.0"


def test_strips_leading_v() -> None:
    assert cpc._strip_v("v1.2.3") == "1.2.3"
    assert cpc._strip_v("1.2.3") == "1.2.3"  # no-op if no leading v
