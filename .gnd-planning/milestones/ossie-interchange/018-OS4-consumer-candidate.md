# OS4 pinned consumer gate candidate

The original [OS4 spec](016-OS4-spec-gate.md) and [delegated scope
amendment](017-OS4-spec-amendment.md) bind the gate. The amendment's
SHA-256 is `681a15fd035b28e4d321e0c925110c31af19b2c817ee5cd10c8c5f5cfdf5cb52`.
The required independent diff review remains pending.

The [consumer observations](evidence/OS4/consumer-limitations.json)
have SHA-256
`a1cd2ad3c5593445ae8dbe24dd6f80bb6fb9be17993107a1edc41067e3ed9d4b`.
The lane used Ossie `ee89dbdc2844d8b7d293ed42c8613928bb99505f`,
ossie-converters `83ddc294c8840f5f497a2bdbec2348a128fc2254`, and
RelationalAI 1.39.0 (wheel SHA-256
`33cbf6bc1a2ad598ffa4960bc0ddada1eab0a719de61ad6cc48ab378845126c7`).

| Input | Observation |
|---|---|
| 38 intact exports | 36 conversions matched every compared declaration. Two refused. |
| Composition | The SDK source generator asserted while emitting the chain. Removing only the recorded `derived_by` lets the control convert with exact declaration agreement. |
| Library with subtypes | The converter refuses an inherited parent property in the child's `identify_by`. Removing the two recorded subtype fields lets the control convert with exact declaration agreement. |
| Formula corpus | The chain also triggers the SDK assertion. The requires-only control converts, with all eight requires missing. |
| OR and EXISTS derivations | The converter reports each as unsupported. |
| GND LQP source | The intact formula corpus renders 12 `require` calls. The census companion counts or records a refusal for every source model. |

The first gate returned 1 after collecting all 38 results, disproving
the all-intact conversion and chain premises. The amended gate returns 0
only for the exact measured boundaries. A newly failing case or mismatch
in an intact successful conversion fails it. The isolation controls
compare against their own inputs, and the intact failures remain visible.

```sh
.venv/bin/pytest -q tests/test_ossie_consumer.py tests/test_ossie_external_oracle.py --tb=short
GND_OSSIE_ORACLE_ROOT="$OSSIE_SCRATCH" GND_OSSIE_CONSUMER_OUTPUT="$OSSIE_SCRATCH/os4-consumer-final.json" .venv/bin/pytest -q -m ossie_oracle tests/test_ossie_external_oracle.py -k offline_consumer --tb=short
```

The ordinary gate reported `2 passed, 49 deselected`. The opt-in gate
reported `1 passed, 48 deselected in 38.06s`. Ruff and the strict
component index check passed. The converter subprocess refused socket
access, and the comparison only parsed the emitted source. The product
export report remains independent of consumer observations.
