# Phase RN1: candidate content (version, lock, manifests, notes)

## 1. Status

**Blocked draft r2, 2026-11-10; E1 appended 2026-11-11 (§12). Not
implementable.** The plan gate is passed and E1 has run. It now needs: the
owner's ruling on the plan amendment E1 raised (plan §12: main's lane is red
by 26); the moved digests measured in a scratch copy (§12, still owed); then
this spec's own owner gate. No code is written.

## 2. Provenance

Derives from [the plan](release-0.3.0-plan.md) r1 (draft, not reviewed), §4
RN1, and from the predecessor phase
[RR1](../../rule-check-release/002-phase-RR1.md) and its
[spec](../../rule-check-release/notes/phase-RR1-spec.md), whose method this
phase repeats for a second bump. Baseline: main `2490dd77`. r1 (sha256
`70418c41…7b3`, uncommitted) was read by the plan's one reviewer (Codex,
`revise`; plan §11). Changes applied for it are tagged `(r1)`; owner rulings
`(o)`. The repaired bytes carry no review opinion.

## 3. Obligations (step 0 harvest)

| Row | Obligation | Source | Discharged in |
|---|---|---|---|
| RN1-C1 | version 0.3.0 in `pyproject.toml`, lock entry, three manifests | plan §4 | M1 to M3, T1 |
| RN1-C2 | E1 list and grep inventory in the spec before code, each entry classified | plan §4, N12, N13 | E1, §12 (to be appended), M5 |
| RN1-C3 | one 0.3.0 notes section, Ossie first; every user-visible change of N9 noted or reasoned | plan §2, N8, N9, N25 | M6, T5, T9, the reconciliation table of §6 |
| RN1-C4 | compatibility, support and plugin pages say prepared, not published; pins stay 0.2.0 | plan §4, N15 | M7 to M9, T2, T3, T10 (r1) |
| RN1-C5 | `tests/test_release_version.py` exits 0; its mutants fail | plan §4 | T1 to T3 |
| RN1-C6 | full default lane: no failure the merge base lacks | plan §4, N22 | T7 |
| RN1-C7 | the `grow-a-model.md` paragraph test and the scaffold reference test exit 0, if D4 rules "fix" | plan N20, N26, RN-D10 | M10, M11, T6 |
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
| M5 | per D2 and E1 | the recorded outputs E1 names | unknown until E1; 31 files for 0.2.0 |
| M6 | `docs/release-notes.md` | opening paragraph; `## 0.3.0 (prepared, not published)`; a new first block "Ossie interchange"; the seven present subsections kept in order | about 60 new, 110 moved |
| M7 | `docs/compatibility.md` | 0.3.0 is prepared and not published; availability observed, with its date | 3 |
| M8 | `docs/support.md` | no profile is yet observed for 0.3.0 | 2 |
| M9 | `docs/marketplace-plugins.md` | until 0.3.0 is published, install the runtime from the repository; pins untouched in all four pin files | about 6 |
| M10 | `docs/how-to/grow-a-model.md` | split or shorten the one paragraph over the limit (141 words against 90), meaning unchanged | about 8 |
| M11 | `tests/test_development_scaffold.py` | (r1; replaces "correct the links in `ossie-interchange/evidence/OS1/spec-r1.md`", which would have changed bytes that `009-phase-OS1.md` pins) add the retained ossie snapshots to `RETAINED_DOCUMENT_ORIGINS` with their original homes and present digests: `evidence/OS1/spec-r1.md` and `evidence/OS0/spec-r4.md` by the reviewer's traversal; the implementation reruns the test until it exits 0 and lists every entry added. No evidence byte changes | about 8 |

### The Ossie notes block (M6), content

Stated from `docs/explanation/ossie.md`, `docs/how-to/share-an-ossie-ontology.md`
and `ossie-interchange/034-milestone-close.md`: the two commands
(`gnd export ossie MODEL --out FILE`, `gnd import ossie FILE --out MODEL`);
the three files an export writes (ontology, GND sidecar, loss report); that
import is offline and admits the pinned upstream revision only; what the loss
report says is not carried; the two documented converter refusals; links to
the explanation and the how-to. No sentence claims certification by the
upstream project.

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
| D2 | How are E1's moved bytes handled (plan RN-D7)? | Method: **Ruled (o, 2026-11-10): as proposed** ("Approve as proposed", answering "How do you rule on the open plan decisions RN-D0 and RN-D3 to RN-D11?"): re-record as for 0.2.0 and carry the refactor to an issue (o). Still open (r1): the per-file classification and each moved digest, which need E1; a file E1 names that is not a current-output record is a new question, not covered by the ruling | method ruled; per-file handling open until E1 |
| D3 | Opt-in lanes in E1 and the gate (plan RN-D11) | run them on both trees, or record them as excluded as for 0.2.0 | **Ruled (o, 2026-11-10): as proposed** ("Approve as proposed", answering "How do you rule on the open plan decisions RN-D0 and RN-D3 to RN-D11?"): excluded (o) |
| D4 | The two red tests on main (plan RN-D10) | fix both here, each as its own commit (M10, M11), or leave them as known failures | **Ruled (o, 2026-11-10): as proposed** ("Approve as proposed", answering "How do you rule on the open plan decisions RN-D0 and RN-D3 to RN-D11?"): fix both (o). The ruling was given when M11 meant editing the links; after the review M11 registers the snapshots instead and changes no evidence (r1). The owner sees this change at the plan gate |
| D5 | Notes shape (plan RN-D3) | as §6, or the present sections renamed in place | **Ruled (o, 2026-11-10): as proposed** ("Approve as proposed", answering "How do you rule on the open plan decisions RN-D0 and RN-D3 to RN-D11?"): as §6 (o). The Ossie block's wording is approved with this spec |

## 8. Tests

| ID | Case | Expected |
|---|---|---|
| T1 | `tests/test_release_version.py::test_lock_manifests_and_notes_agree_with_pyproject` and `test_drift_is_refused` (4 sites) | exit 0; each mutant raises `AssertionError` |
| T2 | `test_install_pins_name_a_published_version`, `test_a_pin_to_the_next_version_is_refused_until_it_is_released` | exit 0 with pins at 0.2.0; a `==0.3.0` pin fails |
| T3 | `test_notes_and_compatibility_do_not_claim_publication` and its mutants | exit 0; mutants fail |
| T4 | `tests/test_marketplace_plugins.py`, `tests/test_rf1_pin_harness.py` | exit 0 |
| T5 | `tests/test_release_docs.py`, `tests/test_release_preparation.py`; strict docs build and `tools/check_docs.py site` | exit 0 (the new notes links resolve; the workflow is untouched) |
| T6 | `tests/test_plan_app_docs.py -k grow-a-model`; `tests/test_development_scaffold.py`, including its per-snapshot digest case for each entry M11 adds | exit 0; both are exit 1 on the base. A changed snapshot byte fails the digest case |
| T9 (r1) | new `test_notes_section_names_the_headline_change` in `tests/test_release_version.py`: the declared version's section has an Ossie `###` block that links `explanation/ossie.md` | exit 0; a mutant section without the block raises `AssertionError` |
| T10 (r1) | new `test_support_and_plugin_pages_state_the_prepared_version`: while the declared version is not in `RELEASED`, `docs/support.md` names it as having no observed profile and `docs/marketplace-plugins.md` gives the repository route | exit 0; an empty support page and a plugin page without the route each raise `AssertionError` |
| T7 | six-shard default lane on beast-3, base and RN1 tree | the RN1 failing-id list has no id the base list lacks |
| T8 | the files E1 names | exit 0 after M5 |

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
other docs lines, about 50 test lines (M4, M11) (r1; was 0), plus M5 (unknown
until E1). The stop rule
applies to the total once E1 gives M5's size.

## 11. Approval instrument

This prose, after §12 (E1 results and the per-file classification) is
appended.

## Verification commands

```bash
uv lock --check
uv run pytest -q tests/test_release_version.py tests/test_marketplace_plugins.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_rf1_pin_harness.py --tb=short
uv run ruff check
```

Unresolved: the beast-3 shard invocation (the script copy and its PATH fix),
and the files E1 adds to the focused gate.

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

**Still owed before the gate:** the moved digests, old and new, measured by
applying M5 in a scratch copy, as `evidence/e1/moved-digests.md`. Not done
yet, because the amendment below may change the base the digests are taken
on.

### 12.2 A premise of this spec is refuted

§3 and D4 assume main has two red default-lane tests. The base lane has 26
(evidence README, with attribution: 0 at the 0.2.0 close, 6 after model
composition, 26 after the Ossie merge). M10 and M11 cover two of them. The
other 24 are structure and inventory guards and are outside this spec as
approved. T7 as written still works (it compares lists), but RN1-C7's "no
known failure of its own" does not hold for the candidate. The plan carries
the proposed amendment (plan §12); this spec changes only after the owner
rules on it.
