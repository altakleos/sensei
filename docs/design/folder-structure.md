---
status: accepted
date: 2026-04-20
implements:
  - learner-is-not-the-goal
---
# Folder Structure — Design

## Context

`sensei init <target>` scaffolds a learning-environment folder. The original ideation document §6.1 sketched an aspirational layout during ideation. The actual implementation diverges in several deliberate ways, documented here so that future work knows where things live and why.

## Specs

- [learner-profile](../specs/learner-profile.md) — the profile that lives at `instance/profile.yaml`
- [P-learner-is-not-the-goal](../foundations/principles/learner-is-not-the-goal.md) — the principle that the profile is global, not goal-scoped

## Canonical Layout (v1)

```
~/learning/                          # user-chosen location
├── .sensei/                         # engine bundle (copied from package)
│   ├── engine.md                    # kernel: dispatch table, invariants
│   ├── defaults.yaml                # engine-level tunables
│   ├── protocols/                   # prose-as-code protocol files
│   ├── scripts/                     # deterministic helper scripts
│   ├── .sensei-version              # installed engine version
│   └── ...
├── instance/                        # learner-specific state and config
│   ├── profile.yaml                 # the learner (evolves through conversation)
│   └── config.yaml                  # instance-level overrides for defaults.yaml
├── AGENTS.md                        # boot document (read by any LLM agent)
├── CLAUDE.md                        # tool shim → AGENTS.md
├── .kiro/steering/sensei.md         # tool shim → AGENTS.md
├── .cursor/rules/sensei.mdc         # tool shim → AGENTS.md
├── .github/copilot-instructions.md  # tool shim → AGENTS.md
├── .windsurf/rules/sensei.md        # tool shim → AGENTS.md
├── .clinerules/sensei.md            # tool shim → AGENTS.md
├── .roo/rules/sensei.md             # tool shim → AGENTS.md
└── .aiassistant/rules/sensei.md     # tool shim → AGENTS.md
```

## Divergences from §6.1

| §6.1 Sketch | Actual (v1) | Rationale |
|---|---|---|
| `profile.yaml` at `.sensei/profile.yaml` | `instance/profile.yaml` | The `.sensei/` directory is the engine bundle — overwritten on `sensei upgrade`. Learner state must survive upgrades, so it lives in `instance/`. |
| `config.yaml` at `.sensei/config.yaml` | `instance/config.yaml` | Same reason: config is learner-owned, not engine-owned. Separating engine defaults from instance overrides follows the overlay pattern. |
| `knowledge-state.yaml` at `.sensei/` | Not present | Cross-goal knowledge transfer (§4.4) is deferred. The principle holds but the file doesn't exist until a protocol requires it. |
| `agents/` directory with per-mode files (`tutor.md`, `assessor.md`, etc.) | Not present | Per ADR-0013, modes are protocol-level concerns — behavioural shifts within a single mentor, not separate agent context files. The dispatch table in `engine.md` handles mode transitions. |
| Goal workspace folders (`interview-prep/`, `rust-systems/`) | Not present | Goal workspaces are a future feature. They will be created by Sensei during conversation, not by the CLI. |

## Future Components

The following will land in future plans. Their locations are noted here for orientation:

- **Goal workspaces** — top-level sibling directories (e.g., `interview-prep/`) containing `curriculum.yaml`, `progress.yaml`, `exercises/`, `notes/`. Created by the mentor during conversation, never by CLI.
- **Cross-goal knowledge state** — likely `instance/knowledge-state.yaml`, tracking foundational concepts that span goals. Deferred until a protocol needs it.
- **Session logs** — location TBD. Likely `instance/sessions/` or within goal workspaces.

## Decisions

- [ADR-0003: Tool-Specific Agent Hooks](../decisions/0003-tool-specific-agent-hooks.md) — shim files pointing at AGENTS.md
- [ADR-0004: Distribution Model](../decisions/0004-distribution-model.md) — engine bundle copied into `.sensei/`
- [ADR-0013: Context Composition](../decisions/0013-context-composition.md) — modes are protocol-level, no per-mode agent files

## Notes

The `.sensei/` directory is treated as immutable between upgrades. `sensei upgrade` replaces it wholesale from the installed package. Anything the learner customizes must live in `instance/` or at the instance root.
