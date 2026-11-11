# OS3 offline Ossie import

The [approved import spec](013-OS3-spec-gate.md), [candidate
record](015-OS3-import-candidate.md), and [identity report
amendment](019-OS3-spec-amendment.md) bind the import contract.
The independent [Claude Code review](notes/phase-OS3-claude-review.md)
read the exact public candidate `a380e9a6`, its diff from `9f6db1e7`,
and the named GND sources. One reviewer is one reviewer. The reviewer
read the artifacts without running the gates.

| Finding | Disposition |
|---|---|
| Empty foreign readings cause an unhandled index error | Reproduced. Empty readings and stray braces now refuse the individual relationship. |
| Missing report or invented refusal hides a mismatched identity | Reproduced. Refused rows must describe supported population roots or descendants of other refused rows. When a sidecar is supplied, the output reports whether its source identity matches the restored model. A lossless companion still requires a match. |
| Repeated ancestry searches exceed the budget on a valid chain | Reproduced. Parent-first traversal reuses cached resolutions along the path. The 160-node repeated-key control admits, and a distinct-key search exhausts the work budget within the time bound. |
| Bounds and provenance coverage | The gate exercises output size and pointer depth refusals, the offline core reference, duplicate names, the sidecar header and an empty foreign projection. Flights counts and source provenance are pinned. |
| Imported modality and n-ary multiplicity | The pinned document states hard multiplicities. D-03's default applies to unconfirmed inferred and induced constraints. The pinned ontology prose defines the n−1 determinant for a relationship of higher arity. |
| Output report schema and include refusal | The import report has its own schema identifier and a fixed renderer for the documented rows. The GND byte loader refuses unresolved includes via the validation error caught at the model boundary. |

Six regression cases failed against the archived candidate. The repaired
focused selection passes all 307 tests.

```sh
.venv/bin/pytest -q tests/test_ossie_import.py tests/test_ossie_export.py tests/test_rf1_cli_pins.py tests/test_rf1_layering.py --tb=short
```

Ruff, the strict component index and diff whitespace checks passed.
The earlier OS3 candidate's expanded affected selection passed 404 tests.
The repaired importer still restores all 38 expected census documents,
including 30 intact models and eight with the frozen population
omissions. The gate checks equal GND diff digests on 34 non-temporal
models. It compares the authored and restored documents directly on the
four temporal models. Flights yields 45 object types, 48 fact types,
55 proposed imported constraints, and 607 native and 146 refused rows.

## Refactoring review and boundary

Read, parse, schema, name checks, sidecar and report binding, restoration,
and GND admission remain ordered. The common reading helper governs
direct references and ordinary facts. The existing create-once writer
publishes the report before the model. Review dispositions are backed by
reproduction and focused reruns. The checks compare source and restored
identities, and an accompanying report that describes real omissions
does not supply the omitted source values. The digests bind bytes and
identify models. Authenticity requires trust in the supplied artifacts.
