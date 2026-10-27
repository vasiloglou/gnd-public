# Milestone close: induced knowledge — close spec r1

Date: 2026-10-27. `auto=false`. Skill: process-milestone (close).
Base: `b99dfec` (main, after PR #44). Branch: `claude/ik-milestone-close`.
**Draft; awaiting the owner's rulings in §6.** Nothing below is implemented,
reviewed or accepted.

## 1. Effective plan and authority

- Plan r4 (`notes/induced-knowledge-plan.md`), approved 2026-10-24 (record 001).
  Its header still reads "Draft; awaiting owner approval". The plan is never
  edited, so record 001 is the authority for its approval. This close record
  notes that the header is stale.
- Amendments: 004 (IK1-Q1, nesting cap 64) and 008 (IK5-Q1, facts bound 500,000).
- Close protocol, from plan §0 predicate 7 and §8:
  - four-reviewer close evidence, using the D7 instrument (four local reviewer
    agents, owner-selected 2026-10-23);
  - a question sweep;
  - a PR;
  - owner acceptance, recorded separately.

## 2. Readiness

| Phase | Spec gate | Record | Review | Merged |
|---|---|---|---|---|
| IK1 | 001 (r4) | 002 | one reviewer | yes |
| IK2 | spec §17–18 | 003; repair `evidence/IK2-repair/` | one reviewer | yes |
| IK4 | spec §18 | 005 | one reviewer | yes |
| IK3 | spec §16 | 006 | one reviewer | yes |
| IK5 | spec r1 gate | 007; amendment 008 | one reviewer | yes |
| IK4-Q2 | spec r1 gate | 009 | one reviewer | yes |
| IK6 | spec §13–14 | 010 | one reviewer | yes (PR #44, `b99dfec`) |

**Evidence bindings checked 2026-10-27:**
- Records 006–010 still match every file they bind.
- Records 002, 003 and 005 bind 10, 11 and 17 files that later phases edited.
  Those records describe their own bytes, so this is not a defect. The close
  binds the merged bytes.

## 3. Completion predicates (provisional, to be audited by reader one)

| # | Predicate | Provisional verdict | Evidence |
|---|---|---|---|
| 1 | IK1 descriptions | met | 002 |
| 2 | IK2 induced provenance and admission | met | 003, the IK2 repair |
| 3 | IK3 measure in two label modes | met | 006 |
| 4 | IK4 discover | met for models that evolve can preview | 005 C2 caveat; IK4-Q2 lifted the reference-population part (009); YAML-only values remain (IK4-Q3) |
| 5 | IK5 tool-neutral bridge, golden across two seeds | met; no learner ran | 007; IK5-Q5 open |
| 6 | IK6 public walk exits 0 at every step | met for the predicate's steps | 010. The walk also contains one deliberate exit 3 (the over-claim). That step is beyond the predicate and is documented on the page |
| 7 | per-phase approval, focused checks, review, refactoring review, record; close evidence | phase half met; close half is this work | 002–010 |

## 4. Proposed close sequence

1. **Owner rulings on §6.** These decide what the close fixes and what it
   carries forward.
2. **Close fixes.** Do each fix the owner selects, with its regression test
   shown red first. Log every fix in §7 of this spec.
3. **Close gate on the final bytes:**
   - the union of the phase gates (every test file named in records 002–010's
     gate commands, and every `test_rf*.py`);
   - the docs build (`zensical build --strict` and `tools/check_docs.py`);
   - `tools/check_installed_docs.py`, both wheel origins;
   - a full default-lane suite only if the owner rules C-G1 below.
4. **Four close readers (D7)**, each with fresh context and one lens, run on the
   final bytes:
   - **One, predicates:** does each predicate in §3 hold against the evidence?
   - **Two, ledger:** does every open-question row from 002–010 have a
     disposition, and do the records agree with each other and with the README?
   - **Three, evidence, honesty and privacy:** digests, sanitized paths, no
     downstream names (IK-R10, IK-R11), and claims that match the bytes.
   - **Four, newcomer:** an installed wheel, following the tutorial and its
     commands page.

   All four readers are the same model family, so no vendor diversity is
   claimed. Each finding is reproduced before anyone believes it.
5. **Owner decisions** on any reader finding that needs a ruling, as their own
   record.
6. **The close record**, the README update, a PR, and **owner acceptance**,
   recorded separately. Merge happens only on the owner's yes.

Running the readers after the fixes means they review the bytes that ship. The
alternative is the pyrel-agent-loop order: readers first, then decisions and
fixes. That costs a second check of the fixed bytes.

## 5. Question sweep

Every row from records 002–010, plus the rows that IK6 spec §3 lists as
inherited. "Small" means a guess of under an hour, with one regression test.
Sizes are estimates and have not been measured.

### 5a. Proposed: fix at the close

| ID | Question | Why now | Size |
|---|---|---|---|
| IK1-Q2 | Show annotations in text-format `gnd diff` | Targeted at the close since IK1 (IK6-D6). Today the text output hides a description change that the JSON output reports | small–medium; moves RF1 CLI goldens |
| IK1-Q5 | `evolution-contract.md` surface list omits `operation` | doc drift | small |
| IK2-Q2 | `rai_import._default_modality` copies the D-03 table | one-home rule IK-R4 | small refactor |
| IK3-Q2 | Case-insensitive file systems accept alias manifest paths, so the result depends on the host | Make it host-independent: refuse a spelling that differs from the on-disk name, with exit 3 as on Linux | small |
| IK3-Q4 | "model changed while it was read" has no failing case | shipment rule: a declared branch must have a case that can fail it | small (test only) |
| IK5-Q3 | Aggregates with a compound goal are named `unparsable`, not `aggregate` | refusal naming (IK5-C2 names each refused construct) | small |
| IK5-Q4 | `discover.output.candidate_text` writes YAML-unkept characters verbatim | a discover proposal could be written that does not round-trip | small |
| IK5-Q6 | Check 10's candidate reloads are not counted in the work counter | IK-R6 work-counter honesty | small |
| IK4-Q2-Q2 | Invalid candidate YAML exits 70; it should be a named exit 3 | a crash exit on user input | small |
| IK6-R1 | Exempt `src/gnd/examples/**` from the RF6 dynamic-query and RF7 parser scans by one rule; lift the walk normalization into the runner | ends per-example churn | small–medium; changes RF controls |

### 5b. Proposed: carry forward with a named target

| ID | Question | Proposed target |
|---|---|---|
| IK4-Q3, IK4-Q2-Q1, IK4-Q2-R1 | evolve and YAML-only values (dates); strict JSON for `.json` models; one load-then-bind helper | one **evolve-loading** follow-up PR. They touch the same five load homes, and Q1 refuses inputs that B accepts, which is a compatibility ruling |
| IK1-Q4 | Generated tools' runtime `__doc__` can forge a role line (pre-existing at B; the source text is safe) | a codegen hardening issue. The fix moves codegen goldens, so it is outside this milestone's surfaces |
| IK2-Q3 | Typed refusals in place of `_evolve_service_exit`'s substring mapping | the refactoring milestone that owns RF5 |
| IK3-Q5 | Merge the two measure `fail()` closures | after the RF5 shim retirement, as recorded |
| IK4-Q4, IK3-Q1 | Checker witness and role-unresolved message defects (pre-existing) | GND checker issues |
| IK4-Q5 | `test_prepared_policy_rechecks_live_hashability` fails on main | separate maintenance (owner-ruled); stays excluded from gates |
| IK1-Q3 | Normalize `gnd_version` in T7 row 4 | the next phase that bumps the version |
| IK5-Q2 | SWI octal escapes in Popper text | with IK5-Q5: no real Popper output has been seen |
| IK5-Q5 | A real Popper run | stays open; owner's call (installing Popper was declined) |
| IK6-Q1 | A packaged skill for the induction loop | its own milestone |
| IK4Q2-D3 | Lift the refusal that IK5's `gnd export ilp` gives for reference-bearing models ("IK6 or later", `phase-IK4-Q2-spec.md:100`) | an ILP-bridge follow-up, with IK5-Q5 |

### 5c. Proposed: accept as residual

| ID | Question | Reason |
|---|---|---|
| IK2-Q5 | `orm-meta` patterns accept a trailing newline (pre-existing; the induced block's loader already refuses one) | Fixing it refuses models that are valid at B, which is an IK-R3 compatibility break. A schema-version milestone could take it |
| IK3-Q3 | A constraint-free model cannot be measured in expected-state mode | Such a model has nothing to measure; the refusal is named. Document it in `measure-labels.md` |

**Closed earlier:** IK1-Q1 (004), IK2-Q1, IK2-Q4, IK4-Q1, IK4-Q2 (009), IK5-Q1
(008), C-F7.

## 6. Owner rulings requested

| ID | Decision | Proposed |
|---|---|---|
| C-D1 | The 5a fix list | fix all ten |
| C-D2 | The 5b targets | as listed |
| C-D3 | The 5c residuals | accept both; add the IK3-Q3 sentence to `measure-labels.md` |
| C-D4 | Order: readers after the fixes (§4) | yes |
| C-G1 | Close gate: union of phase gates plus docs and installed checks; or also one full default-lane suite | union plus one full default-lane suite as close evidence, run in the background. Failures that also fail on `b99dfec` are listed, not fixed |

## 7. Findings

(none yet)

## 8. Owner gate

**Approved by the owner 2026-10-27 (o):** "Approve close spec r1 with C-D1 to
C-D4 and C-G1 as proposed." The approved bytes are r1 as committed in `5283590`
plus the IK4Q2-D3 row, SHA-256
`be048c882f216dc8a59294e7d0c97a8136604297ce814bdbc06770ffe7350e2e`.
Sections 7 and 8 are append-only after this point.

- **C-D1:** fix all ten 5a rows at the close.
- **C-D2:** carry the 5b rows to the targets listed.
- **C-D3:** accept IK2-Q5 and IK3-Q3 as residuals, and add the IK3-Q3 sentence
  to `measure-labels.md`.
- **C-D4:** the readers run after the fixes.
- **C-G1:** the close gate is the union of the phase gates plus the docs and
  installed checks, plus one full default-lane suite.

## 9. Close-fix findings (appended after the gate, 2026-10-27)

Every fix has a regression in `tests/test_ik_close.py`. Against base `b99dfec`,
11 of those 13 tests fail (`evidence/close/regressions-red.txt`). The other two
pass on the base by design:
- the D-03 behaviour pin, which the IK2-Q2 refactor must keep;
- IK3-Q4, which adds only a test. That test fails when the check it covers is
  deleted from the source.

- **F1, IK2-Q2: the "one home" is prose.** The D-03 table lives in
  `provenance-and-modality.md`, and no code module holds it. Reading Markdown at
  run time would be fragile. Instead, the fix makes `rai_import` table-driven
  (`D03_DEFAULTS`), and a test parses the reference table and requires the two
  to be equal, row for row (12 rows). Its refusal messages and their order are
  unchanged.
- **F2, IK5-Q6: the ceiling's arithmetic, stated under IK-R12.**
  - Check 10 loads the candidate model once per clause, then twice for all K
    clauses together: K + 2 loads, now counted in `work.reloads`.
  - The import ceiling becomes P × (1 + K) + K + 2. Checks and verdict reads
    stay within the approved P × (1 + K). Only the new term was added, and C-D1
    ("count the reloads in the work counter") is the ruling it rests on.
  - `ilp-import.schema.json` gains an optional `reloads`, so earlier reports
    stay valid.
  - Two IK5 review tests had their expected ceilings moved: T9 by + 34, and R6
    from 24 to 29. Neither belongs to the approved IK5 corpus.
- **F3, IK4-Q2-Q2: three parse sites, not one.** A malformed candidate reached
  three readers:
  - `input_policy.guard_yaml`;
  - `gnd.model.load_model_bytes`, through evolve's `_load_model_bytes`;
  - evolve's own YAML load.

  Evolve's two wrappers now name the refusal: "<label> is not valid YAML at line
  L, column C", exit 3. `gnd.model` still lets ruamel's error escape to its
  other callers; `gnd validate` already maps that to 3.
- **F4, IK5-Q4: both output branches.** The JSON branch escapes each character
  YAML does not keep raw. The block-YAML branch, used only when a model holds a
  YAML-only value such as a date, now writes ASCII-only, because ruamel's
  emitter writes NEL raw and its reader then folds it. No committed golden
  moved.
- **F5, IK3-Q2.** Each path component's spelling is compared with its parent
  directory's listing. A case-insensitive alias is refused as "does not exist"
  (exit 3), the same result a case-sensitive file system gives.
- **F6, IK6-R1: scope.** Only `src/gnd/examples/**` is exempt, as ruled. The
  three standalone skill scripts stay listed in RF7. The rule's one home is
  `tests/support/scan_scope.py`, which checks that the layer map excludes the
  same glob.
  - The close RF6 successor (`evidence/close/dynamic-query-successor.json`)
    removes all 84 example rows (89 occurrences) and adds the six new
    non-example rows.
  - Rerunning its build script after the successor is registered recomputes the
    delta against the file itself, as the script's docstring warns. That
    happened once, and the delta was regenerated before any gate.
- **F7, a lint gap left by IK6.** Two `subprocess.run` calls in
  `tests/test_ik6_walk.py` lacked `check=` (PLW1510). They were already present
  on `b99dfec`, and are fixed here.
