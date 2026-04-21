# Foundations

Cross-cutting source material above the six-layer SDD stack. Not a processing layer; not a feature-spec genre; source that feature artifacts cite. See [`docs/development-process.md § Foundations`](../development-process.md#foundations) for the method-level description.

## Layout

```
docs/foundations/
├── README.md             — this file
├── vision.md             — product mission + identity (single narrative file)
├── principles/<slug>.md  — cross-cutting principles (one per file, TOGAF shape)
└── personas/<slug>.md    — design-stressing personas (one per file)
```

## Principles: `kind:` decision guide

Every principle file carries `kind: pedagogical | technical | product`. The boundary matters because it predicts who will invoke the principle in which PR.

- **`pedagogical`** — stances about *how learning works* that shape product behaviour. Examples: "silence is teaching", "ask don't tell", "mastery before progress". These drive protocol prose and spec invariants.
- **`technical`** — stances about *how artifacts are built*. Examples: "prose is code", "scripts compute, protocols judge", "config lives in yaml, not hardcoded". These drive design decisions and implementation patterns.
- **`product`** — user-facing promises broader than any one feature spec can name. Examples: "every release has a changelog entry" (already realised by `release-communication.md`), "the folder is the program" (from ideation §1). These constrain multiple specs and designs simultaneously.

When a stance could reasonably sit in two categories, prefer `pedagogical` over `product`, and `technical` over `pedagogical`. The rationale: more specific tag wins. A reviewer who cannot decide is a signal to rewrite the Statement until the tag is obvious.

## Linkage conventions

| From | Frontmatter field | Points at |
|---|---|---|
| Feature spec (`docs/specs/*.md`) | `serves: [...]` | Vision / product principles |
| Feature spec | `realizes: [<P-slug>, ...]` | Technical / pedagogical principles |
| Feature spec | `stressed_by: [<persona-slug>, ...]` | Personas |
| Persona (`personas/*.md`) | `stresses: [<spec-slug>, <P-slug>, ...]` | Specs + principles |

Slugs are the `id:` frontmatter field in each foundation file — `vision` (fixed), `P-<kebab-case>` for principles, `persona-<kebab-case>` for personas.

## Enforcement

See [`development-process.md § Foundations`](../development-process.md#foundations) for the method-level enforcement rules. Sensei's concrete validator is `ci/check_foundations.py`.

## Migration

Moving an invariant between layers (feature spec ↔ principle, principle ↔ vision) requires an [ADR-lite](../decisions/0005-adr-lite-format.md) with Before-state / After-state / Why sections. The superseded artifact is never deleted; it carries `superseded-by:` and stays for archaeology.

## References

- [ADR-0012: Adopt `docs/foundations/` for Cross-Cutting Concerns](../decisions/0012-foundations-layer.md)
- [`docs/development-process.md § Foundations`](../development-process.md#foundations)
- [`docs/sensei-implementation.md`](../sensei-implementation.md) — Sensei-specific instantiation pointers
