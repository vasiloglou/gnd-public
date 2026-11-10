# OS1 exporter candidate

Date 2026-11-10. Base `47e2ce98`. The [delegated OS1 spec gate](007-OS1-spec-gate.md)
and [explicit OD6 confirmation](004-owner-OD6.md) authorize this candidate.
The independent phase diff review and opt-in oracle remain required before
an OS1 completion record.

The command exports YAML or JSON and writes a canonical loss report and
document-bound sidecar. The ordinary census covers all 41 listed paths.
Thirty-eight export and validate against the vendored schema. The three
include roots refuse. Four invalid role names in three shipped examples
were corrected in their fixture data. Strict mode refuses population loss.

## Gate output

```sh
.venv/bin/pytest -q tests/test_ossie_export.py tests/test_ossie_external_oracle.py tests/test_rf1_cli_pins.py tests/test_pyrel_export.py tests/test_rf4_peripheral.py tests/test_rf1_layering.py tests/test_packaged_skills.py::test_base_dependency_set_is_frozen --tb=short
```

Exit 0.

```text
1153 passed, 42 deselected in 58.10s
```

The 42 deselected cases are the pinned oracle lane. Ruff on the changed
Python modules and tests exits 0 with `All checks passed!`.
`python3 scripts/components_index.py --check` and `git diff --cached --check`
exit 0. The component index has zero fixes, warnings and rereads against
the phase base. An offline wheel build exits 0. The archive contains the
exporter, pinned ontology schema, pin receipt and loss-report schema.
The packaged ontology schema matches the source byte for byte.

## Pending

- Run `GND_OSSIE_ORACLE_ROOT=... .venv/bin/pytest -q -m ossie_oracle tests/test_ossie_external_oracle.py --tb=short`
  after explicit lane selection.
- Review the exact candidate diff independently and disposition any findings.
- Complete the OS1 record and show the OS5 early documentation checkpoint
  as scoped by the plan.
