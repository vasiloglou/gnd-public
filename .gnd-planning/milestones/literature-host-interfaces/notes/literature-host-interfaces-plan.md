# Literature host interfaces · plan r6, amended at close

**Status at close, 2026-11-23 (close A4): r6 was approved by the owner at
the plan gate (`001-plan-gate.md`, sha256 `2dc760e5…1528`) and executed;
this file is r6 with the close amendments of §11, which the milestone close
record (`006-milestone-close.md`) binds. The paragraph below is r6's status
at the gate, kept as it was:** Status: r6 draft, 2026-11-23. Not approved; r6's own bytes are not
reviewed. The owner selected the full GND review panel (D14, ruled `(o)`),
and it ran twice. The first round read r4 (sha256
`6cadaa9134585b348d53ef50ef5c35638a3b0bb20c7c36726ac53039ac357cb6`): four of
six reviewers succeeded, all asking for revision, with twelve ranked fixes
([r4 record](../../../reviews/literature-host-interfaces-r4-panel/README.md)).
r5 applied them, tagged `(p1)`. The second round read r5 (sha256
`c1a832378a2f303cdf1be8884ea61e745eca7f22e4fab19a449761d62b082c9b`): five of
six succeeded, one approving and four asking for revision, with seven ranked
fixes ([r5 record](../../../reviews/literature-host-interfaces-r5-panel/README.md)).
r6 applies those, tagged `(p2)`. §11 maps every fix of both rounds to its
sites. The convergence rules allow no third panel round. The owner's rulings on D6, D9 and D10 (2026-11-22, r3) and on D14 and
D17 (2026-11-23, r4 and r5) are tagged `(o)`. r2 to r4 were never committed.
No plan-gate record exists. The owner gates the plan before any spec is
approved and before any code.

This plan covers [#216](https://github.com/vasiloglou/gnd-public/issues/216)
and [#215](https://github.com/vasiloglou/gnd-public/issues/215). It delivers
the interface half of the "host-scale reading and extraction" carryover from
the [literature-depth close](../../literature-depth/016-milestone-close.md).
The run over a separately selected corpus and provider budget stays carried
with the literature-identity follow-up, as that close assigned it.

**Provenance.** Outline r1 is the previous bytes of this file (sha256
`abefb05f7fa7c19d068182eeeb557efea36bbc89d555647d98ec350b1017bea0`, commit
`0cf94434`, merged in PR 219). Its phase IDs LH1–LH4 and decisions D1–D3 are
kept. Its reviews, `.gnd-planning/reviews/pr-219-r2/` and `pr-219-panel/`,
read the roadmap outline, not these bytes. The r4 panel's opinion covers r4's
bytes only, and the r5 panel's covers r5's; no sentence new in r6 carries a
review opinion. Every code citation was re-read on 2026-11-22 at `4ad0d216`,
and those r5 and r6 add or correct on 2026-11-23 at the same commit;
`src/gnd/examples/literature/` is unchanged since `0f39c392`, where the outline
cited it. The outline wrote the two module paths without `src/gnd/`; they are
`src/gnd/examples/literature/reading.py` and
`src/gnd/examples/literature/assertion_admission.py`. Below, `reading.py`,
`assertion_admission.py` and `depth.py` mean the files in that folder.

## Goal and completion predicates

A host with its own corpus and its own model calls the two literature examples
as library functions instead of reimplementing them. The examples stay
examples: neither is promoted to stable CLI (both issues say so).

- **LH1.** `reading.py` has a public producer protocol. `run()` drives the six
  stages with a caller's producer over a caller's input root: its own
  documents, its own reading model with its own includes, no saved responses
  and no producer pin. Each of the fixture-only steps runs on caller data or
  is recorded as skipped. The run has a byte budget per document as well as
  the global one, and its caps are parameters. The responses and review
  receipts a live run produces are retained in its run folder.
- **LH2.** `replay()` re-derives a live LH1 run from its run folder and the
  caller's input root with zero producer calls and zero reviewer calls. It
  takes every setting from the run, and refuses a changed response, receipt or
  input.
- **LH3.** `assertion_admission.py` admits assertions of a caller-named entity
  in a caller's model. An assertion is identified by its own handle `(o)`.
  Every fact row attached to an admitted assertion is kept, whatever its fact
  type, together with the facts of the entities reached from it `(o)`. Absent
  optional facts are simply absent. An include root is admitted.
- **LH4.** Which values make a supported assertion admissible is caller data.
  A supported assertion that fails those rules has a status of its own. The
  target cap is a parameter.

The milestone is closed when each phase has its record and the close record
cites green focused lanes for LH1–LH4, the structure and inventory guards,
the whole-repository `uv run ruff check`, as `project.md` requires `(p1)`,
the replies drafted for #216 and #215, and the close review. Baseline, measured 2026-11-22 at `4ad0d216`
with gnd 0.4.0:
`uv run pytest -q tests/test_ld3_reading_workflow.py tests/test_ld4_revision.py
tests/test_ld5_verdict.py tests/test_li4_assertions.py tests/test_li5_lineage.py
--tb=short` gave `90 passed in 166.21s`; `uv run ruff check src tests tools`
exits 0. The whole-repository `uv run ruff check` exited 1 at `4ad0d216`,
with all 198 findings in the scripts delivered from dev-tools (H25). The owner
had them fixed upstream: dev-tools PR 34, merged as `a29562a`. After
`devtools/sync.py apply` from that commit, the whole-repository lint exits 0
and the gate-guard and scaffold tests pass (measured 2026-11-23). The re-sync
is committed with this plan, so LH1 starts from a `main` where the whole
repository lints clean `(p1)`: the start condition in §3 is that commit, not
`4ad0d216` `(p2)`.

## 0. Binding design rules

- **R0.1 Formats stay.** The stage record (`stage-N.json`), the attempt rows
  and their three outcomes, and the coverage rows with their eight states are
  unchanged; #216 says they work as they are. `literature-rebind/1` belongs to
  `interop.py` and is not touched.
- **R0.2 Packaged bytes stay.** With no new argument, the three packaged
  reading run configurations (`full`, `--scenario unavailable` and
  `--budget-bytes 0`; `SCENARIOS` itself has two values, `reading.py:38`)
  `(p1)` and the packaged admission write the bytes they write today. The comparison goes through `tests/support/recorded_version.py`,
  because the reading run retains two fidelity reports that carry
  `gnd_version` (H11).
- **R0.3 Example status stays.** Public here means named in the example's
  README and covered by tests. No `gnd` subcommand is added, and the two
  module command lines keep every argument they have.
- **R0.4 One loop, one walk.** Reading: the caller route and the packaged
  route run the same stage loop; the packaged constants become default data
  for it, not a second copy of it (standing rule 4). Admission `(p1)`: the
  D10 ruling keeps the packaged model, whose `assertion` objectifies a fact
  type, out of the generic projection, so admission has two projections, the
  packaged one as it is today and the generic attached-and-followed one. They
  share everything else, each in one home: the snapshot and the
  `gnd judgments check` route (`_judgments`, `_verify_report_inputs`), the
  mapping from a target's verdicts to a support reason (the target half of
  `_support`), the admission-rule evaluator of LH4, and the record writer and
  publication. The packaged projection gains no feature of the generic one;
  it stops at the packaged shape, as it does today.
- **R0.5 A setting is retained evidence.** Every argument that shapes a caller
  run is written into the run. Replay reads settings from the run, never from
  its caller.
- **R0.6 Skipped is not passed.** A step the caller did not supply is recorded
  with the status `skipped`. No report presents it as qualified, as measured
  or as zero.
- **R0.7 The stable commands stay the judges.** `gnd extract`, `verify`,
  `check`, `fidelity` and `judgments check` are invoked as today. Neither
  example re-implements one of their checks or widens one of their caps.
- **R0.8 A parameter has a ceiling.** Each cap that becomes a parameter has a
  hard maximum fixed in its spec, and a time-bound test at that maximum
  (standing rule 2).

The project's six standing rules
(`.codex/skills/process-phase/references/project.md`) bind every phase; each
spec discharges them by name.

## 1. Scope, sources and authority

Harvested obligations. "Observed" means re-read or run on 2026-11-22 at
`4ad0d216`; "inherited" means claimed by a source and not re-measured;
"proposed" means new in this plan.

| # | Source | Obligation | Kind | Phase |
|---|---|---|---|---|
| H1 | #216 "Problem" | `run()` (`reading.py:562`) builds `SavedProducer(inputs.responses)` at `:566`; only the private `_evaluate(..., producer=)` at `:445` takes another | observed | LH1 |
| H2 | `reading.py`, `ReadingInputs` | the root is bound to saved responses by the pin (`:72-75`, "saved producer table differs from its pin") and by the roster check (`:113`, "saved response roster differs"), and to the packaged vocabulary (`:135`) | observed | LH1 |
| H3 | `reading.py`, stage loop | the fixture bindings: the outline's six, the producer label and, found by the panel, the calibration path's literals `(p1)`: the `unavailable` scenario names `study-methods` (`:448`); `_calibrate` names that section, the fact `approximation` (`:317`) and `CALIBRATION_FACTS` (`:42`, `:311-327`), and the absence floor is the literal `[2, 2]` (`:372`); and the calibration path also fixes its renderer label `authored-public-fixture` (`:300`), its case folders `run-methods` and `held-back-predicate` (`:320`, `:323`) and its count of two cases (`:335`) `(p1)`; `_combined` adds `LABEL` to every population (`:48`, `:247`); `_public_results` needs `conflict.json`, `conflict.txt`, a `subject_label` fact with exactly two labels and exits 1 from `verify` and `check` (`:395-407`); `absence_status` needs the predicate `alternative_integrator` (`:373`); `_review_attempts` needs a `reviews.json` receipt bound to each accepted response's facts digest (`:198-209`); the extraction sidecar names its producer `saved-public-fixture` (`:264`) | observed | LH1 |
| H4 | `reading.py`, producer boundary | `produce(stage, section)` gets two names and no source bytes (`:156`); the loop reads a `calls` attribute from the producer (`:457`). `_inspect` accepts exactly three outcomes, `accepted`, `empty`, `refused` (`:185`). The outline's "and the existing others" was wrong: the other five coverage states are decided by the loop before or without a call | observed | LH1 |
| H5 | `depth.py:21-30`, `:56`, `:61` | three fixture-scale limits the outline did not list: every input file, source documents included, is read with a 128 KiB cap (`INPUT_LIMIT`); every JSON input is capped at 1 MiB; every `gnd` route has 30 seconds and 1 MiB of output (`PROCESS_LIMITS`). A caller document over 128 KiB refuses at read. Replay reads the run's own files through the same `_read` (`reading.py:414-437`), and each `payload-N.json` embeds every response of its stage (`:190-192`), so two 64 KiB responses already make a payload replay cannot read `(p1)` | observed | LH1 (D4) |
| H6 | `reading.py:27-30`, `:86`, `:263`, `:298`, `:384-387` | file names are fixed: the eleven `INPUTS` are all required; a source's path must be `<id>.txt`; the model must be `reading.orm.json` with one include named `vocabulary.orm.json`; the artifact names `reading.orm.projection.schema.json` and `reading.orm.applicable.json` are literals. Probe: `gnd extract caller.orm.json` on a renamed copy exits 0 and names its artifacts `caller.orm.*` | observed | LH1 |
| H7 | `reading.py:386`; include-root-routes IR2 | the loop runs `gnd extract` on the reading model after the producer has answered. `gnd extract` refuses a temporal model. A caller's reading model must be one `gnd extract` accepts, and a refusal there should cost no producer call | observed | LH1 |
| H8 | `reading.py:473-478`, `:172-174` | the global "stop" is a reason computed after the loop; the only thing that ends reading early is the byte budget, which omits sections. "Per document" has no present meaning | observed | LH1 (D6) |
| H9 | #216 "Request" | producer protocol, live and replayable; stop rule per document; roster cap and byte budget as parameters; `replay()` against a caller root | inherited | LH1, LH2 |
| H10 | consumers of `reading.py` | `revision.py:171` calls `reading.replay(retained, fixture=inputs, vocabulary_fixture=inputs)` and `:62-64` reads `reading.FIXTURE` and `reading.DEPTH_FIXTURE`; `assurance_report.py:760` calls `replay(run_dir)` with no root and `:725` caps coverage rows at 128 `(p1)`; the tests patch `SavedProducer.produce`, `_read` (on the replay path, `test_ld3_reading_workflow.py:238-246`) and `_public_results`, call `_inspect` directly with six positional arguments and read `producer.calls` (`:153-165`) `(p1)`, and read `ROSTER_LIMIT` | observed | LH1, LH2 |
| H11 | probe, 2026-11-22 | no test pins the bytes of a packaged reading run. `fidelity-high.json` and `fidelity-low.json` carry `gnd_version`. Evidence digests at gnd 0.4.0: `full` `ee67e13c…fd1c`, `--scenario unavailable` `d4010f94…6ddf`, `--budget-bytes 0` `7dcf43ec…a071` | observed | LH1 |
| H12 | #215 "Problem" | `project()` (`assertion_admission.py:100`) accepts three fact types only (`:105`); every role is a mandatory non-empty string (`:45-52`); absence is a sentinel (`:30`, `:84`); identity is (work, passage) (`:55-63`, `:111-113`); the admissible pair is hard-coded (`:122`); `MAX_TARGETS` (`:29`) bounds rows (`:46`) and targets (`:67`) | observed | LH3, LH4 |
| H13 | `src/gnd/judgments.py:115`, `:121` | `gnd judgments check` itself refuses a policy with more than 1,024 targets or more than 4,096 judge-target pairs. A `MAX_TARGETS` parameter can lower the example's bound; it cannot admit more than 1,024 targets in one call. The reporter's gold set has about 3,600 claims | observed | LH4 (D11) |
| H14 | `src/gnd/model/_validation.py:942`, `model_verbalization.py:124`, `evolve/service.py:577` | `objectified_as` is read by validation, verbalization and evolve only. The checker does not join an objectified fact's row to the entity that objectifies it; that link is the model author's convention | observed | LH3 (D10) |
| H15 | `assertion_admission.py:146-148`, `:188-191`; include-root-routes plan §1 H11 | the admission snapshot copies one model file, so an include root fails its include read. `gnd judgments check` accepts include roots since IR1 | observed | LH3 |
| H16 | `assertion_admission.py:35-39`, `:83-88`, `:118`, `:132` | checks that belong to the packaged shape only: the five closed tag vocabularies, the rule that `conditional` needs a condition and `unqualified` forbids one, and the fixed `covers` list | observed | LH3 |
| H17 | consumer of `assertion_admission.py` | `lineage_run.py:33` imports `ABSENT_CONDITIONS`, `PASSAGE`, `ROLES`, `SCHEMA`, `STATEMENT`, `WORK` and `admit`; `:203` calls `admit` with six positional arguments; `:254` compares the marker's `schema` with `SCHEMA` | observed | LH3, LH4 |
| H18 | probe, 2026-11-22 | packaged admission output at `4ad0d216`: `admitted.population.json` `6e45b93d…39e1`, `raw.population.json` `ea96584c…0173`, `judgment-report.json` `3726a424…c43c`, `admission.json` `6d262018…f16f`. Statement indices 3, 4, 5 and 6 pass `semantic-support` and fail `positive-own-findings` with `negated`, `baseline-comparison`, `speculation`, `cites-other-work` | observed | LH3, LH4 |
| H19 | #215, measured shape | 98 % of claims share a passage; about half have other than one actor and one object; 9 % have several conditions; 44 % carry a quantity | inherited | LH3 fixture |
| H20 | literature-depth close, row "Host-scale reading and extraction" | interface half only; the corpus and provider-budget run stays with the literature-identity follow-up | inherited | LH1, LH2 |
| H21 | PROJECT.md, roadmap after 0.4.0 | third milestone; independent of the two export milestones, both merged | inherited | all |
| H22 | component index, `scripts/components_index.py` | `examples.literature_reading` and `examples.literature_assertion_admission` exist, both `canonical`; the capabilities below adapt them and add no component. `review` lists seven literature entries whose descriptions are older than their code. The index changes in the same commit as the code | observed | all |
| H23 | probe, 2026-11-22; `reading.py:283-285`, `:393` | the loop completes only when `verify` and `check` both exit 0 on the broad and the targeted population, and admits only exits 0 and 1 from them. On a copy of the reading model, a population with one `system` fact and no `subject_label` exits 2 (`inadequate`) from both; adding one `subject_label` row gives 0 and 0. `LABEL` is what keeps the packaged model's one constrained fact type populated. A caller model with a constraint over a fact type a pass has not read yet exits 2, and the run refuses "check exited 2" | observed | LH1 (D16) |
| H24 | `docs/reference/rule-check-report.md:85-93`; `checker/_core.py:423`; `reading.py:268-271` | a checking route's exits are 0, 1, 2 and 4, with precedence 1 > 4 > 2 > 0; 4 means a must-hold rule is unchecked. `_route` refuses any exit outside the set it is given `(p1)` | observed | LH1 (D16) |
| H25 | probe, 2026-11-23; `project.md` lint gate | the whole-repository `uv run ruff check` exited 1 at `4ad0d216` with 198 findings, all in `review_tool.py`, `rules_check.py` and `handoff.py` as delivered from dev-tools (both discovery roots); `project.md` requires it to exit 0. Fixed upstream (dev-tools PR 34, `a29562a`) and re-synced; it exits 0 after the sync `(p1)` | observed | all |

Out of scope: the corpus and provider-budget run (H20); promoting either
module to stable CLI; any change to a stable command or its caps (R0.7, H13);
the assurance scorer's own 128-row cap (H10); #218, #221 and #222; release,
tag and publication.

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
| #215: polarity and attribution rules as data, with a distinct disposition | LH4 |
| #215: `MAX_TARGETS` as a parameter | LH4 |

This is a framework milestone. An experiment-claim census (`gnd coverage`)
counts claims over a domain model; it says nothing about which arguments an
example function accepts, so none is read here. The baseline is the test run
above and the probes H6, H11, H18 and H23.

## 2. Contract proposal and product behavior

Exact names and signatures are fixed in each phase spec. What follows is the
contract each spec must realise.

### LH1 — a live producer over a caller root

- **The protocol.** A producer is any object with
  `produce(call) -> dict`. `call` is a `ProducerCall`: the stage, the section
  ID, its source ID and version, its kind and span, the section's source bytes
  and their sha256, and the open questions that point at the section. The
  result is the response object the loop accepts today: `outcome` (one of
  `accepted`, `empty`, `refused`), `facts` and `proposal_keys`. The loop
  counts calls itself; a producer needs no `calls` attribute. `SavedProducer`
  is one implementation and keeps its pin and roster checks.
- **A response is untrusted input.** The loop validates each response as a
  bounded JSON value of the declared shape before it uses it (standing
  rule 1). A response that fails, or a producer that raises, refuses the run
  with nothing written (D7).
- **A caller root.** A root that holds `profile.json` is a caller root. The
  profile names the reading model file and its include files, and supplies
  what the loop takes from constants today: the facts added to every
  population, the producer's label, and the optional review, calibration,
  conflict and absence steps. A
  root without a profile is the packaged layout and keeps the packaged
  constants. A live producer over a root without a profile refuses. A
  declared calibration step takes its renderer label and the names of its two
  case folders from the profile; the packaged label, folder names and count
  of two are the packaged profile's values (H3) `(p1)`.
- **Unavailable sections `(p1)`.** On a caller root the caller names its
  unavailable sections with an argument, and the manifest records them.
  `scenario="unavailable"` names the packaged section `study-methods`, so
  over a caller root it refuses before any producer call.
- **Steps.** A step the profile does not declare is recorded `skipped`
  (R0.6). A declared step runs on the caller's files. A reviewer, if given,
  is called once per accepted response and must return a `supported` receipt;
  any other decision refuses the run, as a stale review does today. The
  reviewer is a check, not a filter (D3).
- **Order.** Inputs are validated, then the reading model is extracted, then
  the first producer call is made (H7, standing rule 3).
- **Route exits.** On a caller root the exits of `verify` and `check` over
  the broad and the targeted population are recorded as observed, 0, 1, 2 or
  4, and the run completes; any other exit refuses (D16, H23, H24) `(p1)`.
  The report shows the exits; it never calls a population verified. The
  packaged root keeps requiring 0.
- **Per document.** `document_budget` bounds the bytes read from each source.
  It follows the global budget's rule `(p1)`: a section that does not fit in
  what is left of its document's budget is omitted, and a later, smaller
  section of the same document is still read (`reading.py:172-174`). Other
  documents continue. The report states a stop reason for each source, with
  the three reasons the global stop has. A document whose required questions
  are resolved still gets its other scheduled reads (D6, ruled `(o)`). It is
  a `run()` argument beside the global budget, with the largest-budget limit
  as its ceiling (D4).
- **Limits.** The roster cap, the largest budget, the per-file input cap, the
  response cap, the route timeout, the route output cap and the retained-file
  cap are fields of one limits argument, each with a default equal to
  today's constant or today's effective bound (the retained-file cap of a
  `/2` run excepted, below), and a hard ceiling (D4, R0.8) `(p1)`. A JSON file is decoded under the cap it was read with, so a raised
  input cap also raises the decode cap of that input; the fixed 1 MiB decode
  cap of `depth.py:61` no longer applies to the reading loop.
- **Retained files `(p1)`.** The packaged `/1` run keeps today's path: no
  bound before the first call, and replay reads its files through
  `reading._read(folder, name)` as today, so its bytes do not move (R0.2)
  `(p2)`. A `/2` run, before its first producer call, computes an upper bound
  for each file it will retain from the roster alone: a file that carries
  responses or receipts holds at most the sections eligible for it times the
  response cap plus a per-attempt overhead the spec fixes; any other file is
  bounded by the roster cap times a per-row size the spec fixes `(p2)`. With
  no retained-file cap given, the run's cap is the largest of those bounds,
  and never less than 128 KiB; the run refuses if that exceeds the
  retained-file ceiling, or if the bounds exceed a cap the caller gave
  `(p2)`. The manifest records the cap, and replay of a `/2` run reads under
  it through a reader local to `reading.py` `(p2)`. A run that completes can
  therefore always be read back.
- **What a caller run writes.** The captured response table and the captured
  review receipts are artifacts of the run. Its manifest has format
  `literature-reading-run/2` and records the settings, the unavailable
  sections and each step's status (D5, R0.5). A packaged run with no new
  argument writes `literature-reading-run/1`, byte for byte (R0.2).
- In LH1, `replay()` refuses a `/2` run by name; LH2 replaces that refusal.

### LH2 — replay of a live run

- `replay(folder, fixture=ROOT)` reads the manifest, takes the settings and
  step statuses from it, reads the caller root through its profile, reads
  the run's files under the recorded retained-file cap `(p1)`, and
  re-derives every artifact. It has no producer, reviewer, budget or limits
  argument.
- It refuses a response table, receipt table, stage, payload or input whose
  bytes differ from what the manifest binds, and a manifest whose settings
  exceed a hard ceiling.
- A manifest binds a run internally. `replay(..., expected_evidence_sha256=)`
  compares the run with the digest `run()` returned, which the host keeps
  outside the folder; without it a consistently rewritten folder replays. The
  README says so. For the packaged run the independent producer pin keeps
  that role.
- `score_reading_coverage` gains the same `fixture` argument and passes it
  through. Its 128-row cap stays (out of scope).

### LH3 — admission over a caller's assertion entity

- **Shape.** The caller passes an assertion shape: the ID of an entity type
  in its model, and the entity types to follow from it (D17, ruled). With no shape,
  `admit()` runs the packaged shape and writes today's bytes.
- **Attached facts.** A fact type is attached when one of its roles is played
  by the assertion entity. A row belongs to the assertion its role value
  names. Every attached row of an admitted assertion is kept, except a row
  that also names an assertion that was not admitted: the one limit stated
  under "Followed facts", which holds for attached and followed rows alike
  `(p2)`.
- **Followed facts `(o)`.** Admission follows links outward (D9, ruled). When
  a kept row names an instance of a followed entity type, the rows of the
  fact types that entity plays a role in are kept for that instance too, and
  the walk continues from them. Example: a claim's row names quantity `Q7`;
  `Q7`'s value row and unit row are kept. The walk stops at the shape's
  list (D17, ruled): an instance of an entity type the shape does not list is
  kept as a value in the row that names it, and its own facts are not copied.
  With an empty list nothing is followed. One limit holds beside the list: a
  row that names an assertion which was not admitted is never kept, whichever
  route reaches it.
- **Coverage.** The admitted population's `covers` lists the attached fact
  types and the fact types of the followed entity types. A fact type outside
  both is not copied.
- **Identity `(o)`.** The assertion's own handle is its identity (D10,
  ruled). The model's preferred uniqueness is enforced by the stable
  commands, not re-implemented (R0.7). No rule links an objectified fact
  type's rows to the entity (H14): a shape that names an entity which
  objectifies a fact type refuses, naming the objectification. The packaged
  model's `assertion` is such an entity, so the packaged example stays on the
  packaged path.
- **Judged unit.** Policy targets are rows attached directly to the
  assertion. An assertion is supported when at least one of its rows is a
  target and every target among its rows is admitted by
  `gnd judgments check` (D8). A target on any other row refuses.
- **Optional facts.** An assertion with no row in an attached fact type
  simply has none. No value is read as "absent". The tag vocabularies and the
  condition rule of H16 apply to the packaged shape only.
- **Row bound `(p1)`.** The generic projection bounds the rows it reads,
  attached and followed together, with its own `max_rows` argument, separate
  from the target cap (D18). The packaged projection keeps `MAX_TARGETS` as
  its row bound (`:46`), so its bytes do not move. `max_rows` without a
  shape refuses the call, since the packaged projection would not apply it
  `(p2)`.
- **Include roots.** The snapshot copies each declared include beside the
  root, and the record binds each include's sha256 (H15).
- **Record.** A call with any new argument (a shape, rules, `max_targets` or,
  with a shape, `max_rows`) writes `literature-assertion-admission/2`; the packaged call
  with none keeps `/1` (D12). A `/2` record binds the shape and the rules by
  sha256 of their canonical bytes, and records `max_targets` and `max_rows`
  `(p1)`. A call with rules and no shape is a packaged-shape `/2` call: it
  records the shape as `packaged` and `max_rows` as `null` `(p2)`.

### LH4 — admission rules as data

- **Rules.** The caller passes admission rules: an ordered list of
  requirements, each with an ID, an attached fact type, a role, the
  admissible values and, optionally, a reason for each inadmissible value.
  An assertion satisfies a requirement when it has at least one row of that
  fact type and every such row has an admissible value. Requirements are
  evaluated in order, and the first one that fails gives the reason: the
  reason declared for the offending value, else the requirement's ID `(p1)`.
- **Default rules `(p1)`.** The packaged comparison at `:122` becomes the
  default rules, evaluated by the one evaluator (R0.4): first `polarity` with
  `asserts` admissible and the reason `negated` for `negates`, then
  `attribution` with `own-finding` admissible and each other value as its own
  reason. List order keeps today's polarity-first precedence, and the
  reasons are today's strings, so the H18 stage table does not move.
- **Disposition.** In a `/2` record, a supported assertion that fails a
  requirement has status `policy-refused` and that reason; an unsupported
  one keeps `fail` (D2). The `/1` record keeps today's statuses, so it keeps
  its bytes.
- **A rule that names nothing refuses.** A requirement naming an unknown fact
  type or role refuses the call. It is never evaluated as "no row matched".
- **The packaged shape `(p2)`.** There the assertion entity plays no role in
  the fact type that carries polarity and attribution (its roles,
  `assertion_admission.py:31-34`, have no `assertion`), so "attached" does
  not apply. On the packaged shape the one fact type a requirement may
  name is `assertion_statement` (`STATEMENT`, `assertion_admission.py:21`),
  which has one row per assertion, and the default rules name it. A
  requirement naming `assertion_names_work`, `assertion_names_passage` or any
  other fact type refuses there, as an unknown fact type does.
- **Target cap.** `max_targets` is an argument from 1 to 1,024. The ceiling
  is the stable command's (H13, D11).

## 3. Dependencies and artifact homes

| Phase | Needs | Homes it changes |
|---|---|---|
| LH1 | nothing | `src/gnd/examples/literature/reading.py`, `src/gnd/examples/literature/depth.py` (one keyword on `_command` and one on `_decode`, each defaulting to today's value `(p2)`), a new `tests/test_lh1_reading_host.py`, a new `tests/fixtures/lh1-reading/` (the caller root and the recorded packaged trees), `src/gnd/examples/literature/reading_fixture/README.md`, `dev/components/` |
| LH2 | LH1 | `reading.py`, `src/gnd/examples/literature/assurance_report.py` (one pass-through argument), a new `tests/test_lh2_reading_replay.py`, the same README, `docs/literature/commands.md`, `docs/release-notes.md`, `dev/components/` |
| LH3 | nothing | `src/gnd/examples/literature/assertion_admission.py`, a new `tests/test_lh3_admission_shape.py`, a new `tests/fixtures/lh3-admission/`, `src/gnd/examples/literature/README.md`, `dev/components/` |
| LH4 | LH3 | `assertion_admission.py`, a new `tests/test_lh4_admission_rules.py`, `tests/fixtures/lh3-admission/` (rules files), the same README, `docs/literature/commands.md`, `docs/release-notes.md`, `dev/components/` |

Order: LH1, LH2, LH3, LH4, one at a time, LH1 and LH2 on the branch
`claude/literature-host-interfaces` and LH3 and LH4 on
`claude/literature-host-interfaces-admission` (close A2; r6 named the first
branch only). The graph is acyclic. The two pairs share
no source file; they run in sequence so that `docs/literature/commands.md`,
`docs/release-notes.md` and `dev/components/` have one writer at a time. Start
condition `(p2)`: `main` at the merge that lands this plan with the dev-tools
re-sync (H25). Its history holds `4ad0d216`, and so IR1, so LH3's fixture can
be an include root. The LH1 spec records that commit and that the
whole-repository `uv run ruff check` exits 0 on it.

Fixtures are test fixtures under `tests/fixtures/`, not packaged examples: a
packaged model would join the inventory in `tests/test_mc1_guards.py:365-376`
and the wheel. Each phase authors its own; no phase needs another phase's
output files.

## 4. Phases

| Phase | Criteria | Inherited residuals |
|---|---|---|
| LH1 | **LH1-C1** a test producer with no `calls` attribute drives six stages over the caller root (two sources, its own model and include, its own section and fact names, no `responses.json`, `producer-pin.json` or `reviews.json`); broad and targeted populations exit 0 from `verify` and `check`; no packaged section, fact or label name occurs in the run folder. **LH1-C2** each call's bytes equal the section's span and its sha256 equals the attempt row's; `producer_calls` equals the calls the test producer counted. **LH1-C3** the run folder holds the captured response table and the captured receipts, both bound by the manifest. **LH1-C4** with no step declared, each step's status is `skipped` and the report says `skipped`, not `unavailable` and not a number; with each step declared, it runs on the caller's files; a declared file that is missing refuses before any producer call; unavailable sections named by argument are recorded, and `scenario="unavailable"` over a caller root refuses before any producer call `(p1)`. **LH1-C5** a document budget ends one document and not the other; in the document it ends, a section after an oversized one is still read `(p1)`; each source has its stop reason; a document whose required questions are resolved early still gets its other scheduled reads (D6) `(p1)`. **LH1-C6** a lowered roster cap and budget ceiling are honoured and recorded; a raised input cap admits a 200 KiB source the default refuses; a limit above its ceiling refuses. **LH1-C7** each malformed response in the spec's list refuses with `ExampleError` and nothing written. **LH1-C8** a producer that raises refuses, naming the stage and section. **LH1-C9** the three packaged run configurations equal the trees recorded at `4ad0d216`, through the version helper `(p1)`; `test_ld3`, `test_ld4` and `test_ld5` pass unedited. **LH1-C10** each limit at its ceiling stays within the spec's time bound: inputs at each roster ceiling load, with the input cap raised as they need; a source at the input-cap ceiling, a response at the response-cap ceiling and a budget at its ceiling each run; a route that reaches the timeout refuses within the timeout plus its grace; a route whose output reaches the route-output ceiling, and a `/2` run that retains a file at the retained-file ceiling, each complete within the bound `(p2)`. The spec may let ceilings share one test if it says which and why `(p1)`. **LH1-C11** a model `gnd extract` refuses, and a live producer over a root with no profile, each refuse before any producer call. **LH1-C12** `replay()` of a `/2` run exits 3. **LH1-C13** a caller run whose broad population leaves a constrained fact type empty completes and records exit 2 for it; one whose targeted population violates a constraint completes and records exit 1; exit 4 is recorded like 2, held by a caller model whose check exits 4 or, if the spec shows no caller model can reach it, by a unit test of the exit table `(p1)`. **LH1-C14** `(p1)` `(p2)` a `/2` run whose bounds exceed a retained-file cap the caller gave refuses before any producer call; so does one whose derived cap would exceed the retained-file ceiling, held by a run at the roster and response ceilings with every section eligible; a run at the response ceiling whose eligible sections keep the bound within the ceiling completes, and each retained file reads back under the recorded cap; the LH1-C1 run, with default limits and more than one eligible section per stage, completes under the derived cap | H20 stays carried |
| LH2 | **LH2-C1** the LH1-C1 run replays from its folder and the caller root, byte-identical, with the same evidence digest and zero calls. **LH2-C2** one changed byte in the response table or in a receipt refuses; a consistently rewritten folder refuses when the expected digest is given. **LH2-C3** a run recorded with non-default limits replays with them, including the completing LH1-C14 run at the response ceiling `(p1)` `(p2)`; a manifest with a setting above its ceiling refuses. **LH2-C4** a changed source, profile, model or include refuses "stale reading input". **LH2-C5** a `/1` run replays as today; `test_ld3`, `test_ld4`, `test_ld5` pass unedited. **LH2-C6** `score_reading_coverage` scores the caller run when given its root. **LH2-C7** a manifest that claims `skipped` for a step the profile declares refuses | none |
| LH3 | **LH3-C1** a model with claims that share a passage, a claim with two actors and no object, one with three conditions and one with a quantity that is an entity with a value row and a unit row `(o)` admits; every attached row of each admitted claim is kept, with the rows of its quantity `(o)`, and no row of another claim is; `gnd check` on the admitted population exits 0. **LH3-C2** `(o)` a shape naming an entity that objectifies a fact type, the packaged `assertion` for one, exits 3 with a reason that names the objectification, and nothing is published. **LH3-C3** a claim with one admitted and one rejected target is not admitted; a claim with one admitted target and untargeted rows is, with all its rows; a claim with no target has disposition `missing`. **LH3-C4** a row attached to two assertions is kept only when both are admitted, the one exception to LH3-C1's "every attached row" `(p2)`. **LH3-C5** the model as an include root admits and the record binds each include; an include edited without a new pin exits 3 with nothing published. **LH3-C6** each refusal in the spec's list exits 3 with a value-free reason and nothing published. **LH3-C7** the value `none` in a generic-shape row is an ordinary value. **LH3-C8** the packaged call writes `admitted.population.json` and `raw.population.json` with the H18 digests and the H18 stage table; `test_li4` and `test_li5` pass unedited. **LH3-C9** 1,024 targets with attached and followed rows up to the `max_rows` ceiling project within the spec's time bound; one row over `max_rows` refuses `(p1)`; `max_rows` with no shape exits 3 with nothing published `(p2)`. **LH3-C10** `(o)` a quantity named by an admitted and by a rejected claim keeps its own rows once, and the rejected claim's row that names it is not kept; a row reached through a followed entity that names a rejected claim is not kept; an entity type the shape does not list is not followed (D17) | H15 closes here |
| LH4 | **LH4-C1** two rules files over the same inputs admit two different sets, each stated in the fixture. **LH4-C2** a supported assertion that fails a requirement has status `policy-refused`; an unsupported one has `fail`. **LH4-C3** an assertion with one admissible and one inadmissible row of the named fact type is `policy-refused`; so is one with no row of it. **LH4-C4** a lowered `max_targets` refuses a policy over it; a value above 1,024 refuses the call. **LH4-C5** a requirement naming an unknown fact type or role, a packaged-shape requirement naming `assertion_names_work` `(p2)`, and each malformed rules document in the spec's list, exit 3 with nothing published. **LH4-C6** the packaged call keeps the H18 bytes and statuses, now through the default rules and the one evaluator `(p1)`. **LH4-C7** `(p1)` a `/2` record binds the shape and rules digests and records `max_targets` and `max_rows`; changing any one changes the record; a call with rules and no shape writes `/2` with the shape `packaged` and `max_rows` `null` `(p2)` | none |

Each phase also runs the structure and inventory guards, the
whole-repository `uv run ruff check` `(p1)`, an independent review of its
diff, a refactoring review and its record.

## 5. Documentation, skill and compatibility surfaces

- **One home each.** The reading protocol, the profile, the limits and the
  `/2` manifest are described in
  `src/gnd/examples/literature/reading_fixture/README.md`, which already
  holds the stage files and the coverage states. The assertion shape, the
  admission rules and the `/2` record are described in the admission section
  of `src/gnd/examples/literature/README.md`. `docs/literature/commands.md`
  gains one short "drive it from your host" passage per example that links to
  those two homes and restates nothing normative.
- **Release notes.** One entry per pair under the unreleased heading of
  `docs/release-notes.md`, written by LH2 and LH4.
- **Skills.** No packaged skill names these functions; none changes.
- **Compatibility.** `SavedProducer.produce` takes one call object where it
  took two names; `test_ld3` patches it with a function that accepts any
  arguments. `test_ld3` also calls `_inspect` directly with six positional
  arguments and reads `SavedProducer.calls`, and patches `reading._read` on
  the replay path (H10). These stay: `_inspect` keeps its six positional
  parameters and its return shape, and every new parameter is keyword-only;
  `SavedProducer` keeps its `calls` counter, though the loop no longer needs
  one; `reading._read(folder, name)` stays the `/1` replay read path with its
  two positional parameters `(p1)`, and only a `/2` replay reads through the
  capped reader local to `reading.py` `(p2)`. `run()`, `replay()`, `admit()` and
  `project()` keep their present arguments and defaults. `/1` readers are not
  given `/2` documents by any packaged route.
- **Issue replies.** The close drafts a reply to #216 and to #215. Each says
  what was not done: the 1,024-target ceiling (H13), the corpus run (H20) and
  admission of an objectified fact type (D10).
  The owner posts them.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| The generic projection admits rows the packaged example refused | LH3-C8 and LH4-C6 pin the packaged admitted set, the stage table and the output digests |
| Dropping the saved-response pin for live runs weakens the packaged replay | the pin and roster checks stay for `SavedProducer` (existing `test_ld3` cases); LH2-C2 binds a live run by digest |
| A caller root silently gets a packaged constant | the profile is the only source of caller bindings; LH1-C1 searches the run folder for packaged names |
| A skipped step reads as a passed one | R0.6; LH1-C4 and LH2-C7 |
| A provider answer crashes the loop after spend | LH1-C7, LH1-C8; the order rule and LH1-C11 put every input and model refusal before the first call |
| A completed caller run is read as a verified extraction | D16; the report carries the route exits, the README says a completed run is not a verified one, and LH1-C13 holds a run that completes with exits 2 and 1 |
| Following outward keeps a rejected assertion's row, or grows to most of the population | the limit in §2 "Followed facts" and D17; LH3-C10 holds a shared entity, a row reached the long way round and an unlisted entity type |
| The reporter's assertion is an objectified fact type after all | LH3-C2 refuses it by name, and the #215 reply states the ruling (D10), so the mismatch is reported, not silent |
| A raised cap turns a legal input into minutes of CPU | R0.8; LH1-C10, LH3-C9 |
| A live run retains files that its own replay cannot read `(p1)` | a `/2` run bounds its files before the first call and records its cap; LH1-C14, LH2-C3 |
| The retained-file bound refuses runs that work today `(p2)` | the bound applies to `/2` runs only, and a `/2` run's default cap is derived from its own bounds; LH1-C9, LH1-C14 |
| The generic admission path drifts from the packaged one `(p1)` | R0.4 names the shared homes; LH4-C6 runs the packaged rules through the one evaluator |
| A rule quantified "any" or "every" passes on fixtures that cannot tell them apart | LH3-C3, LH3-C4 and LH4-C3 each hold the discriminating case |
| A host reads "parameter" as "no limit" for `MAX_TARGETS` | LH4-C4; the README and the #215 reply state the stable ceiling |
| A large caller vocabulary exceeds the route timeout ([#221](https://github.com/vasiloglou/gnd-public/issues/221)) | the timeout is a limit (D4); a route that times out refuses naming the route |
| LH1 is larger than one phase | its spec states the size; if the estimate passes 400 source lines the spec proposes a split at its gate, with new IDs LH1a and LH1b |
| The packaged bytes pin moves at a version bump | the comparison uses `tests/support/recorded_version.py`, with `RECORDED_AT = "0.4.0"` |

## 7. Out of scope

The corpus and provider-budget run; stable-CLI promotion of either module; a
change to `gnd judgments check`'s caps or to any stable command; batching
inside `admit()`; the assurance scorer's row cap; admission of an entity that
objectifies a fact type under a shape (D10, ruled); following an entity type
the shape does not list (D17, ruled); #218, #221, #222;
release, tag and publication.

## 8. Execution, approval and review protocol

- The plan review is held to the project's bar, the maintained GND review
  panel. The owner selected the full panel (D14, ruled `(o)` 2026-11-23); its
  first round read r4 and, at the owner's request, its second round read r5.
  The convergence rules allow two rounds at most, so r6 goes to the plan gate
  without a third `(p2)`.
- The plan gate is recorded in `001-plan-gate.md` once the owner rules, with
  the review's instrument, reviewed digest and dispositions, or the statement
  that none ran.
- Execution is `process-milestone literature-host-interfaces`, or
  `process-phase LH1 literature-host-interfaces` for one phase. `auto=true`
  needs the owner's explicit delegation for this milestone; none has been
  given (D15).
- Each phase: spec, spec gate, code, focused gates, one independent reviewer
  over the diff (D13), refactoring review, record, commit.
- Two pull requests (close A2): the reading pair (LH1, LH2) from
  `claude/literature-host-interfaces`, then the admission pair (LH3, LH4)
  from `claude/literature-host-interfaces-admission`, each to `main`. Before
  it, `python3 scripts/components_index.py changed --base origin/main
  --strict` exits 0. Merge stays with the owner.

## 9. Per-phase verification

| Phase | Focused lane | Expected |
|---|---|---|
| LH1 | `uv run pytest -q tests/test_lh1_reading_host.py tests/test_ld3_reading_workflow.py tests/test_ld4_revision.py tests/test_ld5_verdict.py tests/test_li1_assurance_report.py --tb=short` | exit 0 |
| LH2 | `uv run pytest -q tests/test_lh2_reading_replay.py tests/test_lh1_reading_host.py tests/test_ld3_reading_workflow.py tests/test_ld4_revision.py tests/test_ld5_verdict.py tests/test_li1_assurance_report.py --tb=short`, then `uv run python tools/run_tutorials.py --group literature` | exit 0 each |
| LH3 | `uv run pytest -q tests/test_lh3_admission_shape.py tests/test_li4_assertions.py tests/test_li5_lineage.py --tb=short` | exit 0 |
| LH4 | `uv run pytest -q tests/test_lh4_admission_rules.py tests/test_lh3_admission_shape.py tests/test_li4_assertions.py tests/test_li5_lineage.py --tb=short`, then `uv run python tools/run_tutorials.py --group literature` | exit 0 each |
| all | the structure and inventory guard block of `project.md`, and the whole-repository `uv run ruff check` `(p1)` | exit 0 |

Affected consumers named here are read at each spec and may be widened there.
No broad lane (`-m "evidence or census"`) is selected.

## 10. Owner decisions and open questions

D6, D9 and D10 carry the owner's ruling of 2026-11-22 `(o)`, and D14 and D17
the rulings of 2026-11-23 `(o)`. Every other row is a proposal until the plan
gate rules it. D1–D3 keep their outline IDs; D4–D16 are new in r2, D17 in r3
and D18 in r5. r6 adds none.

| ID | Question | Proposed | What the other reading costs |
|---|---|---|---|
| D1 | Where the producer protocol lives | In `reading.py`, until a second example uses it | A shared module now is a public home with one user |
| D2 | Name and reach of the LH4 disposition | `policy-refused`, in the `/2` record only; `/1` keeps `fail` | Applying it to `/1` changes the packaged record's bytes and `test_li4`'s expectations |
| D3 | The fixture-only steps on a caller root | Calibration, the conflict check and the absence scope are optional and declared in the profile; an undeclared step is `skipped`. The population label is profile data. A reviewer is optional, and a decision other than `supported` refuses the run | A reviewer that filters instead needs a ninth coverage state, which changes the row format #216 asks to keep |
| D4 | Which caps become parameters, and their ceilings | Seven limits `(p1)`: roster cap (default 128, ceiling 4,096), largest budget (1 MiB, 64 MiB), per-file input (128 KiB, 8 MiB), response (128 KiB, today's effective bound, since a response cannot exceed the 128 KiB read of `responses.json`; ceiling 1 MiB), route timeout (30 s, 600 s), route output (1 MiB, 16 MiB), retained file (for `/2` runs only `(p2)`: derived from the run's own bounds and never less than 128 KiB, today's read of a run's own files; ceiling 10 MiB, the repository's JSON read cap `gnd.input_policy.MAX_BYTES` (close A1)). The ceilings cannot all be reached together: at the 1 MiB response ceiling a retained file holds fewer than 10 eligible sections `(p2)` (close A1). A JSON file is decoded under its read cap. `document_budget` is a `run()` argument whose ceiling is the largest-budget limit | #216 names the first two only; with only those, a source over 128 KiB still refuses, a slow `gnd check` still stops the run at 30 s, and a live run can retain files its replay cannot read (H5) |
| D5 | Manifest format of a caller run | `literature-reading-run/2` for any run that uses a new argument; `/1` unchanged otherwise | Optional keys in `/1` let an older reader accept a run it cannot re-derive |
| D6 | What "the stop rule per document" means | **Ruled `(o)` 2026-11-22: as proposed.** A byte budget per source, enforced in the loop, and a stop reason per source in the report. A document whose required questions are resolved still gets its other scheduled reads | Ending a document at required coverage reads less, and changes which optional questions are answered; it could be a later switch |
| D7 | A malformed response, or a producer that raises | Refuse the run with nothing written; a host that prefers to continue returns `refused` from its own producer | Recording it as `refused` reports a transport failure as the producer's verdict |
| D8 | LH3: what is judged, and how row verdicts make an assertion's verdict | Targets are attached rows; supported means at least one target and every target admitted | "Any target admitted" admits an assertion with a rejected participant row |
| D9 | LH3: how far "hangs off" reaches | **Ruled `(o)` 2026-11-22: the other reading, follow entities outward.** Not adopted: directly attached fact types only; they form `covers`; other fact types are not copied | Following entities outward keeps a quantity entity's own facts, at the price of a reachability rule the model does not state. That rule is D17 |
| D10 | LH3: linking an objectified fact's row to its handle | **Ruled `(o)` 2026-11-22: the other reading, own handle only.** Not adopted: a link through the preferred external uniqueness, each identifying role matched to a role of the same name and object type in the objectified fact type | No rule means the objectified form is refused and only entities with their own handle are admitted, which leaves the packaged model on the old path only |
| D11 | LH4: the ceiling of `max_targets` | 1,024, the stable command's cap; a larger set is admitted in several calls the host makes | Raising `judgments.py`'s caps changes a stable command; that would be its own issue |
| D12 | LH3: the record of a shaped call | `literature-assertion-admission/2`; the packaged call keeps `/1` | One format with optional keys makes `lineage_run.py:254` accept records it was not written for |
| D13 | Phase diff reviewer | The review helper (`.claude/skills/process-phase/scripts/review_tool.py`, subject `phase`), one reviewer in a different tool | none; this is `project.md`'s default |
| D14 | Plan-review instrument | **Ruled `(o)` 2026-11-23: the full GND panel** ("full"). Its first round read r4, its second r5 | none |
| D15 | How the milestone runs | The owner selects: phase by phase with an owner gate on each spec, or `process-milestone … auto`. Ruled at the plan gate as phase by phase; superseded on 2026-11-23 by the owner's `/process-milestone literature-host-interfaces auto` (close A3) | none |
| D16 | LH1: which `verify` and `check` exits let a caller run complete | 0, 1, 2 and 4 are recorded and the run completes; the host gates on them; any other exit refuses (H24) `(p1)` | Requiring 0, as the packaged root does, refuses every run over a model with a constraint on a fact type not yet read (H23). Refusing on 1 only loses every producer call of a run whose extraction violates a constraint, which is a finding the host wants kept |
| D17 | LH3: where following stops (opened by the D9 ruling) | **Ruled `(o)` 2026-11-23: as proposed.** The shape lists the entity types to follow, for example `quantity`; an instance of any other entity type is kept as a value in the row that names it, and its own facts are not copied | Not adopted: following every entity type. It needs no list, but one admitted claim then keeps its paper, the paper's authors, their other papers and so on: most of the population, whatever was judged. With an empty list the result is the reading D9 did not adopt |
| D18 | LH3: the generic projection's row bound `(p1)` | A `max_rows` argument, default 16,384, ceiling 65,536, bounding attached and followed rows together; separate from `max_targets`. The packaged projection keeps `MAX_TARGETS` as its row bound, and `max_rows` without a shape refuses `(p2)` | Reusing `max_targets` as the row bound refuses 1,024 claims with two actors each (H19) |

The owner ruled D6, D9, D10 and D17 without waiting for the reporter. The
reply to #215 states the three LH3 rulings, so the reporter can say if their
model does not fit them: an assertion is identified by its own handle,
admission follows outward from it, and the host lists the entity types it
follows.

## 11. Rulings before the gate

### 2026-11-22, r3

Owner rulings given in the planning session, in reply to the three questions
r2 marked for the reporter. The owner's words: "d6: proposed", "d9:
alternative", "d10: own number". Prior wording is r2's.

| Tag | Site | Prior wording (r2) | Now |
|---|---|---|---|
| o | §10 D6; §2 LH1 "Per document" | proposal, "To confirm with the reporter" | ruled as proposed; no criterion changes |
| o | §10 D9; Goal LH3; §2 LH3 "Attached facts" | "The admitted population holds exactly the attached rows of admitted assertions, and its `covers` lists the attached fact types (D9)." | "Followed facts" and "Coverage" in §2; LH3-C1 widened; LH3-C10 added; D17 opened |
| o | §10 D10; Goal LH3; §2 LH3 "Identity" | "For an entity that objectifies a fact type, a row of that fact type is linked to its handle through the entity's preferred external uniqueness, role by role (D10, H14). A row that links to no handle or to two refuses." | own handle only; an objectifying entity refuses under a shape |
| o | §4 LH3-C2 | "the packaged model under a shape naming `assertion` admits exactly the statements whose target is admitted, each with its two link rows" | the refusal of an objectifying entity |
| o | §7 | "facts reachable from an assertion only through another entity (D9)" | removed; two items added for D10 and D17 |

### 2026-11-23, r4

Owner ruling on D17, the question the D9 ruling opened. Asked "the host lists
the types, or follow everything?", with the list as the proposal, the owner
answered "your auggestion", read here as "your suggestion": the proposal.
Prior wording is r3's.

| Tag | Site | Prior wording (r3) | Now |
|---|---|---|---|
| o | §10 D17 | proposal, with "follow every entity type" as the other reading | ruled as proposed |
| o | §2 LH3 "Followed facts" | "Where the walk stops is D17. One limit holds under every reading of D17" | the walk stops at the shape's list; an empty list follows nothing |
| o | §7 | "following an entity type the shape does not list (D17, if ruled as proposed)" | "(D17, ruled)" |

No criterion changed: LH3-C10 already holds an entity type the shape does not
list.

### 2026-11-23, r5: the panel's fixes

The full panel over r4 (D14) returned two blocking concerns and twelve ranked
fixes ([PANEL-REVIEW.md](../../../reviews/literature-host-interfaces-r4-panel/PANEL-REVIEW.md)).
Every cited code fact was re-checked at `4ad0d216` before a fix was written,
and each held. Every fix is applied; sites are tagged `(p1)`.

| Fix | Concern (reviewers) | Sites in r5 |
|---|---|---|
| 1 | R0.4 cannot hold for admission under the D10 ruling (Claude, blocking) | §0 R0.4 names the two projections and their shared homes; §2 LH4 "Rules" and "Default rules"; LH4-C6; §6 |
| 2 | the narrowed lint gate conflicts with `project.md` (Codex, blocking) | the owner had the dev-tools scripts fixed (dev-tools PR 34, `a29562a`) and gnd-public re-synced; the whole-repository lint is the gate in the completion predicates, §4 and §9; H25 |
| 3 | retained files can outgrow the fixed read caps (Claude) | H5; §2 LH1 "Limits" and "Retained files"; §2 LH2; D4; LH1-C14; LH2-C3; §6 |
| 4 | `gnd check` exit 4 is not covered (Claude) | H24; §2 LH1 "Route exits"; D16; LH1-C13 |
| 5 | the 64 KiB response default is not today's constant (Claude, Kimi, GLM) | D4: 128 KiB, today's effective bound |
| 6 | the per-document budget's semantics, home and ceiling, and the D6 continuation criterion (Claude, Kimi, GLM) | §2 LH1 "Per document"; D4; LH1-C5 |
| 7 | a time bound at every ceiling (Kimi) | LH1-C10 |
| 8 | the generic projection has no row bound (Claude) | §2 LH3 "Row bound"; D18 (new, proposed); LH3-C9 |
| 9 | the admission record does not bind its settings (Claude) | §2 LH3 "Record"; LH4-C7 |
| 10 | the unavailable scenario has no owner on a caller root (Claude) | §2 LH1 "Unavailable sections"; LH1-C4 |
| 11 | §5 misstates how `test_ld3` reaches the producer (Claude) | H10; §5 "Compatibility" |
| 12 | citations: H10 lines (Claude, GLM), H3 calibration literals (Claude), "three scenarios" (GLM) | H10; H3; §2 LH1 "A caller root"; R0.2; LH1-C9 |

D14 is recorded as ruled: the owner answered "full" when asked which review
the plan should get. Fix 2's direction is the owner's: asked how the plan
should handle the lint gate, the owner answered "fix the devtools script
first", then "merge pr 34" and "override and merge".

### 2026-11-23, r6: the second round's fixes

At the owner's request ("Run round two") the full panel read r5 and returned
seven ranked fixes
([PANEL-REVIEW.md](../../../reviews/literature-host-interfaces-r5-panel/PANEL-REVIEW.md)).
Every cited code fact was re-checked at `4ad0d216` before a fix was written,
and each held. The owner asked for r6 ("Write r6"). Every fix is applied;
sites are tagged `(p2)`.

| Fix | Concern (reviewers) | Sites in r6 |
|---|---|---|
| 1 | under D4's defaults the retained-file bound refuses the packaged runs (Claude, blocking); LH1-C14's run at the response and roster ceilings cannot fit the retained-file ceiling (Claude, Codex, Kimi) | §2 LH1 "Limits" and "Retained files": the bound applies to `/2` runs only, with a derived default cap; D4; LH1-C14; LH2-C3; §6 |
| 2 | §3 starts LH1 at `4ad0d216`, before the lint re-sync (Claude, Codex, GLM) | completion predicates; §3 start condition |
| 3 | LH3 keeps every attached row, but LH3-C4 drops one (Codex, blocking) | §2 LH3 "Attached facts"; LH3-C4 |
| 4 | LH1-C10 has no time bound at the route-output and retained-file ceilings (Kimi, GLM) | LH1-C10 |
| 5 | the frozen two-argument `reading._read` cannot take the recorded cap (Claude) | §2 LH1 "Retained files"; §3 LH1 row (`depth.py`); §5 "Compatibility" |
| 6 | which fact type a rule names on the packaged shape (Claude) | §2 LH4 "The packaged shape"; LH4-C5 |
| 7 | `max_rows` on a packaged-shape call bounds nothing (Claude) | §2 LH3 "Row bound" and "Record"; D18; LH3-C9; LH4-C7 |

No ruling changed. The plan gate still rules D1–D5, D7, D8, D11–D13, D15, D16
and D18.

### 2026-11-23, close amendments

Repairs the phase records named, applied at milestone close under the
owner's delegated close ruling (auto=true). Prior wording is r6's.

| Tag | Raised in | Site | Prior wording (r6) | Now |
|---|---|---|---|---|
| A1 | `003-phase-LH2.md`, refuted premise and open question Q1 | §10 D4 | "retained file (…; ceiling 64 MiB). The ceilings cannot all be reached together: at the 1 MiB response ceiling a retained file holds fewer than 64 eligible sections" | ceiling 10 MiB, `gnd.input_policy.MAX_BYTES`, which every JSON reader of the repository applies, so a larger retained file could never be read back; fewer than 10 eligible sections |
| A2 | milestone README, "Deviation from plan §8" | §8, §3 "Order" | "One pull request from `claude/literature-host-interfaces` to `main`." | two pull requests, the reading pair then the admission pair; the milestone-coordinator session relayed the owner's words "Accept the split" |
| A3 | `002-phase-LH1.md`, Gate | §10 D15 | "The owner selects: phase by phase …" with the plan gate's phase-by-phase ruling | superseded by the owner's `/process-milestone literature-host-interfaces auto` |

| A4 | close panel (`evidence/close-review/PANEL-REVIEW.md`) | the status block | "Status: r6 draft … Not approved … No plan-gate record exists" | the status at close, with r6's gate status kept |

The departures from the plan's letter below the plan level are recorded in
the phase specs' findings and phase records; `close-delta.md` is their
complete list (items 4 to 13).
