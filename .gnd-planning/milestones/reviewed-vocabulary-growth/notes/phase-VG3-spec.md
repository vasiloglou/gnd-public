# Phase VG3 · an unattended root that includes a reviewed vocabulary · spec r1

## 1. Status

**Approved by delegated ruling (auto=true), 2026-11-23; implemented, recorded in [003-phase-VG3.md](../003-phase-VG3.md)** `(d)`. The owner
invoked `process-milestone reviewed-vocabulary-growth auto` on 2026-11-23,
which delegates spec rulings within this milestone; this is the driving
agent's ruling, not the owner's reading. The ruled bytes are this file's r1
(§7).

## 2. Provenance

- Derives from [plan r4](reviewed-vocabulary-growth-plan.md), approved by the
  owner on 2026-11-23 with D3 (a), D5 (a), D13 (a) and D14 (a)
  ([plan gate](../001-plan-gate.md)): Goal (VG3), §0 (R0.3–R0.5, R0.7), §1
  (H14–H19, H30–H34, H37–H39), §2 (VG3), §4 (VG3-C1 to VG3-C11), §5, §6, §9
  (the VG3 lane), §10 (D3, D5, D13, D14 and the VG3 open questions).
- From [#222](https://github.com/vasiloglou/gnd-public/issues/222), cases 1
  and 2 and its request.
- Written by `process-milestone` on 2026-11-23 on the topic branch after VG1
  (`7b68c558`). VG2 is not run: it waits for GO1 (plan §3); VG3 needs no
  VG2 file and does not wait for it (plan §3, "they do not wait for each
  other"). No review has read this spec.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan H14; #222 case 2 | the #222 root exits 3 with U2–U5 on the included elements | §6; T1 |
| plan H15; #222 case 1 | the seed with the mode on itself stays refused | T4 |
| plan H16 | the U rules run over the composed document under the root's `source`; origins are known to the caller, not to `_rule_unattended` | §6, "The origin test" |
| plan H17 | U4 issues on included object types have no `includes[ID]:` prefix; `remap_issues` maps fact-type selectors only | §6; T8 |
| plan H18; R0.7 | "Unattended source" becomes the home of the include rule; "Model includes" cites it | §6, pages; T12 |
| plan H19, H34, H39; D14 (a) | the span walk; U7 has no walk of its own; a skipped span's only message is `spans-unchecked` | §6; T5, T6 |
| plan H30; VG3-C10 | a root 0.4.0 validates keeps its exit, issues, span counts and JSON payload | T10 |
| plan H31; D13 (a) | composition proves validity, not review; U8 kept for an included element that is not `confirmed` | §6; T9 |
| plan H32, H33; R0.4 | the root's own elements, operations and obligations included, and a constraint attached to an included fact type keep every U rule | T2, T3 |
| plan H37; D5 | span-walk issues get the `includes[ID]:` prefix | §6; T11 |
| plan H38; D5 (a) | the attribution lines are in text output only; the JSON payload is unchanged | §6; T7, T10 |
| plan R0.3 | a model without the mode, with or without includes, is byte-identical | T7 |
| plan R0.5 | an included file with `mode: unattended` keeps `include:forbidden-section` | T4 |
| plan §6 risks | exemption leak (T2, T3); two enforcement sites (one origin test, T5); a 0.4.0 root changing output (T10) | as named |
| plan §9 | the VG3 lane, the guard block, `uv run ruff check src tests tools` | §8 ledger |
| plan H28 | component index updated in the same commit | §8 ledger |
| VG1 record, open question | the `ModelIndex` cache-key collision | not touched here: VG3 does not read `ModelIndex` |

## 4. The standing rules, bound to this phase

- **Totality (rule 1).** The origin test and the U-rule branches read a
  composed document that parsed; every new access goes through `_listed`,
  `isinstance(..., Mapping)` and `.get`, as the rule does today. T5 adds a
  non-mapping span and a non-string digest inside an include.
- **A cap bounds the algorithm (rule 2).** The origin test is one walk over
  the composed document; the attribution counts are one walk per include.
  Both are linear. T13 bounds `gnd validate` on a root with an include of
  1,000 object types and 1,000 fact types at under 10 s in process.
- **Validation order (rule 3).** Unchanged: composition refusals
  (`include:*`) precede semantic rules; the U rules run in U1–U8 order; the
  span walk runs after the model validates. The attribution lines print
  after warnings and before `OK:`.
- **One walk for N kinds (rule 4).** One origin test, `included_rows(doc,
  origins)`, read by the rule walk and by the span walk (plan §6, "Two
  enforcement sites").
- **One home (rule 5).** "Unattended source" gains the include paragraph and
  the attribution sentence; "Model includes" cites it in one sentence.
- **Measurement (rule 6).** VG3-C10's "what the base commit gives" is
  measured by running the H30 root at the base, not argued: T10 holds the
  base output as a literal captured before the first edit.
- **R0.3** T7. **R0.4** T2, T3. **R0.5** T4. **R0.6, R0.7** pages; R0.6 is
  VG4's.

## 5. Goal

The #222 root validates, exit 0, with `--document` and `--require-documents`,
and prints one attribution line per include. Each root-owned defect exits 3
with its rule. An included unconfirmed inferred `alethic` constraint exits 3
with U8 under `includes[ID]:`. A root 0.4.0 validates gives the same exit,
issues, counts and JSON. The VG3 lane, the guard block and `uv run ruff check
src tests tools` exit 0.

## 6. Design

### Reuse

| Capability | Searches | Found | Decision |
|---|---|---|---|
| which composed elements came from an include | `components_index.py search "include origin composed address"`; `git grep -n "ElementOrigin\|_ids(" src/gnd/model` | `model.composition`: `_includes._ids` (the one id-bearing walk, the same addresses `_merge` keys origins by) and `Model._provenance` | reuse: the test walks `_ids(doc)` and reads each address's origin; no address is parsed |
| issue addresses under an include | `git grep -n remap_issues src/gnd` | `_includes.remap_issues` (`:245`) | adapt: also map `$.object_types[id=…]` (H17) |
| span shape | `_unattended._span_issue` | reuse for U7 on included spans |

### The origin test (`src/gnd/model/_includes.py`, re-exported by `gnd.model`)

```python
def included_rows(document: Mapping, origins: Iterable[ElementOrigin]) -> frozenset[int]:
    """id() of every element of DOCUMENT whose origin is an include.

    Walks _ids(document), the walk _merge keys origins by, and keeps the
    elements whose origin is not 'model'. A constraint the root attaches to an
    included fact type has origin 'model' (H33). Positional, so it reads the
    composed document and a model_dump of it alike."""
```

### The rule walk (`src/gnd/model/_unattended.py`, `src/gnd/model/__init__.py`)

- `_model_warnings(doc, origins)` sets a context variable `_INCLUDED` to
  `included_rows(doc, origins)` around `semantic_validate` and resets it.
  Nothing else sets it, so every other caller of `semantic_validate` sees an
  empty set and today's rules (VG3-D1).
- `_rule_unattended` reads `_INCLUDED`. For an included element: U2–U6 ask
  nothing. Each span it carries in `provenance.spans`, and each
  `sample_spans[k].span`, whose `document_sha256` is a string naming a
  document the root declares, is checked by `_span_issue` (U7, D14 (a)).
  Any other included span is read by no rule. U8 applies unless the element
  is `confirmed` (D13 (a)). U1 and every root-owned element: as today.

### The span walk (`_unattended.py`, `src/gnd/commands/checking.py`)

- `unattended_span_issues` and `unattended_span_coverage` take
  `included: frozenset[int] = frozenset()`. `_iter_unattended_spans` yields
  whether each span's owner is in it. An included span is visited only when
  it is a mapping whose `document_sha256` names a root-declared document;
  otherwise it is neither counted nor re-hashed (D14 (a)).
- `_cmd_validate_documents` computes `included_rows` over the same dump it
  walks, with `result.model._provenance`, and passes the walk's issues
  through `remap_issues` (H37, D5).

### Remapping (`_includes.remap_issues`)

The `[id=…]` selector branch maps object types as it maps fact types, so a
U-rule issue on an included object type reads
`includes[ID]:$.object_types[id=X]…` (H17).

### Attribution (`_includes.include_attribution`, `checking.py`)

```python
def include_attribution(model: Model) -> list[dict[str, Any]]:
    """One row per include: id, sha256 and what the included file declares."""
```

Counts are read from each included file's own document (`IncludedFile`),
which is what composition appends (`_merge`). Text output, printed for a
model with `source.mode: unattended` and includes, after the warnings and
before `OK:`, one line per include in declaration order:

```text
INCLUDE seed sha256=<64 hex>: 2 object types, 1 fact types, 0 sample rows, 1 constraints (1 confirmed, 1 alethic, 1 explicit or user-supplied), 0 deontic notes
```

The JSON payload is unchanged (D5 (a), H38).

### Pages

- "Unattended source": a paragraph "An unattended root that includes a
  reviewed model": the exemption (U2–U6; U7 as D14; U8 as D13), the pin as
  the statement of review and its limit, the span walk for included spans,
  the attribution line, and that the JSON payload carries the prefix but not
  the line.
- "Model includes": after "Its source mode cannot be `unattended`", one
  sentence: an unattended root may include a reviewed file; "Unattended
  source" says what its rules ask of included elements.
- `docs/release-notes.md`: one entry.

## 7. Decisions

Ruled by delegated approval (auto=true), 2026-11-23 `(d)`.

| ID | Question | Readings and their cost | Ruling |
|---|---|---|---|
| VG3-D1 | How the origin reaches `_rule_unattended` (plan §10) | (a) a context variable set only by `_model_warnings`: no signature changes, every other caller unchanged. (b) an argument: `semantic_validate`'s rule protocol takes the document alone; every rule would change. (c) a filter over remapped issues: U8's exception and U7's narrowing cannot be expressed as a filter | (a) |
| VG3-D2 | The attribution line's exact text | as §6 | as §6 |
| VG3-D3 | Instrument | prose with a fixture case per criterion; the cases are small and live in the test file, which the owner can read as the corpus | prose |
| VG3-D4 | Redacted text output (a disclosure-projected payload) | the line carries only an id, a digest and counts, no values; it is printed on that path too | printed |

Budget: one diff review round (plan D7).

## 8. Tests

`tests/test_vg3_unattended_includes.py`, default lane. The fixture is #222's
two files, written by the test: the seed (version 4, `explicit`,
`confirmed`, `alethic`, `reviewed_in`) and the root (version 5,
`unattended`, `reviewer: none`, one document, the include, empty own
sections), plus `doc.md`.

| # | Criterion | Case | Expected |
|---|---|---|---|
| T1 | VG3-C1 | the #222 root, `--document doc.md --require-documents` | exit 0 |
| T2 | VG3-C2 | the root with one owned defect each: a `confirmed` constraint (U2), a `confirmed` operation (U2), an `explicit` constraint (U3), an object type without a span (U4), a fact type whose `sample_spans` miss a row (U6), a span naming an undeclared document (U7) | exit 3, that rule, a root address |
| T3 | VG3-C3 | a constraint attached to the included fact type: without a span; as `alethic` `sample` | exit 3, U5; exit 3, U8; at `$.fact_type_constraints[0].constraints[0]` |
| T4 | VG3-C4 | an included file with `mode: unattended`; the seed alone with the mode | `include:forbidden-section`; U2–U5 |
| T5 | VG3-C5 | span counts: an included span over the root's document is counted and re-hashed; one over another document is not counted and raises no U7; a root operation's span is not counted; an included span over the root's document with `start >= end` exits 3, U7, under `includes[seed]:`, with and without `--document`; an included span that is not a mapping, or whose digest is not a string, is read by no rule | as stated |
| T6 | VG3-C6 | the attribution line of T1 | the text of §6, with the seed's counts |
| T7 | VG3-C7, R0.3 | a model without the mode, without includes and with includes: `gnd validate` text and JSON, with and without `--document` | byte-identical to the base output, held as literals captured at `7b68c558` |
| T8 | VG3-C8 | `remap_issues` over a synthetic issue at `$.object_types[id=work]` where `work` came from `seed` | `includes[seed]:$.object_types[id=work]` |
| T9 | VG3-C9 | the seed with a `proposed`, `llm-inferred`, `alethic` constraint, under the root | exit 3, U8, under `includes[seed]:`; the same constraint `confirmed`: exit 0 |
| T10 | VG3-C10 | the H30 root (included elements `llm-inferred`, `proposed`, `deontic`, spans over the root's document) | exit, issues, span counts and JSON payload equal to literals captured at `7b68c558`; the text output differs by the attribution line only |
| T11 | VG3-C11 | an included span over the root's document with a wrong `excerpt_sha256`, `--document` | exit 3, `unattended:excerpt-mismatch` at `includes[seed]:…`, text and JSON |
| T12 | R0.7, pages | the "Unattended source" section names the exemption and the attribution line; "Model includes" cites it | present |
| T13 | rule 2 | a root including a file of 1,000 object types and 1,000 fact types | `gnd validate` under 10 s in process |

Branch table: included vs owned × U2–U8; included span: declared-document
mapping (checked, counted), other document (ignored), non-mapping
(ignored), malformed over a declared document (U7). Each has a case above.

### Verification-selection ledger

| Obligation | Disposition | Command or evidence | Input boundary | Justification | Invalidation |
|---|---|---|---|---|---|
| VG3-C1 to C11; T1–T13 | run | `uv run pytest -q tests/test_vg3_unattended_includes.py tests/test_unattended_mode.py tests/test_unattended_span_coverage.py tests/test_mc1_model_includes.py tests/test_mc1_guards.py tests/test_include_root_close.py --tb=short`, exit 0 | `_unattended.py`, `_includes.py`, `model/__init__.py`, `commands/checking.py`, the page | the plan §9 VG3 lane as written | any change to those |
| Guards | run | the `project.md` guard block, exit 0 | | issue 171 | |
| Lint | run | `uv run ruff check src tests tools`, exit 0 | | plan D11 | |
| Component index | run | `python3 scripts/components_index.py changed --base 7b68c558 --strict`, exit 0 | | plan H28 | |
| Other consumers of `semantic_validate` and `remap_issues` (evolve candidate validation, flatten, compose) | cadence | the default lane at milestone close | | the context variable is set only by `_model_warnings`, and the remap change touches only `[id=…]` selectors of included object types | a change to either |

## 9. Out of scope for this phase

- U1's first-document rule (D4) and growth rounds (VG4).
- Attribution in `gnd check` or `gnd judgments check` (plan §6).
- Spans on operations and obligations (still unchecked and uncounted).
- The `ModelIndex` cache key (VG1's open question).

## 10. Size

About 120 source lines, 30 page lines, 350 test lines.

## 11. Approval instrument

This prose (VG3-D3).

## Implementation findings, recorded as they were found `(d)`

2026-11-23, at `702496c8`.

1. **`_cmd_validate` is pinned by its AST digest** (`tests/test_rf5_commands.py`,
   the RF5 relocation pins). Printing the attribution line changes it. The
   change is registered as an RF5 successor in
   `evidence/VG3/source-successors.json`, chained after release-0.3.0 RN0's
   row (its `before` is RN0's `after`, raw and algorithm digests), and
   `tests/support/rf9_ci_sources.py` lists the file.
2. **The MC3 raw-body pin had no successor path.**
   `tests/test_mc3_source_observations.py` holds five command bodies,
   `_cmd_validate` among them, to raw digests recorded once, so any later
   change to one of them failed it. It now follows registered successor
   rows from each recorded digest; its negative control, an unregistered
   change, still fails.
3. **The query-policy guard counts `row['fact_types']`** in
   `commands/checking.py` as a model read. The attribution row's keys are
   `object_type_count` and `fact_type_count`.
4. **MC1's T44 asserted the behaviour D3 (a) changes**: an unattended root
   raising U rules on an included anonymous constraint. Its claim is the
   remapping of an anonymous included constraint; the constraint is now an
   unconfirmed inferred `alethic` one, which U8 still refuses (D13), so the
   claim keeps an issue to carry.
5. **UG3's a13 test wraps `_iter_unattended_spans` with a one-argument
   fake.** Its fake now passes the include set through.
6. **A known red outside the phase.** Five tests of
   `tests/test_ir3_pyrel_includes.py` (T3 ×4, T6) fail at `main`
   `1f403b07` and at VG1's head `5427e8fe`, verified in those checkouts on
   beast-3. VG3 changes no PyRel code and that file is not in its lane.
7. **A test-authoring slip.** T2's owned constraints were first written as
   top-level `mandatory` constraints, which the schema refuses at the top
   level; they are top-level `value` constraints.
8. **Review r1 (Codex), F1, reproduced and fixed at `01b76996`.** U7 read
   `sample_spans` on included object types and constraints, which no rule
   read before and which the span walk does not count. A malformed one
   there refused a root 0.4.0 accepts (VG3-C10). Sample spans are read on
   included fact types only.
9. **Review r1, F2, reproduced and fixed at `01b76996`.** The `[id=…]`
   selector pattern stopped at a newline, so an id holding one lost its
   `includes[ID]:` prefix. `remap_issues` now matches each declared
   element's whole selector text, longest first, and parses no id.
