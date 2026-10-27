# Close reader two: the open-question ledger and record consistency

Subject: branch `claude/ik-milestone-close` at `85880f5` (base `b99dfec`).
Lens: every ledger item has a disposition; §5 rows match their sources; records,
README and close spec agree; `85880f5` implements C-D1 plus the C-D3 sentence and
nothing else. Paths below are relative to
`.gnd-planning/milestones/induced-knowledge/` (call it `M/`) unless they start
with `src/`, `tests/`, `docs/` or `tools/`.

The repository was not modified. One throwaway probe script was written to the
scratchpad, run, and deleted.

## Ledger table

"5a/5b/5c" are close-spec §5 subsections. "Closed (cite)" means the close spec
lists the item under "Closed earlier", with the source of the ruling if the
close spec gives one.

### Numbered open questions

| Item | Source | Close-spec disposition |
|---|---|---|
| IK1-Q1 nesting cap | 002:271; 003:289 | Closed (004) |
| IK1-Q2 text diff annotations | 002:272 | 5a, fixed |
| IK1-Q3 `gnd_version` in T7 row 4 | 002:273 | 5b |
| IK1-Q4 runtime `__doc__` forging | 002:274 | 5b. Row narrowed, see finding 2 |
| IK1-Q5 contract omits `operation` | 002:275 | 5a, fixed |
| IK2-Q1 archived induced proposals | 003:284 | Closed. No ruling cited in the close spec (IK2 spec §18) |
| IK2-Q2 D-03 copy | 003:285 | 5a, fixed |
| IK2-Q3 typed refusals | 003:286 | 5b |
| IK2-Q4 confirmation stays on host | 003:287 | Closed. No ruling cited (IK2 spec §17) |
| IK2-Q5 trailing-newline patterns (S1) | 003:288 | 5c |
| IK3-Q1 role-unresolved message (C-F5) | 006:177 | 5b |
| IK3-Q2 case-insensitive aliases | 006:178 | 5a, fixed |
| IK3-Q3 constraint-free model | 006:179 | 5c. Rationale narrowed, see finding 11 |
| IK3-Q4 model-changed branch | 006:180 | 5a, fixed (test only) |
| IK3-Q5 two `fail()` closures | 006:181 | 5b |
| C-F7 X1 harness | 006:182 | Closed. No ruling cited (IK3 spec §16) |
| IK4-Q1 existing `--out` | 005:271 | Closed. No ruling cited (IK4 spec §18) |
| IK4-Q2 evolve with references | 005:272 | Closed (009) |
| IK4-Q3 YAML-only values in evolve | 005:273 | 5b. Overrides an owner ruling, see finding 3 |
| IK4-Q4 checker witness defect | 005:274 | 5b. Overrides an owner ruling, see finding 3 |
| IK4-Q5 hashability test | 005:275 | 5b |
| IK5-Q1 bounds disagree | 007:225 | Closed (008) |
| IK5-Q2 SWI octal escapes | 007:226 (target "milestone close") | 5b |
| IK5-Q3 aggregate naming | 007:227 | 5a, fixed |
| IK5-Q4 `candidate_text` | 007:228 | 5a, fixed |
| IK5-Q5 real Popper run | 007:229 | 5b. Row narrowed, see finding 4 |
| IK5-Q6 check-10 reloads | 007:230 | 5a, fixed |
| IK4-Q2-Q1 strict JSON for `.json` | 009:149 | 5b |
| IK4-Q2-Q2 invalid YAML exits 70 | 009:150 | 5a, fixed. One branch untested, see finding 1 |
| IK4-Q2-R1 load-then-bind helper | 009:151 | 5b |
| IK4Q2-D3 lift IK5 `references` refusal | notes/phase-IK4-Q2-spec.md:100; 009:141 | 5b |
| IK6-Q1 induction-loop skill | 010:181 | 5b |
| IK6-R1 exempt examples; lift normalization | 010:182, 010:154-156 | 5a, fixed (both parts) |

### Review dispositions, spec findings, boundary residuals and "seen but deferred" items without a question ID

| Item | Source | Close-spec disposition |
|---|---|---|
| IK1 review R3 / R7 | notes/phase-IK1-agent-review.md:23,27 | through IK1-Q1 and IK1-Q2 |
| IK1 description can restate a constraint, and the docs do not warn | 002:256-258; IK1 review :101 | MISSING (recorded boundary only) |
| IK1 `gnd export pyrel --rules duckdb` on `pyrel-oracle/basics` exits 70, `export failed: 'id'` (pre-existing) | notes/phase-IK1-agent-review.md:132 | MISSING |
| IK1 known red: `ruff check src`, I001 in `expense_cli.py` | 002:178-180 | MISSING (still red, see finding 9) |
| IK1 codegen linear scan, "no row is needed" | 002:240-243 | explicitly no row; fine |
| IK2-D5 single-token residual | 003:269-270; IK2 spec :232, :400 | ruled at the IK2 gate (spec §13). Not in "Closed earlier" |
| IK2 §15 residual: real learner output fits the block | 003:271-272; IK2 spec :615-617; 007:201-202 | only implicit in IK5-Q5. The row drops it (finding 4) |
| IK2 R4 | 003:216-217 | through IK2-Q1 |
| IK2 F7 (`..` inside a segment) | IK2 spec §16 F7 | "the approved grammar stands"; fine |
| 004 evolve window at about 60-64 levels | 004:45-47, :55-57; IK4 spec §18 | owner-ruled residual (IK4 spec §18). The close spec cites only "IK1-Q1 (004)" |
| IK3 R8: refusals redacted under a redacting model | IK3 review :23; 006:163-165 | accepted at review; fine |
| IK3 review: a directory as manifest gives 66 | IK3 review :57 | MISSING. In fact fixed (now exit 3), see finding 10 |
| IK3 review: `gnd check` on a FIFO hangs (pre-existing) | IK3 review :56 | MISSING |
| IK3 R10: "unreachable branches are argued unreachable in the record" | IK3 review :25 | not argued in 006 (finding 10) |
| IK3 C-F3: the 10,000 bound is unreachable | 006:166-167 | owner-ruled C-F3; fine |
| IK3 RF1 measure goldens captured on 3.14 only | 006:168-169 | MISSING (boundary only) |
| IK4 F8: recapture differences not applied | IK4 spec §16 F8 | MISSING (minor) |
| IK4 R13 mutant D12 (derived skip disabled) | IK4 review :136 | not stated as killed; see finding 10 |
| IK4 F17 | IK4 spec §17 | through IK4-Q4 |
| IK4-Q2 R4: binder defect reported as 3 | 009:105, 135-136 | through IK4-Q2-R1 ("where R4 lives") |
| IK4-Q2 R4 cosmetic: `ReferenceInputError` wrapped twice | IK4-Q2 review :48-49 | MISSING (cosmetic) |
| IK5 review "not checked": `type(wrong,(ex,))`, `direction` declarations | 007:198-200 | through IK5-Q5 |
| IK5 RF1 3.11 goldens derived from a 3.12 capture | 007:215 | MISSING (boundary only) |
| IK6 join space never exercised | 010:164-166 | MISSING (boundary only) |
| IK6 goldens move on a version bump | 010:170-171 | accepted at review; same class as IK1-Q3 |
| IK6 H4 minor: a census reason containing a pipe or a back-ticked path reports `missing:` | IK6 review :20 | MISSING (no disposition) |
| IK6 F12 | IK6 spec §14 | through IK6-R1 |
| Plan-review residuals (R1-F3, R1-F6, P-1..P-9) | notes/plan-review-r2-disposition.md:48-50, 151-161 | discharged by r3 and the phase specs; fine |

## Findings

### 1. Hardening: one of the two new IK4-Q2-Q2 refusals has no failing case, and it names the wrong model

**Claim.** Finding F3 (close-spec.md:187-195) says "Evolve's two wrappers now name the refusal". `test_ik4_q2_q2_invalid_candidate_yaml_is_a_named_exit_3` (tests/test_ik_close.py:168-185) reaches only the `_load_model_bytes` branch. In preview the candidate is loaded by `_validated_candidate` before `_parse_model_text` runs (src/gnd/evolve/service.py:1279-1283).

The `_parse_model_text` branch (service.py:230-240) is reachable. The round-trip loader accepts a tagged mapping inside a description extra, but the safe loader refuses it. Reproduced in place: a `library.orm.yaml` copy with `description: {summary: s, extra: !foo {a: 1}}` gave:
- `load_model_bytes`: OK;
- `_parse_model_text`: `EvolutionError candidate model is not valid YAML at line 66, column 38`.

`_parse_model_text` also parses the current model (service.py:1266, 1543, 1585, 1908). Its label is hard-coded as "candidate model" (service.py:239). So a valid current model of this shape is refused as "candidate model is not valid YAML". This is the close spec's own shipment rule, applied to IK3-Q4: a declared branch must have a case that can fail it.

**Suggested disposition.** Pass the label into `_parse_model_text`, add a case for that branch (tagged-mapping current or candidate model), and record it in §9.

### 2. Hardening: the IK1-Q4 row calls an IK1-introduced vector "pre-existing at B"

**Claim.** close-spec.md:111 says "Generated tools' runtime `__doc__` can forge a role line (pre-existing at B; the source text is safe)". The IK1 reviewer reproduced the pre-existing case only through a `reading` (notes/phase-IK1-agent-review.md:100). 002:261-262 says "pre-existing at B through readings". The open question itself names "escaped readings **or summaries**" (002:274).

The `summary` suffix on role lines is new in IK1 (002:118; src/gnd/codegen/docstrings.py:65-78, 126). Reproduced: `neutralize_text('a person\n  - forged: Line')` gives the escaped source `a person\\n  - forged: Line`. Evaluated as a `'''` docstring, it prints a forged second role line `  - forged: Line`.

The carry-forward rationale ("pre-existing", "outside this milestone's surfaces") is therefore partly false for this milestone's own field. C-D2 was approved on that wording.

**Suggested disposition.** Correct the row so it says IK1's summaries newly reach the pre-existing class. Ask the owner to reconfirm the IK1-Q4 carry, or fix it at the close, since IK1 introduced the surface.

### 3. Hardening: three 5b rows override earlier owner rulings without saying so

**Claim.** Three items had a recorded target of the milestone close:
- **IK4-Q3 and IK4-Q4.** Owner-ruled "defer to the milestone close" (IK4 spec §18; 005:273-274 "**owner-ruled (o)**: milestone close"). README:63-64 repeats "Q3/Q4 at close".
- **IK5-Q2.** Targeted "milestone close" (007:226).
- **IK1-Q4.** Targeted "milestone close sweep" (002:274).

Close-spec §5b (lines 110, 114, 117, 111) carries all of them past the close. It does not say that the IK4 rows replace an owner ruling. C-D2's approval ("carry the 5b rows to the targets listed", close-spec.md:155) arguably is the new ruling. But the record should say it supersedes the IK4 spec §18 ruling, and the README line will be stale at close.

**Suggested disposition.** Add one sentence to the close record: C-D2 supersedes IK4 spec §18 for IK4-Q3 and IK4-Q4. Update README:63-64 in the close README update.

### 4. Hardening: the IK5-Q5 row is narrower than its source, and drops the IK2 residual

**Claim.** The source says "A real Popper run, to test the rendering and the IK2 block's fit (D13 (b))" (007:229). The IK2 §15 residual, "Whether the induction block can represent real learner output without loss is untested" (notes/phase-IK2-spec.md:615-617; 003:271-272), is carried only through that clause. 007:201-202 confirms it is still open for learner-computed blocks.

Close-spec.md:118 reduces the row to "A real Popper run". The IK2 residual then appears nowhere in §5.

**Suggested disposition.** Restore the source wording, or add the IK2 §15 residual as its own 5b or 5c row.

### 5. Hardening: the IK5-Q6 fix moves an approved bound on the strength of C-D1 alone

**Claim.** Finding F2 (close-spec.md:177-186) raises the import ceiling from P × (1 + K) to P × (1 + K) + K + 2 (src/gnd/export/ilp_service.py diff; docs/reference/ilp-bridge.md:191). Two IK5 test ceilings also move (tests/test_ilp_bridge.py:370, 525).

IK-R12 says bounds move only by owner ruling. IK5 records "No bound was moved after implementation" (007:141), and 008 shows a bound change done as its own amendment. C-D1's text is "fix all ten 5a rows", and the 5a row says only "count the reloads". The owner did not see the new ceiling formula. F2 itself says C-D1 "is the ruling it rests on".

**Suggested disposition.** Put the new ceiling and its arithmetic in front of the owner as an explicit ruling, as 008 did for IK5-Q1. Or record it as an amendment row.

### 6. Hardening: close-spec internal inconsistencies after the gate

**Claim.** Each of these is reproducible by reading the file:
- **Stale header.** close-spec.md:5-6 still reads "Draft; awaiting the owner's rulings in §6. Nothing below is implemented, reviewed or accepted". §8 records approval and §9 records implemented fixes.
- **Fix log in the wrong section.** §4 step 2 (line 57) says "Log every fix in §7 of this spec". §8 (line 152) says sections 7 and 8 are append-only. But §7 still reads "(none yet)" (line 144), and the fixes went into a new §9. A reader of §7 sees no findings.
- **Confusing approved-bytes wording.** §8 (lines 149-151) says the approved bytes are "r1 as committed in `5283590` plus the IK4Q2-D3 row". `git show 5283590:<close-spec>` hashes to `be048c88…7e2e`, the stated digest. So the row was already in `5283590`, and "plus" suggests bytes that are not in the commit. The hash is correct; the wording is not.
- **"Spec gate" column cites later rulings.** §2 cites the last ruling section, not the gate:
  - IK2: "spec §17–18". The gate is IK2 spec §13, the corpus approval §15.
  - IK4: "spec §18". The gate is §13.
  - IK3: "spec §16". The gate is §13; §16 is the C-F7 ratification.

**Suggested disposition.** In the close record, state the current status. Point §7 to §9 with an appended line, as the append-only rule allows. Correct the §8 wording and the §2 gate column there too.

### 7. Completeness: the skill census does not record the close's packaged-skill edit, and its test cannot see it

**Claim.** `85880f5` edits `src/gnd/skills/gnd-model-evolve/references/evolution-contract.md` (IK1-Q5). The census row still reads "IK1, IK2, IK4-Q2" (skill-census.md:36). The census test passes: `uv run pytest -q tests/test_ik6_skill_census.py::test_t4_each_changed_cell_names_the_phases_git_records ...::test_t4_the_changed_cells_agree_with_git` gave `2 passed`. That is because its phase regex is `IK[1-6](?:-Q\d+)?` (tests/test_ik6_skill_census.py:11), and the commit scope "IK-close" never matches.

The census claims to record what the milestone changed in each file and why (010:75-77).

**Suggested disposition.** Add "close (IK1-Q5)" to that row in the close record or README update, or let the test's phase pattern accept the close scope.

### 8. Completeness: the close fix commit includes one change outside C-D1 and C-D3

**Claim.** `git show 85880f5` touches only the ten 5a rows, the C-D3 sentence (docs/reference/measure-labels.md:39-41), their direct consequences, and evidence:
- consequences: `diff.reference.md`, `ilp-bridge.md`'s work row, `ilp-import.schema.json`, two `test_ilp_bridge.py` ceilings, the RF6 successor registration in `tests/support/pyrel_application_successors.py`, and `tests/support/scan_scope.py`;
- evidence: under `evidence/close/`.

The one exception is F7: `check=False` added to two `subprocess.run` calls in `tests/test_ik6_walk.py` (diff hunks at :160, :167). It is a lint fix, not a C-D1 row. It is disclosed in §9 F7 (close-spec.md:214-216), so nothing is silent. It is still outside the approved scope.

Every C-D1 row has a regression in `tests/test_ik_close.py`. There are 13 tests, and 11 are red on base per `evidence/close/regressions-red.txt:3-14`:

| Row | Regression |
|---|---|
| IK1-Q2 | :199 |
| IK1-Q5 | :215 |
| IK2-Q2 | :33, :40 |
| IK3-Q2 | :55 |
| IK3-Q4 | :72, with a mutant at regressions-red.txt:17-19 |
| IK5-Q3 | :109, :117 (all three source forms: conjunction, negation, comparison) |
| IK5-Q4 | :130 |
| IK5-Q6 | :143 |
| IK4-Q2-Q2 | :168 (one of two branches, finding 1) |
| IK6-R1 | :223, :233 (both parts) |

The C-D3 sentence has no test, as expected for prose.

**Suggested disposition.** Note in the close record that F7 was outside C-D1 and was accepted by disclosure, or ask the owner to ratify it.

### 9. Completeness: IK6's lint gap is wider than F7 says, and the IK1 known red was never ledgered

**Claim.** `uv run ruff check --no-cache --output-format concise src` gives two errors:
- `src/gnd/examples/refunds/stand_in_learner.py:60:17: PLC0206`. It is the same on `b99dfec` (checked with `git show b99dfec:… | ruff check --stdin-filename …`). It is IK6's own new file. 010 records no lint run at all.
- the IK1-recorded `expense_cli.py:3:1: I001` (002:178-180). No later record or the close spec disposes of it.

F7 calls itself "a lint gap left by IK6" and names only the test file. The ruff check over the files `85880f5` changed passes.

**Suggested disposition.** Add both to the ledger (fix, or residual with a reason). Correct F7's scope.

### 10. Completeness: review items that no record or close row disposes of

Each item below is cited. None is blocking.
- **pyrel duckdb export.** IK1 review: `gnd export pyrel --rules duckdb` on `tests/fixtures/pyrel-oracle/basics.orm.yaml` exits 70, `export failed: 'id'`, pre-existing (notes/phase-IK1-agent-review.md:132). There is no disposition anywhere. I did not reproduce it, because the command writes an output file.
- **FIFO hang in `gnd check`.** The IK3 review says "`gnd check` on a FIFO also hangs, so this predates IK3" (notes/phase-IK3-agent-review.md:56). There is no disposition.
- **Directory as manifest.** The IK3 review says it gives 66 (notes/phase-IK3-agent-review.md:57), with no disposition. Reproduced now: `uv run gnd measure src/gnd/examples/refunds/model.orm.yaml --labels src/gnd/examples/refunds` gives `ERROR: label manifest … is not a regular file`, exit 3. So R1's fix resolved it, but nothing records that.
- **Unreachable branches.** The IK3 review disposition says they "are argued unreachable in the record" (notes/phase-IK3-agent-review.md:25). 006 contains no such argument (`grep -n unreachable 006-phase-IK3.md` finds nothing). Only the reviewer's text argues it (notes/phase-IK3-agent-review.md:105).
- **IK4 R13 mutant D12.** The reviewer lists D12 (the derived and semiderived skip disabled) among the surviving mutants (notes/phase-IK4-agent-review.md:136). The disposition and 005:177-178 claim kills for D1, D3, D7 and D11 only ("4 of 4"). D12 is described only as "recorded as intended (F14)", and no record says it is killed.
- **IK4-Q2 parameter name.** The disposition says "The parameter name is recorded in the record" (notes/phase-IK4-Q2-agent-review.md:89). It is in spec §16 (notes/phase-IK4-Q2-spec.md:236), not in 009.
- **Minor unledgered items:**
  - IK6 H4 minor: a pipe or a back-ticked path in a census reason (notes/phase-IK6-agent-review.md:20);
  - IK4-Q2 double `ReferenceInputError` wrap (notes/phase-IK4-Q2-agent-review.md:48-49);
  - IK4 F8 unapplied recapture differences.

**Suggested disposition.** One "accepted residuals and review leftovers" list in the close record, each item marked fix, carry or accept.

### 11. Completeness: smaller row-to-source mismatches in §5

- **IK3-Q3** (close-spec.md:127). The rationale says "Such a model has nothing to measure". The source finding contrasts the two paths: "The synth path measures it" (notes/phase-IK3-agent-review.md:96). The fixture `tests/fixtures/derivation/cases/a01-string-arm.orm.yaml:103` has `constraints: []`. So the residual is an inconsistency between paths, and the row should say so.
- **IK3-Q2** (close-spec.md:98) says "alias manifest paths". The source is population path spellings inside a manifest (006:178; review :95). The fix is in `_population_bytes` only (src/gnd/measure/labels.py:305-312). The wording invites reading it as the manifest's own path.
- **IK5-Q3** (close-spec.md:100) says "compound goal". The source names conjunction, negation or comparison (007:227). The fix and test cover all three, so this is wording only.
- **IK1-Q2 size.** 5a (close-spec.md:95) and IK6-D6 (notes/phase-IK6-spec.md:226) both predict that IK1-Q2 "moves RF1 CLI goldens". The fix moved none, and §9 does not record this.
- **"Closed earlier" citations** (close-spec.md:129-130) give no ruling source for:
  - IK2-Q1 (IK2 spec §18);
  - IK2-Q4 (IK2 spec §17);
  - IK4-Q1 (IK4 spec §18);
  - C-F7 (IK3 spec §16).

  It also omits the IK2-D5 residual (IK2 spec §13) and the 004 evolve-window residual (IK4 spec §18), both of which owner rulings closed.

### 12. Completeness: the README lags the records it indexes

- README:7 still labels the IK1 spec "draft".
- README:8-11 link the specs only up to IK5. The IK4-Q2 spec, the IK6 spec and close-spec.md are not linked.
- README:83 lists "IK4-Q2-Q1 and Q2" as open and omits IK4-Q2-R1 (009:151).
- README:61-64 (IK4) and README:85-89 (IK6) give no gate result. The IK4 gate was exit 1 with one pre-existing failure (005:9-10).

The close README update is the natural place for all four.

### Checked and consistent

- **Evidence bindings.** I recomputed every record's front-matter path and SHA-256 pairs against `git show <ref>:<path>`:
  - at `b99dfec`: 002 has 10 mismatches, 003 has 11, 005 has 17, and 006-010 have 0. This exactly matches close-spec §2 (lines 34-38).
  - at HEAD: 002 adds `src/gnd/diff.reference.md` and 003 adds `src/gnd/rai_import.py` (both edited by the close).
- **Test counts.**
  - Gate counts in the README match the records: 2309, 4003, 4366 (`evidence/IK2-repair/final-gate.txt`), 4360, 4473, 3162.
  - The census has 65 rows, matching 010:75 and README:86.
  - The 13 close tests and "11 of 13 red" in §9 match the file and `regressions-red.txt`.
  - F6's "84 rows (89 occurrences) removed, 6 added" matches `evidence/close/dynamic-query-successor.json`, summing `removed[*][3]` and `added[*][3]`.
- **Dates and statuses.** The record dates and owner-ruling dates across 001-010, the README and the close spec agree. Every phase in close-spec §2 has a merge on main (`git log --merges 1d6eee0..b99dfec`). The plan's stale "Draft; awaiting owner approval" header is expected, and the close spec notes it.

## What I did not check

- I ran no full suite or gate (a gate was running concurrently). I ran only two census test nodes and ruff.
- I ran no mutants. In particular, I did not check whether IK4 mutant D12 or the IK3-Q4 removed-branch mutant is killed. For the latter I relied on `regressions-red.txt`.
- I did not reproduce the IK1 pyrel duckdb exit 70, because it would write an output file.
- I did not verify the predicates (reader one), the digests and privacy (reader three), or the newcomer path (reader four).
  - One observation for reader three: several committed review notes keep a full absolute scratch path containing the local user's home-style prefix. Examples are notes/phase-IK2-agent-review.md:42, notes/phase-IK4-agent-review.md:53 and notes/phase-IK5-agent-review.md:17. I did not judge this against IK-R10 or IK-R11.
- I did not read the plan-review reader notes (r1 and r2, readers 1-4) line by line. I relied on their two disposition files, which are their ledger.
- I did not read the evidence directories beyond the IK2 repair gate, the close evidence and the census.
