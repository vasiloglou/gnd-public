<!-- DC1 draft, 2026-11-01. Illustrative: written from the approved plan r3
before any code exists. Not committed to docs/. This is the new section of
docs/reference/why-not.md, placed after "The blocker". Payloads are
illustrative; DC2 replaces them with real output. -->

## Values spelled differently

A join can be empty for two reasons: the fact you need is missing, or it is
there but spelled differently. `ACME CORP.` and `Acme Corp.` are two values to
GND, so a blocker caused by either reads the same. To tell them apart, every
atom blocker reports *near-misses*: rows of its fact type that would have
joined if bound strings were compared after a fixed normalization.

Near-misses never change the answer. The status, the blocker, the counts, the
`work` counters and the exit are what exact matching gives. Whether two
spellings name one entity is your decision; why-not only points at the
candidates.

```json
{"kind": "atom", "index": 1, "fact_type": "party_to",
 "roles": {"party": {"variable": "$p", "bound": true},
           "case": {"variable": "$c", "bound": true}},
 "sample_count": 1,
 "samples": [{"party": "Acme Corp.", "case": "c-9"}],
 "near_miss_count": 1,
 "near_miss_truncated": false,
 "near_misses": [
   {"roles": ["party"],
    "sample": {"party": "Acme Corp.", "case": "c-9"},
    "candidate": {"party": "ACME CORP.", "case": "c-9"}}]}
```

*Illustrative.* This blocker says: the binding for `Acme Corp.` reached
`party_to` and found no row, but the population holds a row for `ACME CORP.` in
the same case. Fix the spelling on one side, or add the row with the spelling
the rule expects.

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
   removed.

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
roles is compared with the binding at each.

A binding and a candidate row form a **near-miss** when, at every bound role,
the two values are equal or have the same `N`, and at least one bound role
differs exactly. `roles` lists the bound roles that differ exactly.

### Count, list and order

- `near_miss_count` counts distinct (binding, row) pairs, each projected onto
  the bound roles. Rows or bindings that differ only at other roles count once.
- `near_misses` lists up to five pairs, ordered by the canonical encoding of
  `sample`, then of `candidate`. `sample` and `candidate` are projected onto
  the bound roles. Values that are one value to GND (`1` and `1.0`) are shown in
  their smallest canonical form.
- Near-misses appear on positive atom blockers at every descent level, not on
  `negated`, `comparison` or `head` blockers.

### Limits

The search looks at every row of the fact type and every binding once, and
builds at most 25 pairs for each normalized value. It has its own ceiling of
200,000 inspections, separate from the walk's budgets, so it can never cause a
`work-limit` exit. If the ceiling is reached, `near_miss_truncated` is true,
`near_miss_count` is a lower bound and the list holds what was found. With the
default limits the ceiling cannot be reached, because the walk's own probes
already cover every row and binding the search inspects.

### Values in the answer

In the redacted view, `near_miss_count` and `near_miss_truncated` are shown and
`near_misses` reads `"redacted"`. The [disclosure mode](disclosure.md) decides
which view you get: under `customer`, `api.why_not` also returns the redacted
view and `--raw` is refused.

The count is shown even when the values are not. A caller who supplies a `--row`
therefore learns whether a value spelled like theirs exists;
[disclosure](disclosure.md#who-customer-mode-protects) explains why that is
accepted.

<!-- Also in this page at NM3: the schema id becomes gnd-why-not/2, with a
migration line in the release notes. -->
