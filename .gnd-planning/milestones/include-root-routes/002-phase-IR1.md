---
milestone: include-root-routes
station: "phase-IR1"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-IR1
date: 2026-11-21
gates:
  - command: "uv run pytest -q tests/test_ir1_judgments_includes.py tests/test_mc1_guards.py tests/test_mc1_review_regressions.py tests/test_mc1_model_includes.py tests/test_public_v71_judgment_successor_guards.py tests/test_public_v71_full_judgments.py --tb=short"
    exit: 0
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py tests/test_release_text.py --tb=short"
    exit: 0
  - command: "uv run ruff check src tests tools"
    exit: 0
  - command: "uv run ruff check"
    exit: 1
evidence:
  - path: src/gnd/api.py
    commit: 6867be3c
    sha256: 076cc0564777fe406dde066973e9b7b541ceef2c6707432eb7bb468a05ca226c
  - path: src/gnd/judgments.py
    commit: 6867be3c
    sha256: 05940960e391335c055cb34cc55914aa60e5597189856eb557e40a711f52b2f9
  - path: src/gnd/model/__init__.py
    commit: 6867be3c
    sha256: f8a6c6f1bb24194efe17d2fd1f9f33662716581aa3245a9d006762c21883b90d
  - path: src/gnd/model/_includes.py
    commit: 6867be3c
    sha256: 4d68c5f7cff284b3a9c60bb79d006bbe116f29163c29f340e8c008fc26b16122
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    commit: 6867be3c
    sha256: 7774abfd669b09fbc975dc734d305e724a081e1a1d3b433e59162de81dbe7d3a
  - path: tests/test_ir1_judgments_includes.py
    commit: 6867be3c
    sha256: 23f48b2f1597991893dafb9928b09194d2c8ea48b2c2578f6fb71598e1f71349
  - path: tests/test_mc1_guards.py
    commit: 40d3265b
    sha256: f718bc402971e2b0dec74f5a6ff21571c257f619c1e46e8e4dbd7cc2b9240ab6
  - path: tests/fixtures/ir1/include-free-judgments-report.json
    commit: 6867be3c
    sha256: 7916a76d3e35d0a7b0a4d984779d499d99264251c0496392bc258caeb3495452
  - path: .gnd-planning/milestones/include-root-routes/notes/phase-IR1-spec.md
    commit: 6867be3c
    sha256: 46d95d24f12159e124c94959e13241ed5509536c2ce3b47569a8b095520bdb19
  - path: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.md
    sha256: ff966880b6ea8c50e3515367d9f5188f21fe270907286c6ae2ede58b522ba34b
  - path: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/FINDINGS.md
    sha256: c40b02449cb044ececcb75ad6c2e0408ad43768f46e2c3bd03cca4561a636aeb
---

# Claim

`gnd judgments check` judges a version-5 include root: the IR1 focused lane
exited 0 (669 passed), covering IR1-C1 to IR1-C9 over the interop fixture,
and the guard block exited 0 (712 passed).

## Gate output (verbatim)

Focused lane, summary line and exit:

    669 passed in 109.43s (0:01:49)
    exit=0

Structure and inventory guard block, plus `tests/test_release_text.py`
because the release notes changed:

    712 passed, 2 deselected in 96.37s (0:01:36)
    exit=0

Lint over the code this phase can touch:

    All checks passed!
    exit=0

Whole-repository lint (`project.md` names it the lint gate):

    [*] 10 fixable with the `--fix` option (154 hidden fixes can be enabled with the `--unsafe-fixes` option).
    exit=1

**Known red, not caused by this phase.** Every whole-repository ruff
finding is in a dev-tools-delivered skill script under `.claude/skills/` and
`.codex/skills/` (`process-phase/scripts/review_tool.py`,
`components/scripts/rules_check.py`, `dev-handoff/scripts/handoff.py`),
which the dev-tools sync `541e3e33` (PR 219) added. The same command exits 1
on `185ccaca` (that tree's `src/` equals the phase base `1e419a88`). This
phase changes no file under `.claude/` or `.codex/`, and the repository does
not edit those files (`project.md`).

Corpus, committed red before code (`40d3265b`, then T13 in `1e419a88`): 17
cases failed and the T6 negative control passed on the unchanged code;
all pass now.

## What the cases establish

| Criterion | Case | Result |
|---|---|---|
| IR1-C1 temporal root judges | T1 | exit 0, `error` null, `admission` true |
| IR1-C2 direct equals flat | T2 | equal `admission`, `repair`, `review_required`, `targets` |
| IR1-C3 integrity | T3, T4 | `include:hash-mismatch`; "stale judgment subject" |
| IR1-C4 nested | T5 | `include:forbidden-section` |
| IR1-C5 schema-valid refusals | T6 (five codes) and its negative control | valid; 0.4.0's shape invalid |
| IR1-C6 pins | T7, T10 (`test_R5_judgments_api` rewritten), `test_R4_judgments`, `test_R10_session_judgments` | green |
| IR1-C7 include-free bytes | T11 golden from `1e419a88`, with its negative control | byte-identical |
| IR1-C8 `--reference-root` | T12 | exit 0 |
| IR1-C9 orphan attachments | T13 | `include:declaration` |
| order (rule 3) | T8 | `reason` `shape` |
| time bound (rule 2) | T9, corrected (spec i1) | two compositions at 1,000 types under 5 s |

## Review

One reviewer is one reviewer: Codex, read-only, through the review helper
(`notes/reviews/phase-IR1-r1/`, brief sha256 `40614115…3eca`), over the diff
from `1e419a88` to the working tree before the F1 fix. Verdict
`CHANGES_REQUESTED`, one finding. F1 (IR1-C7 rested on observation-level
suites) was reproduced and fixed in `6867be3c` by the T11 golden. The fix's
bytes were not re-reviewed. The reviewer confirmed every brief claim by
probe and measured the composition layer at 0.283 s; under its sandbox it
ran no test suite. `review.md` was sanitized of local paths and says so.

## Boundary -- what this result did NOT establish

- The green lane covers the listed cases over the interop fixture and the
  small `write_case` model. It says nothing about include roots of other
  shapes beyond what `compose`'s own tests cover.
- It establishes nothing about `gnd check`'s speed: the checker is
  superlinear in the number of object types (spec i1: 266 s at 1,000 extra
  types), with or without includes. A judgments run pays it twice.
- `gnd exp` session judgments still refuse include roots, and the
  assertion-admission example (`src/gnd/examples/literature/assertion_admission.py`)
  copies the model alone and so now refuses an include root with
  `include:unreadable`.
- The F1 fix carries no review opinion.
- No merge, publication or issue reply is authorized by this record.

## Open questions

- **Checker scaling (spec i1).** `universe._denoting_types` →
  `resolve_reference_value_type` → `model_queries._supertype_parents` runs a
  supertype walk per object type inside per-role loops. Carried to the
  milestone close for a separate issue; it is not this milestone's work.
- **Whole-repository lint red** in dev-tools-delivered scripts. Carried to
  the close; its owner is the dev-tools source (or a `pyproject.toml`
  exclusion, which is a repository policy change).

## Refactoring review

Refactors EXECUTED: one. `bytes_declare_includes` (`model/_includes.py`)
now holds the parse-tolerant "do these bytes declare includes?" test that
was inside `guard_bytes`; `guard_bytes` calls it, and so do
`api.judgments` and `evaluate_judgments` (spec i2). Behaviour-preserving
for `guard_bytes`: every guard pin in `tests/test_mc1_guards.py` and
`tests/test_mc1_review_regressions.py` stays green in the focused lane.

Seen and not done: `evaluate_judgments` composes the root a second time for
its raw-subject check. That repeats an existing design (it re-reads
`model_bytes` for any model) rather than a new one, and costs 0.14 s at
1,000 types; no row is owed.
