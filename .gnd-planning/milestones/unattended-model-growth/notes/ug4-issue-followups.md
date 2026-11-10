# UG4: issue follow-ups (drafted, not posted)

Drafted 2026-11-09 for the owner (UG-D0 (a), UG4-D2 (a)). Each text follows up the comment
posted on 2026-11-08 ([ug1-issue-dispositions.md](ug1-issue-dispositions.md)) and updates the
UG1 matrix row it names to the shipped state. The texts name no downstream application.
**Not posted.** Posting, and closing any issue, is the owner's: each needs the owner's explicit
instruction. **Tracker state, observed at the milestone close (2026-11-09):** #74, #75 and #76
are closed (completed, 2026-11-08 14:44 UTC), each with a disposition comment posted when it was
closed and a second, near-identical one posted at 17:59 UTC; #104 is open. The #74 and #76
texts below are therefore follow-up comments on closed issues; only #104 remains to close.

| Issue | UG1 matrix row (posted state) | Shipped state | Follow-up |
|---|---|---|---|
| #74 | open: an unsupplied document's spans are not re-hashed; a round cannot declare its own document through `evolve` | both shipped in PR 149 (UG3 parts A and B) | yes |
| #75 | no open item | unchanged | none |
| #76 | open: what the host does with a match, UG4 | documented in PR 151 | yes |
| #104 | item 5, second option open (UG2) | shipped in PR 147 (UG2); procedure text in PR 151 | yes |

## #74

> Follow-up to the disposition above: both items it left open are now on main (PR 149).
>
> - **Unchecked spans are counted.** `gnd validate MODEL --document DOC` on an unattended model
>   adds one `unattended:spans-unchecked` warning ("N of M source spans were not re-hashed")
>   when at least one source span was not re-hashed (its document was not supplied); `--require-documents` makes it an error (exit 3),
>   also with no `--document`. Runs that re-hash every span, runs without `--document`, and
>   models without the mode are unchanged. Rules: `gnd-orm-core` representation format,
>   "Unattended source". Record: `.gnd-planning/milestones/unattended-model-growth/004-phase-UG3a.md`.
> - **A round declares its own document.** A `source-document` operation in a `gnd evolve`
>   proposal (schema version 3) adds a `source.documents` entry by digest; `--policy additive`
>   admits the add and refuses a relabel or removal (`source_document.modify`,
>   `source_document.delete`). GND 0.2.0 cannot read such a proposal. Rules: the evolution
>   contract, "Stable locators" and "EvolutionOperation". Record: `005-phase-UG3b.md` in the
>   same directory.
>
> The `gnd-model-from-text` unattended-growth procedure uses both (PR 151). One more
> documented deviation from "every constraint cites a span": since PR 150 (issue 148), an
> `induced` constraint from `gnd discover` cites its `provenance.induction` block in place of a
> span (U5); spans it does carry are still checked. Nothing in this issue's scope is open.

## #76

> Follow-up to the disposition above: the open item, what the host does with a match, is now
> documented in the `gnd-model-from-text` unattended-growth procedure ("Acting on a shape
> match", PR 151). For each existing fact type the report names, the host reuses the
> existing id, keeps both with the reason in `provenance.rationale`, or keeps both and records
> the doubt in `open_questions` for the consolidation round; it never merges, renames or deletes
> inside a round. The report itself is unchanged: advice, exit 0. Nothing in this issue's scope
> is open.

## #104

> Follow-up to the disposition above: item 5's second option is now on main (PR 147).
> `gnd evolve preview --policy additive --check-population FILE` admits a new constraint, or a
> change to one whose differing keys all strengthen, weaken or are admitted, on a fact type that already holds facts, when the constraint is
> `proposed` and `deontic`, `FILE` holds facts for every populated fact type it ranges over and
> none has sample rows, and the constraint's own verdict over `FILE` is `pass`. The admission
> holds relative to `FILE`; the constraint stays advisory. `apply` repeats the option and refuses
> a changed file (exit 11). Rules: the evolution contract, "Population check". Record:
> `.gnd-planning/milestones/unattended-model-growth/003-phase-UG2.md`. The unattended-growth
> procedure now says when to use it (PR 151). A round can also declare its own source
> document inside `evolve` (PR 149). Items 1 to 4 are as the disposition above says.
