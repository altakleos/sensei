#!/usr/bin/env python3
"""Migrate sensei tests/transcripts/ fixtures to kanon .kanon/fidelity/ format.

Reads each fixture file, parses YAML frontmatter, and emits one kanon
fidelity file + one dogfood copy per fixture entry.
"""

import glob
import os
import shutil

import yaml

SENSEI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(SENSEI_ROOT, "tests", "transcripts")
DST_DIR = os.path.join(SENSEI_ROOT, ".kanon", "fidelity")

# Teaching-density patterns (from ADR-0033 / task spec)
TEACHING_PATTERNS = [
    r"(?i)\blet me explain\b",
    r"(?i)\bhere's why\b",
    r"(?i)\bhere's a hint\b",
    r"(?i)\bthe (correct |right )?answer is\b",
    r"(?i)\bthink about\b",
    r"(?i)\bremember that\b",
    r"(?i)\bto help you\b",
    r"(?i)\bto clarify\b",
    r"(?i)\bactually,",
    r"(?i)\bwhat if i told you\b",
    r"(?i)\bconsider this\b",
    r"(?i)\bthe trick is\b",
    r"(?i)\bthe solution is\b",
    r"(?i)\bwhat you need to know\b",
]

QUESTION_PATTERN = r"(?<!\?)\?(?=\s|$|[.!?,;])"


def slugify(name: str) -> str:
    return name.replace("_", "-")


def yaml_list(items: list[str], indent: int = 2) -> str:
    """Render a YAML list of quoted strings."""
    prefix = " " * indent
    return "\n".join(f'{prefix}- "{item}"' for item in items)


def yaml_list_unquoted(items: list[str], indent: int = 2) -> str:
    """Render a YAML list of unquoted strings (for patterns with special chars)."""
    prefix = " " * indent
    return "\n".join(f"{prefix}- '{item}'" for item in items)


def yaml_quote(s: str) -> str:
    """Quote a string for YAML, choosing single or double quotes as needed.

    Single-quoted YAML strings treat everything literally (no escape sequences),
    so they're ideal for regex patterns. When the string contains a literal
    single quote, we must switch to double-quoted YAML, which requires
    escaping backslashes and double quotes.
    """
    if "'" in s:
        escaped = s.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return f"'{s}'"


def build_pattern_density_entry(
    pattern: str | None = None,
    patterns: list[str] | None = None,
    strip_code_fences: bool = True,
    min_val: float | None = None,
    max_val: float | None = None,
    indent: int = 2,
) -> str:
    """Build one pattern_density list entry as YAML text."""
    prefix = " " * indent
    inner = " " * (indent + 2)
    lines = [f"{prefix}-"]
    if pattern is not None:
        lines[0] += f" pattern: {yaml_quote(pattern)}"
    if patterns is not None:
        lines.append(f"{inner}patterns:")
        for p in patterns:
            lines.append(f"{inner}  - {yaml_quote(p)}")
    lines.append(f"{inner}strip_code_fences: {'true' if strip_code_fences else 'false'}")
    if min_val is not None:
        lines.append(f"{inner}min: {min_val}")
    if max_val is not None:
        lines.append(f"{inner}max: {max_val}")
    return "\n".join(lines)


def build_frontmatter(protocol: str, fixture: dict) -> str:
    """Build the YAML frontmatter string for a kanon fidelity file."""
    lines = ["---"]
    lines.append(f"protocol: {protocol}")
    lines.append("actor: MENTOR")
    lines.append("turn_format: bracket")

    # forbidden_phrases
    if "forbidden_phrases" in fixture:
        lines.append("forbidden_phrases:")
        for phrase in fixture["forbidden_phrases"]:
            lines.append(f'  - "{phrase}"')

    # required_one_of
    if "required_one_of" in fixture:
        lines.append("required_one_of:")
        for pat in fixture["required_one_of"]:
            lines.append(f"  - {yaml_quote(pat)}")

    # required_all_of
    if "required_all_of" in fixture:
        lines.append("required_all_of:")
        for pat in fixture["required_all_of"]:
            lines.append(f"  - {yaml_quote(pat)}")

    # silence_ratio → word_share
    if "silence_ratio" in fixture:
        sr = fixture["silence_ratio"]
        lines.append("word_share:")
        if "min" in sr:
            lines.append(f"  min: {sr['min']}")
        if "max" in sr:
            lines.append(f"  max: {sr['max']}")

    # pattern_density (aggregated from question_density + teaching_density)
    pd_entries = []

    if "question_density" in fixture:
        qd = fixture["question_density"]
        pd_entries.append(
            build_pattern_density_entry(
                pattern=QUESTION_PATTERN,
                min_val=qd.get("min"),
                max_val=qd.get("max"),
            )
        )

    if "teaching_density" in fixture:
        td = fixture["teaching_density"]
        pd_entries.append(
            build_pattern_density_entry(
                patterns=TEACHING_PATTERNS,
                max_val=td.get("max"),
            )
        )

    if pd_entries:
        lines.append("pattern_density:")
        for entry in pd_entries:
            lines.append(entry)

    lines.append("---")
    return "\n".join(lines)


def build_body(fixture: dict, sensei_file: str) -> str:
    """Build the markdown body for a kanon fidelity file."""
    name = fixture["name"]
    what = fixture.get("what_it_pins", "").strip()
    return (
        f"# Fidelity fixture: {name}\n"
        f"\n"
        f"{what}\n"
        f"\n"
        f"Migrated from sensei fixture `{sensei_file}::{name}`.\n"
    )


def find_dogfood(src_file: str) -> str | None:
    """Find the dogfood file for a given source fixture file."""
    stem = os.path.splitext(os.path.basename(src_file))[0]
    dogfood = os.path.join(SRC_DIR, f"{stem}.dogfood.md")
    return dogfood if os.path.exists(dogfood) else None


def migrate():
    os.makedirs(DST_DIR, exist_ok=True)

    src_files = sorted(glob.glob(os.path.join(SRC_DIR, "*.md")))
    created_fixtures = []
    created_dogfoods = []

    for src_file in src_files:
        basename = os.path.basename(src_file)
        if basename == "README.md" or ".dogfood." in basename:
            continue

        with open(src_file) as f:
            content = f.read()

        parts = content.split("---", 2)
        if len(parts) < 3:
            print(f"  SKIP {basename}: no YAML frontmatter")
            continue

        fm = yaml.safe_load(parts[1])
        protocol = fm.get("protocol", "unknown")
        protocol_slug = slugify(protocol)
        fixtures = fm.get("fixtures", [])
        sensei_stem = os.path.splitext(basename)[0]
        dogfood_src = find_dogfood(src_file)

        for fixture in fixtures:
            name_slug = slugify(fixture["name"])
            out_stem = f"{protocol_slug}-{name_slug}"

            # Write fixture file
            fixture_path = os.path.join(DST_DIR, f"{out_stem}.md")
            frontmatter = build_frontmatter(protocol, fixture)
            body = build_body(fixture, basename)
            with open(fixture_path, "w") as f:
                f.write(frontmatter + "\n" + body)
            created_fixtures.append(fixture_path)

            # Copy dogfood
            dogfood_dst = os.path.join(DST_DIR, f"{out_stem}.dogfood.md")
            if dogfood_src:
                shutil.copy2(dogfood_src, dogfood_dst)
                created_dogfoods.append(dogfood_dst)
            else:
                print(f"  WARN: no dogfood for {basename}")

    # Summary
    print(f"\n{'='*60}")
    print(f"Migration complete")
    print(f"{'='*60}")
    print(f"Fixture files created:  {len(created_fixtures)}")
    print(f"Dogfood files created:  {len(created_dogfoods)}")
    print(f"Total .md files:        {len(created_fixtures) + len(created_dogfoods)}")
    print(f"Target directory:       {DST_DIR}")
    print()
    print("Fixtures:")
    for p in created_fixtures:
        print(f"  {os.path.basename(p)}")
    print()
    print("Dogfood copies:")
    for p in created_dogfoods:
        print(f"  {os.path.basename(p)}")


if __name__ == "__main__":
    migrate()
