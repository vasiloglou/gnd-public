# F1 · Report the pool byte cap through PoolValidationError

Awaiting owner review.

## 2. Provenance

Draft r1, 2026-11-25, at main `4dea8dac`. [Plan §§0, 4 and 9](refactoring-followups-plan.md), issue #300, RF9 repair and close-sweep C64. No review has run over this draft.

## 3. Obligations

| Source | Required result | Discharge |
|---|---|---|
| #300 and C64 | Oversized input has a single input finding, like depth refusal | §§5–8, boundary pair |
| RF9 CI repair | Malformed JSON keeps its decoder exception. Duplicate keys, nonfinite values and depth retain domain refusal | §8, existing regression cases |
| Pool loader contract | Schema before coherence, stable identity on success | §§6, 8, existing pool tests |
| Plan §§0, 9 | Bounded read, one policy owner and focused consumer evidence | §§4, 6, 8 |

## 4. Standing rules

**Totality.** Bound the pool read before decoding and give over-budget bytes a defined domain error. Exercise malformed and deep input. **Algorithmic cost.** Request at most the cap plus one byte. Instrument the read size and run the over-limit path in a subprocess with a proposed five-second processing deadline after imports. **Order.** Check size, then decode, parse, check schema and check coherence. Use overlapping failures to prove priority. **One policy walk.** Reuse the shared JSON checks and one size constant. **One normative home.** Put the caller-visible exception contract on `load_pool`. **Measurement.** Run the existing and proposed fixtures on base and candidate, recording actual exception types and identity.

## 5. Goal

A caller catching `PoolValidationError` receives `.failures == ["input: JSON input exceeds byte cap"]` for a pool one byte above the limit. The focused test command exits 0.

## 6. Design

| Search and existing owner | Decision |
|---|---|
| Component searches for “poolfile” and “pool artifact”, verified in src/gnd/synth/poolfile.py | Adapt synth.pool at the existing loader. |
| Search for “input_policy”, verified in src/gnd/input_policy.py | Reuse infra.input_policy.MAX_BYTES and its JSON decoder. |

Keep `load_pool(path: str | Path, model: Model) -> Pool` and `PoolValidationError(failures: list[str])`. Replace the unbounded text read with a binary read of at most `MAX_BYTES + 1`. Refuse overflow immediately, then decode admitted bytes as strict UTF-8, preserving the current text reader's newline handling for existing diagnostics. Pass text to the existing parser. Preserve the existing shared-refusal handler and native I/O, Unicode and malformed-JSON exceptions. The shared byte decoder accepts other encodings, so feeding it raw bytes would widen the input contract. No schema or hash changes.

## 7. Decision

| ID | Proposed ruling | Observable cost |
|---|---|---|
| D1 · open | Count file bytes before UTF-8 decoding and universal-newline conversion. | A CRLF-heavy file whose disk size exceeds the cap can currently fit after translation. A raw-byte limit refuses it. Retaining translated-text sizing requires a streaming text budget and a distinct physical-read policy. |

## 8. Tests

Extend `tests/test_poolfile.py` with a valid pool padded to the exact cap and one byte over. Compare the admitted hash to its unpadded control. Verify the one-byte-over and reported 11 MiB cases have exactly the finding in §5. Pin D1 with a CRLF-heavy boundary case. Test an oversized malformed prefix to establish priority and a guarded reader to assert maximum requested bytes. Confirm under-budget invalid UTF-8, malformed JSON, missing file, schema and coherence outcomes retain their types. Use deterministic local fixtures. Each test expects pytest exit 0 on the candidate.

Run `uv run pytest -q tests/test_poolfile.py tests/test_rf9_ci_repairs.py tests/test_rf7_input_policy.py tests/test_rf7_consumers.py --tb=short` and `uv run ruff check src/gnd/synth/poolfile.py tests/test_poolfile.py`. Record the baseline mismatch for the new regression, the candidate summaries and the time-bound result.

## 9. Scope

F4 owns other producers and validator policy. F1 changes the pool file boundary only.

## 10. Size

Estimate 10–20 changed source lines in the pool loader and 45–80 test lines. Record actual size at phase close.

## 11. Approval instrument

The owner gates this prose and D1 after the milestone plan gate. Implementation begins only on a separately selected phase execution.
