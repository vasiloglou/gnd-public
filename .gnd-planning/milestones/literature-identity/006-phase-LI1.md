---
milestone: literature-identity
station: "phase-LI1"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-LI1
date: 2026-11-15
gates:
  - command: "uv run pytest -q tests/test_li1_literature_corpus.py tests/test_li1_assurance_report.py --tb=short"
    exit: 0
  - command: "uv run pytest -q tests/test_composition_example.py tests/test_fidelity_payload.py tests/test_fidelity_match.py tests/test_public_fidelity_scope.py tests/test_mc1_guards.py tests/test_gnd_arch.py tests/test_li0_witness_wire.py --tb=short"
    exit: 0
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
  - command: "uv run ruff check"
    exit: 0
  - command: "python3 scripts/components_index.py changed --base 547acaf1 --strict"
    exit: 0
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request only"
  reason: "LI1 changes no historical bytes, census input or src/gnd module outside src/gnd/examples/literature"
evidence:
  - path: src/gnd/examples/literature/assurance_report.py
    sha256: ce46bbb837443a52ca55d89315766e0d1943dc8ca8c3382526a947a498dd6149
  - path: tools/build_literature_example.py
    sha256: 54ddc55abab17fa6ecb84bb45fd4e85c78a722db14955c0d33c28ab27f5dbe3d
  - path: tests/test_li1_assurance_report.py
    sha256: 99cd86c6ddc29fea49053472e452e5ba5e930517b7449527481bc2f6f18bb7ae
  - path: tests/test_li1_literature_corpus.py
    sha256: 870b39283485440c9a2449cb6b542694fbc1171542ad9fdd7a39d62805334f01
  - path: src/gnd/examples/literature/README.md
    sha256: 0cdcc7e64883db9a7a2c059843e40fdc788d83dc52520433e30997d9c4335717
  - path: src/gnd/examples/literature/answers/answer-key.json
    sha256: e183f2cf840b176925da2bbcf4d3cd207fb116933ebbd732301f96a385058944
  - path: src/gnd/examples/literature/corpus/corpus.json
    sha256: 9b572f981660f273a6db95ec248f106db0e618fecea7de8dda934c329fdcd5f1
  - path: src/gnd/examples/literature/expected/reference.report.json
    sha256: 483fc2772b33f83e81da57d8e44b58d39af702bd2c51ca88bd3066528ffff499
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI1-spec.md
    sha256: d2868b5624b64438fa31c282d94357db040618f187b31409d85aeef3d6733228
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI1-codex-review.md
    sha256: cabf74d1df36c04c184e28f1463752b9781a48d0be814256f7c5c31200232174
---

# Claim

`python -m gnd.examples.literature.assurance_report CORPUS ANSWERS RUN`
scores a literature run in seven separate stages:
- **The reference run:** exit 0. Its five active stages pass, and
  `identity-decisions` and `coverage` are `not-measured`, owned by LI2 and
  literature-depth LD3.
- **The six C2 mutations and the X1 and X2 cases:** each exits 1 and fails
  exactly the stages its owner-approved expectation file names (C2, C5).
- **Invalid input:** exit 3 with a value-free reason, and no traceback.

The corpus meets every C1 floor. Its held-out answer key is off the branch
and pinned by digest (C6). The harness reads gnd only through four literal
CLI routes (C3). Every report states its sample sizes and disagreements, and
says the labels are not independent expert ground truth (C4). The
abstaining run reports precision 4/4, recall 4/8 and abstention 6/12 (C5).
Dormant stages never count toward exit 0 (C7).

## Gate output (verbatim)

    == direct
    71 passed in 78.42s (0:01:18)
    exit 0
    == consumers
    149 passed in 32.32s
    exit 0
    == guards
    679 passed, 2 deselected in 92.10s (0:01:32)
    exit 0
    == ruff
    All checks passed!
    exit 0
    == components
    changed against 547acaf1 (547acaf): 135 file(s) differ; 0 to fix, 0 warning(s), 0 to reread
    exit 0

**Red first.** At the corpus gate (`cd30649b`), the 47 harness tests failed,
every one on the missing harness module, while the 6 corpus tests passed. At
`4c261d29` the same 47 passed against the unchanged expectation files.

## Verification-selection ledger

| Obligation | Disposition | Command or evidence | Result |
|---|---|---|---|
| LI1 direct tests (C1–C7, T1–T24, the review regressions) | run | first gate | 71 passed |
| Affected consumers (plan §9 row, the example walks, the layer exclusion, the LI0 identity golden) | run | second gate | 149 passed |
| Structure guard list | run | third gate | see the gate output |
| Lint | run | `uv run ruff check` | clean |
| Component index | run | `changed --base 547acaf1 --strict` | exit 0 |
| Broad lanes | cadence | `uv run pytest -q -m "evidence or census"` on explicit request | not run: no historical bytes or census inputs changed |

## Review

One reviewer is one reviewer. Codex (`gpt-6-sol`, xhigh, read-only, prompt on
stdin) reviewed `4c261d29`, and the [review note](notes/phase-LI1-codex-review.md)
keeps the review verbatim with its triage. It found five defects, and all
five were reproduced before any fix:
- **R1 (blocking).** A composition that leaves out a run source still
  passed, at exit 0.
- **R2 (blocking for validity).** A route that prints no report still
  counted as an agreement.
- **R3.** A field of the wrong type was refused as `internal`.
- **R4.** An unwritable `--out` printed a traceback.
- **R5.** The version came from importing gnd.

Each fix has a regression test that fails against `4c261d29`. The red run
gave 7 failed and 1 control passed. The fixes moved no approved outcome: the
nine report goldens changed only in `harness_sha256`.

## Refactoring review

**Refactors EXECUTED.**
- **The local derivation rule now has one home:**
  `tools/build_literature_example.py::with_derived`. It was written twice
  before, in the builder's `source_facts` and in the test module's
  `_drop_fact`.
- **Behavior preserved.** The rebuild is byte-identical (`diff -r` against a
  pre-refactor copy), and all 71 direct tests pass.

**Seen and deferred.** These become open questions below.
- **Two layouts for one document's evidence.** A composition source folder
  holds `document.txt`, `population.json` and its sidecars. A fidelity case
  holds `document.md`, `extracted.population.json` and its sidecar. The
  harness copies bytes from one layout into the other. One layout would
  remove that step.
- **gnd's safe readers refuse a path that passes through a symlink.** That
  includes macOS's system temporary directory. Every caller must resolve
  its paths first, and nothing says so in the CLI reference.

## Boundary -- what this result did NOT establish

- **Labels.** The labels are one author's reading of public works. They are
  not independent expert ground truth, and the report says so.
- **The held-out key.** It is on the local branch `literature-heldout`
  (`2f3d441c`), which is not pushed. Its separation from LI5 development is
  procedural, not blind, and three chains are a smoke test (plan C6).
- **Body-level passages.** Four passages paraphrase claims from their
  papers' bodies, not their abstracts: sbi-frontier.p2, roberta.p3,
  roberta.p4 and segment-anything.p2. They were not checked against those
  bodies.
- **What the stages measure.** `derivation` measures agreement with the
  model's own rules, not truth. The false chains are committed but unscored
  until LI5. `identity-decisions` waits for LI2, and `coverage` for
  literature-depth.
- **Host-scale sets.** They were not run (plan D1). The harness accepts any
  answer key in the format.
- **No docs page.** No business-facing docs page was written (D7: LI5).
- **The time bound covers only the harness's own index.** T21 times
  `passage_index` and `anchors_in_passages`. Route costs are gnd's own.
- **Further authority.** No merge, publication, release or certification is
  authorized. One reviewer is one reviewer.

## Open questions

- **One evidence layout per document.** Composition and fidelity disagree on
  the file names for the same evidence. Target: literature-interop, which
  owns making extraction, composition and witnesses work together. Owner:
  unassigned.
- **Symlinked paths.** Document, or relax, the safe readers' refusal of
  symlinked path components such as macOS `/var`. Target: a maintenance
  pass. Owner: unassigned.
- **Model serializer tangle.** Carried unchanged from
  [003](003-phase-LI0.md).
