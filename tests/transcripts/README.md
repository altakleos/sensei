# Transcript Fixtures

Behavioural verification for prose-as-code protocols. Each engine protocol at `src/sensei/engine/protocols/<name>.md` earns two files here:

- `<name>.md` — **fixtures file.** YAML frontmatter declares one or more `fixtures:` entries, each pinning a cluster of invariants from the protocol's spec with regex/string assertions.
- `<name>.dogfood.md` — **captured LLM session.** Verbatim transcript with `[LEARNER]` and `[MENTOR]` turn prefixes. Re-captured at each release and whenever the protocol changes.

The pytest loader in `conftest.py` discovers fixture files, pairs each with its dogfood companion, and emits one parametrised test case per fixture. A missing dogfood transcript produces `pytest.skip` — never a failing case.

## Authoring a fixtures file

1. Copy an existing fixtures file as a template.
2. Update `protocol:` and `spec:` frontmatter.
3. Replace the `fixtures:` list. For each invariant cluster, write a fixture with:
   - `name` — short slug.
   - `what_it_pins` — one or two sentences of rationale.
   - `forbidden_phrases` — literal case-sensitive substrings that must NEVER appear in any mentor turn.
   - `required_one_of` — optional regex list; at least one mentor turn must match at least one regex.
   - `required_all_of` — optional regex list; every regex must match at least one mentor turn.
4. Regex patterns should be single-quoted in YAML so backslashes aren't consumed by the parser.

## Capturing a dogfood transcript

1. `sensei init /tmp/dogfood` and hand-edit `/tmp/dogfood/instance/profile.yaml` so it has several topics at varying freshness (some stale).
2. Open the folder with the target LLM agent (Claude Code, Cursor, etc.) and type `review` to trigger the protocol.
3. Paste the session verbatim into the `.dogfood.md` file. Prefix each learner message with `[LEARNER]` and each mentor message with `[MENTOR]`. Anything outside a turn (framing, blank lines) is ignored by the loader.
4. Update the frontmatter `agent`, `model`, and `captured` fields.
5. Run `pytest tests/transcripts/` — green means the LLM respected every fixture. Red means either the protocol drifted (fix the protocol) or the fixture is over-strict (loosen).

## Verification tiers

Prose-as-code correctness is checked at four tiers. ADR-0011 introduced Tier 1; Tier 2 landed at the v0.1.0a9 cut.

| Tier | Runs | What it checks | When |
|------|------|----------------|------|
| 0 | default pytest | script CLI ↔ protocol prose consistency (`tests/ci/test_protocol_script_consistency.py`), schema round-trip of emitted YAML (`tests/test_schema_validation.py`), unit tests of helper functions | every PR, CI-gated |
| 1 | default pytest | lexical assertions on captured `.dogfood.md` transcripts (forbidden phrases, required regexes) via `conftest.py` parametrization | every PR, CI-gated; missing dogfood → `SKIPPED` (not failure) |
| 2 | **manual pre-release** | one scripted E2E in `tests/e2e/` that invokes headless Claude Code against a fresh Sensei instance and asserts the emitted goal file validates against `goal.schema.json` | before each release tag, maintainer workstation |
| 3 | **deferred post-v0.1.0a9** | LLM-in-CI matrix across multiple protocols + agents, cost-capped, nightly only | not yet |

Tier 2 skips in default CI because runners lack the `claude` binary and API credentials. Opt in with `ANTHROPIC_API_KEY=...` or `SENSEI_E2E=1` plus `pytest tests/e2e/ --no-cov`. See `docs/operations/release-playbook.md` § Pre-release gate.

## References

- Design: [`docs/design/transcript-fixtures.md`](../../docs/design/transcript-fixtures.md)
- Decision: [`docs/decisions/0011-transcript-fixtures.md`](../../docs/decisions/0011-transcript-fixtures.md)
- Load-bearing principle #6 in [`docs/sensei-implementation.md`](../../docs/sensei-implementation.md)
