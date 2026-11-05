# Phase TS2 spec: judgements and rendering

## 1. Status

**r1, draft, 2026-11-05. Not approved.** `auto=false`. No review has run over
these bytes and no implementation file has been created. The owner's
"go ahead" was relayed from the parent session to start drafting; it is not a
reading of this spec and approves nothing in it. The owner gate (§11) asks
for the instrument and the §7 rulings in this session.

## 2. Provenance

- Plan: [type-induction-skills-plan.md](type-induction-skills-plan.md) r1,
  approved `(a1)` 2026-11-05 without plan review
  ([gate](../001-plan-gate.md)); §0, §2.2, §4 TS2, §5, §6, §9 TS2 row, §10.
- TS1: [record](../002-phase-TS1.md) and [spec r2](phase-TS1-spec.md),
  merged to main by PR #88 as `7b171bb2`. TS1 keyed groups `g<n>` (its D6),
  not `{generic, attribute_sha256}`, because 008 omits the attribute digest
  under `customer`. This spec follows TS1, not the plan's §2.2 example.
- Code read at `7b171bb2`:
  - `src/gnd/discover/types.py`: `propose` `:111`, `existing` `:133-135`,
    the `multi_valued` branch `:189-194`, `match` `:206-212`, the operations
    `:213-264`, `drop_last` `:79-85`, `GroupRecord` `:39-61`.
  - `src/gnd/discover/type_evidence.py`: `origins` `:38`, `build_evidence`
    `:111`, `evidence_bytes` `:225`.
  - `src/gnd/discover/service.py`: `discover` `:194`, the type budget and
    `propose` call `:310-316`, `_cmd_discover` `:362`, the written-bytes
    loop and evidence build after it.
  - `src/gnd/commands/discover.py:53-131`.
  - `src/gnd/discover.schema.json`: `fact_type_proposals`, all objects closed.
  - `src/gnd/schema/orm-meta.schema.json`: `provenance_policy`, the
    `induced` branch; `fact_type.provenance` (open object).
  - `src/gnd/model/_induction.py:92-146` (support arithmetic).
  - `src/gnd/evolve/policy.py:302` (`additive_policy_issues`) and
    `src/gnd/evolve/shapes.py` (the shape report is advice).

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| Plan O1, TS2-C2, C3 | `distinct` lifts the once-per-generic limit; `duplicate` reports against `of` | §6.3; T9, T10, T11 |
| Plan O2, O3, TS2-C5 | `many-to-many`: binary fact type, uniqueness spanning both roles, support over pairs, exact repeats as counterexamples, redaction copied | §6.4; T14, T15, T16 |
| Plan TS-R3, TS2-C1 | binding: stale, wrong digest, wrong `kind`, missing, extra or repeated group exit 3 with nothing written | §6.2; T3–T8 |
| Plan TS-R2, TS2-C4 | a verdict the data contradicts exits 3 | §6.3, §6.4; T12, T13, T17 |
| Plan TS-R5, O6, TS2-C6 | a rationale that leaks a value exits 3 unless the mode allows values | §6.5; T19, T20 |
| Plan TS-R4, O8, O13, TS2-C7 | judged proposals stay `induced`/`proposed`/`deontic`; pass `preview --policy additive`; apply; the budget counts them; provenance recomputable | §6.6; T21, T22, T23 |
| Plan O5, TS-R1, TS2-C8 | without the judgement options, parity | §6.7; T26, T27 |
| Plan TS2-C9 | round trip: a fresh evidence file shows the applied fact type's `origin` | §6.6; T24 |
| Plan O14 | redacted roles stay redacted | §6.4; T16 |
| Plan §5 | four `discover` options in all; report keys only under judgement; RF1 goldens | §6.1, §6.7; T25 |
| Plan §9 TS2 row | "Judged rendering, refusals, preview passes"; TS1 gate plus `tests/test_discover_type_judgements.py`, `tests/test_schema_sync.py` | §8 ledger |
| Plan TS-Q2 | does `duplicate` carry a rename of the existing reading | D8 |
| TS1 record, TS-Q3 | what `induced_from` stores under `customer` | D3 |
| TS1 record, refactor deferred | `types._kind` used across modules; no public home for the kind vocabulary | D9 |
| TS1 record, CT4 DateTime kind | DateTime data minted as a String value type | §9, D9 |
| TS1 record, plan repairs | P2, TS-R7 "growth zero", the packaging test name | carried to the close; §8 uses the right test names |
| Plan TS-D4, TS-D9, TS-D10 | where verdicts enter; unjudged groups; contradicted verdicts | ruled as plan proposals (a) here: D1 |
| Plan TS-D5 | vendor the schemas into `gnd-orm-core/references` | D7 |

## 4. Standing rules, bound

- **TS-R1:** without `--type-evidence-in`, `--duplicate-judgements` and
  `--shape-judgements`, `propose` is called exactly as today and nothing new
  runs. T26 compares bytes over the TS1 fixture and modes; T27 is the IK4
  parity run.
- **TS-R2:** the CLI reads verdicts and checks them against facts it already
  computes (statuses, `multi`, candidate lists, `origin`). It never chooses a
  verdict. Every disagreement is a refusal (exit 3), never a repair.
- **TS-R3:** §6.2. The judgements file binds the raw-byte SHA-256 of the
  evidence file. The CLI recomputes the evidence from the model and
  population and refuses when its bytes differ, so the evidence's own model
  and population digests bind the data.
- **TS-R4:** every rendered constraint keeps `source: induced`,
  `status: proposed`, `modality: deontic` and an `induction` block. **The
  judgement record moves to the fact type** (refuted premise P1, §6.6):
  the model schema closes an induced constraint's `provenance` to
  `induction`, `reviewed_in` and `spans`.
- **TS-R5:** §6.5. Evidence and judgements are inputs; the CLI does not
  print verdict text. A refusal names the verdict index and field, never
  the matched text.
- **TS-R6, TS-R8:** no skill in TS2; inapplicable. The judgements files in
  the tests are fixtures written by hand.
- **TS-R7:** `gnd.discover.type_judgements` added to `tools/gnd_layers.json`,
  lane `discover`, zero allowances. Model reads through `ModelIndex`. The RF6
  live query count and the dynamic-read inventory are measured before and
  after; growth in the inventory gets a successor file as in TS1 (I7 there).
  No downstream application is named.
- **Standing rule 1 (totality):** the judgements reader is total over any
  bytes: the size cap is applied to the read (§6.2), a strict JSON parse
  refuses `NaN`, infinities, duplicate keys and very long integers, deep
  nesting is caught, and the schema is closed. Every failure is
  `TypeJudgementError` (exit 3). Hostile cases in T2.
- **Standing rule 2 (algorithm bound):** the evidence is recomputed once.
  Verdict checks are linear in verdicts plus candidates. The rationale scan
  (§6.5) is linear in rationale bytes per verdict, using one compiled
  alternation over the forbidden texts, not one search per text: its cost is
  bounded by the judgements cap times the automaton. T28 is a time-bound
  test: 20,000 groups, rationales at the cap.
- **Standing rule 3 (validation order):** §6.1 states it per boundary, and
  T29 pins it by source order and by paired cases.
- **Standing rule 4 (one walk):** the disclosure decisions (`show_values`,
  `show_digests`) are still taken once in `commands/discover.py`. One
  function decides each verdict's outcome; `propose` calls it for every
  group, rather than one branch per status.
- **Standing rule 5 (one home):** the judgements format's normative home is
  `src/gnd/type-judgements.schema.json` plus one section in
  `docs/reference/discover.md`. The rationale rule's home is that section.
- **Standing rule 6 (measure):** P1 was settled by reading the shipped
  schema; T21 proves it by loading a judged model.

## 5. Goal

`gnd discover MODEL POP --out P --report R --families fact-type
--type-evidence-in E --duplicate-judgements J [--shape-judgements S]` exits
0 when every verdict is bound, complete and consistent with the data, and
writes a proposal in which each `distinct` group is proposed, each
`duplicate` group is reported against its named fact type, and each
`many-to-many` group is proposed as a binary fact type with a uniqueness
spanning both roles. `gnd evolve preview --policy additive` exits 0 on that
proposal and `gnd evolve apply` applies it. Every refusal exits 3 with
nothing written. Runs without the new options are unchanged. The focused
gate exits 0.

## 6. Design

### 6.1 CLI and validation order

`commands/discover.py` gains three options (the fourth, `--type-evidence`,
shipped in TS1):

- `--type-evidence-in PATH`: "fact-type family: the evidence file the
  judgements bind";
- `--duplicate-judgements PATH`: "fact-type family: read duplicate verdicts
  (needs --type-evidence-in)";
- `--shape-judgements PATH`: "fact-type family: read multi-valued shape
  verdicts (needs --type-evidence-in)".

Order, each step before the next (standing rule 3):

1. **Usage, 64.** Any of the three without `--families fact-type` (the
   existing family-flags message, extended to name them). Either judgements
   option without `--type-evidence-in`, or `--type-evidence-in` without
   either. `--type-evidence` together with `--type-evidence-in`. Paths: the
   distinct-paths check covers every given path (outputs and inputs).
2. **Paths.** Inputs: MODEL, POPULATION, evidence and judgements files must
   be regular files (66). Outputs as today (74 symlink, 11 existing).
3. **Judgements, 3.** Each judgements file is read under the cap, parsed and
   schema-checked; `kind` must match its option; `evidence_sha256` must
   equal the SHA-256 of the evidence file's raw bytes. The evidence file is
   read under `MAX_EVIDENCE_BYTES` + 1. No model or population is read yet,
   so a wrong file refuses cheaply.
4. **Model and population, 3,** as today, then `generic_declarations`.
5. **Recompute, 3.** The deterministic run (§6.2) and its evidence bytes;
   unequal bytes exit 3 ("the evidence does not match this model and
   population under these settings"). `truncated_groups > 0` exits 3 (D5).
6. **Coverage and verdicts, 3.** §6.3 and §6.4, in verdict order; then the
   rationale scan (§6.5).
7. **Render,** then the written-bytes trim, then writes in today's order.
   No evidence file is written under judgement.

### 6.2 Binding and the deterministic run

`type_judgements.py` (new, about 220 lines):

```python
FORMAT = "gnd-type-judgements/1"
MAX_JUDGEMENTS_BYTES = 10 * 1024 * 1024
MAX_RATIONALE_CHARS = 2000

class TypeJudgementError(ValueError):
    """A judgements file that is unbound, incomplete or contradicted (exit 3)."""

@dataclass(frozen=True)
class Verdict:
    group: int              # position in the evidence, from "g<n>"
    verdict: str            # distinct | duplicate | many-to-many | skip
    of: str | None          # duplicate only
    kind: str               # "duplicates" | "shapes"

@dataclass(frozen=True)
class Judgements:
    evidence_sha256: str
    duplicates_sha256: str | None
    shapes_sha256: str | None
    skills: dict[str, str]  # kind -> judge.skill
    verdicts: dict[int, Verdict]

def read(path: Path, *, kind: str, evidence_raw: bytes) -> dict[str, Any]: ...
def bind(evidence: dict[str, Any], files: list[dict[str, Any]], *,
         show_values: bool, show_digests: bool,
         forbidden: Callable[[], Iterable[str]]) -> Judgements: ...
```

**The deterministic run.** The evidence describes the family's outcome
without judgement, including `over_budget` from the written-bytes trim. So
the service first runs exactly the TS1 path: `propose` without verdicts, the
written-bytes trim on that proposal, `build_evidence`, `evidence_bytes`. The
result must equal the evidence file's raw bytes. It then runs `propose`
again with the verdicts and trims that proposal. The cost is one more
`propose` and one more serialisation, both already bounded (TS1 T20).

The comparison is over bytes, so it also refuses evidence written under
other settings (`min_support`, `show_values`, `show_digests`): those are in
the bytes. The message names the first top-level key that differs when it is
one of `model_sha256`, `population_sha256`, `min_support`, `show_values`,
`show_digests`, else "groups differ"; no value is printed.

**The judgements file**, schema `src/gnd/type-judgements.schema.json`
(Draft 2020-12, closed objects):

```json
{"format": "gnd-type-judgements/1", "kind": "duplicates",
 "evidence_sha256": "<64 hex>",
 "judge": {"skill": "gnd-judge-fact-types", "agent": "<free text, at most 200 chars>"},
 "verdicts": [
   {"group": "g0", "generic": "item_has_attribute", "verdict": "duplicate",
    "of": "item_has_attribute_induced_0", "rationale": "..."},
   {"group": "g1", "generic": "item_has_attribute", "verdict": "distinct",
    "rationale": "..."}]}
```

- `kind: "duplicates"`: `verdict` in `distinct`, `duplicate` (needs `of`).
- `kind: "shapes"`: `verdict` in `many-to-many`, `skip` (D2).
- `group` matches `^g(0|[1-9][0-9]*)$`; `generic` must equal the evidence
  group's `generic` (a cheap misalignment check); `rationale` is 1 to
  2,000 characters; `judge.skill` matches the packaged-skill name pattern.
- **Coverage (plan TS-D9 (a)).** A duplicates file has exactly one verdict
  for each evidence group whose status is `proposed`, `shape_match` or
  `over_budget`; a shapes file for each `multi_valued` group. A missing,
  extra, repeated or ineligible group exits 3, naming the group id.
- **Both files given:** their eligible sets are disjoint, so they never
  judge one group twice.

### 6.3 Duplicate verdicts

Checked against the evidence group (TS-R2):

- `duplicate`: `of` must be the `fact_type` of one of that group's
  candidates in the evidence; otherwise 3. A candidate dropped by
  `truncated` cannot be named; the message says so.
- `distinct` on a group with a candidate whose `origin.generic` equals the
  group's `generic` and whose `origin.same_attribute` is true exits 3: that
  attribute was already induced into that fact type (D4). The same rule
  applies to `many-to-many` (§6.4).

Rendering, in `propose` through one verdict hook (`verdicts: dict[int,
Verdict] | None`, keyed by the group's position, which the evidence's
`g<n>` equals because grouping does not depend on verdicts):

- `distinct`: the group is rendered as a proposed group today is, skipping
  the signature match. Its status before judgement may be `proposed`,
  `shape_match` or `over_budget`; the budget then decides as for any group.
- `duplicate`: the group is not proposed; it is appended to
  `shape_matches` as `{generic, existing: of, judged: true}` plus
  `attribute_sha256` when `show_digests`.
- A judged proposed entry carries `judged: true` in `proposed[]` (D6).

### 6.4 Shape verdicts

- `many-to-many` on a `multi_valued` group renders:
  - the value type exactly as the functional path chooses it (an existing
    value type, or a minted `<id>_value` with the observed primitive);
  - the fact type `<generic>_induced_<n>` (the existing id and clash rule),
    the same placeholder reading, roles `entity` and `value`, each with
    `redact: true` when the generic's role is redacted (CT4 F4);
  - a uniqueness `roles: [entity, value]`, `source: induced`,
    `status: proposed`, `modality: deontic`, with `induction` using the run's
    envelope and: `support` `{numerator: distinct (entity, value) pairs,
    denominator: rows}`; `examples` the first row id of each distinct pair,
    at most 256; `counterexamples` the row ids of exact repeats (each row
    after the first of its pair), at most 32. The loader's arithmetic
    (`_induction.py:135-146`) holds: examples ≤ pairs, counterexamples ≤
    rows − pairs.
  - The report entry is the proposed entry with `support` as above,
    `judged: true` and `shape: "many-to-many"`.
- `skip`: not proposed; counted in `skipped.judged_skip`, not in
  `multi_valued`.
- `many-to-many` is refused (3) on a group that is not `multi_valued` (by
  coverage) and under D4's origin rule.
- The spanning uniqueness states that each (entity, value) pair is recorded
  once. It states nothing functional. Exact repeats in the population are
  its counterexamples and would be its violations if confirmed.

### 6.5 Rationale and free text (TS-R5)

When `show_values` is false (unset without the flag, and `customer`), each
`rationale` and `judge.agent` is scanned, case-folded, for these texts:

- the text form of every group's attribute value, which the evidence hides;
- the text form of every distinct value-role value of every group;
- under `customer` only, every group's 64-hex attribute digest, which the
  evidence withholds there.

A text matches as a whole token: the characters on either side are not
letters, digits or `_`. A match exits 3 with "verdict N: rationale names a
population value"; the text is never printed. Texts that occur as whole
tokens in the model file's bytes are exempt, because the judge reads the
model and those texts are already model text (D10). Under `internal`, or
with `--show-values` when allowed, nothing is scanned.

**Limit:** this catches exact text only. A paraphrase, a spelling change or
an encoding escapes it. Docs state the skill-level rule as the main control.

### 6.6 Provenance and the round trip

Refuted premise P1: plan TS-R4 and §2.2 put `provenance.judgement` on the
constraint, but an induced constraint's `provenance` is closed to
`induction`, `reviewed_in` and `spans` (`orm-meta.schema.json`,
`provenance_policy`). The loader would refuse the proposal. Repair within
TS2-C7: both records go on the **fact type**, whose `provenance` is an
open object:

```yaml
provenance:
  induced_from: {generic: item_has_attribute, attribute_sha256: <64 hex>}
  judgement:
    evidence_sha256: <64 hex>
    judgements_sha256: <64 hex>   # the file that decided this group
    kind: duplicates               # or shapes
    verdict: distinct              # or many-to-many
    skill: gnd-judge-fact-types
```

`judgement` is written for every judged proposal in every mode. It holds
digests of files the caller wrote and a verdict, no population value.
`induced_from` follows D3. Its digest is the one TS1 validates and reads
back as `origin`, so after `gnd evolve apply` a fresh `--type-evidence` run
shows the new fact type as a candidate with `origin.same_attribute: true`
(T24), and D4 then refuses a second `distinct` for the same attribute.

The proposal's `rationale` names the judgements: "gnd discover: N candidate
operations observed in POP; fact-type verdicts from J". The report's
`fact_type_proposals` gains `judgements: {evidence_sha256,
duplicates_sha256, shapes_sha256}` (null for a file not given), present only
under judgement.

### 6.7 Report schema and parity

`discover.schema.json`, additive only:

- `proposed[]` items: optional `judged` (const true), optional `shape`
  (const `many-to-many`);
- `shape_matches[]` items: optional `judged` (const true);
- `skipped`: optional `judged_skip` (integer ≥ 0);
- `fact_type_proposals`: optional `judgements` as above.

A report from a run without judgement has none of these keys, so old
reports and unjudged runs validate unchanged. TS1's evidence schema does
not change.

## 7. Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 (plan TS-D4, D9, D10) | Where verdicts enter; unjudged groups; contradicted verdicts | (a) judgement files read by `gnd discover`, full coverage required, contradictions exit 3; (b) skills write evolve operations, or fall back to the signature rule, or count and skip | (a), the plan's proposals |
| D2 | Shapes vocabulary | (a) `many-to-many` and `skip` only: a "the extra values are errors" outcome is the skill's route to fixing the population, recorded as `skip`; (b) keep `functional` as the plan wrote it: every eligible group is `multi_valued`, so it would always exit 3, a verdict that can never be accepted | (a); refuted premise P2. TS2-C4 is kept as "`functional`, or any word outside the vocabulary, exits 3" |
| D3 (TS-Q3) | `induced_from` under `customer` | (a) write it anyway: the model is the caller's file, but it puts a guessable digest of the attribute name into the model, which 008 removed from reports; (b) omit `induced_from` under `customer`: later customer runs have no `origin` for this fact type and the judge relies on overlap counts, and D4 cannot fire; (c) write a reference to the evidence digest and group id: not recomputable once the population changes | (b). Every judged proposal still carries `judgement`. T24 runs under `internal`; T24b shows `origin: null` under `customer` |
| D4 | Re-inducing an induced attribute | (a) `distinct` or `many-to-many` on a group with a candidate whose origin names the same generic and attribute exits 3: a fact the CLI already computes, not a judgement of meaning; (b) accept it and let review catch the duplicate | (a) |
| D5 | Truncated evidence | (a) `truncated_groups > 0` exits 3: some groups cannot be judged, and full coverage (D1) cannot hold; (b) groups absent from the evidence keep the signature rule: a quiet partial judgement | (a). Candidate truncation (`truncated > 0`) is allowed; `of` must name a listed candidate |
| D6 | Marking judged entries in the report | (a) `judged: true` on judged `proposed[]` and `shape_matches[]` entries, plus `judgements` digests; (b) only `shape_matches[]`, as the plan's §5 says: a reader cannot tell a judged proposal from a deterministic one | (a); additive to plan §5 |
| D7 (plan TS-D5) | Vendor the schemas into `gnd-orm-core/references` | (a) in TS2, now that both exist: moves the packaged-skill file inventory pin in a phase that ships no skill; (b) in TS3, beside the first skill that links them | (b) |
| D8 (TS-Q2) | A rename on `duplicate` | (a) no: renaming a reading is `gnd-model-evolve`'s operation, and the judge may propose it in prose; (b) a `rename` field the CLI renders as a MODIFY: a breaking-class change the additive policy refuses | (a) |
| D9 | The kind vocabulary and the DateTime defect | (a) move `_kind`, `_PRIMITIVE_FOR_KIND` and `_primitive_of` to a public home in `discover/types.py` (names without the underscore), behaviour unchanged, in the refactoring step; leave the DateTime defect to maintenance, because fixing it changes default output and TS-R1 forbids that here; (b) fix both in TS2 with a stated parity exception | (a) |
| D10 | Rationale exemption for model text | (a) exempt texts that are whole tokens of the model bytes: the judge reads the model, so quoting a reading is not a leak; (b) no exemption: a rationale that quotes an existing reading whose word equals an attribute name is refused | (a) |
| D11 | Approval instrument | (a) prose; (b) a committed fixture corpus with narrated outcomes first | §11 |

## 8. Tests and verification selection

File `tests/test_discover_type_judgements.py` unless stated. Fixture: TS1's
model and population (generic `item_has_attribute`; applied
`item_has_attribute_induced_0` from `size`; `colour` functional; `tag`
multi-valued with one exact repeat; `rare`; `mixed`), plus a canary
attribute and a canary value. Judgements files are written by the tests.

| # | Case | Criterion | Expect |
|---|---|---|---|
| T1 | each new option without the family; a judgements option without `--type-evidence-in`; `--type-evidence-in` alone; with `--type-evidence`; a repeated path | §6.1 | 64 |
| T2 | hostile judgements: not JSON, `NaN`, duplicate key, 10,000-digit integer, 100,000-deep nesting, over the cap, extra key, wrong `format` | rule 1 | 3, nothing written |
| T3 | `evidence_sha256` not the evidence file's digest | C1 | 3 |
| T4 | stale evidence: population changed after the evidence was written | C1 | 3, message names `population_sha256` |
| T5 | evidence written under another `min_support`, and under another mode | C1 | 3, message names the key |
| T6 | `kind` does not match its option | C1 | 3 |
| T7 | missing, extra, repeated and ineligible group; `generic` mismatch | C1 | 3, names the group id |
| T8 | evidence with `truncated_groups > 0` | D5 | 3 |
| T9 | `distinct` on a `shape_match` group is proposed | C2 | 0 |
| T10 | `distinct` on `proposed` and `over_budget` groups; the budget then decides | C2, C7 | 0 |
| T11 | `duplicate` on a group with no equal signature is reported against `of`, `judged: true` | C3 | 0 |
| T12 | `of` not a listed candidate, including one dropped by `truncated` | C3 | 3 |
| T13 | `distinct` on the `size` group whose candidate has `same_attribute` true | D4 | 3 |
| T14 | `many-to-many` on `tag`: two roles, uniqueness over both, support pairs/rows, examples, the repeat as counterexample, `shape` in the report | C5 | 0 |
| T15 | `skip` counts `judged_skip`, `multi_valued` not incremented | C5 | 0 |
| T16 | redacted entity role: the many-to-many fact type copies `redact` | C5, O14 | 0 |
| T17 | `functional` and any other word in a shapes file; `many-to-many` in a duplicates file | C4, D2 | 3 |
| T18 | both files at once; disjoint coverage | §6.2 | 0 |
| T19 | rationale holding the canary attribute, a canary value, or (under `customer`) a digest: refused under `customer` and unset-without-flag; accepted under `internal` | C6 | 3 / 3 / 0 |
| T20 | rationale quoting an existing reading whose word equals an attribute value (D10); a canary inside a longer word | C6 | 0 / 0 |
| T21 | every judged proposal loads as a model candidate; `gnd evolve preview --policy additive` exits 0 | C7 | 0 |
| T22 | `gnd evolve apply` applies it; `gnd validate` of the result exits 0 | C7 | 0 |
| T23 | `induced_from` and `judgement` present and recomputable from the files' bytes | C7 | 0 |
| T24 | round trip under `internal`: a fresh `--type-evidence` shows the new fact type with `origin.same_attribute: true`; a second `distinct` exits 3 | C9, D4 | 0, then 3 |
| T24b | the same under `customer`: no `induced_from`, `origin` null, `judgement` present | D3 | 0 |
| T25 | `tests/test_rf1_cli_pins.py`: `discover` help and usage re-pinned; the diff is the three options | §5 | gate |
| T26 | without the judgement options: `--out`, `--report` and `--type-evidence` bytes equal to `7b171bb2` over the TS1 fixture, three modes | C8 | equal |
| T27 | the CT4 parity script over the IK4 corpus, without the options | C8 | equal to `7b171bb2` except the usage text |
| T28 | time bound: 20,000 groups judged, rationales at the cap, values at the population cap | rule 2 | under a stated ceiling |
| T29 | order: a judgements digest mismatch with a malformed model exits 3 from step 3 (message), not from the model; an existing `--out` with a bad judgements file exits 11 | rule 3 | 3 / 11 |
| T30 | every written report validates against `discover.schema.json`; every judgements fixture the tests accept validates against its schema | all | valid |

### Selection ledger

| Obligation | Disposition | Command or evidence | Input boundary | Justification | Invalidation |
|---|---|---|---|---|---|
| Direct TS2 cases | run | `uv run pytest -q tests/test_discover_type_judgements.py` exit 0 | `types.py`, `type_judgements.py`, `type_evidence.py`, `service.py`, `commands/discover.py`, both schemas, the fixture | every new branch has a case | any change to those files |
| Plan §9 TS2 row (TS1 gate) | run | `uv run pytest -q tests/test_discover_type_evidence.py tests/test_discover_fact_type_family.py tests/test_discover.py tests/test_evolve_additive_policy.py tests/test_evolve_shape_matches.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py` exit 0 | as above plus RF1 goldens, layer map, disclosure docs | the family, evidence, pins, layers, RF6 and disclosure consumers | changes to discover, evolve, disclosure, layer map |
| Plan §9 schema sync | run | `uv run pytest -q tests/test_schema_sync.py` exit 0 | vendored model schemas | named by the plan | schema edits |
| Packaging of the new runtime schema (TS1 I8) | run | `uv run pytest -q -m distribution tests/test_public_built_inventory.py::test_wheel_carries_every_vendored_runtime_schema` exit 0, after listing it in `tests/support/runtime_schema_inventory.py` | the wheel | the schema ships | packaging changes |
| Parity T27 | run | `evidence/CT4/capture_parity.py`, compared with TS1's `parity-after.json` | discover CLI | TS-R1 | any discover change |
| Mutations | run | one mutation per new refusal and rendering branch, as TS1 did | new branches | the shipment rule | — |
| Docs | run | `uv run zensical build --strict`; `uv run python tools/check_docs.py site` exit 0 | `docs/reference/discover.md`, release notes | the TS2 doc section | doc edits |
| Broad historical lanes (`evidence or census`) | cadence | milestone close or explicit owner request | n/a | outside TS2's impact closure | owner request |

### Implementability sweep

| Requirement | Can some implementation meet it? |
|---|---|
| Recompute the evidence exactly | Yes: the TS1 path is deterministic over model, population and settings, and the service already runs it; T26 pins its bytes. |
| `g<n>` maps to the group under judgement | Yes: groups are formed in row order before any status is set (`types.py:151-180`); verdicts change statuses only. |
| A `distinct` group on an equal signature passes the additive policy | Yes: `additive_policy_issues` admits any fact-type ADD (`policy.py:368-371`); the shape report is advice (`shapes.py:1-10`). |
| The judgement record is schema-valid | Not on the constraint (P1); yes on the fact type, whose `provenance` is an open object. |
| Many-to-many support passes the loader | Yes: numerator = pairs ≤ rows; examples ≤ pairs; counterexamples ≤ rows − pairs = exact repeats. |
| A `functional` shapes verdict can be accepted | No, as the plan wrote it (P2); D2 removes it. |
| The rationale scan stays linear | Yes, with one compiled alternation (or Aho–Corasick) built once per run; the token-boundary test is a per-match check. |
| Full coverage over truncated evidence | No; D5 refuses it. |

## 9. Out of scope for TS2

The skills (TS3, TS4) and vendoring the schemas (D7). The how-to (TS5).
Shapes beyond binary functional and many-to-many. Fixing the CT4 DateTime
value-type defect (D9; it changes default output). The malformed-YAML
traceback (maintenance). Migrating rows into induced fact types. A Python
API (plan TS-D8). Any judgement inside the CLI.

## 10. Size

About 330 source lines (`type_judgements.py` 220, `types.py` +60, service
and CLI +50), a 90-line judgements schema, 25 lines of report schema, and
about 750 test lines.

## 11. Approval instrument

The plan's review-convergence reference defaults to corpus-first for a
serialized format and an exit-code contract, and TS2 is both. The argument
for prose: the only writers of the format are this milestone's two skills,
T30 validates every file the tests accept, and §8 gives every refusal a
case with its exit. The argument for a corpus: TS2's refusals are many and
order-dependent, and a narrated corpus would let the owner read each outcome
before implementation. The owner chooses. Optional spec review panel:
omitted unless asked for.

## 12. Implementation findings

None yet.
