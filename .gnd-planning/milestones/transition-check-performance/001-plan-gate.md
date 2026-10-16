---
milestone: transition-check-performance
station: plan-gate
skill: start-milestone
scope: plan-gate
date: 2026-10-16
---
# Owner approval of plan r5 and the TP0 spec

On 2026-10-16 the owner was shown the reviewed plan, the TP0 spec and the
recommended rulings for the open decisions. The owner answered "go on with all
of them". This is the owner's own approval (`auto=false`), not a delegation.

| Artifact | SHA-256 | Approved |
|---|---|---|
| `notes/transition-check-performance-plan.md` r5 | `01fae9d8de08d9dc0d6de7dbd1df1ef3b7efcee15e0fe00138f390242a5daca3` | plan |
| `notes/phase-TP0-spec.md` r5 | `2165ada0a123e3e761f4b506f4b1016ff0dacf3bda14fdb6786c275124cc1e3b` | TP0 spec, approval instrument "this prose" |

Rulings given with the approval:

- **D-p1-1:** exit 2 (warnings or vacuity) is **not** a failing pre-check. Only
  exit 1 or a refusal band (≥ 3) blocks minting a receipt.
- **D-p1-2:** TP-D6 is accepted in counter units: `model_index_key_paths` (with
  `model_dumps_other` not increasing), `deepcopy_nodes`, and the workload total
  of `checker_runs` going from 25 to 19.
- **TP0 D1–D8:** accepted as proposed. That covers test-time counters at every
  lookup owner; the driver logic reimplemented and not committed; minimal path
  normalization with separate branch-trace digests; a 120 s hang guard; the
  3.11 and 3.13 interpreters plus the session default; the anonymizing import
  transform (D7); and wrapping the `course` plans with `steps_document` (D8).

**Review basis:** four local readers over r3, then a confirmation round by
readers 2 and 4 over r4, with the stop rule applied
([disposition](notes/plan-review-r1-disposition.md)). The `(p2)` repairs in r5
carry no reader opinion. The owner approved r5's bytes as they stand.

**Not approved here:** specs for TP1 to TP3, each of which has its own owner
gate; merging the pull request; publication.
