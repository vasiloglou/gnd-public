# Phase IK3 — adversarial review (one local reviewer agent)

**One reviewer is one reviewer.** One local agent read `git diff 9dd59af 572bc52`
with the brief summarised below, edited no tracked file and kept its scratch
outputs under the session scratchpad. The author reproduced findings R1–R3
before fixing them; R4 and R5 follow from the code as cited.

Brief: hunt synth-path regressions, reader totality, binding and scoring,
class-mode cells and work, redaction and IK-R11, determinism and TOCTOU, and
branches no case can fail; reproduce every finding.

## Disposition

| # | Class | Finding | Disposition |
|---|---|---|---|
| R1 | hardening (near blocking) | a FIFO as manifest or population blocks forever | **fixed**: the manifest opens non-blocking and no-follow and must be a regular file; populations are inspected component by component and read through `safefs.read_regular_bounded`. Regressions `test_r1_*` (timeout-guarded subprocess) |
| R2 | hardening | symlinks on intermediate directories followed; a check-then-open race | **fixed**: every path component is `lstat`ed (a link anywhere is 74) and the read is no-follow and regular-only (a swapped-in link is 3). Regressions `test_r2_*` |
| R3 | hardening | a checker ref outside the bound labels raised a bare `KeyError` | **fixed**: raises `ExpectationMissingError`, exit 3, as on the synth path. Regression `test_r3_*` |
| R4 | hardening | defect rows name a population by path, which several ids may share | **fixed**: v4 defect rows add `population_id` (schema-required in v4, forbidden in v1–3). Approved answers unchanged (the corpus harness compares the approved keys). Regression `test_r4_*` |
| R5 | completeness | the work counter was arithmetic, so the ceiling check was a tautology | **fixed**: `populations` now counts checker runs actually made (the cache makes N1 one run); `label_rows` counts scored rows. Regression `test_r5_*` |
| R6 | completeness (spec claim) | spec §3's IK-R11 row says the report repeats only ids and digests, but v4 evidence excerpts carry population facts | **recorded** as implementation finding I-F2 (spec §15); no code change, since IK3-C2 parity requires the synth row shape and redaction governs the output |
| R7 | process | the approved X1 harness used a path as a population id, which the approved grammar refuses | **recorded** as C-F7 (spec §15) for owner ratification; the expected answer is unchanged |
| R8 | completeness | under a redacting model every post-load refusal's message is `[REDACTED INSTANCE DETAIL]` | **accepted**, same as the synth path's `fail()`; recorded in the boundary |
| R9 | completeness | case-insensitive file systems accept alias spellings; a constraint-free model cannot be measured (`minProperties: 1`) | **deferred**: open questions IK3-Q2, IK3-Q3 |
| R10 | completeness | unreachable defensive branches; the over-cap population and the model-changed branch untested | over-cap now tested (`test_r10_*`, exit 5, coverage not regression); the unreachable branches are argued unreachable in the record; model-changed stays untested (IK3-Q4) |

All seven regressions (`test_r1_*` ×2, `test_r2_*` ×2, `test_r3_*`, `test_r4_*`,
`test_r5_*`) fail on a copy of `572bc52`'s source and pass after the fixes;
`test_r10_*` passes on both.

## What held (reviewer's words, condensed)

- Synth JSON, text and exits byte-identical between `9dd59af` and `572bc52` on
  the committed movie corpora, a fresh redacting-model corpus and two refusals;
  the v1–3 schema behaviour identical under single-key mutations.
- Reader totality: 1,500 fuzzed manifests and 38 hand-built hostile ones gave
  named exits, no tracebacks.
- Verdict refs equal declared refs on 54 models; expected-state parity on 19
  more models with id refs rewritten; the cache never reuses a report for
  unverified bytes; no digest/load TOCTOU.
- Class cells match the agreement docstring; exits 64, 66, 74 and the
  validation order hold; output is deterministic under `PYTHONHASHSEED`.

## Reviewer report (verbatim)

```
IK3 adversarial review: `git diff 9dd59af 572bc52` (branch claude/ik3-measure)

I found no blocking defect in scoring, binding, class-mode cells or the synth path. The real problems are a hang on non-regular files, a symlink check that a race can get past, and an uncaught KeyError. One spec claim is false (IK-R11) and one approved test was edited after approval. I edited no tracked file. All scratch files are under <scratch>/review/ (called R/ below). The reproductions run from R/w, a copy of the ik3-corpus, using the R/g wrapper around the worktree's `.venv/bin/gnd`.

## Findings

**1. Hardening, close to blocking because the module docstring claims "total over arbitrary input". A FIFO as manifest or population hangs forever.**
- Where: `src/gnd/measure/labels.py:163` (`path.open("rb")`) and `:272` (`candidate.open("rb")`). Both are blocking opens with no regular-file check.
- Reproduction: `R/fs.py` runs `mkfifo` on `fifo.labels.json` and on `pops/fifo.yaml` (with a manifest pointing at it).
- Observed: `fifo-manifest TIMEOUT after 8s (hung)` and `fifo-population TIMEOUT after 8s (hung)`. `gnd check` on a FIFO also hangs, so this predates IK3, but this is new code that claims totality.
- Also: a directory given as the manifest returns 66 "could not read". Spec 66 means "missing"; 3 or 74 would fit better.
- Expected: a named refusal. `safefs.file_sha256` already opens with `O_NONBLOCK` and rejects non-regular files (the model path takes this route, so a FIFO model gets exit 3). `safefs.read_regular_bounded(root, relative, max_bytes=...)` (`artifacts.py:899`) gives a no-follow, regular-only, bounded read and fixes this and finding 2 together.

**2. Hardening: the symlink refusal is check-then-open, and symlinks in intermediate directories are followed.**
- Where: `labels.py:262-272`. The steps are `is_symlink()` on the leaf only, then `resolve()` and `relative_to`, then a plain `open()` that follows links.
- Reproduction (a): `R/fs.py` "symlinked-dir-inside" creates `popslink -> pops` and uses path `popslink/ok.yaml`. Observed: exit 0. The spec says symbolic links are refused.
- Reproduction (b): `R/race.py` swaps `pops/ok.yaml` for a symlink to a byte-identical file outside the manifest folder, between the checks and the `open()`. Observed: `exit 0 | leaf is symlink: True -> .../review/outside_ok.yaml`.
- Mitigation: the digest still has to match, so the risk is containment, not content.
- Expected: 74 or 3. Use the same safefs seam as in finding 1.

**3. Hardening: a checker ref outside the bound labels is a traceback, where the synth path gives exit 3.**
- Where: `report.py:479`, `lambda mp, ref: mp.expectations[ref]`, raises a bare KeyError. `service.py:544` catches `ExpectationMissingError` and `ConstraintRefError`, which this path never raises.
- Reproduction: `R/keyerr.py` monkeypatches `check` to add one extra verdict for `constraints[7]`. Observed: `UNCAUGHT KeyError 'constraints[7]'`. The same fault on the synth path (`R/keyerr_synth.py`) gives `synth exit 3 ... carries no expectation for constraint 'constraints[7]'`.
- It cannot be reached today. I compared checker verdict refs with `ModelIndex.iter_constraints` refs on 54 fixture models and they matched exactly.
- Expected: raise `ExpectationMissingError` (exit 3), or a `PartitionError` (exit 70).

**4. Hardening: defect rows and evidence name a population by path, not by its manifest id, and one path may appear several times.**
- Where: `report.py:703` (`"population": mp.population_path`). The cache in `labels.py:294` explicitly supports repeated paths.
- Reproduction: a manifest lists `pops/ok.yaml` twice, as ids `labeller-A` and `labeller-B`, and B mislabels uniqueness (`violated/fail`). Observed: one defect `{'kind': 'false-pass', ..., 'population': 'pops/ok.yaml'}`. Nothing says which labelling it came from.
- Expected: v4 defect rows (and evidence) carry the population `id`. The spec's IK-R11 row says the report repeats ids.

**5. Completeness: the work counter is arithmetic, not counted, so the W <= P x (1 + C) check is a tautology.**
- Where: `service.py:514-530` and `labels.py:316`. `checked += 1` runs for cache hits too.
- In expected-state mode, total = P + P·C = ceiling, always. In class mode, rules can never outnumber C. So the `> ceiling` guard can never fire.
- Reproduction: `R/work.py` runs 500 class populations on one file with a counting `check`. Observed: `check() calls 1 work {'ceiling': 2000, 'label_rows': 1500, 'populations': 500, 'total': 2000}`.
- Expected: either count real units (checks actually run, plus label rows actually scored), or record in the spec that T7 holds by construction.

**6. Completeness, a spec claim: IK-R11 is not honoured as worded in spec §3 ("the report repeats only [ids and digests]").**
- v4 `per_constraint[].evidence` carries raw values. E2 shows `"offending_facts": [{"person": 1, "team": "A"}, {"person": 1, "team": "B"}]` and a message containing `person '1' has 2 facts`.
- Redaction does work. With `redact: true` on `person_in_team` (`R/w/red.orm.yaml`), the evidence becomes `[REDACTED INSTANCE DETAIL]`, and the text output carries the REDACTION header. This matches the synth path.
- My reading: IK-R11 governs induction evidence that persists into models (`provenance.induction`, discovery counterexamples), not CLI measurement output, which the redaction policy governs. C2 parity in fact requires the evidence to equal the synth row.
- Recommendation: fix the §3 traceability row ("population ids and digests in `labels`; evidence follows the model's redaction policy"). Do not change the code, because dropping evidence would break C2.

**7. Completeness, process: the approved corpus test was edited after approval with no recorded ruling.**
- `tests/test_measure_labels.py`, X1: `"id": row["population"]` became `f"p{number}"`.
- The approved X1 could never pass. Its ids are like `conforming/model.orm.conforming.seed1.json`, and the approved id grammar `^[A-Za-z0-9][A-Za-z0-9._:#-]{0,63}$` forbids `/`.
- §14 binds the corpus to the bytes in 9dd59af. This fix needs its own C-F7 entry in §14, or a ruling.

**8. Completeness: under a redacting model, every refusal after the model loads loses its named cause.**
- Wrong `model_sha256`, an unknown id (E7) and a load failure (E11) all print `"error": "[REDACTED INSTANCE DETAIL]"`, and the envelope is stamped `schema_version: 3`.
- Reproduction: `red-e7.labels.json` and `red-e1.labels.json` (with model_sha256 set to `0`×64), run against `red.orm.yaml`.
- This is consistent with the synth path's `fail()`, but binding errors carry no instance data. T2's "named cause" therefore holds only for models with no redaction declarations.

**9. Completeness, minor:**
- **Case-insensitive file systems:** on macOS, `"path": "pops/OK.yaml"` exits 0 and the report records the alias spelling. On Linux the same manifest exits 3, so the result depends on the host.
- **Constraint-free models:** `expectations.minProperties: 1` (`labels.schema.json:71`) means a model with no constraints cannot be measured. Observed on `derivation/cases/a01-string-arm.orm.yaml`: exit 3. The synth path measures it.

**10. Branches with no failing case:**
- Unreachable: the duplicate-id branch in `RefTable.for_model` (model validation rejects duplicate ids first, which I confirmed), "rules name X twice", "labels X twice", work > ceiling, and the verdict-count `PartitionError` in the agreement module.
- Reachable but untested: a population over 10 MiB (exit 5), and "model changed while it was being read" (exit 3).

## What held
- **Synth path byte identity:**
  - JSON and text output, and exit codes, are byte-identical between the base source (`git archive 9dd59af`) and HEAD on both committed movie corpora, on a fresh `--class all` corpus of the redacting `v70-phase5/private` model, and on two refusal (exit 3) cases.
  - The schema restructuring is equivalent for versions 1-3. Both committed payloads, plus every single-key deletion, `labels`/`rules` additions, defect rows without `sidecar`/`seed`, and `schema_version` swaps to 1-5, validate identically under the old and new schemas: 0 differences (`R/schema_cmp.py`).
  - 292 targeted measure/synth tests, the RF/arch/inventory tests (2431 passed), and `tests/test_measure_labels.py` (68 passed) all pass.
- **Reader totality:** 1,500 random type-mutation fuzz runs ended 1475 × exit 3 and 25 × exit 0, with no tracebacks (`R/fuzz.py`). A further 38 hand-built cases (`R/hostile.py`) all gave named exits. They covered:
  - BOM, invalid UTF-8, lone surrogates, a 5,000-digit int, depth 64;
  - `constraints[01]`, `constraints[0]` on a model without top-level constraints, `id:` with a zero-width space, NBSP, fullwidth or NFD characters, index 999999, unknown fact types;
  - duplicate population ids, a directory population, the manifest or model given as a population (exit 5), non-ASCII paths, `reason` set to an int or null, mode/field mismatches, uppercase digests, a positional ref to an id-bearing constraint in class mode.
- **Binding and scoring:**
  - Verdict refs equal the declared refs on 54 models, so D4 coverage is exact.
  - Expected-state parity with the synth report (rows minus the two C-F2 fields, and defects minus sidecar/seed) holds on 19 more fixture models with top-level constraints, up to 156 populations, with id refs rewritten (`R/parity.py`).
  - The cache key (path, declared digest) only reuses a report for bytes already verified against that same digest. Each population is read once, then digested and loaded from the same bytes, so there is no TOCTOU between digest and load. The model is digested before and after loading.
- **Class-mode cells** match the agreement docstring and spec §6. Vacuous and unchecked stay out of the four class cells. A wrong `fires_on` cannot score against another constraint, because the resolver is one-to-one.
- **Exits:** 64 with `--promote`, 74 for a symlinked manifest, a missing model is 66 after the manifest is read, validation order follows the source, and output is deterministic under PYTHONHASHSEED.
```
