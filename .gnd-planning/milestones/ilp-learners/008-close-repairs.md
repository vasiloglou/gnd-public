---
milestone: ilp-learners
station: close-part-A
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: IL-close
date: 2026-10-29
gate:
  command: "uv run pytest -q -p no:randomly <IL6's gate files plus tests/test_il_close.py, evidence/IL-close/gate-files.txt>"
  exit: 0
  output: "1281 passed, 24 deselected in 273.13s (0:04:33)"
  note: >-
    The spec §9 gate, run on the final bytes after the review fixes (cbc6432;
    a ruff import-order fix followed, no behaviour). T9 ran on the same bytes:
    tools/check_installed_docs.py, both wheel origins, 229 tutorial blocks
    each. Ruff clean on the changed Python files.
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection or separately configured CI"
  reason: "outside part A's impact closure; the reduced v6.3 selection was run"
evidence:
  - path: .gnd-planning/milestones/ilp-learners/notes/phase-IL-close-spec.md
    sha256: f768cdd59f86b4808b1966d63a03bbe0c7a699f7fd0dca50da7d312ac4c98b22
  - path: .gnd-planning/milestones/ilp-learners/notes/phase-IL-close-agent-review.md
    sha256: ee3d7dbb9f2387ee9d16474b19b787ad6b265c2d85fbba2e7a9fbf2fcadce44f
  - path: tests/fixtures/ilp_learners/close/cases.json
    sha256: 2d92a8e6aa1e5caf7ebbbbab10b816e08c8c93d48270292fcfb16f04ebc0cb52
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL-close/red.txt
    sha256: 649d91e602ac84613060c00c44a5b5a67f8a6994881efa62f744ebb02c0a3d27
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL-close/review-red.txt
    sha256: c908be57fef3e468a2751f2a38046b7d768fa7e6cd289b0de4e74fde5fa38b03
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL-close/final-gate.txt
    sha256: b84f3ce36d91c842a5292a725708b1dffbcb3be7678e51897f273b6ed657c31d
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL-close/gate-files.txt
    sha256: 2c2d1484475e115b4481cdbb0b998dc48b1003d333777b58c774b5f235ec13ce
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL-close/installed.txt
    sha256: 5727d7af13f4503d50758b6a9a75eb1e9905da9959f7a1ccdceebdb4bea8b29b
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL-close/installed-results.json
    sha256: 9a70721b2fb76dcd85cfcbddce38f9538d30efe828704a24102ff4b4a58c0931
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL-close/rederive.py
    sha256: 034a136c8d2ea1a66e35e226686bf790a7b5d0775e7ce7e8f0ce4828fe65e503
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL-close/dynamic-query-successor.json
    sha256: ca7bcc5079fc3abf096981bc5ea4a16af248e04c114ddb0d473d1a7f037cfbe5
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-1/reported.json
    sha256: 1d9a504318a0bf210b0dc9de6b71d0fb4b47803b5e3af2c11231d193e382a712
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-1/reported-r0.json
    sha256: 365eda612c7b62ce1e579c21533fb4793ad93ea2c9d35a2bb5d8497a94eca8c3
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-2/reported.json
    sha256: 2dc09dd494a633d6ba7fe48aae73dbfa68ec2e9dddee6c2e49f3dd103324e871
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-2/reported-r0.json
    sha256: 366cefd20acc5f26bafb2c7582011db31bfa04695da4c69253582e3373128c74
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-2/proposal.json
    sha256: 765a4b04256ba97b17994fead270993b72face78199524128c8b85a8dc849073
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-2/proposal-r0.json
    sha256: c5aae4920d8b52c643244d854f5b3608be0a674395a23583b518a4c652232822
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-2/import-report.json
    sha256: f50ee9c159fa20f470838a5614c0443a1a98be6ab3800e35b3f83b6b9104fc5b
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-2/import-report-r0.json
    sha256: 347e9b6bf0d7c1109882a23120d3fcb27348ffdb4d855269f1bd82779ac96dbc
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL4/run_amie.py
    sha256: 748dbbb538d6f7d659e9eebff4aed4e063b957824e86168afb0d7216de447c63
  - path: tests/fixtures/ilp_learners/il6/walk-goldens.json
    sha256: 2c408c83b513ba81bf6902538113ec222df065845b0e2bc5930032383a93c76f
  - path: tests/fixtures/ilp_learners/il6/comparison.json
    sha256: 6e32bc0a837846ff80d829f14fa7542c76ce811fd3e666bd9775914c6cc3a45c
---

# IL-close part A -- the close repairs

**One reviewer is one reviewer.** The adversarial review of this part was a
single agent's reading of the diff; it is evidence, not a proof. The
milestone's four-reviewer close review is part D, still to come.

## What shipped

Every question the owner ruled "fix" on 2026-10-29 (close plan, Part A), under
spec r1, approved the same day with every proposed ruling, ILC-D1 to ILC-D9,
corpus-first:

| Row | Fix | Cases |
|---|---|---|
| IL4-Q1 | The AMIE export spells a subtype hierarchy by its **family**, the least top-type id of its reference-inheriting subtype component, so a join through a subtype counts as the checker does. AMIE adapter version 2 | C1a–e, R1, R2 |
| IL4-Q2 | `gnd-mined-run/1` requires `facts_sha256`, the digest of the `amie/facts.tsv` the miner read; other facts, or none, are refused `facts-mismatch`, after `population-mismatch` | C2a–c, R4, R6 |
| IL6-Q2 | `tools/ilp_comparison.py` exits 2 and names a rule, or rules, it cannot count | C3, R5 |
| IL1-Q1 | An infix comparison of two variables is a join for check 9b | C4a–c |
| IL2-Q3 | An ILASP constant outside the rendered thresholds is refused `off-threshold`, through the registry hook `Learner.vet` | C5a–c, R3 |
| IL1-Q4 | `extract_program` keeps every rule line of the solution block | C6a–b |
| IL2-Q1 | A bare `true`/`false` in Popper text is a boolean | C7 |
| IL1-Q5, IL6-Q1 | The missing tests: the join check's pair count, a subtype closure, refusals per bridge section | C8a–c |
| IL3-Q2, IL4-Q3 | `ilp_popper.threshold_rows` and `ilp.export_value` are public; the private names are gone | C9 |

**The retained runs.** No learner ran (IL-R9).
`evidence/IL-close/rederive.py` re-derived both AMIE run records: each gains
the digest of its own retained `facts.tsv`, and the original is kept as
`reported-r0.json`. Invocation 2's `proposal.json` and `import-report.json`
move only in the run record's digest; their originals are kept as `-r0`. The
shipped staffing copies equal the derived records. `run_amie.py` writes the
field for a future run.

**What did not move** (C10, C11): `comparison.json` (all 8 rows, byte-equal
to main), every IK5 and IK6 golden, the Popper, ILASP, rules and llm export
digests, the refunds walk outputs, and every other run's retained outcome.

## Gate output (verbatim)

```
$ uv run pytest -q -p no:randomly $(cat .gnd-planning/milestones/ilp-learners/evidence/IL-close/gate-files.txt)
1281 passed, 24 deselected in 273.13s (0:04:33)
```

Exit 0. T9, `uv run python tools/check_installed_docs.py --out <scratch>`:
"229 tutorial blocks passed", "Both installed wheel origins passed the
documented learning paths." (`evidence/IL-close/installed.txt`). The full
`uv run pytest -q` was not run.

## Criteria

| Test | Result |
|---|---|
| Red corpus before code: 19 failed, 12 passed, each failure its own defect (`evidence/IL-close/red.txt`) | recorded |
| C1–C9 | pass |
| C10 every retained run replays (IL1–IL6 replay tests, in the gate) | pass |
| C11 the comparison tool exits 0; the walk passes its 12 blocks | pass |
| T8 RF1 pins, RF5, layering, arch, RF6 (an IL-close census successor), built inventory, schema sync, API pins | pass (in the gate) |
| T9 both wheel origins | pass |

## Review

`notes/phase-IL-close-agent-review.md`, retained (scratch prefix scrubbed).
1 blocking, 4 hardening, 2 completeness; every finding reproduced and fixed,
each with a regression shown red before its fix (`evidence/IL-close/review-red.txt`).

| # | Finding | Class | Disposition |
|---|---|---|---|
| 1 | An own-reference subtype shared its supertype's family; Integer `1` and String `"1"` met and the import exited 70 | blocking | fixed, R1 (ILC-F8) |
| 2 | A cyclic hierarchy fell back to per-type names | hardening | fixed, R2 |
| 3 | An undeclared ILASP comparison was named `off-threshold` | hardening | fixed, R3 |
| 4 | The re-render could refuse `no-relations` ahead of `facts-mismatch` | hardening | fixed, R4 |
| 5 | The comparison tool tracebacked with exit 1 on unparsable rules | hardening | fixed, R5 |
| 6 | `facts-mismatch`'s order was untested | completeness | fixed, R6 (red against the reviewer's mutant) |
| 7 | The page said facts are checked "before any rule is read" | completeness | fixed |

## Refactoring review

**None executed.** The part touched one function in each of six bridge
modules, the tool and the evidence; each change is a local repair whose
neighbours were already shaped for it (the registry took a hook rather than a
learner name; the join check took a second loop over the sites it already
built). One structural point is deferred:

- **The mined import renders the facts twice.** The `facts-mismatch` check
  calls `ilp_amie.render`, then the import builds the relation table and the
  spelled pairs again for the count. One shared pass would serve both. The
  cost is bounded by the export's fact cap, so it is left for the milestone
  that owns the bridge's performance (IL-close-Q1).

## Boundary -- what this part does NOT establish

- **That an own-reference subtype's joins are counted.** They are refused
  `support-mismatch`, as before IL-close: a false refusal, never an admission.
  Whether raw values identify entities across such a subtype is a modelling
  question.
- **Clause order of refusals for ILASP.** The threshold check runs over every
  clause before the rewrite (§6.5), so a later clause's `off-threshold`
  outranks an earlier clause's rewrite refusal. Both refuse the set.
- **Any learner behaviour.** No learner ran; the retained runs were re-derived.
- **The milestone's close.** Parts B to E (plan repairs, the question sweep,
  the four-reviewer review, the close record) follow.

## Open questions

| Id | Question | Owner | Target |
|---|---|---|---|
| ILC-F5 | IL1's test r5 pinned a bare `true` at a string role as the string; under IL2-Q1 it is the boolean. Accept the moved assertion? | owner | **accepted 2026-10-29** |
| ILC-F6 | Moves beyond spec §8: the IL4 `export.json` goldens (`adapter_version` 2), invocation 2's `import-report.json`, walk block 10 (not 9), T9's adapter-version assertion, `run_amie.py`. Accept? | owner | **accepted 2026-10-29** |
| IL-close-Q1 | Share one rendering pass between `facts-mismatch` and the count | owner | later milestone |

**Owner ruling, 2026-10-29,** quoted: "I accept ILC-F5 and ILC-F6 as
recorded. Continue with close parts B to E." Recorded after this record's
commit `d6c70c7`; the rest of the record is unchanged.

## Refuted premises

1. **"Siblings of one type are disjoint"** (spec §6.1, C1d): they share that
   type and pass 9b (ILC-F1); C1d now uses types of one family with no common
   ancestor, and C1e pins that siblings count.
2. **"An own-reference subtype compared by raw value agrees with the checker"**
   (spec §6.1 Boundary): the family spelling erased the primitive (ILC-F8,
   review 1).
3. **"The Popper boolean fix changes no golden"** (spec §6.7): IL1's r5
   assertion moved (ILC-F5).
4. **"§8 lists everything that moves"**: ILC-F6.
