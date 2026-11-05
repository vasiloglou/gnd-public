# CT2 (composition) diff review

Subject: uncommitted working tree on `f20f5c3` in
`<worktree>`
(`.claude/launch.json` ignored). Read-only review; probes and mutants ran in
the scratchpad only.

## Verdict

**approve-with-fixes.** The CLI path is sound for the attacks I tried: every
record field is compared, a swapped document is refused by its digest, and
no refusal or record I produced carried a value. The gate passes (567 passed).
Two findings must be fixed before merge, and the tests have real gaps (F11: 10 of 18 mutants survive). F1 is an API soundness hole: the
verified bytes are not the bytes that get checked, which also crashes the
report builder. F2 is a composition-semantics bug: renamings skip `instances`,
so a composed population can report a false violation of a value the manifest
renamed away.

Gate: the focused selection in the spec ran with
`uv run pytest -q -p no:cacheprovider ...` and reported
`567 passed, 30 deselected in 63.17s`.

CT-R1 claim checked: `evidence/CT2/parity-after.json` and
`evidence/CT1/parity-a2e44f8.json` have the same 33 keys. Only
`U01-unpaired-anchors:check-json` and `:check-text` differ, and only in
`stderr_sha256` (exit 64, empty stdout). That stderr is the usage line,
which now lists `[--composition COMPOSITION] [--sources SOURCES]`
(reproduced with `gnd check a b --anchors x`). The claim holds.

## Findings

### F1 (blocking): `api.check(..., population_bytes=, composition=)` verifies one population and checks another; unanchored rows pass `anchored`; the report builder crashes

`src/gnd/checking_service.py:156-158` (`_composition_view`) compares the
caller's `population_bytes` with the record and the re-derivation, but
`_run_check_raw` checks the `population` it loaded from the path
(`checking_service.py:292`, then `:383`). `check_with_composed_anchors`
(`src/gnd/checker/_core.py`, the `failed_refs` comprehension) treats a composed
row with no lineage entry as not failing, so an injected row passes
`anchored`.

Reproduction (`ct2probe/probe1.py` P1 and `ct2probe/probe3.py`, using the test
fixture `build`):

```python
orig = out.read_bytes(); edited = json.loads(orig)
edited["facts"]["contract_has_party"].append({"contract": "C-X", "party": "Evil"})
api.check(m, edited_path, population_bytes=orig, composition=rec, sources=directory)
# -> exit_code 0, anchored: pass, uniqueness: pass   (a row in no source and in no document)
```

When the injected row breaks a uniqueness
(`{"party": "Acme Corp.", "city": "Nowhere"}`), `api.check` raises
`KeyError ('party_is_based_in_city', 1)` from `_composition_block`
(`checking_service.py:198`, `lineage[(fact_type, index)]`), which breaks the
totality rule. The CLI also re-reads the file after loading it, a
time-of-check/time-of-use gap of the same kind, though narrow
(`_composition_view` reads `population_coordinate` again).

Fix: under `composition`, check the population parsed from
`derived.population_bytes` (or require `population_bytes is None` and parse
the population from the one raw read used for verification). In
`check_with_composed_anchors`, count a row with no lineage entry as failing,
or assert that every composed row has lineage. Use
`lineage.get(...)` in `_composition_block`. Add a test for each.

### F2 (blocking): renamings rewrite facts but not `instances`, so the composed population can keep the old value and report a false violation

`src/gnd/composition.py:264-267` unions every source's `instances` without
renaming. Reproduction (`ct2probe/probe2.py` Q1): add
`{type: mandatory, role: party}` to `party_is_based_in_city`, give
`contract-b` `"instances": {"party": ["ACME CORP."]}` (re-signed sidecar),
and keep the fixture renaming `ACME CORP. -> Acme Corp.`. Then:

- `gnd check` of `contract-b` alone has a mandatory failure with offending
  values `['CANARY-7f3a']` only (the fixture's own unrelated gap);
- the composed instances are `{'party': ['ACME CORP.']}`;
- the composed check has a mandatory failure with offending values
  `['ACME CORP.', 'CANARY-7f3a']`. `ACME CORP.` plays the role in B; it fails
  only because composition renamed its facts and left its instance. The
  `composition.lineage` block is empty, so nothing explains this.

That breaks CT-R3 ("every change composition makes is in the manifest"): the
composed population now holds a value that is neither in any source's facts
nor renamed. The spec does not say what happens to instances, so this is a
design gap, not a deviation from the spec.

Fix: choose one rule and write it down in `docs/reference/composition.md`. One
option renames an instance of the role's object type in that source when it
equals `from`. The other refuses a renaming whose `from` is listed in that
source's instances of that object type (`composition:invalid: renaming N
also matches an instance`). Refusing is the more explicit choice and fits D2.
Add a test.

### F3 (non-blocking): `_composition_block` misattributes lineage when the same row appears in two fact types

`src/gnd/checking_service.py:184-186`: for non-anchored families the row is
looked up in every fact type (`candidates = list(positions)`). Reproduction
(`ct2probe/probe2.py` Q2): add `party_was_based_in_city(party, city)` with
the row `{"party": "Acme Corp.", "city": "Lyon"}` in A, plus the cross-source
uniqueness conflict of T13 on `party_is_based_in_city`. The lineage block
names `party_was_based_in_city#0`, which offends nothing, beside the two
genuine facts. The witness also shows that non-row witnesses (mandatory gives
values, see F2) never get lineage. That is defensible because they are not
facts, but the docs claim lineage for "every composed fact in any verdict's
offending facts" without saying this.

Fix: restrict the candidates to the verdict's own fact type. It is
recoverable from `constraint_ref` (`fact_types[<id>].constraints[i]`) or from
`fact_refs` where present. Say in the reference page that value-shaped
witnesses (mandatory, value constraints) carry no lineage. A fact type whose
roles are named `fact_type` and `roles` would also be read as the anchored
shape at `:180`. That is a nit, and it goes away once the block keys on
`fact_refs`/`constraint_ref`.

### F4 (non-blocking): `api.check(composition=<dict>)` is not total

`checking_service.py:154`: `parse_record(canonical_json_bytes(composition))`
raises `TypeError` (a set inside the dict) or `ValueError` (`nan`) out of
`api.check`, because `_run_check_raw` catches only `CompositionError`
(probe1 P2). A non-dict, non-path value (a list) is reported as "composition
record could not be read safely", which is misleading but bounded. Fix: wrap
the serialisation in `try/except (TypeError, ValueError)` and raise
`CompositionError("record is not JSON")`. Reject non-`dict`/non-path types
with a clear message, either in `_check_unresolved` or as a `TypeError`
matching `api.compose`.

### F5 (non-blocking): `gnd compose` output writes

`src/gnd/commands/checking.py:756-761` (`_cmd_compose`):

- `--out X --record X` exits 0 and prints "Composed ..."; the record
  overwrites the population (probe1 P3). Refuse equal (resolved) paths with
  64.
- When the record cannot be written, the population has already been
  replaced. Exit 74, but a composed population is left with no record, or
  with a stale record from an earlier run (probe1 P4: `--record nodir/r.json`
  leaves `--out` written). The spec says "on refusal neither is written", and
  a write failure is not a refusal, but a stale pair is the worse outcome.
  Write both to temporaries first, then replace both. Also say in the docs
  that 74 can leave the population written.
- `--out`/`--record` may point inside `DIR` (for example over a source's
  `population.json`), which silently destroys an input. Consider refusing.

### F6 (non-blocking): `gnd compose` can write a record that `gnd check` refuses by size

The record cap is 16 MiB (`composition.py:41`), and `parse_record` enforces
it on check, but `compose` never checks the size of the record it writes. At
the 100,000-fact cap each fact costs about 130 bytes plus about 60 bytes per
lineage entry, plus twice the fact-type id length and the source id length
(up to 64). With 80-character fact-type ids and 64-character source ids,
100,000 single-source facts come to about 30 MB. I argued this and did not
run it. Fix: refuse in `compose` when `len(record_bytes) > MAX_RECORD_BYTES`,
or derive the cap from `MAX_ENTRIES`.

### F7 (nit): composed `unchecked` verdicts drop the per-source `fact_refs`

`checker/_core.py`, `check_with_composed_anchors`: an opaque-value source
gives `unchecked` with `fact_refs` naming its opaque rows (see
`_anchored_verdicts`). The composed verdict copies only `scope_id` and
`reason_code`, so `fact_refs` is `[]`. A single-source check keeps them.
Map them through the lineage as the `fail` case does. I did not check whether
admission output relies on them in this path. Also, a source where opaque
values mask a failing row (CT1 gives opaque precedence inside one source)
contributes `unchecked`, not `fail`, to the composed verdict. That follows
the spec's order, but write it down.

### F8 (nit): `--admission` with `--composition` is accepted, but the composed path ignores the partial evaluator

`checking_service.py:382-385` always uses `check_with_composed_anchors`, which
calls `_check_dispatch` and not `check_partial`, even when `admission=True`
selected `check_partial` (`_run_check`). The CLI allows `--admission`, and
the probe exits 0 with an `admission` block (probe1 P5). Either exclude
`--admission` (CLI and API), or add a partial variant as
`check_with_anchors_partial` does. The spec is silent on this.

### F9 (nit): recorded deviations

- Header `source` copied from the first source: acceptable. `Population.source`
  is `Literal["agent-output", "synthetic", "fixture"]`
  (`src/gnd/population.py:131`), so `"composition"` would not load. Mixed
  sources (`synthetic` + `agent-output`) silently take the first. Either
  refuse a mix or note it on the reference page, which today says only "takes
  its header from the first source". `model`/`model_id` are not compared
  across sources. Validation against the one model probably makes this
  harmless, but I did not prove it.
- Per-fact `renamings` as the union of indexes: acceptable. Each manifest
  index names its source, so the per-entry attribution T4 describes can be
  recovered. The spec's T4 wording ("on B's entry only") should be amended
  to match.

### F10 (nit): small items

- `_row_key` is duplicated inline in `_composition_block`
  (`checking_service.py:172,186`) and again in `_anchored_verdicts`. The spec
  says dedupe keys on `values.identity_key`; the code uses its own
  `(name, type name, repr)` key. That is consistent across the three sites,
  but it is a second definition of row identity.
- On a case-insensitive filesystem (macOS default) the ids `A` and `a` are
  distinct in the manifest and read the same folder. Every row then dedupes
  with two lineage entries. That is harmless but surprising; consider
  refusing ids that differ only by case.
- `MAX_ENTRIES` is checked on the sum of source facts before dedupe, so the
  cap is stricter than the composed size. That is fine; T6 sits exactly at
  the cap.

## Checked and found sound

- Every record field is either digest-checked (`model_sha256`,
  `population_sha256`) or compared with the re-derivation (`manifest_sha256`,
  `sources`, `scope_tags`, `facts`). `schema` is checked by `parse_record`,
  and the composed bytes are compared too. A swapped document that the
  sidecar still binds is refused by `document_sha256`.
- `parse_record` validates the whole shape before use (keys, types, hex,
  ids, non-negative ints, non-empty lineage).
- Value leaks: refusal paths wrap population-validation, read and JSON errors
  in value-free messages. `AnchorError` messages
  (`src/gnd/anchors.py:102-276`) are fixed strings. An extra manifest key
  holding the canary was refused with no value. `GND_DISCLOSURE=customer`
  compose succeeds (every-mode row) and the `composition` block is identical
  across modes (T15).
- Symlinks: `read_regular_path` refuses a symlink at every path component.
- `format_version` takes the maximum; version 2 only admits `$opaque`
  values, so promoting is a superset.
- Per-source anchored evaluation uses each source's unrenamed population,
  sidecar and document. With deduplication, a composed fact fails when any
  lineage entry fails. Deontic gives `warning`. The order fail > unchecked >
  vacuous > pass matches the spec.

## Mutants

Run on a copy of `src` under the scratchpad with `PYTHONPATH=<copy>/src`,
`PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`, against
`tests/test_composition.py tests/test_anchor_sidecar_v2.py tests/test_public_api.py`.

| Mutant | Change | Result |
|---|---|---|
| M1 | drop `facts` from the re-derivation comparison | killed |
| M2 | drop `scope_tags` from the comparison | killed |
| M3 | drop `sources` from the comparison | **survived** |
| M4 | drop `manifest_sha256` from the comparison | **survived** |
| M5 | skip the `model_sha256` check | **survived** |
| M6 | accept an unused renaming | killed |
| M7 | record no renaming indexes | killed |
| M8 | no deduplication | killed |
| M9 | composed anchored: only the first lineage entry counts | **survived** |
| M10 | composed anchored: unchecked takes precedence over fail | **survived** |
| M11 | composed anchored: deontic gives fail, not warning | **survived** |
| M12 | no hex check on record digests | killed |
| M13 | `_composition_block` ignores non-anchored witnesses | killed |
| M14 | CLI allows `--anchors` with `--composition` | killed |
| M15 | skip the re-derived population-bytes comparison | **survived** |
| M16 | `covers` not unioned | **survived** |
| M17 | composed anchored: empty fact type reports pass, not vacuous | **survived** |
| M18 | composed population not re-validated | survived (probably redundant with the check-time load; low value) |

### F11 (non-blocking): test gaps the mutants expose

Ten of the eighteen mutants survive, so these guards and branches have no
test:

- M3, M4, M5, M15: no test changes only bytes that the other comparisons
  cannot see. Take a reformatted `population.json` with a re-signed sidecar,
  which gives the same composed bytes and lineage: only `sources` catches it.
  A whitespace-only manifest edit is caught only by `manifest_sha256`, and a
  whitespace-only model edit only by `model_sha256`. M15 matters because
  `derived.record["population_sha256"]` is not in the comparison tuple; the
  bytes comparison is the only link between the re-derivation and the file.
  The T9 drift cases ("document", "manifest") are each caught by an earlier
  guard (the binding failure, the scope-tag comparison), so they do not
  exercise these lines.
- M9: no test has a deduplicated fact whose second source fails while the
  first passes.
- M10, M17: no composed `unchecked` (opaque or non-lexical) case, and no
  empty anchored fact type.
- M11: no deontic `anchored` constraint (T13's deontic case is the
  uniqueness).
- M16: `covers` union is not asserted.

Add one test per survivor; each is a few lines with the existing `build`
fixture.

## Not checked

- No full suite run (focused gate only); `test_incremental_performance` was
  not run.
- Docs build and link gates for the new page (zensical) were not run.
- RF1 golden regeneration was not checked byte for byte, beyond the gate
  passing. Nor was the RF6 dynamic successor evidence content.
- F6 was argued, not reproduced. Concurrent-writer races were not tested.
- I did not trace whether `admission` consumers rely on composed
  `fact_refs` (F7/F8).
