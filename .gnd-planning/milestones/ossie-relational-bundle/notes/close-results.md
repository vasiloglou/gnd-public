# ossie-relational-bundle · close results

**Repaired after the close review** `(c2)`. The review read this file at sha256
`a1bde13803d8c51dfbfa566321fdba6fa06ddd771f9bddce97f120f4dbba0aea`; rows marked `(c2)` changed since and carry
no review opinion. The section "After the close review" at the end says what
changed in the code.

Measured 2026-11-25 on `main` at `f5462783`, which holds pull requests 266
(OB1), 270 (OB2), 271 (OB3), 272 (OB4) and 273 (OB5). The tree at `f5462783`
equals the tree tested and recorded at `979e5211`. These are the results the
close review reads beside plan r3 (`notes/ossie-relational-bundle-plan.md`)
and the delta (`notes/close-delta.md`). This file is not the close record.

## Phases

| Phase | Record | Focused lane at its record | Review (one reviewer each, Codex read-only) |
|---|---|---|---|
| OB1 size bounds | `004-phase-OB1.md` | 448 passed | 1 round; 2 findings, fixed |
| OB2 Rmap | `008-phase-OB2.md` | 110 passed | 2 rounds; 9 then 8 findings, fixed (`171665e8`); the round-2 fixes are not re-reviewed |
| OB3 relational files | `011-phase-OB3.md` | 695 passed | 1 round; 5 findings: 4 fixed (`110f805a`), 1 ruled by the owner |
| OB4 physical binding | `015-phase-OB4.md` | 925 passed | 1 round; 6 findings, fixed (`527cf956`) |
| OB5 docs and skill | `020-phase-OB5.md` | 1084 passed | 1 round; 7 findings, fixed (`7a6ccfe9`) |

Every spec was approved by the owner before implementation (`auto=false`).
OB2, OB3 and OB4 were corpus-first: hand-written expected answers were
approved before any code. Gates: `002`, `003`, `005`–`007`, `009`, `010`,
`012`–`014`, `016`–`019`.

## Exit gates on `main` at `f5462783`

| Gate | Result |
|---|---|
| `uv run pytest -q tests/test_ossie_export.py tests/test_ossie_import.py tests/test_rmap.py tests/test_ossie_relational.py tests/test_physical_binding.py tests/test_ossie_docs.py tests/test_ossie_formulas.py tests/test_rf1_cli_pins.py "tests/test_documentation_tutorials.py::test_documented_learning_path[ossie]" --tb=line` (the focused test files of the five phases' plan §9 rows; the affected consumers that §9, §5 and A3 name, the disclosure tests among them, run in the guard block below) `(c2)` | `954 passed in 164.60s`, exit 0 |
| the project guard block (16 files) | `1 failed, 865 passed, 2 deselected in 124.04s`, exit 1. The failure is `tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap`, the known red. Evidence `(c2)`: record `004` shows it failing identically on the OB1 base with the phase's diff set aside, and `git diff --stat 1926e895 f5462783 -- .agents .codex/skills/review-pr tests/test_development_scaffold.py` is empty, so the milestone touched neither the test nor the files it reads. |
| `uv run ruff check` | `All checks passed!`, exit 0 |
| `uv run --group docs zensical build --strict` | exit 0 |
| `uv run python tools/check_docs.py site` | `19530 local links/assets/anchors checked`, exit 0 |
| The opt-in Ossie oracle lane, `-k "not consumer"`, run on the owner's request at `7a6ccfe9`. `git diff 7a6ccfe9 f5462783 -- src tests tools docs` is empty `(c2)`. | `90 passed, 1 deselected in 45.26s`, exit 0 |

## Completion predicates (plan, as amended by §11)

| # | Predicate | Evidence that would fail if it were false |
|---|---|---|
| 1 | Size bound | `tests/test_ossie_export.py` (the OB1 baseline of 82 census exports under `--ontology-only`; the bound admits and refuses) and `tests/test_ossie_import.py`. **Holds for sources within the 10 MiB model cap** (A16). |
| 2 | Default run, D2 (a) | `tests/test_ossie_relational.py`: the original three files are byte-equal to the baseline with and without `--ontology-only`; a collision on any of the five paths exits 11. A model with no table writes three files (A8). **A second new failure** `(c2)`: the size bound covers the two new files, so a default run can exit 3 with `ossie:output-size` where the three-file run succeeded (A17; `test_t8_the_output_bound_covers_the_relational_files`). |
| 3 | Rmap | `tests/test_rmap.py`: the approved answer corpus, the census, determinism, the scale test at 1,400 entity types and 4,500 fact types and at 5 times that. The Rmap refuses no admitted model. D5 was ruled HALPIN by the owner (`007-OB2-D5-gate.md`) from the measurement in `notes/OB2-variant-measurement.md` `(c2)`. |
| 4 | Relational files | `tests/test_ossie_relational.py`: seven approved cases byte for byte, the pinned schemas, the one walk over every fact type and constraint, two runs equal. **Upstream validator: passed** for every census model (the oracle lane above). |
| 5 | Physical binding | `tests/test_physical_binding.py`: seven approved cases, 50 refused bindings each with its rule id, 152 pairs for the order, 910 hostile values, the no-flag baseline. Upstream validator: passed for every corpus binding and for names that are not regular identifiers. |
| 6 | Docs | `tests/test_ossie_docs.py`: every rule id, reason and flag on a page must be in the two normative sections (A18), and the release-note section must give the exit numbers of `gnd.exits` (`test_the_release_note_states_the_exits_by_their_constants`). The tutorial group `ossie` runs the commands and compares shown output. The strict build and link check. **One home** `(c2)`: these tests fail when a page names a rule the home lacks. Nothing fails when a page restates a rule in other words; that was read by one reviewer in OB5 and by this panel, and is a stated boundary. |

**External acceptance is missing.** The reporter's own checks (datasets equal
their DDL, relationships equal their foreign keys, their counts) need their
model, which is not in this repository. No reporter run is cited. D10 has not
been sent.

## Open-questions sweep

| Question | Raised in | Disposition |
|---|---|---|
| OB1-Q1: `guard_yaml`'s default `max_bytes` is captured at import, unlike `loads` | `004` | carried, owner: the repository owner; a maintenance issue to file `(c2)` |
| OB1-Q2 / D11: a source-cap parameter | `004`, plan D11 | accepted residual (A16): not added. Two separate measurements `(c2)`: OB1 measured output at about 6 times the source on its generated model, and a generated model at the reporter's stated scale (1,400 entity types, 4,500 fact types) is 1.5 MB of source. Neither is the reporter's own model, whose export they report at about 32 MiB; their source size is question 5 of the drafted message, and the answer can reopen this |
| OB2-Q1: `export/ossie.py` keeps its own "confirmed alethic" predicate beside `gnd.rmap.dispositions` | `008` | carried, owner: the repository owner; a deferred refactor, a maintenance issue to file `(c2)` |
| OB2-Q2: `refscheme.reference_identity` ignores `preferred` and confirmation | `008` | carried, owner: the repository owner; a separate issue to file; the Rmap does not use it `(c2)` |
| OB2-Q3, OB3-Q4, OB4-Q2: more review rounds on phase repairs | `008`, `011`, `015` | closed by rulings ("Move on to OB3", "Merge 271, start OB4", H10); the files are listed below as carrying no review opinion |
| OB3-Q1, OB3-Q2: the four OB3 departures | `011` | closed: accepted (`012`) |
| OB3-Q3: run the oracle lane | `011` | closed: run on request (`018`); it found the quoting defect, repaired (`019`) |
| OB3-Q5: identifiers the ontology does not declare (unit-based references, multi-supertype subtypes) | `011` | carried, owner: the repository owner; a successor question for the ontology export `(c2)` |
| OB3-Q6: one fixture-model scan | `011` | closed: `tests/support/model_scan.py` (OB4) |
| OB4-Q1: the two OB4 rules | `015` | closed: accepted (`016`) |
| OB4-Q3: does the reporter's schema use surrogate keys | `015` | carried, owner: the repository owner; it is question 3 of the drafted reporter message (`notes/D10-drafts.md`) `(c2)` |
| OB4-Q4: one RFC 6901 pointer helper for four private ones | `015` | carried, owner: the repository owner; a deferred refactor, a maintenance issue to file `(c2)` |
| OB4-Q5: one depth bound instead of two | `015` | retired: the 32-role and 8-level limits bound different recursions |
| OB4-Q6: the OB2 timing test failed once in a long run | `015` | accepted residual: left as is; it passed in every run since, including this close's `(c2)` |
| OB5-Q1: a non-ASCII letter upper-cases by the exporter's Unicode tables | `020` | accepted residual `(c2)`: the owner answered "go with your recs" on 2026-11-25 to the proposal to accept it as a stated limit; it is in the normative text |
| OB5-Q2: the OB5 repairs and the quoting fix are not re-reviewed | `020` | closed `(c2)`: the close review read them; its one code finding is the name-collision rule, repaired below |
| OB5-Q3: the oracle lane's consumer test | `020` | accepted residual: not run; it measures the PyRel converter, which this milestone does not change |
| D10: ask the reporter; file the three issues | plan D10 | carried, owner: the repository owner; the texts are drafted in `notes/D10-drafts.md` and nothing is sent until the owner confirms each `(c2)` |

## Files that carry no review opinion

`review_tool.py status` over the milestone's rounds reports 67 files as
reviewed and these source and page files as changed after the last round
that read them (the repairs of that round's own findings):

- `src/gnd/input_policy.py`, `src/gnd/ossie_import.py`, `tests/test_ossie_import.py` (OB1)
- `src/gnd/export/physical_binding.py` (OB4)
- `src/gnd/export/ossie_relational.py` is **not** on this list `(c2)`: the OB5 review read it after the quoting fix. It changed again after the close review; see below.
- `src/gnd/skills/gnd-orm-core/references/representation-format.md`,
  `docs/explanation/ossie.md`, `docs/how-to/share-an-ossie-ontology.md`,
  `docs/release-notes.md`, `tests/test_ossie_docs.py`,
  `tests/test_ossie_relational.py`, `tests/test_ossie_external_oracle.py`,
  `tests/support/ossie_relational_corpus.py` (OB5)

## Residuals

- External acceptance by the reporter: missing.
- Sources above the 10 MiB model cap still cannot be exported.
- A fact held only through a surrogate key cannot be bound.
- A non-ASCII name can miss a reader on other Unicode tables (OB5-Q1).
- Import reads the ontology only; the relational files are not imported.

## After the close review `(c2)`

The light panel at effort high ran over plan r3, this file and the delta
(`evidence/close-review/PANEL-REVIEW.md`; dispositions in
`evidence/close-review/disposition.md`). Five of six seats succeeded and all
five asked for revision.

**Code changed after the review:**

- `binding:name-collision` compared names after upper-casing, so two tables
  that are not regular identifiers and differ only in case, such as
  `fin.cust` and `FIN.CUST`, were refused. It now compares Ossie's
  normalized form through `normalized_identifier`, which `_quoted` also
  uses. Test: `test_close_names_collide_by_ossies_normalized_form`, which
  failed before the fix. The pinned validator accepts two such datasets in
  one semantic model (checked by hand in the oracle environment).
- The release note says the size bound covers the two new files (A17).

**The oracle lane was re-run on the final code** on the owner's request
(2026-11-25), at `98344052`: `91 passed, 1 deselected in 64.80s`, exit 0. It
includes a new case, `test_external_tables_that_differ_only_in_case`. The
consumer test was again not run.

**Gates on the repaired tree** are in the close record.
