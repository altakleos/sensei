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

## References

- Design: [`docs/design/transcript-fixtures.md`](../../docs/design/transcript-fixtures.md)
- Decision: [`docs/decisions/0011-transcript-fixtures.md`](../../docs/decisions/0011-transcript-fixtures.md)
- Load-bearing principle #6 in [`docs/sensei-implementation.md`](../../docs/sensei-implementation.md)
