# Phase LR1 · why a source fails verification · spec r1

## 1. Status

**Draft, awaiting owner review. Implementable once the plan gate approves
the plan, rules D7 and D8, and the owner signs off this spec.** Written by
`start-milestone` on 2026-11-23; `process-phase` has not run and no owner
gate is recorded. The spec is written for D7 (a) and D8 (a), the plan's
proposals; §7 says what changes under the other readings.

## 2. Provenance

- Derives from [plan r2](literature-reading-reference-plan.md), Goal (LR1),
  §0 (R0.1, R0.3, R0.6), §1 (H1–H6, H19, H20, H22), §2 (LR1), §4 (LR1-C1 to
  LR1-C5), §9 (the LR1 lane) and §10 (D7, D8). The plan is not reviewed and
  not approved.
- From [#226](https://github.com/vasiloglou/gnd-public/issues/226), request
  3.
- No review has read these bytes.
- Code and pages were read at `548b9a1d`. The probe of plan H2 to H4 was run
  on that commit on 2026-11-23.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan H1; #226 request 3 | a host can see which constraint failed, on which rows, per source | §6 (the section); T1 |
| plan H2 | the JSON report already carries each failing verdict with `constraint_ref`, `constraint_type`, `modality`, `message` and `offending_facts` | §6 (the steps name these fields); T1, T3 |
| plan H3 | the text output prints the constraint and message, not the rows | §6 (the section says to use `--format json` for rows); LR1-D2 |
| plan H4 | the declared constraint id is not in the report; `--rule-ids` is refused on `gnd verify` | §6 (the section says how to find the constraint from `constraint_ref`); LR1-D2 |
| plan H5 | a redacting model replaces the message and the rows with markers | §6; T5 |
| plan H6 | no page shows the steps for a verify report | §6 |
| plan H19, R0.1, LR1-C5 | the default verify text and JSON keep their bytes | §6 ("What does not change"); T6 |
| plan H20 | exit 1 and the deontic case are pinned; nothing lists rows for verify | T1, T4 |
| plan R0.3 | no fidelity rate enters the verify payload | §6 ("What does not change") |
| plan R0.6, D8 | one home for the steps; other pages cite it | §6; T7 |
| LR1-C1 | the reported conflict gives one failing constraint with its two rows | T1 |
| LR1-C2 | the broad population gives none, exit 0 | T2 |
| LR1-C3 | every field name the page uses is in the schema and in a live report | T3 |
| LR1-C4 | a deontic-only violation is a warning, not a failure; a redacting model gives the marker | T4, T5 |
| plan §9 | the LR1 lane, the guard block, `uv run ruff check src tests tools` | §8, closing paragraph |
| `AGENTS.md`, "General solutions, not pattern-matched ones" | read structured text with its parser | §4; §8 (how the test reads the page) |

## 4. The standing rules, bound to this phase

- **Totality (project rule 1).** The phase adds no consumer of untrusted
  input to the package. The test's reader of the page takes a file this
  repository writes; it reads the fenced block through the tutorial
  runner's own parser (`tools/run_tutorials.py:37`, `parsed_blocks`), not a
  new pattern.
- **A cap bounds the document, not the algorithm (rule 2).** Inapplicable:
  no work proportional to an input is added.
- **Validation order (rule 3).** Inapplicable: no refusal is added and none
  moves.
- **One walk for N kinds (rule 4).** The documented steps are one filter
  over `verdicts` that serves every constraint family. The page has no
  per-family recipe; T1 and T4 use two families.
- **One home for normative prose (rule 5).** "Reading a failed
  verification" lives in `docs/guides/documents.md` (D8 (a)).
  `extraction-contract.md` §5 keeps its table and gains one line that cites
  the section; `docs/literature/commands.md` gains one line. T7 fails if a
  second page restates the field list.
- **Measurement, not argument (rule 6).** What the report carries was
  settled by running it (plan H2 to H4), not by reading the builder.
- **General solutions (`AGENTS.md`).** The steps select by the report's own
  fields (`verdict`, `modality`), never by a constraint's name, a message's
  wording or a fixture's ids. The test decodes JSON with the JSON loader and
  compares decoded values.
- **Plan R0.1, R0.3, R0.6:** T6; §6; T7. **R0.2, R0.4, R0.5** concern LR3's
  figures, fixtures and live run; this phase reads the packaged reading run
  and changes none of its bytes.

## 5. Goal

A reader of `docs/guides/documents.md` who runs the documented steps on a
source that `gnd verify` exits 1 on gets each failing constraint with its
violating rows; on the reading example's reported conflict that is one
constraint and two rows, and on its broad population none. `gnd verify`
prints byte-identical text and JSON before and after. The focused lane, the
guard block and `uv run ruff check src tests tools` exit 0.

## 6. Design

### Reuse

| Capability | Searches | Found | Decision |
|---|---|---|---|
| list a failed constraint and its rows | `components_index.py search "verify population"`; `git grep -n "offending_facts" docs src/gnd` | `export.verification` builds the report; the verdict already carries `offending_facts` (plan H2) | reuse: nothing is built in the package |
| a failing source that ships with the package | `components_index.py search "literature reading"`; `git grep -n "reported-conflict" src/gnd/examples` | `examples.literature_reading`: the reported conflict, verified at exit 1 by the example itself (`reading.py:404-406`) | reuse as the test's input |
| read a fenced block out of a page | `git grep -n "def parsed_blocks" tools` | `tools/run_tutorials.py:37` | reuse in the test |

### `docs/guides/documents.md` (about +35 lines)

A new section after "Ask an agent to extract, then verify its output",
titled "Reading a failed verification". It states, in this order:

1. Exit 1 means at least one alethic constraint failed. Run the command
   with `--format json`.
2. The failing constraints are the entries of `verdicts` whose `verdict` is
   `fail` and whose `modality` is `alethic`.
3. For each one: `constraint_ref` says where the constraint is declared in
   the model (`fact_types[<fact type id>].constraints[<n>]` for a constraint
   written inside a fact type, `constraints[<n>]` at the top level), so the
   constraint's own `id` is at that address in the file that declares it,
   which for an include root can be an included file;
   `constraint_type` names its kind; `message` says what it requires and
   what broke it; `offending_facts` lists the violating rows, one object per
   row with its role values.
4. A `warning` verdict is a deontic violation. It does not change the exit.
5. If the model redacts a role, `message` and `offending_facts` hold a
   marker in place of the values.
6. The text output prints the same constraints and messages without the
   rows.
7. One fenced example: the command on the literature reading example's
   reported conflict, and the one verdict it returns, trimmed to the five
   fields above.

The sentence "checker acceptance is not proof of faithfulness" stays where
it is (`extraction-contract.md:152`); the section links to it and adds no
rate (R0.3).

### Citing lines (2 lines)

- `src/gnd/skills/gnd-extract/references/extraction-contract.md`, §5, the
  row "The checker found an alethic violation": its last cell gains "see
  Reading a failed verification in the documents guide".
- `docs/literature/commands.md`, beside the line that shows the conflicting
  labels' exits: one sentence with the same link.

### What does not change

`gnd verify`, its payload, its schema version (7), its text and its exits;
`report.schema.json`; the reading example and its fixture. No source file
under `src/gnd` changes except the one packaged reference page, whose
manifest digest `tests/test_packaged_skills.py` holds.

## 7. Decisions

Every row is open.

| ID | Question | Readings and their cost | Proposed |
|---|---|---|---|
| LR1-D1 | The home of the section (plan D8) | (a) `docs/guides/documents.md`: where a reader already runs the command; the packaged skill cites a site page. (b) `extraction-contract.md` §5: travels with the installed skill, and the site page cites the package. (c) `docs/reference/cli.md`: beside the exit table, away from the worked example | (a) |
| LR1-D2 | Does `gnd verify` change (plan D7) | (a) no: a page and a test, about 35 page lines and 150 test lines. (b) the text output also prints each failing verdict's rows: about 15 source lines in the renderer, every text golden of a failing verify changes, and LR1-C5 narrows to JSON. (c) `gnd verify` accepts `--rule-ids`: the verdict then carries the constraint's declared id, the opt-in payload follows `gnd check`'s version 15, and step 3 of the section shrinks to one field | (a). No exit code differs between the three |
| LR1-D3 | How the test reads the page | (a) through the tutorial runner's block parser, comparing the page's example verdict with the live one field by field. (b) add the page to a tutorial group so the runner executes its command: the example then needs a population file on disk in the tutorial's working folder | (a); (b) if the owner wants the command itself executed from the page |
| LR1-D4 | Which fields the example shows | the five of step 3, or the whole verdict object (nine serialized fields, H2) | the five; the section names the other four in one sentence |

## 8. Tests

New file `tests/test_lr1_verify_failure_listing.py`, default lane. A fixture
runs the packaged reading example once into a temporary folder and copies
its model, vocabulary, `reported-conflict.population.json` and
`broad.population.json` beside each other. `listing(report)` in the test is
the documented steps: the `verdicts` with `verdict == "fail"` and
`modality == "alethic"`.

| # | Case | Expected |
|---|---|---|
| T1 | `gnd verify MODEL reported-conflict.population.json --no-extraction --format json` | exit 1; `listing` has one entry: `constraint_ref` `fact_types[subject_label].constraints[0]`, `constraint_type` `uniqueness`, and two `offending_facts` whose `subject` values are equal and whose `label` values differ. The declared constraint at that address, in the included vocabulary, has id `subject_has_one_label` |
| T2 | the same on `broad.population.json` | exit 0; `listing` is empty |
| T3 | every field name the section's step 3 and its example use | each is a property of the verdict in `src/gnd/report.schema.json` and a key of T1's live verdict. The page's example verdict equals T1's verdict on those fields |
| T4 | a model with one deontic uniqueness constraint and a population that violates it (the case of `tests/test_verify_cli.py:309`) | exit 0; `listing` is empty; one verdict is `warning` |
| T5 | T1's model with `redact: true` on the `label` role, the include re-pinned | exit 1; `listing` has the entry; its `message` and `offending_facts` hold the redaction marker and no label value |
| T6 | T1 and T2 in text and in JSON, at the phase base and at the head | byte-identical. Held in the phase record by digest; in the test, the JSON key set and the text's first lines equal the values written in the test at the base |
| T7 | the field list of step 3 | appears in `docs/guides/documents.md` once and in no other page under `docs/` or `src/gnd/skills/`; the two citing lines link to the section |

Branch table. The documented filter has three branches: an alethic failure
(listed), a deontic violation (not listed), a pass (not listed). T1, T4 and
T2 reach them. The redacted reading of a listed entry is T5. Every branch
has a case that fails if the filter selects by anything other than the two
fields.

Gate: the plan §9 LR1 lane with this file, the guard block of `project.md`
(the phase changes files outside `.gnd-planning/`),
`uv run ruff check src tests tools`, and
`python3 scripts/components_index.py changed --base origin/main --strict`.

## 9. Out of scope for this phase

- Any change to `gnd verify` (LR1-D2 (b) and (c)), unless the owner rules
  one in.
- A summary across many sources. A host loops over its sources.
- Why the reporter's 280 rows are unanchored (#226): that is the anchor
  sidecar's coverage, which LR2's page addresses.
- The quote rule (LR2) and the reference figures (LR3).
- A constraint too strict for the data against a reading error: the section
  shows the constraint and the rows; which of the two is wrong is the
  host's judgment.

## 10. Size

Estimate at write time: about 37 page lines (35 in the guide, 2 citing
lines), 0 source lines, about 150 test lines. The record states the measured
figures.

## 11. Approval instrument

This prose. The expected answers are exits, one constraint reference, row
counts and field names stated in §8; there is no separate answer key.
