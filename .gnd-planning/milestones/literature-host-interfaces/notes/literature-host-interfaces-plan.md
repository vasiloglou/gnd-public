# Literature host interfaces · plan r1 (outline)

**Status: outline draft, 2026-11-21. Not reviewed and not approved.** This
plan covers [#216](https://github.com/vasiloglou/gnd-public/issues/216) and
[#215](https://github.com/vasiloglou/gnd-public/issues/215). It delivers the
interface half of the "host-scale reading and extraction" carryover from the
[literature-depth close](../../literature-depth/016-milestone-close.md); the
run over a separately selected corpus and provider budget stays carried with
the literature-identity follow-up, as that close assigned it. Phases are
outlines; none has a spec yet. `start-milestone` turns this outline into the
full plan and the LH1 draft spec, and the plan review runs then. Repaired after
the PR 219 reviews (`.gnd-planning/reviews/pr-219-r2/` and `pr-219-panel/`).

## Goal and completion predicates

A host with its own corpus and its own vocabulary model calls the two
literature examples as library functions instead of reimplementing them. The
examples stay examples: neither is promoted to stable CLI (both issues say so).

- **LH1.** `examples/literature/reading.py` exposes a public producer protocol:
  a call goes in, an outcome (`accepted`, `empty`, `refused`, and the existing
  others) comes out. `SavedProducer` is one implementation of it. `run()`
  takes a producer, a caller input root, a caller vocabulary model, a stop rule
  per document as well as the global one, the roster cap (today
  `ROSTER_LIMIT = 128`) and the byte budget (today `MAX_BUDGET = 1 << 20`).
  With a live producer, the input root needs no saved `responses.json` or
  producer pin: `ReadingInputs` today requires both (`reading.py:72-75`,
  "saved producer table differs from its pin"), requires the saved responses
  to cover every section (`:113`, "saved response roster differs"), and loads
  the vocabulary from the packaged depth fixture unless told otherwise
  (`:135`). The responses a live run produces are written to its run folder.
  The protocol's call carries the section's source bytes: today
  `produce(stage, section)` gets two names only (`:156`), and the loop reads a
  `calls` count from the producer (`:457`).
  The stage loop is also tied to the packaged fixture in six places, listed in
  §1. LH1 makes each one caller data or an optional step (owner decision D3).
- **LH2.** `replay()` already takes a run folder and an input root
  (`reading.py:574`, `fixture=`). LH2 makes it replay a live LH1 run from its
  folder and the caller's input root, with the captured responses and the
  caller's vocabulary, with zero producer calls.
- **LH3.** `examples/literature/assertion_admission.py` takes the assertion
  entity (objectified fact type or entity type) by name. Its identity is that
  model's preferred uniqueness, not (work, passage). Optional roles are
  optional, with no `unspecified|none|n/a` sentinels. Every fact row attached
  to an admitted assertion is kept.
- **LH4.** Admissible polarity and attribution values are policy data, not the
  hard-coded `("asserts", "own-finding")`. A supported row that fails the
  policy gets its own disposition. Today the record has two stages,
  `semantic-support` and `positive-own-findings` (`:115-125`), and both mark a
  row `fail`; a supported row that fails the policy passes the first and fails
  the second with reason `negated` or its attribution value. `MAX_TARGETS`
  (today 1024) is a parameter.

## 0. Binding design rules

- **Formats stay.** The stage-file, coverage-row and rebind formats are
  unchanged; #216 says they work as they are.
- **Fixture bytes stay.** The packaged runs and their recorded outputs are
  byte-identical with the defaults. The saved-response pin and roster checks
  stay in force for `SavedProducer`.
- **Example status stays.** Public here means documented and tested as the
  example's library surface, not a stable CLI.

## 1. Scope, sources and authority

| Source | Obligation | Phase |
|---|---|---|
| #216 "Problem" | `reading.py:562` `run()` builds `SavedProducer(inputs.responses)` at `:566`; only private `_evaluate(..., producer=)` at `:445` takes another. `ReadingInputs` binds the root to saved responses at `:72-75` and `:113`, and to the packaged vocabulary at `:135`. Confirmed at `0f39c392` on 2026-11-21 | LH1 |
| `reading.py`, fixture bindings in the stage loop | The `unavailable` scenario names section `study-methods` (`:448`). `_calibrate` names that section and the two facts in `CALIBRATION_FACTS` (`:42`, `:311-327`). `_combined` adds the fixture's `LABEL` to every population (`:48`, `:247`). `_public_results` needs the fixture's `conflict.json` and `conflict.txt` and a conflict that fails `verify` and `check` (`:395-407`). `absence_status` needs predicate `alternative_integrator` (`:373`). `_review_attempts` needs a `reviews.json` receipt bound to the facts digest of each accepted response (`:198-209`), which cannot be written before a live producer has answered. Read at `0f39c392` on 2026-11-21 | LH1 |
| #216 "Request" bullets 2–4 | Per-document stop rule; `ROSTER_LIMIT` `:41` and `MAX_BUDGET` `:40` as parameters; `replay()` at `:574` against a caller root | LH1, LH2 |
| #215 "Problem" | `assertion_admission.py:100` `project()`; sentinels `:30`; policy `:122`; `MAX_TARGETS` `:29` | LH3, LH4 |
| #215 measured shape | 98 % of claims share a passage; about half lack one actor and one object; 9 % have several conditions; 44 % carry a quantity | LH3 acceptance fixture |
| literature-depth close, row "Host-scale reading and extraction" | Interface half only; the corpus and provider-budget run stays with the literature-identity follow-up | LH1, LH2 |

### Issue requests and the phases that discharge them

| Request | Phase |
|---|---|
| #216: a public producer protocol, live and replayable | LH1, LH2 |
| #216: the stop rule per document as well as global | LH1 |
| #216: the roster cap and the byte budget as parameters | LH1 |
| #216: `replay()` against a caller-given input root | LH2 |
| #215: caller-named assertion entity, identity from its preferred uniqueness | LH3 |
| #215: every fact row of an admitted assertion kept | LH3 |
| #215: optional roles are optional | LH3 |
| #215: polarity / attribution policy as data, with a distinct disposition | LH4 |
| #215: `MAX_TARGETS` as a parameter | LH4 |

## 2–3. Contract sketch and dependencies

- **LH1–LH2** adapt `reading.py` only; the stage loop already exists in
  `_evaluate`, with the fixture bindings §1 lists. LH2 needs LH1.
- **LH3–LH4** adapt `assertion_admission.py`; `gnd judgments check` stays the
  admitting command. LH4 needs LH3.
- The two pairs are independent and can run in parallel on separate branches.
- Start condition: none. No other roadmap milestone uses these interfaces.
  Running it after include-root-routes lets LH3's fixture use an include root,
  which is the reporter's real setup. That also needs the admission snapshot
  to copy the includes: today it copies one model file (`:146-148`,
  `:188-191`).

## 4. Phases

| Phase | Outline criteria |
|---|---|
| LH1 | A test producer drives all six stages over a caller corpus and a caller vocabulary model, both distinct from the packaged fixture, with no saved `responses.json` or pin, and with no section or fact named as the packaged fixture names them. Each fixture-only step runs on caller data or is recorded as skipped, as D3 rules. The captured responses land in the run folder. A per-document stop ends one document and not the others. A lowered cap and budget are honoured and recorded. The packaged `SavedProducer` run is byte-identical |
| LH2 | That live run replays from its own folder and the caller's input root with zero producer calls, byte-identical. A tampered captured response refuses |
| LH3 | A model with a multi-participant, multi-condition, quantity-bearing assertion and a passage shared by two assertions admits with every row intact. The packaged example still admits as before |
| LH4 | A policy file changes which rows admit. A supported row that fails the policy has a status distinct from the `fail` of an unsupported one |

## 5. Owner decisions and open questions

| ID | Question | Proposed |
|---|---|---|
| D1 | Where the producer protocol lives: in `reading.py`, or a small shared module other examples can use | In `reading.py` until a second user appears |
| D2 | Name of the new LH4 disposition | Status `policy-refused` in the policy stage, beside `pass` and `fail`; the packaged record keeps its bytes under the default policy |
| D3 | LH1: for a caller run, which fixture-only steps become caller data and which become optional: the semantic review receipts, the held-back fidelity calibration, the reported-conflict check, the absence scope and the subject label | Review receipts come from a caller reviewer after the producer answers and are captured in the run folder, so replay checks them. Calibration, the conflict check and the absence scope are optional caller inputs; a run without one records that step as skipped. The label is caller data |

## 6–9. Surfaces, risks, protocol, verification

- **Surfaces.** The literature examples page and the literature tutorial each
  gain a "drive it from your host" section.
- **Risks.**
  - A generic admission could admit rows the packaged example refused.
    Control: the packaged fixture's admitted set is pinned.
  - Dropping the saved-response pin for live runs could weaken the packaged
    replay. Control: the pin and roster checks stay for `SavedProducer`, and
    LH2 binds a live run's captured responses by digest.
- **Protocol.** `process-milestone` with the project rules in
  `.codex/skills/process-phase/references/project.md`.
- **Verification.** Each spec names its focused lane from
  `test_ld3_reading_workflow.py`, `test_ld4_revision.py`, `test_ld5_verdict.py`
  and `test_li4_assertions.py`, plus the structure and inventory guards.
