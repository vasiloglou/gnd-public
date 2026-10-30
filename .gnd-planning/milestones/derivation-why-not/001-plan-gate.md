# Plan gate: derivation-why-not r3

Date: 2026-10-30. `auto=false`.

**Owner approval (o).** The owner approved the plan and the WN1 spec in the
session on 2026-10-30: "I approve plan r3 (SHA-256 fb590faa...441d) and WN1 spec
r3 (SHA-256 78fbfe88...3faa), confirm WN-D3, D4 and D5, and take the proposed
answers for WN-D1, D2, D6, D7, D9-D14 and spec D6."

The full digests of the approved bytes were checked against the working files
before this record was written:

| Artifact | SHA-256 |
|---|---|
| `notes/derivation-why-not-plan.md` (r3) | `fb590faadbe2b474affc9f6abfa21be4a8d45c0346837cd20ef7a7837fde441d` |
| `notes/phase-WN1-spec.md` (r3) | `78fbfe88d414bd4db3fa305cab6b8eaf6147963ad3ab31a5631fdc2a6faf3977` |

**Review history.**
- **Rounds:** round 1 reviewed r1, and the confirmation round reviewed r2, each
  with four local reviewer agents (WN-D8 (o)).
- **The stop:** review stopped under its declared rule (self-inflicted ratio
  0.93); see the [round-2 disposition](notes/plan-review-r2-disposition.md).
- **r3:** applied the round-2 repairs L–S at the owner's direction, with no
  further review round.
- **No opinion on r3:** r3 carries no review opinion, and this approval adds
  none.

**The plan is not edited to record its own approval.** This file is the
record.

## Rulings

| Decision | Ruling |
|---|---|
| WN-D3 descent | confirmed: ground atoms only, structured-rule predicates only, cycles keyed on (predicate, row), depth 8 |
| WN-D4 values | confirmed: API raw like `api.witness`; CLI redacted by default, `--raw` shows values |
| WN-D5 exit bands | confirmed: `0` blocked or derived, `2` unsupported (incl. opaque), `3` invalid input, `4` unavailable or work limit |
| WN-D1 surface | (a) new command and API in the witness lane |
| WN-D2 order | (a) declaration-order prefixes, named in the payload |
| WN-D6 fragment and ceilings | as stated: `WhyNotLimits` with `pre_joins` and the walk's `joins`, `probes`, `binding_cells`, projected onto `WitnessLimits` for input loading |
| WN-D7 code home | (a) `gnd.witness.why_not` |
| WN-D8 review instrument | ruled earlier (o): four local readers for plan and close |
| WN-D9 samples | 5, with the total count always given |
| WN-D10 approval instrument | WN1 prose; WN2 corpus-first |
| WN-D11 rows per call | (a) one row matching `--fact-type`, else exit 3 |
| WN-D12 schema home | (a) `src/gnd/why-not.schema.json`, no skill copy |
| WN-D13 stale runtime tuple | (a) fixed in WN2 to the twelve names, recorded |
| WN-D14 validation order | (a) malformed row before unsupported fragment, as `witness` |
| spec D6 semiderived blockers | as proposed: production's extension decides; `asserted_not_read: true` on such blockers |

The per-phase diff instrument (one local reader per phase, plan §8) was
proposed; it is approved with the plan as written.

## What the approval leaves open

**WN1's own gate items**, named at the WN1 gate before implementation:
- the WN1 base commit, a full 40-hex SHA reachable from main;
- the forbidden-token list for the WN-R8 anonymity test: the owner supplies the
  tokens, and only their normalized SHA-256 digests are committed;
- T13's literal counter values are restated before that gate if the
  implementation's charging granularity differs, with the arithmetic recorded
  (standing rule 6).

**WN2 and WN3** need their own specs and gates; WN2's golden payloads are
committed red before its code (WN-D10).

## Selection

No phase has been selected. Execution starts only when the owner explicitly
selects `process-phase WN1 derivation-why-not`.

## Boundary

- **Later phases:** approval of the plan is not approval of the WN2 or WN3
  specs.
- **No push, PR, merge, release, publication or certification** is authorized by
  this record.
