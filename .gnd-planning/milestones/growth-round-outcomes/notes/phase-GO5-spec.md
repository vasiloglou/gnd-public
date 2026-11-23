# Phase GO5 · the round summary · spec r1

## 1. Status

**Draft r1, 2026-11-23, awaiting its gate.** Planning only. GO5 needs GO2
merged into the branch, and VG2 and VG5 merged on `main` because it edits
`unattended-growth.md` (plan §3); the coordinating session answers
"READY GO5".

## 2. Provenance

- Derives from [plan r4](growth-round-outcomes-plan.md) (sha256
  `b107bd36…7431`): Goal (GO5), R0.3, R0.4, R0.6, §1 H17–H19, §2 GO5, §4
  GO5-C1 to C4, §10 D4 and the GO5 open question; the GO2 spec r1 (verdicts,
  report); the GO4 spec r1 (reused ids are named by id only).
- From [#227](https://github.com/vasiloglou/gnd-public/issues/227),
  request 3.
- Code read at `92cc161f`. No review has read these bytes.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan GO5, D4 (a) | GND computes the summary from the host's round file, the proposal and preview or report, and the evolution record | §6; T1 |
| plan GO5-C1 | counts add up; a known-mix round gives each bucket its built count | T1, T2 |
| plan GO5-C1b | previewed and not applied: 0 added; narrowed then applied: the narrowed proposal's additions | T3 |
| plan GO5-C2 | two rounds with no proposal, differing only in reused ids, differ | T4 |
| plan GO5-C3 | the host's drops under the host's name; a malformed file refused | T5, T6 |
| plan GO5-C4 | the replies to #227 and #228 drafted in `notes/issue-replies.md` | §6 |
| plan H18 | the shape matches are reported as the preview carries them | §6 |
| plan open question | a file `apply` writes, or a command's output | GO5-D2 |

## 4. The standing rules, bound to this phase

- **Totality (rule 1).** The round file is host-written JSON: its reader
  caps the read at 1 MiB, refuses NaN, deep nesting, long integers, extra
  keys and duplicate keys, and names each refusal (T6).
- **A cap bounds the document (rule 2).** The summary is one pass over
  operations, outcomes, round-file rows and record entries; T7 times
  10,000 of each.
- **Validation order (rule 3).** The round file is read and refused first,
  then each artifact is bound to the round (proposal sha256 in the preview
  or report, preview sha256 in the record), then counted. Pinned by T6's
  order case.
- **One walk (rule 4).** One function counts every bucket; no per-bucket
  reader.
- **One home (rule 5).** The summary's fields live in the evolution
  contract; `unattended-growth.md`, "What one round is", cites them in one
  sentence.
- **Measurement (rule 6).** The H19 baseline (20 rounds, 2 elements) is
  replayed in T1 as three rounds of the acceptance replay.
- **General solutions.** All inputs are JSON documents read with their
  closed models.

## 5. Goal

`gnd evolve summary ROUND_FILE [--proposal P] [--preview V | --outcome-report R] [--record D]`
prints one JSON summary of the round: ids reused, host drops, operations by
kind and collection, verdicts (GO2), shape matches, and elements added
(from the record only).

## 6. Design

### The round file (`gnd-round/1`, host-written)

```json
{"schema_version": 1, "round": "r7", "document": "policy.txt",
 "reused": [{"collection": "fact_types", "id": "policy_has_holder"}],
 "host_drops": [{"kind": "fact_type", "id": "policy_has_note", "reason": "no constraint and no open question"}]}
```

`reason` is the host's text and is reported as the host's, under
`host_drops`; GND judges nothing in it. A closed Pydantic model with a
1 MiB read cap.

### The summary (`gnd-round-summary/1`)

`round`, `document`, `reused` (count and ids), `host_drops` (count and
rows), `proposed` (operations by kind and collection; zero when no
proposal), `outcomes` (count per GO2 verdict; absent when the preview
carries none), `shape_matches` (count of groups, as the preview carries
them), `added` (element ids by collection: the `add` operations on element
locators in the evolution record's `operations`, the record bound by its
`preview_sha256`; zero without one), `bindings` (the sha256 of each artifact read).
`proposed` equals the sum of `outcomes` when outcomes are present (GO5-C1).
A narrowed round passes the narrowed proposal and its record; the summary
names `narrowed_from` when the proposal has it.

### Where it lives

`src/gnd/evolve/summary.py` (new): `round_summary(...)` and the round-file
reader. `gnd evolve summary` in `src/gnd/commands/evolve.py` and
`src/gnd/evolve/cli_service.py`, printing to stdout; it writes no file and
`apply` is unchanged (GO5-D2).

### Pages and replies

Evolution contract: "Round summary" (fields). `unattended-growth.md`,
"What one round is": one sentence and the command. `notes/issue-replies.md`:
replies to #227 and #228 naming what is on `main` and what is not
released (GO5-C4); the owner posts them.

## 7. Decisions

| ID | Question | Readings | Proposed |
|---|---|---|---|
| GO5-D1 | Instrument | a serialized format: corpus-first is the default; the round file and the summary are one closed model each, with T1–T5 as the narrated corpus | prose, with T1–T5's fixtures committed under `tests/fixtures/round-summary/` |
| GO5-D2 | A file `apply` writes, or a command (plan open question) | (a) a command over artifacts the host already keeps: `apply` unchanged (R0.3). (b) `apply` writes it: a new record and an `apply` change | (a) |
| GO5-D3 | Where `added` comes from | (a) the evolution record only (plan r4, p2). (b) the preview: counts what was never applied | (a) |

## 8. Tests

New `tests/test_go5_round_summary.py`; fixtures under
`tests/fixtures/round-summary/`.

| # | Case | Expected |
|---|---|---|
| T1 | three rounds of the unattended acceptance replay, each with its round file, preview and record (GO5-C1) | counts add up to the operations proposed; `added` equals the record's |
| T2 | a committed known-mix round: one admitted, one `refused-by-policy`, one `dropped-with`, one host drop, one reused id, one shape match (GO5-C1) | each bucket the count the fixture was built with, stated in the fixture's README |
| T3 | an admitted round previewed and not applied; a narrowed-then-applied round (GO5-C1b) | 0 added; the narrowed proposal's additions, `narrowed_from` named |
| T4 | two rounds with no proposal, one listing reused ids (GO5-C2) | different summaries; the empty one zero in every count |
| T5 | host drops (GO5-C3) | under `host_drops`, reason verbatim |
| T6 | hostile round files: 2 MiB, NaN, depth 10,000, a 5,000-digit integer, an extra key, a duplicate key; a preview of another proposal; a record of another preview | a named refusal each, in the order of §4 rule 3 |
| T7 | 10,000 operations, outcomes and rows | under one second |
| T8 | `tests/test_unattended_growth_guidance.py`, the CLI option guard included | exit 0 |

Gate: plan §9 GO5 lane, guard block, both lint commands, component check.

## 9. Out of scope

A summary across rounds (the host compares summaries); any judgment of the
host's reasons; GND reading the reply.

## 10. Size

About 180 source lines and 350 test lines, plus fixtures.

## 11. Approval instrument

This prose, with the committed fixtures (GO5-D1).

## 12. Gate — delegated approval (auto=true)

**Delegated approval (auto=true), 2026-11-23**, of this spec r1, sha256
`2249d8201ce3667a4fb9cc69ab3d291bff6f676b8605dec551e361e182057dc8` (the bytes above this section). Authorization: the owner's
delegation of `auto` for growth-round-outcomes, recorded in
`001-plan-gate.md`. An agent ruling under that delegation, not the owner's
reading of the spec. No spec review ran (optional, omitted).

- Rulings: GO5-D1 prose with committed fixtures; GO5-D2 (a); GO5-D3 (a) [delegated].
- Sweep: the evolution record carries `operations` and `preview_sha256`, so `added` and the binding are computable; the round file is new host input and gets a total reader. Depends on GO2's verdicts and GO3's `narrowed_from`.
- Budget: one diff review round (D8), a second only if the first blocks.
- **Approval is of the design only. Implementation waits** for the
  start condition of plan §3 on `main` and the coordinating session's
  "GO" to "READY GO5". A spec approved now is re-read against `main` at
  that start; a change on `main` that moves a cited line or a premise
  amends this spec before code, with the prior wording retained.
