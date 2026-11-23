# LH1 spec · a live producer over a caller root

## 1. Status

**Draft, blocked, 2026-11-23 (brought to plan r6).** Implementable once the plan gate has ruled
plan decisions D1, D3, D4, D5, D7 and D16, and the owner has approved this
spec. No code may be written against it before both. D6 was ruled by the owner
on 2026-11-22, as proposed `(o)`.

## 2. Provenance

Derived from [plan r6](literature-host-interfaces-plan.md), Goal (LH1), §0,
§1 (H1–H11, H20–H25), §2 "LH1", §4 (LH1-C1 to LH1-C14) and §9. Written by
`start-milestone` in the session that wrote the plan. Of the owner's rulings
since r2 (D6, D9, D10, D14, D17), only D6 touches LH1, and it was ruled as
this spec assumed. Plan r5 answers the full panel over plan r4; the fixes
that touch LH1 are brought into this spec and tagged `(p1)`: seven limits and
a decode cap that follows the read cap (fixes 3, 5), exit 4 (fix 4), the
per-document budget's skip rule (fix 6), a time bound at each ceiling
(fix 7), unavailable sections on a caller root (fix 10), the frozen test
surface (fix 11), the calibration literals (fix 12) and the whole-repository
lint gate (fix 2). Plan r6 answers the second panel round, over r5; its
fixes that touch LH1 are tagged `(p2)`: the retained-file bound applies to
`/2` runs only, with a derived default cap (fix 1), the start commit (fix 2),
time bounds at the route-output and retained-file ceilings (fix 4), and the
frozen two-argument `_read` on the `/1` replay path (fix 5). Both panel
rounds read this spec as context only; no review has run over it. Code was read, and the probes below were run, on
2026-11-22 at `4ad0d216` with gnd 0.4.0. `reading.py` and `depth.py` mean the
files in `src/gnd/examples/literature/`.

Measurements this spec rests on:

- **P1, model names.** `gnd extract caller.orm.json --out bundle`, on a
  renamed copy of the packaged reading model beside its include, exits 0 and
  writes `bundle/caller.orm.artifacts.json` with artifacts named
  `caller.orm.*`. Its `header_template.covers` lists the model's 22 asserted
  fact types.
- **P2, route exits.** On that model, a population holding one `system` fact
  exits 2 (`inadequate`) from `verify` and from `check`; adding one
  `subject_label` row gives 0 and 0 (plan H23).
- **P3, packaged bytes.** Evidence digests of `run --out DIR`:
  `full` `ee67e13c082c340052cd37b09c77f2feb90c124b633738b8863bcd3d22b8fd1c`,
  `--scenario unavailable`
  `d4010f94712aa9bd46bf6f62f148a05f22e7f88acf9bc82d7c736d4cb9ba6ddf`,
  `--budget-bytes 0`
  `7dcf43ecab3a6c7d3a1d0b8dbe3b503a28e698fed170506469cad4820a37a071`.
- **P4, the serializer.** `canonical_json_bytes` raises `ValueError` on NaN,
  `TypeError` on a non-JSON object and `RecursionError` on deep nesting. It
  writes the integer key `1` as `"1"` without complaint.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| H1, H4 | a public protocol; the call carries the section's bytes; the loop counts calls | §6.1, §6.4; T1, T2 |
| H2 | no saved responses, pin or packaged vocabulary on a caller root | §6.2, §6.3; T1 |
| H3 | the fixture bindings, the calibration literals included `(p1)`, become profile data or optional steps | §6.2, §6.5; T4, T5 |
| H5, D4 | seven limits with ceilings; retained files readable by replay `(p1)` | §6.1, §6.3; T8, T12, T20 |
| H6 | model and include names come from the profile; artifact names derive from the model name | §6.2, §6.5; T1 |
| H7 | the model is extracted before the first producer call | §6.3; T13 |
| H8, D6 | a byte budget and a stop reason per source | §6.4; T7 |
| H10 | `revision.py`, `assurance_report.py` and the tests' patch points keep working | §6.6; T11 and the unedited `test_ld3`, `test_ld4`, `test_ld5` |
| H11, R0.2 | packaged runs keep their bytes, compared through the version helper | §6.7; T11 |
| H22 | component index entry updated in the same commit | §6.8 |
| H23, H24, D16 | route exits 0, 1, 2 and 4 recorded on a caller root `(p1)` | §6.5; T15 |
| D3 | reviewer is a check; an undeclared step is `skipped` | §6.4, §6.5; T4, T18 |
| D5 | `/2` manifest for a caller run | §6.5; T1, T8 |
| D7 | a malformed response or a raising producer refuses with nothing written | §6.4; T9, T10 |
| LH1-C1 to C14 | each criterion | §8, column "Criterion" |
| plan §5 | the protocol's one home is `reading_fixture/README.md` | §6.8 |
| plan §6, size risk | a split is proposed if the estimate passes 400 source lines | §10 |

## 4. Standing rules, bound to this phase

| Rule | Bound here |
|---|---|
| R0.1 formats stay | `stage-N.json` keys, attempt-row keys and the three outcomes, coverage rows: no key added or renamed. T1 compares the key sets with the packaged run's |
| R0.2 packaged bytes | T11 |
| R0.3 example status | `main()` gains no argument in LH1; nothing is registered in `tools/gnd_entrypoints.json` |
| R0.4 one loop | one `_evaluate`; the packaged layout is the constant `PACKAGED_PROFILE`. One row validator, `_fact_rows`, serves responses, base facts, gold, calibration and conflict facts |
| R0.5 settings retained | `settings` in the `/2` manifest (§6.5); T8 |
| R0.6 skipped is not passed | the statuses of §6.5; T4 |
| R0.7 stable commands judge | the loop reads `header_template.covers` from `gnd extract`'s own output and adds no role or type check (LH1-D3) |
| R0.8 ceilings | `LIMIT_CEILINGS` (§6.1); T8, T12 |
| 1 totality | four new consumers of untrusted input: `_profile` (file), `_response` and `_receipt` (values a caller's object returns), `ReadingLimits` validation. Each walks its input with an explicit stack and a depth of 8, refuses a non-string mapping key before serializing (P4), and refuses non-finite numbers. T8, T9, T16, T18 |
| 2 time bound | T12, at every limit's ceiling `(p1)`, the roster ones with a supersession chain of maximum length |
| 3 validation order | the order of §6.3. T6 and T13 pin it with a producer that fails the test if called |
| 4 one walk | as R0.4 |
| 5 one home | `reading_fixture/README.md`, new section "Drive it from your host". `docs/literature/commands.md` is not edited in LH1 |
| 6 measurement | P1–P4 settled the model naming, D16's framing, the pin and the key check |

## 5. Goal

`run()` in `reading.py`, called with a producer object over a root that holds
`profile.json`, writes a `literature-reading-run/2` folder and returns a
report, with every refusal raised as `ExampleError` or `ArtifactError` before
anything is written. The focused lane of plan §9 (LH1), the guard block and
the whole-repository `uv run ruff check` `(p1)` each exit 0, and the three
packaged run configurations equal their recorded trees.

## 6. Design

Reuse, from the component index (`python3 scripts/components_index.py search`):

| Capability | Searches | Found | Decision |
|---|---|---|---|
| drive the reading stages | `literature reading producer`; `saved producer replay` | `examples.literature_reading` (canonical): `_evaluate`, `_inspect`, `SavedProducer` | adapt |
| bounded file and JSON intake | `bounded read regular file strict json` | `infra.artifacts` `read_regular_bounded`; `model.anchors` `strict_json` | reuse |
| run a `gnd` route with limits | `bounded process` | `infra.bounded_process`, through `depth._command` | adapt (one keyword) |

### 6.1 New public names in `reading.py`

```python
LIMIT_CEILINGS = {"roster": 4096, "max_budget": 1 << 26, "input_bytes": 8 << 20,
                  "response_bytes": 1 << 20, "route_seconds": 600,
                  "route_output_bytes": 16 << 20, "retained_bytes": 1 << 26}

@dataclass(frozen=True)
class ReadingLimits:
    roster: int = 128            # sources, sections and questions, each
    max_budget: int = 1 << 20    # the largest `budget` a run may ask for
    input_bytes: int = 128 * 1024  # each input file, source documents included
    response_bytes: int = 128 * 1024  # one response or receipt, as canonical JSON
    route_seconds: int = 30      # each `gnd` route
    route_output_bytes: int = 1 << 20  # each `gnd` route's stdout
    retained_bytes: int | None = None  # each file of a /2 run; None derives it (§6.3 step 7) (p2)

@dataclass(frozen=True)
class ProducerCall:
    stage: str             # "broad-extraction" or "targeted-extraction"
    section: str
    source: str
    source_version: str
    kind: str              # "section", "equation" or "table"
    start: int
    end: int
    excerpt: bytes         # documents[source][start:end]
    excerpt_sha256: str
    questions: tuple[dict, ...]  # {"id", "fact", "denial"}; not superseded, pointing at the section

class Producer(Protocol):
    def produce(self, call: ProducerCall) -> dict: ...

@dataclass(frozen=True)
class ReviewCall:
    section: str
    excerpt: bytes
    excerpt_sha256: str
    facts: dict
    facts_sha256: str      # sha256 of canonical_json_bytes(facts)

class Reviewer(Protocol):
    def review(self, call: ReviewCall) -> dict: ...  # {"decision": "supported", "basis": "<text>"}

def run(out: Path, *, budget=DEFAULT_BUDGET, scenario="full", fixture: Path = FIXTURE,
        producer: Producer | None = None, reviewer: Reviewer | None = None,
        document_budget: int | None = None, unavailable: Iterable[str] | None = None,
        limits: ReadingLimits | None = None) -> dict: ...
```

Every limit is an `int`, not a `bool`, from 1 to its ceiling. Each default
is today's constant or today's effective bound `(p1)`: `ROSTER_LIMIT`,
`MAX_BUDGET` and `depth.INPUT_LIMIT`, which stay as names; the response's
128 KiB, since a response cannot exceed the 128 KiB read of `responses.json`;
the two `PROCESS_LIMITS` fields. `retained_bytes` is the exception `(p2)`:
left as `None`, a `/2` run derives it from its own bounds (§6.3 step 7), and
it is never below the 128 KiB `_read` that replay applies to a `/1` run's
files. A JSON file is decoded under the cap it was read with,
not under `depth.py`'s fixed 1 MiB.

`SavedProducer.produce` takes one `ProducerCall` where it took
`(stage, section)`. It keeps `responses` and its `calls` counter, which
`test_ld3` reads (`:164`) `(p1)`.

### 6.2 The profile

`profile.json` at the root makes it a caller root. Format
`literature-reading-profile/1`; the key set is closed and every key is
required (LH1-D2):

```json
{
  "format": "literature-reading-profile/1",
  "model": "survey.orm.json",
  "includes": ["terms.orm.json"],
  "producer_label": "host-extractor",
  "base_facts": {"paper_title": [{"paper": "paper-a", "title": "A"}]},
  "review": false,
  "calibration": null,
  "conflict": null,
  "absence": false
}
```

- `model` and each of `includes` match `[a-z][a-z0-9-]{0,63}\.orm\.json`, are
  distinct, and number at most 17 together. They are read from the root and
  placed beside each other for `gnd extract`. Artifact names are
  `<model minus ".json">.<suffix>` (P1).
- `producer_label` matches `[a-z0-9][a-z0-9._-]{0,63}`; it is the sidecar's
  `executing_model`.
- `base_facts` maps fact-type names to rows, and may be `{}`.
- `calibration` is `null` or
  `{"section": ID, "section_facts": [...], "held_back_facts": [...],
  "renderer_label": LABEL, "case_names": [A, B]}`: a targeted section with a
  span, two non-empty disjoint lists whose union equals the keys of
  `gold.json`, the label the calibration sidecars name as their renderer, and
  the two case folder names, distinct and matching `[a-z][a-z0-9-]{0,63}`
  `(p1)`. It needs `gold.json`, `calibration.json`
  and `calibration.txt`.
- `conflict` is `null` or `{"fact_type": NAME, "role": NAME}`. It needs
  `conflict.json` and `conflict.txt`; the named fact type must hold exactly
  two rows whose `role` values occur in the text, and `verify` and `check`
  must both exit 1 on them, as today.
- `absence: true` needs `calibration`, `scope.json` and `closure.json`. The
  scope's `predicate` must equal the `fact` of every scoped question, and the
  floor is every gold row recalled.

`PACKAGED_PROFILE` is the same object for a root without `profile.json`:
`reading.orm.json`, `vocabulary.orm.json` read from `vocabulary_fixture`,
`saved-public-fixture`, `{"subject_label": [LABEL]}`, review on, calibration
on `study-methods` with `["approximation"]` and `["alternative_integrator"]`,
renderer `authored-public-fixture` and cases `run-methods` and
`held-back-predicate`, conflict on `subject_label` / `label`, absence on. It
also carries what a caller cannot set: the route exits that let a run
complete, `(0,)` for the packaged layout and `(0, 1, 2, 4)` for a caller root
(D16, H24) `(p1)`.

### 6.3 Branches and order

| Root | New arguments | Result |
|---|---|---|
| no `profile.json` | none | `/1` run, today's bytes |
| no `profile.json` | any of `producer`, `reviewer`, `document_budget`, `unavailable`, `limits` | refuses "caller arguments need profile.json" (LH1-D1) |
| `profile.json` | `producer=None` | saved route: `responses.json` and `producer-pin.json` required and checked as today; `/2` run |
| `profile.json` | a producer | live route; `/2` run |
| `profile.json` | `scenario` other than `"full"` | refuses; a caller names sections in `unavailable` |

Review: `review: true` takes receipts from `reviewer` if given, else from the
root's `reviews.json`; with neither it refuses. `review: false` with a
reviewer refuses.

Order, each step refusing before the next starts:

1. `limits`, `budget`, `document_budget` (at most `limits.max_budget`) and
   `out`.
2. `profile.json`.
3. `roster.json`, the sources, sections and questions, as today, and
   `unavailable` against the sections.
4. The model, its includes and every file a declared step needs.
5. The saved responses and pin, and the saved reviews, where the branch
   needs them.
6. `gnd extract` on the model; `base_facts` names against its `covers`.
7. The retained-file bound, `/2` runs only `(p1)` `(p2)`: each payload that
   carries attempts is bounded by the roster sections eligible for its stage
   times `response_bytes` plus 1 KiB per attempt row; the response and
   receipt tables by every eligible section, the same way; every other
   retained file by `limits.roster` times 1 KiB per row. With
   `retained_bytes` `None`, the run's cap is the largest bound, at least
   128 KiB; the run refuses if that exceeds `LIMIT_CEILINGS["retained_bytes"]`,
   or if a bound exceeds a `retained_bytes` the caller gave. The manifest
   records the cap. A run that passes can be read back by replay (LH1-C14).
   The packaged `/1` run skips this step and keeps today's bytes.
8. The first producer call.

`ReadingInputs.__init__` gains keyword-only `limits=None` and `live=False`
and performs steps 2 to 5. The packaged layout keeps reading through the
module-level `_read(root, name)`, which `test_ld3` and `test_ld4` patch; a
caller root reads through the same `read_regular_bounded` with
`limits.input_bytes`. Replay of a `/1` run keeps calling
`reading._read(folder, name)` with two positional arguments, which
`test_ld3:240-244` patches; a `/2` run's files are read in LH2 through
`_read_run_file(folder, name, max_bytes)`, local to `reading.py` `(p2)`.

### 6.4 The loop

- `_inspect` builds one `ProducerCall` per attempted section from an index of
  questions by section built once, counts the call, and validates the result
  with `_response`: a JSON object with `outcome`, `facts` and `proposal_keys`;
  `facts` maps names in `covers` to lists of rows; a row maps role names to a
  string, integer, finite float or boolean; `facts` is non-empty exactly when
  the outcome is `accepted`; each proposal key is one of the roster's
  `revisit_keys`. The validated value is serialized once, capped at
  `response_bytes`, and that parsed copy is what the loop uses and retains.
- An exception from `produce` or `review` is raised as
  `ExampleError("producer failed at <stage> <section>")` or
  `"reviewer failed at <section>"`, with the original as its cause.
- A section is omitted when its length exceeds the remaining global budget,
  as today, or the remaining `document_budget` of its source. Either way the
  loop goes on to the next section, as `:172-174` does today, so a smaller
  section after an omitted one is still read `(p1)`.
- `_inspect` keeps its six positional parameters and its return shape, which
  `test_ld3` calls directly (`:160`); the per-document remainder and the
  limits are keyword-only `(p1)`.
- After the loop, each source gets a stop reason by the global rule applied
  to its own questions and sections: `required-coverage-completed`, else
  `budget-exhausted` if one of its sections was omitted, else
  `available-evidence-exhausted`. A source with no required question is
  `required-coverage-completed`, as the global rule is with none (LH1-D4).
- The required-question walk (`:463-469`) resolves each supersession chain
  once.
- `_evaluate`'s check of `producer.calls` (`:457`) is removed: the loop owns
  the count.

### 6.5 What a caller run writes

Manifest:

```json
{"format": "literature-reading-run/2", "scenario": "full", "budget_bytes": 4096,
 "inputs": {"<name>": "<sha256>"}, "artifacts": {"<name>": "<sha256>"},
 "settings": {"document_budget_bytes": null, "unavailable": [],
              "limits": {"roster": 128, "max_budget": 1048576, "input_bytes": 131072,
                         "response_bytes": 131072, "route_seconds": 30,
                         "route_output_bytes": 1048576, "retained_bytes": 524288},
              "producer": "live", "reviewer": "none"},
 "steps": {"review": "skipped", "calibration": "skipped", "conflict": "skipped",
           "absence": "skipped"}}
```

`producer` is `live` or `saved`; `reviewer` is `live`, `saved` or `none`;
each step is `ran` or `skipped`. `retained_bytes` is the cap the run used,
derived when the caller gave none (512 KiB here, as an example) `(p2)`.

Artifacts: the six stage and six payload files, `coverage.json`,
`broad.population.json`, `targeted.population.json` and
`producer-output-table.json` always; `reviews.json` when review ran;
`fidelity-high.json` and `fidelity-low.json` when calibration ran;
`reported-conflict.population.json` and `reported-conflict.source.txt` when
the conflict step ran; `scope.json` and `closure.json` when absence ran. On
the live route `producer-output-table.json` is the canonical JSON of the
responses by section, and `reviews.json` of the receipts by section.

Skipped values: payload 4 has `"semantic_reviews": []`; payload 5 and the
report have `"fidelity": null`, `"reported-conflict": "skipped"` among the
routes, and `"skipped"` for both absence statuses.

The report of a `/2` run adds `settings`, `steps` and
`documents: [{"source", "stop", "reading_bytes", "attempted", "omitted"}]` in
roster order. `public_routes.broad` and `.targeted` hold the observed exits,
each 0, 1, 2 or 4; any other exit refuses the run `(p1)`.

`replay()` refuses a `/2` manifest with "replay of a caller run is not
available" until LH2.

### 6.6 Other modules

- `depth.py`: `_command(out, *args, limits=PROCESS_LIMITS)` and
  `_decode(data, *, max_bytes=PROCESS_LIMIT)`, both keyword-only and
  defaulting to today's values `(p1)`.
- `revision.py`, `assurance_report.py`: not edited. Both reach the packaged
  layout only.

### 6.7 Test fixtures

- `tests/fixtures/lh1-reading/caller/`: `profile.json` with no step declared,
  `profile-declared.json` with every step declared, `roster.json`,
  `survey.orm.json` with its include `terms.orm.json`, two sources, and the
  seven step files. The model has one uniqueness constraint, so that exits 2
  and 1 are reachable (T15). It shares no section, fact, label or subject
  name with the packaged fixture. Producer answers live in the test module.
- `tests/fixtures/lh1-reading/packaged/{full,unavailable,budget-0}/`: the
  three run folders, recorded at the start commit (plan §3) `(p2)` **before any source edit** with
  the three commands of P3. The first commit of the phase holds these trees
  and nothing else.
- `tests/fixtures/lh1-reading/README.md`: how each was made.

### 6.8 Documents

- `src/gnd/examples/literature/reading_fixture/README.md`: a new section,
  "Drive it from your host", the one home of the protocol, the profile, the
  limits, the `/2` manifest, the step statuses and the sentence that a
  completed caller run is not a verified extraction. It says replay of a
  caller run arrives with LH2.
- `dev/components/COMPONENTS.md`: the `examples.literature_reading` entry
  (`does`, `verbs`, `in`, `out`, `tests`), then `components_index.py write`.

## 7. Decisions

Plan decisions this spec depends on: D6, ruled by the owner on 2026-11-22 as
proposed `(o)`; and D1, D3, D4, D5, D7 and D16, all open.

| ID | Question | Proposed | What the other reading costs | Ruling |
|---|---|---|---|---|
| LH1-D1 | A new argument over the packaged layout | Refuse | Allowing it needs a `/2` run built from packaged constants, a third branch with no user | open |
| LH1-D2 | Profile keys | Closed set, all required, `null` or `false` for an undeclared step | Optional keys let a misspelt key skip a step silently | open |
| LH1-D3 | How much of a response is checked on arrival | Shape, and fact-type names against the bundle's `covers`. Role names and value types are `verify`'s, after the loop; a wrong one refuses the run then, with exit 3 from the route | Checking rows on arrival re-implements the population loader (R0.7); not checking names on arrival moves that refusal to after the last call as well | open |
| LH1-D4 | Stop reason of a source with no required question | `required-coverage-completed`, the global rule's answer | A fourth reason, `nothing-required`, extends the report's vocabulary | open |
| LH1-D5 | The time bounds of T12 | `ReadingInputs` at each roster ceiling in under 10 s; a whole run at the roster ceiling with a producer that answers `empty` in under 90 s; a run with one source at the input ceiling, one response at the response ceiling and the budget at its ceiling in under 60 s; a route held past the timeout refuses within the timeout plus 2 s `(p1)`; a route with 16 MiB of output, and a `/2` run that retains a 64 MiB file, each in under 60 s `(p2)` | Looser bounds stop catching a quadratic walk at 4,096 rows | open |

## 8. Tests

`tests/test_lh1_reading_host.py`. "Refuses" means `ExampleError` or
`ArtifactError` is raised and `out` does not exist.

| ID | Case | Expected | Criterion |
|---|---|---|---|
| T1 | a producer class with only `produce`, over the caller root | report returned; six stages; manifest format `/2`; stage, attempt and coverage key sets equal the packaged run's; broad and targeted exits 0; none of `study-methods`, `alanine`, `approximation`, `alternative_integrator`, `subject_label`, `saved-public-fixture` occurs in any file of the run | C1 |
| T2 | the same run | each call's `excerpt` equals the source's span and its sha256 the attempt row's; `producer_calls` equals the producer's own count per stage | C2 |
| T3 | a live producer and a live reviewer | `producer-output-table.json` and `reviews.json` exist, hold what the two objects returned, and the manifest binds their sha256 | C3 |
| T4 | `profile.json`, no step declared | four steps `skipped`; `fidelity` is `null`; both absence statuses and `reported-conflict` are `"skipped"`; no fidelity, conflict, scope or closure artifact | C4 |
| T5 | `profile-declared.json` | four steps `ran`; fidelity `[n, n]` and `[m, n]` with `m < n`; conflict exits 1 and 1; absence `qualified` and `unavailable` | C4 |
| T6 | each declared step with one of its files removed (7 cases), producer fails the test if called | refuses | C4 |
| T7 | `document_budget` below the first source's targeted section, which comes before a smaller section of the same source | that source: its targeted section omitted, the smaller one after it read `(p1)`, stop `budget-exhausted`; the other source reads in full with its own stop; global `stop` as the global rule gives. A second case marks one source's questions not required: its stop is `required-coverage-completed`. A third resolves a source's required question in the broad pass: its other scheduled sections are still read (D6) `(p1)` | C5 |
| T8 | limits: roster 2 against a three-source roster; `budget` above `max_budget`; a 200 KiB source with the default and with `input_bytes` 1 MiB; each limit at ceiling plus one; a limit of 0, `True` and `1.5` | refuses; refuses; refuses, then runs; refuses (5 cases); refuses (3 cases). The run that completes records its limits in `settings` | C6 |
| T9 | responses: not a mapping; a key missing; outcome `"maybe"`; `accepted` with no facts; `empty` with facts; `facts` a list; a fact's value not a list; a row not a mapping; a nested row value; a NaN; an `object()`; an integer key; nesting 100,000 deep; a response over `response_bytes`; a non-string proposal key; a proposal key outside the roster; a fact type outside `covers` | each refuses, with `ExampleError` and no other exception type | C7 |
| T10 | a producer that raises `RuntimeError` on its second call | refuses; the message names the stage and section; `__cause__` is the `RuntimeError` | C8 |
| T11 | the three packaged commands | `tree_as_recorded(fresh, "0.4.0")` equals the recorded tree, file for file; the recorded `run.json` has the P3 digest | C9 |
| T12 | rosters at 4,096 sources, sections and questions, with one supersession chain of 4,095 and `input_bytes` raised to fit; one source at 8 MiB; one response at 1 MiB; `budget` at 64 MiB; a route that sleeps past `route_seconds` 1 `(p1)`; a route stub that writes 16 MiB under `route_output_bytes` at its ceiling, and a run with 63 eligible sections answered at 1 MiB `(p2)` | within the bounds of LH1-D5; the sleeping route refuses naming the route | C10 |
| T13 | a model file `gnd extract` refuses; a producer over the packaged root; each of the other four new arguments alone over the packaged root. The producer fails the test if called | each refuses | C11 |
| T14 | `replay()` on T1's run; the module command `replay` on it | refuses; exit 3 with `status` `incomplete` | C12 |
| T15 | no base facts, so the constrained fact type is empty after the broad pass and filled by the targeted one; a second producer returns two titles for one paper; exit 4 `(p1)` | completes with broad `{"verify": 2, "check": 2}` and targeted 0 and 0; completes with targeted 1 and 1; exit 4 is recorded like 2, through a caller model whose check exits 4 if the phase finds one, else through a unit test of the exit table, and the record says which | C13 |
| T16 | profiles: not an object; a key missing; an extra key; a wrong format; a model name with a slash; an include equal to the model; 17 includes; `absence` true with `calibration` null; a calibration section that is not targeted; overlapping calibration lists; a base fact outside `covers`; a file over `input_bytes` | each refuses before any producer call | rule 1 |
| T17 | the caller root with `responses.json` and its pin, `producer=None`; the same with a wrong pin | runs with `settings.producer` `saved`; refuses "saved producer table differs from its pin" | §6.3 |
| T18 | `review: true` with a reviewer that returns `supported`; one that returns `unsupported`; one that returns a list; none and no `reviews.json`; `review: false` with a reviewer | runs; refuses "stale semantic reading review"; refuses; refuses before any producer call; refuses | D3 |
| T19 | `scenario="unavailable"` on the caller root; `unavailable` naming an unknown section; `unavailable` naming a targeted section | refuses before any producer call; refuses; runs, with that section's question `unavailable`, no call for it, and the section in `settings.unavailable` `(p1)` | C4, §6.3 |
| T20 | `(p1)` `(p2)` `retained_bytes` given below the computed bound; `retained_bytes` `None` at `roster` 4,096 and `response_bytes` 1 MiB with every section eligible; `response_bytes` 1 MiB with 63 eligible sections and `retained_bytes` `None`; T1's run with default limits | refuses before any producer call; refuses before any producer call; completes, and every retained file reads back under the recorded cap; completes under a derived cap above 128 KiB | C14 |

`test_ld3`, `test_ld4` and `test_ld5` run unedited (C9).

Branch walk. §6.3's five rows: T11, T13, T17, T1, T19. The review branches:
T18. Each step, declared and undeclared: T4, T5. Each omission cause, global
and per document: the unedited `test_other_stop_reasons` and T7. Each route
exit 0, 1, 2, 4 and other: T1, T15, T15, T15, T13.

## 9. Out of scope for this phase

Replay of a `/2` run, the `expected_evidence_sha256` argument, the scorer's
`fixture` argument and any command-line flag (LH2). `docs/literature/commands.md`
and `docs/release-notes.md` (LH2). The admission module (LH3, LH4). Source
paths other than `<id>.txt`. Ending a document at required coverage (D6). Retaining a partial run after a
refusal (D7). The assurance scorer's 128-row cap.

## 10. Size

Estimate at write time: `reading.py` grows by 300 to 380 lines from 610;
`depth.py` by 2; `tests/test_lh1_reading_host.py` about 520 lines; 15 authored
fixture files and 72 recorded ones; the README section about 70 lines. The
plan's threshold for proposing a split is 400 source lines; the estimate is
under it and close to it. If the implementation passes 400, the phase stops
and proposes LH1a (protocol, profile, steps) and LH1b (limits, per-document
budget) at this gate.

## 11. Approval instrument

This prose. No fixture corpus is authored before approval; the caller root
of §6.7 is written in the phase, after the recorded packaged trees.
