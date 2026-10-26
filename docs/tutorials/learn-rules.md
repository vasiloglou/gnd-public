# Learn rules from labelled data

A shop has a written rule: a refund should not be more than 1000. Auditors
checked one week of refunds from each of its eight stores, and marked each
store's batch **clean** or **flagged**. This page asks what the labels say about the rule,
and whether a better rule is hiding in them. You will:

1. score the written rule against the auditors' labels;
2. ask GND which constraints one clean batch suggests;
3. export the labelled batches for a rule learner, run one, and bring its rule
   back, with GND checking every claim the learner makes;
4. preview both sets of proposals as a model change.

Nothing on this page changes the model. Every rule found here arrives as
**proposed** and **advisory**, and admitting it is your reviewed step in
`gnd evolve`.

!!! info "Files on GitHub"

    - [`refunds/model.orm.yaml`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/refunds/model.orm.yaml): the model and its written rule
    - [`refunds/batches/`](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/examples/refunds/batches): the eight batches (synthetic data)
    - [`refunds/labels.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/refunds/labels.json): the auditors' labels
    - [`refunds/stand_in_learner.py`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/refunds/stand_in_learner.py): the example's stand-in learner (not a GND command)
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/tutorials/learn-rules.md)

## Before you start

Set GND up first as the [course planner's "Before you start"](course-planner.md#what-youll-build)
shows: this page needs a GND newer than the 0.1.0 release, installed from a
checkout, and `python` must be that environment's Python. Work in an empty
folder. The first command copies the example into it from the installed
package and checks the model.

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/refunds', '.', ignore=shutil.ignore_patterns('__pycache__'), dirs_exist_ok=True)"
gnd validate model.orm.yaml
```

```text
OK: model.orm.yaml is a valid GND ORM model
```

The model has refunds, the customer who asked for each, its amount and how it
was paid. The written rule is a `guarded` constraint: for every refund amount,
the amount is at most 1000. It is **deontic**: a broken one is a warning, not
an error.

`labels.json` lists the eight batches, each bound by its SHA-256 so the labels
cannot silently point at changed data. It marks each batch `positive` (the
auditors' clean) or `negative` (flagged), and says the written rule should fire
on the flagged ones. [Measuring host labels](../reference/measure-labels.md)
defines the format.

## 1. Score the rule you have

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd measure model.orm.yaml --labels labels.json
```

```text
REDACTION applied:
MEASUREMENT model.orm.yaml [labels=class] populations=8
WORK 16 (ceiling 24)
  constraints[0] [guarded/deontic] fires_on=negative
      fired_on_negative=2/4 fired_on_positive=0/4 silent_on_negative=2/4 silent_on_positive=4/4 vacuous=0/8 unchecked=0/8
```

The first line says redaction is on; this model redacts nothing. Each cell is
a count over batches, with its denominator:

- `fired_on_negative=2/4`: the rule fired on only two of the four flagged
  batches;
- `silent_on_positive=4/4`: it stayed quiet on every clean batch;
- `silent_on_negative=2/4`: two flagged batches got past it.

The written rule never accuses a clean batch, but it misses half the flagged
ones. The auditors are seeing something the rule does not say.

## 2. Discover what one clean batch suggests

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd discover model.orm.yaml batches/south.yaml --families uniqueness,mandatory --out discovered.json --report discover-report.json --actor reader --requested-at 2026-10-26T00:00:00+00:00
```

```text
GND DISCOVER
MODEL model.orm.yaml
POPULATION batches/south.yaml
EMITTED 10
  fact_types[refund_by].constraints[1] uniqueness support=3
  fact_types[refund_amount].constraints[0] uniqueness support=3
  fact_types[refund_amount].constraints[1] uniqueness support=3
  fact_types[refund_channel].constraints[0] uniqueness support=3
  fact_types[refund_by].constraints[2] mandatory support=3
  fact_types[refund_by].constraints[3] mandatory support=3
  fact_types[refund_amount].constraints[2] mandatory support=3
  fact_types[refund_amount].constraints[3] mandatory support=3
  fact_types[refund_channel].constraints[1] mandatory support=3
  fact_types[refund_channel].constraints[2] mandatory support=2
NEAR MISSES 0
REJECTED vacuous=0 unchecked=0 fail=0 warning=1
SUPPRESSED declared=1 spanning-uniqueness=3
WORK total=50
PROPOSAL discovered.json
```

`gnd discover` proposes constraints that hold in this batch. It keeps a
candidate only when `gnd check` passes it with support above zero, and only
when the model does not already declare or imply it. `SUPPRESSED declared=1`
is the model's own uniqueness rule, found again and not proposed twice.

Some of these hold only by accident. The first line says each customer asks
for at most one refund, and the third says no two refunds have the same
amount. Both are true of three refunds in one week and probably false in
general. That is why discovery writes **proposals**, not
rules: `discovered.json` is a `gnd evolve` proposal whose constraints are
`induced`, `proposed` and `deontic`. The `--families` option keeps this page
short; without it, discovery tries all seven families. [Discovering
constraints](../reference/discover.md) has the details.

## 3. Export the batches for a rule learner

An inductive logic programming (ILP) learner looks for rules that separate the
flagged batches from the clean ones. GND writes the batches in a form a learner
can read:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd export ilp model.orm.yaml --labels labels.json --target neutral --out ilp
```

```text
EXPORTED 8 examples and 60 facts to ilp (neutral)
export_sha256 2d36bb264d71feca2fd990452f1bb84d719e058c17120244bd82450a346c137f
work 68 (ceiling 500008)
```

`ilp/neutral.json` holds one fact per refund row, tagged with its batch, plus
which batches are flagged. `export_sha256` is the digest of `ilp/export.json`.
Everything the learner later claims is bound to it. `--target popper` would
also write files for the [Popper](https://github.com/logic-and-learning-lab/Popper)
learner.

## 4. Run a learner

This page uses a stand-in instead of a real learner, so it runs anywhere with no
install. `stand_in_learner.py` is the example's own program, not a GND command
and not Popper. It tries 40 simple rules of the form "a batch is wrong when one
of its refunds has an amount above (or below) some value". It keeps those that
fit some flagged batch and no clean one, then picks the fewest that cover every
flagged batch.

<!-- gnd-run expect=0 output=stdout -->
```sh
python stand_in_learner.py ilp learned
```

```text
searched 40 rules; 4 hold in some flagged batch and in no clean one
learned: wrong(A) :- f_refund_amount(A,V0,V1), V1 > 500   covers harbor, market, airport, station
```

It wrote `learned/learned.clauses.json`, the rule in GND's neutral clause form,
and `learned/learned.run.json`, the batches the learner **claims** the rule
covers.

## 5. Bring the rule back

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd import ilp-rules model.orm.yaml learned/learned.clauses.json --labels labels.json --reported-coverage learned/learned.run.json --target neutral --out learned.proposal.json --requested-at 2026-10-26T00:00:00+00:00
```

```text
IMPORTED 1 learned clauses -> learned.proposal.json
  clause 0 constraints[1]: covers 4 (support 4/4), vacuous 0, unchecked 0
```

GND does not take the learner's word for anything:

- it recomputes the export digest and checks that the run record names it;
- it rewrites the learned clause as a guarded constraint;
- it checks that constraint against every batch itself;
- it compares the set of batches it covers with the set the learner reported.

Here the sets agree: the rule covers all four flagged batches (support 4/4)
and no clean one. The rule the learner found is "a refund over 500 is wrong",
so GND proposes "a refund amount is at most 500".

## 6. A claim GND does not reproduce

Now suppose a learner over-claims: it says the rule also covers the clean
`north` batch. This Python snippet writes that claim:

<!-- gnd-run expect=0 -->
```python
import json
run = json.load(open("learned/learned.run.json"))
run["coverage"][0]["covered"].insert(0, "north")
open("learned/overclaimed.run.json", "w").write(json.dumps(run, indent=1) + "\n")
```

<!-- gnd-run expect=3 output=stderr -->
```sh
gnd import ilp-rules model.orm.yaml learned/learned.clauses.json --labels labels.json --reported-coverage learned/overclaimed.run.json --target neutral --out overclaimed.proposal.json --requested-at 2026-10-26T00:00:00+00:00
```

```text
clause 0: coverage-mismatch: GND covers [] that the learner did not report, and the learner reports ['north'] that GND does not cover; vacuous [], unchecked []
```

**What went wrong:** the learner's report and the data disagree. `north` holds
no refund over 500, so the rule cannot cover it.

**How GND caught it:** GND checked the rule on `north` itself, found it holds
there, and compared sets rather than counts. It refused with exit 3 and wrote
nothing. A learner that miscounts, or a run record edited by hand, cannot get a
rule into a proposal.

## 7. Preview both proposals

`gnd evolve preview` shows what each proposal would change, without changing
anything:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd evolve preview model.orm.yaml discovered.json --workspace . --records records --out discovered.preview.json
```

```text
PREVIEW 9ed28afa3d064a8fd5613900cd349f220f75fda075bedd0e02d2c1f785cfdd43
  proposal: b6110ad862402561bf0a4c70885b76162123b60c8277d9cff527e433b910665a
  before: 00fdeab3cb764decdf87c95619b4c315f8dbee8be2170ceea7722a91b6d27440
  candidate: c7abff3a0e8484a992cfaef15319b3aa07225c26a9bd8f109714d0399a41db58
  blast-radius: 7b2135b64cf635808de686c46bc8f1fa230d6da982072ad4141a25fa4ebcf8f7
  breaking: false
  affected: fact_types[refund_amount].constraints[mandatory:new:0]
  affected: fact_types[refund_amount].constraints[uniqueness:new:0]
  affected: fact_types[refund_by].constraints[mandatory:new:0]
  affected: fact_types[refund_by].constraints[uniqueness:new:0]
  affected: fact_types[refund_channel].constraints[mandatory:new:0]
  affected: fact_types[refund_channel].constraints[uniqueness:new:0]
```

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd evolve preview model.orm.yaml learned.proposal.json --workspace . --records records --out learned.preview.json
```

```text
PREVIEW ad84a556fbc06b88e10c18b4bdc908bf8bb15b58cf70ed05c7dcad260da66f56
  proposal: 3355696729503356c40c04512cb588c0620ec6a2f5e486becb6d808ebd385c96
  before: 00fdeab3cb764decdf87c95619b4c315f8dbee8be2170ceea7722a91b6d27440
  candidate: 6bf5890e4ff072a3707e3511395e820fdb69d4423b6753ea55758a60c98f09da
  blast-radius: 0c9c75cfb076dbab104ae7197d3e53fe9769a40b7e1b3a5a44df403de4e7cb3b
  breaking: false
  affected: model.constraints[guarded:new:0]
```

Each `affected:` line names a place where the proposal adds constraints:
the ten discovered ones land in six places, the learned one in one.
`breaking: false` means no existing element changes. The preview carries the candidate model's full
verbalization. This Python snippet prints the learned rule from it:

<!-- gnd-run expect=0 output=stdout -->
```python
import json
text = json.load(open("learned.preview.json"))["verbalization"]["text"]
print(next(line.split(" source=")[0] for line in text.splitlines() if "[from induced" in line))
```

```text
[constraint:model:guarded:75cc21ac8125e58fc46e8aec6e3f7333bc064c44ca8dc9dee6f834093173d6df:0] [from induced, proposed; modality=deontic] If refund_amount(refund = $v_v0, amount = $v_v1), then $v_v1 is at most 500.
```

The rule is marked `induced` and `proposed`. Its provenance records which
batches it covers, its support, the learner's name and version, and the
digests of the export, the clauses and the run record. To admit it, you apply
the proposal with `gnd evolve apply`. Confirming it later takes a recorded
review ([Evolving a model](../guides/evolution-and-recovery.md)).

## What this does not establish

- **That the learned rule is true.** It fits these eight batches. A rule that
  fits the labelled examples can still be wrong on data nobody has labelled.
  GND checks that the learner's claims are exact, not that the rule is right.
- **That the discovered constraints are true.** Each held in one batch of three
  refunds.
- **Anything about a real learner.** The stand-in is not Popper. The [ILP
  bridge](../reference/ilp-bridge.md) describes the contract a real learner
  meets; this page has not run one.
