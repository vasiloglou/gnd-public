---
milestone: report-output-fidelity
station: milestone-close
skill: "n/a -- repository development under process-milestone auto=false, not a gnd-solve station over a domain model"
scope: milestone-close
date: 2026-11-09
source_base: 8eb4fe60
gates:
  - command: "~/rof-shards/rof-shards.sh close-8eb4fe60 8eb4fe60 on beast-3: the full default lane, six round-robin shards, at main 8eb4fe60"
    exit: "1 (13 failed, 2 errors; every failure passed on rerun, below)"
    output: "main 8eb4fe60: 18238 passed, 13 failed, 2 errors; the 10 failing only here and the 3 failing in both runs each passed when rerun alone"
    note: >-
      Plan section 9's close row: the full suite against the merge-base
      record (main 12daa5b7). The ROF1 base record
      (evidence/ROF1/full-suite-main-12daa5b7.txt) was taken on the author's
      machine, whose environment fails about 120 tests that pass elsewhere,
      so the same runner also ran 12daa5b7 on beast-3 (next gate) and the
      comparison is between the two beast-3 runs. Main also merged other
      milestones' PRs in that range (rule-check-followups, rule-check-release,
      PRs 135, 137, 142), so the comparison is of the observed failing-test
      sets, not of this milestone's commits alone.
  - command: "~/rof-shards/rof-shards.sh base-12daa5b7 12daa5b7 on beast-3: the same lane at the merge base"
    exit: "1 (14 failed, 2 errors)"
    output: "merge base 12daa5b7: 17805 passed, 14 failed, 2 errors"
  - command: "ruling: owner -- pending (the close ruling over this record and plan section 11)"
    exit: n/a -- ruling
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request"
  reason: "not selected at this close; the broad historical lanes are outside the milestone's impact closure"
evidence:
  - path: .gnd-planning/milestones/report-output-fidelity/notes/report-output-fidelity-plan.md
    sha256: 8fb1869a0b47c0672992b8ea3f50cc2b0449c4f8495993ee83deee53f57148ba
  - path: .gnd-planning/milestones/report-output-fidelity/001-plan.md
    sha256: ad5b883f643c39657d9d0d84e137a316136c4bcf5ea5e6bc4813c46872e84064
  - path: .gnd-planning/milestones/report-output-fidelity/002-phase-ROF1.md
    sha256: 165bdbf19ca5b519e4fe32ea92c8e1f30f8e6de37e75df4e062dc085ace6e3e3
  - path: .gnd-planning/milestones/report-output-fidelity/003-phase-ROF2.md
    sha256: 4a71139b8c3247f6da7b4f8fd2b1decafd1ac121503b00e25fce1ad1b83c4a9f
  - path: .gnd-planning/milestones/report-output-fidelity/004-phase-ROF3.md
    sha256: b63d02a2ffd9b4be30d4c59f20669d4fbf65108c4547a1d327d1266b56cf50c1
  - path: .gnd-planning/milestones/report-output-fidelity/005-phase-ROF4.md
    sha256: 9519c9f8fad14874c566b668c35589daeb94adee24bb07b64818d4ae3482c315
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/ROF1/full-suite-main-12daa5b7.txt
    sha256: 5b1573a294c053260bdfd2bd85caae6fe7e188f325f6fd0ce85e7bbf4b6f6197
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/close/full-suite-close-8eb4fe60.txt
    sha256: de49145f2380b3dcff2d2450395552ac654222c320f0a394442f55cda7ad96e5
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/close/full-suite-base-12daa5b7.txt
    sha256: e4514abee5889ed230e08e512f7c58c5698a1a016e362058cac0848a41b59c77
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/close/codex-review.md
    sha256: fc6974138edf525ccb548c0a109355052aee2022a1b6c9945c6c72709b51c3cc
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/close/review-prompt.txt
    sha256: 754052f3d8364ef9a9a1a017309b2b0c1163113208673cdddd36125b8c3d1f60
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/close/issue-states.txt
    sha256: fe5be88b4608cb80f2f1b116ac93c0b1e093e4dcbb18aaae1d987290c375d806
---

# Claim

All four delivered phases of report-output-fidelity (ROF1-ROF4) are on
main. Each has an owner-approved spec, a record with verbatim focused-gate
output, one independent reviewer, and a PR the owner merged (124, 127, 132,
138). ROF5 is withdrawn by the owner's ruling R1 (2026-11-09): reports keep
the legacy `model_digest`.

Both issues are closed as completed, by the owner:
- 112 on 2026-11-08, after ROF1 and ROF2 merged.
- 111 on 2026-11-09, with the report-side gap stated on the issue.

Completion predicates 1, 2, 3 and the phase half of 5 hold by the evidence
the phase records bind, with the qualifications in the table below.
Predicate 3's compatibility clause rests at main 8eb4fe60 on the close
runs; every failure there passed on rerun. Predicate 4's issue-111 clause and predicate 5's issue
clauses hold only as amended in plan section 11 (rows 1-3, the owner's
ruling R1). Section 11 also records four places where an owner-approved
phase spec departed from r3's wording (rows 4-7). All of section 11 takes
effect with the close ruling.

**Full suite.** The default lane ran on beast-3, at main 8eb4fe60 and at the
merge base 12daa5b7. Both runs were on a loaded host and each failed 13-14
tests from the same families: process-timeout, process-kill, session and
session-pin tests. Plus the two uv-pin errors present at every base. The
failing sets differ test by test. Every test that failed at 8eb4fe60 passed
when rerun alone at 8eb4fe60: the 10 that failed only there, and the 3 that
failed in both runs. No failure points at this milestone's files.

The close review has run (one Codex reviewer, by the owner's ruling) and
both close runs are in. The owner's close ruling has not been given (see
"What the close still needs").

## Phases

| Phase | Issue | Record | Focused gate | Review (one reviewer, Codex) | PR, merge |
|---|---|---|---|---|---|
| ROF1 | 112 (check, validate) | [002](002-phase-ROF1.md) | 525 passed | `block`, 8 findings: 7 applied, P6's remedy not taken (E34) | 124, 4f3afc9e |
| ROF2 | 112 (walk, admission, verify) | [003](003-phase-ROF2.md) | 1371 passed | `block`, 6 findings: P1, P2, P5, P6 applied; P3, P4 declined (spec I8) | 127, 8f9781b9 |
| ROF3 | 111 (canonical identity, `gnd validate --identity`) | [004](004-phase-ROF3.md) | 3 failed, 2970 passed (the 3 are the load-sensitive checker timing tests; 3 passed alone) | `block`, 8 findings, all applied or argued (spec I7) | 132, 6058c674 |
| ROF4 | 111 (accept either identity) | [005](005-phase-ROF4.md) | 79 passed, 1 deselected (ROF4 tests); full suite equal to its base | `block`, 7 findings: P1-P4, P6, P7 fixed; P5 accepted as a limit | 138, db762f29 |
| ROF5 | 111 (report emission) | none | -- | -- | withdrawn (R1) |

## Completion predicates

| # | Predicate (plan) | Evidence | Holds |
|---|---|---|---|
| 1 | Text output of `check`, `validate`, `transition` (full and plan) and export verification prints the plain layout for a model with a redaction policy or temporal terms. The body is rendered from the projected tree only. A canary secret never appears. The plan excepts `validate --trace` and `validate --document`, which print from the model. | ROF1 and ROF2 corpora, canaries and goldens; ROF1 spec section 6 | yes, with the plan's own exception: `validate --trace` prints the model's structure, and `validate --document` can return early with warnings and issues. Neither prints from the projected tree; both are canary-tested. ROF2's boundary: temporal `--admission` and temporal `verify` are not projected and print plain text, unchanged |
| 2 | A caller outside GND can recompute a model's identity, with one normative home, a shipped producer and a differential test | ROF3: `representation-format.md` subsection, `gnd validate --identity`, T1 over every tracked loadable model (313 at ROF3; the plan's 306 was measured at 12daa5b7), hand-written byte vectors | yes |
| 3 | Every matching site accepts both identities through one helper. Exact-coherence and copy sites stay exact. No recorded digest is rewritten, and pre-milestone artifacts verify. | ROF4: `values.model_identity_matches`, seven sites, the T1 source scan; T10: the 14 executable legacy `steps.json` pins, `recordings/TASK.md` (which quotes the digest and is byte-preserved), and the new canonical example; ROF4's full suite at d83e972c equal to its base | yes for the helper, the sites and the shipped pins (ROF4 evidence). At main 8eb4fe60 (main gained other PRs after d83e972c), the close runs (gates 1 and 2) show no failure attributable to this milestone. Every failure there passed on rerun, and none is in an identity, transition, coverage, measure or witness test. Plan ROF4-C3's "15 ... (executable)" is qualified in section 11, row 7. A generated Pyrel plan refuses a canonical pin by D7. T8, which shows that, needs DuckDB and has not run on the author's machine |
| 4 | D3 honoured: ROF5 withdrawn with its reason, or delivered. Issue 111 stays open unless ROF5 delivers. | R1 (below); evidence/close/issue-states.txt | **as amended (plan section 11, row 1)**: ROF5 is withdrawn with its reason; issue 111 is closed by the owner's ruling, with the gap stated |
| 5 | Approved spec, verbatim focused gate and one independent reviewer per phase. The close disposes every open question and closes 112. 111 closes only if ROF5 delivers. | the four records; the sweep below | the phase half holds. The question sweep is below. **As amended (section 11, row 2)**: the owner closed 112 before this close and 111 under R1 |

## Gate output (verbatim)

Full default lane, six round-robin shards on beast-3 (18 cores; load
average about 40-78 from other jobs during the runs). Retained:
[close](evidence/close/full-suite-close-8eb4fe60.txt),
[base](evidence/close/full-suite-base-12daa5b7.txt).

    main 8eb4fe60:
    shard0: 4253 passed, 85 deselected in 1068.22s (0:17:48)  shard exit=0
    shard1: 1 failed, 2295 passed, 278 deselected in 945.84s (0:15:45)  shard exit=1
    shard2: 2259 passed, 123 deselected, 2 errors in 596.83s (0:09:56)  shard exit=1
    shard3: 4 failed, 3570 passed, 58 deselected, 1 warning in 818.30s (0:13:38)  shard exit=1
    shard4: 2 failed, 2869 passed, 122 deselected in 880.04s (0:14:40)  shard exit=1
    shard5: 6 failed, 2992 passed, 133 deselected in 854.29s (0:14:14)  shard exit=1
    failing list sha256 7886252a7dfd7a4cfee2494e30e59c3d5831ac4e480577ab51d0eb4ff60258cb

    merge base 12daa5b7:
    shard0: 1 failed, 3776 passed, 123 deselected in 991.01s (0:16:31)
    shard1: 3 failed, 2586 passed, 169 deselected in 411.12s (0:06:51)
    shard2: 3461 passed, 95 deselected in 1360.92s (0:22:40)
    shard3: 4 failed, 2635 passed, 228 deselected, 1 warning in 629.72s (0:10:29)
    shard4: 1 failed, 2252 passed, 97 deselected, 2 errors in 1014.48s (0:16:54)
    shard5: 5 failed, 3095 passed, 82 deselected in 1011.16s (0:16:51)
    failing list sha256 440a5dffb017ddfd387daef11cc4e845c0aca7d4322f9d0a60206e6fa45fee96

    comm -23 close.fail base.fail: 10 ids (test_agent_cli 2, test_exp_session_e2e 2,
      test_public_session_derivation 1, test_public_tests_mode_corpus 1,
      test_rf1_agent_cli_pins 1, test_rf1_session_pins 3)
    comm -13 close.fail base.fail: 11 ids (same families, other members)
    comm -12: the 2 test_public_optional uv-pin errors and 3 failures
      (test_agent_cli 2, test_public_constraint_sessions 1)

    rerun at 8eb4fe60, the 10 ids failing only there, one process: 10 passed in 15.67s
    rerun at 8eb4fe60, the 3 FAILED ids common to both runs:        3 passed in 3.65s

Several failures show `PermissionError` from `gnd/process.py:151` or a
timeout outcome (`sigterm` where `sigkill` was expected). Both are the
host's load, not a code path this milestone changed. The comparison is of
the observed failing sets; main also merged other milestones' PRs in that
range. T8 (`pyrel_oracle`) is deselected by the default lane in both runs.

Component index, this close's files:

    python3 scripts/components_index.py changed --base origin/main --strict
    changed against origin/main (8eb4fe6): 8 file(s) differ; 0 to fix, 0 warning(s), 0 to reread

    uv run pytest -q -p no:cacheprovider tests/test_development_scaffold.py
    57 passed, 1 deselected in 23.12s

## Close review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only, prompt on
stdin), selected by the owner ("One Codex reviewer", 2026-11-09). It
reviewed the draft at d38670e9 (`git diff 8eb4fe60 d38670e9`) and returned
`block` with 10 findings:
- K1-K3 blocking;
- K4 and K6-K9 completeness;
- K5 and K10 hardening.

Every finding was reproduced from the cited bytes before it was acted on,
and all 10 were accurate and fixed:
- K1 restates the R1 amendment.
- K2 and K4 add plan section 11 rows 4-7.
- K3 marks predicate 3's main-level claim as resting on the close runs (now filled in).
- K5 corrects the line numbers.
- K6 and K7 add sweep rows and a refuted premise.
- K8 states predicate 1's plan exception.
- K9 lists the runs, which were then pending (now filled in).
- K10 marks the README's older status as history.

The review is retained verbatim with its triage in
[evidence/close/codex-review.md](evidence/close/codex-review.md). The
reviewer could not run the suite. The corrected record was not
re-reviewed.

## Owner rulings recorded at this close

Every quote below was relayed to this session by the session that started
it ("Recent fixes summary"). This session did not see the owner's words
directly.

| ID | Question (as relayed) | Ruling (quoted as relayed) | Date | Effect |
|---|---|---|---|---|
| R1 (D3 re-ask after ROF4) | First, the explanation that ROF5 would emit the canonical identity in reports. Then: "Close #111 now, without ROF5?" | "ok skip it for now", then "Yes, close #111" | 2026-11-09 | No emission in this milestone; ROF5 withdrawn; issue 111 closed as completed by the session that started this one, at 2026-11-09T05:08:59Z. The closing comment states what shipped (PRs 132, 138) and the gap the owner accepted (evidence/close/issue-states.txt). This departs from plan predicate 4 ("Issue 111 stays open as partially addressed unless ROF5 delivers"). It is the owner's ruling, recorded as plan section 11 row 1, as the rule-check-release close recorded RL-D10 |
| Close review instrument | "How should the report-output-fidelity close be reviewed?" | "One Codex reviewer" | 2026-11-09 | One read-only Codex review over this draft (section "Close review"). This waives the project's panel bar for the close, as RF-D0 did for the plan |
| ROF4-O1 | Accept the corrected S1 answer: a canonical-pinned walk report's `transition.model_digest` echoes the pin as the steps supplied it, as the report schema defines | relayed as ruled; the owner's own wording was not relayed | 2026-11-09 | No change. The behaviour is on main in PR 138, which the owner merged at 2026-11-09T03:15:53Z |

## Open-questions sweep

| Item | Raised | Disposition |
|---|---|---|
| ROF1-O1: keep the `[reason: ...]` suffix (answer E34)? | 002 | closed: ruled 2026-11-07, keep the suffix (002) |
| ROF1-O2: the dynamic-query successor list conflicts when a sibling branch also appends | 002 | closed. It did not occur for ROF1. It did occur for ROF4 against FU5 (PR 134). The ROF4 branch merge 0ff79efa resolved it: FU5 is chained first and ROF4's successor names FU5's file (005, "Merge with main") |
| ROF1-O3: 77 `test_public_tests_mode_corpus` failures and four others, on the author's machine only | 002 | retired: environment-specific. On beast-3, `test_public_tests_mode_corpus` failed once at 8eb4fe60 (`experiment-dir-stable`, which passed on rerun) and not at all at 12daa5b7; the 77 failures do not reproduce off the author's machine |
| ROF1 refactoring, not done: `_print_projected_text` served three routes; `render_text_header` raised on an empty list | 002 | closed by ROF2's refactoring (003): `_print_projected_header`, `_projected_preamble` and the walk and verify rows |
| ROF2-O1: should the projected error line add the error type? | 003 | closed: ruled 2026-11-08, leave it to `--format json` (003) |
| ROF2-O2: retire the unused historical bindings `_print_check_verdicts` and `_print_derived_change_summaries` | 003 | **carried**: the shim-retirement phase under RF-D5. Both are still defined on main (`output.py:675` and `:663` respectively) as `gnd.cli` bindings |
| ROF2-O3: PR 127 was stacked on PR 124 | 003 | closed: both merged on 2026-11-08 (4f3afc9e, then 8f9781b9) |
| ROF3-O1: `reference_model_digest` refuses a mutated non-string declaration key | 004 | closed: ruled 2026-11-08, accept the refusal (004) |
| ROF3-O2: the checker timing tests fail under parallel load | 004 | closed by rule-check-followups FU4 (PR 129; issue 117 closed) |
| ROF4-O1: the S1 walk report echoes the supplied pin | 005 | closed: ruled (above) |
| R1: emit the canonical identity in reports (D3 re-ask) | plan D3, 005 | closed: ruled (above); ROF5 withdrawn; plan section 11 |
| Deferred refactor (ROF3, ROF4): three names for the legacy value (`transition.transition_model_identity`, `values.reference_model_digest`, `synth.provenance.validated_model_sha256`), in two spellings; renaming them was ROF4's or later | 004, 005 | **carried**: the phase that retires the legacy identity (plan section 2, item 6), when one is planned. That phase is out of scope here (section 7); the owner names it or files an issue (proposed) |
| Deferred refactor (ROF4): `coverage.read_evidence_document` takes both `census_model_digest` and `census_model` | 005 | **carried** with the row above: the digest could be derived from the model, but the function is public and tests call it with the digest only |
| Issue 112 | plan | closed as completed by the owner, 2026-11-08 (issue-states.txt) |
| Issue 111 | plan | closed as completed by the owner, 2026-11-09, under R1 (issue-states.txt) |
| Report-side gap of 111: reports print the legacy `model_digest`, which a caller cannot recompute without GND | plan 2.2, 005 | **accepted residual** (R1). Stated on the issue. A later milestone starts from D3 (b) or (c) |
| Generated Pyrel plans refuse a canonical pin (D7) | plan D7, 005 | accepted residual by ruling D7; documented in `docs/agents/plans.md`. T8 has not run on the author's machine (no DuckDB) |
| Legacy identity not retired | plan 2.6, section 7 | retired from this milestone: out of scope; any retirement is a separately approved phase with its own trigger |
| ROF1 and ROF2 boundaries: no `WARNING at` or derivation `[finding]` corpus line; the reason suffix pinned at payload level only (T18) | 002, 003 | accepted residual |
| ROF2 declined findings: no output-size cap on projected text (P3); a non-serializable computed post on the direct plain printer (P4) | 003 | accepted residual (spec I8) |
| ROF3 boundaries: a caller starting from YAML text needs GND's defaults or the `--identity` output; T1 and `derive_vectors.py` share Python's JSON encoder (the hand-written vectors do not) | 004 | accepted residual |
| ROF4 boundary: S2 cannot observe the widening (a reference-bearing model has one identity); T1 pins that S2 asks the helper | 005 | accepted residual (review P5) |
| The slow `evidence or census` lane did not run to green; its acceptance-runner cases fail on main too | 002 | carried: not this milestone's. It runs only on explicit owner request (`slow_cadence`) |
| ROF2 size: source lines added reached 1.76 times the estimate (1.2 times net), past the 1.5 times stop rule, without the pause the plan requires | 003 | accepted residual: recorded in 003 as a finding about the estimate; the owner merged PR 127 over that record. The pause was missed, not waived |
| ROF3 size: tests reached 1.55 times their estimate (review regressions and hand-written vectors) | 004 | accepted residual: recorded in 004; the owner merged PR 132 over that record |
| ROF3 review P7: proposed repairs to T8 and T12, argued rather than applied (T7 was applied) | 004 | accepted residual: spec I7 states the argument |
| ROF4 spec I5: two pre-existing crashes found while authoring the corpus (a text walk on a reference model; coverage on a `derivations: null` report) | 005 | closed by their own PRs, both on main 8eb4fe60: PR 135 (859b852d) and PR 136 (54554bf0) (issue-states.txt) |
| Repairs after each phase review carry no review opinion | 002-005 | accepted residual (boundary below) |

## Plan repair

Phase records named one plan repair: ROF4's R1, the predicate-4 clause on
issue 111. This close adds the predicate-5 issue clauses and ROF5's
withdrawal (rows 1-3). The close review (K2, K4) found four more places
where an owner-approved phase spec departed from r3's wording (rows 4-7):
- the refusal rule id (ROF3 D4);
- the scope of the legacy pin (ROF3 D6);
- the wrong-pin message (ROF4 D2);
- the count of executable shipped pins (ROF4 T10).

All seven rows are written into plan section 11 with the r3 wording kept.
They are **proposed** amendments that take effect with the owner's close
ruling. The amended plan is bound above by sha256.

## Refuted premises

- The approved ROF4 S1 answer said that a walk pinned with the canonical
  identity gives a payload byte-identical to the legacy-pinned one. Review
  P2 refuted it: `transition.model_digest` echoes the supplied pin, as the
  report schema defines ("As SUPPLIED by the steps document"). The corpus
  and the spec were corrected (ROF4 spec I1). The owner accepted the
  corrected answer (ROF4-O1). This was a spec premise, not a plan premise;
  the plan needs no repair for it.
- The approved ROF4 T6 answer said a measure corpus mixing both spellings
  gives a payload byte-identical to the all-legacy run. It cannot: the
  report's `corpus[].sidecar_sha256` is the SHA-256 of the sidecar file the
  case rewrote (ROF4 spec I2, review P4). The runner checks each published
  value against its file and compares every other byte. A spec premise; no
  plan repair.

## Refactoring review

- ROF1, ROF2 and ROF3 each executed behaviour-preserving refactors, named in
  their records: the shared check rows, the walk rows and projected
  preamble, and the version-1 envelope's one home. ROF4 executed none
  beyond the helper.
- Every deferred refactor has a sweep row with a target: ROF2-O2 (RF-D5);
  the legacy-value names and `read_evidence_document` (legacy-identity
  retirement); ROF1's not-done items, which ROF2 closed.

## Boundary: what this close does NOT establish

- Each phase had one reviewer (Codex). The project's panel bar ran over
  nothing in this milestone. Repairs after each review carry no review
  opinion. This close had one reviewer; its repairs were not re-reviewed.
- Owner rulings R1 and ROF4-O1 are recorded as relayed by another session.
- T8 (a generated Pyrel plan refuses a canonical pin) needs the DuckDB
  runtime and has not run on the author's machine.
- The broad lanes (`slow_cadence`) did not run.
- GitHub issue and PR states are as observed at 2026-11-09T05:11:59Z
  (evidence/close/issue-states.txt).
- Merge of this close is the owner's. It is the close ruling over this
  record and the plan section 11 amendments.

## What the close still needs

1. **The close ruling**: the owner's ruling over this record and plan
   section 11 (rows 1-7), and the merge of PR 145. The merge is that ruling.
