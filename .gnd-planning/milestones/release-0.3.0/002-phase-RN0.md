---
milestone: release-0.3.0
station: "phase RN0"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RN0
date: 2026-11-11
source_base: 2490dd77
gates:
  - command: "ruling: owner approved .gnd-planning/milestones/release-0.3.0/notes/phase-RN0-spec.md sha256 d3a83b559bceec3f7b00bbf7f5c7b8534204cd99954e73ab0859fecb7f37436a (r1 at 99fbdbcd), D1 to D6 as recommended"
    exit: "n/a -- ruling"
  - command: "uv run pytest -q tests/test_conformance_payload.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_ossie_consumer.py tests/test_ossie_export.py tests/test_ossie_external_oracle.py tests/test_ossie_formulas.py tests/test_ossie_import.py tests/test_pyrel_rules.py tests/test_rf1_cli_pins.py tests/test_rf1_layering.py --tb=short -p no:cacheprovider (at 326a1900)"
    exit: 0
    output: "942 passed, 89 deselected in 88.47s (0:01:28)"
  - command: "the ten guard files of the spec's verification command, at the base 2490dd77"
    exit: 1
    output: "24 failed, 559 passed, 1 deselected in 74.38s (0:01:14)"
  - command: "uv run pytest -q tests/test_ossie_export.py -k rn0_k1 (the K1 regression test, against 2a9bd6b8, before the fix)"
    exit: 1
    output: "1 failed, 80 deselected in 0.27s"
  - command: "uv run python evidence/RN0/t4-digests.py OUT at 2490dd77 and at 326a1900; cmp of the two listings"
    exit: 0
    output: "316 rows each, listing sha256 d6558d003e7406933a0c1efb4e54ee687d92a7bae3d31d92189d41d648a218fa both times"
  - command: "e1-shards.sh rn0final on beast-3: the default lane, six round-robin shards, at 326a19001e3494944c965993c4362bd1d4152f3c"
    exit: "1 (the 2 known tests/test_public_optional.py errors and the two tests RN1 owns)"
    output: "18996 passed, 2 failed, 2 errors"
  - command: "uv run ruff check src/gnd/disclosure.py src/gnd/export/ossie.py src/gnd/export/ossie_formulas.py src/gnd/ossie_import.py tests/test_ossie_export.py"
    exit: 0
    output: "All checks passed!"
  - command: "uv run --group docs zensical build --strict; uv run python tools/check_docs.py site"
    exit: 0
    output: "No issues found; 16452 local links/assets/anchors checked"
  - command: "python3 scripts/components_index.py changed --base 2490dd77 --strict (at 7329b85d)"
    exit: 0
    output: "37 file(s) differ; 0 to fix, 0 warning(s), 3 to reread"
  - command: "codex exec --ephemeral --config model_reasoning_effort=\"xhigh\" --sandbox read-only --color never --skip-git-repo-check - (diff review over 2490dd77..2a9bd6b8, prompt on stdin)"
    exit: 0
    output: "DISPOSITION: revise; K1, K2, both reproduced and fixed"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request"
  reason: "excluded for this milestone by the owner (RN-D11, 2026-11-10)"
evidence:
  - path: .gnd-planning/milestones/release-0.3.0/notes/phase-RN0-spec.md
    sha256: 8bef2c2e748eaeeadb95be185a05a84c19375cabcd9a32922630ad53ce21aba0
  - path: .gnd-planning/milestones/release-0.3.0/notes/phase-RN0-codex-review.md
    sha256: c954b590db750c1ce9567ab13c3f207c3c9687779a28caaefe805e43be93ee74
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN0/source-successors.json
    sha256: 7900aedafde385995c14cd34349ded3b0aef3fef44750dcca81b78b2b439b110
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN0/query-successor.json
    sha256: dcd97f4b5b89d8a21fd485523dc5d1afca6f07b778956da6183ad4b51cda82b8
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN0/dynamic-query-successor.json
    sha256: b7cd2f9c7e6f048b7b4e1bed5ea13d8ff19f4c4aba8d5bec89c6d2fa74730d75
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN0/lane-326a1900.txt
    sha256: 816b626498d328dad890b35b9976089b3e0387ac228e8534e3365d07bb689721
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN0/lane-2a9bd6b8.txt
    sha256: 74410ec47989588dff4e23ee4b1192934e05f7468eae0f1fe2be54ecdda4c8d4
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN0/t4-digests-2490dd77.txt
    sha256: d6558d003e7406933a0c1efb4e54ee687d92a7bae3d31d92189d41d648a218fa
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN0/t4-digests.py
    sha256: 5abfab81f5e9ac8d6a0ab3fd7796496cec192cbd6cd20bfa0cc4521a383975e3
  - path: .gnd-planning/milestones/release-0.3.0/evidence/e1/failed-base.txt
    sha256: c9b2da3546eb6d1decd7fb37a144048118a40c7cfadb3754a06d57e3813c78ad
  - path: src/gnd/disclosure.py
    sha256: 1f59f866a4de396080caf76a33b09418cbdbac36348bbee2fb651b7b08dc2a89
  - path: src/gnd/export/ossie.py
    sha256: a4b13d8de683192d78718cd51da64eb5e789e0ec587bd5cfff89cd5a782b08a7
  - path: src/gnd/export/ossie_formulas.py
    sha256: f06a191c3d22a1b68a8f7e3bdc7a298e33699f6012421e5116958269fb2b37d9
  - path: src/gnd/ossie_import.py
    sha256: a07d14c50d097d4265943be597e652a9f7570e4efce0d891ab1e01f6612a08e2
  - path: tools/gnd_entrypoints.json
    sha256: 6a07011f89ad7172c1c4dc1caf77effe0e13483951f49b8212f482e5b465f561
  - path: docs/reference/disclosure.md
    sha256: 6543695a258265cf1c42cdebcebfc2f56d4702fc0d6309d570134cd7e7edf007
---

# Claim

At `326a1900` the 24 structure and inventory guards that were red on main
`2490dd77` exit 0, the Ossie test selection passes with the count it had
before (352, plus one new regression test), and the six-shard default lane
lists only the 2 known `tests/test_public_optional.py` errors and the two
tests RN1 owns (plan N20, N26). A 316-row listing of Ossie export and import
digests over the census is byte-identical before and after the source edits.

Nothing is bumped, built or published. The phase is on the topic branch
`claude/gnd-version-ossie-release-cec607` (PR 162), not on main.

## What shipped

Source (4 files, 50 insertions, 34 deletions):

- `src/gnd/export/ossie.py`, `src/gnd/export/ossie_formulas.py`: fact types,
  role names and role object types come from `ModelIndex`; the packaged schema
  loads through `gnd.input_policy.loads`.
- `src/gnd/ossie_import.py`: one accessor, `_relationship_roles`, reads a
  foreign relationship's roles; the three packaged schemas load through the
  shared reader.
- `src/gnd/disclosure.py`: `gnd export ossie` and `gnd import ossie` get rows
  in the disclosure table, kind `every-mode`. They had none.

Pins and policy:

- five command-body successors (`evidence/RN0/source-successors.json`) for
  bodies that UG2, UG3 and MC3 changed;
- the exact query successor (one row added; both budgets now full, 365 of 365
  and 310 of 310) and the dynamic-query successor (133 rows added, 1 removed);
- six entry-point exception rows in `tools/gnd_entrypoints.json` (D1);
- the packaging-guard entry for `gnd/ossie-loss-report.schema.json`;
- the skill-link edge, two count literals, two identity-site sets (D3).

Docs: `docs/reference/disclosure.md` lists both commands. Two generated
component-index pages are regenerated.

New test: `tests/test_ossie_export.py::test_rn0_k1_ossie_surfaces_are_every_mode_because_exports_carry_model_literals`.

## Gate output (verbatim)

Ruling, owner, 2026-11-10, in this session, answering "Approve the RN0 spec
with decisions D1 to D6 as recommended?":

    Approve as recommended

The lane at `326a1900`, from [lane-326a1900.txt](evidence/RN0/lane-326a1900.txt):

    rn0final shard0: 3682 passed, 53 deselected in 468.91s (0:07:48) (shard exit=0)
    rn0final shard1: 1 failed, 2921 passed, 152 deselected in 422.85s (0:07:02) (shard exit=1)
    rn0final shard2: 2833 passed, 130 deselected in 330.30s (0:05:30) (shard exit=0)
    rn0final shard3: 1 failed, 4082 passed, 88 deselected in 824.19s (0:13:44) (shard exit=1)
    rn0final shard4: 2652 passed, 282 deselected in 258.95s (0:04:18) (shard exit=0)
    rn0final shard5: 2826 passed, 145 deselected, 1 warning, 2 errors in 589.16s (0:09:49) (shard exit=1)
    ERROR tests/test_public_optional.py::test_base_wheel_refuses_missing_synth_extra_and_still_checks
    ERROR tests/test_public_optional.py::test_declared_synth_extra_is_seeded_and_loader_valid
    FAILED tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap
    FAILED tests/test_plan_app_docs.py::test_plain_short_prose_without_exit_codes[grow-a-model.md]

The base lane (E1, `2490dd77`): 18,971 passed, 26 failed, 2 errors
([failed-base.txt](evidence/e1/failed-base.txt)). An earlier lane at
`2a9bd6b8` is retained too ([lane-2a9bd6b8.txt](evidence/RN0/lane-2a9bd6b8.txt));
it found the docs failure described below.

Lint over the whole repository reports 182 findings on the base tree and on
this one alike; the gate above is the changed source and test files.

## Adversarial review

One reviewer is one reviewer: Codex (gpt-6.1-sol, xhigh, read-only) over
`2490dd77..2a9bd6b8`, disposition `revise`, 2 findings
([retained output](notes/phase-RN0-codex-review.md)). Both were reproduced
before they were accepted.

- **K1 (blocking, fixed in `0b4c78b8`).** This phase first classed the two
  Ossie commands `value-free`. They are not: an export writes constraint
  literals and description text in every disclosure mode, and a default
  export of a model with populations succeeds. Both rows are now
  `every-mode`. The regression test failed against `2a9bd6b8` before the fix.
- **K2 (hardening, fixed in `0b4c78b8`).** A successor file's reason
  miscounted the reads; the counts were right.

The reviewer confirmed: all three successor files authenticate their
predecessors; the five body digests chain; both budgets are unchanged and
full; the guards' mutation controls still refuse their violations; the three
schemas decode identically through both readers; 164 old and new exports
matched, 28 refusals among them; malformed role lists are rejected before the
rewritten code. It could not run the full lane, an installed wheel or the
external Ossie oracle. The fixes after it were not re-reviewed.

Own coverage audit against the spec's branch table: every re-recorded pin has
a guard that fails when the pin is wrong. Two count literals
(`tests/test_disclosure_mode.py`, `tests/test_rf5_commands.py`) are covered
only by the set assertions beside them.

## Refactoring review

Refactors executed, each behavior-preserving behind the gates above: the
exporter's nine direct document reads replaced by `ModelIndex` reads; the
importer's five foreign-document reads consolidated into one accessor.

Seen and deferred, each with a row below: both query budgets have no room
left; the structure guards are in no milestone's focused gate, which is how 26
failures reached main.

## Boundary -- what this phase does NOT establish

- The digest comparison shows equal bytes on the census models and two
  examples, not on every model. The reviewer found no counterexample and
  could not prove equivalence.
- **The opt-in `ossie_oracle` lane did not run (D5).** It reads its pinned
  checkout from `GND_OSSIE_ORACLE_ROOT`, which is not set in this session. The
  pinned upstream validator has not seen the changed exporter.
- The lane ran once, on one machine (beast-3, macOS 27.0.1, uv 0.13.7), at
  `326a1900`. Commit `7329b85d` after it changes one generated index page and
  planning files.
- One reviewer is one reviewer, and its fixes were not re-reviewed.
- The disclosure rows state what the commands do today. They are this
  phase's reading, corrected once by review, and not an owner ruling.
- No installed wheel was built; the three files under `src/gnd/schema/ossie/`
  still have no packaging check (RN2's probe).
- N20 and N26 are still red; RN1 owns them.

## Open questions

- **D5, for the owner:** where the pinned Ossie oracle checkout is, or a
  ruling that the lane is not rerun for 0.3.0.
- **Redaction and Ossie export, for the owner.** A fact type's `redact: true`
  does not stop its constraint literals or descriptions from being exported,
  in customer mode as in any other (review K1). The reference page now says
  so. Whether export should refuse, omit or keep them is a product decision;
  it is not in RN1 to RN3 as planned.
- **Query budgets are full** (365 of 365, 310 of 310). The next direct read
  of `fact_types` or `roles` outside the model layer fails the guard. Target:
  the owner, as a ruling on the ceilings or a refactor, before the next
  feature milestone.
- **Structure guards and focused gates.** Model composition and Ossie
  interchange each closed with green focused gates while these guards were
  red. Target: `project.md`'s gate rules (the owner's file), or a required
  check.
- **RN1 is unblocked once this branch is on main.** Its spec still owes the
  moved digests, now taken on the RN0 tree.

## Refuted premises

- The spec read the disclosure failures as a stale count. The table lacked
  both rows.
- This phase's first classification of those rows (`value-free`, argued from
  a population refusal that holds only under `--strict`) was wrong; the
  review refuted it.
- The spec's focused gate was not the phase's impact closure: it omitted
  `tests/test_disclosure_docs.py`, which the lane then failed.
