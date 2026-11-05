# Judge induced fact types with two skills

When extracted facts land in a generic fact type, "an item has an attribute
with a value", `gnd discover --families fact-type` groups the rows by
attribute and proposes a proper binary fact type for each attribute that
recurs. It counts well. Two things it cannot decide by itself. Does a group
mean the same as a fact type the model already has? The same role players say
only that two fact types *could* hold the same facts. And how should an
attribute be modelled when an item holds several values for it? The family
counts such a group `multi_valued` and stops.

Those two judgements belong to two packaged Claude Code skills,
`gnd-judge-fact-types` and `gnd-model-multivalued`. The CLI stays
deterministic. It writes value-free evidence, reads back the skill's verdicts
bound by digest to that evidence, checks them, and renders evolve proposals
that `gnd evolve preview --policy additive` accepts. Applying stays your
reviewed `gnd evolve apply`, which this page names and does not run.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="How a judgement travels between the CLI and a skill">

![gnd discover reads the model and the population and writes evidence that holds counts, digests, opaque row ids and candidate readings, never a value. A skill reads the model and the evidence only, never the population, decides each group by its rules and asks you where the rules stop, then writes a judgements file bound to the evidence by SHA-256. gnd discover reads the judgements back, computes the evidence again, refuses on any difference, checks every verdict and renders an additive proposal. gnd evolve preview with the additive policy checks it; gnd evolve apply is your reviewed step.](../assets/applications/judge-flow.svg)
</div>

*Source: the two rounds of the shipped example, run below.*

!!! info "Files on GitHub"

    - [`type_judgements/duplicates/`](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/examples/type_judgements/duplicates): a model with one applied induction, renamed by review, and a hand-modelled "Item has colour Colour"; a population of four attributes; and `duplicates.judgements.json`, the file `gnd-judge-fact-types` wrote in a recorded session
    - [`type_judgements/multi-valued/`](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/examples/type_judgements/multi-valued): a model whose applied induction is many-to-many, and a hand-modelled "Item has label Label"; a population of five attributes with several values per item; and `shapes.judgements.json`, the file `gnd-model-multivalued` wrote in a recorded session
    - [the example's README](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/type_judgements/README.md)
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/how-to/judge-induced-fact-types.md)

Copy the example into a working folder:

<!-- gnd-run expect=0 -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/type_judgements', 'items', dirs_exist_ok=True)"
```

Both folders are round two of the same story: one induction was proposed,
reviewed and applied, and now the generic fact type has filled up again. The
attribute names in the populations are deliberately meaningless, so a judge
that reads only the evidence cannot see them, and this page does not print
them. There are two folders rather than one evidence file because each
recorded judgements file is bound by digest to the evidence of its own
folder, its own model and its own population; the two rounds have different
models, so neither file could bind the other's evidence.

## Round one, in a sentence

The duplicates folder's model is what the first round left. The family
proposed `item_has_attribute_induced_0` from one attribute, review renamed its
reading to "{Item} has dimension {AttributeValue}" and applied it; the
model's `induced_from` provenance remembers the attribute it came from, as a
digest. Someone also modelled "{Item} has colour {Colour}" by hand. The
population still holds every row in the generic fact type: nothing moves when
a fact type is induced.

Run the family again and ask for evidence:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd discover items/duplicates/model.orm.yaml items/duplicates/items.population.json --families fact-type --type-evidence items/duplicates/evidence.json --out items/duplicates/proposal-0.json --report items/duplicates/report-0.json --actor you --requested-at 2026-11-05T00:00:00+00:00
```

```text
GND DISCOVER
MODEL items/duplicates/model.orm.yaml
POPULATION items/duplicates/items.population.json
EMITTED 0
NEAR MISSES 0
REJECTED vacuous=0 unchecked=0 fail=0 warning=0
SUPPRESSED
FACT TYPES 0
  shape of item_has_attribute_induced_0
  shape of item_has_attribute_induced_0
  shape of item_has_attribute_induced_0
  shape of item_has_attribute_induced_0
WORK total=0
PROPOSAL (none)
```

Nothing is proposed. Every group of one generic fact type has the same role
players, Item and AttributeValue, so once one induced fact type is applied,
every later group is a shape match against it. That is the limit the first
skill lifts.

## The evidence

The evidence file is what the family knows and nothing more: for each group,
its status, its counts and opaque row ids, and for every other fact type the
item plays (the *candidates*), its readings and two overlaps: how many of the
group's items play it, and how many of the group's (item, value) pairs it
already holds. A candidate induced from this very attribute carries an
`origin`. No attribute name and no value appears in it; the two populations'
and the model's digests do. The format is in the
[type evidence](../reference/discover.md#type-evidence) reference.

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import json; e=json.load(open('items/duplicates/evidence.json')); print(e['format'], 'show_values', e['show_values'], 'truncated_groups', e['truncated_groups']); [print(g['group'], g['status'], 'rows', g['rows'], 'items', g['support'], [(c['fact_type'], c['overlap']['pairs'], bool(c['origin'] and c['origin']['same_attribute'])) for c in g['candidates']]) for g in e['groups']]"
```

```text
gnd-type-evidence/1 show_values False truncated_groups 0
g0 shape_match rows 24 items 24 [('item_has_attribute_induced_0', 24, True), ('item_has_colour', 0, False)]
g1 shape_match rows 24 items 24 [('item_has_attribute_induced_0', 0, False), ('item_has_colour', 24, False)]
g2 shape_match rows 24 items 24 [('item_has_attribute_induced_0', 0, False), ('item_has_colour', 0, False)]
g3 shape_match rows 24 items 24 [('item_has_attribute_induced_0', 0, False), ('item_has_colour', 12, False)]
```

Each tuple is a candidate: its id, the pairs it shares with the group, and
whether it was induced from the group's own attribute. Read as a table:

| Group | Rows | Shares pairs with `..._induced_0` | Shares pairs with `item_has_colour` | Same attribute as `..._induced_0` |
|---|---|---|---|---|
| g0 | 24 | all 24 | none | yes |
| g1 | 24 | none | all 24 | no |
| g2 | 24 | none | none | no |
| g3 | 24 | none | 12 of 24 | no |

## Judge the duplicates

**You type.** From inside `items/duplicates`, where the model and the
evidence sit, the recorded session's first turn was exactly:

```text
/gnd:gnd-judge-fact-types model.orm.yaml evidence.json
```

**Claude Code does.** The skill checks the evidence before it judges: the
format, that `model_sha256` is the digest of the model it was given, and that
no group was left out. Then it applies four rules to each group, in order,
and stops where they stop. In plain words: a candidate induced from this very
attribute is the same fact type (R1); a candidate that already holds nearly
all of the group's pairs is the same fact type under another name (R2); when
every comparable candidate shares no pair at all, the group is distinct, and
the skill says that this rests only on the absence of shared facts (R3);
anything in between, a partial overlap, or no candidate it can compare, is a
question for you (R4). Equal role players are evidence neither way.

The recorded agent (Sonnet 5.5) decided g0, g1 and g2 and asked about g3. Its
reply began:

> I haven't written a judgements file. Group `g3` needs your decision first, and the skill says to write nothing until every eligible group has a verdict.

and ended with the question, after noting that `item_has_colour` shares half
of g3's pairs, below the bar for R2 and above zero for R3:

> Is `g3` the same attribute as colour, only partly recorded in `item_has_colour`? Or is it a different attribute for the same items?
>
> - **`duplicate` of `item_has_colour`:** choose this if it is colour, and the rest of its values are simply missing from the model's fact type.
> - **`distinct`:** choose this if it is a separate attribute that happens to agree with colour on half the items.

**You answer.** The recorded second turn:

```text
Group g3 is a different attribute from every candidate: distinct. Write the file.
```

**You get.** The shipped `items/duplicates/duplicates.judgements.json` is the
file the agent then wrote. Its reply began:

> I wrote the judgements file to `...duplicates.judgements.json`. I haven't run `gnd` on it, so the CLI hasn't checked it yet.

and it gave the two commands of the next section with placeholders for you to
fill. The file binds the evidence by the SHA-256 of its raw bytes, which is
why the digest you compute here equals the one in the file:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import hashlib, json; print(hashlib.sha256(open('items/duplicates/evidence.json', 'rb').read()).hexdigest()); print(json.load(open('items/duplicates/duplicates.judgements.json'))['evidence_sha256'])"
```

```text
75c734f87cfc1702eca3746c2cdd4bbac2d33012e7db405c6d85867cff83717b
75c734f87cfc1702eca3746c2cdd4bbac2d33012e7db405c6d85867cff83717b
```

One verdict per group, in evidence order, each with the rule that decided it:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import json; [print(v['group'], v['verdict'], v.get('of', '-'), v['rationale'].split(':')[0]) for v in json.load(open('items/duplicates/duplicates.judgements.json'))['verdicts']]"
```

```text
g0 duplicate item_has_attribute_induced_0 Rule R1
g1 duplicate item_has_colour Rule R2
g2 distinct - Rule R3
g3 distinct - Rule R4
```

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="The four groups of the duplicates round and their verdicts">

![Four groups of 24 rows each, g0 to g3, compared with two candidates, Item has dimension AttributeValue and Item has colour Colour. g0 shares every pair with has dimension, which was induced from the same attribute: duplicate by R1. g1 shares every pair with has colour: duplicate by R2. g2 shares no pair with either: distinct by R3, resting on the absence of shared facts. g3 shares half its pairs with has colour: R4, asked; you answered distinct. g2 and g3 are proposed as item_has_attribute_induced_2 and _3; g0 and g1 are listed as judged shape matches.](../assets/applications/judge-duplicates.svg)
</div>

*Source: the evidence and the judgements file printed above.*

The rationales name group ids, fact type ids, words from the model's
readings and the rule. They name no attribute and no value, and, because the
evidence hides values, no number standing alone: g1's says "every distinct
pair" rather than a count, and the agent is "Claude Sonnet" with no version.
A short value could equal a count or a version, and the CLI refuses free text
that matches one.

## Render the verdicts

**Claude Code gives you two commands.** The first runs the family once more,
with the evidence it wrote and the judgements the skill wrote, under the same
model, population, `--min-support` and disclosure setting:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd discover items/duplicates/model.orm.yaml items/duplicates/items.population.json --families fact-type --type-evidence-in items/duplicates/evidence.json --duplicate-judgements items/duplicates/duplicates.judgements.json --out items/duplicates/proposal.json --report items/duplicates/report.json --actor you --requested-at 2026-11-05T00:00:00+00:00
```

```text
GND DISCOVER
MODEL items/duplicates/model.orm.yaml
POPULATION items/duplicates/items.population.json
EMITTED 0
NEAR MISSES 0
REJECTED vacuous=0 unchecked=0 fail=0 warning=0
SUPPRESSED
FACT TYPES 2
  item_has_attribute_induced_2 support=24
  item_has_attribute_induced_3 support=24
  shape of item_has_attribute_induced_0
  shape of item_has_colour
WORK total=0
PROPOSAL items/duplicates/proposal.json
```

**GND says.** Before rendering anything it computed the evidence again, byte
for byte, and compared it with the file the judgements bind; had the
population or the model changed, or the disclosure setting, it would have
refused with exit 3 and named the setting that differs. It then checked every
verdict against the evidence: a group may not be missing, repeated or of
another kind; `of` must name a candidate of that group; and `distinct` is
refused on a group whose attribute some fact type's `induced_from` already
names, whether or not the judge noticed. The rules the CLI holds a judgements
file to are in the [type judgements](../reference/discover.md#type-judgements)
reference.

Then it rendered. The two `distinct` groups are proposed even though their
signature matches `item_has_attribute_induced_0`; the two `duplicate` groups
are listed as shape matches against the fact type the judge named, not
against the first fact type with the same shape as before:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import json; p=json.load(open('items/duplicates/report.json'))['fact_type_proposals']; [print('proposed', x['fact_type'], 'judged', x['judged']) for x in p['proposed']]; [print('shape match', m['existing'], 'judged', m['judged']) for m in p['shape_matches']]"
```

```text
proposed item_has_attribute_induced_2 judged True
proposed item_has_attribute_induced_3 judged True
shape match item_has_attribute_induced_0 judged True
shape match item_has_colour judged True
```

Each proposed fact type carries a placeholder reading for a reviewer to
rename, and in its provenance both where it came from and who judged it:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import json; [print(op['after']['reading'], '|', op['after']['provenance']['judgement']['skill'], op['after']['provenance']['judgement']['verdict']) for op in json.load(open('items/duplicates/proposal.json'))['operations'] if op['after'].get('reading')]"
```

```text
{Item} has induced item_has_attribute attribute 2 {AttributeValue} | gnd-judge-fact-types distinct
{Item} has induced item_has_attribute attribute 3 {AttributeValue} | gnd-judge-fact-types distinct
```

The second command previews the round under the additive policy, as in
[grow a model by additions](grow-a-model.md):

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd evolve preview items/duplicates/model.orm.yaml items/duplicates/proposal.json --workspace items/duplicates --records items/duplicates/records --out items/duplicates/preview.json --policy additive
```

```text
...
  breaking: false
  affected: fact_types[item_has_attribute_induced_2]
  affected: fact_types[item_has_attribute_induced_2].constraints[uniqueness:new:0]
  affected: fact_types[item_has_attribute_induced_3]
  affected: fact_types[item_has_attribute_induced_3].constraints[uniqueness:new:0]
  policy: additive
  populated: -
```

Admitted: two new fact types, each with a uniqueness on the item role that
stays induced, proposed and deontic. Applying it is your step, with the same
policy and after reading the preview:

```sh
gnd evolve apply items/duplicates/model.orm.yaml items/duplicates/proposal.json --preview items/duplicates/preview.json --workspace items/duplicates --records items/duplicates/records --policy additive
```

This page does not run it. Review can rename the placeholder readings, and
it can still overturn a verdict: g2's `distinct` rests on the absence of
shared facts, and a synonym attribute recorded for different items would
pass R3 the same way.

## The multi-valued round

The second folder's first round went differently: the induced attribute held
several values per item, so review applied `item_has_attribute_induced_0` as
"{Item} is tagged {AttributeValue}" with a uniqueness spanning both roles.
Someone also modelled "{Item} has label {Label}" by hand, with the same
spanning uniqueness. Now five more attributes have several values per item.

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd discover items/multi-valued/model.orm.yaml items/multi-valued/items.population.json --families fact-type --type-evidence items/multi-valued/evidence.json --out items/multi-valued/proposal-0.json --report items/multi-valued/report-0.json --actor you --requested-at 2026-11-05T00:00:00+00:00
```

```text
GND DISCOVER
MODEL items/multi-valued/model.orm.yaml
POPULATION items/multi-valued/items.population.json
EMITTED 0
NEAR MISSES 0
REJECTED vacuous=0 unchecked=0 fail=0 warning=0
SUPPRESSED
FACT TYPES 0
WORK total=0
PROPOSAL (none)
```

Not even a shape match: a multi-valued group has no signature, because the
family does not know what shape to give it. The evidence says how many items
hold several values and how many rows repeat an (item, value) pair exactly:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import json; [print(g['group'], g['status'], 'rows', g['rows'], 'items', g['support'], 'with several values', g['multi']['entities'], 'exact repeats', g['exact_repeats'], [(c['fact_type'], c['overlap']['pairs'], bool(c['origin'] and c['origin']['same_attribute'])) for c in g['candidates']]) for g in json.load(open('items/multi-valued/evidence.json'))['groups']]"
```

```text
g0 multi_valued rows 48 items 24 with several values 24 exact repeats 0 [('item_has_attribute_induced_0', 48, True), ('item_has_label', 0, False)]
g1 multi_valued rows 48 items 24 with several values 24 exact repeats 0 [('item_has_attribute_induced_0', 0, False), ('item_has_label', 48, False)]
g2 multi_valued rows 37 items 24 with several values 12 exact repeats 1 [('item_has_attribute_induced_0', 0, False), ('item_has_label', 0, False)]
g3 multi_valued rows 25 items 24 with several values 1 exact repeats 0 [('item_has_attribute_induced_0', 0, False), ('item_has_label', 0, False)]
g4 multi_valued rows 48 items 24 with several values 24 exact repeats 0 [('item_has_attribute_induced_0', 0, False), ('item_has_label', 24, False)]
```

**You type.** From inside `items/multi-valued`, the recorded first turn:

```text
/gnd:gnd-model-multivalued model.orm.yaml evidence.json
```

**Claude Code does.** This skill borrows a convention from schema-to-ORM
work: an attribute with several values per item is a junction table, one
many-to-many fact type with a uniqueness over both roles, which says each
(item, value) pair is recorded once and nothing about how many values an item
may have. Its four rules, in plain words: a candidate induced from this very
attribute already models it, so skip, and if that candidate's uniqueness
covers the item alone the data has changed shape and that is a job for a
reviewed model change, not a judgement (S1); a candidate that already holds
nearly all the pairs covers it, so skip (S2); when nothing was truncated, no
candidate shares a pair, and at least one item in ten holds several values,
it is a junction table, many-to-many, and the rows that repeat a pair become
the uniqueness's counterexamples (S3); anything else, including an attribute
where only a few items hold several values, which may be entry errors, is a
question for you (S4). A shapes file can say many-to-many or skip; it cannot
declare an attribute single-valued.

The recorded agent decided g0, g1 and g2, and read the model to confirm that
the applied fact type's uniqueness spans both roles before applying S1. It
began:

> I've checked the inputs and decided three of the five groups. I haven't written the judgements file, because g3 and g4 need your answer first.

and asked two questions:

> - **g3 (S4, few multi-valued entities).** Only one item has two values; the other 23 have one. ... Is that second value a real second value, or an entry error?
>   - If it's real, the verdict is `many-to-many`.
>   - If it's an error, the verdict is `skip`. You would then correct the population and regenerate the evidence, because a shapes file can't declare an attribute single-valued.
> - **g4 (S4, partial overlap).** `item_has_label` already holds 24 of the group's 48 distinct pairs, about half. Should this be:
>   - `many-to-many`, kept as its own fact type even though half its pairs are already in `item_has_label`?
>   - `skip`, because it's meant to be covered by `item_has_label`?

**You answer.** The recorded second turn:

```text
In group g3 the one item's second value is an entry error: skip it, and the population will be fixed. Group g4 repeats labels the model already holds: skip it too. Write the file.
```

**You get.** The shipped `items/multi-valued/shapes.judgements.json`. The
agent's reply closed with:

> Only g2 is rendered as a proposal, a binary fact type with a uniqueness over both roles. The four skips are counted under `skipped.judged_skip`.

and, of g3, it repeated what a skip means here: correct the population, then
make new evidence, because the binding will stop matching once the
population changes.

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import json; [print(v['group'], v['verdict'], v['rationale'].split(':')[0]) for v in json.load(open('items/multi-valued/shapes.judgements.json'))['verdicts']]"
```

```text
g0 skip Rule S1
g1 skip Rule S2
g2 many-to-many Rule S3
g3 skip Rule S4, answered by the user
g4 skip Rule S4, answered by the user
```

Render:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd discover items/multi-valued/model.orm.yaml items/multi-valued/items.population.json --families fact-type --type-evidence-in items/multi-valued/evidence.json --shape-judgements items/multi-valued/shapes.judgements.json --out items/multi-valued/proposal.json --report items/multi-valued/report.json --actor you --requested-at 2026-11-05T00:00:00+00:00
```

```text
GND DISCOVER
MODEL items/multi-valued/model.orm.yaml
POPULATION items/multi-valued/items.population.json
EMITTED 0
NEAR MISSES 0
REJECTED vacuous=0 unchecked=0 fail=0 warning=0
SUPPRESSED
FACT TYPES 1
  item_has_attribute_induced_2 support=36
WORK total=0
PROPOSAL items/multi-valued/proposal.json
```

One proposal, with the shape the judge gave it, and four judged skips:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import json; p=json.load(open('items/multi-valued/report.json'))['fact_type_proposals']; [print('proposed', x['fact_type'], x['shape'], 'support', x['support']['numerator'], 'of', x['support']['denominator']) for x in p['proposed']]; print('judged_skip', p['skipped']['judged_skip'])"
```

```text
proposed item_has_attribute_induced_2 many-to-many support 36 of 37
judged_skip 4
```

Support for a many-to-many fact type is distinct pairs over rows: 36 of
g2's 37 rows are distinct (item, value) pairs. The one row that repeats a
pair is the counterexample of the proposed uniqueness, which spans both
roles:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import json; [print(op['after']['type'], 'over', op['after']['roles'], 'counterexamples', op['after']['provenance']['induction']['counterexamples']) for op in json.load(open('items/multi-valued/proposal.json'))['operations'] if op['after'].get('type') == 'uniqueness']"
```

```text
uniqueness over ['entity', 'value'] counterexamples ['ft0#132']
```

`ft0#132` is an opaque row id: the 133rd row of the generic fact type, which
states a pair some earlier row already stated. Nothing is wrong with the
proposal; a deontic uniqueness with one counterexample says exactly what the
data says, and a reviewer who applies it knows which row to look at.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="The five multi-valued groups and the one many-to-many proposal">

![Five multi-valued groups. g0: every pair already in Item is tagged AttributeValue, induced from the same attribute, skip by S1. g1: every pair already in Item has label Label, skip by S2. g2: 12 of 24 items hold two values, no candidate shares a pair, one exact repeat: many-to-many by S3. g3: one item with a second value, asked, you said entry error, skip. g4: half its pairs in has label, asked, you said covered, skip. On the right the one proposal: Item has induced attribute 2 AttributeValue with a uniqueness spanning both roles, 36 distinct pairs of 37 rows, counterexample row ft0#132.](../assets/applications/judge-multivalued.svg)
</div>

*Source: the evidence, the judgements file and the report printed above.*

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd evolve preview items/multi-valued/model.orm.yaml items/multi-valued/proposal.json --workspace items/multi-valued --records items/multi-valued/records --out items/multi-valued/preview.json --policy additive
```

```text
...
  breaking: false
  affected: fact_types[item_has_attribute_induced_2]
  affected: fact_types[item_has_attribute_induced_2].constraints[uniqueness:new:0]
  policy: additive
  populated: -
```

Admitted, and again `gnd evolve apply` with the same policy is your step.
When a run has both kinds of group, both judgements files go to one
`gnd discover` call, `--duplicate-judgements` beside `--shape-judgements`.

## What this proves, and what it does not

The two rounds establish that a skill's verdicts can drive the family
without the CLI ever choosing one: each verdict is checked against the
evidence it was made from, each rendered fact type records the evidence and
judgements digests that produced it, and the result is an ordinary additive
proposal that review admits or overturns. A verdict is a proposal, not a
change. The recorded sessions also show the skills stopping where their
rules stop and asking, writing nothing until every group had a verdict. The
recorder checked that the file was written only after the question, that no
`gnd evolve apply` was called and that no attribute name reached the file;
its one false alarm, a "population" check that tripped on the word in a
rationale the agent wrote rather than on a read, is noted in the recording.

Three limits. The CLI's free-text check catches the exact text of an
attribute or value, ignoring case and whitespace; it does not catch a
paraphrase or an encoding, so the skills' own rule never to quote a value is
the main control, and the digests in the file are what makes an audit
possible, not a guarantee that the rationale is clean. There is one recorded
run per skill over one small model; the rules were followed here, which says
nothing about a model with a hundred candidates or an evidence file near its
size cap. And the skills never read the population, which is the point of
the evidence, but also means g2's `distinct` and g3's `skip` rest on counts
and your word; a synonym recorded for different items, or a second value
that was real, would pass the same way. Review is where those are caught.

## Recap

| Round | The family said | The skill judged | GND rendered |
|---|---|---|---|
| duplicates | four shape matches, nothing proposed | g0, g1 `duplicate` (R1, R2); g2 `distinct` (R3); g3 asked, `distinct` (R4) | two proposed fact types, two judged shape matches; admitted |
| multi-valued | five multi-valued groups, nothing proposed | g0, g1 `skip` (S1, S2); g2 `many-to-many` (S3); g3, g4 asked, `skip` (S4) | one many-to-many fact type with a spanning uniqueness and one counterexample row; admitted |

In both rounds `gnd discover` ran twice, once to write the evidence and once
to read the verdicts back and check them, with a recorded Claude Code session
between the two that read the evidence and never the population. Applying is
still yours.

## Next steps

- The evidence and judgements formats, the binding rule and every refusal
  are in the [type evidence](../reference/discover.md#type-evidence) and
  [type judgements](../reference/discover.md#type-judgements) reference.
- The skills themselves:
  [`gnd-judge-fact-types`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-judge-fact-types/SKILL.md)
  and
  [`gnd-model-multivalued`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-model-multivalued/SKILL.md);
  install them with the [agent skill guide](../agents/index.md).
- The round that applies a proposal, with the policy that keeps it additive,
  is [grow a model by additions](grow-a-model.md) and the
  [additive evolve policy reference](../reference/evolve-policy.md).
- How generic rows get into a population in the first place, from several
  documents at once, is
  [from several documents to one checked answer](compose-documents.md).
