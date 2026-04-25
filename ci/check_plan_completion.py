"""Plan-completion linter (maintainer-side, CI hard-fail).

Enforces the rule in `docs/development-process.md` § "Checkbox convention":
a plan with `status: done` must have every top-level task `- [x]` (shipped)
or `- [~]` (explicitly deferred). An unticked `- [ ]` on a `done` plan is an
internal contradiction — the plan claims the work shipped but its own
checklist says otherwise.

Exit codes:
    0 — all `done` plans have every top-level task ticked or deferred
    1 — at least one `done` plan has an unticked top-level task

Per [docs/development-process.md § Checkbox convention](docs/development-process.md#checkbox-convention).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_PLANS_DIR = _REPO_ROOT / "docs" / "plans"

# Top-level checkbox lines: zero leading whitespace, then "- [<state>] ".
# Sub-bullets (any indentation) are deliberately excluded because plan tasks
# routinely use indented sub-bullets to itemize sub-steps under a single
# top-level task; ticking the parent already represents the work.
_TOP_LEVEL_CHECKBOX = re.compile(r"^- \[(?P<state>[ x~])\] ")


def _split_frontmatter(text: str) -> tuple[dict | None, int]:
    """Return (frontmatter_dict, body_start_line_index_1based) or (None, 1).

    Plans use the `---` … `---` YAML-frontmatter convention. If absent or
    malformed, returns (None, 1) and the linter skips the plan.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, 1
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, 1
    raw = "\n".join(lines[1:end])
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError:
        return None, end + 2
    if not isinstance(data, dict):
        return None, end + 2
    return data, end + 2  # body starts on the line after the closing ---


def lint_plan(path: Path) -> list[str]:
    """Return a list of human-readable violation strings for *path*.

    Empty list = clean. The linter only flags `status: done` plans; non-done
    plans (planned, in-progress, missing) are silently skipped because their
    unticked tasks are expected, not contradictions.
    """
    text = path.read_text(encoding="utf-8")
    fm, body_start = _split_frontmatter(text)
    if fm is None:
        return []
    if fm.get("status") != "done":
        return []

    violations: list[str] = []
    try:
        rel: Path | str = path.relative_to(_REPO_ROOT)
    except ValueError:
        # Plans dir outside the repo (test fixtures); fall back to absolute.
        rel = path
    for offset, line in enumerate(text.splitlines()[body_start - 1:]):
        match = _TOP_LEVEL_CHECKBOX.match(line)
        if match is None:
            continue
        if match.group("state") == " ":
            line_no = body_start + offset
            summary = line[6:].strip()  # everything after "- [ ] "
            # Trim noisy markdown formatting and long sub-bullet text.
            if len(summary) > 80:
                summary = summary[:77] + "..."
            violations.append(f"{rel}:{line_no}: unticked task on `done` plan — {summary}")
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument(
        "--plans-dir",
        type=Path,
        default=_DEFAULT_PLANS_DIR,
        help="Directory containing plan files (default: docs/plans/)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress green-path output; print only on failure.",
    )
    args = parser.parse_args(argv)

    plans_dir: Path = args.plans_dir
    if not plans_dir.is_dir():
        print(f"plans directory not found: {plans_dir}", file=sys.stderr)
        return 1

    all_violations: list[str] = []
    for plan_path in sorted(plans_dir.glob("*.md")):
        # README and templates are not plans even if they live in plans/.
        if plan_path.name == "README.md":
            continue
        all_violations.extend(lint_plan(plan_path))

    if all_violations:
        print("plan-completion: violations found:", file=sys.stderr)
        for v in all_violations:
            print(f"  {v}", file=sys.stderr)
        print(
            "\nFix: tick `- [x]` for shipped tasks, mark deferred ones `- [~]` "
            "with a NOTE explaining why, or change frontmatter `status:` to "
            "match reality (planned/in-progress).",
            file=sys.stderr,
        )
        return 1

    if not args.quiet:
        print(f"plan-completion: OK ({sum(1 for _ in plans_dir.glob('*.md'))} plans scanned)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
