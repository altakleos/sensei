---
status: accepted
weight: lite
date: 2026-04-22
protocols: []
---
# ADR-0022: Shell Wrapper for Script Interpreter Resolution

**Decision:** `sensei init` writes a `.sensei/run` shell wrapper and a `.sensei/.python_path` file recording `sys.executable`. Engine protocols invoke scripts as `.sensei/run <script>.py --args` instead of `python .sensei/scripts/<script>.py`. The wrapper uses the recorded interpreter; falls back to bare `python3` if the path is stale.

**Why:** LLM agents invoke scripts with whatever `python3` is on PATH — typically the system Python, which lacks `pyyaml`/`jsonschema`. The wrapper resolves the interpreter that has `sensei-tutor` installed (pipx venv, user venv, or global). A shell wrapper was chosen over shebangs (LLMs use `python3 script.py`, never `./script.py`), `python -m` (fails with pipx), or `PYTHONPATH` manipulation (fragile, leaks into child processes).

**Alternative:** Inline `try/except ImportError` in every script with a "run `pip install sensei-tutor`" message. Implemented as a complementary safety net but insufficient alone — it tells the user what's wrong but doesn't fix it. The wrapper fixes it.
