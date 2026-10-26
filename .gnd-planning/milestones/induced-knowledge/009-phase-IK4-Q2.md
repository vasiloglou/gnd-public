---
milestone: induced-knowledge
station: phase-IK4-Q2
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: phase-IK4-Q2
date: 2026-10-26
gate:
  command: "uv run pytest -q -p no:randomly tests/test_evolve_references.py tests/test_*evolve*.py tests/test_discover.py tests/test_ilp_bridge.py tests/test_measure_labels.py <every tests/test_*.py naming reference_populations> tests/test_rf*.py tests/test_gnd_arch.py tests/test_packaged_skills.py tests/test_public_binding_prose.py tests/test_public_built_inventory.py tests/test_public_distribution_runtime.py tests/test_verification_fixes.py tests/test_model_v2.py"
  exit: 0
  output: "3162 passed, 39 deselected in 264.10s (0:04:24)"
  note: >-
    Spec §8's selection, plus the skill-file inventories (the evolution
    contract changed) and test_model_v2.py (its source scan pins the preview
    call order). The expanded command line is the first line of
    evidence/IK4-Q2/final-gate.txt.
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection or separately configured CI"
  reason: "outside IK4-Q2's impact closure; the reduced v6.3 selection was run"
evidence:
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK4-Q2/tests-red.txt
    sha256: fef148c061c95829824973bf2a3c1a917d886d26a8ec97ddad588f07e56d87bf
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK4-Q2/regressions-red.txt
    sha256: 883ba28571993da4abfd60ef5c44e850810c43affc6a2143d331862e490c9ef2
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK4-Q2/final-gate.txt
    sha256: 2b3ac540fa8fca2e51c432764fb6c7cc89ce22ecc65b252f6d37ec7e3adf6124
  - path: tests/fixtures/induced_knowledge/ik4-q2-preview-at-b.json
    sha256: 9a3cdc1949ed1d0fe7c7e3c14f7050cd37ca385ad6858b9c6cc260075f3afa8b
  - path: .gnd-planning/milestones/induced-knowledge/notes/phase-IK4-Q2-agent-review.md
    sha256: 99ee2ca4bb2580498d1ee51ffa6c88d2bf3bbcd31831f6d41449aa1667420793
---

# Phase IK4-Q2 — evolve over reference-bearing models

**Claim.** `gnd evolve preview`, `apply` and `finalize` work on a model that
declares reference populations, binding them from the workspace model's own
directory as `gnd validate` does. A reference that cannot be bound is a named
refusal at evolve's existing exit for its class, never 70. Reference-free
outcomes are unchanged.

**Authority:**
- spec r1, approved 2026-10-26 with rulings D1..D4 (spec §13);
- the owner's ruling on I-F2, 2026-10-26 (spec §15): a missing reference file
  exits 66, a linked one 74, a digest mismatch 3.

## What shipped

- **One loader** in `src/gnd/evolve/service.py`, `_load_model_bytes`, for all
  seven model loads:
  - preview: current and candidate;
  - apply: current, candidate and staged;
  - finalize: staged before and staged candidate.
- **How it loads:** the bytes are loaded as if they sat at the workspace model's
  path, then bound with `gnd.model.bind_references` at its directory. This
  replaces the temporary-directory copy, where binding could not work. The
  parse is B's: a `.json` name does not select the strict JSON parser (review
  R1).
- **Binding failures** are wrapped as `ReferenceInputError`, as `load_model`
  does (I-F1), then as `EvolutionError` with the load's label.
- **The candidate's declarations** must equal the current model's. A candidate
  that differs is refused (3) before any of its files is read (review R2).
- **Contract:** `evolution-contract.md` §3 gains the binding sentence and its
  exits.
- **Tests:** `tests/test_evolve_references.py`, T1..T7 and four review
  regressions. `tests/test_model_v2.py`'s source scan follows the call's new
  shape; its ordering assertion is unchanged.

## Gate output (verbatim)

```
3162 passed, 39 deselected in 264.10s (0:04:24)
exit 0
```

The tests were committed red first (`ebad6cc`, `evidence/IK4-Q2/tests-red.txt`):
7 failed at exit 70, and T6 passed by design.

## Criteria

| Obligation | Test | Result |
|---|---|---|
| preview handles reference-bearing models | T1 | 0 |
| apply and finalize publish the candidate | T2 | 0, published bytes equal the candidate |
| unbindable reference: named refusal, never 70 | T3 missing, T3 changed, T4 | 66, 3, 74 (ruled) |
| a discover proposal previews | T5 | 0 |
| reference-free previews unchanged | T6, R1 | byte-identical to B's golden, including a `.json`-named model |
| a reference changed after preview | T7 | apply 3, model unchanged |
| every load site binds | R3 (two tests) | 2 binds at preview, 9 through apply and finalize; finalize 66, then 0 |
| a candidate cannot change its references | R2 | 3, before binding |

## Adversarial review

One local reviewer agent read the diff against B. **One reviewer is one
reviewer.** It found no blocking defect: nothing it tried exited 70 through the
binder. It ran over 25 damaged-reference cases (directories, fifos, unreadable
files, dangling links, escaping paths, oversized files) and found each a named
exit.

**What it found, each reproduced first:**
- **Fixed:**
  - R1 (completeness): `.json`-named reference-free models changed outcome.
  - R2 (hardening): a tampered candidate was bound before the replay check.
  - R3 (completeness): five load sites had no failing case.
  - R6 (docs): the contract sentence named only three outcomes.
- **Kept:** R4 (hardening), a binder defect reported as 3, for parity with
  `load_model`.
- **Deferred:** R5 (completeness), invalid candidate YAML exits 70 on B and now,
  as IK4-Q2-Q2.

The regressions for R1 and R2 fail on the reviewed code, and the R3 tests fail
on the reviewer's mutant (`evidence/IK4-Q2/regressions-red.txt`). The report and
disposition are in
[phase-IK4-Q2-agent-review.md](notes/phase-IK4-Q2-agent-review.md).

## Refactoring review

**Seen, deferred:** a load-then-bind helper. Five homes now load model bytes and
then bind references at the model's directory:
- evolve's `_load_model_bytes`;
- `discover.service._bind_references`;
- `api.py`;
- `export/lean_io.py` and `export/pyrel_rules.py`.

`load_model`'s own no-follow path does the same internally. One
`gnd.model.load_model_bytes_bound(data, source, root)` would give them one
wrapping rule, which is where R4 lives. It touches five consumers outside this
phase's scope, so it is open question **IK4-Q2-R1**, targeted at the milestone
close.

**None needed** inside evolve. The fix removed two duplicate temp-file loaders
and left one.

## Boundary — what this phase does NOT establish

- **A binder defect is reported as 3, not 70** (review R4). This is parity with
  `load_model`, which wraps every binding failure the same way.
- **A `.json`-named model is still parsed as YAML by evolve.** So evolve can
  publish YAML text into a `.json` model, which `gnd validate` then refuses.
  This is B's behaviour, kept on purpose (IK4-Q2-Q1).
- **Invalid YAML in a candidate exits 70**, as on B (IK4-Q2-Q2).
- **IK5's `references` export refusal stays** (D3).
- **Evolve operations cannot edit `reference_populations`;** none exist, and R2
  refuses a candidate that changes them.

## Open questions

| ID | Question | Proposed | Owner |
|---|---|---|---|
| IK4-Q2-Q1 | Should evolve parse a `.json`-named model as strict JSON, as `gnd validate` does? That would refuse what B accepts: YAML text in a `.json` model, or a YAML candidate for one. | yes, with a named refusal and a test, at milestone close | owner |
| IK4-Q2-Q2 | Invalid candidate YAML exits 70; catch ruamel's `YAMLError` as 3 | yes, with IK4-Q3 (YAML in evolve) | owner |
| IK4-Q2-R1 | One load-then-bind helper for the five homes | milestone close | owner |

## Refuted premises

- **"Reference-free outcomes are unchanged" by moving the load to the workspace
  path (spec §5).** False for `.json` names: the parser is chosen by suffix.
  Repaired by keeping B's parse (R1).
- **"T2 covers apply, publish and finalize" (spec §8 branch walk).** A mutant
  that bound only the current model passed all eight tests. Repaired by R3's
  tests.
- **"A missing or linked reference exits 3" (spec §5, §8).** Evolve already
  names those classes 66 and 74. Ruled by the owner (spec §15).

## Size

`git diff --stat 8f89af4 -- src tests`: 5 files, 693 insertions, 21 deletions.
`src/gnd/evolve/service.py` accounts for 64 insertions and 20 deletions, and the
contract for a few lines. The rest are tests and the 376-line golden preview.
