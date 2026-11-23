# Phase VG2 · the sources a new constraint may carry in `gnd evolve` · spec r1

## 1. Status

**Approved by delegated ruling (auto=true), 2026-11-23; implemented, recorded in [004-phase-VG2.md](../004-phase-VG2.md)** `(d)`. The owner
invoked `process-milestone reviewed-vocabulary-growth auto` on 2026-11-23,
which delegates spec rulings within this milestone. That is the driving
agent's ruling under the delegation, not the owner's reading of the spec.
The ruled bytes are this file's r1 (§7).

## 2. Provenance

- Derives from [plan r4](reviewed-vocabulary-growth-plan.md), approved by the
  owner on 2026-11-23 with D2 ruled (a) ([plan gate](../001-plan-gate.md)):
  Goal (VG2), §0 (R0.3, R0.7), §1 (H11, H12, H13, H36), §2 (VG2), §3 (VG2
  row; "Other writers"), §4 (VG2-C1 to VG2-C4), §5, §6 ("D-12 widened too
  far"), §9 (the VG2 lane).
- From [#218](https://github.com/vasiloglou/gnd-public/issues/218) and the
  [maintenance page](../../../maintenance/2026-11-21-evolve-constraint-sources/README.md),
  whose "Done when" list this spec carries.
- Written by `process-milestone` on 2026-11-23 from `main` at `11a7ebf7`
  merged into the topic branch, gated while GO1 runs, at the milestone
  coordinator's suggestion; implementation waits for GO1 on `main`. No
  review has read this spec.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan H11; #218 | `unattended-growth.md` tells the host to write `sample` (row evidence) and `common-sense` (library evidence), `proposed` and `deontic`; `_enforce_d12` refuses both | §6; T1 |
| plan H12; R0.7 | D-12 has one home, "Evolve admission (D-12)" in `provenance-and-modality.md`; the evolution contract restates it (`:279-280`, §6) | §6 (pages); T3 |
| plan H13 | U5 exempts `common-sense` and `induced` from spans; U8 refuses `alethic` for `sample` and `common-sense` | T4 |
| plan §2 VG2 (D2 (a)) | admit a new `sample` and a new `common-sense` constraint when `proposed` and `deontic`; `confirmed` or `alethic` still refuses; the refusal names the two combinations | §6; T1, T2 |
| VG2-C1 | a proposal built exactly as the growth document describes previews and applies, exit 0 | T1 |
| VG2-C2 | each source with `confirmed`, and each with `alethic`, exits 3 with the D-12 refusal | T2 |
| VG2-C3 | the D-12 home, its restatement and the growth document name the same combinations; a test reads all three | T3 |
| VG2-C4 | on an unattended model the same proposal passes U5 and U8 | T1 (it runs on an unattended model), T4 |
| plan R0.3 | VG2 is the named exception: it admits two more sources in `gnd evolve` for every model | §6; T2's control on a model without the mode |
| plan §6, "D-12 widened too far" | four refusal cases, one per source and failing field | T2 |
| plan §3, "Other writers"; H36 | growth-round-outcomes GO1–GO3 change `evolve/service.py`, GO4 `unattended-growth.md`; one writer at a time | §9; checked at the start (below) |
| maintenance page, "Done when" | the affected lane (`tests/test_evolve_*.py`, `tests/test_unattended_*.py`) and the guards pass; the issue gets a reply after the merge | §8 ledger; VG5 drafts the reply |
| IK2 T5 (found while harvesting) | `tests/test_induced_provenance.py::test_t5_d12_outcomes_equal_the_base_commit_table` holds `_enforce_d12`'s answer for every source, status and modality to a table captured at `328061ee`. Eight of its rows change by design | T5 |
| plan D11 | lint gate `uv run ruff check src tests tools` | §8 |

**Other writers, checked.** GO1 of growth-round-outcomes started on
2026-11-23 in its own session and goes before VG2 (plan §3; the milestone
coordinator holds VG2 until GO1 merges). GO1's spec (on `main` at
`11a7ebf7`) opens a parse scope at `EvolutionService.preview`, `apply` and
`finalize`, in `_load_model_document`, in `evolve/cli_service.py` and in
`model/_parsing.py`; it does not change `_enforce_d12`, and neither phase
changes `unattended-growth.md`. VG2 starts from a `main` that holds GO1:
before the first edit the branch is rebased onto it, every citation of
`evolve/service.py` in this spec is re-read there, and the base for the
component check and the review becomes that commit. Prior wording, kept:
"At `11a7ebf7`, growth-round-outcomes has a full plan and no phase has
started … VG2 is the one writer of `evolve/service.py` and
`unattended-growth.md` until it merges." `(d)`

## 4. The standing rules, bound to this phase

- **Totality (rule 1).** `_enforce_d12` reads candidate constraints that
  candidate validation has already admitted; the new branch reads `source`,
  `status` and `modality` with `.get`, as the existing branches do. No new
  consumer of untrusted shapes.
- **A cap bounds the algorithm (rule 2).** Inapplicable: the branch is
  constant work per constraint.
- **Validation order (rule 3).** Stated per boundary: the induction-block
  refusal still runs first for every source, then the source branch. A
  `sample` constraint carrying `provenance.induction` keeps the induction
  refusal. T2 pins that case.
- **One walk for N kinds (rule 4).** One function, `_enforce_d12`, decides
  every source; the new branch sits beside `llm-inferred`'s.
- **One home (rule 5).** The D-12 section of `provenance-and-modality.md`
  gains the two rules; the evolution contract's §6 bullet list and its
  `:279-280` sentence cite and follow it; `unattended-growth.md` already
  says what the code will admit and does not change.
- **Measurement (rule 6).** The question "which rows of IK2's table move" is
  settled by running T5 against the change, not argued (§6, T5).
- **Plan R0.3.** VG2 is its named exception; §5 of the plan says so, and
  the release notes name it.
- **Plan R0.7.** As rule 5.

## 5. Goal

A proposal written as `unattended-growth.md` describes, with one `sample`
and one `common-sense` constraint, `proposed` and `deontic`, previews and
applies on an unattended model, exit 0, and the result passes
`gnd validate --document --require-documents`, exit 0. Each source with
`confirmed` or `alethic` exits 3 with the named D-12 refusal. The D-12 home,
its restatement and the growth document agree, and a test reads all three.
The VG2 lane, the guard block and `uv run ruff check src tests tools` exit 0.

## 6. Design

### Reuse

| Capability | Searches | Found | Decision |
|---|---|---|---|
| deciding which new constraints evolve admits | `components_index.py search "evolve admission D-12 constraint sources"`; `git grep -n _enforce_d12 src/gnd` | `evolve.service`: `_enforce_d12` (`evolve/service.py:402`) | adapt: one branch |
| building a proposal as the growth document describes | `git grep -n "_translate\|_SOURCE_BY_BASIS" tests` | `tests/test_unattended_growth_guidance.py:_translate`, the test-only reading of the reply shape; `tests/test_unattended_model_growth_acceptance.py:_operations`, `_round`, the replay driver | reuse both, imported as modules the way the acceptance test imports the guidance test |

### `src/gnd/evolve/service.py` (`_enforce_d12`, about +6 lines)

After the `llm-inferred` branch and before `user-supplied`:

```python
elif source in ("sample", "common-sense"):
    if (status, modality) != ("proposed", "deontic"):
        raise EvolutionError(
            "new sample and common-sense constraints must be proposed/deontic (D-12)"
        )
```

The catch-all refusal keeps its text. It already omits `induced`, which IK2
admitted without changing it, and its text is pinned for `explicit`,
`imported` and an unknown source by IK2's table (VG2-D2).

### Pages

- `provenance-and-modality.md`, "Evolve admission (D-12)": two bullets after
  the `llm-inferred` one, "A new `sample` constraint is `proposed` and
  `deontic`: it records rows that are evidence, never a review." and the
  same for `common-sense` with library evidence; the refusal table gains
  the new refusal's row.
- `evolution-contract.md`: §6's bullet list gains "a new `sample` or
  `common-sense` rule is `proposed`, `deontic`"; the `:279-280` sentence
  names the two sources.
- `docs/release-notes.md`: one entry under the unreleased heading, naming
  the R0.3 exception.
- `unattended-growth.md`: unchanged. Lines 93–95 and 289 already say what
  the code now admits; T3 reads them.

## 7. Decisions

Ruled by delegated approval (auto=true), 2026-11-23 `(d)`.

| ID | Question | Readings and their cost | Ruling |
|---|---|---|---|
| VG2-D1 | Instrument | prose; the phase is a validation predicate, for which corpus-first is the default, but its cases are eight rows of one table that T2 and T5 enumerate in full | this prose |
| VG2-D2 | The refusal text for a `sample` or `common-sense` constraint that is not `proposed`/`deontic` | (a) a dedicated refusal naming the two sources, as `llm-inferred` has; the catch-all unchanged. (b) also rewrite the catch-all to list every admitted combination: 9 more IK2 rows change text, and every consumer that quotes it | (a). Same exit either way; (a) moves the fewest pinned strings |
| VG2-D3 | IK2's table | (a) keep the fixture at `328061ee` and apply an explicit, counted VG2 delta in T5. (b) re-capture the fixture: the historical evidence would then describe new bytes | (a) |
| VG2-D4 | Where VG2's tests live | a new `tests/test_vg2_evolve_sources.py`, reusing the guidance test's translator and the acceptance test's replay driver | as stated |

Budget: one diff review round through the review helper (plan D7).
Compatibility: admits inputs 0.4.0 refuses, refuses nothing it admits
(plan §5).

## 8. Tests

`tests/test_vg2_evolve_sources.py`, default lane, unless the row names
another file.

| # | Case | Expected |
|---|---|---|
| T1 | the acceptance test's grown unattended workspace; one more round whose reply, written in the growth document's shape, adds a fact type with two sample rows and two constraints: a `rows`-basis uniqueness constraint and a `library`-basis value constraint. Translated by `_translate`, previewed and applied with `--policy additive` | preview exit 0, `policy_issues` empty; apply exit 0; the published model holds one `sample` and one `common-sense` constraint, both `proposed` and `deontic`; `gnd validate --document … --require-documents` over every round document, exit 0 |
| T2 | on the evolve-policy fixture model, which has no unattended mode: a new constraint with each of `sample`, `common-sense` × `confirmed`/`deontic` and `proposed`/`alethic` (four cases) | preview exits 3; the refusal is "new sample and common-sense constraints must be proposed/deontic (D-12)". Controls: each source with `proposed`/`deontic` previews, exit 0; a `sample` constraint with `provenance.induction` exits 3 with the induction refusal |
| T3 | the D-12 section of `provenance-and-modality.md`, §6 of `evolution-contract.md` and the "Evidence" paragraph of `unattended-growth.md` | each names `sample` and `common-sense` as `proposed` and `deontic` for a new constraint; the set of sources the D-12 section admits for a new constraint equals the set `_enforce_d12` admits, computed by running it over every source |
| T4 | VG2-C4's negative controls on T1's workspace: the same round with the `rows` constraint's span removed; the same round with the value constraint `alethic` | the first exits 3 at preview, U5, at the constraint; the second exits 3 at preview (candidate validation, U8, or D-12: the test asserts exit 3 and that the refusal names U8 or D-12) |
| T5 | `tests/test_induced_provenance.py::test_t5_d12_outcomes_equal_the_base_commit_table`, amended: the captured table at `328061ee` with a VG2 delta of exactly eight rows applied | the two `proposed:deontic` rows read `admitted`; the six other `sample` and `common-sense` rows read the new refusal; every other row unchanged |

Branch table. The new branch has two outcomes, admit and refuse; each
source reaches both (T2, T5). The induction refusal precedes it (T2). The
catch-all still answers `explicit`, `imported` and unknown sources (T5).

### Verification-selection ledger

| Obligation | Disposition | Command or evidence | Input boundary | Justification | Invalidation |
|---|---|---|---|---|---|
| VG2-C1 to C4; T1–T5 | run | `uv run pytest -q tests/test_vg2_evolve_sources.py tests/test_evolve_additive_policy.py tests/test_evolve_loading.py tests/test_unattended_growth_guidance.py tests/test_unattended_mode.py tests/test_induced_provenance.py --tb=short`, exit 0 | `evolve/service.py`, the two reference pages, the growth page, the fixtures named | the plan §9 VG2 lane as written | any change to those |
| The maintenance page's lane: `tests/test_evolve_*.py`, `tests/test_unattended_*.py` | run | `uv run pytest -q tests/test_evolve_*.py tests/test_unattended_*.py --tb=short`, exit 0 | the evolve and unattended code | "Done when" of the maintenance page | as above |
| Guards | run | the `project.md` guard block, exit 0 (packaged-skill manifests: two reference pages change) | packaged skills, structure | issue 171 | any file outside `.gnd-planning/` |
| Lint | run | `uv run ruff check src tests tools`, exit 0 | | plan D11 | |
| Component index | run | `python3 scripts/components_index.py changed --base <VG2 base> --strict`, exit 0 | `dev/components/` | plan H28 | |

## 9. Out of scope for this phase

- Rewriting the catch-all refusal (VG2-D2).
- `unattended-growth.md`'s text (unchanged); its new section is VG5's.
- Any change to U5, U8, D-03 or validation.
- Unattended include roots (VG3, VG4).

## 10. Size

About 6 source lines, about 20 page lines, about 200 test lines.

## 11. Approval instrument

This prose (VG2-D1).

## Implementation findings, recorded as they were found `(d)`

2026-11-23. The branch took `main` with GO1 (`fdffdcd1`) at `11ca75b0`;
`_enforce_d12` was unchanged there (one line of offset), so every citation
held.

1. **Test-authoring slips.** T3 first expected D-12 to refuse a proposed,
   deontic `induced` constraint; D-12 admits it, and the induction block is
   required by candidate validation. T4 first edited operations in place;
   they are immutable, and the test rebuilds them. Neither changed a rule.
2. **Review r1 (Codex), F1, fixed at `53280cba`.** The new refusal was not
   in `_evolve_service_exit`'s marker list, so the command exited 70. The
   marker joins the D-12 markers; the change is an RF5 successor in
   `evidence/VG2/source-successors.json`, chained after IK2's row.
3. **Review r1, F2, a corrected claim.** The brief said a changed constraint
   is judged as before. D-12 judges a new or changed constraint by one rule
   (its home's first sentence), so a `sample` or `common-sense` constraint
   that changes and stays `proposed`/`deontic` is now admitted. This spec's
   §6 already wrote "a changed constraint still has to be … sample or
   common-sense and proposed/deontic" into the contract. Pinned by a test.
4. **Review r1, F3, a corrected claim.** On an unattended model a
   `confirmed` or `alethic` constraint is refused by U2 or U8 first, because
   candidate validation precedes D-12. VG2-C2's named refusal holds on a
   model without the mode; on any model the exit is 3.
5. **Review r1, F4, fixed at `53280cba`.** T3's section reader matched a
   heading inside a fenced example; it now reads sections outside fenced
   blocks.
