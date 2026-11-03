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
 "samples": [{"work": "w1"}, {"work": "w2"}],
 "near_miss_count": 0, "near_miss_truncated": false, "near_misses": []}
```

- `roles` covers every role of the atom. A role holds a variable, with whether
  an earlier step bound it, or a constant.
- `ground` is true when every role is a constant or a bound variable.
- `sample_count` is the number of bindings that reached the blocker.
- `samples` holds up to five of them, keyed by role and projected onto the
  bound roles, in a fixed order.
- `derivation` is `base` for a fact type with asserted rows only, including one
  with a prose rule. Otherwise it is `derived` or `semiderived`.
- `near_miss_count`, `near_miss_truncated` and `near_misses` report rows that
  differ from a binding only in spelling; see
  [values spelled differently](#values-spelled-differently).

So the blocker above says: two listed works reached `wrote`, and neither has an
author. Adding `wrote(w1, someone)` would unblock the clause for `w1`.

For a `negated`, `comparison` or `head` blocker, `reads` lists the bound
variables the step reads, and `samples` are keyed by variable.

## Values spelled differently

A join can be empty for two reasons: the fact you need is missing, or it is
there but spelled differently. `FIELD NOTES` and `Field Notes` are two values
to GND, so a blocker caused by either reads the same. To tell them apart, every
atom blocker reports *near-misses*: rows of its fact type that would have
joined if bound strings were compared after a fixed normalization.

Near-misses never change the answer. The status, the blocker, the counts, the
`work` counters and the exit are what exact matching gives. Whether two
spellings name one entity is your decision; why-not only points at the
candidates.

This is the blocker for the claim `certified(q-17, Ada Byrne)` over the
packaged `quoted_claims` example's `spelling-gap.pop.json`, with `--raw`:

```json
{"kind": "atom", "index": 1, "fact_type": "authored", "derivation": "base",
 "ground": true, "asserted_not_read": false,
 "roles": {"work": {"variable": "$w", "bound": true},
           "person": {"variable": "$p", "bound": true}},
 "sample_count": 1,
 "samples": [{"work": "Field Notes", "person": "Ada Byrne"}],
 "near_miss_count": 1,
 "near_miss_truncated": false,
 "near_misses": [
   {"roles": ["work"],
    "sample": {"work": "Field Notes", "person": "Ada Byrne"},
    "candidate": {"work": "FIELD NOTES", "person": "Ada Byrne"}}]}
```

The binding for `Field Notes` reached `authored` and found no row, but the
population holds a row for `FIELD NOTES` by the same person. Fix the spelling
on one side, or add the row with the spelling the rule expects. The population
also holds `Field notes` by Bo Lin; it is not reported, because the other bound
role, `person`, differs.

An empty list with `near_miss_count: 0` means that why-not searched and found
nothing close: the fact is missing.

This section is the normative definition.

### The normalization

Near-misses compare strings by `N(v)`:

1. Unicode NFKC normalization;
2. case folding (`str.casefold`);
3. deletion of every character whose Unicode general category is punctuation
   (`P*`);
4. each run of whitespace becomes one space; leading and trailing spaces are
   removed. Whitespace is what Python's `str.split()` splits on: Unicode
   whitespace plus the separators U+001C to U+001F.

`N` is defined only for strings. Numbers, booleans and other values never
near-match, and neither does a string whose `N` is empty (`"..."`). `N` uses
the Unicode database of the Python running GND.

So `ACME CORP.` near-matches `Acme Corp.`, and `Straße` near-matches `STRASSE`.
Punctuation is deleted, not replaced: `ACME-CORP` near-matches `ACMECORP`, not
`ACME CORP`. `Acme . Corp` near-matches `Acme Corp`, and `℅` near-matches
`co`. There is no fuzzy, edit-distance or locale-dependent matching.

### Which rows are candidates

Let the blocker's *bound roles* be the roles whose variable an earlier step
bound. A blocker with no bound role has no near-misses.

A row of the blocker's fact type is a candidate when it has every role of the
atom, every constant role matches exactly, and a free variable that appears at
two roles has the same value at both. A bound variable that appears at two
roles is compared with the binding at each occurrence, so a candidate row may
spell it differently at different roles.

A binding and a candidate row form a **near-miss** when, at every bound role,
the two values are equal or have the same `N`, and at least one bound role
differs exactly. `roles` lists the bound roles that differ exactly.

### Count, list and order

- `near_miss_count` counts distinct (binding, row) pairs, each projected onto
  the bound roles. Rows or bindings that differ only at other roles count once.
- `near_misses` lists `min(5, near_miss_count)` pairs, ordered by the canonical
  encoding of `sample`, then of `candidate`. `sample` and `candidate` are
  projected onto the bound roles.
- Values that are one value to GND, such as `1` and `1.0`, are shown once.
  When separate bindings or rows differ only in such spellings, the pair shows
  the projection whose canonical encoding comes first. The whole projection is
  compared, not the number alone, so which spelling wins can depend on the
  other values and the role names; the choice is the same on every run. Within
  one binding, each value shows the spelling, among every row that met it,
  whose canonical encoding comes first (`1` before `1.0`), whatever the row
  order. This rule applies to `near_misses` only. `samples` keep the first value why-not met, so one
  blocker can show `1` in `samples` and `1.0` in `near_misses`.
- Near-misses appear on positive atom blockers at every descent level. The
  three fields are absent from `negated`, `comparison` and `head` blockers.

### Search limits

The search looks at every row of the fact type and every binding once, and
builds at most 25 pairs for each normalized value. It has its own ceiling of
200,000 inspections, separate from the walk's budgets, so it can never cause a
`work-limit` exit. One ceiling serves the whole request: every clause and
every descent level draws on it, so a lowered ceiling can truncate a later
blocker after an earlier one used it up. If the ceiling is reached,
`near_miss_truncated` is true,
`near_miss_count` is a lower bound and the list holds what was found. With the
default limits the ceiling cannot be reached and the flag is always false,
because the walk's own probes already cover every row and binding the search
inspects.

## Descent into a derived blocker

When the blocker is an atom over a derived or semiderived fact type with a
structured rule, and a sample binds every role, why-not explains that row in
turn: the first such sample, as a claimed row. The answer nests under the
clause's `descent`. Descent stops, and `descent_stopped` says why, when:

- the blocker's fact type is base (`not-derived`);
- no sample binds every role (`not-ground`). Ask again with `--row` to choose
  the row;
- the blocker's fact type is computed by an aggregate, which why-not does not
  walk (`aggregate`);
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

With no [disclosure mode](disclosure.md) set, the Python API returns raw
values, like `api.witness`, and the CLI prints a redacted view: `samples`,
constant roles and an unavailable term's binding read `"redacted"`, and the
answer carries `"view": "redacted"`. An atom blocker keeps
`near_miss_count` and `near_miss_truncated` and shows `near_misses` as
`"redacted"`. Pass `--raw` to print the values, with `"view": "raw"`.

Under `GND_DISCLOSURE=internal` both print the raw view. Under `customer`
both return the redacted view and `--raw` is refused with exit 3. The
near-miss counters stay visible in every mode; [who customer mode
protects](disclosure.md#who-customer-mode-protects) says what they reveal.

## Limits

Inputs have the witness lane's ceilings: 10 MiB per file, nesting depth 64,
4,096 bytes per string, and 128 digits per number. Work has two budgets.
GND's evaluator may perform 200,000 joins while deciding the status. The
walk may make 100,000 joins and 200,000 probes, and may store 400,000 binding
cells in total across all its steps, clauses and descent levels.
Reaching any of them returns `refused` with `reason: work-limit` and exit 4.
The near-miss search has its own ceiling of 200,000 inspections, which never
refuses a request (see [search limits](#search-limits)).

The output is described by `why-not.schema.json`, packaged with GND. Its
`schema_version` is `gnd-why-not/2`.
