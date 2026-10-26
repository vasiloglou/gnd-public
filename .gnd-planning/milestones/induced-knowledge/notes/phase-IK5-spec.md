# IK5 — ILP bridge

## 1. Status

**r1, awaiting owner review.** No code exists. Nothing in this file is approved.
Implementation starts only after the owner rules on §7 and approves these bytes.

## 2. Provenance

- **Plan:** r4, approved 2026-10-24 (SHA-256 `8afbdcbd…cd51a`, re-checked against
  the bytes at B). This spec expands:
  - §2 "Request 5";
  - §4 IK5 (C1–C4);
  - the §9 IK5 row;
  - D4 (o), the tool-neutral bridge with Popper first;
  - D8 (o), `guarded` output only.
- **Source request:** [issue #34](https://github.com/vasiloglou/gnd-public/issues/34),
  request 5.
- **Dependencies (plan §3):** IK3 → IK5 and IK2 → IK5. Both are merged: IK2 (the
  induction block and the D-12 gate) and IK3 (the label manifest,
  `gnd.measure.labels`). IK6 needs IK5's commands for its walk.
- **Base commit B:** `1bcb899` (`main`, after PR #40).
- **Harvest:** done by the author, without agents (fan-out needs the owner's
  go-ahead). Sources: plan r4 in full; the IK2, IK3 and IK4 specs and records;
  and the code (`src/gnd/commands/{export,checking}.py`, `src/gnd/export/`,
  `src/gnd/discover/output.py`, `src/gnd/measure/labels.py`,
  `src/gnd/process.py`, `tools/gnd_layers.json`, `tools/gnd_entrypoints.json`,
  `tools/gnd_arch.py`, `orm-meta.schema.json` `$defs.guarded` and
  `$defs.induction`, and `representation-format.md` §"Guarded constraints").
- **Review:** none has run over these bytes.

## 3. Obligations — inline harvest

| Obligation | Source | Discharge here |
|---|---|---|
| IK5-C1: the neutral export form and its Popper rendering each equal a committed golden digest across two runs with different `PYTHONHASHSEED`; modes derived from fact-type roles; examples from IK3 manifests; import contract stated against the neutral form | plan §4 | §6 export; T1, T2 |
| IK5-C2: import emits only `guarded` constraints by body rewriting; NAF, aggregates, disjunction and non-ground absence each refused by name, one test each; a fixture clause maps to a schema-valid guarded constraint | plan §4; D8 (o) | §6 fragment and rewriting; T4, T5 |
| IK5-C3: re-evaluation compares **sets** of covered example ids, vacuous = not covered; equal counts with different sets refuse; a difference in one vacuous example refuses; a matching fixture is admitted as a proposal | plan §4 | §6 re-evaluation; T6 |
| IK5-C4: recorded learner fixtures bind the exported-bytes digest and the learner name and version; a mismatched binding refuses; a live run is evidence only, never a required lane | plan §4; IK-R8 | §6 run record; T7; IK5-D12, IK5-D13 |
| §9 row: "guarded-only; set-equality refusal; bound fixtures; golden export digest". Consumers: new ILP tests, export tests | plan §9 | T1–T7; §8 selection |
| Completion predicate 5: one export format, Popper renders it, one golden digest across two hash seeds; import only in the fragment, `guarded` only; a named non-zero exit on any set difference | plan "Completion" | T1, T2, T4–T6 |
| §2: `gnd export ilp --target <adapter> MODEL --labels MANIFEST` | plan §2 | §6 commands |
| §2: `gnd import ilp-rules MODEL CLAUSES --labels MANIFEST --reported-coverage FILE` | plan §2 | §6 commands; IK5-D5 adds `--target` |
| §2: the head `wrong(X)` is a host label and never becomes a fact type | plan §2 | §6 rewriting, step 1 |
| §2: the fragment table states, per accepted construct, how GND's semantics differ from the learner's (closed-world rosters, boolean typing, vacuity) | plan §2 | §6 fragment table |
| §2: coverage agreement is necessary, not sufficient | plan §2 | §6 fragment table; record boundary |
| §2: output is an evolve proposal under IK2 provenance | plan §2; D8 | §6 output; T8 |
| §3 home: export in the `export` lane (`src/gnd/export/ilp*.py`); import home and lane fixed here; bounded process through `gnd.process.run_bounded_process` | plan §3 | §6 registration; IK5-D4, IK5-D12 |
| §5: new CLI commands, lane and entry-point registration; `api.__all__` and signature pins only if public Python names are added | plan §5 | §6 registration (no public Python names) |
| §5: packaged skills that teach provenance or evolve are inspected; edits only where behaviour changed | plan §5 | §6 skills: pin sites `gnd-model-evolve/SKILL.md:280` and `gnd-solve/SKILL.md:141` (the `gnd discover` lines), measured at B |
| §6 risk: "learned rule becomes an ungated hard rule" | plan §6 | D8: `guarded`, `proposed`/`deontic`, through D-12; T8 |
| §6 risk: "ILP translation changes meaning" | plan §6 | fragment table; set equality; T4–T6 |
| §6 risk: "thresholds chosen after measurement" | plan §6; IK-R12 | §6 bounds (IK5-D14), fixed here |
| §7: no learner in CI or as a required lane; no bundled solvers; no automatic admission; no induced `derivation_rule` | plan §7 | §9; IK5-D12 |
| Learner numbers are claims to check | IK-R2 | §6 re-evaluation: GND recomputes coverage and support; the learner's sets are only compared |
| Induction evidence carries opaque ids and digests only | IK-R11 | §6 provenance: example ids are manifest population ids; evidence is digests under fixed logical refs |
| ILP tools optional, explicit, bounded; absent tools give a named refusal | IK-R8 | IK5-D12 |
| Free text is untrusted; learned clause text never executes | IK-R5 | §6: clause text is parsed by a closed grammar into data and is never evaluated; constants pass through `guarded`'s typed literals |
| Caps before reading; total loaders | IK-R6; standing rule 1 | §4 rule 1; T3 |
| **IK2 residual:** "Whether the induction block can represent real learner output without loss is untested. A shortfall found in IK5 needs an owner amendment" | IK2 spec §15; 003 record boundary | §6 provenance maps every field; IK5-D13 decides whether a real Popper run tests the fit |
| **IK2-D11:** `ilp-popper` is a documented `method` spelling | IK2 spec §7 | §6 provenance: `method: ilp-popper` |
| **IK3 inheritance:** class-mode manifests (populations, classes, `rules` with ≥ 1 entry); the reader `gnd.measure.labels`; labels are the host's claim | 006 record | §6 export input; §12 sweep row on `rules` |
| **IK3-Q2** (case-insensitive file systems accept alias path spellings) applies to IK5 too, because IK5 reuses the population reader | 006 record | not discharged; inherited into the boundary |
| **IK4-Q2:** evolve cannot preview reference-bearing models (before IK6) | 005 record | T8 uses a model without references; inherited into the boundary |
| **IK4-Q5:** the pre-existing red hashability test | 005 record | excluded from the gate, as in IK3 |
| Standing rules 1–6 | IK-R9 | §4 |
| Privacy of fixtures | IK-R10 | synthetic only; no downstream name |

## 4. Standing rules bound to IK5

| Rule | Application |
|---|---|
| 1 Totality | **Four new loaders**, each total over arbitrary input, with hostile cases in T3: the clauses reader (`gnd-ilp-clauses/1` JSON), the Popper program parser (text), the run-record reader (`gnd-ilp-run/1` JSON), and the reused IK3 manifest reader. The JSON readers read at most cap + 1 bytes, go through the RF7 JSON policy (depth, duplicate keys, non-finite numbers, long integers), then the schema, before any field is read. The Popper parser is a closed tokenizer over at most cap bytes; anything outside its grammar is exit 3 with the line and column. |
| 2 Input cap vs algorithm | **Export:** work = populations loaded + facts written, with a ceiling of `P + F_max` (IK5-D14). **Import:** one checker run per population over the model plus every learned constraint, and one verdict read per (population, clause), so `W ≤ P × (1 + K)` for K clauses. The parser is linear in its input. T9 pins both counters on near-cap inputs. |
| 3 Validation order | **Export:** arguments; the manifest read and schema; the mode check; model load; binding; per population (path, digest, load); representability; render; write. **Import:** arguments; the clauses read; the run-record read; the manifest read and binding; the export recomputed and its digest compared; the learner binding; per clause, the fragment checks in §6 order; candidate-model validation; re-evaluation; set comparison; proposal write. Source-order pin, T10. |
| 4 One walk | **One proposal builder:** IK4's (`gnd.discover.output`), generalized by keyword for origin and id prefix, not copied. **One replay:** evolve's `_apply_declared_operations`. **One manifest reader and population reader:** IK3's. **One checker run** per population serves every clause. **One fragment checker** serves both import targets; the Popper adapter only parses into the neutral clause form. |
| 5 One home | **Fragment table and rewriting order:** `docs/reference/ilp-bridge.md`; the module docstrings cite it. **Wire formats:** four closed schemas (§6). **The D-03 table** stays in `provenance-and-modality.md`; IK5 writes only `proposed`/`deontic`. |
| 6 Measurement | Golden export bytes are decided by committed files (T1). The "equal counts, different sets" and "vacuous-only difference" refusals are decided by fixtures (T6), not argued. Facts about Popper's own behaviour are not decided by this spec (IK5-D13). |

## 5. Goal

- **`gnd export ilp MODEL --labels MANIFEST --target popper --out DIR`** exits 0
  and writes a new directory. It holds the neutral form, the Popper rendering
  and an index whose SHA-256 is the export digest E, printed on stdout. Two runs
  under different `PYTHONHASHSEED` values write byte-identical directories,
  equal to the committed goldens.
- **`gnd import ilp-rules MODEL CLAUSES --labels MANIFEST --reported-coverage
  FILE --target popper|neutral --out PROPOSAL`** exits 0 and writes an evolve
  proposal only when all of these hold:
  - every clause is in the fragment;
  - the run record binds E, the clauses' digest and the learner;
  - for every clause, the set of example ids GND's re-evaluation covers equals
    the learner-reported set.

  The proposal adds one `guarded` constraint per clause, each
  `source: induced`, `status: proposed`, `modality: deontic`, with a computed
  `provenance.induction` block. `gnd evolve preview` of that proposal exits 0.
- **Every refusal** is exit 3 with a named reason (IK5-D8), and nothing is
  written. No `derivation_rule` is ever emitted.

## 6. Design

### Commands

```
gnd export ilp MODEL --labels MANIFEST --target popper --out DIR
gnd import ilp-rules MODEL CLAUSES --labels MANIFEST --reported-coverage FILE
                     --target {popper,neutral} --out PROPOSAL [--actor ID] [--format {text,json}]
```

- `--target` names the adapter. Popper is the only learner adapter in this
  phase (D4 (o)). For import, `neutral` reads the neutral clause form directly
  (IK5-D5).
- `--out` must not exist (exit 11), and a symbolic link is refused (exit 74).
- The import report goes to stdout: `gnd-ilp-import/1` with `--format json`,
  otherwise text.

### Examples and the target (IK5-D2, IK5-D3)

- **Examples:** one example is one population of a **class-mode** IK3
  manifest, named by its manifest `id`. An expected-state manifest is exit 3,
  named.
- **Target:** the learned predicate is `wrong/1`. Populations of class
  `negative` are its positive examples; `positive` populations are its negative
  examples. The manifest's `rules` are validated and bound, as IK3 does, and
  are otherwise unused.

### Neutral form (`gnd-ilp/1`, `src/gnd/ilp.schema.json`, closed)

```json
{"schema_version": "gnd-ilp/1",
 "model_sha256": "<hex>", "manifest_sha256": "<hex>",
 "target": {"predicate": "wrong", "arity": 1, "covers_class": "negative"},
 "types": [{"name": "t_order", "object_type": "order", "primitive": "integer" | "string" | "boolean" | null}],
 "predicates": [{"name": "f_order_amount", "fact_type": "order_amount",
                 "roles": ["order", "amount"], "types": ["ex", "t_order", "t_amount"]}],
 "comparisons": [{"name": "gt_t_amount", "operator": ">", "type": "t_amount"}],
 "examples": [{"id": "n1", "class": "negative", "label": "pos"}],
 "facts": [{"example": "n1", "predicate": "f_order_amount", "values": [7, 120]}],
 "skipped": {"derived_fact_types": ["..."]}}
```

- **Predicates (modes from fact-type roles):** one per asserted fact type,
  named `f_<fact type id>`. Its first argument is the example (type `ex`), then
  one argument per role in declared order. A fact type id outside
  `^[a-z][a-z0-9_]{0,61}$` is exit 3, named. Derived and semiderived fact types
  are not exported. They are listed in `skipped`, and a clause naming them is
  refused as `unknown-predicate`.
- **Types:** one per object type a role uses, named `t_<object type id>`, with
  its primitive when it is a value type.
- **Comparisons:** for every `integer`-typed type, `gt_`, `lt_`, `ge_` and `le_`
  predicates. Comparison on other primitives is outside the fragment
  (`comparison-type`).
- **Facts:** the population's asserted facts, with each value spelled in the
  checker's typed identity (`canonical_scalar`).
- **Refused at export** (exit 3, named):
  - a population with an opaque or unrepresentable cell;
  - a model whose redaction policy covers any exported role (IK5-D11);
  - an export over the facts bound (IK5-D14).
- **Order:** examples in manifest order; facts by (example position, predicate
  name, canonical JSON of the values); types, predicates and comparisons by
  name. Written as canonical JSON (sorted keys, two-space indent, trailing
  newline).

### Popper rendering (adapter `popper`)

- `popper/bk.pl`: one fact per line, `f_order_amount('n1',7,120).`
  - Example ids and string values are single-quoted atoms, with `\` and `'`
    escaped.
  - Integers are written bare; booleans are `true` and `false`.
  - The comparison definitions follow, for example `gt_t_amount(A,B) :- A > B.`
- `popper/exs.pl`: `pos(wrong('n1')).` for each negative-class population, and
  `neg(wrong('p1')).` for each positive one, in manifest order.
- `popper/bias.pl`:
  - `head_pred(wrong,1).` and `type(wrong,(ex,)).`;
  - one `body_pred` and `type` per predicate and comparison;
  - `magic_value_type(t_…).` for each integer type;
  - fixed `max_vars(6).`, `max_body(5).` and `max_clauses(4).`
- `export.json` (`gnd-ilp-export/1`, same schema file, closed):
  `{schema_version, target, adapter_version, files: [{path, sha256, bytes}]}`
  sorted by path, covering `neutral.json` and the three `.pl` files.
  **E = SHA-256 of `export.json`'s bytes**, so a caller reproduces it with
  `sha256sum DIR/export.json`.
- **Not established:** whether a real Popper accepts and learns from this
  rendering. This is IK5-D13.

### Clause form (`gnd-ilp-clauses/1`, `src/gnd/ilp-clauses.schema.json`, closed)

```json
{"schema_version": "gnd-ilp-clauses/1",
 "clauses": [{"head": {"predicate": "wrong", "args": [{"var": "X"}]},
              "body": [{"atom": {"predicate": "f_order_amount", "args": [{"var": "X"}, {"var": "O"}, {"var": "A"}]}},
                       {"compare": {"operator": ">", "left": {"var": "A"}, "right": {"const": 100}}},
                       {"not": <literal>},
                       {"or": [[<literal>…], [<literal>…]]},
                       {"aggregate": {"name": "<token>", "args": [<term>…]}}]}]}
```

- A term is `{"var": "<Prolog variable>"}` or `{"const": <string | integer | boolean>}`.
- `not`, `or` and `aggregate` are in the **form**, so that they reach the
  fragment checker and are refused there **by name**, not by the schema.
- **The Popper adapter's parser** reads Popper's printed program into this form.
  - **Clauses:** `wrong(A):- l1, …, ln.` One clause per `.`; `%` comments
    are skipped.
  - **Literals:**
    - `p(t, …)` gives an atom, or a comparison when `p` is an exported
      comparison predicate;
    - `T1 op T2`, with `op` in `> < >= =< =:= =\= = \=`, gives a comparison.
      Prolog's `=<` is `<=`, and `\=` and `=\=` are `!=`;
    - `\+ L` and `not(L)` give `not`;
    - `(B1 ; B2)` gives `or`;
    - `findall`, `bagof`, `setof`, `aggregate_all`, `count`, `sum`, `max`
      and `min` give `aggregate`.
  - **Terms:** a capitalized name or `_` is a variable. A quoted or lowercase
    atom is a string constant; an integer is an integer constant.
  - Anything else is exit 3, `unparsable`, with the line and column.

### Fragment and rewriting (normative home: `docs/reference/ilp-bridge.md`)

Per clause, in this order. The first failing check refuses with the construct
name shown, and the clause index.

| # | Check | Refusal name |
|---|---|---|
| 1 | head is `wrong` with exactly one variable argument X | `head-shape` |
| 2 | every body literal is `atom` or `compare` | `negation-as-failure` (`not`), `disjunction` (`or`), `aggregate` |
| 3 | every atom names an exported predicate with arity 1 + roles; `wrong` in the body | `unknown-predicate`, `arity`, `recursion` |
| 4 | every atom's first argument is X, and X occurs nowhere else | `example-variable` |
| 5 | at most one `compare`, with at least one variable operand, over an `integer` type | `multiple-comparisons`, `comparison-type` |
| 6 | **designation:** the `compare`, if present; otherwise the last atom, in clause order, whose variables all occur in the other atoms | `non-ground-absence` (no atom qualifies) |
| 7 | the remaining atoms (the antecedent) are non-empty and connected by shared variables | `empty-antecedent`, `disconnected-body` |
| 8 | every variable of the designated literal occurs in the antecedent | `non-ground-absence` (atom), `unbound-comparison` (compare) |
| 9 | no string constant begins with `$`, because a `guarded` bind reads such a string as a variable | `constant-spelling` |
| 10 | the model plus the constraint validates (`gnd validate` semantics) | `invalid-guarded`, with the validator's issue codes |

**Rewriting (body rewriting, plan §2):**
- X is dropped from every atom.
- Each remaining atom becomes `{fact_type, bind: {role: term}}`.
  - A variable `V` becomes `$v_<lowercased V>`; each `_` becomes a fresh
    `$anon<k>`.
  - A constant becomes a scalar literal.
- **A designated comparison** `L op R` becomes
  `consequent: {comparison: {operator: negate(op), left, right}}`, where
  `negate` maps `>`↔`<=`, `<`↔`>=` and `=`↔`!=`.
- **A designated atom** becomes `consequent: {absence: {fact_type, bind}}`.
- The constraint is
  `{type: guarded, antecedent, consequent, source: induced, status: proposed, modality: deontic, rationale, provenance: {induction}}`,
  top-level, with no `id`.

**Semantic differences (the fragment table's second half, plan §2):**

| Construct | Learner (Prolog / ASP) | GND `guarded` | Consequence |
|---|---|---|---|
| clause body true for some binding | covers the example | a violating binding → `warning` (deontic) | covered ⇔ `warning` |
| an empty antecedent fact type | the body is false: not covered | `vacuous` | not covered, reported separately (C3) |
| a populated antecedent with no join | not covered | `pass`, `bindings=0` | not covered |
| a disconnected body | a cross product | `unchecked` `join-disconnected` | refused at check 7 |
| an absent fact | closed world in `bk.pl` | closed world over the population, whatever `covers` says | agree on exported facts; GND also sees facts the export skipped (derived), which the fragment refuses (check 3) |
| a comparison | Prolog arithmetic on integers | typed comparison; an unordered pair → `unchecked` | integers only (check 5); `unchecked` → not covered, reported separately (IK5-D7) |
| a constant | an atom or integer | a typed literal, matched by scalar identity | `'7'` (atom) ≠ `7` (integer), on both sides |
| unary / boolean roles | an ordinary argument | a typed value | rendered `true`/`false`; no truthiness |

Agreement on these sets is **necessary, not sufficient**: two rules that cover
the same examples can disagree on unseen populations.

### Re-evaluation and comparison (C3)

1. Read and bind the manifest against MODEL (IK3's `bind_manifest`).
2. Build the candidate model: MODEL plus the K rewritten constraints, through
   evolve's replay.
3. Per population, in manifest order: read it with IK3's reader (path, digest,
   no links), run the checker once on the candidate model, and read the verdict
   of each new constraint.
   - `warning` → covered;
   - `pass` → not covered;
   - `vacuous` → not covered, listed in `vacuous`;
   - `unchecked` → not covered, listed in `unchecked` (IK5-D7);
   - `fail` → exit 70, because the constraint is deontic.
4. **Per clause k:** G_k is the covered set and R_k the reported set. An id in
   R_k that is not in the manifest is exit 3, `unknown-example`. If G_k ≠ R_k,
   the import is refused with `coverage-mismatch`. The report names both
   differences (ids only, the first 32 of each) and the vacuous and unchecked
   ids.
5. **All-or-nothing (IK5-D9):** any refused clause or mismatch refuses the
   whole import, and nothing is written.

### Run record (`gnd-ilp-run/1`, `src/gnd/ilp-run.schema.json`, closed) (C4)

```json
{"schema_version": "gnd-ilp-run/1",
 "learner": {"name": "popper", "version": "<induction token>"},
 "export_sha256": "<E>", "clauses_sha256": "<sha256 of CLAUSES bytes>",
 "coverage": [{"clause": 0, "covered": ["n1", "n2"]}]}
```

The binding checks, each exit 3, named:
- `export_sha256` must equal E, recomputed in memory from MODEL, MANIFEST and
  `--target` (`export-mismatch`);
- `clauses_sha256` must equal the CLAUSES digest (`clauses-mismatch`);
- with `--target popper`, `learner.name` must be `popper` (`learner-mismatch`);
- `coverage` must list every clause exactly once (`coverage-shape`).

### Provenance written (IK2 block; IK2 residual)

Per constraint, computed by GND and never copied from the learner (IK-R2).
Let C_k = G_k, with C⁻ its negative-class ids and C⁺ its positive-class ids.

| Field | Value |
|---|---|
| `inducer` | `{name, version}` from the bound run record |
| `method` | `ilp-<target>`, so `ilp-popper` (the IK2-D11 spelling) or `ilp-neutral` |
| `manifest_sha256` | the manifest's digest |
| `examples` | C⁻, the first 256 in manifest order |
| `counterexamples` | C⁺, the first 32 in manifest order |
| `support` | `{numerator: |C⁻|, denominator: |C_k|}` (IK5-D10); a clause covering nothing is refused, `covers-nothing` |
| `evidence` | `[{ref: "ilp/export.json", sha256: E}, {ref: "ilp/clauses", sha256: <CLAUSES digest>}, {ref: "ilp/run", sha256: <run-record digest>}]`, logical refs in the IK2 ref grammar |
| `confidence` | absent (IK2: present only for methods that define it) |
| `reviewed_in` | absent (R-I2) |

All four IK2 inequalities hold by construction:
- `examples ≤ numerator`;
- `counterexamples ≤ denominator − numerator`;
- `examples` and `counterexamples` are disjoint;
- `numerator ≤ denominator`.

The rationale is `learned by <name> <version> from manifest <sha8>, clause <k>`.

### Output

- **Proposal:** an evolve schema-3 proposal of K ADD operations, written to
  `--out`. It is built by IK4's proposal builder, generalized with
  `origin="gnd import ilp-rules"` and the id prefix `ilp-`, through evolve's
  replay.
- **Report `gnd-ilp-import/1`** (`src/gnd/ilp-import.schema.json`, closed), on
  stdout:
  - the inputs and their digests, the learner and the target;
  - per clause: the refs, G and R sizes, the vacuous and unchecked ids, and
    the support;
  - the work counter and its ceiling.

### Exits

| Exit | Export | Import |
|---|---|---|
| 0 | written | proposal written |
| 3 | invalid manifest, mode, binding or digest; an unrepresentable cell; a redacted role; too large | a fragment refusal; a binding mismatch; `coverage-mismatch`; `covers-nothing`; invalid inputs |
| 5 | a population fails to load | the same |
| 11 | `--out` exists | the same |
| 64 | usage | usage |
| 66 | model, manifest or input missing | the same |
| 70 | internal invariant | internal invariant (including `fail` on a deontic constraint) |
| 74 | a refused path or link | the same |

### Bounds (IK5-D14, fixed before results)

| Item | Bound |
|---|---|
| manifest | IK3's bounds, unchanged |
| exported facts F, all populations together | ≤ 1,000,000 |
| each written file | ≤ 64 MiB |
| CLAUSES bytes | ≤ 1 MiB |
| clauses K | 1 … 32 |
| body literals per clause | 1 … 16, nesting depth inside `not`/`or` ≤ 4 |
| run-record bytes | ≤ 32 MiB |
| ids per clause in the run record | ≤ the manifest's population count |

### Registration (IK5-D4)

- **Homes:** new modules in the existing `export` lane:
  - `gnd.export.ilp` (the neutral form);
  - `gnd.export.ilp_popper` (render and parse);
  - `gnd.export.ilp_rewrite` (fragment and rewriting);
  - `gnd.export.ilp_service` (both commands; the RF5 service target).
- **CLI:** `gnd export` gains the `ilp` target. `gnd import` (in
  `gnd.commands.checking`) gains `ilp-rules`, which routes to
  `gnd.export.ilp_service`. Both bindings go in `gnd_entrypoints.json`.
- **Cross-lane edges:** export → measure (labels), export → discover (the
  proposal builder) and export → evolve (replay). They are measured, as IK4's
  discover → evolve is, and none adds an allowance.
- **RF1:** CLI goldens change for the `export` and `import` subtrees only. RF6
  gets a chained census delta, and the schema inventories gain four schemas.
- **Docs:** `docs/reference/ilp-bridge.md`, rows in `cli.md` and
  `capabilities.md`, and a nav entry.
- **Skills:** one line beside each `gnd discover` line at the two pin sites.
- **No public Python names** are added, so `api.__all__` is unchanged.

## 7. Decisions

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| IK5-D1 | Approval instrument | **Corpus-first** (the default for formats, exits and predicates). Hand-written expected export files whose digests become the goldens; clause, run-record and refusal cases with hand-written exits and constraints; committed red. **Prose** relies on this spec's tables. | corpus-first |
| IK5-D2 | What is one example? | **One population** (a manifest entry): matches IK3 manifests, which label populations, not entities. **One entity:** needs per-entity labels that no manifest carries, so it needs a manifest amendment. | population |
| IK5-D3 | Which class is `wrong`? | **Fixed: `negative`.** One spelling everywhere. **A `--covers-class` flag:** more general, with two spellings of every count. | fixed `negative` |
| IK5-D4 | Import home | **(a) The `export` lane** for both directions: one bridge home, three measured cross-lane edges. **(b) The `discover` lane** for import: it groups induction, but splits the bridge across lanes. **(c) A new `ilp` lane:** a closed-lanes edit, an RF5 group and entry points. | (a) |
| IK5-D5 | Import input form | **`--target popper|neutral`:** Popper's printed program is parsed by its adapter, and the neutral JSON is read directly. The contract is stated over the neutral form (C1). **Neutral only:** hosts convert Popper output themselves, and the adapter is export-only. | both |
| IK5-D6 | Coverage granularity | **Per clause:** each constraint carries its own evidence, a stronger check. **Program union:** the shape of Popper's own scoring, but a weaker check with one shared block. | per clause |
| IK5-D7 | `unchecked` verdict on a learned constraint | **Not covered, listed separately** (as with vacuous): a learner-covered example then mismatches and refuses. **Refuse at once,** whatever the learner said. Both refuse on a disagreement; they differ only when the learner also did not cover the example. | not covered, listed |
| IK5-D8 | Exit for `coverage-mismatch` | **3, with a named reason:** consistent with every other refusal. **A new exit 19:** scripts can tell a disagreement from malformed input, at the cost of an exit constant, redaction exit lists and docs. | 3 |
| IK5-D9 | Partial admission | **All-or-nothing:** one refusal refuses the import. **Per clause:** admit the agreeing clauses, which mixes refusal with success under exit 0. | all-or-nothing |
| IK5-D10 | Support | **numerator = covered negatives, denominator = covered** (precision-shaped): satisfies all four IK2 inequalities. **Recall-shaped** (denominator = all negatives): violates IK2's `counterexamples ≤ denominator − numerator`, so it needs an IK2 schema amendment. | precision-shaped |
| IK5-D11 | Redacted roles and opaque cells | **Refuse export (3):** the export writes raw values, and redaction is the model's word. **Export digests of redacted values:** joins survive but comparisons and constants on them do not, and digests reach a learner. | refuse |
| IK5-D12 | Who runs the learner? | **No GND command runs it.** An optional evidence script, `evidence/IK5/run_popper.py`, uses `run_bounded_process` and refuses by name when Popper is absent; no test requires it. **A `--run` flag on export:** a runtime path to an external solver, against plan §7's spirit. | no command; optional script |
| IK5-D13 | Real Popper evidence | Checked at B: there is no `popper` module and no `swipl` or `clingo` on this machine. **(a) Hand-author** the recorded fixtures in Popper's printed syntax, labelled as authored rather than produced by a run; the IK2 residual and "does Popper accept the rendering" stay open in the boundary. **(b) The owner authorizes installing** `popper-ilp`, SWI-Prolog and clingo in a scratch environment, for one real run recorded as evidence. This is an install on this machine. | owner's call; (a) if not authorized |
| IK5-D14 | Bounds | the §6 table | as stated |
| IK5-D15 | Base and branch | `claude/ik5-ilp-bridge` from B = `1bcb899` | as stated |

## 8. Tests

New file `tests/test_ilp_bridge.py`, with the corpus under
`tests/fixtures/induced_knowledge/ik5-corpus/` (IK5-D1). The fixture model is a
small synthetic orders model: orders with an integer amount, a customer and a
unary `order_flagged`. Its class manifest has negative populations with a large
or flagged order, positive ones without, and one positive population with no
orders, which makes the learned rule vacuous there.

| ID | Case | Expected |
|---|---|---|
| T1 | export equals the committed `neutral.json`, `bk.pl`, `exs.pl`, `bias.pl` and `export.json`, and E equals the golden digest | 0; byte-equal |
| T2 | two exports in subprocesses under `PYTHONHASHSEED=0` and `=1` | byte-identical trees |
| T3 | hostile inputs: an expected-state manifest; an opaque cell; a redacted role; a bad fact type id; over the facts bound; clauses, run records and Popper text that are over cap, deep, carry duplicate keys or NaN, are unparsable, are past the clause or literal bounds, or use a wrong schema version | 3, named; nothing written |
| T4 | the fragment: one case per refusal name in the §6 fragment table (16 names), including NAF (`\+` and `not/1`), aggregate (`count`, `findall`), disjunction (`;`) and non-ground absence | 3, with the construct named |
| T5 | a comparison clause → a `guarded` with the negated operator; an atom clause → an `absence`; both schema-valid under `gnd validate`; Popper text and its neutral JSON give the same proposal | 0; equal constraints |
| T6 | C3: matching sets → admitted; equal counts, different sets → `coverage-mismatch`; a difference that is only a vacuous example → `coverage-mismatch`; an unknown reported id → `unknown-example` | 0 / 3 / 3 / 3 |
| T7 | C4: E, clauses digest and learner name each mismatched; a missing or duplicate clause entry | 3, named |
| T8 | the proposal: schema-3, K ADD ops, every constraint `guarded` and `induced`/`proposed`/`deontic` with the computed block and no `reviewed_in`; `gnd evolve preview` exits 0; no `derivation_rule` anywhere | 0 |
| T9 | work counters: export at or under `P + F_max` on a near-cap export; import at or under `P × (1 + K)` with P = 10,000 and K = 32; the parser on a 1 MiB program | at or under |
| T10 | validation-order source pins for both commands; exits 11 (`--out` exists), 66 (missing inputs), 74 (a linked `--out` or population), 64 (usage) | as listed |
| T11 | RF1 (export and import goldens), RF5, RF6, layering, schema inventories, docs nav, skill twins | pass |
| T12 | determinism: two imports give byte-identical proposals and reports | equal |

**Criteria to tests:**

| Criterion | Tests |
|---|---|
| C1 | T1, T2 |
| C2 | T4, T5, T8 |
| C3 | T6 |
| C4 | T7; IK5-D12/D13 for the live run |

**Branch walk (the defining defect class):** every row of the fragment table
(T4), every binding check (T7), every verdict mapping (`warning`, `pass`,
`vacuous`, `unchecked`, and `fail` → 70, the last by a seeded alethic copy in
T6) and every export refusal (T3) has a case that fails on a wrong
implementation.

**Verification selection:**

| Gate | Disposition | Command or evidence | Input boundary | Invalidation |
|---|---|---|---|---|
| direct | run | `uv run pytest -q -p no:randomly tests/test_ilp_bridge.py` → 0 | the new modules, schemas and corpus | any IK5 edit |
| impact: reused readers | run | `tests/test_measure_labels.py` | `gnd.measure.labels` | an edit there |
| impact: proposal builder | run | `tests/test_discover*.py`, plus the evolve preview and proposal tests that name `discover` | `gnd.discover.output` | its generalization |
| impact: CLI and lanes | run | every `tests/test_rf*.py`, `test_gnd_arch.py`, the export CLI tests (souffle, lean, pyrel) and the `rai_import` tests | `commands/export.py`, `commands/checking.py`, goldens, layers, entry points | a dispatch edit |
| impact: packaging and docs | run | the schema inventories, `test_public_built_inventory.py`, docs nav and link tests, the skill sync tests | the new schemas, docs and skill lines | an edit there |
| broad default lane | cadence | `uv run pytest -q` on explicit owner selection or CI | — | — |
| pre-existing red | excluded | `test_incremental_performance.py` (IK4-Q5) | — | a fix on `main` |

The final file list is built by `git grep` at execution and committed as
evidence, with each name checked to be a real file (lesson from IK3's gate).

## 9. Out of scope for this phase

- running any learner in CI, or as a required lane;
- adapters other than Popper (an LLM proposer, neural learners, ILASP and the
  rest are later work on the same bridge);
- entity-level examples; expected-state manifests as learning input;
- `derivation_rule` output; recursion; negation as failure; aggregates;
  disjunction; comparisons over non-integer types;
- automatic admission or confirmation; scoring learned rules with IK3 (a host
  may run `gnd measure --labels` on the previewed model);
- reference-bearing models in evolve preview (IK4-Q2, before IK6);
- the IK6 walk, docs tour and skill census.

## 10. Size

Estimate:
- about 1,100 source lines: neutral form 250, Popper adapter 300, rewrite 200,
  service 250, CLI 100;
- about 250 schema lines;
- about 900 test lines, plus the corpus;
- about 200 doc and registration lines.

This is about 2.4 times IK3's estimate.

## 11. Approval instrument

Proposed in IK5-D1: corpus-first, under
`tests/fixtures/induced_knowledge/ik5-corpus/`.
- The README tells each case's story.
- The answers are split out:
  - `expected.json` holds exits, refusal names and constraints;
  - `expected-export/` holds the hand-written export files.
- The corpus is committed red, then approved by reading.

## 12. Implementability sweep (author inspection, not review)

| Requirement | Finding |
|---|---|
| "examples come from IK3 manifests" | Only class mode carries a class, so IK5 needs a class-mode manifest. That mode requires `rules` with at least one entry, so a host must name one existing rule to export. They are bound and ignored. Not a blocker; stated in §6. |
| "body rewriting" with comparisons | A `guarded` antecedent is positive atoms only (`$defs.guarded.antecedent.items: atom`). So a comparison can only be the designated literal, which gives check 5 (`multiple-comparisons`). |
| "non-ground absence refused" | `semantic:guarded-consequent-ground` needs every absence variable bound by the antecedent. Check 6 picks a ground atom when one exists, and refuses only when none does. |
| Golden digest of export (C1) | The goldens are hand-written expected files, so their digest is an answer the owner reads, not a number fixed after a run. |
| Set equality (C3) needs learner sets | Popper prints counts, not sets. The run record carries sets, computed by the host or the optional script. Recorded fixtures carry them by hand (IK5-D13). |
| IK2 block fit | Every field is mapped in §6, and the inequalities hold under IK5-D10. With precision-shaped support, the IK2 residual is discharged for computed blocks. Real-learner fit stays open unless IK5-D13 (b). |
| Model digest after import | The proposal's candidate model differs from MODEL, so the manifest no longer binds it. That is expected: a new manifest is needed to measure it. |
| Lane rules | `tools/gnd_arch.py` measures cross-lane edges and does not refuse them (`cross_lane`, line 718; IK4's discover → evolve edge exists), so IK5-D4 (a) needs no allowance. |
| `--out` refusal before work | As IK4-Q1 ruled: exit 11 before anything is written. |
| String constants in binds | `$defs.bindings` values are plain scalars, and a string beginning with `$` is a variable. A learned constant `'$x'` would silently become a variable, which widens the rule, so check 9 refuses it (`constant-spelling`). Found by this sweep. |
| Anchors named in §6 | Checked at B: `canonical_scalar` (`semantic_adapter.py:114`), `_apply_declared_operations` (`evolve/service.py:813`), `bind_manifest` (`measure/labels.py:229`), `run_bounded_process` (`process.py:385`), the `$defs.guarded`, `atom`, `comparison_operator` and `induction` schemas, and both skill pin sites. |

## 13. Owner gate record (2026-10-26)

**Approval (o).** The owner was asked "Approve IK5 spec r1 with the proposed
rulings?" and replied "Approve IK5 spec r1 with every proposed ruling, and D13
option (a): hand-authored Popper fixtures, no install." on 2026-10-26. The
approved bytes are spec r1 as committed in `326d6ad`, before this section was
added:

| Artifact | SHA-256 |
|---|---|
| `notes/phase-IK5-spec.md` (r1) | `39a15d8dba0469e1fac03d8698b689f5284e99fd23d66dc82b9a311cf25a1121` |

**Rulings (o).** IK5-D1 to D15 are ruled as proposed in §7:
- **D1:** corpus-first.
- **D2:** one example is one manifest population.
- **D3:** `wrong` covers the `negative` class, fixed.
- **D4:** both commands live in the `export` lane.
- **D5:** import takes `--target popper|neutral`.
- **D6:** coverage is compared per clause.
- **D7:** `unchecked` is not covered and is listed separately.
- **D8:** `coverage-mismatch` is exit 3 with a named reason.
- **D9:** all-or-nothing admission.
- **D10:** precision-shaped support.
- **D11:** redacted roles and opaque cells refuse the export.
- **D12:** no GND command runs a learner; an optional evidence script only.
- **D13:** option (a). Recorded fixtures are hand-authored in Popper's printed
  syntax and labelled as such; nothing is installed. Whether a real Popper
  accepts the rendering, and whether real Popper output fits the IK2 block,
  stay open in the record's boundary.
- **D14:** the §6 bounds.
- **D15:** branch `claude/ik5-ilp-bridge` from B = `1bcb899`.

**Next under IK5-D1.** The corpus is committed red before any implementation
file, and the owner approves it by reading.

## 14. Corpus findings (2026-10-26, awaiting the owner)

Found while authoring the corpus, before any implementation file. C-F2 and
C-F3 amend spec r1 and need an owner ruling; the others fix details r1 left
open.

- **C-F1 — two verdict branches the commands cannot reach.**
  - **`unchecked`:** the export refuses opaque cells, comparisons are
    integer-only and always ordered, and disconnected bodies are refused. So no
    corpus input can make a learned constraint `unchecked`.
  - **`fail` → 70:** every learned constraint is deontic, so `fail` cannot
    arise either.

  **Proposed:** keep both branches as defensive code. Each gets an
  implementation unit test that feeds the re-evaluation step a crafted checker
  result, so each has a case that fails it. They are not corpus cases.
- **C-F2 — the neutral import needs an export to bind.** With
  `--target neutral`, the import must recompute an export digest E, but r1's
  export has only the `popper` target. **Proposed:** `gnd export ilp
  --target neutral` writes `neutral.json` and `export.json` only, and E binds
  that tree (case X2). This adds one export target.
- **C-F3 — aggregate arguments are goals, not terms.** Popper-style aggregates
  (`aggregate_all(count, f(…), N)`) take a goal as an argument, which r1's term
  shape cannot hold. **Proposed:** `aggregate.args` items are terms or
  literals (cases F06, F07). The schema changes only inside a construct that is
  always refused.
- **C-F4 — names the corpus fixes.**
  - **Export refusals:** `expected-state` (XE1) and `opaque` (XE2).
  - **Refusal messages:** a fragment refusal names `clause <k>`.
  - **Export stdout:** includes E.
  - **The import report:** has `clauses[k].vacuous`.
  - **The neutral `primitive` spelling:** `integer` and `string` for the
    model's `Integer` and `String`.
  - **`export.json`:** `adapter_version` is the string `"1"`.
- **C-F5 — the hand-authored learner identity.** Recorded fixtures name the
  learner `popper 0.0.0+authored`, a token in IK2's grammar that says no run
  produced them (IK5-D13 (a)).
- **C-F6 — the rule-B designation is pinned.** For
  `wrong(A):- f_order_amount(A,B,C), f_order_flagged(A,B)`, check 6 designates
  the flagged atom, which is the last atom whose variables all occur
  elsewhere. That gives an `absence` consequent over the amount antecedent.
  Rule C (support 2 of 4, counterexamples p1 and p2) is the case that tells
  precision-shaped support apart from a count of covered examples.

**Red check:** `uv run pytest -q -p no:randomly tests/test_ilp_bridge.py` gives
41 failed and 2 passed by design. The two that pass check the answer key itself:
every case has an answer, and I1 and I2 agree on their rules.

## 15. Corpus approval (2026-10-26)

**Approval (o).** The owner was asked "Approve the IK5 corpus as committed, with
C-F1 to C-F6 as proposed?" and replied "Approve the IK5 corpus as committed in
d0cb831, with C-F1 to C-F6 as proposed. Go ahead and implement." on
2026-10-26. The approved corpus is `tests/fixtures/induced_knowledge/ik5-corpus/`
and `tests/test_ilp_bridge.py` as committed in `d0cb831`, red at 41 failed and
2 passed by design.

**Findings ruled as proposed (o):**
- **C-F1:** `unchecked` and `fail` stay as defensive branches, each with a unit
  test.
- **C-F2:** `gnd export ilp --target neutral` writes `neutral.json` and
  `export.json` only.
- **C-F3:** `aggregate.args` items are terms or literals.
- **C-F4:** the names the corpus fixes.
- **C-F5:** the learner identity `popper 0.0.0+authored`.
- **C-F6:** the rule-B designation.

## 16. Implementation findings (2026-10-26)

Recorded as found. No approved corpus answer changed: all 43 corpus tests
pass, and the implementation tests are separately identified successors in the
same file.

- **I-F1 — the audit time is a flag.** r1 named only an optional `--actor`.
  `--requested-at` is added beside it (ISO-8601 with a UTC offset; the default
  is now). Without it, two imports cannot be byte-identical (T12), as in IK4's
  discover.
- **I-F2 — the name bound is 59 characters, not r1's 62.** The model schema
  already restricts fact type ids to `^[a-z][a-z0-9_]*$`. So the `name`
  refusal fires only on length. It is set so that `ge_t_<id>` still fits the
  64-character schema name.
- **I-F3 — role reads go through `ModelIndex`.** RF6 refuses a literal
  `roles` read outside the model package. Model roles come from
  `ModelIndex.role_object_types()`. The rewriter takes the export's own column
  table, not the neutral dicts, so no RF6 exception is widened.
- **I-F4 — comparison predicates are converted after parsing.** The parser runs
  before the export exists (§4 rule 3), so it cannot know which names are
  comparisons. It keeps `gt_t_amount(C,100)` as an atom, and the fragment step
  turns any exported comparison predicate into a comparison, whichever form
  wrote it.
- **I-F5 — boolean constants round-trip.** The rendering spells booleans as the
  atoms `true` and `false`. At a boolean-typed role, the rewriter maps them back
  to booleans; otherwise a learned constant would never match.
- **I-F6 — two export refusals r1 did not name.**
  - `primitive`: a value type other than Integer, String or Boolean. Decimal,
    Date and the rest have no faithful rendering in this fragment.
  - `references`: a model with declared reference populations. Their facts are
    not in the manifest's populations, and evolve cannot preview such models
    (IK4-Q2).
- **I-F7 — the RF1 goldens across Python versions.**
  - The new `gnd import ilp-rules` help, and the changed `gnd export` help,
    wrap differently before 3.13, so both carry 3.11-, 3.13- and 3.14-keyed
    goldens.
  - The 3.11 keys are the 3.12 capture, because 3.11 is not installed. They
    differ from the old 3.11 golden only by the `ilp` addition.
  - 3.12, 3.13 and 3.14 were captured; the tree is identical on all three.
- **I-F8 — refactors made for one walk.**
  - IK3's per-population read became `labels.read_population`, shared by
    `score_populations` and the export.
  - IK4's proposal builder gained `add_operations` and keyword `origin`,
    `prefix` and `rationale` on `proposal`.
  - IK3's 76 and IK4's 65 tests pass unchanged.
- **I-F9 — check 10 validates with a placeholder induction block.** Support is
  not known until re-evaluation, so the single-constraint validation uses a
  block that validates (support 0/1, no examples). The final constraints carry
  the computed block, and the candidate model is validated again with all of
  them.
- **I-F10 — the near-cap import uses 7,500 examples, not 10,000.** The 1 MiB
  manifest holds about 7,500 class-mode entries in compact JSON (IK3's C-F3).
  T9 runs P = 7,500 and K = 32 and checks the work against P × (1 + K).
