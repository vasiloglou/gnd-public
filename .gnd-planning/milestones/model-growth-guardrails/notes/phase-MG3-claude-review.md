# Phase MG3 review: duplicate-shape report (`gnd evolve preview --shape-report`)

Reviewer: single adversarial local reviewer agent (spec D1 review instrument).
Subject: `git diff 9b069e2` plus untracked `src/gnd/evolve/shapes.py`,
`tests/test_evolve_shape_matches.py` and `evidence/MG3/` in worktree
`intelligent-pasteur-df4027`, as of 2026-11-04. I treated the repository as read-only. Every probe
lives in this scratch directory and writes only to pytest `tmp_path`.

Probe files:
- `/private/tmp/claude-501/-Users-nikolaosvasiloglou-github-repos-gnd-public--claude-worktrees-intelligent-pasteur-df4027/3c87e025-cf83-4ba9-a19d-bb65f88a9984/scratchpad/review-mg3/probe_mg3.py`
- `/private/tmp/claude-501/-Users-nikolaosvasiloglou-github-repos-gnd-public--claude-worktrees-intelligent-pasteur-df4027/3c87e025-cf83-4ba9-a19d-bb65f88a9984/scratchpad/review-mg3/probe_mg3_cap.py`

Run them from the repo root with `uv run pytest -p no:cacheprovider -s -q <file>`.

## Verdict

**approve-with-fixes.** The signature rule, the bucket index, the omission in the serializer, and
the apply wiring (fresh preview, breaking-acceptance rebuild, retry identity) are correct for the
cases the spec names. MG-R1 parity holds: I recaptured it and got byte-identical output. Without
the option, MG-R4 holds.

One blocking defect remains. The report's output grows quadratically, so a `--shape-report`
preview can exceed the 10 MiB preview read cap. Apply then exits 74 on a proposal whose plain
preview applies. That breaks the spec Goal and MG-R4. There are also two content bugs in edge
cases and two doc contradictions.

## Findings

### R-F1 (blocking): option-only size blow-up makes apply exit 74 (MG-R4, spec Goal)

Each entry repeats the whole bucket. With `k` adds sharing a signature with `m` existing fact
types, the report emits `k*(m+k-1)` `ShapeMatch` rows. Standing rule 2 bounds probes and T7
counts probes, but nothing bounds the output. The preview read path caps claims at
`MAX_EVOLUTION_PROPOSAL_BYTES` (10 MiB, `service.py` `_read_evolution_claim`). Apply therefore
refuses a report-carrying preview whose plain twin applies.

Reproduction: `probe_mg3_cap.py`. The base fixture gets 400 extra `(order, memo)` fact types
(model of about 600 fact types), and the proposal adds 200 more `(order, memo)` fact types.

```
[CAP] preview plain exit=0 bytes=990719
[CAP] preview ('--shape-report',) exit=0 bytes=22725344
[CAP] apply after --shape-report exit=74 stderr=b'EVOLUTION APPLY REFUSED (74): preview .../preview.json is malformed: evolution preview could not be read safely: artifact preview.json is 22725344 bytes, over the 10485760-byte cap\n'
```

Related time bound (probe P8c in `probe_mg3.py`): 5,000 existing fact types and 500 adds, all in
one bucket. `shape_matches` alone emits 2,749,500 matches in 12.7 s. T7's "under 5 s" holds only
for its spread-out generator (`i%100`, `i*7%100`).

Suggested fix: make the output linear. Group by signature, for example one `signatures` table
(`signature`, `existing: [ShapeMatch]`, `added: [ids]`) and per-ADD entries that name their
signature. A weaker alternative is a per-entry cap with a `truncated_count`. Either way, add a
T7 variant with a single bucket that asserts preview bytes and time, plus a CLI case where a
large bucket previews and then applies with exit 0. If quadratic output is kept on purpose,
the spec and contract must say that apply can refuse with 74, which contradicts MG-R4.

### R-F2 (hardening): an ADD that the same proposal later DELETEs gets a phantom entry with reading `"None"`

`_added_fact_types` takes every fact-type ADD from the operations without checking that the id
survives in the candidate. `candidate_signatures.get(id, ())` then gives the signature `()`. Two
such ids match each other as `added`. `_match` reads `candidate_index.fact_type(other) or {}`,
and `str(fact_type.get("reading"))` turns a missing reading into the literal string `"None"`.
That is a fabricated reading, and `NonEmptyString` accepts it.

Reproduction: `probe_mg3.py::test_p3b_add_then_delete_with_other_change`. The proposal adds
`order_has_note` and `order_has_note2`, deletes both, then adds `customer_visits_order`. The
preview succeeds with and without the option, and the option reports this:

```
{"operation_index": 0, "fact_type": "order_has_note", "signature": [], "references": [],
 "matches": [{"fact_type": "order_has_note2", "origin": "added", "reading": "None", ...}]}
```

The same path likely applies to ADD followed by RENAME of a fact type. I did not reproduce that
case.

Suggested fix:
- Report only added ids present in `candidate_signatures`, or follow renames.
- Never `str()` an absent reading; skip the entry or raise internally.
- Add a test.

### R-F3 (hardening): "existing" uses before-model shapes even for fact types the proposal MODIFYs

D3(a) chose the before model so that deletions still match. A MODIFY that changes roles also
reads the stale before-shape, which causes two errors.

- **P5 (missed duplicate):** the proposal changes `order_has_memo` to `(order, note)` and adds
  `order_has_note` `(order, note)`. The candidate then holds two fact types of the same shape,
  but the report says `matches: []`.
- **P5b (stale match):** the proposal changes `order_has_memo` away from `(order, memo)` and adds
  `order_keeps_memo` `(order, memo)`. The report lists `order_has_memo` with its before-reading,
  although no such shape exists in the candidate.

Output from `probe_mg3.py::test_p5_modify_existing_collides`:

```
P5 entries  [{"operation_index": 1, "fact_type": "order_has_note", "signature": ["note","order"], ..., "matches": []}]
P5b entries [{"operation_index": 1, "fact_type": "order_keeps_memo", "signature": ["memo","order"], ...,
              "matches": [{"fact_type": "order_has_memo", "origin": "existing", "reading": "{Order} has {Memo}", ...}]}]
```

The contract line "Equal ids imply equal reference schemes" has the same weakness when the same
proposal modifies an entity's `reference`, because `references` come from the candidate. This is
an inference from the code; I did not probe it.

Suggested fix:
- Also insert candidate signatures of existing ids that the proposal MODIFYs, either as origin
  `existing` with the candidate shape or as a third origin such as `modified`.
- Or state the limit in the contract's "Shape report" section and in D3.
- MG4 reuses the helper, so settle this now.

### R-F4 (completeness, doc contradiction): a stripped report does not apply on the retry branch

The contract says: "A report removed from the preview, digest recomputed, applies as a preview
made without it: nothing is gated on it." On the candidate-already-live retry branch,
`_evolve_same_review_identity` compares the full dump, `shape_matches` included, against the
staged preview, so apply exits 11.

Reproduction: `probe_mg3.py::test_p6_retry_with_stripped_report` (preview `--shape-report`,
apply, re-apply, strip, re-apply):

```
[P6] retry same preview 0
[P6] retry stripped preview 11 b'EVOLUTION APPLY REFUSED (11): staged accepted preview differs from the reviewed preview identity\n'
```

Suggested fix: either exclude `shape_matches` from `_evolve_same_review_identity`, which is safe
because the report gates nothing, or qualify the contract sentence to say it holds outside the
interrupted-apply retry branch. MG2's matching sentence about stripped policy fields probably has
the same gap. I did not reproduce that one.

### R-F5 (completeness, doc contradiction): "a fact type the same proposal deletes still matches" fails when it is re-added under the same id

The proposal deletes `order_has_memo` (and its exclusion) and adds `order_has_memo` again with a
new reading and the same roles. The report shows `matches: []`, because the
`other != fact_type_id` filter, which the reader rule "a shape match never names its own fact
type" requires, also drops the deleted before-model fact type.

Reproduction: `probe_mg3.py::test_p4_delete_then_readd_same_id`:

```
entries [{"operation_index": 2, "fact_type": "order_has_memo", "signature": ["memo","order"], ..., "matches": []}]
```

Suggested fix: exclude only `("added", own id)`, and relax the reader rule to "never names its
own fact type with origin added". Or document the same-id exception in the contract and in D3.

### R-F6 (hardening): the reader accepts shape reports inconsistent with their own preview

`_check_shape_matches` checks only ordering, uniqueness and self-exclusion. With the digest
recomputed, `EvolutionPreview.model_validate` accepts all of the following:
- an `operation_index` past the operations
- a `fact_type` that the proposal does not add
- a signature that is not the fact type's
- phantom match ids
- an extra entry
- `identity: composite` together with a `value_type`
- `identity: direct` with `value_type: null`
- a duplicated signature id

Reproduction: `probe_mg3.py::test_p7_reader_accepts_inconsistent_report`. P7a through P7i all
print `OK -> accepted`.

Apply is not affected: the fresh/reviewed equality refuses such a document with 11, and T5
proves it. But a preview is also a review artifact that a human or a panel reads, so the closed
reader is weaker than MG2's policy-field checks.

Suggested fix: in `_bindings_match`, require the `(operation_index, fact_type)` pairs to equal
the proposal's fact-type ADD operations. Also require `value_type is not None` exactly when
`identity == "direct"`. Both checks are cheap.

### R-F7 (completeness): no test exercises the declared composite and unmatchable `references` branches

The spec's branch list names "entity and value role player in references (T2)". T2 covers
`direct` only. `test_t2_identity_spellings_match_reference_identity` greps the source of
`reference_identity` for the three literals, so it cannot fail if `entity_reference` returns a
`value_type` for `composite`, or misclassifies a kind.
`grep -n "composite\|unmatchable" tests/test_evolve_shape_matches.py` finds only lines 185 and
187, the literal check.

Probe P8b shows the current code is right for `composite` (`value_type=None`). The gap is
coverage, not a bug.

T3d also lacks reader cases for unsorted `signature` and unsorted `references`.

Suggested fix:
- Add a preview case with an external-reference entity anchored by an external uniqueness
  constraint (composite) and an entity with no resolvable reference (unmatchable).
- Assert `identity` and `value_type` for both.
- Add the two missing T3d reader cases.

## Checked and found sound

- **Signature correctness.**
  - Role order makes no difference.
  - Multiplicity is kept: `(A,A,B)` differs from `(A,B,B)`.
  - A subtype does not match its supertype.
  - Value types are compared by id.
  - Hostile mappings are handled totally.
  - Duplicate role names inside one fact type are rejected by model validation before the report
    runs (P1: `ModelValidationError ... declares role_name(s) ['x'] more than once`), so the
    dict keyed by `role_name` in `role_object_types` cannot hide multiplicity.
- **ADD then MODIFY of the same added fact type** (P2): the entry uses the final candidate shape
  and matches `order_has_amount`. Correct.
- **MG-R1.**
  - `evidence/MG3/parity-before.json` and `parity-after.json` are byte-identical.
  - Both equal MG2's `parity-after.json`.
  - I re-ran `uv run python .gnd-planning/milestones/model-growth-guardrails/evidence/MG2/capture_parity.py <scratch>/parity-rerun.json` (exit 0); the output is byte-identical to `parity-after.json`.
- **MG-R4 without the option.** The report is computed after `_policy_values` and refusals, and
  only `values` reads it. T4 and T4b are meaningful.
- **Apply wiring.** The fresh preview and the breaking-acceptance rebuild both pass
  `shape_report`. A tampered report gives 11 on both the fresh and the retry branches.
- **Reader gating.** V1 and V2 readers stay closed. `_check_shape_matches` is total over typed
  input.
- **Composite reference cost** (P8b): 500 adds over a composite entity take 1.75 s.
- **Anonymity.** A grep over all changed and untracked MG3 files finds no downstream-app names.
- **Layering and RF6.** The tests pass.

## What I ran

- `uv run pytest -q tests/test_evolve_shape_matches.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py`: 121 passed.
- `uv run pytest -q -p no:cacheprovider` over test_evolve_additive_policy, test_evolve_loading,
  test_evolve_references, test_model_evolution, test_public_evolution_{drift_readers,
  legacy_readers,version_graph}, test_public_legacy_evolution, test_v51_phase2_extraction_scope,
  test_evolution_conformance, test_disclosure_mode and test_disclosure_docs: 345 passed.
- The probes in `probe_mg3.py` (P1 to P8c) and `probe_mg3_cap.py`.
- The parity recapture (MG2 `capture_parity.py`) into scratch, compared with `cmp`.
- The anonymity grep and `cmp` of the parity files.

## What I did not run

- The T11 docs build (`zensical build --strict`), `tools/check_docs.py` and `tools/run_tutorials.py`.
- T12 RF1 goldens and `tests/test_rf1_cli_pins.py`. That recapture was in progress in the
  working tree, and I was told to ignore it.
- The T13 mutation controls. I read `evidence/MG3/mutants.json` and did not re-execute it,
  because that requires editing the repo.
- An independent capture of parity-before at `9b069e2`. I relied on its equality with MG2's
  recorded after-capture.
- The ADD-then-RENAME variant of R-F2, the reference-mode MODIFY variant of R-F3, and the MG2
  policy-strip variant of R-F4. These are inferred and not reproduced.
- The broad `evidence`/`census` lanes.
- `tests/test_il6_skill_census.py`.

Observation outside MG3's scope: a proposal of only ADD+DELETE pairs fails in
`BlastRadiusReport` with a pydantic `too_short` `ValidationError` whether or not the option is
given (P3). This behavior predates MG3 and is worth a separate look at the error's exit mapping.
