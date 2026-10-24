---
milestone: induced-knowledge
station: phase-IK1
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: phase-IK1
date: 2026-10-24
gate:
  command: "uv run pytest -q -p no:randomly <56 affected test files, listed in evidence/IK1/final-gate.txt>"
  exit: 0
  output: "2309 passed, 55 deselected in 404.89s (0:06:44)"
  note: >-
    Direct IK1 tests (tests/test_object_type_description.py, 58 tests) plus
    affected consumers: schema sync, verbalization, vocabulary, projection,
    codegen, conformance, evolve, validation, diff/report schemas, redaction,
    packaged skills, the RF1 pins and mutation harness, the RF5/RF6 controls and
    the successor inventories. The default lane filter (pyproject addopts)
    deselected 55. Lint: ruff check on every changed Python file, "All checks
    passed!".
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection or separately configured CI"
  reason: "outside IK1's impact closure; the reduced v6.3 selection was run"
evidence:
  - path: src/gnd/schema/orm-meta.schema.json
    sha256: 907ae7b80e19372027f461ae6f6f3e695fe5931aed79f549f2fd2b3c7d6a6d70
  - path: src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json
    sha256: 907ae7b80e19372027f461ae6f6f3e695fe5931aed79f549f2fd2b3c7d6a6d70
  - path: src/gnd/model/_validation.py
    sha256: 5b9552ffc8b9f28a3dbdd6f5e11401a145acd997fb16edaa6b44801d9924742b
  - path: src/gnd/verbalize.py
    sha256: 98009ad082388edce4b86c3ef54b80f6137989cfd17d383aa3416d82bfa28eb3
  - path: src/gnd/model_verbalization.py
    sha256: 760c5b4314dfad52065a0e1088ed68ceb946a6428504ad0ab96287edc39bdac8
  - path: src/gnd/vocabulary.py
    sha256: 2cd1301882b058fdd42835e6f9aa1131d153e30bb97f5627a7a7c8ab1ebfc5bd
  - path: src/gnd/codegen/docstrings.py
    sha256: 05e3176c42d9178025f67e28aa33f0e2fe0122d9c22777f960e5f2f98c1825b8
  - path: src/gnd/anchors.py
    sha256: fe25cfc0501ff9d7515efb16323a23a64996ad538961093d2b638ea39e0b52c6
  - path: src/gnd/diff.py
    sha256: b0af505ba3245b4b6f42fc31c8b5cc95c6f2cd806371038a9461aad613262ee9
  - path: src/gnd/diff.schema.json
    sha256: 0e528953e9ada1cbc1ef5f2404b131b37877fbe18a1474659b9e9c4383f35107
  - path: src/gnd/report.schema.json
    sha256: beaedd0226a14c2ad53088fcb62e3faae61d4a93060e6d149ecdbbbf3cd79350
  - path: src/gnd/evolve/service.py
    sha256: 330471dbd282d6217803f91c5dde6578dad77021ae1d65e10414f96dc5744346
  - path: src/gnd/evolve/models.py
    sha256: 236c1a61a946550da4cf11fa08fb304d8b158fafea1bbd848dab9743b280ff20
  - path: src/gnd/diff.reference.md
    sha256: ae2b8ce40d9d4d5626aa7b06e951c9d989bf151cb759d0bea53eb59822dfa244
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    sha256: 7ab683bb84a75658989d8ad9a7b4dba3aab3c60611bcf6760152f49e130c0eea
  - path: src/gnd/skills/gnd-orm-core/references/constraint-reference.md
    sha256: a1877c9822c3afc97875aa1c6304472641e04069a0d844f9276d93c3808018b2
  - path: src/gnd/skills/gnd-orm-core/references/verbalization-patterns.md
    sha256: 1b0c7ebd695d017484a4adb1cce48742373a4a613e53ac716ed114c872289579
  - path: src/gnd/skills/gnd-model-evolve/references/evolution-contract.md
    sha256: 9f941a4d07b3458b9538931fd691d7304f5e7757267f7478aaffe1581336dd48
  - path: src/gnd/skills/gnd-extract/SKILL.md
    sha256: cfe2a8a882ad9d9ee2d92aa3d0a4f7cd7eee524d95bb718137068fcb81de0e16
  - path: tests/test_object_type_description.py
    sha256: 05bbf22561ab43d0610d3fe8257f13ecdf59090f68356e6e041d8686a2d6ea3b
  - path: tests/fixtures/induced_knowledge/ik1-baseline.json
    sha256: a5af09dd986b8fd0e7552761277667b48e62d18b1ba9426b66ad4a98e907b4b8
  - path: tests/support/pyrel_application_successors.py
    sha256: 079bc7693731a1ae0bbe5f2da4b4da1887f2f13d42d6de0e122cd63d8dd0d11d
  - path: .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/source-successors.json
    sha256: 2630f420ce2a718fda016c9ff6e238142e9b1090e10641070f6f693f12ded7fb
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK1/dynamic-query-successor.json
    sha256: e371da7d26d2c78caccb2fdb4786dfe0e1c81f212572ed1c0191eb00c17c9e9e
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK1/capture_ik1_baseline.py
    sha256: 68ad6d531e03de0f6b747d195c0b2cda709593200bba24f570a555f82a1b57e8
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK1/final-gate.txt
    sha256: 0c499c9887d13a10f97e8c4962e4898ef4d7bbb90f0e87402c81bbc01dd9c768
  - path: .gnd-planning/milestones/induced-knowledge/notes/phase-IK1-spec.md
    sha256: 20cccbbdfde82206bcd87399948b8d0ac47af17669e0d1761c5dc75bb5dcb656
  - path: .gnd-planning/milestones/induced-knowledge/notes/phase-IK1-agent-review.md
    sha256: 351a8c1ba74f9adfb3e2a9a19b1ecc681373e77547b6a33c9823871a20714491
  - path: .gnd-planning/milestones/induced-knowledge/notes/induced-knowledge-plan.md
    sha256: 8afbdcbd4a7757053c8775cc4faaade1225534664ccd7cdb6ad22ae5b54cd51a
  - path: .gnd-planning/milestones/induced-knowledge/001-plan-gate.md
    sha256: bf8a5c382de2b9a73ea83372c72494dcb0f53350b1e19099d63a026e8005c1ee
  - path: tests/test_development_scaffold.py
    sha256: 278777a058afb9998a3deba3d8544a715a6bf1d7ab6b02a46967fd454033471f
---

# Phase IK1 — object-type descriptions

**Claim.** An object type may carry an optional `description` object. IK1-C1 to
C5 hold on the evidence below, and the outputs for undescribed models are
byte-identical to base commit B = `1d6eee0`.

## What shipped

- **Schema** (`orm-meta.schema.json`, both copies byte-identical):
  - `object_type.description` holds core keys `summary` (required), `row`,
    `source` and `notes`, each a `description_text` of 1–4,096 characters;
  - extras are typed by the recursive `description_extra`, which admits JSON
    values only (§12 amendment);
  - the model version is not bumped (D1).
- **Layer-1 screen** (`model/_validation.py`). One predicate,
  `_description_value_without_json_form`, scoped by path to object-type
  descriptions. It refuses NaN, infinity, lone surrogates and anchored YAML
  booleans with exit 3 (IK1-D6, F1, F5). Behaviour at B is unchanged everywhere
  else.
- **Escaping** (`verbalize.py`):
  - `neutralize_text` performs `_neutralize`'s escape steps without the cap, and
    `_neutralize` is now that function plus the unchanged cap;
  - `DESCRIPTION_CORE_KEYS` and `DESCRIPTION_LABELS` are the single home for
    order and labels;
  - `description_lines` is the one walk both prose renderers use.
- **Renderers.** In each case extras are never prose:
  - model verbalization appends `Description: '…'.` and the other core-key
    labels; the extras remain in `canonical=`;
  - the extraction vocabulary emits indented core-key lines, and the projection
    is unchanged;
  - codegen docstrings append ` — <summary>` to each role line.
- **Vocabulary digest** (`anchors.py`): the whole `description` is excluded (D11).
- **Diff** (`diff.py`, `diff.schema.json`, `report.schema.json`):
  - `description_annotations` compares descriptions by canonical JSON, extras
    included;
  - `gnd-diff/2` with `annotations` is emitted only when the list is non-empty
    (D12), and the `"schema_version": "gnd-diff/1",` anchor line is unchanged;
  - both schemas use `if`/`then`/`else` on the version, and the embedded copy
    equals its source;
  - redaction is not edited, and the pass-through is pinned under an active
    policy.
- **Evolve**: the surface is `object_types[<id>].description`, of kind
  `annotation`, and the `BlastRadiusEntry` literal gains `annotation`.
- **References**: `representation-format.md` (the field, extras, refusals,
  rendering and digest exclusion), `constraint-reference.md:47`,
  `verbalization-patterns.md`, `evolution-contract.md`, `diff.reference.md`,
  the gnd-extract `SKILL.md`, and the `extract/vocabulary.py` shim docstring.
- **RF successors** (F6): an RF6b definition-body successor for
  `gnd.model._layer1_structural`, and a new chained dynamic-candidate delta,
  `evidence/IK1/dynamic-query-successor.json` (7 added, 1 removed, no
  model-query widening).

Size, measured at record time with `git diff --numstat 1d6eee0 -- src tests`:
- 299 added source and schema lines, about 190 of them JSON schema;
- 42 added lines in packaged reference docs;
- 721 added test, fixture and support lines;
- 17 deleted lines.

The spec estimated about 110, 340 and 80. Tests ran over budget because T2, T7
and the review's regression cases are table-driven.

## Gate output (verbatim)

```
$ uv run pytest -q -p no:randomly <56 files; evidence/IK1/final-gate.txt>
2309 passed, 55 deselected in 404.89s (0:06:44)
$ uv run ruff check <changed .py files>
All checks passed!
```

Also run during the phase:
- the baseline capture at B, twice, byte-identical, with all 25 commands
  exiting 0 (`tests/fixtures/induced_knowledge/ik1-baseline.json`);
- the same capture on the implementation tree, equal (T7);
- the RF1 mutation `M-SEM-diff-schema` applied to `diff.py`. Its expected-red
  test failed (`1 failed`), so the anchor is still killed;
- review-mutant proofs. The new R4, R5 and R6 tests each fail (`1 failed`)
  against the corresponding mutant in an isolated copy of `src`, imported first
  through `PYTHONPATH`.

Planning-branch repair: `tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap`
failed at `eb18024` (the planning branch merged with B, before any IK1 code) and
passed at B. The four retained plan-review snapshots under
`evidence/plan-review-r{1,2}/` keep their original relative links. They are now
registered in `RETAINED_DOCUMENT_ORIGINS` with their original homes and the
digests the plan's provenance table records, following the `fb40ca3`
precedent. Afterwards: `uv run pytest -q tests/test_development_scaffold.py
tests/test_contributor_preparation.py tests/test_plan_app_docs.py
tests/test_rf4_peripheral.py` gives `1009 passed, 1 deselected`.

Known red outside IK1: `ruff check src` reports I001 in
`src/gnd/examples/expense/project/cli/expense_cli.py`, a file unchanged since
`a22ccde`. It is not in IK1's lint selection.

## Criteria

| Criterion | Result | Tests |
|---|---|---|
| C1 | met | T1, T2 (accepted, refused, IK1-D6 incl. review R1/R2, JSON-form scalars kept, scope outside descriptions) |
| C2 | met | T3 (full, at cap, fixed order), T4 (inside delimiter, summary only), T5, T6, T13, T14 |
| C3 | met | T8 (four change kinds, schema negatives, active redaction), T10, T11, T12 |
| C4 | met | T7 rows 1–7 against `ik1-baseline.json` (B = `1d6eee0`) |
| C5 | met for the surface; references review-checked | T9; reference text read by the reviewer |

No numeric threshold was moved. `L` = 4,096 was fixed at the gate (IK1-D1).

## Adversarial review

One local reviewer agent read `git diff 1d6eee0 ad52105` and tried to refute
C1–C5. **One reviewer is one reviewer**: this is not a panel. The reviewer could
run targeted commands and mutants, but not the full suite, `evolve apply` or
`finalize`, or exported PyRel programs.

There were no blocking findings. The coordinator reproduced the findings before
fixing them:
- R1 and R2 (hardening) were fixed under D6/D14, with tests that were red before
  the fix;
- R4, R5 and R6 (completeness) were fixed with tests proven to kill their
  mutants;
- R3 and R7 are deferred.

Findings are retained verbatim, with the disposition, in
[phase-IK1-agent-review.md](notes/phase-IK1-agent-review.md).

The reviewer confirmed, among other claims:
- schema twin identity;
- `_neutralize` identity with B over 20,009 fuzzed inputs;
- every renderer, digest and diff mutant it tried was killed;
- T7 rows recomputed from the B sources;
- descriptions on every object-type kind in all four fixtures pass validate,
  diff, codegen, conformance and extract.

**Coverage audit against the branch table:**
- every T row in §8 has at least one case that fails a wrong implementation;
- T6's allowlist check and T13 are non-regression guards by declaration;
- T13 alone cannot kill an escape mutant, but T5 does.

## Refactoring review

**Refactors EXECUTED:**
- `neutralize_text` factors `_neutralize`'s escape steps into one walk, the
  spec's rule 4. `_neutralize` output is identical, as T13 and the reviewer's
  fuzz show.
- `verbalize.description_lines` replaces two hand-written loops in model
  verbalization and the vocabulary, which answered the same question (order,
  labels, escaping) in two places. It landed after the review behind the same
  gate; R4's order test runs through it.

**Seen but deferred:**
- The `BlastRadiusEntry` surface list in `evolution-contract.md` had already
  drifted from the code before IK1 (it lacks `operation`). That is IK1-Q5, for
  milestone close.
- `codegen/docstrings.py` scans object types linearly per role in both
  `_display_name` and `_summary_suffix`. This is unchanged behaviour at fixture
  scale, and not worth a lookup index until profiling says otherwise. No row is
  needed.

## Boundary — what this phase does NOT establish

- One reviewer is one reviewer. The diff review is a single agent's reading, not
  a panel, and it did not run the full suite.
- The broad default and historical lanes were not run (`slow_cadence`). Only the
  reduced selection listed in the evidence ran.
- C5's reference updates are review-checked only, not test-checked (spec §8).
- Extras have no declared nesting bound. Refusal depth depends on Python's
  recursion limit, and evolve proposals cap JSON depth at 64 (R3, IK1-Q1).
- The text format of `gnd diff` does not show annotations; only JSON does
  (R7, IK1-Q2).
- The vocabulary's constraint-blindness is now structural only. A description
  can restate a constraint in prose, and GND does not inspect description
  wording.
- T7 row 4 hashes `.gnd-codegen.json` raw, including `gnd_version`, as the spec
  declares. A version bump needs a declared normalization (IK1-Q3).
- The runtime `__doc__` of generated tools turns escapes back into characters.
  That is pre-existing at B through readings, and T5 checks source text only
  (IK1-Q4).
- Descriptions on fact types, roles and constraints, any checker use, and any
  schema for extras are out of scope (spec §9).

## Open questions

| ID | Question | Target |
|---|---|---|
| IK1-Q1 | Declare a nesting cap for description extras (review suggests 64, matching `input_policy.MAX_DEPTH`) | owner ruling under IK-R12; before IK6 |
| IK1-Q2 | Show annotations in text-format `gnd diff` | IK6 docs/integration or milestone close |
| IK1-Q3 | Normalize `gnd_version` in T7 row 4, as row 5 does | the next phase that bumps the version |
| IK1-Q4 | Runtime `__doc__` line forging through escaped readings or summaries (pre-existing) | milestone close sweep |
| IK1-Q5 | `evolution-contract.md` surface list omits `operation` (pre-existing drift) | milestone close sweep |

## Refuted premises

- **The spec's "`representation-format.md` §272" is a line number, not the
  vocabulary-digest paragraph.** That line is the `depends_on` digest sentence;
  the sidecar composition lives only in `constraint-reference.md:47` (IK1-F2).
  The exclusion is recorded in the new field bullet and at line 47.
- **r4's `"additionalProperties": true` would carry every extra as JSON.** It
  does not: YAML timestamps pass an untyped schema node, and NaN, lone
  surrogates and anchored booleans pass even a typed one. The owner ruled exit 3
  (§12), and F1/F5 implement it.
