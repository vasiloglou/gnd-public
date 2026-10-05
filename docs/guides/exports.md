# Explain a derivation or export a bounded model

A concrete derived fact may deserve an explanation: why is a destination
reachable, or why is a particular item eligible? A finite witness records
the premises and rule applications for a requested tuple. Standalone exports
serve another purpose: inspecting or evaluating a supported fragment with
an explicitly selected external tool.

## Produce and replay a finite witness

The [Python reference](../reference/python-api.md#witness-explain-one-derived-fact-with-a-finite-proof)
contains a complete runnable route proof using packaged inputs. A request
names the fact type and typed tuple in the model's role order. The following
is the same request shape, shown as data rather than an executable command:

```json
{
  "version": 1,
  "targets": [{
    "fact_type": "dispatch_reachable",
    "tuple": [
      {"primitive": "String", "value": "WH-A"},
      {"primitive": "String", "value": "DEST-D"}
    ]
  }]
}
```

After saving a request and choosing its matching model/population, contextual
CLI commands are:

```sh
gnd witness model.orm.json candidate.pop.json --targets targets.json
gnd witness model.orm.json candidate.pop.json --targets targets.json --raw --out route-certificate.json
gnd replay model.orm.json candidate.pop.json route-certificate.json --json
```

The first command displays a value-redacted view. The second explicitly
publishes a raw certificate to a new destination. The third replays that
certificate with an independent finite inference kernel. A displayed witness
view, including an expanded view, is not replayable input.

Read every target status. Exit `0` requires every requested tuple to be
proved. Missing, unknown, or unsupported targets use band `2`; invalid input
uses `3`; bounded work refusal uses `4`. An invalid proof uses `1`. A missing
witness is not an absence theorem, and a proof for one tuple does not prove
that every required tuple was produced.

Positive range-restricted derivations and finite grounded recursion are
supported in the witness profile. Negative premises, aggregates, opaque rules,
semiderived claims, unsupported numeric primitives, and expression trees are
outside that profile. The checker can support a construct that the proof lane
does not.

## Choose an export by the question it can answer

For complete inputs, real native execution, developer-owned source and explained
failures, follow [release governance across PyRel, Soufflé and Lean](../runtimes/scenario.md).

| Export | Intended artifact | Separate next step |
|---|---|---|
| Souffle | A bounded standalone derivation program and fixed facts | Verify bundle, then explicitly select native execution |
| Lean | Finite definitions, propositions, and unproved obligation templates | Verify bundle, then optionally compile/elaborate |
| PyRel | A standalone program for the supported translation profile | Provision the selected runtime and execute independently |

An export is not a universal translation of every GND feature. Souffle's
profile includes positive recursion, stratified negation, and a bounded
distinct-count form; it excludes constraint evaluation and operations.
The Lean finite profile is positive and acyclic and supports a selected
constraint subset; it refuses unsupported constructs instead of omitting them.
Consult the exact profile before choosing an exporter.

These commands are contextual and require a supported model/population. They
render and verify a new raw bundle; they do not run a compiler:

```sh
gnd export souffle model.orm.yaml candidate.pop.json --raw --out souffle-bundle
gnd export souffle-verify souffle-bundle --json
gnd export lean model.orm.yaml candidate.pop.json --toolchain leanprover/lean4:v4.34.0 --raw --out lean-bundle --json
gnd export lean-verify lean-bundle --json
```

## Keep tool execution and proof claims explicit

`souffle-run`, `souffle-witness`, and `lean-compile` require separately
provisioned supported tools and an explicit invocation. Merely installing a
tool never activates it during `validate` or `check`.

Lean output includes `ProofObligations.lean` with explicitly unproved templates.
Successful compilation or stub elaboration does not discharge those theorems.
Witness replay establishes the selected finite inference against bound inputs;
it does not establish source truth, completeness, or higher assurance. Raw
bundles contain source values, so publish them only for an audience permitted
to see those values.

Use the [export boundary](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-export/references/export-contract.md)
for exact fragments, tool pins, refusal bands, and resource ceilings, and the
[certificate contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-export/references/witness-contract.md)
for finite proof semantics.
