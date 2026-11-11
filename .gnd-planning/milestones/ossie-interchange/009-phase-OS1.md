---
milestone: ossie-interchange
station: phase-OS1
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-OS1
date: 2026-11-10
gates:
  - command: ".venv/bin/pytest -q tests/test_ossie_export.py tests/test_ossie_external_oracle.py tests/test_rf1_cli_pins.py tests/test_pyrel_export.py tests/test_rf4_peripheral.py tests/test_rf1_layering.py tests/test_packaged_skills.py::test_base_dependency_set_is_frozen --tb=short"
    exit: 0
    output: "1170 passed, 43 deselected in 82.14s (0:01:22)"
  - command: "GND_OSSIE_ORACLE_ROOT=$SCRATCH .venv/bin/pytest -q -m ossie_oracle tests/test_ossie_external_oracle.py --tb=short"
    exit: 0
    output: "43 passed in 29.56s"
  - command: "replay eight targeted regression nodes against git archive 050a2f62"
    exit: 1
    output: "8 failed, 72 deselected in 2.63s"
  - command: ".venv/bin/ruff check src/gnd/export/ossie.py src/gnd/safefs.py src/gnd/commands/export.py tests/test_ossie_export.py tests/test_ossie_external_oracle.py tests/test_rf1_cli_pins.py tools/ossie_oracle.py"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py --check"
    exit: 0
  - command: "python3 scripts/components_index.py changed --base 47e2ce98 --strict"
    exit: 0
  - command: "git diff --cached --check"
    exit: 0
  - command: "UV_CACHE_DIR=$SCRATCH/uv-a uv build --offline --wheel --out-dir $SCRATCH/os1-reviewed-wheel"
    exit: 0
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: explicit owner or separately scoped CI selection
  reason: the phase uses the ordinary affected checks and the separately selected Ossie oracle.
evidence:
  - path: .gnd-planning/milestones/ossie-interchange/evidence/OS1/spec-r1.md
    sha256: b17b774364ce381b5ff3173a0b5546b377fec7a2044275ae31c45fc39a853353
  - path: .gnd-planning/milestones/ossie-interchange/notes/phase-OS1-spec.md
    sha256: b32dbef5fc93f695e8771ea895fc84882263ec196cae76a49a7ecacbff173ac5
  - path: .gnd-planning/milestones/ossie-interchange/notes/phase-OS1-claude-review.md
    sha256: fa5b7f08fb73e0fa18e4287c4242df296f91dab527d7387b2a961da802445f89
  - path: src/gnd/schema/ossie/PINNED.json
    sha256: 6f5683ba7c63a6e8d4fafba677bae0c2ee49044cb0b9634606aad1b0747c8ba0
  - path: src/gnd/schema/ossie/ontology.json
    sha256: c94c6ee9831a65aac52c52353072c2480c04c43a49139ed8ebafc90a2d9b9588
  - path: src/gnd/ossie-loss-report.schema.json
    sha256: a9e76c1442b49b0c0975d08410784e503e842ac6dc1213209736169b554d83e7
  - path: src/gnd/export/ossie.py
    sha256: e8c7fcdce59765c988b8a8051483f65ebdab39d6d8f0322278d448bd0280e99f
  - path: src/gnd/safefs.py
    sha256: af1c46c81ae6869516190a9a68fec9d3682a1b9940cf11dba2f4e37b06dde915
  - path: tests/test_ossie_export.py
    sha256: 31f993bb2900eedea1ab9d687373a8e51a58a73403733f548c107b93b54c5c2a
  - path: tests/test_ossie_external_oracle.py
    sha256: 06e73d4c9a0bacf3f7f6c2a29bfb77f5b9079ea38bc0d4362ac688cc9bb5a6ce
---

# OS1 phase record

The standalone Ossie exporter writes a pinned YAML or JSON ontology, a
digest-bound reconstruction sidecar and one loss disposition per source
pointer. The three include roots refuse with `include:unsupported-route`.
Four role spelling corrections made the previously inadmissible skill
examples eligible. The implementation base is `47e2ce98`.

## Gate output

```text
1170 passed, 43 deselected in 82.14s (0:01:22)
43 passed in 29.56s
8 failed, 72 deselected in 2.63s
All checks passed!
Wheel matches exporter and all three interchange resources.
```

The exit-1 command is the intended negative control. The eight final
regression nodes run against the archived pre-fix package from `050a2f62`.
They fail on nonfunctional identifiers, omitted names, YAML scalar typing,
empty population strict policy, deontic and proposed multiplicity, the YAML
depth band and loss of a racing replacement. Those nodes pass in the
final focused gate. The initial pinned oracle also exited 0 with
`42 passed in 7.56s`. The final oracle adds the YAML role-name probe.

## Criteria

| Criterion | Measured result |
|---|---|
| OS1-C1 | 38 eligible census documents exit 0 and validate against the vendored schema. |
| OS1-C2 | The pinned validator and parser both accept all 38. Three exact include guards, an unknown-role-concept refusal and a YAML 1.1 role-name control complete the 43-case lane. |
| OS1-C3 | YAML and JSON are byte-stable across input paths. The sidecar and report bind the admitted model identity and exact ontology bytes. The built wheel matches the exporter and packaged schemas. |
| OS1-C4 | The complete census loss paths match an independent ordered RFC 6901 walk. Retained literal and copy entries match each admitted source value. Nonempty population pointers are omitted from the sidecar. |
| OS1-C5 | The three census include roots and a missing-dependency include fixture refuse before resolution. |

## Independent review

The owner answered “Authorize OS1 Claude Code review” for candidate
`050a2f62` and “Run the OS1 oracle gate” for the local pinned tools. Claude
Code Sonnet, high effort, exit 0, read with file tools and requested
changes. The reviewer could not run the gates. [Verbatim review](notes/phase-OS1-claude-review.md)

| Finding | Disposition |
|---|---|
| F1 | Blocking. Reproduced KeyError on an admitted unnamed object type. Allocate the source ID as the default name. |
| F2 | Blocking. Reproduced Task identification through a nonfunctional link. Require functional binary links in the identifying direction and exercise both outcomes. |
| F3 | Blocking. A confirmed deontic source rule became hard multiplicity. The delegated spec amendment limits native multiplicity and composite identification to confirmed alethic constraints. Proposals and deontic policy retain their scope and values in the sidecar. |
| F4 | Blocking. The pinned YAML reader loaded a valid role name as a boolean. The writer uses YAML 1.1-compatible spelling. Both pinned readers accept the synthetic case. |
| F5 | Hardening. Preserve empty populations as extension shape. Strict refuses when a nonempty subtree produces refused rows. |
| F6 | Hardening. Help describes a refused disposition. The CLI successor checks the exact words and preserves the predecessor branches. |
| Coverage | Add input-depth, non-JSON, FIFO, directory and cyclic-subtype cases, ordered pointer assertions, a fixed census count, exact include selection, staged-write faults and both output alias paths. Generated names and links come from GND admission and typed projection. The pinned reader checks remain the independent whole-document validation. |
| Local rollback audit | Blocking. The pre-fix race test removed a foreign replacement after its identity check. Rollback now withdraws an entry before checking identity, restores a foreign entry without replacement, and checks all already-published leaves on failure. |

## Refactoring review

Refactors executed. The exporter now calls the existing regular-file intake
and YAML guard in place of its duplicated descriptor logic. The rollback
repair uses the filesystem component's existing exclusive rename. Focused
consumer tests cover the existing filesystem seams.

## Boundary

One reviewer is one reviewer. Its opinion is over `050a2f62`; the repaired
bytes have the selected regression and oracle results. The oracle establishes
schema and parser admission. Formula equivalence, round-trip import and
RelationalAI consumer output belong to their dependent phases. Publication
uses the ontology as the completion marker. A process interruption can leave
uncommitted companions, and a second concurrent replacement can require
retaining the withdrawn foreign entry under a private sibling name.

## Open questions

- **OS2:** constraints and derivations remain in the sidecar pending the
  corpus-first formula gate. Preserve the original modality and status.
- **OS3:** reconstruct the retained source shape using the digest-bound
  sidecar and refuse tampered bindings before admission.
- **OS5:** present the required early explanation checkpoint, then integrate
  the final interoperability wording at its gate.
