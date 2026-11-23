# Phase LR1 · why a source fails verification · spec r2

## 1. Status

**r2, 2026-11-23, written by `process-phase` under `auto=true`.** r1 was the
draft `start-milestone` wrote against plan r2. r2 brings the spec to plan r4
(both panel rounds' fixes), rules the open rows of §7 and replaces r1's
page reader. The spec gate is recorded in the phase record once the plan gate
is ruled; no code is written before that.

## 2. Provenance

- Derives from [plan r4](literature-reading-reference-plan.md): Goal (LR1),
  §0 (R0.1, R0.3, R0.6), §1 (H1–H6, H19, H20, H22, H23, H25), §2 (LR1),
  §3 (LR1 homes and fixtures), §4 (LR1-C1 to LR1-C6), §5, §9 and §10 (D7,
  D8).
- From [#226](https://github.com/vasiloglou/gnd-public/issues/226), request
  3.
- The probe of H2–H4 was re-run at `11a7ebf7` on 2026-11-23 with the
  command H2 states. H23 and H25 were read at `11a7ebf7`.

Changes from r1 `(r2)`:

- The documented steps also list failing derivations (H23, LR1-C6).
- The page's example is a runnable tutorial block. r1 proposed reading the
  page through `parsed_blocks` (LR1-D3 (a)); that reader only reads
  `gnd-run` blocks and refuses a page with none, so r1's design could not
  be built. Executing the block is the stronger check and needs no new
  reader.
- The skill cites the guide by absolute URL (H25).
- The deontic, redacting and derivation fixtures are named (§8).

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan H1; #226 request 3 | a host can see which constraint failed, on which rows, per source | §6; T1 |
| plan H2 | the steps name only fields the report carries; the model's include is staged beside it | §6; T1, T3, the runnable block |
| plan H3 | the text output prints no rows | §6 step 7 |
| plan H4 | the declared id is not in the report | §6 step 3 |
| plan H5 | a redacting model hides message and rows | §6 step 6; T5 |
| plan H6 | no page shows the steps | §6 |
| plan H19, R0.1, LR1-C5 | default verify bytes unchanged | §6 "What does not change"; T6 |
| plan H20 | nothing lists rows for verify today | T1, T4 |
| plan H23, LR1-C6 | a derivation failure also exits 1 and is listed | §6 step 4; T8 |
| plan H25 | the skill links the guide by absolute URL | §6 citing lines; guard block |
| plan R0.3 | no rate enters the verify payload | §6 |
| plan R0.6, D8 | one home for the steps | §6; T7 |
| LR1-C1 … C6 | the criteria | T1, T2, T3, T4/T5, T6, T8 |
| plan §9 | the LR1 lane, the guard block, `uv run ruff check`, the component-index check | §8 Gate |
| `AGENTS.md`, general solutions | read structured text with its parser | §4 |

## 4. The standing rules, bound to this phase

- **Totality (1).** No package code changes. The test decodes reports with
  `json.loads` and reads the schema with `json.load`.
- **Cap bounds the document (2).** Inapplicable: no work proportional to an
  input is added.
- **Validation order (3).** Inapplicable: no refusal is added or moved.
- **One walk for N kinds (4).** The steps are one filter over `verdicts`
  and one over `derivations`, by the report's own fields, for every
  constraint family; no per-family recipe. T1 (uniqueness), T4 (value
  range), T8 (a derivation) reach three kinds.
- **One home (5).** The steps live in `docs/guides/documents.md`. The skill
  page and the literature commands page cite it in one line each and
  restate no field list; T7 holds that.
- **Measurement (6).** The report's fields were settled by running it
  (H2–H4), and the page's example is executed, not compared by eye.
- **General solutions (`AGENTS.md`).** The page block and the test select
  by `verdict`, `modality` and the array they sit in, never by a
  constraint's id, message or a fixture value. No regular expression is
  added. The page's example is read by the tutorial runner's existing
  grammar (`tools/run_tutorials.py:17`, the `gnd-run` marker), which states
  the whole grammar of the block it reads. The field names of §6 step 3 are
  a list in the test checked against the schema and the live report, not
  scraped from prose.

## 5. Goal

A reader of `docs/guides/documents.md` who runs the documented steps on a
source `gnd verify` exits 1 on gets each failing constraint or derivation
with its rows. On the reading example's reported conflict that is one
constraint and two rows; on its broad population, none. `gnd verify`'s
default text and JSON are byte-identical before and after. The LR1 lane, the
guard block, `uv run ruff check` and the component-index check exit 0.

## 6. Design

### Reuse

| Capability | Search | Found | Decision |
|---|---|---|---|
| list a failed constraint and its rows | `components_index.py search "verify population"`; `git grep offending_facts docs src/gnd` | the report already carries them (H2) | reuse; nothing built in the package |
| a failing source that ships | `search "literature reading"` | `examples.literature_reading`: the reported conflict, exit 1 (`reading.py:404-406`) | reuse as the page's and test's input |
| execute a page's example and compare its output | `git grep -n "def groups" tools` | `tools/run_tutorials.py` groups and `run_pages`; `tests/test_documentation_tutorials.py::test_documented_learning_path` | reuse: one new group |
| a deontic-only violation | `git grep -n deontic_only tests/test_verify_cli.py` | `tests/test_verify_cli.py:309-336` | reuse its model and mutation |
| a derivation failure | `git grep -n '"derivations"\]' tests` | the book tutorial fixtures (`tests/test_bookrec_tutorial.py:125-147`) | reuse the smallest failing derivation fixture the spec's implementation finds there; if none is reachable without the tutorial run, author one model with one derivation in the test |

### `docs/guides/documents.md`: "Reading a failed verification" (about +45 lines)

After "Ask an agent to extract, then verify its output":

1. Exit 1 means at least one alethic constraint or derivation failed. Run
   the same command with `--format json`. A model that includes another
   file needs it at the path its `includes` names, beside the model.
2. The failing constraints are the `verdicts` whose `verdict` is `fail` and
   whose `modality` is `alethic`.
3. Each names where it is declared by `constraint_ref`
   (`fact_types[<fact type>].constraints[<n>]`, or `constraints[<n>]` at
   the top level; the constraint's own `id` is at that address in the file
   that declares it, which for an include can be the included file), its
   kind by `constraint_type`, what it requires and what broke it in
   `message`, and the violating rows in `offending_facts`, one object per
   row with its role values.
4. The failing derivations are the `derivations` whose `verdict` is `fail`.
   Each names itself by `derivation_ref` and lists its `findings`.
5. A `warning` verdict is a deontic violation and does not change the exit.
6. A model that redacts a role shows a marker in `message` and one marker
   row in `offending_facts`. Whether the rows are shown is the disclosure
   mode's rule, whose home is `docs/reference/disclosure.md`: the step
   links it and names `--unredacted` and `GND_DISCLOSURE=internal`, and
   restates no table (plan r4).
7. The text output prints the same constraints and messages without rows.
8. One runnable block (`<!-- gnd-run expect=0 -->`, Python): it runs the
   reading example into the working folder, stages `reading.orm.json` and
   its vocabulary beside the conflict population, runs `gnd verify … --format
   json` with `--no-extraction`, applies steps 2 and 4, and prints each
   listed entry's `constraint_ref`, `constraint_type` and rows. The `text`
   block under it shows the output, which the runner compares.

The section links `extraction-contract.md`'s "checker acceptance is not
proof of faithfulness" and adds no rate (R0.3).

### Citing lines

- `src/gnd/skills/gnd-extract/references/extraction-contract.md` §5, row
  "The checker found an alethic violation", last cell: "; to list the
  failing constraints and their rows, see [Reading a failed
  verification](https://vasiloglou.github.io/gnd-public/guides/documents/#reading-a-failed-verification)".
  The packaged manifest digest moves; `tests/test_packaged_skills.py` (guard
  block) holds the new bytes through its regeneration path.
- `docs/literature/commands.md`, after the line that prints the conflicting
  labels' exits: one sentence with a relative link to the section.

### Tutorial runner (outside the plan's LR1 homes, said in the PR)

- `tools/run_tutorials.py` `groups()`: a new group `failed-verification:
  [docs/guides/documents.md]`.
- `tests/test_documentation_tutorials.py`: the group joins the
  `test_documented_learning_path` parameter list.

### What does not change

`gnd verify`, its payload, schema version 7, text and exits;
`report.schema.json`; the reading example, its fixtures and its recorded
outputs (R0.4). No file under `src/gnd` changes except the one packaged
reference page.

## 7. Decisions, ruled under `auto=true`

| ID | Question | Ruling |
|---|---|---|
| LR1-D1 (plan D8) | home of the section | (a) `docs/guides/documents.md`, as the plan gate rules D8 |
| LR1-D2 (plan D7) | does `gnd verify` change | (a) no, as the plan gate rules D7 |
| LR1-D3 `(r2)` | how the page is held | the runnable block executed by the tutorial runner (r1's reading (b)), plus the field-name list in the test. r1's (a) is withdrawn: `parsed_blocks` reads only `gnd-run` blocks (§2) |
| LR1-D4 | which fields the example prints | `constraint_ref`, `constraint_type` and the rows; `message` is named in the steps and not printed, because the example's message is long and the runner compares output byte for byte |

## 8. Tests

New file `tests/test_lr1_verify_failure_listing.py`, default lane. Every
subprocess runs with `GND_DISCLOSURE` removed from its environment unless a
case sets it. A module fixture runs the packaged reading example once into a temporary
folder and stages `reading_fixture/reading.orm.json` and
`depth_fixture/vocabulary.orm.json` beside its populations. `listing(report)`
is steps 2 and 4: `verdicts` with `verdict == "fail"` and
`modality == "alethic"`, plus `derivations` with `verdict == "fail"`.

| # | Case | Expected |
|---|---|---|
| T1 | `gnd verify` on `reported-conflict.population.json`, `--no-extraction --format json` | exit 1; one entry: `constraint_ref` `fact_types[subject_label].constraints[0]`, `constraint_type` `uniqueness`, two `offending_facts` with equal `subject` and different `label`. The constraint at that address in the staged vocabulary has id `subject_has_one_label` |
| T2 | the same on `broad.population.json` | exit 0; empty listing |
| T3 | the field names of steps 2–4 and 6 (a list in the test: `verdicts`, `verdict`, `modality`, `constraint_ref`, `constraint_type`, `message`, `offending_facts`, `derivations`, `derivation_ref`, `findings`) | each is a property at its level in `src/gnd/report.schema.json`, each occurs in the section's text, and each verdict-level name is a key of T1's live verdict (derivation-level names of T8's) |
| T4 | the deontic-only case of `tests/test_verify_cli.py:309` | exit 0; empty listing; one `warning` verdict |
| T5 | a copy of the staged vocabulary with `redact: true` on the `subject_label` fact type, and a copy of the reading model whose include pins the new digest | exit 1; one entry; `message` is the redaction marker and `offending_facts` one marker row; no label value in the payload. The same run with `--unredacted`, and once more under `GND_DISCLOSURE=internal`, shows the two rows |
| T6 | T1 and T2, text and JSON, default flags | the SHA-256 of each output equals the value pinned in the test, measured at the phase base `11a7ebf7` |
| T7 | the section | the field list appears in `docs/guides/documents.md` only; the skill page and `docs/literature/commands.md` each link the section once |
| T8 | a population that fails one derivation | exit 1; the listing holds that derivation by `derivation_ref`, with non-empty `findings` (LR1-C6) |
| T9 | the runnable block | `test_documented_learning_path[failed-verification]` exits 0 with the shown output |

Branch table. The filter has four outcomes: an alethic constraint failure
(T1), a derivation failure (T8), a deontic violation (T4), a pass (T2). The
redacted reading of a listed entry is T5. A filter that selects by anything
but `verdict`, `modality` and the array fails one of them.

Gate:

```bash
uv run pytest -q tests/test_lr1_verify_failure_listing.py tests/test_verify_cli.py tests/test_ld3_reading_workflow.py tests/test_documentation_tutorials.py --tb=short
```

plus the guard block of `project.md`, `uv run ruff check`, and
`python3 scripts/components_index.py changed --base origin/main --strict`.
The phase changes no module, so no component entry changes; if the check
asks for one, the record says why.

## 9. Out of scope

- Any change to `gnd verify` (plan D7 (b), (c)).
- A summary across many sources.
- Why the reporter's rows are unanchored (LR2's page).
- The quote rule (LR2) and the reference figures (LR3).

## 10. Size

Estimate: about 50 page lines, 2 citing lines, 2 runner lines, 0 package
source lines, about 200 test lines. The record states the measured figures.

## 11. Approval instrument

This prose and the expected exits, references, row counts and field names
of §8.
