# Growth round outcomes · plan r4

**Status: r4, 2026-11-23.** r2 was the full plan `start-milestone` wrote from
outline r1 (2026-11-22, merged in PR 229). The owner delegated `auto` for this
milestone only on 2026-11-23 and ruled D7 ("Full panel, both") and D8
("Review helper, both"). The full GND panel read r2 (sha256 `a041b21d…17ba`)
in round 1: five of six seats, 8 agreed groups and 5 single-reviewer
concerns, all reproduced
([disposition](../evidence/plan-review-r1/disposition.md)). r3 applies them,
each change tagged `(p1)`. Round 2 read r3 (sha256 `2d9e62f8…8d48`): three
of six seats, 2 agreed groups and 10 single-reviewer concerns, all
reproduced ([disposition](../evidence/plan-review-r2/disposition.md)). r4
applies them, tagged `(p2)`; the review budget of two rounds is spent and no
reviewer has read r4. Approval is recorded only in a plan-gate record.

This plan covers two open issues:
[#228](https://github.com/vasiloglou/gnd-public/issues/228) (a growth round
costs time in proportion to the whole model) and
[#227](https://github.com/vasiloglou/gnd-public/issues/227) (a round is applied
whole, replies restate what they reuse, and a host cannot tell an empty round
from a covered one).

**Provenance.** Phase IDs GO1–GO5 and decisions D1–D6 are the outline's and
keep their meaning. r2 adds criteria IDs, obligations H1–H24 and decisions
D7–D9. The outline read code at `17ab99d2`; every citation here was read
again at `548b9a1d` (`main`, 2026-11-23), and no cited file under
`src/gnd/evolve`, `src/gnd/model`, `src/gnd/discover` or
`src/gnd/input_policy.py` differs between the two, by `git diff`.
Measurements marked "observed" were run on one laptop, in process, once each,
on 2026-11-23, while other work ran on the same machine. Two runs of the same
unchanged case differed by 12 % for `apply` at 2,404 object types and by up to
77 % for the sub-second and one-second timings at 604, so only the large
differences below are evidence.

## Goal and completion predicates

A host that grows one model over many documents with no reviewer gets more
out of each round, and each round costs less.

- **GO1.** One `gnd evolve preview` or `gnd evolve apply` parses each distinct
  model text once per reader (a `.json` workspace model is parsed once as
  strict JSON and once under the YAML name `_parse_model_text` uses) (p2). Today `apply` parses two texts 22 times and `preview` 6
  times (H2). The number of parses does not depend on the size of the model,
  and every record `gnd evolve` writes is byte-identical.
- **GO2.** `gnd evolve preview` names an outcome for every operation of the
  proposal, in the preview when the candidate validates and in a separate
  outcome report when it does not (p1). Today the additive policy lists each operation it refuses
  (`policy_issues`), and every other refusal is one error for the whole
  proposal, tied to no operation (H10, H11).
- **GO3.** A host can keep the admitted operations of a proposal and drop the
  others with one call. The result is a new proposal with its own preview;
  `apply` still applies a reviewed preview whole.
- **GO4.** `unattended-growth.md` states what a reply carries for a fact type
  the model already has, and a guard test holds the statement.
- **GO5.** A round ends with a summary a host can log and compare across
  rounds and growers: operations proposed, mapped onto existing elements,
  dropped and why, and elements added.

The milestone is closed when each phase has its record and the close record
cites green focused gates for GO1–GO5, the structure and inventory guards,
`uv run ruff check src tests tools`, the component-index check, a drafted
reply to each of the two issues, and a close review on the instrument D7
selects.

## 0. Binding design rules

- **R0.1 `apply` stays whole.** A preview is applied exactly as reviewed. No
  phase adds partial application to `apply`.
- **R0.2 No check is relaxed and none is skipped.** Revalidation in `apply`
  stays (#228, "Not requested"). GO1 removes repeated reading of the same
  bytes; it does not remove a validation, a guard or a digest comparison.
  New constraints stay `proposed` and `deontic` (#227, "Not requested").
- **R0.3 Records keep their bytes.** A proposal that is admitted today
  produces the same preview, pending state, record and published model after
  GO1. GO2, GO3 and GO5 add only optional fields that are omitted when unset, as
  `_OPTIONAL_PREVIEW_FIELDS` does today (`evolve/models.py:874`), and move no
  schema version, so a preview that does not carry them keeps every byte and
  digest (D2) (p1).
- **R0.4 Previews stay value-free.** A per-operation outcome names ids, key
  names and a verdict word, as `PolicyIssue.detail` does today
  (`evolve/models.py:890-900`).
- **R0.5 A cache is keyed by content and reader and lives for one call.**
  Anything GO1 remembers is keyed by the sha256 of the bytes and by whether
  the source name selects the strict JSON reader (a `.json` suffix), the only
  way the name changes a successful parse (H5); one helper computes that bit
  for the parser and for the key (p1). It is dropped when the command
  returns. A changed file is different bytes and is read again.
- **R0.6 One home per rule.** What a reply carries lives in "The reply shape"
  of `unattended-growth.md`; the preview's fields live in the evolution
  contract. Every other page cites them.

The project's six standing rules
(`.codex/skills/process-phase/references/project.md`) and the rule "General
solutions, not pattern-matched ones" (`AGENTS.md`) bind every phase; each
spec discharges them by name.

## 1. Scope, sources and authority

Harvested obligations. "Observed" means read or run at `548b9a1d` on
2026-11-23; "inherited" means claimed by a source and not re-measured here.

| # | Source | Obligation | Kind | Phase |
|---|---|---|---|---|
| H1 | #228 "Measured" | one round (validate, preview, apply) that adds one fact type and one constraint: 2.4 s at 34 object types, 6.6 s at 304, 11.3 s at 604, 21.0 s at 1,204, 42.6 s at 2,404, CLI wall time at `4ad0d216`; `apply` is two thirds of it | inherited (measured in this session on 2026-11-22) | GO1 |
| H2 | probe: a call hook on `parse_model_document` | `gnd evolve apply` parses 22 times, two distinct texts (the current model 10 times, the candidate 12); `gnd evolve preview` 6 times, 3 each. The count is the same at 64 and at 2,404 object types | observed | GO1 |
| H3 | `evolve/service.py:241-297` | `_load_model_document` parses its bytes three times: in `guard_bytes` → `bytes_declare_includes` (`model/_includes.py:285-302`), in `load_model_bytes` (`model/__init__.py:287-296`) and at `:291` for the document it returns | observed | GO1 |
| H4 | probe (H2), by caller | one `apply` calls `_load_model_document` 7 times: twice in `apply` (`:2203`, `:2344`), twice in `finalize` (`:2532`, `:2539`), once in the `preview` that `apply` runs again (`:1594`), and twice through `_validated_candidate` (`:1507-1518`). `_parse_model_text` (`:338-349`, called at `:2145`) is the 22nd parse | observed | GO1 |
| H5 | `model/_parsing.py:25-…` | `parse_model_document(data, *, source)` reads `source` only for its suffix (`.json` selects the strict JSON reader) and for the name in a refusal. Text starting with `{` under any other name tries JSON and falls back to YAML; under a `.json` name the same text is refused. For the same bytes and the same suffix test it returns equal documents (p1) | observed by reading | GO1 |
| H6 | scratch prototype, not the implementation | with `parse_model_document` memoized by content for one command, the same document object handed to every caller: `preview` and `apply` print byte-identical output and publish the identical model, with 2 parses each. In-process seconds, before and after: at 604 object types `preview` 1.93 → 0.94, `apply` 6.72 → 2.07; at 2,404, `preview` 8.51 → 4.43, `apply` 28.43 → 9.95 | observed | GO1 (the bound is reachable) |
| H7 | the same prototype, handing each caller a `copy.deepcopy` | slower than parsing at size: `apply` 41.3 s at 2,404 object types against 28.43 s unchanged | observed | GO1 (a copy per caller is refuted) |
| H8 | `evolve/service.py:300-314`; `input_policy.py:113-134`; probe | `_guard_yaml_document` scans the text again as YAML events for a document the YAML reader built: 4 scans in one `apply`, 1 in `preview`. Remembering the verdict too gave `apply` 8.04 s at 2,404 in a second series whose unchanged run was 31.86 s | observed | GO1 (spec decision) |
| H9 | probe; `model/__init__.py:326-…`, `:287` | `load_model` itself parses twice: `_load_model_at` parses to see whether the file declares includes, then `load_model_bytes` parses again. `gnd validate` on the 2,404-type model: 4.30 s, 2.34 s with one parse | observed | D9 |
| H10 | `evolve/cli_service.py:364-368`; `evolve/models.py:890-900` | under `--policy additive` the preview carries `policy_issues`, one row per refused operation: `operation_index`, `operation_id`, `reference`, `cell`, `detail` | observed by reading | GO2 |
| H11 | `evolve/service.py:292-297`, `:338-349`, `:402-477` | a refusal outside the policy (the candidate does not validate, the candidate does not equal the replayed operations, rule D-12) raises one `EvolutionError` for the proposal. Its exit code and whether the message names an element were not re-read here; the GO2 spec reads them | observed by reading, in part | GO2 |
| H12 | `evolve/models.py:26-32`, `:647-651` | a proposal is a candidate model text plus its operations, schema versions 1 to 3; the current version is 3 | observed by reading | GO2 (D2), GO3 |
| H13 | #227 cause 1 | one fact type with neither a constraint nor an open question sinks the round. The rule that rejects it is the reporter's host rule, not a GND refusal. GND's part: dropping one operation means rebuilding the candidate model and the operations together | inherited | GO2, GO3 |
| H14 | `discover/output.py:90-91`, `:102-…` | `candidate_document(before, ops)` replays operations over a model and `candidate_text(document)` writes the candidate text; component `discover.output` | observed by reading | GO3 reuses them |
| H15 | #227 cause 2 | replies restate reused fact types with their rows: 12,000 to 16,000 output tokens a round against 4,700 for a reply that does not; one round truncated at 16,000 | inherited | GO4 |
| H16 | `unattended-growth.md:235`, `:286` (`src/gnd/skills/gnd-model-from-text/references/`) | "The reply shape" says of `object_types` and `fact_types`: "ids that already exist are reused". Nothing says whether a reply repeats a reused element or its rows | observed | GO4 |
| H17 | #227 request 3 | a diagnostic per round: proposed, mapped onto existing elements, dropped, added | inherited | GO5 |
| H18 | `evolve/shapes.py:1-13`; `evolve/cli_service.py:373-376`; `unattended-growth.md:57-73` | `--shape-report` lists, for each added fact type, the existing fact types over the same role players. It is advice; the host decides and logs | observed by reading | GO5 reuses it |
| H19 | #227 "What we measured" | 20 rounds over four growers added 2 elements; two growers applied 0 of 5 rounds | inherited | GO5 (the baseline a summary must explain) |
| H20 | #227 "Not requested"; #228 "Not requested" | no relaxing of `proposed` and `deontic`; no check is weakened, skipped or removed, and no existing refusal changes its exit (R0.2). Optional fields added under R0.3 are not a record change in this sense (p1) | inherited | R0.2 |
| H21 | [reviewed-vocabulary-growth](../../reviewed-vocabulary-growth/notes/reviewed-vocabulary-growth-plan.md) r4, approved by the owner on 2026-11-23 (PR 236), §3 and H36; `PROJECT.md`, "Proposed order" | that plan's VG2 and VG4 change `src/gnd/evolve/service.py`, and its VG2 and VG5 change `unattended-growth.md`. Under that plan's ruled D2 (a), VG2's homes omit `unattended-growth.md` and only VG5 changes it there; the conditions below keep VG2 because the coordinating session set them that way (p2). One writer at a time on each: VG1, then GO1, then VG2–VG5, then GO2–GO5. `tests/test_unattended_growth_guidance.py` is shared with VG2 and VG5 too; `docs/release-notes.md`, `PROJECT.md` and `dev/components/` are append-only homes every lane edits (p1) | observed by reading | §3 |
| H22 | `model_index.py:52-71` | `index_scope()` already gives one public call a shared cache through a context variable, re-entrant, dropped on exit | observed by reading | GO1 reuses the pattern |
| H23 | `project.md`, "Component index"; `components_index.py review` | the index is searched before a capability is built and updated in the same commit. `review` lists 276 leads in 10 groups; an index review is offered to the owner and is not a prerequisite | observed | all |
| H24 | reviewed-vocabulary-growth plan H27, D11; `project.md`, "Test and gate commands" | r2 said whole-repository `uv run ruff check` exits 1. Re-run at `11a7ebf7` on 2026-11-23: both `uv run ruff check` and `uv run ruff check src tests tools` exit 0 (p1). Records name `uv run ruff check src tests tools`, as that plan's D11 rules, and also run the whole-repository form | observed | all |

Component index (`dev/components/`), searched 2026-11-23:

| Capability | Search | Found |
|---|---|---|
| parse one model text | `search "parse model document yaml"` | component `model.loading` (`load_model`, `flatten_model`, binding) |
| per-operation outcome in a preview | `search "evolve preview policy issue"` | `src/gnd/evolve/cli_service.py` (`_cmd_evolve_preview`); `PolicyIssue` in `evolve/models.py` |
| rebuild a proposal from operations | `search "candidate proposal operations replay"` | `src/gnd/discover/output.py`: `candidate_document`, `candidate_text`, `add_operations` |
| a per-round summary | `search "growth round summary"` | nothing that fits; the shape report (H18) is the nearest |

### Issue requests and the phases that discharge them

| Request | Phase |
|---|---|
| #228: parse each distinct model text once per `gnd evolve` invocation (once per text and reader, p2) | GO1 |
| #228: a bound a test can hold on the number of parses, the same at 100 and at 1,000 object types | GO1 |
| #227: a per-element outcome from `evolve preview` | GO2 |
| #227: or a documented way to apply part of a proposal | GO3 |
| #227: guidance on what a reply contains when it reuses existing fact types | GO4 |
| #227: a growth diagnostic per round | GO5 |

This is a framework milestone. An experiment-claim census (`gnd coverage`)
counts claims over a domain model; it says nothing about what `gnd evolve`
costs or reports, so none is read here. The baseline is rows H1, H2, H6 and
H19.

## 2. Contract proposal and product behavior

### GO1 — one parse per model text

- `gnd evolve preview`, `apply` and `finalize` open a parse scope. Inside it
  `parse_model_document` returns the document it already built for the same
  bytes and the same suffix test (R0.5): YAML-flow bytes that start with `{`
  and parsed under a `.yaml` name are still refused under a `.json` name
  (p1). Outside a scope it behaves as today, so no other
  command changes.
- The scope follows `index_scope()` (H22): a context variable, re-entrant,
  dropped when the outermost call returns.
- A parse that raises is not remembered: the refusal is raised again by a
  second parse, with the caller's own name in the message.
- The remembered document is shared, not copied (H7). Every `Model` loaded
  inside the scope holds its nested lists and mappings, because
  `_finish_model` copies only the top level (`model/__init__.py:315`) and a
  frozen `Model` leaves nested content mutable (`documents.py:40-41`), so a
  write through a loaded model is a write into the shared document (p2). A
  verify mode of the scope compares the snapshots below at every scope close
  and is switched on for the whole GO1 lane, not only for GO1's own cases
  (p2). No caller may write into it; a test compares a type-preserving snapshot of it (one that keeps
  YAML dates, tags and other values JSON cannot spell) when the scope closes
  with the same snapshot taken when it was built (p1).
- No record, flag, message or exit code changes (R0.3). The details and the
  spec's own decisions (the guard scan of H8, the loader's double parse of
  H9) are in the [GO1 draft spec](phase-GO1-spec.md).

### GO2 — an outcome for every operation

Proposed under D1 (a) and D2 (a), repaired in r3 (p1). Two documents carry
outcomes, because a candidate that does not validate has no preview:
`EvolutionPreview` requires validation evidence, a verbalization and a blast
radius built from a validated candidate (`evolve/models.py:1035-1055`), and
the refusal is raised before any preview exists (`evolve/service.py:294-295`).

- **Admitted candidate.** The preview gains `operation_outcomes`, an
  optional field omitted when unset (R0.3), one row per operation in proposal
  order: index, id, reference, a verdict (`admitted`, `refused-by-policy`,
  `dropped-with` for an operation that depends on a refused one) and a
  value-free detail. No schema version moves. `policy_issues` keeps its rows
  and its meaning.
- **Refused candidate.** `gnd evolve preview` writes no preview, exits as
  today, and, when asked, writes an outcome report: a separate document with
  its own type that `apply` refuses by type. Each refusal the gate can tie to
  an operation (by the element's id or locator) is a row with
  `refused-by-validation` or `refused-by-d12`; a refusal the gate cannot tie
  to an operation is one whole-proposal row, and every operation is then
  `unassessed`. The report carries the before model as the preview does
  (its text and sha256), so GO3 can replay the admitted operations over it
  (p2). An operation that a later gate never reached because an earlier gate
  refused the candidate is `unassessed`, and the row names the gates that did
  not run; `admitted` in an outcome report means every gate ran over it
  (p2).
- **Apply replays the setting.** Outcomes are switched on by a preview flag
  beside `--shape-report` and the matching library keyword. `apply` reads the
  setting from the reviewed preview, as it does for the shape report
  (`cli_service.py:810`), so the fresh preview it compares carries outcomes
  exactly when the reviewed one does (p2).
- **One pass.** Today `_enforce_d12` and the validators stop at the first
  fault (`service.py:402-477`; `model/__init__.py:302-304`). GO2 collects
  every fault the gate can locate in one pass where the gate allows it, keeps
  today's first message and exit for the whole-proposal path, and defines
  `admitted` as "every gate ran over the operation and none refused it in
  this pass" (p2). A narrowed proposal is
  previewed again (GO3), which is where a masked fault surfaces.
- The GO2 spec reads the exit and message of each whole-proposal refusal
  (H11's unread half) and states the report's fields.

### GO3 — the admitted part as a new proposal

Proposed under D5 (a): a library function beside `candidate_document` takes a
proposal and its preview or outcome report and returns the proposal of the
operations that are `admitted` or `unassessed`, dropping those refused and
those `dropped-with` a refused one (p2):
the candidate text rebuilt by `candidate_document` and `candidate_text`, a
new `proposal_id`, and the id of the proposal it came from, in an optional
proposal field omitted when unset (R0.3), so a proposal without it keeps its
bytes and `proposal_sha256` (p2). An operation that
depends on a dropped one is dropped with it and named. The host previews and
applies the narrowed proposal as any other (R0.1).

### GO4 — what a reply carries for a reused fact type

Proposed under D3 (a): "The reply shape" says a reply names a fact type the
model already has by its id only. It carries rows for it only when the
document adds rows, and then under the existing id. The example in the page
shows one reused and one new fact type.

### GO5 — the round summary

Proposed under D4 (a), repaired in r3 (p1) and r4 (p2): GND computes the
summary from a round file the host writes plus, when the round produced one,
the proposal and its preview or outcome report, and the evolution record
when the round was applied. Elements added come from the evolution record
only; a round that was previewed and not applied adds none. A narrowed
round reads the narrowed proposal that was applied and names the original
(p2). The round file lists the ids the reply
reused (mapped onto existing elements) and what the host dropped before the
proposal, with reasons. A reused element leaves no operation and an empty
round leaves no proposal, so without the round file the two rounds cannot be
told apart. The summary reports: ids reused (from the round file), host drops
(under the host's name), operations by kind and collection, the shape matches
of H18, the operations GO2 refused with their verdicts, and the elements
added. A round with no proposal has a summary whose operation counts are
zero.

## 3. Dependencies and artifact homes

| Phase | Needs | Homes it changes |
|---|---|---|
| GO1 | nothing; reviewed-vocabulary-growth VG2 not started | `src/gnd/model/_parsing.py`, `src/gnd/evolve/cli_service.py`, `src/gnd/evolve/service.py` (three scope openings), a new `tests/test_go1_evolve_parse_once.py`, `docs/release-notes.md`, `dev/components/` |
| GO2 | D1 and D2 ruled; reviewed-vocabulary-growth VG2 and VG4 merged on `main` (H21) (p1) | `src/gnd/evolve/service.py`, `src/gnd/evolve/models.py`, `src/gnd/evolve/cli_service.py`, the evolution contract's preview section, a new `tests/test_go2_operation_outcomes.py`, `tests/test_evolve_additive_policy.py`, `docs/release-notes.md` |
| GO3 | GO2 merged into the branch; D5 ruled | `src/gnd/discover/output.py` or a new module beside it, `src/gnd/evolve/models.py` (the origin field, p2), a new `tests/test_go3_narrowed_proposal.py`, the evolution contract, `docs/release-notes.md` |
| GO4 | D3 ruled; VG2 and VG5 of reviewed-vocabulary-growth merged on `main` (H21) (p1) | `unattended-growth.md`, `tests/test_unattended_growth_guidance.py`, the packaged growth example if its replies restate a reused element |
| GO5 | GO2 merged into the branch; D4 ruled; VG2 and VG5 merged on `main`, because GO5 edits `unattended-growth.md` (p1) | `src/gnd/evolve/` (one new module), the evolution contract, `unattended-growth.md`, a new `tests/test_go5_round_summary.py`, `docs/release-notes.md`, `notes/issue-replies.md` |

Order: GO1, then GO2, GO3 and GO5 in that order; GO4 after its ruling once
VG2 and VG5 are merged on `main` (p1). The graph is acyclic. GO1 needs no ruling beyond the plan gate and is
the first ready phase. GO2 to GO5 are outlines until GO2's spec is approved.

Other writers. reviewed-vocabulary-growth (H21) is the one milestone that
shares source and guidance files with this one. Its plan and the roadmap give
the order: VG1, then GO1, then VG2–VG5, then GO2–GO5. VG1 and GO1 share only
the append-only homes `docs/release-notes.md` and `dev/components/`, where
the branch that merges second merges `main` in and regenerates the index
(p1). If GO1 merges by its own pull request ahead of the rest (D6), GO2
starts from a `main` that holds VG2–VG5. GO1's own pull request is binding,
not optional (D6): the reviewed-vocabulary-growth plan starts VG2 from a
`main` that holds GO1, so a single pull request holding GO1 and GO2 would
wait on VG2 while VG2 waits on it. The graph is acyclic under that rule
(p2). Before each phase starts, this
session fetches `origin/main`, checks the start condition above and sends
"READY <phase>" to the coordinating session, which owns the cross-milestone
order; a phase whose condition is unmet stops and is reported (p1). Start condition: `main` at `78934ee3` or later;
`main` moved there from `548b9a1d` while this plan was written, by merges that
changed planning files and six skill scripts dev-tools delivers, and nothing
under `src`, `tests` or `docs`.

Fixtures. GO1 builds its models with the helpers of
`tests/test_unattended_model_growth_acceptance.py` and
`tests/test_unattended_growth_guidance.py`, as the #228 measurement did. GO2,
GO3 and GO5 use the proposals of `tests/test_evolve_additive_policy.py` and
the unattended acceptance replay.

## 4. Phases

| Phase | Criteria | Inherited residuals |
|---|---|---|
| GO1 | **GO1-C1** one `gnd evolve apply` parses at most 3 times and one `preview` at most 2, the same number at two model sizes and for a YAML and a `.json` workspace model; with the scope switched off the counts are 22 and 6 (p2). **GO1-C2** for every case of the focused evolve lane, and for an include root, a `.json` model, a YAML model with a value JSON cannot spell, a policy refusal and a D-12 refusal: preview bytes, pending state, record, published model, messages and exits are identical with the scope on and off. **GO1-C3** no remembered document differs when the scope closes from what the parser built, checked by the scope's verify mode across the whole GO1 lane (p2). **GO1-C4** a model file changed between preview and apply is refused as today, and a second command in the same process parses again. **GO1-C5** at 604 object types `apply` with the scope costs at most 0.6 of `apply` with it switched off, measured on one machine and recorded (the prototype measured 0.31, H6); its test is marked `slow`, which the default lane excludes (p1). **GO1-C6** the #228 table is measured again at the phase head and recorded beside the base figures. **Which gate is which:** C1 to C4 read no clock and are the required regression gates; C5 and C6 are recorded measurements, and a C5 ratio over 0.6 is a failed criterion reported in the record, not a red lane (p1), and it stops GO1 for a ruling before its pull request (p2) | none |
| GO2 | **GO2-C1** a proposal of four operations, one of which the candidate validation refuses at a locatable element: no preview is written, the outcome report names all four: one `refused-by-validation` and three `unassessed` naming D-12 and the policy as not run, or `admitted` where the GO2 spec runs those gates over the parsed candidate; the exit is the one today's refusal gives (p1, p2). **GO2-C2** one case per verdict word (`admitted`, `refused-by-policy`, `refused-by-validation`, `refused-by-d12`, `dropped-with`, `unassessed`), each reachable with a committed fixture, plus a proposal with two faults in two operations that names both or names the second `unassessed` as the spec rules (p1). **GO2-C3** a proposal admitted today, previewed without outcomes, gives a byte-identical preview with the same `proposal_sha256` and `preview_sha256`; with outcomes, every row is `admitted` and every other field is unchanged apart from `preview_sha256` (p1). **GO2-C4** no outcome row carries a constraint or sample value; the disclosure tests hold it. **GO2-C5** `apply` refuses an outcome report given in place of a preview (p1). **GO2-C6** a preview that carries `operation_outcomes` applies with exit 0, and the same preview with one outcome row edited is refused as stale (p2). **GO2-C7** in the GO2-C1 report, an operation no later gate reached is `unassessed` with the gates named (p2) | H11's unread half |
| GO3 | **GO3-C1** from the GO2-C1 outcome report, one call returns a proposal of the three operations not refused, replayed over the report's before model; it previews and applies, exit 0, or its preview names the fault the first pass masked (p2). **GO3-C2** a constraint on a dropped fact type is dropped with it and named. **GO3-C3** on a second fixture, an admitted preview with a policy refusal: the narrowed proposal has its own `proposal_id` and names its origin, and an original proposal without the origin field keeps its bytes (p2). Narrowing writes nothing, so before the narrowed proposal is applied the original preview behaves exactly as today; after the narrowed proposal is applied, applying the original preview is refused as a stale model, as any stale preview is (p1). **GO3-C4** a proposal with no operation `admitted` or `unassessed` returns no proposal and says so (p2) | none |
| GO4 | **GO4-C1** "The reply shape" states the rule and shows it in the example. **GO4-C2** a guard test fails when the sentence is removed. **GO4-C3** the packaged growth example's replies follow the rule, or change in this phase | none |
| GO5 | **GO5-C1** three rounds of the unattended acceptance replay each produce a summary whose counts add up to the operations proposed; a committed round with a known mix (one admitted, one `refused-by-policy`, one `dropped-with`, one host drop, one reused id, one shape match) gives each bucket the count the fixture was built with (p2). **GO5-C1b** an admitted round previewed and not applied reports 0 added; a narrowed-then-applied round reports the narrowed proposal's additions (p2). **GO5-C2** two rounds with no proposal, whose round files differ only in that one lists reused ids, give different summaries; the empty one reports zero in every count (p1). **GO5-C3** the host's own drops, given as a file, appear under the host's name and a malformed file is refused. **GO5-C4** the two replies are drafted and name what is on `main` and what is not released | H19 |

Each phase also runs the structure and inventory guards,
`uv run ruff check src tests tools`, an independent review of its diff that
carries the pattern-matched-solutions claim of `project.md`, a refactoring
review and its record.

## 5. Documentation, skill and compatibility surfaces

- **One home each (R0.6).** The reply rule goes in "The reply shape"; the
  preview's new fields and the narrowed proposal go in the evolution
  contract; the summary's fields go in the evolution contract and
  `unattended-growth.md` cites them.
- **Packaged skills.** `gnd-model-from-text` and `gnd-model-evolve` reference
  files change in GO2 to GO5; their manifests are held by
  `tests/test_packaged_skills.py`, in the guard block.
- **Release notes.** One entry per phase under the unreleased heading.
- **Compatibility.** GO1 changes no output. GO2 adds an optional preview
  field, omitted when unset, and a separate outcome report; no schema version
  moves and a preview without outcomes keeps its bytes (p1). A consumer that
  reads `policy_issues` reads the same rows. GO3 and GO5 add surfaces and change none. GO4 changes a page
  and, if D3 is ruled (a), what the packaged example's replies contain.
- **Issue replies.** The close drafts them; the owner posts them.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A remembered parse hides a file that changed between two reads | R0.5: the key is the sha256 of the bytes each caller already holds, so changed bytes are parsed again; GO1-C4 |
| A caller writes into the shared document and a later caller reads the change | GO1-C3 compares every remembered document at scope close with its form at build, over every case of GO1-C2. A copy per caller is not the control: it costs more than the parse it saves (H7) |
| A remembered refusal is replayed with another caller's wording | a failed parse is not remembered (§2) |
| The scope leaks into another command or thread | a context variable, reset on exit (H22); GO1-C4's second command |
| A time bound passes or fails with the machine | the required gates count parses and compare bytes; the one timed criterion (GO1-C5) is a ratio of two runs, recorded outside the focused lane (p1) |
| A `.json` caller receives a document the YAML fallback built | the key carries the suffix test (R0.5); a GO1 case parses YAML-flow `{` bytes as `.yaml` and then requests them as `.json` (p1) |
| An outcome report is applied as a preview | a distinct type that `apply` refuses (GO2-C5) (p1) |
| A per-operation outcome leaks a value into the preview | R0.4 and GO2-C4 |
| A verdict word with no fixture that reaches it | GO2-C2: one case per word, walked from the verdict table and not from the code |
| A narrowed proposal is mistaken for the reviewed one | GO3-C3: its own `proposal_id`, its origin named, and the original preview stale |
| The summary's counts are fitted to the acceptance replay | GO5-C2's two discriminating rounds; the diff review's pattern-matched claim |
| Two milestones edit `evolve/service.py` and `unattended-growth.md` at once | one writer at a time, in the roadmap's order (§3, H21) |

## 7. Out of scope

- A round that validates only what changed. #228 names it as a larger
  request; after GO1 a round still costs time in proportion to the model
  (H6: 9.95 s for `apply` at 2,404 object types).
- `gnd check` cost in the number of object types
  ([#221](https://github.com/vasiloglou/gnd-public/issues/221),
  reviewed-vocabulary-growth VG1).
- Partial application in `apply` (R0.1).
- The host's own rule that a fact type needs a constraint or an open
  question. GND reports and narrows; the host decides.
- The empty replies of one grower (#227): the reporter has not confirmed the
  cause.
- Starting growth from a reviewed vocabulary (#222) and the sources a new
  constraint may carry (#218): reviewed-vocabulary-growth.
- Release, tag and publication.
- The stale lines of `project.md` (H24): owner policy, outside a phase.
  The whole-repository ruff run is green (H24) (p2).

## 8. Execution, approval and review protocol

- The owner delegated `auto=true` for this milestone only on 2026-11-23
  ("they should both start with /process-milestone auto"). Plan, spec and
  close rulings are delegated rulings, recorded as such; merge, release and
  publication stay with the owner (p1).
- Plan review and close review: the full maintained GND panel, ruled by the
  owner (D7, "Full panel, both"). Convergence follows the bounded rules; the
  budget is two rounds, and round 1 blocked, so r3 has a second round (p1).
- The plan gate is recorded in `001-plan-gate.md` once the owner rules D1–D9
  or amends them.
- Each phase: spec, owner gate, code, focused gates, one independent
  reviewer over the diff (D8), refactoring review, record, commit.
- One pull request from the topic branch to `main`, or two if GO1 merges
  ahead of the rest (D6). Merge stays with the owner. Before the pull
  request, `python3 scripts/components_index.py changed --base origin/main --strict`
  exits 0.

## 9. Per-phase verification

| Phase | Focused lane | Expected |
|---|---|---|
| GO1 | `uv run pytest -q tests/test_go1_evolve_parse_once.py tests/test_evolve_additive_policy.py tests/test_evolve_source_document.py tests/test_evolve_loading.py tests/test_mc3_evolution.py tests/test_unattended_model_growth_acceptance.py --tb=short` | exit 0 |
| GO2 | `uv run pytest -q tests/test_go2_operation_outcomes.py tests/test_evolve_additive_policy.py tests/test_evolve_loading.py tests/test_evolve_source_document.py tests/test_evolve_population_check.py tests/test_evolve_shape_matches.py tests/test_mc3_evolution.py tests/test_unattended_model_growth_acceptance.py --tb=short` (p1) | exit 0 |
| GO3 | `uv run pytest -q tests/test_go3_narrowed_proposal.py tests/test_go2_operation_outcomes.py tests/test_evolve_additive_policy.py --tb=short` | exit 0 |
| GO4 | `uv run pytest -q tests/test_unattended_growth_guidance.py tests/test_growth_example.py --tb=short` | exit 0 |
| GO5 | `uv run pytest -q tests/test_go5_round_summary.py tests/test_go2_operation_outcomes.py tests/test_unattended_model_growth_acceptance.py tests/test_unattended_growth_guidance.py --tb=short` | exit 0 |
| all | the structure and inventory guard block of `project.md`, `uv run ruff check src tests tools` and `uv run ruff check` (H24) | exit 0 |

The lanes name files that exist at `548b9a1d`, plus one new file per phase.
Affected consumers are read again at each spec and may be widened there. No
broad lane (`-m "evidence or census"`) is selected.

## 10. Owner decisions and open questions

All rows are proposals until the plan gate rules them.

| ID | Question | Proposed |
|---|---|---|
| D1 | GO2: how far "an outcome for every operation" goes. (a) Policy issues plus the candidate-validation and D-12 refusals, each tied to its operation where the gate can locate the element, collected in one pass, with `admitted` meaning no refusal found in this pass. (b) Policy issues only, as today, with the first other refusal named | (a). A refusal the gate cannot locate stays a whole-proposal refusal and every operation is `unassessed` (p1) |
| D2 | GO2: where the outcomes live. (a) An optional `operation_outcomes` field in the preview, omitted when unset, with no schema version move, and a separate outcome report for a candidate that does not validate. (b) Reuse `policy_issues` with new cells | (a). `policy_issues` keeps its meaning and its consumers (p1) |
| D3 | GO4: what a reply carries for a reused fact type. (a) Its id only; rows for it go against the existing id when the document has new ones. (b) The full element, as replies do today | (a). It is the two-thirds cut #227 measured |
| D4 | GO5: who computes the summary. (a) GND, from the proposal and the preview, with the host's own drops as an input file. (b) A log format in the document that the host fills alone | (a) |
| D5 | GO3: the surface. (a) A library function beside `candidate_document`. (b) A `gnd evolve` subcommand that writes the narrowed proposal | (a) until a host asks for the command |
| D6 | Whether GO1 ships alone, by its own pull request, before the rest | Yes, and binding (p2): ruling no makes a cycle with VG2 (§3). It needs no ruling beyond the plan gate, shares no file with VG1, and the roadmap places it before VG2 |
| D7 | Plan review and close review instrument | **Ruled by the owner, 2026-11-23: "Full panel, both"** — the full maintained GND panel (`gnd-review-panel`) for plan and close review |
| D8 | Phase diff reviewer | **Ruled by the owner, 2026-11-23: "Review helper, both"** — the review helper (`.claude/skills/process-phase/scripts/review_tool.py`, subject `phase`), one reviewer in a different tool |
| D9 | The loader's own double parse (H9): `load_model` parses every model twice, in every command | Out of GO1 as planned; decided in the GO1 spec (GO1-D4). It is a two-line change in `model/__init__.py` that halves `gnd validate` at size, and it touches every command, so it is the owner's call whether it rides with GO1 or is a maintenance pass of its own |

Open questions carried into the specs: GO2, the exit and wording of each
whole-proposal refusal (H11), whether an operation's dependents are computed
from locators or from the candidate, which faults one pass can collect, and
the outcome report's fields and file name (p1); GO3, whether the narrowed
proposal keeps the original operation ids; GO5, the summary's schema and
whether it is a file `apply` writes or a command's output.

## 11. Close amendments (2026-11-23)

Made at the milestone close under the delegated ruling (auto=true) of
`001-plan-gate.md`; the r4 text above is kept as it was approved.

| ID | Amends | Amendment | Raised in |
|---|---|---|---|
| A1 | §10 D3 reading (a), "rows for it go against the existing id when the document has new ones" | Refuted: the additive policy refuses a changed sample row on an existing fact type (`fact_types.modify`). A reply names an existing element by id only, and rows for an existing fact type are an `open_questions` entry; "Acting on a shape match" says the same for a reused fact type | `notes/phase-GO4-spec.md` r2 and §14; `005-phase-GO4.md`; close review (codex, `go4-orphaned-subtype`) for the example |
| A2 | §4 GO5-C1, "a committed round with a known mix (one admitted, one `refused-by-policy`, one `dropped-with`, one host drop, one reused id, one shape match)" | The known-mix round has one admitted operation more and no `dropped-with` row: a `dropped-with` row needs a refused addition, the additive policy refuses no element addition, and every other refusal writes no preview and so no shape matches. `dropped-with` is counted in its own case over an outcome report | `notes/phase-GO5-spec.md` §13.1; `006-phase-GO5.md`; checked by the close review against `src/gnd/evolve/policy.py` |
| A3 | §4 GO5-C2, "the empty one reports zero in every count" | Unchanged; the code now meets it: a round with no proposal reports `outcomes` `{}` and `shape_matches` `0` (it reported `null`) | close review (codex, `go5-empty-counts`) |
