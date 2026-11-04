Retained text of the reader's report. Local paths read `<repo>`, `<scratch>`.

# Close review, reader 3: unattended mode as a security control, and disclosure (MG-R5)

Subject: branch `claude/process-milestone-model-growth-4cac43` at `2ed15f8` (MG3 41be029, MG4 9e36e70, MG5 7961119, MG6 2ed15f8 over main `9b069e2`).
Lens: MG5 (`semantic:unattended-u1..u8` in `src/gnd/model/_validation.py`, `gnd validate --document` in `src/gnd/commands/checking.py`, `$defs.source_span` in both schema copies), measured against plan §2.5 and completion predicate 5. Also MG-R5 disclosure for every new option.

## Verdict

**approve-with-fixes.** Nothing is blocking. Every rule in the §2.5 matrix fires through `gnd validate`. I re-ran U5 and U8 on `induced` end to end myself, not only at the rule level. Models without the mode validate as before, apart from the one exception the phase already recorded (finding 6). I found no document text in any `--document` message. The gaps are fail-open edges that sit outside the matrix (findings 1 to 4) and holes in the recorded evidence (findings 5 to 8).

Probe scripts and outputs: `<scratch>/close/r3/` (`probe.py`, `probe2.py` to `probe5.py`, `par.py`, `out*/`, `par-old.json`, `par-new.json`, `old/` = `git archive 9b069e2`).

## Findings

### 1. Hardening: a near-miss spelling of the mode turns off every rule, with no signal

`_unattended_source` compares `source.mode == "unattended"` exactly, and the schema's `source` is just `{"type": "object"}`. A pipeline that writes `Unattended`, `UNATTENDED` or `"unattended "` gets no unattended checks and exit 0, even when the model contains a confirmed `explicit` constraint.

- Reproduction: `probe.py <out> mode` makes these models from the conforming fixture with `constraints[0]` set to `status: confirmed, source: explicit`. Results: `mode_Unattended_10: exit=0 issues=[] warnings=[]`, `mode_unattended_11: exit=0`, `mode_UNATTENDED_10: exit=0`.
- An enum would break parity, because the corpus has `mode: mvp-fast` (my survey found one-shot 76, guided 43, unattended 1, mvp-fast 1).
- Suggested fix: add a warning, or an error, when `str(mode).strip().casefold() == "unattended"` but `mode != "unattended"`. No corpus model has such a value, so parity holds. Alternatively, apply the rules to the case-folded, stripped value.

### 2. Hardening: under unattended mode, operations and obligations can still claim alethic certainty with only a warning

Plan §2.5 says "D-03 becomes an error in this mode". GND already applies D-03 to obligations (`semantic:op-modality-policy`), but U8 covers constraints only. Spec D6 ruled spans on operations out of scope, but D6 is about spans, not modality.

- Reproduction: `probe3.py <out>` adds a v2 operation (`source: llm-inferred`, `status: proposed`, no spans) to the conforming model, with an alethic precondition and an alethic frame. Results: `op_llm-inferred: exit=0 issues=[] warnings=['semantic:op-modality-policy']`, and the same for `common-sense`.
- `representation-format.md` "Unattended source" names operations only under U2, so a reader cannot tell that U4 to U8 exempt them.
- Suggested fix: extend U8 to every obligation from `_iter_operation_obligations` whose source is in `_UNATTENDED_ALETHIC_SOURCES` (and possibly to `frame.modality`). At minimum, state the exemption in the reference page.

### 3. Hardening: `rejected_proposals` can attribute statements and reviews to a human in a model declaring `reviewer: none`

U3 walks active constraints only.

- Reproduction: `probe4.py <out>` adds a `rejected_proposals` entry with `source: user-supplied`, `provenance: {user_quote: ..., rejected_by: owner, reviewed_in: ...}`, `modality: alethic`. Result: `rejected_user_supplied: exit=0 issues=[] warnings=[]`.
- MG-R8 names only `confirmed`, so this is outside the matrix. Still, it contradicts the mode's meaning: "nobody said it".
- Suggested fix: apply U3's source check to `rejected_proposals` under the mode, or document that archived proposals are exempt.

### 4. Hardening: `--document` can verify nothing and still exit 0, and the output does not say so

`unattended_span_issues` silently skips every span whose document was not supplied. It also reports nothing when a supplied, declared document is cited by no span.

- Reproduction: `probe2.py <out>` (`uncited_doc_supplied`) declares a second document `other.txt` and corrupts every object-type `excerpt_sha256` over `source.txt`. Running `--document other.txt` gives exit 0 with no issues.
- Reproduction: `probe.py <out> partial` declares a second document and gives an object type a span with a bogus excerpt over it. Running `--document source.txt` gives `partial_doc: exit=0`.
- This is documented ("Spans over a declared document that was not supplied are not re-hashed"), and MG-D9 (a) made the documents optional. But a host pipeline that reads exit 0 as "spans verified" is wrong, with nothing in the JSON telling it otherwise.
- Suggested fix: add per-document counts of re-hashed spans to the validate payload and text output (additive, and only when `--document` is given). Optionally add `--require-documents` to refuse when a declared document is missing or a supplied one is cited by no span. Either way, say in `--help` that unsupplied documents are skipped.

### 5. Completeness: the MG5-C4 parity table leaves out the 27 shipped example models

`evidence/MG5/capture_parity.py` globs `tests/fixtures/**`, `examples/**` (a repo-root directory with no models) and `src/gnd/skills/**`. It misses `src/gnd/examples/**`: 27 `*.orm.yaml` files at `9b069e2`, which ship with the package and are what users run. Predicate 5 says "every corpus model".

- Reproduction: `git ls-tree -r --name-only 9b069e2 | grep -E '\.orm\.(yaml|json)$' | grep ^src/gnd/examples | wc -l` gives 27. None of them appears in `parity-before.json`.
- I ran them myself with `par.py`: in-process `gnd validate --format json` under `PYTHONPATH=old/src` (the `9b069e2` tree), then under HEAD. All 27 exit 0 and the output is identical (`diff` is empty). The behavior is fine; only the record is incomplete.
- Suggested fix: add `src/gnd/**/examples/**/*.orm.*` to the capture globs, and re-record or append these rows in the close evidence.

### 6. Completeness and governance: the MG-R1 exception needs an owner ruling

The exception is that `spans` on induced provenance is now admitted in every mode, and those spans are never checked without the mode.

- Reproduction: I took `tests/fixtures/evolve-policy/base.orm.yaml` (`source: {kind: fixture}`, no mode) and added `spans: [{document_sha256: "a"*64, start: 0, end: 1, excerpt_sha256: "b"*64}]` to its induced constraint. At `9b069e2` it exits 3 (`jsonschema:additionalProperties ('spans' was unexpected)`). At HEAD it exits 0, and a span naming a document nobody declared is accepted.
- MG-R1 says a phase that cannot keep parity "lists the exception and stops for an owner ruling". The MG5 record accepts R-F2 as an agent ruling under delegated `auto` (spec R-F2; 006 "Refuted premises").
- Suggested fix: bring the exception to the owner explicitly at close and in the PR body. Alternatively, restore the refusal outside the mode with a semantic rule refusing `provenance.spans` on an induced constraint when `source.mode != unattended`. It still exits 3 but with a different message, so either way the owner rules.

### 7. Completeness: MG-R5's wording does not match what was built, and the MG5 spec misnames the validate row

- Plan MG-R5 asks for a site-table row for every new CLI option. `gnd.disclosure.SURFACES` is keyed by CLI leaf, and the new options (`--policy`, `--populated`, `--shape-report`, `--guidelines`, `--document`) have no rows. Each spec argued that the existing leaf row covers the option. That argument is reasonable, but nothing records it as a reading of MG-R5 at milestone level.
- `phase-MG5-spec.md:57` says `gnd validate --document` is "a new option on an existing leaf (`value-free`)". In `src/gnd/disclosure.py`, `gnd validate` is a `site` with `convention: declared`, not `value-free`.
- What I checked, and found no value leak in:
  - `--document` messages: digests, offsets, paths and the codec error's byte position.
  - MG2 policy detail: element references plus diff paths, never values (`policy.py:231-256`).
  - MG4 guideline: readings, names, descriptions and primitives, which is model content.
  - A `--document` refusal on a `redact: true` model, with and without `GND_DISCLOSURE=customer`, has the same shape as an ordinary exit-3 validate payload (neither carries a `redaction` block).
- Suggested fix: record in the close record that MG-R5 was applied at leaf granularity, and correct the spec row to "`site`, declared; the new messages carry no values".

### 8. Completeness: three matrix branches are tested only by calling the rule directly

The untested branches are U2 on an operation, U5 on `induced`/`imported`, and U8 on `induced`. `test_t2_branches_unreachable_through_this_fixture_at_the_rule` calls `_rule_unattended` on documents that would not load, arguing that a valid model is "out of proportion". Plan MG5-C2 asks for one refusing case per branch that asserts its id.

- I built loadable cases quickly. `probe3.py` is a valid v2 operation model that exits 0 under the mode. `probe5.py` sets the mode on `tests/fixtures/evolve-policy/base.orm.yaml`, and `gnd validate` reports `semantic:unattended-u5` at `$.constraints[0]` (induced, no spans). With alethic plus a span it reports `semantic:unattended-u8` at `$.constraints[0]`. The behavior is correct end to end.
- Suggested fix: add these end-to-end cases (the evolve-policy base already loads with an induced constraint) so a change to layer order or to the walk is caught. `imported` I did not build end to end.

## Observations, no finding

- All 87 MG5 cases, plus the schema-sync and disclosure tests, pass (147 passed).
- With every bad digest I tried, `--document` re-hash catches spans on object types, sample rows and common-sense constraints (`cs_span_bad_doc`, `sample_span_bad_doc`, `ot_span_bad_doc`: all `unattended:excerpt-mismatch`, exit 3). The walk over `model_dump()` therefore does not drop these locations.
- Every element may cite the same one-character span `[0, 1)` and still pass the rules and `--document` (`probe2.py` `vacuous_one_char`, exit 0). Spans are recorded claims, never checked for relevance. This is inherent to the design, but the skill text could say plainly that a span proves only that its excerpt exists, not that it supports the element.
- An unattended model with no object types or fact types exits 0 (`empty_unattended`). Under §2.5 this is a vacuous pass.
- A non-UTF-8 `--document` reports the codec's byte position and offending byte value (for example `0xff in position 18`), never text. T5 covers only the excerpt-mismatch path; adding the unreadable path to it would be cheap.
- A `--document` on a model without the mode exits 3 `unattended:document-undeclared`, as documented.

## What I ran

- I read plan §0, the predicates, §2.5, MG5, §10, phase records 006 (MG5) and 007, the MG5 spec and its R-F dispositions, and the diffs of `_validation.py`, `checking.py`, both schema copies, `guidelines.py`, the `policy.py` messages, `disclosure.py`, the skill and the reference section.
- Probes `probe.py` to `probe5.py`: `.venv/bin/gnd validate --format json` over temp-dir copies of the conforming fixture and the evolve-policy base, with `PYTHONDONTWRITEBYTECODE=1`.
- The old-against-new comparison of induced spans, and of the 27 examples, used `git archive 9b069e2` extracted to the scratch directory and `PYTHONPATH=<old>/src` (I confirmed `gnd.__file__` resolved to the old tree).
- `uv run pytest -q -p no:cacheprovider tests/test_unattended_mode.py tests/test_schema_sync.py tests/test_disclosure_mode.py`: 147 passed.

## What I did not run

- I did not re-run the 322-model parity capture or the MG5 mutant table.
- I did not run the full focused gate, the docs build or the tutorials.
- I did not build an `imported` constraint end to end under the mode.
- I did not check `gnd evolve preview`/`apply` publishing into an unattended model (whether evolve re-applies U2 to an ADD with `status: confirmed`).
- I did not time `--document` (MG5-Q1).
- I did not review MG3's or MG4's own logic beyond their disclosure.
