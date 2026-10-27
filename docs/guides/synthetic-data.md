# Explore a model with synthetic populations

Synthetic populations help you exercise a rule before real application data
exists. For a maximum amount, you want a normal amount, a boundary amount, and
an amount that exceeds the limit. GND can derive supported cases from the
model, retain their generation provenance, and measure the checker's behavior
on the resulting corpus.

## Choose useful cases

`gnd synth` has four classes:

| Class | Intended use |
|---|---|
| `conforming` | A baseline the checker accepts |
| `violating` | Mutations admitted only after the checker confirms the predicted finding |
| `boundary` | Cases derived from declared bounds, including empty-subject and unchecked frontiers |
| `all` | The combined generation selection |

Generation support is narrower than model validation. Some combinations have
no supported generation strategy. Inspect `not_derivable` and other refusal
details; do not silently count an ungenerated case as covered. In particular,
the current synth and measure consumers refuse temporal models. Source
anchoring requires a source document and is not evaluated by population-only
generation and measurement.

## Generate a small reproducible corpus

Install the optional `synth` extra for the selected GND distribution. If working
from a local wheel, request its extra in your install command. The following
commands are contextual: supply a supported model with meaningful constraints
and a fresh corpus directory.

```sh
gnd synth model.orm.yaml --out corpus --class all --seed 17 --seeds 1 --format json
gnd measure model.orm.yaml --populations corpus --format json --out rates.json
```

An explicit seed provides a reproducible generation choice. Omitting the seed
draws fresh entropy and records it so a particular variant can be regenerated.
An admitted value pool can be supplied with `--pool`; otherwise the generator
builds and records a Faker pool. Keep the index, population files, and
provenance sidecars together.

If you already have real populations and know what each should show, you can
skip generation and measure against your own labels with
`gnd measure model.orm.yaml --labels labels.json`. See
[Measuring host labels](../reference/measure-labels.md).
[Find the rule your auditors are really using](../tutorials/learn-rules.md)
walks the whole loop: score a rule against labels, learn a better one, and
propose it as a model change.

Start with one seed and inspect the facts. Are the relations populated? Does
the interesting join actually happen? Does the violating example isolate the
intended rule? Increase the sample count only after the baseline is useful.
More empty or irrelevant populations do not improve evidence.

## Read measurement per constraint

`measure` checks sidecar bindings before scoring and reports false-pass,
false-fail, and undecided rates separately, each with its own numerator and
conditional denominator. It does not turn them into one blended accuracy
score. A zero numerator over zero eligible cases cannot establish that the
checker handled that case family correctly.

The report is reproducible from its committed input artifacts. Changed
population bytes with stale provenance are an input refusal. A detected
checker/prediction disagreement is retained as a defect signal, not relabeled
to make the rate green. `--promote DIR` can copy defect-revealing cases and
print manifest rows for review; it does not append those rows on your behalf.

## Use the corpus in application work

Use selected cases as regression inputs, or bind them into an
[experiment session](experiments.md). Keep the expected outcome independent
of the candidate implementation. Synthetic coverage describes the generated
cases and supported operators; it does not certify source truth, model
completeness, or every future input.

For a small reversible feature, a focused hand-authored valid/invalid pair can
be enough. BookRec and the expense tutorial start with such understandable
fixtures. The command's live `gnd synth --help` and `gnd measure --help`, plus
the [session grounding guide](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-dev-session/SKILL.md),
define the current generation and evidence contract.
