"""Validator for learner/hints/hints.yaml.

Runs JSON Schema validation (no cross-field invariants needed).

Exits:
    0 — hints file is valid
    1 — parse failure or schema violation

Always prints a single JSON line to stdout summarizing what was checked and
what failed, so protocols can surface the failure to the learner without
parsing stderr.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError as _err:  # pragma: no cover
    print(f"ERROR: Missing dependency ({_err.name}). Install with: pip install sensei-tutor", file=sys.stderr)
    sys.exit(1)

_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "hints.yaml.schema.json"


def _load_schema() -> dict[str, Any]:
    with _SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        schema: dict[str, Any] = json.load(fh)
    return schema


def validate_hints(data: dict[str, Any]) -> tuple[str, list[str]]:
    """Validate a parsed hints dict.

    Returns a tuple (status, errors) where status is one of:
        "ok"     — hints file is valid
        "schema" — schema violations
    """
    schema = _load_schema()
    validator = Draft202012Validator(schema)
    schema_errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    if schema_errors:
        return "schema", [f"{list(e.absolute_path) or '<root>'}: {e.message}" for e in schema_errors]
    return "ok", []


def _emit(status: str, errors: list[str], path: str) -> None:
    print(json.dumps({"path": path, "status": status, "errors": errors}))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--hints-file", required=True, help="Path to hints.yaml")
    args = parser.parse_args(argv)

    path = Path(args.hints_file)
    if not path.is_file():
        _emit("schema", [f"hints file not found: {path}"], str(path))
        return 1

    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        _emit("schema", [f"yaml parse error: {exc}"], str(path))
        return 1

    if not isinstance(data, dict):
        _emit("schema", ["top-level yaml must be a mapping"], str(path))
        return 1

    status, errors = validate_hints(data)
    _emit(status, errors, str(path))
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
