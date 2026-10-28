# The ILP bridge

The bridge lets an inductive logic programming (ILP) learner propose rules from
populations you have labelled, and brings the rules back as **reviewable,
advisory** model constraints. It has two halves:

- `gnd export ilp` writes the learner's input;
- `gnd import ilp-rules` checks the learner's output and turns it into a
  `gnd evolve` proposal.

GND never runs a learner itself. The bridge is **tool-neutral**: one export form
and one import contract, with a small adapter per learner. The first adapter is
[Popper](https://github.com/logic-and-learning-lab/Popper). To see the bridge
end to end, including a refused over-claim,
[find the rule your auditors are really using](../tutorials/learn-rules.md).

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
| `popper/bk.pl` | one background fact per population fact, with the example id as its first argument, grouped by predicate; then each threshold predicate's facts |
| `popper/exs.pl` | `pos(wrong('<id>')).` or `neg(wrong('<id>')).` per population, in manifest order |
| `popper/bias.pl` | the modes: `head_pred(wrong,1)`, one `body_pred`/`type` pair per predicate and per threshold predicate, and fixed `max_vars(6)`, `max_body(5)` and `max_clauses(4)` |
| `ilasp/task.las` | with `--target ilasp`: one ILASP learning task (see [ILASP adapter](#ilasp-adapter)) |
| `rules/features.json` | with `--target rules`: the feature table, `gnd-ilp-features/1` (see [Boolean rule sets](#boolean-rule-sets)) |
| `export.json` | `gnd-ilp-export/1`: the target, the adapter version, and each other file's path, SHA-256 and size |

With `--target neutral`, only `neutral.json` and `export.json` are written.

**Threshold predicates (Popper adapter version 3).** Popper v5.0.1 has no way
to supply a constant, so each comparison against an observed value is its own
one-argument predicate. It is written as ground facts: the observed values of
its type that the comparison holds for. Popper analyses `bk.pl` in an ASP
solver and calls predicates with unbound arguments, and both need facts:

```prolog
gt_t_amount__120(150).
gt_t_amount__120(200).
lt_t_amount__m5(-10).
```

- **Operators:** `gt` and `lt`.
- **Values:** the distinct observed values of each integer type. Above 32
  values, 32 are taken at evenly spaced ranks, always including the minimum
  and the maximum. A threshold that holds for no observed value (`gt` at the
  maximum, `lt` at the minimum) is not written.
- **Reading back:** the parser reads `gt_t_amount__120(V)` as the declared
  comparison `gt_t_amount(V, 120)`; `ge` and `le` names are read too. A
  negative value is spelled `m`, and the value follows the last `__`.

The `popper` target's `export.json` says `"adapter_version": "3"`; the
`neutral` target's says `"1"`.

**Adapters.** Each `--target` is one entry of the bridge's learner registry
(`gnd.export.ilp_learners`):
- its rendering, if any;
- its parser, if any;
- the learner name its run records must carry;
- the `method` token written into each admitted rule's
  `provenance.induction` (`ilp-<target>`).

Today the entries are `popper` and `neutral`.

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
- `too-large`: more than 500,000 facts, or a file over 64 MiB, whichever comes
  first (wide facts reach the file cap sooner);
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
   - `learner-mismatch`: the run record names a learner other than the
     adapter's (`popper` for a Popper import). A neutral import accepts any
     learner name; its rules carry `method: ilp-neutral`;
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
| 9b | no variable joins object types that share no ancestor. A variable's sites are the atom positions it holds and the declared type of a comparison predicate it is an operand of (`gt_t_amount(C,100)` makes C an `amount`); every pair must share an ancestor, as `semantic:op-term-type-compat` requires. Each `_` is its own variable | `type-confused-join` |
| 10 | the model plus the constraint validates | `invalid-guarded`, with the validator's rule ids |

A comparison predicate the export declared, such as `gt_t_amount(C,100)`, counts
as a comparison, whichever form wrote it. Popper text that is outside the
parser's grammar is `unparsable`, with its line and column.

**Quoted atoms in Popper text.** The parser reads the escapes SWI-Prolog
writes:
- `\\` and `\'`;
- `\n` and `\t`, and `\a`, `\b`, `\v`, `\f` and `\r`;
- a hexadecimal code point, `\x41\`;
- an octal code point of 1 to 7 digits, `\101\`.

An octal escape without its closing backslash, with more than 7 digits, or
outside Unicode scalar values is `unparsable`, with a message naming the octal
escape. SWI itself also reads an octal escape without its closing backslash;
GND reads only what SWI writes.

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

## ILASP adapter

`--target ilasp` writes one ILASP learning task, `ilasp/task.las`, and
`gnd import ilp-rules --target ilasp` reads the hypothesis ILASP prints. The
run record's learner must be `ilasp`, and the method token is `ilp-ilasp`.

**The task, in order:**

- **Background:** the comparison definitions only. For each integer type with
  observed values, one `dom_t(V)` rule per predicate argument of that type,
  one `thr_t(c).` fact per threshold, and one rule per comparison:
  `gt_t_amount(X, C) :- dom_t_amount(X), thr_t_amount(C), X > C.` The
  thresholds are the Popper adapter's selection (at most 32), and the
  operators are `gt` and `lt`.
- **Constants:** `#constant(t, c).` per threshold.
- **Mode bias:** `#modeh(wrong).`; `#modeb(2, p(var(t1), …))` per exported
  predicate, without the example argument; `#modeb(1, gt_t(var(t), const(t)))`
  per comparison; `#maxv(4).`
- **Examples:** `#pos(e<i>, {wrong}, {}, {…}).` or `#neg(…)` per population,
  where i is the 1-based position in `neutral.json`. The context holds that
  population's facts without the example argument, grouped by predicate.

**The reader** maps `wrong :- body.` to `wrong(X) :- body'`: every body atom
except a comparison takes `X` as its first argument, where `X` is the first of
`X`, `X0`, `X1`, … the rule does not use. `not` and aggregates are carried, so
the fragment table refuses them by its own names. The reader refuses, with
exit 3 and `clause K: <name>`:

| Construct | Example | Refusal |
|---|---|---|
| a constraint | `:- p(V1).` | `asp-constraint` |
| a choice rule | `{ wrong } :- p(V1).` | `choice-rule` |
| a weak constraint | `:~ p(V1). [1@1]` | `weak-constraint` |
| classical negation | `-p(V1)` | `classical-negation` |
| an arithmetic term | `p(V1+1)`, `p(-V1)` | `arithmetic-term` |
| an interval or a pool | `p(1..3)`, `p(1;2)` | `interval-or-pool` |
| a directive | `#show wrong/0.` | `directive` |
| an infix comparison | `V2 > 500` | `builtin-comparison` |
| a rule without a body | `wrong.` | `empty-body` |
| a disjunctive head | `wrong \| p :- …` | `disjunction` |
| any head but bare `wrong` | `wrong(V1) :- …` | `head-shape` |

**Constants:**

| ASP term | Read as |
|---|---|
| `40`, `-3` | an integer |
| `"a\"b"` | a string; the escapes are `\\`, `\"` and `\n` |
| `true`, `false` | a boolean |

Any other bare name, such as `web`, is refused `unparsable`: clingo reads
`web` and `"web"` as different constants. On a boolean role a quoted
`"true"` or `"false"` is refused `constant-spelling`, because the export
writes booleans bare (IL2-D13).

The export refuses as `unrepresentable` an exported string with a control
character other than a newline, which has no ASP spelling, and an integer
outside clingo's 32-bit range, which clingo would wrap (IL2-D14).

**Read differently by clingo.** The reader refuses these with exit 3
`unparsable` and a line and column, because clingo would read them otherwise:

- an integer outside clingo's 32-bit range, or one with a leading zero;
- a bare name other than `true` or `false` (above);
- an identifier that starts with underscores and then a lowercase letter
  (`_cash`, a constant to clingo), or one with a prime (`V'`);
- a block comment, `%* … *%`;
- a `ge_` or `le_` comparison, which the task never defines, and a `gt_` or
  `lt_` comparison whose arguments are not a variable and then an integer.

The hypothesis is every non-blank line after ILASP's last `%%` line, whatever
its head, so a learned constraint reaches the reader and is refused
`asp-constraint`.

## LLM proposer

`gnd import ilp-rules --target llm` reads clauses that a language model wrote
as `gnd-ilp-clauses/1` JSON. No GND command calls a model: an evidence script
builds the prompt with `gnd.export.ilp_prompt`, runs an agent through
`gnd.agents`, and hands the import the answer and an independent run record.

- **`exports` is false:** `gnd export ilp --target llm` exits 64. The entry's
  `binds` is `neutral`, so the run record binds the export digest of
  `gnd export ilp --target neutral` over the same inputs. A run record that
  binds another target's export is refused `export-mismatch`.
- **The learner** must be an agent adapter id, `claude` or `codex`. Any other
  name is refused `learner-mismatch`. The method token is `ilp-llm`.
- **The answer** is read as any other JSON clauses file and goes through the
  same fragment table and coverage re-check. A malformed answer exits 3 at the
  clauses reader; a wrong claimed coverage is refused `coverage-mismatch`.

**The prompt (prompt version 1)** is a fixed instruction section, one data
section and a fixed trailer. The data section opens with the line
`=== DATA ===`, closes with the line `=== END DATA ===`, and holds, in order:

| Heading line | Lines under it |
|---|---|
| `-- Model --` | the model's constraint-blind verbalization, from `=== Object Types ===` on, with object-type descriptions |
| `-- Predicates --` | one JSON line per exported predicate: name, roles, types |
| `-- Comparisons --` | one JSON line per comparison: name, operator, type and the thresholds the Popper adapter selects |
| `-- Examples --` | one JSON line per example: id and label |
| `-- Facts --` | one JSON line per fact: example, predicate, values |

Fact values reach the prompt only as ASCII JSON, so they cannot start a line.
Model text reaches it through the verbalization's neutralizers, which keep each
name or reading on one line but leave its characters alone. So the prompt
builder refuses `forged-line` when a verbalization line, trimmed, equals one of
the prompt's own structural lines, starts with ```` ``` ````, or has the form
`model: ID`. That fixes the prompt's structure, not its meaning: a
sentence inside a value is still text the model reads. GND's re-check of every
clause is the control.

**The answer** is the text of the one block that opens with a line equal to
```` ```json ```` and closes with the next line equal to ```` ``` ````. No
block, two blocks, an unterminated block, or any other line starting with
```` ``` ```` outside the block is no answer. The first line of
the form `model: ID` is recorded as the agent's own claim, never verified.

## Boolean rule sets

`--target rules` serves propositional rule-set learners, which read a table
rather than relational facts. The run of record uses wittgenstein's RIPPER.

**The export** writes `rules/features.json`, `gnd-ilp-features/1`: one row per
example and one 0/1 column per feature.
- **A feature** is one integer argument position of an exported predicate,
  crossed with one of the threshold comparisons the Popper adapter selects
  (`gt_` and `lt_`, at up to 32 observed values). A cell is 1 when the example
  has a fact of that predicate whose value at that position passes the
  comparison.
- **Only thresholded features are exported.** A feature without a comparison
  would be a single atom, which the fragment table can only refuse.
- **Each column states its meaning:** predicate, position, arity, role, type,
  comparison, operator and threshold. Its name spells the same thing:
  `<predicate>__<position>__<arity>__<comparison>__<threshold>`, for example
  `f_refund_amount__2__3__gt_t_amount__500`, with the threshold written as
  Popper writes it (`m` for minus). The arity counts the example argument.
- **Bounds:** at most 4,096 features and 4,000,000 cells (rows × features).
  Beyond them the export is refused `too-many-features` or `too-large`; an
  export with no thresholded argument is refused `no-features`. A column
  whose name would exceed 160 characters, carry a threshold over 32 digits,
  or not read back as the same feature (an id that itself looks like a column
  name) is refused `column-name`, so the export never writes a name the
  import cannot read. The table's
  `work` field records the cells and the ceiling.

**The import** reads the learner's rule set as wittgenstein prints it, one
line with no trailing newline: `[[cond^cond] V [cond]]`, where a condition is a column name and a
value. Each rule is read by the polarity table, in this order:

| The rule | Spellings | Result |
|---|---|---|
| a rule list (`if … then … else …`) | a line starting with `if`, in any case, after any leading spaces | refused `ordered-rule-list` |
| no condition | `[True]` | refused `empty-antecedent` |
| a feature required false | `=0`, `=0.0`, `=False`, `<=0.5` | refused `negation-as-failure` |
| two or more features | `[a=1^b=1]` | refused `propositional-conjunction` |
| one feature required true | `=1`, `=1.0`, `=True`, `>0.5` | the feature's clause |

A true feature becomes the clause its name spells, with a fresh variable at
every position:

```
wrong(X) :- f_refund_amount(X, V1, V2), gt_t_amount(V2, 500).
```

The clauses then go through the fragment table and the coverage re-check like
any other target's, so a name whose comparison the export never declared is
refused there, and a comparison whose type differs from its position's is
refused `comparison-type`. Admission is all-or-nothing: one refused rule
refuses the set. Anything outside the grammar, an empty set `[]`, more than 32
rules, more than 16 conditions in a rule, a name over 160 characters, an
arity over 64 (an atom's argument cap) or a threshold over 32 digits is
refused `unparsable`.

The learner's own coverage of each rule, in rule order, is the run record's
coverage. The learner is named `wittgenstein`; the method token is
`ilp-rules`.

## Bounds

| Item | Bound |
|---|---|
| exported facts | at most 500,000 |
| each written file | at most 64 MiB |
| CLAUSES | at most 1 MiB; 1 to 32 clauses; 1 to 16 body literals; `not`/`or`/`aggregate` nesting at most 4 |
| run record | at most 32 MiB |
| work | export: populations + facts, at most populations + 500,000; import: checker runs + verdict reads + candidate reloads, at most P × (1 + K) + K + 2 |

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
