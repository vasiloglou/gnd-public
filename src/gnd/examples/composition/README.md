# Composition example

Two contracts, extracted one document at a time, composed into one checked
population. Used by the how-to "From several documents to one checked answer"
(`docs/how-to/compose-documents.md`).

- `model.orm.yaml`: contracts, parties and cities; an `anchored` party and
  city, a uniqueness (a party has one seat) and the derived
  "Contract is in City".
- `composition/`: a composition directory. `contract-a` is agreement C-1,
  signed by "Acme Corp."; `contract-b` is addendum C-2, signed by
  "ACME CORP.". Each source folder holds the document, its population and a
  version-2 anchor sidecar; contract-a's party has two anchors. The manifest
  renames "ACME CORP." to "Acme Corp." in contract-b and deduplicates
  identical rows.
- `composition-conflict/`: the same, except that contract-b says the party is
  based in Zurich where contract-a says Lyon.
- `targets.json`: the derived fact "C-2 is in Lyon", for `gnd witness`.

The sidecars bind digests of the model's vocabulary, each population and each
document; in the source repository, regenerate them with
`tools/build_composition_example.py` after any edit.
