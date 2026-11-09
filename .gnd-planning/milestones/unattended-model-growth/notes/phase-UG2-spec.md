# Phase UG2: Population-checked constraint admission

## 1. Status line

**Corpus approved `(o)`, 2026-11-09; implementation authorized.** Asked "Do you
approve the UG2 corpus answers?", the owner replied, quoted: "Approve the
corpus". Approved bytes: the five files in "Corpus authoring" at the digests
listed there (commit `c635ef9d`). This authorizes implementing UG2 as specified.
No merge, release or issue action. Changing an approved expected answer returns
it to the owner.

Earlier status, kept: **Corpus authored and red, 2026-11-09; waiting for the owner's corpus approval.**
The corpus (§11) is committed before any source edit: 15 cases (C01 to C11c),
each red for the intended reason (exit 64, `--check-population` is not an
option on the base), plus a green flag-free parity baseline (12 rows) and a
check that the narration gives no outcome. See "Corpus authoring" below. No
source file is edited. Implementation starts only when the owner approves the
corpus.

Earlier status, kept: **Spec gate `(o)`, 2026-11-09: approved as proposed.** The owner was asked
"How do you rule on UG2-D1 to UG2-D12?" and replied, quoted: "Approve all as
proposed". Every decision in §7 is ruled as its **(proposed)** reading,
including UG2-D12 (a): the approval instrument is **corpus-first**. So this
approval covers the design and the decisions. Under corpus-first the next step
is the fixture corpus and its red harness (§11), committed before any source
edit and put to the owner. Approved bytes: r1 at `bff83562`, sha256 `7164d48b…`;
only this paragraph, the §7 ruling column and the revision history changed
after. No source file may be edited until the owner approves the corpus. No
merge, release or issue action is authorized.

Superseded status text, kept for provenance: **Draft r1, waiting for this spec's owner gate.** Not approved, no code written,
`auto=false`. The plan (r1.2) was approved at its gate on 2026-11-07
([001-plan.md](../001-plan.md)). That approval covers the plan only, not this
spec. Decisions UG2-D1 to UG2-D12 (§7) are open. No implementation file may be
created or edited before the owner rules on them and approves this spec.

## 2. Provenance

- Derived from [the plan](unattended-model-growth-plan.md) r1.2: §0 (UG-R1 to
  UG-R11), §2.2 (UG2 shape, proposed), §3 (artifact homes, serial landing), §4
  UG2 (named criteria UG2-C1 to C8, proposed), §5 (surfaces), §6 (risks), §9
  (UG2 row) and §10 (UG-D2 ruled (b); UG-Q1, UG-Q2, UG-Q3 open for this spec).
- Prior record: [002-phase-UG1.md](../002-phase-UG1.md) (UG1 merged in PR 123).
  Its matrix row "104-5 second option" is `open`, and its T4 shows today's
  refusal. That refusal is what UG2 turns into an admission for a clean
  population.
- Code read by the author on `8eb4fe60` (main after PR 143), the base of this
  branch: `src/gnd/evolve/{policy,service,models,cli_service}.py`,
  `src/gnd/commands/evolve.py`, `src/gnd/population.py`
  (`read_population_bytes`, `load_population_bytes`), `src/gnd/checker/_core.py`
  (`check`, verdict vocabulary), `src/gnd/checker/_reports.py`
  (`ConstraintVerdict`), `src/gnd/address.py` (`positional_constraint_ref`),
  `src/gnd/model/__init__.py` (`resolve_context`), and the evolution contract
  "Additive policy". Line numbers below are at `8eb4fe60`.
- **No review has run over these bytes.** A review is the owner's call at the
  gate (§11).

## 3. Obligations (the step 0 harvest)

| Row | Obligation (source) | Discharged in this spec |
|---|---|---|
| O6 | Admit a clean-population constraint over a populated fact type (issue 104 item 5, second option; plan O6; UG-D2 (b)) | §6 design; T1 to T12 |
| UG2-C1 | A population whose constraint verdict is `pass` clears the two populated cells | T1 (add), T2 (strengthening modify) |
| UG2-C2 | A violating population (`warning`), a population with no rows for a subject (`vacuous`), an `unchecked` verdict, a population violating only a different, pre-existing constraint (rule stated first) and a population for the wrong model each leave the refusal, naming the operation index and reference, with no value | T3, T4, T5, T6 (rule: UG2-D9), T7 |
| UG2-C3 | A non-proposed or non-deontic constraint, and a modify outside the strengthening list, is not cleared | T8 |
| UG2-C4 | apply without the option, or with it on one side only, exits 3; the same option over different bytes at the same path exits 11 (one exit pinned per case) | T9 |
| UG2-C5 | Flag-free parity (UG-R1) | T10 |
| UG2-C6 | No population value in any output, shown with canary values and an exclusion list for model-carrying preview keys; per-disclosure-mode behavior stated | T11; §6.6 |
| UG2-C7 | Hostile population cases, and a time-bound test that counts operations with spies for linearity, not wall clock | T12, T13 |
| UG2-C8 | Layering and RF6 gates green | §8 gate rows G-layers, G-rf6 |
| Plan §9 UG2 row | "As UG2-C1..C8"; UG1 gate plus the listed modules, a new `tests/test_evolve_population_check.py`, and `components_index.py changed --base main --strict`, exact list fixed in the spec | §8 selection ledger |
| Plan §2.2 open points | how an operation maps to its verdict; populated subjects the population does not mention; inline `sample_population` rows; several files; whether `model_id` becomes mandatory; D-13 record carries the digests | §6.3; UG2-D4; UG2-D5; UG2-D2; UG2-D7; UG2-D10 |
| Plan §6 "`evolve/service.py` is 2221 lines" | new logic beside `policy.py`; no checker-core change | §6.1 (new module `population_check.py`); §4 rule 2 |
| Plan §6 "a new option moves RF1 goldens" | only the two touched leaves are re-pinned | §6.7; G-rf1 |
| Plan §3 serial landing | UG2 lands first; appends to the RF6 dynamic-candidate chain, `MANIFEST_SHA256`, `goldens.sha256` | §6.7; G-rf6 |
| Plan §5 surfaces owned by UG2 | evolution contract "Additive policy" (normative); `docs/reference/cli.md`; `docs/release-notes.md` entry; RF1 goldens for `evolve preview`/`apply`; disclosure canary test; packaged-skill pins measured | §6.8; §8 |
| UG-Q1 | Can the evolve lane call the checker with zero allowances? | §4 UG-R8: confirmed by G-layers, G-arch at execution |
| UG-Q2 | Option name | UG2-D3 |
| UG-Q3 | Artifact locator or new option; one composed input or several files | UG2-D1, UG2-D2 |
| UG1 refactoring note | the UG1 test file imports private helpers from two test modules | inherited, not owned: UG2's new test file uses `tests/support/` helpers or its own; it adds no new private cross-import (§9) |
| UG-Q6 | `project.md` both denies and locates a component index | carried; this spec applies the `dev/components/` reading, as the plan does |
| UG-Q7 | Tracker labels | carried, owner |

**Plan §2.2 wording this spec departs from (each needs a ruling):** the plan's
option is repeatable (UG2-D2 proposes one file), and it says "with a count only"
(UG2-D8 proposes no count). Both are flagged in §7 rather than changed silently.

## 4. The standing rules, bound to this phase

**Plan §0:**

| Rule | Discharge |
|---|---|
| UG-R1 defaults do not move | The new preview field is in `_OPTIONAL_PREVIEW_FIELDS`, so without the option it is omitted and `preview_sha256` is unchanged; `additive_policy_issues` with no verdict map behaves as today. T10 compares preview bytes and digests, and the `apply` exits, without the option against goldens captured on `8eb4fe60` before the first source edit |
| UG-R2 nothing confirms | Clearing needs the constraint's `after` to be `status: proposed` and `modality: deontic` (T8). No code writes provenance |
| UG-R3 evidence licenses, a human admits | The preview's `population_check.admitted` list names every operation the population cleared, with the verdict word `pass`. The constraint's bytes are the proposal's own and are never relabelled (T1 asserts the published constraint equals the proposal's `after`) |
| UG-R4 one walk, one home | `additive_policy_issues` stays the one walk. It gains one keyword argument (a verdict map) and decides clearing in its existing constraint branch. The service computes verdicts and never decides a cell. The evolution contract "Additive policy" is the one normative home (§6.8) |
| UG-R5 digest-bound | The file is read once through `gnd.artifacts.read_regular_file_bytes` beneath the workspace (no symlink, regular file, cap at the read). The SHA-256 of those bytes goes into the preview, and the same bytes are parsed with `load_population_bytes`. `apply` repeats the option. A different digest changes the fresh preview, so `apply` exits 11; the service re-reads and re-checks before publishing, and a changed digest there exits 11 ("changed before apply"). No path is recorded (T9, T11) |
| UG-R6 disclosure | No message, issue detail or preview field carries a population value, a count of facts, or the checker's `message`/`offending_facts`. Only ids from the model, operation indexes, verdict words and digests appear (T11, UG2-D8) |
| UG-R7 totality and cost | The reader is total: every hostile case exits 3, 66 or 74 with no traceback (T12). The checker runs once per preview, whatever the number of operations, and the mapping is linear in the operations (T13, spies) |
| UG-R8 layering and query policy | One new module `gnd.evolve.population_check` in the `evolve` lane, layer `lanes`, added to `tools/gnd_layers.json`; its imports go down to `gnd.checker` (`checking`), `gnd.population`, `gnd.artifacts`. Zero new allowances. Model reads go through `ModelIndex`. The RF6 counted reads and the dynamic-candidate chain are measured at execution (G-layers, G-arch, G-rf6); if an allowance would be needed, the spec returns to the owner |
| UG-R9 installer-owned links | No packaged file is added. If one were, links come from `uv run gnd install --symlink --project --force` |
| UG-R10 anonymity | Fixtures use a neutral lending domain (the UG1 fixture's), and the record repeats UG1's digest-set scan over UG2's files, commits and PR body |
| UG-R11 approval and protection | `auto=false`; topic branch and PR; merge only on the owner's word |

**Project standing design rules (`project.md`):**

| Rule | Discharge |
|---|---|
| 1 Totality belongs to the function | `read_population_for_check` (§6.1) is total over arbitrary bytes: oversize (cap at the read), non-UTF-8, NaN/Infinity, a 10^5-digit integer, nesting deeper than 64, YAML alias bomb, a JSON array top level, a directory, a FIFO, a symlink, a missing file. Each case is in T12 with its exit |
| 2 A cap bounds the document, not the algorithm | The new layer is the mapping from operations to verdicts. It is one replay with identity tracking, O(operations + constraints). T13 counts `check` calls (exactly one) and the replay's visits (linear) for 1, 10 and 100 constraint operations |
| 3 Validation order is pinned per boundary | §6.4 states the order for preview and for apply; T14 pins it by source-order assertion where two orders would both reject with the same exit |
| 4 One walk for N kinds | Clearing applies to both populated cells (add, modify) in the one existing branch; no per-family copy. T1, T2 and a parametrized family sweep (uniqueness, mandatory, frequency, value, ring) in T1 |
| 5 Normative prose has one home | The evolution contract "Additive policy" gains the population-checked paragraph; `docs/reference/evolve-policy.md`, `docs/reference/cli.md` and the release note cite it. UG4 reconciles the pages that restate "keeps every fact interpretable" (plan UG4-C5) |
| 6 Contested representation by measurement | The verdict mapping (positional ref against declared id) is settled by T15, a measurement: a constraint carrying a declared `id` is checked and its verdict located, before the mapping code is final |

**Failure classes this project has committed:**

- *Any versus every* (fixture-made unfalsifiability): T5 is a spanning
  constraint with two populated subjects where the population has facts for one
  only. UG2-D4 (a) refuses it; the reading "verdict is pass" would clear it. The
  fixture tells the two readings apart.
- *Interchange field in Python terms*: the new preview field holds a SHA-256 hex
  of raw bytes and JSON lists of ints and strings; no repr.
- *"Not implemented" folded into "violated"*: an `unchecked` verdict leaves the
  refusal with its own word (`unchecked`), not `warning` (T5b).
- *A guard that goes quiet*: a population that fails to load never yields an
  empty verdict map that clears nothing silently. It exits (T12), so the run
  never reports "refused because the population was empty" when the truth is
  "the population was unreadable".

## 5. Goal

With `--policy additive --check-population PATH` on `gnd evolve preview`, an
operation the additive policy would refuse as `constraint.populated.add`, or as a
strengthening `constraint.populated.modify`, is admitted when its constraint
after the operation is `proposed` and `deontic`, the supplied population has at
least one fact for every populated subject of that constraint, and that
constraint's own verdict over the candidate model and the population is `pass`.
The preview then exits 0 and records the population's digest and the admitted
operations. Any other verdict leaves the refusal (exit 3), and the issue names
the operation index, reference and verdict word. `gnd evolve apply` with the same
option over the same bytes publishes (exit 0). It exits 3 when the option is
present on only one side, and 11 when the bytes changed. Without the option,
every preview byte and every exit equals `8eb4fe60`.

## 6. Design

### 6.0 Reuse (component index, `dev/components/`)

Searched with `python3 scripts/components_index.py search` on 2026-11-09:

| Capability | Searches | Found | Decision |
|---|---|---|---|
| Read one population file safely, cap at the read | `population check`; `read population file digest` | `model.population_loading` (`read_population_bytes`, `load_population_bytes`); `gnd.artifacts.read_regular_file_bytes` (used by `evolve.service._regular_bytes`) | **reuse** `read_regular_file_bytes` with `max_bytes=MAX_POPULATION_BYTES` (workspace-anchored, refuses symlinks, the evolve lane's existing read), then `load_population_bytes` on those same bytes. Not `read_population_bytes`: it opens a raw path with no workspace anchor |
| One verdict for one constraint | `constraint verdict for one constraint` | `checker.evaluate` (`gnd.checker.check`), `checker.reports` (`ConstraintVerdict`) | **reuse** `gnd.checker.check`; no checker change |
| Locate a constraint's position after replay | `replay declared operations` | `evolve.service` (`_apply_declared_operations`), `model.address` (`positional_constraint_ref`) | **adapt** `_apply_declared_operations`: one optional keyword records placed objects; **reuse** `positional_constraint_ref` |
| The policy decision | n/a (known) | `evolve.policy` (`additive_policy_issues`) | **adapt** (one keyword argument) |

New code beside canonical components: only the module in §6.1, which composes
the four rows above and holds no reader, checker or policy of its own.

### 6.1 `src/gnd/evolve/population_check.py` (new, about 160 lines)

```python
POPULATION_CHECK_PASS: Final = "pass"

@dataclass(frozen=True)
class PopulationCheck:
    sha256: str                     # hex SHA-256 of the raw bytes read
    outcomes: Mapping[int, str]     # operation_index -> outcome token (below)

def read_population_for_check(
    anchor: Path, relative: str, *, candidate: Model
) -> tuple[str, Population]:
    """Read once, hash, and load the bytes against the candidate (layer 1 and 2)."""

def population_check(
    before_document: dict[str, Any],
    proposal: EvolutionProposal,
    *,
    candidate: Model,
    population: Population,
    sha256: str,
    populated: frozenset[str],
) -> PopulationCheck:
    """One check() call; one outcome per constraint ADD/MODIFY operation."""
```

**Outcome tokens** (closed set, `PopulationOutcome = Literal[...]` in
`models.py`): `pass`, `fail`, `warning`, `unchecked`, `vacuous` (the checker's
`Verdict` spelled the same way), plus `uncovered` (a populated subject has no
fact in the population, UG2-D4), `sample-rows` (a subject has before-model
`sample_population` rows, UG2-D5) and `not-located` (no verdict was found for the
placed constraint: a defect guard, fail closed). Only `pass` clears.

**Read.** `read_regular_file_bytes(anchor, relative, label="population",
max_bytes=MAX_POPULATION_BYTES)`, then `sha256_hex(data)`, then
`load_population_bytes(data, source=relative, model=candidate)`. One read; the
hashed bytes are the parsed bytes. Errors are re-raised as `EvolutionError`
with the cause chained, so the existing exit mapping (`_evolve_service_exit`)
gives 66 (missing), 74 (symlink, not regular, unreadable) and 3 (malformed,
oversize, layer-1 or layer-2 invalid). The message names the label
`population`, never the operator's path beyond what the existing artifact read
already prints. (Whether that existing message prints the relative path is
measured in T11; if it does, the population label replaces it.)

**Model identity (UG2-D7 (a)).** After load, `population.model_id` must equal
`candidate.model_id`. Absent or different: `EvolutionError("population model_id
… does not match the candidate model")`, exit 3.

**Reference populations (UG2-D11 (a)).** If the candidate declares
`reference_populations`, the option exits 3 before reading the file: `check()`
needs a bound reference context the evolve lane does not build.

**Placement.** `_apply_declared_operations(before_document, proposal.operations,
placed=recorder)` (a new keyword-only argument, default `None`, so the
discover caller is unchanged) records, for each constraint ADD and MODIFY, the
object it appended or assigned. After replay, the position of each recorded
object in its host list is found **by identity** (`is`), which survives later
deletes in the same proposal. Replay equality (`declared_document ==
candidate_document`) has already passed, so that position is the candidate's
position. The verdict is the one whose `constraint_ref ==
positional_constraint_ref(host_id, position)`.

**Check.** `gnd.checker.check(candidate, population)`: one call. For each
recorded operation, in order: `sample-rows` if any subject has before-model
sample rows; else `uncovered` if any populated subject has no fact in
`population.facts`; else the located verdict word; else `not-located`.
"Subject" and "populated" are the policy's (`_role_ref_fact_types`,
`playing`, `effective_populated`); to keep one definition the subject
computation moves from inside `additive_policy_issues` to a module-level
function in `policy.py`, `constraint_subjects(index, operation) -> set[str]`,
called by both (rule 4).

### 6.2 `src/gnd/evolve/policy.py` (about +40 lines)

```python
def additive_policy_issues(
    before: Model,
    proposal: EvolutionProposal,
    *,
    populated: frozenset[str],
    population_outcomes: Mapping[int, str] | None = None,
) -> tuple[PolicyIssue, ...]:
```

In the constraint branch, where today it would call `refuse(...)` for
`constraint.populated.add` or a `constraint.populated.modify` detail:

1. `population_outcomes is None`: unchanged (byte parity, T10).
2. Eligible means `after.status == "proposed"` and `after.modality ==
   "deontic"`, and, for MODIFY, every refusing key's verdict is `strengthening`
   (a `neither` key is never cleared).
3. Eligible and `population_outcomes.get(position) == "pass"`: no issue.
4. Otherwise the issue is raised as today, with the detail suffixed by
   `; population: <outcome>` when eligible, or `; population: not eligible`
   when not. The cell is unchanged (`PolicyCell` gains no member).

The function stays free of I/O and keeps one walk.

### 6.3 `src/gnd/evolve/models.py` (about +40 lines)

New closed classes and one optional preview field:

```python
PopulationOutcome = Literal["pass", "fail", "warning", "unchecked", "vacuous",
                            "uncovered", "sample-rows", "not-located"]

class PopulationAdmission(_ClosedFrozenModel):
    operation_index: int = Field(ge=0)
    reference: NonEmptyString
    outcome: Literal["pass"]

class PopulationCheckRecord(_ClosedFrozenModel):
    sha256: Sha256String
    model_id: StableId
    admitted: tuple[PopulationAdmission, ...]
```

`_EvolutionPreviewV3` and `EvolutionPreview` gain `population_check:
PopulationCheckRecord | None = None`. It is added to `_OPTIONAL_PREVIEW_FIELDS`
(omitted when `None`) and validated: set only when `policy` is set. Literal
JSON, for the T1 golden:

```json
"population_check": {
  "sha256": "<64 hex>",
  "model_id": "lending",
  "admitted": [
    {"operation_index": 0, "reference": "fact_types[loan_has_due_date].constraints[mandatory:new:0]", "outcome": "pass"}
  ]
}
```

No path, no count, no value. **Forward compatibility:** previews that carry
the field are refused by GND readers older than UG2 (closed models). Old
previews read unchanged. The release note says so (§6.8).

### 6.4 Service and CLI wiring

`EvolutionService.preview(..., check_population: str | None = None)` and
`EvolutionService.apply(preview, *, check_population: str | None = None)`.
`cli_service` and `commands/evolve.py` add `--check-population PATH` (single,
not repeatable, UG2-D2) to `evolve preview` and `evolve apply`, resolved with
`_evolve_workspace_path(workspace, PATH, label="population", required=True)`.

**Preview order (normative home: the contract's "Order" sentence, extended):**
pending state (11), stale identity (11), operations gate (18), candidate
validation, replay equality and D-12 (3), **then** `--check-population`
without `--policy` (3), reference-bearing candidate (3), the population read and
load (66/74/3), `model_id` (3), **then** the policy walk with the outcomes.
Nothing before the population read changes, so a malformed proposal still
reports its own error first.

**Apply order.** `cli_service.apply` compares the option's presence with the
reviewed preview's `population_check` beside the `--populated` comparison,
before the retry branch: present on one side only exits 3 ("--check-population
differs from the reviewed preview"). The fresh preview rebuilt from the same
path must equal the reviewed one; changed bytes change `sha256`, so the
equality fails and the command exits 11. `EvolutionService.apply` today re-runs
the policy **before** `_validated_candidate`. The population check needs the
candidate model, so under the option the policy re-run moves to after
`_validated_candidate`, replay equality and D-12 (the order preview already
uses). Without the option the existing order stays, so the flag-free exits
do not move (T10, T14). The service re-reads the population; a digest different
from `preview.population_check.sha256` raises "population changed before
apply" (the `changed before` stale marker, exit 11); a non-empty issue list
raises `EvolutionPolicyRefusedError` (3). The candidate-already-live retry
branch publishes nothing new and does not re-check, as today for the policy.

**Human output** (`cli_service` text claim): one line `population:
<sha256>` and one `population-admitted: <index> <reference>` per admission,
after the existing `policy-issue` lines.

### 6.5 What "clean" means (normative, contract home)

The issue clears only on the outcome `pass`. `warning` (a deontic violation),
`fail`, `unchecked`, `vacuous`, `uncovered`, `sample-rows` and `not-located` all
leave the refusal. The `gnd check` exit band is never consulted. Verdicts of
other constraints in the candidate do not matter (UG2-D9 (a)). The admission
holds relative to the supplied population: the constraint stays `proposed` and
`deontic`, so a later violating fact is a reported warning, not an
uninterpretable fact.

### 6.6 Disclosure, per mode

`gnd evolve` sits in the disclosure table's "emits no population values" row,
and stays there. Under every disclosure mode, including models with
`redact: true` roles, the new outputs are the same: a digest, the candidate's
`model_id`, operation indexes, references built from model ids, and outcome
words. No count of facts or violations is emitted (UG2-D8 (a)), so a redacted
role gets no counting oracle. The admission itself (pass or not) is the one bit
the feature exists to reveal, and the contract says so. `docs/reference/disclosure.md`
gets no new row.

### 6.7 Pins and chains UG2 moves (measured at execution, never derived here)

- RF1 goldens: `cli-help` and `cli-exit` for `evolve preview` and `evolve apply`
  on 3.11, 3.13 and 3.14; `cli/tree.json`; `goldens.sha256`; `MANIFEST_SHA256`
  in `tests/test_rf1_pin_harness.py`. Only these leaves are re-captured.
- RF6: `evidence/UG2/dynamic-query-successor.json` (and
  `query-successor.json` only if a counted query moves) under this milestone,
  chained onto the current tail of `DYNAMIC_SUCCESSORS` /
  `QUERY_SUCCESSORS` in `tests/support/pyrel_application_successors.py`.
- `tools/gnd_layers.json`: one module entry. `dev/components/`: the new module
  assigned to `evolve.policy` or a new `evolve.population_check` component,
  regenerated in the same commit.
- `docs/reference/cli.md`: the option lines (read by
  `test_documentation_tutorials.py`).

### 6.8 Documentation owned by UG2

- `gnd-model-evolve/references/evolution-contract.md`: "Additive policy" gains
  a **Population check** paragraph (§6.5 text, the order, the apply rule, the
  forward-compatibility sentence), and "EvolutionPreview" lists the field. This
  is the one normative home.
- `docs/reference/evolve-policy.md`: one cited sentence and the command.
- `docs/release-notes.md`: the UG2 entry, replacing "remains open" for the
  clean-population policy, with the forward-incompatibility of older readers.
- Everything else (how-to, agents pages, `unattended-growth.md`, the
  "keeps every fact interpretable" wording) is UG4's.

## 7. Decisions

At first write every row was open; the proposed reading is marked **(proposed)**. Rulings are in the last column.

| ID | Question | Readings and cost | Proposed | Owner ruling |
|---|---|---|---|---|
| UG2-D1 (UG-Q3) | How does the population arrive? | (a) a new `--check-population PATH` on `preview` and `apply`, digest recorded in the preview: a new option on two commands; the artifact locator keeps today's meaning (evolve never opens artifacts). (b) open the proposal's existing `population` artifact locators, digest already in `proposal_sha256`: no path option on `apply`, but a boolean flag is still needed on both commands, because opening artifacts by default would move every existing proposal's exits (UG-R1); and the contract sentence "evolution does not … open … the artifact" changes for all artifacts | **(a)** | `(o)` 2026-11-09: as proposed |
| UG2-D2 (UG-Q3) | One file or several? | (a) exactly one file. A host with several populations composes them first with `gnd compose` (shipped in CT2), which already keeps per-source anchors. (b) repeatable, files concatenated into one population: needs instance merging rules GND does not have. (c) repeatable, each checked alone: unsound, since two clean files can violate in union. The plan's §2.2 said "repeatable" provisionally | **(a)** | `(o)` 2026-11-09: as proposed |
| UG2-D3 (UG-Q2) | Option name | `--check-population` (the plan's placeholder) / `--population` / `--admit-on-population` | **`--check-population`** | `(o)` 2026-11-09: as proposed |
| UG2-D4 | A populated subject with no fact in the population | (a) refuse with `uncovered`; (b) rely on the checker, which gives `vacuous` only when **every** subject is empty, so a spanning constraint with one covered and one uncovered populated subject could `pass` (the any/every trap, T5) | **(a)** | `(o)` 2026-11-09: as proposed |
| UG2-D5 | A subject populated by before-model `sample_population` rows | (a) refuse with `sample-rows` (fail closed; `check` does not see sample rows); (b) convert sample rows into facts and check them too: new conversion code and a second population source | **(a)** | `(o)` 2026-11-09: as proposed |
| UG2-D6 | Do the supplied population's fact types count as populated? | (a) no change to `populated`: it stays `effective_populated`'s set, and the population only clears refusals; (b) add them: a constraint on a fact type populated only by the file would then be checked, and could be refused, where without the flag it is admitted. (b) is stricter but makes the opt-in flag able to refuse what the flag-free run admits | **(a)** | `(o)` 2026-11-09: as proposed |
| UG2-D7 | Population `model_id` | (a) required, must equal the candidate's (exit 3 if absent or different); (b) the loader's default: optional, a mismatch is an error, an absence is a warning. (a) costs hosts one header field; (b) lets a population for another model with the same shape clear a refusal | **(a)** | `(o)` 2026-11-09: as proposed |
| UG2-D8 | Counts in refusal details | (a) no counts: the outcome word only. (b) the plan's "count only": the number of offending facts. Over a `redact: true` role a count is an oracle, and (a) removes the question for every mode | **(a)** (departs from plan §2.2 wording) | `(o)` 2026-11-09: as proposed |
| UG2-D9 | A population that violates a different, pre-existing constraint | (a) ignored: only the operation's own verdict decides; (b) every constraint must pass: a host's existing data may already carry deontic warnings, which would then block every admission | **(a)** | `(o)` 2026-11-09: as proposed |
| UG2-D10 | How the D-13 record shows what an admission rested on | (a) transitively: the record binds `preview_sha256` and the staged `preview.json` carries `population_check`; no record schema change. (b) an explicit record field: a record-schema change and new pins | **(a)** | `(o)` 2026-11-09: as proposed |
| UG2-D11 | Candidate declares `reference_populations` | (a) refuse the option, exit 3: `check()` needs a bound reference context the evolve lane does not build; constraints over reference-owned fact types stay refused. (b) build the context: more code and a second input class | **(a)** | `(o)` 2026-11-09: as proposed |
| UG2-D12 | Approval instrument (step 2) | (a) **corpus-first**, the default for a phase with an exit-code contract and a serialized field: before any source edit, commit T1 to T9's fixtures, the T1 preview golden (§6.3 JSON with real digests) and the expected-exit table, red, and approve those. Costs one authoring session. (b) this prose, with the test list (§8) as the narrated cases; then the reason must be on the page: the exit bands are existing ones and the field is small | **(a)** | `(o)` 2026-11-09: as proposed |

## 8. Tests

New file `tests/test_evolve_population_check.py` (CLI-level unless marked
*service*). Fixture: a copy of the UG1 lending model with a populated
`loan_has_due_date`, and small populations written per test. Every refusal
assertion checks the cell, the operation index and the outcome word: exit 3 alone
is not enough, since candidate-validation failures also exit 3.

| Test | Case | Expected |
|---|---|---|
| T1 | ADD a `proposed`/`deontic` mandatory constraint on a populated fact type; clean population. Parametrized over uniqueness, mandatory, frequency, value, ring | preview 0, `population_check.admitted` names op 0; apply 0; published constraint equals `after`; T1-golden preview bytes (corpus) |
| T2 | MODIFY strengthening (`roles` subset on uniqueness; `range.min` raised); clean | preview 0; apply 0 |
| T3 | Violating population (deontic) | preview 3; issue `constraint.populated.add`, op 0, `population: warning` |
| T4 | Population with no facts for the subject | preview 3; `population: uncovered` (UG2-D4 (a)); the checker's `vacuous` is reached in T4b with a subject covered by an empty-role edge case, or recorded as unreachable with the reason |
| T5 | Spanning constraint, two populated subjects, facts for one only | preview 3; `population: uncovered` (any/every discriminator); T5b: an `unchecked` verdict (a family the checker reports as unchecked) gives `population: unchecked` |
| T6 | Population clean for the new constraint, violating an older deontic constraint | preview 0 (UG2-D9 (a)) |
| T7 | `model_id` absent; `model_id` of another model; layer-2 invalid for the candidate | each preview 3, before the policy walk; message names `population`, no value |
| T8 | Not eligible: `status: confirmed` after (D-12 permitting); `modality: alethic`; MODIFY changing `type` (neither) | preview 3; `population: not eligible` |
| T9 | apply: option missing (3); option only on apply (3); same path, different bytes after preview (11); bytes changed between the fresh preview and the service re-read (*service*, monkeypatched read: 11 "changed before apply") | as listed; model bytes unchanged in every case |
| T10 | Parity: every UG1 replay preview and the `test_evolve_additive_policy.py` cell table without the option, against bytes and digests captured on `8eb4fe60` before the first source edit | byte-identical; exits identical |
| T11 | Canaries: unique strings in instance values of the population; scan stdout, stderr, the preview file (excluding `candidate_model`, `before_model`, `verbalization`, which carry model text) and the D-13 record; positive control plants a canary in a scanned channel | 0 hits; control found |
| T12 | Hostile file, each with its exit: missing 66; symlink 74; directory 74; FIFO 74 (non-blocking); oversize (cap+1) 3; non-UTF-8 3; NaN 3; 10^5-digit integer 3; depth 65 3; YAML alias bomb 3; top-level list 3; `--check-population` without `--policy` 3; reference-bearing candidate 3 | exits as listed, no traceback on stderr |
| T13 | *service*, spies: 1, 10, 100 constraint ADD operations | `check` called exactly once per preview; replay visits grow linearly (ratio bound, not wall clock) |
| T14 | Order: a proposal that is both replay-unequal and carries a missing population file | exit 3 with the replay message (replay before the read); source-order assertion that, in `preview`, the population read follows `_enforce_d12` and precedes `additive_policy_issues` |
| T15 | Measurement (rule 6): a candidate constraint with a declared `id` | the verdict is located by positional ref; if the checker emits the declared id instead, the mapping takes it, and this test records which |
| T16 | *service*: a proposal that ADDs constraint A then DELETEs an earlier constraint on the same host | A's verdict is located at its shifted position (identity placement) |

**Branch walk.** Outcomes `pass`, `warning` (T3), `fail` (T3b: an alethic
constraint is not eligible, so `fail` is reachable only through the
not-eligible path; recorded as such), `unchecked` (T5b), `vacuous` (T4b or
recorded unreachable), `uncovered` (T4, T5), `sample-rows` (T17: a subject with
before-model sample rows, clean population: preview 3), `not-located` (a
monkeypatched empty report: preview 3). Eligibility branches: T8. Apply
branches: T9. Flag-free branch: T10.

### Verification-selection ledger

| Gate | Disposition | Command |
|---|---|---|
| G-phase | run | `uv run pytest -q tests/test_evolve_population_check.py --tb=short` |
| G-ug1 (plan §9: UG1 gate) | run | `uv run pytest -q tests/test_unattended_model_growth_acceptance.py tests/test_unattended_mode.py tests/test_unattended_growth_guidance.py tests/test_evolve_additive_policy.py tests/test_evolve_shape_matches.py tests/test_growth_example.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_digest_helpers.py --tb=short` |
| G-rf1 | run | `uv run pytest -q tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py --tb=short` |
| G-layers, G-arch | run | `uv run pytest -q tests/test_rf1_layering.py tests/test_gnd_arch.py tests/test_rf6_packages.py --tb=short` |
| G-rf6 | run | `uv run pytest -q tests/test_rf6_query_policy.py --tb=short` (and the successor-chain consumer tests that import `tests/support/pyrel_application_successors.py`, listed by `git grep` at execution) |
| G-disclosure | run | `uv run pytest -q tests/test_disclosure_mode.py --tb=short` |
| G-skills | run | `uv run pytest -q tests/test_packaged_skills.py tests/test_skill_prose_sync.py tests/test_ik_close.py tests/test_public_binding_prose.py --tb=short` (contract prose edit; no file added) |
| G-docs | run | `uv run pytest -q tests/test_documentation_tutorials.py --tb=short` |
| G-evolve-consumers | run | `uv run pytest -q tests/test_model_evolution.py --tb=short` and every test module that imports `gnd.evolve` or calls `_apply_declared_operations` (including discover's `candidate_document`), listed by `git grep` at execution |
| G-lint | run | `uv run ruff check src/gnd/evolve tests/test_evolve_population_check.py` |
| G-components | run | `python3 scripts/components_index.py changed --base main --strict` |
| G-anon | run | UG1's digest-set scan over UG2's files, commits and PR body |
| Full default lane; `-m "evidence or census"`; distribution lane | cadence | not selected (verification-selection: no explicit request) |
| Certification | not selected | opt-in only |

## 9. Out of scope for this phase

- More than one population file, or composing them (UG2-D2: `gnd compose`
  first).
- Reference-bearing candidates (UG2-D11).
- Any other policy cell: rename, delete, element modify, role cells, model
  identity, the replaced reference scheme all stay refused.
- Admitting a non-`proposed` or non-`deontic` constraint.
- The `source.documents` locator and span counts (UG3); documentation pages
  other than §6.8 (UG4); the "keeps every fact interpretable" wording (UG4-C5).
- Moving UG1's private test helpers to `tests/support/` (UG1 refactoring note;
  owner's choice, not this phase).
- A checker change; a D-13 record schema change (UG2-D10 (a)).
- Merge, release, certification; posting to or closing issue 104.

## 10. Size

Estimate: source about 300 lines (`population_check.py` 160, `policy.py` +40,
`models.py` +40, `service.py` +40, CLI +25), plus pins and evidence JSON. Tests
about 850 lines. Within the plan's 400 to 650 / 800 to 1000. Measured at record
time.

## 11. Approval instrument

Proposed: corpus-first (UG2-D12 (a)). If chosen, the corpus is T1 to T9's
fixtures under `tests/fixtures/unattended-model-growth/ug2/`, an entry README
narrating each case without its exit, and the answer key (expected exits,
cells, outcome words, the T1 golden) in a separate `expected.json`, committed
red before the first source edit, then put to the owner. If the owner chooses
prose, this spec is the instrument as written.

Optional spec review: none proposed. The owner may call one (the project's
instrument is the maintained panel; UG-D1 ruled four local readers for plan and
close review only).

## Corpus authoring (step 2 instrument, recorded as it was done)

Committed red before any source edit, on the spec gate's ruling UG2-D12 (a).

| File | sha256 |
|---|---|
| `tests/fixtures/unattended-model-growth/ug2/README.md` (narration, no outcomes) | `3935544a51462987cbb1be2a00cc54e48251f48979d2f3d5fc657c2058f1d602` |
| `tests/fixtures/unattended-model-growth/ug2/expected.json` (answer key) | `622a47a65357689f95e773c03a7f21810544808620389cf1b816abdb28a3f2c4` |
| `tests/fixtures/unattended-model-growth/ug2/parity-baseline.json` (T10 baseline) | `cce0c1dbba4697ea7926e819b498a3d324c19add1a9cef2f16ced9b95a45442b` |
| `tests/fixtures/unattended-model-growth/ug2/base.orm.yaml` | `1a8db33084817e9e418b4fb06d9ac08bfc6876d460fb1b9e908639cdaecae314` |
| `tests/test_evolve_population_check.py` (harness) | `3d994ac280aaac5e95b0cde82935569b7d2ad1b57e3df6c580245022b0c82fcb` |

Run on the base source (`git status` clean under `src` and `tools`):
`uv run pytest -q tests/test_evolve_population_check.py` gives `15 failed, 13
passed`. Every failure is exit 64 with the argparse usage line. The 13 passes are
the 12 parity rows and the narration check. `ruff check` is clean.

Mapping to §8: C01 is T1 (one family; the family sweep stays a service-level
test to add during implementation), C02 T2, C03 T3, C04 T4, C05 T5, C06 T6,
C07a/b T7, C08a/b T8, C09 T17, C10 the T12 row "without `--policy`", C11a to
C11c T9. T4b, T5b, T11 to T16 and the remaining T12 rows are implementation
tests, not part of the approval corpus.

Findings while authoring:

- **F-c1.** The CLI's usage-error exit is 64, not argparse's 2. Only the red
  state shows it; no corpus answer depends on it.
- **F-c2.** On macOS `tempfile` paths under `/var` are refused by the evolve
  workspace check ("workspace crosses symlink /var", exit 74). pytest's
  `tmp_path` is already resolved; the parity capture script had to `resolve()`.
  This is test plumbing only.
- **F-c3.** Every flag-free `--policy additive` preview of the corpus proposals
  is refused (3) on the base, and every policy-free preview is 0. That is what
  T10 pins. So the parity rows cover both the refusal bytes and the admission
  bytes without the option.
- **F-c4.** `gnd check` over `amounts-only.json` reports the existing
  order-number rule as `vacuous` (exit 2): the checker's vacuity is per
  constraint over empty subjects, as §7 UG2-D4 assumed. Whether a spanning
  constraint with one empty subject gets `pass` (the any/every trap) is still
  measured by C05 and T5 during implementation, not assumed.

## Implementation findings (recorded as found, 2026-11-09)

- **F-i1 (refutes §6.4 wiring, fixed).** The first wiring resolved
  `--check-population` in the CLI with `required=True`, so a missing file exited
  66 before the proposal's replay check: the order §6.4 pins was broken. T14
  caught it. The CLI now checks spelling and containment only
  (`required=False`), and the service read gives 66 after every proposal refusal.
- **F-i2 (seams preserved).** Two existing tests patch internals: MG3's T4b
  patches `EvolutionService._policy_values` as a staticmethod, and MG2's T1a
  swaps `additive_policy_issues` for a lambda with MG2's signature. The first
  wiring made `_policy_values` an instance method and always passed
  `population_outcomes`. Both seams are restored: `_policy_values` stays static
  and takes the population check as a closure, and without the option the
  policy is called exactly as before (AGENTS.md: patch lookups keep their owner).
- **F-i3.** RF2's exit-allocation census requires every `EXIT_*` constant to
  live in `gnd/exits.py`; the new module imports `EXIT_NO_INPUT` and `EXIT_IO`
  and writes band 3 as the literal the evolve lane already uses.
- **F-i4 (departs from §6.7 and plan §4 UG2 wording).** The RF1 harness has, since
  RC1, kept its historical goldens frozen and asserted later CLI changes through
  successor fixtures (`check --rule-ids`, `--baseline`, `--allow-vacuous`,
  `validate --identity`). UG2 follows that convention:
  `tests/fixtures/check-population-cli/expected.json` holds the two actions, their
  indexes, and the help and exit probe per Python minor, captured with
  `GND_RF1_CAPTURE` under 3.11, 3.13 and 3.14. `goldens/`, `goldens.sha256` and
  `MANIFEST_SHA256` do not change. A fresh capture also differs for `gnd check`
  and `gnd validate`, which are already covered by their successors; those
  goldens were not touched.
- **F-i5 (refines §6.1).** The population loader's messages can quote values
  (layer-2 issues name offending data). Re-raising them as `EvolutionError`, as
  §6.1 said, would breach UG-R6 on stderr. `EvolutionPopulationError` carries
  a fixed category message (missing; not a readable regular file; over the cap;
  `model_id` mismatch; not valid, with rule ids only) and its exit band, and is
  mapped by type in `_evolve_error_exit`.
- **F-i6 (deviation in T1).** The family sweep uses uniqueness, mandatory,
  frequency, value and a model-level subset. Ring is replaced by subset: the
  corpus model has no fact type with two roles of one type.
- **F-i7.** Through the CLI, `vacuous` is unreachable (an empty populated
  subject is `uncovered` first) and so is `fail` (alethic constraints are not
  eligible). `test_t4b_vacuous_and_t3b_fail_reachability` pins the precedence;
  the words stay in the vocabulary because they are the checker's.
- **F-i8 (rule 6 measurement).** T15: a constraint with a declared `id` is
  located by its positional reference; `check()` without `--rule-ids` emits
  positional references.
- **F-i9.** `admitted` is computed as the operations refused by the policy
  without outcomes and not refused with them: two calls of the same pure walk,
  so a `pass` on an operation that was never refused is not listed.
- **F-i10.** The RF6 dynamic-candidate census moved (the resolver class, the
  placement recorder, the new literals): successor
  `evidence/UG2/dynamic-query-successor.json` chained after ROF4, 6 rows removed
  and 57 added, the exact query policy unchanged.

## Revision history

- r1, 2026-11-09: first draft. Not reviewed. Not approved.
- r1 approved, 2026-11-09: spec gate `(o)`, "Approve all as proposed". Status line and ruling column only.
- 2026-11-09: corpus authored red; status line replaced and "Corpus authoring" appended.
- 2026-11-09: corpus approved `(o)` ("Approve the corpus"); status line only.
