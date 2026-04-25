"""Tests for ci/check_plan_completion.py.

Builds synthetic plan files in tmp_path and runs the validator. The smoke
test at the bottom runs against the real `docs/plans/` and expects exit 0.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_VALIDATOR_PATH = _REPO_ROOT / "ci" / "check_plan_completion.py"
assert _VALIDATOR_PATH.is_file(), f"validator not found: {_VALIDATOR_PATH}"


def _load_validator():
    spec = importlib.util.spec_from_file_location("check_plan_completion", _VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


cpc = _load_validator()


def _write_plan(plans_dir: Path, name: str, frontmatter: dict, body: str) -> Path:
    p = plans_dir / name
    p.parent.mkdir(parents=True, exist_ok=True)
    fm_lines = "\n".join(f"{k}: {v}" for k, v in frontmatter.items())
    p.write_text(f"---\n{fm_lines}\n---\n{body}", encoding="utf-8")
    return p


def test_done_plan_all_ticked_passes(tmp_path: Path) -> None:
    plans = tmp_path / "plans"
    _write_plan(
        plans,
        "p1.md",
        {"status": "done"},
        "# Plan\n\n- [x] T1: ship the thing\n- [x] T2: ship the other thing\n",
    )
    rc = cpc.main(["--plans-dir", str(plans), "--quiet"])
    assert rc == 0


def test_done_plan_with_unticked_task_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    plans = tmp_path / "plans"
    plan_path = _write_plan(
        plans,
        "p1.md",
        {"status": "done"},
        "# Plan\n\n- [x] T1: did this\n- [ ] T2: did NOT do this\n",
    )
    rc = cpc.main(["--plans-dir", str(plans)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "violations found" in err
    assert plan_path.name in err
    assert "T2: did NOT do this" in err


def test_deferred_task_is_acceptable(tmp_path: Path) -> None:
    """`- [~]` is the explicitly-deferred state and must not trigger the lint."""
    plans = tmp_path / "plans"
    _write_plan(
        plans,
        "p1.md",
        {"status": "done"},
        "# Plan\n\n- [x] T1: shipped\n- [~] T2: deferred (NOTE: blocked on upstream)\n",
    )
    rc = cpc.main(["--plans-dir", str(plans), "--quiet"])
    assert rc == 0


def test_planned_status_unticked_is_not_flagged(tmp_path: Path) -> None:
    """Only `done` plans are policed. An in-progress plan can have any state."""
    plans = tmp_path / "plans"
    _write_plan(
        plans,
        "p1.md",
        {"status": "planned"},
        "# Plan\n\n- [ ] T1: future work\n- [ ] T2: more future work\n",
    )
    rc = cpc.main(["--plans-dir", str(plans), "--quiet"])
    assert rc == 0


def test_in_progress_status_unticked_is_not_flagged(tmp_path: Path) -> None:
    plans = tmp_path / "plans"
    _write_plan(
        plans,
        "p1.md",
        {"status": "in-progress"},
        "# Plan\n\n- [x] T1: done already\n- [ ] T2: still working\n",
    )
    rc = cpc.main(["--plans-dir", str(plans), "--quiet"])
    assert rc == 0


def test_missing_frontmatter_is_skipped(tmp_path: Path) -> None:
    """Files without YAML frontmatter (e.g., notes) are not policed."""
    plans = tmp_path / "plans"
    plans.mkdir()
    (plans / "loose-notes.md").write_text(
        "# Just some notes\n\n- [ ] something\n", encoding="utf-8"
    )
    rc = cpc.main(["--plans-dir", str(plans), "--quiet"])
    assert rc == 0


def test_sub_bullets_not_flagged(tmp_path: Path) -> None:
    """A `- [ ]` indented under a parent `- [x]` is a sub-step itemizer.
    Ticking the parent represents the work; sub-bullets must not gate the lint."""
    plans = tmp_path / "plans"
    _write_plan(
        plans,
        "p1.md",
        {"status": "done"},
        (
            "# Plan\n\n"
            "- [x] T1: shipped this\n"
            "  - [ ] sub-step a (itemized for clarity)\n"
            "  - [ ] sub-step b (itemized for clarity)\n"
        ),
    )
    rc = cpc.main(["--plans-dir", str(plans), "--quiet"])
    assert rc == 0


def test_acceptance_criteria_unticked_is_flagged(tmp_path: Path) -> None:
    """Acceptance criteria are top-level checkboxes too — they count."""
    plans = tmp_path / "plans"
    _write_plan(
        plans,
        "p1.md",
        {"status": "done"},
        (
            "# Plan\n\n## Tasks\n\n- [x] T1: shipped\n\n"
            "## Acceptance Criteria\n\n- [ ] AC1: forgot to verify\n"
        ),
    )
    rc = cpc.main(["--plans-dir", str(plans)])
    assert rc == 1


def test_readme_in_plans_dir_is_skipped(tmp_path: Path) -> None:
    """The plans/README.md is the index, not a plan, even if it has unticked items."""
    plans = tmp_path / "plans"
    plans.mkdir()
    (plans / "README.md").write_text(
        "---\nstatus: done\n---\n# Index\n\n- [ ] not a real task\n", encoding="utf-8"
    )
    rc = cpc.main(["--plans-dir", str(plans), "--quiet"])
    assert rc == 0


def test_invalid_yaml_frontmatter_is_skipped(tmp_path: Path) -> None:
    plans = tmp_path / "plans"
    plans.mkdir()
    (plans / "p1.md").write_text(
        "---\nstatus: done\n  bad: : indent\n---\n- [ ] T1: would normally fail\n",
        encoding="utf-8",
    )
    rc = cpc.main(["--plans-dir", str(plans), "--quiet"])
    assert rc == 0


def test_smoke_real_plans_dir_passes() -> None:
    """The repo's own docs/plans/ must pass the lint after T1+T2 fixes.

    This is the regression guard: if a future commit re-introduces a `done`
    plan with unticked tasks, this test catches it before CI runs."""
    rc = cpc.main(["--plans-dir", str(_REPO_ROOT / "docs" / "plans"), "--quiet"])
    assert rc == 0
