# Phase RV1: candidate content (version, lock, manifests, notes)

## 1. Status

**r3, measured implementation scope.** The first ruling approved E1.
The second ruling binds the implementation changes below.

## 2. Provenance

This spec derives from [the plan](release-0.4.0-plan.md) r2 and its plan-gate record and from the predecessor phase
[RN1](../../release-0.3.0/003-phase-RN1.md), whose method it repeats. Two
parts of that method are left out:

- the re-record step, because issue 172 replaced it with
  `tests/support/recorded_version.py`;
- the main-repair modules, because PR 207 left the base lane clean.

The baseline is main `cc4c8bf0`. Plan r2 §11 governs this phase.

## 3. Obligations (step 0 harvest)

| Row | Obligation | Source | Discharged in |
|---|---|---|---|
| RV1-C1 | version 0.4.0 in `pyproject.toml`, the lock entry and three manifests | plan §4 | M1 to M3, T1 |
| RV1-C2 | E1 and the grep inventory are in this spec before code, with each entry classified | plan §4, V10 | E1, §12 (appended), M5 |
| RV1-C3 | one 0.4.0 notes section; every user-visible change of V8 is noted or reasoned | plan §2, V7, V8 | M4, M6, T4, the reconciliation table |
| RV1-C4 | compatibility, support and plugin pages say 0.4.0 is prepared and not published; the pins stay at 0.3.0 | plan §4 | M7 to M9, T2, T3 |
| RV1-C5 | `tests/test_release_version.py` and `tools/release_text.py check` exit 0 | plan §4 | T1 to T5 |
| RV1-C6 | the full default lane has no failure the base (V13) lacks | plan §4 | T7 |
| structure guards | issue 171: a change outside `.gnd-planning/` runs them | `project.md` | T6 |
| R1 | the bump moves recorded bytes | plan §6 | E1, D2 |
| R3 | main says 0.4.0 before PyPI | plan §6 | M6 to M9, T2 |
| RR1 finding | `uv lock` regeneration dropped an unrelated wheel line | predecessor RR1 record | M3 edits the one line by hand; `uv lock --check` |

## 4. The standing rules, bound to this phase

- Plan rule 1: no command here builds or uploads.
- Plan rule 2: M1 is the only place the version is typed as the version. T1
  checks M2 and M3 against it.
- Plan rule 3: the four pin files keep `==0.3.0` (T2).
- Plan rule 4: no recorded byte moves unless E1 shows it must. Each moved byte
  is listed with its old and new digest before code (D2).
- Plan rule 5: not applicable, because nothing is built here.
- Plan rule 6 and `project.md` rule 6: E1 runs before M5.
- Plan rule 7: `release.yml`, `tests/test_release_preparation.py` and the
  dependencies are not edited.
- Plan rule 8: bound to §10's total.
- `project.md` rule 5: each notes block summarizes its milestone's reference
  page and links to it, and adds no rule of its own.
- `project.md` rules 1 to 4: this phase adds no consumer of untrusted input,
  no input-proportional work, no validation boundary and no policy walk.

## 5. Goal

On the RV1 tree, all of the following hold:

- `uv run pytest -q tests/test_release_version.py` exits 0 with the declared
  version 0.4.0;
- `uv lock --check` exits 0;
- `uv run python tools/release_text.py check` exits 0;
- the focused gate of §8 exits 0;
- the six-shard default lane lists no failing test id outside the 2 known
  `test_public_optional` errors.

## 6. Design

### E1: the bump's effect (recorded before it runs)

- **What it measures:** which default-lane test ids change result when only
  the version changes. On a scratch tree of `cc4c8bf0`, set 0.4.0 in
  `pyproject.toml`, the lock line and the three manifests. Re-sync, run the
  six-shard default lane on beast-3, and compare against V13.
- **Expected:** no id moves, because `recorded_version.py` maps 0.3.1 outputs
  to 0.4.0. Tests that name the declared version's notes heading or its
  prepared state (`test_release_version.py`) are expected to fail until M6 to
  M9. E1 lists them.
- **What it cannot measure:** opt-in lanes (D3).
- **Liveness:** the bumped tree with no notes change must turn at least the
  `test_release_version.py` heading checks red. If it does not, the instrument
  is not reading the bump.

### Inventory (observed at `cc4c8bf0`; classified at implementation)

Outside planning and the lock:

- **0.3.1** is named by 25 tracked files: `pyproject.toml`, 3 manifests, 2
  copies of the components rules, `docs/compatibility.md`,
  `docs/expense/05-receipts.md`, `docs/release-notes.md`, `docs/releasing.md`,
  12 recorded example reports and artifacts under
  `src/gnd/examples/{expense,literature}`, and 3 tests.
- **0.3.0** is named by about 40 files.

Each file is classified as one of:

- historical: a statement about a past release;
- current pin: an install instruction, which moves only at publication;
- recorded output: compared through `recorded_version.py`;
- stale: edited here.

### Modules

| ID | Path | Change | Lines (estimate) |
|---|---|---|---|
| M1 | `pyproject.toml` | `version = "0.4.0"` | 1 |
| M2 | `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json` | `"version": "0.4.0"` | 3 |
| M3 | `uv.lock` | the editable `get-nick-done` line, by hand | 1 |
| M4 | `tests/test_release_version.py` | add a `HEADLINE_BLOCK["0.4.0"]` entry (D4). No other case changes | 1 |
| M5 | files E1 names, if any | handled as D2 rules, with the digests listed before code | 0 expected |
| M6 | `docs/release-notes.md` | edit the opening paragraph; add `## 0.4.0 (prepared, not published)` above 0.3.1, with the pointer line (plan RV-D3) and the blocks below | about 70 |
| M7 | `docs/compatibility.md` | 0.4.0 is prepared and not published, with the date availability was observed | 3 |
| M8 | `docs/support.md` | a row saying no profile is observed for 0.4.0 | 1 |
| M9 | `docs/marketplace-plugins.md` | until 0.4.0 is published, install the runtime from the repository. The pins are untouched | about 6 |

### Notes blocks (M6), proposed outline

The exact text is drafted at implementation from each milestone's close
record and reference pages. It goes into the record, and the review reads it.

1. `### Literature: identity, composition and depth` (the headline, D4), which
   links `literature/01-lineage.md` and covers:
   - LI0 to LI2: witness and why-not accept version-1 models, plus the
     literature regression corpus and its staged report;
   - LX1 to LX4: include roots with flat re-entry, `gnd compose` resolution
     files (`same`, `different`, `unresolved`), fixed reference catalogs, and
     witness and replay over them, where a changed catalog is refused;
   - LD1 to LD3: time dimensions, exact decimal replay and reading fixtures.
2. `### Guarded-rule clauses`: GC1 literal set membership, GC2 antecedent
   filters, GC3 disjunctive consequents (`any_of`), and GC4 as its record
   says.
3. `### Other changes`, which includes the expense receipts example
   (PR 205/206), the five Layer 2 rule ids added to the representation format
   (PR 207), and the guarded-rule pages (PR 191).

### V8 reconciliation table (filled at implementation)

The table has one row per user-visible change, not per pull request, and goes
into the phase record. It is built by reading
`git diff v0.3.1 cc4c8bf0 -- src` file by file. Changes that are tests only,
planning only or internal get a reason instead of a note.

### Normative order

None is added. The heading carries "not published" while 0.4.0 is not in
`RELEASED`, and that rule's one home is `tests/test_release_version.py`.

## 7. Decisions

| ID | Question | Readings and cost | Ruling |
|---|---|---|---|
| D1 | Version (plan RV-D1) | -- | 0.4.0, from the owner's request |
| D2 | If E1 moves a recorded byte | (a) fix the comparison in `recorded_version.py` or the test's `RECORDED_AT` so that no byte moves; (b) re-record that file with its digests listed. (a) keeps issue 172's promise. Either way the owner sees the list first | proposed: (a) |
| D3 | Opt-in lanes (plan RV-D8) | excluded, or run on both trees | proposed: excluded |
| D4 | The headline block for 0.4.0 | the literature block, linking `literature/01-lineage.md`, or the guarded-rule clauses block. The headline is what `HEADLINE_BLOCK` makes a test require | proposed: literature |

## 8. Tests

| ID | Case | Expected |
|---|---|---|
| T1 | `tests/test_release_version.py::test_lock_manifests_and_notes_agree_with_pyproject` and `test_drift_is_refused` | exit 0; each mutant raises `AssertionError` |
| T2 | `test_install_pins_name_a_published_version`, `test_a_pin_to_the_next_version_is_refused_until_it_is_released` | exit 0 with pins at 0.3.0; a `==0.4.0` pin fails |
| T3 | `test_notes_and_compatibility_do_not_claim_publication`, `test_support_and_plugin_pages_state_the_prepared_version` and their mutants | exit 0; mutants fail |
| T4 | `test_notes_section_names_the_headline_change` with M4, and `test_a_notes_section_without_its_headline_is_refused` | exit 0; mutants fail |
| T5 | `uv run python tools/release_text.py check`; `tests/test_recorded_version.py`; `tests/test_package_description.py` | exit 0 |
| T6 | the structure guards of `project.md`; `tests/test_marketplace_plugins.py`, `tests/test_release_docs.py`, `tests/test_release_preparation.py`; the strict docs build | exit 0 |
| T7 | six-shard default lane on beast-3 at the RV1 tree | failing ids are only the 2 known `test_public_optional` errors |

## 9. Out of scope for this phase

- Building or installing a wheel, and `tests/test_release_acceptance.py`
  (RV2).
- The install pins and `RELEASED` (publication stage).
- Any upload, tag or release.
- Any change under `src/`, unless D2 (a) needs one in a test helper.

## 10. Size

The estimate is:

- 5 config lines;
- about 70 notes lines;
- about 10 other docs lines;
- 1 test line;
- M5, expected 0.

Past 1.5 times this total, the phase pauses.

## 11. Approval instrument

This prose, plus §12 once E1 has run.

## Verification commands

```bash
uv lock --check
uv run pytest -q tests/test_release_version.py tests/test_recorded_version.py tests/test_marketplace_plugins.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_package_description.py --tb=short
uv run python tools/release_text.py check
uv run ruff check
```

The structure-guard command is the one in `project.md`. The E1 diagnostic runs [e1-shards.sh](../evidence/RV1/e1-shards.sh) via SSH
on beast-3. It clones exact base `cc4c8bf0`, changes only the five version
fields, and uses six round-robin shards over C-sorted `tests/test_*.py` with
the default pytest marker filter and recorded Python 3.13.18. Compare the
collected outcomes to V13, separately naming the two known optional wheel
errors. A runner/setup failure supplies no E1 result. The later verification
run uses the same partition and defaults at the recorded RV1 tree.

### Implementability and verification selection

- Version synchronization checks the editable lock, the three manifests,
  the current notes heading, prepared-state pages and published install pins.
  The existing headline map supports the 0.4.0 literature heading and link.
- The E1 script checks its source and changes exactly the synchronized
  release fields before locked setup. Its liveness test is a red notes-heading
  case. An unexpected change to a recorded result requires measurement and
  separate diagnosis before the second ruling.
- The RV1 record reconciles both tag ranges under plan r2 §11. The inventory
  lists historical entries, retained pins, recorded outputs and stale text.
  Record the version-bound distribution test as a carryover to RV2.
- Run all direct and affected tests named in §8, repo-wide lint, the exact
  structural guard block and the strict docs build. Leave the default marker
  filter active for the E1 and RV1 lanes. Distribution acceptance is RV2's
  separate selected gate. Historical, census and other opt-in lanes are
  excluded.
- The diagnostic and later candidate diff have separate gates. Use spec
  prose for this version synchronization, which adds no serialized format
  or exit contract. Optional spec panel omitted. The candidate diff still
  requires an independent reviewer.


## 12. E1 results and measured implementation amendments

E1 showed 19,662 passed, 13 skipped, 37 failures and the two known optional
wheel setup errors, against V13's 19,699 passed, 13 skipped and the same
errors. The 37 failures account for the entire pass-count difference. The
[shard summary](../evidence/RV1/e1-summary.txt) lists each affected ID. The
[prior-version inventory](../evidence/RV1/version-inventory.txt) classifies
the exact tracked literals. The [notes reconciliation](../evidence/RV1/notes-reconciliation.md)
covers both tag ranges, including LI3–LI5 and LD4–LD5.

| Failure set | Disposition |
|---|---|
| Five release version checks | Add the prepared heading and pages and the literature headline check. |
| Ten literature report goldens | Require the emitted live version, then use the existing version normalizer before full equality, preserving the harness hash check and detailed report expectations. |
| Two example rebuild checks | Compare each generated tree after moving only the recorded-version fields and any bound file references via the existing helper. The file sets and every other byte must agree. |
| Twenty publication text tests | Use an explicit historical tagged fixture for synthetic publication and mutation checks. Preserve the live page check and the ten stale-page negative controls. Verify actual checkout check output for its current state. |

[The byte measurement](../evidence/RV1/e1-moved-bytes.txt) lists all 12
version-bearing outputs that moved in scratch. Keep their committed bytes.
The two rebuilds were matched across their complete file sets after applying
the existing normalizer. The report comparisons retain all fields except the
version translation and the existing harness hash successor.

M5 therefore covers `tests/test_li1_assurance_report.py`,
`tests/test_li1_literature_corpus.py`, `tests/test_expense_receipts_example.py`
and `tests/test_release_text.py`. Add all four to the direct test selection.
All release-text edits are test-only. Keep the distribution acceptance case
bound to RV2 and leave the 0.3.0 install pins. Strict documentation verification
uses `uv run --group docs zensical build --strict` followed by
`uv run python tools/check_docs.py site`.

The revised estimate is 150 implementation lines, with a 225-line stop
threshold. This increases the estimate for the synthetic fixture and measured
test consumer changes. The initial estimate and ruling remain in history.
