# Grow a model by additions, with GND checking each round

A model does not have to be written in one sitting. In this how-to a program
grows a shop's model one document at a time. A short note arrives, the program
(an LLM behind the `gnd-model-evolve` skill, or your own code) proposes what the
note adds, and GND checks the round before anything is published.

The one rule of a growing model is that each round only **adds**. A rename, a
delete, or a new constraint on facts the model already holds would change what
earlier facts mean, and the rounds that produced them could no longer be
trusted. GND checks that for you, round by round, for the facts it can see
(below), and it points out when a new fact type looks like one you already have.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="One round of growing a model">

![A document arrives. The program proposes additions as a proposal bound to the model's digest. gnd evolve preview with the additive policy and the shape report checks the round. An admitted round is applied with the same policy and the model grows, as round 1 does with "is returned via". A refused round leaves the model unchanged, as round 2 does with a mandatory rule. Then the next document arrives.](../assets/applications/growth-rounds.svg)
</div>

*Source: the two shipped rounds of the growth example, run below.*

!!! info "Files on GitHub"

    - [`growth/model.orm.yaml`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/growth/model.orm.yaml): the shop's model with two sample orders and one derived fact type
    - [`growth/round-1.document.txt`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/growth/round-1.document.txt) and [`round-1.proposal.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/growth/round-1.proposal.json): a returns note, and the addition "Order is returned via Channel" proposed from it
    - [`growth/round-2.document.txt`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/growth/round-2.document.txt) and [`round-2.proposal.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/growth/round-2.proposal.json): an intake note, and the mandatory rule proposed from it
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/how-to/grow-a-model.md)

Copy the example into a working folder:

<!-- gnd-run expect=0 -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/growth', 'growth', dirs_exist_ok=True)"
```

## The model you start with

The shop knows customers, orders and channels. Two fact types connect them,
and a third is derived: a customer who has placed an order is active. GND
already holds two sample orders. There are no constraints yet.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="The shop model before any round">

![Three object types: Customer and Order are entities identified by a number, Channel is a value. Two fact types connect them: Order is placed by Customer, and Order arrives via Channel. A derived unary fact type, Customer is active, follows from an order being placed. GND already holds two sample facts: order 10 is placed by customer 1 and order 11 by customer 2. No constraints.](../assets/applications/growth-start.svg)
</div>

*Source: `growth/model.orm.yaml` as shipped.*

GND can read the model back as sentences. `gnd extract` writes a bundle whose
verbalization lists every fact type and the object type each role is played by:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd extract growth/model.orm.yaml --out start >/dev/null && sed -n '/=== Fact Types/,$p' start/model.verbalization.txt
```

```text
=== Fact Types ===
Order is placed by Customer
  - order: Order (Integer)
  - customer: Customer (Integer)

Order arrives via Channel
  - order: Order (Integer)
  - channel: Channel (String)

Customer is active
  - customer: Customer (Integer)
```

## Round 1: a returns note arrives

The first document is a note from the returns desk:

<!-- gnd-run expect=0 output=stdout -->
```sh
cat growth/round-1.document.txt
```

```text
Returns desk note, week 44

Customers may send an order back within 30 days. A returned order comes
back through one of our channels, which need not be the channel it arrived
by. Order 10 arrived by courier and was returned in store; order 11 arrived
by post and was returned by post.
```

**You type.** With Claude Code and the `gnd-model-evolve` skill, the ask is a
plain sentence:

```text
Use gnd-model-evolve on growth/model.orm.yaml with the additive policy. Read
growth/round-1.document.txt and propose only what it adds to the model. Preview
the round with the shape report and show me what GND says before you apply it.
```

**Claude Code does.** The skill writes a closed proposal that binds the current
model's digest and states the one addition: a fact type "Order is returned via
Channel", read from the note's second sentence. The shipped
`growth/round-1.proposal.json` is that proposal. Then it previews the round:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd evolve preview growth/model.orm.yaml growth/round-1.proposal.json --workspace growth --records growth/records --out growth/round-1.preview.json --policy additive --populated order_arrives_via_channel --shape-report
```

```text
...
  breaking: false
  affected: fact_types[order_returned_via_channel]
  policy: additive
  populated: order_arrives_via_channel order_placed_by_customer
  shape-group: channel,order added order_returned_via_channel existing order_arrives_via_channel
```

**You get.** The model with one more fact type, drawn in green:

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="Round 1: a returns note adds one fact type">

![A returns desk note says a returned order comes back through one of the shop's channels. The program proposes one addition, Order is returned via Channel, drawn in green beside the existing Order arrives via Channel. Both connect Order and Channel, so the shape report names "arrives via" as a candidate. GND admits the round under the additive policy: breaking false, affected order_returned_via_channel.](../assets/applications/growth-round-1.svg)
</div>

*Source: `growth/round-1.document.txt` and the preview above.*

**GND says.** Three things, in plain words:

- *Admitted.* The round only adds, so the additive policy lets it through.
  `breaking: false` and the only affected element is the new fact type.
- *These fact types hold facts.* The `populated:` line names
  `order_placed_by_customer`, because the model carries sample rows for it,
  and `order_arrives_via_channel`, because the command said so with
  `--populated`. Facts your program extracted into its own population files are
  invisible to GND unless you name their fact types this way; the next round
  shows why that list matters.
- *Look at this one.* The `shape-group:` line says the new
  `order_returned_via_channel` has the same role players, Order and Channel,
  as the existing `order_arrives_via_channel`. That is a candidate, not a
  duplicate: "returned via" and "arrives via" are different facts about the
  same two things. A program that proposes fact types from text will sometimes
  reinvent one it already has under new words, so GND points at every
  same-shape pair and leaves the decision to you. The report never changes the
  exit.

### Apply the round, repeating the policy

`apply` must repeat `--policy additive` and the same `--populated` ids. It
refuses when the options differ from the preview's, and checks the policy
again on exactly what it publishes.

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd evolve apply growth/model.orm.yaml growth/round-1.proposal.json --preview growth/round-1.preview.json --workspace growth --records growth/records --policy additive --populated order_arrives_via_channel
```

```text
...
  proposal: round-1
...
  conformance-exit: 0
```

The grown model now reads back with four fact types:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd extract growth/model.orm.yaml --out after-1 >/dev/null && grep -v "^  -" after-1/model.verbalization.txt | sed -n '/=== Fact Types/,$p'
```

```text
=== Fact Types ===
Order is placed by Customer

Order arrives via Channel

Customer is active

Order is returned via Channel
```

One thing to know about the published file: `apply` writes the proposal's
candidate model text exactly as the proposal carries it. These proposals were
built with the canonical candidate writer that `gnd discover` also uses, which
writes one-line JSON, so the comments and YAML layout of the original file are
gone. A proposal whose candidate text keeps them publishes them.

<!-- gnd-run expect=0 output=stdout -->
```sh
head -c 40 growth/model.orm.yaml; echo
```

```text
{"version":1,"model_id":"growth-shop","s
```

## Round 2: an intake note arrives

The second document says something about orders the model already holds:

<!-- gnd-run expect=0 output=stdout -->
```sh
cat growth/round-2.document.txt
```

```text
Order intake note, week 45

Every order must be placed by a customer. The shop no longer accepts
anonymous counter sales, so an order with no customer on it is a mistake.
```

**You type.** The same ask as before, for the new note:

```text
Use gnd-model-evolve on growth/model.orm.yaml with the additive policy. Read
growth/round-2.document.txt and propose only what it adds. Preview the round
and show me what GND says before you apply it.
```

**Claude Code does.** The note reads like a rule, so the program proposes one:
a mandatory constraint on "Order is placed by Customer", saying every order
must have one. The shipped `growth/round-2.proposal.json` is that proposal,
bound to the model as round 1 published it. The preview:

<!-- gnd-run expect=3 output=stdout -->
```sh
gnd evolve preview growth/model.orm.yaml growth/round-2.proposal.json --workspace growth --records growth/records --out growth/round-2.preview.json --policy additive --populated order_arrives_via_channel 2>&1
```

```text
EVOLUTION PREVIEW REFUSED (3): additive policy refused 1 operation(s); see policy_issues in <run>/growth/round-2.preview.json
...
  affected: fact_types[order_placed_by_customer].constraints[mandatory:new:0]
  policy: additive
  populated: order_arrives_via_channel order_placed_by_customer
  policy-issue: 0 constraint.populated.add fact_types[order_placed_by_customer].constraints[mandatory:new:0]
```

**You get.** Nothing new in the model. The proposed rule is drawn as an orange
dot, and the model stays as round 1 left it:

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="Round 2: a rule on facts already held is refused">

![An order intake note says every order must be placed by a customer. The program proposes a mandatory constraint, drawn as an orange dot where "Order is placed by Customer" meets Order. That fact type already holds orders 10 and 11, so the additive policy refuses the round with exit 3 and policy issue constraint.populated.add. The model is unchanged.](../assets/applications/growth-round-2.svg)
</div>

*Source: `growth/round-2.document.txt` and the refused preview above.*

**GND says.** *Refused.* The `policy-issue:` line names the operation
(the first and only one), the cell of the policy that refused it,
`constraint.populated.add`, and the constraint it would have added.

A constraint is not an addition in the sense the policy means. The two sample
orders were accepted under a model that said nothing about customers being
required; a rule added on top of them could reject them, or reject the next
batch of facts extracted the same way, so every earlier round would mean
something different from what it meant when it ran.

The `populated:` line is
the list the policy consulted, which is why naming extracted fact types with
`--populated` matters: a fact type GND does not know to be populated would
take the rule.

The preview file is still written, so the refusal can be read by a program as
well as a person; its `policy_issues` carry the same three fields. The full
policy is in the [additive evolve policy reference](../reference/evolve-policy.md).
A rule like this one is a job for a reviewed change with a person in the loop,
as in [Expense chapter 3](../expense/03-evolution.md), not for the growing
program. There is one exception: when the facts the program extracted are in a
population file and every one of them satisfies the rule, `--check-population`
lets the policy admit the rule as a proposed, advisory constraint, relative to
that file ([admitting a constraint on clean data](../reference/evolve-policy.md#admitting-a-constraint-on-clean-data)).
Here the rule's fact type carries two sample rows in the current model, and the
population check never clears a rule over such a fact type, so round 2 stays
refused.

## Give the extractor guidelines

With the model grown, the program's next job is to extract facts from the
documents into it. `--guidelines` adds a constraint-blind guide to the
extraction bundle: each fact type's reading, what each role means, and the
fact types that share role players. With Claude Code you would ask for the
`gnd-extract` skill:

```text
Use gnd-extract with growth/model.orm.yaml and its guidelines. Extract the
facts in growth/round-1.document.txt and verify what you wrote.
```

The command behind it:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd extract growth/model.orm.yaml --out bundle --guidelines
```

```text
extracted bundle for growth/model.orm.yaml -> bundle
  model.projection.schema.json
  model.verbalization.txt
  model.applicable.json
  model.guidelines.md
  model.artifacts.json
```

The guide repeats the shape report's finding where the extractor will see it:

<!-- gnd-run expect=0 output=stdout -->
```sh
grep "Same role players" bundle/model.guidelines.md
```

```text
- Same role players as: `order_returned_via_channel`
- Same role players as: `order_arrives_via_channel`
```

The guide states no constraint (an external uniqueness that identifies an
entity shows only as how that entity is identified), so the extractor writes
what the document says, even where it breaks one. Round 1's note says order 10
arrived by courier and came back in store: two facts, one per fact type, and
the guide's role descriptions tell the extractor which is which. A description
is the modeller's prose and may restate a constraint; the guide repeats it as
written.

## Read the derivation rules back

Derivation rules your program wrote can be read back in GND's controlled
language. The helper below prints each rule's fact type and its text.
Constraints are not derivation rules and do not appear here:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "from gnd import api; [print(r['fact_type'], '->', r['text']) for r in api.verbalize_rules('growth/model.orm.yaml')['rules']]"
```

```text
customer_is_active -> when order_placed_by_customer(order = $o, customer = $c), derive (customer = $c)
```

See the [rule verbalization reference](../reference/rule-verbalization.md).

## When nobody reviews the model

If the model itself was proposed by an LLM with no person confirming it,
declare that with `source.mode: unattended`; `gnd validate` then requires
every element, sample row and constraint to cite its source text, except
`common-sense` constraints, which cite a library entry, and `induced` ones from
`gnd discover`, which cite the population they were found in. See the
[`gnd-model-from-text` skill's Unattended mode](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-model-from-text/SKILL.md).

A program that proposes only fact types stops at the skill's Steps 1 and 2: its
model fills with `String` value types and unrelated entity types, with no
uniqueness, mandatory or subtype rule. The skill's
[unattended growth procedure](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-model-from-text/references/unattended-growth.md)
says what the program asks for at Steps 3 to 7, document by document, and when
to run a consolidation round over the whole model. One consequence for this
page's rounds: propose a fact type's constraints in the round that adds it, as
round 2 above shows a later one is refused. The procedure also says how a round
declares its new source document inside its proposal and checks every span with
`gnd validate --document ... --require-documents`.

## Recap

| Round | The document said | The program proposed | GND said | The model |
|---|---|---|---|---|
| 1 | a returned order comes back through a channel | add "Order is returned via Channel" | admitted; same role players as "arrives via" | grew by one fact type |
| 2 | every order must be placed by a customer | a mandatory rule on "is placed by" | refused (3): `constraint.populated.add` | unchanged |

Both rounds ran the same two commands with the same policy. The first grew the
model and the second protected the facts it already held. Nothing was renamed,
deleted or constrained behind the program's back.

## Next steps

- The policy's every cell, and what `--populated` changes, are in the
  [additive evolve policy reference](../reference/evolve-policy.md).
- A change that is not additive, such as round 2's rule, goes through a
  reviewed proposal: [Expense chapter 3](../expense/03-evolution.md) adds a
  required currency that way, and [BookRec chapter 6](../bookrec/06-evolution.md)
  promotes an advisory rule to a hard one.
- The skills behind the asks on this page: [change the rules safely](../agents/evolve.md)
  for `gnd-model-evolve`, and the [agent skill guide](../agents/index.md) for
  `gnd-extract`.
- Extracted facts are checked with `gnd verify`; see
  [evolution and recovery](../guides/evolution-and-recovery.md) for the whole
  model-change workflow.
