# Derivation-failure explanation (why-not)

Draft r3, 2026-10-30. **Awaiting owner review.** Milestone: `derivation-why-not`.
Source: [gnd-public issue #66](https://github.com/vasiloglou/gnd-public/issues/66)
(request GR-T7 in the reporter's numbering).
Inspection baseline: `fb03739` (main after PR #64).
Planning only. Plan approval, phase execution, implementation and publication
have not occurred.

**Revision history.** Tags mark where a sentence came from:

- **r1:** first draft. Reviewed in plan review round 1 (four local readers) as
  SHA-256 `77928fb29f34589501843e20fe1db945fab550ca15d3e899fc0b20d3bb84cc70`
  (WN1 spec `cbc99f2643350c4eea495142abf26a6f8c715642d74dbda01e80538702081f03`);
  see the [round-1 disposition](plan-review-r1-disposition.md).
- **`(o)` 2026-10-30:** WN-D8, quoted: "WN-D8: use four local reviewer agents
  for the plan and close review, as in recent milestones. Run plan review round
  1 over r1." Instrument only.
- **`(p1)` r2, 2026-10-30:** the owner's direction, quoted: "I accept the
  round-1 disposition's repair themes A-K. Apply them as r2, take the proposed
  answers where a decision is re-argued, and run the one confirmation round over
  the blocking themes." Theme letters are cited as `(p1-A)` and so on. r2 was
  read in the confirmation round as SHA-256
  `b0308e35e0e088d7264b24c0f34de0bec2f676e7d83cc325bd90bbfa1514630e` (WN1 spec
  `d1c87cb1315341e453debb6fd7088abc0b8f5a4dc831dd2a4ac33abdf44f6f69`); see the
  [round-2 disposition](plan-review-r2-disposition.md).
- **`(p2)` r3, 2026-10-30:** the owner's direction, quoted: "I accept the
  round-2 disposition's repair themes L-S. Apply them as r3 with no further
  review round. Then I will decide on plan approval over r3." Cited as `(p2-L)`
  and so on. Review stopped by the stop rule (round-2 self-inflicted ratio 0.93).
  **Sentences marked `(p2)` carry no review opinion.**

The round-1 disposition gave no single proposed answer for WN-D3, D4 and D5.
The answers below were written by the plan's author after the owner's r2
direction. They are **proposed under that direction; the owner confirms them at
the plan gate**. (p2-S) Rulings on individual decisions are not approval of the
plan.

## Problem and completion predicates

When an admitted derivation rule derives no rows, `gnd check` reports an empty
extension (a vacuous or passing derivation verdict) and nothing more. It does not
say which body atom found no match, or under which bindings the join became
empty. `gnd witness` explains a row that *was* derived; nothing explains a row
that was not.

The reporter runs a certified-answer loop: a model answers, and a GND rule over
quote-verified facts either derives the claim or does not. The silent tier is
the one where the rule derives nothing. On the reporter's tuning set no change
of rule fixes those cases; the retry has to extract the missing fact, and that
needs the missing predicate named. Without the signal, the reporter's only move
is to re-ask the whole question. Their experiment added 25 facts and gained 3 of
45 answers, and was dropped. The workaround today is one claim-and-recheck run
per body atom, host-side.

**What the issue asks for.** For a named rule, or for a claimed row of its head:
the first body atom, in rule order, at which the conjunction becomes empty, with
its predicate, the constants bound by the earlier atoms, and the row count each
earlier atom still had. It offers three shapes: a `gnd why-not` command, a field
in the `check` report, or a new `gnd.api` function.

**Inspection of current bytes** (`fb03739`):

- `gnd.api.__all__` has eleven names (`api.py:119`), of which eight are
  functions (`python-api.md:8-9`). The issue's "eighth `gnd.api` function" counts
  functions as of its pin (`8a3a98b`); why-not would be the ninth function and the
  twelfth `__all__` name. Three pages still say "seven-function"
  (`cli.md:108`, `tour.md:29`, `runtimes/decision.md:93`). (p1-I)
- The witness lane (`src/gnd/witness/`, about 1,400 lines) captures grounded
  firings through `_WITNESS_TRACE` (`extensions.py:454`) and charges work only
  through it (`_witness_charge`, `extensions.py:457-460`), at four sites that
  count bindings (`:404`, `:737`, `:763`, `:872`). (p2-L) It records only
  successful firings, so it cannot name a failure.
- The production join (`extensions._clause_bindings`, `extensions.py:921`) does
  **not** evaluate body atoms in declaration order. It splits the body into
  connected components, reorders each to the earliest connected atom
  (`_joined_bindings`, `extensions.py:683`), takes their product, applies `negate`
  atoms, then `where` comparisons (`extensions.py:1699`), then head terms. The
  join returns a bag; duplicates are removed only at head projection
  (`extensions.py:952-958`). (p1-D)
- In production, an unavailable comparison or head term for **any** binding, or a
  non-integral head value, makes the **whole** head relation unavailable, even
  when other bindings or clauses derive rows. It is carried out of band in
  `_ExactExtensions.unavailable` and propagates to dependents. `check` then
  reports `unchecked` (band 4). (p1-A)
- Opaque values make every head downstream of them `unchecked`/`opaque-value`
  in `check` (`branches.py:786`), through a closure built from
  `population.facts`, which includes asserted rows of derived types
  (`_evaluate_derivations_dispatch`). `witness` reports the same case as band 2
  `value-unknown` (`witness/types.py:62`). `_base_relations` drops the asserted
  rows of every structured-rule type, and an opaque cell anywhere switches the
  stratified evaluator to its partial path. (p2-N)
- `check` reports unsound surplus only for `derivation: derived`
  (`extensions.py:2496`); asserted semiderived rows are never read by dependent
  rules, because `_base_relations` drops them. (p2-P)
- `tests/test_rf6_query_policy.py` counts every `.fact_types` load and every
  `fact_types`/`roles` subscript or `.get` under `src/gnd`, whatever the
  receiver. (p2-R)
- The `check` report schema is a closed, versioned output contract with ten
  derivation-verdict variants. Adding a field is a schema version bump.
- `api.witness` returns raw values; only the CLI view redacts them
  (`python-api.md:270-274`). `check` and `transition` spell their switch
  `unredacted=False` (`test_public_api.py:18-20`). (p1-G)

**Outcome.** A read-only explanation lane beside `witness`. Given a model, a
population and a derived fact type (optionally one claimed head row), GND first
asks its own evaluator whether the rule (or row) is derived, unavailable or not
derived, and refuses fragments it cannot explain. Only when the target is
cleanly not derived does why-not walk each clause and report the first blocking
step, the binding counts before it, and the roles the host must fill. A host can
then extract the named missing fact, add it, and re-check.

The milestone can close when:

1. On every corpus case, why-not's top status agrees with the `gnd check`
   derivation verdict under the map in WN1 T8, and with the oracle's own
   derivability (WN1). (p2-M)
2. For every walked clause, the declared-order prefix counts and the first
   blocking step match an independent naive oracle on a corpus whose named
   discriminators each have their property asserted (WN1). (p1-D, p2-Q)
3. The production pre-evaluation and the walk are each charged against their own
   ceiling; counter tests with literal expected values fix the outcome on both
   sides of each ceiling (WN1, WN2). (p2-L)
4. `gnd why-not` and `gnd.api.why_not` expose the kernel with the witness lane's
   input ceilings, a closed redacted CLI view and the exit bands of WN-D5; an
   output schema validates every payload; every pin listed in WN2-C3 is updated.
   If WN-D10 is ruled as proposed, golden payloads were committed before the code
   (WN2). (p1-G, p1-H, p1-I, p2-S)
5. A packaged two-gap example shows the repair loop with facts built only from
   payload fields, negative controls, and a final `witness` exit 0 (WN3). (p1-J)
6. Focused gates, independent diff reviews, the question sweep and a PR are
   recorded. Owner acceptance is separate.

## 0. Binding design rules

| Rule | Requirement |
|---|---|
| WN-R1: Read-only, no new verdict | Why-not never changes a check verdict, exit code, report schema or extension. `gnd check` and `gnd witness` payloads stay byte-identical. The kernel may install only a charge-only trace (its row hook records nothing); an outer witness trace is restored unchanged (WN1 T15b). (p1-C) |
| WN-R2: Production decides, the walk explains | `derived` and `unavailable` come from the production exact evaluation over the target's dependency closure (target included); `unsupported` from the fragment scan over the facts `check` reads. The walk runs only when production reports the target not derived and available. A relation in `unavailable` is never read as empty. A walked clause that ends with a non-zero count is an internal defect, raised as such. Matching, identity, negation, comparisons and head terms reuse the production helpers; there is no second matcher. (p1-A, p2-N, p2-O) |
| WN-R3: A falsifiable answer | Every blocked clause carries the counts that make the claim checkable: the prefix before the blocker is non-zero and the prefix through it is zero. An independent oracle recomputes them, and decides derivability on its own. (p2-M) |
| WN-R4: Bounded work, counted | Two budgets in `WhyNotLimits` (WN-D6): `pre_joins` for the production pre-evaluation, charged through the charge-only trace in bindings only, as `witness` is; and the walk's `joins`, `probes` and `binding_cells`. Probe work inside the pre-evaluation is bounded only by the input ceilings, as in `check` and `witness`. A breach is exit 4 `work-limit`; the raised error carries the counters for tests, and the payload withholds partial counts. Tests assert counters, not wall time. (p2-L) |
| WN-R5: Values only where asked | The API returns raw values, as `api.witness` does; the CLI's default view is a closed allow-list selection that shows predicates, roles, variable names, counts and flags, never population values, including in nested descent, the claimed row, reasons and errors. `--raw` shows values. (p1-G, WN-D4) |
| WN-R6: One home per sentence | The normative definition of the blocking step lives in the WN1 spec and, after WN2, in `docs/reference/why-not.md`; every other page cites it. The stable-API count sentence gets one home in WN2 (`python-api.md`); the other pages cite it. (p1-I) |
| WN-R7: Layering and query policy | New modules join the `witness` lane in `tools/gnd_layers.json` with zero new allowances. Model reads use only `ModelIndex.fact_type(id)`, `ModelIndex.iter_fact_types_shared()`, `witness.io.roster(model)`, `relation.roles` and `checker._relation_facts`; never `.fact_types` and never a `roles` subscript or `.get`, so the RF6 allow-list gains no row. Public names follow AGENTS.md shim rules. (p1-I, p2-R) |
| WN-R8: Approval, evidence, anonymity | `auto=false`. Plan authorship is not approval. Downstream applications are not named in committed artifacts. A mechanical test enforces it: it holds SHA-256 digests of normalized forbidden tokens (lower-cased, whitespace-collapsed), so nothing is named in the repository; it scans every file added since `fb03739`; a negative control plants a token whose digest is in a test-only list; it fails, never skips. (p2-S) |

Each phase spec binds every rule above and every paid-for rule in
`.claude/skills/process-phase/references/standing-rules.md`, by name or with a
one-sentence argument that it does not apply.

## 1. Scope, sources and authority

| Source | Use |
|---|---|
| Issue #66 | Request, use case, proposed shapes |
| `src/gnd/extensions.py` (join, negation, where, head, unavailable propagation, `_witness_charge`, `_WITNESS_TRACE`, `_evaluate_derivations_dispatch`) | Production semantics |
| `src/gnd/branches.py` | The `check` derivation verdict variants (T8 map) |
| `src/gnd/witness/` and `src/gnd/commands/witness.py` | Input lane, targets, limits, redaction, exit bands, command registration |
| `src/gnd/model/_validation.py` (`iter_derivation_clauses`, negation and head safety rules) | Clause presentation and reachable branches |
| `src/gnd/model_index.py`, `tests/test_rf6_query_policy.py` | Model query policy |
| `src/gnd/api.py`, `docs/reference/python-api.md`, `cli.md`, `capabilities.md`, `docs/compatibility.md` | Public surface, pins, release-note rule |
| `report.schema.json`, `payloads.py` | Why the check report is not the home (WN-D1) |
| `tools/gnd_layers.json`, AGENTS.md, CONTRIBUTING.md | Layering, PR rules |

A `gnd coverage MODEL` census counts experiment claims; it says nothing about
whether an explanation feature exists, so it does not settle this scope.

### Obligations harvested

| ID | Obligation (source) | Kind | Owner |
|---|---|---|---|
| O1 | Name the first body atom at which the conjunction becomes empty (issue, "Asked for") | requested | WN1 |
| O2 | Report its predicate (issue) | requested | WN1, WN2 payload |
| O3 | Report constants bound by earlier atoms (issue) | requested | WN1 role-keyed samples; WN2 `--raw` |
| O4 | Report the row count each earlier atom still had (issue) | requested | WN1 |
| O5 | Rule mode and claimed-row mode (issue) | requested | WN1 |
| O6 | Choose a surface (issue) | owner decision | WN-D1; WN2 |
| O7 | Name the missing predicate so the host can extract it (issue, "Why") | requested outcome | WN1 role map and descent; WN3 |
| O8 | Avoid one claim-and-recheck per atom (issue, "Workaround") | requested outcome | WN2: one call returns every clause |
| O9 | Agreement with `check`; check and witness results unchanged | cross-cutting gate | WN-R1, WN-R2; WN1 T8; WN2-C5 |
| O10 | Bounded work and counter-based time-bound tests (standing rule 2) | inherited | WN1-C5, WN2-C6 |
| O11 | Totality over hostile input (standing rule 1) | inherited | WN2-C1 |
| O12 | Layer map, RF6 query policy, shim inventory, API and CLI pins | cross-cutting | WN1-C7, WN2-C3 |
| O13 | Docs and release note for the new public surface (`compatibility.md:7`) | cross-cutting | WN2-C4, WN3-C3 |
| O14 | Downstream anonymity (owner constraint, as in `transition-check-performance` plan O14) | owner constraint | WN-R8 test; every diff review |
| O15 | Related direct-derivation request GR-T5 | noted | out of scope (§7); whether it is filed here is unchecked |
| O16 | Reporter acceptance in their loop | carried | the reporter, after merge |

## 2. Contract proposal and product behavior

All of this is proposed unless marked otherwise; §10 lists the rulings.

**Surface (WN-D1, proposed (a)).** A new command and API function in the
witness lane:

```text
gnd why-not MODEL POPULATION --fact-type ID [--row REQUEST] [--reference-root DIR] [--raw]
```

```python
gnd.api.why_not(model_path, population_path, fact_type, *, row_path=None,
                reference_root=None) -> dict
```

If WN-D11 is ruled as proposed, `--row` takes the witness request format with
**exactly one** target, whose `fact_type` must equal `--fact-type`; anything
else is exit 3. (p1-G, p2-S) The API returns raw values like `api.witness`; the
CLI view redacts unless `--raw` (WN-D4). Not a field in the `check` report: that
would bump the report schema and make every check pay for an explanation nobody
asked for.

**Status first (WN-R2).** (p1-A, p2-N) The kernel:

1. computes the closure: the target plus its transitive dependencies;
2. scans `population.facts` and reference facts for every fact type in the
   closure, target included, as `_evaluate_derivations_dispatch` does, and
   returns `unsupported` for an opaque value there (`opaque-value`), an aggregate
   in a target clause (`aggregate`) or a string target rule (`rule-opaque`); a
   body predicate with a string rule is read as base, as production reads it;
3. strips opaque rows of fact types outside the closure before building
   relations, so the pre-evaluation takes the exact path, as `check` does;
4. runs the production exact evaluation over the closure under a charge-only
   trace;
5. returns `unavailable` with production's reason, binding (raw only) and
   `source_relation` if the target is in `unavailable`;
6. returns `derived` if the claimed row is in the extension by identity, or (rule
   mode) the extension is non-empty;
7. otherwise walks each clause.

Why-not ignores `covers`: derivation evaluation never reads a derived type's
asserted rows, whatever `covers` says. A target that `check` reports as
`unchecked-not-covered` is explained normally. (p2-M)

**Blocking step (WN-D2, proposed: declared-order prefixes).** For each clause
(as presented by `iter_derivation_clauses`), walk the positive body atoms in
declaration order. Prefix *k* is the conjunction of atoms 1..*k*, with head
constants bound first in row mode. Its count is the number of distinct bindings
under production identity. The first *k* whose count is 0 is the blocker. If
every positive prefix is non-empty, continue with negated atoms, then `where`
comparisons (root comparisons before clause-local ones), then head terms. The
payload states `"order": "declared"`, so the reader knows it is not the
evaluator's order.

**Descent (WN-D3, proposed under the owner's direction; confirmed at the gate:
ground atoms only).** When the blocker is an atom over a derived or semiderived
predicate with a structured rule, and at least one sample binding grounds every
role of it, why-not explains the first such grounded row (canonical order) as a
claimed row, recursively, up to depth 8. Cycles are keyed on (predicate,
canonical row). A string-rule predicate is not descended into; its blocker says
`derivation: base`. When no sample grounds the atom, descent stops with
`not-ground`, and the payload's role map tells the host which roles are free;
the host asks again with a row. (p1-F, p2-O, p2-S)

**Semiderived rows.** An asserted semiderived row is never read by a dependent
rule. When the absent row at a blocker is asserted in the population, the
blocker carries `"asserted_not_read": true`. The WN2 reference doc says so. (p2-P)

**Payload sketch (CLI redacted view).** (p1-F)

```json
{"status": "blocked", "mode": "row", "order": "declared",
 "clauses": [{"clause_index": 0,
   "steps": [{"kind": "atom", "index": 0, "fact_type": "Quote", "count": 4},
             {"kind": "atom", "index": 1, "fact_type": "AuthorOf", "count": 0}],
   "blocker": {"kind": "atom", "index": 1, "fact_type": "AuthorOf",
               "derivation": "base", "ground": false, "asserted_not_read": false,
               "roles": {"work": {"variable": "$w", "bound": true},
                         "person": {"variable": "$p", "bound": false}},
               "sample_count": 4, "samples": "redacted"},
   "steps_after_blocker": "not-evaluated",
   "descent": null}]}
```

Under `--raw`, `samples` is a list of up to WN-D9 (5) role-keyed objects, e.g.
`{"work": "w1"}`, and constant terms show their values.

**Exit bands (WN-D5, proposed under the owner's direction; confirmed at the
gate).** (p1-H, p2-N)

| Exit | Status | Meaning for a host loop |
|---|---|---|
| 0 | `blocked` or `derived` | an answer about derivability; read `status` |
| 2 | `unsupported` | why-not cannot explain this fragment; reason `opaque-value`, `aggregate` or `rule-opaque` |
| 3 | input invalid | as elsewhere |
| 4 | `unavailable` or work limit | indeterminate, as `check`'s band 4; reason `term:…` or `work-limit` |

Opaque values follow `witness`'s band 2, not `check`'s band 4, because why-not
is a witness-lane explanation; T8's map states the correspondence. `cli.md`'s
exit paragraph gains a why-not sentence.

**Supported fragment (WN-D6).** Positive atoms, negated atoms, comparisons,
constant, variable and computed head terms, multiple clauses, base and derived
body predicates, reference populations. The validator already refuses unbound
negated and head variables (`_validation.py:4306`, `:4330`), so the walk has no
branch for them. (p1-E)

## 3. Dependencies and artifact homes

WN1 → WN2 → WN3 → close. No phase depends on provider review, downstream
execution, publication or certification.

| Artifact | Home |
|---|---|
| Plan, specs, records, review notes | `.gnd-planning/milestones/derivation-why-not/` |
| Kernel | `src/gnd/witness/why_not.py` (WN1) |
| Service, CLI, view | `src/gnd/witness/service.py`, `cli.py`, `view.py` extended; registration in `src/gnd/commands/witness.py` (WN2) (p1-I) |
| Output schema | `src/gnd/why-not.schema.json` (WN-D12): root-level output contracts are what `VENDORED_SCHEMAS` in `test_public_built_inventory.py` enumerates, beside `report.schema.json` (p2-R) |
| API | `src/gnd/api.py` re-export, appended to `__all__` (WN2) |
| Reference doc | `docs/reference/why-not.md`, `zensical.toml` nav; rows in `cli.md`, `python-api.md`, `capabilities.md` (WN2) |
| Golden payloads (WN2 approval corpus, if WN-D10) | `tests/fixtures/why_not/` |
| Example | a small certified-answer model under `src/gnd/examples/` (name chosen in the WN3 spec) |

## 4. Phases

### WN1: The explanation kernel

Spec: [phase-WN1-spec.md](phase-WN1-spec.md), r3, blocked on plan approval and
on WN-D2, D3, D6, D7, D9, D10 and D14, and on spec D6. (p2-S)

- **WN1-C1:** status first: closure with the target, opaque scan over the facts
  `check` reads, opaque stripping outside the closure, production
  pre-evaluation, `unavailable` and `derived` from production; the walk only
  otherwise. (p1-A, p2-N)
- **WN1-C2:** declared-order prefix counts and the first blocking step for
  positive atoms, negated atoms, comparisons and head terms, per clause; row
  mode with both `head-bind` sub-branches.
- **WN1-C3:** an independent oracle with its own identity table and naive
  fixpoint agrees on every count, the full blocker record and derivability, over
  a corpus whose discriminators each have their property asserted. (p1-D, p2-M,
  p2-Q)
- **WN1-C4:** ground-only descent (structured-rule predicates only) with
  (predicate, row) cycle keys and three stop reasons, each with a case. (p1-F,
  p2-O)
- **WN1-C5:** two budgets (`pre_joins`; walk `joins`, `probes`,
  `binding_cells`); counter tests with literal values on both sides of each
  ceiling, on fixtures where production does not enumerate what the walk does.
  (p2-L)
- **WN1-C6:** one case per declared, reachable branch (spec §8 branch walk).
  (p1-E, p2-O)
- **WN1-C7:** layer map entry; RF6 query policy unchanged; T15b outer-trace
  isolation. (p1-I, C)

### WN2: Public command, API and docs

Approval instrument: if WN-D10 is ruled as proposed, corpus-first: golden
payloads for the redacted and `--raw` views, expected exits and refusals are
committed red before code. (p1-K, p2-S)

- **WN2-C1:** `gnd why-not` and `gnd.api.why_not` through the witness input lane.
  The service projects `WhyNotLimits` onto a `WitnessLimits` for input loading,
  because the lane's `checked_limits` accepts only that class; a test pins the
  projection. Hostile inputs (oversize, deep nesting, NaN, long integers, unknown
  or non-derived fact type, and, if WN-D11 is ruled as proposed, a row file with
  zero, two or a mismatched target) exit 3. (p2-R, p2-S)
- **WN2-C2:** `why-not.schema.json` validates every golden payload; the redacted
  view is a closed allow-list in `witness/view.py`; a leak test asserts that no
  population value appears anywhere in the redacted payload or in error text,
  including descent and the claimed row. `VENDORED_SCHEMAS` gains the schema.
  (p1-G, I)
- **WN2-C3:** pins: (p1-I, p2-R)
  - API: the three exact `__all__` literals (`test_public_api.py:16`,
    `test_v61_phase2_api.py:38`, `tools/run_public_acceptance.py:373`, exercised
    by `test_public_acceptance_runner.py`); a separate `why_not` signature
    assertion in `test_public_api.py` (its `expected` loop requires
    `unredacted`, which `why_not` does not take), matching `api.witness`'s shape;
    a new case in `test_public_reference_signatures.py`; and
    `test_public_runtime.py:52` (WN-D13);
  - CLI: `test_rf1_cli_pins.py` (`EXPECTED_PARSERS` 56 → 57, `cli/tree.json`,
    new `cli-help/gnd_why-not` and `cli-exit/gnd_why-not` goldens, and every
    golden that embeds the command list, including the root and the
    `install`/`doctor`/`uninstall` exit goldens for Python 3.11, 3.13 and 3.14,
    all regenerated with `tools/rf1_pins.py capture`, then `goldens.sha256`);
    `test_rf5_commands.py:118`; a `tests/fixtures/rf5-handlers/cases.json` case
    with its `answers.json` entry and a `target` for the disabling control;
    `commands/witness.py` and `witness.cli` keep importing `gnd.witness.service`,
    not `gnd.api`.
- **WN2-C4:** docs: `docs/reference/why-not.md` is the one home, with a
  `zensical.toml` nav entry and the semiderived and `covers` notes; `cli.md` row
  (probed by `test_reference_command_routes_exist`) and exit sentence;
  `python-api.md` section with a runnable `gnd-run` block and fixture;
  `capabilities.md` row; the stable-API count sentence gets one home and the
  three stale pages cite it; a release note. (p1-I, p2-P)
- **WN2-C5:** `gnd check` and `gnd witness` payloads byte-identical on the
  existing contract fixtures.
- **WN2-C6:** counter-based time-bound tests over target intake and view
  rendering. (p1-C)

### WN3: The repair loop, end to end

- **WN3-C1:** a small packaged example with a claim rule over quoted facts and a
  population with **two** missing base facts; it joins the example list in
  `tools/check_installed_docs.py`. (p1-I, J)
- **WN3-C2:** a committed test walks the loop in row mode on the claimed row:
  (p1-J, p2-Q)
  - before repair, `check` gives a `pass` derivation verdict with the claimed row
    absent from the extension (the spec names the exact variant);
  - each gap sits at body index ≥ 1 and has at least one bound role whose value
    comes from the raw samples;
  - why-not exits 0 `blocked` and names gap 1; the test builds the fact **only**
    from payload fields (`fact_type`, the role map, raw samples) plus an explicit
    "extracted" table that supplies free roles only; the test asserts that the
    table's roles and the blocker's bound roles are disjoint;
  - negative controls: the same values on the previous step's predicate, and the
    right predicate with a wrong bound value, both leave the claim underived and
    the blocker's (kind, index, fact_type) unchanged;
  - after repair 1, why-not names gap 2; after repair 2 it exits 0 `derived`;
  - `witness` then exits 0 for the row.
- **WN3-C3:** a how-to page (`docs/how-to/`). Business-facing tutorial pages, if
  any, follow the skills-not-code rule.
- **WN3-C4:** packaged skills: the spec decides whether `gnd-export` (which owns
  the witness workflow) or `gnd-dev-session` routes to why-not; any edit is a
  route sentence only. `gnd-induce` is not packaged at this baseline. (p1-I)

### Milestone close (not a feature phase)

Final parity evidence, the four-reader close review (WN-D8), the question sweep,
carryovers (O15 to its own issue if the owner wants one, O16 to the reporter),
and a PR.

### Obligation-to-gate map

| Obligation | Gate |
|---|---|
| O1, O2, O4 | WN1-C2, C3 |
| O3 | WN1-C2 samples; WN2-C2 |
| O5 | WN1-C2 |
| O6 | WN-D1; WN2-C1 |
| O7 | WN1-C4; WN3-C2 |
| O8 | WN2-C1 |
| O9 | WN1-C1 and T8; WN2-C5; close |
| O10 | WN1-C5; WN2-C6 |
| O11 | WN2-C1 |
| O12 | WN1-C7; WN2-C3 |
| O13 | WN2-C4; WN3-C3 |
| O14 | WN-R8 test; every diff review |
| O15, O16 | close carryovers |

## 5. Documentation, skill and compatibility surfaces

- New: one command, one API function (ninth function, twelfth `__all__` name,
  appended), one schema, one reference page, one how-to, one example.
- No change to the `check`, `witness` or `replay` contracts.
- Release note in WN2, with the surface (`compatibility.md:7`). (p1-I)
- Packaged skills: WN3-C4.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| Why-not and `check` disagree | WN-R2 status-first design; WN1 T8 against the `check` verdict over the whole corpus |
| An unavailable relation read as empty | WN-R2; T1 cases for target, positive dependency, negated dependency, descent target |
| An opaque claimed row missed | Opaque scan over `population.facts` (WN-R2); T14 case |
| Declared order misleads when the evaluator reorders | `"order": "declared"` in the payload; a corpus case where the orders differ, with the difference asserted |
| Unbounded work | WN-R4 two budgets; counter tests (WN1-C5) |
| Values leak | WN-R5 closed view; WN2-C2 leak test |
| "Blocked" read as "false" | Docs state why-not explains a missing derivation in this population; it proves nothing about the world |
| The oracle shares code with the kernel | Oracle imports nothing from `gnd.extensions`, `gnd.terms`, `gnd.values`, `gnd.checker` or `gnd.witness`, enforced by an AST import test |
| Downstream names leak | WN-R8 test; review lens |
| A repair round introduces defects | §8 round budget and stop rule |

## 7. Out of scope

- A field in the `check` report or any report schema bump.
- The direct-derivation request (GR-T5) and the reporter's other requests.
- Automatic repair: GND names the gap; adding facts is the host's move.
- Partially bound descent (WN-D3).
- Explaining constraint violations (already reported by `check`).
- Aggregates and opaque rules; native, LQP and PyRel runtimes.
- Changes inside the downstream application. Publication, release,
  certification.

## 8. Execution, approval and review protocol

`auto=false`. Each phase follows `process-phase`: spec, owner gate,
implementation and focused tests, an independent diff review, a refactoring
review and a record. No code is written before recorded spec approval. Plan and
close review: four local readers, WN-D8 `(o)`, with lenses: correctness against
production semantics; implementability; protocol and anonymity; test design and
falsifiability. The per-phase diff instrument is **proposed**: one local reader
per phase. (p1-K) One reader is one reader, not a panel.

Plan review: round 1 ran over r1 and round 2 (confirmation) over r2. Round 2's
self-inflicted ratio was 0.93, above one half, so the stop rule in
`review-convergence.md` ended review; r3 applies the round-2 repairs at the
owner's direction with no further round, and the owner decides plan approval over
r3. (p2-S) Work happens on a topic branch, then a PR; merge requires the owner.

## 9. Per-phase verification story

| Phase | Expected result | Focused gate |
|---|---|---|
| WN1 | Kernel agrees with `check` and the oracle; counters fix outcomes; no public diff | `uv run pytest -q tests/test_why_not_kernel.py tests/test_why_not_oracle.py tests/test_rf1_layering.py tests/test_rf4_peripheral.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_public_v71_witness_corpus.py tests/test_public_optional_value_witness.py` plus the check-contract files T15 names (WN1 spec §8) (p2-R) |
| WN2 | Goldens pass; schema validates; pins updated; check/witness parity | WN1 gate plus `tests/test_public_why_not.py tests/test_public_api.py tests/test_v61_phase2_api.py tests/test_public_reference_signatures.py tests/test_rf1_cli_pins.py tests/test_rf5_commands.py tests/test_rf5_handler_pins.py tests/test_documentation_tutorials.py tests/test_public_acceptance_runner.py`; `test_public_built_inventory.py` and `test_public_runtime.py` are distribution lanes, run on owner selection |
| WN3 | Two-gap repair loop passes; docs build | WN2 gate plus the example test and the installed-docs check |

The broad suite runs on explicit owner selection.

## 10. Owner decisions and open questions

| ID | Question | Readings and cost | Ruling or proposal |
|---|---|---|---|
| WN-D1 | Surface | (a) new command + API in the witness lane; (b) a `check` report field: schema bump, cost on every check; (c) both | proposed **(a)** |
| WN-D2 | Which order defines "first blocking atom" | (a) declaration-order prefixes: readable; the walk can enumerate a product production avoided (the walk budget breaches sooner); (b) the evaluator's reordered join: cheaper, but the "first" atom depends on connectivity | proposed **(a)**, order named in the payload |
| WN-D3 | Descent into a derived blocker | (a) none: one call per level from the host; (b) ground atoms only, structured-rule predicates only, cycles keyed on (predicate, row): extra work bounded by depth 8; (c) partially bound descent: a new pattern mode | **(b)**, proposed under the owner's direction of 2026-10-30; the owner confirms at the plan gate |
| WN-D4 | Values in output | (a) API raw like `api.witness`, CLI redacted with `--raw`; (b) `unredacted=False` like `check`: API redacted by default, a third spelling for the lane; (c) a new `raw=False`: a fourth convention | **(a)**, proposed under the owner's direction; confirmed at the gate |
| WN-D5 | Exit bands | (a) r1: `0` blocked, `2` derived or unsupported: host cannot tell them apart; (b) `0` blocked or derived (read `status`), `2` unsupported (incl. opaque, as `witness`), `3`, `4` unavailable or work limit | **(b)**, proposed under the owner's direction; confirmed at the gate |
| WN-D6 | Fragment and ceilings | fragment as §2; a sibling `WhyNotLimits` with `pre_joins` and the walk's `joins`, `probes`, `binding_cells`, projected onto `WitnessLimits` for input loading, rather than widening `WitnessLimits` | proposed as stated (p2-L) |
| WN-D7 | Code home | (a) `gnd.witness.why_not`; (b) a new lane | proposed **(a)** |
| WN-D8 | Review instrument for plan and close | | **Ruled (o) 2026-10-30:** four local readers |
| WN-D9 | Sample count | | proposed 5, total count always given |
| WN-D10 | Approval instrument per phase | WN1 prose: its payload is internal and WN2 fixes the wire form; WN2 corpus-first: it ships a serialized format, exit codes and refusals (`review-convergence.md`) | proposed as stated |
| WN-D11 | Rows per call | (a) one row matching `--fact-type`, else exit 3; (b) many rows with a combining rule: a host loop asks per claim anyway | proposed **(a)** |
| WN-D12 | Schema home and vendoring | (a) `src/gnd/why-not.schema.json`, no skill copy; (b) `src/gnd/schema/` beside the witness schemas; (c) also vendor into `gnd-export/references` with a sync test and two `EXPECTED_SKILL_FILES` pins | proposed **(a)** |
| WN-D13 | The stale ten-name tuple in `test_public_runtime.py:52` | (a) fix it in WN2 to the twelve names, recorded; (b) leave it: a distribution probe that would then be two names behind | proposed **(a)** |
| WN-D14 | Validation order between a malformed row and an unsupported fragment | (a) malformed row first (exit 3 before exit 2): the same order as `witness`, whose intake refuses malformed targets before `classify_targets` reports unsupported; (b) unsupported first: r1's order | proposed **(a)** (p2-S) |

No open question is inherited from an earlier milestone.
