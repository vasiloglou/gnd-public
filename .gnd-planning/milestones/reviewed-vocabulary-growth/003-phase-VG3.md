---
milestone: reviewed-vocabulary-growth
station: "phase-VG3"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-VG3
date: 2026-11-23
gates:
  - command: "uv run pytest -q tests/test_vg3_unattended_includes.py tests/test_unattended_mode.py tests/test_unattended_span_coverage.py tests/test_mc1_model_includes.py tests/test_mc1_guards.py tests/test_include_root_close.py --tb=short"
    exit: 0
    output: "334 passed in 22.53s"
    note: "the plan's section 9 VG3 lane with the new file, at 01b76996"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 124.18s (0:02:04)"
  - command: "uv run ruff check src tests tools"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base 3ea39d7f --strict"
    exit: 0
    output: "changed against 3ea39d7f (3ea39d7): 26 file(s) differ; 0 to fix, 0 warning(s), 7 to reread"
  - command: "uv run pytest -q --tb=no -p no:cacheprovider <the 22 test files named test_mc*, test_unattended*, test_ir*, test_lx*, test_evolve_source*, test_growth*, test_include*>"
    exit: 1
    output: "5 failed, 718 passed, 2 deselected in 121.31s (0:02:01)"
    note: "a wider sweep, not a selected gate; the 5 failures are tests/test_ir3_pyrel_includes.py T3 (4) and T6, red at main 1f403b07 before this milestone (known red, below)"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request, or the milestone-close default lane"
  reason: "the context variable is set only by _model_warnings, and remap_issues changes only for id selectors; the include and unattended consumers ran in the wider sweep above"
evidence:
  - path: src/gnd/model/_unattended.py
    sha256: 524c76737685b786c093420bb07ebf11af48edba4d50e3a7ff778c449a0bbdca
  - path: src/gnd/model/_includes.py
    sha256: e218841aaf5022193d2778d51628d24ef6c928d6d136682ce2e36df212857db6
  - path: src/gnd/model/__init__.py
    sha256: 4bf2f5ecff9b4ef2371b5b8adcc0e4dda5d4af0c15279d7a9805fb14410b7204
  - path: src/gnd/commands/checking.py
    sha256: 48fee6b3300644a4632ca7966a911f475c6e5cea7fd2f512ae6a291168ec6843
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    sha256: a77e4427db612ad496addaadb3a1f3a4400b09338e0018496524e411af12ed9e
  - path: tests/test_vg3_unattended_includes.py
    sha256: 638250a7fc07a9bba58bf10baf5d776da24b31ef18ccb06219bc5e018f101715
  - path: tests/vg3_cases.py
    sha256: 73121ddc981b2cf6c878265d812c79124b810ebc13266e329bc6fadd20095cb6
  - path: tests/fixtures/vg3/base-outputs.json
    sha256: 4a95873c1f51e12707f1d0332f7e2b378e0842418d3896925628221aa4c1b436
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/VG3/source-successors.json
    sha256: 3cfe99852c33fdcdcfdb2cf46896e2e3bdeb54e85a0186956d905fe4cbefe498
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/phase-VG3-spec.md
    sha256: 309388b01aeb093d9c7f5c47453f894e2766b2bfa53a32cca5ae3bbc34aa2df1
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG3-r1/review.md
    sha256: f2244ff06ba84b7c018e54853eb5e6b61583f0fc4006855d9baf293964ee5a26
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG3-r1/FINDINGS.md
    sha256: 959fec08908418433a22a2370a08d2c1d1c373c2a2f13aab17b0fa3943797c2f
---

# Claim

At `01b76996`, the VG3 lane exited 0 (334 passed), the guard block exited 0
(679 passed), `uv run ruff check src tests tools` exited 0 and the
component-index check exited 0. Issue 222's root validates, exit 0, with
`--document` and `--require-documents`, and its text output names the
include. A root 0.4.0 validates gives the exit, issues, span counts and JSON
payload captured before the first edit.

## What shipped

- `src/gnd/model/_includes.py`: `included_rows(document, origins)`, the one
  origin test: it walks `_ids`, the walk `_merge` keys origins by, and keeps
  the elements whose origin is an include. `include_attribution(model)`:
  one row of counts per include, read from the included file's own document.
  `remap_issues` maps `$.object_types[id=…]` as it maps fact types, matching
  each declared element's whole selector text (review r1, F2).
- `src/gnd/model/_unattended.py`: a context variable `_INCLUDED`, read by
  `_rule_unattended`: included elements skip U2–U6, keep U8 unless
  `confirmed` (D13 (a)) and keep U7 on spans over a root-declared document,
  sample spans on fact types only (review r1, F1). The span walk skips an
  included span that names no root-declared document (D14 (a)).
- `src/gnd/model/__init__.py`: `_model_warnings` sets `_INCLUDED` around
  `semantic_validate` and resets it; `gnd.model` re-exports
  `included_rows`, `include_attribution` and `remap_issues`.
- `src/gnd/commands/checking.py`: the `--document` walk receives the
  include set and its issues are remapped (H37); the text output of an
  unattended root prints one `INCLUDE` line per include before `OK:`, on the
  redacted path too (VG3-D4). JSON is unchanged (D5 (a)).
- `representation-format.md`: "An unattended root that includes a reviewed
  model" under "Unattended source"; "Model includes" cites it.
- `docs/release-notes.md`: one entry.
- Tests: `tests/test_vg3_unattended_includes.py` (T1–T13 and three review
  regressions) with `tests/vg3_cases.py`; `tests/fixtures/vg3/base-outputs.json`,
  14 outputs captured with the source unchanged at `3ea39d7f`.
- Outside the plan's §3 list (spec findings 1, 2, 4, 5):
  `evidence/VG3/source-successors.json` and
  `tests/support/rf9_ci_sources.py` register the `_cmd_validate` change as an
  RF5 successor chained after RN0; `tests/test_mc3_source_observations.py`
  follows registered successors; `tests/test_mc1_model_includes.py` T44
  keeps its remap claim with a U8 case; `tests/test_unattended_span_coverage.py`
  a13's fake passes the include set through.
- `dev/components/`: `model.loading`, `model.validation` and
  `cli.checking_command` name the additions; the seven subsystem entries the
  check lists were re-read and are still accurate.

Measured size: 797 lines added and 29 removed under `src` and `tests`
(`git diff --stat 3ea39d7f 01b76996`), against an estimate of about 470; the
difference is the base-output fixture (about 200 lines) and the review
regressions.

## Gate output (verbatim)

    $ uv run pytest -q tests/test_vg3_unattended_includes.py tests/test_unattended_mode.py tests/test_unattended_span_coverage.py tests/test_mc1_model_includes.py tests/test_mc1_guards.py tests/test_include_root_close.py --tb=short
    334 passed in 22.53s
    $ uv run pytest -q <the project.md guard block> --tb=short
    679 passed, 2 deselected in 124.18s (0:02:04)
    $ uv run ruff check src tests tools
    All checks passed!
    $ python3 scripts/components_index.py changed --base 3ea39d7f --strict
    changed against 3ea39d7f (3ea39d7): 26 file(s) differ; 0 to fix, 0 warning(s), 7 to reread

## The criteria

| Criterion | Test | Result |
|---|---|---|
| VG3-C1 | T1: issue 222's root, `--document --require-documents`; control: with the origin test emptied, U2–U5 fire under `includes[seed]:` | exit 0; control exit 3 |
| VG3-C2 | T2: five root-owned defects through the CLI, the confirmed operation at the rule | each exits 3 with its rule at a root address |
| VG3-C3 | T3: an attached constraint without a span; as `alethic` `sample` | U5; U8; at `$.fact_type_constraints[0].constraints[0]` |
| VG3-C4 | T4 | `include:forbidden-section`; U2–U5 on the seed alone |
| VG3-C5 | T5: counted and re-hashed over the root's document; ignored over another document, as a non-mapping, with a non-string digest; a root operation's span not counted; a malformed included span over the root's document is U7 under `includes[seed]:` with and without `--document` | as stated |
| VG3-C6 | T6 | the `INCLUDE` line with the seed's counts; none in JSON |
| VG3-C7 | T7: 8 outputs of models without the mode | byte-identical to the base |
| VG3-C8 | T8, R1-F2 | `includes[seed]:$.object_types[id=work]…` |
| VG3-C9 | T9 | `proposed`: exit 3, U8 under `includes[seed]:`; `confirmed`: exit 0 |
| VG3-C10 | T10: 6 outputs of the H30 root | equal to the base; text exit 0 differs by the `INCLUDE` line only |
| VG3-C11 | T11, text and JSON | `unattended:excerpt-mismatch` at `includes[seed]:…` |
| rule 2 | T13: an include of 1,000 object types and 1,000 fact types | `gnd validate` under 10 s |

## Review

One reviewer is one reviewer: Codex (default model, effort high, read-only)
through the review helper, round `notes/reviews/phase-VG3-r1/`, over the
diff from `3ea39d7f` to the working tree at `6034a651`. Verdict
`CHANGES_REQUESTED`, two findings, both reproduced and fixed at `01b76996`
with regression tests that failed first:

- F1, blocking: U7 read `sample_spans` on included object types and
  constraints, so a root 0.4.0 accepts could be refused.
- F2, hardening: an id holding a newline lost the `includes[ID]:` prefix.

The reviewer checked and found true: eleven tests runnable without writing
files, the fourteen base comparisons (recaptured), five root-owned CLI
defects, the operation, obligation and attached-constraint rule cases,
twelve included U8 source and status probes, the included-span filter, six
forbidden-include cases, and that the context variable is restored. It
could not run the filesystem-dependent suite. It noted that the spec's
bytes differed from the brief, because the implementation findings were
appended while it ran. The brief's diff also swept in the untracked VG2
draft spec, which this phase does not commit. `review.md` and `review.log`
were sanitized by the helper, which says so at the top of each.

Audit against the branch table: owned against included for each of U2–U8
(T2, T3, T9, T1's control); an included span over a root document (T5,
T11), over another document, not a mapping, or with a non-string digest
(T5), malformed over a root document (T5); sample spans on an included
object type (R1-F1).

## Refactoring review

None needed beyond what shipped, argued from what the phase touched: the
origin test is one function read by both walks, and the selector matching
in `remap_issues` was rewritten rather than extended with a second pattern.
The remaining positional pattern in `remap_issues`, which finds the
composed section and index at the start of a path, reads addresses this
module writes; replacing it with structured origins is deferred (open
questions).

## Boundary -- what this phase does NOT establish

- One reviewer is one reviewer. The fix commit `01b76996` carries no review
  opinion; the round read `6034a651`.
- GND checks an include's bytes against the pin and that the file is a
  valid model; it cannot know who reviewed it (plan §6, a named limit).
- The `INCLUDE` line is in text output only; a host reading JSON sees the
  prefix on issue paths but not the counts (D5 (a)).
- Spans on operations and obligations stay unchecked and uncounted.
- `gnd check` and `gnd judgments check` print no attribution (plan §6).
- U1's first-document rule (D4) and growth rounds are VG4's.
- The wider sweep is not a selected gate; the five IR3 failures in it are
  a known red, not VG3's.

## Known red

`tests/test_ir3_pyrel_includes.py` T3 (four parameters) and T6 fail at
`main` `1f403b07`, verified in that checkout on beast-3, and at VG1's head
`5427e8fe`. T6's golden `duckdb-small-flat` lacks the `EXACT_FLOAT` line RP3
added after IR3 recorded it (the milestone coordinator's reading). The
owner has a separate fix proposed; VG3 changes no PyRel code.

## Open questions

- `remap_issues` still finds the composed address with a pattern over
  addresses `_includes` writes. Passing the origin with each issue would
  remove it. Target: a maintenance pass, if the owner wants one.
- VG4: U1's first-document rule, read on the root's own document (plan D4).

## Refuted premises

- The spec's T7 and T10 said the base literals were "captured at
  `7b68c558`". They were captured with the source unchanged at `3ea39d7f`,
  which differs from `7b68c558` only by this spec.
