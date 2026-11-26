# Find the rule your auditors are really using

A shop's refund policy says **no refund over 1000**. Its auditors looked at one
week of refunds from each of eight stores and flagged four weeks. The written
rule explains only two of them. So the auditors are applying a rule nobody has
written down.

On this page you ask Claude Code to find that rule, let GND check every claim
made about it, and add it to the model as an advisory rule. You type a prompt
for the `gnd-induce` skill; under each prompt is a recording of Claude Code
doing the work. All the data is synthetic.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="Eight weeks of refunds, two rules">

![Each dot is one refund, placed by amount. The clean weeks north, south, east and west never go over 500. The flagged weeks harbor 1200, market 750, airport 1500 and station 640 each have a refund over 500. The written rule, over 1000, catches only harbor and airport. The learned rule, over 500, catches all four flagged weeks and no clean week.](../assets/applications/refunds-weeks.svg)
</div>

*Source: the shipped refunds example and the auditors' verdicts in
`labels.json`. The replays are real recorded runs of Claude Code with Haiku over
that example, recorded on 2026-11-26. The
[commands page](../how-to/learn-rules-commands.md) shows every command with the
output of a real run.*

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
| You | type the prompts, read the answers, decide |
| Claude Code | runs the `gnd-induce` skill, and the `gnd-model-evolve` skill when the model changes |
| A rule learner | looks for a rule that separates flagged weeks from clean ones |
| GND | scores rules, re-checks the learner's claims, and refuses what it cannot reproduce |

Nothing becomes a rule because a program found it. GND writes every suggestion
as a **proposal**, and only you can accept one.

!!! info "Files on GitHub"

    - [`refunds/model.orm.yaml`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/refunds/model.orm.yaml): the model and the written rule
    - [`refunds/batches/`](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/examples/refunds/batches): one week of refunds from each store
    - [`refunds/labels.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/refunds/labels.json): the auditors' verdicts
    - [`refunds/stand_in_learner.py`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/refunds/stand_in_learner.py): the example's stand-in rule learner (not a GND command)
    - [`gnd-induce`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-induce/SKILL.md): the skill's instructions
    - [`gnd-model-evolve`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-model-evolve/SKILL.md): the skill's instructions
    - [`refunds/skill-sessions/`](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/examples/refunds/skill-sessions): the recordings behind the replays
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/tutorials/learn-rules.md)

**Before you start.** Install GND from PyPI as the [installation page](../installation.md)
shows, or from a checkout of the repository for unreleased work on `main`, as the [course planner's "Before you start"](course-planner.md#what-youll-build)
shows. Add the Claude Code plugin as the [plugin page](../marketplace-plugins.md)
shows, then copy the `refunds` example into an empty folder.

The
[commands page](../how-to/learn-rules-commands.md) has the copy step, and shows
every command with the output of a real run. The replays on this page are real
recorded runs of Claude Code with Haiku over the shipped example, recorded on
2026-11-26. The example's README states the rule the data hides, and the
recorded Claude Code read it; the stand-in learner found the rule from the
data alone. Your own run will word things differently; GND's verdicts should
be the same.

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

## How to read a replay

Each replay is one recorded conversation. It shows only the first line of
each result; the full output is in the recording files linked under "Files on
GitHub". Three kinds of trouble can show up in one, and each note below says
which is which:

| What you see | What it is |
|---|---|
| **refused by Claude Code's permission rules** | a limit of the recording. The recording let Claude Code run GND commands, the stand-in learner and `shasum` (a checksum tool), plus the read-only commands Claude Code permits on its own, such as `ls`, `cat` and `cd`. A command in a form that allow list did not cover was refused: for example, one that also printed the previous command's exit status, ran a loop or ran an inline Python script. Haiku then ran the plain command again or read the file another way. Nothing is wrong with the data or the rule. |
| a wrong or surprising step by Haiku | a model's mistake or shortcut. The note says what it was. |
| **Exit code 3** from GND | GND refusing something it could not reproduce. This is the check the page is about. |

Each replay on this page has at most two messages from the reader. The second
one tells Claude Code who to record a proposal as, and when. The skill never takes a
name from the computer; it asks you.

## 1. How good is the written rule?

**You type**

```text
/gnd:gnd-induce Score the written refund rule against the auditors' verdicts in
labels.json. How many flagged weeks does it catch, and does it ever accuse a
clean week?
```

**You answer**

```text
Record it as reader, at 2026-10-26T00:00:00+00:00. Write every output in this folder.
```

<figure class="gnd-replay" tabindex="0" role="region" aria-label="Replay: Claude Code (Haiku) scores the written refund rule (recorded run 1)">
--8<-- "docs/assets/replays/refunds-score-haiku-run-1.svg"
</figure>

??? note "Transcript of the replay"

    ```text
    --8<-- "docs/assets/replays/refunds-score-haiku-run-1.txt"
    ```

**In this run.** Haiku ran GND's measure over the eight weeks and the verdicts.
GND's report opens with "REDACTION applied:" and then nothing: that line names
the parts of the data whose values the model asks GND to hold back, and this
model names none.

The score
followed, and Haiku read it correctly: the rule fired on 2 of the 4 flagged
weeks and on none of the 4 clean ones. The second message named who to record
the work as. Haiku answered that scoring writes no proposal, so there was
nothing to record, and it wrote nothing extra.

Two commands were refused by
Claude Code's permission rules: each also printed the previous command's exit status,
a form the recording's allow list did not cover. That is a limit of the
recording, not a mistake GND caught, and Haiku ran each plain command again.

One small departure from the skill: it says to ask who to record the work as
before the first command that writes anything, and Haiku wrote the score's
output file, `measure.json`, in its first turn. That file is not a proposal,
and the name is recorded only on proposals.

**GND says**

| The written rule: no refund over 1000 | Flagged weeks | Clean weeks |
|---|---|---|
| fired | 2 of 4 (harbor, airport) | 0 of 4 |
| stayed quiet | 2 of 4 (market, station) | 4 of 4 |

Good news: the rule never accuses a clean store. Bad news: it lets half the
flagged weeks through. Market's 750 and station's 640 are below 1000.

## 2. Ask a rule learner what the auditors see

**You type**

```text
/gnd:gnd-induce Export the labelled weeks for a rule learner, run the stand-in
learner on them, and tell me the rule it finds. Don't import it yet.
```

The skill asks GND to pack the labelled weeks into files a learner can read,
then runs the example's stand-in learner on them. A real learner such as
[Popper](https://github.com/logic-and-learning-lab/Popper) reads the same
files. The stand-in tries 40 simple rules of the form "a week is wrong when it
has a refund above (or below) some amount". From those that touch no clean
week, it picks a small set, one rule at a time, until every flagged week is
explained.

<figure class="gnd-replay" tabindex="0" role="region" aria-label="Replay: Claude Code (Haiku) runs the stand-in learner (recorded run 1)">
--8<-- "docs/assets/replays/refunds-learn-haiku-run-1.svg"
</figure>

??? note "Transcript of the replay"

    ```text
    --8<-- "docs/assets/replays/refunds-learn-haiku-run-1.txt"
    ```

**In this run.** Haiku exported the eight weeks, ran the stand-in learner
under a two-minute time limit, and reported the learner's rule: a refund over
500, covering harbor, market, airport and station. It said the claim was still
unchecked and imported nothing, as asked.

Three commands were refused by
Claude Code's permission rules (a loop over the week files, and two commands
that also printed the previous command's exit status); that is a limit of
the recording, and Haiku read the files another way or ran the plain command
again.

One small departure from the skill: it says to ask who to record the work as
before the first command that writes anything. Haiku wrote the export and the
learner's output in its first turn, and said it would ask only when a proposal
is written. Nothing it wrote was a proposal, and the name is recorded only on
proposals.

The learner's own printout
is not in this replay. The recorder keeps the output only of a command that is
the learner or GND on its own. Haiku started the learner under the time limit
and joined two file-printing commands onto it, so its printout was dropped.
GND's printout for the export was dropped the same way: that command was
joined to a change of folder and a file listing. The same learner's printout
is in step 4's replay ("searched 40 rules").

The recorded conversation had a second turn, and the replay stops
before it. That second turn belongs to the recording script, not to this
step: it gave the name to record as and described the faulty learner. The
first turn had said "Don't import it yet". Haiku imported anyway in the second
turn and tried both claims: GND accepted the
honest one and refused the faulty one. Steps 3 and 4 show
those two imports in their own recordings.

**The learner says**

> A week is wrong when one of its refunds is over 500. This covers harbor,
> market, airport and station.

That is the learner's claim. Nobody has checked it yet.

## 3. GND checks the learner's work

This recording starts in a folder where the weeks are already exported and the
learner has already run, as in step 2.

**You type**

```text
/gnd:gnd-induce Bring the learned rule into GND as a proposal. Check its
coverage on every week before you believe the learner.
```

A proposal carries the name of the person who asked for it and the time. The
skill does not guess either one. It stops and asks, and you answer:

**You answer**

```text
Record it as reader, at 2026-10-26T00:00:00+00:00. Write every output in this
folder. The stand-in learner runs as python stand_in_learner.py EXPORT_DIR
OUT_DIR, with --also-claim north for the faulty learner.
```

<figure class="gnd-replay" tabindex="0" role="region" aria-label="Replay: Claude Code (Haiku) brings the learned rule into GND (recorded run 1)">
--8<-- "docs/assets/replays/refunds-import-haiku-run-1.svg"
</figure>

??? note "Transcript of the replay"

    ```text
    --8<-- "docs/assets/replays/refunds-import-haiku-run-1.txt"
    ```

**In this run.** First message: Haiku read the learner's output and the week
files and drew its own table of which weeks the rule covers. It said plainly
that this was its own reading, not GND's check, and then asked who to record
the proposal as and when.

Second message: GND re-ran the rule on all eight
weeks and agreed with the learner. It printed "IMPORTED 1 learned clauses" and
"covers 4 (support 4/4)", and wrote the proposal.

The second message also
described the faulty learner, so Haiku ran that too and tried to import its
claim. GND refused it, because of a coverage mismatch on north; step 4
shows that refusal on its own.

Three commands were refused by Claude Code's
permission rules (a loop over the week files, and two commands that also printed the previous command's
exit status); that is a limit of the recording, not something GND caught. Haiku
handed the proposal over for review and did not start `gnd-model-evolve`
itself.

**GND says** the claim holds. The rule covers exactly the four flagged weeks,
support 4 of 4, and no clean week. GND writes the rule into a proposal. In plain
English: **a refund amount is at most 500**. Nothing in the model has
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
/gnd:gnd-induce Run the stand-in learner again, this time as the faulty learner
that also claims north. Try to import what it produces.
```

**You answer**

```text
Record it as reader, at 2026-10-26T00:00:00+00:00. Write every output in this
folder. The stand-in learner runs as python stand_in_learner.py EXPORT_DIR
OUT_DIR, with --also-claim north for the faulty learner.
```

<figure class="gnd-replay" tabindex="0" role="region" aria-label="Replay: Claude Code (Haiku) tries to import a faulty learner's claim (recorded run 1)">
--8<-- "docs/assets/replays/refunds-faulty-haiku-run-1.svg"
</figure>

??? note "Transcript of the replay"

    ```text
    --8<-- "docs/assets/replays/refunds-faulty-haiku-run-1.txt"
    ```

**In this run.** Haiku first looked at the folder and asked who to record the
import as. After the answer it ran the faulty learner, which printed "searched
40 rules; 4 hold in some flagged batch and in no clean one", then its rule,
then "deliberate mistake: also claiming that rule 0 covers north". Haiku
passed that claim to GND unchanged.

GND refused the import:
"coverage-mismatch: ... the learner reports ['north'] that GND does not
cover". No proposal was written. Haiku reported the refusal as printed and did
not change the claim or try again.

Two commands were refused by Claude Code's
permission rules (one with an inline Python script attached, one that also
printed the previous command's exit status); that is a limit of the recording. GND's refusal of the import is the only
refusal here that comes from GND.

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

**Also recorded, not shown.** Three more conversations sit in the
[recordings folder](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/examples/refunds/skill-sessions).
One asks for a learner that is not installed: Haiku stopped with "no learner
named popper is installed". One starts in a folder where an output file
already exists. One says "Make the import pass" after the refusal above: Haiku
refused to change the learner's claim, then ran the honest learner and
imported that instead.

These runs were not tidy. In the first, Haiku asked the computer which
packages were installed and ran GND from outside the folder. In the last, it
looked outside the folder. Read the recordings before relying on them.

## 5. What does one clean week say on its own?

The learner needs verdicts. GND can also suggest rules from a single clean
week, with no verdicts at all.

**You type**

```text
/gnd:gnd-induce Look at south's week alone and suggest rules of two kinds:
"each X has exactly one Y" and "every X has a Y". Read each suggestion back to
me in plain English.
```

**You answer**

```text
Record it as reader, at 2026-10-26T00:00:00+00:00. Write every output in this folder.
```

<figure class="gnd-replay" tabindex="0" role="region" aria-label="Replay: Claude Code (Haiku) suggests rules from south's week (recorded run 1)">
--8<-- "docs/assets/replays/refunds-discover-haiku-run-1.svg"
</figure>

??? note "Transcript of the replay"

    ```text
    --8<-- "docs/assets/replays/refunds-discover-haiku-run-1.txt"
    ```

**In this run.** Haiku read south's week, then asked who to record the
proposal as before running anything that writes one. After the answer, GND's
discover ran on that one week and printed "EMITTED 10" and "SUPPRESSED
declared=1 spanning-uniqueness=3". Haiku read the ten suggestions back in
plain English and marked the same two as likely accidents that the table below
does.

Four commands were refused by Claude Code's permission rules: two also
printed the previous command's exit status, and two were inline Python scripts
over the proposal file. After the last refusal Haiku read the proposal file
directly. That is a limit of the recording, not a mistake GND caught.

It had two small costs, and Haiku said both: it
could not report GND's exit code, because the commands that would have
printed it were refused, and it left two parts of GND's report unexamined: one candidate
GND rejected with a warning, and the four it suppressed.

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

**Not recorded.** This review was not recorded in this tutorial's runs, which
record `gnd-induce` only. What follows, down to the re-check, comes from the
run on the [commands page](../how-to/learn-rules-commands.md), which is also
where the two file names in the prompt come from.

**GND says** neither proposal is breaking: each only adds rules, and nothing
already in the model changes or disappears. You accept the learned rule and
leave the discovered proposal for a closer look.

**You get** a model that holds the new rule. In plain English: *if a refund
has an amount, that amount is at most 500*. The rule carries three labels:

| Label | Meaning |
|---|---|
| **induced** | a program found it |
| **proposed** | no one has confirmed it yet |
| **advisory** | breaking it gives a warning, not an error |

The model also records where the rule came from: the learner's name, the four
weeks it covers, and a fingerprint (digest) of each file the claim was
checked against, so a later change to those files can be detected.

**Check the market week again**, the one the written rule missed. This
recording starts in a folder where the learned rule has already been applied,
by the commands page's steps.

**You type**

```text
/gnd:gnd-induce Check batches/market.yaml against the model again.
```

**You answer**

```text
Record it as reader, at 2026-10-26T00:00:00+00:00. Write every output in this folder.
```

<figure class="gnd-replay" tabindex="0" role="region" aria-label="Replay: Claude Code (Haiku) re-checks the market week (recorded run 1)">
--8<-- "docs/assets/replays/refunds-recheck-haiku-run-1.svg"
</figure>

??? note "Transcript of the replay"

    ```text
    --8<-- "docs/assets/replays/refunds-recheck-haiku-run-1.txt"
    ```

**In this run.** Haiku ran GND's check on market's week. GND found nothing
blocking and printed one advisory "[warning]": refund 601, for 750, breaks the
new rule. The totals were pass=2 fail=0 warning=1, so the written rule still
passes.

Two commands were refused by Claude Code's permission rules: one asked the
computer where GND is installed, in a form the recording's allow list did not
cover, and one also printed the previous command's exit status. That is a
limit of the recording, and Haiku ran the plain check again.

One small departure is Haiku's own. The
skill says a re-check writes nothing. After the second message Haiku saved the
check's output to a file and wrote a short notes file of its own beside it,
holding the name and time. Those notes are Haiku's, not a GND record, and
GND's verdict is the same either way.

**GND says**

| Market's week: 750, 140, 55 | Before | After |
|---|---|---|
| The written rule: at most 1000 | quiet | quiet |
| The learned rule: at most 500 | not in the model | **warning** on refund 601, for 750 |

"Before" is derived from step 1: the written rule did not fire on market, and
the learned rule was not in the model yet. "After" is the recording above.

The written rule is still there, and still quiet. If a later review confirms
the new rule, a refund over 500 is something the shop warns about everywhere
the model is used.

## What you did

| Step | What happened | You used | Who checked it |
|---|---|---|---|
| 1 | the written rule caught 2 of the 4 flagged weeks | `gnd-induce` | GND, against the auditors' verdicts |
| 2 | a learner found "a refund over 500 is wrong" | `gnd-induce` | nobody yet: a learner's claim |
| 3 | the rule covered exactly the four flagged weeks | `gnd-induce` | GND re-ran it on every week |
| 4 | an overstated claim was refused | `gnd-induce` | GND, comparing week by week |
| 5 | one clean week suggested ten rules, two of them accidents | `gnd-induce` | GND; you sort them |
| 6 | you accepted the learned rule; market's 750 now gets a warning | `gnd-model-evolve` to review (not recorded here), `gnd-induce` to re-check | GND, before and after the change |

The [commands behind this page](../how-to/learn-rules-commands.md) show
every GND command behind these prompts, with the output of a real run.

## What this does not establish

- **That the learned rule is right.** It fits these eight weeks. A rule that
  fits labelled examples can still be wrong on weeks nobody has labelled. GND
  checks that claims about the rule are exact, not that the rule is wise.
- **That the auditors were right.** GND measures a rule against their
  verdicts; it cannot tell you whether the verdicts were correct.
- **Anything about a real learner.** The stand-in is not Popper. The
  [ILP bridge](../reference/ilp-bridge.md) describes what a real learner
  reads and writes; this page has not run one.
- **That Claude Code always follows the skill.** Each conversation was
  recorded once, and three of the nine recorded conversations did not follow
  the skill fully. The `learn` conversation imported although the first turn
  said not to import yet. The unshown `absent-learner` conversation ran GND
  from outside the working folder. The unshown `make-it-pass` conversation
  looked outside the folder and did not end as the skill asks.
