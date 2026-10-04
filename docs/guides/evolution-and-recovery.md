# Change a model, or recover one from code

Choose evolution when a valid model already exists. Choose recovery when the
application exists but its conceptual rules have not been captured in a GND
model. They have different inputs and evidence: a change proposal is not a
recovered-code inventory.

## Evolve an existing model

A requirement such as “each expense must record its currency” can affect the
model, populations, generated tools, application commands, and tests. Start by
identifying those consequences rather than editing the final YAML in place.

The evolution workflow records a closed proposal with a complete candidate
model and explicit `add`, `modify`, `rename`, or `delete` operations. Unchanged
constraints keep their provenance. Renames and deletions require a reviewed
blast radius and explicit acceptance of its exact identity.

After authoring a proposal using the
[evolution contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-model-evolve/references/evolution-contract.md),
use these contextual commands from its authoritative workspace:

```sh
gnd evolve preview model.orm.yaml proposal.json --workspace . --records records --out preview.json --format json
```

Inspect candidate validation, verbalization, every declared affected artifact,
and linked-project impact. Preview publishes an immutable review artifact; it
does not replace the model. After accepting the proposal and any required
breaking-change digest, apply that exact preview:

```sh
gnd evolve apply model.orm.yaml proposal.json --preview preview.json --workspace . --records records --format json
```

Apply revalidates against current bytes, publishes the model through
compare-and-swap, and completes the verbalization, linked conformance checks,
and immutable record. Exit `13` can mean that the model was published and a
linked project now drifts; it does not mean the model was rolled back. Read
the output before deciding what to regenerate.

If interruption leaves pending finalization, use the exact pending identity
reported by the command with `gnd evolve finalize`; do not start a second
evolution or reconstruct the pending file. This completes the original
transaction. It does not author another model change.

Follow the [expense chapters](../expense/01-model.md) for a concrete currency
change. After evolution, explicitly select code generation if needed, adapt
extension behavior, and rerun the affected examples and application tests.

## Recover a model from an existing repository

Recovery is a bounded, one-time static pass over explicitly chosen roots.
The inventory command does not import the application or run its tests. Use
source, tests, documentation, configuration, and schemas as evidence, and
retain disagreements between them rather than treating code as unquestionable
domain truth.

The following contextual invocation assumes the named directories exist:

```sh
gnd recovery inventory . --source src --tests tests --docs docs --out recovery-inventory.json
```

An agent using `gnd-model-from-code` reads that inventory, authors the model
and full verbalization, and records evidence and uncertainty in
`model.recovery.json`. You review the interpretation. Then verify the bundle:

```sh
gnd recovery verify . model.recovery.json --model model.orm.yaml --verbalization model.verbalization.txt
```

Verification rechecks the selected-path census, digests, locators, model, and
verbalization. It establishes the recorded recovery evidence, not that every
possible source file was included or that runtime behavior was executed.
There is no watcher or continuous code-to-model synchronization.

For an explicit GSD migration, `gnd-adopt` adds imported requirement mapping
and a manual cleanup checklist around recovery. Select that skill separately.
See [agent skills](agent-skills.md) and the
[recovery contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-model-from-code/references/recovery-contract.md)
for bounded scope, exclusions, ambiguity, and output requirements.
