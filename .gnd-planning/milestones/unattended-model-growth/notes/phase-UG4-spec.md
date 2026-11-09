# Phase UG4: Documentation, skill and dispositions

## 1. Status line

**Spec gate `(o)`, 2026-11-09: approved as proposed.** Asked "How do you rule on UG4-D1 to
UG4-D7?", the owner replied, quoted: "Approve all as proposed". Every decision in §7 is ruled
as its proposed reading, including UG4-D1 (a): the approval instrument is this spec's prose.
Approved bytes: r1 at `478ea2a2` (sha256 `f475810eb62a06aba44b402baa255e4e3b6c116f8df935320a0553db1f91338a`). Implementation follows.

Earlier status, kept: Draft r1, 2026-11-09: awaiting the owner's ruling on UG4-D1 to UG4-D7.

## 2. Provenance

- Plan: [unattended-model-growth-plan.md](unattended-model-growth-plan.md) r1.2, approved
  2026-11-07 ([record](../001-plan.md)): §2.4, §4 "UG4", §5, §9 UG4 row, §10.
- Base: `ad454305` (main after PR 149, UG3 merged). Branch `claude/ug4-spec`.
- Inherited from the records: UG1 ([002](../002-phase-UG1.md)) disposition matrix and the
  posted comments ([ug1-issue-dispositions.md](ug1-issue-dispositions.md)); UG2
  ([003](../003-phase-UG2.md)) and UG2 spec §6.8 ("everything else is UG4's", including the
  "keeps every fact interpretable" wording); UG3 ([004](../004-phase-UG3a.md),
  [005](../005-phase-UG3b.md)) boundaries ("`unattended-growth.md`, the skill pointer,
  retiring the out-of-band step") and open question UG3-Q2.

## 3. Obligations (the step 0 harvest)

| Source | Obligation | Where discharged |
|---|---|---|
| Plan §4 UG4 deliverables | the final text in each §5 home; the out-of-band declaration step described only as pre-UG3 behavior, the final text describing the shipped locator; release notes; the drafted dispositions updated to the shipped state; docs gates | §6.1 to §6.9 |
| UG4-C1 | every statement has one home and the other pages cite it | §6 table "home / citers"; T1 |
| UG4-C2 | docs gates exit 0 | §8 G-docs |
| UG4-C3 | packaged-skill pins pass (`test_packaged_skills.py`, `test_skill_prose_sync.py`; the IK6/IL6 censuses do not discharge this) | §8 G-skills |
| UG4-C4 | each drafted disposition matches the matrix | §6.9; T5 |
| UG4-C5 | no unqualified "keeps every fact interpretable" wording once UG2 weakened the guarantee | §6.3 to §6.6; T2 |
| Plan §2.4 | `unattended-growth.md` gains the final item-5 answer, the shape-match procedure and the shipped commands; how-to, evolve-policy, agents pages and release notes cite, never restate | §6.1, §6.4 to §6.7 |
| Plan §5 table | the eight surfaces named for UG4 | §6 |
| Plan §9 UG4 row | `tools/run_tutorials.py`; `zensical build --strict`; `tools/check_docs.py site`; `test_packaged_skills.py` and the install, doctor and skill-census tests | §8 |
| §10 UG-D6 (a), ruled | act on a shape match by reusing the existing id, recording the doubt in `open_questions`, or keeping both with a stated reason | §6.1 (c) |
| §10 UG-D0 (a), ruled | the owner closes issues from drafted dispositions after merge | §6.9; UG4-D2 |
| UG1 record, matrix row "76 what the host does with a match" | open, UG4 | §6.1 (c), §6.9 |
| UG2 spec §6.8 | how-to, agents pages, `unattended-growth.md` and the "interpretable" wording are UG4's | §6.1, §6.4 to §6.6 |
| UG3 records, boundary | `unattended-growth.md`, the skill pointer, retiring the out-of-band step | §6.1 (a), §6.2 |
| UG3-Q2 (target "owner; UG4 or the milestone close") | U1 accepts a digest declared twice | UG4-D5 |
| UG-R9 | discovery links from the installer only | no packaged file is added or moved (§6), so no link changes; argued in §4 |
| UG-R10 | anonymity | §8 G-anon |
| UG-R11 | `auto=false`, branch + PR, no merge without the owner | §1, §11 |

## 4. The standing rules, bound to this phase

| Rule | Binding |
|---|---|
| UG-R1 defaults do not move | No code changes, so no command output moves. The one test edit (UG4-D4) only reads files |
| UG-R2 nothing confirms | Every procedure text keeps `proposed` + `deontic`; the `--check-population` paragraph says the admitted constraint stays advisory |
| UG-R3 evidence licenses | §6.1 (d) states the admission is relative to the supplied population and never relabels the constraint |
| UG-R4 one walk, one home | Normative homes stay where UG2 and UG3 put them: the evolution contract ("Additive policy", "Population check", "Stable locators", "EvolutionOperation") and `representation-format.md` ("Unattended source"). Every UG4 page cites them |
| UG-R5, R6, R7, R8 | Not applicable: no reader, input, cost or import changes. Stated once, here |
| UG-R9 installer-owned links | No packaged file is added, renamed or removed, so the installer's link set is unchanged; `gnd doctor --project` is still in G-skills as a check |
| UG-R10 anonymity | G-anon over every changed file, the commit messages and the PR body |
| UG-R11 approval | this gate |
| project.md: totality, cap, validation order, one walk | not applicable (no code) |
| project.md: normative prose has one home | the central rule of this phase (UG4-C1) |
| project.md: contested representation by measurement | UG4-D4's guard measures the reference against the real parser instead of asserting it |

## 5. Goal

After UG4 a host reading the packaged skill can run the whole unattended loop with what
shipped: declare the round's document inside the round's proposal, validate with every
declared document under `--require-documents`, preview and apply under `--policy additive`
(with `--check-population` for a constraint on clean data), and act on a shape match in a
stated way. Every page that restates the additive guarantee says it holds relative to the
populations GND sees. The issue follow-ups are drafted for the owner.

## 6. Design (the edits, page by page)

**Homes and citers (UG4-C1).**

| Statement | One home (unchanged) | Pages that cite it after UG4 |
|---|---|---|
| The policy matrix, the strengthening list, the clean-population admission | evolution contract "Additive policy" and "Population check" | `evolve-policy.md`, `gnd-model-evolve/SKILL.md`, `unattended-growth.md`, `docs/agents/evolve.md`, `grow-a-model.md` |
| The source-document operation | evolution contract "Stable locators", "EvolutionOperation" | `unattended-growth.md`, `gnd-model-from-text/SKILL.md`, `evolve-policy.md` |
| Span counts and `--require-documents` | `representation-format.md` "Unattended source" | `unattended-growth.md`, `gnd-model-from-text/SKILL.md`, `cli.md` |
| The unattended round procedure, the shape-match procedure, the reply shape | `unattended-growth.md` (procedure home, not a rule home) | `gnd-model-from-text/SKILL.md`, `docs/agents/model-from-text.md`, `grow-a-model.md` |

### 6.1 `gnd-model-from-text/references/unattended-growth.md`

- **(a) Declaring the round's document** (retires the out-of-band step). In "What one round
  is", move 3 says the host's proposal opens with one `source-document` `add` for a document
  the model does not yet declare (its raw-bytes digest and a label), before the elements that
  cite it; a document already declared is not declared again (a second declaration of the
  same digest makes a later `modify` or `delete` of it ambiguous, UG3-Q2). One sentence says
  that before this operation shipped the host edited `source.documents` before the round, and
  that a declaration in the candidate with no operation is still refused. Cites the contract.
- **(b) The gate.** Move 4 becomes: `gnd validate MODEL --document DOC ... --require-documents`
  with every declared document supplied, then `gnd evolve preview --policy additive
  --shape-report` (plus `--check-population FILE` when the round adds a constraint on a fact
  type that holds facts), then `apply` with the same options. Cites "Unattended source" for
  the counts.
- **(c) Acting on a shape match** (UG-D6 (a), issue 76). A short subsection after the round:
  for each `existing` fact type the report names, the host does one of three things and logs
  which: reuse the existing id (drop the new fact type and re-point its facts), keep both with
  the reason in the new fact type's `provenance.rationale` ("returned via" is not "arrives
  via"), or keep both and record the doubt in `open_questions` for the consolidation round.
  Never a silent merge, rename or delete; a merge is the consolidation round's reviewed
  proposal.
- **(d) "Constraints on fact types that already hold facts"** (item 5, final answer). Replace
  "`--policy additive` offers no route" with the shipped route: `--check-population FILE`
  admits a new or strengthening-only constraint when it is `proposed` and `deontic`, every
  populated fact type it ranges over has facts in FILE and no sample rows, and its own verdict
  over FILE is `pass`; the admission holds relative to FILE and the constraint stays advisory.
  Otherwise, a reviewed non-additive proposal, as today. Cites "Population check".

### 6.2 `gnd-model-from-text/SKILL.md`, "Unattended mode" (pointer text only)

Two bullets change: the `source.documents` bullet adds "a growth round declares a new document
with a `source-document` operation in its `gnd evolve` proposal"; the validate bullet becomes
`gnd validate MODEL --document DOC ... --require-documents`. The "Unattended runs all of Steps 1
to 7" list gains "how a round declares its document and acts on a shape match". No rule is
restated.

### 6.3 `gnd-model-evolve/SKILL.md`, "The additive policy"

The first sentence ("must never invalidate facts it has already admitted") is qualified: the
policy judges the facts GND can see (sample rows, reference populations, `population`
artifacts, `--populated`, and the file given to `--check-population`). One added sentence names
the two later cells families by pointer: `--check-population` (clean-data admission) and the
`source_document.*` cells. The matrix stays in the contract.

### 6.4 `docs/agents/evolve.md`, "Additions only"

"refuses any round that would make earlier facts uninterpretable" gains "that GND can see",
and one sentence points at `--check-population` and at declaring a document, citing
`evolve-policy.md`.

### 6.5 `docs/agents/model-from-text.md`

The Unattended paragraph's last sentence adds "how a round declares its new document" to the
list of what `unattended-growth.md` says. Nothing else.

### 6.6 `docs/reference/evolve-policy.md`, the opening paragraph

"refuses a proposal that would make facts already admitted under the current model
uninterpretable" is qualified as in §6.3, with a link to its own "Admitting a constraint on
clean data" section. No matrix text is added.

### 6.7 `docs/how-to/grow-a-model.md` (UG4-D7)

Proposed (a): no new executed commands. Two cited paragraphs: after round 2, "A rule like
this one can still be admitted on clean data" with a pointer to `--check-population` in the
reference; in "When nobody reviews the model", one sentence that a round declares its new
source document in its proposal and validates with `--require-documents`, pointing at the
skill reference. The Recap table is unchanged (round 2 is still refused, as run).

### 6.8 `docs/release-notes.md` (UG4-D6)

Proposed (a): the Unreleased heading "model identity and plain text for projected reports"
becomes "model identity, projected text, and unattended growth", since the section now holds
the UG2 and UG3 entries. No entry is restated. The 0.2.0 sentence "remains open" stays: it
describes a published release (UG2's ruling).

### 6.9 Issue follow-ups (UG4-D2), new note `notes/ug4-issue-followups.md`

Drafted texts for the owner, each matching the UG1 matrix row it updates (UG4-C4):

- **#74:** the two items the posted comment left open are shipped: span counts with
  `--require-documents` (PR 149, UG3 part A) and the `source-document` operation (PR 149, UG3
  part B). Nothing in the issue's scope is open.
- **#75:** no follow-up (the posted comment said no open item).
- **#76:** the host's handling of a match is documented (§6.1 (c), this phase's PR).
- **#104:** item 5's second option is shipped (`--check-population`, PR 147, UG2); the
  procedure text says how to use it (this phase's PR). Items 1 to 4 unchanged from the posted
  comment.

Each names PRs and record paths, no downstream application. Posting is not part of this phase.

### 6.10 The evolution contract, "Additive policy" (one clause in the normative home)

The opening sentence "The policy keeps every fact already admitted under the current model
interpretable under the candidate" gains "that GND can see (sample rows, a declared reference
population, a `population` artifact, `--populated`; under `--check-population`, relative to
that file)". This is the one normative edit; every page in §6.3 to §6.6 then cites a qualified
home.

## Implementability sweep (author inspection, not review)

| Requirement | Can some edit satisfy it as written? |
|---|---|
| The procedure describes only shipped commands | Yes: `--require-documents`, `--check-population`, `--shape-report` and the `source-document` locator are all on main at `ad454305` |
| No page restates the matrix | Yes: every new sentence names a cell family and links the contract |
| The how-to stays executable | Yes under UG4-D7 (a): no `gnd-run` block changes, so `tools/run_tutorials.py --group growth` replays the same steps |
| The guard test (UG4-D4) can fail | Yes: it parses each `gnd …` command line in `unattended-growth.md` with the real parser; a misspelt or removed flag exits 64 (measured: `--require-documents` exited 64 on `5c6a0c5f`) |
| UG4-C5 is a predicate | Yes: `git grep -n -i "uninterpretable\|keeps every fact"` over `docs/` and `src/gnd/skills/`, each hit qualified. The contract's own sentence ("The policy keeps every fact already admitted under the current model interpretable", "Additive policy") is itself unqualified; only "Population check" says "relative to the supplied population". §6.10 qualifies it in place |

## 7. Decisions

| ID | Question | Readings | Proposed |
|---|---|---|---|
| UG4-D1 `(o)` 2026-11-09: as proposed | Approval instrument | (a) this spec's prose: a docs phase is none of the three shapes for which corpus-first is the default (serialized formats, exit-code contracts, validation predicates); (b) a corpus of page excerpts | **(a)** |
| UG4-D2 `(o)` 2026-11-09: as proposed | Issue follow-ups | (a) draft them in a note (§6.9); post only on the owner's later instruction, after merge; (b) post them as part of this phase | **(a)** (plan §7 and UG-D0) |
| UG4-D3 `(o)` 2026-11-09: as proposed | The "interpretable" wording | (a) qualify each restating sentence ("that GND can see") and link the contract; (b) delete the restatements and leave only links | **(a)**: the pages stay readable on their own |
| UG4-D4 `(o)` 2026-11-09: as proposed | A guard for the procedure's commands | (a) extend `tests/test_unattended_growth_guidance.py`: every `gnd` command line in a code span or block of `unattended-growth.md` parses with the real CLI parser (no 64), and the reference names `source-document`, `--require-documents` and `--check-population`; (b) prose only | **(a)**: about 30 test lines, catches the drift class the reference already had |
| UG4-D5 `(o)` 2026-11-09: as proposed | UG3-Q2 (a digest declared twice passes U1) | (a) document "declare each document once" in the procedure and leave UG3-Q2 to the close sweep; (b) a U1 rule refusing duplicates: a validation change for existing unattended models (UG-R1), code in a docs phase | **(a)** |
| UG4-D6 `(o)` 2026-11-09: as proposed | Release notes | (a) retitle the Unreleased heading only; (b) also merge the UG2/UG3 entries into one "unattended growth" block | **(a)** |
| UG4-D7 `(o)` 2026-11-09: as proposed | The how-to | (a) two cited paragraphs, no executed change; (b) a third executed round showing `--check-population` (fixture and tutorial-runner changes) | **(a)** |

## 8. Tests and verification ledger

| Test | Case | Expected |
|---|---|---|
| T1 (UG4-C1) | author table §6 checked against the diff: each new sentence cites its home | recorded in the record |
| T2 (UG4-C5) | `git grep -n -i "interpretable\|keeps every fact\|invalidate facts" -- docs src/gnd/skills` (at `ad454305`: `docs/agents/evolve.md:39`, `docs/reference/evolve-policy.md:4`, the contract `:229-230` and `:338`, `gnd-model-evolve/SKILL.md:125`) | every hit qualified (the contract's included, §6.10); release notes excepted as history; listed in the record |
| T3 (UG4-D4) | the new guard in `tests/test_unattended_growth_guidance.py` | passes; shown failing against a scratch copy of the reference with one flag misspelt |
| T4 | the existing guard file and the UG1 replay | pass unchanged |
| T5 (UG4-C4) | each follow-up text against the UG1 matrix and the UG2/UG3 records | author check, recorded |

| Gate | Disposition | Command |
|---|---|---|
| G-docs | run | `uv run python tools/run_tutorials.py --group growth`; `uv run --group docs zensical build --strict`; `uv run python tools/check_docs.py site`; `uv run pytest -q tests/test_documentation_tutorials.py` |
| G-skills | run | `uv run pytest -q tests/test_packaged_skills.py tests/test_skill_prose_sync.py tests/test_ik_close.py tests/test_public_binding_prose.py tests/test_install.py tests/test_doctor_uninstall.py tests/test_public_installer.py tests/test_ik6_skill_census.py tests/test_il6_skill_census.py`; `uv run gnd doctor --project` |
| G-ug | run | `uv run pytest -q tests/test_unattended_growth_guidance.py tests/test_unattended_model_growth_acceptance.py tests/test_unattended_mode.py` |
| G-lint | run | `uv run ruff check tests/test_unattended_growth_guidance.py` |
| G-components | run | `python3 scripts/components_index.py changed --base main --strict` (expected: nothing to fix; no module changes) |
| G-anon | run | UG1's digest-set method over the changed files, commit messages and PR body |
| Full tutorial run, full default lane, distribution, certification | cadence | not selected (no explicit request); the growth group is the only tutorial whose page changes |

## 9. Out of scope for this phase

- Any code change, including a U1 duplicate-digest rule (UG4-D5).
- Posting or closing issues (UG-D0, plan §7).
- UG3-Q1, UG3-Q3, UG2-Q1, UG2-Q2: they stay with the close sweep.
- The milestone close (record, question sweep, close review, close parity table).
- Moving UG1's private test helpers (owner's choice).

## 10. Size

About 80 to 120 lines of Markdown across ten files, one new note of about 40 lines, and
about 30 test lines (UG4-D4).

## 11. Approval instrument

Proposed UG4-D1 (a): the owner rules UG4-D1 to UG4-D7 on this text. Implementation starts only
after that ruling is recorded here.

## Revision history

- r1, 2026-11-09: first draft. Not reviewed.
- r1 ruled, 2026-11-09: all of UG4-D1 to D7 as proposed.
