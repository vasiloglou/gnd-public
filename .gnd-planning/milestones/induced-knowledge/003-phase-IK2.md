---
milestone: induced-knowledge
station: phase-IK2
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: phase-IK2
date: 2026-10-24
gate:
  command: "uv run pytest -q -p no:randomly <90 affected test files, listed in evidence/IK2/gate-files.txt>"
  exit: 0
  output: "4003 passed, 61 deselected, 1 warning in 386.80s (0:06:26)"
  note: >-
    Direct IK2 tests (tests/test_induced_provenance.py: the approved 89-case
    corpus, the 27-row D-12 baseline, T6-T13 and the review regressions) plus
    IK1's 56-file gate and the IK2 impact closure: coverage (incl. the public
    goldens), exp sessions, rai import, skill prose, the RF5/RF6 controls,
    scaffold and docs. The default lane filter deselected 61. The one warning is
    pre-existing at B. Lint: ruff check on every changed Python file, "All
    checks passed!".
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection or separately configured CI"
  reason: "outside IK2's impact closure; the reduced v6.3 selection was run"
evidence:
  - path: src/gnd/schema/orm-meta.schema.json
    sha256: 9d35441bb3f732813ee62b81fc3751db59b7b7f055b75b9cb357d9c4de46f301
  - path: src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json
    sha256: 9d35441bb3f732813ee62b81fc3751db59b7b7f055b75b9cb357d9c4de46f301
  - path: src/gnd/model/_validation.py
    sha256: 38deb51e6bd14e69201986db97460e3d7dd9c5bdb1794ff4b2b768bb5640cfed
  - path: src/gnd/model/_induction.py
    sha256: 4f7a328333655e08d43bf061b51daa190cfa4eed0a02e6840add0923e0ca60d0
  - path: src/gnd/model/__init__.py
    sha256: da5a4f51a2f0b488b9b17e67e6bbbaf747d02ed17b53a5a20902ba2c53fab481
  - path: src/gnd/evolve/service.py
    sha256: 1b507a5374659bb2bedec13f0547f77d9fc1b99cc97b4da070c0f6e9579bee14
  - path: src/gnd/evolve/cli_service.py
    sha256: 75d1de3f2876d0186a9266827661a6569fa2e0f32bdf793baedf85933f4ade61
  - path: src/gnd/coverage.py
    sha256: 6580c084be92e4aab66b0ebabc1f8c21f7640d4b63af09e2996f5d2936b7ee93
  - path: src/gnd/coverage.schema.json
    sha256: 7f5836a58f21ce562b14cdb8b7bd974dd0e447c5de88db9dc6c3bdc89f7aaa15
  - path: src/gnd/exp/session_eval.py
    sha256: 4cbb4e95fa13bb79c2ed2f0393a58d10cdfcc74cef5aae0ecbb407787800ef6c
  - path: src/gnd/rai_import.py
    sha256: bcf01a19e185fbef577312dfad2785901827e641a3752341e58701c22b81cc46
  - path: src/gnd/skills/gnd-orm-core/references/provenance-and-modality.md
    sha256: d2d344780dd8e501bfe43b191fe23606c1aaa9dfab24e8ff7d65459aae44d93f
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    sha256: f12d3ddd7a3f9c40fe1dcab094b85a50b13c5e53dfef152057a623dd6e2eeedb
  - path: src/gnd/skills/gnd-orm-core/references/coverage-and-element-addressing.md
    sha256: d654a9f4c1a261e4f3a2de0bcc5127656a52c520d096db1a2095e798c503a028
  - path: src/gnd/skills/gnd-orm-core/SKILL.md
    sha256: 3c99c9ecf45a8385d0ee80007f50b32d2a5ee908a4578cad34765f106f9d3a0f
  - path: src/gnd/skills/gnd-model-evolve/SKILL.md
    sha256: b9be9d08e50a5894bb63fca106fcfc78a20e6e5144b1ed61d3924df372cef978
  - path: src/gnd/skills/gnd-model-evolve/references/evolution-contract.md
    sha256: a3cf3c448e49638508aff7da2edc17f16086aa700f4e1e9d21b6124e06a04fb2
  - path: src/gnd/skills/gnd-model-from-code/SKILL.md
    sha256: 271eae7fe9f0dfe300e64efad7a7025ef0ac6a716276b256ca8861b647a8934c
  - path: src/gnd/skills/gnd-model-from-text/SKILL.md
    sha256: 3ea6511cc5050e1fa8317acfb4d6495d7762d72f369ed6cf50c5d317ad313a78
  - path: tools/gnd_layers.json
    sha256: 65b44464ed6fce1d2a6c153940c37080d496c2e3da088bc763fc1571d11cf2fd
  - path: tests/test_induced_provenance.py
    sha256: 805ac536a61055241b9f265db2d0525a9d3ae1ef9d174a9e940fd01ac4009d86
  - path: tests/fixtures/induced_knowledge/ik2-corpus/README.md
    sha256: 114cf1fe0e18a3b32ea6fab5f10973d0e8766424e2840ffa24c1e594d7da6013
  - path: tests/fixtures/induced_knowledge/ik2-corpus/cases.json
    sha256: a348d696bdcfb4165b5ffb71017ce1e69872bbd658f91a813fd21288b5c524c1
  - path: tests/fixtures/induced_knowledge/ik2-corpus/expected.json
    sha256: a44a1b77845e63797ffa053d7e4b8b968a39683a7de3e8f0bbf1d99833447061
  - path: tests/fixtures/induced_knowledge/ik2-d12-baseline.json
    sha256: 6a8ad5a14db88097fa62e94240695888354fa18c4a4b03f91b3cd33932e4066a
  - path: tests/test_rf6_packages.py
    sha256: 85950aeb3a3b6e0e4059fbf70af87fa8d4fcf818e57385981faa3d2085c62879
  - path: tests/test_skill_prose_sync.py
    sha256: 3857378fd92213d39fdbe5a2c759fdca544d7136a1c6974fb4fd91a05324edc0
  - path: tests/support/pyrel_application_successors.py
    sha256: 5fa50913b498bca9cbdd7bbafc47f8cd957a79b9fdc5b0b0f0d4d8c0bbabe3d2
  - path: .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/source-successors.json
    sha256: 8797c52d3bf4a232025ee90a904587606d5cde7489a6616fc5d3a6b9cdbe16ed
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK2/dynamic-query-successor.json
    sha256: 98f2530ad6320a8b95c7a7e2daa674fd1346d04d0b1be7603f2e3216777f7671
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK2/build_dynamic_successor.py
    sha256: 1089719bc7c1f9a19034521bbb50036e2ff5cdb63cec9622fef52867996107f6
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK2/update_source_successors.py
    sha256: dd27c972d75e999cfd0a347b7c8316e29aef310928235c95051fb90a9beaaaef
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK2/build_ik2_corpus.py
    sha256: 1f85d391b81d05e2e93397867f21fc3e229e1b961d8e43f2a12c5f4dc3e7aca6
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK2/capture_ik2_d12_baseline.py
    sha256: be57524aaf9563e38decf78e240574b9731921ab1a1467811eae87f3b2afb5ea
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK2/corpus-red.txt
    sha256: 5b32e726cf804fe37a2ca90f8b5f51baab425b214badc68430753503559972a1
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK2/gate-files.txt
    sha256: eec5dc19d77620498eed0d0dfab3e2a2a40a09d6f459cd074596828211746c50
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK2/final-gate.txt
    sha256: 3e9ba8fcd7347e3b659aa6134c904b23f59b05187092329112886a01c4de65c3
  - path: .gnd-planning/milestones/induced-knowledge/notes/phase-IK2-spec.md
    sha256: e5f3f6b3372833222d9c0e384be3fb8a72239eafe0dba1c1e9618908d7bb9c76
  - path: .gnd-planning/milestones/induced-knowledge/notes/phase-IK2-agent-review.md
    sha256: 620398d2ce9b5d8347fe2501c3c8b26f6b12b3c5180f87ca0ab682fe24e2d054
  - path: .gnd-planning/milestones/induced-knowledge/notes/induced-knowledge-plan.md
    sha256: 8afbdcbd4a7757053c8775cc4faaade1225534664ccd7cdb6ad22ae5b54cd51a
---

# Phase IK2 — induced provenance and admission

**Claim.** IK2-C1 to C4 hold on the evidence below:
- A constraint may carry `source: induced` with a closed `provenance.induction`
  block.
- `gnd evolve` admits it only as proposed and deontic, and confirms it only as a
  reviewed status change in place.
- `gnd coverage` lists it.
- Every D-12 outcome at base commit B = `ebb1f04`, and every coverage output for
  models without induced constraints, is unchanged.

## What shipped

- **Schema** (both twins, byte-identical):
  - `induced` is the seventh `source_kind`;
  - `$defs.induction` is closed, with every bound from spec §6;
  - `provenance` under `induced` is closed to `induction` and `reviewed_in`, and
    `reviewed_in` is required once confirmed;
  - operations, preconditions and dynamic rules refuse `induced` (IK2-D2).
- **Loader:**
  - the layer-1 JSON-form screen also covers induction blocks of `induced`
    constraints, refusing NaN, infinity, anchored booleans, lone surrogates and
    dates (dates via the schema's string type);
  - `semantic:induced-provenance` checks that support counts are exact
    integers, `numerator ≤ denominator`, examples ≤ numerator, counterexamples
    ≤ the remainder, no id is in both lists, and no whitespace appears in a
    token, id, ref or digest;
  - `semantic:induced-confirmed-reviewed` refuses a blank `reviewed_in`;
  - `semantic:modality-policy` also warns on proposed/alethic induced rules,
    and its existing messages are byte-identical.
  
  The new rules live in the new home `gnd.model._induction`.
- **D-12 gate** (`evolve/service.py::_enforce_d12`, at preview, apply and
  finalize):
  - a new induced rule is admitted only as proposed/deontic without
    `reviewed_in`;
  - `confirmed` is admitted only as a status change of an unclaimed proposed
    induced predecessor on the same host, differing only in `status`,
    `modality` and an added non-blank `reviewed_in`;
  - `provenance.induction` under any other source is refused;
  - there are four named refusals (R-I1–R-I4), all exit 3 through
    `cli_service`;
  - the single in-order pass is kept, so every pre-IK2 refusal order holds.
- **Coverage:**
  - `schema_version` 5 (3 + induced) and 6 (4 + induced) carry a required,
    non-empty `induced` list, and the text view gains an `INDUCED` section;
  - versions 1–4 forbid the key;
  - constraint addressing is shared by the census and the induced view.
- **Other consumers:**
  - both exp-session verdict `Literal`s accept `induced`;
  - `rai_import`'s D-03 copy gains the `induced` row (IK2-D9).
- **References:**
  - `provenance-and-modality.md`: the seven-source taxonomy, the `induced` block
    and its bounds, the residual, the D-03 row, and the D-12 admission
    lifecycle, of which this file is the one home;
  - the representation-format rule table, the coverage reference, the evolution
    contract and four skills that counted sources.

## Gate output (verbatim)

```
$ uv run pytest -q -p no:randomly <90 files; evidence/IK2/gate-files.txt>
4003 passed, 61 deselected, 1 warning in 386.80s (0:06:26)
$ uv run ruff check <changed .py files>
All checks passed!
```

Also run during the phase:
- **Approval corpus:**
  - committed red at `ef39b1a`: 100 failed, 4 passed by design (`evidence/IK2/corpus-red.txt`);
  - all of it passes on the implementation.
- **D-12 baseline at B:** captured twice, byte-identical, and equal on the
  implementation (T5).
- **First gate run on `a35d8fe`:** 3,986 passed and 1 failed. The failure was the
  RF5 body pin of `_evolve_service_exit`, before its successor row existed.
- **Review regressions:**
  - every R1, R2 and R3 test failed on `a35d8fe` (7 failed in the red run) and
    passes after the fixes;
  - the 8 R5 tests each kill the reviewer's surviving mutant (8 of 8), and pass
    on the reviewer's unmutated copy of `a35d8fe` (8 passed).
- **The one warning:** it is in `test_exp_session_store.py` and also occurs at B
  (`1 passed, 1 warning`).

## Criteria

| Criterion | Result | Tests |
|---|---|---|
| C1 | met | T1, corpus L01–L38, R1, R2, R5 loader cases, T10, T12; the D-03 reference edit is review-checked |
| C2 | met | corpus A01–A17 (gate and preview), T5 (27-row baseline at B), T6, T7, T8, T9, R3, R5 re-confirmation |
| C3 | met | T11 (v5, v6, v3, schema negatives), R5 coverage rows and empty-list schema, T15 (public coverage goldens and the four coverage files unchanged) |
| C4 | met | corpus B01–B34, every row of the §6 bounds table at, below and above its limit |

No numeric bound was moved after implementation. The bounds are those approved
in IK2-D6.

## Adversarial review

One local reviewer agent read `git diff ef39b1a a35d8fe` and tried to refute
C1–C4. **One reviewer is one reviewer**: this is not a panel. It ran targeted
commands, mutants and the B tree, but not the full suite or real apply and
finalize runs.

The coordinator reproduced R1–R3 before fixing:
- **R1 (blocking):** float support counts passed validation and skipped the
  support checks. Fixed.
- **R2 (hardening):** the screen also changed `gnd validate` for an `induction`
  key under other sources, against IK2-D3. Fixed.
- **R3 (hardening):** a confirmation could move the rule to another host. Fixed
  by keying claims by host; spec finding F6 records that this narrows an
  approved sentence.
- **R4 (hardening):** induced entries in `rejected_proposals` go unchecked.
  Deferred to IK2-Q1.
- **R5 (completeness):** eight undiscriminated branches, and the coverage schema
  accepting `induced: []`. Fixed with tests.
- **R6 (docs):** recorded as spec finding F7.

The findings are retained verbatim with their disposition in
[phase-IK2-agent-review.md](notes/phase-IK2-agent-review.md).

The reviewer confirmed, among other claims:
- refusal order and the audit precedence;
- totality of the gate over hostile provenance and status;
- the CLI mapping;
- the gate call sites at preview, apply and finalize;
- that coverage JSON and text equal B byte for byte for 7 fixtures plus an
  `induction` key under `llm-inferred`, apart from `gnd_version`;
- schema twin identity;
- `rai_import`'s rows.

## Refactoring review

**Refactors EXECUTED:**
- **Coverage addressing has one home.** `_element_universe`'s two hand-written
  constraint loops became `_located` and `_constraint_address`, shared by the
  census and the induced view. Behaviour is unchanged: the public coverage
  goldens, the four coverage files and the reviewer's byte comparison with B all
  pass.
- **One screen predicate.** IK1's description-only screen became
  `_json_form_screened(path, induced)`. `_value_without_json_form` is the single
  predicate, and IK1's name is kept as an identity alias.
- **One constraint walk in evolve.** The gate's host-aware walk is a keyword on
  the existing `_constraints` reader, not a second walk.
- **Package split.** The IK2 semantic rules moved to `gnd.model._induction`, as
  the RF6 size ceiling requires (spec F4).

**Seen but deferred:**
- **A second D-03 copy (IK2-Q2).** `rai_import._default_modality` restates the
  D-03 table. IK2 kept it in agreement (IK2-D9), but it should read the one home
  rather than copy it.
- **Message-substring exit mapping (IK2-Q3).** `cli_service._evolve_service_exit`
  maps refusals to exits by message substrings, so every new refusal needs a
  marker and an RF5 successor. Typed refusal subclasses would remove that
  coupling.

## Boundary — what this phase does NOT establish

- One reviewer is one reviewer. The diff review is a single agent's reading, not
  a panel, and it did not run the full suite or real apply and finalize
  transactions.
- The broad default and historical lanes were not run (`slow_cadence`).
- **An induction block is a recorded claim.** The loader checks shape, bounds
  and arithmetic, never truth; a model has no population to recompute support
  from. IK4 and IK5 must compute what they write.
- **Single-token raw values** (`alice`, `42`) cannot be told apart from opaque
  ids (IK2-D5 residual).
- **Whether real learner output fits the block is untested** (§15 residual,
  carried to IK5).
- **Archived induced proposals in `rejected_proposals` are unchecked** (R4,
  IK2-Q1).
- **The trailing-newline pattern gap** in the five pre-existing `orm-meta`
  patterns is untouched (S1, IK2-Q5).
- **`gnd discover`, ILP import and automatic confirmation are out of scope**
  (spec §9).

## Open questions

| ID | Question | Target |
|---|---|---|
| IK2-Q1 | Validate induced entries in `rejected_proposals` (review R4), which would change validation for models valid at B | owner ruling; before IK4 emits proposals |
| IK2-Q2 | Make `rai_import._default_modality` read the D-03 table from its one home instead of copying it | milestone close sweep |
| IK2-Q3 | Replace `_evolve_service_exit`'s message-substring mapping with typed refusals | milestone close sweep, or the refactoring milestone that owns RF5 |
| IK2-Q4 | Confirm F6: a reviewed status change must stay on its host (narrows spec §6 "location-insensitive") | owner ruling at this record |
| IK2-Q5 | Trailing-newline acceptance in the pre-existing `orm-meta` `pattern`s (S1) | milestone close sweep |
| IK1-Q1 | Nesting cap for description extras (carried, still open) | owner ruling under IK-R12; before IK6 |

## Refuted premises

- **"No new module, lane or entry point" (spec §6 Registration).** The RF6
  package-size ceiling forced a new `gnd.model._induction` home. No lane or
  entry point was added (F4).
- **"Matching is location-insensitive, as the existing exact-match rule is"
  (§6).** That is right for unchanged constraints, and unsafe for confirmation
  (R3, F6).
- **"No string anywhere in the block contains whitespace" (§6 check 5).** This
  contradicts approved case L02. The check is scoped to the pattern-governed
  fields (F3).
