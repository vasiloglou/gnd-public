# Phase RN1: candidate content (version, lock, manifests, notes)

## 1. Status

**Owner-decided (2026-11-11): approved, with D6 as recommended** ("Approve,
start RN1", answering "Approve the RN1 spec, with the redaction sentence in
the notes (D6) as recommended?"). The approved bytes are r3 at commit
`e34059b4`, sha256 `89312abe14c8a1dfa360632c0b9d9add3be02406ac5a2d10af22e4ae6ff7eba8`. D7 stays open; it does not block this phase and
must be answered before RN2. Implementation follows; findings are appended
below.

## 2. Provenance

Derives from [the plan](release-0.3.0-plan.md) r2 (approved 2026-11-10) with
its §12 amendment, from [RN0](../002-phase-RN0.md), and from the predecessor
phase [RR1](../../rule-check-release/002-phase-RR1.md) and its
[spec](../../rule-check-release/notes/phase-RR1-spec.md), whose method this
phase repeats. Baseline: main `d7317d25` (the PR 162 merge; RN0 included).

r1 (sha256 `70418c41…7b3`) was read by the plan's one reviewer (Codex,
`revise`; plan §11); changes for it are tagged `(r1)`, owner rulings `(o)`.
r3 (2026-11-11) rewrites the status, the base, M5, M10, M11 and the tests from
measurements taken after RN0, and adds §13 and the notes text of §6; those
bytes have had no review.

## 3. Obligations (step 0 harvest)

| Row | Obligation | Source | Discharged in |
|---|---|---|---|
| RN1-C1 | version 0.3.0 in `pyproject.toml`, lock entry, three manifests | plan §4 | M1 to M3, T1 |
| RN1-C2 | E1 list and grep inventory in the spec before code, each entry classified | plan §4, N12, N13 | E1, §12 (to be appended), M5 |
| RN1-C3 | one 0.3.0 notes section, Ossie first; every user-visible change of N9 noted or reasoned | plan §2, N8, N9, N25 | M6, T5, T9, the reconciliation table of §6 |
| RN1-C4 | compatibility, support and plugin pages say prepared, not published; pins stay 0.2.0 | plan §4, N15 | M7 to M9, T2, T3, T10 (r1) |
| RN1-C5 | `tests/test_release_version.py` exits 0; its mutants fail | plan §4 | T1 to T3 |
| RN1-C6 | full default lane: no failure the merge base lacks | plan §4, N22 | T7 |
| RN1-C7 | the `grow-a-model.md` paragraph test and the scaffold reference test exit 0 | plan N20, N26, RN-D10 (ruled: fix) | M10, M11, T6 |
| RN0 open question | the redaction behavior of Ossie export is stated where users read it | `002-phase-RN0.md` | M6 (the notes block), D6 |
| RN0 refuted premise | a focused gate that omits a docs-mirror test is not impact closure | `002-phase-RN0.md` | §8 adds `tests/test_disclosure_docs.py` and the release-notes and docs tests |
| N14 | the carried fixtures refactor has a ruling | predecessor close | D2 |
| R1 | moved recorded bytes | plan §6 | E1, D2 |
| R3 | main at 0.3.0 before PyPI | plan §6 | M6 to M9, T2 |
| RR1 finding | `uv lock` regeneration dropped an unrelated wheel line | `002-phase-RR1.md` | M3 edits the one line by hand; `uv lock --check` |
| RR1 F2, F3 | publication guard and version mask defects | `002-phase-RR1.md` | already tested in `tests/test_release_version.py` and `tests/test_rf1_pin_harness.py`; rerun in T1, T4 |

## 4. The standing rules, bound to this phase

- Plan rule 1 (prepare, never publish): no command here builds or uploads.
- Plan rule 2 (one home): M1 is the only place the number is typed as the
  version; M2 and M3 are checked against it by T1.
- Plan rule 3 (no unpublished pin): M9 leaves the four pin files alone; T2.
- Plan rule 4 (evidence belongs to exact bytes) (r1): M11 leaves the retained
  ossie snapshots byte-identical; the registry entry carries each digest and
  the scaffold test's snapshot case checks it. M5 re-records only outputs
  whose purpose is to equal the current command's output, each digest listed
  old and new before code.
- Plan rule 5 (carrying is shown by running): not applicable; nothing is
  built or installed in RN1 (RN2).
- Plan rule 8 (size stop) (r1): bound to §10's total once E1 gives M5's size;
  past 1.5 times that total the phase pauses.
- Plan rule 6 and `project.md` rule 6 (measure): E1 runs before M5 is written.
- Plan rule 7 (frozen surfaces): no edit to `release.yml`,
  `tests/test_release_preparation.py` or dependencies; M3 changes one line.
- `project.md` rule 5 (one home for prose): the Ossie scope is stated in
  `docs/explanation/ossie.md`; the notes summarize and link to it, and add no
  rule of their own.
- `project.md` rules 1 to 4: no new consumer of untrusted input, no new
  input-proportional work, no new validation boundary, no policy walk.

## 5. Goal

On the RN1 tree `uv run pytest -q tests/test_release_version.py` exits 0 with
the declared version 0.3.0, `uv lock --check` exits 0, the focused gate of §8
exits 0, and the six-shard default lane lists no failing test id that the
merge base's lane lacks.

## 6. Design

### E1: the bump's effect (recorded before it runs)

- **Measures:** which default-lane test ids change result when only the
  version changes. On a scratch copy of `2490dd77`: set 0.3.0 in
  `pyproject.toml`, the lock line and the three manifests, re-sync, run the
  six-shard default lane on beast-3; run the same lane on the unchanged tree;
  compare the failing-id lists.
- **Cannot measure:** opt-in lanes (D3); any site read only by them.
- **Liveness:** the 0.2.0 bump moved 47 ids with this instrument, so it can
  show a nonzero result; the unchanged tree is the zero end, apart from the two
  known failures (N20, N26) and the two known `tests/test_public_optional.py` errors.
- **Limits:** one run per tree on one machine. Results are appended as §12
  before any code, with each moved file classified as in RR1 spec §13.

### Modules

| ID | Path | Change | Lines (estimate) |
|---|---|---|---|
| M1 | `pyproject.toml` | `version = "0.3.0"` | 1 |
| M2 | `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json` | `"version": "0.3.0"` | 3 |
| M3 | `uv.lock` | the editable `get-nick-done` line, by hand | 1 |
| M4 | `tests/test_release_version.py` | no change to the existing cases: the reviewer ran all 22 against an in-memory 0.3.0 tree and they passed. New cases T9 and T10 (r1) | about 40 |
| M5 | 22 fixture files and 8 test files (§13) | run [rerecord.py](../evidence/RN1/rerecord.py) on the bumped tree: it moves the recorded `gnd_version` to 0.3.0 and re-derives the digests that follow, and refuses any other difference. The result must equal the measured digests of [moved-digests.md](../evidence/e1/moved-digests.md) | 445 lines, generated |
| M6 | `docs/release-notes.md` | opening paragraph; `## 0.3.0 (prepared, not published)`; a new first block "Ossie interchange"; the seven present subsections kept in order | about 60 new, 110 moved |
| M7 | `docs/compatibility.md` | 0.3.0 is prepared and not published; availability observed, with its date | 3 |
| M8 | `docs/support.md` | no profile is yet observed for 0.3.0 | 2 |
| M9 | `docs/marketplace-plugins.md` | until 0.3.0 is published, install the runtime from the repository; pins untouched in all four pin files | about 6 |
| M10 | `docs/how-to/grow-a-model.md` | one blank line: the 141-word paragraph is split before "There is one exception:", giving 65 and 76 words (measured). No word changes | 1 |
| M11 | `tests/test_development_scaffold.py` | (r1) add two entries to `RETAINED_DOCUMENT_ORIGINS`: `ossie-interchange/evidence/OS1/spec-r1.md` with origin `notes/phase-OS1-spec.md` and digest `b17b7743…3353`, and `ossie-interchange/evidence/OS0/spec-r4.md` with origin `notes/phase-OS0-spec.md` and digest `47b62ba0…eefd`. Measured at `d7317d25` with the test's own walk: these two files hold the only four unresolved links in the tree, and all four resolve from those origins. No evidence byte changes | about 8 |

### The Ossie notes block (M6), proposed text

Approved with this spec (D5). Every sentence is taken from
`docs/explanation/ossie.md`, `docs/how-to/share-an-ossie-ontology.md`, the
commands' `--help`, `src/gnd/schema/ossie/PINNED.json` and
`docs/reference/disclosure.md`. Links are written out as paths here, because a
relative link in this note would not resolve from this directory.

> ### Apache Ossie interchange
>
> GND can share a model as an Apache Ossie ontology and start a model from
> one. ("Apache Ossie" links to `explanation/ossie.md`.)
>
> - **Export.** `gnd export ossie MODEL --out ONTOLOGY.yaml` writes three
>   files: the ontology, a sidecar (`ONTOLOGY.yaml.gnd.json`) that keeps the
>   GND details Ossie has no place for, and a loss report
>   (`ONTOLOGY.yaml.loss.json`) that lists each source field and how it was
>   handled. `--format json` writes JSON. Example populations are omitted and
>   listed in the report; `--strict` stops the export when any field would be
>   refused.
> - **Import.** `gnd import ossie ONTOLOGY.yaml --out MODEL.json` writes a GND
>   model and its own loss report. With the sidecar beside an unchanged
>   ontology, the original model is restored and the report says whether its
>   identity matched. An ontology from another tool imports through the
>   supported projection. Import opens no network connection.
> - **Scope.** The ontology layer of Ossie `0.3.0.dev0`, pinned to Apache
>   Ossie commit `ee89dbdc`: concepts, relationships and a documented subset
>   of constraint formulas. Ossie's semantic models, mappings and query
>   interfaces are outside it.
> - **Disclosure.** Both commands behave the same in every disclosure mode.
>   An export writes the model's constraint literals and description text,
>   also for a fact type marked `redact`. Read the loss report before you
>   share an export.
>
> Start with sharing the refunds example (links to
> `how-to/share-an-ossie-ontology.md`).
> The mapping is in the `gnd-orm-core` representation format, "Ossie
> interchange".

The Ossie version string `0.3.0.dev0` is the upstream format's own and is
unrelated to this package's 0.3.0.

### N9 reconciliation table (filled at implementation)

One row per user-visible change, not per pull request (r1): the note that
covers it, or the reason none is needed (tests only, planning only,
internal). Rows known to have no note today: PR 68, hashability recheck on
Python 3.14; PR 136, null `derivations` in coverage, in session snapshots and
in the redaction diff (three rows); the role-name repairs in three packaged
`gnd-model-from-text` examples. The table is built from `git diff v0.2.0 HEAD
-- src` read file by file, and goes into the phase record.

### Normative order

None added. The notes heading must carry "not published" while 0.3.0 is not in
`RELEASED`; that rule's one home is `tests/test_release_version.py`.

## 7. Decisions

| ID | Question | Readings and cost | Ruling |
|---|---|---|---|
| D1 | The version (plan RN-D1) | -- | **Ruled (o, 2026-11-10): 0.3.0** |
| D2 | How are E1's moved bytes handled (plan RN-D7)? | Method: **Ruled (o, 2026-11-10): as proposed** ("Approve as proposed", answering "How do you rule on the open plan decisions RN-D0 and RN-D3 to RN-D11?"): re-record as for 0.2.0 and carry the refactor to an issue (o). Per file (r3): §12.1 classifies all 31 as current-output records and §13 lists every file's old and new digest; no file raised the reserved question | method ruled (o); the per-file list is approved with this spec |
| D3 | Opt-in lanes in E1 and the gate (plan RN-D11) | run them on both trees, or record them as excluded as for 0.2.0 | **Ruled (o, 2026-11-10): as proposed** ("Approve as proposed", answering "How do you rule on the open plan decisions RN-D0 and RN-D3 to RN-D11?"): excluded (o) |
| D4 | The two red tests on main (plan RN-D10) | fix both here, each as its own commit (M10, M11), or leave them as known failures | **Ruled (o, 2026-11-10): as proposed** ("Approve as proposed", answering "How do you rule on the open plan decisions RN-D0 and RN-D3 to RN-D11?"): fix both (o). The ruling was given when M11 meant editing the links; after the review M11 registers the snapshots instead and changes no evidence (r1). The owner sees this change at the plan gate |
| D5 | Notes shape (plan RN-D3) | as §6, or the present sections renamed in place | **Ruled (o, 2026-11-10): as proposed** ("Approve as proposed", answering "How do you rule on the open plan decisions RN-D0 and RN-D3 to RN-D11?"): as §6 (o). The Ossie block's wording is approved with this spec |

| D6 | Does the 0.3.0 notes block state that Ossie export does not honor `redact` (RN0 open question)? | (a) yes, one sentence under "Disclosure", as drafted in §6: users learn it before they share a file; the behavior itself is unchanged. (b) say nothing in the notes; the reference page already says it. (c) hold 0.3.0 until export honors `redact`: a product change with its own phase, not planned | **Ruled (o, 2026-11-11): (a)**, with the spec approval |
| D7 | The opt-in `ossie_oracle` lane after RN0's source edits (RN0 D5, not yet answered) | run it before RN2 builds the candidate, which needs the pinned checkout's path in `GND_OSSIE_ORACLE_ROOT`; or accept for 0.3.0 that the changed exporter is checked by the default-lane Ossie tests and RN0's byte comparison only. RN1 changes no Ossie source, so this does not block RN1 | open; it must be answered before RN2 |

## 8. Tests

| ID | Case | Expected |
|---|---|---|
| T1 | `tests/test_release_version.py::test_lock_manifests_and_notes_agree_with_pyproject` and `test_drift_is_refused` (4 sites) | exit 0; each mutant raises `AssertionError` |
| T2 | `test_install_pins_name_a_published_version`, `test_a_pin_to_the_next_version_is_refused_until_it_is_released` | exit 0 with pins at 0.2.0; a `==0.3.0` pin fails |
| T3 | `test_notes_and_compatibility_do_not_claim_publication` and its mutants | exit 0; mutants fail |
| T4 | `tests/test_marketplace_plugins.py`, `tests/test_rf1_pin_harness.py` | exit 0 |
| T5 | `tests/test_release_docs.py`, `tests/test_release_preparation.py`; strict docs build and `tools/check_docs.py site` | exit 0 (the new notes links resolve; the workflow is untouched) |
| T6 | `tests/test_plan_app_docs.py`; `tests/test_development_scaffold.py`, including its per-snapshot cases for the two entries M11 adds (`none`, `changed-snapshot`, `missing-target`) | exit 0; both files are exit 1 on the base `d7317d25`. A changed snapshot byte fails the digest case |
| T9 (r1) | new `test_notes_section_names_the_headline_change` in `tests/test_release_version.py`: the declared version's section has an Ossie `###` block that links `explanation/ossie.md` | exit 0; a mutant section without the block raises `AssertionError` |
| T10 (r1) | new `test_support_and_plugin_pages_state_the_prepared_version`: while the declared version is not in `RELEASED`, `docs/support.md` names it as having no observed profile and `docs/marketplace-plugins.md` gives the repository route | exit 0; an empty support page and a plugin page without the route each raise `AssertionError` |
| T7 | six-shard default lane on beast-3, base and RN1 tree | the RN1 failing-id list has no id the base list lacks |
| T8 | the 14 files E1 names, with `tests/test_rf1_pin_harness.py` and `tests/test_rf1_cli_pins.py` | exit 0 after M5 (measured in scratch: `440 passed`); on the bumped tree before M5, `31 failed, 242 passed` over the 14 |
| T11 (r3) | after M5, `git diff` of the 30 files against `d7317d25`, each file's sha256 | equals the New column of `evidence/e1/moved-digests.md`; any other digest stops the phase |
| T12 (r3) | `tests/test_disclosure_docs.py`, `tests/test_release_docs.py`, strict docs build and `tools/check_docs.py site` | exit 0 |

Branches without a failing case: none of T1 to T3 is new, and each already has
a mutant. T9 and T10 hold only while 0.3.0 is unreleased; their released
branch is exercised by a case with a synthetic `RELEASED`, as the existing
pin tests do. The completeness of the notes beyond the Ossie block has no
test: it is shown by the reconciliation table, which a reviewer can diff
against `git diff v0.2.0 HEAD -- src` (r1). T7 compares lists, so it cannot pass by both trees failing alike in
a new place; the base list is recorded first.

## 9. Out of scope for this phase

Building or installing a wheel; `tests/test_public_distribution.py` and
`tests/test_release_acceptance.py` (RN2); install pins and `RELEASED` (RN3
patch); any upload, tag or release; any change under `src/`.

## 10. Size

Estimate: 5 config lines, about 80 new notes lines and 110 moved, about 20
other docs lines, about 50 test lines (M4, M11) (r1; was 0), and M5's 445
generated lines in 30 files (measured, §13). The stop rule
applies to the total once E1 gives M5's size.

## 11. Approval instrument

This prose, with §12 and §13.

## Verification commands

```bash
uv lock --check
uv run pytest -q tests/test_release_version.py tests/test_marketplace_plugins.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_rf1_pin_harness.py --tb=short
uv run ruff check
```

The lane is the E1 instrument (`evidence/e1/README.md`). Nothing is
unresolved.

## 12. E1 results (2026-11-11 UTC, appended; the experiment is the one recorded in §6)

Retained outputs and method: [evidence/e1](../evidence/e1/README.md).

| Tree | Passed | Failed | Errors |
|---|---|---|---|
| base, main `2490dd77` | 18,971 | 26 | 2 |
| bumped, M1 to M3 only | 18,936 | 61 | 2 |

Thirty-five ids fail only at the bump; none of the base failures disappears.

### 12.1 Classification of the 35

| Test (failures) | Class | Handling |
|---|---|---|
| `test_release_version.py` (4): agreement, its control, the notes drift case, the publication-claim case | expected: the notes have no 0.3.0 heading on the E1 tree | M6 and M7; no test edit |
| `test_rf1_semantic_pins.py::test_synth` (8), `test_tp2_shared_fact_types.py` (1) | current-output record | (b), as RR1 spec §13.1 |
| `test_object_type_description.py` (4) | current-output record | (b) |
| `test_rf2_pre_move_pins.py::test_measure_output_bytes` (1) | current-output record | (b), through `measure-successor.json` |
| `test_ik6_walk.py::test_t2` (1) | current-output record | (b) |
| `test_fidelity_stub_gate.py` (1) | current-output record | (b) |
| `test_public_extract_controls.py` (5) | current-output record | (b) |
| `test_public_coverage_goldens.py` (3) | current-output record | (b) |
| `test_public_measurement_publication.py` (2) | current-output record | (b) |
| `test_public_measure_corpus.py` (1) | current-output record | (b) |
| `test_public_legacy_codegen_pins.py` (1) | current-output record | (b) |
| `test_public_book_runtime.py` (1), `test_public_book_skills.py` (1) | current-output record | (b) |
| `test_public_expense_current.py` (1) | current-output record | (b) |

The 31 non-release ids are the same ids as the 31 method-(b) failures of the
0.2.0 bump, so D2's ruled method covers every one and no file raises the new
question D2 reserved. The 16 `test_extract` ids of the 0.2.0 bump do not fail:
method (a) holds. M5 is therefore the same set of sites as RR1's M5b to M5n
(31 files, 7 gzip containers at that time); its size estimate is the measured
size of that edit.

The moved digests are in §13.

### 12.2 A premise of this spec was refuted, and is settled

r2 assumed main had two red default-lane tests. E1's base lane had 26
(evidence README). The owner added phase RN0 (plan §12), which repaired 24;
[its record](../002-phase-RN0.md) shows the lane at `326a1900` with the 2
known errors and the two tests this phase owns (M10, M11), and nothing else.

## 13. Moved digests and the lane at the changed tree (2026-11-11, appended before any code)

E1 ran on `2490dd77`, before RN0. On main `d7317d25` with M1 to M3 applied in
a scratch copy, the 14 files of §12.1 gave `31 failed, 242 passed`: the same
31 ids.

M5 was then measured in that scratch copy by a script,
[rerecord.py](../evidence/RN1/rerecord.py), written for this purpose by a
subagent of this session under a brief that allowed only recorded data and
digest literals to change, and then checked here:

- the 16 affected test files give `440 passed` on the scratch tree (run twice,
  once by the subagent and once by this session);
- 30 files change, 445 insertions and 445 deletions; every one is listed with
  its old and new sha256 in [moved-digests.md](../evidence/e1/moved-digests.md);
- every changed value is the version, a digest that follows from it, or the
  one sentence appended to `measure-successor.json`'s reason. This session
  checked that separately from the script (the evidence file says how);
- the file set equals the fixture and pin files of the 0.2.0 bump
  (`5a1c9d57`); members that record an older version on purpose are
  untouched, as then.

How each value was obtained: the RF1 synth goldens, the IK1 and IK6 digests,
the two measurement payloads, the roundtrip artifact, the RF2 successor and
the extract-controls answers come from running the command or the test's own
capture path. For five containers (book runtime and skills, expense,
legacy codegen, coverage goldens, measure corpus) the script moves the
version inside the stored document and re-derives the digests; the owning
tests compare those bytes with the live command and pass.

Limits: the capture ran under Python 3.14 only, and the moved goldens are not
interpreter-keyed files; the 3.11 and 3.13 legs were not run. The script
exists in this repository only as evidence; it is run from a scratch `_work`
directory and leaves no file behind.

### 13.1 The lane at the scratch tree

The six-shard default lane on the scratch tree (M1 to M3 and M5, commit
`7923ac98`, not in this repository; [output](../evidence/RN1/lane-scratch-m5.txt)):
18,992 passed, 6 failed, 2 errors. The failing list is the 2 known
`tests/test_public_optional.py` errors, N20, N26, and four
`tests/test_release_version.py` ids (agreement, its control, the notes drift
case, the publication-claim case), which need the 0.3.0 notes heading and the
compatibility sentence (M6, M7). No other test fails, so M5 moves nothing the
lane can see beyond the 31.

## Implementation findings, recorded as they were found (2026-11-11)

1. **M1 to M3.** `uv lock --check` exits 0 after the one-line lock edit.
2. **M5 and T11.** `rerecord.py` ran in the repository from a temporary
   `_work` directory, since removed; it stopped no family. All 30 files have
   the sha256 of the New column of `evidence/e1/moved-digests.md` (0
   mismatches).
3. **Refutes M10.** The spec said one paragraph of
   `docs/how-to/grow-a-model.md` is over the limit. There are two: the test
   stops at the first, so the second (115 words, "A program that proposes
   only fact types...") was hidden. Both are split at a sentence boundary with
   no word changed. A walk over every checked page with the test's own
   `prose` function finds no other paragraph over 90 words.
4. **M11 as designed.** Two registry entries; the test's own parametrized
   cases (`none`, `changed-snapshot`, `missing-target`) run for both.
5. **M4.** Two helpers and six test functions (three parametrized) are added
   to `tests/test_release_version.py`. Run against the base pages, T9 fails
   with "the 0.3.0 notes do not open with '### Apache Ossie interchange'" and
   T10 with "docs/support.md has no row saying no profile is observed for
   0.3.0". The existing cases are unchanged.
6. **M6.** The notes block is the approved text with its links restored. The
   "Fixes" list gains four entries (Python 3.14 prepared-policy reuse, null
   `derivations`, the example role names, the disclosure reference). The
   reconciliation table is in the phase record.
7. **M9.** The plugin page already told a `main` user to install from the
   repository; one sentence now says that this is the present state and
   names 0.3.0 as prepared and not published.
8. **Lint.** The two findings `ruff` reports in
   `tests/test_development_scaffold.py` (lines 50 and 52) are on the base
   tree; the lines this phase adds have none.

## Review findings (2026-11-11, appended)

One reviewer, Codex, over `d7317d25..73884f6c` outside `.gnd-planning/`
([retained output](phase-RN1-codex-review.md)): `revise`, 7 findings. Each was
reproduced before it was accepted.

| Finding | Reproduced | Triage | Fix |
|---|---|---|---|
| F1 the notes said an import with its sidecar restores the original model | yes: exporting and importing the growth example gives `source_identity_verified: false` and no `sample_population`; the format reference says "Exported omissions remain omissions on import" | blocking: a false sentence in the notes. It was in the block the owner approved, taken from the explanation page, which says "restores those details" | the Import bullet now says the kept content is restored, that omissions stay omitted and that the identity then does not match |
| F2 no note for model format version 5 and its incompatibility with 0.2.0 | yes: the schema diff since `v0.2.0` adds `includes`, `fact_type_constraints` and version 5; the evolution contract documents `repin-include`, `before_includes`, `candidate_includes`; `--previous-include` is in `gnd evolve preview --help` | blocking: `docs/compatibility.md` requires incompatibilities in the notes | three bullets under "Shared definitions" |
| F3 no note for the stricter additive rule | yes: `tests/test_evolve_population_check.py::test_close_r1_f1_flag_free_...` and the unattended-model-growth close (R1-F1) record that the flag-free walk admitted such a constraint before the fix | blocking: a behavior change against 0.2.0 | a paragraph under "Constraints admitted on clean data" |
| F4 `gnd verbalize model` and `gnd.api.verbalize_model` unnamed | yes: both exist; the disclosure table rows say every mode | hardening | a bullet under "Shared definitions" |
| F5 the unattended procedure's "Acting on a shape match" unnoted | yes: the section is new since `v0.2.0` | completeness, done because it is one paragraph | a paragraph under "A growth round can declare its source document" |
| F6 the headline check accepted a link outside the headline block | yes: the old helper accepts that input (run against `73884f6c`), the new one refuses it | hardening | the link is searched inside the block; mutant `link-in-a-later-block` |
| F7 the page check accepted a row observing another version, and a publication claim on the plugin page | yes: both inputs accepted at `73884f6c`, refused now | hardening | the observation must name the declared version; the plugin page is scanned for a claim; mutants `support-observes-another`, `plugins-claim` |

**Corrects the approved notes text of §6, kept as written above.** The Import
bullet's sentence "the original model is restored" was wrong for any model
with populations. The owner approved that wording; the corrected wording is in
the phase record for the owner to see.

**Refutes plan RN1-C3's method as the spec applied it.** The reconciliation
started from the present notes and the list of pull requests. F2 to F5 are
changes inside pull requests that already had a note. The reviewer found them
by reading `git diff v0.2.0 -- src`; the record's table is rebuilt that way.

## Lane findings (2026-11-11, appended)

- The lane at `73884f6c` (before the review fixes) listed only the 2 known
  errors: N20 and N26 are repaired and the bump adds no failure.
- The lane at `a46952b5` (after the review fixes) listed the 2 known errors
  and one failure this phase caused:
  `tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap`.
  The retained review output quotes one line of test code and one mutant
  input that have the shape of a markdown link, which the reference check
  reads as links. Both strings are now in `RETAINED_EXTERNAL_REFERENCES` for that one
  file, as verbatim reviewer text; the review file is not edited. The focused
  gate had run before the review file existed.
- After `a46952b5` the notes gained one sentence
  (`include:unsupported-route`, commit `7fba7d9e`): a route that does not
  support a model with includes refuses it. Confirmed by running the Ossie
  exporter on the packaged `sales.orm.json`.
- The lane at `40af7c87` failed the same test again, on this file: the
  paragraph above first repeated the two quoted strings. It now describes
  them without their link syntax. The scaffold test had been run before that
  paragraph was written, not after.
