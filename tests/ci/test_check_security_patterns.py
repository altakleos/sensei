"""Tests for ci/check_security_patterns.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "ci" / "check_security_patterns.py"
assert _SCRIPT_PATH.is_file(), f"script not found: {_SCRIPT_PATH}"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_security_patterns", _SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


mod = _load_module()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_clean_file_no_findings(tmp_path: Path) -> None:
    _write(tmp_path / "clean.py", "def hello():\n    return 42\n")
    findings = mod._scan_file(tmp_path / "clean.py")
    assert findings == []


def test_sql_interpolation_detected(tmp_path: Path) -> None:
    _write(tmp_path / "bad.py", 'query = f"SELECT * FROM users WHERE id={uid}"\n')
    findings = mod._scan_file(tmp_path / "bad.py")
    assert any(f["rule"] == "sql-interpolation" for f in findings)


def test_verify_false_detected(tmp_path: Path) -> None:
    _write(tmp_path / "bad.py", "requests.get(url, verify=False)\n")
    findings = mod._scan_file(tmp_path / "bad.py")
    assert any(f["rule"] == "tls-disabled" for f in findings)


def test_chmod_777_detected(tmp_path: Path) -> None:
    _write(tmp_path / "bad.py", "os.chmod(path, 0o777)\n")
    findings = mod._scan_file(tmp_path / "bad.py")
    assert any(f["rule"] == "permissive-mode" for f in findings)


def test_eval_not_in_rules_but_entropy_clean(tmp_path: Path) -> None:
    """eval() is not a pattern this scanner checks — verify no false positive."""
    _write(tmp_path / "bad.py", "result = eval(user_input)\n")
    findings = mod._scan_file(tmp_path / "bad.py")
    # eval is not in the scanner's rule set; should produce no findings.
    assert findings == []


def test_skip_dirs_ignored(tmp_path: Path) -> None:
    _write(tmp_path / ".venv" / "lib" / "bad.py", "requests.get(url, verify=False)\n")
    files = mod._collect_files(tmp_path)
    assert not any(".venv" in str(f) for f in files)
