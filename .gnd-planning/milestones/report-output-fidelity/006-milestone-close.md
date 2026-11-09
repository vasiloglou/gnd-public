---
milestone: report-output-fidelity
station: milestone-close
skill: "n/a -- repository development under process-milestone auto=false, not a gnd-solve station over a domain model"
scope: milestone-close
date: 2026-11-09
source_base: 8eb4fe60
gates:
  - command: "~/rof-shards/rof-shards.sh close-8eb4fe60 8eb4fe60 on beast-3: the full default lane, six round-robin shards, at main 8eb4fe60"
    exit: "PENDING"
    output: "PENDING -- the beast-3 run has not finished; filled in a follow-up commit"
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
    exit: "PENDING"
    output: "PENDING -- the beast-3 run has not finished; filled in a follow-up commit"
  - command: "ruling: owner -- pending (the close ruling over this record and plan section 11)"
    exit: n/a -- ruling
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request"
  reason: "not selected at this close; the broad historical lanes are outside the milestone's impact closure"
evidence:
  - path: .gnd-planning/milestones/report-output-fidelity/notes/report-output-fidelity-plan.md
    sha256: 33594798e442e06b78302123c2fc3ae87ac1b0e838d775e9e377ec605ce66ea6
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
    sha256: PENDING (file not yet written)
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/close/full-suite-base-12daa5b7.txt
    sha256: PENDING (file not yet written)
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
the phase records bind. Predicate 4's issue-111 clause, and predicate 5's
issue clauses, hold only as amended in plan section 11. These amendments
are the owner's ruling R1 and take effect with the close ruling.

**Full suite: PENDING.** The beast-3 runs at main 8eb4fe60 and at the merge base 12daa5b7 were still running when this draft was committed; their results come in a follow-up commit.

**This record is a draft.** It has had no close review, and no close
ruling has been given (see "What the close still needs").

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
| 1 | Text output of `check`, `validate`, `transition` (full and plan) and export verification prints the plain layout for a model with a redaction policy or temporal terms. The body is rendered from the projected tree only. A canary secret never appears. | ROF1 and ROF2 corpora, canaries and goldens | yes. ROF2's boundary: temporal `--admission` and temporal `verify` are not projected and print plain text, unchanged |
| 2 | A caller outside GND can recompute a model's identity, with one normative home, a shipped producer and a differential test | ROF3: `representation-format.md` subsection, `gnd validate --identity`, T1 over the 306 loadable models, hand-written byte vectors | yes |
| 3 | Every matching site accepts both identities through one helper. Exact-coherence and copy sites stay exact. No recorded digest is rewritten, and pre-milestone artifacts verify. | ROF4: `values.model_identity_matches`, seven sites, the T1 source scan, the 15 shipped pins plus the new canonical example | yes. A generated Pyrel plan refuses a canonical pin by D7. T8, which shows that, needs DuckDB and has not run on the author's machine |
| 4 | D3 honoured: ROF5 withdrawn with its reason, or delivered. Issue 111 stays open unless ROF5 delivers. | R1 (below); evidence/close/issue-states.txt | **as amended (plan section 11, row 1)**: ROF5 is withdrawn with its reason; issue 111 is closed by the owner's ruling, with the gap stated |
| 5 | Approved spec, verbatim focused gate and one independent reviewer per phase. The close disposes every open question and closes 112. 111 closes only if ROF5 delivers. | the four records; the sweep below | the phase half holds. The question sweep is below. **As amended (section 11, row 2)**: the owner closed 112 before this close and 111 under R1 |

## Gate output (verbatim)

**PENDING.** The full default lane at 8eb4fe60 and at 12daa5b7 on beast-3 (gates 1 and 2 above) had not finished when this draft was committed.

Component index, this close's files:

    python3 scripts/components_index.py changed --base origin/main --strict
    changed against origin/main (8eb4fe6): 4 file(s) differ; 0 to fix, 0 warning(s), 0 to reread

    uv run pytest -q -p no:cacheprovider tests/test_development_scaffold.py
    57 passed, 1 deselected in 21.12s

## Owner rulings recorded at this close

Every quote below was relayed to this session by the session that started
it ("Recent fixes summary"). This session did not see the owner's words
directly.

| ID | Question (as relayed) | Ruling (quoted as relayed) | Date | Effect |
|---|---|---|---|---|
| R1 (D3 re-ask after ROF4) | First, the explanation that ROF5 would emit the canonical identity in reports. Then: "Close #111 now, without ROF5?" | "ok skip it for now", then "Yes, close #111" | 2026-11-09 | No emission in this milestone; ROF5 withdrawn; issue 111 closed as completed by the session that started this one, at 2026-11-09T05:08:59Z. The closing comment states what shipped (PRs 132, 138) and the gap the owner accepted (evidence/close/issue-states.txt). This departs from plan predicate 4 ("Issue 111 stays open as partially addressed unless ROF5 delivers"). It is the owner's ruling, recorded as plan section 11 row 1, as the rule-check-release close recorded RL-D10 |
| ROF4-O1 | Accept the corrected S1 answer: a canonical-pinned walk report's `transition.model_digest` echoes the pin as the steps supplied it, as the report schema defines | relayed as ruled; the owner's own wording was not relayed | 2026-11-09 | No change. The behaviour is on main in PR 138, which the owner merged at 2026-11-09T03:15:53Z |

## Open-questions sweep

| Item | Raised | Disposition |
|---|---|---|
| ROF1-O1: keep the `[reason: ...]` suffix (answer E34)? | 002 | closed: ruled 2026-11-07, keep the suffix (002) |
| ROF1-O2: the dynamic-query successor list conflicts when a sibling branch also appends | 002 | closed. It did not occur for ROF1. It did occur for ROF4 against FU5 (PR 134). The ROF4 branch merge 0ff79efa resolved it: FU5 is chained first and ROF4's successor names FU5's file (005, "Merge with main") |
| ROF1-O3: 77 `test_public_tests_mode_corpus` failures and four others, on the author's machine only | 002 | PENDING: disposed against the beast-3 runs (follow-up commit) |
| ROF1 refactoring, not done: `_print_projected_text` served three routes; `render_text_header` raised on an empty list | 002 | closed by ROF2's refactoring (003): `_print_projected_header`, `_projected_preamble` and the walk and verify rows |
| ROF2-O1: should the projected error line add the error type? | 003 | closed: ruled 2026-11-08, leave it to `--format json` (003) |
| ROF2-O2: retire the unused historical bindings `_print_check_verdicts` and `_print_derived_change_summaries` | 003 | **carried**: the shim-retirement phase under RF-D5. Both are still defined on main (`output.py:663`, `:675`) as `gnd.cli` bindings |
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
| Repairs after each phase review carry no review opinion | 002-005 | accepted residual (boundary below) |

## Plan repair

Phase records named one plan repair: ROF4's R1, the predicate-4 clause on
issue 111. This close adds the predicate-5 issue clauses and ROF5's
withdrawal. All three are written into plan section 11 with the r3 wording
kept, as **proposed** amendments that take effect with the owner's close
ruling. The amended plan is bound above by sha256.

## Refuted premises

- The approved ROF4 S1 answer said that a walk pinned with the canonical
  identity gives a payload byte-identical to the legacy-pinned one. Review
  P2 refuted it: `transition.model_digest` echoes the supplied pin, as the
  report schema defines ("As SUPPLIED by the steps document"). The corpus
  and the spec were corrected (ROF4 spec I1). The owner accepted the
  corrected answer (ROF4-O1). This was a spec premise, not a plan premise;
  the plan needs no repair for it.

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
  opinion. This close has had no review yet.
- Owner rulings R1 and ROF4-O1 are recorded as relayed by another session.
- T8 (a generated Pyrel plan refuses a canonical pin) needs the DuckDB
  runtime and has not run on the author's machine.
- The broad lanes (`slow_cadence`) did not run.
- GitHub issue and PR states are as observed at 2026-11-09T05:11:59Z
  (evidence/close/issue-states.txt).
- Merge of this close is the owner's. It is the close ruling over this
  record and the plan section 11 amendments.

## What the close still needs

1. **The close review instrument.** Plan section 9 names none for the close.
   The project's bar is the maintained panel. Each phase of this milestone,
   and the rule-check-followups close, used one reviewer (Codex) by the
   owner's selection.
2. **The close review itself**, then its findings' dispositions in this
   record.
3. **The close ruling** over this record and plan section 11 (the R1
   amendments), and the merge of this PR.
