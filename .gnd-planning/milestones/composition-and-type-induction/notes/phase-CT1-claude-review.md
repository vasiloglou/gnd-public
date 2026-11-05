# CT1 diff review: several anchors per fact role

Reviewer: independent local agent, read-only. Subject: the uncommitted working tree at
`<worktree>`
(base `a2e44f8`). Spec: `notes/phase-CT1-spec.md` r3 `(d1)`.

## Verdict: approve-with-fixes

I found no correctness bug in the parser or checker change. v1 parity holds on every input
I tried, including one the recorded table does not cover. The fixes below close test gaps
and correct docs and schema wording. None of them blocks.

## Gate

The focused gate (14 files, including skill-prose-sync and packaged-skills) passed:
`463 passed, 16 deselected in 62.63s`.

## What I verified as correct

- **Other readers of `.anchors`.** I checked every consumer in `src/gnd`.
  - `verbalize_population._excerpts` (`:127-137`) buckets per (fact key, role) and keeps distinct texts. With several anchors this is correct, and T12 covers it.
  - `export/verification_service.py:492-511` and `checking_service.py:247-290` go through the parser and `bind_anchors`, which loops per anchor with no per-key assumption.
  - `api.py:801` goes through `validate_anchor_sidecar`, which calls the same parser.
  - `fidelity/match.py`, `recovery/*` and `model/_validation.py` mention `fact_key` or `excerpt_sha256` but do not read sidecar records.
  - I found no remaining code that assumes one record per key.
- **Checker branches.**
  - The recogniser path, the lexical path, the non-string path (`uncertain`, which skips evaluation as before) and the opaque path (decided before rows are walked) all behave as in v1.
  - `failed.append` runs at most once per (row, role) because of the `break`.
  - The result does not depend on anchor order. The lexical wanted-sets are unions, recogniser limits are maxima, and the pass rule is a conjunction.
- **v1 identity.** The parser's v1 identity `(fact_type, json.dumps(roles), role)` and the checker key `(fact_type, ((name, type, repr)...), role)` define the same equivalence on parsed JSON scalars. I checked int/float/bool, `-0.0`, `1.0` vs `1.00`, NFC vs NFD strings and key order. So a v1 sidecar still gives a list of length 1 per key, and the old "last record wins" never mattered.
- **T7 parity, reproduced independently.**
  - I ran `capture_parity.py` over `git archive 1446f90 src`, extracted to scratch. The output is byte-identical to `parity-1446f90.json`.
  - Rerunning it over the working-tree src is byte-identical to `parity-after.json`. All three recorded columns are identical (`cmp`).
- **A v1 failing case not in T7.** I took the phase1 fixture and moved the `label` and `party` anchors to span 40-60, with correct excerpts. Then I ran `gnd check --format json` and `--format text` at `1446f90` and at the working tree. Both exit 1, and both outputs are byte-identical.

## Findings

**F1 (non-blocking): the lexical occurrence union is untested.** `src/gnd/checker/_core.py:1921-1924`.
- **Mutant M4:** `lexical_wanted.setdefault(...).add(occ)` → `lexical_wanted[...] = {occ}`. Only the last record's occurrence is indexed.
- It survives `tests/test_anchor_sidecar_v2.py` and all of T6: 199 passed.
- It is a real behaviour difference. `scratchpad/repro_union.py` has one row with label `Alpha` in a document where `Alpha` appears twice, and two valid v2 anchors, one at occurrence 0 and one at occurrence 1.
  - Working tree: `pass []`.
  - M4: `fail [row]`.
- No test, v1 or v2, has two anchors with the same value text that ask for different lexical occurrences.
- **Fix:** add a T1-style case with two valid anchors on one role at occurrences 0 and 1 of the same text. It must pass, and it fails under M4.

**F2 (non-blocking): the schema accepts a digest with a trailing newline; the parser refuses it, and this is not one of P1–P9.** `src/gnd/anchor-sidecar.schema.json`, `$defs.digest`.
- The pattern is `^[0-9a-f]{64}$`. Python `jsonschema` uses `re.search`, where `$` also matches before a final `\n`.
- Probe (`scratchpad/schema_probe.py`): `population_sha256 = <64 hex> + "\n"` gives schema=True, parser=`invalid digest`.
- A related nit: a UTF-8 BOM before the JSON gives schema=True (if the bytes go through `json.loads(bytes)`, which strips the BOM) and parser=refused. T11's helper decodes to `str` first, so it cannot see this.
- **Fix:** add `"minLength": 64, "maxLength": 64` to `digest`. That is portable across regex dialects. Alternatively, list both cases as parser-only rules.

**F3 (nit): the parser-refusal table in the docs is inexact for integers and overflow.** `docs/reference/anchors.md`, the "What the parser refuses" table. Also the schema `description` and spec P6.
- `_integer` refuses literals longer than 18 **characters**, sign included.
  - `-100000000000000000` (18 digits) is refused: `oversized integer`.
  - `999999999999999999` (18 digits) is accepted.
- `1e400` is a float literal. `_integer` does not see it; it is refused as `nonfinite JSON number`. The spec's "P6 (1e400-style overflow included)" therefore names the wrong rule, and the docs mention it nowhere.
- **Fix:** write "integer literals over 18 characters, sign included", and add "numbers that overflow to infinity (`1e400`)" to the NaN/Infinity row.

**F4 (non-blocking): the T7 parity table has less coverage than it appears to.** `evidence/CT1/capture_parity.py:23-37`.
- The script ignores the case's `unredacted: true` field. So `R02-private-unredacted` runs exactly the command `R01-private-applied` runs, and their digests are identical in all three files.
- The recorded exits are only 0, 3 and 64. No v1 input reaches the failing anchored path, which is the path the `break` and append change touched.
- My extra failing-v1 run (see above) shows parity holds there too. But that is not in the evidence.
- **Fix:** pass `--unredacted` when a case sets it, add a v1 failing-anchor input (as above), and recapture all three columns.

**F5 (nit): T8 does not measure what the spec says it measures.** `tests/test_anchor_sidecar_v2.py:244-264`.
- The spec says "record-dictionary lookups = 1,000". The test counts only `span` reads (3,000) and `lexical_ranges` calls; nothing counts `records.get`.
- T8b counts `occurrence` reads (7,000) as a proxy for "occurrence-set insertions = 3,500".
- T5 asserts the limit and the fail, but not "both evaluated".
- **Fix:** count `records` lookups (for example, wrap the dict, or patch `_anchored_verdicts`'s local through a counted sidecar key), or record the deviation in the phase results.

**F6 (nit): the "one home" rule is not followed for the skill reference.** `src/gnd/skills/gnd-orm-core/references/constraint-reference.md:47`.
- Spec rule 5 says this paragraph cites `docs/reference/anchors.md` and yields to it.
- Instead it keeps all its normative prose, adds the v1/v2 identity and pass rule, and cites only the packaged schema path. It does not cite the docs page.
- This may be deliberate, since a packaged skill cannot rely on the docs site. If so, record it as a deviation. The two homes now state the same rules twice, and could drift.

**F7 (nit): "bind" means two things in the CT-R2 wording.**
- In `docs/reference/anchors.md` ("Every anchor on the role must bind"), in `constraint-reference.md:47` ("passes only when every one of its anchors binds") and in the release note, "bind" means that the selected occurrence lies inside the span. That failure is a fail/warning verdict at exit 1 or 4.
- The same page, and `bind_anchors`, use "binding" for the digest and excerpt match, whose failure is a refusal at exit 3.
- A reader could take "must bind" to mean exit 3.
- **Fix:** "every anchor's selected occurrence must lie within its span".
- The CT-R2 sentence itself ("add evidence; none of them proves it") is fine, and I saw no overclaim.

**F8 (non-blocking observation, not a regression in kind): binding cost scales with anchors × span length.** `src/gnd/anchors.py` `bind_anchors`, the excerpt hash per anchor.
- v2 lets one row carry about 3,500 anchors whose spans each cover the whole document, up to 10 MiB.
- `bind_anchors` slices, encodes and hashes each span.
- Measured: 3,500 hashes over a 2 MiB ASCII document took 2.3 s. Extrapolated to 10 MiB, that is about 12 s or more.
- v1 allowed the same total with 3,500 distinct rows, so this is not new in kind. Rule 2 bounds only the checker; the binding step's cost is unstated.
- **Fix:** optional. State the bound in the spec results.

## Mutants (in scratch copies of `src`, loaded with PYTHONPATH; worktree untouched)

| Mutant | Change | Result |
|---|---|---|
| M1 | checker keeps the last record per key (`records[key] = [record]`) | killed (T3 bad-first) |
| M2 | `break` removed after a failing anchor | killed (T3: row reported twice) |
| M3 | only the first anchor of a role is evaluated | killed (T3 bad-last) |
| M4 | the lexical wanted-set is replaced instead of unioned | **survived**: the v2 file and T6, 199 tests (F1) |
| M5 | the recogniser limit is the last occurrence, not the maximum | killed (T5) |
| M6 | v2 identity drops `occurrence` | killed (T2) |
| M7 | the version check accepts 3 | killed (T2) |
| M8 | v2 uses the v1 identity | killed (T1) |

Runner: `scratchpad/mut.py`. Probes: `scratchpad/repro_union.py` and `scratchpad/schema_probe.py`.

## What I could not check

- I did not run the full test suite, only the focused gate.
- I did not render the docs site. The `zensical.toml` nav entry I read, not built.
- I did not check the `a2e44f8` column independently. I re-derived only the `1446f90` and after columns, and `cmp` shows all three identical.
- I did not run T10 as a test; no dedicated test exists in the diff. A manual grep of the added files for the downstream app names found none.
