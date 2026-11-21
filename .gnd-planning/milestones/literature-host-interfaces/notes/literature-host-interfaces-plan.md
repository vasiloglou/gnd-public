# Literature host interfaces · plan r1 (outline)

**Status: outline draft, 2026-11-21. Not reviewed and not approved.** This
plan covers [#216](https://github.com/vasiloglou/gnd-public/issues/216) and
[#215](https://github.com/vasiloglou/gnd-public/issues/215). It also takes the
"host-scale reading and extraction" carryover from the
[literature-depth close](../../literature-depth/016-milestone-close.md).
Phases are outlines; none has a spec yet. `start-milestone` turns this outline
into the full plan and the LH1 draft spec, and the plan review runs then.

## Goal and completion predicates

A host with its own corpus and its own model calls the two literature examples
as library functions instead of reimplementing them. The examples stay
examples: neither is promoted to stable CLI (both issues say so).

- **LH1.** `examples/literature/reading.py` exposes a public producer protocol:
  a call goes in, an outcome (`accepted`, `empty`, `refused`, and the existing
  others) comes out. `run()` takes a producer, a stop rule per document as well
  as the global one, the roster cap (today `ROSTER_LIMIT = 128`) and the byte
  budget (today `MAX_BUDGET = 1 << 20`). `SavedProducer` is one implementation
  of the protocol.
- **LH2.** `replay()` takes a caller-given input root and replays a live run
  with zero producer calls. The packaged fixture stays the default.
- **LH3.** `examples/literature/assertion_admission.py` takes the assertion
  entity (objectified fact type or entity type) by name. Its identity is that
  model's preferred uniqueness, not (work, passage). Optional roles are
  optional, with no `unspecified|none|n/a` sentinels. Every fact row attached
  to an admitted assertion is kept.
- **LH4.** Admissible polarity and attribution values are policy data, not the
  hard-coded `("asserts", "own-finding")`. A supported row that fails the
  policy gets its own disposition. `MAX_TARGETS` (today 1024) is a parameter.

## 0. Binding design rules

- **Formats stay.** The stage-file, coverage-row and rebind formats are
  unchanged; #216 says they work as they are.
- **Fixture bytes stay.** The packaged runs and their recorded outputs are
  byte-identical with the defaults.
- **Example status stays.** Public here means documented and tested as the
  example's library surface, not a stable CLI.

## 1. Scope, sources and authority

| Source | Obligation | Phase |
|---|---|---|
| #216 "Problem" | `reading.py:562` `run()` builds `SavedProducer(inputs.responses)` at `:566`; only private `_evaluate(..., producer=)` at `:445` takes another. Confirmed at `0f39c392` on 2026-11-21 | LH1 |
| #216 "Request" bullets 2–4 | Per-document stop rule; `ROSTER_LIMIT` `:41` and `MAX_BUDGET` `:40` as parameters; `replay()` at `:574` against a caller root | LH1, LH2 |
| #215 "Problem" | `assertion_admission.py:100` `project()`; sentinels `:30`; policy `:122`; `MAX_TARGETS` `:29` | LH3, LH4 |
| #215 measured shape | 98 % of claims share a passage; about half lack one actor and one object; 9 % have several conditions; 44 % carry a quantity | LH3 acceptance fixture |
| literature-depth close | Host-scale reading and extraction carryover | LH1, LH2 |

## 2–3. Contract sketch and dependencies

- **LH1–LH2** adapt `reading.py` only; the stage loop already exists in
  `_evaluate`. LH2 needs LH1.
- **LH3–LH4** adapt `assertion_admission.py`; `gnd judgments check` stays the
  admitting command. LH4 needs LH3.
- The two pairs are independent and can run in parallel on separate branches.
- Start condition: none. Running it after include-root-routes lets LH3's
  fixture use an include root, which is the reporter's real setup.

## 4. Phases

| Phase | Outline criteria |
|---|---|
| LH1 | A test producer drives all six stages through the public call. A per-document stop ends one document and not the others. A lowered cap and budget are honoured and recorded |
| LH2 | A live run with a test producer replays from its own folder with zero calls, byte-identical. A tampered input refuses |
| LH3 | A model with a multi-participant, multi-condition, quantity-bearing assertion and a passage shared by two assertions admits with every row intact. The packaged example still admits as before |
| LH4 | A policy file changes which rows admit. A supported row that fails the policy has a disposition distinct from an unsupported one |

## 5. Owner decisions and open questions

| ID | Question | Proposed |
|---|---|---|
| D1 | Where the producer protocol lives: in `reading.py`, or a small shared module other examples can use | In `reading.py` until a second user appears |
| D2 | Name of the new LH4 disposition | `policy-refused`, beside the existing unsupported one |

## 6–9. Surfaces, risks, protocol, verification

- **Surfaces.** The literature examples page and the literature tutorial each
  gain a "drive it from your host" section.
- **Risks.** A generic admission could admit rows the packaged example
  refused. Control: the packaged fixture's admitted set is pinned.
- **Protocol.** `process-milestone` with the project rules in
  `.codex/skills/process-phase/references/project.md`.
- **Verification.** Each spec names its focused lane from
  `test_ld3_reading_workflow.py`, `test_ld4_revision.py`, `test_ld5_verdict.py`
  and `test_li4_assertions.py`, plus the structure and inventory guards.
