"""CHANGELOG compare-link validator (maintainer-side, CI hard-fail).

Asserts that ``CHANGELOG.md``'s reference-link tail stays in sync with its
release headings — the gap that survived four releases (a16–a19) before
the 2026-04-25 audit caught it.

Rules:

1. Every ``## [X.Y.Z(suffix)] — YYYY-MM-DD`` heading has a matching
   ``[X.Y.Z(suffix)]: <url>`` reference-link line at the file tail.
2. ``[Unreleased]:`` compares from the highest-versioned released tag.
3. Each compare URL matches
   ``https://github.com/<owner>/<repo>/compare/<from>...<to>`` for
   non-first releases, or ``releases/tag/<tag>`` for the first release.
4. Reference-link tail entries are sorted descending by version
   (``[Unreleased]`` first, then released versions newest-to-oldest).

Structural-only — no semantic checks on section bodies.

Exit codes:
    0 — all rules satisfied
    1 — one or more violations
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from packaging.version import InvalidVersion, Version

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_CHANGELOG = _REPO_ROOT / "CHANGELOG.md"

_HEADING_RE = re.compile(r"^## \[(?P<tag>[^\]]+)\]")
_REFLINK_RE = re.compile(r"^\[(?P<tag>[^\]]+)\]: (?P<url>\S+)\s*$")
_COMPARE_RE = re.compile(
    r"^https://github\.com/[^/]+/[^/]+/compare/(?P<from>[^.]+(?:\.[^.]+)*)\.\.\.(?P<to>\S+)$"
)
_TAG_RE = re.compile(r"^https://github\.com/[^/]+/[^/]+/releases/tag/(?P<tag>\S+)$")


def _parse(text: str) -> tuple[list[str], dict[str, str], dict[str, int]]:
    """Return (release_tags_in_doc_order, reflinks_tag→url, reflink_line_no)."""
    headings: list[str] = []
    reflinks: dict[str, str] = {}
    reflink_lines: dict[str, int] = {}
    for i, line in enumerate(text.splitlines(), start=1):
        h = _HEADING_RE.match(line)
        if h and h.group("tag") != "Unreleased":
            headings.append(h.group("tag"))
            continue
        r = _REFLINK_RE.match(line)
        if r:
            reflinks[r.group("tag")] = r.group("url")
            reflink_lines[r.group("tag")] = i
    return headings, reflinks, reflink_lines


def _vkey(tag: str) -> Version:
    return Version(tag.lstrip("v"))


def lint(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    try:
        rel: Path | str = path.relative_to(_REPO_ROOT)
    except ValueError:
        rel = path
    headings, reflinks, lines = _parse(text)
    violations: list[str] = []

    for tag in headings:
        if tag not in reflinks:
            violations.append(f"{rel}: heading [{tag}] has no [{tag}]: reference-link entry")

    if "Unreleased" not in reflinks:
        violations.append(f"{rel}: missing [Unreleased]: reference-link entry")
    elif headings:
        try:
            latest = max(headings, key=_vkey)
        except InvalidVersion as exc:
            violations.append(f"{rel}: cannot version-sort headings: {exc}")
            latest = headings[0]
        m = _COMPARE_RE.match(reflinks["Unreleased"])
        if not m:
            violations.append(f"{rel}:{lines['Unreleased']}: [Unreleased] URL is not a compare URL")
        elif m.group("from") != f"v{latest}" or m.group("to") != "HEAD":
            violations.append(
                f"{rel}:{lines['Unreleased']}: [Unreleased] should compare from v{latest}...HEAD, "
                f"got {m.group('from')}...{m.group('to')}"
            )

    sorted_releases = sorted(headings, key=_vkey, reverse=True)
    for newer, older in zip(sorted_releases, sorted_releases[1:], strict=False):
        url = reflinks.get(newer)
        if url is None:
            continue
        m = _COMPARE_RE.match(url)
        if not m:
            violations.append(f"{rel}:{lines[newer]}: [{newer}] URL is not a compare URL")
            continue
        if m.group("from") != f"v{older}" or m.group("to") != f"v{newer}":
            violations.append(
                f"{rel}:{lines[newer]}: [{newer}] should compare from v{older}...v{newer}, "
                f"got {m.group('from')}...{m.group('to')}"
            )

    if sorted_releases:
        first_tag = sorted_releases[-1]
        url = reflinks.get(first_tag)
        if url is not None and not _COMPARE_RE.match(url) and not _TAG_RE.match(url):
            violations.append(
                f"{rel}:{lines[first_tag]}: [{first_tag}] URL must be a compare URL or releases/tag URL"
            )

    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--changelog", type=Path, default=_DEFAULT_CHANGELOG)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    if not args.changelog.is_file():
        print(f"changelog not found: {args.changelog}", file=sys.stderr)
        return 1

    violations = lint(args.changelog)
    if violations:
        print("changelog-links: violations found:", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"changelog-links: OK ({args.changelog.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
