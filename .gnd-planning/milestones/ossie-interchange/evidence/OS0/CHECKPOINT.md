# OS0 checkpoint

[The GND refunds model](../../../../../src/gnd/examples/refunds/model.orm.yaml)
states that a refund is requested by a customer, has an amount and uses a
payment channel. Its uniqueness rule lets a refund identify at most one
customer. Its deontic rule says the amount should be at most 1,000.

[The hand-written Ossie document](refunds.yaml) uses identifying relationships
for refunds and customers. It uses `ManyToOne` for the requesting customer and
`Amount <= 1000` as a relationship-level `requires` formula. This illustrates
the formula's syntax. The GND modality would travel in the sidecar.

Both upstream readers accepted the document with exit 0. The offline converter
produced six concepts and five property or relationship declarations.
[The generated PyRel](E3-refunds.pyrel.txt) includes:

```python
Refund.refund_by = m.Property(f"{Refund} is requested by {Customer}")
Refund.refund_amount = m.Relationship(f"{Refund} is for {Amount}")
Refund.identify_by(Refund.nr)
```

The source contains zero `require` calls. That reproduces the limitation OS6
targets. Both tested RelationalAI versions produced byte-identical PyRel on
refunds and upstream Flights. [Validator and parser evidence](E5.json),
[RelationalAI 1.39.0](E3.json), [RelationalAI 2.0.1](E3b.json).
