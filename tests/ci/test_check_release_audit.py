"""Tests for ci/check_release_audit.py."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from ci.check_release_audit import REQUIRED_FIELDS, REQUIRED_GATE_TESTS, lint, main

_HEX64 = "a" * 64

# A body that mentions all seven ADR-0027 test paths satisfies the
# ADR-0028 breadth check. Existing happy-path tests rely on this.
_GATE_TEST_LINES = "\n".join(f"  {p}" for p in REQUIRED_GATE_TESTS)

_VALID_BODY = (
    "# Release vX.Y.Z — Tier-2 E2E Audit Log\n\n"
    "## Invocation\n\n"
    f"{_GATE_TEST_LINES}\n\n"
    "## Result\n\n7 passed, 0 failed.\n"
)

# A body that lists only the original three (pre-ADR-0027) tests. Used by
# the legacy-log breadth test to document the forward-looking-gate intent.
_LEGACY_THREE_TEST_BODY = (
    "# Release vX.Y.Z — Tier-2 E2E Audit Log\n\n"
    "## Invocation\n\n"
    "  tests/e2e/test_goal_protocol_e2e.py\n"
    "  tests/e2e/test_assess_protocol_e2e.py\n"
    "  tests/e2e/test_hints_protocol_e2e.py\n\n"
    "## Result\n\n3 passed, 0 failed.\n"
)


def _audit_file(
    tmp_path: Path,
    *,
    tag: str = "v0.1.0a20",
    overrides: dict[str, object] | None = None,
    drop: tuple[str, ...] = (),
    raw_frontmatter: str | None = None,
    body: str = _VALID_BODY,
    filename: str | None = None,
) -> Path:
    """Compose a releases/<tag>.md fixture under *tmp_path*."""
    fields: dict[str, object] = {
        "tag": tag,
        "date": "2026-05-01",
        "tester": "makutaku",
        "tool": "claude",
        "tool_version": "0.5.0",
        "exit_code": 0,
        "transcript_hash": _HEX64,
    }
    if overrides:
        fields.update(overrides)
    for k in drop:
        fields.pop(k, None)

    if raw_frontmatter is None:
        # safe_dump preserves types — string '0' stays quoted, int 0 stays int —
        # so an override like {'exit_code': '0'} round-trips as a string and the
        # validator can reject it.
        body_yaml = yaml.safe_dump(fields, sort_keys=False)
        frontmatter = f"---\n{body_yaml}---\n"
    else:
        frontmatter = raw_frontmatter

    releases_dir = tmp_path / "docs" / "operations" / "releases"
    releases_dir.mkdir(parents=True)
    path = releases_dir / (filename or f"{tag}.md")
    path.write_text(frontmatter + body, encoding="utf-8")
    return path


# ------------------------------ happy paths -------------------------------- #


def test_clean_audit_log_passes(tmp_path: Path) -> None:
    path = _audit_file(tmp_path)
    assert lint(path, "v0.1.0a20") == []


def test_transcript_hash_na_passes(tmp_path: Path) -> None:
    path = _audit_file(tmp_path, overrides={"transcript_hash": "n/a"})
    assert lint(path, "v0.1.0a20") == []


def test_tool_kiro_passes(tmp_path: Path) -> None:
    path = _audit_file(tmp_path, overrides={"tool": "kiro"})
    assert lint(path, "v0.1.0a20") == []


def test_tool_other_prefixed_passes(tmp_path: Path) -> None:
    path = _audit_file(tmp_path, overrides={"tool": "other:cline-0.7"})
    assert lint(path, "v0.1.0a20") == []


# ------------------------------ file-level --------------------------------- #


def test_missing_file_fails(tmp_path: Path) -> None:
    bogus = tmp_path / "docs" / "operations" / "releases" / "v0.1.0a20.md"
    violations = lint(bogus, "v0.1.0a20")
    assert any("audit log not found" in v for v in violations)


def test_no_frontmatter_block_fails(tmp_path: Path) -> None:
    path = _audit_file(tmp_path, raw_frontmatter="not a frontmatter\n")
    violations = lint(path, "v0.1.0a20")
    assert any("frontmatter" in v for v in violations)


def test_unclosed_frontmatter_fails(tmp_path: Path) -> None:
    path = _audit_file(
        tmp_path,
        raw_frontmatter="---\ntag: v0.1.0a20\n",  # no closing fence
        body="\n# body without closing fence\n",
    )
    violations = lint(path, "v0.1.0a20")
    assert any("closing '---' fence" in v for v in violations)


def test_malformed_yaml_frontmatter_fails(tmp_path: Path) -> None:
    path = _audit_file(
        tmp_path,
        raw_frontmatter="---\ntag: : :\n  - bad\n---\n",
    )
    violations = lint(path, "v0.1.0a20")
    assert any("invalid YAML frontmatter" in v for v in violations)


def test_empty_frontmatter_fails(tmp_path: Path) -> None:
    path = _audit_file(tmp_path, raw_frontmatter="---\n---\n")
    violations = lint(path, "v0.1.0a20")
    assert any("frontmatter is empty" in v for v in violations)


def test_non_mapping_frontmatter_fails(tmp_path: Path) -> None:
    path = _audit_file(tmp_path, raw_frontmatter="---\n- one\n- two\n---\n")
    violations = lint(path, "v0.1.0a20")
    assert any("not a mapping" in v for v in violations)


# ------------------------------ field presence ----------------------------- #


@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_each_missing_required_field_fails(tmp_path: Path, field: str) -> None:
    path = _audit_file(tmp_path, drop=(field,))
    violations = lint(path, "v0.1.0a20")
    assert any(f"missing required field {field!r}" in v for v in violations)


def test_empty_required_field_fails(tmp_path: Path) -> None:
    path = _audit_file(tmp_path, overrides={"tester": ""})
    violations = lint(path, "v0.1.0a20")
    assert any("required field 'tester' is empty" in v for v in violations)


def test_null_required_field_fails(tmp_path: Path) -> None:
    path = _audit_file(
        tmp_path,
        raw_frontmatter=(
            "---\n"
            "tag: v0.1.0a20\n"
            "date: 2026-05-01\n"
            "tester: makutaku\n"
            "tool: claude\n"
            "tool_version: '0.5.0'\n"
            "exit_code: 0\n"
            "transcript_hash:\n"
            "---\n"
        ),
    )
    violations = lint(path, "v0.1.0a20")
    assert any("required field 'transcript_hash' is empty" in v for v in violations)


# ------------------------------ field semantics ---------------------------- #


def test_tag_mismatch_fails(tmp_path: Path) -> None:
    path = _audit_file(tmp_path, tag="v0.1.0a19")
    violations = lint(path, "v0.1.0a20")
    assert any("does not match expected tag" in v for v in violations)


def test_nonzero_exit_code_fails(tmp_path: Path) -> None:
    path = _audit_file(tmp_path, overrides={"exit_code": 1})
    violations = lint(path, "v0.1.0a20")
    assert any("exit_code is 1" in v for v in violations)


def test_non_integer_exit_code_fails(tmp_path: Path) -> None:
    path = _audit_file(tmp_path, overrides={"exit_code": "0"})
    violations = lint(path, "v0.1.0a20")
    assert any("exit_code must be an integer" in v for v in violations)


def test_boolean_exit_code_rejected(tmp_path: Path) -> None:
    # YAML coerces `false` to bool; bool is a subclass of int and must be rejected.
    path = _audit_file(
        tmp_path,
        raw_frontmatter=(
            "---\n"
            "tag: v0.1.0a20\n"
            "date: 2026-05-01\n"
            "tester: makutaku\n"
            "tool: claude\n"
            "tool_version: '0.5.0'\n"
            "exit_code: false\n"
            f"transcript_hash: {_HEX64}\n"
            "---\n"
        ),
    )
    violations = lint(path, "v0.1.0a20")
    assert any("exit_code must be an integer" in v for v in violations)


def test_uppercase_transcript_hash_rejected(tmp_path: Path) -> None:
    path = _audit_file(tmp_path, overrides={"transcript_hash": "A" * 64})
    violations = lint(path, "v0.1.0a20")
    assert any("transcript_hash" in v for v in violations)


def test_short_transcript_hash_rejected(tmp_path: Path) -> None:
    path = _audit_file(tmp_path, overrides={"transcript_hash": "a" * 63})
    violations = lint(path, "v0.1.0a20")
    assert any("transcript_hash" in v for v in violations)


def test_non_hex_transcript_hash_rejected(tmp_path: Path) -> None:
    path = _audit_file(tmp_path, overrides={"transcript_hash": "z" * 64})
    violations = lint(path, "v0.1.0a20")
    assert any("transcript_hash" in v for v in violations)


def test_unknown_tool_rejected(tmp_path: Path) -> None:
    path = _audit_file(tmp_path, overrides={"tool": "cursor"})
    violations = lint(path, "v0.1.0a20")
    assert any("tool:" in v for v in violations)


def test_other_prefix_without_value_rejected(tmp_path: Path) -> None:
    path = _audit_file(tmp_path, overrides={"tool": "other:"})
    violations = lint(path, "v0.1.0a20")
    assert any("tool:" in v for v in violations)


def test_non_string_tool_rejected(tmp_path: Path) -> None:
    path = _audit_file(
        tmp_path,
        raw_frontmatter=(
            "---\n"
            "tag: v0.1.0a20\n"
            "date: 2026-05-01\n"
            "tester: makutaku\n"
            "tool: 42\n"
            "tool_version: '0.5.0'\n"
            "exit_code: 0\n"
            f"transcript_hash: {_HEX64}\n"
            "---\n"
        ),
    )
    violations = lint(path, "v0.1.0a20")
    assert any("tool: must be a non-empty string" in v for v in violations)


# ---------------------- body breadth (ADR-0028) ---------------------------- #


def test_body_breadth_complete(tmp_path: Path) -> None:
    """All seven ADR-0027 test paths present → no breadth violation."""
    path = _audit_file(tmp_path)  # _VALID_BODY embeds all seven paths
    assert lint(path, "v0.1.0a20") == []


def test_body_breadth_missing_one(tmp_path: Path) -> None:
    """One test path absent → exactly one breadth violation naming it."""
    body = _VALID_BODY.replace("  tests/e2e/test_challenger_protocol_e2e.py\n", "")
    path = _audit_file(tmp_path, body=body)
    violations = lint(path, "v0.1.0a20")
    breadth = [v for v in violations if "missing required test path" in v]
    assert len(breadth) == 1, breadth
    assert "test_challenger_protocol_e2e.py" in breadth[0]
    assert "ADR-0027/0028" in breadth[0]


def test_body_breadth_missing_all(tmp_path: Path) -> None:
    """Empty body → seven breadth violations, one per required path."""
    path = _audit_file(tmp_path, body="")
    violations = lint(path, "v0.1.0a20")
    breadth = [v for v in violations if "missing required test path" in v]
    assert len(breadth) == 7
    for required_path in REQUIRED_GATE_TESTS:
        assert any(required_path in v for v in breadth), (
            f"path {required_path!r} not flagged in {breadth!r}"
        )


def test_legacy_three_test_log_fails_breadth(tmp_path: Path) -> None:
    """A pre-ADR-0027 audit log with only three paths fails on the four added.

    Documents the forward-looking-gate intent of ADR-0028: legacy logs
    aren't backfilled, but if the validator is run against one (e.g. for
    archaeology) it surfaces exactly the gap that motivated ADR-0027.
    """
    path = _audit_file(tmp_path, body=_LEGACY_THREE_TEST_BODY)
    violations = lint(path, "v0.1.0a20")
    breadth = [v for v in violations if "missing required test path" in v]
    assert len(breadth) == 4, breadth
    expected_missing = {
        "test_tutor_protocol_e2e.py",
        "test_review_protocol_e2e.py",
        "test_reviewer_protocol_e2e.py",
        "test_challenger_protocol_e2e.py",
    }
    found_missing = {
        path_str
        for v in breadth
        for path_str in expected_missing
        if path_str in v
    }
    assert found_missing == expected_missing, breadth


# --------------------------------- main ------------------------------------ #


def test_main_returns_0_on_clean(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _audit_file(tmp_path)
    rc = main(
        [
            "--tag",
            "v0.1.0a20",
            "--releases-dir",
            str(tmp_path / "docs" / "operations" / "releases"),
        ]
    )
    assert rc == 0
    captured = capsys.readouterr()
    assert "OK" in captured.out


def test_main_returns_1_on_missing_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(
        [
            "--tag",
            "v0.1.0a20",
            "--releases-dir",
            str(tmp_path),
        ]
    )
    assert rc == 1
    captured = capsys.readouterr()
    assert "violations found" in captured.err


def test_main_quiet_suppresses_ok_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _audit_file(tmp_path)
    rc = main(
        [
            "--tag",
            "v0.1.0a20",
            "--releases-dir",
            str(tmp_path / "docs" / "operations" / "releases"),
            "--quiet",
        ]
    )
    assert rc == 0
    captured = capsys.readouterr()
    assert captured.out == ""
