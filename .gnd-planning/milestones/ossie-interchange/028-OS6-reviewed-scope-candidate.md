# OS6 tested local contribution candidate

The [phase spec](024-OS6-spec-gate.md) and [scope amendment](027-OS6-spec-amendment.md)
govern this candidate. The upstream branch
`codex/convert-ontology-requires` is local at
`0f00f798dedd139b81c32e32a5b6431fb8a0b825`, based on
`83ddc294c8840f5f497a2bdbec2348a128fc2254`. Its verified Git bundle
has SHA-256
`2d7b1a40c532ca110202cdc54be5a2989326f17287ec64f719abf7d56442f35e`.

The first run exposed the SDK's entity-anchor requirement for PyRel
source emission and a cast that cannot stand in for a finite value
domain. The final implementation binds role variables to each tuple,
refuses ambiguous or unsupported forms, and reports unsupported
formulas as warnings. Both scoped comparison and enumeration survive a
source round trip on entity-anchored controls. The Flights snapshot
adds two PyRel requirements for the Route endpoint checks. The
upstream RelationalAI suite passed all 39 tests under 1.39.0 and the
offline socket guard.

The [final replay](evidence/OS6/consumer-limitations.json) has SHA-256
`45c973248f53ed272e9419986d1ea7c4f9179218bea96d4e170f8b05abd45c05`.
The [replay script](evidence/OS6/replay.py) reports 36 intact conversions
with matching declaration identities and the same two conversion
refusals as the original OS4 gate. Its eight isolated formula inputs
all convert.

| Input | Added metamodel requirements | PyRel require calls |
|---|---:|---:|
| Guarded comparison | 1 | 0 |
| Subset and both equality directions | 1 per formula | 0 |
| Exclusion | 1 | 0 |
| Irreflexivity | 1 | 0 |
| Ontology-level count | 0, with warning | 0 |
| Value-concept enumeration | 0, with warning | 0 |

The six value-tuple requirements are present in the metamodel.
RelationalAI 1.39.0 omits them from source, so the original OS6-C2
emitted-source expectation remains unmet for the GND controls. The
amended scope requires the omissions to stay visible. Upstream
independent review and the owner's publication decision are pending.

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OSSIE_SCRATCH/c/bin/python" -I "$OSSIE_SCRATCH/run-os6-tests.py" -q tests --tb=short
.venv/bin/python .gnd-planning/milestones/ossie-interchange/evidence/OS6/replay.py --checkout "$OSSIE_SCRATCH/os6-converters" --oracle "$OSSIE_SCRATCH" --out "$OSSIE_SCRATCH/os6-gate-final.json"
```
