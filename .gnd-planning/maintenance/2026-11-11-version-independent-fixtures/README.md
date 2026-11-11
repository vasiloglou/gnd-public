# Recorded outputs that do not move at a version bump (issue 172), 2026-11-11

Every release re-recorded the committed outputs that carry `gnd_version`: 30
files for 0.3.0, the same set as for 0.2.0. The owner asked for the open issues
to be addressed and ruled on this one on 2026-11-11: "Normalize per group", in
its own pull request, and not a fixed test version (ruling RR1 D2 stands) and
not continued re-recording.

Base: `main` at `793618f1`.

## What changed

No recorded output was re-recorded. The 13 test files that compare with those
outputs now compare through one helper, `tests/support/recorded_version.py`.
Each states the version its outputs were recorded at (`RECORDED_AT = "0.3.0"`).

Moving a tree of outputs from one version to another changes two things and
nothing else:

- a version field whose value is the old version takes the new one;
- a 64-digit digest that equals the SHA-256 of a file of the same tree, where
  that file changed in the move, becomes the SHA-256 of the moved file.

At the recorded version the move is the identity, so each test compares what
it compared before. A file kept at an older version on purpose (the 0.1.0
inputs) is not touched. A digest that cites nothing in the tree is not
touched, so it must still equal the recorded one.

| Group | Tests | How they compare now |
|---|---|---|
| A payload that carries the version directly | `test_fidelity_stub_gate`, `test_public_measurement_publication`, `test_public_coverage_goldens`, `test_public_measure_corpus`, `test_public_expense_current` | The fresh output is taken as written at the recorded version, then compared byte for byte (parsed, for the expense payload, with the live value asserted first) |
| A digest the test takes of a file that carries the version | `test_rf1_semantic_pins::test_synth` (and `test_tp2_shared_fact_types`, which runs it), `test_rf2_pre_move_pins::test_measure_output_bytes` | The digest and the size are taken of the file as written at the recorded version. The measure payload is moved together with the corpus whose sidecars it cites |
| A tree in which the product cites its own files | `test_public_legacy_codegen_pins`, `test_public_extract_controls`, `test_object_type_description` (rows 4 and 5) | The fresh tree is moved as a whole, so the manifest's and the conformance payload's digests of the version-bearing file follow it |
| A recorded project the product is run over | `test_public_book_runtime`, `test_public_book_skills` | The container is checked as recorded (its digest, and each member's), then unpacked as the product writes it today. The walkthrough's citation of the conformance payload follows the payload |
| The refunds walk | `test_ik6_walk` | Nine files as above. Two files are pinned by structure; see below |

`goldens.sha256`, the seven containers, their eight digest literals and every
other recorded byte are unchanged. One file gained two keys:
`tests/fixtures/induced_knowledge/ik6-walk/goldens.json` now also holds the
structural digests of two files.

## Differences from the mechanism as it was put to the owner

The choice put to the owner described masking the version on both sides, a
placeholder in the two BookRec containers, and one last re-record. What was
built is narrower:

- nothing is re-recorded, and the containers still hold the bytes the product
  wrote at 0.3.0, not a placeholder;
- a digest is never replaced by a name where it can be re-derived: it is
  re-derived from the file it cites, after checking that it cites that file.

## The one place a digest value is no longer compared

`gnd discover` writes the inducer's version into the provenance of each
induced constraint. In `discovered.json` and `discovered.preview.json` that
version feeds digests of parts of the same file: each operation's element
digest, the candidate model's digest, the proposal's id and digest, the
blast-radius report and the preview that binds them. Only the product can
re-derive those. The preview also lists its entries and its verbalization
lines in the order of such a digest.

- At the recorded version both files are compared by exact digest, as before.
- At any other version they are compared by structure: every byte except the
  version values and the digest values. `discovered.json` keeps which digests
  equal which. `discovered.preview.json` is compared as its sorted lines.
- At every version the test now also makes eleven checks that the digests
  and the id the two files state at their top level bind what they name.

So after the next release, the test no longer pins the digest values of those
two files or the order of the preview's lines. It still pins their text, and
the walk itself applies the preview, which the product refuses when a digest
does not bind.

## Evidence

- **Red first.** With the version moved to 0.3.1 (the five homes
  `tests/test_release_version.py` names), 31 tests of these files fail on
  `main`: the same 31 that experiment E1 of release-0.3.0 lists.
- **Green at three versions, with no recorded byte moved.** The 16 affected
  test files and the helper's own tests: 329 passed at 0.3.0, and 329 passed
  with the version moved to 0.10.0, which also has a different length. At
  0.3.1 a full run passed 316 of the then 318; the two that failed, the
  measure pin and the walk, were then corrected and passed there. The walk's
  comparison was reworked once more after that and was run at 0.3.0 and
  0.10.0 only.
- **Full default lane** on `main` plus this change: 19,027 passed, 0 failed, 2
  errors (the two `tests/test_public_optional.py` errors known on `main`), in
  six shards on beast-3 (macOS 27.0.1, Python 3.13.18, uv 0.13.7).
- **The helper's limits** are tests of their own
  (`tests/test_recorded_version.py`): another changed byte still shows, down
  the chain of files that cite it; a product that writes a wrong version is
  not moved into agreement; a broken citation is not repaired.
- **Lint:** the changed files pass `uv run ruff check`.

## Not covered

- The trial bumps moved the version in the five homes and reinstalled the
  package. They did not write release notes, so the four
  `tests/test_release_version.py` cases that need a notes heading were not
  part of the trial.
- A fixture recorded later at another version states that version in its own
  test. No such fixture exists yet.
- The opt-in lanes were not run.
- `.gnd-planning/milestones/release-0.3.0/evidence/RN1/rerecord.py` stays as
  evidence. It is no longer needed for a release.
