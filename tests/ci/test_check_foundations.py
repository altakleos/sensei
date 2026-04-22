"""Tests for ci/check_foundations.py."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_VALIDATOR_PATH = _REPO_ROOT / "ci" / "check_foundations.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location("check_foundations", _VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


cfn = _load_validator()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _principle_file(tmp_path: Path, slug: str, kind: str = "pedagogical", status: str = "accepted") -> Path:
    p = tmp_path / "foundations" / "principles" / f"{slug.replace('P-', '')}.md"
    _write(
        p,
        f"---\nstatus: {status}\ndate: 2026-04-20\nid: {slug}\nkind: {kind}\n---\n"
        f"# {slug}\n## Statement\nX.\n## Rationale\nY.\n## Implications\nZ.\n",
    )
    return p


def _persona_file(tmp_path: Path, slug: str, stresses: list[str] | None = None, status: str = "accepted") -> Path:
    p = tmp_path / "foundations" / "personas" / f"{slug.replace('persona-', '')}.md"
    stresses_yaml = "[]" if not stresses else "[" + ", ".join(f"{s!r}" for s in stresses) + "]"
    _write(
        p,
        f"---\nstatus: {status}\nowner: test\nid: {slug}\nstresses: {stresses_yaml}\n---\n"
        f"# {slug}\n## Scenario\nX.\n",
    )
    return p


def _spec_file(
    tmp_path: Path, name: str, serves=None, realizes=None, stressed_by=None, fixtures=None, fixtures_deferred=None
) -> Path:
    p = tmp_path / "specs" / f"{name}.md"
    fm_lines = ["---", "status: accepted", "date: 2026-04-20"]
    for field, value in [
        ("serves", serves), ("realizes", realizes), ("stressed_by", stressed_by), ("fixtures", fixtures)
    ]:
        if value is not None:
            fm_lines.append(f"{field}: [" + ", ".join(f"{v!r}" for v in value) + "]")
    if fixtures_deferred is not None:
        fm_lines.append(f"fixtures_deferred: {fixtures_deferred!r}")
    fm_lines.append("---")
    _write(p, "\n".join(fm_lines) + f"\n# {name}\n")
    return p


def test_empty_foundations_ok(tmp_path: Path) -> None:
    (tmp_path / "foundations").mkdir()
    (tmp_path / "specs").mkdir()
    errors, warnings = cfn.check(tmp_path / "foundations", tmp_path / "specs")
    assert errors == []
    assert warnings == []


def test_valid_references_ok(tmp_path: Path) -> None:
    _principle_file(tmp_path, "P-prose-is-code", kind="technical")
    _spec_file(tmp_path, "my-feature", realizes=["P-prose-is-code"], fixtures=["tests/test_something.py"])
    errors, warnings = cfn.check(tmp_path / "foundations", tmp_path / "specs")
    assert errors == [], errors
    assert not any("does not resolve" in w or "not referenced" in w for w in warnings), warnings


def test_broken_realizes_fails(tmp_path: Path) -> None:
    _spec_file(tmp_path, "my-feature", realizes=["P-does-not-exist"])
    (tmp_path / "foundations").mkdir()
    errors, warnings = cfn.check(tmp_path / "foundations", tmp_path / "specs")
    assert errors, "expected an error for unresolved realizes"
    assert any("does not resolve" in e for e in errors)


def test_broken_serves_fails(tmp_path: Path) -> None:
    _spec_file(tmp_path, "my-feature", serves=["vision"])
    (tmp_path / "foundations").mkdir()
    errors, _ = cfn.check(tmp_path / "foundations", tmp_path / "specs")
    assert any("'vision'" in e and "does not resolve" in e for e in errors)


def test_broken_stressed_by_fails(tmp_path: Path) -> None:
    _spec_file(tmp_path, "my-feature", stressed_by=["persona-ghost"])
    (tmp_path / "foundations").mkdir()
    errors, _ = cfn.check(tmp_path / "foundations", tmp_path / "specs")
    assert any("persona-ghost" in e for e in errors)


def test_invalid_kind_fails(tmp_path: Path) -> None:
    _principle_file(tmp_path, "P-bogus", kind="aesthetic")
    (tmp_path / "specs").mkdir()
    errors, _ = cfn.check(tmp_path / "foundations", tmp_path / "specs")
    assert any("invalid kind" in e for e in errors)


def test_vision_resolves(tmp_path: Path) -> None:
    vision = tmp_path / "foundations" / "vision.md"
    _write(vision, "---\nstatus: accepted\ndate: 2026-04-20\n---\n# Vision\n")
    _spec_file(tmp_path, "my-feature", serves=["vision"], fixtures=["tests/test_something.py"])
    errors, _ = cfn.check(tmp_path / "foundations", tmp_path / "specs")
    assert errors == [], errors


def test_persona_stresses_spec_ok(tmp_path: Path) -> None:
    _spec_file(tmp_path, "my-feature")
    _persona_file(tmp_path, "persona-jacundu", stresses=["my-feature"])
    errors, _ = cfn.check(tmp_path / "foundations", tmp_path / "specs")
    assert errors == [], errors


def test_persona_stresses_broken_slug_fails(tmp_path: Path) -> None:
    _persona_file(tmp_path, "persona-jacundu", stresses=["does-not-exist"])
    (tmp_path / "specs").mkdir()
    errors, _ = cfn.check(tmp_path / "foundations", tmp_path / "specs")
    assert any("does not resolve" in e for e in errors)


def test_persona_stresses_principle_ok(tmp_path: Path) -> None:
    _principle_file(tmp_path, "P-silence", kind="pedagogical")
    _persona_file(tmp_path, "persona-jacundu", stresses=["P-silence"])
    errors, _ = cfn.check(tmp_path / "foundations", tmp_path / "specs")
    assert errors == [], errors


def test_orphan_principle_is_warning_not_error(tmp_path: Path) -> None:
    _principle_file(tmp_path, "P-lonely", kind="pedagogical")
    (tmp_path / "specs").mkdir()
    errors, warnings = cfn.check(tmp_path / "foundations", tmp_path / "specs")
    assert errors == []
    assert any("P-lonely" in w and "not referenced" in w for w in warnings)


def test_non_accepted_principle_not_warned(tmp_path: Path) -> None:
    _principle_file(tmp_path, "P-draft", kind="pedagogical", status="draft")
    (tmp_path / "specs").mkdir()
    errors, warnings = cfn.check(tmp_path / "foundations", tmp_path / "specs")
    assert warnings == []


def test_main_exits_0_on_ok(tmp_path: Path) -> None:
    (tmp_path / "foundations").mkdir()
    (tmp_path / "specs").mkdir()
    rc = cfn.main(["--foundations", str(tmp_path / "foundations"), "--specs", str(tmp_path / "specs")])
    assert rc == 0


def test_main_exits_1_on_broken_ref(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _spec_file(tmp_path, "my-feature", realizes=["P-missing"])
    (tmp_path / "foundations").mkdir()
    rc = cfn.main(["--foundations", str(tmp_path / "foundations"), "--specs", str(tmp_path / "specs")])
    assert rc == 1
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert parsed["status"] == "fail"


def test_main_warnings_as_errors_blocks_on_orphan(tmp_path: Path) -> None:
    _principle_file(tmp_path, "P-lonely", kind="pedagogical")
    (tmp_path / "specs").mkdir()
    rc = cfn.main(
        [
            "--foundations", str(tmp_path / "foundations"),
            "--specs", str(tmp_path / "specs"),
            "--warnings-as-errors",
        ]
    )
    assert rc == 1


def _spec_with_fixtures(
    tmp_path: Path,
    name: str,
    realizes: list[str] | None = None,
    fixtures: list[str] | None = None,
    fixtures_deferred: str | None = None,
) -> Path:
    """Variant of _spec_file that adds fixture-naming frontmatter fields."""
    p = tmp_path / "specs" / f"{name}.md"
    fm_lines = ["---", "status: accepted", "date: 2026-04-20"]
    if realizes is not None:
        fm_lines.append("realizes: [" + ", ".join(f"{v!r}" for v in realizes) + "]")
    if fixtures is not None:
        fm_lines.append("fixtures: [" + ", ".join(f"{v!r}" for v in fixtures) + "]")
    if fixtures_deferred is not None:
        fm_lines.append(f"fixtures_deferred: {fixtures_deferred!r}")
    fm_lines.append("---")
    _write(p, "\n".join(fm_lines) + f"\n# {name}\n")
    return p


def test_spec_with_fixtures_emits_no_fixture_warning(tmp_path: Path) -> None:
    _principle_file(tmp_path, "P-prose-is-code", kind="technical")
    _spec_with_fixtures(
        tmp_path,
        "named",
        realizes=["P-prose-is-code"],
        fixtures=["tests/scripts/test_check_profile.py"],
    )
    errors, warnings = cfn.check(tmp_path / "foundations", tmp_path / "specs")
    assert errors == [], errors
    assert not any("names no 'fixtures:'" in w for w in warnings)


def test_spec_without_fixtures_or_defer_emits_error(tmp_path: Path) -> None:
    _principle_file(tmp_path, "P-prose-is-code", kind="technical")
    _spec_with_fixtures(tmp_path, "unnamed", realizes=["P-prose-is-code"])
    errors, warnings = cfn.check(tmp_path / "foundations", tmp_path / "specs")
    assert any(
        "unnamed.md" in e and "names no 'fixtures:'" in e for e in errors
    ), errors


def test_spec_with_fixtures_deferred_suppresses_warning(tmp_path: Path) -> None:
    _principle_file(tmp_path, "P-prose-is-code", kind="technical")
    _spec_with_fixtures(
        tmp_path,
        "deferred",
        realizes=["P-prose-is-code"],
        fixtures_deferred="awaiting first learner session",
    )
    errors, warnings = cfn.check(tmp_path / "foundations", tmp_path / "specs")
    assert errors == [], errors
    assert not any("deferred.md" in w and "fixtures" in w for w in warnings)


def test_spec_without_realizes_or_serves_emits_no_fixture_warning(tmp_path: Path) -> None:
    """Specs that don't claim to realize/serve anything aren't required to name fixtures."""
    _spec_with_fixtures(tmp_path, "bare")
    errors, warnings = cfn.check(tmp_path / "foundations", tmp_path / "specs")
    assert errors == [], errors
    assert not any("bare.md" in w and "fixtures" in w for w in warnings)


def test_real_repo_passes() -> None:
    """The repo's actual foundations + specs must pass (once populated)."""
    foundations = _REPO_ROOT / "docs" / "foundations"
    specs = _REPO_ROOT / "docs" / "specs"
    if not foundations.is_dir():
        pytest.skip("foundations not yet populated")
    errors, _ = cfn.check(foundations, specs)
    assert errors == [], errors
