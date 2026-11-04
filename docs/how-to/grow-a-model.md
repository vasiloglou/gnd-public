# Grow a model by additions, with GND checking each round

Use this when a program, not a person, grows your model: an LLM proposes
new fact types from document passages, extracts facts into them and adds more
as new questions need them. Each round must only **add**. A rename, a delete
or a new constraint on facts you already hold would make earlier facts
uninterpretable. GND checks that for you, round by round.

!!! info "Files on GitHub"

    - [`growth/model.orm.yaml`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/growth/model.orm.yaml): a shop's model with two sample orders and one derived fact type
    - [`growth/round-1.proposal.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/growth/round-1.proposal.json): adds "Order is returned via Channel"
    - [`growth/round-2.proposal.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/growth/round-2.proposal.json): adds a mandatory constraint on the orders the model already holds
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/how-to/grow-a-model.md)

Copy the example:

<!-- gnd-run expect=0 -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/growth', 'growth', dirs_exist_ok=True)"
```

## Refuse a round that is not additive

Round 2 adds the constraint "every order is placed by a customer" to
`order_placed_by_customer`, which already holds two sample orders. A new
constraint there could reject facts the model has already accepted. Preview
it with `--policy additive`:

<!-- gnd-run expect=3 output=stderr -->
```sh
gnd evolve preview growth/model.orm.yaml growth/round-2.proposal.json --workspace growth --records growth/records --out growth/round-2.preview.json --policy additive
```

```text
EVOLUTION PREVIEW REFUSED (3): additive policy refused 1 operation(s); see policy_issues in <run>/growth/round-2.preview.json
```

The preview is still written, so the refusal can be read. Its
`policy_issues` name the operation and the cell of the policy that refused
it:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import json; [print(i['operation_index'], i['cell'], i['reference']) for i in json.load(open('growth/round-2.preview.json'))['policy_issues']]"
```

```text
0 constraint.populated.add fact_types[order_placed_by_customer].constraints[mandatory:new:0]
```

The model is unchanged. The full policy is in the
[additive evolve policy reference](../reference/evolve-policy.md).

GND treats a fact type as holding facts when the model carries sample rows
for it, a declared reference population owns it, or the proposal names a
population for it. Facts your program extracted into its own population
files count only when you say so: pass `--populated FACT_TYPE` for each such
fact type, to `preview` and again to `apply`. The rounds below do that for
`order_arrives_via_channel`.

## Check a new fact type against the ones you have

Round 1 adds "Order is returned via Channel". Before taking it, ask whether
the model already has a fact type whose roles are played by the same object
types: `--shape-report` lists them.

<!-- gnd-run expect=0 -->
```sh
gnd evolve preview growth/model.orm.yaml growth/round-1.proposal.json --workspace growth --records growth/records --out growth/round-1.preview.json --policy additive --populated order_arrives_via_channel --shape-report
```

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import json; [print(g['added'][0]['fact_type'], '~', m['fact_type'], '|', m['reading']) for g in json.load(open('growth/round-1.preview.json'))['shape_matches'] for m in g['existing']]"
```

```text
order_returned_via_channel ~ order_arrives_via_channel | {Order} arrives via {Channel}
```

GND reports a candidate, not a duplicate: "returned via" and "arrives via"
are different facts with the same role players. Whether they mean the same
thing is your program's call. The report never changes the exit.

## Apply the round, repeating the policy

`apply` must repeat `--policy additive` and the same `--populated` ids. It
refuses when the options differ from the preview's, and checks the policy
again on what it publishes.

<!-- gnd-run expect=0 -->
```sh
gnd evolve apply growth/model.orm.yaml growth/round-1.proposal.json --preview growth/round-1.preview.json --workspace growth --records growth/records --policy additive --populated order_arrives_via_channel
```

`apply` publishes the proposal's candidate model text exactly as the
proposal carries it. These proposals were built with the canonical candidate
writer that `gnd discover` also uses, which writes one-line JSON, so the
comments and YAML layout of the original file are gone. A proposal whose
candidate text keeps them publishes them.

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "print(open('growth/model.orm.yaml').read()[:40])"
```

```text
{"version":1,"model_id":"growth-shop","s
```

## Give the extractor guidelines

The next round extracts facts from a document into the grown model.
`--guidelines` adds a constraint-blind guide to the bundle: each fact
type's readings, the fact types with the same role players, and what each
role means.

<!-- gnd-run expect=0 -->
```sh
gnd extract growth/model.orm.yaml --out bundle --guidelines
```

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
what the document says, even where it breaks one. A description is the modeller's prose and
may restate a constraint; the guide repeats it as written.

## Read the derivation rules back

Derivation rules your program wrote can be read back in GND's controlled
language. Constraints are not derivation rules and do not appear here:

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
every element, sample row and constraint (except `common-sense` ones, which
cite a library entry) to cite its source text. See the
[`gnd-model-from-text` skill's Unattended mode](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-model-from-text/SKILL.md).
