# The ILP bridge

The bridge lets an inductive logic programming (ILP) learner propose rules from
populations you have labelled, and brings the rules back as **reviewable,
advisory** model constraints. It has two halves:

- `gnd export ilp` writes the learner's input;
- `gnd import ilp-rules` checks the learner's output and turns it into a
  `gnd evolve` proposal.

GND never runs a learner itself. The bridge is **tool-neutral**: one export form
and one import contract, with a small adapter per learner. The first adapter is
[Popper](https://github.com/logic-and-learning-lab/Popper).

This page is the one home of the bridge's contract, including the fragment
table. The four wire formats are the packaged closed schemas
`ilp.schema.json`, `ilp-clauses.schema.json`, `ilp-run.schema.json` and
`ilp-import.schema.json`.

## The workflow

```
gnd export ilp MODEL --labels MANIFEST --target popper --out DIR
#   ... run the learner on DIR/popper/, record what each learned clause covers ...
gnd import ilp-rules MODEL CLAUSES --labels MANIFEST --reported-coverage RUN \
    --target popper --out PROPOSAL [--actor ID] [--requested-at TIME] [--format text|json]
gnd evolve preview MODEL PROPOSAL --workspace . --records records --out preview.json
```

**Examples are populations.** The manifest is a **class-mode** label manifest
(see [Measuring host labels](measure-labels.md)). Each of its populations is one
example, named by its `id`. The learned predicate is `wrong/1`, and it should
cover the `negative` populations:
- `negative` populations are Popper's positive examples (`pos`);
- `positive` populations are its negative examples (`neg`).

The manifest's `rules` entry is still required and still bound to the model, but
the bridge does not use it.

## Export

The command creates `DIR`, which must not exist, and writes these files:

| File | What it holds |
|---|---|
| `neutral.json` | the learner-neutral form, `gnd-ilp/1` |
| `popper/bk.pl` | one background fact per population fact, with the example id as its first argument, then the comparison definitions |
| `popper/exs.pl` | `pos(wrong('<id>')).` or `neg(wrong('<id>')).` per population, in manifest order |
| `popper/bias.pl` | the modes: `head_pred(wrong,1)`, one `body_pred`/`type` pair per predicate, `magic_value_type` for integer types, and fixed `max_vars(6)`, `max_body(5)` and `max_clauses(4)` |
| `export.json` | `gnd-ilp-export/1`: the target, the adapter version, and each other file's path, SHA-256 and size |

With `--target neutral`, only `neutral.json` and `export.json` are written.

**The export digest E** is the SHA-256 of `export.json`. The command prints it,
and `sha256sum DIR/export.json` reproduces it. Two exports of the same inputs
are byte-identical.

**Modes come from fact-type roles:**
- **Predicates:** each asserted fact type `ft` becomes the predicate `f_ft`. Its
  first argument is the example (type `ex`), followed by one argument per role
  in declared order.
- **Types:** each object type `ot` becomes the type `t_ot`.
- **Comparisons:** each integer-typed type gets four comparison predicates:
  `ge_`, `gt_`, `le_` and `lt_`.
- **Values:** written in the checker's typed identity. Integers are bare, and
  strings and example ids are quoted atoms. Booleans are `true` and `false`.
- **Derived and semiderived fact types:** not exported, and listed under
  `skipped`.

**Refused at export (exit 3), by name:**
- `expected-state`: an expected-state manifest, which has no classes;
- `opaque` or `unrepresentable`: a population cell the export cannot render;
- `redacted`: a role the model redacts, because the export would write its raw
  values;
- `primitive`: a value type other than Integer, String or Boolean;
- `name`: an id longer than the export's name bound;
- `too-large`: more than 1,000,000 facts, or a file over 64 MiB;
- `references`: a model with declared reference populations.

## Import

CLAUSES is either Popper's printed program (`--target popper`) or the neutral
clause form `gnd-ilp-clauses/1` (`--target neutral`). The run record
(`gnd-ilp-run/1`) is what the learner run claims:

```json
{"schema_version": "gnd-ilp-run/1",
 "learner": {"name": "popper", "version": "<version>"},
 "export_sha256": "<E>", "clauses_sha256": "<sha256 of the CLAUSES file>",
 "coverage": [{"clause": 0, "covered": ["n1", "n2"]}]}
```

Popper prints counts, not sets. You compute `covered` yourself, for example by
running each learned clause over `bk.pl` and `exs.pl` in Prolog.

**The import refuses (exit 3) unless every check passes**, and then it writes
nothing. Admission is all-or-nothing.

1. **Binding:**
   - `clauses-mismatch`: the run record's `clauses_sha256` is not the CLAUSES
     digest;
   - `export-mismatch`: its `export_sha256` is not E, which GND recomputes from
     MODEL, MANIFEST and `--target`;
   - `learner-mismatch`: a Popper import's learner is not `popper`;
   - `coverage-shape`: `coverage` does not list every clause exactly once.
2. **The fragment:** each clause is checked in the order of the table below.
3. **Re-evaluation:** GND adds every rewritten constraint to the model, runs the
   checker once per population, and reads each new constraint's verdict:
   - `warning` means covered;
   - `pass` means not covered;
   - `vacuous` and `unchecked` mean not covered, and are listed separately.
4. **Set comparison, per clause:**
   - `unknown-example`: a reported id is not in the manifest;
   - `coverage-mismatch`: the set GND covers differs from the reported set.
     Equal counts are not enough.
   - `covers-nothing`: the clause covers no example at all.

Agreement is **necessary, not sufficient**. Two rules that cover the same
examples can still disagree on populations neither has seen.

## The fragment table

Each learned clause `wrong(X) :- B1, …, Bn` is checked in this order. The first
failing check refuses the clause with the name shown, as `clause <k>: <name>`.

| # | Check | Refusal |
|---|---|---|
| 1 | the head is `wrong` with exactly one variable X | `head-shape` |
| 2 | every body literal is an atom or a comparison | `negation-as-failure` (`\+`, `not`), `disjunction` (`;`), `aggregate` (`findall`, `aggregate_all`, `count`, …) |
| 3 | every atom names an exported predicate with its arity; `wrong` is not in the body | `unknown-predicate`, `arity`, `recursion` |
| 4 | every atom's first argument is X, and X occurs nowhere else | `example-variable` |
| 5 | at most one comparison, with a variable operand, over an integer type | `multiple-comparisons`, `comparison-type` |
| 6 | **designation:** the comparison if there is one, otherwise the last atom whose variables all occur in the other atoms | `non-ground-absence` |
| 7 | the remaining atoms (the antecedent) are non-empty and joined by shared variables | `empty-antecedent`, `disconnected-body` |
| 8 | every variable of the designated literal occurs in the antecedent | `non-ground-absence`, `unbound-comparison` |
| 9 | no string constant starts with `$`, which a guarded bind reads as a variable | `constant-spelling` |
| 10 | the model plus the constraint validates | `invalid-guarded`, with the validator's rule ids |

A comparison predicate the export declared, such as `gt_t_amount(C,100)`, counts
as a comparison, whichever form wrote it. Popper text that is outside the
parser's grammar is `unparsable`, with its line and column.

**The rewrite (body rewriting):**
- X is dropped from every atom.
- Each remaining atom becomes a guarded antecedent item `{fact_type, bind}`.
- The designated literal moves into the consequent, negated:
  - a comparison `L op R` becomes `comparison` with the opposite operator (`>`
    and `<=`, `<` and `>=`, `=` and `!=`);
  - an atom becomes `absence`.
- A Prolog variable `V` is spelled `$v_` plus an injective encoding: upper case
  becomes lower case, a lower-case letter gains a leading `_`, and `_` doubles.
  So `B` becomes `$v_b`. Each anonymous `_` becomes a fresh `$anon<k>`.
- At a boolean-typed role, the atoms `true` and `false` become booleans.

Each constraint is top-level `guarded`, with `source: induced`,
`status: proposed` and `modality: deontic`. It is never a `derivation_rule`. Its
`provenance.induction` block is computed by GND:

| Field | Value |
|---|---|
| `inducer` | the run record's learner |
| `method` | `ilp-popper` or `ilp-neutral` |
| `examples` | the covered `negative` ids, the first 256 in manifest order |
| `counterexamples` | the covered `positive` ids, the first 32 |
| `support` | covered negatives over all covered examples |
| `evidence` | E, the CLAUSES digest and the run-record digest, under the refs `ilp/export.json`, `ilp/clauses` and `ilp/run` |

**How GND's meaning differs from the learner's:**

| Construct | Learner | GND `guarded` | Consequence |
|---|---|---|---|
| a body true for some binding | covers the example | a violating binding gives `warning` | covered means `warning` |
| an empty antecedent fact type | the body is false | `vacuous` | not covered, listed separately |
| a populated antecedent with no join | not covered | `pass` with `bindings=0` | not covered |
| a disconnected body | a cross product | `unchecked` (`join-disconnected`) | refused at check 7 |
| an absent fact | closed world in `bk.pl` | closed world over the population | they agree on exported facts; derived facts are not exported and are refused at check 3 |
| a comparison | Prolog arithmetic | typed comparison; an unordered pair gives `unchecked` | integers only (check 5) |
| a constant | an atom or an integer | a typed literal, matched by identity | `'7'` (atom) and `7` (integer) differ on both sides |

## Bounds

| Item | Bound |
|---|---|
| exported facts | at most 1,000,000 |
| each written file | at most 64 MiB |
| CLAUSES | at most 1 MiB; 1 to 32 clauses; 1 to 16 body literals; `not`/`or`/`aggregate` nesting at most 4 |
| run record | at most 32 MiB |
| work | export: populations + facts, at most populations + 1,000,000; import: checker runs + verdict reads, at most P × (1 + K) |

## Exits

| Exit | Meaning |
|---|---|
| 0 | the export or the proposal was written |
| 3 | a named refusal (above) or invalid input |
| 5 | a population failed to load |
| 11 | `--out` already exists; nothing was written |
| 64 | usage |
| 66 | a missing input |
| 70 | an internal defect (for example, a deontic constraint that drew `fail`) |
| 74 | a refused path or symbolic link |

## What the bridge does not establish

- That a learner accepts the rendering. The Popper rendering has not been run
  against a real Popper in this repository.
- That learned rules are true. Coverage agreement on the labelled examples is
  necessary, not sufficient. Admission is your reviewed `gnd evolve` step.
