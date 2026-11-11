# OS2 formula renderer candidate

Date 2026-11-10. The [approved r2 corpus and spec gate](011-OS2-spec-gate.md)
were committed at `a0c0ac7d` before the renderer. The independently reviewed
corpus was repaired for discrimination and scope. Its checker replay matches
all 29 expected verdicts.

The renderer uses the existing requirement and clause lowering and projected
Ossie role identities. Seven constraint families in their approved shapes
and one binary derivation shape have formula placements. The eligible
census emits 19 `requires` and one `derived_by` expression. Mandatory,
frequency and other unverified source shapes retain their semantics in the
sidecar. [Census counts](evidence/OS2/implementation/census-formulas.json)

## Local gates

```sh
.venv/bin/pytest -q tests/test_ossie_formulas.py tests/test_ossie_export.py tests/test_ossie_external_oracle.py tests/test_pyrel_rules.py tests/test_pyrel_rules_calendar.py tests/test_pyrel_rules_derivations.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_plans.py tests/test_rf1_layering.py --tb=short
GND_OSSIE_ORACLE_ROOT="$OSSIE_SCRATCH" .venv/bin/pytest -q -m ossie_oracle tests/test_ossie_external_oracle.py --tb=short
```

Both exit 0.

```text
180 passed, 295 deselected in 11.58s
44 passed in 8.52s
162 matching PyRel target observations; 130 programs and 32 refusals
All checks passed!
```

The ordinary suite deselects the optional PyRel and Ossie oracle cases.
The separate selected Ossie lane includes the emitted combined corpus and
its malformed formula control. The native PyRel execution lane remains
outside the selected gate. The PyRel render comparison compares the
[observation manifest](evidence/OS2/implementation/pyrel-observations.json)
against the same inputs and target options with the package archived from
`a0c0ac7d`. Both manifests have SHA-256
`198e4ba512f46b67d9fd3e01c0b4baf396b140beb4ad569e1f4c656daf90ad24`.
The [capture script](evidence/OS2/implementation/check-pyrel-parity.py) runs
from the repository root with the selected package on PYTHONPATH.

The focused suite checks exact approved scope and formula text, original
source-pointer identity, unsupported shape fallback, an indivisible
cardinality group, and the formula projection time bound. The original
Ossie corpus reviewer read pre-implementation r1. The required independent
implementation diff review remains pending.
