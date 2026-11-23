# Seeded growth example

An unattended model grown from an owner-reviewed vocabulary, used by
"Starting from a reviewed vocabulary" in
`src/gnd/skills/gnd-model-from-text/references/unattended-growth.md`.

- `seed.orm.yaml`: the reviewed vocabulary. Version 4, not unattended; its one
  constraint is `explicit`, `confirmed` and `alethic`, with `reviewed_in`.
- `root.orm.yaml`: the growth root. Version 5, `source.mode: unattended`,
  `reviewer: none`; it includes the seed by pin and holds nothing of its own,
  so it declares no document yet.
- `round-1.document.txt`, `round-1.proposal.json`: round 1 declares the
  document and adds an Author value type and "Author writes WorkKey", with
  spans and two sample rows.
- `round-2.document.txt`, `round-2.proposal.json`: round 2 binds the root as
  round 1 publishes it, declares its document and attaches a `sample`,
  `proposed`, `deontic` mandatory constraint to the seed's fact type.
- `population.json`, `policy.json`, `receipts.json`: a population of the grown
  root, and a two-judge policy with approving receipts that bind it.

From a copy of this folder (the commands write into it):

```bash
gnd validate root.orm.yaml
gnd evolve preview root.orm.yaml round-1.proposal.json --workspace . --records records --out preview-1.json --policy additive
gnd evolve apply root.orm.yaml round-1.proposal.json --preview preview-1.json --workspace . --records records --policy additive
gnd evolve preview root.orm.yaml round-2.proposal.json --workspace . --records records --out preview-2.json --policy additive
gnd evolve apply root.orm.yaml round-2.proposal.json --preview preview-2.json --workspace . --records records --policy additive
gnd validate root.orm.yaml --document round-1.document.txt --document round-2.document.txt --require-documents
gnd check root.orm.yaml population.json
gnd judgments check root.orm.yaml population.json --policy policy.json --receipts receipts.json --trusted-root .
```

Each command exits 0. `gnd validate` prints one `INCLUDE seed …` line naming
what the seed carries. The proposals and the judgment inputs bind digests; in
the source repository, regenerate them with
`tools/build_seeded_growth_example.py` after any edit to the seed, the root or
a document.
