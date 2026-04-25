# Shim Validation Runbook

`sensei init` writes one tool-specific shim file per supported LLM coding agent (per [ADR-0003](../decisions/0003-tool-specific-agent-hooks.md)). Each shim points the tool at `AGENTS.md`, the boot document. CI asserts the **format** of every shim is correct (see `tests/test_init.py` § Shim format validation), but **behavioral validation** — does the tool actually read the shim, follow the import, and behave as a Sensei mentor — requires running each tool against a scaffolded instance, which CI cannot do. This runbook is the manual checklist for that.

> Status legend used throughout this doc and in `README.md`:
>
> - ✅ **Verified** — shim format passes CI, AND a maintainer has completed the steps below for this tool against a recent release.
> - ⚙ **Format validated; behavior unverified** — shim format passes CI, but no maintainer has completed the steps below for this tool yet.

## Prerequisites

```bash
pip install sensei-tutor      # or: uv pip install sensei-tutor
sensei init ~/sensei-shim-test
cd ~/sensei-shim-test
```

The folder `~/sensei-shim-test/` now contains `.sensei/`, `AGENTS.md`, the per-tool shim files, and a seeded `learner/profile.yaml`. Open this folder with each tool below.

## Probe

For every tool, the validator opens the scaffolded folder and sends one probe prompt as a fresh chat:

> **Probe**: `Teach me about ownership in Rust.`

**Pass criteria** — the agent's first reply must demonstrate it has read the boot chain. Look for any of:

1. The reply mentions reading `AGENTS.md` or `.sensei/engine.md`, OR
2. The reply demonstrates Sensei-protocol behaviour: a probing question before explaining (Socratic stance per `protocols/tutor.md`), OR an acknowledgement that no goal exists yet and a request to set one (`protocols/goal.md`), OR
3. The reply mentions **silence-is-teaching**, **two-failure principle**, or **three unknowns** by name (these are pedagogical signatures of the loaded protocols).

**Fail criteria** — the reply is a generic chatbot answer ("Ownership in Rust is a memory-management feature where each value has one owner..."). A generic answer means the tool ignored the shim or failed to follow the import to `AGENTS.md`.

## Per-tool checklist

### ✅ Claude Code

- **Shim path**: `CLAUDE.md` (uses Claude Code's `@AGENTS.md` import directive)
- **Install**: comes via Anthropic; see `claude --version`
- **Run**: `cd ~/sensei-shim-test && claude` then send the probe
- **Verified**: yes — `tests/e2e/` runs Claude Code headless against multiple Sensei protocols on every nightly CI cron.

### ✅ Kiro

- **Shim path**: `.kiro/steering/sensei.md`
- **Install**: see Kiro's documentation for the desktop app or `kiro-cli`
- **Run**: open `~/sensei-shim-test/` in the Kiro app, or `kiro-cli` from the folder, then send the probe
- **Verified**: yes — dogfooded end-to-end during early Sensei development; `tests/e2e/agent_runner.py` supports it.

### ⚙ Cursor

- **Shim path**: `.cursor/rules/sensei.mdc` (YAML frontmatter `description: ...` + `alwaysApply: true`)
- **Install**: https://cursor.com (download the desktop app)
- **Run**: open `~/sensei-shim-test/` in Cursor; open Cursor's chat panel; send the probe.
- **Pass**: as defined in § Probe.
- **Record result**: append a dated note to this section: `<YYYY-MM-DD> validated by <name> against Cursor <version>: pass/fail` plus a short transcript snippet.

### ⚙ GitHub Copilot

- **Shim path**: `.github/copilot-instructions.md` (single plain-prose file; Copilot reads custom instructions from this exact path)
- **Install**: comes via the GitHub Copilot subscription + the IDE extension (VS Code, JetBrains, Visual Studio, Neovim).
- **Run**: open `~/sensei-shim-test/` in your IDE with Copilot Chat enabled; send the probe.
- **Note**: Copilot's instruction-file feature was previously a preview; verify the active feature flag if the instructions seem to be ignored.
- **Record result**: per Cursor's pattern.

### ⚙ Windsurf

- **Shim path**: `.windsurf/rules/sensei.md` (YAML frontmatter `trigger: always_on`)
- **Install**: https://codeium.com/windsurf
- **Run**: open `~/sensei-shim-test/` in Windsurf; send the probe via Cascade.
- **Pass**: as defined in § Probe.
- **Record result**: per Cursor's pattern.

### ⚙ Cline

- **Shim path**: `.clinerules/sensei.md` (plain prose; Cline reads `.clinerules/` directory contents as project-level rules)
- **Install**: VS Code Marketplace → search "Cline"
- **Run**: open `~/sensei-shim-test/` in VS Code; open Cline's chat panel; send the probe.
- **Note**: confirm Cline's "rules" feature is active in the version installed (the directory name has changed across releases).
- **Record result**: per Cursor's pattern.

### ⚙ Roo

- **Shim path**: `.roo/rules/sensei.md` (plain prose; Roo Code's project-rules feature)
- **Install**: VS Code Marketplace → search "Roo Code"
- **Run**: open `~/sensei-shim-test/` in VS Code; open Roo's chat panel; send the probe.
- **Record result**: per Cursor's pattern.

### ⚙ JetBrains AI Assistant

- **Shim path**: `.aiassistant/rules/sensei.md` (plain prose)
- **Install**: comes with JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm, etc.) on a JetBrains AI subscription.
- **Run**: open `~/sensei-shim-test/` in a JetBrains IDE; open the AI Assistant panel; send the probe.
- **Note**: confirm the rules-file feature is enabled in your IDE version (the path may differ across JetBrains releases).
- **Record result**: per Cursor's pattern.

## After validating a tool

1. Tick the corresponding section header to ✅ in this file.
2. Update the "Behavior verified" column for that tool in `README.md`.
3. Open a PR with both edits in one commit; reference this runbook section in the description.

## When a tool's shim format changes upstream

If a tool changes its instruction-file path or required frontmatter (Cursor renames `alwaysApply` → something else, Windsurf adds a required field, Cline moves `.clinerules/` to `.cline/`):

1. Update `_SHIMS` in `src/sensei/cli.py`.
2. Update the snapshot in `tests/test_init.py:_EXPECTED_SHIMS` and the per-tool format assertion (e.g. `test_shim_cursor_format`).
3. Update this runbook with the new path / required fields.
4. Re-validate the tool end-to-end and update its status here.
5. Add a CHANGELOG entry under `### Changed`.

## Escalation

If you cannot get a tool to read its shim despite a format-correct file in the documented path, the issue is upstream (the tool's instruction-file feature is broken, gated, or differently shaped than documented). Open an issue in this repo with the tool's version, OS, and reproduction steps so the fact is recorded; do NOT silently downgrade the README claim without a corresponding `## [Unreleased]` `### Changed` note.
