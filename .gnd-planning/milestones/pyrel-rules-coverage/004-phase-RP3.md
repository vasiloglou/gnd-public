---
milestone: pyrel-rules-coverage
station: "phase-RP3"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RP3
date: 2026-11-22
gates:
  - command: "uv run pytest -q tests/test_rp3_number.py tests/test_rp1_external_uniqueness.py tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_derivations.py tests/test_rules_in_pyrel.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_ossie_formulas.py tests/test_ossie_export.py --tb=short"
    exit: 0
    output: "260 passed, 233 deselected in 26.83s"
  - command: "uv run pytest -q -m pyrel_oracle tests/test_rp3_number.py tests/test_rp1_external_uniqueness.py tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_derivations.py --tb=short"
    exit: 0
    output: "217 passed, 105 deselected in 218.58s (0:03:38)"
    note: "opted in by the owner for this milestone (plan §8); the derivations file joins the oracle lane because RP3 changes its refusal messages"
  - command: "the project.md structure and inventory guard block (12 files)"
    exit: 0
    output: "679 passed, 2 deselected in 96.10s (0:01:36)"
  - command: "uv run ruff check src tests tools"
    exit: 0
    output: "All checks passed!"
  - command: "uv run ruff check"
    exit: 1
    output: "Found 198 errors."
    note: "known red, unchanged (RP2's record)"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the unchanged broad controls are outside this phase's impact closure"
evidence:
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/phase-RP3-spec.md
    sha256: 19564054fe0ac09eca659f0247500328db655ed8021e8dc3e4acfa8f8d2160dd
  - path: src/gnd/export/pyrel_rules.py
    sha256: 1118889620d1f42200ed04fa3402e475f96710d52ace03905a417d2430919ca7
  - path: docs/runtimes/pyrel.md
    sha256: a76ce7354ca28253e60c6a68ff04fb681d4b1f96bfc9098772a8cc26bac4e747
  - path: tests/test_rp3_number.py
    sha256: dd8f7422641d41839ded7d3d965c7a233156f7d60d8c35ebaea3a296e3221812
  - path: tests/test_pyrel_rules.py
    sha256: bcc7a1c457a0fd943edbda94e5952c8bdc99ca2ccc06d535af17684f8791eeb8
  - path: tests/test_pyrel_rules_derivations.py
    sha256: 77d2d97bf1400e0ad754c3ab19aabbfdfb5160958dabcc9930eec056289cb579
  - path: tests/support/pyrel_application_successors.py
    sha256: ab99a0f3d1232d7b78b68d5f31d8d30efee3e30fc4f6180ddc3fe78ee719d6b7
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/RP3/dynamic-query-successor.json
    sha256: c4ead81606deb9bef17fc06d9d3adbadfab0760e8b9d396c509fa6d8079160fd
  - path: tests/fixtures/pyrel-rules-coverage/rp3/allowed-beyond.orm.json
    sha256: 2575c355fe4ccd2f83bc2476423300bbf5327a06eeed0639e24c174c437563c8
  - path: tests/fixtures/pyrel-rules-coverage/rp3/anchor-beyond.population.json
    sha256: f00a0d53b9f7b4220143065540d33ffaa6c263b8284348504616d6adb2528860
  - path: tests/fixtures/pyrel-rules-coverage/rp3/arithmetic.orm.json
    sha256: b31092be400e78f3f7041b24b6070943ba4edd4d4b0d2bae0c0e3081caf3a643
  - path: tests/fixtures/pyrel-rules-coverage/rp3/at-bound.population.json
    sha256: 12cd79553b2b897406e5e95ec9c88dafad316e248659c5301bd197b6627f039f
  - path: tests/fixtures/pyrel-rules-coverage/rp3/beyond.population.json
    sha256: 27d6e2c35ba5331560a77ba9e96e4a2f7fb9d9af1ca12f8fdb78a9d3bc7ee702
  - path: tests/fixtures/pyrel-rules-coverage/rp3/boolean.population.json
    sha256: 38393e12ee97f26369196be0e7b6b0f30bf46f6fa8a4cdbb3eae5973a7ae42ae
  - path: tests/fixtures/pyrel-rules-coverage/rp3/compare-beyond.orm.json
    sha256: 80fb56a869275989629944365fc0a5f7f9da331083432626b3116f8efa4bb779
  - path: tests/fixtures/pyrel-rules-coverage/rp3/computed-beyond.orm.json
    sha256: 5488c3748dc840b7e849b164ed413035943b7eb9d75512ad0af431492297131b
  - path: tests/fixtures/pyrel-rules-coverage/rp3/count-into-number.orm.json
    sha256: 0fa8a742a93907832b5656ffcc1cd601f0d967c1a1dd328a33ddff27856ffb15
  - path: tests/fixtures/pyrel-rules-coverage/rp3/duplicate.population.json
    sha256: c1605ddab8a000905d28a565cb73d0a7ffedad7e83f3d48b7c08698a9b9e2f22
  - path: tests/fixtures/pyrel-rules-coverage/rp3/float.orm.json
    sha256: ecdb57e13faaba619f167d6618862d058a58a819f0ebafd2616c108f904a2822
  - path: tests/fixtures/pyrel-rules-coverage/rp3/head-beyond.orm.json
    sha256: 69f059e275880aed9be4dc6456209c93e42214dea07ce2d2eba6a2f59f3a9bbd
  - path: tests/fixtures/pyrel-rules-coverage/rp3/int-arithmetic.orm.json
    sha256: eaf10ef2dfe8a875e73d90c64f4e566be5a4a36d25854ea6ea278a92171ad60e
  - path: tests/fixtures/pyrel-rules-coverage/rp3/nested-beyond.orm.json
    sha256: ee679d3a118a2eaeab704f93ea912e0c8378a25a3c1639a40f25fd1fb6621e5e
  - path: tests/fixtures/pyrel-rules-coverage/rp3/order-beyond.orm.json
    sha256: 79af57f7dd1d1cf82a57ed41471c9bef552f50f1acf8643da753bb1eea64b0a4
  - path: tests/fixtures/pyrel-rules-coverage/rp3/pass.population.json
    sha256: 86f49f990c7d5951f566f7bffb2c3810d2ec2bde1d53f18b6674ccd4133ebae4
  - path: tests/fixtures/pyrel-rules-coverage/rp3/range-beyond.orm.json
    sha256: edaaa636d7cc2784afc46d9d27fd4bd332351d77313b54230326f995f6582e33
  - path: tests/fixtures/pyrel-rules-coverage/rp3/reference/empty.population.json
    sha256: 5dcdcebedb882943583c4c8291fd90832f73eaa611181e7877ff1356e8eaba3b
  - path: tests/fixtures/pyrel-rules-coverage/rp3/reference/model.orm.json
    sha256: 8900d383d92ebfda5a0a1570a3e85f30d1056a061e298173a5dfafb9b2f5eba5
  - path: tests/fixtures/pyrel-rules-coverage/rp3/reference/references/anchors.pop.json
    sha256: ccb5aba04ba3505c5394b214dc293d326e7a9b0529919a2d6ee7c48b28845c6f
  - path: tests/fixtures/pyrel-rules-coverage/rp3/six-line.orm.json
    sha256: d27c126262a79e01d7cc919c56749aef083a6d52d4eccc5b9697399608b98668
  - path: tests/fixtures/pyrel-rules-coverage/rp3/sum-compared.orm.json
    sha256: 7e01ba8ecc9fa2e7d324426a50e7f679d5234d26b8c0f3e3a4ef0e42fc029fc4
  - path: tests/fixtures/pyrel-rules-coverage/rp3/sum-into-number.orm.json
    sha256: cc2882bd9140dfc2959c33c2ae61da5543ae10c072631966eddf476a50c987d9
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/BRIEF.md
    sha256: 548192d94078d7d81c90fa879d5d048b63712c0f4b1a5cbc8b939435bd9283fe
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/review.md
    sha256: 0762c18d8e80cc5572e06ef06c27827a0f9d9ddd58bc81967c217b8798458fa3
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/FINDINGS.md
    sha256: 59e0f1728182748e85efeb15afc1d73ce30930a4cd0a2125d68a647831253a39
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/BRIEF.md
    sha256: 70863fe1db8c76ef705d1e190d3ca21d9c5833dbc50d7d27360606466d178bf8
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/review.md
    sha256: 388fc6325925ffbf19c72ab525ff6709c062c6e1732982a5ca12f4b880304f48
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/FINDINGS.md
    sha256: 34bfe782a79c5c254ec0b20b26c6242a05027bf412c32072ce3d98cf760bc6ec
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/BRIEF.md
    sha256: 8e4b2ec53e01eb61dae4c68791363cab47bc4355eeb9101334f8faae5576ec51
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/review.md
    sha256: 1dd3d195baee2300266fd21344a40b2760edc6098d7ed4f946be60284d1fce08
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/FINDINGS.md
    sha256: 2a18e0e567d4f6fbf9c5d3f872e9a5bc4c8fd9a5f72e985af32081876fe0b178
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/BRIEF.md
    sha256: 8fc4d3b44fb26ef55f2a3afc871c62b8a31528ed2dd34ac212aca2b43f6b91d4
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/review.md
    sha256: ab7a2fb8ce665b79c8439b66e282e5524f13591cc08f5a990871c14152504c39
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/FINDINGS.md
    sha256: 59e102ba5ac46cbb55f1a95c371d39d7738faca99d693bc927443cab76774e13
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r4/BRIEF.md
    sha256: 03cc65f2b8ff8b3352f2b9803a0f282e4a329c5ea8e228a628967fdc2f19aeaf
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r4/FINDINGS.md
    sha256: 3e301ba96742cc92ac6d0b073a007fd5f85fd90839b6f07403526b1ac114dd56
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r6/BRIEF.md
    sha256: 033b01c52a2a01b8a32b0e93713f4bb80595f980ca6da9f24ca4f31bdd0d432c
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r6/FINDINGS.md
    sha256: f8232e6541d22904bb6f2e3618ef53cce1aa3ed9dde9098ab5acf3e88b0b44ec
---

# Claim

RP3's criteria C1–C5 hold at these bytes. `Number` exports as PyRel `Float`
with GND's admission rule, and no accepted input gives either program a
number a binary float would round. Integers beyond 2**53 are refused by
name (exit 3) wherever a Float or Number value is held, compared or
computed. RP1's deferred review finding is closed.

## What shipped

- `export/pyrel_rules.py`:
  - `_TYPES["Number"] = "Float"`; `raw_primitive` keeps `Number`, so
    messages name it. `check_cell` admits for `Number` what it admits for
    `Float`, and refuses an integer beyond `EXACT_FLOAT` (2**53, rendered
    from `_EXACT_FLOAT`) in either. That covers cells, rosters, plan
    bindings and, newly, embedded reference facts and rosters.
  - Model constants: `_literal` bounds every integer written into a Float
    field (`allowed`, ranges, atom literals).
  - `_refuse_binary_context`: where a Float or Number value takes part in a
    guarded or derivation comparison, every literal at any depth is bounded
    and any arithmetic term is refused. "Takes part" is read from every
    role a variable fills (`_binary_variables`).
  - `_refuse_inexact_head`: a Float or Number head role takes a Float or
    Number value, a count, a min or max of such values, or a constant. A
    sum over or into one is refused. The aggregate result's type is known
    to the comparison guard.
  - Arithmetic refusals name `Float or Number values`.
- `tests/test_pyrel_rules.py`: the shared comparator compares witnesses by
  GND's numeric identity (an integral float equals its integer), because
  the programs print Float values as floats and GND echoes the input's
  form. It reads models without a top-level `constraints` key.
- `tests/test_pyrel_rules_derivations.py`: two expectations follow the
  renamed message.
- `docs/runtimes/pyrel.md`: `Number` as `Float`, and D6.
- RF6: `evidence/RP3/dynamic-query-successor.json`, chained after RP1's.

## Gate output (verbatim)

    260 passed, 233 deselected in 26.83s
    217 passed, 105 deselected in 218.58s (0:03:38)
    679 passed, 2 deselected in 96.10s (0:01:36)
    All checks passed!
    Found 198 errors.            (uv run ruff check; known red)

## Criteria, measured

| Criterion | Test | Result |
|---|---|---|
| C1 | `test_number_models_render` (4), `test_number_is_a_float_field` | pass |
| C2 | `test_duckdb_program_agrees_with_gnd[pass, duplicate, at-bound, decimal]` (oracle), `test_a_boolean_in_a_number_role_is_refused_by_both` | agree; 3 both |
| C3 | `test_arithmetic_on_a_number_value_is_refused_as_on_float` | pass |
| C4 | `test_an_integer_beyond_2_53_is_refused_by_name[Number, Float]` (oracle); 2**53 admitted (`at-bound`) | 3; GND 1 |
| C5 | `test_a_model_constant_beyond_2_53_is_refused_at_export` (allowed, range, compare) | exit 3 |
| RP1 r2-F1 | `test_rp1_deferred_float_anchors_beyond_2_53_are_refused` (oracle) | 3; GND 1 |
| plan §0 Ossie | `test_ossie_export_is_unchanged` (2) | digests from `6e04fe7f` |
| review regressions | `test_integer_arithmetic_still_exports`, `test_a_nested_computed_or_head_constant_beyond_2_53_is_refused` (4), `test_reference_facts_beyond_2_53_are_refused`, `test_a_sum_into_a_number_head_is_refused`, `test_a_count_into_a_number_head_still_exports`, `test_an_integer_sum_compared_with_a_number_value_is_refused` | pass |

## Implementation findings

1. The first cumulative run used `$T` unquoted under zsh, which does not
   word-split, so pytest ran no tests (exit 4). That run is not evidence;
   every gate above uses explicit lists.
2. GND refuses an Integer variable copied into a Number head role at
   validation (`semantic:derivation-term-type`); the programs' refusal of
   that case is defensive only.

## Review

One reviewer is one reviewer: Codex, read-only, through the review helper.
Every finding was reproduced before its repair, and each has a regression
test:

- r1 (`phase-RP3-r1/`), CHANGES_REQUESTED, four findings, all fixed:
  - F1: the guard looked up a function term as a type, a crash;
  - F2: nested and head constants escaped;
  - F3: reference facts skipped the cell checks;
  - F4: two existing tests expected the old message.
- r2: two findings, fixed:
  - F1: a constant computed by arithmetic escaped;
  - F2: a Number role behind an Integer antecedent hid the context.
- r3: one finding, fixed: aggregates into a Float or Number head.
- r4: ended without a verdict (the provider's content flag).
- r5 (the same scope rerun): one finding, fixed: an Integer aggregate
  result compared with a Number variable.
- r6: ended without a verdict, the same way as r4.

Rounds stop there. The r5 repair is verified by its regression test and the
lanes above, not by a second reader. The findings after r1 were gaps in
RP3's own scope, not defects its repairs introduced. The milestone close
review (the full GND panel) rereads RP3. `review.log` files are not
retained.

## Refactoring review

Executed: the D6 checks for comparisons share one helper,
`_refuse_binary_context`, used by the guarded and derivation paths. Head
roles have their own, `_refuse_inexact_head`. The bound is one constant
rendered into the program.

Not executed: `_atom_types` keeps its first-role `setdefault`. The program's
variable declarations depend on it, so the guard reads every role through
`_binary_variables` instead of changing the declared types.

## Boundary — what this phase does NOT establish

- No RelationalAI engine ran; the LQP program's enforcement is unverified.
- The programs are stricter than GND here, by design (D6, stated): an
  integer beyond 2**53 in a Float or Number context, arithmetic next to a
  Float or Number value, and a sum over or into one are refused (exit 3)
  where GND decides them exactly.
- The comparator treats `1` and `1.0` as one witness value (GND's identity);
  it cannot tell a program that prints the other form.
- The last repair (r5-F1) has not been reread by an independent reviewer.
- `uv run ruff check` over the whole tree stays red (known).

## Open questions

None new.
