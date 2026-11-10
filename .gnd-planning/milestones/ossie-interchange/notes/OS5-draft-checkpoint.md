# Early review copy — Share a refund model as an Ossie ontology

A shop records who requested each refund, the amount and the payment
channel. Its GND model says each refund can be requested by at most one
customer. Export the model to share those concepts and relationships with
a tool that reads the Apache Ossie ontology layer.

```sh
gnd export ossie src/gnd/examples/refunds/model.orm.yaml --out refunds.ossie.yaml
```

The ontology describes the refund-to-customer relationship with
`multiplicity: ManyToOne`. This gives the reader the same direction as the
business rule. Several refunds can refer to one customer, and each refund
has at most one customer.

```yaml
name: refund_by
verbalizes:
  - '{Refund} is requested by {Customer:customer}'
roles:
  - concept: Customer
    name: customer
multiplicity: ManyToOne
```

The command also writes `refunds.ossie.yaml.gnd.json` and
`refunds.ossie.yaml.loss.json`. The sidecar retains GND-specific details
such as the source's deontic refund-limit policy. The report tells you
which source elements are projected, retained or refused. For an example
with sample rows, export the growth model and inspect the report.

```sh
gnd export ossie src/gnd/examples/growth/model.orm.yaml --out growth.ossie.json --format json
```

Its report records seven refused pointers under
`/fact_types/0/sample_population`. The sample population stays outside the
ontology. Add `--strict` when that refusal should stop publication.

This checkpoint shows the closed OS1 output. The validator and parser
passed the selected oracle gate over all 38 eligible examples. The
interchange target is Apache Ossie ontology version 0.3.0.dev0 at
`ee89dbdc2844d8b7d293ed42c8613928bb99505f`, with the parser at
`83ddc294c8840f5f497a2bdbec2348a128fc2254`. A consumer can read the
ontology independently. PyRel is optional.

[OS1 evidence](../009-phase-OS1.md)
