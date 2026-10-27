---
milestone: induced-knowledge
station: phase-IK6
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: phase-IK6
date: 2026-10-26
gate:
  command: "uv run pytest -q -p no:randomly tests/test_ik6_walk.py tests/test_ik6_skill_census.py tests/test_documentation_tutorials.py tests/test_tutorial_output_blocks.py tests/test_plan_app_docs.py tests/test_replays.py tests/test_release_docs.py tests/test_packaged_skills.py tests/test_skill_prose_sync.py tests/test_public_binding_prose.py tests/test_public_built_inventory.py tests/test_public_distribution_runtime.py tests/test_verification_fixes.py tests/test_public_api.py tests/test_gnd_arch.py tests/test_ilp_bridge.py tests/test_discover.py tests/test_measure_labels.py tests/test_evolve_references.py tests/test_rf*.py"
  exit: 0
  output: "2990 passed, 36 deselected in 257.34s (0:04:17)"
  note: >-
    Spec §8's selection plus the plan-app, replay and tutorial-output docs
    tests, which also read docs/tutorials and docs/how-to. The same run also
    did zensical build --strict (no issues) and tools/check_docs.py site
    (11416 local links/assets/anchors checked). The expanded command is the first line of
    evidence/IK6/final-gate.txt.
slow_cadence:
  command: "uv run python tools/check_installed_docs.py --out <scratch>"
  exit: 0
  output: "217 tutorial blocks passed (each wheel origin); Both installed wheel origins passed the documented learning paths."
  note: "T7, run once on the final bytes; results.json retained"
evidence:
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK6/final-gate.txt
    sha256: 355210223c2a96cfb0e1d5d976e717a0b498d87b67f8acb2b3bb35baa6d5d5a2
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK6/regressions-red.txt
    sha256: b624fdd7083210983e7460c150fbf0a94ff12b5bf7416df8ea53c62849b18ce3
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK6/installed.txt
    sha256: 24802ab1a0179d452c942fe5ede1fb44b6db6f8da1c06f3b20e7e959406245a3
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK6/installed-results.json
    sha256: ce49bca8da006bfd380aa889e49b3ad34320f311730f88433cab286843d6073a
  - path: tests/fixtures/induced_knowledge/ik6-walk/goldens.json
    sha256: ac778a94a4c0b0039b8e78983f44704b303ad6ea44ce503d83b9a6f796cb10a6
  - path: .gnd-planning/milestones/induced-knowledge/skill-census.md
    sha256: 9ee6d2a63dc5701f541663bca22aaa958b0750d0193d865fde7ff7d981bef05c
  - path: .gnd-planning/milestones/induced-knowledge/notes/phase-IK6-agent-review.md
    sha256: 9847db02afa7bb877eeee014fa3f7216973a996a55b4102a37bda67e5fbb80f4
---

# Phase IK6 — end-to-end example, docs, integration

**Claim.** A reader copies the `refunds` example from the installed package
and follows one walk:
- score a written rule against an auditor's labels;
- learn a better rule with a stand-in learner, have GND re-check the learner's
  claim, and see GND refuse an over-claim;
- discover candidate rules from one clean week;
- preview both proposals and apply the learned one as proposed and advisory.

Every number the business tutorial states comes from that walk, and the walk's
written files match committed goldens under two hash seeds. Every packaged
skill file is in a census, with what the milestone changed and why.

**Authority:**
- spec r1, approved 2026-10-26 with rulings D1..D9 (spec §13);
- checkpoint C1, three rounds, approved at r3: "C1 r3 looks good. Continue with
  the goldens, skills, census and docs." (spec §14).

## What shipped

- **The example,** `src/gnd/examples/refunds/`: a model with the written rule
  "a refund should not be more than 1000" (deontic); eight store weeks (four
  clean, four flagged); a class-mode `labels.json`; `stand_in_learner.py`
  (standard library, deterministic, not a GND command); and a README. The batches
  and labels come from `evidence/IK6/build_refunds_example.py`.
- **The tutorial,** `docs/tutorials/learn-rules.md`, "Find the rule your auditors
  are really using". It is written for a business reader: requests to Claude
  Code, the `gnd-model-evolve` skill for the model change, two figures
  (`refunds-weeks.svg`, `refunds-claim-check.svg`) and tables that restate real
  output. It has no commands (owner, C1).
- **The commands page,** `docs/how-to/learn-rules-commands.md`: the runnable
  walk, ten blocks, the runner group `induced`. It is the one walk (rule 4).
- **Goldens:** `tests/test_ik6_walk.py` and `ik6-walk/goldens.json`, eleven
  written files (T2). The file also holds T3 privacy, T8 learner determinism,
  and the review regressions.
- **The census,** `skill-census.md`: 65 rows. `tests/test_ik6_skill_census.py`
  checks each file appears once, and that each changed cell equals the
  phases git records (T4, T5).
- **Skill edits:**
  - `gnd-export`: `gnd export ilp` is the ILP bridge, not a derivation export;
  - `gnd-dev-session`: `gnd measure --labels` beside `--populations`;
  - `gnd-codegen`: docstrings carry the description `summary`.

  `gnd-extract/references/extraction-contract.md` was inspected and needs no
  line (F10).
- **Docs:** a release-notes entry; a pointer in the synthetic-data guide; "see it
  end to end" links in `measure-labels.md`, `discover.md` and `ilp-bridge.md`;
  two nav entries.
- **Controls:** the learner is a standalone example in RF7's list, and its
  syntax-only query candidates are a counted IK6 entry in the RF6 successor
  chain (`evidence/IK6/dynamic-query-successor.json`), as for every earlier
  example script.

## Gate output (verbatim)

```
2990 passed, 36 deselected in 257.34s (0:04:17)
exit 0
```

## Criteria

| Obligation | Test | Result |
|---|---|---|
| the walk exits as documented at every step (IK6-C1) | T1, `induced` group | 10 blocks pass; the over-claim exits 3 |
| its outputs match committed goldens | T1 output blocks; T2 | 11 file digests equal under PYTHONHASHSEED 0 and 4242 |
| privacy | T3 | no absolute path, downstream name or run directory in the example, pages or written files; induction examples are batch ids |
| a census of every packaged skill file | T4 | 65 rows, each once; changed cells equal git; four seeded faults and a wrong phase fail by name |
| skill edits | T5, inventory and sync tests | present; routing graph unchanged |
| controls (IK6-C3) | T6, the gate | pass |
| installed candidate | T7 | both wheel origins, 217 blocks each, `induced` included |
| the learner is deterministic | T8 | byte-identical; the faulty claim is the true cover plus north |

## Adversarial review

One local reviewer agent read the diff against B. **One reviewer is one
reviewer.** It found no blocking defect, four hardening issues and five
completeness items, and checked every number on the pages against real runs.

**Fixed, each reproduced first:**
- H1: a Windows-path pattern that never matched;
- H2: no test read the walk's written files for paths;
- H3: the learner ignored or misreported bad `--also-claim` values;
- H4: the census test did not check which phase changed a file;
- C1: no test tied the tutorial's numbers to the walk;
- C2: "under 500" was false for south's 500;
- C3: "keeps the fewest" overstated a greedy cover;
- C4: the release notes described `induced` too narrowly;
- C5: the nav label, the retained T7 results, and committing everything.

H3 and C2's regressions failed on the reviewed code
(`evidence/IK6/regressions-red.txt`: 6 failed). H1, H2, H4 and C1 were defects
in tests, so there was no code for their regressions to fail on. The
reviewer's probes (`t3probe`, `t4probe`) are the red evidence; they are
retained in the session's scratch space, and the review note quotes them.

**Not reproduced:** two RF1 session-pin failures in the reviewer's sandbox.
Both pass in the phase gate. The report and disposition are in
[phase-IK6-agent-review.md](notes/phase-IK6-agent-review.md).

## Refactoring review

**Seen, deferred:** every executable example under `src/gnd/examples/` must be
entered in two places:
- RF7's standalone list;
- a counted RF6 dynamic-query successor.

Neither inventory applies to these scripts: they read no model through GND, and
`tools/gnd_layers.json` already exempts `src/gnd/examples/**` from layering.
IK6 paid this twice, because the learner's rewrite moved its count. Exempting
the examples tree in both scans by one shared rule would end that churn. It
changes RF controls outside this phase, so it is open question **IK6-R1**,
targeted at the milestone close.

**Seen, deferred:** `tests/test_ik6_walk.py` repeats the runner's run-directory
normalization for file contents. Making it a runner function is small, but it
touches the shared runner other groups rely on. It is recorded under IK6-R1.

**None needed** in GND's own modules: IK6 changed no `src/gnd` module outside
the example and the skills' prose.

## Boundary — what this phase does NOT establish

- **No real learner ran.** The stand-in is not Popper; IK5-Q5 stays open (D7).
- **The learner's join space is never exercised.** This model yields 40
  comparison candidates and 0 joins; the join code is example code with no
  case.
- **The tutorial's numbers are pinned by string pairs** to the commands page
  (C1's test), not by running the tutorial. A reworded tutorial sentence must
  move its test pair with it.
- **The goldens move on a GND version bump:** `measure.json`,
  `discover-report.json` and `discovered.json` record the version.
- **The walk applies a rule in its scratch copy.** It is `proposed` and
  advisory; nothing is confirmed.
- **No skill runs the measure, discover, export or import steps** (F8); the
  tutorial shows them as plain requests.

## Open questions

| ID | Question | Proposed | Owner |
|---|---|---|---|
| IK6-Q1 | A packaged skill for the induction loop: measure against labels, discover, export to and import from a learner, then review. The owner wants tutorials to show skills, and today four of the six steps are plain requests. | a new skill, planned as its own phase or milestone | owner |
| IK6-R1 | Exempt `src/gnd/examples/**` from the RF6 dynamic-query and RF7 parser scans by one rule; lift the walk test's normalization into the runner | milestone close | owner |

Carried, not IK6's: IK1-Q2 (milestone close, D6), IK5-Q5 (open, D7), and the
items spec §3 lists for close.

## Refuted premises

- **"The page is the walk" (spec §4 rule 4, §6).** After the owner's C1 rulings,
  the business page shows no commands. The walk lives on a companion page, and a
  string-pair test ties the two (F1, C1).
- **"A committed overclaimed.run.json" (spec §6 step 6).** It would bind
  digests that move with any model edit; a learner flag replaced it (F3).
- **"Nothing is admitted" (spec §5).** The walk applies the learned proposal in
  its scratch copy, as proposed and advisory (F2).

## Size

`git diff --stat 705ad94 -- src tests`: 21 files, 791 insertions, 4 deletions. GND modules: none. The rest is the example (model, eight batches, labels, a 134-line learner, README), three skill prose edits, the two IK6 test files, the goldens, and two RF control registrations. Evidence files are sanitized: scratch, temporary and repository paths read `<scratch>`, `<tmp>` and `<repo>`.
