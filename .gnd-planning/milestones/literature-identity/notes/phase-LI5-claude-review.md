# LI5 Claude Code diff review

One read-only Claude Code reviewer, Sonnet high effort, prompt on stdin. Phase base 0fffbba5. Prompt SHA-256: `ce866ee28c93f6a86dac664a3d560eca85dafdcf97e9cba26444e41cd4cb3a99`. Output retained verbatim with host paths sanitized if present. The reviewed inputs disclose both aggregates and exclude the reserved key and private annotations.

---

# LI5 independent review: L1–L6 and C6

**Verdict:** I could not refute the positive half of the claims. The "supported kept" counts, the transfer interface arm and the replay exit contract hold up. I did refute the strength of three claims:

- The false-chain exclusion counts do not discriminate.
- The proof does not carry decision provenance beyond a whole-record digest.
- The reserved L1 pass is a post-hoc result, not an independent one.

I ran nothing, as instructed. Every "reproduction" below is a prediction from reading the code. I did not hash any files. I did not open the reserved key, the reserved annotations or the `literature-heldout` ref.

## Findings

### F1 (High): "false chains excluded" cannot fail by construction (L1, L2, C6)

- **Constructor.** `lineage_run.assemble` always writes the manifest with `"renamings": []`.
- **Join rule.** A `same` decision requires equal outcomes (`composition_resolution.py:325-328`). Without renamings, an outcome is the spelling itself. A `same` decision across different spellings therefore makes compose refuse with "keys are not joined", and `lineage_run` returns exit 3.
- **Consequence.** Every merge-style false chain in development uses different spellings: c04 (VAMPnet/VampNet, WhAM/WHAM) and c05/c06 ($PINN/PINNs). No input the constructor accepts can make any of them accepted.
- **Decisions are no-ops here.** The three `different` decisions in `development-input.json` sit on differently spelled keys. The spelling-group check at `composition_resolution.py:353-362` never fires for them.
- **Reproduction (predicted).**
  - Delete the three `different` decisions and assemble. It still succeeds and `score` still reports 3/3 supported and 5/5 excluded.
  - Add a `same` decision for `(vampnets, VAMPnet)` and `(wham-whale, VampNet)`. Assemble exits 3.
- **The other false chains are not independent evidence either.**
  - c07 is overdetermined: "Boltz-1" differs from "Boltz-1 family" and the predicate is `evaluated-as`. Only the extra `PoseX → Boltz-1 family` query in `test_named_development_paths` isolates the predicate.
  - c08 is excluded by dispositions the annotator copied from the key's own labels (`stretched`, `contradicted`), which is circular.
- **Direct evidence from the phase.** The first reserved run scored supported 0/1 and excluded 2/2 (`"phase": "first-frozen-input"`). A run with a broken annotation still excluded everything. The excluded numerator is satisfied by an empty input.
- **Scorer detail.** `score()` records only the witness exit and discards which claim was unsupported. A misspelled labelled path counts as "excluded" (`lineage_run.score`, the `kind`/`correct` block). No test shows a false chain being accepted and counted as a miss.
- **What is real.** c01–c03 depend on the three `same` decisions, because equal spellings across sources need a `same` decision or compose refuses (`composition_resolution.py:346-352`). The supported-kept counts are therefore genuine evidence.

### F2 (High): the proof binds decisions only through the record's file digest (L5)

- **What reaches the proof.** `lineage_index` returns only `fact["sources"]` (`composition.py:408-409`). `_stamp_composition` copies those into base nodes and adds the record digest (`witness/service.py:62-83`). Decision indexes never enter the certificate.
- **Producer path.**
  - `_composition_lineage` (`service.py:44-59`) checks only that the record parses and that its model and population digests match.
  - `parse_record` enforces canonical form and decision-list shape (`composition.py:154-204`).
  - It does not re-derive decisions. Only `verify_composition` (`composition.py:391-403`) does that, and the scorer calls it. `gnd witness --composition` does not.
- **Reproduction (predicted).**
  - Use the test's `other` record (decisions emptied, re-canonicalised) with the same population.
  - `gnd witness … --composition other` should exit 0 and stamp the forged digest.
  - `gnd replay` against that forged record should also exit 0.
- **What the test shows.** `test_proof_binds_contextual_claims_and_decision_lineage` shows that any byte change to the record gives `binding-stale` (`kernel.py:313-314`). It does not show that decisions specifically are bound.
- **Weaknesses in the test.**
  - It asserts `lineage["decisions"]` is non-empty only for `contextual[0]`'s row. The other base node and the decisions on the path's own edges are not examined.
  - `stamp_lineage` cites every decision touching a row's keys (`composition_resolution.py:256-276`), including the no-op `different` ones from F1.
- **Proof-side mutation.** The test edits `node["sources"][0]["fact_index"]`. That hits the sources-versus-record check at `kernel.py:330-334` and gives exit 1. It does not edit a base node's fact tuple or origin.
- **Effect on L5.** The plan says the witness names the assertions and the record names the decisions, and that removing either fails replay. That holds as digest binding only. The scored route is protected because `score()` calls `verify_composition` first. The public witness and replay route is not.

### F3 (Medium): the transfer rule's assumption and qualification arms are unexercised (L3)

- **Interface arm.** `Serein`/`Nimbus` (regime `unspecified`) is a clean minimal pair against `Nimbus`/`Atlas`. `test_qualified_transfer_and_transitive_missing_interface` also asserts lineage exit 0 for those rows. This arm genuinely discriminates.
- **Assumption arm.**
  - Every conditional row in `control-input.json` has `condition: "low noise"`.
  - LI4 admission already rejects `conditional` with an absent condition, and `unqualified` with a concrete one (`assertion_admission.py:83-97`). Such a statement is removed from lineage too, so it cannot be a transfer-only discriminator.
  - The `$condition != …` where-clauses (`model.orm.yaml:367-378` and the four repeats) are unreachable from assembled runs.
- **Sentinels.** The `none` and `n/a` sentinels are also dead for assembled runs, because `_authority` rewrites them to `unspecified`. Case and whitespace handling lives only in the assembler, not in the model.
- **Qualification gate.** No fixture has `unqualified` plus a concrete regime, so the `qualification: "conditional"` binding is not isolated either.
- **Reproduction (predicted).** Remove the condition where-clauses and the qualification binding from `transfer_step` and rebuild. T3 still passes.
- **Claim refuted.** The corpus gate's statement that "two separate support conditions … can be removed independently" is false for the assumption. Spec T3's "one missing transfer prerequisite" is met only for the interface.

### F4 (Medium): the `training-on-outputs` positive arm is witnessed nowhere, and the L3 unreviewed-edge case depends on it

- A grep of `tests/` finds no reference to `Adaptor A`, `Tuned A`, `Port A`, `System P` or `training-on-outputs`. Those control rows (`control-input.json`, p10–p12) are never queried.
- The `Alto → Beta` unreviewed case itself uses `training-on-outputs`. If that clause were deleted from the model, the blocked case would still exit 2.
- Positive arms for `fine-tunes`, `implements`, `extends` and `component-use` are witnessed through c01–c03 and the control. Transfer arms are exercised only through `extends`.
- Asserting exit 0 on the three unqueried rows would give each excluded relation its minimal positive twin.

### F5 (Medium): T2's "opposite direction" has no test

- `test_only_eligible_relationships_supply_a_lineage_edge` queries the four non-chaining pairs and the two blocked pairs, all in the forward direction.
- No test queries a reversed eligible edge, for example `lineage_ancestor(Atlas, Nimbus)`.
- Orientation is implied only by the 3/3 supported scores (`pairwise` yields `(parent, child)`, and the claim is `arc(child, parent)`).

### F6 (Medium): the scorer does not do what the freeze records say it does (C6)

- **Missing bindings.** `score(model, run, answer_key)` neither reads `path-policy.json` nor compares the model or key digest to any pinned value. Record 021 says the key digest is verified before scoring.
- **Unreviewed wrapper.** The committed aggregate JSONs carry `path_policy_sha256`, `annotations_sha256` and `phase`. `score()` emits none of these and does not emit the key, so a wrapper outside this diff produced them. That wrapper is unreviewed and unrecorded.
- **Receipt chain not re-verified.** `verify_composition(..., run/"sources")` re-derives composition from `sources/` only. It never re-runs admission or compares `sources/<id>/population.json` with `admissions/<id>/admitted.population.json`. A hand-edited source population with a recomputed composition would pass.
- **T7 coverage.** Only two hostile cases are tested: NaN JSON, and a trailing space in `resolution.json`. These are untested:
  - document digest mismatch (`input:document-digest`)
  - path escape
  - the 32/32/128 caps
  - an unadmitted resolution key
  - stale receipts
  - an existing output directory

### F7 (Low): policy and model drift risks

- `non_chaining` is never read by the builder or any test.
- `absence_words` is not tied to `ABSENT_CONDITIONS`.
- Spec says the policy has "lineage and transfer arms" per predicate. The file has one global `transfer` block.
- No test regenerates the model from the policy. The "byte-identical regeneration" in 021 cannot be re-checked from the suite.
- Record 021 froze `lineage_run.py` at `1fbc…`. Record 022 re-pins it at `a00b…` after the rule freeze. It is disclosed and happened before key access. I cannot tell from here whether the diff's final file is `a00b…`.

### F8 (Low): L4 and T6 assertions are looser than the plan wording

- **Cycle test.** `warnings` accepts any warning, not specifically the ring constraint on `lineage_arc`. The acyclic control is a hand-truncated copy of the cycle population with hand-written derived rows. `assert len(...) == width` on the control is tautological, because the test sliced the rows itself. Only the initial `== 2` on the assembled run is real. `gnd witness` on the cyclic run is never invoked.
- **Reversed-claim test.** The `any(row["verdict"] == "fail" …)` assertion does not pin the fact type (`lineage_arc`) or the "unsound or missing" reason that T6 asks for.

## Reserved-input correction versus the plan's procedural criteria

**Plan text.** C6 (plan lines 461-467) requires:
- the key stays off the development branch;
- rule and policy digests are committed before the held-out set is scored, and the score binds them;
- three chains count as a smoke test.

L1 (line 550) requires every supported chain to be kept on the held-out set as well.

**What holds literally, on both runs.**
- Both result files carry the same model (`a63b…`) and policy (`cc27…`) digests, committed before scoring in 3463cdd1 and 021.
- The first run used exactly the input pinned in 022 (`5ac1…`, composition `cd27…`).
- Both results are labelled smoke.

**What does not hold.**
1. **The pre-registered measurement failed L1.** It scored supported 0/1 with exit 1. The pass exists only after a second input (`387b…`).
2. **The correction used key knowledge.** Record 023 says the change came from "identifying the missing endpoint". Only the key reveals that endpoint's name. The participant naming was then fitted to the key, and the encoder qualifier was moved into `regime`.
3. **The held-out sample cannot absorb that.** With one supported chain, a post-hoc annotation edit is as large as the sample. C6 exists to prevent exactly this overfitting. Because C6 guards only rule and policy digests, the fitting moved into the annotation layer, which the digests do not cover.
4. **The 2/2 excluded numerator adds nothing.** It was identical before and after the correction and is non-discriminating (F1).
5. **The approval is not independent.** The amendment is an `auto=true` self-approval. 022 calls the first preparation "independent", yet the correction came from the same operator after seeing the result.
6. **Reproducibility.** 023 and `evidence/LI5/` are untracked. The corrected input was never pinned before the second score. Both inputs stay outside the worktree, so only digests are auditable.

**Conclusion.** The correction does not meet the intent of C6, though the digest mechanics are intact. The reserved L1 outcome should be recorded as: pre-registered measurement failed (supported 0/1, excluded 2/2); post-hoc corrected result 1/1 and 2/2, not an independent confirmation. Whether L1's reserved clause can then close is an owner ruling, because the plan has no provision for amending an input after a failed measurement.

## Claims I tried to refute and could not

- **Eligible-path rules.**
  - `lineage_step` and `transfer_step` (`model.orm.yaml:117-262`, `336-658`) each contain exactly the five chainable predicates.
  - Each requires `polarity=asserts`, `attribution=own-finding` and both participant kinds `sense`.
  - The four non-chaining predicates have no clause. Each has its own control pair, and each pair is asserted present in the admitted statements.
- **Directed-edge scoring.**
  - `lineage_arc` is a one-hop projection (`model.orm.yaml:751-763`).
  - The scorer demands every arc plus the endpoint. An alternate route cannot rescue a path with a missing arc.
  - `exit_code in (0, 2)` is enforced, so a checked refusal is never counted as an exclusion.
- **Boltz-1.** The `evaluated-as` statement is in the admitted population, and `lineage_ancestor(PoseX, Boltz-1 family)` exits 2.
- **Unresolved and unreviewed gating.** The `Beta → Gamma` mention and the `missing` disposition behave as designed. The latter produces no receipt, and `_support` returns `missing`.
- **Transfer chain.** `transfer_ancestor` requires `transfer_step` on every hop, and `Cumulus → Atlas` fails on the middle hop with a lineage twin asserted.
- **Replay exits.** A changed base-node source gives `InvalidProof` (`kernel.py:330-334`), exit 1. A different record gives `binding-stale` (`kernel.py:313-314`), exit 3. Both match `cases.json`.
- **Cycle and flat-whale fixtures.** The cycle run retains both edges and the acyclic control shows no warning. The flat whale fixture is not referenced from the scored input.
- **Input bounds.** Assembly has the required caps, rooted document reads, a document digest check, passage uniqueness and refusal of unadmitted resolution keys.

## Limitations of this review

- I executed no tests, builds or hashes. F1, F2 and F3 reproductions are predictions from `composition_resolution.py`, `service.py`, `kernel.py` and `assertion_admission.py`. I did not read the producer or kernel beyond the lines cited, so I did not check whether base-node fact tampering is caught elsewhere.
- I could not confirm that the model, policy, scorer and builder in the tree match the digests in 021 and 022.
- I did not see the wrapper that produced the aggregate JSON, the reserved annotations or the reserved key, so the correctness of the reserved chains is outside this review.
- I assumed `api.witness(..., composition=…)` routes to `composed_witness_result`. I did not read `api.py` or the customer disclosure view.
- The reserved false chains might use identical spellings across sources, which would make F1 weaker for them. I cannot tell without seeing the annotations.
