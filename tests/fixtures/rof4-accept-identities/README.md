# ROF4 corpus: where GND accepts either model identity (issue 111)

The approval instrument for phase ROF4 of the `report-output-fidelity`
milestone (spec: `.gnd-planning/milestones/report-output-fidelity/notes/phase-ROF4-spec.md`,
section 11). It is committed before any implementation.
`tests/test_rof4_accept_identities.py` runs every case from this directory.
This README tells the stories only; which cases are accepted, with what exit
code and what refusal text, is in `expected/cases.json`, and the identities
themselves are in `expected/identities.json`.

A model now has two identities: the old one (`model_digest`, a SHA-256 over
Python's `repr` of the loaded model) and the canonical one that ROF3 added,
which `gnd validate MODEL --identity` prints. A model with reference
populations has only one: its old identity already is its canonical
(version 1) identity. ROF4 lets every place where GND compares a model
identity that someone supplied accept either value. A value that is neither
is refused exactly as today. GND keeps writing the old identity in every
report.

## What is here

- `models/`: copies of four committed models, so the cases never move when
  the originals change.
  - `approvals/`: the shipped approvals example (`src/gnd/examples/approvals`),
    with its `state.pop.yaml`.
  - `reference/`: the ROF3 corpus's `reference-operations` model, which binds
    a fixed reference population (`references/catalog.pop.json`) and has one
    operation; `pre.pop.json` is a one-shipment population for it.
  - `nonstructured/`: the model of the `public-binding-reports` corpus.
  - `dependencies/`: the shipped `release_governance/dependencies` model, with
    one population and one witness target.
- `artifacts/`: one supplied artifact per site, as GND writes it (or, for the
  steps files, as a caller writes it), pinned with the old identity. Each case
  copies the artifact, writes one spelling of the identity into it, and runs
  the site.
  - `s1-approvals.steps.json`: the shipped `plan-draft-2` walk.
  - `s1-reference.steps.json`: a one-step walk on the reference model.
  - `s2s3-reference.check.json`: `gnd check --admission --format json` on the
    reference model: a reference wrapper (its own `model_digest`) around an
    admission report (another `model_digest`).
  - `s3-approvals.check.json`: `gnd check --admission --format json` on the
    approvals model.
  - `s4-nonstructured.check.json`: the `current-v5-valid` check report of the
    `public-binding-reports` corpus.
  - `s5s7-corpus/`: `gnd synth --seed 7 --seeds 2` on the approvals model:
    two populations, their sidecars and one pool. A sidecar writes the
    identity as bare hex, without `sha256:`.
  - `s6-dependencies.witness.json`: `gnd witness --raw` for the target in
    `models/dependencies/reach.targets.json`.

## The spellings

Each case writes one of these where the artifact names the model:
**legacy** (the old identity), **canonical** (the identity
`gnd validate --identity` prints), **wrong** (`sha256:` and 64 zeros),
**dropped_references** (for the reference model only: the version-2 identity
the same model would have without its reference populations, which is not
an identity of this model), and, for the measure sidecars only,
**prefixed-legacy** and **prefixed-canonical** (the `sha256:` spelling where
bare hex belongs).

## The stories

1. **A caller pins a walk (S1).** `gnd check MODEL --pre PRE --steps STEPS
   --format json` with the approvals walk pinned three ways, and the
   reference walk pinned with its one identity, with the version-2 identity
   it does not have, and wrongly. This is the site where a person writes the
   pin by hand.
2. **A session replays an admission report (S2, S3).** The admission
   validator reads a recorded `gnd check --admission` report back. On the
   reference model it checks the wrapper's identity (S2) and the inner
   report's identity (S3); on the approvals model only the report's (S3).
3. **Coverage reads a check report (S4).** `gnd coverage MODEL --check
   REPORT --format json`, with the report's identity in each spelling.
4. **Measure reads a synthesized corpus (S5, S7).** `gnd measure MODEL
   --populations CORPUS --format json` with both sidecars in one spelling,
   with the two sidecars in different spellings (S7: the corpus is still one
   model), with one wrong sidecar, and with a `sha256:` spelling where bare
   hex belongs.
5. **A witness is replayed (S6).** `gnd replay MODEL CANDIDATE CERTIFICATE
   --raw --json` with the certificate's `binding.model_digest` in each
   spelling; and, with the canonical spelling, a wrong `candidate_digest`, an
   extra binding key and a missing one. Only the model field may accept two
   values; the rest of the binding stays exact.
6. **The shipped pins.** The 14 shipped approvals walks that pin the old
   identity, and the new shipped example `plan-draft-2.canonical.steps.json`,
   pinned with the canonical one, are each checked against the shipped model
   and pre-state.
7. **One helper, nowhere else.** A scan of `src/gnd` says which functions
   decide whether a supplied identity matches (the seven sites) and that the
   exact comparisons (a receipt against its report, a bound context, the
   in-process population marker), the places that only copy or produce an
   identity, and the generated Pyrel plans do not change.
8. **A generated Pyrel plan keeps the old identity (ruling D7).** The
   approvals model's DuckDB program refuses the canonical example that
   `gnd check` accepts.
9. **The legacy path costs what it costs today.** With the canonical
   identity function made to fail, every legacy case above is still accepted.
