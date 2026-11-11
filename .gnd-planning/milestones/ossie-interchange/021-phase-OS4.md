# OS4 pinned PyRel consumer comparison

The [spec](016-OS4-spec-gate.md), [amendment](017-OS4-spec-amendment.md)
and [candidate](018-OS4-consumer-candidate.md) bind the measured scope.
The independent [Claude Code review](notes/phase-OS4-claude-review.md)
read the diff through `4c9416ce` and its public evidence. One reviewer
is one reviewer. The reviewer read the artifacts without running them.

The [reviewed consumer observations](evidence/OS4/reviewed/consumer-limitations.json)
have SHA-256
`b5a0981e8c925d4ddd0725a47ff2fd240499429e9b22f2fc108c5d20edad0116`.
The pinned converter emits PyRel for 36 intact exports with exact
agreement on the compared declaration names and edges. The two intact
refusals and their isolation controls are retained. The library failure
is triggered by the GND export's explicit inherited `identify_by` links.
The composition chain and the reviewed corpus chain reach an SDK
source generation assertion. The observed limits attach to the
converter and SDK versions. The original export bytes and product loss
reports are unchanged by this comparison.

The converter output contains no `require` calls. The 36 successful
census rows contain 17 source requires expressions, and the
requires-only control contains eight. The GND LQP source for the full
formula corpus contains 12 `require` calls. The two renderers count
different units.

| Review finding | Disposition |
|---|---|
| Extra declarations can disappear from the AST comparison | Reproduced on the archived extractor. Reconcile total call counts with the parsed declarations. Static tests catch unassigned, nested and direct-name calls and an incorrect literal name. Repeated identifier calls on one concept contribute all of their edges. |
| Claim should describe emitted source | The limitation is `no-require-in-emitted-source`. The pinned gate rejects any observed requirements. Record `where`, `require` and `not_` counts. |
| Offline guard evidence | Test audited DNS, datagram send and connection events inside each subprocess and fail on a recorded attempt after setup. Dependencies may create sockets for local capability probes. The audit hook guards Python socket operations. It is not an operating system sandbox. |
| Pin verification | Require a clean checkout including untracked paths. The local wheel file digest and installed SDK version match the OS0 environment record. This does not independently hash the installed distribution's files. |
| Semantic limits | The extractor compares declarations and identifier edges. It does not check the rule engine, readings, multiplicities, role targets or compound key grouping. Isolation proves sufficiency of the recorded changes. |

```sh
.venv/bin/pytest -q tests/test_ossie_consumer.py tests/test_ossie_external_oracle.py --tb=short
GND_OSSIE_ORACLE_ROOT="$OSSIE_SCRATCH" GND_OSSIE_CONSUMER_OUTPUT="$OSSIE_SCRATCH/os4-reviewed-closed.json" .venv/bin/pytest -q -m ossie_oracle tests/test_ossie_external_oracle.py -k offline_consumer --tb=short
```

Results: `5 passed, 49 deselected` and `1 passed, 48 deselected in
40.82s`. Ruff, the strict component index and diff whitespace checks
passed. All audited socket guards passed their self-test and no
after-setup network attempt was observed.

## Refactoring review and open question

Keep declaration extraction and call reconciliation in the static AST
reader. The converter environment and network guard live in the same
subprocess wrapper. Only the opt-in test compares runtime observations;
the exporter has no consumer dependency.

| Question | Target |
|---|---|
| Plan predicate 6 expected all 38 intact exports to convert. The pinned experiment refutes that premise. | Milestone close amends predicate 6 to require all 38 attempts, exact declaration identities on the 36 successful conversions, and the two evidenced refusals. |
| Can the upstream converter emit requirements? | OS6 tests the local contribution independently of the pinned result. |
