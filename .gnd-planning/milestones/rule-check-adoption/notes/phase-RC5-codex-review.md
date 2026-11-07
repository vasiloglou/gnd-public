# RC5 diff review (Codex), retained verbatim

- Instrument: one reviewer in a different tool. One reviewer is one reviewer.
- Command: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin (codex-cli 0.163.0), 85,475 tokens, exit 0.
- Reviewed bytes: `git diff 14f66ad3 a59693d3 -- src tests tools` (implementation commit a59693d3; corpus commit 6b45985b inside the range).
- The reviewer ran in a read-only sandbox and ran no suites. The output below is unedited and contains no local path; the trailing "codex exit=0" line is the driver's.

## Reviewer output (verbatim)

```text
DISPOSITION: revise

ID: T1
SEVERITY: high
LOCATION: src/gnd/witness/io.py:284
QUOTE: `+ hashlib.sha256(canonical_json_bytes(candidate.model_dump(mode="json"))).hexdigest(),`
PROBLEM: `model_dump()` now includes `producer: None`. For the same pre-RC5 population with no producer, this changes the witness `candidate_digest`; replay compares it to the certificate binding and returns `binding-stale`. The preserved `_content_digest` does not protect existing witness certificates.
FIX: Exclude `producer` from this digest when it is `None`, while including a present producer.

ID: T2
SEVERITY: medium
LOCATION: src/gnd/witness/io.py:437
QUOTE: `for k in ("model", "model_id", "source", "label", "covers")`
PROBLEM: `population_wire()` drops a present producer. A loaded corpus `tool-output-producer` population becomes a wire document without `producer`; reloading it yields `producer=None` and a different witness identity.
FIX: Include `producer` in the header when present.

ID: T3
SEVERITY: medium
LOCATION: src/gnd/composition.py:319
QUOTE: `header: dict[str, Any] = {"model": first.model, "source": first.source, "covers": covers}`
PROBLEM: Composition inherits the first population’s `source` but drops its producer. Composing a first source labelled `tool-output` with `producer: "components-scan 1.4.0"` emits a `tool-output` population with no producer, losing that header value.
FIX: Carry `first.producer` with the inherited header when present, and update the composition header documentation.

ID: T4
SEVERITY: low
LOCATION: src/gnd/population_shape.py:242
QUOTE: `parts.append(core_schema.str_schema(strict=True, min_length=minimum, max_length=maximum))`
PROBLEM: The fast path is not equivalent to Draft 2020-12. A JSON producer containing the escaped lone surrogate `"\ud800"` is accepted by Draft and loads, but `accepts_shape` returns false. Also, Draft accepts `42` against `{"maxLength": 200}` because the keyword applies only to strings; this compiler rejects it. The loader’s Draft fallback preserves acceptance.
FIX: Compile length keywords with a predicate that counts Python string code points and leaves nonstrings unconstrained when no string type is required.

ID: T5
SEVERITY: low
LOCATION: src/gnd/population.py:157
QUOTE: `def _producer_names_tool_output(self) -> Population:`
PROBLEM: The invariant is bypassed by `model_copy(update=...)`: `Population(model="m", source="fixture").model_copy(update={"producer": "x"})` produces an invalid `Population`, as does a copy with a 201-character producer. Pydantic does not run this validator on `model_copy` updates.
FIX: Validate the producer and source invariant on copied `Population` instances.

ID: T6
SEVERITY: low
LOCATION: src/gnd/skills/gnd-orm-core/references/population-format.md:3
QUOTE: `**The normative spec** for GND population files (CORE-02) — the universal interchange every population flows through, whether it is an **agent output**, a **synthetic dataset**, or an **eval fixture**. One format, one loader, one checker.`
PROBLEM: This in-scope reference still presents only the three old source categories. The packaged schema’s description likewise omits `tool-output` and `producer`.
FIX: Update both descriptions to include deterministic tool output and its optional producer.

CONFIRMED: The corpus’s three valid `tool-output` cases load and retain their producers; the three invalid cases receive the expected schema refusals.
CONFIRMED: The two schema copies agree, `Population.source` matches their enum, and the extraction projection remains the ruled three-value subset.
CONFIRMED: The loader and reference binder pass a present producer into their `Population` constructors.
CONFIRMED: `_content_digest` preserves its pre-RC5 value when producer is absent.
CONFIRMED: The corpus check payloads match the fixture control apart from the population path.
codex exit=0
```

## Triage (driving agent, 2026-11-06)

Every finding was reproduced or confirmed by reading before it was
believed. Regressions for T1-T3 and T6 are in `tests/test_rc5_tool_output.py`,
each observed failing against a59693d3.

| ID | Class | Reproduced | Disposition |
|---|---|---|---|
| T1 | blocking | yes, and wider than reported: `Population.model_dump()` gained `producer: None`, which moves every digest built from a dump. The full suite at a59693d3 failed 32 tests main passes (witness corpus, session pins, certificate replay, timing instruments), all traced to it | fixed once at the field: `producer` is excluded from every dump when unset (`Field(exclude_if=...)`), so all dump consumers (witness identity, assurance, content digest) see pre-RC5 bytes; the earlier `values.py` special case is reverted. The 32 tests pass with the fix. Regression `test_t1_a_population_without_producer_dumps_as_before` |
| T2 | hardening | yes: `population_wire` dropped a present producer | fixed: the wire header carries it. Regression `test_t2_the_witness_wire_keeps_the_producer` |
| T3 | hardening | yes: composition kept the first source's `source` but not its producer | fixed: carried when present; `docs/reference/composition.md` says so. Regression `test_t3_composition_keeps_the_first_sources_producer` (a source-level pin; the composition route has no small behavioural entry point) |
| T4 | not a defect | confirmed: the fast path refuses a few Draft-valid documents (a lone surrogate; a non-string under a bare `maxLength`) | no change: the fast path is positive-only and every refusal falls back to Draft, so acceptance is unchanged. The record's claim is narrowed to "accepts only what Draft accepts" |
| T5 | hardening, deferred | confirmed: `model_copy(update=...)` skips pydantic validators | deferred: no caller copies a `Population` with a `source` or `producer` update (the two `model_copy` calls update `facts` only); open question in the record |
| T6 | completeness | yes | fixed: the reference's opening paragraph and both schema descriptions name tool output and `producer`. Regression `test_t6_the_reference_and_schema_describe_tool_output` |

The fixes were not re-reviewed.
