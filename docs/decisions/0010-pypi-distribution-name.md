---
status: accepted
date: 2026-04-20
weight: lite
protocols: [release]
---
# ADR-0010: PyPI Distribution Name is `sensei-tutor`

## Decision

The PyPI distribution name for Sensei is **`sensei-tutor`**. Users install with `pip install sensei-tutor`. The Python package name (the importable module), the CLI command, the `.sensei/` instance directory, and the product name itself remain `sensei`.

## Why

`sensei` on PyPI is already taken by an unrelated project. The distribution name is the sole PyPI-side identifier; every other touchpoint (CLI, import path, folder name) is ours to keep. `sensei-tutor` preserves the product identity up-front (`sensei-`), is unambiguously available on PyPI, and matches the product's actual behaviour — Sensei is a tutor. PyPI-name availability was verified directly against `https://pypi.org/pypi/sensei-tutor/json` (404 at the time of this ADR).

## Alternative

Rename the Python package and CLI command too (e.g., `sensei-learn` everywhere including imports and `.sensei/` → `.sensei-learn/`). Rejected because the Python-side identity is already deeply embedded in engine prose, schemas, protocols, tests, and file paths, and all of those touchpoints would have to change for no functional gain. Distribution name and import name are routinely different in Python (e.g., `beautifulsoup4` / `bs4`, `PyYAML` / `yaml`); there is no reason to couple them here.
