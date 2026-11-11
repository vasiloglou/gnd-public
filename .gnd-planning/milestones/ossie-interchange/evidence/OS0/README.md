# OS0 measurements

The upstream source commits, five file digests, converter configuration digest,
installed dependency versions and RelationalAI wheel digests are in
[pins.json](pins.json). The [checkpoint](CHECKPOINT.md) walks through the
hand-written example and generated PyRel.

| Experiment | Observation | Decision or input to later phases |
|---|---|---|
| [E1](E1.json) | Baseline 0/0. Concept and relationship `custom_extensions` each exit 1/1 in the validator and parser. | OD2 selects the document-digest-bound sidecar. |
| [E2](E2.json) | Five of nine authored formula probes accepted. The malformed formula exits 1. | The accepted probes are candidates for OS2's semantic cases. The ring probe only covers self-loops. Failed probes establish the result of those forms only. [Probe definitions](formulas.json) |
| [E3](E3.json), [E3b](E3b.json) | Both versions convert Flights and refunds offline. Source digests match pairwise. Both cases produce zero `require` calls. | Target the converter pin, RelationalAI 1.39.0, for OS4 and OS6. |
| [E4](E4.json) | 65 fact types. Two non-prefix declarations, zero reordered cases and zero reading-order exceptions among n−1 determinants. | Reordering alone cannot express the one-column determinant of the ternary reimbursement fact. The binary's full-tuple uniqueness is inherent in Ossie relationship set semantics. |
| [E5](E5.json) | Flights exits 0/0. The unknown concept exits 1/1. When the version type also fails, each tool reports shape first. | The pinned validator and parser both score the positive and negative controls. |
| [E6](E6.json) | Zero observed bidirectionally unique binaries. The synthetic control distinguishes OneToOne from ManyToOne. All 73 alethic and four deontic constraint marks receive extension dispositions. | Preserve modality via the sidecar. Add an authored OneToOne control in OS1. |

The [census](census.txt) fixes 14 source paths at GND base `d5156595`.
[The inventory](inventory.json) records 2,673 distinct model/pointer pairs and
accounts for all 62 metaschema definitions, 35 observed and 27 absent.
Every row has one disposition. Formula probes alone do not establish an
equivalent GND constraint, so unresolved constraints remain extension
candidates. Forty-seven population pointers are refused with
`population:out-of-scope`. The sidecar retains source identifiers, original
reference-mode spelling and the GND role name of the implicit first role.

[Baseline GND validation](gnd-validation.json) exits 0 for 11 census models and
3 for three skill examples. Their exact JSON pointers and the role-name pattern
failures also appear in the inventory. The later export gate will need to
address admission of these examples without silently broadening the schema.

The original GND model sources, upstream repository sources, scratch package
environments and proprietary wheels stay at their respective locations. Each
wheel used was downloaded from the public PyPI file endpoint, checked against
its published SHA-256 and reinstalled from those local bytes. E3b's raw PyRel
duplicates the retained E3 output byte for byte. The converter measurements
compiled to the local metamodel and decompiled it to source with the upstream
offline configuration and a socket guard. No generated code was executed.

## Reproduce

In an empty scratch directory, check out `apache/ossie` as `ossie/` and
`apache/ossie-converters` as `converters/`, at the exact commits in
`pins.json`. Copy the files in `reproduce/` into scratch and place
`refunds.yaml` and `formulas.json` in `cases/`. Download the two wheel files
named in `pins.json` and verify the digests. Set `REPO` to a GND checkout of
`d5156595`. Use Python 3.11 and isolated environments.

```sh
for env in a b c d; do uv venv --python 3.11 "$env"; done
uv pip install --python a/bin/python pyyaml==6.0.3 jsonschema==4.26.0 sqlglot==30.31.0
uv pip install --python b/bin/python ./converters/ontology
uv pip install --python c/bin/python ./converters/ontology ./converters/relationalai ./relationalai-1.39.0-py3-none-any.whl
uv pip install --python d/bin/python ./converters/ontology ./converters/relationalai ./relationalai-2.0.1-py3-none-any.whl
a/bin/python inventory.py "$REPO" cases
a/bin/python oracle.py
a/bin/python formulas.py
```

Use the full environment list in `pins.json` to match the original
dependency resolution. The oracle runner recreates the E1 and E5 mutations
from the authored example and pinned Flights document. It replaces its
scratch directory in tool diagnostics with `<scratch>`. Run the baseline GND
validation commands in `gnd-validation.json` from the pinned GND worktree with
`PYTHONPATH=src`.
