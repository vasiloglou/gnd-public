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
`ilp-import.schema.json`. A rule miner, which needs no labels, has its own
command and schema: see [AMIE-style miner](#amie-style-miner).

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
| `amie/facts.tsv`, `amie/relations.json` | with `--target amie`, instead of every file above but `export.json`: the typed triples of one population (see [AMIE-style miner](#amie-style-miner)) |
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
- **Range:** Popper grounds `bk.pl` in clingo, so an integer outside clingo's
  32-bit range is refused `unrepresentable` at export, as for ILASP (IL2-D14).
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

CLAUSES is the program Popper logs: every `wrong(…).` line between its last
`********** SOLUTION **********` line and the closing line of 30 stars. The
block's other lines, such as its scores or a warning, are skipped, so no rule
is dropped.

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
2. **Thresholds:** `off-threshold`, as `clause K: off-threshold`: a threshold
   the learner could not have learned from the export.
   - **Popper:** a threshold atom of a declared comparison, `ge_` and `le_`
     included, that `bias.pl` does not declare, such as `gt_t_amount__501`
     when no observed amount is 501, or `gt` at the maximum. A binary
     comparison atom, the earlier spelling, is not checked here.
   - **ILASP:** a comparison constant the task does not offer for its type.
   - **Rules:** a column of a declared `gt` or `lt` comparison, at an
     integer position of its own type, that `features.json` does not hold.
     Any other column goes on to the fragment table.
   - **LLM and neutral:** not checked; any constant goes on to the fragment
     table.
3. **The fragment:** each clause is checked in the order of the table below.
4. **Re-evaluation:** GND adds every rewritten constraint to the model, runs the
   checker once per population, and reads each new constraint's verdict:
   - `warning` means covered;
   - `pass` means not covered;
   - `vacuous` and `unchecked` mean not covered, and are listed separately.
5. **Set comparison, per clause:**
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
| 9b | no variable joins object types that share no ancestor. A variable's sites are the atom positions it holds and the declared type of a comparison predicate it is an operand of (`gt_t_amount(C,100)` makes C an `amount`); every pair must share an ancestor, as `semantic:op-term-type-compat` requires. An infix comparison of two variables, `C > D`, joins them: each type of C must share an ancestor with each type of D. A variable compared with a constant joins nothing. Each `_` is its own variable | `type-confused-join` |
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
- The bare atoms `true` and `false` are booleans, as the export writes them;
  Popper quotes every string, so `'true'` is the string. At a boolean-typed
  role, the quoted `'true'` and `'false'` also become booleans.

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
The live run is in [Comparing the learners](#comparing-the-learners): ILASP 4.4.1 accepted the task, and GND refused
its hypothesis as `empty-antecedent`.

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

**Thresholds.** After the run record's checks and before the fragment table,
the import checks each comparison's constant against the thresholds the task
offers for its type, its `thr_t` facts. Any other constant, such as `501` when
no observed amount is 501, is refused `off-threshold`, as
`clause K: off-threshold`: ILASP could not have learned it from the export.

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
The live run (Claude Code) is in [Comparing the learners](#comparing-the-learners): one clause, admitted.

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
the prompt's own structural lines, starts with three backticks, or has the form
`model: ID`. That fixes the prompt's structure, not its meaning: a
sentence inside a value is still text the model reads. GND's re-check of every
clause is the control.

**The answer** is the text of the one block that opens with a line equal to
three backticks followed by `json` and closes with the next line equal to
three backticks. No block, two blocks, an unterminated block, or any other
line starting with three backticks outside the block is no answer. The first line of
the form `model: ID` is recorded as the agent's own claim, never verified.

## Boolean rule sets

`--target rules` serves propositional rule-set learners, which read a table
rather than relational facts. The run of record uses wittgenstein's RIPPER;
its rule was admitted with a measured support of 4 of 5, see [Comparing the learners](#comparing-the-learners).

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

A condition on a column the export could write but did not, such as
`f_refund_amount__2__3__gt_t_amount__451` when no observed amount is 451, is
refused `off-threshold`, as `clause K: off-threshold`: wittgenstein could not
have learned it from the export.

The clauses then go through the fragment table and the coverage re-check like
any other target's, so a name whose comparison the export never declared is
refused there, and a comparison at a position that is not an integer is
refused `comparison-type`. Admission is all-or-nothing: one refused rule
refuses the set. Anything outside the grammar, an empty set `[]`, more than 32
rules, more than 16 conditions in a rule, a name over 160 characters, an
arity over 64 (an atom's argument cap) or a threshold over 32 digits is
refused `unparsable`.

The learner's own coverage of each rule, in rule order, is the run record's
coverage. The learner is named `wittgenstein`; the method token is
`ilp-rules`.

## AMIE-style miner

`--target amie` serves rule miners such as
[AMIE](https://github.com/dig-team/AMIE), which look for regularities in one
population instead of learning a labelled target. The run of record uses
AMIE 4.0.0: GND refused it as `does-not-hold`, and a second, owner-approved
run with standard confidence 1 was admitted, see [Comparing the learners](#comparing-the-learners).

```
gnd export ilp MODEL --population POP --target amie --out DIR
#   ... run the miner on DIR/amie/facts.tsv, keep its rule lines ...
gnd import mined-rules MODEL RULES --population POP --reported RUN \
    --target amie --out PROPOSAL [--actor ID] [--requested-at TIME] [--format text|json]
```

**Which input.** `--target amie` takes `--population` and refuses `--labels`;
every other target takes `--labels` and refuses `--population`. A wrong pair
exits 64.

**The export** writes, beside `export.json`:
- `amie/facts.tsv`: one `subject TAB relation TAB object` line per distinct
  fact, sorted. Each binary asserted fact type the population `covers` is one
  relation, `f_<fact type id>`. Each value is spelled
  `<object type id>:<value>`, so the miner cannot join a refund number with an
  equal amount. A type in a subtype hierarchy is spelled by its **family**
  instead: the least top-type id, in code-point order, of the connected part of
  the subtype graph that holds it. So a `manager` that is a subtype of `staff`
  is spelled `staff:m1`, and a rule joining the two counts as the checker
  does. Only a subtype that inherits its supertype's reference joins its
  family; one with its own reference scheme starts a family of its own,
  because its values may be spelled like the supertype's and still differ, and
  the import refuses a rule that joins the two (see its table). A type that
  is a subtype of both still puts them in one family, and its values may be
  of either kind; the import refuses a variable over such types (see its
  table). A
  hierarchy with no top type, a cycle, is named by its least type id. Types of
  one family that share no ancestor are refused by the join check first. `export.json`'s `adapter_version` is `2`; a model without
  subtypes renders the same facts as version `1`. A tab, newline or backslash in a string is written `\t`,
  `\n` or `\\`; any other character that is not printable (a control
  character, a non-breaking or zero-width space) is refused `unrepresentable`.
- `amie/relations.json`: the population's SHA-256, each relation's fact type,
  roles, object types and fact count, and every skipped fact type with its
  reason: `derived`, `arity` (not binary) or `not-covered`.

A population that covers no binary asserted fact type is refused
`no-relations`. As for every target ([Export](#export)), an opaque value is
refused `opaque` and an export over the fact cap `too-large`. There are no
labels and no `neutral.json`.

**The import** reads RULES as AMIE prints them: one line per rule, eight
tab-separated fields: the rule, head coverage, standard confidence, PCA
confidence, Support, body size, PCA body size and the functional variable. The
rule is space-separated triples, `=>`, then one triple:
`?a  f_works_in  ?b  ?b  f_team_site  ?c   => ?a  f_based_at  ?c`. Support and
body size are counts; a body size of `-1` (AMIE computes it only with
`-enstd`) means not reported. The other figures are kept verbatim and never
compared. Anything else is refused `unparsable`: a line in another shape, an
empty file, a blank line, a rule printed twice (up to variable renaming and
body order), a variable other than `?a` to `?z`, more
than 256 rules, more than 4 atoms, a count over 18 digits, more than 1 MiB.

**The run record** (`gnd-mined-run/1` in `mined-import.schema.json`) names the
miner and binds RULES, the population and `amie/facts.tsv`, the facts the
miner read, by SHA-256:

```json
{"schema_version": "gnd-mined-run/1",
 "learner": {"name": "amie", "version": "4.0.0"},
 "rules_sha256": "<sha256 of RULES>", "population_sha256": "<sha256 of POP>",
 "facts_sha256": "<sha256 of DIR/amie/facts.tsv>"}
```

A different miner is refused `learner-mismatch`, other RULES
`rules-mismatch`, another population `population-mismatch`, compared on the
population's bytes before they are parsed. The import then
renders the facts again from MODEL and POP; facts other than the ones the
miner read are refused `facts-mismatch`, and so is a pair from which no export
can be written, naming the export's reason. The facts hold every relation name,
role order and spelled value, so a model that reads the population
differently, such as one with a fact type's roles swapped, is refused before
any rule is mapped. The record does not bind the export's version: version `2`
renders the facts of a model without subtypes byte for byte as `1` did. The
proposal binds the model it was built against.

**The mapping.** A rule `B1, …, Bn => r(x, y)` becomes one `guarded`
constraint whose antecedent is the body's atoms and whose consequent is the
`atom` `r(x, y)`, each variable `?v` written `$v`. These shapes are refused,
in this order:

| The rule | Result |
|---|---|
| a head relation outside the population's `covers` | refused `open-world-head`: a missing head fact is not evidence |
| a relation the export does not write (unknown, or outside `covers`) | refused `unknown-predicate` |
| a constant (AMIE prints one only with `-const`) | refused `constant-atom` |
| an atom whose two ends are one variable | refused `reflexive-atom` |
| the head relation also in the body | refused `recursion` |
| a head variable the body does not bind | refused `unbound-head` |
| body atoms that fall into parts sharing no variable | refused `disconnected-body`: the checker evaluates a connected antecedent only |
| a variable joining roles of incompatible object types | refused `type-confused-join`, by the fragment table's join check |
| a variable whose types span two families (a subtype that does not inherit its supertype's reference starts one), or whose types' references, taken together, resolve to more than one kind of value: text, number (Integer and Number) or boolean. A type under two references, such as a subtype of both an own-reference subtype and its supertype, may hold `1` and `"1"` | refused `own-reference-join`: the count spells such values apart or alike where the checker does not, so it cannot count them as the checker does |

**The counting.** GND counts every rule itself, over distinct head pairs:
- **the denominator** is the number of distinct `(x, y)` that some binding of
  the body reaches;
- **the numerator** is how many of those are facts of `r`;
- **the confidence** is numerator over denominator, reported with formula
  `std-confidence-head-pairs`.

The body's join is bounded before it runs: if the product of its relations'
sizes exceeds 1,000,000 rows the rule is refused `too-large`. Every rule is
counted before any is checked, so any rule's `too-large` comes first. Then,
rule by rule, in this order: a denominator of 0 is refused `covers-nothing`; a numerator that
differs from the miner's Support is refused `support-mismatch`; and a rule
that does not hold on every head pair is refused `does-not-hold`, because only
rules that hold are admitted. A body size that differs from the denominator is
recorded in the report (`body_size_agrees`), not refused. Admission is
all-or-nothing: one refused rule refuses the set.

**The proposal** carries, for each rule, the IK2 envelope `gnd discover`
writes: the inducer from the run record, method `ilp-amie`,
`manifest_sha256` the population's SHA-256, `examples` the opaque fact ids of
the satisfied head facts (the first 256), `support` the counts and no
`counterexamples`; evidence is the population, RULES and the run record. The
checker re-checks the candidate model before the proposal is written. The
report is `gnd-mined-import/1`, with `command` `import mined-rules`.

## Comparing the learners

Each adapter's learner was run during development, and each run's output is
kept as evidence. [Compare the rule learners on real runs](../how-to/compare-ilp-learners.md)
replays every imported output through `gnd`. The table is generated from that
evidence by `tools/ilp_comparison.py`; a test checks it against the committed
golden, so do not edit it by hand.

Columns: the outcome is the learner's termination and the import's result.
*Clauses proposed* is what the target's reader parses from the learner's
output; output the import refused at that reader has no count. *Not
evaluated* is the clauses after the first refusal, which the import never
reached; a refusal at a binding or the threshold check, before the first
clause, leaves every clause unevaluated. *Hold (GND's
count)* is how many mined rules GND counts as holding on every head pair. A dash means there was nothing to count.

<!-- ilp-comparison:start (generated by tools/ilp_comparison.py; do not edit) -->
**Labelled learners, on the refunds example.**

| Adapter (learner) | Inv. | Run of record | Outcome | Clauses proposed | Import exit | First refusal | Not evaluated | Admitted |
|---|---|---|---|---|---|---|---|---|
| popper (popper 5.0.1+578a4e2) | 1 | yes | `rendering-rejected` / `none` | — | — | — | — | — |
| popper (popper 5.0.1+578a4e2) | 2 | no (ruled) | `completed` / `none` | — | — | — | — | — |
| popper (popper 5.0.1+578a4e2) | 3 | no (ruled) | `completed` / `admitted` | 1 | 0 | — | 0 | 1 |
| ilasp (ilasp 4.4.1) | 1 | yes | `completed` / `refused:empty-antecedent` | 1 | 3 | `empty-antecedent`, clause 0 | 0 | 0 |
| llm (claude, version not reported) | 1 | yes | `completed` / `admitted` | 1 | 0 | — | 0 | 1 |
| rules (wittgenstein 0.3.5) | 1 | yes | `completed` / `admitted` | 1 | 0 | — | 0 | 1 |

**The rule miner, on the staffing population.**

| Adapter (learner) | Inv. | Run of record | Outcome | Rules mined | Hold (GND's count) | Import exit | First refusal | Admitted |
|---|---|---|---|---|---|---|---|---|
| amie (amie 4.0.0) | 1 | yes | `completed` / `refused:does-not-hold` | 8 | 2 | 3 | `does-not-hold`, rule 0 | 0 |
| amie (amie 4.0.0) | 2 | no (ruled) | `completed` / `admitted` | 2 | 2 | 0 | — | 2 |

Every row is a single run. Reproducibility, as each run recorded it: "single run, not repeatable"; "single run, reproducibility not measured"; "single run, reproducibility not measured; repeated runs pick other thresholds (IL3-F5)".
<!-- ilp-comparison:end -->

Run 1 of Popper failed because the adapter-1 rendering wrote thresholds as
comparisons with constants, which Popper 5.0.1 cannot fill in; runs 2 and 3
used the later renderings, and the shipped rendering is run 3's.

## Bounds

| Item | Bound |
|---|---|
| exported facts | at most 500,000 |
| each written file | at most 64 MiB |
| CLAUSES | at most 1 MiB; 1 to 32 clauses; 1 to 16 body literals; `not`/`or`/`aggregate` nesting at most 4 |
| run record | at most 32 MiB; a mined run record at most 64 KiB |
| mined RULES | at most 1 MiB; 1 to 256 rules; 2 to 4 atoms; counts of at most 18 digits; a body join of at most 1,000,000 rows |
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

- That a learner accepts the rendering in general. Each rendering was run
  against one learner version, under the few settings the
  [comparison](#comparing-the-learners) records, one run each; any other
  version or setting is untested.
- That learned rules are true. Coverage agreement on the labelled examples is
  necessary, not sufficient. Admission is your reviewed `gnd evolve` step.
