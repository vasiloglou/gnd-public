# Phase VG4 · growth rounds on a root that includes a reviewed vocabulary · spec r1

## 1. Status

**Approved by delegated ruling (auto=true), 2026-11-23; implemented, recorded in [005-phase-VG4.md](../005-phase-VG4.md)** `(d)`, under the
owner's `process-milestone reviewed-vocabulary-growth auto` of 2026-11-23;
the driving agent's ruling, not the owner's reading. Implementation waits
for GO1 of growth-round-outcomes on `main` and for the milestone
coordinator's clearance (VG4 changes `evolve/service.py`); the branch is
rebased onto that `main` and every `evolve/` citation below is re-read
there before the first edit.

## 2. Provenance

- Derives from [plan r4](reviewed-vocabulary-growth-plan.md), approved by the
  owner on 2026-11-23 with D4 (a) and D6 as proposed
  ([plan gate](../001-plan-gate.md)): Goal (VG4), §0 (R0.4, R0.6), §1 (H20–H23,
  H32, H33, H35), §2 (VG4), §3 (VG4 row), §4 (VG4-C1 to VG4-C5), §6, §9.
- From [#222](https://github.com/vasiloglou/gnd-public/issues/222), case 3.
- Builds on VG3 ([record](../003-phase-VG3.md)): the origin test
  `included_rows` and the `_INCLUDED` context variable.
- Written by `process-milestone` on 2026-11-23 at `59289af6`, while GO1 runs,
  at the milestone coordinator's suggestion. Citations of `evolve/` were
  read at `11a7ebf7`. No review has read this spec.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan H20; #222 case 3 | an unattended root with no documents exits 3 with U1; `gnd evolve preview` refuses it | §6 (U1); T3 |
| plan H21; R0.6 | evolve composes an include root, keeps included elements read-only (`evolve/_includes.py:enforce_ownership`), places owned constraints on included fact types | T1, T2 |
| plan H22; D6 | `repin-include` is refused by `--policy additive` only (`policy.py:487-489`) | §6 (D6); T4 |
| plan H23 | the `source-document` operation is not exercised on an include root | T1, T3 |
| plan H32, H33; D4 (a) | the first-document rule covers every section, attachments, operations and obligations included | §6; T3 |
| plan H35 | five U1 branches are pinned in `tests/test_unattended_mode.py:118-122`; two are documents absent and empty on a model that owns elements | T3 keeps them; §8 ledger |
| VG4-C1 | a round adds a root-owned fact type with spans and a constraint attached to an included fact type; preview, apply, finalize exit 0; the result validates | T1 |
| VG4-C2 | an operation that modifies, renames or deletes an included element exits 3 | T2 |
| VG4-C3 | the first-document cases (plan §4, VG4-C3, all of them) | T3 |
| VG4-C4 | `repin-include` on an unattended root exits 3 with and without `--policy additive` | T4 |
| VG4-C5 | `--check-population` and `--populated` behave on the root as on a model without includes | T5 |
| plan §5; R0.7 | U1's first-document rule in "Unattended source"; D6 in the evolution contract | §6 pages; T6 |
| plan §9 | the VG4 lane, guards, lint | §8 |

## 4. The standing rules, bound to this phase

- **Totality (rule 1).** The first-document test reads the composed
  document and `_INCLUDED` with `.get` and `isinstance` guards; the
  source-document add reads `source` only when it is a mapping. T3 holds
  hostile values (a `documents` that is not a list, a `source` that is not a
  mapping).
- **A cap bounds the algorithm (rule 2).** The first-document test is one pass
  over the root's sections, linear. No new per-operation work.
- **Validation order (rule 3).** U1's issues keep their position (first);
  the D6 refusal sits with the other ownership refusals, which precede
  operation gating (evolution contract, "Shared vocabulary evolution"), so a
  re-pin on an unattended root is refused before the additive policy reads
  it. T4 pins the order.
- **One walk for N kinds (rule 4).** "The root owns nothing" is read with
  VG3's origin set: a section the composition merges counts its entries
  whose origin is the root; any other section counts all its entries.
- **One home (rule 5).** U1's rule in "Unattended source"; D6 in "Shared
  vocabulary evolution"; the policy matrix's `include.repin-include` row
  cites it.
- **Measurement (rule 6).** Whether the composed reading equals the
  root's own file is measured by T3's per-section cases, not argued.

## 5. Goal

A root with includes, no documents and nothing of its own validates; its
first `gnd evolve` round declares a document and adds elements, preview,
apply and finalize exit 0, and the result validates with its document. A
root that owns anything and declares no document still exits 3 with U1, as
does any unattended model without includes. `repin-include` on an unattended
root exits 3 with and without the additive policy. The VG4 lane, the guards
and lint exit 0.

## 6. Design

### U1's first-document rule (`src/gnd/model/_unattended.py`)

`_declared_documents` keeps every check. Its one "must declare at least one
source document" issue is not raised when all of these hold (D4 (a)):

1. the composed document declares a non-empty `includes` list;
2. every top-level section other than `version`, `model_id`, `source` and
   `includes` holds nothing of the root's: for `object_types`,
   `fact_types`, `constraints` and `deontic_notes`, every entry is in
   `_INCLUDED`, and no included fact type holds a constraint outside
   `_INCLUDED` (an attachment is the root's, H33); every other section
   (`operations`, `rejected_proposals`, `reference_populations`,
   `fact_type_constraints`, and any other) is absent, `null` or an empty
   list or mapping.

Read this way the test is the root's own document as authored: composition
appends only included entries to those four sections, attachments enter an
included fact type with origin `model`, and an include cannot declare the
other sections (`_includes.py:222-223`). `reviewer: none` is still required,
and a `documents` value that is present and not a list still raises.

### `gnd evolve` (`src/gnd/evolve/service.py`, `_includes.py`, `policy.py`)

- **The first document.** `_source_document_target`'s add, on a model whose
  `source` is a mapping without `documents`, creates the list and appends to
  it (VG4-D1). A `documents` present and not a list keeps today's refusal.
- **D6.** `enforce_ownership` refuses any `repin-include` operation when the
  current model's `source.mode` is `unattended`:
  `evolve:unattended-repin: <reference>`, exit 3, under every policy. The
  owner re-pins by editing the root (plan §2). The additive matrix row stays.

### Pages

- "Unattended source", U1 row and the include paragraph: the first-document
  rule.
- Evolution contract, "Shared vocabulary evolution": the D6 sentence; the
  `include.repin-include` policy row cites it.
- `docs/release-notes.md`: one entry.

## 7. Decisions

Ruled by delegated approval (auto=true), 2026-11-23 `(d)`.

| ID | Question | Readings and their cost | Ruling |
|---|---|---|---|
| VG4-D1 | A first `source-document` add when `documents` is absent | (a) the add creates the list: #222's root as written (no `documents` key) grows. (b) require `documents: []`: one more authored line, and a root with the key absent validates (D4 says absent or empty) but cannot grow | (a) |
| VG4-D2 | Where D6's refusal lives (plan §10, VG4 question) | (a) the mode, in `enforce_ownership`, before policy. (b) the additive table: a round without the policy would still re-pin | (a) |
| VG4-D3 | Instrument | prose | prose |

Budget: one diff review round (plan D7).

## 8. Tests

`tests/test_vg4_seeded_growth_rounds.py`, default lane, reusing
`tests/vg3_cases.py` and the evolve helpers of
`tests/test_evolve_additive_policy.py`.

| # | Criterion | Case | Expected |
|---|---|---|---|
| T1 | VG4-C1 | on VG3's #222 root with its document: one round adding a root-owned value type and fact type with spans and sample rows, and an `llm-inferred`, `proposed`, `deontic` constraint with a span attached to `work_has_version` (`host: included_fact_type`) | preview, apply and finalize exit 0; `gnd validate --document --require-documents` exit 0 |
| T2 | VG4-C2 | modify, rename and delete of an included object type, fact type and constraint, under the mode | each exits 3, `evolve:included-element` |
| T3 | VG4-C3 | the #222 root with no `documents` key and nothing of its own validates; one round declares the document and adds an element (exit 0, result validates). U1 kept, one case each: owns an object type; only an attached constraint; only an operation; only a fact type; only a top-level constraint; only an operation carrying an obligation; only a deontic note; only a `rejected_proposals` entry; only a `reference_populations` entry (at the rule); `reviewer` absent; `reviewer` not `none`; an unattended model without includes, documents or elements; `documents` not a list | as stated; the two pinned branches of `tests/test_unattended_mode.py:118-122` unchanged |
| T4 | VG4-C4 | `repin-include` on the unattended root, with and without `--policy additive`; control: the same re-pin on a root without the mode | exit 3 `evolve:unattended-repin` both times, before any policy issue; control as today |
| T5 | VG4-C5 | `--populated` naming an included fact type, and `--check-population`, on the unattended root and on the same model flattened without includes | the same exits and refusal cells |
| T6 | pages | the U1 row and the contract name the rules | present |

### Verification-selection ledger

| Obligation | Disposition | Command or evidence | Justification |
|---|---|---|---|
| VG4-C1 to C5 | run | `uv run pytest -q tests/test_vg4_seeded_growth_rounds.py tests/test_mc3_evolution.py tests/test_evolve_source_document.py tests/test_evolve_additive_policy.py tests/test_evolve_population_check.py tests/test_unattended_model_growth_acceptance.py tests/test_unattended_mode.py tests/test_unattended_span_coverage.py --tb=short`, exit 0 | the plan §9 VG4 lane as written |
| Guards, lint, component index | run | the `project.md` guard block; `uv run ruff check src tests tools`; `python3 scripts/components_index.py changed --base <VG4 base> --strict` | plan §9, D11, H28 |
| VG3's lane | run | the VG3 lane, since U1 changes in `_unattended.py` | VG3 shares the file |

## 9. Out of scope for this phase

- Include-bearing linked-project evolution (still refused).
- Any change to what an include may declare.
- The packaged example and the growth page (VG5).

## 10. Size

About 40 source lines, 20 page lines, 300 test lines.

## 11. Approval instrument

This prose (VG4-D3).

## Implementation findings, recorded as they were found `(d)`

2026-11-23, at `002dc86e`, on the branch holding `main` with GO1
(`11ca75b0`). `_source_document_target` and `enforce_ownership` were
unchanged by GO1; every citation held.

1. **The first-document add is limited to unattended models.** §6 said the
   add creates the list "on a model whose `source` is a mapping without
   `documents`". The code also requires `source.mode: unattended`, so a
   model without the mode keeps today's refusal (plan R0.3). Prior wording
   kept above.
2. **Refusal cases need the authored root as the candidate.** An operation
   on an included element cannot be replayed on the authored file (the
   discovery replay helper finds no such element), and ownership is refused
   before the candidate is read. T2 and T4 build their proposals with the
   authored root as the candidate.
3. **T5 is narrower than its row.** It holds that `--populated` naming an
   included fact type refuses an attached constraint with the same cell as
   on any model, and that `--check-population` reads the composed root. It
   does not compare against a flattened copy of the root.
4. **A known timing flake.** One run of the VG3 and VG2 lanes failed one
   test and three reruns passed (246 each); the same lanes' MC1 T22 timing
   test (median of three, linear against a quadratic mutant) flaked once in
   VG3's first run too.
5. **Review r1 (Codex), F1, fixed at the commit after `002dc86e`.** A
   present `documents: null` passed the first-document rule, which the
   first round's add cannot extend. The rule admits only an absent key or
   an empty list, as plan D4 says.
