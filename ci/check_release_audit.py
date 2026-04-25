"""Release audit-log validator (maintainer-side, CI hard-fail).

Asserts that a per-release Tier-2 E2E audit log exists, parses, and reports
a clean run for the tag being released. Closes the gap that ADR-0024 names:
the workstation-only Tier-2 gate had no machine-checked artifact, so a
maintainer who skipped the gate and the log produced an unobservably-broken
release.

Rules (all must hold):

1. ``docs/operations/releases/<tag>.md`` exists and is readable.
2. The file begins with a YAML frontmatter block delimited by ``---`` lines
   that parses to a mapping.
3. The frontmatter contains every required field, non-empty:
   ``tag``, ``date``, ``tester``, ``tool``, ``tool_version``,
   ``exit_code``, ``transcript_hash``.
4. The frontmatter ``tag`` field equals the ``--tag`` argument (catches
   copy-paste of last release's log).
5. ``exit_code`` is integer ``0``.
6. ``transcript_hash`` is either a 64-char lowercase hex string or the
   literal string ``n/a`` (template allows the latter when stdout was
   discarded).
7. ``tool`` is one of ``claude``, ``kiro``, or a string beginning with
   ``other:`` (keeps ADR-0003 conformance auditable while permitting
   future tools without a code change).
8. The body (everything after the closing frontmatter fence) mentions
   every test file path in ``REQUIRED_GATE_TESTS`` — the seven Tier-2
   tests enumerated in ADR-0027. Per ADR-0028; closes the breadth
   honour-system gap left by ADR-0024 + ADR-0027 alone.

Per [ADR-0024](docs/decisions/0024-release-audit-log-required.md),
[ADR-0027](docs/decisions/0027-tier2-gate-expansion.md),
[ADR-0028](docs/decisions/0028-tier2-gate-breadth-enforcement.md), and the
template at [docs/operations/releases/README.md](docs/operations/releases/README.md).

Exit codes:
    0 — all rules satisfied
    1 — one or more violations
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_RELEASES_DIR = _REPO_ROOT / "docs" / "operations" / "releases"

REQUIRED_FIELDS: tuple[str, ...] = (
    "tag",
    "date",
    "tester",
    "tool",
    "tool_version",
    "exit_code",
    "transcript_hash",
)

_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
_KNOWN_TOOLS: frozenset[str] = frozenset({"claude", "kiro"})

# ADR-0027 expanded the Tier-2 gate from 3 to 7 protocols. ADR-0028 makes
# that breadth machine-checked: every release's audit-log body must mention
# each path verbatim. The maintainer copy-pastes the playbook's bash-array
# invocation into the body, so the seven paths land there for free; missing
# paths mean the gate did not run all seven.
REQUIRED_GATE_TESTS: tuple[str, ...] = (
    "tests/e2e/test_goal_protocol_e2e.py",
    "tests/e2e/test_assess_protocol_e2e.py",
    "tests/e2e/test_hints_protocol_e2e.py",
    "tests/e2e/test_tutor_protocol_e2e.py",
    "tests/e2e/test_review_protocol_e2e.py",
    "tests/e2e/test_reviewer_protocol_e2e.py",
    "tests/e2e/test_challenger_protocol_e2e.py",
)


def _split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str, str | None]:
    """Return ``(frontmatter_dict, body_text, error_message)``.

    On success: ``(dict, body, None)`` where ``body`` is everything after
    the closing fence's terminating newline (may be empty).
    On failure: ``(None, "", error_string)``.
    """
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return None, "", "file does not start with a YAML frontmatter block"
    # Search from index 3 (the opening fence's terminating newline) so an empty
    # frontmatter — '---\n---\n' — finds its closing fence at the same newline.
    end = text.find("\n---\n", 3)
    body = ""
    if end < 0:
        # Allow the closing fence to be the final line without a trailing newline.
        stripped = text.rstrip()
        if stripped.endswith("\n---"):
            end = stripped.rfind("\n---")
            # No body content possible after a bare-end fence.
        else:
            return None, "", "frontmatter closing '---' fence not found"
    else:
        body = text[end + len("\n---\n") :]
    try:
        fm = yaml.safe_load(text[4:end])
    except yaml.YAMLError as exc:
        return None, "", f"invalid YAML frontmatter: {exc}"
    if fm is None:
        return None, "", "frontmatter is empty"
    if not isinstance(fm, dict):
        return None, "", "frontmatter is not a mapping"
    return fm, body, None


def _validate_tool(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return "tool: must be a non-empty string"
    if value in _KNOWN_TOOLS:
        return None
    if value.startswith("other:") and len(value) > len("other:"):
        return None
    return (
        f"tool: {value!r} is not one of {sorted(_KNOWN_TOOLS)} and does not "
        f"start with 'other:'"
    )


def _validate_body_breadth(body: str) -> list[str]:
    """Return one violation per missing test file path in *body*.

    Per ADR-0028, the audit-log body must mention every test file path in
    ``REQUIRED_GATE_TESTS``. Substring match is sufficient — the playbook's
    bash-array invocation lists each path on its own line, and the
    maintainer copy-pastes that block into the audit log's
    ``## Invocation`` section.
    """
    return [
        f"body: missing required test path {path!r} (ADR-0027/0028 gate breadth)"
        for path in REQUIRED_GATE_TESTS
        if path not in body
    ]


def _validate_transcript_hash(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return "transcript_hash: must be a non-empty string"
    if value == "n/a":
        return None
    if _HEX64_RE.match(value):
        return None
    return (
        f"transcript_hash: {value!r} is neither 'n/a' nor a 64-char "
        f"lowercase hex string"
    )


def lint(audit_path: Path, expected_tag: str) -> list[str]:
    """Return the list of violations for *audit_path* against *expected_tag*."""
    try:
        rel: Path | str = audit_path.relative_to(_REPO_ROOT)
    except ValueError:
        rel = audit_path

    if not audit_path.is_file():
        return [f"{rel}: audit log not found for tag {expected_tag!r}"]

    text = audit_path.read_text(encoding="utf-8")
    fm, body, err = _split_frontmatter(text)
    if fm is None:
        return [f"{rel}: {err}"]

    violations: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in fm:
            violations.append(f"{rel}: missing required field {field!r}")
            continue
        value = fm[field]
        if value is None or (isinstance(value, str) and not value.strip()):
            violations.append(f"{rel}: required field {field!r} is empty")

    # Field-level checks below depend on the field being present and non-empty.
    if not violations:
        if fm["tag"] != expected_tag:
            violations.append(
                f"{rel}: frontmatter tag {fm['tag']!r} does not match "
                f"expected tag {expected_tag!r}"
            )
        if not isinstance(fm["exit_code"], int) or isinstance(fm["exit_code"], bool):
            violations.append(
                f"{rel}: exit_code must be an integer, got "
                f"{type(fm['exit_code']).__name__}"
            )
        elif fm["exit_code"] != 0:
            violations.append(
                f"{rel}: exit_code is {fm['exit_code']}, must be 0 for a passing gate"
            )
        tool_err = _validate_tool(fm["tool"])
        if tool_err is not None:
            violations.append(f"{rel}: {tool_err}")
        hash_err = _validate_transcript_hash(fm["transcript_hash"])
        if hash_err is not None:
            violations.append(f"{rel}: {hash_err}")

    # Body-breadth check (ADR-0028). Independent of frontmatter validity:
    # a malformed-frontmatter run still surfaces breadth gaps in the same
    # report so the maintainer fixes everything at once.
    for breadth_err in _validate_body_breadth(body):
        violations.append(f"{rel}: {breadth_err}")

    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0] if __doc__ else None
    )
    parser.add_argument(
        "--tag",
        required=True,
        help="Release tag to audit (e.g. v0.1.0a20). Must match the file at "
        "docs/operations/releases/<tag>.md and the frontmatter 'tag' field.",
    )
    parser.add_argument(
        "--releases-dir",
        type=Path,
        default=_DEFAULT_RELEASES_DIR,
        help="Directory containing per-release audit logs (default: %(default)s).",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    audit_path = args.releases_dir / f"{args.tag}.md"
    violations = lint(audit_path, args.tag)
    if violations:
        print("release-audit: violations found:", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        return 1

    if not args.quiet:
        try:
            rel = audit_path.relative_to(_REPO_ROOT)
        except ValueError:
            rel = audit_path
        print(f"release-audit: OK ({rel})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
