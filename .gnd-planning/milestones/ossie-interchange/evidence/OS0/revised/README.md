# Reviewed OS0 measurements

This evidence supersedes the first candidate's census and E2, E4 and E6.
The original files remain at their original paths. The original
[E1](../E1.json), [E3](../E3.json), [E3b](../E3b.json) and [E5](../E5.json)
use unchanged fixtures and pins.

The [revised census](census.txt) includes all 41 tracked ORM documents across
both roots at `54483d03`. GND admits 38 and refuses three legacy skill examples
on four role spellings. The proposed Ossie guard explicitly refuses the three
include roots among the 38. [Admission observations](gnd-validation.json)

The [pointer inventory](inventory.json) accounts for all 11,442 source
pointers, with 45 of 62 metaschema definitions observed and 17 absent. Each
row is a disposition under the candidate mapping. OS1 establishes which
admitted documents the exporter writes. The three invalid and three
include-bearing documents have whole-model refusals. Among the remaining
models, 257 population pointers have `population:out-of-scope`.

| Experiment | Measured result |
|---|---|
| [E2](E2.json) | Seven of twelve formula probes accepted. The malformed control failed. All eleven observed constraint types were probed, including both forms of uniqueness. Outcomes apply to the individual expressions and scopes in [formulas.json](formulas.json). |
| [E4](E4.json) | Twenty-four projectable facts have a non-prefix determinant. Eight reorder for ManyToOne, and all eight preserve reading bindings in the pinned parser. There are zero reading-binding exceptions. Non-native determinant reasons are recorded individually. |
| [E6](E6.json) | Three projected facts have uniqueness in both binary directions. A further 54 direct reference declarations are candidates for generated OneToOne identifiers. All 237 projectable active constraint modality pointers take the sidecar disposition (215 alethic and 22 deontic). The other 54 marks belong to whole-model refusals. |
| [Controls](controls.json) | The pinned parser confirmed the original and projected readings for 209 facts. An ambiguous repeated role was refused. The parser preserved the ManyToOne and OneToOne annotations. The inventory verifier refused missing and incorrectly native modality mutations. The source counter observed positive and negative calls and confirmed zero in both retained PyRel outputs. |

OneToOne's two uniqueness directions are specified in the pinned
`ontology.md`. The controls test the parser's treatment of the declaration.
The converter's `Property` API representation does not distinguish the two
directions. OS1 owns the identifier semantics and whole-document checks.

## Reproduce the revised measurements

Use the original [pinned environments](../README.md#reproduce). Copy the
scripts in `reproduce/` and `formulas.json` into a new scratch directory named
by `REVISED`. Copy the original `refunds.yaml` into it and make the parser
environment available as `REVISED/b` (symlink or copy). Create
`REVISED/input`. Set `REPO` to a checkout of `54483d03`, `ORIGINAL` to the
original OS0 evidence directory and `ENV_A` to the validator environment.

```sh
cd "$REPO"
git ls-files ':(glob)src/gnd/examples/**/*.orm.yaml' \
  ':(glob)src/gnd/examples/**/*.orm.yml' ':(glob)src/gnd/examples/**/*.orm.json' \
  ':(glob)src/gnd/skills/gnd-model-from-text/examples/**/*.orm.yaml' \
  ':(glob)src/gnd/skills/gnd-model-from-text/examples/**/*.orm.yml' \
  ':(glob)src/gnd/skills/gnd-model-from-text/examples/**/*.orm.json' > "$REVISED/census.txt"
PYTHONPATH=src .venv/bin/python "$REVISED/admission.py" "$REVISED/census.txt" "$REVISED/gnd-validation.json"
"$ENV_A/bin/python" "$REVISED/inventory.py" "$REPO" "$REVISED"
cd "$REVISED"
"$ENV_A/bin/python" formulas.py
b/bin/python controls.py "$REPO" "$REVISED" "$ORIGINAL"
```
