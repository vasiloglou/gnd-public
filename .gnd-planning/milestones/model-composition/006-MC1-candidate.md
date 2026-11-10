---
milestone: model-composition
station: "MC1 candidate snapshot"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: MC1-candidate
date: 2026-11-09
gates:
  - command: "uv run pytest -q tests/test_mc1_model_includes.py tests/test_mc1_guards.py tests/test_mc1_review_regressions.py tests/test_schema_sync.py tests/test_model_validation.py tests/test_model_identity.py tests/test_model_v2.py tests/test_compiled_snapshot_obligations.py tests/test_reference_population_corpus.py tests/test_public_reference_budget.py tests/test_evolve_loading.py tests/test_rf8_structure.py tests/test_pyrel_export.py tests/test_rf6_packages.py tests/test_rf6_query_policy.py tests/test_rf8_sessions.py 'tests/test_rf5_commands.py::test_historical_cli_name_is_the_defining_object[_cmd_check_batch]' 'tests/test_rf5_commands.py::test_relocated_algorithm_and_qualification_are_unchanged[_cmd_check_batch]' --tb=short"
    exit: 0
    output: "1017 passed, 3 deselected in 274.53s (0:04:34)"
    note: "Executed with this checkout's .venv/bin/pytest and locked dependencies; uv 0.10.10 launcher is the canonical spelling. Default exclusions preserved."
  - command: "uv run ruff check src tests"
    exit: 1
    output: "Found 13 errors."
    note: "Exactly the baseline's 13 code/path/line/column findings, independently reproduced on beast-3 at 459ca8d2. Not a green lint gate."
  - command: "python3 scripts/components_index.py changed --base d2d6309b --strict"
    exit: 0
    note: "Generated views current; zero failures and warnings. Full output retained."
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census" tests/test_mc1_census.py --tb=short'
  trigger: "Explicit owner selection already received; pending candidate execution on beast-3"
  reason: "This is a candidate snapshot, not the phase-completion record."
evidence:
  - path: .gnd-planning/milestones/model-composition/evidence/MC1/candidate-source-manifest.json
    sha256: 9d2944a096ca097f48647bcb2e65504d2b2de031426762cf1f74684b222f7045
  - path: .gnd-planning/milestones/model-composition/evidence/MC1/focused-final.txt
    sha256: 355ee1590ac9ea93dcc0b1ed43205a86c4016cbd1955064fc9f8d59a374bb1cf
  - path: .gnd-planning/milestones/model-composition/evidence/MC1/baseline-full-default.txt
    sha256: 6b64751cbadcf06dd7f4a58fe23265857e5aa70a3619738dd10bf6c70c335184
  - path: .gnd-planning/milestones/model-composition/evidence/MC1/baseline-census.json
    sha256: 43e1692d7393190243ae551e1001d5a904341c77401fa0184f8c525a497274de
  - path: .gnd-planning/milestones/model-composition/notes/phase-MC1-codex-confirmation.md
    sha256: ab08d3e130ce1b558c94aaed6033ee429e4b515be7ceda8e4bfec033b5edb021
  - path: .gnd-planning/milestones/model-composition/evidence/MC1/baseline-lint.txt
    sha256: b9727009aeb40a84cecec650d646e431d272189e36ee2c95d7050d306253f668
  - path: .gnd-planning/milestones/model-composition/evidence/MC1/lint-current.txt
    sha256: d3caf02609e70845838288270ae80aa15abaaf91e5a13b98400c4fb32ac877b9
  - path: .gnd-planning/milestones/model-composition/evidence/MC1/components-current.txt
    sha256: 527825cda7c7857cb0f69f5568d79e277298efa95a84e210eb7e188ac477c25f
  - path: .gnd-planning/milestones/model-composition/evidence/MC1/scaling.txt
    sha256: a8503b2887949b2d1a70db56e5bc6b4a6ae97f6fb2479e5e25f0576c34b283c5
  - path: .gnd-planning/milestones/model-composition/evidence/MC1/red-review-regressions.txt
    sha256: 5aeb42f60e7238b0c776f385545e5fcc66f9f3ef9a977c496c3ad278e02e0266
  - path: .gnd-planning/milestones/model-composition/notes/phase-MC1-codex-review.md
    sha256: b27b6d700765cd0e67340769a3462968b714fa6156043157dd3fa16ce492ca5f
  - path: .gnd-planning/milestones/model-composition/notes/MC1-review-disposition.md
    sha256: 7f64fbc3ad44dc44f1a3ec2d6b821e40081827d74d99eb7d076e4be6dafdb092
---

# Claim

The MC1 candidate passes 1,017 focused checks and the bounded independent
repair confirmation approves it with no findings. Its full default-suite
comparison and marked census remain pending; MC1 is not complete.

## Gate output (verbatim)

Focused checks:

    1017 passed, 3 deselected in 274.53s (0:04:34)

Lint:

    Found 13 errors.

Frozen beast-3 default baseline, clean source at
459ca8d293eeef79110c8def26ae7b061d5a8fd5:

    6 failed, 18392 passed, 799 deselected, 1 warning in 2324.31s (0:38:44)
    exit 1

Frozen census:

    models=400 loaded=334 load_refused=66 loaded_identity_refused=1

Merge/index scaling (16k / 4k declarations): linear ratio
4.322745525305249, within 6; quadratic mutant ratio 15.180779585637014,
outside 6. Exact medians and the command result are in scaling.txt.

## Review and delegated snapshot ruling

The first independent Codex CLI review returned nine reproduced findings.
All 17 corrected regression cases were observed red pre-fix and green
post-fix, with three additional legacy controls green. The one bounded
confirmation returned approve, no findings. One reviewer is one reviewer;
its scope and limits remain in the retained outputs. The declared review
budget is exhausted; no further prose plan round is selected.

Delegated (auto=true), under the current owner authorization for the named
milestone: accept this candidate snapshot for the already selected beast-3
comparison. This is not a final phase/close acceptance. Retain the known
nonzero baseline and lint results; do not repair unrelated historical tests
or describe them as passed. MC1's size remains within the owner's 1100-source
and 1900-test stop (conservative gross production/schema additions: 818).

## Refactoring review

Refactors EXECUTED: acyclic path/parser/exception homes with identity and
metadata aliases; one wrapping serializer instead of duplicated empty-field
policy; one include-reason helper across legacy export adapters. Current
focused gates cover these moves and behaviors. No additional refactor is
needed for the bounded loader/guard surface examined in this candidate.

## Boundary

No full candidate gate, marked candidate census, MC1 completion, main-branch
merge, owner docs reaction, milestone close, issue closure, publication or
certification is established. The six default baseline failures and 13 lint
errors remain non-green. The 400-member comparison is a bounded compatibility
measurement, not proof of behavior over arbitrary programs.

## Open questions

- Run candidate full/default and marked census on beast-3; compare all six
  known-red identities and establish no added failure.
- Preserve the early owner docs checkpoint and its merge prerequisite.
- Close: repair the census membership and guard/intake-hash wording, with
  provenance from records 003/005 and the phase record.
