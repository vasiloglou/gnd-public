# OS2 formula semantics corpus, draft r1

The model and population cases are authored before the renderer. The
[model](model.orm.json) defines small account relationships and value domains.
The [case file](cases.json) contains a complete base population. Each case
overrides only the listed fact rows or instance roster. The
[expected verdicts](expected.json) record the candidate formula text, the
rule under test, the expected verdict and the reason from those rows.

The expected verdicts were hand-derived against the pinned Ossie
ontology specification, version 0.3.0.dev0. The examples exercise scoped
comparisons, existence, relationship membership, negation, binary role
comparison, enum membership, counting and a derived binary join. Each
selected rule has a satisfying and a violating case. GND reports may include
other rules affected by a case. Only the named constraint or derivation is
the assertion under test.

The corpus is ready for independent semantic review. After it is reviewed
and committed, the renderer must produce the accepted formulas for these
shapes. The pinned parser checks syntax and scope. The checker comparison
tests agreement with the hand-derived semantics, as the plan requires.

Run the GND comparison from the repository root with

```sh
.venv/bin/python .gnd-planning/milestones/ossie-interchange/evidence/OS2/corpus-r1/replay.py
```
