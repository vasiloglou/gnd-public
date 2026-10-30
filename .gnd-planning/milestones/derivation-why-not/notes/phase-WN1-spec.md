# Phase WN1 -- the why-not explanation kernel

## 1. Status

**Draft r3, blocked.** Implementable once the owner approves plan r3 and rules
WN-D2, WN-D3 (confirmation), WN-D6, WN-D7, WN-D9, WN-D10 and WN-D14 (plan §10),
and spec D6 below. These change the algorithm, the module path, the limits
class, the validation order and the payload fields below. No implementation has
started. (p2-S)

## 2. Provenance

- Derived from [plan r3](derivation-why-not-plan.md) §0, §2, §4 WN1 and §10, at
  baseline `fb03739`.
- r1 (SHA-256 `cbc99f2643350c4eea495142abf26a6f8c715642d74dbda01e80538702081f03`)
  was read in plan review round 1 and r2
  (`d1c87cb1315341e453debb6fd7088abc0b8f5a4dc831dd2a4ac33abdf44f6f69`) in the
  confirmation round, each by four local readers; see the
  [round-1](plan-review-r1-disposition.md) and
  [round-2](plan-review-r2-disposition.md) dispositions. Review stopped by the
  stop rule. r3 applies the round-2 themes L-S at the owner's direction of
  2026-10-30 (quoted in the plan header). **These r3 bytes carry no review
  opinion.**
- Change tags: `(p1-X)` marks a round-1 repair and `(p2-X)` a round-2 repair
  under theme X.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan WN1-C1, WN-R2, O9 | status first: closure with the target, opaque scan over the facts `check` reads, production pre-evaluation | §6.1, §6.2; §8 T1, T8 |
| plan WN1-C2, O1, O2, O4, O5 | declared-order prefix counts and the first blocking step; row mode | §6.3; §8 T2..T7 |
| plan WN1-C3, WN-R3 | independent oracle with its own derivability; discriminators with asserted properties | §6.6; §8 T8, T9 |
| plan WN1-C4, O7, WN-D3 | ground-only descent over structured-rule predicates | §6.5; §8 T10, T11 |
| plan WN1-C5, WN-R4, O10 | two budgets; literal counter tests | §6.7; §8 T12, T13 |
| plan WN1-C6 | one case per declared, reachable branch | §8 branch walk |
| plan WN1-C7, WN-R7, O12 | layer map, RF6 query policy, outer-trace isolation | §6.8; §8 T15, T15b, T16 |
| plan O3, WN-R5, WN-D9 | role-keyed raw samples (the kernel returns raw; WN2 redacts) | §6.3, §6.4 |
| plan WN-R1 | no change to check, witness or report contracts | §8 T15 |
| plan semiderived note (p2-P) | `asserted_not_read` flag | §6.3; §8 T10 |
| plan O14, WN-R8 | no downstream names | §8 T17 |

## 4. Rules bound to WN1

Plan rules:

- **WN-R1** read-only: the kernel returns a value; it registers no branch and
  writes no report field. It installs only a charge-only trace (§6.7) and resets
  it. T15 pins check and witness results; T15b runs the kernel inside an active
  witness trace and asserts that trace's rows and charges are unchanged.
- **WN-R2** production decides: §6.2 takes `derived` and `unavailable` from
  production and `unsupported` from the fragment scan. The walk uses
  `checker._joined_atom_candidates` for atom matching, `_identity_key` and
  `_identity_token` for identity, the negation identity rule of
  `_apply_negation`, `terms.compare_terms`, and `terms.evaluate_term` plus
  `materialize_scalar` for head values. A walked clause that ends non-zero raises
  `WhyNotInternalError`. (p2-O)
- **WN-R3** falsifiable: every `blocked` clause carries the counts that make the
  claim checkable; T9 recomputes them independently, and T8 checks the status
  against `check` and the oracle. (p2-M)
- **WN-R4** two budgets, counted: §6.7.
- **WN-R5** values: the kernel returns raw values; WN2's view redacts.
- **WN-R6** one home: §6.3 is the normative definition until WN2 moves it to
  `docs/reference/why-not.md`; this spec then cites the doc.
- **WN-R7** layering and query policy: §6.8.
- **WN-R8**: `auto=false`; anonymity by T17.

Standing rules:

1. **Totality.** The kernel is called only by WN2's service after the witness
   input lane loads and validates the inputs. It is still total over its own
   arguments: an unknown or non-derived fact type, a malformed row or a
   malformed clause raises `WhyNotInputError` (a `ValueError`), never another
   class (T14).
2. **Cap bounds the algorithm.** The pre-evaluation is bounded in bindings
   (`pre_joins`), as `witness` is; its probe work is bounded only by the input
   ceilings. The walk is bounded in bindings, probes and cells. T13 fixes both
   with literal counter values. (p2-L)
3. **Validation order (WN-D14, proposed).** Limits check, fact-type existence,
   derived-ness, row shape (row mode), fragment scan, pre-evaluation, then the
   walk. A malformed row is refused (exit 3) before an unsupported fragment is
   reported (exit 2), the order `witness` uses: its intake refuses malformed
   targets before `classify_targets` reports unsupported. Pinned by a case with
   both faults (T14). (p2-S)
4. **One walk over N kinds.** One step loop handles the step kinds (atom,
   negated, comparison, head) in a fixed sequence, with one counting and
   charging path.
5. **One home.** See WN-R6.
6. **Measure, don't argue.** WN-D2's cost claim is measured by T13(a)/(b) on a
   fixture where production avoids the product the walk enumerates; the measured
   counters are recorded in the phase record.

## 5. Goal

`gnd.witness.why_not.explain(model, candidate, fact_type_id, *, row=None,
references=None, limits=DEFAULT_WHY_NOT_LIMITS) -> WhyNotResult`, where
`candidate` is a loaded `Population`, `references` a resolved reference context
(as `produce_witness` takes them), and `row` either `None` (rule mode) or a list
of typed cells `{"primitive": …, "value": …}` in the target's role order, the
witness target-cell format.

On the T8 and T9 corpora: top `status` agrees with the `gnd check` derivation
verdict under the T8 map and with the oracle's derivability; for `blocked`,
every count and blocker record equals the oracle's. A ceiling breach raises
`WhyNotWorkError` carrying the counters. (p2-M)

## 6. Design

### 6.1 Fragment scan

The closure is the target plus its transitive dependencies
(`checker.derivation_dependencies`). (p2-N)

| Feature | Behavior |
|---|---|
| positive atoms, constants and repeated variables in atoms | walked |
| `negate` atoms | walked |
| `where` comparisons, root before clause-local (`iter_derivation_clauses`) | walked |
| several clauses | one entry per clause |
| derived or semiderived body predicates with structured rules | read from production's exact extension |
| body predicate with a string (opaque) rule | read as base from its asserted rows, as `_base_relations` does; blocker says `derivation: base`; no descent |
| constant, variable and computed head terms | walked; computed terms are evaluated, not bound |
| `aggregate` in a target clause | `unsupported`, reason `aggregate` |
| target rule is a string | `unsupported`, reason `rule-opaque` |
| an opaque (dict) value in `population.facts` or reference facts for any fact type in the closure, target included | `unsupported`, reason `opaque-value` |

Opaque rows of fact types **outside** the closure are stripped before relations
are built, so the pre-evaluation takes the exact path, as `check` does. Unbound
negated and head variables cannot reach the kernel: the validator refuses them
(`_validation.py:4306`, `:4330`). Why-not ignores `covers`. (p2-M, p2-N)

### 6.2 Status first

1. Validate per §4 rule 3; scan per §6.1.
2. Build base relations as `produce_witness` does (`bind_population` with
   references, then `checker._base_relations`), after stripping opaque rows
   outside the closure.
3. Under the charge-only trace (§6.7), call
   `checker._evaluate_stratified_extensions(model, relations, heads=closure, exact=True)`;
   `closure` includes the target.
4. If the target is in `result.extensions.unavailable`: return `unavailable` with
   `reason`, `source_relation` and the raw `binding`.
5. Row mode: if the claimed row's identity token is in the target extension,
   return `derived`. Rule mode: if the extension is non-empty, return `derived`.
6. Otherwise walk each clause (§6.3) over production's relations and extensions.
   No relation is read as empty unless production returned it. If **any** walked
   clause ends with a non-zero count, raise `WhyNotInternalError`. (p2-O)

### 6.3 Normative definition: steps and the blocking step

For one clause *c* with positive atoms *a1..an*, negated atoms *n1..nm*,
comparisons *w1..wp* and head *h*:

1. Seed *B0*: rule mode `[{}]`. Row mode: one binding mapping each head variable
   to its claimed cell value. Step `head-bind` with count 0 if a head variable
   appears at two roles with different claimed values (`head-bind:variable`), or a
   constant head term differs from its claimed cell (`head-bind:constant`).
   Computed head terms are not bound here.
2. For *k* = 1..n: *Bk* = the join of *B(k-1)* with the candidates of *ak*
   (`_joined_atom_candidates`), through a hash index on shared variables, as a
   **set** of bindings under `_identity_key`. A disconnected *ak* is a product.
   Step record `{"kind": "atom", "index": k-1, "fact_type": …, "count": |Bk|}`.
3. Each negated atom in order: remove bindings whose ground tuple is in the
   relation. Step kind `negated`.
4. Each comparison in order: keep bindings where `compare_terms` returns
   `True`. (An unavailable result cannot occur here: §6.2 step 4 already
   returned.) Step kind `comparison`.
5. Head, row mode only: evaluate every head term, materialize it, and keep
   bindings whose row identity token equals the claimed row's. Step kind `head`.
   In rule mode a non-empty set reaching the head would mean production derived
   a row, which §6.2 step 6 treats as an internal defect.
6. The **blocking step** is the first step whose count is 0. Later steps are not
   computed; the clause carries `"steps_after_blocker": "not-evaluated"`.

Counts are counts of distinct bindings over the variables bound so far, under
`_identity_key` (so `1` and `1.0` are one value, `True` and `1` are two).

The blocker record:

```json
{"kind": "atom", "index": 1, "fact_type": "AuthorOf", "derivation": "base",
 "ground": false, "asserted_not_read": false,
 "roles": {"work": {"variable": "$w", "bound": true},
           "person": {"variable": "$p", "bound": false}},
 "sample_count": 4,
 "samples": [{"work": "w1"}, {"work": "w2"}]}
```

`roles` covers every role of the atom: `{"variable": name, "bound": bool}` or
`{"constant": value}`. `ground` is true when every role is a constant or a bound
variable. `asserted_not_read` is true when the blocker's predicate is
semiderived and some sample's ground row is asserted in the population, because
dependent rules never read asserted semiderived rows (p2-P). `samples` holds up
to WN-D9 (5) bindings of the previous step, projected onto the atom's bound
roles and **keyed by role**, in canonical order (sorted by canonical JSON).
`sample_count` is the previous step's count. For `negated`, `comparison` and
`head` blockers, `fact_type`/`roles` are replaced by the step's index and the
bound variables it reads.

### 6.4 Result types

```python
@dataclass(frozen=True)
class ClauseExplanation:
    clause_index: int
    steps: tuple[dict, ...]
    blocker: dict
    steps_after_blocker: Literal["not-evaluated"] | None
    descent: "WhyNotResult | None"
    descent_stopped: Literal["not-ground", "cycle", "depth", "not-derived"] | None

@dataclass(frozen=True)
class WhyNotResult:
    fact_type: str
    mode: Literal["rule", "row"]
    order: Literal["declared"]
    status: Literal["derived", "blocked", "unavailable", "unsupported"]
    reason: str | None
    unavailable: dict | None        # reason, source_relation, binding (raw)
    clauses: tuple[ClauseExplanation, ...]
    work: dict                      # {"pre_joins": int, "joins": int, "probes": int, "binding_cells": int}
```

Every walked clause is blocked; there is no clause `derived` status. (p2-O)
`descent_stopped` is `not-derived` when the blocker's predicate is base or has a
string rule.

### 6.5 Descent (WN-D3, proposed; confirmed at the gate)

When the blocker is an atom over a derived or semiderived predicate **with a
structured rule** and at least one sample grounds it, call `explain` on that
predicate in row mode with the first grounded row in canonical order, at depth
+ 1, sharing both budgets. Stop and record `descent_stopped` when no sample
grounds the atom (`not-ground`), when (predicate, canonical row) is already on
the path (`cycle`), or at depth 8 (`depth`). A descent that returns `derived`
is an internal defect (production said the parent's body row is absent) and
raises `WhyNotInternalError`. (p2-O)

Depth precedence: the depth-8 stop is recorded, not raised. `proof_depth`
(default 128) can only breach when a caller lowers it below 8; then the breach
raises `WhyNotWorkError` before the depth-8 stop is reached. T12 uses
`proof_depth=3` for that case. (p2-O)

### 6.6 The independent oracle (tests only)

`tests/why_not_oracle.py`: (p1-D, p2-M, p2-Q)

- imports nothing from `gnd.extensions`, `gnd.terms`, `gnd.values`,
  `gnd.checker` or `gnd.witness`; an AST import test enforces the ban; it reads
  the model document and population as plain JSON;
- owns its identity table: booleans are a domain apart from numbers; integers and
  floats compare by exact numeric value; strings compare as strings;
- computes every derived predicate, the target included, by naive fixpoint over
  its own rows, so it decides derivability independently;
- supports comparisons with literal operators over variables and constants only;
  corpus rules use no function terms (those are covered by T1, T5 and T7
  against production);
- returns derivability, the full step list and the blocker record, samples
  included.

Corpus: hand-built discriminators, each a named case, plus 200 generated cases
from seeds 0..199 (`random.Random(seed)`), each with at most 4 atoms and 12 rows
per relation. Named discriminators, each with the property the census asserts:

| Discriminator | Census asserts |
|---|---|
| `1` and `1.0` in a Number column; an exact duplicate row | candidate count exceeds the distinct-binding count |
| a Boolean column joined with a Number column of `1`s through one variable | the join is empty although Python `True == 1` |
| atoms 1 and 2 disconnected, atom 3 bridging them | the declared order differs from the order `_joined_bindings` chooses (computed once by the census test, which may import production; the oracle may not) |
| a constant in an atom; a variable repeated within an atom; a variable shared across atoms | each appears in the rule as stated |
| negation that removes all bindings; a comparison that removes all bindings | the blocker kind is `negated` / `comparison` |
| two clauses with different blockers | the two blocker indexes differ |
| a derived body predicate; a recursive one | the oracle's fixpoint needs more than one round |

r2's `True`/`1`/`"1"` single-column case is withdrawn: population validation
refuses mixed primitives in one column. (p2-Q)

### 6.7 Budgets and the charge-only trace (WN-D6)

`WhyNotLimits`: the `WitnessLimits` fields and defaults, plus
`pre_joins: int = 200000` and `probes: int = 200000`; validation refuses raising
any default. The service projects it onto a `WitnessLimits` for input loading,
because `witness.types.checked_limits` accepts only that class. (p2-L, p2-R)

- **Pre-evaluation.** The kernel sets `checker._WITNESS_TRACE` to a
  `_ChargeOnlyTrace` whose `charge(n)` adds to `pre_joins` and whose `row(...)`
  does nothing, for the pre-evaluation only, then resets the token. Production
  charges bindings at `extensions.py:404`, `:737`, `:763` and `:872`; nothing else
  in the pre-evaluation is charged.
- **Walk.** Each binding stored charges 1 to `joins` and its cell count to
  `binding_cells`. Each candidate row scanned charges 1 to `probes`, and each
  hash-index lookup charges 1 to `probes`.
- **Descent depth:** §6.5.

A breach raises `WhyNotWorkError` with `work` holding all four counters; tests
read it there. Setting the trace also disables incremental-context reuse and the
scope cache for that evaluation (`extensions.py:1026`, `:1441`), as it does for
`witness`; this costs time, not results.

### 6.8 Module, layering and query policy

- `src/gnd/witness/why_not.py`, about 450 source lines.
- `tools/gnd_layers.json`: `"gnd.witness.why_not": {"lane": "witness", "layer":
  "lanes"}`.
- Model reads use only `ModelIndex.fact_type(id)`,
  `ModelIndex.iter_fact_types_shared()`, `witness.io.roster(model)`,
  `relation.roles` and `checker._relation_facts`. Never `.fact_types`, and never a
  `"roles"` or `"fact_types"` subscript or `.get`, whatever the receiver: the RF6
  scanner counts them all. The allow-list gains no row (T16). (p2-R)
- No change to `extensions.py`. If the walk needs a private helper not already
  re-exported by `gnd.checker`, the spec is amended (append-only) rather than the
  helper copied.

## 7. Decisions

| ID | Question | Readings and cost |
|---|---|---|
| D1 (=WN-D2) | Declared-order prefixes vs evaluator order | Declared order can enumerate a product production avoided, so the walk budget breaches sooner on bridged bodies; evaluator order names a different "first" atom on disconnected bodies. Different blockers, same exit code. (p2-L) |
| D2 (=WN-D3) | Descent | (a) none: the host asks per level; (b) ground-only over structured-rule predicates: extra work bounded by depth 8, a partially bound blocker stops at `not-ground`; (c) partially bound descent: a new pattern mode. Proposed (b) under the owner's direction; confirmed at the gate. (p2-S) |
| D3 (=WN-D6) | Limits class | A sibling `WhyNotLimits` with `pre_joins` and `probes`, projected onto `WitnessLimits`; or widening `WitnessLimits`, which changes a class witness validates by iterating its fields. |
| D4 (=WN-D7) | Module home | `gnd.witness.why_not` in the witness lane, or a new lane. |
| D5 (=WN-D9) | Sample count | 5 proposed; payload size only. |
| D6 | Semiderived blockers | Proposed: production's extension decides. `check` reports no unsound surplus for semiderived types (`extensions.py:2496`), and dependent rules never read asserted semiderived rows, so a blocker over such a row is reported with `asserted_not_read: true` and descent explains why the rule does not derive it. Alternative: treat asserted semiderived rows as present, which would disagree with production. (p2-P) |
| D7 (=WN-D10) | Approval instrument for WN1 | Prose: the kernel's records are internal; WN2 fixes the wire form corpus-first. |
| D8 (=WN-D14) | Validation order | §4 rule 3: malformed row before unsupported fragment, as `witness`; or the reverse. |

## 8. Tests

All in `tests/test_why_not_kernel.py` unless named; each asserts exact values.

| ID | Case | Expected |
|---|---|---|
| T1 | status first: target unavailable through (a) its own comparison, (b) a computed head term, (c) a non-integral head, (d) a positive dependency, (e) a negated dependency; a two-clause rule where one clause derives and the other has an unavailable comparison | `unavailable` with production's reason and `source_relation`; never `derived` or `blocked` |
| T2 | two-atom rule, second atom has no match | `blocked`, counts `[n, 0]`, blocker atom index 1, `steps_after_blocker` set |
| T3 | first atom empty; a constant in an atom filters everything | blocker index 0; constant role shown as `{"constant": …}` |
| T4 | negated atom removes all bindings | blocker kind `negated` |
| T5 | comparison removes all bindings | blocker kind `comparison` |
| T6 | two clauses blocked at atom 0 and atom 2 | two clause entries, each with its own blocker |
| T7 | row mode: derived row; underived row; `head-bind:variable`; `head-bind:constant`; computed head reaching 0 at `head`; rule mode with a computed head and an empty body atom | `derived`; `blocked`; each sub-branch named; `head` blocker; rule-mode blocker at the atom, no `head` step |
| T8 | agreement over every T1..T7, T9, T10 and T14 case. Map from the `check` derivation verdict for the target: `pass` or `fail` with the row (row mode) or any row (rule mode) in the production extension → `derived`; `pass` or `fail` otherwise → `blocked`; `unchecked` with a `term:` reason or `dependency-unavailable` → `unavailable`; `unchecked` with `opaque-value` or `derivation-rule-opaque` → `unsupported`; `unchecked` with `derivation-not-covered` → compared with the oracle only (why-not ignores `covers`). Any other variant, or an unmapped reason, fails the test. The oracle's derivability must also agree on every case it supports. | every case agrees with both |
| T8b | `WhyNotInternalError`: a monkeypatched production result whose extension omits a row the walk reaches; a monkeypatched descent that returns `derived` | each raises `WhyNotInternalError` |
| T9 | `tests/test_why_not_oracle.py`: the §6.6 corpus, census and AST import ban | every count and the full blocker record equal the oracle's; each discriminator's property holds; the oracle imports none of the banned modules |
| T10 | descent: blocker over a derived predicate with a grounding sample; over a recursive predicate with a different row at each level; a semiderived predicate whose absent row is asserted | nested result names the base predicate; recursion continues past the first level; `asserted_not_read: true` |
| T11 | descent stops: not ground; cycle on the same (predicate, row); depth 8; a string-rule predicate | each `descent_stopped` reason, the last `not-derived` with `derivation: base` |
| T12 | each ceiling separately with lowered limits: `pre_joins`, `joins`, `binding_cells`, `probes`, `proof_depth=3`; a budget exhausted inside descent | `WhyNotWorkError` in each case, with the breached counter at its limit + 1 |
| T13 | counters, literal values asserted from `WhyNotResult.work` or the raised error's `work`. Fixture shape: one-role atoms *a1*(x), *a2*(y) disconnected, *a3*(x, y) bridging them with **one** row, then an empty atom *a4*(x). Production joins *a1*–*a3* first and probes *a2* only through the bridge; the declared walk enumerates *a1* × *a2* at prefix 2. (a) |*a1*| = |*a2*| = 320: prefix 2 holds 102,400 bindings, so the walk breaches `joins` (100,000) with `joins` = 100,001 and `pre_joins` below 1,000. (b) The twin with 310 rows completes: walk prefix counts `[310, 96100, 1, 0]`, `joins` = 310 + 96,100 + 1 = 96,411. (c) A zero-output connected join: *b1*(x) with 5,000 rows and *b2*(x) with 300 rows sharing no value: walk `probes` = 5,300 rows scanned + 5,000 index lookups = 10,300, `joins` = 5,000; a nested-loop walk would scan 5,000 × 300 = 1,500,000 rows and breach `probes`. (d) A blow-up inside a derived body predicate breaches `pre_joins`. (e) Linear growth: the (b) shape at 155 rows gives `joins` = 155 + 24,025 + 1 = 24,181, and at 310 rows 96,411, as the prefix sum predicts. A secondary wall cap of 10 s. | exact values as stated; any implementation-level charging difference is recorded and the figures restated before the gate, per standing rule 6 |
| T14 | aggregate, opaque target rule, opaque value two strata upstream, an opaque claimed row of the target in `population.facts`, unknown and non-derived fact type, malformed row, a call with both a malformed row and an unsupported fragment | named reason or `WhyNotInputError`; the malformed row is reported first |
| T15 | parity: `tests/test_public_v71_witness_corpus.py`, `test_public_optional_value_witness.py`, `test_derivation_rule.py`, `test_derivation_covers.py`, `test_public_derivation_evaluation_complete.py`, `test_public_derivation_parity_local.py` | pass unmodified |
| T15b | `explain` inside an active witness trace | the outer trace's rows and charges are unchanged afterwards |
| T16 | `test_rf1_layering.py`, `test_rf4_peripheral.py`, `test_rf6_query_policy.py` | pass, zero allowances, no new query rows |
| T17 | anonymity test per WN-R8: committed digests of normalized forbidden tokens, every file added since `fb03739`, a negative control with a test-only digest | no match; the control is caught; the test never skips |

Branch walk: top statuses `derived`/`blocked`/`unavailable`/`unsupported` (T7,
T2, T1, T14); step kinds atom, negated, comparison, head, `head-bind:variable`,
`head-bind:constant` (T2..T7); descent and its four stop reasons, and the
`asserted_not_read` flag (T10, T11); both internal-defect raises (T8b); each
ceiling and the depth precedence (T12, T13). (p2-O)

Focused gate: `uv run pytest -q tests/test_why_not_kernel.py
tests/test_why_not_oracle.py tests/test_rf1_layering.py tests/test_rf4_peripheral.py
tests/test_rf6_query_policy.py tests/test_gnd_arch.py
tests/test_public_v71_witness_corpus.py tests/test_public_optional_value_witness.py
tests/test_derivation_rule.py tests/test_derivation_covers.py
tests/test_public_derivation_evaluation_complete.py
tests/test_public_derivation_parity_local.py`. (p2-R)

## 9. Out of scope for WN1

The CLI, API, schema, redacted view, docs and pins (WN2); the example (WN3);
any change to `check`, `witness` or `extensions.py` semantics; partially bound
descent.

## 10. Size

Estimate: about 450 source lines and about 850 test lines including the oracle,
corpus and census. Measured at record time.

## 11. Approval instrument

This prose (D7 = WN-D10, proposed): the kernel's records are internal and WN2
fixes the wire form corpus-first. T9's corpus is built at implementation from
the named discriminators and fixed seeds.
