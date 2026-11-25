# An ontology from a stack of papers

You have a folder of research papers, and a question that crosses them:
**which methods descend from which?** A model that reads papers can
answer quickly. The answers are fluent, and some of them are wrong. A
paper may say a method was *evaluated*, not *built on*. It may quote
someone else's claim, or deny it. Two fields may give two different
methods the same name.

GND 0.4.0 and later let you build one checked ontology over many papers. The
agent still does the reading. GND keeps each claim tied to its passage in the
document version it was read from ([where a quote may lie](../reference/anchors.md#where-a-span-may-lie)), refuses
to join names nobody decided, and proves or refuses every answer. This
page follows one stack of sixteen papers from eleven fields through three
acts.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="The three acts of the papers story">

![Sixteen papers from eleven fields flow through three acts. Act 1, who is who: keep who said each claim and the passage, review each statement, decide which names are the same method. Act 2, one vocabulary: read every paper the same way, merge spellings and check a catalogue, flag dates that run backwards. Act 3, depth and change: answer or say unknown, know what was not read, revise and give each claim a verdict.](../assets/applications/papers-journey.svg)

</div>

!!! note "What is real on this page"

    Every result below comes from the packaged literature example, run for
    real. The reading agent's answers are saved in the
    example, so you get the same results without a model account. The
    *You ask* boxes show how you would phrase each step to Claude Code. The
    [commands page](commands.md) reproduces every result in about a
    minute.

## The stack

The papers are short paraphrases of public works. Among them:

| Paper | Field | What it says, in one line |
|---|---|---|
| VampNet (2023) | music | makes music; built on a bidirectional transformer |
| VAMPnets (2017) | molecular dynamics | learns molecular kinetics |
| WhAM (2025) | bioacoustics | whale codas, made by fine-tuning VampNet |
| WHAM (2023) | computer vision | 3D human motion; uses a SLAM system |
| OpenCap Monocular (2026) | biomechanics | starts from WHAM's pose estimates |
| PoseX (2025) | structural biology | a benchmark that *evaluates* the Boltz-1 family |

Read those names aloud and you see the trap. VampNet and VAMPnet sound
alike, and so do WhAM and WHAM.

---

## Act 1: who is who, and who said what

### The trap, in two sentences and a chain

Two notes, each one true:

> **Notes A.** VampNet builds on DMD. OpenCap Monocular builds on WHAM.
>
> **Notes B.** WHAM builds on VampNet.

In Notes A, *VampNet* means the molecular method and *WHAM* means the
human-pose model. In Notes B, they mean the whale model and the music
model. Combine the notes by spelling and the three true sentences form a
chain that nobody wrote: a smartphone biomechanics method descends from
a molecular-kinetics method.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="The whale chain, joined by spelling and by decision">

![Top: joined by spelling, OpenCap Monocular builds on WHAM, WHAM builds on VampNet, VampNet builds on DMD. The two shared spellings are false merges, and GND proves the false claim that OpenCap Monocular descends from DMD. Bottom: joined by decision, a reviewer recorded both pairs as different. Four separate methods remain, each true edge survives, and the claim is missing.](../assets/applications/papers-whale.svg)

</div>

**You ask**

```text
Combine Notes A and Notes B, and prove that OpenCap Monocular descends from DMD.
```

**What happens.** Joined by spelling, GND *proves* it. The proof is
valid, because every step is in the data. The data is wrong. That is why
the next step exists.

### Decide who is who

Before combining papers, GND lists the names that look alike as
**candidates**, never as matches. A person, or a reviewing agent, decides
each pair: **same**, **different** or **unresolved**. Each decision cites
the passages it rests on.

The sixteen papers carry six such decisions:

| Name, in which paper | Name, in which paper | Decision |
|---|---|---|
| VAMPnet, in VAMPnets | VampNet, in WhAM | **different**: molecules vs music |
| WhAM, in WhAM | WHAM, in OpenCap Monocular | **different**: whales vs human pose |
| $PINN, in APINN | PINNs, in a PINN failure-modes paper | **different**: an augmented PINN, not PINNs itself |
| VampNet, in VampNet | VampNet, in WhAM | same |
| WHAM, in WHAM | WHAM, in OpenCap Monocular | same |
| PINNs, in APINN | PINNs, in a PINN failure-modes paper | same |

**You ask**

```text
Combine Notes A and Notes B again, this time with the recorded decisions,
and prove the same claim.
```

**What you get**

| | Joined by spelling | Joined by decision |
|---|---|---|
| Edges kept | 3 | 3 |
| Methods | VampNet, WHAM *(each covering two methods)* | VampNet, VampNet [music], WHAM, WhAM [whale] |
| "OpenCap Monocular descends from DMD" | **proved** | **missing** |

Nothing was deleted. The same three true sentences are still there, and
they no longer form a false chain.

**And if you forget a decision?** GND refuses to combine the papers. It
does not guess:

```text
ERROR: composition:invalid: keys at whale-a method_builds_on_method#0.method and
whale-b method_builds_on_method#0.base_method (object type method) are joined
without a same decision
```

The message names the two places where the same spelling appears, and
says which decision is missing.

### Keep who said it

The PoseX paper says that it *evaluates* the Boltz-1 family. A loose
reading turns that into "PoseX builds on Boltz-1". GND keeps each claim as
a **statement**, with the paper's version, the exact passage, the
relation, and whether the authors assert, deny or only report it.

**You ask**

```text
Read the sixteen papers with /gnd:gnd-extract. For every claim about one
method and another, record the passage, the relation (builds on, evaluates,
compares with), who makes the claim, and whether it is asserted or denied.
```

A reviewer then checks each statement against its passage. The review is
saved as **approved**, **rejected** or **abstained**, or the statement is
left unreviewed. A lineage step counts only if its statement was approved
and is the authors' own finding.

### Follow a chain only when every step holds

The answer key for the sixteen papers labels eight lineage paths. Three
are real. Five are traps.

| Path | Label | GND |
|---|---|---|
| bidirectional transformer → VampNet → WhAM | real | **proved** |
| PINNs → XPINN → $PINN | real | **proved** |
| SLAM → WHAM → OpenCap Monocular | real | **proved** |
| VAMPnet → WhAM → OpenCap Monocular | trap: two homonyms | missing |
| XPINN → PINNs → curriculum regularization | trap: name family | missing |
| PINNs → XPINN → PINNs | trap: a loop | missing |
| Boltz-1 → PoseX | trap: evaluation, not ancestry | missing |
| normalizing flows → simulation-based inference → deep optimal sensor placement | trap: a contrast, not a parent | missing |

**3 of 3 real paths kept. 5 of 5 traps excluded.** A separate, reserved
set of papers, scored once after the rules were frozen, kept 1 of 1 real
path and excluded 2 of 2 traps.

Every proved path comes with a certificate that names its statements and
their passages, so anyone can replay it.

---

## Act 2: one vocabulary for every paper

Sixteen papers are only useful together if they are read the same way.
Act 2 gives the stack one shared vocabulary of papers, methods and dates,
and keeps it in its own files that every paper's extraction uses.

### Two papers, two spellings, one method

A 2026 survey writes **P.I.N.N.s**. A 2019 replication study writes
**PINNs**. Both mean physics-informed neural networks.

**You ask**

```text
Extract the survey and the replication study against our shared literature
vocabulary, merge the two spellings of the parent method, and check the
result against our reference method catalogue.
```

**What you get**

| Step | Result |
|---|---|
| Extraction, scored against a hand-checked answer | 2 of 2 papers, no failures |
| Combined | both papers name parent method **PINNs** |
| Checked against the method catalogue | **accepted** |
| "The survey names PINNs as a parent method" | **proved** |
| "PINNs is a catalogue method" | **proved** |

The catalogue is a fixed input. Checking a paper against it never changes
it.

### Dates that run backwards

If a 2019 paper "extends" a 2021 paper, something is off. Perhaps the
claim is wrong, or perhaps one date is the preprint date. GND reports
this as **advice**, never as a refusal, and says why it could not decide:

| Edge | Outcome | Why |
|---|---|---|
| 2026 survey extends a 2019 paper | pass | |
| 2019 replication extends a 2019 paper | pass | same year |
| a 2019 paper extends a 2021 paper | **advisory** | parent published later |
| the parent is not in the date list | unresolved | unknown work |
| the child has two different years | unresolved | conflicting dates |
| the child has no date | unresolved | missing date |
| a day compared with a year | unresolved | mixed precision |
| only a preprint date is known | unresolved | publication date missing |

---

## Act 3: depth, and changing your mind

### Ask what a scientist asks

A reviewer reading a physics or algorithms paper asks specific questions.
What is the equation, and in which regime? What are the boundary
conditions? What is the complexity, under which assumptions? GND answers
each one from a reviewed passage, or says **unknown** when the paper does
not support an answer.

| Paper | Question | Answer |
|---|---|---|
| Shallow-water dam break | equation and regime | supported |
| | boundary treatment | supported |
| | discretization | supported |
| | measured conservation residual | **unknown**: the run reports none |
| Alanine dipeptide, OPES-eABF | system and force field | supported |
| | sampling objective | supported |
| | numerical approximation | supported |
| | does it hold in another solvent? | **unknown**: the run is in vacuum |
| Randomized SVD | operator and objective | supported |
| | algorithm components | supported |
| | complexity with its assumptions | supported: O(mn log(k)) flops, dense input |
| | run time on an H100 | **unknown**: no benchmark reported |

"Unknown" is an answer. It says the question was asked and the paper
does not answer it. That is different from a question nobody asked.

Numbers stay exact, too. One source gives the same time step as
`2 fs`, `0.002 ps` and `0.000002 ns`, and also mentions `2 eV` and
`0.0001 ps`. GND records the step as exactly `0.002 ps`, ties it to the
second line, proves the value, and replays the proof.

### Read again, and find more each time

One quick read of a paper misses things. The method details sit in the
methods section, and a limitation sits in a closing sentence. So the agent
reads in passes. Each pass goes after the questions that are still open,
and GND checks each pass before its facts are kept.

The example is a molecular simulation study with seven questions: the
system, the method, any stated denial, an alternative integrator, a method
in the annex, an equation, and an older form of the method question.

**You ask**

```text
Read the alanine study with /gnd:gnd-extract in passes. Start with a broad
read of each source's opening. Then go back only to the sections that can
answer the questions still open, and stop when every required question has
an answer or a reason it has none.
```

**What each pass added**

| Pass | Sections read | What the agent returned | Facts kept so far |
|---|---|---|---|
| 1. Broad | study opening, annex opening, a withheld table | 1 answer, 1 empty, 1 refusal | **2**: the subject's label and the system, *alanine dipeptide in vacuum* |
| 2. Targeted | study methods, study limits | 2 answers | **4**: adds *Langevin integration at 300 K with 2 fs steps* and *no barostat* |
| 3. Review | none | proposes a new vocabulary term, *method family* | 4, and the study opening goes back on the list to re-read under the new term |

The targeted pass found two more facts and answered two more questions.
It read 234 bytes in all, so the run reports its yield as 2 new facts per
234 bytes read. The agent was called 3 times in the broad pass and 2 times
in the targeted pass. A refused or empty answer is recorded as refused or
empty, and never as "nothing there".

A candidate can also be stopped before it is kept. A separate report gave the same molecule
two different labels. GND's verify and check steps both rejected that
candidate, so it never joined the kept facts.

**Know what was not read.** When the run stops, each question has exactly
one disposition:

| Question | Section | Read? | Disposition |
|---|---|---|---|
| system | study opening | yes | supported |
| method | study methods | yes | supported |
| denial | study limits | yes | **explicitly denied** |
| alternative | study methods | yes | **read, not found** |
| annex method | annex methods | no | **unavailable** |
| equation | control equation | no | **not applicable** |

"Read, not found", "unavailable" and "denied" no longer look alike.
"Read, not found" is only allowed when the reading is good enough to
trust. Scored against an independent answer, the extraction found 2 of 2
facts, so the
absence of an alternative integrator counts, scoped to the methods
section. At 1 of 2, the same absence would be reported as unavailable.

Every pass is saved with its inputs, so the whole run replays later
without calling the reading agent again.

### How much does the reading find?

A reference set ships with the example: the twelve development papers of
the literature corpus, with 31 labelled facts. One recorded run of the
reading stages over it, with Claude Sonnet as the reading agent, gives:

| Run | Recall | Precision |
|---|---|---|
| This set, after the broad pass | 9 of 31 | 9 of 10 |
| This set, after the targeted pass | 27 of 31 | 18 of 23 (targeted rows) |
| Issue #226, 20 papers, broad pass (best model) | 29 of 101 | 15 to 38 % |
| Issue #226, targeted pass (best model) | 30 of 100 | 10 to 20 % |

**A figure here is a measurement of one run.** It names its producer, its
settings and its set, and says nothing about other papers or models. The
set's papers are short paraphrases written to state their claims plainly,
and its rule scores a fact by the section it was read from, while #226
scored quotes; the two rows are a point of comparison, not a ranking. The
[reference set](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/literature/reference_fixture/README.md#the-scoring-rule)
holds the scoring rule, the settings and the run, which replays without
calling the reading agent.

Both passes use one prompt that asks no question; the rows differ only in
which sections were read. This section's figures are reproduced by the
reference set's replay, not by the commands page.

### Change the vocabulary, and see what goes stale

Suppose the team decides to split the whale senses after the release has
shipped. That is a change to the vocabulary, made through
[/gnd:gnd-model-evolve](../agents/evolve.md).

**You ask**

```text
With /gnd:gnd-model-evolve, separate the music VampNet from the molecular
VAMPnet and the whale WhAM from the human-pose WHAM. Show which lineage
answers, reviews and reading coverage the change affects.
```

**What you get**

| Lineage question | Before | After |
|---|---|---|
| OpenCap Monocular descends from VampNet | yes | **no** |
| OpenCap Monocular descends from DMD | yes | **no** |
| WHAM descends from DMD | yes | **no** |
| OpenCap Monocular descends from WHAM | yes | yes |
| VampNet descends from DMD | yes | yes |

Three false paths disappear and two true ones remain. GND also lists what
must be looked at again:

- the saved review of the changed statement is **stale**, and a renewed
  review is **current**;
- the reading answer "read, not found" for one question is **stale**, and
  an unrelated "denied" answer stays **current**;
- one mention of WHAM has no source context, so it stays on the
  re-reading list with both possible senses.

The release from before the change stays intact and replays on its own.

### Give each claim a verdict

"VampNet descends from DMD" rests on two independent papers. Each support
has its own saved opinion. The verdict follows the opinions:

| Opinions on the two supports | Verdict |
|---|---|
| both approved | **supported** |
| one rejected, one approved | **supported**, by the other paper |
| both rejected | **unsupported** |
| both approved, under the old definition | **needs revalidation** |

Rejecting one paper removes only its own support. Changing what "descends
from" means makes every old opinion stale, until someone reviews the
claim again.

---

## What you end up with

One ontology over the whole stack, where:

- every claim points to its paper, its passage and who made it;
- names are joined only by a recorded decision, and a missing decision
  stops the merge;
- every lineage answer is proved with a certificate, or reported missing;
- "unknown", "not read" and "denied" stay distinct;
- a change to the vocabulary lists everything it made stale;
- every derived claim carries a verdict you can recompute.

## Go further

- [The commands behind this story](commands.md): every result above, run
  for real in about a minute.
- [Trace a method's lineage](01-lineage.md): the lineage and transfer
  queries in more detail.
- [BookRec, chapter 10](../bookrec/10-what-reviews-say.md): the same ideas
  applied to book reviews.
- [Expense approvals, chapter 5](../expense/05-receipts.md): one claim
  checked across three documents.
