# ROF3 corpus: test vectors for the canonical model identity (issue 111)

The approval instrument for phase ROF3 of the `report-output-fidelity`
milestone (spec: `.gnd-planning/milestones/report-output-fidelity/notes/phase-ROF3-spec.md`,
section 11). It is committed before any implementation.
`tests/test_rof3_model_identity.py` runs every case from this directory. This
README tells the stories only; the expected documents, digests and output are
in `expected/`, not here.

Today a model's identity (`model_digest`) is a SHA-256 over Python's `repr`
of the loaded model, which no caller outside Python can recompute. ROF3 adds a
second, canonical identity: SHA-256 over a JSON document with sorted keys and
no whitespace, which `gnd validate MODEL --identity` prints together with its
digest. A model with reference populations already has a canonical identity
(version 1) and keeps it; every other model gets version 2. The old digest
does not change.

Each model is a copy, so the vectors never move when the file it came from
changes.

## The cases

1. **plain-small** (`models/plain-small.orm.yaml`, from the ROF1 corpus): a
   short model of customers, emails and nicknames. The vector a reader can
   check by eye.
2. **floats** (`models/floats.orm.yaml`, from `tests/fixtures/v62-phase5`):
   numbers written `1.0` and `200.0` in the model. A canonical form that
   prints them as `1` and `200` would give a different digest.
3. **float-spellings** (`models/float-spellings.orm.json`, from
   `tests/fixtures/pyrel-rules-derivations/review/num.orm.json`): the numbers
   `0.30000000000000004` and `2.5`.
4. **negative-zero** (`models/negative-zero.orm.json`, from
   `tests/fixtures/pyrel-rules-derivations/review/misc.orm.json`): the number
   `-0.0`, which some canonical forms print as `0`.
5. **dates-and-text**: the plain-small model with a provenance note carrying
   an unquoted date (`recorded: 2025-01-01`) and a quote written partly in
   Greek. The date becomes text; the Greek letters stay as they are, not
   escaped.
6. **operations-a** and **operations-b** (from the ROF2 corpus): two models
   that differ only in the wording of one operation. Operations are not part
   of the version-2 identity (they have their own `operations_digest`), so
   both have the same identity.
7. **reference** (`models/reference/`, from
   `tests/fixtures/rc1-rule-ids/models/reference`): a model with a reference
   population. It keeps its version-1 identity, and there is no version 2
   for it.
8. **reference-operations**: the same model with one operation added. The
   version-1 identity does cover operations, so it changes.
9. **surrogate** (`models/surrogate.orm.json`): a model whose quote contains
   the JSON escape `\ud800`, half of a character pair. The model loads, but
   it cannot be written as UTF-8, so it has no canonical identity: GND must
   refuse to give one rather than crash or guess. The old digest still works
   for it.

For each case the expected results say what `gnd validate MODEL --identity`
prints and what its exit code is.
