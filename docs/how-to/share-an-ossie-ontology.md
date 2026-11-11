# Share a refund model as an Ossie ontology

Your team records who requested each refund, how much it was for, and how
it was paid. A partner wants the same vocabulary for their reporting tool.
Share the ontology so both teams use the same relationships. Keep the
sidecar when a GND user needs to recover the original rules.

!!! info "Files on GitHub"

    [Refunds example model](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/refunds/model.orm.yaml)

From the GND repository, give the `/gnd` skill this prompt:

> Export the refunds example as an Ossie ontology. Show how the output
> represents who requested a refund. Then import it and compare the
> restored model with the original.

Run these commands in the repository:

```sh
gnd export ossie src/gnd/examples/refunds/model.orm.yaml --out refunds.ossie.yaml
gnd import ossie refunds.ossie.yaml --out restored.orm.json
gnd diff src/gnd/examples/refunds/model.orm.yaml restored.orm.json
```

The output relationship `refund_by` is many-to-one. One customer can
request several refunds. Each refund has at most one requesting customer.

![Each refund has at most one requesting customer.](../assets/applications/refund-requester.svg)

| File | What it gives you |
|---|---|
| `refunds.ossie.yaml` | The ontology you can share with an Ossie reader. |
| `refunds.ossie.yaml.gnd.json` | The GND details needed to restore the original model, including the policy about refund amounts. |
| `refunds.ossie.yaml.loss.json` | A list of source fields and how the export handled each one. |

The diff reports the same model identity for both files. It also reports
that each version contains the same two rules. Keep the ontology and its
companion files together if a recipient plans to import it into GND.

For other models, check the loss report before sharing. For example, a
model's example data can be omitted and listed as refused. Add `--strict`
to stop export if any source field would be refused.

[Read the Ossie interchange scope](../explanation/ossie.md).
