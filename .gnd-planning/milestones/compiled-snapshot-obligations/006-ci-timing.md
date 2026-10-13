---
milestone: compiled-snapshot-obligations
station: ci-timing
skill: n/a -- local CI measurement hardening
scope: ci-timing
date: 2026-10-13
gate:
  command: uv run pytest -q -raP tests/test_guarded_corpus.py tests/test_guarded_timing_batches.py --tb=short
  exit: 0
  output: "103 passed in 28.39s; 103 passed in 26.35s"
---

# Claim

The complete guarded test group passes locally on Python 3.11 and 3.13 using
fixed consecutive batches. Each of nine retained paired samples is the mean of
five checks, with ten additional warmup checks: all 100 checks are executed.

## Reproduction and accepted change

Two retained GitHub macOS logs had individually sampled stability failures
(relative MAD up to 21.5%) while their scaling ratios stayed inside 2.2. Both
local individual-sample gates passed. No new cloud run was explicitly launched:
these were automatic PR pushes before the owner's local-only instruction.
Cloud logs are diagnosis inputs, not acceptance gates for this record.

Fixed-batch averaging keeps every duration, normal garbage collection, the
individual two-second ceiling, 45-second total deadline, nine paired samples,
10% relative-MAD threshold, 2.2 scaling ratio and 0.2-second floor. Stability now
measures batch means; this changes statistical sensitivity and is recorded as a
measurement-method change, not an unchanged statistical experiment. There is no
retry-until-pass, selected sample disposal or disabled check.

The batch-inclusion control reproduced red before implementation (one failed,
one passed). An asymmetric sequence distinguishes the arithmetic mean from a
median or discarded slow observation. A single 2.1-second check is rejected even
when its batch average would pass. Existing every-report controls were updated
from 20 to 100 calls and still kill invalid verdicts/counts at first, later and
last call indexes 0, 10 and 99.

## Gate output

    103 passed in 28.39s
    103 passed in 26.35s
    All checks passed!

Real measured scaling passes with the complete deterministic guard group on
both Python versions. The asymmetric fixture and report-order controls are included in these final
gates and separately passed together (3 passed in 0.11s). Median substitution
is rejected by the asymmetric fixture.

## Review and refactoring

One local reader reviewed the method and controls and found no blocker; one
reviewer is one reviewer. Its asymmetric-fixture suggestion was applied and
follow-up opinion is retained in notes/ci-timing-review-one.md. No production
refactor is needed; this repair changes only the bounded test instrument.

## Boundary and open questions

The owner requires local-only CI. No additional cloud execution is authorized;
active PR cloud work was canceled. Subsequent pushes must honor this restriction.
Final full local regressions and installed acceptance are still in flight at
runtime commit 45d0ae3 and are separately recorded when complete. This gate does
not establish green full CI, Linux equivalence, certification, release or merge.
Existing app/admission carryovers retain their named owners.

## Artifact identities
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/guarded-batch-red.log: 0c91d1c0b8e1f6ce9ee816a32a3411450b401c0f921905cc20f8db0719cd7381
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/guarded-batched-final-3.11.log: 5f3849d4ad6861bd4ea8b062b78af3d3275d8315be228db9f0c14f5032f23294
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/guarded-batched-final-3.13.log: aa45d5a150a6c3ded7480c10914ef52b7bb6a2d59a3e00405bc5dba24c55852d
- .gnd-planning/milestones/compiled-snapshot-obligations/notes/ci-timing-review-one.md: 623d4bb09ee0ed63a5f2597456b0ef529eb23a41910f9c2b815a398e1a2acb08
- tests/test_guarded_corpus.py: 9f278d268373644928ed415a989bd0851e6c5a0c3ad395e5ed70525c1bd4dc5b
- tests/test_guarded_timing_batches.py: 184a4b0defab2b3aa6156d1ca56bfa88414dafcccd7091186a7dc3d13f700ff2
