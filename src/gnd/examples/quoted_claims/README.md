# Quoted claims

A certified-answer model for `gnd why-not`. A quotation is certified as said by
a person when it appears in a work, the person wrote the work, and an editor
reviewed it.

- `model.orm.json`: the model; `certified` is derived.
- `gap.pop.json`: where two quotations appear; no authorship and no reviews.
- `claim.json`: the claimed row, `certified(q-17, Ada Byrne)`, as a witness
  request.
- `extracted.json`: the reviewer a source document names, for the one role no
  binding reaches.

The how-to "Repair a claim that does not derive" walks the repair loop: why-not
names `authored` as missing, then `reviewed`, then reports the row derived, and
`gnd witness` proves it. Because the population covers `certified`, the
repaired population must also assert the derived row for `gnd check` to pass.
The data is synthetic.
