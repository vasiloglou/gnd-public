# Phase UG3: The unattended source header across rounds

## 1. Status line

**Corpus authored and red, 2026-11-09: waiting for the owner's corpus approval.**
The corpus (§11) is committed before any source edit: 23 cases (A1 to A6b, B1 to
B8 with B3, B5 and B7 split), each red for the intended reason except A1, which
asserts that nothing is added and so holds on the base too. The flag-free
baselines (A10, B9) and the B7 control are green. See "Corpus authoring" below.
No source file is edited. Implementation starts only when the owner approves the
corpus.

Earlier status, kept: Spec gate `(o)`, 2026-11-09: approved as proposed.** Asked "How do you rule on
UG3-D1 to UG3-D14?", the owner replied, quoted: "approved". Every decision in §7 is
ruled as its **(proposed)** reading, including UG3-D14 (a): the approval
instrument is **corpus-first**. Approved bytes: r1 at `e3b95610` (sha256
`6c65d9f5…`). Next: the corpus and its red harness (§11), committed before any
source edit and put to the owner. No source file is edited until the corpus is
approved.

Earlier status, kept: Draft r1, 2026-11-09: awaiting owner review.

## 2. Provenance

- Derived from [the plan](unattended-model-growth-plan.md) r1.2:
  - §0 (UG-R1 to UG-R11)
  - §2.3 (UG3 shape, proposed): (i) declaring a document, ruled UG-D9 (b); (ii) failing closed on unchecked spans, ruled UG-D3 (c)
  - §3 (artifact homes; landing order "UG2, then UG3 (ii), then UG3 (i)")
  - §4 UG3 (named criteria UG3-C1 to C7, proposed)
  - §5 (surfaces), §6 (risks) and §9 (the UG3 row)
  - §10: UG-Q2 (names) and UG-Q5 (schema version) are open for this spec
- Prior records:
  - [002-phase-UG1.md](../002-phase-UG1.md). Its matrix row "74/104 a round declares its own new document" is `open`. The gap is pinned by `test_t12_declaring_a_document_inside_a_round_is_refused_but_before_it_is_admitted` (`tests/test_unattended_model_growth_acceptance.py:567`). That test's helper `_declare` (line 144) is the out-of-band edit, and its docstring says UG3 (i) retires it.
  - [003-phase-UG2.md](../003-phase-UG2.md), merged in PR 147 at `5c6a0c5f`. UG2 used the RF1 successor-fixture convention (`tests/fixtures/check-population-cli/expected.json`) and an RF6 dynamic-candidate successor. UG3 repeats both. Open rows UG2-Q1 to Q3 are carried, not owned.
- Code read on `5c6a0c5f` (main after PR 147), the base of this branch. Two read-only readers mapped the sites, and the author re-read every site this spec names. Line numbers below are at `5c6a0c5f`.
- **No review has run over these bytes.** A review is the owner's call at the gate (§11).

## 3. Obligations (the step 0 harvest)

| Row | Obligation (source) | Discharged in this spec |
|---|---|---|
| O14 | Spans over a declared document that was not supplied are not re-hashed, so an unattended gate can pass having checked nothing (MG5-Q3; UG-D3 (c)) | Part A (§6.1, §6.2); A1 to A12 |
| O20 | A round cannot declare its new document through `evolve` (UG-D9 (b)) | Part B (§6.3 to §6.6); B1 to B16 |
| UG3-C1 | Counts are reported with documents supplied and not supplied, with one unchecked-span case for each span location (element spans, constraint spans, `sample_spans`) | A2a, A2b, A2c |
| UG3-C2 | The opt-in flag exits 3 on an unchecked span, including with no `--document`, and 0 when every span is covered | A4, A5, A3 |
| UG3-C3 | Flag-free parity: default output equals the baseline except the one carved-out `warnings` entry on a run that leaves a span unchecked | A10 (baseline captured on `5c6a0c5f`; see §4 UG-R1) |
| UG3-C4 | No document text in any output (MG-R5) | A9 |
| UG3-C5 | A round that appends a declaration and adds elements citing it previews and applies under `--policy additive` with exit 0 | B1 |
| UG3-C6 | A modified or removed declaration is refused with a named cell | B2, B3 |
| UG3-C7 | A proposal without the new locator keeps its bytes and digest, compared to golden bytes captured before the change | B9 (UG1 pinned no golden proposal bytes, so B9 captures them on `5c6a0c5f` before the first source edit; recorded as a finding about the plan's "UG1 pins them") |
| Plan §2.3 (ii) | Counts cover element spans, constraint spans and `sample_spans`. The spec defines how malformed, undeclared-document and supplied-but-undeclared spans are counted. Strict with no `--document` exits 3 for an unattended model with any span; against a model without the mode it is a pinned no-op | §6.1 counting table; A5, A6, A11, A12 |
| Plan §2.3 (ii) | Counts as one `warnings` entry, present only when a span is unchecked. If "counts always reported" cannot be met without a report-version bump, return to the owner with that cost | UG3-D3, which puts that cost to the owner |
| Plan §2.3 (i) | Define "modified", "removed", "reordered" and "duplicate". Touch `StableLocator`, the operation validator, `_operation_references`, `_apply_declared_operations`, `_operation_target`, the policy walk, the blast-radius builder, the contract "Stable locators", and discover's `candidate_document` | §6.3 to §6.6 |
| Plan §2.3 (i), three traps | The policy admits an unknown locator kind; `BlastRadiusReport.entries` has `min_length=1`; `schema_version` is `Literal[1, 2, 3]` with closed readers | §6.5 (fail-closed default, B11); §6.4 (the always-present `model` entry, B14); UG3-D10 |
| UG-Q2 | Flag name | UG3-D2 |
| UG-Q5 | Which schema versions carry the locator; what old readers do | UG3-D10; release note §6.7 |
| Plan §4 UG3 | The release-note entry, including the forward-incompatibility for old readers, ships with UG3 | §6.7 |
| Plan §4 UG3 (ii) | Re-pin the `gnd validate` help and exit goldens, `tree.json`, `goldens.sha256` and `MANIFEST_SHA256` | §6.7: through a successor fixture, as RC1 and UG2 did; historical goldens untouched (UG3-D13) |
| Plan §3 | `_unattended.py` stays where it is (it is exempt from the RF6 query scan by path; `model/` has per-file ceilings) | §6.1; G-rf6, G-packages |
| Plan §3 serial landing | Each source part appends to the RF6 dynamic-candidate chain | §6.7; G-rf6 |
| Plan §6 "a new locator widens the closed proposal contract" | State the schema-version decision; prove old proposals parse and digest unchanged | UG3-D10; B9 |
| Plan §5 surfaces | `representation-format.md` "Unattended source" (Part A, normative); evolution contract "Stable locators" and "Additive policy" (Part B, normative); `docs/reference/cli.md`; `docs/release-notes.md` | §6.7 |
| UG1-T12 | Its (a) leg says UG3 (i) "will change this message and must edit this assertion knowingly" | Measured: T12 (a) declares the document in the candidate **without an operation**, so the replay still refuses it and the message does not change. The assertion stands. B10 keeps it and B1 adds the positive case. Recorded as a finding about the test comment |
| UG2-Q1, Q2, Q3; UG-Q6, Q7; MG3-Q2 (O15) | inherited | carried, not owned (§9) |

## 4. The standing rules, bound to this phase

**Plan §0:**

| Rule | Discharge |
|---|---|
| UG-R1 defaults do not move | **Part A:** without the strict flag, a run with no `--document`, or with every span re-hashed, is byte-identical (stdout, stderr, exit) to `5c6a0c5f`. The one carve-out: a `--document` run that leaves a span unchecked gains one `warnings` entry (A10). **Part B:** a proposal without the new locator keeps its bytes, `proposal_sha256` and preview bytes. No blast-radius entry is added for existing documents (§6.4), so unattended models' previews do not move (B9) |
| UG-R2 nothing confirms | Neither part writes provenance. The locator carries only `{sha256, label}` |
| UG-R3 evidence licenses, a human admits | Part B: a declaration is admitted as an append, never relabelled. A label change stays a reviewed proposal (`source_document.modify` is refused under `--policy additive`) |
| UG-R4 one walk, one home | **Part A:** one span walk, `_iter_unattended_spans`, shared by the re-hash and the counts (§6.1). **Part B:** the additive policy stays one walk and gains one branch. "Unattended source" in `representation-format.md` is the home for Part A; the evolution contract is the home for Part B |
| UG-R5 digest-bound | Part B: the declaration is an operation inside the digest-bound proposal (`proposal_sha256`), replayed and checked for equality like every other operation. Part A reads no new input |
| UG-R6 disclosure | Part A: messages carry counts of spans, paths and digests, never document text (A9). Part B: a label is model text the operator wrote, already shown in previews today |
| UG-R7 totality and cost | **Part A:** no new reader. The `--document` reader is unchanged and already total (MG5). Counting is the same O(spans) walk (A13). **Part B:** the locator is a closed Pydantic model, so hostile shapes exit 3 (B5, B6, B15). Replay stays linear (B16) |
| UG-R8 layering and query policy | Part A stays in `model/_unattended.py` (289 lines, under the 5000-line `model/*.py` ceiling, exempt from the RF6 query scan by path) and `commands/checking.py`. Part B stays in the `evolve` lane. No new module, so `tools/gnd_layers.json` does not change. The RF6 counted reads are measured at execution (G-rf6). If a new counted read appears, it goes through an existing resolver, as in UG2 |
| UG-R9 installer-owned links | No packaged file is added |
| UG-R10 anonymity | Neutral fixtures (UG1's lending domain). The record repeats UG1's digest-set scan |
| UG-R11 approval and protection | `auto=false`; topic branch `claude/ug3-spec` and a PR; merge only on the owner's word |

**Project standing design rules (`project.md`):**

| Rule | Discharge |
|---|---|
| 1 Totality belongs to the function | The new counting function and the locator validator are total over arbitrary model and proposal shapes. A non-mapping span is counted as unchecked; a locator with a bad `sha256` is a validation error, exit 3 (A12, B5) |
| 2 A cap bounds the document, not the algorithm | Counting is one pass over the spans; replay of a declaration is O(declared documents). A13 and B16 count visits with spies for 1, 10 and 100 spans or operations |
| 3 Validation order is pinned per boundary | §6.2 (validate) and §6.5 (evolve) state the order. A11 and B4 pin the cases where two orders would exit with the same code |
| 4 One walk for N kinds | Part A: one span walk covers all three span locations (A2a to c). Part B: one policy walk, with an explicit branch for every locator kind and a fail-closed default (B11) |
| 5 Normative prose has one home | Part A: "Unattended source". Part B: the contract's "Stable locators" table and the "Additive policy" matrix. `cli.md`, the release note and `evolve-policy.md` cite them |
| 6 Contested representation by measurement | Whether the counts can ride in the existing `warnings` list without a report-version bump is settled by A12: the payload with the new entry validates against `report.schema.json` `$defs.issue` |

**Failure classes this project has committed:**

- *A guard that goes quiet:* the exact defect O14 names. A6 pins that strict mode against a model without the mode changes nothing, and A5 shows that strict mode with no `--document` refuses rather than passing vacuously.
- *Any versus every:* A2 supplies one of two declared documents. A reading "some span was checked" would pass it; the counts and A4 tell the readings apart.
- *A declared branch with no failing case:* malformed spans are unreachable through the CLI, because layer one (U6, U7) refuses them before `--document` runs. They are covered at the function (A12b), and the unreachability is recorded, not assumed.
- *A fall-through that admits:* the locator `else` branches at `models.py:343` and `service.py:904-914` treat any non-element, non-role, non-identity locator as a constraint. Each gets an explicit branch (B11, B12).

## 5. Goal

**Part A.** `gnd validate MODEL --document PATH` over an unattended model exits as today. When at least one span was not re-hashed, its `warnings` gain one `unattended:spans-unchecked` entry giving the number of spans not re-hashed and the total. With the new flag `--require-documents`, the same condition exits 3 with that entry as an issue. That includes a run with no `--document`, which leaves every span unchecked. Without the flag, a run with every span re-hashed, or with no `--document`, is byte-identical to `5c6a0c5f`.

**Part B.** A proposal can carry `add` operations on a new `source-document` locator that append `{sha256, label}` to `source.documents`. `gnd evolve preview --policy additive` admits them (exit 0), and `apply` publishes them (exit 0). A `modify` or `delete` of a declaration is refused under the policy with the cell `source_document.modify` or `source_document.delete` and its operation index (exit 3). A proposal without the locator keeps its bytes and digest.

## 6. Design

### 6.0 Reuse (component index, `dev/components/`)

| Capability | Searches | Found | Decision |
|---|---|---|---|
| Counting spans re-hashed vs not | `search unattended span document`; `search span rehash document digest` | `gnd.model._unattended.unattended_span_issues` and `_iter_unattended_spans` | **adapt**: one private walker returns issues and counts; the public function keeps its signature |
| Carrying counts in the validate payload | `search validate warnings payload` | `ValidationIssue` in the existing `warnings` list; `infra.text_output` prints `WARNING at …` | **reuse** the list and printer; no new payload key |
| A new evolve operation locator | `search evolve locator stable`; `search source documents header` | `evolve.schema` (`StableLocator`), `ModelIdentityLocator` as the closest precedent (a header field, fixed shape) | **adapt**: a fifth union member modelled on `ModelIdentityLocator`; no new module |

### 6.1 Part A: `src/gnd/model/_unattended.py` (about +45 lines)

One private walker, shared by both public functions:

```python
@dataclass(frozen=True)
class SpanCoverage:
    total: int        # every span _iter_unattended_spans yields
    rehashed: int     # spans whose document was supplied and whose shape is valid
    @property
    def unchecked(self) -> int: return self.total - self.rehashed

def _span_walk(doc, documents) -> tuple[list[ValidationIssue], SpanCoverage]: ...
def unattended_span_issues(doc, documents) -> list[ValidationIssue]   # unchanged signature and behaviour
def unattended_span_coverage(doc, documents) -> SpanCoverage | None   # None when source.mode is not "unattended"
```

`unattended_span_coverage` is exported from `gnd.model` beside `unattended_span_issues` (`model/__init__.py:39`).

**Counting table (normative; its home is "Unattended source"):**

| Span | Counted as | Reachable through the CLI? |
|---|---|---|
| Its document is supplied, and its shape is valid; it re-hashes (match, mismatch or out of range) | re-hashed | yes |
| Its document is declared but not supplied | unchecked | yes (A2) |
| Its document was supplied but is not strict UTF-8 | unchecked | yes, but the run already exits 3 with `unattended:document-unreadable` |
| A non-mapping span or a malformed one (`_span_issue` returns an issue) | unchecked (fail closed) | no: layer one refuses it (U6, U7), so `--document` never runs. Covered at the function (A12b) |
| It cites an undeclared document | unchecked | no: U7 refuses it at layer one. Function only |
| A supplied document whose digest is not declared | not a span; the existing `unattended:document-undeclared` issue, exit 3 | yes, unchanged |

**The entry (one `ValidationIssue`, which fits `$defs.issue`):**

```json
{"path": "$.source.documents", "rule_id": "unattended:spans-unchecked", "severity": "warning",
 "message": "3 of 7 source spans were not re-hashed; supply every declared document with --document"}
```

With the strict flag, the same entry appears in `issues` with `"severity": "error"`, and the run exits 3.

### 6.2 Part A: `src/gnd/commands/checking.py` (about +40 lines) and the order

New option on `gnd validate`:

```
--require-documents
    exit 3 unless every source span of an unattended model was re-hashed over a
    supplied --document; a no-op for a model without the unattended mode
```

**Order (normative, per boundary):**

1. Model load and layer-one validation, as today. An invalid model reports its own issues and exit first.
2. `--identity` combined with `--require-documents` is a usage error, the same message family as `--document` (exit 64; corrected from 2 by F-c1).
3. `--document` reading, as today (66, 74, 3 for oversize).
4. The span walk: the existing issues (`document-undeclared`, `document-unreadable`, `span-out-of-range`, `excerpt-mismatch`) and the coverage counts.
5. If the existing issues are non-empty, exit 3 as today. The `spans-unchecked` entry rides in `warnings`, or in `issues` under the strict flag.
6. Else, if unchecked > 0: under the strict flag, exit 3 with the issue; without it, exit 0 with the warning appended to the payload's `warnings` (JSON) or printed as a `WARNING at` line (text).
7. With no `--document` and no strict flag: the walk does not run (UG-R1). With no `--document` and the strict flag on an unattended model: the walk runs with no documents, so every span is unchecked, and step 6 applies.

The projected-text route (`"redaction" in mechanical_payload`, `checking.py:113`) prints warnings from the payload, so the entry reaches it through the payload. A8 checks both text routes.

### 6.3 Part B: `src/gnd/evolve/models.py` (about +45 lines)

```python
class SourceDocumentLocator(_ClosedFrozenModel):   # the base ModelIdentityLocator uses (models.py:102)
    locator_kind: Literal["source-document"]
    sha256: str            # 64 lowercase hex, validated

    def reference(self) -> str:
        return f"source.documents[{self.sha256}]"

StableLocator = ElementLocator | RoleLocator | ConstraintLocator | ModelIdentityLocator | SourceDocumentLocator
```

These rules are added to `EvolutionOperation._shape_and_digests` as an explicit branch, placed before the constraint `else`:

- `rename` is refused: "source documents cannot be renamed; change the label with modify".
- `before` and `after`, when present, have exactly the keys `{sha256, label}`. Their `sha256` equals the locator's, and `label` is a non-blank string.
- `modify` may change only `label`. A different `sha256` is a different document: delete the old one, add the new one.

`PolicyCell` gains `source_document.modify` and `source_document.delete`.

**Schema version (UG3-D10, proposed (a)).** The locator is admitted in `schema_version` 3 only. A v1 or v2 proposal carrying it is refused, exit 3, because those graphs are frozen. A v3 proposal without it is byte-identical. An older GND (0.2.0) reading a v3 proposal **with** the locator refuses it, exit 3. That is the forward-incompatibility the release note states.

### 6.4 Part B: `src/gnd/evolve/service.py` (about +50 lines)

| Site | Change |
|---|---|
| `_apply_declared_operations` (`:917`) | New branch. `add` requires `document["source"]["documents"]` to be a list (else `EvolutionError`, exit 3: "the model declares no source.documents to append to"). It refuses a `sha256` already declared (duplicate, exit 3), then appends `after`. `modify` finds the entry by `sha256`, checks it equals `before`, and replaces it in place. `delete` finds it, checks it, and removes it. No operation reorders, so a candidate that only reorders still fails replay equality |
| `_operation_target` (`:874`) | Explicit branch returning the matching `source.documents` entry, before the constraint fall-through |
| `_delta_element_ids` (`:598`) | `frozenset()` for the new kind, like `ModelIdentityLocator` |
| `_operation_references` (`:705`) | Unchanged in shape: `operation.reference()` |
| Blast radius (`_surface_index`, `:440`) | **No new entries.** Adding `source.documents[...]` entries for existing documents would move every unattended model's preview (UG-R1). The operation matches the always-present `model` entry (`:466`), so `entries` is never empty (B14) |
| Replay equality (`:1413`, `:1934`) | Unchanged. The declaration is now an operation, so a candidate carrying it with the matching `add` is equal |

`gnd.discover.output.candidate_document` calls the same replay. It produces constraint operations only and gains nothing, but its tests run in G-evolve-consumers.

### 6.5 Part B: `src/gnd/evolve/policy.py` (about +12 lines) and the order

New branch in `additive_policy_issues`, before the end of the loop body:

```python
if locator_kind == "source-document":
    if kind is not _ADD:
        refuse(position, operation, f"source_document.{kind.value}", f"{kind.value} of a declared source document refused")
    continue
# fail closed: a locator kind with no rule is refused, never admitted
raise EvolutionPolicyGapError(locator_kind)   # mapped to exit 3 by type
```

`EvolutionPolicyGapError` lives in `gnd.evolve.models` beside `PolicyIssue`. It is a plain exception carrying the kind word, never operator text, and is mapped by type (the UG2-Q2 lesson). The union is closed by Pydantic, so the line is reachable only through `model_construct`; B11 drives it that way.

**Order** is unchanged from MG2 and UG2: proposal validation (the locator branch rejects shape errors), candidate validation, replay equality, D-12, then the policy.

### 6.6 What "modified", "removed", "reordered" and "duplicate" mean (normative; home: evolution contract)

| Term | Definition | Outcome |
|---|---|---|
| modified | `modify` on an existing `sha256` with a different `label` | policy: `source_document.modify` (3); without `--policy`, admitted |
| removed | `delete` on an existing `sha256` | policy: `source_document.delete` (3). Without `--policy`, admitted only if no span cites it; otherwise candidate validation (U7) exits 3 |
| reordered | any change in order with no operation | replay equality, 3 |
| duplicate | `add` of a `sha256` already declared | replay, 3 |
| a different `sha256` under a `modify` | | operation validation, 3 |

### 6.7 Pins, chains and documentation UG3 moves (measured at execution)

- **RF1 (Part A):** a successor fixture `tests/fixtures/validate-documents-cli/expected.json` for the `validate` action. It supersedes `IDENTITY_SUCCESSOR` for `gnd validate` help and exit, per minor (3.11, 3.13, 3.14), captured with `GND_RF1_CAPTURE`. `test_cli_tree` inserts the new action. The historical goldens and `MANIFEST_SHA256` stay unchanged (UG3-D13).
- **RF6:** each part appends one `dynamic-query-successor.json` under `evidence/UG3a/` and `evidence/UG3b/`, plus a `DYNAMIC_SUCCESSORS` entry, if its inventory moves. Measured; an unmoved inventory adds nothing.
- **Pins moved knowingly:** `tests/test_evolve_additive_policy.py::test_t14_the_cell_literal_the_contract_table_and_the_walk_agree`. Its regex and `CELL_CASES` gain the two cells and one case each.
- **Normative docs:**
  - `representation-format.md` "Unattended source" (`:679-687`): the counting table, the entry, the flag. The sentence "Spans over a declared document that was not supplied are not re-hashed" gains "and are counted".
  - Evolution contract: a `SourceDocumentLocator` row in "Stable locators" (`:68-75`), its operation rules beside the identity rules (`:109`), a matrix row in "Additive policy" (`:216-225`), the definitions in §6.6, and a sentence under "EvolutionProposal" that the locator exists in schema version 3 only.
- **Citing docs:** `docs/reference/cli.md` (the validate rows `:18-20`, the flag syntax; read by `test_documentation_tutorials.py`); `docs/reference/evolve-policy.md` (one matrix row, citing the contract); `docs/release-notes.md` Unreleased (two entries, including "GND 0.2.0 cannot read a proposal that declares a source document"). UG4 does the rest (`unattended-growth.md`, the skill pointer, retiring the out-of-band step).

### Implementability sweep (author inspection, not review)

| Requirement | Can some implementation satisfy it as written? |
|---|---|
| The entry fits the frozen v3 payload | Yes: `ValidationIssue` is `{path, message, rule_id, severity}` with `severity` in `{error, warning}` (`errors.py:13-19`), the same closed shape as `report.schema.json` `$defs.issue`. A12 measures it |
| Both text routes print the entry | Yes: the plain route prints `result.warnings` (`checking.py:119`); the projected route prints `payload["warnings"]` (`output.py:406-418`). The entry must be added to the result's warnings **before** the payload is projected. The projected payload may sit under `"report"` (`checking.py:112`), so the implementation appends at the one place both read, and A8 runs both |
| Strict with no `--document` reaches the walk | Yes: today `_cmd_validate` calls the document path only when `documents` is truthy (`checking.py:101`); the flag adds a second trigger |
| A usage error for `--identity` with the flag | Yes: the existing `parsers["validate_parser"].error(...)` (`checking.py:1079-1083`) exits 64 (F-c1) |
| `add` appends without moving other bytes | Yes: replay works on the parsed document; the canonical candidate text is produced by the same writer as today, and B1 compares the published model |
| The policy's fail-closed default is testable | Yes, only through `model_construct` (the union is closed); B11 |
| `entries` non-empty for a declaration-only proposal | Yes: `_surface_index` always adds `model` (`service.py:466`) |
| A v3-only locator | Yes: `EvolutionOperation` is shared by v1 to v3 (`models.py:518-550`), so the refusal sits in the v1 and v2 proposal validators, which see their operations |
| No document text in output | Yes: the entry carries counts only; the existing messages carry paths, digests and offsets (MG-R5) |

## 7. Decisions

At first write every row is open; the proposed reading is marked **(proposed)**.

| ID | Question | Readings and cost | Proposed | Owner ruling |
|---|---|---|---|---|
| UG3-D1 | One spec or two | (a) one spec, two parts (UG3a = (ii) counts and flag; UG3b = (i) locator), each with its own corpus cases, commits and record (`004-phase-UG3a.md`, `005-phase-UG3b.md`), landing (ii) then (i) on one branch and one PR. (b) two specs and two PRs: a second gate and a second PR for about 300 lines | **(a)** | `(o)` 2026-11-09: as proposed |
| UG3-D2 (UG-Q2) | Flag name | `--require-documents` (the plan's placeholder; reads as "the run requires the documents") / `--require-spans-checked` / `--strict-spans` | **`--require-documents`** | `(o)` 2026-11-09: as proposed |
| UG3-D3 | Where the counts go | (a) one `unattended:spans-unchecked` entry in the existing `warnings` list, present only when a span is unchecked. No version bump, fits `$defs.issue` (A12), but a run with every span checked shows no count. (b) counts always present: a new report variant or version bump (`build_validate_payload` is documented frozen; `counts` and the variants are `additionalProperties: false`). It moves every `validate --document` payload and needs a schema change and new pins. The owner's UG-D3 ruling said "counts always reported"; (a) meets it only when there is something to report | **(a)**, with this cost stated as the plan required | `(o)` 2026-11-09: as proposed |
| UG3-D4 | No `--document`, no flag, unattended model | (a) unchanged: no entry, byte-identical (UG-R1 as the plan wrote it). (b) always warn: closes the hole without the flag, but moves every unattended `validate` output | **(a)** | `(o)` 2026-11-09: as proposed |
| UG3-D5 | Form of the strict refusal | (a) the same entry in `issues` with `severity: error`, exit 3: machine-detectable by `rule_id`. (b) `error` object only: one less list shape, but no `rule_id` | **(a)** | `(o)` 2026-11-09: as proposed |
| UG3-D6 | Strict flag on a model without the mode | (a) no-op: the same bytes and exit as without the flag (plan). (b) usage error: a host could not pass the flag uniformly | **(a)** | `(o)` 2026-11-09: as proposed |
| UG3-D7 | Malformed spans and spans on an undeclared document | (a) counted as unchecked (fail closed), reachable only at the function. (b) excluded from the total: the counts would then hide them | **(a)** | `(o)` 2026-11-09: as proposed |
| UG3-D8 | Locator shape | `SourceDocumentLocator{locator_kind: "source-document", sha256}`, reference `source.documents[<sha256>]`. Alternative: key by position. Positions move when a document is deleted, and the digest is already the identity U1 uses | **digest-keyed** | `(o)` 2026-11-09: as proposed |
| UG3-D9 | Operation kinds | (a) `add`, `modify` (label only), `delete`; no `rename`. The policy admits `add` and refuses the other two with named cells (UG3-C6 needs the cells to exist). (b) `add` only: smaller, but a removal is then an operation-validation error with no cell, which misses UG3-C6 | **(a)** | `(o)` 2026-11-09: as proposed |
| UG3-D10 (UG-Q5) | Schema version | (a) admitted in v3 only; v1 and v2 stay frozen and refuse it; GND 0.2.0 refuses a v3 proposal carrying it (forward-incompatible, stated in the release note). (b) a new schema version 4 across proposal, preview, intent and record: the principled reading of "one closed graph per version", at the cost of four new nested classes, readers and pins, perhaps +250 lines. (c) all of v1 to v3: rewrites frozen graphs | **(a)** | `(o)` 2026-11-09: as proposed |
| UG3-D11 | `add` on a model without a `source.documents` list | (a) refuse, exit 3: adopting the unattended mode stays a reviewed change outside this locator. (b) create the header: the locator would then also switch a model into a mode | **(a)** | `(o)` 2026-11-09: as proposed |
| UG3-D12 | An unknown locator kind in the policy | (a) fail closed: a typed error, exit 3 (§6.5). (b) a catch-all cell in `PolicyCell`: the contract table and `test_t14` would carry a cell no real case reaches | **(a)** | `(o)` 2026-11-09: as proposed |
| UG3-D13 | RF1 re-pin form | (a) a successor fixture, as RC1 and UG2 did; historical goldens untouched. (b) re-pin the historical goldens and `MANIFEST_SHA256` as the plan's text says; a fresh capture drifts about 60 unrelated goldens (MG3-Q1) | **(a)** (departs from the plan's wording) | `(o)` 2026-11-09: as proposed |
| UG3-D14 | Approval instrument | (a) **corpus-first**, the default for exit-code contracts and a serialized field. Before any source edit, commit the fixtures for A1 to A6 and B1 to B8, a README narrating each without its outcome, and a separate `expected.json` answer key (exits, rule ids, cells, the entry's exact text). Committed red, then put to the owner. (b) this prose, with §8 as the narrated cases | **(a)** | `(o)` 2026-11-09: as proposed |

## 8. Tests

Two new files: `tests/test_unattended_span_coverage.py` (Part A) and `tests/test_evolve_source_document.py` (Part B). Both are CLI-level unless marked *function* or *service*. Fixtures live in `tests/fixtures/unattended-model-growth/ug3/`: the UG1 lending model with two declared documents, spans of all three kinds over both, and their document files. Every refusal assertion checks the rule id or the cell and operation index, never exit 3 alone.

**Part A:**

| Test | Case | Expected |
|---|---|---|
| A1 | Both documents supplied | 0; no `spans-unchecked` entry; payload bytes equal the baseline |
| A2a, A2b, A2c | One document supplied; the unsupplied one is cited only by (a) an element span, (b) a constraint span, (c) a `sample_spans` entry | 0; one warning, `1 of N` |
| A3 | `--require-documents`, both supplied | 0 |
| A4 | `--require-documents`, one supplied | 3; issue `unattended:spans-unchecked`, severity `error` |
| A5 | `--require-documents`, no `--document`, unattended model | 3; `N of N` |
| A6 | `--require-documents` on a model without the mode, with and without `--document` | bytes and exit equal the same run without the flag |
| A7 | `--require-documents --identity` | 64, usage error (corrected from 2 by F-c1) |
| A8 | Text output on both text routes, plain and projected | the `WARNING at $.source.documents: …` line |
| A9 | Canaries: unique strings in both documents' text; scan stdout and stderr of A1 to A8 | 0 hits; positive control found |
| A10 | Parity: every `tests/test_unattended_mode.py` T3 case and UG1's validate calls, without the flag, against bytes captured on `5c6a0c5f` | identical, except A2's carved-out entry |
| A11 | Order: an excerpt mismatch on the supplied document plus an unsupplied one, with the flag | 3; the existing issue is listed first, then the `spans-unchecked` issue |
| A12 | The A2 payload validates against `report.schema.json`; A12b *function*: a non-mapping span, a malformed span and a span on an undeclared document each count as unchecked | valid; counts as stated |
| A13 | *function*, spies: 1, 10 and 100 spans | visits linear; one pass |
| A14 | RF1 successor: `gnd validate` help and exit probe on 3.11, 3.13 and 3.14 | equal to the fixture |

**Part B:**

| Test | Case | Expected |
|---|---|---|
| B1 | A round that `add`s the declaration and adds an object type citing the new document | preview with `--policy additive` 0 with no issues; apply 0; the model's `source.documents` gains the entry at the end; `validate --document` over every document 0 with no entry |
| B2 | `modify` of a label | `--policy additive`: 3, `source_document.modify`, op index. Without `--policy`: 0 |
| B3 | `delete` of an uncited declaration; of a cited one | policy: 3, `source_document.delete`. Without the policy: 0 for the uncited one, and 3 by U7 for the cited one |
| B4 | `add` of an already declared `sha256` | 3, the replay's duplicate message |
| B5 | `sha256` not 64 lowercase hex; `after.sha256` different from the locator's; extra key in `after` | 3, operation validation |
| B6 | `rename` | 3 |
| B7 | The locator in a v1 and in a v2 proposal | 3 |
| B8 | `add` on a model with no `source.documents` | 3 |
| B9 | Parity: every UG1 replay proposal and the `test_evolve_additive_policy.py` cell-table proposals, without the locator: proposal bytes, `proposal_sha256`, preview bytes and exits against goldens captured on `5c6a0c5f` | identical |
| B10 | UG1 T12 (a) unchanged: a declaration in the candidate with no operation | 3, the replay-equality message |
| B11 | *service*: a forged locator kind through `model_construct` | 3 by type, never admitted |
| B12 | *service*: `_operation_target` and `_delta_element_ids` for the new kind; neither reaches the constraint fall-through | the entry; `frozenset()` |
| B13 | `test_t14` agreement with the two new cells | pass |
| B14 | A declaration-only proposal | preview 0; `blast_radius.entries` non-empty |
| B15 | apply repeats `--policy additive` over a preview made without the policy that carries a `modify` | apply 3, `source_document.modify` (apply re-runs the policy) |
| B16 | *service*, spies: 1, 10 and 100 `add` operations | replay visits linear |

**Branch walk.** Part A: re-hashed (A1), unchecked for each location (A2a to c), unchecked with no documents (A5), malformed or undeclared at the function (A12b), not the mode (A6), strict vs not (A3, A4), the existing issues present (A11). Part B: `add` (B1), `modify` (B2), `delete` uncited and cited (B3), duplicate (B4), shape (B5), `rename` (B6), version (B7), no header (B8), unknown kind (B11), apply re-check (B15).

### Verification-selection ledger

| Gate | Disposition | Command |
|---|---|---|
| G-phase | run | `uv run pytest -q tests/test_unattended_span_coverage.py tests/test_evolve_source_document.py --tb=short` |
| G-ug1 (plan §9 UG1 row) | run | the UG1 gate list, as in UG2's ledger |
| G-ug2 | run | `uv run pytest -q tests/test_evolve_population_check.py --tb=short` (it shares the policy walk and the replay) |
| G-unattended | run | `uv run pytest -q tests/test_unattended_mode.py --tb=short` |
| G-rf1 | run | `uv run pytest -q tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py --tb=short`, plus 3.11 and 3.13 with `uv run --isolated --python` |
| G-layers, G-arch, G-packages | run | `uv run pytest -q tests/test_rf1_layering.py tests/test_gnd_arch.py tests/test_rf6_packages.py tests/test_atom_bind.py --tb=short` |
| G-rf6 | run | `tests/test_rf6_query_policy.py` and the successor-chain consumers, listed by `git grep` at execution |
| G-evolve-consumers | run | `tests/test_model_evolution.py`, `tests/test_public_evolution_version_graph.py`, `tests/test_public_evolution_legacy_readers.py`, and every module importing `gnd.evolve` or calling `_apply_declared_operations` (including discover), listed by `git grep` at execution |
| G-report-schema | run | the tests that validate payloads against `report.schema.json`, listed by `git grep` at execution |
| G-disclosure | run | `tests/test_disclosure_mode.py` |
| G-skills | run | `tests/test_packaged_skills.py tests/test_skill_prose_sync.py tests/test_ik_close.py tests/test_public_binding_prose.py` |
| G-docs | run | `tests/test_documentation_tutorials.py` |
| G-lint | run | `uv run ruff check` on every changed Python file |
| G-components | run | `python3 scripts/components_index.py changed --base main --strict` |
| G-anon | run | UG1's digest-set scan over the phase's files, commits and PR body |
| Full default lane; `-m "evidence or census"`; distribution lane | cadence | not selected (no explicit request) |
| Certification | not selected | opt-in only |

## 9. Out of scope for this phase

- Switching a model into or out of the unattended mode through `evolve` (UG3-D11).
- A new validate report version or a `counts` key (UG3-D3 (a)).
- Warning on unattended `validate` runs with no `--document` and no flag (UG3-D4 (a)).
- Locators for any other `source` field (`mode`, `reviewer`).
- `unattended-growth.md`, the skill pointer, and retiring the out-of-band step in the docs (UG4). UG1's `_declare` helper stays; T12 (b) still uses it to pin the before-the-round route.
- UG2-Q1, UG2-Q2 (the evolve lane's message-substring exit mapping; UG3 maps its new error by type and changes nothing else), UG2-Q3, MG3-Q2.
- Merge, release, certification; posting to or closing issues 74 or 104.

## 10. Size

Estimate:

- **Source:** Part A about 85 lines (`_unattended.py` +45, `checking.py` +40). Part B about 110 lines (`models.py` +45, `service.py` +50, `policy.py` +12). With UG2's lesson (its plumbing and docstrings were missed), add half again: about 300 in total.
- **Tests:** about 700 lines across the two files.

The plan's range is 230 to 450 source lines and 300 to 500 test lines. The test estimate is above it because of the parity and RF1 cases. Measured at record time.

## 11. Approval instrument

Proposed: corpus-first (UG3-D14 (a)). If chosen, the corpus lives in `tests/fixtures/unattended-model-growth/ug3/`:

- an entry `README.md` narrating A1 to A6 and B1 to B8 without their outcomes;
- a separate `expected.json` answer key;
- a parity baseline captured on `5c6a0c5f`.

It is committed red (the flag and the locator do not exist) before the first source edit, then put to the owner. If the owner chooses prose, this spec is the instrument as written.

Optional spec review: none proposed. The owner may call one.

## Corpus authoring (step 2 instrument, recorded as it was done)

Committed red before any source edit, on the spec gate's ruling UG3-D14 (a). The
fixtures were generated once by a throwaway script (not committed) from the MG5
fixture `tests/fixtures/unattended/` and checked on the base: every model
validates (exit 0), and `--document` over both documents exits 0 for each
span model.

| File (under `tests/fixtures/unattended-model-growth/ug3/`) | sha256 |
|---|---|
| `README.md` (narration, no outcomes) | `c0a6980ca1c571cd92537962ab10606a1bfb8a342c90f41c32c1be14e7806718` |
| `expected.json` (answer key: parts A and B) | `a46dc7dcdc702aa4c361024990d10e8f97179345a38099ab03ac9e0feebd7358` |
| `parity-baseline.json` (captured on `5c6a0c5f`) | `6b84dfb57a5475dbf21d6cacbf60bbc6b10a3634e2fc9c31c596106bc4957035` |
| `documents/ledger.txt` (the MG5 `source.txt` bytes) | `6cec7fe354bc7c620fccfeece167c43dec11096669d934a54ce5ef8fffd155e8` |
| `documents/annex.txt` | `69897fa97fa34393398757221b81b99c4fad230ffc46c28cd1dd8d088061d5e4` |
| `documents/round.txt` | `780ce83053b3e907a53cd0026934ff4bab7f63cda98ee1ece44e8035d093d7e6` |
| `models/span-element.orm.yaml` | `56213db71bb18914d8825a76613ba363355cdc3232277f0af9e318fea1a5370e` |
| `models/span-constraint.orm.yaml` | `4feeee1df49065396a4731cf3c3be0c72835f25d6ae7a750c56724a4b5b16734` |
| `models/span-sample.orm.yaml` | `e8a581fee1b769d6b3a5b398dbd6f9905fc11e8de6d8b401bc0bbec153476dce` |
| `models/plain.orm.yaml` | `d58221bd2637f02cf25391584da3bf1b80a4fff078105c1d8aafe3332dfb09e9` |
| `models/rounds.orm.yaml` | `47d43750e81a47733ca84bd19e3c3228b6902ad7cb59020c551d24d9b96e6519` |

Harness: `tests/test_unattended_span_coverage.py` (part A, sha256 `3fd779d8…`) and
`tests/test_evolve_source_document.py` (part B, sha256 `800f7b82…`). On the base:
`21 failed, 5 passed`, ruff clean, `tests/test_digest_helpers.py` green.

| Red case | Reason on the base |
|---|---|
| A2a, A2b, A2c | the `warnings` list has no `unattended:spans-unchecked` entry |
| A3, A4, A5, A6a, A6b | 64: `--require-documents` is not an option |
| A10b | the carved-out runs carry no entry |
| B1 to B8 (12) | `ImportError`: `SourceDocumentLocator` does not exist, so the case's proposal cannot be built |

Green on the base, by design: A1 (it asserts that nothing is added); the answer-key
split check; A10 (18 runs outside the carve-out, byte-identical); B9 (six
locator-free previews: proposal digests, proposal file bytes, preview bytes and
exits); the B7 control.

**What the owner approves:** the answers in `expected.json`. In plain words:

- **Part A:**
  - A1 and A3 (both documents supplied, with and without the flag) exit 0 with no entry.
  - A2a to A2c (only the ledger supplied, one span at each location) exit 0, with exactly one warning: `1 of 10 source spans were not re-hashed; supply every declared document with --document`, path `$.source.documents`.
  - A4 is A2a with the flag: exit 3, with the same text as an `error` issue and no warning.
  - A5 is the flag with no document: exit 3, `10 of 10 …`.
  - A6a and A6b (the plain model) are unchanged by the flag: 0 and 3, byte for byte.
- **Part B:**
  - B1: the round previews and applies with exit 0 under `--policy additive`, the published `source.documents` is ledger, annex, round in that order, and `validate` over all three documents exits 0 with no entry.
  - B2 (label change) and B3a (removing the uncited annex): exit 3 under the policy, with cells `source_document.modify` and `source_document.delete` on operation 0. Without the policy, both exit 0.
  - B3b (removing the cited ledger): exit 3 with and without the policy, by candidate validation ("the span names a document the source does not declare"); no preview is written.
  - B4 (duplicate): exit 3, "source document is already declared".
  - B5a to B5c (bad shapes), B6 (`rename`) and B7a and B7b (the locator in schema versions 1 and 2): exit 3, with no preview written.
  - B8 (a model with no `source` header): exit 3, "the model declares no source.documents to append to".

## Implementation findings (recorded as found)

- **F-c1 (corpus authoring), a spec correction:** a usage error in this CLI exits **64**, not 2 (measured: an unknown `--require-documents` on the base exits 64). §4, §6.2 step 2 and A7 said 2. A7's expected exit is corrected to **64** before implementation; this is not a corpus answer.
- **F-c2:** `gnd evolve preview` refuses every v1 or v2 proposal with exit **70** ("versions 1 and 2 are read-only compatibility evidence", `service.py:1357`), after the proposal is read. B7's answer (3) therefore holds only if UG3-D10's refusal sits in **reading** the v1 and v2 graphs, as §6.3 says. The control pins the 70 for an ordinary operation, so B7 cannot pass by reaching the version gate.
- **F-c3:** UG1 pinned no golden proposal bytes (plan §4 UG1-C8 said it "may"). B9 captures them now on `5c6a0c5f`: three locator-free proposals, each previewed with and without the policy, giving outcomes 0 and 3, written and not written.

## Revision history

- r1, 2026-11-09: first draft. Not reviewed. Approved as proposed at the spec gate.
- r1 + corpus, 2026-11-09: rulings recorded, corpus authoring and findings F-c1 to F-c3 added; A7's exit corrected (F-c1). Not reviewed.
