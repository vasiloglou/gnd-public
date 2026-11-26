---
name: gnd-induce
description: Runs GND's induction loop over host-labelled populations and hands every proposal to review -- `gnd measure --labels` to score a model's rules against the host's labels, `gnd discover` to propose rules that hold in one population, `gnd export ilp` then `gnd import ilp-rules` to round-trip a rule learner the user names, with GND re-checking the learner's coverage claim, `gnd import mined-rules` for a rule miner over one unlabelled population, and `gnd check` to re-check a population after a rule is applied. Use when asked to "score our rules against the auditors' labels", "find the rule our reviewers are using", "suggest rules from this data", "run a rule learner", or "import learned rules". Every rule it produces is a proposal of induced, proposed, advisory constraints, reviewed and applied only through gnd-model-evolve; its reports stay reports. Not for judging the fact types `gnd discover --families fact-type` forms (gnd-judge-fact-types, gnd-model-multivalued), measuring a synth corpus (gnd-dev-session), derivation or Lean exports (gnd-export), applying or confirming a rule (gnd-model-evolve), or installing a learner.
---

# Induce rules from labelled data, and hand them to review

A host has a model and populations, and often a verdict on each population
from the people who know the business: an auditor's "flagged" or "clean", a
reviewer's "should have been refused". This skill runs GND's induction
commands over them and reports what GND printed. It has five intents:

| Intent | What you ask | What GND writes |
|---|---|---|
| **Score** | how well the model's rules agree with the host's labels | a measure report |
| **Discover** | which rules hold in one population | a discovery report and, when anything is emitted, an evolve proposal |
| **Learn** | what rule a learner the user names finds, checked by GND | the learner's inputs, then an evolve proposal only if GND reproduces the learner's coverage claim |
| **Re-check** | what a population says against the model after a change | nothing; the check output only |
| **Hand off** | review the proposals | nothing; a route to the review skill |

Nothing becomes a rule because a program found it. Every rule this skill
produces is **induced**, **proposed** and **advisory**, as
[provenance and modality](../gnd-orm-core/references/provenance-and-modality.md)
defines those words. Every proposal goes to [gnd-model-evolve](../gnd-model-evolve/SKILL.md); this skill never applies it.

## Fix the inputs first

Before any command, settle these with the user and say them back:

- **The model**, and either the **label manifest** (for score and learn) or
  the **population** (for discover, a rule miner and re-check). The label
  manifest's format is the read-only
  [label manifest schema](../gnd-orm-core/references/labels.schema.json);
  `gnd measure --help` names its modes. Labels come from the user.
- **The audit actor and the request time**, for every command that writes a
  proposal. Ask before the first command that writes anything, and wait for
  the answer: "Who should the proposal be recorded as, and at what time?"
  The actor is the user's answer, never a placeholder and never a name taken
  from git, the shell or the environment.
- **The working folder.** Every output path is in the folder the user works
  in: these files are the user's results, so write them there, never in a
  temporary or scratch folder. Read nothing outside the working folder but this
  skill's linked references.
- **New output paths.** Discover, export and both imports refuse an existing
  `--out` (exit 11). `gnd measure` overwrites its `--out` without warning, so
  confirm that the measure output path does not exist before you run it.

## Score

```sh
gnd measure MODEL --labels MANIFEST --out OUT
```

Report every cell GND printed for each rule, as printed, with its numerator
and denominator ("fired on 2 of 4 flagged populations"). The cells differ by
mode, and the [measure reference](https://github.com/vasiloglou/gnd-public/blob/main/docs/reference/measure-labels.md)
lists them: a class-mode manifest scores rules against classes, and an
expected-state manifest scores each population against its expected verdict.
In expected-state mode `gnd measure` exits 6 on a checker defect, which you
report as printed. It never combines measure cells into one accuracy number.

## Discover

```sh
gnd discover MODEL POPULATION --families uniqueness,mandatory --out PROPOSAL --report REPORT --actor ACTOR --requested-at TIMESTAMP
```

Choose `--families` with the user; `gnd discover --help` lists them. Report
the `EMITTED` and `SUPPRESSED` counts as printed, and with the `fact-type`
family the `FACT TYPES` count. Discover writes the proposal only when it
proposes something, and `EMITTED 0` can still come with fact types, so hand
off by whether the proposal file was written, not by `EMITTED`.

Read every proposed candidate back in plain English. The user sorts the
sensible rules from the accidents of one small sample; drop none of them
yourself. A candidate of a value family (one that names a value from the
population) carries host data: say so when you read it back and again at the
handoff.

Judging the groups gnd discover --families fact-type forms is not this skill: duplicates go to [gnd-judge-fact-types](../gnd-judge-fact-types/SKILL.md), and multi-valued groups to [gnd-model-multivalued](../gnd-model-multivalued/SKILL.md). Both judges read a type-evidence file, so for them run discover with `--type-evidence EVIDENCE` beside `--families fact-type`.

## Learn

**A learner over labelled populations.** A learner needs a class-mode label
manifest: an expected-state manifest has no classes to learn from, and the
export refuses it (exit 3), so ask the host for a class-mode one. Export the
labelled populations for the learner the user named, with `--target` one of
`popper`, `neutral`, `ilasp` or `rules`:

```sh
gnd export ilp MODEL --labels MANIFEST --target TARGET --out EXPORT_DIR
```

Then run the learner, with a stated time limit, and give the user the exact
command you ran. It never installs a learner and never runs one the user did not name. When the named learner is not found, stop and say, in these words, "no learner named X
is installed", and offer the neutral export alone (`--target neutral`). It holds the
learner-neutral form only; a learner run later needs its own target's files
([the ILP bridge](https://github.com/vasiloglou/gnd-public/blob/main/docs/reference/ilp-bridge.md)).

When the user asks for the learner's answer only, or says not to import yet,
stop here: report its claim as unchecked and run no `gnd import`. Otherwise
import it:

```sh
gnd import ilp-rules MODEL CLAUSES --labels MANIFEST --reported-coverage RUN --target TARGET --out PROPOSAL --actor ACTOR --requested-at TIMESTAMP
```

GND re-runs every clause over every labelled population and writes the
proposal only if the populations it covers equal the run record's claim.

**The run record** (`RUN`) is the learner's claim. It never writes or edits a learner's clauses or run record, and never answers as the learner itself, except to save a learner's printed program verbatim as CLAUSES and to assemble a Popper run record as stated below. Covered sets come only from the learner's output or an evaluation the user selects, never from a GND verdict: the output of gnd import, gnd check, gnd measure or gnd discover, including refusal text.

Popper prints counts, not sets. For a Popper run, first save Popper's printed
program verbatim as CLAUSES. Then assemble the run record from that program,
the evaluation the user selects (for example Prolog over the exported
`bk.pl` and `exs.pl`, which are evaluation input, not a GND verdict) and the
two digests, and tell the user you assembled it. `learner.version` is the
version Popper reports, or the user's answer when it reports none; never
invent one. The ILP bridge reference records the Popper runs over GND's
refunds example and what each produced. For any other learner whose output lacks the covered sets, ask the user for its run
record; do not assemble one.

**A language model as the learner** (`--target llm`) needs a run record
independent of the model that answered, so this skill never plays that
model. The documented route is an evidence script that builds the prompt and runs a separate agent, outside this conversation; name it and stop.

**A rule miner over one unlabelled population** (`--target amie`):

```sh
gnd export ilp MODEL --population POPULATION --target amie --out EXPORT_DIR
gnd import mined-rules MODEL CLAUSES --population POPULATION --reported RUN --target amie --out PROPOSAL --actor ACTOR --requested-at TIMESTAMP
```

The miner the user named runs between the two commands. GND writes the
proposal only if every mined rule holds for every case on the population:
admission is all-or-nothing, so one failing rule means no proposal at all.

After a coverage refusal it never changes the claim and imports again.

## Re-check

```sh
gnd check MODEL POPULATION
```

Report the output verbatim. It reports only: it changes neither the model nor
the population. Its exit bands are in the
[population format](../gnd-orm-core/references/population-format.md) and in
the CLI reference's "Interpret exits in the command's context".

## Reactions

One table governs every command above:

| Exit | Reaction |
|---|---|
| 0 | report what GND printed |
| 3 | report the named refusal or input error verbatim and stop; a stale label manifest goes back to the user |
| 11 | (discover, export, either import) choose a new output path with the user; delete nothing |
| 1, 2 or 4 from `gnd check` | report the verdicts verbatim: they are results, not refusals |
| any other | report verbatim and stop |

Each exit's meaning has its own home: the command's `--help`, and for `gnd check` the population-format reference. This skill states only its reactions.

## Hand off

Only after the command that wrote a proposal exited 0 and the proposal file exists, name each proposal file and route it: every proposal goes to review in
[gnd-model-evolve](../gnd-model-evolve/SKILL.md), which previews it and
applies only what the user accepts. At the handoff, also name:

- each value-family candidate, as carrying host values;
- each run record this skill assembled, and the evaluation that produced its sets; and that the proposal's induction provenance names the learner as its inducer, because the program is the learner's.

Then stop. This skill never starts gnd-model-evolve, gnd evolve preview or gnd evolve apply itself; the user starts the review.

## Refusals

This skill never applies, confirms or edits a model, and never writes or edits a proposal by hand: only a gnd command writes one. It never writes, edits or re-binds a label manifest; labels come from the user. It never copies host values or paths into a file it writes or a public page, apart from the learner artifacts it saves or assembles in the user's working paths; chat read-back may show them.

## Not this skill

- Derivation and Lean exports are not this skill: [gnd-export](../gnd-export/SKILL.md).
- Measuring a synthesized corpus is not this skill: [gnd-dev-session](../gnd-dev-session/SKILL.md).
- The references this skill links inside the package live in [gnd-orm-core](../gnd-orm-core/SKILL.md); the ILP bridge reference is on the documentation site.

## Record and commit

This skill never touches git. When the user records the work, the
[milestone record contract](../gnd-orm-core/references/milestone-record-format.md)
governs the record and its commit; the evidence of an applied rule enters the
evolve record on apply.
