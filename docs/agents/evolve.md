# Change the rules safely

Requirements change. When they do, the model changes first, deliberately, and GND
shows you what the change breaks before anything is published. The `gnd-model-evolve`
skill drives that process; it never edits `model.orm.yaml` in place.

## Ask your agent

```text
Use gnd-model-evolve. Our product owner now says genre fit is mandatory, not
advisory: promote preferred_genre from deontic to alethic. Write the proposal,
preview it, show me the blast radius, and wait for my approval before applying.
```

The agent writes a closed `proposal.json` made of explicit operations (*add*,
*modify*, *rename* or *delete*). Each operation names its target by a digest-bound
locator and states the exact before and after values. It never says "update the genre
rule".

## What GND checks

```sh
gnd evolve preview model.orm.yaml proposal.json --workspace . --records records --out preview.json
gnd evolve apply   model.orm.yaml proposal.json --preview preview.json --workspace . --records records
```

- **Preview** validates the proposal against the current model's digest and publishes
  one immutable review document. Its **blast radius** lists every element, population,
  generated project and piece of evidence the change touches, and whether the change is
  breaking. A rename or delete needs your explicit acceptance of the preview's exact
  `report_sha256`.
- **Apply** rechecks that nothing moved since the preview, publishes the new model with
  a compare-and-swap, rechecks every linked generated project, and writes the record.
  Exit **13** means the model *was* published and a linked project now drifts. It is not
  rolled back; it tells you what to regenerate.
- **Finalize** completes an interrupted apply idempotently.

## Why it matters: legal yesterday, illegal today

In [BookRec chapter 6](../bookrec/06-evolution.md), the same frozen recommendations
pass under the old model and fail under the new one. Not a byte of the output changed;
only the rule did. In [Expense chapter 3](../expense/03-evolution.md), adding a
required currency publishes the model and reports drift in the generated project
(exit 13) until it is deliberately regenerated. Both chapters run every command.

## Compare two versions directly

`gnd diff` compares two models over one vocabulary. It reports a bounded catalogue of
entailment comparisons between their constraints (where *undecided* is not a
counterexample) and, given populations, how each version judges those concrete
facts:

```sh
gnd diff old.orm.yaml new.orm.yaml --populations populations/
```

See [evolution and recovery](../guides/evolution-and-recovery.md) for the proposal
format, acceptance rules and every exit.

See it on an application: [BookRec chapter 7](../bookrec/07-native.md#7-change-a-rule-without-touching-the-query)
promotes a should-rule to a must-rule and [Expense chapter 4](../expense/04-native.md#7-change-a-rule-without-touching-the-query)
lowers a cap, both through a previewed proposal, and rerun the unchanged query.
