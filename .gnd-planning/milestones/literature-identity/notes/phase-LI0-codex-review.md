# Adversarial review: LI0 @ dc4ce588 (base f154a59c)

> **Edited for retention.** Absolute paths of the reviewer's checkout were
> replaced with `<repo>` per the project's evidence guard. The text is
> otherwise verbatim, and the trailing summary paragraph that Codex printed
> twice appears once.

**Instrument.** `codex exec --ephemeral --model gpt-6-sol --config
model_reasoning_effort="xhigh" --sandbox read-only --color never
--skip-git-repo-check -`, with the prompt on stdin. It exited 0.

**Scope.** One reviewer is one reviewer. Pytest could not start in the
read-only sandbox. The reviewer verified some claims by in-memory runs and
the rest by reading, as stated below.

## Review (verbatim)

**I found no behavioral counterexample to claims 1–4. I found three defects in the claimed test evidence (claim 5).**

1. **The tests are not all red on the base source.** [test_li0_witness_wire.py:97](<repo>/tests/test_li0_witness_wire.py:97) includes the already-supported `grandparent-v2.orm.yaml` case. Reproducing the base dump call in memory gave witness **0**, replay **0**, and the committed certificate SHA-256. The baseline-golden tests at lines 163 and 169 are likewise intended to pass before the fix. Thus the “each test is red” part of claim 5 is false. **Verified by running the base-call simulation; the base pytest suite was not run.**

2. **Three baseline failures have the wrong cause.** [test_li0_witness_wire.py:124](<repo>/tests/test_li0_witness_wire.py:124), [line 193](<repo>/tests/test_li0_witness_wire.py:193), and [line 230](<repo>/tests/test_li0_witness_wire.py:230) import or access `model_wire`, which does not exist in the base source. Reproduction: `git show f154a59c:src/gnd/witness/io.py | rg 'def model_wire'` finds nothing. T4 and T10 would fail on import; T8 would fail on attribute access, before testing round-trip or hostile intake. **Verified by reading the base source.**

3. **T8 can pass without reaching intake.** [test_li0_witness_wire.py:209](<repo>/tests/test_li0_witness_wire.py:209) asserts only `exit_code == 3`. With the test’s valid model, population, and targets, I replaced `producer.validate_targets` in memory with a function raising `ValueError("pre-intake")`: `produce_witness` returned **3**, while spies recorded **zero** calls to both `model_wire` and `intake`. This is a false-pass route for claim 5. On the unmodified head, instrumentation *did* observe intake reject all three hostile values with the expected `WitnessInputError`; the weakness is what the test guarantees. **Verified by running both checks.**

The approved T7 description also promises certificate goldens for composition and v7.1 inputs, but [the T7 test](<repo>/tests/test_li0_witness_wire.py:163) iterates a golden containing only `grandparent-v2.orm.yaml`. It cannot detect changed bytes for those promised inputs. This is an evidence gap for claim 2, **not an observed byte regression**.

For the claims without a counterexample: I ran the four LI0 models through CLI witness and why-not (process exit **0**), replayed their certificates in memory (exit **0**), checked **228** loadable fixture models for the exact two-key projection and JSON round-trip (no failures), matched all **228** identity goldens, and matched the supported certificate digest. I read every `intake` call site; replay, Soufflé, and Lean pass parsed raw model documents. Pytest could not start because this read-only sandbox has no writable temporary directory. No files were edited by this review.

## Triage and disposition

| # | Finding | Reproduced | Class | Disposition |
|---|---|---|---|---|
| R1 | Not every test is red on the base source | Yes, by design: the committed red run at `176355e8` shows 12 failed and 4 passed. The 4 passing tests are the version-2 control, the include control, and the two baseline-golden comparisons | — | No change. The prompt's "each test is red" overstated the plan, which names controls |
| R2 | T4, T10 and T8 fail at baseline because `model_wire` is missing, not for the semantic reason | Yes: `git show f154a59c:src/gnd/witness/io.py` has no `model_wire` | hardening | Added `test_unprojected_dump_is_still_refused_by_intake`. It shows that `Model`'s own dump still carries `operations: []` and `model_id: null` and that intake refuses it. That is the semantic cause, and the test also pins D1 |
| R3 | T8 can pass without reaching intake | Yes: the reviewer's early `validate_targets` refusal returns 3 with zero intake calls | blocking | T8 now spies on `gnd.witness.io.intake` and requires exactly one `WitnessInputError` from it. Under the reviewer's mutation the hardened T8 fails (a scratch mutation test passed with `pytest.raises(AssertionError)`) |
| R4 | The T7 golden covers only the LI0 version-2 certificate | Yes | completeness | Already recorded as spec implementation finding 1 (T7 narrowed), with the binding argument. Carried to the record's boundary |

No behavioral counterexample was found to claims 1–4.
