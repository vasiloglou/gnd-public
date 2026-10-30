# Why a derived fact is missing

A derivation rule derives nothing, or derives rows but not the one you
expected. `gnd why-not` reports where each of the rule's clauses runs out of
bindings, how many bindings each earlier step had, and which values reached the
step that emptied them. An application or an agent can then add the missing
fact, or report which fact is missing.

`gnd witness` is the companion command for the other case: it proves a derived
row that is present.

## Ask the question

```text
gnd why-not MODEL POPULATION --fact-type ID [--row REQUEST] [--reference-root DIR] [--raw]
```

```python
gnd.api.why_not(model_path, population_path, fact_type, *, row_path=None,
                reference_root=None) -> dict
```

Without `--row`, the question is about the rule as a whole: why does
`fact-type` have no rows? With `--row`, it is about one claimed row: why is
this row absent? The row file uses the [witness request format](python-api.md#witness-explain-one-derived-fact-with-a-finite-proof)
and holds exactly one target, whose `fact_type` must equal `--fact-type`.

The fact type must be derived or semiderived with a structured rule. Reference
populations bind as they do for `check` and `witness`.

## Read the answer

GND's own evaluator decides first. The answer's `status` is one of:

| `status` | Exit | Meaning |
|---|---|---|
| `derived` | 0 | The evaluator derives the row, or (rule mode) at least one row. |
| `blocked` | 0 | The evaluator derives nothing that answers the question; `clauses` says where each clause stops. |
| `unsupported` | 2 | The rule uses something why-not does not explain: `aggregate`, a prose rule (`rule-opaque`), or an opaque value in a fact type the rule depends on (`opaque-value`). |
| `refused` | 3 | The input is invalid (`reason: input-invalid`). |
| `unavailable` | 4 | A term could not be evaluated, for example a division by zero; `reason` names it. |
| `refused` | 4 | A work limit was reached (`reason: work-limit`); `work` holds the counters. |

A `blocked` or `derived` answer exits 0 because both answer the question; read
`status`. Exit 4 means the answer is indeterminate, as it is for `check`.

## Steps and the blocking step

This section is the normative definition.

For each clause of the rule, in the order the model declares them, why-not
walks the clause's parts in declared order, not in the order GND's evaluator
joins them. The answer says so with `"order": "declared"`.

1. **Seed.** In rule mode the walk starts from one empty binding. In row mode
   each head variable is bound to the claimed row's value. If a head variable
   appears at two roles with different claimed values, the step
   `head-bind:variable` has count 0. If a constant head term differs from the
   claimed value, the step `head-bind:constant` has count 0. Computed head
   terms are not bound here.
2. **Positive atoms**, in declared order. Each step joins the bindings so far
   with the atom's rows, on the variables they share. An atom that shares no
   variable makes a product. The step's `count` is the number of distinct
   bindings after it.
3. **Negated atoms**, in order. Each removes the bindings whose ground row is
   present.
4. **Comparisons**, the rule's root comparisons before the clause's own. Each
   keeps the bindings for which the comparison holds.
5. **Head**, row mode only. Each binding's head terms are evaluated, and the
   bindings that produce the claimed row are kept.

The **blocking step** is the first step whose count is 0. Later steps are not
computed, and the clause says `"steps_after_blocker": "not-evaluated"`.

Counts are of distinct bindings over the variables bound so far, under GND's
value identity: `1` and `1.0` are one value; `true` and `1` are two.

## The blocker

```json
{"kind": "atom", "index": 1, "fact_type": "wrote", "derivation": "base",
 "ground": false, "asserted_not_read": false,
 "roles": {"work": {"variable": "$w", "bound": true},
           "person": {"variable": "$p", "bound": false}},
 "sample_count": 2,
 "samples": [{"work": "w1"}, {"work": "w2"}]}
```

- `roles` covers every role of the atom. A role holds a variable, with whether
  an earlier step bound it, or a constant.
- `ground` is true when every role is a constant or a bound variable.
- `sample_count` is the number of bindings that reached the blocker.
- `samples` holds up to five of them, keyed by role and projected onto the
  bound roles, in a fixed order.
- `derivation` is `base` for a fact type with asserted rows only, including one
  with a prose rule. Otherwise it is `derived` or `semiderived`.

So the blocker above says: two listed works reached `wrote`, and neither has an
author. Adding `wrote(w1, someone)` would unblock the clause for `w1`.

For a `negated`, `comparison` or `head` blocker, `reads` lists the bound
variables the step reads, and `samples` are keyed by variable.

## Descent into a derived blocker

When the blocker is an atom over a derived or semiderived fact type with a
structured rule, and a sample binds every role, why-not explains that row in
turn: the first such sample, as a claimed row. The answer nests under the
clause's `descent`. Descent stops, and `descent_stopped` says why, when:

- the blocker's fact type is base (`not-derived`);
- no sample binds every role (`not-ground`). Ask again with `--row` to choose
  the row;
- the same fact type and row are already being explained (`cycle`);
- eight levels have been explained (`depth`).

## Semiderived fact types and `covers`

A semiderived fact type's asserted rows are never read by the rules that
depend on it. When a blocker's absent row is asserted in the population, the
blocker says `"asserted_not_read": true`. The fix is to make the rule derive the
row, not to assert it again.

Why-not ignores a population's `covers` list. Derivation never reads a derived
type's asserted rows, whatever `covers` says. So a target that `check` reports
as not covered is explained like any other.

## Values in the answer

The Python API returns raw values, like `api.witness`. The CLI prints a
redacted view by default: `samples`, constant roles and an unavailable term's
binding read `"redacted"`, and the answer carries `"view": "redacted"`. Pass
`--raw` to print the values, with `"view": "raw"`. Use the raw view only where
those values are appropriate for the reader.

## Limits

Inputs have the witness lane's ceilings: 10 MiB per file, nesting depth 64,
4,096 bytes per string, and 128 digits per number. Work has two budgets.
GND's evaluator may perform 200,000 joins while deciding the status. The
walk may make 100,000 joins and 200,000 probes and hold 400,000 binding cells.
Reaching any of them returns `refused` with `reason: work-limit` and exit 4.

The output is described by `why-not.schema.json`, packaged with GND.
