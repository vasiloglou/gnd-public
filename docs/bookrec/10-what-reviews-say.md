# 10. Recommend from what the reviews actually say

In [chapter 9](09-suggested-rules.md) the catalogue team exported which book
continues which. That export was clean data. The next request is messier:
**"Readers who finish a book should be offered the next one in the series,
and the series facts should come from reviews and publisher notes."** Those
sources are prose. They quote other people, deny things, use one title for
two different works, and get revised.

This chapter explains, in BookRec terms, what GND now does with that kind of
source. It covers six ideas:

| The problem in BookRec | What GND does |
|---|---|
| A reviewer quotes the publisher's claim that a book is a sequel | keeps **who said it**, whether it was **denied**, and the passage it came from |
| *Tidewater* is a novel and also a film | treats a shared title as a **candidate** for review, never as proof of one work |
| "Offer the next book" depends on a chain of sequel steps | follows a chain only when **every step is supported** by a reviewed source |
| A long publisher catalogue is read in passes | records what was **read, found, not found or unavailable** |
| The team changes what "sequel" means | finds the reviews and answers that the change makes **stale** |
| A recommendation rests on two reviews | gives the recommendation a **verdict** that survives rejecting one review but not both |

!!! warning "This chapter is a concept walk-through"

    The tables on this page illustrate the ideas with an invented series. They
    are not output from a BookRec run. The runnable version of each idea lives
    in the [literature example](../literature/01-lineage.md), which uses
    research papers instead of books. Each section ends with a link to it. The
    ideas that already run as plain `gnd` commands are demonstrated for real
    on an expense claim in [Expense approvals, chapter 5](../expense/05-receipts.md).

## The series

The invented *Tidewater* series has three novels: *Tidewater*, then *Tidewater
Rising*, then *Tidewater Deep*. A film called *Tidewater* adapts the first
novel. The film has its own sequel, *Tidewater: Undertow*, which no novel
continues.

## 1. Keep who said it

A review says: *"The publisher calls* Tidewater Deep *the sequel to*
Tidewater Rising, *but it reads more like a companion novel."*

A plain extraction would store one fact: *Tidewater Deep* continues
*Tidewater Rising*. That loses two things BookRec needs. The claim is the
**publisher's**, not the reviewer's own finding, and the reviewer **doubts**
it.

**You type**

```text
Read the Tidewater reviews with /gnd:gnd-extract. For every series statement,
record the passage, who makes the claim, whether it is asserted or denied, and
any condition on it.
```

**What gets recorded** is a statement, not a bare fact:

| Statement | Says who | Polarity | Passage |
|---|---|---|---|
| *Rising* continues *Tidewater* | the reviewer | asserted | review 1, line 3 |
| *Deep* continues *Rising* | the publisher, as quoted | asserted | review 2, line 1 |
| *Deep* is a companion novel, not a sequel | the reviewer | hedged | review 2, line 1 |

A person then reviews each statement against its passage, and the review is
saved alongside it: **approved**, **rejected**, **abstained** or **not yet
reviewed**. A correct extraction of the publisher's claim can be approved as an
accurate extraction and still not count as the reviewer's own finding. Only
approved own findings feed the recommendation.

*Runnable version:* [contextual assertions and saved reviews](../literature/01-lineage.md#start-with-the-passage).

## 2. One title, two works

The film *Tidewater* and the novel *Tidewater* share a title. If BookRec joins
them by name, the film's sequel *Undertow* becomes the next novel after
*Tidewater*, and readers get offered a film tie-in that is not part of the
series.

The name-diagnostics step finds titles that look alike, for example the same spelling in
different contexts or the same name in different capitalization. It lists
them as **candidates** for a person to decide. Every decision is one of
**same**, **different** or **unresolved**, cites the passages it rests on,
and is checked when the sources are combined. A pair of identical titles from
two sources that has no decision is refused, as the
[expense chapter](../expense/05-receipts.md#5-forget-a-decision-and-gnd-stops)
shows with a real run.

| Title in source A | Title in source B | Decision |
|---|---|---|
| *Tidewater* (novel, review 1) | *Tidewater* (film, studio note) | different |
| *Tidewater Rising* (review 1) | *TIDEWATER RISING* (catalogue) | same |

*Runnable version:* the [literature example](../literature/01-lineage.md#start-with-the-passage) keeps the music *VampNet* and the
molecular-kinetics *VAMPnet* apart in exactly this way.

## 3. Follow a chain only when every step holds

"Offer the next book in the series" is a **chain**: *Tidewater*, then
*Rising*, then *Deep*. GND derives the chain from the sequel steps, and a
step counts only if its statement passed review. So the answer depends on
the evidence behind each link:

| Question | Answer | Why |
|---|---|---|
| After *Tidewater*, offer *Rising*? | yes | one approved, reviewer-own step |
| After *Rising*, offer *Deep*? | not yet | the only source is the publisher's quoted claim, and the reviewer hedged it |
| After *Tidewater*, offer *Undertow*? | no | the path only exists if the film and the novel are joined, and they were decided **different** |

When the answer is "not yet", GND can say which step is missing, the same way
[chapter 5](05-repair.md) explains a refused recommendation.

*Runnable version:* [context-qualified lineage](../literature/01-lineage.md#review-the-statements-before-querying).

## 4. Read a long catalogue in passes

The publisher's catalogue is forty pages. Reading it once, broadly, finds most
series facts but misses the one buried in a table of reissues. A second,
targeted pass goes back to the sections that matter.

GND keeps a record of each pass and, for every question, says which of these
holds:

| Disposition | Meaning for *"Is there a fourth Tidewater novel?"* |
|---|---|
| found | a passage names it |
| read, not found | every relevant section was inspected and none names it |
| unavailable | the reissue table could not be read |
| explicitly denied | the catalogue says the series ends at three |

"Read, not found" and "not read" stop looking the same. A recorded run can be
replayed later without calling the reading agent again.

*Runnable version:* the [multipass reading example](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/literature/reading_fixture/README.md).

## 5. Change what "sequel" means

The product owner decides that **companion novels** are not sequels and adds
them as their own kind of link. That is a change to the model, made through
the same reviewed evolution as [chapter 6](06-evolution.md).

The change has knock-on effects. A review that approved *Deep continues
Rising* approved it under the **old** meaning of "sequel", so it is now
**stale**, even though the passage did not change. GND records which saved
reviews, reading coverage and chain answers depend on the old definition, and
lists every one that must be looked at again. The release from before the
change stays intact and can still be replayed on its own.

*Runnable version:* the [semantic revision example](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/literature/revision_fixture/README.md).

## 6. Give the recommendation a verdict

Suppose two independent reviews each support *Rising continues Tidewater*.
The recommendation "after *Tidewater*, offer *Rising*" then rests on two
supports, and each has its own saved opinion.

| Opinions on the two supports | Verdict on the recommendation |
|---|---|
| both approved | supported |
| one rejected, one approved | still supported, by the other review |
| both rejected | no support |
| the definition changed after the reviews | needs revalidation |

A rejected review takes away only its own support, not the whole
recommendation.

*Runnable version:* the [derived verdict example](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/literature/verdict_fixture/README.md).

## Run the literature version of the verdicts

Section 6 has a runnable counterpart in the literature example. There, the
claim is that the music model VampNet descends from DMD, and two
independent sources support it. The block below reads the example's
sources, releases them, and asks for the verdict under each set of saved
opinions. It runs from a checkout of the repository, needs no model account
or network connection, and takes under a minute:

<!-- gnd-run expect=0 output=stdout -->
```python
import json
import subprocess
import sys

def run(*args):
    return subprocess.run([sys.executable, "-m", *args], capture_output=True, text=True)

run("gnd.examples.literature.reading", "run", "--out", "reading-run")
run("gnd.examples.literature.revision", "run", "reading-run", "--out", "revision-run")
for case, edition in [("both-approved", "current"), ("reject-whale-a", "current"),
                      ("reject-both", "current"), ("both-approved", "revised")]:
    result = run("gnd.examples.literature.verdict", "evaluate", "revision-run",
                 "--case", case, "--edition", edition)
    verdict = json.loads(result.stdout)
    print(f"{case} ({edition} definition): {verdict['decision']}, exit {result.returncode}")
```

```text
both-approved (current definition): supported, exit 0
reject-whale-a (current definition): supported, exit 0
reject-both (current definition): unsupported, exit 2
both-approved (revised definition): revalidation-required, exit 3
```

The four lines are the four rows of the verdict table: both approved,
one rejected, both rejected, and a definition changed after the reviews.

## What you have now

| Before | Now |
|---|---|
| A series fact was a bare row | it is a statement with a source, a speaker, a polarity and a saved review |
| Equal titles meant one work | equal titles are candidates, and every join is a reviewed decision |
| A chain was as strong as the data said | a chain holds only when every step is supported |
| "Not found" was ambiguous | reading coverage says what was inspected and what was unavailable |
| Changing a definition was silent | the reviews and answers it makes stale are listed |
| A recommendation passed or failed | it has a verdict tied to the opinions behind it |
