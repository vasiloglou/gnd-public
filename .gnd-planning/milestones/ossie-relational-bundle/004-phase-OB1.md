---
milestone: ossie-relational-bundle
station: "phase-OB1"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-OB1
date: 2026-11-24
gates:
  - command: "ruling: owner approved .gnd-planning/milestones/ossie-relational-bundle/notes/phase-OB1-spec.md sha256 068f24c4f1368ff0d0c2a5749be953ba1128b58cb1db809465dc1a77c1413824"
    exit: "n/a -- ruling"
  - command: "uv run pytest -q tests/test_ossie_export.py tests/test_ossie_import.py tests/test_rf1_cli_pins.py tests/test_rf7_input_policy.py --tb=short"
    exit: 0
    output: "448 passed in 51.44s"
    note: "plan §9 OB1 row, plus the two affected consumers found during the phase (spec IF7)"
  - command: "the project.md structure and inventory guard block (16 files)"
    exit: 1
    output: "1 failed, 865 passed, 2 deselected in 122.14s (0:02:02)"
    note: "the one failure, tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap, is a known red: it fails identically on the phase base a7847f2b with this diff stashed (see Gate)"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base a7847f2b --strict"
    exit: 0
    output: "changed against a7847f2b (a7847f2): 25 file(s) differ; 0 to fix, 0 warning(s), 4 to reread"
    note: "the reread entries are subsystem.check, cli.checking_command, cli.export_command and infra.input_policy. Each was read beside the diff and is still accurate. cli.arguments, export.ossie and model.ossie_import gained byte-bound verbs."
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the broad controls are outside this phase's impact closure"
evidence:
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/phase-OB1-spec.md
    sha256: f5df83d463d4f3effdd7b418fbce8ea1181bb632b0c9b83ed26b65425596b505
  - path: src/gnd/export/ossie.py
    sha256: bd2c4e0abf50bb2b642693bd94a22f49398344dcd4a2e70fa1eebb22088231eb
  - path: src/gnd/ossie_import.py
    sha256: 7f5bbee55d033c1e77b4caefa5a90c53a8205f952dcccfe528e6cf4af2973e6d
  - path: src/gnd/input_policy.py
    sha256: 2421a5626641eab913131f50db7c8c7ad1b0cba612b532323cb71178fa213f93
  - path: src/gnd/commands/_arguments.py
    sha256: 69d0943f858d1bdb16b79578a5aaf285e34ad967e66351526d4d55f0415e61ab
  - path: src/gnd/commands/export.py
    sha256: 76a6a1bf27315b9b9266f645dbd57a8dd71cfd30b6e074a5fd99770f5c9a5ae1
  - path: src/gnd/commands/checking.py
    sha256: 993f6d4a198a0207f04f55d813fcf3db20f783436526876568529f9a0d5bb4bd
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    sha256: 47781711cd46738a3a2c8064ae5def4f065adea97061f3c524c21e42fc02cfea
  - path: tests/test_ossie_export.py
    sha256: 1137a0893c380365c8d87b3b84926ecec08fd9c2df24761012f70a3b510be416
  - path: tests/test_ossie_import.py
    sha256: 83c00bfaf305256816a862f48c2241cb623ece2e013853217578910d9b5bd081
  - path: tests/test_rf1_cli_pins.py
    sha256: 798f7fc8e8504ac0814907af22c7c2157bd2269fbe49ff43c263b5bd45be5bbf
  - path: tests/support/ossie_large.py
    sha256: 223322bc505b56563d1bc7726a44d63ab9011ed44da6b0ef7aed4f7f3b642f20
  - path: tests/fixtures/ossie_ob1_baseline.json
    sha256: 2380653ac758335f73d51f48446ea0137a498d7604d4cb4f36c75e3225b02835
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB1-r1/review.md
    sha256: f8272abfba9eaa08b4760c98674a9a27dcce3cd346da4a6b6602a61d1a308c92
    note: "sanitized; the reviewer's original bytes are e3407a134a02cf1f4942812b26a55652f15665b347af02a4eeda78980a1a479f, bound by run.json"
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB1-r1/SANITIZATION.md
    sha256: 8dccb00b735218b490fbe8ca100156ed9b1c2aebcffc8d06eec2a0ba0447ff4e
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB1-r1/FINDINGS.md
    sha256: 03dad4871dae51f76dd8cec0636931cbb5135b4182473befdee668145e493644
---

# Phase OB1: parameters for the Ossie size bounds

## Claim

- **Export flag.** `gnd export ossie` takes `--max-output-bytes N`, which
  bounds each written artifact. The default is 10485760 bytes and the
  ceiling 268435456.
- **Unchanged default.** Without the flag, every census export is
  byte-identical to the baseline at `1926e895`: 82 entries, 41 models in two
  formats (T1).
- **Large exports.** The generated 5,000-fact model has a 10.95 MB loss
  report. It publishes with `--max-output-bytes 33554432` and is refused at
  the default with `ossie:output-size` (T2, T2b).
- **Each artifact bounded.** Whichever artifact is largest, the run refuses
  at that size minus 1 and publishes at that size (T3, T3a). A strict
  refusal still precedes the size refusal (T3b).
- **Import flag** (D3 b). `gnd import ossie` takes `--max-input-bytes N`.
  - It moves the read cap, the YAML guard, both JSON decoder caps and the
    loss-size cap (2N).
  - The model-size cap stays fixed (T6, T6b, T6c).
  - The large bundle round-trips in JSON and YAML to a model equal to its
    source (T6).
- **Invalid bounds.** An invalid N exits 64 for either flag before any read
  (T4, T6d). The library functions refuse one with `ValueError`.
- **Docs.** The normative paragraph in `representation-format.md` §
  "Ossie interchange" states the flags, the default, the ceiling, exit 64
  and the kept cap.

## Gate

The front matter gives each command and its exit verbatim.

**Known red.** `tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap`
fails on the phase base. This diff was set aside with
`git stash push -u -m ob1-knownred-check-7b24`, and the test ran on base
`a7847f2b`:

    FAILED tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap
    1 failed in 0.47s

The stash was then applied by SHA and dropped. The test checks that
`.agents/skills/review-pr/SKILL.md` resolves `../process-phase/references/review-tool.md`.
That is a discovery-link layout this worktree has not adopted (AGENTS.md:
`uv run gnd install --symlink --project --force`), and OB1 touches no part
of it.

## Review

There was one reviewer, Codex, run through `review_tool.py` with a read-only
sandbox and effort high. **One reviewer is one reviewer.**

| Item | Value |
|---|---|
| Brief sha256 | `f14e9e6c…6083` |
| Review | [review.md](notes/reviews/phase-OB1-r1/review.md), sha256 `e3407a13…479f` as written, `f8272abf…8c92` after path sanitization ([SANITIZATION.md](notes/reviews/phase-OB1-r1/SANITIZATION.md)) |
| Verdict | CHANGES_REQUESTED, with two findings |
| Ledger | [FINDINGS.md](notes/reviews/phase-OB1-r1/FINDINGS.md) |

| Id | Class | Reproduced | Disposition |
|---|---|---|---|
| F1 | blocking | yes: 4 RF7 controls failed | **fixed.** Defaults resolve `MAX_BYTES` per call. The four existing RF7 tests are the regressions, shown failing on the pre-fix bytes. |
| F2 | completeness | yes | **fixed** for the normative paragraph. Rejected for the help text: help states defaults and is not a normative home. |

The reviewer independently confirmed several claims:
- All 82 baseline entries match.
- Each artifact is bounded at size minus 1, and the strict refusal comes
  first.
- An invalid bound exits 64 with no model read, including a 5,000-digit
  integer.
- Large JSON and YAML bundles round-trip, and the loss-size and model-size
  behaviour is as claimed.
- The 10 MiB defaults are exact.

Its standing matcher probes found no input the code mishandles.

**The repaired bytes are not reviewed.** These are F1, F2 and the
refactoring below, which came after the review. No second round ran.

## Refactoring review

**Refactor EXECUTED.**
- **What:** `render_ossie` and `plan_ossie_import` each validated their bound
  with a copy of the same check. Both now call
  `input_policy.require_byte_bound(name, value)`.
- **Behaviour:** preserved. The messages still name the parameter.
- **Tests:** `test_ob1_library_bound_is_validated` covers the export side,
  and the new `test_ob1_library_input_bound_is_validated` covers the import
  side.
- **Gate:** the same focused gate and guard block reran green apart from the
  known red.

**Seen and deferred.**
- **The defect:** `input_policy.guard_yaml` still captures `MAX_BYTES` in its
  default argument at definition time. This is the class F1 found in the
  code OB1 added, but it predates OB1 and OB1 does not change it. A test that
  lowers `MAX_BYTES` does not lower `guard_yaml`'s default.
- **Where it goes:** an open-questions row in this milestone (below), for
  the OB5 or close sweep.

## Refuted premises and findings

The spec's §12 lists IF1–IF9. The ones that change what an earlier document
says:

- **IF1, a refuted premise.** Plan r2 §1.2 says no test covered
  `ossie:output-size`. One did, in `tests/test_ossie_import.py`.
- **IF2.** The plan named five import caps. There were six: `JSONDecoder`
  re-checks the cap after `loads`.
- **IF3.** Spec T6b is unreachable for the YAML guard and the JSON decode
  caps, because they equal the read cap over the same bytes.
- **IF7.** The plan's §9 affected-consumer list missed the CLI pins and the
  RF7 input-policy tests.
- **IF9, for D11.** The measured output-to-source ratio is about 6×. A
  32 MiB export needs a source of only about 5.3 MB, so D11 probably needs
  no work. This is an estimate, pending the reporter's model size (D10).

## Open questions

| Id | Question | Target |
|---|---|---|
| OB1-Q1 | Should `guard_yaml`'s default `max_bytes` resolve `MAX_BYTES` at call time, like `loads` now does? | the OB5 or milestone-close sweep |
| OB1-Q2 | D11: is a source-cap parameter needed? IF9 suggests not. | after D10's answer |

## Boundary

- **Size** (spec §10 estimated about 70 source and 220 test lines):
  - Source: 121 lines added and 38 removed across six modules. About 1.7×
    the estimate, because of the decoder cap (IF2), the per-call defaults
    (F1) and the shared check.
  - Tests: 256 lines in test files, plus a 48-line support module and the
    780-line baseline data file.
- **Not done:** no semantic model, mapping or Rmap (OB2–OB4); no streaming;
  no change to `MAX_BYTES` or `MAX_MODEL_BYTES`.
- **Not run:** the opt-in oracle lane, and the evidence and census lanes.
- **Approval:** this record approves nothing beyond OB1. Merge is the
  owner's.
