# UG3 corpus

The approval corpus for phase UG3 of the unattended-model-growth milestone
(spec: `.gnd-planning/milestones/unattended-model-growth/notes/phase-UG3-spec.md`,
§8 and §11). Each case below says what is run. What should happen is kept
separately in `expected.json`, so this page can be read without it.

## The files

- `documents/ledger.txt`: the shop's ledger text, the same bytes as the MG5
  fixture `tests/fixtures/unattended/source.txt`.
- `documents/annex.txt`: a short annex to the ledger.
- `documents/round.txt`: the text of a later growth round.
- `models/span-element.orm.yaml`, `models/span-constraint.orm.yaml`,
  `models/span-sample.orm.yaml`: three unattended models. Each declares
  `ledger.txt` and `annex.txt` and has ten source spans. Nine cite the ledger.
  Exactly one cites the annex: a span on a fact type (element), a span on a
  uniqueness constraint (constraint), or a span on a sample row (sample).
- `models/plain.orm.yaml`: the same shop model without the unattended mode: no
  `source` header and no spans.
- `models/rounds.orm.yaml`: the starting model for part B. It declares
  `ledger.txt` (cited by its spans) and `annex.txt` (cited by nothing).
  `round.txt` is not declared.
- `parity-baseline.json`: outputs captured on `5c6a0c5f`, before the first
  source edit, for runs that use neither new feature.

## Part A: `gnd validate --document` and `--require-documents`

Every run is `gnd validate MODEL --format json`, with a `--document PATH` for
each listed document.

### A1
The element-span model, with both the ledger and the annex supplied.

### A2a
The element-span model, with only the ledger supplied. The annex's one span sits
on a fact type.

### A2b
The constraint-span model, with only the ledger supplied. The annex's one span
sits on a uniqueness constraint.

### A2c
The sample-span model, with only the ledger supplied. The annex's one span sits
on a sample row.

### A3
As A1, adding `--require-documents`.

### A4
As A2a, adding `--require-documents`.

### A5
The element-span model with `--require-documents` and no document at all.

### A6a
The plain model with `--require-documents` and no document. Compared with the
same run without the flag.

### A6b
The plain model with `--require-documents` and the ledger supplied. Compared
with the same run without the flag.

## Part B: a `source-document` operation in `gnd evolve`

Every case starts from `models/rounds.orm.yaml` (B8 from `models/plain.orm.yaml`)
and runs `gnd evolve preview`, with `--policy additive` unless the case says
otherwise. The proposal's candidate model is the starting model with the
operations applied.

### B1
A growth round with two operations: `add` a `source-document` declaring
`round.txt` (its digest, label `round.txt`), then `add` an object type
`invoice_no` whose provenance span cites `round.txt`. After the preview, `gnd
evolve apply` with `--policy additive`, then `gnd validate` of the published
model over all three documents.

### B2
`modify` the annex's declaration, changing its label to `annex-2025.txt`. Run
with and without `--policy additive`.

### B3a
`delete` the annex's declaration (nothing cites it). Run with and without
`--policy additive`.

### B3b
`delete` the ledger's declaration (the model's spans cite it). Run with and
without `--policy additive`.

### B4
`add` a `source-document` for the ledger, which is already declared.

### B5a
`add` a `source-document` whose locator digest is not 64 lowercase hex
characters.

### B5b
`add` a `source-document` whose `after.sha256` differs from the locator's digest.

### B5c
`add` a `source-document` whose `after` carries a third key besides `sha256` and
`label`.

### B6
`rename` the annex's declaration.

### B7a
B1's declaration operation alone, in a proposal written as `schema_version` 1.

### B7b
The same, as `schema_version` 2.

### B8
Starting from the plain model, which has no `source` header: `add` a
`source-document` for `round.txt`, without `--policy`.
