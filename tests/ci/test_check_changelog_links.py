"""Tests for ci/check_changelog_links.py."""

from __future__ import annotations

from pathlib import Path

import pytest
from ci.check_changelog_links import lint, main

_REPO_ROOT = Path(__file__).resolve().parents[2]
_OWNER = "altakleos"
_REPO = "sensei"
_BASE = f"https://github.com/{_OWNER}/{_REPO}"


def _changelog(*, headings: list[tuple[str, str]], reflinks: list[tuple[str, str]]) -> str:
    """Compose a minimal CHANGELOG body. headings = [(tag, date)], reflinks = [(tag, url)]."""
    lines = ["# Changelog\n"]
    lines.append("## [Unreleased]\n")
    for tag, date in headings:
        lines.append(f"## [{tag}] — {date}\n")
        lines.append("### Added\n- something\n")
    lines.append("")
    for tag, url in reflinks:
        lines.append(f"[{tag}]: {url}")
    return "\n".join(lines) + "\n"


def test_clean_changelog_passes(tmp_path: Path) -> None:
    cl = tmp_path / "CHANGELOG.md"
    cl.write_text(
        _changelog(
            headings=[("0.1.0a2", "2026-04-21"), ("0.1.0a1", "2026-04-20")],
            reflinks=[
                ("Unreleased", f"{_BASE}/compare/v0.1.0a2...HEAD"),
                ("0.1.0a2", f"{_BASE}/compare/v0.1.0a1...v0.1.0a2"),
                ("0.1.0a1", f"{_BASE}/releases/tag/v0.1.0a1"),
            ],
        )
    )
    assert lint(cl) == []


def test_missing_compare_link_for_heading_fails(tmp_path: Path) -> None:
    cl = tmp_path / "CHANGELOG.md"
    cl.write_text(
        _changelog(
            headings=[("0.1.0a2", "2026-04-21"), ("0.1.0a1", "2026-04-20")],
            reflinks=[
                ("Unreleased", f"{_BASE}/compare/v0.1.0a2...HEAD"),
                # missing [0.1.0a2]: line entirely
                ("0.1.0a1", f"{_BASE}/releases/tag/v0.1.0a1"),
            ],
        )
    )
    violations = lint(cl)
    assert any("heading [0.1.0a2] has no [0.1.0a2]: reference-link entry" in v for v in violations)


def test_unreleased_pointing_at_old_tag_fails(tmp_path: Path) -> None:
    cl = tmp_path / "CHANGELOG.md"
    cl.write_text(
        _changelog(
            headings=[("0.1.0a3", "2026-04-22"), ("0.1.0a2", "2026-04-21"), ("0.1.0a1", "2026-04-20")],
            reflinks=[
                ("Unreleased", f"{_BASE}/compare/v0.1.0a1...HEAD"),  # stale: should be v0.1.0a3
                ("0.1.0a3", f"{_BASE}/compare/v0.1.0a2...v0.1.0a3"),
                ("0.1.0a2", f"{_BASE}/compare/v0.1.0a1...v0.1.0a2"),
                ("0.1.0a1", f"{_BASE}/releases/tag/v0.1.0a1"),
            ],
        )
    )
    violations = lint(cl)
    assert any("[Unreleased] should compare from v0.1.0a3...HEAD" in v for v in violations)


def test_malformed_url_fails(tmp_path: Path) -> None:
    cl = tmp_path / "CHANGELOG.md"
    cl.write_text(
        _changelog(
            headings=[("0.1.0a2", "2026-04-21"), ("0.1.0a1", "2026-04-20")],
            reflinks=[
                ("Unreleased", f"{_BASE}/compare/v0.1.0a2...HEAD"),
                ("0.1.0a2", "https://example.com/not-a-compare-url"),
                ("0.1.0a1", f"{_BASE}/releases/tag/v0.1.0a1"),
            ],
        )
    )
    violations = lint(cl)
    assert any("URL is not a compare URL" in v for v in violations)


def test_compare_pointing_at_wrong_predecessor_fails(tmp_path: Path) -> None:
    cl = tmp_path / "CHANGELOG.md"
    cl.write_text(
        _changelog(
            headings=[("0.1.0a3", "2026-04-22"), ("0.1.0a2", "2026-04-21"), ("0.1.0a1", "2026-04-20")],
            reflinks=[
                ("Unreleased", f"{_BASE}/compare/v0.1.0a3...HEAD"),
                ("0.1.0a3", f"{_BASE}/compare/v0.1.0a1...v0.1.0a3"),  # skips a2
                ("0.1.0a2", f"{_BASE}/compare/v0.1.0a1...v0.1.0a2"),
                ("0.1.0a1", f"{_BASE}/releases/tag/v0.1.0a1"),
            ],
        )
    )
    violations = lint(cl)
    assert any("[0.1.0a3] should compare from v0.1.0a2...v0.1.0a3" in v for v in violations)


def test_missing_changelog_file_returns_1(tmp_path: Path) -> None:
    bogus = tmp_path / "does-not-exist.md"
    assert main(["--changelog", str(bogus)]) == 1


def test_real_repo_changelog_passes() -> None:
    """The shipped CHANGELOG.md must satisfy the validator on every commit."""
    assert lint(_REPO_ROOT / "CHANGELOG.md") == []


def test_main_reports_ok_when_clean(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--changelog", str(_REPO_ROOT / "CHANGELOG.md")]) == 0
    captured = capsys.readouterr()
    assert "OK" in captured.out
