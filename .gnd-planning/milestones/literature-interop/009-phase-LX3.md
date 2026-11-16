---
milestone: literature-interop
station: phase-LX3
skill: "n/a -- repository development under process-phase"
scope: phase-LX3
date: 2026-11-15
gates:
  - command: "uv run pytest -q tests/test_lx3_catalog_composition.py tests/test_composition.py tests/test_composition_example.py tests/test_witness_composition.py tests/test_li2_resolution.py tests/test_reference_population_corpus.py tests/test_lx2_witness_flattening.py tests/test_mc2_consumers.py tests/test_public_semantic_composition.py tests/test_schema_sync.py tests/test_public_replay_admission.py tests/test_gnd_arch.py --tb=short"
    exit: 0
    output: "802 passed, 3 deselected in 114.06s (0:01:54)"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 104.34s (0:01:44)"
  - command: "uv run ruff check --output-format=json"
    exit: 1
    output: "188 diagnostics equal the predecessor by file, line, code and message."
  - command: "uv run ruff check <changed Python files>"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base 6d2ecece --strict"
    exit: 0
    output: "0 to fix, 0 warning(s), 13 to reread"
  - command: "claude -p --model opus --permission-mode plan --add-dir <review-dir> -- '<brief-path prompt>'"
    exit: 0
    output: "VERDICT: CHANGES_REQUESTED"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: explicitly scoped owner or CI selection
  reason: the affected-route gates cover the changed wire, bindings and source obligations
evidence:
  - path: .gnd-planning/milestones/literature-interop/008-phase-LX3-spec-gate.md
    sha256: aeaad3e30f5625a5d7e4d9cb71cd07ed76abfd31e96809abe39fa2bc59295bfe
  - path: .gnd-planning/milestones/literature-interop/notes/phase-LX3-spec.md
    sha256: bd048c716eb1b59c31b7aedc10ec61a6bd08dae0209272085c344fa3d1a50455
  - path: .gnd-planning/milestones/literature-interop/evidence/LX3/dynamic-query-successor.json
    sha256: 0c6ae733681b978f8f7206e3edc032f4203a90886e979acf2ad62cbaf6888330
  - path: .gnd-planning/milestones/literature-interop/evidence/LX3/review-dynamic-query-successor.json
    sha256: 36ee51ab7b585743b2a35628d2e051f0055b00d9a450b390fdfad8afedcd3c51
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX3-r1/BRIEF.md
    sha256: c7f5042f57a2dc4706c82a6bf8fc3c8a35da280ad864f0ba4cb0a5537052cef9
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX3-r1/FINDINGS.md
    sha256: acbe96741e0f92f709f520d4192ef3902e79cdd3efaeb0babed234877d1f6ac2
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX3-r1/brief.json
    sha256: 26b45b05499e6abd4156ddaad0cd7d3130ced86eec763956a6a6dd10605cc522
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX3-r1/diff.patch
    sha256: 075a371d811ba60ee5e58f8fbfbdb9dd6cb27ab473c41bbd08d63d561bda6e89
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX3-r1/review.log
    sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX3-r1/review.md
    sha256: 85072479536f5e6d0234052ffd0009611285d7f214b0a17eef1ce7f01a49253f
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX3-r1/run.json
    sha256: 22ef9513c2befd6c6bbbee59ee16a47d4c05f8576df23da61d66c57d043d00ae
  - path: src/gnd/composition.py
    sha256: d003fd8148e8e7d428d406d6e1d35053a4c440af973a583bb882624a008c873f
  - path: src/gnd/checking_service.py
    sha256: 8b0a4a56d5aea378d1b7f2f5a39086fa184dfd8baac2d3c16af704b99bbf9da4
  - path: src/gnd/checker/_composed.py
    sha256: 27e7c227b66931980bced06b51b7d98ae8fbfb9ecf492d79d48f1572d1ba7d43
  - path: src/gnd/model/__init__.py
    sha256: dc50019af1b32b9661a415d63af98bbfe9af763e2fee9b97584be8a2faba92ba
  - path: src/gnd/witness/service.py
    sha256: 1c163e45a9934937a4ea07ff5594a7d3c469a70ecc30ab557c626571f24490e4
  - path: src/gnd/witness/kernel.py
    sha256: 17dcb159bbdc0a201ba8afe9b1ff423a8c9c62d7a8b11e6e8ed3e3b34d12b4e6
  - path: src/gnd/witness/io.py
    sha256: daf40df3e737eb283cf369b85a590de11685dc573da0420d2a30a0ce694e2716
  - path: src/gnd/schema/witness.schema.json
    sha256: 4e5ee050eec431d8eb2c7fb9e2f4f6a150da6a0559bddbf4912e1cd390ec9409
  - path: tests/test_lx3_catalog_composition.py
    sha256: 44c20a60f98be8341e65bc40efbd5e8027b6a875208037b22bd1598f250d3a0d
---

# Claim

LX3 composes candidate sources with fixed reference catalogs and produces
a checked, reproducible mixed witness. The catalog and candidate rows keep
separate bindings. Legacy reference-free record bytes and replay controls pass.

| Criterion | Evidence |
|---|---|
| LX3.a | Compose renames the candidate alias onto an authenticated catalog value. The output and lineage coordinates contain candidate rows. The composed checker binds one combined view, its subset check passes and the candidate-only subset fails. Both reference-free artifact hashes match the phase base. |
| LX3.b | Catalog keys, subset and equality dependence, current invalid data, changed pins and stale records have executable refusals. Independent source mutation is detected by source verification. The LI2 unjustified-join control still refuses. Explicit anchor and reference overrides retain their refusal. |
| LX3.c | Version 4 binds a mixed proof over candidate and catalog facts. Swapping either fact origin, forging the model origin or changing the catalog binding refuses independently. Both include-bearing and include-free catalog proof routes replay. |

## Gate output

    802 passed, 3 deselected in 114.06s (0:01:54)
    679 passed, 2 deselected in 104.34s (0:01:44)
    All checks passed!
    0 to fix, 0 warning(s), 13 to reread

Whole-tree Ruff retains the same 188 diagnostics by file, line, code and
message. The locked CPython 3.11 environment ran with the default marker
filters. The replay-admission harness used host process inspection.

## Independent review

The owner authorized one Claude Code Opus review at `28dc21b7`. It
returned CHANGES_REQUESTED after verifying all 32 brief digests. It
reported 103 selected tests, compared the pre-change reference-free
artifact bytes and checked the schema, version and catalog downgrade
controls. Its structural, lint and component checks were outside its
executed tests. The original [review](notes/reviews/phase-LX3-r1/review.md)
and [ledger](notes/reviews/phase-LX3-r1/FINDINGS.md) are retained. The patch
keeps its unified-diff context bytes for the review digest.

Equality dependence and current-invalid diagnostics reproduced on the
reviewed commit. The driver also reproduced a witness accepting a record
with a catalog occurrence listed in candidate lineage. Four new failing
cases passed at `9e1c1d29`. The tentative ambiguous-lineage concern had no
reproduced observable case. The review status identified 18 unchanged
reviewed files and 14 updated files. The selected local gates establish
the evidence over the repairs.

## Refactoring review

Refactors EXECUTED. Candidate merging and record construction share one
implementation between compose and checking reconstruction. Catalog
validation uses the existing bound reference snapshot and the shared
typed identity and model-role helpers. The same digest-specific input
error serves both rooted load paths. Witness and replay share one
catalog and coordinate validation path.

## Boundary

One reviewer is one reviewer. Check authenticates the original candidate
sources. A witness binds their given record and verifies its coordinates
and occurrence proof. The example's extraction-to-checking rebind and
advisory dates belong to LX4.

## Open questions

- The synchronized dev-tools prompt separator follow-up from LX1 remains
  with the tool maintainer.
