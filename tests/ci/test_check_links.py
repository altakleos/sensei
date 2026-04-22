"""Tests for ci/check_links.py.

Writes small synthetic markdown trees in tmp_path and runs the validator
against each. Verifies: valid links pass, broken file links fail, external
URLs are ignored, same-file anchors are ignored, and fenced code blocks
are skipped. Also includes a sanity test against the real repo docs/ so
the suite surfaces any newly-introduced broken link.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_VALIDATOR_PATH = _REPO_ROOT / "ci" / "check_links.py"
assert _VALIDATOR_PATH.is_file(), f"validator not found: {_VALIDATOR_PATH}"


def _load_validator():
    spec = importlib.util.spec_from_file_location("check_links", _VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


cl = _load_validator()


def test_valid_relative_link_passes(tmp_path: Path) -> None:
    (tmp_path / "target.md").write_text("# target\n", encoding="utf-8")
    (tmp_path / "source.md").write_text(
        "See [target](target.md) for details.\n", encoding="utf-8"
    )
    assert cl.check_links(tmp_path) == []


def test_broken_relative_link_fails(tmp_path: Path) -> None:
    (tmp_path / "source.md").write_text(
        "See [gone](missing.md) — does not exist.\n", encoding="utf-8"
    )
    errors = cl.check_links(tmp_path)
    assert len(errors) == 1
    assert "missing.md" in errors[0]
    assert "source.md" in errors[0]


def test_link_with_fragment_anchor_validates_file_part(tmp_path: Path) -> None:
    (tmp_path / "target.md").write_text("# target\n\n## section\n", encoding="utf-8")
    (tmp_path / "source.md").write_text(
        "Jump to [the section](target.md#section).\n", encoding="utf-8"
    )
    assert cl.check_links(tmp_path) == []


def test_broken_file_with_fragment_still_fails(tmp_path: Path) -> None:
    (tmp_path / "source.md").write_text(
        "Jump to [gone](missing.md#section).\n", encoding="utf-8"
    )
    errors = cl.check_links(tmp_path)
    assert len(errors) == 1
    assert "missing.md" in errors[0]


def test_same_file_anchor_ignored(tmp_path: Path) -> None:
    """Pure #anchor links reference the current document; no file to check."""
    (tmp_path / "source.md").write_text(
        "See [above](#introduction).\n", encoding="utf-8"
    )
    assert cl.check_links(tmp_path) == []


def test_external_urls_ignored(tmp_path: Path) -> None:
    """http/https/mailto links are not validated — we don't hit the network."""
    (tmp_path / "source.md").write_text(
        "[github](https://github.com/altakleos/sensei) "
        "[http](http://example.com/page) "
        "[email](mailto:test@example.com)\n",
        encoding="utf-8",
    )
    assert cl.check_links(tmp_path) == []


def test_fenced_code_block_links_skipped(tmp_path: Path) -> None:
    """Links inside ``` ... ``` blocks are illustrative, not real links."""
    (tmp_path / "source.md").write_text(
        "Some prose.\n\n"
        "```markdown\n"
        "[not-a-real-link](does-not-exist.md)\n"
        "```\n",
        encoding="utf-8",
    )
    assert cl.check_links(tmp_path) == []


def test_link_outside_code_block_still_checked(tmp_path: Path) -> None:
    """Toggling in/out of a code block must not leak skip-state past the close."""
    (tmp_path / "source.md").write_text(
        "```\n"
        "[inside](inside.md)\n"
        "```\n"
        "\n"
        "[outside](outside.md)\n",
        encoding="utf-8",
    )
    errors = cl.check_links(tmp_path)
    # Only the outside link is validated and should fail.
    assert len(errors) == 1
    assert "outside.md" in errors[0]


def test_image_links_validated(tmp_path: Path) -> None:
    """![alt](path) is a markdown image link; the path must resolve."""
    (tmp_path / "source.md").write_text(
        "![broken](missing.png)\n", encoding="utf-8"
    )
    errors = cl.check_links(tmp_path)
    assert len(errors) == 1
    assert "missing.png" in errors[0]


def test_nested_subdirectory_resolves_correctly(tmp_path: Path) -> None:
    (tmp_path / "sub").mkdir()
    (tmp_path / "root-target.md").write_text("", encoding="utf-8")
    (tmp_path / "sub" / "source.md").write_text(
        "Up one: [root](../root-target.md).\n", encoding="utf-8"
    )
    assert cl.check_links(tmp_path) == []


def test_broken_up_one_link_fails(tmp_path: Path) -> None:
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "source.md").write_text(
        "Up one: [missing](../missing.md).\n", encoding="utf-8"
    )
    errors = cl.check_links(tmp_path)
    assert len(errors) == 1
    assert "missing.md" in errors[0]


def test_link_to_directory_passes(tmp_path: Path) -> None:
    """Linking to a directory (trailing slash) passes when the dir exists."""
    (tmp_path / "subdir").mkdir()
    (tmp_path / "source.md").write_text(
        "See [the dir](subdir/).\n", encoding="utf-8"
    )
    assert cl.check_links(tmp_path) == []


def test_main_exits_zero_on_ok(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "target.md").write_text("", encoding="utf-8")
    (tmp_path / "source.md").write_text("[ok](target.md)\n", encoding="utf-8")
    rc = cl.main(["--root", str(tmp_path)])
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["status"] == "ok"
    assert parsed["errors"] == []


def test_main_exits_one_on_broken(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "source.md").write_text("[gone](missing.md)\n", encoding="utf-8")
    rc = cl.main(["--root", str(tmp_path)])
    assert rc == 1
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["status"] == "fail"
    assert len(parsed["errors"]) == 1


def test_main_rejects_missing_root(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = cl.main(["--root", str(tmp_path / "nope")])
    assert rc == 1
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["status"] == "fail"


def test_real_repo_docs_tree_has_no_broken_links() -> None:
    """Sanity guard: the repo's own docs/ tree validates clean.

    If this fails, a new broken link has landed on main. Run
    `python ci/check_links.py` locally to see the broken references.
    """
    errors = cl.check_links(_REPO_ROOT / "docs")
    assert errors == [], "broken links in docs/:\n  " + "\n  ".join(errors)
