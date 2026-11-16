---
milestone: literature-interop
station: milestone-close
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: milestone-close
date: 2026-11-15
gates:
  - command: "uv run --no-sync pytest -q tests/test_lx1_flattening.py tests/test_lx2_witness_flattening.py tests/test_lx3_catalog_composition.py tests/test_lx4_literature_interop.py tests/test_composition.py tests/test_composition_example.py tests/test_mc1_guards.py tests/test_mc2_consumers.py tests/test_reference_population_corpus.py tests/test_witness_composition.py tests/test_li2_resolution.py tests/test_li5_lineage.py tests/test_public_replay_admission.py tests/test_fidelity_payload.py tests/test_public_fidelity_scope.py tests/test_schema_sync.py tests/test_li0_witness_wire.py --tb=short"
    exit: 0
    output: "693 passed, 3 deselected in 163.61s (0:02:43)"
  - command: "uv run --no-sync pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 107.31s (0:01:47)"
  - command: "uv run --no-sync pytest -q tests/test_lx1_flattening.py::test_relabelled_unattended_metadata_refuses_extraction --tb=short"
    exit: 0
    output: "1 passed"
  - command: "uv run --no-sync ruff check tests/test_lx1_flattening.py tests/test_lx4_literature_interop.py"
    exit: 0
    output: "All checks passed!"
  - command: "uv run --no-sync ruff check --output-format=json"
    exit: 1
    output: "188 inherited diagnostics, exact match"
  - command: "python3 scripts/components_index.py changed --base 183972ea --strict"
    exit: 0
    output: "0 to fix, 0 warning(s), 14 to reread"
  - command: "uv run --no-sync python tools/run_gnd_review_panel.py .gnd-planning/milestones/literature-interop/evidence/close-request.json --out ../panel-run --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
    output: "quorum-established; six valid responses; reviewed artifacts unchanged"
  - command: "uv run --no-sync gnd review finalize ../panel-run ../synthesis.json --out ../PANEL-REVIEW.md"
    exit: 0
    output: "5 agreed groups, 8 divergent concerns, 5 prioritized fixes"
  - command: "uv run --no-sync pytest -q -p no:cacheprovider tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap --tb=short"
    exit: 0
    output: "1 passed in 0.34s"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-interop/notes/literature-interop-plan.md sha256 dbfd3ecfd6c3b008ca67159b7e5ead2870f2855992dd5b0db48e8cf00d0aabfb"
    exit: "n/a -- ruling"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: explicitly scoped owner or CI selection
  reason: the affected contracts are covered by the focused gates and installed fixture
evidence:
  - path: .gnd-planning/milestones/literature-interop/003-plan-gate.md
    sha256: db8fc47587e79b86bc8693cff1479c023896f7ba0d558a6271c284236b2f377e
  - path: .gnd-planning/milestones/literature-interop/005-phase-LX1.md
    sha256: 42a68ecde3c670cf706abe932a35e61e7a34ef0c93ca3c430690ac5082c0bebb
  - path: .gnd-planning/milestones/literature-interop/007-phase-LX2.md
    sha256: 04881624cdf820ca16f54ecd7f37065792fbe48ce20c4c70041d21e3f946cf61
  - path: .gnd-planning/milestones/literature-interop/009-phase-LX3.md
    sha256: 78d13149683a5d74f61b94cd60468a5333fa3a7be91645abf0ba9235b87affc0
  - path: .gnd-planning/milestones/literature-interop/011-phase-LX4.md
    sha256: ea02cf9e9068c1302edc4f6eb42f77337a499b6ac56ede735f975d73fbad5ee1
  - path: .gnd-planning/milestones/literature-interop/012-close-candidate.md
    sha256: 93af88731d3a97184f3d6470600b04044a4161334b804c75f07dbdaedb92484b
  - path: .gnd-planning/milestones/literature-interop/013-panel.md
    sha256: 85f763dcbec262d4f5e676112633f11f2a92203e4666d19ecf6bdc7c4df9c6e6
  - path: .gnd-planning/milestones/literature-interop/notes/literature-interop-plan.md
    sha256: dbfd3ecfd6c3b008ca67159b7e5ead2870f2855992dd5b0db48e8cf00d0aabfb
  - path: .gnd-planning/milestones/literature-interop/notes/close-delta.md
    sha256: cc5de49c174eda35d70f0b74a8a63c3ec8761ce7d52fba995e8d67bef38cfc71
  - path: .gnd-planning/milestones/literature-interop/evidence/close-request.json
    sha256: 1328d2d54ac60dad331d62dd3fa0a762f2abb71871213539857248a4d2006662
  - path: .gnd-planning/milestones/literature-interop/evidence/close/dispositions.md
    sha256: b02aecd419fc8486e46fed0fb7001e3fbad29e3e5193571aadb82f01f70b9faa
  - path: .gnd-planning/milestones/literature-interop/evidence/close/phase-review-scope.json
    sha256: 4370970612b85926185e60baee5862c38c56c1d04bc8a222eadaa308acdb807d
  - path: .gnd-planning/milestones/literature-interop/evidence/close/verification-scope.json
    sha256: a20b19f50cf086012d684794efd58a45a6f9acd800edf864167f2b0d59ef54e6
  - path: .gnd-planning/milestones/literature-interop/evidence/LX4/installed-observation.json
    sha256: 5dd61435b73a58f558ed3613fbfbe1ed176671354d74e399e9b6c863142390a5
  - path: tests/test_lx1_flattening.py
    sha256: 6ca88c215e2bd4a65be9c9029b843aa6d2225206f24b72bdde6fd6c84bad0fce
  - path: tests/test_lx4_literature_interop.py
    sha256: be3d80cc1a2f74b19a78109dac42e5b21a5859dd3fa3a27836deea41d7766210
---

# Literature interoperability milestone close

The delegated ruling closes LX1 through LX4 for issue #193 part 5 and the
dates step of part 4 in draft PR #202.

## Ruling

ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-interop/notes/literature-interop-plan.md sha256 dbfd3ecfd6c3b008ca67159b7e5ead2870f2855992dd5b0db48e8cf00d0aabfb

The owner's `process-milestone literature-interop auto` invocation delegated
this decision. The owner separately authorized the standard close panel on
`14fdc81f`. The panel met the four-reviewer requirement. The ruling accepts
the verified implementation, the plan clarification and the added controls
documented in the [dispositions](evidence/close/dispositions.md).

## Exit evidence

| Phase | Verified outcome |
|---|---|
| [LX1](005-phase-LX1.md) | Extract against a flattened projection of two pinned includes, authenticate the bundle and re-derive the projection. Preserve the include-free controls. |
| [LX2](007-phase-LX2.md) | Produce and independently replay rooted version 3 witnesses, preserving model and fact provenance, and replay compatible legacy versions 1 and 2. |
| [LX3](009-phase-LX3.md) | Compose and check with fixed catalog facts, retain candidate and catalog origins through version 4 proof replay, and preserve reference-free bytes. |
| [LX4](011-phase-LX4.md) | Run the installed example from authenticated source extraction through rebind, composition, checking, witness, replay and both fidelity cases. Keep optional date advice separate from product-stage bytes. |

The verified installed wheel ran in both modes. Each produced three
checking passes. Of nine proposed date candidates, eight entered the
LI5 chainable advisory set. Two passed, one produced the PINN advisory
and five were unresolved. One fell outside the chainable set. The two
original extractions are shared between fidelity and composition. The
composition route adds two document copies and zero original population
or extraction sidecar copies. The [installed observation](evidence/LX4/installed-observation.json)
binds these counts and the matching outputs.

The [verification audit](evidence/close/verification-scope.json) binds the
tested runtime to the reviewed packet and the exact 188 inherited Ruff
diagnostics. The focused test run used the default marker selection, which
deselected the two historical B24 delivery cases and the phase 2 dirty
registration control. The structural run deselected the ROF4 generated
plan control and the scaffold manifest byte/mode census under the same
marker selection. The separately run unattended-metadata regression
passed. The reserved evidence and census cadence retains its existing
owner or CI trigger.

## Review and repairs

The independent [close panel](013-panel.md) returned six valid responses.
Claude, Qwen and Gemini requested revisions, and Codex, Kimi and GLM
approved. The adopted repairs add seven coordinated mutation cases at the
LX4 handoffs and an unattended-metadata test for LX1, clarify legacy wire
reading in plan §2, and link each refusal and evidence-scope claim to its
control. Plan §12 preserves the prior wording and binds the reviewed plan
at `14fdc81f`. The runtime source, dependency lock and tools match the
panel's source commit. The [dispositions](evidence/close/dispositions.md)
record the treatment of every concern and the narrower review scope of
the added tests and plan clarification.

The four independent phase reviews are scoped to their original candidate
commits. The [scope audit](evidence/close/phase-review-scope.json) lists each
verdict and the amended paths for each completion snapshot. The review
helper reported four finished rounds, zero ledger problems, 73 reviewed
entries and 21 updated entries. Local regressions establish the repaired
bytes. The [reviewed packet](012-close-candidate.md) and its
[delta](notes/close-delta.md) preserve what the close panel received.

## Open-questions sweep

| Raised in | Disposition |
|---|---|
| [001](001-panel.md), [002](002-panel.md), [003](003-plan-gate.md) and plan §7 | Closed. The phase specs and controls establish the wire fields, exact-byte compatibility, diagnostic order and unsupported routes. The [refusal matrix](evidence/close/dispositions.md) ties each row to a control. |
| [001](001-panel.md), [002](002-panel.md), [011](011-phase-LX4.md), LI1 and LI5 | Closed for the installed public fixture. The shared source layout accepts two document copies from the existing filename conventions, shares the extraction populations and sidecars, and retains distinct rebound evidence. The LX4 record and installed observation establish the dated rows, manifest, timing of the optional step and actual copy counts. |
| [005](005-phase-LX1.md), [007](007-phase-LX2.md), [009](009-phase-LX3.md) and [011](011-phase-LX4.md) | Carry the Claude prompt separator to the dev-tools maintainer for the next review-helper sync. The four phase reviews used the explicit separator. |
| LI1 and the [literature-identity close](../literature-identity/035-milestone-close.md) | Carry generic strict-reader symlink behavior to filesystem maintenance and broader serializer consolidation to the existing refactoring target. LX2 verified the specific explicit caller path. |
| [013](013-panel.md) | Closed for this ruling by the [dispositions](evidence/close/dispositions.md), regression tests and plan §§2 and 12. |

## Refactoring review

The four phase records inventory the executed refactors and retain their
verification. The review-helper, generic filesystem and broader
serialization follow-ups retain the owners and targets in the sweep above.
The panel repairs are confined to documentation, verification evidence and
regression tests.

## Boundary

The public example uses saved extractor responses. Reserved evidence,
certification and merge retain their own authorization. PR #202 is a draft.
