# Plan review -- round 1 disposition

2026-10-27. Owner-selected instrument (plan D13, quoted: "use four local
reviewer agents for the plan and close review, as in the induced-knowledge
milestone"). The selection names the instrument only. It does not approve plan
or spec bytes or authorize implementation.

## Subjects and limits

| Subject | SHA-256 | Retained snapshot |
|---|---|---|
| plan r1 as reviewed (D13 recorded) | `526ab075473ab60cf2e8090fe7c0f177aa54e4a82b7fce83af1cb50d1919c411` | [evidence/plan-review-r1/induction-skill-plan.md.snapshot](../evidence/plan-review-r1/induction-skill-plan.md.snapshot) |
| IS1 spec r1 as reviewed | `0510b5275622f8b38aff8865500d40601c9ea4e3ce3b2e58ed2fcf5b9363515a` | [evidence/plan-review-r1/phase-IS1-spec.md.snapshot](../evidence/plan-review-r1/phase-IS1-spec.md.snapshot) |

The reviewed plan differs from the bytes committed in `3b3dc36` only by the D13
ruling (§8, §10, header, README); R3-F9 is right that both were called r1. The
reviewed bytes are the ones above. The next revision is **r2**.

Snapshots are kept with a `.snapshot` suffix. Their bytes are exact, and the
reviewers' line numbers refer to them. As `.md` files, their relative links
would break the repository-wide reference check (R2-F3), because they sit one
level deeper than `notes/`. [Manifest](../evidence/plan-review-r1/manifest.json)
records the snapshot and reader-note digests.

The four readers started with fresh context. Each received the two digests and a
different lens, verified both digests, and read the full subjects and the
relevant sources. They ran concurrently as local model agents, not as humans or
a provider panel. No paid tools, credentials or network were used. Probes ran
only in the session scratchpad; no reader wrote to the repository. Reader 2 left
a long test run unfinished on a shared machine. Opinions are static readings of
the named bytes, plus the probes each one names.

## Opinions

| Reader | Lens | Verdict | Blocking | Hardening | Completeness |
|---|---|---|---|---|---|
| [1](plan-review-r1-reader-1.md) | semantics and admission safety | request-changes | 3 | 3 | 1 |
| [2](plan-review-r1-reader-2.md) | implementability, pins and homes | request-changes | 4 | 5 | 2 |
| [3](plan-review-r1-reader-3.md) | protocol, authority, compatibility, privacy | request-changes | 3 | 7 | 2 |
| [4](plan-review-r1-reader-4.md) | measurability and the end-to-end demonstration | request-changes | 4 | 3 | 2 |

Total: 45 findings, 14 blocking. R1-F3 and R2-F1 are the same defect, so there
are 13 distinct blocking findings.

## Coordinator reproduction

Each blocking finding was checked against the reviewed bytes and the repository
at `3b3dc36`, or at `origin/main` where noted. Probes ran in the scratchpad.

| Finding | Check | Result |
|---|---|---|
| R1-F1 | the const of the stand-in's clause edited 500 → 600 and `clauses_sha256` recomputed: `gnd import ilp-rules` exits 0, "covers 4 (support 4/4)" | reproduced |
| R1-F2 | the reviewed plan and spec have no refusal over writing, editing or re-binding a label manifest; D3 exists to let the agent read its format | reproduced by reading |
| R1-F3 / R2-F1 | `grep -rn "This skill never touches git" src/gnd/skills` → `gnd-export/SKILL.md:27` | reproduced |
| R2-F2 | `EXPECTED_SKILL_FILE_COUNT = 65` at `test_install.py:51`, `test_doctor_uninstall.py:47`, `test_verification_fixes.py:18`; `== 65` / `== 16` at `test_public_built_inventory.py:306-312`; `len(names) == 16` at `test_development_scaffold.py:109`; none in spec §6.3 | reproduced |
| R2-F3 | `uv run pytest tests/test_development_scaffold.py -k reference_closure` failed on `notes/phase-IS1-spec.md` → `../gnd-induce/SKILL.md` | reproduced; **repaired now** (below) |
| R2-F4 | `gnd export --help` lists no `--labels`; the help-option test reads the subcommand path the guard normalizes to | reproduced in part (help text); reader 2 ran the failing test on its probe tree |
| R3-F1 | `git log 077f46e..origin/main`: `07f4d45` adds the approved `ilp-learners` plan. Its §5: IL1 adds `type-confused-join` and neutral `learner-mismatch` refusals; IL2–IL5 add `--target` values; IL4 adds `gnd import mined-rules`; skill pin sites "inspected per phase" | reproduced |
| R3-F2 | sibling commit `33827e2` (`docs(IK-close)`) edits `gnd-orm-core/references/representation-format.md`, a packaged skill file | reproduced (the census-row edit taken from the reader) |
| R3-F3 | `verification-selection.md` asks for a selection ledger; spec §8 has none and uses `-m distribution`; `test_public_distribution_runtime.py` is marked `distribution` | reproduced by reading |
| R4-F1 | `record_skill_sessions.py:57` `TOOLS` allows only `gnd`, `.venv/bin/gnd` and `shasum` in Bash; `:234` requires `phase-PL18-skill-recording` | reproduced |
| R4-F2 | `test_replays.py:59-73` accepts only `plan_apps` sources and `course-<skill>-<model>-run-N` names | reproduced |
| R4-F3 | the tutorial's step-6 "Check batches/market.yaml against the model again." is `gnd check`; no intent in plan §2 covers it; `gnd-model-evolve` says "Not for … population checking" | reproduced by reading |
| R4-F4 | `TUTORIAL_CLAIMS` is a nine-pair hand list; the 5/2/3 split and "north's largest refund is 120" have no pair | reproduced by reading |
| R1-F4 (hardening) | `echo old > m.json; gnd measure … --out m.json` exits 0 and overwrites | reproduced |

No blocking finding was refuted.

## Repair applied now (R2-F3)

The committed IS1 spec turned a default-lane test red. Because this is a defect
in this session's own bytes, and it breaks the branch, the spec's five quoted
route sentences and its AGENTS.md row example now describe their links in words
("gnd-induce, linked as ../gnd-induce/SKILL.md") instead of using Markdown link
syntax. No meaning changed. `tests/test_development_scaffold.py` then passed
(39 passed). The reader notes escape quoted link syntax the same way. These
working-copy bytes differ from the reviewed spec, and carry no review opinion.

## Proposed repairs for r2, by theme

Each theme names the findings it discharges. **None is applied until the owner
accepts the disposition.**

**A. Admission-safety refusals** (R1-F1, R1-F2, R1-F5, R1-F6, R1-F7, R1-F4):
- add "It never writes or edits a learner's clauses or run record." For Popper,
  which prints counts, the skill assembles the run record from Popper's printed
  program, the user's selected non-GND evaluation and the two digests, and says
  that it did;
- add "It never writes, edits or re-binds a label manifest; labels come from the
  user." A stale manifest (exit 3) goes back to the user. The vendored schema
  (D3) is for reading only;
- reword R-c: covered sets come from the learner's output or the user's
  selected non-GND evaluation, never from any `gnd` command's output;
- limit R-f to written and public artifacts. Chat read-back may show values.
  Value-family candidates are flagged at handoff as carrying host data;
- discover with `EMITTED 0`: report the counts and hand off nothing;
- measure: confirm the output path is new before running, since measure
  overwrites. Exit 11 applies to discover, export and import only.

**B. T8's one-home set** (R1-F3, R2-F1): drop R-g from the set. `RECORD_ROUTES`
already pins "never touches git".

**C. Pins, gate and verification selection** (R2-F2, R2-F5, R2-F6, R2-F8,
R2-F11, R3-F3):
- §6.3 lists every literal: the three `EXPECTED_SKILL_FILE_COUNT = 65`
  constants, `test_public_built_inventory.py:306-312`,
  `test_development_scaffold.py:109`, and the "fifteen" test name and messages;
- gate line 1 adds `test_public_packaged_command_help.py`,
  `test_public_workflow_claim_routes.py` and `test_development_scaffold.py`, and
  drops `test_public_distribution_runtime.py`;
- a verification-selection ledger before the gate. The `distribution` lane
  becomes an owner decision row (D20), not a `-m` in the ordinary gate;
- the docs command is `uv run --group docs zensical build --strict`;
- the snippet floor is measured at 30 at baseline, so 34 after;
- the orm-core route is a table row in the workflow index;
- plan §9 no longer says `gnd-export` cites GitHub URLs; a test pins the
  `docs/agents/index.md` row; §10 is re-sized.

**D. Planning-tree links** (R2-F3): done (above).

**E. D9** (R2-F4): mandatory. Its cost text is corrected: no fenced snippet at
baseline starts with `gnd export` or `gnd import`.

**F. Routing regexes** (R2-F7): §6.1 gains the exact out-route sentences, and
each new `ROUTING_MATRIX` regex is tied to a sentence that does not exist
today (e.g. `host labels.{0,200}never applies`).

**G. D3's home** (R2-F9): the canonical copy is the runtime
`src/gnd/labels.schema.json`. The skill copy is vendored, held identical by its
own test (not a `SCHEMA_PAIRS` entry). The orm-core reference index gains a row
that says which copy is canonical.

**H. The IK census pin** (R3-F2, R2-F10, R3-F8, R4-F7):
- the pin reads `skill-census.md` itself at the pinned commit (`git show`), so
  the census and the git reads always describe the same bytes;
- the pinned commit is a full 40-hex SHA. It is named at the IS1 gate as the
  merge commit of the last IK-scoped change, after the IK-close docs-gaps PR
  lands;
- red evidence is two controls: the pin edits (T2–T4, T6, T7) over the pre-IS1
  tree; and the unchanged T5 and T9 over a tree with the skill added.

**I. The ilp-learners milestone** (R3-F1, R4-F6):
- re-baseline on `origin/main` (`45c8603`). Harvest the approved `ilp-learners`
  plan r3. Name it in §1, §3 and §6;
- IS1's edits to `gnd-export` and `gnd-dev-session` are route sentences only.
  IL inspects those files per phase, so whichever lands second rebases;
- the Popper branch is stated unproven on refunds, and no page implies a real
  learner reproduced step 2;
- the ordering of IS2 against IL1 is an owner decision (D17).

**J. IS2's recording protocol** (R4-F1, R4-F2, R3-F5, R3-F6, R3-F7, R4-F4,
R4-F5, R4-F8, R4-F9). The IS2 outline names each edit:
- the recorder gets an example parameter, an allowlist entry for exactly
  `python stand_in_learner.py *`, a keep rule for that output, a gate-record
  parameter, per-example sources and a per-skill `done` predicate. A
  `kept_stream` unit test runs before any paid run;
- a new IS-scoped gate record (never PL18's). Credentials are Claude Code's own
  login, with no environment import. User turns are declared before any run,
  with a run bound and a cost ceiling (D11);
- `--actor` is asked of the user, never derived from git. Scripted turns use a
  synthetic actor. The email and name scan covers the refunds recording home,
  and the recorder's needles add `user.name`;
- `test_replays.py` is generalized to an example and skill map, red first;
- `TUTORIAL_CLAIMS` gains a recording column. A test checks that each
  commands-side string appears in its recording's kept output, and that each
  "You type" fence equals that replay's `said`. "Every number" becomes "every
  number in `TUTORIAL_CLAIMS`", and the 5/2/3 row is decided;
- adversarial scripted turns for the absent learner, exit 11 and "make the
  import pass". Any branch left uncovered is named as a residual;
- a page-structure test (a `/gnd:` prompt in each step; the old sentence gone;
  a skill on every row of the summary table). IS-R7 gains an explicit exception
  for replay transcripts;
- the learn intent can stop after the learner run when asked (steps 2 and 3).

**K. Step 6's re-check** (R4-F3): an owner decision (D18).

**L. Protocol hygiene** (R3-F4, R3-F9, R3-F10, R3-F11, R3-F12):
- T13 checks `git diff --quiet <IS1 base> -- src/gnd/skills/<frozen>` with a
  seeded negative control, in `test_induce_skill.py`;
- the next revision is r2. Owner statements are quoted with dates, or labelled
  as stated in conversation;
- spec §4 binds IS-R1..IS-R10 by name;
- stale wording and the 010 citation (line 181) are fixed. The round budget
  goes into the plan's own §8 (below).

## New decisions for the owner

| ID | Question | Proposed |
|---|---|---|
| D17 | Order against `ilp-learners` | IS1 may land at any time (route sentences only). IS2 records after IL1 merges, so the recordings bind to IL1's import contract. Recordings name their commit |
| D18 | Step 6's "check the market week again" | add a fifth intent, "re-check a population after an apply" (`gnd check`), which reports only; or label that sub-step a plain request on purpose. Proposed: the fifth intent |
| D19 | Snapshot form | keep reviewed snapshots as `*.md.snapshot` (exact bytes, inert links) |
| D20 | The distribution lane in IS1 | run `tests/test_public_built_inventory.py` once at the IS1 gate as an owner-selected lane, recorded separately from the ordinary gate |

Existing D1..D12 and D14..D16 stand as proposed, with D9 now mandatory (E) and
D3 amended (G).

## Convergence budget (declared before round 2)

r2 plus **at most one** confirmation round with the same four lenses. Stop when
the self-inflicted ratio exceeds one half, or when same-reader counts are flat
or rising while severity falls. After that, remaining questions move into the
IS1 spec gate.

| Round | Readers | Per-reader counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| 1 | 4 of 4 | 7 / 11 / 12 / 9 | n/a (first draft) | 14 / 45 | high | 4 request-changes |

## Next action

The owner accepts, amends or rejects this disposition's repairs and rules on
D17..D20. On acceptance, r2 applies themes A–L and receives the one declared
confirmation round.
