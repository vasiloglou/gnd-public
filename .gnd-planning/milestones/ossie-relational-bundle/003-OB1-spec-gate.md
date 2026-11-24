# OB1 spec gate

**Owner approval, 2026-11-24.** `auto=false`.

The owner was asked "Approve the OB1 spec r2 so implementation can start?"
and answered:

> Approve OB1 spec

| Item | Value |
|---|---|
| Approved spec | [OB1 spec r2](notes/phase-OB1-spec.md) |
| SHA-256 | `068f24c4f1368ff0d0c2a5749be953ba1128b58cb1db809465dc1a77c1413824` |
| Under | plan r2 (`52d946a4…6e1d`), approved at the [plan gate](002-plan-gate.md) |
| Review state | not reviewed by a panel |

## Spec decisions

| ID | Ruling |
|---|---|
| D3a | The `--max-output-bytes` and `--max-input-bytes` ceiling is 256 MiB (268435456), as plan D3 ruled. |
| D3b | Plan D3 (b): OB1 adds `--max-input-bytes` to `gnd import ossie` and threads it through the moved caps of §6.3. |
| D3c | A separate `DEFAULT_MAX_OUTPUT_BYTES` constant, not an alias of `input_policy.MAX_BYTES`. |

## What this covers

**In scope:** the OB1 code and tests of spec §6 and §8, the baseline digest
file, and the phase's record and commits. Work happens on a topic branch,
with its own PR.

**Not selected:** no opt-in gate, no paid panel run, and no oracle lane.
Merge stays the owner's decision.
