# RC1 diff review (Codex), retained verbatim

- Instrument: one reviewer in a different tool. One reviewer is one reviewer.
- Command: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin (codex-cli 0.163.0), 133,983 tokens, exit 0.
- Reviewed bytes: `git diff 76c5af11 24bb5c9e -- src tests` (implementation commit 24bb5c9e; corpus commit 8b2d403a inside the range).
- The reviewer ran in a read-only sandbox and ran no tests; its claims were checked by reading. The output below is unedited and contains no local path.

## Reviewer output (verbatim)

```text
DISPOSITION: block

ID: P1
SEVERITY: high
LOCATION: src/gnd/checking_service.py:271
QUOTE: model, _ = _resolve_model(model_input)
PROBLEM: Reference models bind and read their reference population during model load, before the new refusal at line 304. If the reference file is missing or its hash is wrong, model loading raises ReferenceInputError with an attached model. The error path builds an inner version-15 payload, which _reference_wrap then places in a version-12 wrapper. That wrapper’s schema does not admit a version-15 report. The result also lacks check:rule-ids-unsupported. The committed refusal test uses a valid reference file and misses this path.
FIX: For --rule-ids, validate the model and decide the unsupported-model refusal before binding reference populations. Keep the refusal’s inner report at version 7.

ID: P2
SEVERITY: low
LOCATION: tests/test_tp2_shared_fact_types.py:138
QUOTE: "tests/test_v70_phase4_constraints.py", "tests/test_rf1_semantic_pins.py"
PROBLEM: The TP2 subprocess installs the new frozen-constraint iterator but never runs an RC1 --rule-ids path. T13 checks copying and timing without freezing rows. An identity walk that writes to a shared constraint row could therefore pass these tests, leaving the claimed must-not-mutate contract untested.
FIX: Run an RC1 identity case with the freeze plugin and assert that the constraint iterator served frozen rows.

ID: P3
SEVERITY: low
LOCATION: tests/test_rc1_rule_ids.py:196
QUOTE: assert "remedy:" not in text and "constraint:no_import_loops" not in text
PROBLEM: T10 claims byte-identical text without the flag, but checks only two absent strings and one verdict substring. Changes to headings, counts, spacing, or other lines would pass.
FIX: Compare the complete unflagged text output with a frozen pre-RC1 golden.

CONFIRMED

- Static inspection shows CLI conflicts are rejected before model dispatch, with no JSON payload.
- For an eligible plain model, the identity map uses positional references and the new iterator does not copy or mutate constraint rows.
- The no-flag call uses the existing payload version gates and the text renderer’s default argument.
- The version-15 schema defines the added verdict and top-level fields, including the widened derivation reason set. I did not run tests, builds, or network access.
```

## Reproduction and triage (driving agent)

| Finding | Reproduced | Class | Fix | Regression test (proven red before the fix) |
|---|---|---|---|---|
| P1 reference model whose references cannot be bound yields a v12 wrapper around a v15 report (schema-invalid, no refusal issue) | yes: copy of `models/reference/model.orm.yaml` without its `references/`, `--rule-ids --format json` → exit 3, wrapper 12, inner 15, `issues: []`, schema-invalid; without the flag the same input is valid (inner 7). A second route found while fixing: the "reference model identity is invalid" branch also built before the refusal | blocking (an invalid payload on a reachable input) | `refuse_rule_ids` applied on both reference error routes and the main path (`checking_service._run_check_raw`) | `test_p1_reference_model_with_unreadable_references_is_refused`: fails on 24bb5c9e's `checking_service.py` |
| P2 no test exercises the must-not-mutate contract on an RC1 path | yes: T13 freezes nothing; the TP2 subprocess suites never pass `--rule-ids` | hardening, of this phase's own deliverable (fixed in-phase) | the freeze plugin counts constraint rows; the corpus runs under it | `test_p2_identity_walk_reads_frozen_constraint_rows`: fails with an identity walk that calls `setdefault` on a row |
| P3 T10's "unchanged" claim checked only absences | yes: a changed heading (`BLOCKING  (alethic)`) passes T10 | hardening, of this phase's own claim | pre-RC1 text bytes captured at 8bfbe417 as `tests/fixtures/rc1-rule-ids/pre-rc1/declared-fail.txt` | `test_p3_unflagged_text_is_byte_identical_to_pre_rc1`: fails with that heading change while T10 passes |

What the reviewer confirmed: conflicts are rejected before model dispatch with no payload; the identity map uses positional refs and the new iterator neither copies nor mutates; the unflagged call uses the existing version gates and the renderer's default; the v15 schema defines the added fields and the widened derivation reasons.
