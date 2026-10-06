---
milestone: code-refactoring
station: phase-RF9
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RF9
date: 2026-10-06
source_base: f5a83186f7c2215ac2b2afb0a010c2294eaa433a
reviewed_source_commit: d440b2e37449ef46647d18c491c46d9bb8d3e851
gate:
  command: "PYTHONDONTWRITEBYTECODE=1 .venv/bin/python .gnd-planning/milestones/code-refactoring/evidence/RF9/local_checks.py"
  exit: 0
  output: "Graph: 227 modules, zero explicit SCC/wrong-way/entry violations; 432 frozen controls unchanged; production unchanged."
  note: "Review completion only. The focused stale RF6 test exits1; reproduced defects remain open."
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "Broad default, historical, provider/oracle, evidence/census, proof, distribution and certification suites are outside RF9 review-only scope."
evidence:
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9/A-behavior-prompt.txt, sha256: f311732cc84ced4ce3a11b1809edec6a7053e75748a33236c9951cb0b2f11086}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9/B-architecture-prompt.txt, sha256: b895e1b9efb09dcddd2959fb1320cdd56d2c4888930d53f644cc93d33eff0e4e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9/C-state-input-prompt.txt, sha256: f8bc52ce900da4d746b2e71651179e9150f862ddb03f52a430d83daceeccf81e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9/C-state-input-retry-prompt.txt, sha256: 63452ec82f52a4ca2c0e9c362c73c2b6b18303b0d236a1dd0954a2ee7d51a7c5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9/D-test-integrity-prompt.txt, sha256: 287c1dfc83e69fdf4c200b64eaff045d53ef0f0484fea968a497a14a7eb89ff0}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9/architecture-comparison.json, sha256: be01544a932538dd135da49917f059f43fee8df7ff04e2e938096dbe0788751d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9/authorization.json, sha256: 45ba509fe4b04e07bbe77c61b21725e61d30eb0e448db6d7d0a49b9dd8a67d83}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9/final-checks.txt, sha256: a4d1f9201f4c0ad836d6805d4418a2404ab6580b4cd6580ccd471cf11d008f2e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9/local-checks.json, sha256: defd84e8194b266f4ceb5bc240ad12f5a0002c1a0af9627a1a5da02bc2996167}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9/local-checks.txt, sha256: 7a41450ce5069c780affa15325b63a4c8a54cabd779f467e49c13cf85800cbc6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9/local_checks.py, sha256: 8ea896689dec0b823d0c92b031ab6972f383a15dfd5ddfcd21e15235e6da0381}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9/provider-status.json, sha256: a1c307232398f5e83e6df4d4046ae26af8ef7c7916c19bf6dd548e93d9564f7f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9/reproductions.json, sha256: daf2a814101d7f362a997fb7ad95412239e85c077914c62b826b52d9269d5f62}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9/reproductions.py, sha256: 7d5aed7fe074f3e7317c00f07ab052050085c0c8b96e3df792d00f7aa9f4c4fa}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9/stale-test.txt, sha256: 818abd8754d0924efe6e86457bd8cc09ec4da46ad89e5471826116d4d548be0c}
  - {path: .gnd-planning/milestones/code-refactoring/notes/code-refactoring-plan.md, sha256: 06508743abf6c039390171e1d85a09f6383da75f43f1993f5e1303d087976d20}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF9-A-review.md, sha256: 6f380a991fd7fb59ba38f9879cca445a18f9d205c6efd85dbecfa6a54acf6c51}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF9-B-review.md, sha256: 0b0ccd7f95e8f5a1a8d2b2c52dcd026dbfd41b17cccc6a4bf9ee39491ff9cd27}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF9-C-review.md, sha256: 3af74ebaf3d86bca04ce3f99e02cbb408c581b231ec1239e255bcd9e59b79d22}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF9-D-review.md, sha256: d6d98fb118ee378410f51abcab04f334e24a517f782139174c3e6b27ea254400}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF9-review-status.md, sha256: 3199eb65fbbb61a3f36d02318f7ea578eedee81f0d734016dd7c3128c86caa9e}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF9-review.md, sha256: 8c41ceb2257523304f3afa188f380765af68ecaabd81bd4c76e5ce629d54279b}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF9-spec.md, sha256: 46969598bba7e6924c934bd686e81c548a4dd18b6ea39de709adf1869f0a670c}
  - {path: .gnd-planning/milestones/code-refactoring/014-phase-RF8.md, sha256: 6b8ae1618922138d8beaed414c461ac075540cf237cdba48ae1ebbb0062f8b13}
---

# Claim

RF9 completes the owner-requested cumulative review of RF2–RF8 at d440b2e, with
four retained native area assessments and nine reproduced, triaged observations
in notes/phase-RF9-review.md. The local-check command exited0; the focused stale
RF6 test exited1. This is review completion with open findings, not product
acceptance or completed repairs.

## What shipped and authorization

The owner requested registration and detailed review; ab00c5d added the narrow
RF9 plan amendment and review-only spec before work. fd5c635 retained initial
local checks and the provider refusal. The subsequent owner reply approved four
native Codex review areas and source/diff transmission with native authentication.
No credential environment file was read. The initial launch was rejected by
automatic approval review before execution; provider-status.json preserves it.
Area C then hit provider capacity, exit1, with no final assessment. One retry of
the same initial area completed exit0; no repair review or scope expansion ran.
The four returns use the same model/provider and separate native CLI contexts.
One reviewer is one reviewer; this is not the maintained advisory panel, a
model-diverse consensus, certification, or milestone-close review.

Delivered: four sanitized verbatim returns, fixed prompts and execution status,
a detailed findings report, current/baseline architecture metrics, reproducible
local counterexamples, a focused pytest failure, and this record. Original plan
r2/e1 text remains historical; the additive owner amendment controls RF9 and
recognizes the subsequent RF7 authorization. Old review/certificate opinions do
not attach to this amendment or changed production bytes.

## Criteria and branch audit

| Criterion / declared review branch | Evidence and result |
|---|---|
| RF9-C1 four areas | A/B/C/D final notes identify fixed subject, scopes and gaps; all four completed exit0, C after one capacity retry |
| RF9-C2 findings | F1–F9 each have exact source, trigger, expected/observed, severity, relevance, reproduction and proposed successor |
| RF9-C3 origin / approved policy | Exact historical modules/AST distinguish RF3/RF8 regressions, RF6/RF8 evidence gaps, pre-existing close/import-walk issues; RF7 strictness is approved |
| RF9-C4 coverage / metrics | Report matrix plus architecture comparison and limitations; 625 binding checks establish existence only; absent baseline entry policy is null |
| RF9-C5 stable source | git diff d440b2e -- src tests tools empty; all432 frozen controls SHA-identical |
| Counterexample controls | Honest stagnation refused, forged terminal accepted, malformed extra field refused; empty-launch outer gate refuses despite helper crash |
| Observer controls | Literal query injection invisible; early-cache injection invisible while unrelated statement detected; from-import missed while direct import detected |
| Compatibility controls | Equality true/false/true around serializing one/both contracts versus always-true predecessor; digest type hints resolved before and fail now |

The report records F1/F2/F3 as blocking their acceptance/test/exact-inventory
claims; F4–F9 are hardening. No repairs were made before or after triage.
F7 explicitly narrows the native candidate: only the direct declared-case helper
crash is reproduced, while the outer gate refuses the tested empty-launch case.
No unproven end-to-end close traceback is presented as fact. The feedback-tamper
hypothesis was rejected by actual validation; the confirmed F1 is terminal-result
acceptance, not feedback acceptance.

## Measurements and budget

Explicit AST runtime SCCs:5 ->0; wrong-way edges:27 ->0; modules:148 ->227.
Private imports:242 ->670; identical-AST candidate groups:15 ->12.
Largest module:9088-line cli ->4890-line model._validation. These are instrument
measurements, not an aggregate quality score. Seven service imports execute an
entry-mapped parent omitted by the graph; the parent currently has only a
docstring. No harmful hidden cycle is established. Each revision uses its own
layer map with the current instrument. Baseline entry policy was absent.

Budget:24 touched RF9 artifact/probe paths against25; evidence probe lines and
non-evidence additions are measured in final-checks.txt against1000/1500. No
budget increase was selected. Four initial areas yielded four assessments through
five provider executions (one failed capacity attempt); zero repair rounds.

## Gate output (verbatim)

Command: PYTHONDONTWRITEBYTECODE=1 .venv/bin/python .gnd-planning/milestones/code-refactoring/evidence/RF9/local_checks.py

```text
Graph: 227 modules, zero explicit SCC/wrong-way/entry violations; 432 frozen controls unchanged; production unchanged.
Bindings: 625 definitions/constants in 12 selected modules remain importable; existence only.
Exit: 0
```

Command: PYTHONDONTWRITEBYTECODE=1 .venv/bin/python .gnd-planning/milestones/code-refactoring/evidence/RF9/reproductions.py

Exit:0. Full structured output is reproductions.json. This exit means the saved
counterexamples and comparison assertions reproduced; it does not mean those
product properties pass. The focused existing pytest output is retained verbatim
in stale-test.txt:

```text
1 failed in 0.06s
Exit: 1
```

Command: .venv/bin/ruff check .gnd-planning/milestones/code-refactoring/evidence/RF9/reproductions.py .gnd-planning/milestones/code-refactoring/evidence/RF9/local_checks.py --output-format concise

```text
All checks passed!
Exit: 0
```

Command: git diff --check

```text
Exit: 0
```

Each native command template, prompt path and exit is retained in
provider-status.json. No full default or historical suite ran. Initial probe
instrument errors and lint observations are retained in the spec, with corrected
successor scripts. In particular, mismatched launch counts and invalid wire fields
were correctly refused; they are not product defects. The initial graph-map and
missing-key errors arose in the comparison instrument. Historical local status
and its old hashes remain available at fd5c635; this report supersedes its
pending-provider status and unqualified graph wording.

## Refactoring review

What did this phase's work reveal about existing structure that should change?
None needed within the review-only artifacts: one shared probe file, one detailed
finding report and thin evidence/record bindings suffice; no production refactor
was executed. Seen but deferred: central terminal-acceptance verification and
absence handling (F1/F7), profile cache/equality ownership (F4), graph/package
ownership (F6), and precise physical-observer scope (F3/F5/F9). Their named
successors are in the report and the open questions below. Deferral is required
by the authorized review-only boundary, not an assertion that repairs are unnecessary.

## Boundary -- what this phase does NOT establish

Every criterion is satisfiable even when defects remain: RF9 produces an assessed
review, not an assertion of correctness. Four views can share blind spots.
Focused probes cannot establish untested platform, timing, installed-package or
release behavior. Review-only phase has no production implementation step;
subsequent repair work needs an explicit user instruction. No production/test
repair, full default/historical replay, provider oracle, certification, release,
merge or milestone close ran. The outer work acceptance gate and helper probes
are not a complete close command across all obligations. Historical module
comparisons use current compatibility dependencies, not a full historical
execution environment. Current name existence does not prove full ABI behavior.

GitHub CI was refused before steps on d440b2e due to account billing/spending
limits. That historical observation does not establish current-head CI results;
any PR status after this commit is a separate remote observation. Required CI and
review conversations must be resolved before merge. The PR remains a draft.

## Open questions

- F1/F7 -> session acceptance-integrity successor: verify retained terminal claims
  and missing best; add a genuine launched/no-eligible control for full reach.
- F2 -> RF7 affected-test successor: align inheritance assertions with approved
  literal-True rules, preserving positive and negative coverage.
- F3 -> RF6 query-policy successor: inventory fixed getattr reads and classify them.
- F4 -> session-profile successor: cache-neutral contract equality.
- F5 -> RF8 observer successor: position/cardinality plus refusal-state controls.
- F6 -> architecture-policy successor: implicit parent initialization and shared
  output placement, without blanket exemptions.
- F8 -> compatibility/typing successor: runtime annotation resolution without cycles.
- F9 -> source-owned OQ-V52-P1-IMPORTWALK-1 successor; no authority transfer.
- Prior RF1-OQ2/OQ4/OQ6/OQ7, source-owned questions, original RF6b/RF7/RF8 budget
  misses, historical-body/ownership reconciliation and shim retirement keep
  their existing owners. Milestone close must sweep them explicitly.
- GitHub billing/required CI -> owner/platform before any merge.

## Refuted premises

F3 refutes the exact live-query inventory claim; F5 refutes unrestricted moved-body
normalization as proof that arbitrary body changes are detected; F6 limits the
runtime graph guarantee to explicit imports; F2 refutes current RF6 test alignment
with RF7. F1 refutes terminal-acceptance sufficiency; F4/F8 refute the selected
compatibility assumptions. F7 narrows a reviewer candidate rather than asserting
its full reach. Evidence is bound in the frontmatter; original phase records remain historical
and are not rewritten into retrospective passing claims. No further review round
is selected merely because these findings remain open.
