# Find the rule your auditors are really using

A shop's refund policy says one thing: **a refund should not be more than
1000**. Its auditors read one week of refunds from each of the shop's eight
stores and flagged four of those weeks. The written rule explains only two of
the four. So the auditors are applying a rule nobody wrote down.

On this page you'll find that rule from the auditors' labels, let GND check
every claim made about it, and add it to the model as an advisory rule. All the
data is synthetic.

!!! info "Files on GitHub"

    - [`refunds/model.orm.yaml`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/refunds/model.orm.yaml): the model and the written rule
    - [`refunds/batches/`](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/examples/refunds/batches): one week of refunds from each store
    - [`refunds/labels.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/refunds/labels.json): the auditors' verdicts
    - [`refunds/stand_in_learner.py`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/refunds/stand_in_learner.py): the example's stand-in rule learner (not a GND command)
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/tutorials/learn-rules.md)

## What you'll do

| Who | Does what |
|---|---|
| The auditors | mark each store's week **clean** or **flagged** |
| GND | scores the written rule against those verdicts, and suggests rules from a clean week |
| A rule learner | looks for a rule that separates flagged weeks from clean ones |
| GND | re-checks the learner's rule on every week before it believes it |
| You | read the suggestions and decide which become part of the model |

Nothing becomes a rule because a program found it. GND writes every suggestion
as a **proposal**, and only you can accept one.

## The data

Here are the eight weeks. Each number is one refund.

| Store | Refunds that week | The auditors said |
|---|---|---|
| north | 40, 120, 75 | clean |
| south | 500, 60, 230 | clean |
| east | 310, 90 | clean |
| west | 450, 35, 180 | clean |
| harbor | **1200**, 80 | flagged |
| market | **750**, 140, 55 | flagged |
| airport | **1500**, 260 | flagged |
| station | **640**, 95 | flagged |

Look at the bold numbers. Every flagged week has a refund above 500, and no
clean week does. With eight weeks a person can spot that; with eight hundred,
or with patterns that span customers and payment methods, nobody can. That
search is what a rule learner is for. This page lets one find the pattern and
then shows how GND checks it.

**Before you start.** Set GND up as the [course planner's "Before you
start"](course-planner.md#what-youll-build) shows. In an empty folder, copy the
example and check the model:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/refunds', '.', ignore=shutil.ignore_patterns('__pycache__'), dirs_exist_ok=True)"
gnd validate model.orm.yaml
```

```text
OK: model.orm.yaml is a valid GND ORM model
```

The model knows refunds, the customer who asked for each, its amount and how it
was paid. It holds the written rule with the policy's own words as its source.
The rule is **advisory**: breaking it gives a warning, not an error.
`labels.json` holds the auditors' verdicts, each tied to the exact bytes of the
week it judged, so a verdict can't silently drift onto changed data.

## 1. How good is the written rule?

**You ask** GND to score the rule against the auditors' verdicts:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd measure model.orm.yaml --labels labels.json | grep fired_on
```

```text
      fired_on_negative=2/4 fired_on_positive=0/4 silent_on_negative=2/4 silent_on_positive=4/4 vacuous=0/8 unchecked=0/8
```

GND counts weeks. In its words "negative" is a flagged week and "positive" a
clean one, so `fired_on_negative=2/4` means the rule fired on two of the four
flagged weeks. **GND says**, in business terms:

| | Flagged weeks | Clean weeks |
|---|---|---|
| The rule fired | 2 of 4 (harbor, airport) | 0 of 4 |
| The rule stayed quiet | 2 of 4 (market, station) | 4 of 4 |

The written rule never accuses a clean store, which is good. But it lets half
the flagged weeks through: market's 750 and station's 640 are under 1000.

## 2. Ask a rule learner what the auditors see

GND packs the labelled weeks into files a rule learner can read. A learner
such as [Popper](https://github.com/logic-and-learning-lab/Popper) can use them
directly. This page uses a small stand-in instead, so it runs anywhere with
nothing to install. `stand_in_learner.py` is the example's own program, not part
of GND. It tries 40 simple rules of the form "a week is wrong when it has a
refund above (or below) some amount", and keeps the fewest that explain every
flagged week without touching a clean one.

**You type**

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd export ilp model.orm.yaml --labels labels.json --target neutral --out ilp > /dev/null
python stand_in_learner.py ilp learned
```

```text
searched 40 rules; 4 hold in some flagged batch and in no clean one
learned: wrong(A) :- f_refund_amount(A,V0,V1), V1 > 500   covers harbor, market, airport, station
```

**The learner says:** a week is wrong when one of its refunds is over 500.
That's the `learned:` line in the learner's notation, where `V1` is the refund
amount. It claims the rule covers all four flagged weeks.

## 3. GND checks the learner's work

A learner's report is only a claim. GND brings the rule back as a proposal, and
first checks it on every week itself.

**You type**

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd import ilp-rules model.orm.yaml learned/learned.clauses.json --labels labels.json --reported-coverage learned/learned.run.json --target neutral --out learned.proposal.json --requested-at 2026-10-26T00:00:00+00:00
```

```text
IMPORTED 1 learned clauses -> learned.proposal.json
  clause 0 constraints[1]: covers 4 (support 4/4), vacuous 0, unchecked 0
```

**GND says** the claim holds. It ran the rule on all eight weeks: it covers
exactly the four flagged ones (support 4/4), the same weeks the learner named.

| Rule | Flagged weeks caught | Clean weeks accused |
|---|---|---|
| The written rule: at most 1000 | 2 of 4 | 0 of 4 |
| The learned rule: at most 500 | **4 of 4** | 0 of 4 |

GND writes the learned rule as "a refund amount is at most 500" in
`learned.proposal.json`. Nothing in the model has changed yet.

## 4. A learner that overstates its rule

Learners have bugs, and run reports get edited by hand. Here the stand-in plays
a faulty learner: it also claims the rule covers the clean `north` week.

<!-- gnd-run expect=0 output=stdout -->
```sh
python stand_in_learner.py ilp faulty --also-claim north
```

```text
searched 40 rules; 4 hold in some flagged batch and in no clean one
learned: wrong(A) :- f_refund_amount(A,V0,V1), V1 > 500   covers harbor, market, airport, station
deliberate mistake: also claiming that rule 0 covers north
```

<!-- gnd-run expect=3 output=stderr -->
```sh
gnd import ilp-rules model.orm.yaml faulty/learned.clauses.json --labels labels.json --reported-coverage faulty/learned.run.json --target neutral --out faulty.proposal.json --requested-at 2026-10-26T00:00:00+00:00
```

```text
clause 0: coverage-mismatch: GND covers [] that the learner did not report, and the learner reports ['north'] that GND does not cover; vacuous [], unchecked []
```

**What went wrong:** the learner said the rule covers `north`. North's
largest refund is 120, so a rule about refunds over 500 can't cover it.

**How GND caught it:** GND doesn't count, it compares. It ran the rule on every
week, listed the weeks the rule really covers, and set that list beside the
learner's. They differed by one week, `north`, so GND refused with exit 3 and
wrote no proposal. A rule only reaches you with a claim GND has reproduced.

## 5. What does a clean week say on its own?

The learner needs verdicts. GND can also suggest rules from a single clean week,
with no verdicts at all. Here it reads south's week and looks for two kinds of
rule: "each X has exactly one Y" and "every X has a Y".

**You type**

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd discover model.orm.yaml batches/south.yaml --families uniqueness,mandatory --out discovered.json --report discover-report.json --actor reader --requested-at 2026-10-26T00:00:00+00:00 | grep -E "^(EMITTED|SUPPRESSED)"
```

```text
EMITTED 10
SUPPRESSED declared=1 spanning-uniqueness=3
```

**GND says** ten rules held in that week. It left out four more: one is
already in the model (each refund has one customer), and three are true of any
list of facts, so they say nothing. Read in plain English, the ten fall into
three groups:

| Suggested rule | What to make of it |
|---|---|
| Each refund has one amount. Each refund is paid one way. | sensible: worth accepting |
| Every refund has a customer, an amount and a payment method. | sensible: worth accepting |
| Each customer asks for at most one refund. No two refunds have the same amount. | **accidents**: true of three refunds in one week, false in general |
| Every customer, amount and payment method in the file belongs to some refund. | how the week's file is written, not a business rule |

This is why discovery writes proposals, not rules. A small sample makes
accidents look like laws, and only someone who knows the business can tell
them apart. [Discovering constraints](../reference/discover.md) explains how
GND finds them and the five other kinds of rule it can look for.

## 6. Review and decide

Before you accept anything, GND shows what each proposal would change:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd evolve preview model.orm.yaml discovered.json --workspace . --records records --out discovered.preview.json | grep breaking
gnd evolve preview model.orm.yaml learned.proposal.json --workspace . --records records --out learned.preview.json | grep breaking
```

```text
  breaking: false
  breaking: false
```

**GND says** neither proposal changes or removes anything already in the
model; each only adds rules. You decide to accept the learned rule and leave
the discovered proposal for a closer look.

**You type**

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd evolve apply model.orm.yaml learned.proposal.json --preview learned.preview.json --workspace . --records records > /dev/null
grep -o "\[from induced.*" model.verbalization.txt | sed "s/ source=.*//"
```

```text
[from induced, proposed; modality=deontic] If refund_amount(refund = $v_v0, amount = $v_v1), then $v_v1 is at most 500.
```

**GND says** the model now holds the rule, in its own words: if a refund has an
amount, that amount is at most 500. It is marked **induced** (a program found
it) and **proposed** (no one has confirmed it yet), and it is advisory. The
model also records where it came from: the learner's name, the four weeks it
covers, and the exact files the claim was checked against.

Check the market week again, the one the written rule missed:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check model.orm.yaml batches/market.yaml | grep -A1 ADVISORY
```

```text
ADVISORY (deontic)
  [warning] constraints[1]: Guarded comparison consequent evaluated over bindings=3 — violated by bindings: {'$v_v0': '601', '$v_v1': '750'}.
```

`constraints[1]` is the new rule. Refund 601, for 750, now gets a warning. The written rule is still there, and
still quiet about it. If a later review confirms the new rule, a refund over
500 is something the shop warns about everywhere the model is used.

With an assistant, you'd do this step by asking the `gnd-model-evolve` skill:

```text
/gnd:gnd-model-evolve Review learned.proposal.json and discovered.json with me. Preview both, explain each rule in plain English, and apply only the ones I accept.
```

## What you did

| Step | What happened | Who checked it |
|---|---|---|
| 1 | the written rule caught 2 of the 4 flagged weeks | `gnd measure`, against the auditors' verdicts |
| 2 | a learner found "a refund over 500 is wrong" | nobody yet: a learner's claim |
| 3 | the rule covered exactly the four flagged weeks | `gnd import ilp-rules` re-ran it on every week |
| 4 | an overstated claim was refused | the same import, comparing week by week |
| 5 | one clean week suggested ten rules, two of them accidents | `gnd discover`; you sort them |
| 6 | you accepted the learned rule; market's 750 now gets a warning | `gnd evolve`, then `gnd check` |

## What this does not establish

- **That the learned rule is right.** It fits these eight weeks. A rule that
  fits labelled examples can still be wrong on weeks nobody has labelled. GND
  checks that claims about the rule are exact, not that the rule is wise.
- **That the auditors were right.** GND measures a rule against their verdicts;
  it can't tell you whether the verdicts were correct.
- **Anything about a real learner.** The stand-in is not Popper. The [ILP
  bridge](../reference/ilp-bridge.md) describes what a real learner reads and
  writes; this page has not run one.
