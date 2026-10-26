# The commands behind "Find the rule your auditors are really using"

[Find the rule your auditors are really using](../tutorials/learn-rules.md)
tells the refunds story with Claude Code prompts and plain-English results.
This page holds the exact `gnd` commands behind every number on it. Each block
runs in the project's tests, and the output shown is the output of a real run.

!!! info "Files on GitHub"

    - [`refunds/model.orm.yaml`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/refunds/model.orm.yaml): the model and the written rule
    - [`refunds/batches/`](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/examples/refunds/batches): one week of refunds from each store
    - [`refunds/labels.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/refunds/labels.json): the auditors' verdicts
    - [`refunds/stand_in_learner.py`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/refunds/stand_in_learner.py): the example's stand-in rule learner (not a GND command)
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/how-to/learn-rules-commands.md)

## Before you start

Set GND up as the [course planner's "Before you start"](../tutorials/course-planner.md#what-youll-build)
shows. In an empty folder, copy the example and check the model:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/refunds', '.', ignore=shutil.ignore_patterns('__pycache__'), dirs_exist_ok=True)"
gnd validate model.orm.yaml
```

```text
OK: model.orm.yaml is a valid GND ORM model
```

## 1. Score the written rule against the verdicts

`gnd measure` reads the auditors' verdicts in `labels.json` and counts, for
each rule, the weeks it fired on. In its words "negative" is a flagged week and
"positive" a clean one.

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd measure model.orm.yaml --labels labels.json | grep fired_on
```

```text
      fired_on_negative=2/4 fired_on_positive=0/4 silent_on_negative=2/4 silent_on_positive=4/4 vacuous=0/8 unchecked=0/8
```

The written rule fired on 2 of the 4 flagged weeks and on no clean week.
[Measuring host labels](../reference/measure-labels.md) defines every field.

## 2. Export the weeks and run a learner

`gnd export ilp` writes the labelled weeks in a form a rule learner can read.
A learner such as [Popper](https://github.com/logic-and-learning-lab/Popper)
can use that export directly. The example ships a small stand-in learner
instead, so the walk runs with nothing to install. It tries 40 simple rules of
the form "a week is wrong when it has a refund above (or below) some amount"
and keeps the fewest that explain every flagged week without touching a clean
one.

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd export ilp model.orm.yaml --labels labels.json --target neutral --out ilp > /dev/null
python stand_in_learner.py ilp learned
```

```text
searched 40 rules; 4 hold in some flagged batch and in no clean one
learned: wrong(A) :- f_refund_amount(A,V0,V1), V1 > 500   covers harbor, market, airport, station
```

`V1` is the refund amount. The learner claims the rule covers the four flagged
weeks. That is its claim; the next command checks it.

## 3. Re-check the learner's claim

`gnd import ilp-rules` runs the learned rule on every week itself and writes a
`gnd evolve` proposal only when its own coverage equals the learner's.

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd import ilp-rules model.orm.yaml learned/learned.clauses.json --labels labels.json --reported-coverage learned/learned.run.json --target neutral --out learned.proposal.json --requested-at 2026-10-26T00:00:00+00:00
```

```text
IMPORTED 1 learned clauses -> learned.proposal.json
  clause 0 constraints[1]: covers 4 (support 4/4), vacuous 0, unchecked 0
```

## 4. Refuse an overstated claim

With `--also-claim north`, the stand-in plays a faulty learner that also claims
the rule covers the clean north week.

<!-- gnd-run expect=0 output=stdout -->
```sh
python stand_in_learner.py ilp faulty --also-claim north
```

```text
searched 40 rules; 4 hold in some flagged batch and in no clean one
learned: wrong(A) :- f_refund_amount(A,V0,V1), V1 > 500   covers harbor, market, airport, station
deliberate mistake: also claiming that rule 0 covers north
```

GND compares the weeks it covers with the weeks the learner reported. They
differ by `north`, so the import exits 3 and writes no proposal.

<!-- gnd-run expect=3 output=stderr -->
```sh
gnd import ilp-rules model.orm.yaml faulty/learned.clauses.json --labels labels.json --reported-coverage faulty/learned.run.json --target neutral --out faulty.proposal.json --requested-at 2026-10-26T00:00:00+00:00
```

```text
clause 0: coverage-mismatch: GND covers [] that the learner did not report, and the learner reports ['north'] that GND does not cover; vacuous [], unchecked []
```

The [ILP bridge](../reference/ilp-bridge.md) defines the export, the import
and this refusal.

## 5. Suggest rules from one clean week

`gnd discover` reads one population and proposes the rules that hold in it.
Here it looks for two kinds: "each X has exactly one Y" (uniqueness) and
"every X has a Y" (mandatory).

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd discover model.orm.yaml batches/south.yaml --families uniqueness,mandatory --out discovered.json --report discover-report.json --actor reader --requested-at 2026-10-26T00:00:00+00:00 | grep -E "^(EMITTED|SUPPRESSED)"
```

```text
EMITTED 10
SUPPRESSED declared=1 spanning-uniqueness=3
```

Ten rules held. Four more were left out: one is already declared in the model
and three hold in any list of facts. [Constraint discovery](../reference/discover.md)
explains the families and the suppression rules.

## 6. Preview, apply, and check a week again

Both proposals only add rules, so neither is breaking:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd evolve preview model.orm.yaml discovered.json --workspace . --records records --out discovered.preview.json | grep breaking
gnd evolve preview model.orm.yaml learned.proposal.json --workspace . --records records --out learned.preview.json | grep breaking
```

```text
  breaking: false
  breaking: false
```

Apply the learned proposal and read the new rule back in the model's own words:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd evolve apply model.orm.yaml learned.proposal.json --preview learned.preview.json --workspace . --records records > /dev/null
grep -o "\[from induced.*" model.verbalization.txt | sed "s/ source=.*//"
```

```text
[from induced, proposed; modality=deontic] If refund_amount(refund = $v_v0, amount = $v_v1), then $v_v1 is at most 500.
```

The market week, which the written rule let through, now gets a warning on
refund 601 for 750:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check model.orm.yaml batches/market.yaml | grep -A1 ADVISORY
```

```text
ADVISORY (deontic)
  [warning] constraints[1]: Guarded comparison consequent evaluated over bindings=3 — violated by bindings: {'$v_v0': '601', '$v_v1': '750'}.
```

`constraints[1]` is the new rule. With an assistant, step 6 is the
[gnd-model-evolve](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-model-evolve/SKILL.md)
skill's work; the other steps are plain requests that Claude Code carries out
with the commands above.
