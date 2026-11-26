---
milestone: induction-skill
station: "phase-IS2"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-IS2
date: 2026-11-26
source_base: a223ac7266967feb4b3f533d535c5a8c9a22c5b5
source_subject: 902c8949
gates:
  - command: "uv run pytest -q -p no:randomly tests/test_record_induce_sessions.py tests/test_induce_skill.py tests/test_learn_rules_page.py tests/test_replays.py tests/test_ik6_walk.py tests/test_documentation_tutorials.py tests/test_tutorial_output_blocks.py tests/test_plan_app_docs.py tests/test_release_text.py tests/test_release_version.py tests/test_packaged_skills.py tests/test_public_packaged_invocation_guards.py tests/test_solve_successors.py tests/test_schema_sync.py tests/test_gate_guard_list.py"
    exit: 0
    output: "892 passed in 196.53s (0:03:16)"
  - command: "uv run pytest -q <the structure guards of project.md>"
    exit: 0
    output: "872 passed, 2 deselected in 122.61s (0:02:02)"
  - command: "uv run ruff check; uv run --group docs zensical build --strict; uv run python tools/check_docs.py site; python3 scripts/components_index.py changed --base a223ac72 --strict; uv run gnd install --symlink --project --force; uv run gnd doctor --project"
    exit: "0, after one index regeneration"
    output: "ruff: All checks passed!; docs build finished; check_docs: 19722 local links/assets/anchors checked, exit 0; components index: 1 to fix (stale line numbers), regenerated in 312d1067, then 0 to fix; install and doctor: exit 0"
  - command: "uv run python tools/check_installed_docs.py --out <scratch>, then tools/run_tutorials.py --group induced from each installed wheel"
    exit: "1, then 0"
    output: "the check stops in the release origin at docs/bookrec/08-guarded-rules.md block 15 (gnd synth needs the synth extra), as it does at the base a223ac72 (F15); the induced group passes 10 blocks from each wheel; both wheels 12,621,060 bytes, under 13 MiB"
    note: "T12; evidence/IS2/installed.txt"
  - command: "ruling: owner, checkpoints C1 and C2"
    exit: "n/a -- ruling"
    output: "C1 \"Fix and re-record\"; C2 \"Approve the page (Recommended)\" and \"Raise cap to 13 MiB (Recommended)\""
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"; the full default lane'
  trigger: "explicit owner request or the milestone close"
  reason: "the broad historical lanes are outside IS2's impact closure"
evidence:
  - path: .gnd-planning/milestones/induction-skill/notes/phase-IS2-spec.md
    sha256: a9e0869e19b838d9756df7c989f8bd1a9dd90f8343afe7a846212b89ee1e9b4d
  - path: .gnd-planning/milestones/induction-skill/notes/induction-skill-plan.md
    sha256: 46e8e6c82d34dd6ca5b61abeebdc0c58fc9860671f08be7580a9a28d1834b0e7
  - path: .gnd-planning/milestones/induction-skill/003-IS2-recording-gate.md
    sha256: 6fe958f2979d3be04f51f1e194ba7bf12a37aa8dab79d3a69723095830339169
  - path: .gnd-planning/milestones/induction-skill/004-IS2-recording-gate.md
    sha256: 528099f47e6906a98063e5a1c034748baf4159bad1229324a47e5eebd5602436
  - path: .gnd-planning/milestones/induction-skill/evidence/IS2/owner-statements.txt
    sha256: 31bcf5d71d2850267a93fbf76fec59819b92a0eccd48cfc2b0c0e380be104faf
  - path: .gnd-planning/milestones/induction-skill/evidence/IS2/owner-statements-c1.txt
    sha256: 51aaad66cbadc660956a79e253ff88ae53be1349905baf92b1787b760b54e9b7
  - path: .gnd-planning/milestones/induction-skill/evidence/IS2/owner-statements-c2.txt
    sha256: eb9e4fcaebf087cbf5005fab76bd46d41d53f184832f73c499ccbc12f7ce996e
  - path: .gnd-planning/milestones/induction-skill/evidence/IS2/gate-final.txt
    sha256: 0b315d0ee8c2be3cd684ecba0e6a0681c8cfa8e31986b4683a9c3ae7a1dc0a04
  - path: .gnd-planning/milestones/induction-skill/evidence/IS2/installed.txt
    sha256: 13873666aa742a67ad2fc3ef7a2e40d775008bf318a48e6225b07d909321006d
  - path: .gnd-planning/milestones/induction-skill/evidence/IS2/rechecked-checks-attempt-2.txt
    sha256: 6432bb5d36bbc8eaeb93ad0b1932110d5cdd21f069f351388dd57e2713f87698
  - path: .gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/rechecked-checks.txt
    sha256: 64cd95f23b2536ba5f6cf3fbaa1f12358a9aa572788389cbad80e2328cf7fcad
  - path: .gnd-planning/milestones/induction-skill/notes/reviews/phase-IS2-r1/review.md
    sha256: 288d2cc3e46b754f8d6309d5205f22927ca1c5570aa213c7c3920eb5b926b94e
  - path: .gnd-planning/milestones/induction-skill/notes/reviews/phase-IS2-r1/FINDINGS.md
    sha256: 87679295200bc3d3f0f68604626a10b4c6164efadba92ee0b9700cf59d9d744e
  - path: .gnd-planning/milestones/induction-skill/notes/reviews/phase-IS2-r2/review.md
    sha256: 42e76ecf673c6ca3083e661ba603be50342aa82a7421482e20af73b2335dde07
  - path: .gnd-planning/milestones/induction-skill/notes/reviews/phase-IS2-r2/FINDINGS.md
    sha256: 156ec002a2617ed1e476207e84f0919cbc5351260ed25fa8bc3edfb68bf467eb
  - path: src/gnd/skills/gnd-induce/SKILL.md
    sha256: 8517e32d0c10c35f22652e01e2b798bbeca00bd773b47a23980279f734eec5f0
  - path: tools/record_induce_sessions.py
    sha256: 6a187b748ed9959f6f0ec7c735a08708680c7609d96948ed0be24dcc3a34260c
  - path: docs/tutorials/learn-rules.md
    sha256: 37c0020487be3e991d7132688f92b452e8e4038b5f95db26d7b37ce4672a441e
  - path: tests/test_learn_rules_page.py
    sha256: 3f1d6cee442cfe7b8d3d2071d260cfee88ad87b26ff6884911f7ad831235fab6
  - path: tests/test_record_induce_sessions.py
    sha256: e7986bdb0c1bafefa978092de6fc6ad9b123e878c5ed9661ccfc354a4be2311b
  - path: docs/assets/replays/replays.json
    sha256: 7f6d3987314ee12e7100bd141965f6ee74948cdd9babf58524f6d5eb03c66a3f
---

# Phase IS2: recorded runs of gnd-induce and the tutorial rewrite

## What shipped

The learn-rules tutorial now shows Claude Code (Haiku) running the
`gnd-induce` skill, step by step, from real recordings:

- **Nine recorded conversations** over the refunds example
  (`src/gnd/examples/refunds/skill-sessions/`), made by a new recorder,
  `tools/record_induce_sessions.py`, under two gate records: 003 (the first
  attempt) and 004 (the re-recording the owner chose at C1). Every check runs
  outside the agent; a leak gate keeps no local path, key or git identity.
- **The skill amended once** (IS2-A1, spec section 14): outputs stay in the
  working folder, the actor is asked before the first writing command, "don't
  import" stops at the learner, no proposal is written by hand, the handoff
  stops, and the absent-learner stop is said in its words.
- **Six replays** on `docs/tutorials/learn-rules.md`, rewritten by Fable (D12):
  a `/gnd:gnd-induce` prompt in every step, the recording and its transcript,
  and an "In this run." note explaining every failure. Step 6's review prompt
  is marked **Not recorded.**
- `TUTORIAL_CLAIMS` gains a recording column; `tests/test_learn_rules_page.py`
  is new; the commands page names the skill; one release-notes bullet.
- The wheel budget is 13 MiB, by the owner's C2 decision (the recordings are
  432 KB).

| Attempt | Spend | Result |
|---|---|---|
| 1 (record 003), kept as evidence in `evidence/IS2/attempt-1/` | USD 1.446, plus F2's USD 0.084 | every conversation departed from the skill; C1 |
| 2 (record 004), in the packaged example | USD 0.265 | six of nine pass every check; `learn`, `absent-learner` and `make-it-pass` depart, as spec section 15 records |

Total spend USD 1.79 of D11's USD 10 ceiling.

## Gate output (verbatim)

From [gate-final.txt](evidence/IS2/gate-final.txt):

```text
IS2 final gate, run 2026-11-26 in a clean clone at the commit below (macOS, Python 3.14).
902c894950417cac2ed2d59904efde2318d8aad7
$ uv run pytest -q -p no:randomly <IS2 spec gate files>
892 passed in 196.53s (0:03:16)
$ uv run pytest -q <project structure guards, project.md>
872 passed, 2 deselected in 122.61s (0:02:02)
$ uv run ruff check
All checks passed!
$ uv run --group docs zensical build --strict
Build finished in 1.13s
$ uv run python tools/check_docs.py site
19722 local links/assets/anchors checked
exit 0
$ python3 scripts/components_index.py changed --base a223ac72 --strict
changed against a223ac72 (a223ac7): 154 file(s) differ; 1 to fix, 0 warning(s), 0 to reread
$ uv run gnd install --symlink --project --force && uv run gnd doctor --project
exit 0

The component index's one fix was dev/components/modules/tools.md, stale line numbers after the round-2 repairs; regenerated in 312d1067, then:
$ python3 scripts/components_index.py changed --base a223ac72 --strict
changed against a223ac72 (a223ac7): 193 file(s) differ; 0 to fix, 0 warning(s), 0 to reread
```

## Measured criteria

| Criterion | Evidence | Result |
|---|---|---|
| IS2-C1 a recorder with declared conversations, a gate, checks outside the agent and a leak gate | `tests/test_record_induce_sessions.py` (T1 to T6 and the review cases) | holds; review round 2 left eleven hardening findings in its checks (IS2-Q1) |
| IS2-C2 the replay test learns the refunds path, red first | `test_each_replay_is_named_after_the_run_it_replays`: 6 failed on the committed test, 15 passed after | holds |
| IS2-C3 checkpoint C1 with the real runs, the owner's reaction before the rewrite | the C1 page; [owner-statements-c1.txt](evidence/IS2/owner-statements-c1.txt) | holds |
| IS2-C4 the rewrite: a skill prompt per step, fences equal to declared turns, the recording column, step 6's Before column derived | the page; `tests/test_learn_rules_page.py`; `TUTORIAL_CLAIMS` | holds; step 6's review prompt is the marked exception |
| IS2-C5 the page-structure test, red on the old page | 12 failed on the old page, then pass | holds; round 2 F13's test gaps are IS2-Q1 |
| IS2-C6 checkpoint C2, the rendered page | the local build shown in the app; [owner-statements-c2.txt](evidence/IS2/owner-statements-c2.txt) | holds |
| IS2-C7 the commands page names the skill; its blocks run | one closing sentence; the induced group from both wheels | holds |
| IS2-C8 release notes; the installed docs check | one bullet; [installed.txt](evidence/IS2/installed.txt) | partly: the whole check is red at the base too (F15); IS2's pages pass from both wheels |

## Adversarial review

One reviewer, Codex through the review helper, in two rounds. One reviewer is
one reviewer.

- **Round 1** ([review](notes/reviews/phase-IS2-r1/review.md),
  [ledger](notes/reviews/phase-IS2-r1/FINDINGS.md)), over the IS2 diff at
  `f7aebc80`: fourteen findings, all reproduced, all fixed with failing-first
  tests (spec section 17). The page said Haiku "imported both claims"; the
  recorder's checks misread shell and weakened the spec's done table; the gate
  admitted any file and any model; three tests and two scans missed their input
  class.
- **Round budget**, declared before round 2: one more round, the last.
- **Round 2** ([review](notes/reviews/phase-IS2-r2/review.md),
  [ledger](notes/reviews/phase-IS2-r2/FINDINGS.md)), over the repairs:
  fourteen findings; twelve were introduced by round 1 (0.86 > 0.5), so the stop
  rule ended the loop. F14 (the page), F4 and F11 were fixed, unreviewed; eleven
  are residual IS2-Q1. The reviewer reproduced both published check tables and
  all fifteen replays.
- **The bytes repaired after round 2 carry no review opinion.**

## Refactoring review

**None executed.** One refactor was seen and deferred. The recorder's checks
now hold a small shell reader (`segments`, `outside_words`, `PATH_WORD`) that
both review rounds found gaps in. A shell command's effect cannot be read
reliably from its text; the durable fix is to record what Claude Code ran and
returned per command (for example with a hook that logs each Bash call's argv
and exit), and check that instead. That changes how a recording is made, so it
is IS2-Q1's, not this phase's.

## Boundary -- what this phase does NOT establish

- That `gnd-induce` holds on Haiku: three of nine re-recorded conversations
  depart from it (spec section 15), and one run per conversation is a sample
  of one.
- Any other model, or a real learner; the stand-in is not Popper.
- That the recorder's checks are right for every legal command: round 2's
  eleven deferred findings say they are not (IS2-Q1). The published check
  tables were reproduced by the reviewer from the kept files.
- The full installed docs check (F15), Linux, or the broad lanes.
- A review opinion over the bytes repaired after round 2.

## Open questions

| Id | Question | Target |
|---|---|---|
| IS1-Q2 | Partly discharged: the per-command actor and the miner's export line are pinned (spec 6.9). The rest stay as IS1 recorded them | the milestone close |
| IS2-Q1 | Round 2's eleven deferred findings (F1 to F3, F5 to F10, F12, F13): the recorder's shell reading, done predicates, gate front matter, interrupted-run scrubbing, and the page tests' remaining gaps; and recording each command's argv and exit instead of reading shell text | the milestone close; an issue on the owner's word |
| IS2-Q2 | F15: `tools/check_installed_docs.py` installs the wheel without extras, so `docs/bookrec/08-guarded-rules.md` block 15 (`gnd synth`) fails at the base too | proposed as its own task; repository maintenance |
| IS2-Q3 | F10 of section 16: the keep rule drops a learner call prefixed by `timeout`; `learn`'s replay lacks the learner's printout (the page says so) | with IS2-Q1 |
| IS2-Q4 | Branch history: commit `1cbbc18d` carried the unsanitized round-1 review with this machine's paths; later commits remove them | a squash merge keeps them out of main; the owner may ask for a history rewrite of the topic branch |

## Refuted premises

- **Spec section 6.1's `done` table versus the first recorder.** The first
  implementation weakened four predicates (`faulty`, `absent-learner`,
  `existing-output`, `make-it-pass`); round 1 restored the spec's.
- **"The skill's sentences hold on Haiku" (the IS1 assumption behind IS2).**
  Attempt 1 refuted it for every conversation; the amended skill holds in six
  of nine.
- **Spec section 6.4: "`said` equal to the declared turns".** `learn`'s second
  turn was the recorder's script, not the step's; section 15 amended this to a
  leading prefix.
- **The wheel budget of 12 MiB.** The recordings did not fit; the owner raised
  it at C2.
