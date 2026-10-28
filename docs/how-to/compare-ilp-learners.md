# Compare the rule learners on real runs

GND's [ILP bridge](../reference/ilp-bridge.md) exports a model's data for a
rule learner and imports what the learner found as an evolve proposal. It has
one adapter per learner. This page replays each adapter's real, committed
learner output through `gnd`, so you can see what each learner proposed and
what GND did with it. No learner is installed or run here: the learners ran
once each, during development, and their outputs ship with GND.

Each block runs in the project's tests, and the output shown is the output of
a real run. The [comparison table](../reference/ilp-bridge.md#comparing-the-learners)
summarizes every row.

!!! info "Files on GitHub"

    - [`refunds/`](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/examples/refunds): the refunds example, its labelled weeks and `learners/`, one folder per labelled learner
    - [`staffing/`](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/examples/staffing): a small unlabelled population for the rule miner, and its `learners/`
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/how-to/compare-ilp-learners.md)

## Before you start

Set GND up as the [course planner's "Before you start"](../tutorials/course-planner.md#what-youll-build)
shows. In an empty folder, copy the two examples. Use a new empty folder for
every run of this page: the commands refuse to overwrite their own outputs.

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import gnd, pathlib, shutil; root = pathlib.Path(gnd.__file__).parent / 'examples'; shutil.copytree(root / 'refunds', '.', ignore=shutil.ignore_patterns('__pycache__'), dirs_exist_ok=True); shutil.copytree(root / 'staffing', 'staffing')"
mkdir export
gnd validate model.orm.yaml
gnd validate staffing/model.orm.yaml
```

```text
OK: model.orm.yaml is a valid GND ORM model
OK: staffing/model.orm.yaml is a valid GND ORM model
```

The refunds example is the one from
[Find the rule your auditors are really using](../tutorials/learn-rules.md):
eight weeks of refunds, four flagged by the auditors. The rule every learner
is after is "a week is wrong when it has a refund over 500".

Each learner's output comes with a run record, `run.json`, in which the
learner states which weeks each rule covers. That is the learner's claim.
The import re-checks every claim against the labelled data and refuses the
whole set on the first rule it cannot reproduce or represent.

## 1. Popper

[Popper](https://github.com/logic-and-learning-lab/Popper) reads a Prolog
rendering of the export.

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd export ilp model.orm.yaml --labels labels.json --target popper --out export/popper
```

```text
EXPORTED 8 examples and 60 facts to export/popper (popper)
export_sha256 39788cf3c243b83715b448a42c99ba74b8315510be8954dd477dd6711e519493
work 68 (ceiling 500008)
```

Popper 5.0.1 was run three times, each with a different rendering:

- **Run 1, the run of record: rendering rejected.** Popper crashed after
  18 seconds. That rendering wrote "amount over 500" as a comparison with a
  constant, and this Popper version has no way to fill in a constant, so its
  arithmetic failed. Nothing was imported because there was nothing to import.
- **Run 2: no solution.** The second rendering defined the thresholds as
  rules. Popper finished but treated every threshold as useless and printed
  `NO SOLUTION`.
- **Run 3: admitted.** The third rendering, the one shipped and shown above
  (its digest is the one the run record binds), writes each threshold as a
  predicate of its own, such as `gt_t_amount__500`. Popper found the rule in about a second.

Runs 2 and 3 were extra runs the project owner approved after run 1 failed.
Run 3's program and run record are in `learners/popper/`:

<!-- gnd-run expect=0 output=stdout -->
```sh
cat learners/popper/program.pl
gnd import ilp-rules model.orm.yaml learners/popper/program.pl --labels labels.json --reported-coverage learners/popper/run.json --target popper --out popper.proposal.json --actor ilp-live --requested-at 2026-01-01T00:00:00Z --format text
```

```text
wrong(V0):- f_refund_amount(V0,V1,V2),gt_t_amount__500(V2).
IMPORTED 1 learned clauses -> popper.proposal.json
  clause 0 constraints[1]: covers 4 (support 4/4), vacuous 0, unchecked 0
```

The rule says a week is wrong when it has a refund whose amount is over 500.
It covers the four flagged weeks and no clean one, which is what Popper
claimed, so it is admitted as an advisory constraint in
`popper.proposal.json`.

## 2. ILASP

[ILASP](https://www.ilasp.com/) reads an answer-set-programming rendering.

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd export ilp model.orm.yaml --labels labels.json --target ilasp --out export/ilasp
```

```text
EXPORTED 8 examples and 60 facts to export/ilasp (ilasp)
export_sha256 1acb801053b0491a86a393bcce88f482a7431ca62051c9bb6c13f3eab7228a5e
work 68 (ceiling 500008)
```

ILASP 4.4.1 ran once, for about two minutes, and finished:

<!-- gnd-run expect=3 output=stderr -->
```sh
cat learners/ilasp/hypothesis.las
gnd import ilp-rules model.orm.yaml learners/ilasp/hypothesis.las --labels labels.json --reported-coverage learners/ilasp/run.json --target ilasp --out ilasp.proposal.json --actor ilp-live --requested-at 2026-01-01T00:00:00Z --format text
```

```text
clause 0: empty-antecedent: nothing is left for the antecedent
```

**Why it was refused.** ILASP's answer is `wrong :- gt_t_amount(V1,500).`:
"wrong when some amount is over 500". It never says which week the amount
belongs to; the rule names no refund at all. ILASP prefers it because it is
the shortest rule that fits. **How GND caught it.** The import turns a rule
into a constraint over the model's fact types. A comparison is only a test on
a value some fact supplies; with no fact in the rule, nothing is left to
check, so the import refuses with `empty-antecedent` (exit 3) and writes no
proposal.

## 3. A language model

The `llm` adapter has no rendering of its own. GND writes a prompt from the
neutral export, and an agent answers with clauses in GND's own JSON form. The
run used Claude Code.

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd export ilp model.orm.yaml --labels labels.json --target neutral --out export/neutral
```

```text
EXPORTED 8 examples and 60 facts to export/neutral (neutral)
export_sha256 f758a077383a450ea0716ad9056802feb0b5083d185813da5227ed0711417f77
work 68 (ceiling 500008)
```

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd import ilp-rules model.orm.yaml learners/llm/answer.json --labels labels.json --reported-coverage learners/llm/run.json --target llm --out llm.proposal.json --actor ilp-live --requested-at 2026-01-01T00:00:00Z --format text
```

```text
IMPORTED 1 learned clauses -> llm.proposal.json
  clause 0 constraints[1]: covers 4 (support 4/4), vacuous 0, unchecked 0
```

The model proposed "wrong when a refund is at least 640", a different
threshold that separates the weeks just as well on this data. A language
model's answer is not repeatable, so this row is one sample.

## 4. A rule-set learner

The `rules` adapter flattens the export into a feature table for
[wittgenstein](https://github.com/imoscovitz/wittgenstein)'s RIPPER.

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd export ilp model.orm.yaml --labels labels.json --target rules --out export/rules
```

```text
EXPORTED 8 examples and 60 facts to export/rules (rules)
export_sha256 7b455e99b224d1c7ab41fd2bcfdd1eb10914e795f57d2dd8e5b1c0494a2e5827
work 68 (ceiling 500008)
```

<!-- gnd-run expect=0 output=stdout -->
```sh
cat learners/rules/ruleset.txt; echo
gnd import ilp-rules model.orm.yaml learners/rules/ruleset.txt --labels labels.json --reported-coverage learners/rules/run.json --target rules --out rules.proposal.json --actor ilp-live --requested-at 2026-01-01T00:00:00Z --format text
```

```text
[[f_refund_amount__2__3__gt_t_amount__450=1]]
IMPORTED 1 learned clauses -> rules.proposal.json
  clause 0 constraints[1]: covers 5 (support 4/5), vacuous 0, unchecked 0
```

RIPPER chose 450, not 500, so its rule also fires on one clean week (south).
It said so in its run record, GND's re-check agrees, and the rule is admitted
with that measured coverage: 5 weeks, 4 of them flagged. The constraint is
advisory, so reviewing it is where a person decides whether 450 is right.
RIPPER picks other thresholds on other runs; this is the run of record.

## 5. A rule miner, on unlabelled data

[AMIE](https://github.com/dig-team/AMIE) mines rules from facts with no
labels: "whenever these facts hold, that fact holds too". The refunds weeks
have no relations of the shape it mines, so its runs use a small staffing
population instead: who works in which team, where each team sits, and where
each person is based and parks.

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd export ilp staffing/model.orm.yaml --population staffing/population.yaml --target amie --out export/amie
```

```text
EXPORTED 65 facts in 4 relations to export/amie (amie); skipped 2 fact types
export_sha256 d7756509f96fd4b9e4449b53a004fb77d5f1a831378a958c5e1122958ca435f3
```

AMIE 4.0.0's run of record used its defaults and mined 8 rules:

<!-- gnd-run expect=3 output=stderr -->
```sh
gnd import mined-rules staffing/model.orm.yaml staffing/learners/amie/rules.txt --population staffing/population.yaml --reported staffing/learners/amie/reported.json --target amie --out amie.proposal.json --actor ilp-live --requested-at 2026-01-01T00:00:00Z --format text
```

```text
rule 0: does-not-hold: 19 of 20 head pairs hold; only rules that hold are admitted (D11 (o))
```

**Why it was refused.** AMIE reports rules that hold most of the time. Its
first rule, "whoever is based at a site parks there", is true for 19 of the
20 people; one person parks elsewhere. **How GND caught it.** The import
counts every rule on the population itself. A rule becomes a constraint, and
a constraint with an exception is not a rule the data supports, so GND admits
only rules that hold for every case. The first one that does not refuses the
whole set (exit 3). Of the 8 mined rules, 2 hold.

A second run, approved by the project owner, asked AMIE for only rules with
no exceptions (`-enstd -minc 1`, standard confidence 1):

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd import mined-rules staffing/model.orm.yaml staffing/learners/amie-2/rules.txt --population staffing/population.yaml --reported staffing/learners/amie-2/reported.json --target amie --out amie-2.proposal.json --actor ilp-live --requested-at 2026-01-01T00:00:00Z --format text
```

```text
IMPORTED 2 mined rules -> amie-2.proposal.json
  rule 0 constraints[0]: holds on 5 of 5 head pairs
  rule 1 constraints[1]: holds on 20 of 20 head pairs
```

These are the two rules that held in the first run: a team sits where its
members are based, and a person in a team is based at the team's site.

## What the comparison shows

- Every learner was run once, under one setting, on one small example. The
  rows say what happened on that run, not which learner is better.
- The three labelled learners that produced a usable rule found the same
  pattern with different thresholds: 500 (Popper), 640 (the language model)
  and 450 (RIPPER). GND measured each one's coverage itself; RIPPER's 450
  also catches a clean week.
- Two refusals came from GND, not from the learners: ILASP's rule names no
  refund, and AMIE's first run reported rules with exceptions. In both cases
  GND wrote nothing.

The full table, with every count, is in
[Comparing the learners](../reference/ilp-bridge.md#comparing-the-learners).
