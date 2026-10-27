# Round 2, reader 1 -- semantics and admission safety

Retained text of the reader's returned report. Local edits: scratch paths read
`<scratch>`; headings demoted one level.

## Digest check

- `induction-skill-plan.md.snapshot`: 7329cbd216d91a00f10b5b480a4fdaa22f7e7f62a0110913aba7079e28dbc3df. **Matches.**
- `phase-IS1-spec.md.snapshot`: f81590b028fd6fca80eafd7b743ccc7868883a181232b5080c3972aee141f938. **Matches.**

**Verdict: approve-with-fixes**

I found no new blocking finding. All seven round-1 findings are resolved. I found five new findings, two hardening and three completeness. All five are **self-inflicted**: they come from r2's own edits, three of them from the Popper-branch wording.

Scope:
- I read both snapshots in full, plus my round-1 note and the disposition.
- I read `docs/reference/ilp-bridge.md`, `stand_in_learner.py`, `docs/how-to/learn-rules-commands.md` (section 6) and `gnd-orm-core/references/population-format.md` (the exit bands).
- I read the `--help` of check, measure, discover, `export ilp` and `import ilp-rules`.
- I searched `src/gnd/skills` for every proposed one-home sentence and every routing regex.
- Probe: `gnd check model.orm.yaml batches/market.yaml` on a copy under `<scratch>/refunds` exits 0.
- I wrote nothing in the repository.

## Round-1 status

| Finding | Status | Evidence |
|---|---|---|
| R1-F1 agent-edited rule credited to the learner | resolved (the Popper exception leaves residuals, R1-N2 and R1-N3) | plan 93 (IS-R11), 194-195, 359; spec 131 (R-b), 146-149 |
| R1-F2 label manifest rewritten or re-bound | resolved | plan 93, 187, 196-197, 233, 429; spec 118 (schema "read only"), 122 (a stale manifest goes back to the user), 132 (R-c) |
| R1-F3 R-g git denial not unique | resolved | spec 139-141 drops the git denial from the one-home set and pins it through `RECORD_ROUTES`; plan 205-206, 263-265. None of the eight R-a..R-h sentences, nor any of the new trigger or boundary regex texts, occurs in `src/gnd/skills` today (searched) |
| R1-F4 measure overwrites `--out` | resolved | plan 180-184; spec 117 (confirm the path is new) and 122 (exit 11 limited to discover, export and import). Matches each command's `--help` |
| R1-F5 R-c weaker than D5 | resolved, but the new wording contradicts its own example (R1-N1) | plan 84, 199-200, 431; spec 134 (R-e) |
| R1-F6 R-f against verbatim reporting | resolved | plan 87, 203-204; spec 137 (R-h: "chat read-back may show them"). It now conflicts with the Popper exception (R1-N2) |
| R1-F7 discover with EMITTED 0 | resolved | plan 173; spec 55-57, 119 and 123 ("only after exit 0 with something emitted"). Matches discover `--help`: "Exits 0 on success (also with nothing emitted)" |

## New findings

**R1-N1** (hardening, high confidence, self-inflicted). **R-e's new wording forbids the evaluation the plan itself gives as the example.**
- Where: plan 84 (IS-R2) and 431 (D5); spec 134 (R-e) against spec 148.
- Evidence:
  - The rules now say covered sets come "never from any gnd command's output" (spec 134; plan 84 and 431 say the same).
  - The approved example evaluation is "Prolog over `bk.pl` and `exs.pl`" (spec 148; plan 431).
  - Those two files are written by `gnd export ilp` (ilp-bridge.md:49-50).
  - Read literally, the rule bans the example. An agent following it to the letter would refuse, or the rule gets ignored.
- The ban is meant for GND's verdicts, and the r1 circular route went through them: the import's refusal text, and check or measure over a scratch model.
- Fix: "never from a GND verdict: the output of `gnd import`, `gnd check`, `gnd measure` or `gnd discover`, including refusal text". Keep the export files allowed as evaluation input.

**R1-N2** (hardening, high confidence, self-inflicted). **The Popper exception cannot be carried out under R-b and R-h as written.**
- Where: spec 131 (R-b), 137 (R-h), 146-149; plan 87 and 93.
- Evidence:
  - For `--target popper`, CLAUSES "is ... Popper's printed program" (ilp-bridge.md:85). The skill has to save that stdout to a file. That is writing a learner's clauses, which R-b forbids; R-b's exception covers only the run record.
  - The assembled run record holds `coverage[].covered`, which are the manifest's example ids (ilp-bridge.md:89-93). The captured program holds host constants.
  - R-h forbids copying host values "into a file it writes". The exception's own steps break two sibling refusals.
- Fix:
  - Widen R-b's exception: "except to save a learner's printed program verbatim as CLAUSES and to assemble a Popper run record as stated below".
  - Exempt from R-h "the learner artifacts R-b lets it save or assemble, kept in the user's working paths".

**R1-N3** (hardening, medium confidence, self-inflicted). **An assembled Popper run record is admitted under Popper's name with no durable mark that the skill assembled it.**
- Where: spec 146-149 ("says that it assembled it"); plan 93.
- Evidence:
  - `provenance.induction.inducer` is "the run record's learner" (ilp-bridge.md:164).
  - The run-record schema has only `learner.name` and `learner.version` (89-93). Nothing in it can say that the covered sets came from an agent-run evaluation.
  - The disclosure is chat-only. The `gnd-model-evolve` reviewer sees `inducer: popper/<v>`.
  - The plan never says where `learner.version` comes from. The skill would choose it.
  - GND's set comparison still guards that the covered sets are correct. What is misattributed is who made the coverage claim.
- Fix:
  - The handoff message names each assembled run record, the evaluation that produced its sets, and the fact that `inducer` names Popper because the program is Popper's.
  - `learner.version` is Popper's own reported version, or is asked of the user, never invented.
  - T8 pins the handoff sentence.

**R1-N4** (completeness, high confidence, self-inflicted; the re-check intent is new in r2). **The reactions table does not fit `gnd check`.**
- Where: spec 121-122; plan 175 and 186-189.
- Evidence:
  - The table says "The meaning of each exit is in that command's `--help`", but `gnd check --help` states no exit meanings (read in full).
  - Check's exits are verdict bands, in the precedence 3 > 1 > 4 > 2 > 0 (population-format.md:215; exit 1 is fail, 2 vacuous, 4 indeterminate). The how-to pages record `gnd check: exit 1` as an ordinary result (lease-schedule.md:87).
  - So exit 1 is a finding, not "any other non-zero → stop". Exit 3 here is a load error, not a "named refusal", and the table's stale-manifest clause does not apply.
- Fix:
  - For check, cite `../gnd-orm-core/references/population-format.md`, which the skill already links (spec 181).
  - Add the reaction "check exits 1, 2 or 4: report the verdicts verbatim; it is a result, not a refusal".

**R1-N5** (completeness, medium confidence, self-inflicted). **The plan and the spec flag host data in value candidates at different points.**
- Where: plan 87 (IS-R5: "flagged at handoff") against spec 119 (at the Discover read-back) and 123 (the Hand off row has no flag).
- Evidence: discover writes the values themselves into a value-family proposal (discover.md:32, cited in round 1). If the flag is given only at the read-back, it is gone by the time the proposal reaches `gnd-model-evolve`.
- Fix: add the flag to the spec's Hand off row (spec 123), or align IS-R5 with the read-back.

## Note for the stop rule

This reader's count is 7 in round 1 and 5 in round 2. All 5 are self-inflicted (ratio 5/5), and the ceiling falls from blocking to hardening. That meets the plan's stop rule (plan 390-393): carry the fixes into the IS1 spec gate rather than run another round.
