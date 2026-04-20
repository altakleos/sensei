"""Cross-cutting layer linter (maintainer-side, CI hard-fail).

Validates that:
- Every `serves:` / `realizes:` / `stressed_by:` slug in any spec resolves to an
  existing foundation file of the matching type.
- Every `stresses:` slug in any persona resolves to a spec or foundation.
- Every principle file carries a valid `kind:` in {pedagogical, technical, product}.

Warns (non-blocking at v1):
- Any accepted principle not referenced by any spec. Will promote to hard-fail
  in a later ADR once the backreference wiring has settled.

Exit codes:
    0 — all checks pass (warnings may be present)
    1 — one or more broken references or invalid kind values

Per [ADR-0012](docs/decisions/0012-foundations-layer.md) and
[docs/foundations/README.md](docs/foundations/README.md).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_FOUNDATIONS = _REPO_ROOT / "docs" / "foundations"
_DEFAULT_SPECS = _REPO_ROOT / "docs" / "specs"

VALID_KINDS: frozenset[str] = frozenset({"pedagogical", "technical", "product"})


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    try:
        fm = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError:
        return {}, text
    body = text[end + len("\n---\n"):]
    return fm, body


def _load_md(path: Path) -> dict[str, Any]:
    fm, _ = _split_frontmatter(path.read_text(encoding="utf-8"))
    return fm


def discover_allowed_slugs(foundations_root: Path) -> dict[str, dict[str, Any]]:
    """Return a map of slug → {path, type, kind?, status?}."""
    allowed: dict[str, dict[str, Any]] = {}

    vision = foundations_root / "vision.md"
    if vision.is_file():
        fm = _load_md(vision)
        allowed["vision"] = {
            "path": vision,
            "type": "vision",
            "status": fm.get("status"),
        }

    principles_dir = foundations_root / "principles"
    if principles_dir.is_dir():
        for p in sorted(principles_dir.glob("*.md")):
            if p.name == "README.md":
                continue
            fm = _load_md(p)
            pid = fm.get("id")
            if not pid:
                continue
            allowed[pid] = {
                "path": p,
                "type": "principle",
                "kind": fm.get("kind"),
                "status": fm.get("status"),
            }

    personas_dir = foundations_root / "personas"
    if personas_dir.is_dir():
        for p in sorted(personas_dir.glob("*.md")):
            if p.name == "README.md":
                continue
            fm = _load_md(p)
            pid = fm.get("id")
            if not pid:
                continue
            allowed[pid] = {
                "path": p,
                "type": "persona",
                "status": fm.get("status"),
            }

    return allowed


def _iter_spec_files(specs_root: Path):
    if not specs_root.is_dir():
        return
    for p in sorted(specs_root.glob("*.md")):
        if p.name == "README.md":
            continue
        yield p


def check(foundations_root: Path, specs_root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    allowed = discover_allowed_slugs(foundations_root)

    # Principle `kind:` validation
    for _slug, info in allowed.items():
        if info["type"] == "principle":
            kind = info.get("kind")
            if kind not in VALID_KINDS:
                errors.append(
                    f"{info['path']}: invalid kind {kind!r}; "
                    f"must be one of {sorted(VALID_KINDS)}"
                )

    # Scan specs for references to foundations
    referenced: set[str] = set()
    for spec_path in _iter_spec_files(specs_root):
        fm = _load_md(spec_path)
        for field in ("serves", "realizes", "stressed_by"):
            refs = fm.get(field) or []
            if not isinstance(refs, list):
                errors.append(
                    f"{spec_path}: frontmatter {field!r} must be a list; "
                    f"got {type(refs).__name__}"
                )
                continue
            for ref in refs:
                if ref not in allowed:
                    errors.append(
                        f"{spec_path}: {field}: {ref!r} does not resolve to "
                        f"any foundation file"
                    )
                else:
                    referenced.add(ref)

    # Scan personas for `stresses:` — can point at specs OR foundations
    spec_slugs = {p.stem for p in _iter_spec_files(specs_root)}
    personas_dir = foundations_root / "personas"
    if personas_dir.is_dir():
        for persona_path in sorted(personas_dir.glob("*.md")):
            if persona_path.name == "README.md":
                continue
            fm = _load_md(persona_path)
            refs = fm.get("stresses") or []
            if not isinstance(refs, list):
                errors.append(
                    f"{persona_path}: frontmatter 'stresses' must be a list"
                )
                continue
            for ref in refs:
                if ref in allowed or ref in spec_slugs:
                    if ref in allowed:
                        referenced.add(ref)
                    continue
                errors.append(
                    f"{persona_path}: stresses: {ref!r} does not resolve to "
                    f"a spec or foundation"
                )

    # Orphan-principle warnings
    for slug, info in allowed.items():
        if info["type"] == "principle" and info.get("status") == "accepted" and slug not in referenced:
            warnings.append(
                f"{info['path']}: principle {slug!r} is accepted but "
                f"not referenced by any spec or persona"
            )

    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--foundations", type=Path, default=_DEFAULT_FOUNDATIONS)
    parser.add_argument("--specs", type=Path, default=_DEFAULT_SPECS)
    parser.add_argument(
        "--warnings-as-errors",
        action="store_true",
        help="Promote warnings to errors (useful in CI to block orphan principles).",
    )
    args = parser.parse_args(argv)

    errors, warnings = check(args.foundations, args.specs)

    report: dict[str, Any] = {
        "foundations": str(args.foundations),
        "specs": str(args.specs),
        "errors": errors,
        "warnings": warnings,
    }

    if errors:
        report["status"] = "fail"
        print(json.dumps(report, indent=2))
        return 1

    if warnings and args.warnings_as_errors:
        report["status"] = "warn-blocking"
        print(json.dumps(report, indent=2))
        return 1

    report["status"] = "ok"
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
