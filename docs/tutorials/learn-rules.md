# Find the rule your auditors are really using

A shop's refund policy says **no refund over 1000**. Its auditors looked at one
week of refunds from each of eight stores and flagged four weeks. The written
rule explains only two of them. So the auditors are applying a rule nobody has
written down.

On this page you ask Claude Code to find that rule, let GND check every claim
made about it, and add it to the model as an advisory rule. You type requests;
GND does the checking. All the data is synthetic.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="Eight weeks of refunds, two rules">

![Each dot is one refund, placed by amount. The clean weeks north, south, east and west stay under 500. The flagged weeks harbor 1200, market 750, airport 1500 and station 640 each have a refund over 500. The written rule, over 1000, catches only harbor and airport. The learned rule, over 500, catches all four flagged weeks and no clean week.](../assets/applications/refunds-weeks.svg)
</div>

*Source: the shipped refunds example and the auditors' verdicts in
`labels.json`. Every number on this page comes from a real run of the
[commands behind it](../how-to/learn-rules-commands.md).*

On narrow screens, focus a diagram and scroll horizontally with arrow keys or touch.

## The result in one table

| | Flagged weeks caught | Clean weeks accused |
|---|---|---|
| The written rule: no refund over 1000 | 2 of 4 | 0 of 4 |
| The learned rule: no refund over 500 | **4 of 4** | 0 of 4 |

The rest of the page is how you get there, and how GND makes sure nobody,
human or program, slips a rule past you.

## Who does what

| Who | Does what |
|---|---|
| The auditors | mark each store's week **clean** or **flagged** |
| You | ask Claude Code, read the answers, decide |
| Claude Code | runs GND's commands, and the `gnd-model-evolve` skill when the model changes |
| A rule learner | looks for a rule that separates flagged weeks from clean ones |
| GND | scores rules, re-checks the learner's claims, and refuses what it cannot reproduce |

Nothing becomes a rule because a program found it. GND writes every suggestion
as a **proposal**, and only you can accept one.

!!! info "Files on GitHub"

    - [`refunds/model.orm.yaml`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/refunds/model.orm.yaml): the model and the written rule
    - [`refunds/batches/`](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/examples/refunds/batches): one week of refunds from each store
    - [`refunds/labels.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/refunds/labels.json): the auditors' verdicts
    - [`refunds/stand_in_learner.py`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/refunds/stand_in_learner.py): the example's stand-in rule learner (not a GND command)
    - [`gnd-model-evolve`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-model-evolve/SKILL.md): the skill's instructions
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/tutorials/learn-rules.md)

**Before you start.** Install GND and the Claude Code plugin as the
[plugin page](../marketplace-plugins.md) shows, then copy the `refunds`
example into an empty folder. The
[commands page](../how-to/learn-rules-commands.md) has the copy step and every
command Claude Code runs below. No prompt on this page is a recording; the
results are what GND printed when those commands ran.

## The data

Eight weeks, one per store. Each number is one refund.

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

With eight weeks you can see the pattern yourself: every flagged week has a
refund over 500, and no clean week does. With eight hundred weeks, or a pattern
that spans customers and payment methods, nobody can. That search is a rule
learner's job. Checking the learner is GND's.

## 1. How good is the written rule?

**You type**

```text
Score the written refund rule against the auditors' verdicts in labels.json.
How many flagged weeks does it catch, and does it ever accuse a clean week?
```

**Claude Code does** run GND's measure command over the eight weeks and the
verdicts. There is no skill for this step; it is one command.

**GND says**

| The written rule: no refund over 1000 | Flagged weeks | Clean weeks |
|---|---|---|
| fired | 2 of 4 (harbor, airport) | 0 of 4 |
| stayed quiet | 2 of 4 (market, station) | 4 of 4 |

Good news: the rule never accuses a clean store. Bad news: it lets half the
flagged weeks through. Market's 750 and station's 640 are under 1000.

## 2. Ask a rule learner what the auditors see

**You type**

```text
Export the labelled weeks for a rule learner, run the stand-in learner on them,
and tell me the rule it finds.
```

**Claude Code does** ask GND to pack the labelled weeks into files a learner
can read, then runs the example's stand-in learner on them. A real learner such
as [Popper](https://github.com/logic-and-learning-lab/Popper) reads the same
files. The stand-in tries 40 simple rules of the form "a week is wrong when it
has a refund above (or below) some amount" and keeps the fewest that explain
every flagged week without touching a clean one.

**The learner says**

> A week is wrong when one of its refunds is over 500. This covers harbor,
> market, airport and station.

That is the learner's claim. Nobody has checked it yet.

## 3. GND checks the learner's work

**You type**

```text
Bring the learned rule into GND as a proposal. Check its coverage on every
week yourself before you believe the learner.
```

**Claude Code does** ask GND to import the learned rule. GND does not take the
learner's word: it runs the rule on all eight weeks and compares what it finds
with what the learner reported.

**GND says** the claim holds. The rule covers exactly the four flagged weeks,
support 4 of 4, and no clean week. GND writes the rule into a proposal in its
own words: **a refund amount is at most 500**. Nothing in the model has
changed yet.

| Rule | Flagged weeks caught | Clean weeks accused |
|---|---|---|
| The written rule: at most 1000 | 2 of 4 | 0 of 4 |
| The learned rule: at most 500 | **4 of 4** | 0 of 4 |

## 4. A learner that overstates its rule

Learners have bugs, and run reports get edited by hand. Here the stand-in
plays a faulty learner: it also claims its rule covers the clean north week.

**You type**

```text
Run the stand-in learner again, this time as the faulty learner that also
claims north. Try to import what it produces.
```

**GND says** no.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="GND accepts only a claim it can reproduce">

![A faulty learner claims its rule covers north, harbor, market, airport and station. GND runs the rule on all eight weeks and covers harbor, market, airport and station; north's largest refund is 120, never over 500. One week differs, so the import is refused with exit 3 and no proposal is written.](../assets/applications/refunds-claim-check.svg)
</div>

**What went wrong:** the learner said the rule covers north. North's largest
refund is 120, so a rule about refunds over 500 cannot fire there.

**How GND caught it:** GND does not count, it compares. It ran the rule on
every week, listed the weeks the rule really covers, and set that list beside
the learner's. They differed by one week, north. GND refused the import and
wrote no proposal. A rule only reaches you with a claim GND has reproduced.

## 5. What does one clean week say on its own?

The learner needs verdicts. GND can also suggest rules from a single clean
week, with no verdicts at all.

**You type**

```text
Look at south's week alone and suggest rules of two kinds: "each X has exactly
one Y" and "every X has a Y". Read each suggestion back to me in plain English.
```

**Claude Code does** run GND's discover command on the south week. There is
no skill for this step; it is one command, and the proposal it writes is
reviewed in step 6 like any other.

**GND says** ten rules held in that week. It left out four more on its own:
one is already in the model (each refund has one customer), and three are true
of any list of facts, so they say nothing. Read in plain English, the ten fall
into three groups:

| How many | The suggested rules | What to make of them |
|---|---|---|
| 5 | Each refund has one amount. Each refund is paid one way. Every refund has a customer, an amount and a payment method. | **sensible**: worth accepting |
| 2 | Each customer asks for at most one refund. No two refunds have the same amount. | **accidents**: true of three refunds in one week, false in general |
| 3 | Every customer, amount and payment method in the file belongs to some refund. | **how the file is written**, not a business rule |

This is why discovery writes proposals, not rules. A small sample makes
accidents look like laws, and only someone who knows the business can tell
them apart. [Constraint discovery](../reference/discover.md) explains how GND
finds them and the five other kinds of rule it can look for.

## 6. Review and decide

Now the model changes, so the `gnd-model-evolve` skill takes over. It previews
each proposal, shows what it would change, and applies only what you accept.

**You type**

```text
/gnd:gnd-model-evolve Review learned.proposal.json and discovered.json with me.
Preview both, explain each rule in plain English, and apply only the ones I accept.
```

**Claude Code does** preview both proposals with GND, which checks that each
proposal still matches the model it was written against and reports its blast
radius.

**GND says** neither proposal is breaking: each only adds rules, and nothing
already in the model changes or disappears. You accept the learned rule and
leave the discovered proposal for a closer look.

**You get** a model that holds the new rule, in its own words: *if a refund
has an amount, that amount is at most 500*. The rule carries three labels:

| Label | Meaning |
|---|---|
| **induced** | a program found it |
| **proposed** | no one has confirmed it yet |
| **advisory** | breaking it gives a warning, not an error |

The model also records where the rule came from: the learner's name, the four
weeks it covers, and the exact files the claim was checked against.

**Check the market week again**, the one the written rule missed:

```text
Check batches/market.yaml against the model again.
```

**GND says**

| Market's week: 750, 140, 55 | Before | After |
|---|---|---|
| The written rule: at most 1000 | quiet | quiet |
| The learned rule: at most 500 | not in the model | **warning** on refund 601, for 750 |

The written rule is still there, and still quiet. If a later review confirms
the new rule, a refund over 500 is something the shop warns about everywhere
the model is used.

## What you did

| Step | What happened | You asked for | Who checked it |
|---|---|---|---|
| 1 | the written rule caught 2 of the 4 flagged weeks | a plain request | GND, against the auditors' verdicts |
| 2 | a learner found "a refund over 500 is wrong" | a plain request | nobody yet: a learner's claim |
| 3 | the rule covered exactly the four flagged weeks | a plain request | GND re-ran it on every week |
| 4 | an overstated claim was refused | a plain request | GND, comparing week by week |
| 5 | one clean week suggested ten rules, two of them accidents | a plain request | GND; you sort them |
| 6 | you accepted the learned rule; market's 750 now gets a warning | the `gnd-model-evolve` skill | GND, before and after the change |

The [commands behind this page](../how-to/learn-rules-commands.md) show
every GND command Claude Code runs for these requests, with the output of a
real run.

## What this does not establish

- **That the learned rule is right.** It fits these eight weeks. A rule that
  fits labelled examples can still be wrong on weeks nobody has labelled. GND
  checks that claims about the rule are exact, not that the rule is wise.
- **That the auditors were right.** GND measures a rule against their
  verdicts; it cannot tell you whether the verdicts were correct.
- **Anything about a real learner.** The stand-in is not Popper. The
  [ILP bridge](../reference/ilp-bridge.md) describes what a real learner
  reads and writes; this page has not run one.
