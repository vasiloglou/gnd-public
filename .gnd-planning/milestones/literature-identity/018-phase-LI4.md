---
milestone: literature-identity
station: phase-LI4
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-LI4
date: 2026-11-15
base_commit: e76c3c5988cb30262e9488d803f5790f2dc99d0f
gates:
  - command: "uv run pytest -q tests/test_li4_assertions.py tests/test_public_v71_full_judgments.py tests/test_public_v71_judgment_successor_guards.py tests/test_disclosure_mode.py --tb=short"
    exit: 0
    output: "538 passed in 256.85s (0:04:16)"
  - command: "uv run pytest -q tests/test_li4_assertions.py tests/test_public_v71_judgment_successor_guards.py --tb=short"
    exit: 0
    output: "30 passed in 35.50s"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 185.36s (0:03:05)"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base e76c3c59 --strict"
    exit: 0
    output: "changed against e76c3c59 (e76c3c5): 22 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request only"
  reason: "The contextual example uses focused judgment, disclosure and packaged structure controls."
evidence:
  - path: .gnd-planning/milestones/literature-identity/015-phase-LI4-spec-gate.md
    sha256: 670f08ac1fa62cdab84fee21641561b4a12aa0e67f286cef5f8f280bf344ff32
  - path: .gnd-planning/milestones/literature-identity/016-phase-LI4-corpus-gate.md
    sha256: fa58d0f0e322813a1997c7f4d5c5083631024f71e1e9babe3bc179d680b59eac
  - path: .gnd-planning/milestones/literature-identity/017-phase-LI4-review-amendment.md
    sha256: aba4dca5f59e54b2a0af9d1e15eb8db777611f461937227fd917f1a468d067da
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI4-spec.md
    sha256: 30f20e7509b71e5f236fe67897b2af721561f5f84c2a82b7d3f3401b8e2ba90c
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI4-claude-review.md
    sha256: a747b89d7f2c7dc9fc3ec616de5910e0f597028399c704ab5a74030d00ea9342
  - path: .gnd-planning/milestones/literature-identity/evidence/LI4/reference-admission.json
    sha256: 6d262018a18c6feb69922be8b79bee8ee87b2cf46a58e5a65addcc553ad0f16f
  - path: .gnd-planning/milestones/literature-identity/evidence/LI4/review-repair-ruling.md
    sha256: 0190d299ae0452869e253925374424c03d537b3b296ecb982fa1fcd974343fab
  - path: src/gnd/examples/literature/assertion_admission.py
    sha256: 761f67d33e641feabb379882e8e788f6ea505b7d6a7e21b96592eb8cd2a9735b
  - path: src/gnd/examples/literature/assertions/README.md
    sha256: d99ac2d80eb68da97e6e44456739364392d7507d7e12659b8b67bbeda2a2170e
  - path: src/gnd/examples/literature/assertions/case-outcomes.json
    sha256: 8aa6376f99843952d3cd927985d52a86fd476758abdda54d6f0617d5b866a26c
  - path: src/gnd/examples/literature/assertions/evidence/passages.txt
    sha256: 9b0415e9d4eb6cb8bb3f7111e312f0d28e8db78656008c70e76d85c2e909e0f0
  - path: src/gnd/examples/literature/assertions/model.orm.yaml
    sha256: 3212647b84df439e3304d598275864b0b47cc0ef22fc530c6293b27c7e440f5b
  - path: src/gnd/examples/literature/assertions/policy.json
    sha256: 12d39807219c32f35cb625d613d0338cd5421c37454b99347d8af5fbbe0e1817
  - path: src/gnd/examples/literature/assertions/raw.population.json
    sha256: ea96584c9b24d61c2833741001570ebb6c53a92516533e40fdcec2fcdf7b0173
  - path: src/gnd/examples/literature/assertions/receipts.json
    sha256: eef164ad47ec9095e0b946c1195b0b8b88982e4cd8a2176ae5556350a3da2705
  - path: src/gnd/examples/literature/assertions/rubric.json
    sha256: 1c98384795afd57033b0416a6e8dbd6cd3f914a33fadc3510f605394079b0178
  - path: tests/test_li4_assertions.py
    sha256: 407665086a7722571204cf8face573a0539cd60d96d74b1298ec9830826c4297
  - path: src/gnd/skills/gnd-extract/SKILL.md
    sha256: 0fe0787dc83e0801db6f88e56e57ce1bef2123782d71294a2de773104b6212ed
  - path: src/gnd/skills/gnd-model-from-text/SKILL.md
    sha256: 29fad276e35c81897b2dc09904fda0736ddde8238572da0a1df66fec485c0d88
---

# Claim

The contextual assertion example invokes the saved-judgment command over
captured inputs and emits an admitted population plus a digest-bound
record. The worked example retains supported conditional and conflicting
findings under different experiments. It preserves the raw extraction
and source-linked reviews as distinct evidence.

## Criteria

| Criterion | Observed control |
|---|---|
| A1 | Replacing the required condition with the absence marker, while recomputing and pinning the approving input, fails the occurrence's semantic-support check and removes it from the admitted population |
| A2 | A co-occurrence misread as implementation receives the rubric's stretched disposition and a verified rejection |
| A3 | The four polarity and attribution pairs remain distinct in the raw subject and outside the positive projection. Both contradictory findings keep their experiment and condition |
| A4 | Verified abstention and missing review are individually visible and do not appear in the output. Stale subject, stale source and excess targets refuse before publishing |
| A5 | The publication marker binds model, raw, policy, receipts, actual report and admitted bytes. Whitespace-only receipt drift moves the marker but preserves the admitted bytes. A changed pinned verdict moves both. Missing and malformed inputs and a supplied approval report refuse |

The raw subject's context and the approval state are verified separately.
The source model, receipts, rubric and expected outcomes remain tied to
the corpus approval in [016](016-phase-LI4-corpus-gate.md). The current reference action selected 7 of 10 supported statements and
3 of 10 positive own findings. The direct case checks that the admitted population loads and checks at exit 0.

## Verification sequencing

The admitted action's snapshot subprocess is bounded by the shared
process runner. The supported 1,024-occurrence projection passed the
timed control. The process publishes an immutable result with the
existing manifest-last artifact primitive.

## Independent review and repairs

Claude Code checked the exit mapping, manifest-last publication order,
positive projection and fixture rationale by reading. Execution and
caller-specific edge cases remained for the focused gate. The
[review amendment](017-phase-LI4-review-amendment.md) retains the original
choices and binds the revised example boundary.

| Review finding | Verification and disposition |
|---|---|
| F1, self-asserted policy | Reproduced a self-asserted approve producing an admitted projection. The example requires consumer-pinned evidence and refuses that run |
| F2, unpinned verdict | Flipping a receipt without replacing its policy pin now has a refusal control. The generic command retains responsibility for authenticating pinned bytes |
| F3, null-like condition | Reproduced accepted variant spellings of absent conditions. Case and surrounding whitespace are handled for the three documented absence words. The projected source row is copied verbatim |
| F4, work and passage key | The worked model uses one location per statement, with distinct keys for separate excerpts. The complete corpus keeps both experiments. Repeated statement locations refuse rather than coalesce |
| F5, matching report | Check the returned policy and receipts hashes and ordered target coordinates against the captured inputs. Preserve the canonical empty-receipt case. The exact report is bound alongside the raw and admitted bytes |
| F6, mention span | Reproduced the wrong byte slice. The corpus correction selects Quartz in working-notes and rebinds opinion bytes. Accepted indexes and original expected outcomes stay fixed |
| F7, weak controls | Over-limit targets are distinct. Rubric and receipts are cross-checked, four non-positive reasons are distinct, and a determinism check compares every publication file. Timing establishes the tested maximum instance bound |
| F8, disclosure and environment | Reproduced customer mode refusal with the old flag. The ordinary redacted report supplies the required decisions. The tested interface is the installed CLI and its synchronous example producer |
| F9, receipt drift | The retained JSON report and the admission marker bind the raw receipt serialization. A harmless byte edit preserves the admitted population. Configured judgment floors decide which combinations of several opinions suffice |

The original supplied input files are retained by commit caf0c469. The
current raw subject, policy and receipt identities bind the corrected
mention. The evidence text and approved case-outcome file stayed fixed.

## Refactoring review

The example reuses the official judgment command, safe reader, process
limits and no-replace publication. It keeps condition and eligibility in
one projection walk and keeps the underlying judgment contract in its
existing home. The skill pointers lead to the contextual worked example.

## Boundary

For the phase diff, one reviewer is one reviewer. The retained evidence
contains the read-only Claude Code diff review and the outcomes of its
reproductions. Saved opinions and the synthetic example carry the author
rubric and its bounded scope. The admitted population is the selected
digest-bound projection of those inputs.

## Open questions

- LI5 supplies the lineage and transfer interpretation of admitted rows.
- The evidence layout and safe path documentation remain inherited.
