---
milestone: pyrel-rules-coverage
station: "phase-RP4"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RP4
date: 2026-11-22
gates:
  - command: "uv run pytest -q tests/test_rp4_role_value.py tests/test_rp3_number.py tests/test_rp1_external_uniqueness.py tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_derivations.py tests/test_rules_in_pyrel.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_ossie_formulas.py tests/test_ossie_export.py --tb=short"
    exit: 0
    output: "278 passed, 253 deselected in 26.30s"
  - command: "uv run pytest -q -m pyrel_oracle tests/test_rp4_role_value.py tests/test_rp3_number.py tests/test_rp1_external_uniqueness.py tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_derivations.py tests/test_pyrel_rules_plans.py --tb=short"
    exit: 0
    output: "282 passed, 126 deselected in 360.57s (0:06:00)"
    note: "opted in by the owner for this milestone (plan §8); the plan-program suite joins because universes for create effects moved"
  - command: "the project.md structure and inventory guard block (12 files)"
    exit: 0
    output: "679 passed, 2 deselected in 95.57s (0:01:35)"
  - command: "uv run ruff check src tests tools"
    exit: 0
    output: "All checks passed!"
  - command: "uv run ruff check"
    exit: 1
    output: "Found 198 errors."
    note: "known red, unchanged (RP2's record)"
  - command: "render every fixture and example model under both targets here and at f02c58d8, compare SHA-256"
    exit: 0
    output: "573 programs accepted at the base; 0 changed; 0 newly refused; 20 newly accepted (role-scoped value models)"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the unchanged broad controls are outside this phase's impact closure"
evidence:
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/phase-RP4-spec.md
    sha256: 8c27d84c579c85df74b7455905409b0c81a4cac4d7ba29c1895b5e326956b26b
  - path: src/gnd/export/pyrel_rules.py
    sha256: 449b67805f08b7ca3e43b6706aa41d01a72dd20072acd80ae0cb7369ef9a0da2
  - path: src/gnd/export/ossie_formulas.py
    sha256: 9f7c4d6f10a4bcb242709251f5f1da7bd2409878823835cb853622b8b167c93a
  - path: docs/runtimes/pyrel.md
    sha256: 014e743eab2890a875dd9617f94183ca5a66df08210f8aa8f45e8dbb9571899d
  - path: tests/test_rp4_role_value.py
    sha256: df3d886742ad0a3dee7a46a4aa3afedbcc310bb56ac01327aab3a8d7eb1dfe51
  - path: tests/test_rp2_anchored.py
    sha256: 726ac9a3ce5b5593393286eaf555090b4e82392d94052bdf55a1abee8c730c16
  - path: tests/support/pyrel_application_successors.py
    sha256: 77277babbb9cde455e67d4e0e6b4c6551ee9638c0c6291114fe40ced3431907f
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/RP4/dynamic-query-successor.json
    sha256: 5d681ef8727f43f89cccbc88fe6424408c3fda56a1e5c69d66a24aa65c8b019d
  - path: tests/fixtures/pyrel-rules-coverage/rp4/any-named-deny.population.json
    sha256: b1200a75d39081c206f35a36b70aa98da8f922639ecbf1693d762bfd4d4eac75
  - path: tests/fixtures/pyrel-rules-coverage/rp4/any-named-empty-role.population.json
    sha256: 7b55c2be0f3fb653c8877050e5f7329d72a078410b25d15579116af90e9d14a3
  - path: tests/fixtures/pyrel-rules-coverage/rp4/any-named-other-role.population.json
    sha256: 2aaa2c4d867bc555b5b35f13e7f0c9842b98a4c504a6dad9f1556c9a21ae22e7
  - path: tests/fixtures/pyrel-rules-coverage/rp4/any-named.orm.json
    sha256: 20d4730537e4d6937a20531e61197a38ca062d8cc11d47733f895a8dcdb25e7a
  - path: tests/fixtures/pyrel-rules-coverage/rp4/create-named.orm.json
    sha256: 339e92d407d420fa3cabb49132e6262f57bbb70134fa7e097214ea00c4865737
  - path: tests/fixtures/pyrel-rules-coverage/rp4/deny.population.json
    sha256: df3afbce412d0e50ee80290679a1ba690bb74f738f44b2b9dce573e2384d71cc
  - path: tests/fixtures/pyrel-rules-coverage/rp4/empty-role.population.json
    sha256: 580e61fc60f2ec091bde2b64178920b50594e94c5439835a9df8f5afcce71c78
  - path: tests/fixtures/pyrel-rules-coverage/rp4/fact-plain.orm.json
    sha256: 291da941078576734358ee6c2ecf2abfa14eefa1fec652e348a6e3cf44502b2a
  - path: tests/fixtures/pyrel-rules-coverage/rp4/fact.orm.json
    sha256: 43b015988335a3eb522be3fb9b8c985a198d85deffbc1d21357a607299bc86a6
  - path: tests/fixtures/pyrel-rules-coverage/rp4/other-role.population.json
    sha256: aaabdd83fc07f181b310851936535fa30e690bd93f76501e352bbe77e56a2b2d
  - path: tests/fixtures/pyrel-rules-coverage/rp4/range-deny.population.json
    sha256: 612f53bf66f5383541b4d8940a96215c3947e6610707cc9531f3fc1ba530eabc
  - path: tests/fixtures/pyrel-rules-coverage/rp4/range-pass.population.json
    sha256: 24ed55fb7631aa60a63eed52e7ec7b150cb7fd92437bfd07ad77c9058e630a2f
  - path: tests/fixtures/pyrel-rules-coverage/rp4/range.orm.json
    sha256: c50fe4662e9b928d17921ed7d8a6ead59647f6ee4e9d284b9c71cbd525cbd47a
  - path: tests/fixtures/pyrel-rules-coverage/rp4/roster.population.json
    sha256: 3c9ff8ec19ee5c23e03dd0aa8625ef5292214395277d445e0f15069a77843422
  - path: tests/fixtures/pyrel-rules-coverage/rp4/top.orm.json
    sha256: 1ddb2192321f338d9413e718523abd72c52a6cf8b3a9c5e74097b45f3078a0ee
  - path: tests/fixtures/pyrel-rules-coverage/rp4/universe-name.orm.json
    sha256: bf83c4ad1a2a4903802db0a14c1c784e11b8162290fd7366cfe1730a45ed66ac
  - path: tests/fixtures/pyrel-rules-coverage/rp4/universe-named-deny.population.json
    sha256: 76b2a8e5490280bc3054b38e5cc85bbaa937d21324178986a0f85b1ea5af8e87
  - path: tests/fixtures/pyrel-rules-coverage/rp4/universe-named-empty-role.population.json
    sha256: 7badcf77d7957a0357c2157745ab12e81db5ba78845192878d5b38b5e129bd12
  - path: tests/fixtures/pyrel-rules-coverage/rp4/universe-named-other-role.population.json
    sha256: 53ddacac6b0c8e735365b4416b8b326c7d44c184f92749768336f25b32ee6968
  - path: tests/fixtures/pyrel-rules-coverage/rp4/universe-named.orm.json
    sha256: 063b61f45bad0efa32c5827bf91f8f1f27d2163fb5f6944dab57e204afbf9d5c
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/BRIEF.md
    sha256: 9304962c1a242fe368e19451c6794ce800bbbb9e23990d43fedafa670d960d0b
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/review.md
    sha256: 585f24a4bfe0a0e40348da48c9cb03a7f7c657cd89edc519c11dd5ac91ee98ba
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/FINDINGS.md
    sha256: ea4108d0d15ed10987d833186d898070372ca63fedc9008e8dc2a92ee33efa98
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/BRIEF.md
    sha256: 0fdd472636d8cc3174e5ac462e91a162e442a657b97f10d215dc27cdf57c95e3
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/review.md
    sha256: 3992b39a2e3aba20a0ae7b4e3eafa7a884ef594868f8fc3a8e27e54f3cdfe88b
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/FINDINGS.md
    sha256: 2388c65e5591109d9093a2fe215ba461fe225ec10e3a236fcb5e69a2b2b3cc4a
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/BRIEF.md
    sha256: 9c808c3007930c6a0343f3aa86c261fa6c508e9260a431a15b17f991d4be7b5e
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/review.md
    sha256: 7760330ca0daf57fd056f4cfcf237209ae48312aef11f63f1370014006fa7c12
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/FINDINGS.md
    sha256: 89c2e1978fd352a9ba66dd5e7575c0744260070d2781658e1b4e00d4d00c2d6e
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r4/BRIEF.md
    sha256: e6a89bffc0338274563eebafd16091fee42019db79bd9542087dd6ef31813c94
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r4/review.md
    sha256: edaf05db274e075ac407c92a8fdfb1a18581fd44b9f77b12e52657b264d0fcba
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r4/FINDINGS.md
    sha256: 4a1b7ccb2534a9836920bc713f6a8c6352d71b315c741c135c2c20084d24af99
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r5/BRIEF.md
    sha256: 1a113cd0ebb1680775a63a2e1c6b83ff6eb3e53017a479fbb459b5a352178730
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r5/review.md
    sha256: e3af3fdd0b8fcc5e2a7b4ad34b340c439593ddd93a55be3aa90c9b1d801ba9de
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r5/FINDINGS.md
    sha256: 7533b03025a8c1f6a0ba5f665a0ea5fba18fc48c3aee49e15a2b1132cb0319af
---

# Claim

RP4's criteria C1–C3 hold at these bytes. Value constraints with a
`role_ref`, written at the top level or on a fact type, compile in both
programs. Their DuckDB verdicts and witnesses equal `gnd check`'s: a
disallowed value in the role fails; the same value in another role or only
in the roster passes; an empty role is vacuous. This holds for allowed lists
and ranges alike. The quantity fixture exports. Every program accepted at
the base keeps its bytes, and the Ossie export is unchanged.

## What shipped

- `export/pyrel_rules.py`:
  - `_value` with `role_ref`: the domain is one atom over the role's fact
    type, vacuous when that list is empty, no roster read. The `role_ref` is
    checked (shape; the role is played by `object_type`).
  - The fact-scoped dispatch admits `value`. Without `role_ref` it covers
    the object type's universe, as GND scopes it.
  - `_Model.value_rules` and `_Model.allowed_lists` give value rules one
    home, by the id they lower with (fact-scoped `<fact>#<i>` included). The
    allowed relations' rendering, constant set and type lookup read it.
  - `_universe` records each generated `<type>_any` where the lowering
    creates it, and in `requirements` for a plan's create effects. Rendering
    and the name-collision check read that record, so a fact type merely
    named `…_any` is read as itself, and a real clash is refused by name.
- `export/ossie_formulas.py`: a value rule written on a fact type stays an
  Ossie extension, as before (plan §0).
- `docs/runtimes/pyrel.md`: role-scoped value constraints.
- `tests/test_rp2_anchored.py`: the quantity fixture now renders, so RP2's
  test asserts that it lists its anchored rule.
- RF6: `evidence/RP4/dynamic-query-successor.json`, chained after RP3's.

## Gate output (verbatim)

    278 passed, 253 deselected in 26.30s
    282 passed, 126 deselected in 360.57s (0:06:00)
    679 passed, 2 deselected in 95.57s (0:01:35)
    All checks passed!
    Found 198 errors.            (uv run ruff check; known red)

## Criteria, measured

| Criterion | Test | Result |
|---|---|---|
| C1 | `test_role_scoped_value_models_export[top, fact]` (both targets), `test_the_role_scoped_domain_is_the_role_not_the_universe` | pass |
| C2 | `test_duckdb_program_agrees_with_gnd[top-*, fact-*, range-*]` (oracle) | 1, 0, 0, 2; range 1, 0 — agreeing |
| C3 | `test_role_scoped_value_models_export[time]` (both targets) | exit 0 |
| fact-scoped universe | `[fact-plain-*]` (oracle) | 1 each, agreeing |
| Ossie unchanged | `test_ossie_export_is_unchanged` (4, incl. `fact-plain`) | digests at `33bd03db` / `f02c58d8` |
| names | `[any-named-*]`, `[universe-named-*]` (oracle); `..._range_universe_is_refused`, `..._plan_created_universe_is_refused` | pass |
| totality | `test_a_malformed_role_ref_is_refused_by_name` (4) | pass |

## Review

One reviewer is one reviewer: Codex, read-only, through the review helper.
Every finding was reproduced, fixed and given a regression test:

- r1, three findings:
  - F1: a range universe missing from the name check;
  - F2: Ossie lowering changed for fact-scoped value rules;
  - F3: a range rule's type lookup, and RP2's quantity test.
- r2, one finding: a fact type named `…_any` taken for a universe.
- r3, one finding: the name check took `<type>_any` for a universe.
- r4, one finding, predating RP4: plan-created universes were unrecorded.
- r5 (scoped to r4): APPROVE, no findings.

The r4 repair has been reread. `review.log` files are not retained.

## Refactoring review

Executed:
- Value rules and generated universes each have one record on the model,
  replacing three name-based lookups that each scanned top-level rules or
  guessed from a suffix.
- The byte comparison shows the change preserves every accepted program.

Not executed: the remaining suffix-based fallback in `_relation_roles` is
reached only for relations that are not fact types or helpers. Round 3
probed 28 suffix variants without a failure, so it stays.

## Boundary — what this phase does NOT establish

- No RelationalAI engine ran; the LQP program's enforcement is unverified.
- Agreement covers the fixtures listed; value rules on derived roles go
  through the existing derivation path, unchanged here.
- `uv run ruff check` over the whole tree stays red (known).

## Open questions

None new.
