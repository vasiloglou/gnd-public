---
milestone: model-composition
station: "Reproduced close-review repairs"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: close-review-repairs
date: 2026-11-10
gates:
  - command: 'independent Codex CLI close review at b89747d6, one reviewer'
    exit: 0
    result: 'REVISE: one blocking compatibility defect; one hardening guard defect; not approval'
  - command: 'actual regression tests before repair, corrected include admission answer'
    exit: 1
    result: '4 failed, 2 passed in 0.42s'
  - command: 'same actual plain regression controls with baseline459ca8d2 adapter bodies'
    exit: 0
    result: '2 passed, 2 deselected in 0.33s'
  - command: 'focused new regression controls and original source-order guard after repair'
    exit: 0
    result: '7 passed in 0.38s'
  - command: 'pytest RF1 helper pins, MC3 source observations, RF8 structure and RF1 layering'
    exit: 0
    result: '125 passed in 25.82s'
  - command: 'ruff check src tests --output-format json'
    exit: 1
    result: 'exact same13 baseline findings and positions'
  - command: 'components_index.py --no-cache changed --base origin/main --strict'
    exit: 0
    result: '0 to fix,0 warnings; subsystem.witness reread/disposition below'
  - command: 'ruling: delegated (auto=true) approve repair gate and plan amendment sha256 3771e633175c4771af09d404726f981d80b9531f3667272f740404c77f1dc494'
    exit: 'n/a -- scoped repairs only, not close or merge'
evidence:
  - path: .gnd-planning/milestones/model-composition/evidence/close/review-repairs/manifest.json
    sha256: a079a56d7561ec6f9b6adc2dbdb85ba235862ad37ba16ea0ae13d82e982992f2
  - path: .gnd-planning/milestones/model-composition/notes/model-composition-plan.md
    sha256: 3771e633175c4771af09d404726f981d80b9531f3667272f740404c77f1dc494
---

# Claim

The first selected independent close opinion atb89747d6 is REVISE: one blocking include-free witness/replay refusal regression and one hardening gap in a delivered source-order guard. Both reproduce before fixes, and both have actual new controls observed red. Baseline459ca8d2 adapter bodies pass both plain controls. The repaired adapters forward only include:* reasons, preserving input-invalid for semantic validation failures, as neighboring adapters already do. Source-order guard additionally binds the first candidate call argument and rejects two wrong-argument mutations. Runtime candidate binding remains unchanged.

## Gate, observations and limits

Delegated approval (auto=true),2026-11-10, authority original named milestone delegation plus current continue request, gated exact D1–D5 spec before production edits; gate.json binds original prefix and pre-fix implementability correction. Initial6-case run had6failures because the proposed included hash-mismatch answer was itself wrong: composed-population lineage refuses include-bearing inputs as unsupported-route first. The corrected pre-fix run has4fail/2pass; this preserves the admission matrix rather than enabling a route. All model/population/composition/certificate inputs in the regression are real bytes; no synthetic validation exception or lineage skip. Baseline probe substitutes only the two actual baseline adapter bodies, retaining current compatible read/binding helpers.

Existing-regex call binding restores the original intended argument assertion without whitespace coupling or a new parser/helper. A missing tests support import in the first manual guard probe was setup-only; the corrected actual guard invocation reproduces the dirty pass before edits. Initial new local import spacing produced one added lint finding; one blank line restores exactly13same baseline findings. No new warning is accepted.

Current MC2source110/test585 under375/600; MC3source1109/test1239 under1400/1400; MC4test120/120unchanged. New4production/20MC2test/15MC3test lines remain explicitly attributed. Combined post-MC3 support163=120+22+21, not163under120. The witness.service component is reused/adapted; its existing subsystem summary still correctly describes production/replay scope, so reread requires no new subsystem or dependency edge. Generated witness module index is refreshed. Existing homes and zero layer allowances remain unchanged.

## Boundary and next gates

The broader affected witness/composition selection is still running at this record's initial snapshot. Its result will be retained separately, not guessed. Prior full1ca2379f comparison remains historical and no longer covers the changed refusal code. Repeat the named owner-authorized beast-3 corrected candidate default/census with exact six frozen failure IDs and unchanged400originalobservations; rejected/incomplete outputs remain distinct. One remaining narrowly scoped Codex CLI confirmation follows concrete final results, maximum2calls total. No third review, panel, subagent, native/external replay, credential-file read, publication or certification.

Actual maina9b67d8b remains the pre-repair MC4 tree. PR158 now includes the two runtime refusal repairs as well as tests/prose/evidence; its final fixed-head merge needs separate explicit owner authorization. Issue95and actual on-main close remain pending. No local repair ruling or first review REVISE is milestone acceptance.

## Refactoring review

None needed beyond adapting the existing witness component entry: neighboring adapters already establish the include-specific/error-fallback pattern, two local replacements restore frozen behavior with no new home, helper or per-kind policy walk. The guard reuses existing regex support. A broader witness adapter cleanup is outside this bounded compatibility repair and unnecessary to demonstrate it. Existing delivered hook/index contradiction remains repository-owner maintenance.

Current reference/twins check exits0:2 passed in0.35s. Pre-fix failure logs retain only original pytest E-only trailing whitespace; explicit line enumeration is stored before commit. Authored source/metadata must remain clean.
