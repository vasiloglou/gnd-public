# Report output fidelity

**Status: r2, proposed; decisions ruled, plan not yet approved.** The owner
ruled RF-D0 and D1-D6 "as proposed" on 2026-11-07 (section 10). That is a
ruling on those decisions, not approval of the plan: no plan-gate record
exists, and the plan gate ("Approve r2?") is still open. RF-D0 selects one
Codex review over r2; it has not run as of this revision (its status is
recorded below when it does). `auto=false`.

Two issues that the `rule-check-followups` plan split out by owner ruling
(FD1, FD2 in [that plan](../../rule-check-followups/notes/rule-check-followups-plan.md)):

- **Issue 111**: the model digest is a Python `repr()`, which a caller outside
  GND cannot reproduce.
- **Issue 112**: `gnd check --format text` prints projected JSON, not verdict
  lines, for models with an active redaction policy or temporal terms.

Both are about what a report or an identity *says to someone who is not the
checker*. Neither changes a verdict, a band or an exit code.

## Completion predicates

The milestone is complete when, on main after merge:

1. `gnd check`, `gnd validate`, `gnd transition` (full and plan) and the
   export verification route, with `--format text`, print verdict lines (the
   plain snapshot report's layout) for a model with an active redaction policy
   or temporal terms, with and without `--unredacted`, rendered **from the
   projected tree only**; a canary secret in a population never appears
   (ROF1, ROF2; issue 112).
2. A caller outside GND can recompute a model's identity: a normative
   canonical-JSON definition has one home, a shipped producer prints the
   canonical document and its digest, and a differential test proves the
   producer's digest equals an independent re-implementation of the definition
   in the test file (ROF3; issue 111).
3. Every comparison site that today accepts a supplied model digest accepts
   the legacy identity **and** the canonical one, through one helper; no
   recorded digest is rewritten, and every pre-milestone digest-bound artifact
   still verifies (ROF4; issue 111).
4. The owner has ruled whether, and in which report versions, reports emit the
   canonical identity (D3); if the ruling is "emit", ROF5 is specified and
   delivered, otherwise ROF5 is withdrawn with the reason recorded.
5. Each phase has an approved spec, a record with verbatim focused-gate output
   and one independent reviewer; the close record disposes every open question
   and closes issues 111 and 112 (or states what remains of 111 if D3 defers
   emission).

## 0. Binding design rules

Inherited from rule-check-followups §0, restated:

1. **Frozen variants.** No existing report's bytes change; no recorded digest
   changes meaning. A verifier may accept more, never less.
2. **Measure, don't assert.** Every claim about a leak, a digest or a
   compatibility cost is reproduced before it is planned against; every fix
   has a regression observed red first. (project.md design rule 6.)
3. **One home.** The text renderer lives in `output.py`; the canonical-identity
   definition has one normative home (project.md design rule 5) and one
   implementation in `values.py`; consumers call it, never re-implement it
   (the "canonical-form helper re-implemented at a second site" trap).
4. **One walk over N consumers.** The N digest-comparison sites are served by
   one accepting helper, not N edits (project.md design rule 4).
5. **No leak.** Text for a declaration-bearing route is rendered from the
   already-projected tree, never from the unprojected `CheckReport`
   (`output.py:113`'s stated reason). A canary test pins it.
6. **Stop rule (size).** A phase pauses for the owner past 1.5 times its
   estimate.

## 1. Scope, sources and authority

Probes at main `12daa5b7` (2026-11-07), read-only.

| Issue | Observed |
|---|---|
| 112, redaction | `gnd check src/gnd/examples/disclosure/model.orm.yaml …/population.json --format text` prints `REDACTION applied: has_email.email` then one line of JSON (`schema_version` 9). `--unredacted` prints `REDACTION unredacted: …` then JSON. With `--rule-ids` the same route prints the JSON of the `check:rule-ids-unsupported` refusal (exit 3), so "with or without `--rule-ids`" holds. Reproduced. |
| 112, temporal | `tests/fixtures/rc1-rule-ids/models/temporal.orm.yaml` prints `REDACTION applied: ` (an empty coordinate list, a header for a policy that does not exist) then JSON at `schema_version` 11. Reproduced on an ill-formed population; a valid temporal population is part of ROF1's corpus. |
| 112, why | `checking_service._project_result` projects whenever `policy.active or (uses_temporal and kind in {check, transition, plan})` (`checking_service.py:648`); the commands then take `"redaction" in payload` and call `_print_projected_text` (`commands/checking.py:111, 218, 289`; `export/verification_service.py:220`), which prints the header, any transition `STEP` lines, then `render_json(payload)` (`output.py:113-130`). The verdict-line renderer `_print_report` takes the unprojected `CheckReport` (`output.py:~230`). |
| 112, safety property | The projected tree already carries the redaction: a failing verdict's `message` is `[REDACTED INSTANCE DETAIL]` and `offending_facts` is `[{"redacted": true, "roles": […]}]` (`redaction.py:577-649`). A renderer over the projected tree inherits that. |
| 112, pins | 4 files under `tests/fixtures/rf1-pins/goldens/sem-check/` (the dispatch and release example models, both temporal: stdout is `REDACTION applied: ` plus JSON) and `tests/fixtures/public-emitter21/answers.json` (`exact_text_prefixes`) record the JSON-as-text bytes. Changing the text changes those goldens. |
| 111, definition | `values._model_digest` is `sha256(repr(model.model_dump(exclude={warnings, operations, reference_populations})))` (`values.py:179-192`). For a model with `reference_populations` it already returns `reference_model_digest`, a canonical-JSON digest over `{identity_version: 1, model, reference_populations}` (`values.py:201-215`). `transition.operations_digest` beside it is already canonical JSON "for exactly this reason" (`transition.py:94-111`). project.md names the class: "An interchange field defined in Python-only terms". |
| 111, stability | The digest is stable across `PYTHONHASHSEED` (2 seeds, same value), so the defect is reproducibility by a non-Python caller and exposure to Python/pydantic `repr` changes, not in-process flakiness. Python 3.11.15, pydantic 2.13.4. |
| 111, consumers | Cross-process comparisons of a supplied model digest: `transition.verify_digests` (`transition:model-digest-mismatch`), `admission_validation` (two sites), `assurance/transport.py:115`, `coverage.py:689`, `export/pyrel_rules.py:1609` (plans embed `MODEL_DIGEST = '…'`), `witness/io.py`, `export/souffle_runtime.py:513`, `measure/service.py:170` and `measure/report.py:218` (sidecars via `synth.provenance.validated_model_sha256`), `model/__init__.py:627` (in-process). In-process only: `Population._validated_model_digest` (`population.py:205`). Distinct things that share the word and are **not** this digest: `batch.py` and `conformance/currency.py` (raw file bytes). |
| 111, recorded values | Script over `git ls-files` (2026-11-07): 371 model files, 306 load, 273 distinct digests; **167 tracked files record at least one of 58 model digests** (140 under `tests/fixtures`, 15 under `src/gnd/examples/approvals` (shipped `steps.json` pins and recordings), 12 historical `.gnd-planning` evidence files). An undercount: it misses models built inside tests and reference-population digests. |
| 111, feasibility | Canonical JSON over the same `model_dump` (via the existing `values.canonical` walk and `artifacts.canonical_json_bytes`): **total on all 306 loadable models** (0 refusals), and a bijection with the legacy digest on that set (273 classes both ways). Totality over hostile input is not shown; ROF3 owns it. |

Authority: the owner's request (2026-11-07); issues 111 and 112; FD1, FD2 of
rule-check-followups.

## 2. Contract proposal and product behavior

### Issue 112

- One text renderer for a check payload, fed **rows** (mappings): verdicts,
  derivations, counts, coverage, issues, warnings. The plain route adapts its
  `CheckReport` into the same rows and calls it, so the plain and projected
  layouts cannot drift (rule 4). The plain snapshot text stays **byte
  identical** (full-suite goldens).
- The `REDACTION <mode>: <coordinates>` header stays for a route that has
  declarations. For the temporal-only route (no declarations) the header is
  not printed (D2).
- Remedy and `--rule-ids` lines are not rendered for projected routes:
  `--rule-ids` is refused there, so the text of the refusal is an `ERROR` line
  from the payload's `issues`.
- Transition (full and plan), `--admission` and the export verification route
  follow in ROF2 with the same renderer.

### Issue 111, identity

- **Identity version 2** (proposed name; D4): `sha256` over
  `canonical_json_bytes({"identity_version": 2, "model": canonical(model_dump
  minus the same excluded fields), "reference_populations": sorted
  declarations})`. This is the shape `reference_model_digest` already uses
  (version 1), extended to every model; for a model without reference
  populations the declaration list is `[]`.
- The legacy identity stays exactly as it is, named **legacy-repr**. For a
  model with `reference_populations` the legacy function already returns the
  version-1 canonical digest; that value keeps its meaning.
- **Normative home** (rule 3): a new subsection of
  `src/gnd/skills/gnd-orm-core/references/representation-format.md` beside "What
  `population._model_digest` covers (A8)", which every other text cites. The
  empty case, key ordering, number and date handling and the refusal of
  non-string keys (`transition:operations-digest-unrepresentable`) are stated
  there.
- **Shipped producer** (project.md: "a shipped producer"): the canonical
  document and its digest are printed by an existing station command; the
  exact surface (`gnd validate --trace` line, a new flag, or a new
  subcommand) is an ROF3 spec decision (D5) because a trace line moves the
  `validate --trace` goldens.

### Issue 111, compatibility and migration (the story)

1. **No recorded value is rewritten and none changes meaning.** A digest
   string is `sha256:<64 hex>` with no version marker, so the identity cannot
   be told from the string. The verifier therefore computes **both** and
   accepts a supplied digest equal to either. A collision between the two is
   cryptographically negligible, and the helper reports *which* identity
   matched.
2. **Every existing report keeps the legacy digest**, in every existing
   version (rule 1). Report schemas are closed (`additionalProperties:
   false`); the canonical identity cannot appear in a frozen version.
   Consequence, stated plainly: after ROF3 and ROF4 a caller can *author* a
   pin (a `steps.json`, a sidecar, a plan) with the canonical identity and
   have GND accept it, but a caller comparing a *report's* `model_digest` to
   their own computed value still sees the legacy one until D3 rules on
   emission.
3. **Emission needs a report version.** Ruling D3 decides among: (a) no
   emission in this milestone (ROF5 withdrawn; issue 111 closes on "a caller
   can recompute and GND accepts it", with the report-side gap recorded);
   (b) a new report version per live ladder (7, 9, 11, 15 and the wrapped
   12/14 forms) carrying the canonical identity — a large wire change that
   gets its own spec; (c) a single additive successor shape. The plan
   recommends (a) now and re-asks after ROF4 has measured the cost.
4. **Shipped artifacts.** The 15 shipped `src/gnd/examples/approvals/**`
   files keep their legacy pins and must still verify (T-ship). ROF4 adds one
   shipped example pinned with the canonical identity, so both are exercised
   by the package's own tests.
5. **Historical records are bound to old bytes.** The 12 `.gnd-planning`
   evidence files and every phase record quoting a digest are not edited.
6. **Retirement of the legacy identity** is not in this milestone. It would
   be a separately approved later phase with its own trigger (the pattern of
   RF-D5), and it is the only step that could invalidate a user's recorded
   pin.
7. **In-process markers** (`Population._validated_model_digest`) keep the
   legacy function: they never cross a process boundary (project.md allows
   it), and changing them buys a cost (a canonical walk per validation) with
   no benefit. ROF3 measures the cost of the new function under a
   time-bound test (design rule 2) before any caller adopts it.
8. **Failure mode of the new function.** Unlike `repr`, the canonical walk is
   not total (a non-string key or an unrepresentable value is refused). The
   verifier must therefore **not** turn that refusal into a mismatch: a model
   the canonical identity cannot represent matches only by the legacy
   identity, and says so (ROF3 hostile-input cases; ROF4 case).

## 3. Dependencies and artifact homes

```
ROF1 ──> ROF2 ─────────────┐
                           ├──> close
ROF3 ──> ROF4 ──> ROF5? ───┘
```

The 112 chain and the 111 chain are independent and may run in either order.
ROF5 is conditional on D3 and cannot supply a prerequisite to the close
(optional work).

| Artifact | Home |
|---|---|
| text renderer, adapters | `src/gnd/output.py` (component `infra.text_output`); callers `commands/checking.py`, `export/verification_service.py` |
| projected header | `src/gnd/redaction.py` `render_text_header` |
| canonical identity | `src/gnd/values.py` (`model_identity`, `model_identity_document`); `src/gnd/artifacts.py` (`canonical_json_bytes`, reused) |
| accepting helper | `src/gnd/values.py` or `src/gnd/transition.py` (ROF4 spec chooses; one home) |
| normative text | `src/gnd/skills/gnd-orm-core/references/representation-format.md`, `docs/reference/formats.md` cites it |
| producer | decided in ROF3 (D5) |

## 4. Phases, deliverables, named criteria

### ROF1: projected text for `check` and `validate` (issue 112; about 120 source, 250 test lines)
- ROF1-C1: for a redaction-bearing model and for a temporal model,
  `check --format text` and `validate --format text` (with and without
  `--unredacted`, with and without `--rule-ids`) print verdict lines; no
  JSON line; exit codes unchanged.
- ROF1-C2: leak canary: a secret value in a population appears in no line of
  any text output of a redaction-bearing model in `applied` mode; it does
  appear (as today) in `--unredacted` JSON-path-equivalent lines only where
  the unprojected report already prints values.
- ROF1-C3: plain snapshot text is byte-identical (goldens), and the plain and
  projected routes share one row renderer (source-order assertion that
  `_print_report` calls it).
- ROF1-C4: the committed text goldens that pinned JSON-as-text are replaced
  by a list of changed files, written **before** code (rule 1), each with its
  new bytes derived from the report, not from the implementation.

### ROF2: projected text for the remaining routes (issue 112; about 80 source, 150 test lines)
- ROF2-C1: `transition` (full and plan), `check --admission`, and the export
  verification route print their usual text for projected payloads; the
  existing `STEP` derived-change summary is kept, not duplicated.
- ROF2-C2: the ROF1 canary extended to those routes.
- ROF2-C3: `validate --trace` on a redaction-bearing model keeps its trace
  block (today printed before `_print_projected_text`).

### ROF3: canonical model identity (issue 111; about 120 source, 220 test lines)
- ROF3-C1: `model_identity(model, version)` and the canonical document,
  defined in the normative home; an independent re-implementation in the test
  file (JSON dump with sorted keys, no whitespace, over the same document)
  yields the same digest on every tracked loadable model (306).
- ROF3-C2: hostile-input cases: a non-string mapping key refused, not
  coerced; an unrepresentable value refused; deep nesting; the empty case
  (`reference_populations` absent and `[]`).
- ROF3-C3: time-bound test of the new function over a model near the input
  cap (design rule 2); legacy `_model_digest` unchanged byte for byte (the
  306-model digest list pinned).
- ROF3-C4: the producer prints the document and digest; a subprocess test
  recomputes the digest with `hashlib` only.

### ROF4: accept both identities (issue 111; about 150 source, 300 test lines)
- ROF4-C1: one helper `model_identity_matches(supplied, model)` (returns which
  version matched or `None`); every site in section 1 "consumers" calls it
  (source scan: no remaining `!= …model_digest` / `!= transition_model_identity`
  comparison outside the helper).
- ROF4-C2: for each site, three cases: legacy pin accepted; canonical pin
  accepted; a wrong pin refused with a message naming both expected values.
- ROF4-C3: all 167 recorded files verify unchanged (T-ship; full suite).
- ROF4-C4: documentation: `docs/reference/formats.md`,
  `docs/guides/data-and-transitions.md`, the `steps.schema.json` description
  and the gnd-orm-core `representation-format.md` row say "either identity".

### ROF5: emit the canonical identity in reports (issue 111; blocked on D3)
Outline only. Unblocks when D3 rules (b) or (c). Nothing is estimated.

### Close
Close record; question sweep; full suite against the merge-base record.

## 5. Documentation, skill and compatibility surfaces

`representation-format.md` (normative identity text, ROF3; the "Three digests,
three bases" table, ROF4), `docs/reference/formats.md`,
`docs/guides/data-and-transitions.md`, `steps.schema.json` description (both
copies, held identical by `tests/test_schema_sync.py`). The `gnd-orm-core`
skill reference changes, so the packaged skill's twin-sync guards run. No
change to station skill procedure text beyond the digest sentence.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A recorded digest stops verifying (the headline risk of 111) | accept-both (section 2.1); T-ship over the 167 files; legacy retirement excluded |
| A leak through the new text path | render from the projected tree only; canary tests per route; no import of the unprojected report into the projected renderer (source assertion) |
| Plain text bytes move | the plain route adapts into the shared renderer; goldens byte-identical |
| The canonical walk refuses a model the legacy accepted | section 2.8; hostile-input cases; matched by legacy only, never reported as a mismatch |
| Canonical identity costs more than `repr` | ROF3-C3 time-bound test before any caller adopts it; in-process markers keep legacy |
| Two normative homes for the identity | one home in `representation-format.md`; docs cite it |
| The text goldens are pins, not noise | listed before code; derived from the report (ROF1-C4) |

## 7. Out of scope

Retiring the legacy identity; changing any existing report's bytes; new
report versions unless D3 rules otherwise; changing redaction policy or what
is redacted; `--format json` output; the batch and conformance file digests
(raw bytes, already reproducible); the rule-check-followups issues
(113-117, 119).

## 8. Execution, approval and review protocol

`auto=false`. Each phase: spec, owner gate, implement, focused gate, one
independent reviewer in a different tool (Codex), refactoring review, record,
commit on a `claude/…` topic branch, PR. Merge is the owner's. Plan-review bar
is the maintained panel (project.md); RF-D0 asks the owner which instrument
reviews this plan. The 111 chain's ROF4 changes security-relevant comparison
code and the 112 chain is a leak surface: both ask for the owner's
independent reviewer, not an author self-review.

## 9. Per-phase verification story

| Phase | Focused gate (exact files in each spec) | Affected consumers |
|---|---|---|
| ROF1 | new ROF1 tests + `tests/test_rf1_helper_pins.py tests/test_public_emitter21_controls.py tests/test_public_redaction_reports.py tests/test_public_report_redaction_metadata.py` | CLI text golden pins |
| ROF2 | new ROF2 tests + `tests/test_public_transition_walks.py tests/test_public_transition_trace.py tests/test_public_emitter_trust_controls.py` and the export verification CLI tests | text consumers |
| ROF3 | new ROF3 tests + `tests/test_model_v2.py tests/test_reference_population_corpus.py tests/test_rf1_helper_pins.py` | every digest consumer (unchanged) |
| ROF4 | new ROF4 tests + `tests/test_public_transition_contract.py tests/test_coverage_payload.py tests/test_witness_composition.py tests/test_public_v71_witness_corpus.py tests/test_public_measure_corpus.py` and the pyrel-plan suites | all comparison sites |
| ROF5 | withdrawn or specified after D3 | report consumers |
| close | full suite vs the merge-base record (main `12daa5b7`) on beast-3 | — |

Commands are unresolved until each spec lists its files; the full-suite
merge-base run on beast-3 precedes the first code change.

## 10. Owner decisions and open questions

| ID | Question | Proposal |
|---|---|---|
| RF-D0 | Review this plan before the gate, and with which instrument? | one reviewer (Codex), as for rule-check-followups; the maintained panel is the project's bar for plan review, so the plan says plainly that one reviewer is one reviewer **Ruled (o, 2026-11-07): as proposed** ("Approve as proposed", answering "How do you rule on RF-D0 and D1–D6 in the plan?"). |
| D1 | Phase order | 112 chain first (smaller, no wire risk), then 111 **Ruled (o, 2026-11-07): as proposed** ("Approve as proposed", answering "How do you rule on RF-D0 and D1–D6 in the plan?"). |
| D2 | Temporal-only route (no redaction declaration): print the `REDACTION applied:` header with an empty list, or omit it? | omit: it describes a policy that does not exist. Costs a text byte change on a route that already prints JSON, so no recorded text changes beyond ROF1-C4's list **Ruled (o, 2026-11-07): as proposed** ("Approve as proposed", answering "How do you rule on RF-D0 and D1–D6 in the plan?"). |
| D3 | Does this milestone emit the canonical identity in reports? | (a) no: accept-both and the producer close issue 111's core; revisit after ROF4. (b)/(c) cost a report version across the ladder, a separate spec and likely a milestone of its own **Ruled (o, 2026-11-07): as proposed** ("Approve as proposed", answering "How do you rule on RF-D0 and D1–D6 in the plan?"). |
| D4 | Name and shape of the new identity | `identity_version: 2` over the version-1 envelope extended to all models; legacy named `legacy-repr`. Alternative: a different envelope for plain models, which costs a second canonical shape **Ruled (o, 2026-11-07): as proposed** ("Approve as proposed", answering "How do you rule on RF-D0 and D1–D6 in the plan?"). |
| D5 | The shipped producer surface | decided in the ROF3 spec; options are an extra `validate --trace` line (moves the trace goldens), a flag, a subcommand **Ruled (o, 2026-11-07): as proposed**, i.e. deferred to the ROF3 spec ("Approve as proposed", answering "How do you rule on RF-D0 and D1–D6 in the plan?"). |
| D6 | Index review | `components_index.py review` printed 180 leads in 10 groups ("a place to look, not a finding") and names `output.py` among them. The plan does not rely on the index for the renderer's boundaries beyond component ids; the owner may call for the index's Review mode **Ruled (o, 2026-11-07): as proposed** ("Approve as proposed", answering "How do you rule on RF-D0 and D1–D6 in the plan?"). |
