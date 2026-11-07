---
milestone: rule-check-adoption
station: milestone-close
skill: "n/a -- repository development under process-milestone auto=false, not a gnd-solve station over a domain model"
scope: rc-close
date: 2026-11-07
source_base: f4ce6992
gate:
  command: "~/close-shards/close-shards.sh <run> <sha> on beast-3: the full default lane, six round-robin shards, at the merge base 508d6bec and at the closing tree dfce332e"
  exit: "1 (the 2 pre-existing uv-pin errors only)"
  output: "closing tree dfce332e: 17750 passed, 2 errors; merge base 508d6bec: 17566 passed, 4 failed, 2 errors; no failure at the close that the merge base lacks"
  note: >-
    Plan section 9's close row: the full suite against the merge-base record.
    RC1's own merge-base record (508d6bec, 119 failed and 5 errors) was taken
    with uv missing from the shards' PATH; it was rerun here with the fixed
    script. Main also merged unrelated PRs 102, 105 and 106 in that range,
    so the comparison is of the observed failing-test sets, not of the
    milestone's commits alone.
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request"
  reason: "not selected at this close; the broad historical lanes are outside the milestone's impact closure"
evidence:
  - path: .gnd-planning/milestones/rule-check-adoption/notes/rule-check-adoption-plan.md
    sha256: 258c631ffd8f85f8859d639327501838590d2e3d071d24448bbc6737829f6acc
  - path: .gnd-planning/milestones/rule-check-adoption/006-phase-RC1.md
    sha256: eecf804df0e2b5daf6a1aedea43cc0122aa21d6940b830167599dff6dd2793b8
  - path: .gnd-planning/milestones/rule-check-adoption/007-phase-RC2.md
    sha256: 476fc0c1668e8f61276547c2a5df56122a6caf4e8103593f6589edbda5fc0fea
  - path: .gnd-planning/milestones/rule-check-adoption/008-phase-RC3.md
    sha256: 9e355a314a822a20e395e5c22f5f137e071ce2576b28aba002795a4620f41796
  - path: .gnd-planning/milestones/rule-check-adoption/009-phase-RC4.md
    sha256: fd375437b7e490a08b68ef39c1d05bf4e2d4f9b40057769d4ecb6790bae7f876
  - path: .gnd-planning/milestones/rule-check-adoption/010-phase-RC5.md
    sha256: e019564042fc2942566d6fe635ca25500f9cdd03a93d7360b2d8ef78bed294ac
  - path: .gnd-planning/milestones/rule-check-adoption/011-phase-RC6.md
    sha256: 609dbc880ae9f1af5ead2589aafbf93611c358693c591f0b3306c67fd4a9ba74
  - path: .gnd-planning/milestones/rule-check-adoption/notes/close-codex-review.md
    sha256: 0700df3e85187dcc04670bcdbbdb33b5e4af9a6638c6cf9043d91163b0cceb4f
  - path: dev/components/COMPONENTS.md
    sha256: 7999f9a37db537d0c9bf5f122ee2083d5caea97dfecbcb8799586adf83f52ec9
  - path: tests/test_development_scaffold.py
    sha256: f09af3a54b1dfae6859657b593280fa67e216592677cbebb29de2376778300ea
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/close/full-suite-mergebase-508d6bec.txt
    sha256: ff8fe9cf28d39e94a88e082fc4c905628cbb563cf01b0e1ca062d2e1498f2db5
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/close/full-suite-close-dfce332e.txt
    sha256: 3ae4baddfa0af5e2f3a6596583433c4f20189cc61d802832e2f683803650d0eb
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/close/full-suite-main-f4ce6992.txt
    sha256: 021517227da34ab6391b45f4009ab759258241dbde3f2a7158905f6ecdbe341c
---

# Claim

All six phases of rule-check-adoption (RC1-RC6) are on main, each with an
owner-approved spec, a record with verbatim focused-gate output, one
independent reviewer and an owner-merged PR (101, 103, 107, 108, 109, 110).
Completion predicates 1-6 hold on main by the evidence the phase records
bind, predicate 7 by those records and this sweep. The close's full suite
found one regression on main (a retained review note's quoted links),
fixed here in dfce332e; at the closing tree the full default lane
fails only the two pre-existing uv-pin errors, a strict subset of the
merge base's failures.

## Phases

| Phase | Record | Focused gate | Review (one reviewer, Codex) | PR |
|---|---|---|---|---|
| RC1 | [006](006-phase-RC1.md) | 360 passed | `block`, 3 findings, all fixed | 101 |
| RC2 | [007](007-phase-RC2.md) | 120 passed | `block`, 4 findings: 3 fixed, 1 test gap closed | 103 |
| RC3 | [008](008-phase-RC3.md) | 124 passed | `revise`, 3 findings, all fixed | 107 |
| RC4 | [009](009-phase-RC4.md) | 150 passed | `revise`, 2 test gaps, closed | 108 |
| RC5 | [010](010-phase-RC5.md) | 82 passed | `revise`, 6 findings, 4 fixed, 1 no defect, 1 deferred (issue 115) | 109 |
| RC6 | [011](011-phase-RC6.md) | 166 passed | `revise`, 15 findings, 14 fixed, D12 kept (below) | 110 |

## Completion predicates

| # | Predicate (plan) | Evidence | Holds |
|---|---|---|---|
| 1 | `--rule-ids` gives version 15 with `address`, `addressing`, `remedy`; other models refused by rule id; existing variants keep their bytes | RC1 corpus and gate; every phase's full suite against its base | yes |
| 2 | `acyclic` lists every in-group pair; a disjoint cycle leaves existing rows unchanged | RC2 corpus (C1-C4), O21 fixture | yes, for asserted rings; a ring over an exact-term derived fact type under `--rule-ids` is untested (sweep) |
| 3 | `--baseline` marks new/standing, bands on new only, refuses the claim on ill-formed or undecided runs; derivation models refused | RC3 corpus and gate; review B1-B3 | yes |
| 4 | `--allow-vacuous` exits 0 when vacuous is the only shortfall, lists them, records the option | RC4 corpus, T1 truth table | yes |
| 5 | a source for deterministic tool output | RC5 corpus (`tool-output`, `producer`) | yes |
| 6 | documented end to end, worked example under a named test | RC6: how-to under `tests/test_documentation_tutorials.py` | yes |
| 7 | approved spec, verbatim focused gate and independent review per phase; this record disposes every open question | the six records; the sweep below | yes |

## Gate output (verbatim)

Full default lane, six shards on beast-3, both runs at once with the same
script (`~/.local/bin` on PATH):

    merge base 508d6bec: 17566 passed, 4 failed, 2 errors; shards exit 0,0,0,1,1,0
    main f4ce6992:       17749 passed, 1 failed, 2 errors (run alone, before the fix)
    closing dfce332e:    17750 passed, 0 failed, 2 errors; shards exit 0,0,0,1,0,0
    comm -13 mergebase.fail closetree.fail: empty (no new failure)
    comm -23 mergebase.fail closetree.fail: 4 lines
    sha256 of the closing failing-id list: 8261732b…9c20a

The closing tree's failures are the two `tests/test_public_optional.py`
uv-version pins. Every phase base since RC2 had those two errors; the RC3,
RC4 and RC6 bases also had one intermittent session-driver timing failure
(issue 117), so their full lists differ from the closing one, and the
closing list's sha256 equals RC2's and RC5's.
The merge base's four extra failures are not this milestone's: three
`tests/test_doctor_uninstall.py` discovery-root tests, fixed on main by
69218c2c ("pin the vendored components skill in the discovery-root
tests", merged with PR 102), and the session-driver timing flake (issue
117).

At main f4ce6992 the one failure was
`tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap`:
the retained RC6 review note quotes two `cli.md` links that do not resolve
from `notes/`. Fixed in dfce332e (refuted premise below):

    uv run pytest -q tests/test_development_scaffold.py -p no:cacheprovider
    before: 1 failed, 56 passed, 1 deselected in 13.84s
    after:  57 passed, 1 deselected in 14.29s

Component index, whole milestone: `python3 scripts/components_index.py
changed --base 508d6bec --strict` → `271 file(s) differ; 0 to fix, 0
warning(s), 22 to reread`, exit 0.

Evidence: `evidence/close/full-suite-*.txt`.

## Close review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only),
selected by the owner in place of the plan's panel bar, over this record's
draft, the amended plan, the six phase records, the README and the code.
Disposition `revise`, 7 findings (K1, K2 blocking; K3, K4 hardening; K5-K7
completeness), all accurate. K1 is qualified in predicate 2 and deferred to
issue 119; K2's 22 index entries were reread, 6 corrected; K3-K7 are fixed
in this record, the plan and the README. Retained verbatim with the triage
in [close-codex-review.md](notes/close-codex-review.md). The corrected record
was not re-reviewed.

## Open-questions sweep

| Item | Raised | Disposition |
|---|---|---|
| Size overruns RC1, RC2, RC5, RC6 | records 006, 007, 010, 011 | resolved: owner accepted each ("Accept overrun"; RC6 "Accept, open PR") |
| D12: the `--allow-vacuous` closing line prints even when a run exits 1 | RC6 review | **accepted residual, owner ruling 2026-11-06** ("Keep, docs describe it"): the reference and how-to say the exit code is the verdict |
| Model digest is `repr()`-based | 006 | deferred: issue 111 |
| Text output prints projected JSON for redaction/temporal models | 006 | deferred: issue 112 |
| Version-7 report fails its schema on `term:*` derivations (O29, RC-D17) | plan, 006 | deferred: issue 113 (RC-D17's ruling) |
| Unused cycle helpers in `checker/_core.py` | 007 (F2) | deferred: issue 114 |
| `Population.model_copy` bypasses the producer invariant (T5) | 010 | deferred: issue 115 |
| Reference binder drops `label` (F2) | 010 | deferred: issue 116 |
| Session-driver and scope-walk timing tests under parallel load | 008, 011, this close | deferred: issue 117 |
| Full-suite environment reds (uv missing from PATH) | 006 | resolved: the shard script puts `~/.local/bin` on PATH from RC2 on; this close reran RC1's merge base with it |
| Component index drift | 007 (I5) | resolved for this milestone: RC2-RC6 each recorded `0 to fix`, and at this close `components_index.py changed --base 508d6bec --strict` gives `271 file(s) differ; 0 to fix, 0 warning(s), 22 to reread`, exit 0; all 22 were reread at this close against the milestone's diff: 16 accurate, 6 stale and corrected in `dev/components/COMPONENTS.md` (close review K2), index regenerated, `--check` exit 0, and the check then lists the 16 accurate entries only (`0 to fix, 0 warning(s), 16 to reread`); the upstream search limits are tracked as vasiloglou/dev-tools#1 |
| Exact-term derived rings under version 15 | 007 | moot under `--baseline`, which refuses structured-derivation models (RC-D11); under `--rule-ids` alone such a model is accepted (RC3-C3b) and its extent is untested: a ref with no group found keeps its version-7 row (`correspondence.acyclic_extents`), but a mismatch between the two views has no case. Deferred: issue 119 (owner ruling 2026-11-07, "File an issue") |
| RC-D16: r6 unreviewed | plan | retired: the owner approved r6 as written ([005](005-plan.md)) |
| Requests GR-D1, D2, D3, D5, D6 (issues 92, 93, 94, 96, 97) | milestone scope | resolved: the close PR closes them on merge (owner ruling 2026-11-06) |
| GR-D4 (issue 95) | milestone scope | out of scope: its own milestone |

## Plan repair

Three refuted premises named plan repairs: O17 (three SCC implementations,
not two, in its table row and in the implementability sweep), §3's home for the baseline comparison (`src/gnd/baseline.py`), and
RC5-C2's projection clause (a pinned subset). They are applied as plan §15,
keeping the prior wording, under this close's ruling; the amended plan is
bound above by sha256. RC1's refuted premise (spec M9) and RC6's (spec I1)
were spec-level and need no plan change.

## Refuted premises

- RC6's record said the review fixes in 0a46d576 "change only Markdown and
  the SVG, which V2 and V3 cover", so the earlier full run still applied. A
  Python test reads every Markdown file's links
  (`tests/test_development_scaffold.py`), and the retained review note,
  added in 0a46d576, failed it on main. Fixed in dfce332e by registering
  the two quoted links, as for the IL6 review; 1 failed before, 57 passed
  after.

## Boundary: what this close does NOT establish

- Each phase had one reviewer; the plan's six-seat panel ran only over plan
  r2. The close had
  one reviewer too, and the corrected record was not re-reviewed.
- The broad lanes (`slow_cadence`) did not run.
- The caller's own project (209 components) was not checked here; the
  synthetic O21 fixture and the how-to example stand in for it.
- Merge, and the closing of issues 92, 93, 94, 96 and 97, are the owner's.

## Owner rulings at the close

- Close review instrument: "One reviewer (Codex)" (2026-11-06), waiving the
  plan's panel bar for the close, as RC-D0 did for r3.
- D12: "Keep, docs describe it".
- Follow-ups: "File all seven" (issues 111-117); K1: "File an issue" (issue 119).
- Requests: "Close on merge".
