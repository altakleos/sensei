"""Compute mentor teaching-token density from a dogfood transcript.

Teaching-density is the third metric in the Tier-1 quantitative-band
family (silence_ratio + question_density + teaching_density). It closes
the assessor-exception adherence gap named by the 2026-04-25 follow-up
audit Risk #4: ``engine.md`` § Invariants forbids teaching during
assessment, review (no reteach), challenger (provoke, don't tell),
reviewer (feedback ≠ teaching), cross_goal_review (Q&A), status
(reports), and hints (triage). This helper turns those prose
prohibitions into a counted signal a fixture can assert against.

Heuristic: count case-insensitive matches of a curated taxonomy of
"teaching language" phrases across mentor turns, OUTSIDE fenced code
blocks. The taxonomy is mined from existing ``forbidden_phrases`` lists
in ``assess.md``, ``hints.md``, and ``review.md``.

Density = ``total_teaching_tokens / mentor_turns`` (per-turn rate,
mirroring question_density). Degenerate zero-mentor-turn transcripts
yield density 0.0.

Per-protocol expected ranges (see ``tests/transcripts/<protocol>.md``
fixture bands for the load-bearing maxes):

- Forbidden (``max: 0.0``): assess, review, challenger, reviewer,
  cross_goal_review, status, hints
- Bracketed (``max: 1.0``): goal (clarification probes occasionally
  use "consider")
- Omitted (teaching IS the protocol): tutor, performance_training

Invoked by tests and at the CLI as:
    python -m sensei.engine.scripts.teaching_density --transcript <path>

Library entry points:
    compute_teaching_density(text: str) -> float
    compute_teaching_stats(text: str) -> dict[str, int | float]

Exit codes:
    0 — JSON object on stdout: {mentor_turns, teaching_token_count,
        teaching_density}
    1 — file missing or unparseable; error JSON on stdout
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Shared with silence_ratio + question_density via the public
# split_into_turns API: all three Tier-1 metrics see the same canonical
# notion of a turn.
from silence_ratio import split_into_turns  # type: ignore[import-not-found]

# Triple-backtick fenced code block. Strip before pattern matching so a
# code sample with a comment like ``# the answer is`` doesn't inflate
# the count.
_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)

# Canonical teaching-language taxonomy. Mined from existing
# forbidden_phrases lists in assess.md (no-teaching-during-assessment),
# hints.md (triage-not-teaching), and review.md (no-reteach). All
# patterns are matched case-insensitive. Word boundaries (``\b``) anchor
# multi-word phrases to whole-token matches; the answer-is variant
# captures three forbidden_phrases ("the answer is" / "the correct
# answer is" / "the right answer is") in one regex.
_TEACHING_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\blet me explain\b",
        r"\bhere'?s why\b",
        r"\bhere'?s a hint\b",
        r"\bthe (correct |right )?answer is\b",
        r"\bthink about\b",
        r"\bremember that\b",
        r"\bto help you\b",
        r"\bto clarify\b",
        r"\bactually,",
        r"\bwhat if i told you\b",
        r"\bconsider this\b",
        r"\bthe trick is\b",
        r"\bthe solution is\b",
        r"\bwhat you need to know\b",
    )
)


def _strip_code_fences(text: str) -> str:
    """Remove triple-backtick fenced code blocks from *text*."""
    return _CODE_FENCE_RE.sub("", text)


def _count_teaching_tokens(turns: list[str]) -> int:
    total = 0
    for turn in turns:
        cleaned = _strip_code_fences(turn)
        for pattern in _TEACHING_PATTERNS:
            total += len(pattern.findall(cleaned))
    return total


def compute_teaching_stats(text: str) -> dict[str, float]:
    """Return mentor turn count, teaching-token count, and per-turn density.

    ``teaching_density`` is ``teaching_token_count / mentor_turns``,
    or 0.0 when the transcript has no mentor turns (degenerate).
    """
    mentor, _learner = split_into_turns(text)
    tokens = _count_teaching_tokens(mentor)
    turns = len(mentor)
    density = (tokens / turns) if turns > 0 else 0.0
    return {
        "mentor_turns": turns,
        "teaching_token_count": tokens,
        "teaching_density": density,
    }


def compute_teaching_density(text: str) -> float:
    """Convenience wrapper for fixture-level assertions."""
    return float(compute_teaching_stats(text)["teaching_density"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--transcript", required=True, help="Path to a dogfood transcript file")
    args = parser.parse_args(argv)

    path = Path(args.transcript)
    if not path.is_file():
        print(json.dumps({"error": f"transcript not found: {path}"}))
        return 1
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(json.dumps({"error": f"read failed: {exc}"}))
        return 1

    stats = compute_teaching_stats(text)
    if stats["mentor_turns"] == 0:
        print(json.dumps({"error": "transcript has no [MENTOR] turns"}))
        return 1
    print(json.dumps(stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
