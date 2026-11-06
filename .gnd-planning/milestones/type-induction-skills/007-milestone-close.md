---
milestone: type-induction-skills
station: milestone-close
skill: "n/a -- repository development under process-milestone auto=true, not a gnd-solve station"
scope: TS-close
date: 2026-11-05
source_base: b733b2a
gate:
  command: "bash .gnd-planning/milestones/type-induction-skills/evidence/close/close-gate.sh (part B here); part A, the full default lane, on beast-3 over a snapshot of the closing tree"
  exit: "1 (part A and the distribution lane, by pre-existing failures only); part B otherwise 0"
  output: "default lane 17050 passed, 518 failed, 2 errors at 3665e28f vs 16945 passed, 517 failed, 2 errors at 1668a58e; one new failure, fixed; distribution 6 failed 10 errors as at 1668a58e; 303 tutorial blocks; strict build; 14648 links; install idempotent; doctor 0; ruff clean; close-fix tests 503 passed, 2 failed (pre-existing)"
  note: >-
    The default lane (pyproject addopts) contains every TS1 to TS5 pytest
    selection, so it is the union of the phase gates. Its failures are
    compared, test by test, with the same lane over main 1668a58e on the
    same host. The distribution and release-acceptance files fail
    identically at 1668a58e (6 failed, 10 errors): pre-existing, below.
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the broad historical lanes are outside the milestone's impact closure"
evidence:
  - path: .gnd-planning/milestones/type-induction-skills/notes/type-induction-skills-plan.md
    sha256: 055f2618b1f79afba8418ceba0a5cf5486c49fd158b6fb0aab22f804307e3b89
  - path: .gnd-planning/milestones/type-induction-skills/notes/close-review-reader-1.md
    sha256: ec8db5169066c8ed5339520e752d0661e320b82ad7b46416fd628fc5f0af507f
  - path: .gnd-planning/milestones/type-induction-skills/notes/close-review-reader-2.md
    sha256: 054fedd75b210b473b68fef9e297e12c01bf00d85a631ee66a1ff166d46396de
  - path: .gnd-planning/milestones/type-induction-skills/notes/close-review-reader-3.md
    sha256: 642179d0af472ddffcce6c8f22270d1f848d1cf106a3446c974c23a2c5ff59d8
  - path: .gnd-planning/milestones/type-induction-skills/notes/close-review-reader-4.md
    sha256: e3b003e746ddee5c9a4f3fd5fd1ce4cc274343852dc78d10705789186ea026d6
  - path: .gnd-planning/milestones/type-induction-skills/evidence/close/close-gate.sh
    sha256: dd26cd07368772f983d896e214fc31f9312dc4df00701d2047ac4e34a90544fb
  - path: .gnd-planning/milestones/type-induction-skills/evidence/close/close-gate-b.txt
    sha256: d0f23c2575e036c389c361da1f06f9a407566e77aeda7c12e77effc4f99278d4
  - path: .gnd-planning/milestones/type-induction-skills/evidence/close/default-lane-compare.txt
    sha256: 9c1e2ae954232c3421b0af71b481c0ca20f25900e062272f94904ebd39cf64bb
  - path: .gnd-planning/milestones/type-induction-skills/evidence/close/default-lane-failures-3665e28f.txt
    sha256: cc04b83257e710faecd73d2cf9aa75fce9e5821e55a72e5f43993442735cdb0f
  - path: .gnd-planning/milestones/type-induction-skills/evidence/close/fixture-parity-b733b2a.json
    sha256: d9dfc300c9b0e1f651f00dabeae28c2d7a17c32a75c140a20950200b7285ec82
  - path: .gnd-planning/milestones/type-induction-skills/evidence/close/fixture-parity-close.json
    sha256: d54949aa902c5d9d0ba121188b6d826eef0e8a03690fcf2fe5051f41e45d2d49
  - path: .gnd-planning/milestones/type-induction-skills/evidence/close/regressions-red.txt
    sha256: 3ea7da4f31cd91c34373d1521599144653787a8385f43e3e867d883e01f16d13
  - path: .gnd-planning/milestones/type-induction-skills/006-phase-TS5.md
    sha256: e6aea7d3f1d05caa1c100ab7750e19a5ce0d125b759129332c222be30f120276
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS5/gate.sh
    sha256: 23367dd463014fd98fb240404639cb7569ffe9ca73302acba9596b92b747734c
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS5/gate.txt
    sha256: e0723f76994091cea48ffddd3484be3b1b3e80e05d70d592fc15782b7dedfa68
  - path: src/gnd/skills/gnd-judge-fact-types/SKILL.md
    sha256: 48b267b633640ebb3aa1beaa85650426f95b97729d3071d12959117e0055888f
  - path: src/gnd/skills/gnd-model-multivalued/SKILL.md
    sha256: 2a3b486fa2333e4b55d98d4bb7c7ade6bab6519cc6e3e38fe9f95ecc0dd4f1cc
  - path: tools/record_judge_sessions.py
    sha256: f3f5ab363b34e3bc5ed2f66b435e29415a43eb5c2743d0d3eb4e0bc7877251cf
  - path: src/gnd/discover/type_evidence.py
    sha256: c48084d39eb743c8f81b7c2276d8b8a3d9dbf9dfedc65f4d46a5eb1d87a09dea
  - path: src/gnd/discover/type_judgements.py
    sha256: dd164fca5b9aad37143f2ff563172459f245f524c54a9ddc99f9286835781fd2
  - path: src/gnd/discover/service.py
    sha256: 98c3851d16ab385427d1d232c085c1bf402943962ccafad6afb5b98d7703def4
  - path: src/gnd/discover/types.py
    sha256: 9912c0b51cb621523130f500212a756a2e5f9642bf1fd18d8bfb3480b43d7bb9
  - path: docs/reference/discover.md
    sha256: 7455901ed933ec944a1f2fb04134c4c31a16e93f6cf93aacf5cb269539747a64
  - path: docs/how-to/judge-induced-fact-types.md
    sha256: 408046c08ab7c49a401ce895dbd7b1e7e3313bdd034293f063a2a2e8cfbc4ade
  - path: docs/release-notes.md
    sha256: 591b3053c8e7a5f90193899f26dbd88549a1a825aa0d612cb8e586561af0f992
  - path: tests/test_discover_type_evidence.py
    sha256: 6a7c68b27116bf537306bbcacad2daa7c4d5c6a5352ae07c252d044f4cdad6b2
  - path: tests/test_discover_type_judgements.py
    sha256: 15bea2c69111fed7da0e8c74a0010e95263283a28df541f2e8c364f13a932adc
  - path: tests/test_judge_fact_types_skill.py
    sha256: 8b8810ee29e19d745c2ea94703fb465e81d80c33b4c480cebda502af571027ef
  - path: tests/test_model_multivalued_skill.py
    sha256: 2235206276f8dbbc5288bd0875468b92bc283a3b54a31c5b466aacaa2898a41b
  - path: tests/test_type_judgements_example.py
    sha256: 4e4baccc22b59c07f9e7ec244b692df783a9ff97d1aea36a06de1e7aaf118a5f
---

# Type induction skills -- milestone close

**Claim.** The `fact-type` discover family can take a skill's judgement
without deciding anything semantic itself. `gnd discover --type-evidence`
writes value-free evidence for every group; `--type-evidence-in` with
`--duplicate-judgements` and `--shape-judgements` reads verdicts bound by
digest to that evidence, refuses stale, incomplete, contradicted or
value-leaking ones (exit 3, nothing written), and renders them: `distinct`
lifts the once-per-generic limit, `duplicate` reports a match the signature
missed, `many-to-many` proposes a binary fact type with a uniqueness over
both roles. Two packaged skills, `gnd-judge-fact-types` and
`gnd-model-multivalued`, write those files from the evidence and the model,
never the population, and ask when their rules stop; each has a recorded
paid run that matched its key. A how-to walks both. Without the new
options every output is byte-identical to `b733b2a`.

**Authority.** Plan r1 approved by the owner `(a1)` without plan review
([001](001-plan-gate.md)). TS1 to TS3 specs approved by the owner (`(a1)`,
`(a2)`, `(a3)`); those phases merged as PRs #88, #89 and #90. The owner then
invoked `process-milestone type-induction-skills auto`, delegating spec,
amendment and close rulings within this milestone: TS4 `(d4)`, TS5 `(d5)`
and every ruling marked "delegated" below are **delegated approvals
(auto=true)**, agent rulings, never the owner's reading. The two paid
recordings of TS4 rest on the owner's own answer, "TS4 run + TS3 re-run
(Recommended)". The owner answered checkpoint DC-TS5 "Looks good,
continue". Close review instrument: four local readers, TS-D2 (a), ruled
here as delegated. Not merged, released or certified; merge needs the
owner.

## Phase records

| Phase | Record | Commit | Focused gate |
|---|---|---|---|
| TS1 type evidence | [002-phase-TS1.md](002-phase-TS1.md) | `fc38f752` (PR #88) | 52 + 529 passed |
| TS2 judgements and rendering | [003-phase-TS2.md](003-phase-TS2.md) | `8b69a278` (PR #89) | 73 + 581 passed; 31/31 mutations killed |
| TS3 `gnd-judge-fact-types` | [004-phase-TS3.md](004-phase-TS3.md) | `98ed5c76` (PR #90); re-recorded `0c2b23fe` | 791 passed |
| TS4 `gnd-model-multivalued` | [005-phase-TS4.md](005-phase-TS4.md) | `e89fab27` | 879 passed |
| TS5 documentation | [006-phase-TS5.md](006-phase-TS5.md) | `3665e28f` | docs gates, 155 passed |
| close fixes | this record | the commit adding this record | the close gate |

Each phase had one independent diff reviewer (one reviewer is one
reviewer). The four close readers reviewed the committed tree at
`3665e28f`; the close fixes below were not re-reviewed.

## Completion predicates

| # | Predicate | Result |
|---|---|---|
| 1 | value-free evidence for every group; `--out` and `--report` unchanged by the option | holds (TS1); reader 1 reproduced byte identity with and without `--type-evidence` under unset, internal and customer |
| 2 | judgements bound, refused when stale/incomplete/contradicted/leaking, rendered, preview and apply pass | holds (TS2) with refuted premises P1, P2. Reader 1 reproduced every refusal and preview, apply and validate on four judged shapes. The free-text check is narrower than the docs said (reader 1 F2): corrected in `discover.md`; the judgements file name is not scanned (F1, TS-close-Q3) |
| 3 | `gnd-judge-fact-types` writes duplicates judgements, no population read, no forbidden value | holds for the recorded branches (`recording-2`, 10 of 10 checks, current bytes). The close added one R3 sentence (reader 2 F1), on a branch the fixture does not reach; the recording binds the skill minus that sentence, and T14 checks exactly that. One unset-mode run; no customer-mode run |
| 4 | `gnd-model-multivalued` writes shapes judgements | holds for the recorded branches, with R1: the recording kept `no_population_access: false`, a false positive on written text; "no read" rests on the corrected check over the kept streams and on reading the transcript (reader 2 F4: the checks are lexical). Its manifest's recorder digest is stale by design, exempted in T14 (reader 2 F3, reader 3 F7; the TS4 record's sentence that both manifests bind current recorder bytes is wrong for TS4) |
| 5 | without the three options, outputs byte-identical to the baseline | holds. With the family off: the IK4 chain `parity-b733b2a` = CT4 `parity-after`, TS1 and TS2 after-tables (only E6 stderr differs, a stated usage line). With the family on: reader 3 F1 found no recorded table against the pre-milestone baseline; captured at the close, `evidence/close/fixture-parity-{b733b2a,close}.json`, 18 cases without the new options, 0 differing; reader 1 also reproduced it over four inputs |
| 6 | a how-to walks one generic fact type through two rounds with both skills; docs gates | **not met as written.** The page walks two folders, each round two of one generic fact type, one per skill (TS5 D2, delegated). A single walk needs a third paid recording, which was not authorized; P5 was a cost limit, not a refutation (reader 3 F2). Docs gates exit 0. TS-close-Q1 asks the owner |
| 7 | focused gates, diff reviews, sweep, PR | holds: five phase gates, five diff reviews, four close readers, this gate, the sweep below and the PR. **Owner acceptance is separate and pending** |

The predecessor's CT-close-Q1 (once per generic fact type) and CT-close-Q2
(multi-valued attributes), handed to this milestone by the owner's rulings
([CT 008](../composition-and-type-induction/008-owner-rulings.md)), are
discharged: `distinct` lifts the limit (`test_t9_distinct_lifts_the_once_per_generic_limit`,
the TS3 skill and recording, `discover.md`), and `many-to-many` proposes
multi-valued attributes (TS2 T14, T17, the TS4 skill and recording) while
the default still counts `multi_valued`, as ruled.

## Close review (four local readers, TS-D2)

[Reader 1](notes/close-review-reader-1.md) (evidence and judgement core),
[reader 2](notes/close-review-reader-2.md) (the two skills and recordings),
[reader 3](notes/close-review-reader-3.md) (predicates, records, evidence),
[reader 4](notes/close-review-reader-4.md) (compatibility, packaging, docs).
All four approve-with-fixes; no blockers. Findings reproduced by the reader
are marked so; regression for reader 2 F1 red before the fix:
`evidence/close/regressions-red.txt`.

| Finding | Severity | Disposition |
|---|---|---|
| R1-F1 judgements file name quoted in a proposal rationale, unscanned | minor | residual, documented in `discover.md`; TS-close-Q3 (the caller names its own file) |
| R1-F2 free-text scan narrower than the docs | minor | docs corrected: each group's attribute and value cells |
| R1-F3 clash suffix only on id clashes, not reading clashes | minor | docs corrected ("never repeats" removed); TS-close-Q3 |
| R1-F4 schema `$` admits a trailing newline in `skill` | nit | residual, TS-close-Q3 |
| R1-H1 under `customer`, no origin, so a re-induction is not refused | hypothesis | already documented in `discover.md` |
| R2-F1 R3 lacks the redacted-null guard S3 has | major | fixed: one sentence in R3, pinned; T14 binds the recording to the skill minus that sentence; fixture has no redacted role (test) |
| R2-F2 a retyped induced fact type leaves no acceptable verdict | minor | residual; TS-close-Q4 (CLI owner) |
| R2-F3 TS4 manifest binds a superseded recorder | minor | stated here (predicate 4); the TS4 record's sentence is superseded |
| R2-F4 recorder checks are lexical | minor | stated here; residual with TS4-Q1 |
| R2-F5 no fixture near the 90% line | nit | boundary below |
| R2-F6 `asked_before_writing` shows no file, not a question | nit | boundary below; the kept text shows the questions |
| R3-F1 no with-family parity table vs baseline | major | captured at the close, 0 differing |
| R3-F2 predicate 6 overstated | major | recorded "not met as written"; TS-close-Q1 |
| R3-F3 §10 rows and TS-D0 not swept | major | §10 dispositions below |
| R3-F4 README status stale | minor | README rewritten at the close |
| R3-F5 `(a1)` labels two approvals | minor | stated: plan `(a1)` in 001, TS1 spec r2 `(a1)` in its spec; both the owner's quoted words |
| R3-F6 premise labels collide | minor | TS1's own P1, P2 are TS1-P1, TS1-P2 below |
| R3-F7 | minor | = R2-F3 |
| R3-F8 TS1 record lacks the implementation go-ahead | minor | stated: the TS1 spec r2 approval `(a1)` was the go-ahead (`ad7c9ded`); the record does not quote it |
| R3-F9 `test_discover_type_evidence.py` has no current digest | nit | listed in this record's evidence |
| R3-F10 TS4 recording 9 of 10 checks | nit | kept in predicate 4 |
| R4-F1 `gnd discover --help` exit text omits the new options | minor | residual; changing help moves the RF1 goldens on two Pythons (CT2-Q1); TS-close-Q3 |
| R4-F2 exit table gives 11 for `--out` only | minor | fixed in `discover.md` |
| R4-F3 release notes under the previous milestone, phase labels | minor | fixed: own Unreleased section, labels dropped |
| R4-F4, F5 how-to wording | nit | fixed |
| R4-F6 stale install test comment | nit | fixed |
| close gate: the how-to broke the docs prose rule (`test_plan_app_docs`: paragraphs over 90 words, an exit code in prose) | minor | fixed: paragraphs split and the rule lists made lists; quotes unchanged. `compose-documents.md` and `grow-a-model.md` fail the same rule at `1668a58e`: maintenance |
| close gate: TS5's `gate.sh` named the downstream applications in its own scan pattern (`test_why_not_anonymity`) | minor | fixed: T4 runs the anonymity test; TS5 gate rerun, `006` updated |
| R4-F7 IL6 census frozen at a commit | hypothesis | as ruled in TS3 D4; a shallow clone is untested; TS-close-Q5 |

## §10 dispositions

| Row | Ruling |
|---|---|
| TS-D0 | discharged: the owner's words are in [CT 008](../composition-and-type-induction/008-owner-rulings.md) ("semantically with a skill"; "with a skill a variant of rai-orm"), cited by the TS1 spec r2 |
| TS-D1 | met in fact (001) |
| TS-D2 | (a) four local readers; delegated, here |
| TS-D3 | (a) a GND packaged skill; implemented in TS4 under `(d4)`, delegated |
| TS-D4, D5, D9, D10 | (a) each, owner `(a2)` in the TS2 spec |
| TS-D6 | (a), owner `(a3)`; the TS4 runs by the owner's own answer |
| TS-D7 | (a), moot after the owner's CT4-Q1 ruling (CT 008: omit under `customer`). The dependency it asked to record: under unset and internal, `induced_from` carries the canonical-JSON attribute digest, guessable for a low-entropy name, and a later change to that form breaks recorded origins. Recorded here |
| TS-D8 | (a) no Python API; delegated |
| TS-D11 | (a) two skills; delegated (the owner's own phrasing named two) |
| TS-Q1 | TS1 D1, owner `(a1)` |
| TS-Q2, TS-Q3 | TS2 D8 and D3, owner `(a2)` |

## Plan repairs (delegated, recorded here; the r1 bytes stay frozen)

| ID | Plan text | Repair |
|---|---|---|
| P1 | judgement provenance on the induced constraint | on the fact type (TS2) |
| P2 | a `functional` shapes verdict | none exists; shapes are `many-to-many` or `skip` (TS2) |
| P3 | TS3-C4 "over the TS5 fixture" | TS3 authored the fixture |
| P4 | §2.3 `functional` on confirmed errors | `skip` plus "correct the population" (TS4) |
| P5 | predicate 6 as one walk | two folders; predicate 6 not met as written (above) |
| P6 | `docs/reference/type-judgements.md` | not written; `discover.md` is the one home |
| §2.2 key | groups keyed by digest | `g<n>` (TS1, after CT4-Q1) |
| TS1-P1, TS1-P2 | TS1 spec's own: the evidence size refusal; TS-R7 "growth zero" | `truncated_groups`; the dynamic-read inventory grew (32 rows) though the query policy did not |
| I8 | the ledger's packaging test name | as the TS1 record names it |

## Question sweep

| ID | Question | Resolution or owner |
|---|---|---|
| TS3-Q1, TS4-Q1 | one recorder turn loop; one stream walk | residual, maintenance, at the next recording (a refactor now stales two manifests) |
| TS3-Q2 | the free-text scan matches `judge.skill` tokens | CLI owner, maintenance |
| TS3-Q3 | re-record TS3 | resolved (`recording-2`) |
| CT4 DateTime kind; malformed-YAML and UTF-16 tracebacks; `test_rf7_structure.py`, `test_rf4_peripheral.py` (5), `test_rf5_commands.py` (10) and `test_plan_app_docs.py` (two older how-tos) red at base | pre-existing | maintenance; not filed (outward-facing) |
| distribution and release-acceptance lane red at `1668a58e` | pre-existing: the built archive carries example files the expected set omits; release candidates absent | maintenance; not filed |
| TS-close-Q1 | accept predicate 6 as two folders, or authorize a third recording for one walk | owner |
| TS-close-Q2 | a re-recording of `gnd-judge-fact-types` over the R3 sentence | owner (paid); the fixture does not reach the branch, so the run would show the same verdicts |
| TS-close-Q3 | CLI hardening: scan or omit the judgements file name (R1-F1), reading clashes (R1-F3), `$` in the skill pattern (R1-F4), help exit text (R4-F1) | CLI owner, maintenance |
| TS-close-Q4 | a retyped induced fact type: evidence `already_induced` per group, or a skill route (R2-F2) | CLI owner |
| TS-close-Q5 | the IL6 census on a shallow clone | maintenance |
| unowned limits | no customer-mode skill run; S3/R3 null-overlap, redacted-role and truncation branches and R1's other-generic case unrecorded; no fixture near the 90% line; `asked_before_writing` shows no file, not a question | accepted residuals, stated in the TS3 and TS4 boundaries and here |
| CT carried | CT-close-Q3 to Q5, CT2-Q1, CT2-Q2 | stay with the CT owners (CT 008, 009) |
| acceptance | milestone acceptance and merge | owner |

## Gate output

```text
## Part A: the full default lane (beast-3)
# full default lane on beast-3 (macOS, git-archive snapshots with a one-commit history)
## closing tree 3665e28f
518 failed, 17050 passed, 794 deselected, 1 warning, 2 errors in 2389.92s (0:39:49)
EXIT 1
## main 1668a58e
517 failed, 16945 passed, 794 deselected, 1 warning, 2 errors in 2481.57s (0:41:21)
EXIT 1
## failures only at 3665e28f (base ran with -rf, so its two ERROR lines are not listed; tests/test_public_optional.py errors identically at both, rerun below)
ERROR tests/test_public_optional.py::test_base_wheel_refuses_missing_synth_extra_and_still_checks
ERROR tests/test_public_optional.py::test_declared_synth_extra_is_seeded_and_loader_valid
FAILED tests/test_plan_app_docs.py::test_plain_short_prose_without_exit_codes[judge-induced-fact-types.md]
## failures only at 1668a58e
(per-file counts and the full list: evidence/close/default-lane-compare.txt, default-lane-failures-3665e28f.txt)

## Part B and the close-fix tests (local, after the close fixes)
$ uv run pytest -q -m distribution tests/test_public_distribution.py tests/test_release_acceptance.py tests/test_public_built_inventory.py
FAILED tests/test_public_distribution.py::test_artifact_and_installed_resource_sets
FAILED tests/test_public_distribution.py::test_symlink_identity_survives_linux_mode
FAILED tests/test_public_distribution.py::test_archive_members_refuse_hidden_content[duplicate-wheel]
FAILED tests/test_public_distribution.py::test_archive_members_refuse_hidden_content[duplicate-sdist]
FAILED tests/test_public_distribution.py::test_archive_members_refuse_hidden_content[extra-wheel]
FAILED tests/test_public_distribution.py::test_archive_members_refuse_hidden_content[extra-sdist]
6 failed, 28 passed, 10 errors in 5.81s
$ uv run python tools/run_tutorials.py
303 tutorial blocks passed
$ uv run --group docs zensical build --strict
No issues found
Build finished in 0.54s
$ uv run python tools/check_docs.py site
14648 local links/assets/anchors checked
$ uv run gnd install --symlink --project --force (twice: idempotence)
2
link changes: 0
$ uv run gnd doctor --project
doctor exit 0
$ uv run ruff check src/gnd/discover tools/record_judge_sessions.py tools/run_tutorials.py tests/test_discover_type_evidence.py tests/test_discover_type_judgements.py tests/test_judge_fact_types_skill.py tests/test_model_multivalued_skill.py tests/test_type_judgements_example.py
All checks passed!
$ uv run pytest -q <close-fix tests>
FAILED tests/test_plan_app_docs.py::test_plain_short_prose_without_exit_codes[compose-documents.md]
FAILED tests/test_plan_app_docs.py::test_plain_short_prose_without_exit_codes[grow-a-model.md]
2 failed, 503 passed in 62.00s (0:01:02)
```

## Boundary -- what this close does NOT establish

- **Owner acceptance, merge, release, publication, certification.** None.
- **The close fixes carry no review.** R2-F1's sentence, the doc
  corrections, the release-notes move and the how-to paragraph splits were
  made after the readers read `3665e28f`; the full default lane ran over
  `3665e28f`, and the close fixes over the focused selection in part B.
- **The full lane's 517 shared failures** are compared by name with main,
  not diagnosed; part of the set also fails locally at `1668a58e`.
- **Two recordings, one model each.** Branches the fixtures do not reach are
  prose with pinned clauses.
- **Not run:** the `evidence or census` lanes, by the slow cadence above.
