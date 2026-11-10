Retained text of the reader's report. Local paths read `<repo>`, `<scratch>`.

# Close reader 1: UG2 population-checked constraint admission

Subject: `<repo>` at dd3c35a5 (= main), branch claude/ug-close. Scratch: `<scratch>/close-r1/`
(harness `h.py`; reproductions `b.py`, `c.py`, `d.py`, `e.py`, `f.py`, `g.py`, `y.py`; mutation plugin `mut/mutplug.py`).
No repository file was edited. Baseline: `uv run pytest tests/test_evolve_population_check.py` gives 71 passed.

## Verdict

**reject.** One blocking defect: a fact-type-hosted constraint that reaches past its host gets
admitted against populated data it never checked, including the model's own sample rows. Fixing it
is small and contained (one function plus contract text). Once it is fixed and tested, the phase
would be approve-with-fixes (F2, F3).

## Findings

### R1-F1 (blocking): a fact-type-hosted constraint's subjects are only its host, so UG2-D4 (`uncovered`) and UG2-D5 (`sample-rows`) can be bypassed

- Where: `src/gnd/evolve/policy.py:346-347` (`ConstraintSubjects.of`: `if locator.host == "fact_type": return {locator.host_id}`),
  used by `src/gnd/evolve/population_check.py:221-226`. Contract:
  `src/gnd/skills/gnd-model-evolve/references/evolution-contract.md:239-244` defines role-ref and
  object-scoped subjects only for a model-hosted constraint.
- Cause: the schema and validator accept a constraint hosted on fact type A that ranges beyond A:
  - a `value` constraint with `object_type` and no `role_ref`, which the checker evaluates over every instance of the object type in the population;
  - a `value` constraint whose `role_ref` names another fact type B.

  The checker's verdict covers that wider scope. The policy, though, computes subjects, coverage
  and sample rows only for A.
- Reproduction (`<scratch>/close-r1/d.py`, through the CLI via `run_main`): the corpus `base.orm.yaml`,
  with an ADD on `fact_types[customer_places_order]` of
  `{type: value, object_type: order, range: {min: 1, max: 10}, llm-inferred/proposed/deontic}`, and
  `--policy additive --populated customer_places_order --populated order_has_amount --check-population pop.json`.
  `pop.json` holds only `customer_places_order: [{customer: 1, order: 10}]`.
  - Observed preview: exit 0, `policy_issues: []`, and `population_check.admitted` = `[{operation_index: 0, outcome: pass}]`.
    `populated` includes `order_has_amount` (declared populated, no fact in the file) and
    `order_has_channel` (sample rows `{order: 10}` and `{order: 11}`).
  - Observed apply with the same options: exit 0. The published model carries the new `max: 10` constraint.
- Why this is wrong: `<scratch>/close-r1/c.py` runs `gnd.checker.check` on the same candidate.
  - With the model's own sample rows given as facts (`order_has_channel` 10 and 11), the verdict is `warning`.
  - With `order_has_amount: [{order: 50, ...}]`, the verdict is `warning`.

  So the admitted constraint is already violated by facts GND can see (D5), and it was never
  checked over a declared-populated subject (D4). The same happens with
  `role_ref: {fact_type: order_has_channel, role: order}` hosted on `customer_places_order`.
  There the verdict is `pass` with zero `order_has_channel` facts checked (`b.py`/`c.py`), because
  the checker also scopes a hosted constraint to its host (`src/gnd/universe.py:197-198`) for vacuity.
- The same root cause in the flag-free MG2 walk, outside UG2's own cells: the same constraint
  hosted on the unpopulated `order_has_memo` is admitted with no check at all (`d.py`, second leg:
  preview 0, apply 0). The close review R1-F1 widened object-scoped subjects for model-hosted constraints only.
- Minimal fix: in `ConstraintSubjects.of`, for `host == "fact_type"`, return the host **plus**
  `_role_ref_fact_types(before/after)` and `self._playing(_object_scoped_types(before) | _object_scoped_types(after))`,
  which is the model-hosted rule. Extend the contract sentence at line 239 to "a constraint's subjects"
  (its host, if any, plus ...). Add a UG2 test for each of the two shapes, expecting
  `population: sample-rows` and `population: uncovered`.

### R1-F2 (hardening): a deeply nested YAML population takes super-linear time before it is refused (UG-R7)

- Where: `src/gnd/evolve/population_check.py:158-161` sends `.yaml` and `.yml` files to the shared
  `src/gnd/population.py:408` `_parse_document_bytes` (ruamel). The review R3 fix made YAML reachable
  through `evolve`. JSON has an early depth refusal; YAML has no depth guard before the parse.
- Reproduction (`<scratch>/close-r1/y.py`, `read_population_for_check` on `"["*n + "]"*n` named `d.yaml`):
  - n=500: 0.11 s
  - n=1000: 1.18 s
  - n=2000: 3.45 s
  - n=4000: 6.82 s
  - n=8000 (16 KB): 13.05 s

  Every size ends in band 3. A 200 KB file (n=100000), 2% of the cap, did not finish within 90 s
  (the `g.py` first run had to be stopped). The `deep.json` case with the same shape returns in about 1 ms.
  The profile shows ruamel `scanner.stale_possible_simple_keys`, which is O(depth) per token.
  T12's `bomb.yaml` tests aliases only, and T13 counts checker calls, not parser cost.
  This is inherited from the shared loader, so other YAML population readers likely share it.
  The UG2 lane exposes it and its UG-R7 time-bound claim does not cover it.
- Minimal fix: bound the YAML nesting depth (or flow-collection depth) with a byte pre-scan before
  the ruamel parse, as the JSON path does, and refuse with band 3. Add a T12 row
  `deep.yaml` (n about 10^5) with a bounded runtime or a spy on parser events.

### R1-F3 (completeness): declared branches that no test can fail

Found by mutation (`<scratch>/close-r1/mut/mutplug.py`, loaded with `-p`, over
`tests/test_evolve_population_check.py`, `test_evolve_additive_policy.py` and `test_evolve_source_document.py`, 177 tests):

| Mutant | Result | Reachable input that tells it apart |
|---|---|---|
| `_population_eligible` drops the `status == proposed` test (`policy.py:363-367`) | 177 passed | `source: user-supplied, status: confirmed, modality: deontic` passes D-12 and validation. Today it is correctly `population: not eligible` (`e.py`); the mutant would admit it, breaking UG-R2. C08a changes status and modality together, so neither test alone is pinned |
| `_population_eligible` drops the `modality == deontic` test | 177 passed | an `llm-inferred` constraint that is proposed and alethic is refused by D-12 first (`e.py`). This guard is defense in depth with no test |
| `_final_constraint_host` missing-host arm (`service.py:1039-1042`) made to raise | 177 passed | ADD a constraint on X, then DELETE fact type X. The arm (outcome `not-located`) is never run |
| `_strengthening_only` always True | 1 failed | covered (C08b) |
| no sample-row detection | 1 failed | covered (C09) |
| service apply skips the population re-check | 2 failed | covered (T9, R5) |
| coverage ignores `populated` | 3 failed | covered (C04, T4b) |

- Minimal fix: add one case per surviving mutant: a user-supplied/confirmed/deontic ADD expecting
  `not eligible`; a direct `additive_policy_issues` call with a proposed/alethic after expecting
  `not eligible`; and ADD then delete-host expecting `not-located`.

### Categories with no finding

- **Disclosure (UG-R6): no finding.**
  - Every message is a fixed category sentence. Rule ids are fixed or `jsonschema:<validator>`
    (`population.py:352`). A canary value in a type-mismatched file gave only
    `(population:type-mismatch)` (`g.py`).
  - The fuzz in `f.py` (3,000 random documents through `read_population_for_check` and
    `population_outcomes`) raised only `EvolutionPopulationError`.
  - Issue details carry model references only.
- **Apply re-check and option/file bands: no finding.**
- **UG3 replay and policy-walk changes: no finding.**

## Claims checked and found true

- **Eligibility matches the contract.** Only `constraint.populated.add` and `.modify` cells can be
  cleared (`policy.py:411`). A clear needs:
  - the after state `proposed` + `deontic`;
  - a modify whose keys are all strengthening, weakening or admitted (a `neither` key gives `not eligible`);
  - outcome `pass` from this constraint's own positional verdict. Other constraints are ignored (C06),
    and `warning`, `vacuous`, `unchecked` and `not-located` keep the refusal (C03, R9, T5b, tests).
- **Precedence is `sample-rows`, then `uncovered`, then the verdict.** Coverage covers every populated
  subject (C04, C05).
- **The reader is total over hostile bytes, with the cap at the read** (10 MiB + 1 gives 3; exactly
  10 MiB is accepted). Results from `g.py` and `f.py`:
  - band 3: non-UTF-8, BOM, 100k-deep JSON, alias YAML, `!!python/object` tag, a 5,000-digit
    integer, `1e999`, empty, `null`, `[]`;
  - band 74: directory, symlink, FIFO, a path outside the workspace;
  - band 66: a missing file.
- **`model_id` is required and must match** (C07a, C07b). A model that declares
  `reference_populations` is refused with 3.
- **Apply re-runs the check on the bytes it publishes.**
  - The CLI compares `--check-population` presence before the retry branch (`cli_service.py:698`),
    and so does the service (`service.py:1932`, review R6).
  - The fresh preview passes the reviewed digest, so changed bytes are refused with 11 before parsing
    (`population_check.py:152`, R5).
  - The service re-reads the file, re-checks, and re-runs the policy after replay equality and D-12
    (`service.py:2009-2017`). Removing that re-run fails 2 tests.
- **The preview records no path.** `admitted` comes from the difference of two runs of one pure policy walk.
- **UG3's replay changes break no UG2 guarantee.** The `declared` digest set, source-document targets
  and the model-identity `continue` in `_apply_declared_operations` and `_operation_target` record no
  placement and do not move constraint identity. Placements still resolve by identity against the final
  replay tree, with a detached object giving `not-located` (R1, T16). The source-document arm of the
  policy walk refuses before any population cell and cannot reach the clearing code.
- **Flag-free parity (T10) holds,** and the full UG2 test file passes (71).
