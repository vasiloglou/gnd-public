# Plan review -- round 2 (confirmation) disposition

2026-10-27. Instrument: four local reviewer agents (plan D13 (o)). This is the
one confirmation round declared in the round-1 disposition and in plan r2 §8.
The owner's direction for it, quoted: "I accept the round-1 disposition's
repairs A-L and its proposed answers for D17-D20. Apply them as r2 and run the
one confirmation round." (2026-10-27). That acceptance refers to the round-1
disposition committed at `db374d7`, SHA-256
`d4a7e8b0e60dcb938b5d6f1aba7acd037745304c85a88350ceef220c298e9e61`. Neither
the acceptance nor this round approves plan or spec bytes.

## Subjects and limits

| Subject | SHA-256 | Retained snapshot |
|---|---|---|
| plan r2 | `7329cbd216d91a00f10b5b480a4fdaa22f7e7f62a0110913aba7079e28dbc3df` | [evidence/plan-review-r2/induction-skill-plan.md.snapshot](../evidence/plan-review-r2/induction-skill-plan.md.snapshot) |
| IS1 spec r2 | `f81590b028fd6fca80eafd7b743ccc7868883a181232b5080c3972aee141f938` | [evidence/plan-review-r2/phase-IS1-spec.md.snapshot](../evidence/plan-review-r2/phase-IS1-spec.md.snapshot) |

Both were committed in `0c777e3`, and all four readers verified both digests.
The [manifest](../evidence/plan-review-r2/manifest.json) records the snapshot
and reader-note digests.

The readers had fresh context and the same four lenses as round 1. Each received
its own round-1 note and the round-1 disposition. They ran concurrently as local
model agents. No paid tools, credentials or network were used (reader 3 used
read-only `gh`). Probes ran only in scratch clones. Reader 2 built a
spec-shaped tree, measured it and ran the gate files. Reader 4 walked the
commands page in a copy of refunds. No reader wrote to the repository.

## Opinions

| Reader | Lens | Verdict | Blocking | Hardening | Completeness | Self-inflicted |
|---|---|---|---|---|---|---|
| [1](plan-review-r2-reader-1.md) | semantics and admission safety | approve-with-fixes | 0 | 3 | 2 | 5 / 5 |
| [2](plan-review-r2-reader-2.md) | implementability, pins and homes | approve-with-fixes | 1 | 4 | 4 | 8 / 9 |
| [3](plan-review-r2-reader-3.md) | protocol, authority, compatibility, privacy | approve-with-fixes | 0 | 6 | 4 | 8 / 10 |
| [4](plan-review-r2-reader-4.md) | measurability and the end-to-end demonstration | approve-with-fixes | 0 | 7 | 2 | 7 / 9 |

Total: 33 new findings, 1 blocking, 28 self-inflicted (introduced by r2's own
edits).

## Round-1 findings after r2

Of the 13 distinct round-1 blockers, 9 are resolved and 4 partly resolved:

| Round-1 blocker | Status | What remains |
|---|---|---|
| R1-F1, R1-F2, R1-F3/R2-F1, R2-F2, R2-F3, R2-F4, R3-F1, R3-F2, R4-F2 | resolved | — |
| R3-F3 verification selection | partial | ledger shape (R3-N2) |
| R4-F1 recorder | partial | conversation granularity and state seeding (R4-N5, R4-N6) |
| R4-F3 step 6 re-check | resolved in design | not tested (R4-N1); exit citation (R4-N2) |
| R4-F4 claims and recordings | partial | one pair has no single-output form; `said` is not tied to the recorder's declared turn (R4-N3) |

Every round-1 hardening and completeness finding is resolved or narrowed to a
round-2 item below.

## Coordinator reproduction

| Finding | Check | Result |
|---|---|---|
| R2-N1 (blocking) | `test_packaged_skills.py:183` requires the destination link literally in the source, so the sentence reads "Every proposal goes to" followed by link syntax; the trigger regex expects the bare name after "to" | reproduced by reading; reader 2 ran the failing case on its probe |
| R2-N2 | `RELATIVE_LINK_RE` (`test_packaged_skills.py:26`) captures only `../` targets; the orm-core index row's `references/labels.schema.json` adds no edge | reproduced |
| R3-N1 | `test_public_distribution.py:315` `len(paths) == 16`; `test_release_acceptance.py:77` `... == 16` | reproduced |
| R1-N1 | `ilp-bridge.md:49-50`: `bk.pl` and `exs.pl` are written by `gnd export ilp` | reproduced |
| R1-N4 / R4-N2 | `gnd check --help` names no exit except through `-h`; the bands are in `docs/reference/cli.md` "Interpret exits in the command's context" and `population-format.md` | reproduced |
| R2-N3 | `test_development_scaffold.py::test_reference_closure_and_declared_bootstrap` fails on this branch: two links to `plan-review-r1-disposition.md` in `ilp-learners/evidence/plan-review-r2/*.md`, merged from main | reproduced (coordinator link walk; this milestone's files are clean) |
| R3-N9 | the round-1 disposition's SHA-256 is `d4a7e8b0…9e61`, unchanged since `db374d7` | reproduced |

No new finding was refuted.

## Stop rule

The rule declared in plan r2 §8: stop when the self-inflicted ratio exceeds one
half, or when same-reader counts are flat or rising while severity falls.

| Round | Readers | Per-reader counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| 1 | 4 of 4 | 7 / 11 / 12 / 9 | n/a (first draft) | 14 / 45 | high | 4 request-changes |
| 2 | 4 of 4 | 5 / 9 / 10 / 9 | 28 / 33 (0.85) | 1 / 33 | one blocking, a single regex | 4 approve-with-fixes |

Both conditions hold: the ratio is 0.85, and reader 4's count is flat (9 → 9)
while its severity fell from 4 blocking to none. **Plan review stops here.** No
third round runs. The remaining items move to the IS1 spec gate (IS1 items) and
the IS2 spec (IS2 items), as proposed below.

## Proposed r3 repairs, by theme

None is applied until the owner rules. The proposal follows the `ilp-learners`
precedent: r3 applies the repairs with no further review round, and its bytes
carry no review opinion.

**M. Refusal wording** (R1-N1, R1-N2, R1-N3, R1-N5, R2-N9):
- R-e and IS-R2/D5: covered sets never come "from a GND verdict: the output of
  `gnd import`, `gnd check`, `gnd measure` or `gnd discover`, including refusal
  text". The export's files stay allowed as input to an evaluation;
- R-b's exception widens to "save a learner's printed program verbatim as
  CLAUSES and assemble a Popper run record";
- R-h exempts the learner artifacts R-b allows, kept in the user's working
  paths. Example ids in a run record are named as that exception;
- the handoff names each assembled run record, the evaluation that produced its
  sets, and that `inducer` names Popper because the program is Popper's.
  `learner.version` is Popper's own reported version or is asked of the user.
  T8 pins the handoff sentence;
- the host-data flag for value candidates is given at the read-back and again
  in the Hand off row.

**N. The re-check reactions** (R1-N4, R4-N2):
- for `gnd check`, the skill links `population-format.md` for the exit bands
  and names `docs/reference/cli.md` "Interpret exits" in words. IS-R3's home
  list gains that page;
- a reaction row: check exits 1, 2 or 4 → report the verdicts verbatim; they
  are results, not refusals. Exit 3 for check is an input error, reported and
  stopped.

**O. Routing and pins** (R2-N1, R2-N2, R2-N7, R2-N8, R3-N1):
- routing regexes are written against the link form; the handoff trigger
  becomes `Every proposal goes to`;
- "13 new edges"; "the 14th new edge" is dropped. Occurrences are measured at
  implementation (reader 2's probe: 224);
- the orm-core row's cells follow the index's columns: cell 2 a trigger, cell 3
  the claim and what it never does. The two regexes are re-tied to them;
- the `test_schema_sync.py` module docstring and orm-core's "Canonical schemas"
  count are amended with the D3 exception;
- §6.3 adds `test_public_distribution.py:315` and
  `test_release_acceptance.py:77`.

**P. Gate, controls and ledger** (R2-N3, R2-N4, R2-N6, R3-N2, R3-N4, R3-N8,
R4-N8):
- the ledger takes the shape `verification-selection.md` requires
  (obligation, command or evidence, justification, input boundary,
  invalidation), and names the cadence row's lane;
- `test_reference_closure_and_declared_bootstrap` is named as red at baseline
  for a cause outside this milestone (`ilp-learners` snapshot links), not
  claimed. Its repair on main is a follow-up, not an IS1 prerequisite;
- controls 1 and 2 are recorded per test id. T17 is listed as a new test
  committed before its `docs/agents/index.md` row. T16's red comes from the
  owner-selected lane. T7's control-1 red is the per-skill count only;
- gate line 1 adds `test_contributor_preparation.py`; the coverage claim is
  narrowed to the listed files;
- the D20 lane runs only `test_public_built_inventory.py`, as accepted. Running
  `test_public_distribution_runtime.py` too would be a D20 amendment for the
  owner (it builds and installs a wheel).

**Q. The D8 pin commit** (R3-N3, R2-N5): the pin is the IS1 base commit,
reachable from main. #51 touches neither the census nor a skill and is no
dependency. If #50 merges after the IS1 base, its census edit falls outside the
pin, and the pin moves only by an explicit later edit. IS1 keeps "may land at
any time" (D17 (o)).

**R. IS2 outline items, carried to the IS2 spec** (R4-N1, R4-N3, R4-N4, R4-N5,
R4-N6, R4-N7, R4-N9, R3-N5, the R4-F4 `said` gap). The plan's IS2 outline names
them as obligations of the IS2 spec:
- C5 asserts the step-6 re-check fence starts with `/gnd:gnd-induce`, and row 6
  names both skills;
- each `TUTORIAL_CLAIMS` pair gets a recording-side string; divergence needs a
  testable marker beside the replay;
- the recorder's leak gate runs T3's `ABSOLUTE` patterns, T3 reads decoded JSON
  strings, and the commands page ignores `skill-sessions`;
- each conversation is seeded with the commands-page state it needs, with the
  seed's digests in the manifest;
- the recorder is keyed by conversation id, its `done` predicate sees the
  workspace and the kept stream, and the id enters the home path and the
  replay-name regex;
- one declared absence probe for the learner, the exact learner invocation in
  the user turn, and a pass/fail predicate per adversarial turn in
  `results.json`;
- the step-6 "Before" column gets a pre-apply re-check turn or a stated
  derivation from step 1;
- the gate-record parameter checks the record's scope against the example,
  keeps the PL18 check for the course example, and enforces the declared run
  bound;
- the page's "You type" fence is compared with the recorder's declared turn
  (`results.json`), not only with `replays.json`.

**S. Protocol hygiene** (R3-N6, R3-N7, R3-N9, R3-N10, the minor `test_t16` note
in R3-F4):
- IL6's census extension becomes a coordination note for the IL6 gate. The plan
  claims nothing about it;
- the README is brought up to date now (below);
- the plan header cites the accepted disposition's commit and digest;
- #52 (IKE-Q3, which edits `gnd discover` and `discover.md`) is named in §1 and
  IS-O16; IS1 rebases after it if it merges first;
- T13's prose names `test_t16` as the closed frozen-skill comparison and
  `test_t25` as the station numbers.

## Applied now

- The [README](../README.md) is updated (R3-N7). It is a status page, not a
  review subject.
- Nothing in the plan or spec changes; r2's bytes are as reviewed.

## Next action

The owner rules on applying themes M–S as r3 with no further review round, then
decides plan approval over r3. A separate follow-up repairs the two broken
snapshot links in `ilp-learners`' round-2 evidence on main.
