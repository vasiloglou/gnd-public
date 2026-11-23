---
milestone: reviewed-vocabulary-growth
station: "phase-VG2"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-VG2
date: 2026-11-23
gates:
  - command: "uv run pytest -q tests/test_vg2_evolve_sources.py tests/test_evolve_additive_policy.py tests/test_evolve_loading.py tests/test_unattended_growth_guidance.py tests/test_unattended_mode.py tests/test_induced_provenance.py --tb=short"
    exit: 0
    output: "435 passed in 28.68s"
    note: "the plan's section 9 VG2 lane with the new file, at 53280cba"
  - command: "uv run pytest -q tests/test_evolve_*.py tests/test_unattended_*.py --tb=line -p no:cacheprovider"
    exit: 0
    output: "458 passed in 39.64s"
    note: "the maintenance page's lane (issue 218, 'Done when')"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=line"
    exit: 0
    output: "679 passed, 2 deselected in 99.06s (0:01:39)"
  - command: "uv run ruff check src tests tools"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base 11ca75b0 --strict"
    exit: 0
    output: "changed against 11ca75b0 (11ca75b): 17 file(s) differ; 0 to fix, 0 warning(s), 3 to reread"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request, or the milestone-close default lane"
  reason: "one branch of _enforce_d12 and one exit marker change; IK2's whole D-12 table and every evolve and unattended test file ran"
evidence:
  - path: src/gnd/evolve/service.py
    sha256: 404cd6b224937484106d394660de188d0eb4ad60ffd83e50d2fcf9a8d5520f5e
  - path: src/gnd/evolve/cli_service.py
    sha256: 23817312f952cd9b954dc4be81e8cbbf5a902561cd1a1b69dca958a057dcfd91
  - path: src/gnd/skills/gnd-orm-core/references/provenance-and-modality.md
    sha256: e3eb7ecae2c404f7b123389a115d889f0486d448db666760b7c93260fe7108df
  - path: src/gnd/skills/gnd-model-evolve/references/evolution-contract.md
    sha256: fc234d62acc1cd49015baa2afe9ac800e9467496a48e8a51327e18cbf68fc8eb
  - path: tests/test_vg2_evolve_sources.py
    sha256: 098830b756d1d0dab80538a8d11444f4526682abfef6249e85afd8c0f4134a80
  - path: tests/test_induced_provenance.py
    sha256: 8e7b07e51614235f58c17ced3bb4fa85d2bab678326cde8c63d7ad543096b8f3
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/VG2/source-successors.json
    sha256: 83c3ed95027f04ed6097e548dfa6d951f5467f0a0286d35bd410a2e01274800f
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/phase-VG2-spec.md
    sha256: 52e1cf7478af369331d4dee19468dc4ff3300f5420c7ef4de82e403c374457a7
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG2-r1/review.md
    sha256: 7c14f1ce3617dcaa1af7547b91e76329e860fb85a70ff80accb3c922bcce687d
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG2-r1/FINDINGS.md
    sha256: 9be7e361e7d29941242336d2bb96324146ac2128f1b9cef3074744b0175b63fc
---

# Claim

At `53280cba`, the VG2 lane exited 0 (435 passed), every
`tests/test_evolve_*.py` and `tests/test_unattended_*.py` exited 0 (458
passed), the guard block exited 0 (679 passed), `uv run ruff check src tests
tools` exited 0 and the component-index check exited 0. A proposal written as
`unattended-growth.md` describes, with a `sample` and a `common-sense`
constraint, `proposed` and `deontic`, previews and applies on an unattended
model, exit 0, and the result validates with every document.

## What shipped

- `src/gnd/evolve/service.py`, `_enforce_d12`: a new or changed `sample` or
  `common-sense` constraint is admitted when `proposed` and `deontic`, and
  refused otherwise with "new sample and common-sense constraints must be
  proposed/deontic (D-12)" (plan D2 (a), VG2-D2: the catch-all keeps its
  text).
- `src/gnd/evolve/cli_service.py`, `_evolve_service_exit`: that refusal
  exits 3 (review r1, F1); registered as an RF5 successor in
  `evidence/VG2/source-successors.json`, listed by
  `tests/support/rf9_ci_sources.py`.
- `provenance-and-modality.md`, "Evolve admission (D-12)": two rules and the
  refusal's row. `evolution-contract.md`: the `:279-280` sentence and §6
  name the two sources. `unattended-growth.md` is unchanged; it already
  said this. `docs/release-notes.md`: one entry.
- Tests: `tests/test_vg2_evolve_sources.py` (T1–T4 and the review
  regressions); `tests/test_induced_provenance.py` T5 applies an explicit
  eight-row delta to IK2's table captured at `328061ee`, which stays as
  recorded (VG2-D3).
- `dev/components/`: regenerated. `evolve.service` and `subsystem.evolve`
  were re-read beside the diff and are still accurate: neither describes
  D-12's sources.

Measured size: 341 lines added and 3 removed under `src` and `tests`
(`git diff --stat 11ca75b0 53280cba`); source 10 of them, against an estimate
of 6.

## Gate output (verbatim)

    $ uv run pytest -q tests/test_vg2_evolve_sources.py tests/test_evolve_additive_policy.py tests/test_evolve_loading.py tests/test_unattended_growth_guidance.py tests/test_unattended_mode.py tests/test_induced_provenance.py --tb=short
    435 passed in 28.68s
    $ uv run pytest -q tests/test_evolve_*.py tests/test_unattended_*.py --tb=line -p no:cacheprovider
    458 passed in 39.64s
    $ uv run pytest -q <the project.md guard block> --tb=line
    679 passed, 2 deselected in 99.06s (0:01:39)
    $ uv run ruff check src tests tools
    All checks passed!
    $ python3 scripts/components_index.py changed --base 11ca75b0 --strict
    changed against 11ca75b0 (11ca75b): 17 file(s) differ; 0 to fix, 0 warning(s), 3 to reread

## The criteria

| Criterion | Test | Result |
|---|---|---|
| VG2-C1 | T1: on the unattended acceptance workspace, a fourth round in the reply shape adds a fact type with sample rows, a `rows` uniqueness and a `library` mandatory constraint; `--policy additive` | preview exit 0, no policy issue; apply exit 0; `gnd validate --require-documents` with every document exit 0 |
| VG2-C2 | T2 and R1-F1: each source with `confirmed`/`deontic`, `proposed`/`alethic` and `confirmed`/`alethic`, on a model without the mode | exit 3 with the named refusal, in process and at the command line; controls admitted; an induction block still refused first |
| VG2-C3 | T3: the D-12 home, the contract's §6 and the growth page's evidence section, read outside fenced blocks; the admitted sources computed from `_enforce_d12` | the same combinations |
| VG2-C4 | T1 on the unattended model; T4: without its span the `rows` constraint is refused by U5, and an `alethic` library constraint by U8 | as stated |
| IK2 T5 | the captured table with the eight-row delta | every other row unchanged |

## Review

One reviewer is one reviewer: Codex (default model, effort high, read-only)
through the review helper, round `notes/reviews/phase-VG2-r1/`, over the
diff from `11ca75b0` to the working tree at `b2ce8bb0`. Verdict
`CHANGES_REQUESTED`, four findings, all reproduced (`FINDINGS.md`):

- F1, blocking, fixed at `53280cba`: the refusal exited 70 at the command
  line.
- F2, rejected as a defect: a changed `sample` or `common-sense` constraint
  is judged as a new one. That is D-12's rule; the brief's claim that
  changed constraints were judged as before was wrong (refuted premises).
- F3, rejected as a defect: on an unattended model U2 or U8 refuses first,
  because candidate validation precedes D-12; the exit is 3 either way.
  The brief's "on any model" overclaimed (refuted premises).
- F4, hardening, fixed at `53280cba`: T3 read a heading inside a fenced
  example.

The reviewer checked and found true: 51 read-only tests including IK2's
table and the induced admission controls; guide-shaped proposals with
`source-document` adds preview with both sources; 30 spans re-hashed with
none unchecked; the three documents agree; ruff. It did not run apply,
finalize or any lane that writes files. `review.md` and `review.log` were
sanitized by the helper, which says so at the top of each.

## Refactoring review

None needed, argued from what the phase touched: one branch beside the
`llm-inferred` branch of `_enforce_d12`, and one marker in the exit
classifier's message table. The classifier still maps refusals by message
text ("a compatibility adapter", its docstring). Typed refusals would retire
that table; that is older than VG2 and not this phase's to change.

## Boundary -- what this phase does NOT establish

- One reviewer is one reviewer. The fix commit `53280cba` carries no review
  opinion; the round read `b2ce8bb0`.
- On an unattended model the named D-12 refusal is not what a host sees for
  a `confirmed` or `alethic` constraint: U2 or U8 refuses first, exit 3.
- D-12 admits a changed `sample` or `common-sense` constraint that stays
  `proposed`/`deontic`, as it admits a changed `llm-inferred` one.
- The additive policy still judges what D-12 admits; VG2 changes no policy
  cell.
- The issue 218 reply is drafted in VG5, not here.

## Open questions

- The exit classifier's message markers (`cli_service.py:240`): typed
  refusal classes would remove the next missed marker. Target: a
  maintenance pass, if the owner wants one.

## Refuted premises

- The review brief claimed "No D-12 answer other than the eight sample and
  common-sense rows changes; a changed constraint is judged as before". F2
  refuted the second half: D-12 has one rule for new and changed
  constraints. Corrected in the spec (finding 3) and here.
- The brief claimed VG2-C2's named refusal "on any model". F3 refuted it for
  unattended models. Corrected in the spec (finding 4) and here.
