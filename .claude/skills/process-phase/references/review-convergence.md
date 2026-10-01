# Review convergence — when repeated review stops paying

**Where this comes from.** One phase spec was panelled five times in one day
(2026-08-23, Phase 4 of the v2.0 milestone), and the record is unusually clean:
one artifact, mostly the same seats, every finding dispositioned, every count
recomputed. The rules below are measured, not felt. The evidence lives in the
spec's own panel sections (§§13–18 of `phase-4-spec.md` in the milestone's
`notes/`) and the retained seat outputs under the milestone's `evidence/`
directories. `standing-rules.md` already records the repair-round hazard among its measured
failure classes; this file is the *quantified* version, and the stop rule it
buys.

## The record, in one table

| Round | Instrument | Seats | Findings | Verdicts |
|---|---|---|---|---|
| 1 (first draft) | five-seat panel | 5 of 5 returned | 60 concerns | 1 block, 4 revise |
| 2 (over the repaired r2) | five-seat panel | 3 of 5 | 29 concerns; the status recount later showed **13 of 20** round-1 landings reopened | 1 block, 2 revise |
| 3 (over the owner-APPROVED r3) | three seats | 3 of 3 | 38 raw, ~25 distinct; **4 requirements no implementation could satisfy** | 2 block, 1 revise |
| 4 (over r4) | same three seats | 3 of 3 | 14 / 14 / 4 per seat = 32; one seat: *"11 arise directly from r4 repairs or their new claims"* | 1 block, 2 revise |
| 5 (over r5) | same three seats | 3 of 3 | 17 / 13 / 9 = **39**; one seat: *"roughly 11 of my 17 findings attack text r5 created or changed"* | 1 block, 2 revise |

The r3 approval was superseded after round 3 — fourteen findings reproduced
against the bytes and the repository, four of them unimplementable as written.
The severity *ceiling* fell across rounds: four unimplementable cores at round
3, one critical at round 4, and at round 5 two narrow criticals (one against
the round's own checker, one a rule-mismatch two of three seats did not rate
critical at all) — nothing unimplementable remained. **Counts did not fall.**
Same-seat totals went 32 → 39 between the last two rounds.

## The stop rule

Track two numbers across repeated review rounds over one artifact, and compute
them — never estimate them:

- **the self-inflicted ratio** — findings attacking text the previous repair
  round created, over total findings;
- **the same-seat trend** — one seat's finding count, round over round.

**Stop when the self-inflicted ratio exceeds one half, or when same-seat counts
are flat-to-rising for two consecutive rounds while severity falls.** At that
point the panel is measuring the repair process, not the artifact: each repair
round is manufacturing the next round's findings. The next instrument is code,
not another round.

A falling severity ceiling over flat-or-rising counts is the *signature* of the
stop condition, not a reason to continue. It means the design has stopped yielding and the prose has
not — and prose defects that only reading finds slowly are exactly the ones
implementation finds immediately.

**GND already mechanized this rule one level down.** `gnd exp run` bounds
attempts by contract and terminates a nonaccepted session with a disposition
from a closed vocabulary in which `stagnation`, `oscillation`, and
`budget-exhausted` are first-class terminal outcomes — computed facts, not
judgment calls, decided in code. A repeated review loop is the same loop with
prose in place of populations and deserves the same discipline: **declare the
round budget and the stagnation criterion before round two, in the artifact's
own bytes.** A stop condition adopted after seeing a round's results is the
review-side twin of a ceiling changed after seeing a measurement.

## Specify decisions, discover facts

A spec exists to pin **decisions** — an order, a schema, an exit band, a
boundary someone must own. **Facts about the runtime are not decisions**: what
an OS call does to an open file descriptor, which process group a signal
reaches, which exception a library raises, what an argument parser exits.
Reading is a bad instrument for facts. In the measured rounds, a directory
`chmod` was specified as an injection that POSIX makes a no-op (three seats
confirmed it, one round late), an encoder's stated exception was not the one
the library raises (three seats confirmed), and a signal-delivery mechanism
drew a refutation that itself still sits unreproduced — which is the point
twice over: each is answerable by one test in seconds, and neither assertion
nor refutation settles it until one runs.

- When a review finding turns on a runtime fact, its discharge is a **test
  row**, never more prose. Do not adjudicate a fact by argument.
- Prefer stating the *required outcome* and letting the test list carry the
  mechanism; a spec sentence asserting a runtime mechanism is a liability
  whichever way the fact turns out.

This is where "how specific should the spec be" bottoms out: **the spec stops
where the runtime starts answering.**

## Every restatement is a staleness site

Disposition tables, decision rows, and panel records restate rules in order to
discuss them, and each restatement can go stale when the rule moves. By round
five the review apparatus — the decision ledger plus six panel sections — had
grown past a third of the document, and the dominant defect class was
propagation — a rule changed in its home, copies left behind (nine of
round four's twenty findings were this one class). The one-home rule
(`standing-rules.md`, section-0 rule 5) applies to review scaffolding with full
force:

- discussion **cites by anchor**, never by copy;
- when a rule is retired, its exact wording is grepped over the artifact before
  the revision ships;
- a checker built for this must **assert, not print** — see the instrument rule
  below.

## A review that cannot come back empty measures nothing

Nineteen seat-runs were attempted across the five rounds; seventeen returned,
and **no seat ever returned "None survived"**, though every rubric admitted it.
An adversarial reviewer asked to find defects will find defects; at the margin
the panel *generates* findings rather than detecting them. Consequences:

- a raw finding count is not a quality metric — only its trend, its severity,
  and the self-inflicted ratio are;
- reproduce-before-believe (`review-and-record.md`) is not optional at any
  round, and it is what kept the measured rounds honest;
- a finding that names no observable consequence is style, and is triaged as
  style.

## Implementability is a gate precondition, not a review discovery

Before the owner gate is offered, walk the requirements once asking one
question: **can SOME implementation satisfy this as written?** A guard that
must red on content the same spec mandates, an injection that physically cannot
fire, a recomputation whose inputs the artifact does not carry — each takes
minutes to check, and each invalidates an approval retroactively when found
later. One approval in this milestone was superseded exactly this way, and the
supersession cost more than the sweep would have.

## The instrument gets the artifact's treatment

Any checker, corpus, or harness a phase builds to verify itself is believed
**only after a negative control**: feed it a known-dirty artifact and watch it
red. In the measured rounds, a propagation checker shipped whose count half
*printed* values without comparing them — it reported clean while asserting
nothing, its measured recall against the findings that motivated it was 2 of 9,
and the shipping precondition built on it was violated by the very revision
that created it. A checker that reports clean without asserting launders an
unverified claim into a mechanical-sounding one — strictly worse than no
checker, because prose invites doubt and tool output does not.

## Prefer the executable instrument when bytes are in scope

When a phase's deliverables include a **serialized format, an exit-code
contract, or a validation predicate**, the approval instrument defaults to
corpus-first — golden bytes and expected exits authored, approved, and committed
RED before code — and choosing spec prose instead requires stating why. Writing
the expected bytes forces every value prose can leave vague: a version field's
value, a null's representation, an encoder's failure mode, a first index.

The record on both sides: the transition phase and the tests-mode phase ran
corpus-first (golden walks and a 71-row answer key committed red before any
implementation file) and closed with their corpora fully discharged and no spec
re-rounds — each phase's overall gate still carried the repository's one
pre-existing, separately-owned red, recorded as such. The harness phase
ruled corpus-first out on cost grounds — for a phase whose core deliverable was
a byte-exact log format — and spent three panel rounds relitigating byte-level
values a golden fixture fixes by construction. This does not repeal the
owner-gate rule that the instrument is asked, never inherited; it sets the
default answer for these three phase shapes.

## Relevance is not severity — triage every finding before fixing any

**The standing priority: work that moves the product toward a demonstrable MVP
outranks work that increases completeness.** A defect that stops the software
from doing what it claims is not the same kind of thing as a defect that makes
the artifact more complete, and reviewers do not distinguish them — the panel's
only axis is `low|medium|high|critical` (`review/request.py:112`), which rates
*how bad the flaw is*, never *whether fixing it proves anything works*.

Every finding is assigned one of three classes at disposition time, by whoever
dispositions it, not by the reviewer:

| Class | Test | Default handling |
|---|---|---|
| **blocking** | unfixed, the software does not demonstrably do what it claims — it crashes, computes a wrong answer, silently accepts bad input, or the claim cannot be run at all | fixed in-phase |
| **hardening** | a real defect with a real consequence, but the demonstration still stands: an unexercised branch, a reader untotal over bytes nobody sends yet, a race under conditions not yet reached | fixed in-phase **only** when this phase's own deliverable is the thing it hardens; otherwise an open-questions row with a named target |
| **completeness** | the artifact becomes more complete or more consistent, and no user-observable behaviour changes: wording normalized, a table restated, a census recounted, a boundary rephrased in the contract's exact words | **deferred by default**, batched to milestone close; fixing one in-phase costs a sentence saying why it could not wait |

Three consequences:

- **A round whose findings are majority completeness has hit the stop rule from
  the other side.** The artifact stopped yielding defects that matter and the
  reviewers kept finding text to improve. That is not a signal to repair and
  re-round; it is the same "next instrument is code" verdict the trend rule
  reaches by a different route.
- **Severity does not substitute for this.** A `critical` naming a doc
  inconsistency and a `critical` meaning the command exits 0 on invalid input
  arrive identically. Sort by class first, severity second.
- **The structural pressure runs the wrong way, and it is in the code.**
  `ReviewResponse` rejects a non-approve verdict that carries no concern
  ("a {disposition} response must contain a concern", `review/request.py:327`),
  and across nineteen seat-runs no seat ever returned empty. A reviewer who
  found nothing blocking and does not wish to approve must produce *something*,
  and completeness findings are the cheapest thing to produce. Expect the class
  to be over-represented, and triage before counting.

The same triage governs work the reviewers never touched. **A phase ships when
its deliverable is demonstrably working, not when every artifact around it is
internally consistent.** Completeness work is real work and it is not free; it
competes with the next thing that would prove the system does something it
could not do before, and it loses that competition by default.

## The convergence ledger

When a second round over one artifact is contemplated, add this table to the
artifact's panel disposition and keep it current — the stop rule is computed
from it, and a round that cannot fill its row has not measured convergence and
does not get to claim it:

| Round | Seats | Per-seat counts | Self-inflicted / total | **Blocking / total** | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|

**`Blocking / total` is the column that decides whether the round paid.**
A round returning many findings and no blocking ones measured the prose,
not the product.
