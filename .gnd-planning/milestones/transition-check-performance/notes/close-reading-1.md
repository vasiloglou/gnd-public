# Milestone-close review: transition-check-performance (issue #24)

- **Reader:** 1 of 4. One reader is one reader, not a panel.
- **Lens:** semantic correctness, and the CR-01 / no-wrong-answer guarantee across the whole milestone (TP1, TP2 and TP3 together).
- **Main commit reviewed:** `2689ab3` (origin/main, the merge of PR #30). The runtime diff is `git diff 2d1ff4d 2689ab3 -- src/gnd`: 9 files, +218/-19.
- **Method:** I exported `git archive origin/main` into scratch (`scratchpad/main`) and ran every experiment against those bytes with `PYTHONPATH=scratchpad/main/src`. The probe scripts are in `scratchpad/exp/`. I edited no repository file. I briefly checked out `origin/main` detached in the worktree, then restored the original branch (`claude/transition-check-performance-tp3`, clean apart from the pre-existing untracked `.agents/skills/`).

## What I reproduced (evidence for the verdict)

| Check | Result |
|---|---|
| Ran `tools/measure_transition_cost.py --repeat 1` on main bytes | My `digests.json` is **byte-identical** (`cmp`) to `evidence/TP0/digests.json`, and so to TP1, TP2 and TP3 (all hash `d736d4d7…`). Coverage: reporter check / compiled / admission, transition with and without a declared post, the course control, CLI snapshot check, the CLI `--pre/--steps/--post` arm and CLI batch, plus in-process branch-trace digests. |
| Replay counters on main (my run) | Reporter: `checker_runs` 25, `model_index_key_paths` 26 (TP0 540), `model_dumps_other` 457 (unchanged), `deepcopy_nodes` 115,294 (TP0 2,760,394, −95.8%). Course: key paths 2, dumps_other 105, nodes 4,092 (from 21,492). These match `evidence/TP3/counters.json` exactly. |
| `tests/test_tp1_index_scope.py`, `test_tp2_shared_fact_types.py`, `test_tp3_check_receipts.py` on main | 31 passed. This includes T2 of TP3, which asserts 25 → 19 checker runs, 13 identical payloads and identical per-call traces. |
| Do shared TP2 rows escape? I collected the ids of every container reachable from the cached `ModelIndex._document` and intersected them with everything reachable from returned objects. Reporter: 7 `api.check`, 7 `check_with_receipt` payloads, `receipt.report`, raw `checker.check` reports, 12 transitions with and without a receipt. Course: also `compiled_operations=True` and both transition routes. | **0 shared containers** in every case. The cached index object is unchanged afterwards. |
| Does `model_dump` alias live model rows into the content-keyed cache (TP1×TP2)? I mutated model A's `fact_types[0]` after indexing, then loaded a content-equal model B. | 0 containers shared. B receives the cached index without A's mutation, so content-keyed sharing is sound. |
| Receipt reused 3× on the same objects (course attempt-3) | `receipt.report` is unchanged (JSON digest equal). All 3 payloads equal the receipt-free transition. |
| Do receipt payloads share containers with `receipt.report`? | 0, both for the mint payload and for the transition payload. |
| Reference-bearing model (`reference-corpus/dispatch`, embedded context, `references=None`) | Mint payload equals `api.check` for both the clean candidate (exit 0, reusable) and an edited candidate (exit 1, not reusable). The reason: `checker.check` binds the combined population itself (`checker/_core.py:2060`), and the catalog's bytes are pinned by the `sha256` in the model, which the ModelIndex key covers. |
| Model or population state that the receipt keys do not cover | `Model._compiled` and `_references` are private and not in the key. `_compiled` is read only by the transition and output code, never by the default check (grep). `_references` content is pinned by the model's `sha256` (see above). `Population.warnings` is excluded from `_content_digest` and is not read by the checker. `PARTIAL_OPAQUE` and the other ContextVars are set only inside GND's own non-default modes, never left set at a public entry. |

## Findings

| ID | Class | Severity | Finding | Evidence / reproduction | Disposition proposed |
|---|---|---|---|---|---|
| R1-H1 | hardening | low–medium | **A receipt's stored verdicts can be edited in place, and a later transition silently gives a different answer.** `CheckReceipt` is a frozen dataclass, but `receipt.report` is a public, unfrozen pydantic `CheckReport` with a list of mutable verdicts. Nothing at use time detects in-place edits. In two variants, every pre verdict set to `"fail"` and `verdicts.clear()`, the transition with `pre_receipt=` was **accepted** and returned a different normalized payload (exit 0 both ways). This is the TP3 review's H1, reproduced. The TP3 record dismissed it as outside the threat model. Against that: TP-R2 says "mutation of nested content, by any route, invalidates", and the docs call receipts "opaque values" without warning against touching `.report`. A caller post-processing the report (sorting or filtering verdicts) is the accidental case the receipt exists to guard. The default path is unaffected. | `scratchpad/exp/tamper.py`, `tamper2.py` | Carry over. Cheapest fix: keep a private deep copy (or a digest of the report) and refuse or copy at use. Otherwise record it explicitly as a documented limitation in `python-api.md`. Not blocking: the caller has to write into a GND-owned object. |
| R1-H2 | hardening | low | **The TP1 invariant ("a scope lives for exactly one public call") is a convention. `index_scope` / `scoped` are public names in `gnd.model_index`, and a caller-held outer scope weakens the receipt's `model-changed` guard.** Inside a caller's `with index_scope():` I minted a receipt, mutated `operations[0]` and called `transition(..., pre_receipt=r)`: it was **accepted**. Without the outer scope it is refused with `model-changed`. Today's harm is nil. Operations-only edits do not affect the pre-check, and marker-visible edits are still caught by `population-unvalidated`. No GND entry point holds a scope across a caller mutation; I checked all 7 scoped entry points and none mutates model content. | `scratchpad/exp/outer.py` | Carry over as defense in depth. Either underscore the scope API (as F3 proposes for `iter_fact_types_shared`), or have `_validate_pre_receipt` compute the key outside any inherited scope (`_for_model_uncached`). |
| R1-C1 | completeness | low | **The stated boundary does not match the code: references.** The `CheckReceipt` docstring says references are unsupported, and `python-api.md` says references are "outside this feature". The code refuses only an explicit `references=` argument. A reference-bearing model with an embedded bound context mints **reusable** receipts and they are accepted. I reproduced that the behaviour is correct on `dispatch` (good and bad candidates), for the reason given in the table above. No test pins it. This is the TP3 review's C1, still open. | `scratchpad/exp/ref1.py`, `ref2.py` | Either refuse when `model.reference_populations` is non-empty, or narrow the docs to "explicit `references=`" and add the reference-corpus receipt test. |
| R1-C2 | completeness | low | **Coverage of predicate 2 is complete except for two narrow points.** (a) The course control has no declared-post transition surface. The declared-post route is covered on the reporter workload, and the TP3 reviewer probed it on course. (b) The CLI arms run as subprocesses, so their branch traces are not captured. The trace clause is met by the in-process surfaces only. Neither hides a difference I could find. | `tools/measure_transition_cost.py` `surfaces()` / `cli_surfaces()` | Record it in the close record's evidence description. No action needed. |

**No blocking finding survived.** I could not get a default-path result to change, and I could not get stale or mutated state reused through any public route under the stated threat model. The two exceptions above (R1-H1 and R1-H2) need the caller to edit a GND-owned object or to hold an internal scope.

## Answers to the three questions

**(1) Do TP1, TP2 and TP3 together change a default-path result, or let stale or mutated state be reused?** No, by the evidence above.

- **TP1:** the scope is per call, keyed by object, keeps the model alive, holds at most 8 entries, and lives in a ContextVar. It is entered only by the 7 decorated entry points plus `check_with_receipt`, and none of them mutates model content. The only write is the private `_references`, which is outside the key and pinned by the `sha256`. Across calls, a mutation gets a fresh key: TP1 T2/T3 pass on main, and without an outer scope my run refuses with `model-changed`.
- **TP2:** shared rows never escape into payloads, reports or receipts (0 shared containers). `model_dump` copies, so the content-keyed cache cannot carry one model's later edits to another. TP2's frozen-row run covers the 8 readers.
- **TP3:** the receipt's report and branches are the same objects a fresh pre-check would produce. Parity holds over 3 reuses, on the declared-post route (reporter) and with reference models. Receipts minted in one scope and used in another are revalidated in the user's scope, because `_validate_pre_receipt` runs first inside `_run_transition`'s fresh scope. The interaction exceptions are R1-H1 and R1-H2.

**(2) Are completion predicates 2–5 met by the evidence on main?**

- **P2:** met. I reproduced the digests byte-for-byte, with the R1-C2 caveat.
- **P3:** met. Key paths are 26 on the reporter (13 calls plus 13 loads, within the TP1-C1 bound) and 2 on course. `model_dumps_other` is unchanged (457 / 105). The mutation tests pass.
- **P4:** met. Nodes fell 95.8% on the reporter. The removed copies are guarded by the frozen-row tests (`test_t2_frozen_readers`, review F1) and the detached public accessor tests.
- **P5:** met. The tests assert 25 → 19, one checker run per mint, identical payloads and traces, and named refusals with 0 checker runs. The refusal of a mutated receipt report is not covered (R1-H1). Minting is not "no extra run" on the raise fallback (TP3's H2, harmless).

**(3) Does the code fail to honour any boundary the records claim?** Two mismatches:

- "References unsupported / outside this feature" against what the code actually accepts (R1-C1).
- "Opaque" receipts together with "mutation by any route invalidates", against the mutable `receipt.report` (R1-H1).

Neither produces a wrong answer from correct use.

## Verdict

**close-with-carryovers.** Carry R1-H1 (the mutable receipt report) and R1-C1 (reference boundary: docs or refusal, plus a test) into the open-questions sweep or a successor milestone. Record R1-H2 with the F3 naming question. R1-C2 is a note for the close record only.
