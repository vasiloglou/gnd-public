# OS3 offline import candidate

The [delegated spec gate](013-OS3-spec-gate.md) binds the import contract.
The candidate reads the pinned ontology schema and its core dependency
offline, validates the name graph before sidecar binding, then restores
canonical source pointers before GND model admission. The CLI stages the
report first and publishes the validated model last. Input and refusal
diagnostics use stable rule IDs.

## Results

- All 38 eligible census exports restore the expected authored document.
  Thirty restore every field. Eight omit exactly the nonempty population
  subtrees and pointers listed in
  [the frozen refusal controls](evidence/OS3/refused-census-pointers.json).
- GND differential comparison reports equal model digests for the 34
  non-temporal cases. Four temporal cases are compared as complete
  admitted source documents because the current diff command refuses
  temporal models.
- The [pinned Flights bytes](evidence/OS3/flights.ontology.yaml) produce
  45 objects, 48 fact types, and 55 proposed imported multiplicity
  constraints with a real upstream commit and artifact anchor. There are
  607 native and 146 refused source pointers. Altered input bytes disable
  the trusted multiplicity mapping. Foreign root entities that would
  need an unsupported composite identifier and their dependent facts
  receive refusal dispositions.
- Controls exercise capped syntax, malformed pointers, reference cycles,
  missing and dangling companions, report agreement, document and model
  identity mismatches, stable refusal order and create-once publication.

The importer also checks the restored identity for lossless bundles with
an adjacent source report. Export and import share the 10 MiB envelope
limit so a successful export remains inside import's input budget. Import
caps the restored model and streams its report within a separate 20 MiB
budget. The ordinary gate uses no external processes for schema or model
admission.

Run `.venv/bin/pytest -q tests/test_ossie_import.py --tb=short` for the
61 focused cases. The importer, CLI grammar, layering and existing diff
consumers have a combined gate. The independent OS3 diff review remains
pending.
