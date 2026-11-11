# OS2 approved formula corpus r2

The [review of r1](../../../notes/phase-OS2-corpus-review.md) checked the
initial hand-derived verdicts and requested stronger discriminating cases.
The [case file](cases.json) starts from one complete population. Each case
replaces only its listed fact lists or instance roster. The [expected
table](expected.json) names the one constraint or derivation being compared
and pairs each formula with its scope. Equality records both directions.

The checker matches all 29 named verdicts. For a derived relationship,
`pass` means the asserted GND set equals the set the Ossie expression would
construct. Both missing and spurious links produce a failure. The repaired
negative derivation includes an unrelated Business band to distinguish a
join from a cross product. Other cases exercise two join keys and an empty join.

`projection: extension` identifies formulas used as measured counterexamples.
Frequency can distinguish GND rows that Ossie set semantics collapse. The
mandatory rule is vacuous in GND when its covered relationship has no rows,
even though the corresponding Ossie existence condition would fail. Both
sources stay in the sidecar. Other formula groups are the approved positive
rendering targets.

The pinned parser accepts all ten authored groups, including the two groups
with a measured semantic divergence. It rejects the malformed COUNT and the
old r1 derivation call. The revised derivation uses a dotted path and returns
the final role implicitly, following the pinned ontology specification's
derivation-expression rule. For root cardinality, see the pinned parser's
`tests/fixtures/validation/top_level_require_valid.yaml` and
`FormulaValidator.validate_rule`. That fixture and the selected parser
confirm that a bound COUNT is legal at ontology scope. The negative
cardinality case includes the third Account in a fact.

R2 narrows the rendering shapes and adds controls for the findings on r1.
The independent review applies to r1. R2 carries the measured parser,
checker and discrimination results used by the delegated corpus ruling.

```sh
.venv/bin/python .gnd-planning/milestones/ossie-interchange/evidence/OS2/corpus-r2/replay.py
PYTHONPATH=src:. .venv/bin/python .gnd-planning/milestones/ossie-interchange/evidence/OS2/corpus-r2/probe.py "$OSSIE_SCRATCH"
```
