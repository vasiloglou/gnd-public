# IK4 — Constraint discovery

## 1. Status

**r1, awaiting owner review.** No code exists. Nothing in this file is approved.
Implementation starts only after the owner rules on §7 and approves these bytes.

## 2. Provenance

- **Plan:** r4, approved by the owner on 2026-10-24 (SHA-256 `8afbdcbd…cd51a`).
  This spec expands §2 "Request 4", §4 IK4, the §9 IK4 row, the IK-R rules and
  D6 (o).
- **Source request:** [issue #34](https://github.com/vasiloglou/gnd-public/issues/34),
  request 4. It asks for seven families with exact support and counterexamples,
  emitted as a `gnd evolve` proposal with `status: proposed` and an observed
  source.
- **Prior phases:**
  - IK1 ([002](../002-phase-IK1.md)), and its amendment [004](../004-amendment-IK1-Q1.md);
  - IK2 ([003](../003-phase-IK2.md)), whose admission gate IK4 must satisfy.
- **Base commit B:** named at the gate. It is the commit that lands the IK2
  import-cycle repair and IK1-Q1 on `main` (see §12).
- **Harvest:** two read-only explorer agents mapped the checker and family APIs,
  and the CLI, lane and evolve-proposal rules. The author spot-checked their key
  claims. They are research, not review.
- **Review:** no review has run over these bytes.

## 3. Obligations — inline harvest

| Obligation | Source | Discharge here |
|---|---|---|
| IK4-C1 every family has a positive and a counterexample case; every emitted ref has `gnd check` verdict `pass` and support > 0; a seeded wrong discoverer that emits a violated deontic candidate fails | plan §4 IK4; IK-O4 | §6 admission; T3, T4 |
| IK4-C2 output is a valid evolve proposal that IK2's gate admits and `evolve preview` renders | plan §4; IK-R1; IK2 | §6 output; T6 |
| IK4-C3 support numerators/denominators per family match an independent brute-force oracle on small fixtures; counterexamples are opaque ids | plan §4; IK-R2, IK-R11 | §6 support table, ids; T5 |
| IK4-C4 whole-population evaluation within the 10 MiB cap; deterministic work counter ≤ the spec ceiling on a fixed near-cap fixture; value-domain and pair bounds enforced, overridable, reported with skip counts | plan §4; IK-R6; D6 (o) | §6 bounds, work; T7, T8 |
| IK4-C5 suppression counts per catalogue row equal expected counts on a fixture exercising every row, including an alethic constraint suppressing its deontic twin; a candidate-vs-candidate redundancy rule; "min 1 alone" defined | plan §4; C1-F4 | §6 suppression; T9 |
| §9 row: "per-ref pass + support > 0; oracle support; suppression counts; work ceiling" | plan §9 | T3–T9 |
| §2 request 4: input, candidates, bounds, admission test, suppression, canonical forms, support, near-misses, output | plan §2 | §6 |
| Discovery emits `source: induced, status: proposed, modality: deontic` with a full induction block | plan §2; IK2 | §6 induction block |
| New `discover` lane, command group, entry points, `*.service` module | IK-R7; plan §3 | §6 registration; T12 |
| RF6 query ceiling not widened; ModelIndex is the shared query path | IK-R7; AGENTS.md | §6 registration; T12 |
| Bounds before results | IK-R12 | §6 bounds table; IK4-D3..D7 |
| No external solver | IK-R8 | pure Python over the checker |
| Privacy of fixtures | IK-R10 | synthetic fixtures only |
| Induction evidence never persists host data | IK-R11 | §6 ids; IK4-D8 |
| Standing rules 1–6 | IK-R9 | §4 |
| Host's 1,880 constraints carry no import obligation | IK-O18 | out of scope (§9) |

The §5 skill-surface row for IK4/IK5 calls for CLI commands, lanes and
entry-point registrations, plus `api.__all__` pins if public Python names are
added. IK4 adds no public Python name (IK4-D13). The pin sites found at harvest,
counted again at execution:
- the RF1 CLI goldens: tree, help, exit and the manifest digest;
- the parser counts (52 → 53) and the entry-point scope count (19 → 20);
- `docs/reference/cli.md`, whose rows are executed by a test.

## 4. Standing rules bound to IK4

| Rule | Application |
|---|---|
| 1 Totality | **Inputs:** the model and population go through the existing capped, validated loaders, and discovery never reads either file any other way. **Candidates:** discovery's own candidates are built as schema-valid constraints, then re-validated by `load_model_bytes` before the check. A candidate that fails validation is an internal error (exit 70) with a test, never a silent drop. |
| 2 Input cap vs algorithm | Candidate counts are bounded by the IK4-D3..D6 bounds, and every scan charges a deterministic work counter. T7 pins the counter at or under the IK4-D7 ceiling on the near-cap fixture. |
| 3 Validation order | Fixed for `gnd discover`: argument errors, missing inputs, model load, population load (stamped against the model), candidate generation, one check run, admission filter, suppression, output. A source-order test pins it (T10). |
| 4 One walk | One `gnd check` run evaluates every surviving candidate together; discovery never re-implements a family verdict. Support is computed by one per-family table function shared by the emitter and the report. The oracle in T5 is independent by design. |
| 5 One home | **CLI contract** (arguments, exits, output files): `docs/reference/discover.md`, a new page, cited by `cli.md`. **Discovery report wire:** `src/gnd/discover.schema.json`. **Induced provenance:** stays in `provenance-and-modality.md`. |
| 6 Measurement | The near-miss rule, bounds and ceiling are fixed here before any result (IK-R12). T7's fixture is authored in the corpus before code. |

## 5. Goal

`gnd discover MODEL POPULATION --out PROPOSAL --report REPORT --actor ID
--requested-at TIME` exits 0 and writes:
- a discovery report (`gnd-discover/1`) that always states the bounds used,
  every skip count, every suppression count, emitted candidates and near-misses;
- an evolve proposal (`schema_version` 3), only when at least one candidate is
  emitted.

Every emitted constraint:
- is `source: induced`, `status: proposed`, `modality: deontic`, with an
  induction block that IK2's loader and gate accept;
- has `gnd check` verdict `pass` on the same model and population, with support
  numerator > 0 per §6;
- is neither declared in the model nor entailed by a declared constraint under
  the §6 catalogue.

`gnd evolve preview` of the written proposal exits 0.

Exit codes: 3 for invalid arguments, models or populations (including a
population over 10 MiB or one that names another model); 66 for a missing
input; 74 for a refused path; 70 for an internal invariant failure. With zero
emitted candidates the command exits 0, writes the report and writes no
proposal, and the report says so.

## 6. Design

### Command and files

Home: new lane `discover`.
- `src/gnd/discover/__init__.py`;
- `src/gnd/discover/service.py`, the command service (`_cmd_discover`);
- `src/gnd/discover/candidates.py`, generation and suppression;
- `src/gnd/discover/support.py`, the support table and work counter;
- `src/gnd/discover/output.py`, the proposal and report.

About 700 lines in all. Handler: `src/gnd/commands/discover.py`, following
`commands/measure.py`.

```
gnd discover MODEL POPULATION --out PROPOSAL --report REPORT
             --actor ID --requested-at ISO-8601-with-offset
             [--families uniqueness,mandatory,value,frequency,subset,equality,exclusion]
             [--max-values N] [--max-pairs N] [--format text|json]
```

`--actor` and `--requested-at` fill the proposal's audit. They are required,
so the output is deterministic and attributable (IK4-D10). `--format` controls
stdout only, which is a summary of the report.

### Families and candidates

All candidate sequences are single-role.

| Family | Candidates | Emitted shape |
|---|---|---|
| uniqueness | per fact type, every proper non-empty subset of its roles when arity ≤ 4; above 4, subsets of size 1 and 2 only, with the rest counted as skipped (IK4-D4) | inline `{"type":"uniqueness","roles":[…]}` |
| mandatory | every role of every fact type | inline `{"type":"mandatory","role":R}` |
| value | every role whose column has 1 to `--max-values` distinct values (default 20, D6 (o)) | inline `{"type":"value","object_type":OT,"role_ref":{"fact_type":FT,"role":R},"allowed":[sorted distinct values]}` |
| frequency | every single role | inline `{"type":"frequency","scope":"internal","roles":[R],"bound":…}` with the canonical bound below |
| subset | ordered pairs of roles in **different** fact types played by the same object type, up to `--max-pairs` (default 256, IK4-D5) | top-level `subset_role_seq`/`superset_role_seq`, each one `role_ref` |
| equality | the same unordered pairs | top-level `role_seq_a`/`role_seq_b` |
| exclusion | the same unordered pairs | top-level `role_seq_a`/`role_seq_b` |

**Pair enumeration order** (deterministic): object type id, then
`(fact type, role)` in model declaration order. Pairs past the cap are counted
per object type in `skipped.pairs`.

**Canonical frequency bound** (C1-F4). Let `lo` and `hi` be the smallest and
largest group counts for the role.
- If `hi == 1`, the candidate is the uniqueness and the frequency is never
  emitted (redundancy rule).
- If `lo == 1`, emit `{"max": hi}`. A bound of `min: 1` alone is never emitted,
  because every occurring group satisfies it.
- Otherwise emit `{"min": lo, "max": hi}`.

**Fact types skipped:**
- any fact type an existing ORM+ operation references, because evolve's
  operations gate refuses additions there (exit 18) (IK4-D11);
- derived fact types.

Both are counted in `skipped.fact_types` with a reason.

### Admission

1. Build the candidate document: a deep copy of the model with every surviving
   candidate appended in generation order.
2. Load it with `load_model_bytes`, load the population with
   `load_population_bytes(…, model=candidate_model)`, and run one
   `checker.check`.
3. Keep a candidate only if its verdict is `pass` **and** its support numerator
   is > 0.
   - Vacuous, unchecked, warning and fail candidates are never emitted. Each is
     counted by verdict in `rejected`.
   - A failing candidate whose violation count meets the near-miss rule is
     reported as a near-miss.

### Support (IK4-D2)

**Subjects.** "Subjects" is what the rule quantifies over. Support is
`{numerator: subjects satisfying the rule, denominator: subjects in scope}`;
for an emitted (passing) candidate the two are equal. Each group, roster member
or occurrence is a subject:

| Family | Subject |
|---|---|
| uniqueness | each distinct key value over the role subset that occurs |
| frequency | each distinct value of the role that occurs (its group) |
| mandatory | each member of the role's object-type roster |
| value | each occurrence in the role's column |
| subset | each distinct value on the subset side |
| equality | each distinct value on either side |
| exclusion | each distinct value on either side |

**Support > 0 rules out trivial passes:**
- a uniqueness or frequency over an empty fact type;
- a mandatory over an empty roster;
- a subset with an empty subset side.

Exclusion additionally requires both sides non-empty. Equality is non-trivial
whenever either side is non-empty.

**Counts and examples:**
- The numbers are computed by `discover/support.py` from the population,
  never read from the check report, because the report has no count field.
- `examples` holds the first 256 subjects' ids in deterministic order.

**Ids** (IK-R11, IK4-D8): `ft<k>#<i>`, where `k` is the fact type's position in
the model and `i` is the fact's index in the population. A roster member is
`ot<k>#<i>`. Both fit the IK2 id grammar, carry no value, and resolve against
the named population. A subject spanning several facts uses its first fact.

### Near-misses (IK4-D3)

A failing candidate is a near-miss when its violating subjects `v` satisfy
`1 ≤ v ≤ min(32, ⌊0.05 × d⌋)`, where `d` is its subject count. That needs
`d ≥ 20`. Near-misses appear only in the report, with `v`, `d` and up to 32
counterexample ids. They are never constraints.

### Suppression

**The catalogue** is closed and modality-blind. A candidate is suppressed and
counted under its rule id when it matches any declared constraint, whatever
its source, status or modality. So a declared alethic constraint suppresses its
deontic twin.

| Rule id | Suppressed candidate | Because declared |
|---|---|---|
| `declared` | an identical constraint (same family, roles, sides, bound or values) | it |
| `equality-implies-subset` | subset A⊆B or B⊆A | equality A=B |
| `frequency-max-1-is-uniqueness` | uniqueness on R | frequency on R with `max: 1`, or a frequency with `max: 1` declared where uniqueness is the candidate |
| `unscoped-value-implies-scoped` | role-scoped value on R whose allowed set ⊇ the declared one | value on R's object type without `role_ref` |
| `reference-scheme-implies-uniqueness` | uniqueness on either role, and mandatory on the entity role, of a binary fact type whose roles are typed E and E's `reference.value_type` | E's reference scheme |
| `spanning-uniqueness` | uniqueness over all roles of a fact type | (always trivial) |
| `superkey` | uniqueness on a role set that strictly contains a declared uniqueness's role set | that uniqueness |

**Candidate against candidate.** Applied after admission, in this order:
1. An emitted equality A=B suppresses the two subsets A⊆B and B⊆A, counted as
   `redundant-subset`.
2. An emitted uniqueness on R suppresses a frequency `{max:1}` on R. Already
   excluded by the canonical bound; the counter stays as a guard.
3. Among emitted uniquenesses in one fact type, only minimal keys are emitted.
   A key that strictly contains another emitted key is counted as
   `redundant-superkey`.

### Induction block (per emitted candidate)

```json
{"inducer": {"name": "gnd-discover", "version": "<gnd version>"},
 "method": "gnd-discover",
 "manifest_sha256": "<sha256 of the population file bytes>",
 "examples": ["ft0#0", "…"],
 "support": {"numerator": d, "denominator": d},
 "counterexamples": [],
 "evidence": [{"ref": "<population file basename>", "sha256": "<same digest>"}]}
```

- No `confidence`: discovery defines none (plan §2).
- The basename is checked against the IK2 ref grammar. A population whose
  basename fails it is refused with exit 3, naming the file.
- `<gnd version>` must fit the token grammar, which installed versions do.

### Output

**The proposal** (`schema_version` 3):
- `proposal_id`: `discover-<first 16 hex of the candidate model sha256>`.
- `expected_model_sha256`: the model file's bytes.
- `candidate_model`: `application/yaml`, its text the candidate document as
  canonical JSON, which is a YAML subset, as in the shipped proposal fixtures.
- One ADD per emitted constraint, in emission order:
  - a `ConstraintLocator` with `host: fact_type` and `host_id` for inline
    families, or `host: model` for subset, equality and exclusion;
  - so that replaying the operations equals the candidate.
- `rationale`: "gnd discover: N candidate constraints observed in POPULATION".
- `audit` from the flags; `linked_projects: []`; `artifacts: []`.

**The report** (`gnd-discover/1`, `src/gnd/discover.schema.json`, closed):

```
{schema_version, tool, command, gnd_version,
 model {path, sha256}, population {path, sha256},
 bounds {families, max_values, max_pairs, max_key_arity: 4},
 skipped {fact_types[{fact_type, reason}], value_roles, pairs, key_subsets},
 rejected {vacuous, unchecked, fail, warning},
 suppressed {<rule id>: count, …},
 emitted [{ref, family, constraint, support}],
 near_misses [{family, constraint, violations, subjects, counterexamples}],
 work {<counter>: n, total: n},
 proposal: path | null}
```

Every key is always present, possibly empty or zero.

### Work counter and bounds (IK-R12)

**What counts.** One work unit is one fact row or roster member visited by
discovery's own scans. The single `gnd check` run is outside it, since the
checker has its own guards.

**Per-family counters:**
- uniqueness: Σ over candidates of the fact type's row count;
- mandatory: rows + roster;
- value and frequency: the role's rows;
- each set pair: the rows of both fact types.

**Ceiling (IK4-D7).** `W ≤ R × (14 + 4) + 2 × P × R_max`, where:
- `R` is the total fact rows;
- `14` is the most proper subsets an arity-4 fact type can have;
- `4` covers the mandatory, value, frequency and roster passes;
- `P` is the pair cap;
- `R_max` is the largest fact type's row count.

T7's near-cap fixture is authored in the corpus with its exact `R`, `R_max`
and `P`, and its numeric ceiling is stated there before code.

| Bound | Value | Override |
|---|---|---|
| distinct values for a value candidate | ≤ 20 (D6 (o)) | `--max-values N`, N ≥ 1 |
| set-comparison pairs | ≤ 256 (IK4-D5) | `--max-pairs N`, N ≥ 0 |
| uniqueness key arity enumerated in full | ≤ 4 (IK4-D4) | none |
| near-miss violations | `1 ≤ v ≤ min(32, ⌊0.05 d⌋)` (IK4-D3) | none |
| examples per block | ≤ 256 (IK2) | none |
| counterexamples per near-miss | ≤ 32 (IK2) | none |
| population | ≤ 10 MiB (existing) | none |

### Registration (IK-R7)

From the harvest:
- **`tools/gnd_layers.json`:** add `discover` to `lanes`; every
  `gnd.discover.*` module at `{"lane":"discover","layer":"lanes"}`;
  `gnd.commands.discover` at `{"layer":"entry"}`.
- **`tools/gnd_arch.py` `RF5_COMMAND_GROUPS`:** add `discover`.
- **`tools/gnd_entrypoints.json`:** scope, `service_targets`
  (`gnd.discover.service`) and `service_bindings`.
- **`src/gnd/cli.py`:** register the group, with no new `EXIT_*` constant.
- **Pins:**
  - parser counts 52 → 53 and scope 19 → 20;
  - RF1 goldens (`cli/tree.json`, new `cli-help` and `cli-exit` files for
    `gnd discover`), `goldens.sha256` and `MANIFEST_SHA256`;
  - `tests/support/rf5_sources.py`.
- **Model reads:** only through `ModelIndex` methods not named `fact_types`. A
  new query helper, if needed, goes into `model_index.py`.
- **Dynamic census:** a chained `dynamic-query-successor.json`.
- **The checker** is called through `gnd.checker.check`; no private evaluator
  surface is used.

### Docs

- `docs/reference/discover.md` (new) is the one home of the contract.
- A `docs/reference/cli.md` row, executed by the docs test.
- `docs/reference/capabilities.md`, the `gnd-model-evolve` skill (discover's
  output is a proposal) and the `gnd-solve` station map, each one line.

## 7. Decisions

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| IK4-D1 | Approval instrument | **Corpus-first** (default for serialized output, exit codes and predicates): small synthetic models and populations with narrated expected candidates, support, suppression and near-miss counts, committed red. Costs one commit before code. **Prose** relies on §6's tables. | corpus-first |
| IK4-D2 | Support subjects per family | §6 table, with numerator = denominator for emitted candidates. **Alternative:** count facts instead of distinct values, which inflates support for repeated values. | §6 table |
| IK4-D3 | Near-miss rule | `1 ≤ v ≤ min(32, ⌊0.05 d⌋)`. A looser rule floods the report; a stricter one hides useful almost-rules. | as stated |
| IK4-D4 | Uniqueness key enumeration | all proper subsets for arity ≤ 4 (≤ 14), sizes 1–2 above. Full enumeration is 2^a. | as stated |
| IK4-D5 | Set-comparison scope and pair cap | single roles in different fact types sharing an object type, pair cap 256. **Same-fact-type pairs** add ring-like rules the families do not express well. **A higher cap** costs `2 × P × R_max` work. | as stated |
| IK4-D6 | Value candidates carry raw population values in `allowed` | a value constraint must list its domain, so data enters the model. **Emit**, with the owner reviewing every candidate (the IK2-Q1 ruling's control). **Or** require an explicit `--families value`. | emit by default; the report flags it |
| IK4-D7 | Work ceiling formula | §6 formula, numeric value fixed in the corpus. | as stated |
| IK4-D8 | Example id form | `ft<k>#<i>` / `ot<k>#<i>`. **Digests** are opaque but unreadable. **Raw ids** risk data leaks. | as stated |
| IK4-D9 | Manifest and evidence | population file digest, with its basename as the ref. There is no label manifest in IK4. | as stated |
| IK4-D10 | Audit and determinism | required `--actor` and `--requested-at`. **A clock** makes output non-reproducible. | required flags |
| IK4-D11 | Fact types an existing operation references | skip and count. **Emitting** them makes every preview exit 18. | skip |
| IK4-D12 | Zero candidates | exit 0, report only, no proposal (a proposal needs ≥ 1 operation). | as stated |
| IK4-D13 | Public Python API | none. CLI only; `api.__all__` is unchanged. | none |
| IK4-D14 | Branch and base | a new branch from `main` once the IK1-Q1 and cycle-repair branch is merged. B is named then. | as stated |

## 8. Tests

New file `tests/test_discover.py`, with the corpus under
`tests/fixtures/induced_knowledge/ik4-corpus/` (IK4-D1).

| ID | Case | Expected |
|---|---|---|
| T1 | per family, a positive fixture: the candidate is emitted with the expected shape and support | exit 0; emitted equals the answer key |
| T2 | per family, a counterexample fixture: the candidate is absent and counted under `rejected.fail` | exit 0; not emitted |
| T3 | every emitted ref, in every corpus case, has check verdict `pass` and support > 0 | pass |
| T4 | a seeded wrong discoverer (monkeypatched admission keeping `warning`) emits a violated deontic candidate, and T3's assertion fails on it | the T3 assertion raises |
| T5 | an independent brute-force oracle recomputes subjects for every emitted candidate on the small fixtures | equal |
| T6 | `gnd evolve preview` of every written proposal; the IK2 gate admits it; the operations replay equals the candidate | preview exit 0 |
| T7 | near-cap fixture (population close to 10 MiB): work total ≤ the corpus ceiling; bounds stated; skip counts exact | exit 0; at or under the ceiling |
| T8 | `--max-values` and `--max-pairs` overrides change candidates and skip counts as the key says | equal |
| T9 | suppression fixture covering every catalogue row, plus the redundancy rules, including an alethic declared constraint suppressing its deontic twin | counts equal the key |
| T10 | validation-order source pin and exits: bad flag 3, missing file 66, symlinked path 74, population of another model 3, population over 10 MiB 3, zero candidates 0 with no proposal | exits as listed |
| T11 | the report validates against `discover.schema.json`; every key is present on an empty run | pass |
| T12 | lane, RF5, RF6 (static and dynamic), RF1 CLI goldens, layering and scaffold controls, and the `cli.md` docs test | pass |
| T13 | determinism: two runs with different `PYTHONHASHSEED` give byte-identical proposals and reports | equal |
| T14 | near-miss: a fixture with `d = 40`, `v = 2` is reported with 2 counterexample ids and not emitted; `v = 3` (> ⌊0.05 × 40⌋) is not a near-miss | as stated |

**Criterion ↔ tests:**

| Criterion | Tests |
|---|---|
| C1 | T1–T4 |
| C2 | T6 |
| C3 | T5, T14 |
| C4 | T7, T8 |
| C5 | T9 |

**Additional controls:** T10–T13 cover IK-R7, rule 3 and determinism.

**Verification selection:**
- **Direct:** `tests/test_discover.py`.
- **Impact closure:**
  - IK2's 90-file gate;
  - **every** `tests/test_rf*.py` (the IK2 lesson: `test_rf8_structure.py` was
    missing from that gate, see §12);
  - `test_documentation_tutorials.py`;
  - `test_public_packaged_invocation_guards.py`.
- **Selection rule:** the reduced v6.3 selection; broad lanes are not run.

## 9. Out of scope for this phase

- label manifests and measurement (IK3);
- ILP (IK5);
- importing the host's own constraints (IK-O18);
- multi-role subset, equality and exclusion sequences;
- external uniqueness and frequency;
- ring, value-comparison and other families;
- live database profiling;
- streaming beyond the 10 MiB in-memory population;
- automatic confirmation.

## 10. Size

Estimate: about 700 source lines, 900 test lines plus the corpus, and 150 doc
and registration lines. Measured at record time.

## 11. Approval instrument

Proposed in IK4-D1: corpus-first.
- **Corpus:** `tests/fixtures/induced_knowledge/ik4-corpus/`. `README.md` tells
  each fixture's story, and `expected.json` is split out as the answer key.
- **Order:** the corpus is committed red, with T7's numeric ceiling, before
  implementation, and the owner approves it by reading it.

## 12. Harvest findings

- **H1, IK2 regression on `main`.** IK2's `gnd.model._induction` imported
  `_validation` inside a function, and `tests/test_rf8_structure.py` forbids
  that runtime cycle. The test was not in IK2's 90-file gate. A registration
  hook repairs it on the IK1-Q1 branch, and the IK4 gate includes every
  `test_rf*.py`.
- **H2, no support in the check report.** The check report carries no count or
  support field, and a `pass` can be trivial (subset, frequency, exclusion).
  Support must be computed by discovery (§6).
- **H3, positional constraint refs.** Check refs are positional and appended
  candidates come last, so admission maps verdicts by appended index.
- **H4, no ADD-constraint proposal fixture.** No proposal adding a constraint
  to a fact type exists anywhere. T6 is the first, so replay order matters:
  candidates are appended in operation order.
