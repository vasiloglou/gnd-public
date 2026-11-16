---
milestone: literature-depth
station: phase-LD1
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-LD1
date: 2026-11-16
gates:
  - command: "uv run --no-sync pytest -q tests/test_ld1_competency_examples.py tests/test_lx1_flattening.py tests/test_li4_assertions.py tests/test_lx4_literature_interop.py --tb=short"
    exit: 0
    output: "110 passed in 40.57s"
  - command: "uv run --no-sync pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 103.50s (0:01:43)"
  - command: "uv run --no-sync ruff check src/gnd/examples/literature/depth.py tests/test_ld1_competency_examples.py"
    exit: 0
    output: "All checks passed!"
  - command: "ruff check --output-format=json"
    exit: 1
    output: "188 exact inherited Ruff diagnostics; matched the pre-phase checkout"
  - command: "python3 scripts/components_index.py changed --base 15276393 --strict"
    exit: 0
    output: "0 to fix, 0 warning(s), 0 to reread"
  - command: "uv build --offline --wheel --out-dir <scratch>/dist"
    exit: 0
    output: "wheel installed into a fresh environment with the locked dependencies"
  - command: "<wheel-venv>/bin/python -m gnd.examples.literature.depth --out <fresh-dir>"
    exit: 0
    output: "two runs exited 0 and report.json matched byte for byte"
  - command: "claude -p --model opus --permission-mode plan --add-dir <review-dir> -- '<brief-path prompt>'"
    exit: 0
    output: "VERDICT: CHANGES_REQUESTED"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: explicitly scoped owner or CI selection
  reason: the focused, structural and installed-wheel gates cover the affected public evidence
evidence:
  - path: .gnd-planning/milestones/literature-depth/003-phase-LD1-spec-gate.md
    sha256: 6eadcc889201d1fbb682eae202a43d5a61aa9481d12bae60c9c2f1ba00be574e
  - path: .gnd-planning/milestones/literature-depth/notes/phase-LD1-spec.md
    sha256: 96dcbfc91632d226c9f86897699e496155d9831b1ac7af9f1f7c8d20b469dee0
  - path: .gnd-planning/milestones/literature-depth/evidence/LD1/installed-observation.json
    sha256: 2afca6c12174c340f23fcd8c139bcb286a803e92e57f3cfb6671f6f15ce4b08c
  - path: .gnd-planning/milestones/literature-depth/evidence/LD1/review-scope.json
    sha256: 3bfd10e86fce5b7b1477220e022fbee2b066ac7ae4bc62d258ccf157562bf768
  - path: src/gnd/examples/literature/depth.py
    sha256: 160adee1b92da7cff144eee7639c794ce1e1c910513a323072e790dac6a6ff12
  - path: tests/test_ld1_competency_examples.py
    sha256: e659b71609b930fe1344ab41c03877fdf17ad305399aaf0d6e966728d0cb4547
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD1-r1/BRIEF.md
    sha256: 5b0a2f4da1f56c618c622eeff47429c60543a998db6c4165d434363cc4a63492
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD1-r1/FINDINGS.md
    sha256: a784db054dee0ec6988c4f8b0cf023a3d04e5e8547b6c8b9f72d44c567b6846e
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD1-r1/brief.json
    sha256: ae1c995604ed50ba8d633bc1e0f82317886652c79d8e1579764656f62063380d
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD1-r1/diff.patch
    sha256: 2835d3e4aa0d22a9107ef6d8ceefa86d9cc0f0845b051cdbe0a8149d621b8b84
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD1-r1/review.md
    sha256: 181fd428dc5f5ff1351726556447800996ddd2aaf9cd03bf7787fe01eddbbaa9
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD1-r1/review.log
    sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD1-r1/run.json
    sha256: 6e455f9c9abe721da8438243b39c5bbd3438563c10dfc2436315371d4f170f01
---

# LD1 completion

The packaged example checks three rooted models. It returns four
competency answers per case, with nine supported and three scoped
unknowns. The experiment comparison control distinguishes
known incompatible contexts and missing inputs. One label per
subject is enforced by the checker. The reported equation carries
its provenance and claim kind. The independent support roster and
question locator pin block a substituted citation.

## Verified observations

| Criterion | Evidence |
|---|---|
| Question readiness and source support | Three extracts, three verify passes and three check passes. The reviewed primary location, note span and facts are bound independently. Mutations refuse stale or substituted bindings. |
| Qualified results and stable identity | Each missing complexity qualification yields its own unknown. A label change preserves a checked subject occurrence. Changing a component predicate removes the corresponding answer. A contradictory duplicate label fails the public checker. |
| Experiment context | Nine synthetic pairs exercise matching context, five mismatching fields, missing context, missing score, and precedence when both are present. |
| Packaged execution | Two installed runs exited 0 and returned the same report bytes. The [installed observation](evidence/LD1/installed-observation.json) binds the wheel, report and individual case handoffs. |

## Conditional scope for LD2

| Axis | Reproduced observation | Disposition |
|---|---|---|
| Dimension-aware time-step anchors | Integer recognition selects `2 fs` and `2 eV` for magnitude 2. Decimal recognition finds the numeral in the equivalent `0.002 ps` but does not produce canonical time-step evidence. | Open validation of the equivalent time units and rejection of the energy span. |
| Percent versus percentage points | A change from 40% to 45% is five points or a relative 12.5%. Percent recognition sees 40, 45 and 12.5. The point wording is excluded and an injected misrecognition changes the disposition. | Existing route covers the scoped representation. Carry its regression forward. |
| Exact decimal witnesses | A bound fractional `Number` value passes check at 0.002 and witness exits 2 with `fragment-unsupported`. An integral `Number` control proves and replays. The report follows a changed checked value. | Open exact representation and replay for the scoped quantity, with native Float and fractional Number refusals explicitly covered. |

## Independent review

The owner authorized one Claude Code Opus review of `da41bc07`.
The reviewer verified 26 digest entries and ran 20 selected tests. It
confirmed source-span and fact binding, rooted routes, expected unknowns,
ordering of comparison outcomes, label uniqueness and admission refusals.
It did not independently check the selected primary sources, wheel,
whole-tree lint, component catalog or predecessor test selection.
The phase author checked the cited sources and the local verification ran
the remaining selected gates.

The seven findings and dispositions are retained in the
[review ledger](notes/reviews/phase-LD1-r1/FINDINGS.md).
The local verification above establishes the repairs at `11493f45`.
The [review scope](evidence/LD1/review-scope.json) distinguishes the
17 entries with the original bytes and the nine amended entries.

## Refactoring review

Refactors EXECUTED. One strict JSON and bounded-process route serves
all cases. The follow-up shares fact-shape validation across science
and synthetic score inputs and isolates separate quantity measurements.

## Boundary

One reviewer is one reviewer. The reviewed diff binds the original candidate.
The example uses locally authored descriptions and saved responses; its
coverage is the declared small fixture. The model checks structure, while
source-grounded meaning remains a scoped support decision. Part 10 remains
deferred.

## Open questions

- LD2 owns the two opened quantity axes and their installed-route controls.
- The existing phase-review helper's explicit Claude prompt separator
  remains with the dev-tools maintainer for the next helper sync.
