# Review brief: the milestone close

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Refute the close of pins-and-review-check. (1) Does each exit predicate in 004-close.md hold, with evidence in the records? (2) Is every open question raised in the plan, the two phase records and the two specs dispositioned in the sweep, and is each disposition honest? (3) Does plan amendment c1 repair every refuted premise and plan-level finding the phases raised, with the prior wording kept? (4) Read the bytes no reviewer has read: PF1's round-2 guard repair (tests/test_inventory_pin_home.py: does it miss a binding, or flag a non-binding?) and PF2's evidence repairs (gen/grade.py and GRADING.md: does every grade follow, does every reported input run?). (5) Does any claim overstate its evidence?

## The change under review

The files below, as they stand at `b34cf3d2689b`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/pins-and-review-check/004-close.md` | `3f5a55846b153032b724fc4d5e4570f9716bdbfb83d3d4a73f08da1bce3e8b9b` |
| `.gnd-planning/milestones/pins-and-review-check/notes/pins-and-review-check-plan.md` | `d0d8480b16260286288d87aabe9271c788d7191ae82f109a7ccb891b8e293171` |
| `.gnd-planning/milestones/pins-and-review-check/001-plan.md` | `2703940b163cba5d9718ca9b824c753303d3e66fa32abb9a204cbad14b8b81a4` |
| `.gnd-planning/milestones/pins-and-review-check/002-phase-PF1.md` | `0496a47620d8506abf2262ec96e685dbfc6694d02369c4f062531202ccc4d9bb` |
| `.gnd-planning/milestones/pins-and-review-check/003-phase-PF2.md` | `854574ba753cbcacae8b6a20a491978d28912e15e8074f2a924f57749d8824b0` |
| `.gnd-planning/milestones/pins-and-review-check/notes/phase-PF1-spec.md` | `465e08f5f33de6fbf235b48823fae63f34ed29d1a17c7069352b1df7fef71062` |
| `.gnd-planning/milestones/pins-and-review-check/notes/phase-PF2-spec.md` | `22a35a72552c6d32ea7a1f6b7dd4801ecc60fa14e7ec605730ae458a323b30cc` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/GRADING.md` | `d2487cacd2320259e47b5ea8178c28af196658e1095ba27df9d860c791b0c9ba` |
| `tests/test_inventory_pin_home.py` | `baa30ed6a5961376f0a0b7c13fe6dd86b15364154e2363f651dc39f1fe581985` |

You may read anything else in the repository that helps you answer.

## Rules

- Read only. Do not edit, create, stage, commit, push or post anything.
- Do not open `.env` files, keys, tokens, `auth.json` or any other credential file, and do
  not print environment variables. If you need one, name it and go on without it.
- A finding names its file and line and the consequence someone would observe. Run what
  you can to show it; where you only read, say so.

## What to return

1. Findings, each with an id (F1, F2, ...), file and line, what is wrong, the observable
   consequence, and how to reproduce it. A finding with no observable consequence is
   style: label it so.
2. What you checked and found true.
3. What you could not check, and why.
4. A last line: `VERDICT: APPROVE` or `VERDICT: CHANGES_REQUESTED`.
