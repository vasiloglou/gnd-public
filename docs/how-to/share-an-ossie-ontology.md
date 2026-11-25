# Share a refund model as an Ossie ontology

Your team records who requested each refund, how much it was for, and how
it was paid. A partner wants the same vocabulary for their reporting tool.
Share the ontology so both teams use the same relationships, and the tables
that go with it so the partner can see where each fact would be stored. Keep
the sidecar when a GND user needs to recover the original rules.

!!! info "Files on GitHub"

    [Refunds example model](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/refunds/model.orm.yaml)

With the `/gnd` skill, give it this prompt:

> Export the refunds example as an Ossie ontology with its tables. Show how
> the output represents who requested a refund, and which table holds it.
> Then import it and compare the restored model with the original.

## Export the model

The refunds example ships inside GND. The first command copies it into a
`refunds` folder in your working directory. The second writes the export.
Use a new output name for another run.

<!-- gnd-run expect=0 -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/refunds', 'refunds', dirs_exist_ok=True)"
gnd export ossie refunds/model.orm.yaml --out refunds.ossie.yaml
```

The export writes five files:

<!-- gnd-run expect=0 output=stdout -->
```sh
ls refunds.ossie.yaml*
```

```text
refunds.ossie.yaml
refunds.ossie.yaml.gnd.json
refunds.ossie.yaml.loss.json
refunds.ossie.yaml.mapping.yaml
refunds.ossie.yaml.semantic_model.yaml
```

| File | What it gives you |
|---|---|
| `refunds.ossie.yaml` | The ontology you can share with an Ossie reader. |
| `refunds.ossie.yaml.semantic_model.yaml` | The tables, columns, keys and links between tables that would hold the model's facts. |
| `refunds.ossie.yaml.mapping.yaml` | Which table and column holds each concept and relationship of the ontology. |
| `refunds.ossie.yaml.gnd.json` | The GND details needed to restore the original model, including the policy about refund amounts. |
| `refunds.ossie.yaml.loss.json` | A list of source fields and how the export handled each one. |

## Read the relationship

The output relationship `refund_by` is many-to-one. One customer can
request several refunds. Each refund has at most one requesting customer.

<!-- gnd-run expect=0 output=stdout -->
```sh
sed -n '10,16p' refunds.ossie.yaml
```

```text
  - name: refund_by
    verbalizes:
    - '{Refund} is requested by {Customer:customer}'
    roles:
    - concept: Customer
      name: customer
    multiplicity: ManyToOne
```

![Each refund has at most one requesting customer.](../assets/applications/refund-requester.svg)

## See the tables

Because each refund has at most one requesting customer, the customer sits
in a column of the refund's own table. The column may be empty, since the
model does not say every refund has a requester. The table's key is the
refund number.

<!-- gnd-run expect=0 output=stdout -->
```sh
sed -n '6,18p' refunds.ossie.yaml.semantic_model.yaml
```

```text
- name: refund
  source: refund
  primary_key:
  - refund_no
  fields:
  - name: refund_no
    expression:
      sql: '"REFUND_NO"'
    datatype: Integer
  - name: customer_customer_code
    expression:
      sql: '"CUSTOMER_CUSTOMER_CODE"'
    datatype: String
```

The model does not say that a refund has only one amount or one payment
channel. So those two facts each get a table of their own, `refund_amount`
and `refund_channel`, linked back to `refund`. If your business has one
amount per refund, say so in the model and the amount moves into the refund
table.

These tables are GND's reading of the model. They are not tables you have
built, and each one is marked `"source_kind":"logical"` to say so. To
describe the tables you did build, see
[Describe your delivered tables](describe-delivered-tables-for-ossie.md).

## Check what the tables do not carry

Tables can hold facts and keys. They cannot hold every rule. The mapping
file lists each fact type and rule of the model with where it is carried, or
the reason it is not. This command prints the ones that are not:

<!-- gnd-run expect=0 output=stdout -->
```sh
grep -o '"id":"[a-z_/0-9]*","kind":"[a-z_]*","reason":"[a-z-]*"' refunds.ossie.yaml.mapping.yaml
```

```text
"id":"constraints/0","kind":"constraint","reason":"not-relational"
```

That one entry is the policy about refund amounts. It is a rule over values,
which a table definition cannot express, so it travels in the sidecar. The
[Ossie explanation](../explanation/ossie.md#what-is-listed-instead-of-mapped)
describes the reasons you can meet.

## Restore the model

<!-- gnd-run expect=0 -->
```sh
gnd import ossie refunds.ossie.yaml --out restored.orm.json
gnd diff refunds/model.orm.yaml restored.orm.json
```

| File | What it gives you |
|---|---|
| `restored.orm.json` | The restored GND model. |
| `restored.orm.json.loss.json` | The import report, including whether the restored model matched the source identity. |

The diff reports the same model identity for both files and compares
each of the two rules in both directions. For a GND restore, keep the
sidecar and loss report with an exact copy of the original ontology.
Reformatting the ontology changes the bytes the sidecar verifies. Import
reads the ontology and its two companions. It does not read the semantic
model or the mapping.

## Share the ontology alone

If your partner wants only the vocabulary, add `--ontology-only`. The run
writes the ontology, the sidecar and the loss report, as GND did before it
wrote tables.

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd export ossie refunds/model.orm.yaml --out vocabulary.yaml --ontology-only >/dev/null
ls vocabulary.yaml*
```

```text
vocabulary.yaml
vocabulary.yaml.gnd.json
vocabulary.yaml.loss.json
```

An export never overwrites a file. Running the first export again stops with
exit code 11 and writes nothing, because its files already exist:

<!-- gnd-run expect=11 -->
```sh
gnd export ossie refunds/model.orm.yaml --out refunds.ossie.yaml
```

## Before you share another model

Check the loss report and the mapping's list before sharing. For example, a
model's example data is omitted and listed as refused. Add `--strict` to stop
the export if any source field would be refused. A very large model can
exceed the size limit of a file; the
[explanation](../explanation/ossie.md#large-models) says how to raise it.

[Read the Ossie interchange scope](../explanation/ossie.md).
