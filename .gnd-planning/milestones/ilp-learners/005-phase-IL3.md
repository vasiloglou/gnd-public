---
milestone: ilp-learners
station: phase-IL3
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: phase-IL3
date: 2026-10-28
gate:
  command: "uv run pytest -q -p no:randomly <the IL3 file list, evidence/IL3/gate-files.txt>"
  exit: 0
  output: "959 passed, 23 deselected in 170.28s (0:02:50)"
  note: >-
    The literal gate of spec §8: the direct IL3 tests (tests/test_ilp_rules.py)
    and the plan §9 impact closure (the IL1, IL2, IL5 and IK5 bridge tests, the
    IK6 walk, the IK close test, the RF1 CLI goldens and manifest, RF5 commands,
    the layer map, the architecture test, the RF6 census, the built inventory
    and schema sync). The live lane ran separately with the scratch venv:
    1 passed. The RF1 pins also ran under Python 3.11.15 and 3.13.12: 152
    passed each. Ruff clean.
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection or separately configured CI"
  reason: "outside IL3's impact closure; the reduced v6.3 selection was run"
evidence:
  - path: .gnd-planning/milestones/ilp-learners/notes/phase-IL3-spec.md
    sha256: edc45a47bbd3259c5a310f1858eceaeb0f7c3c28760f4ac50a97ac48e112c3e6
  - path: .gnd-planning/milestones/ilp-learners/notes/phase-IL3-agent-review.md
    sha256: 820af0c58cc359992a87650b6197f41a6cfcba4a672994f64976014fece10dd6
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/gate-files.txt
    sha256: f70c232eae5071ea7353e2b0f7609ca75fea1fcc0d58f9f2a73509ac685362b2
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/final-gate.txt
    sha256: add5600d9d809c88a4e19b1c5d513380d559b0a26d1ad2d01ea1163de77d1f86
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/review-brief.md
    sha256: c0edbc0a7824c726c86b2ac9ecd80ff08030a42a6b1ae7acaccd707c717a5815
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/run_rules.py
    sha256: 92aa7d536831709d9cf7e73ec0054bb90dd479320af3516deae9d9de175dcb5e
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/learn_rules.py
    sha256: f187afecfe404c6ee1d552ac04c42c37c9018f44c99fed9f474019dce23c6c8d
  - path: .gnd-planning/milestones/ilp-learners/evidence/live_common.py
    sha256: 6a057780e11bbb99a9859046dc13ca82b54701de9377f1f6f5aa865984e97d6b
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/downloads.json
    sha256: fa5f6a0138831361185e9bb26b7bbce968f3272b3b386a7d7d4aa4972051a05b
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/sdist-members.txt
    sha256: fd13370b41740f270819d980913244839f48fc2f14c2e32a0ea647e84ed0634a
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/dynamic-query-successor.json
    sha256: 9a655d0c063743de4445a88b60f329e2331737c49d407610b423e95cc1e26f7b
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/probe/features.json
    sha256: 4915edf5375d5d2aa85de57aeb5856f4051a7f626d26adefe03ecc1984a654bf
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/probe/invocation.json
    sha256: 6ef050cee0f4bd0b7e2bad9965da0572cf1951fb80c235a99ac2d11fdbde656e
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/probe/probe.json
    sha256: bdba70291b5f44e730d5e16e7bf3d6eb20aec5f7e7b5810d665707e90585e19c
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/probe/raw-stderr.txt
    sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/probe/raw-stdout.txt
    sha256: 386db66ef5ac856e6f67eca8f49cae237b4001c3873c12eeaaf19d1d1c7e2279
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/live/invocation-1/import-report.json
    sha256: b185d837a45eb4c07b3b4b8d68827c4ff71b04d1ca9b10e60d9d179ff3d5ab14
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/live/invocation-1/invocation.json
    sha256: c9412a552c6918d61c9e808e21138ec83ac5939a51b64f56d57ea97458bd0cf6
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/live/invocation-1/outcome.json
    sha256: 0fb6aa2dc2395a7aa79c902882f8f389e0600e173a5a8de35ac52a0ad514cb9b
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/live/invocation-1/proposal.json
    sha256: b0eb52126c3731144164a23038ee227c17d4986a57926a44b8acb59c7466fdef
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/live/invocation-1/raw-stderr.txt
    sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/live/invocation-1/raw-stdout.txt
    sha256: 640779ec77d9979bf27f9300e99f724ed4850ea464ac25e97f53f3154eb97dad
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/live/invocation-1/ruleset.txt
    sha256: 1c63fedce2510e01db0cc6de0210ab74e5e1f23d1efaed5f9b0558bdeaac987e
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/live/invocation-1/run-meta.json
    sha256: 9d2e6242a953d7f0e2622699ff357d67502e71b9c0a2f82ec46fa3b0bd3581fd
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL3/live/invocation-1/run.json
    sha256: 44c158518293123d681b70bf7a4d24c534d4828fb9bc031b688cd41147e2e308
  - path: tests/fixtures/ilp_learners/il3/rulesets.json
    sha256: 02cceab662596e1617de549c1a450e3498de940241eceab6ce768dd3d3d15028
  - path: tests/fixtures/ilp_learners/il3/expected/orders/export.json
    sha256: c4df21b229c2f1fe96090615212f210db33e582f13fc9f18313759e429598261
  - path: tests/fixtures/ilp_learners/il3/expected/orders/features.json
    sha256: e56248a67aec760ad53ca79a64fdba19a06c71e44b648debc843b9b9bb44edf4
  - path: tests/fixtures/ilp_learners/il3/expected/refunds/export.json
    sha256: 7b455e99b224d1c7ab41fd2bcfdd1eb10914e795f57d2dd8e5b1c0494a2e5827
  - path: tests/fixtures/ilp_learners/il3/expected/refunds/features.json
    sha256: f96c151bfcb3c846f63e245f02aaf09d3fc57e7a85e316e59e9e022e031f72d3
---

# Phase IL3 — Boolean rule sets: a feature table out, a rule set back, one RIPPER run

**Claim.** IL3-C1 to C4 hold on the evidence below, under:
- the owner's gate rulings of 2026-10-28 (spec §13);
- the owner's ruling on IL3-F2, "Arity in the name" (spec §14);
- one reviewer's adversarial read, whose 8 findings were all reproduced; 7
  were fixed and 1 is an open question for the owner (IL3-Q1).

## What shipped

- **`src/gnd/export/ilp_rules.py` (new):**
  - `render(neutral)` writes `rules/features.json`, `gnd-ilp-features/1`:
    one row per example, one 0/1 column per (integer argument position,
    Popper threshold row). The column name spells its clause:
    `<predicate>__<position>__<arity>__<comparison>__<threshold>`.
  - **Export refusals:** `no-features`, `too-many-features` (over 4,096),
    `too-large` (over 4,000,000 cells), `column-name` (a name over 160
    characters, a threshold over 32 digits, or an id that does not read back
    as itself).
  - `parse_ruleset(text)` reads wittgenstein's printed rule set. The polarity
    table refuses `ordered-rule-list`, `empty-antecedent`,
    `negation-as-failure` and `propositional-conjunction` by name; a single
    true feature becomes its clause with fresh variables. Caps: 32 rules, 16
    conditions, 160-character names, arity 64, 32-digit thresholds.
  - `extract_ruleset(stdout)`, shared by the run script and T9.
- **`src/gnd/ilp-features.schema.json` (new),** in both schema inventories.
- **The registry entry `rules`** (learner `wittgenstein`, method
  `ilp-rules`); the `gnd export ilp` and `gnd import ilp-rules` choices and
  help texts; both `target` enums, widened within `/1`; the layer map.
- **RF1:** the ILP help and exit goldens and `cli/tree.json`, re-captured
  under Python 3.11, 3.13 and 3.14. `gnd export ilp`'s goldens are now stored
  per version, because 3.11 wraps its usage line differently. The manifest
  lines and `MANIFEST_SHA256` moved with them.
- **RF6:** `evidence/IL3/dynamic-query-successor.json`, 23 added syntax rows,
  chained after IL5's.
- **`docs/reference/ilp-bridge.md`:** a "Boolean rule sets" section, and a
  files-table row; the LLM section's extraction sentence now states IL5-Q2's
  ruling (any stray fence makes no answer).
- **Evidence:**
  - `evidence/live_common.py` (new), the shared live-run helper (IL5-Q4,
    IL3-D10);
  - `evidence/IL3/`: `learn_rules.py` (the driver), `run_rules.py` (the
    script), `downloads.json`, `sdist-members.txt`, `probe/`,
    `live/invocation-1/`, `review-brief.md`, `final-gate.txt`.
- **Tests:** `tests/test_ilp_rules.py` (78 default-lane cases and one live),
  over the corpus `tests/fixtures/ilp_learners/il3/`.

## Gate output (verbatim)

From `evidence/IL3/final-gate.txt`:

```
$ uv run pytest -q -p no:randomly $(cat .gnd-planning/milestones/ilp-learners/evidence/IL3/gate-files.txt)
959 passed, 23 deselected in 170.28s (0:02:50)
$ GND_IL3_PYTHON=<scratch>/venv/bin/python GND_IL3_LEARNER=<scratch>/wittgenstein-0.3.5 uv run pytest -q -p no:randomly -m live tests/test_ilp_rules.py
1 passed, 78 deselected in 2.16s
$ uv run ruff check src/gnd/export src/gnd/commands tests/test_ilp_rules.py .gnd-planning/milestones/ilp-learners/evidence/live_common.py .gnd-planning/milestones/ilp-learners/evidence/IL3
All checks passed!
$ <scratch>/venv311/bin/python -m pytest -q -p no:randomly tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py   # Python 3.11.15
152 passed in 18.12s
$ <scratch>/venv313/bin/python -m pytest -q -p no:randomly tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py   # Python 3.13.12
152 passed in 24.60s
$ uv run pytest -q -p no:randomly tests/test_rf1_pin_harness.py -k golden_manifest
4 passed, 35 deselected in 0.26s
```

`slow_cadence` (`uv run pytest -q`) did not run: it is outside IL3's impact
closure and stays an explicit owner selection.

## The run of record

Invocation 1, `evidence/IL3/live/invocation-1/`:
- **termination** `completed`; **import** `admitted`, exit 0;
- E = `7b455e99…5827`;
- **the learner:** wittgenstein 0.3.5, `RIPPER(random_state=0,
  n_discretize_bins=None)`, on the local CPython 3.13.12 with numpy 2.5.4,
  pandas 3.1.0, python-dateutil 3.0.0, six 1.17.0 and tzdata 2026.6. Those
  versions are the only files the venv was installed from (`--no-index`,
  `downloads.json`); `outcome.json` itself does not list them (review 8);
- **the rule set:** `[[f_refund_amount__2__3__gt_t_amount__450=1]]`, that is
  `wrong(X) :- f_refund_amount(X, V1, V2), gt_t_amount(V2, 450)`;
- **coverage:** the learner's own `Rule.covers` gives airport, harbor,
  market, south and station; GND computes the same 5, with support 4/5
  (`south` is labelled `neg`). The rule is admitted as a proposed, advisory
  constraint with that support recorded.

**The three questions the spec asked:**
1. Does wittgenstein accept the table? Yes: the probe and invocation 1 both
   ran with empty stderr.
2. Does the rule set parse and import? Yes, admitted.
3. Does the learner's coverage agree with GND's? Yes, set for set.

**Not repeatable (IL3-F5).** RIPPER 0.3.5 picks a different threshold on
repeated runs, even with `random_state=0` and a fixed hash seed. 11
diagnostic re-runs, made beyond the one approved run and disclosed in the
spec, gave 500, 450 and 310. Invocation 1 is the run of record as recorded.

## Criteria

| Criterion | Holds | By |
|---|---|---|
| IL3-C1: the table is golden across two hash seeds; the bounds are fixed before results; the work counter stays under its ceiling | yes | T1 (two models, two seeds), T2 (oracle), T3 (each bound at and one over) |
| IL3-C2: each polarity row has a test per spelling; a positive single feature maps to a clause that re-checks | yes | T4 (26 corpus cases), T5 (admitted), R7 |
| IL3-C3: the coverage re-check compares the learner's per-rule sets with GND's, from the learner's own predict | yes | T6 (`coverage-mismatch`), T9, T-live |
| IL3-C4: one live run under IL-R9, with a replay test | yes | invocation 1; T9 (with R6's tamper cases) |

## Review

One reviewer is one reviewer: one local agent read `git diff e30eec8
620f394`. Its report is retained, edited only to replace paths, in
`notes/phase-IL3-agent-review.md`, with the disposition. All 8 findings were
reproduced:
- **1 blocking, fixed:** an unbounded arity in a column name let a 46-byte
  rule set make the import allocate without limit.
- **3 hardening, fixed:** the renderer could write names its reader refuses;
  it refused with an undocumented name; the shared helper mapped unruled
  process statuses.
- **1 hardening, for the owner:** IL3-Q1.
- **3 completeness, fixed:** T9's blind spots, the at-bound reader cases, and
  the help and docs drift. One part stays open: outcome.json does not list
  the pandas and numpy versions (above).

The reviewer did not run the learner or the run script, and did not run the
full suite.

**Coverage audit against the declared branches:**
- **the polarity table:** every row and every spelling has a corpus case;
  the order is pinned by `c2-mixed` and `r1-second-rule-refused`.
- **the export refusals:** each has a case (T3, R2/R3).
- **termination:** `completed` by the run; the mapping's other ruled values
  by the shared helper's tests; `spawn-failed` and `cleanup-failed` now stop
  the script (R4). `learner-timeout` is unreachable (IL3-D9, IL2-Q4).
- **import:** `admitted` by the run; `refused:<name>` by T5–T8; `none` by
  the extractor cases (T10); a non-3 exit stops the script (R4).

## Refactoring review

**Refactors executed:**
- **The shared live-run helper (IL5-Q4),** `evidence/live_common.py`: the
  sanitizer, the bounded environment, the export step, the termination and
  import mappings and the fixed import. `run_rules.py` is the first user.
  IL1's, IL2's and IL5's scripts are unchanged, because their bytes are
  bound by digest in their records.
- **T9 checks the script's constants,** not copies of them (review 6), as
  IL5's T9 calls the script's own mappings.

**Seen and deferred:**
- **`ilp_popper._threshold_rows` is private but now has two users,** Popper
  and `rules`. Making it public moves the RF6 census rows keyed by its name
  and touches the Popper module, which is outside IL3. Open question IL3-Q2,
  target close.

**Not done, argued:**
- **A reader for `parse` that sees the export** (IL3-D6 (b)) would have
  removed the arity from the column names, but it changes every target's
  `parse` signature. The owner ruled IL3-F2 the other way; nothing IL3 found
  argues for revisiting it.

## Boundary — what this phase does NOT establish

- **That RIPPER's rule is the rule.** Invocation 1 is one run of a learner
  that is not deterministic under its seed (IL3-F5). Another run could pick
  500 or 310.
- **That a feature table captures the relational task.** Only thresholded
  features of one integer position each are offered; joins between facts,
  and anything negated or conjoined, cannot be expressed or are refused.
- **That the admitted rule is right.** It is admitted as a proposed,
  advisory constraint with support 4/5; `south` is a counterexample.
- **The pandas and numpy versions in outcome.json** (review 8). They are
  fixed only by the install's provenance.
- **That an off-threshold value is refused by name.** As for every target,
  the re-check evaluates it (IL2-Q3, carried).
- **`learner-timeout` is unreachable,** as for ILASP and the agents (IL2-Q4).
- **The RF6 direct-read scanner** sees `predicate[_ROLES]` as a dynamic read,
  not a direct one (IL3-Q1).

## Open questions

| Id | Question | Owner | Target |
|---|---|---|---|
| IL3-Q1 | Review 5: `ilp_rules` reads the neutral form's `roles` through a module key, which the RF6 direct-read scanner cannot see. Should the scanner resolve module constants, should a counted policy row name the read, or is the dynamic census row enough, as for IL5's `_project`? | owner | close |
| IL3-Q2 | Make `ilp_popper._threshold_rows` public now that `rules` uses it, moving its RF6 census rows. | author | close |
| IL3-Q3 | IL3-F5: should a later evaluation phase measure RIPPER's run-to-run variation, or pin a deterministic configuration, before the IL6 comparison reads one run as the rule-set result? | owner | IL6 |
| IL3-Q4 | The plan's §1 names "integer-programming or certifiable" rule-set learners; IL3-D1 (a) chose a sequential-covering one. Repair the plan's wording at close. | owner | close |
| IL2-Q3, IL2-Q4 | Carried. | owner | close |

## Refuted premises

1. **"9b cannot fire for `rules`"** (spec r1, §4). A column can pair a
   comparison with a position of another type; the checker refuses it, as
   `comparison-type` (IL3-F1).
2. **"The reader needs no export"** (IL3-D6 (a)) held only once the arity
   joined the column name (IL3-F2, owner ruling).
3. **"`random_state=0` makes the run repeatable"** — an implicit premise of
   the T-live test as first written. It does not (IL3-F5).
4. **"Every name the renderer writes is a name the reader reads"** held only
   for short ids and small values (review 2, 3).
