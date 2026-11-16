---
milestone: literature-depth
station: phase-LD2-spec-gate
skill: "n/a -- repository development under process-phase"
scope: phase-LD2-spec-gate
date: 2026-11-16
gates:
  - command: "uv run --no-sync pytest -q tests/test_ld2_quantities.py --tb=short"
    exit: 1
    output: "18 failed, 6 passed in 4.69s"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-depth/notes/phase-LD2-spec.md sha256 86c54934ea6dbffb6e4804281177ce102625b12e217d9df9e4d3eaed73f45e9c"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/literature-depth/004-phase-LD1.md
    sha256: 5a226ac70ee45cdd4893d6cc4d1ea505aeb9b76a04049dbc1b61382f71bafc69
  - path: .gnd-planning/milestones/literature-depth/notes/phase-LD2-spec.md
    sha256: 86c54934ea6dbffb6e4804281177ce102625b12e217d9df9e4d3eaed73f45e9c
  - path: tests/test_ld2_quantities.py
    sha256: d346519b506ac3694c045db4504b33c47ee67ca04dd01e69d6e198733703c184
  - path: tests/fixtures/ld2-quantities/expected.json
    sha256: e9d244adf0a8d550ce29ad4ca0d636fda59d356ddefb92ad05bf68b3fd2b4e75
  - path: src/gnd/examples/literature/quantity_fixture/source.txt
    sha256: b6eb089cd29272137c65a57c40b76070c9e49e8ccd6bd423880c14f6c630db26
  - path: src/gnd/examples/literature/quantity_fixture/time.orm.yaml
    sha256: 55f41279bae5ee1477d6f006690ac638c9b11dcc01825bdfa2e687967229bba8
  - path: src/gnd/examples/literature/quantity_fixture/time.population.json
    sha256: c2a4bda7fe82b422146ae9bdf3076d4432388db595e4ed7081316627af20b568
  - path: src/gnd/examples/literature/quantity_fixture/time.targets.json
    sha256: 772629861f6408132d4b65f597d17d8f009fe0232a2892775ca718768adc1b16
---

# LD2 spec and corpus gate

ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-depth/notes/phase-LD2-spec.md sha256 86c54934ea6dbffb6e4804281177ce102625b12e217d9df9e4d3eaed73f45e9c

Delegated approval under the owner's `process-milestone literature-depth
auto` invocation. The [LD1 record](004-phase-LD1.md) opens time-dimension
validation and exact replay. The instrument is the frozen corpus and its
separate answer key. The existing float and fractional Number refusals
were green against the base. Model admission rejected the unimplemented
time selector; positive checker and witness tests therefore stopped red
before downstream assertions. No optional spec panel was selected.

## Implementability sweep

The existing parsed anchor context supplies number, span and occurrence
coordinates. Matching a complete time unit can use the existing
per-selector scan and its per-value limits. Unit conversion by exponent
shift preserves exactness. The independently replayed capability is a
checked tuple containing whole-femtosecond coefficient, scale and unit.
A preliminary public witness and replay over integer and unit both
exited 0. The accepted corpus adds exact scale and tests both its
constraint and in-proof mutation. No change to existing certificate
versions or native fractional Number semantics is required.

Part 10 remains deferred.
