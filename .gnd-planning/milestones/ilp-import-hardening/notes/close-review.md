# Close review: four readers (verbatim, sanitized)

> Retained by the author. Four general-purpose agents read the whole
> milestone, `git diff fb03739` of the working tree on `4389b61` with IH2's
> uncommitted work, each with its own emphasis (IH-D6 (a): the repository's
> close bar). Each returned its report as message text, because the harness
> refuses report files from subagents. The text is otherwise verbatim.
> **Edited:** the session scratch path is written `<scratch>`, a private
> host name `<host>`, and the user-name strings and home roots that
> reader 3 quoted `<user>` and `<home-root>`. The subject changed under reader 1 while it
> read (it says so). The repairs made after these reports carry no review
> opinion. Dispositions are in `../005-milestone-close.md`.

---

## Reader 1: end-to-end correctness of the AMIE export and mined import

**Verdict: request changes.** One blocking finding: exit 70 can still be reached on validated input, through the diamond shape that IH2 says it fixed. There are also two smaller issues.

**The subject changed while I was reviewing it.** The working tree was edited mid-review: `ilp_amie.py` gained the "close H1" relaxation, `seen.add(kinds)` replacing `seen.update(kinds)`; the docs row and `tools/ilp_comparison.py` changed; and `tests/test_ih_close.py` and `evidence/close/` appeared. I judged the current bytes:
- `src/gnd/export/ilp_amie.py`: MD5 `7fe4d529240894d3692611d453102478`
- `src/gnd/export/ilp_service.py`: MD5 `14018e3cbe5a2418d23aeac632306a20`
- `tools/ilp_comparison.py`: MD5 `2b72259cfb9003465b4e1e9a5bb48869`

To show what the earlier IH2 bytes did, I rebuilt them in scratch ("prev"). Everything below was compared against `fb03739`, extracted with `git archive` into scratch and run via PYTHONPATH.

**Harness:** `uv run python <scratch>/close/r1/bin/harness.py MODEL POP RULES [old|new]`. It runs `export ilp --target amie`, then `import mined-rules` with a correct run record. Fixtures are under `<scratch>/close/r1/cases/`.

### Findings

**1. Blocking: exit 70 inside a family that holds an own-reference subtype.**
- **Location:** `ilp_amie.mapped`, the `own-reference-join` loop, after the close H1 change. It now compares a variable's primitive *sets* across occurrences, not their union.
- **The gap:** a type that inherits from both an own-reference subtype and its supertype has the set {Integer, String}. Its values `1` and `"1"` both spell `manager:1`. The count therefore meets them, but the checker does not.
- **Case (a): one type.** `dd-mixed` is `diamond.orm.yaml` plus `leads(director, team)` and `heads(director, team)`, with population `leads {director: 1}` and `heads {director: "1"}`. Rule: `?a f_leads ?b => ?a f_heads ?b`, Support 1.
  - Observed: export exits 0; import exits 70 with `internal: constraints[0] holds by GND's count but the checker says 'warning'`.
  - The prev IH2 bytes give exit 3, `own-reference-join`.
  - `fb03739` also gave 70, so the milestone fixed this and the close H1 change undid it.
- **Case (b): two types.** `dd2` is the same model with a second type `director2` under both manager and staff. `leads(director: 1)`, `heads(director2: "1")`. Current: exit 70. Prev: exit 3.
- **Expected vs actual:** expected exit 3 with a named refusal; actual exit 70. The release note says this shape "could exit 70 … The exit is now 3", which is false for both cases. The new docs sentence "A variable over one type joins nothing and is not refused" describes exactly case (a).
- **Suggested fix:** refuse any variable whose occurrences hold a primitive set with more than one element, as well as differing sets.

**2. Hardening, likely to be carried: the same exit 70 with no own-reference subtype at all.**
- **Case `tops`:** `x` (String reference) and `y` (Integer reference) are unrelated top types; `d` is a subtype of both, inheriting its reference. Facts `leads(d: 1)` and `heads(d: "1")`.
- **Observed:** export 0, then import 70, both at `fb03739` and now. It is the same spelling collapse, but outside IH2's literal own-reference scope.

**3. Hardening, a regression from `fb03739`: a false refusal for Integer/Number.**
- **Case `diamond-int-number`:** like the diamond fixture, but `staff_code` is Integer and `manager_no` is Number, with int values. Rule: `?a f_manages ?b => ?a f_works_in ?b`, Support 2.
- **Observed:** `fb03739` exits 0 and admits the rule (the checker agrees). Now it exits 3 with `own-reference-join: variable ?a joins references of Integer and Number`.
- **Why it is false:** the check compares primitive names, not how values compare. Integer and Number values compare equal in the checker.
- The release note says only false `support-mismatch` and exit-70 cases change. This case, and any diamond where the manager–staff sets differ but the values agree, was admitted before and is now refused.

**4. Completeness: the docs row is narrower than what is refused.** Two shapes are refused by this name that the "Importing mined rules" row does not describe as an own-reference subtype joined with its supertype:
- **Sibling own-reference subtypes:** `ownref-siblings`, where clerk and manager are both own-reference subtypes of staff. `fb03739` said `support-mismatch`; now it says `own-reference-join: variable ?a joins the families clerk and manager`.
- **Value-type subtypes with `inherits_reference: false`:** `vs-false`. `fb03739` said `support-mismatch`; now it says `own-reference-join … families code and short_code`, although a value type has no reference scheme.

Both refusals are conservative and honest; only the name and the docs wording are off.

### Checked and found true
- **Export bytes are unchanged on valid input.** `facts.tsv` and `export.json` match `fb03739` for all 13 adversarial cases that exported, covering ownref-string, diamond, diamond-string, dd, dd2, tops, value subtypes, siblings, own-reference plus inheriting subtype, duplicates and lattices. `adapter_version` stays 2. Only the `EXPORT_REFUSALS` constant changed.
- **Proposals are byte-identical** to `fb03739` for admitted cases: diamond-string, diamond-int-int, ownref-inherit, vs-true, and duplicate facts (`provenance` takes the first row).
- **IH2's targets are fixed.** ownref-string goes from a false `support-mismatch` to `own-reference-join` (exit 3); the diamond fixture goes from 70 to 3. Both refusals come before any count.
- **Refusal order.** `own-reference-join` is the last mapping refusal, after `type-confused-join`. `facts-mismatch` and the population binding come before mapping.
- **Single build.** `mined_tables` builds the relation table and pairs once. `render_tables` keeps `no-relations` and `too-large` inside the `facts-mismatch` wrapper.
- **`hold()`.** It uses `count_mined_rules`; population `IlpError`s are still turned into `ComparisonError` by `unlabelled_row`.
- **No new exit 70 from missing keys.** No `KeyError` path in `mapped` or `provenance`.
- **Focused tests pass:** test_ih2_ownref, test_il_close, test_ih1_counting, test_ih0_review, test_ilp_amie and test_il6_walk gave 218 passed, 1 skipped (pre-edit bytes). test_ih2_ownref, test_il_close, test_ih1_counting and test_ih_close gave 73 passed on the current bytes.

### Suspected, not reproduced
- **`reference_primitives` slowdown.** `resolve` has no memo inside one traversal, so it is exponential on subtype lattices. Measured on a 20-level lattice: 55s now against 48s at `fb03739`. The baseline is already exponential elsewhere, so this adds about 15% and is not a material regression.
- **Unchecked load paths.** I did not exercise a population `covers` of `None`, or compound or absent reference value types inside a family, which give an empty primitive set. The latter cannot widen `seen`, so it might hide a mismatch, but every such value I could build was refused `unrepresentable` at export first.

Scratch files are under `<scratch>/close/r1/` (`bin/`, `cases/`, `old/`, `prev/`). No worktree file was edited.

---

## Reader 2: IH0 source fixes and the comparison tool

**Verdict:** no blocking finding. I found no valid threshold or clause that is now refused, and no regression against IL's goldens or corpora. Two findings are hardening, one completeness.

Scratch is under `<scratch>/close/r2/`. It holds `mkroot.sh` (copies the tool's evidence tree), `p_cols.py`, `p_asp.py` and `p_fee.py`. I edited nothing in the worktree.

### Findings

**1. Hardening — `tools/ilp_comparison.py`, `_proposed` (llm branch); finding D is not fully closed.**
- **Where:** for `llm`, `parse` is None, so the tool computes `json.loads(text)["clauses"]`. `labelled_row` catches only `IlpError` and `ValueError`.
- **Problem:** an `answer.json` that is valid JSON but not a clauses document escapes as a traceback with exit 1. Exit 1 is also the tool's "table is stale" code. The import refuses the same file with exit 3 (`clauses … fails gnd-ilp-clauses/1 at (root)`).
- **Repro:**
  - Built a root with `mkroot.sh rootA` and wrote `{"schema_version":"gnd-ilp-clauses/1"}` to `IL5/live/invocation-1/answer.json`.
  - Set `import_exit` to 3 and wrote the schema-failure stderr.
  - Ran `uv run python tools/ilp_comparison.py --root …/rootA`: `KeyError: 'clauses'`, exit=1.
  - With `[1,2]` as the answer: `TypeError: list indices must be integers…`, exit 1.
- **Expected vs actual:** expected exit 2 naming the directory (or a row), as for reader refusals. Actual is a traceback with exit 1.
- **Fix:** catch `KeyError`/`TypeError` there, or validate against the schema.

**2. Completeness — schema-size refusals in the Popper and ILASP readers are still unnamed (same class as finding H, which was fixed only for aggregates).**
- **Problem:** these inputs still fail with an unnamed schema error rather than a named refusal:
  - an atom with more than 64 arguments;
  - a predicate name longer than 64 characters;
  - a variable name longer than 64 characters.
- **Repro:** `p_asp.py` builds each case, then runs `parse_hypothesis` / `parse_program` and `_validate`. Each gives `clauses fails gnd-ilp-clauses/1 at clauses/0/body/N: …`. For example, `p(V0..V69)` gives that error from both readers.
- **Effect:** the import still exits 3, but `refusal_name` yields no name. The comparison row would show First refusal "—" and Not evaluated "—".
- **Not a regression:** this behaviour predates the milestone; I'm noting it as an open gap next to H.

**3. Completeness (docs) — `docs/reference/ilp-bridge.md`, Import list, the "Rules:" bullet.**
- **Problem:** the bullet says "a well-formed column that `features.json` does not hold" is refused `off-threshold`. `check_columns` skips several such columns and leaves them to the fragment table:
  - an unknown predicate;
  - an arity mismatch;
  - an undeclared or non-gt/lt comparison;
  - a non-integer position.
- **Repro:** `p_cols.py` shows the vet passes `[[f_refund_amount__1__3__gt_t_amount__450=1]]`, `[[f_refund_amount__2__4__gt_t_amount__450=1]]` and `[[f_nosuch__2__3__gt_t_amount__450=1]]`.
- The rules section itself (lines 430–438) is accurate. Only the Import summary bullet is too broad.

### Checked and found true

**`check_columns`**
- **No false refusal:** each of the 38 columns in the refunds `features.json`, parsed and vetted as a one-rule ruleset, passes.
- **Unwritten values refused:** `…gt_t_amount__451` and `…__m5` are refused `off-threshold`.
- **Cross-type and subtype:** both directions are refused. `f_refund_amount__2__3__gt_t_fee__451` is T6. `f_refund_fee__2__3__gt_t_amount__450` is the "not run" reverse case from FR1, which I ran (`p_fee.py`).
- **Name spelling:** the spelled-back name is canonical, matching `_column`'s rules on leading zeros and `m0`.
- **Order:** the vet runs after the run-record bindings and coverage-shape check and before the rewrite. The rules target always re-parses the text, so the clause shape the vet relies on is guaranteed.
- **Integer types:** comparisons exist only for integer types (`ilp.schema`), so the `integers` set is exactly the integer types.

**Popper `check_thresholds`**
- All 38 rendered threshold atoms pass.
- `ge_t_amount__500` and `le_…` are refused. They are never rendered, so Popper cannot learn them, and the refusal is correct.
- The binary `gt_t_amount(V2,451)` still passes (held under IH0-D4, as documented).
- `\+ gt_t_amount__451` gives `off-threshold` (G, carried).

**ILASP aggregates**
- `#sum+`, `#count` with 40 elements, `not #count{…}`, and a single element with 18 terms all validate and reach the fragment table.
- T4 passes, with exit 3 and `clause 0: aggregate`.

**Comparison tool**
- On the real evidence it exits 0, and the golden and bridge match.
- A reader refusal whose name differs from the import's gives exit 2 with the directory named.
- A matching name (`unparsable`) produces a row with Clauses proposed "—" and an unindexed refusal.
- `_BEFORE_ANY_CLAUSE` (off-threshold counts every clause as not evaluated) matches the bridge page's definition. Only the vets raise `off-threshold`.
- A `hold()` refusal is re-prefixed with its rule index.

**Regressions**
- `git diff fb03739` touches nothing under `tests/fixtures/ilp_learners` or the ilp-learners evidence.
- `uv run pytest -q -o addopts='' -p no:cacheprovider` passed 622 with 8 skipped over these files:
  - `test_ih0_review.py`, `test_ih1_counting.py`, `test_ih2_ownref.py`;
  - `test_il6_walk.py`, `test_il_close.py`;
  - `test_ilp_amie.py`, `test_ilp_asp.py`, `test_ilp_bridge.py`, `test_ilp_learners.py`, `test_ilp_llm.py`, `test_ilp_rules.py`.
- It passed 404 more over `test_ik_close.py`, `test_il6_skill_census.py`, `test_rf5_commands.py` and `test_rf1_cli_pins.py`.

### Suspected, not reproduced

- **`refusal_name` IndexError:** a stderr starting `clause ` but containing no `": "` would raise IndexError, giving exit 1. GND never writes that, so it is contrived.
- **Other exit-1 escapes:**
  - a missing `outcome.json` or `proposal.json`;
  - a non-`IlpError` from `load_mined_inputs`.

  Each would also escape as exit 1 rather than 2. Only committed fixtures are read, so I did not build these.
- **Hard-coded constant:** `_BEFORE_ANY_CLAUSE` is hard-coded rather than derived from the adapters' `IMPORT_REFUSALS`. It is correct today but could drift if a vet gains a new refusal name.
- **Unnamed nesting refusal:** `clause K: nesting deeper than 4` carries no refusal name, so the table would show it as "—" with Not evaluated "—". This predates the milestone, and I did not build such a row.

---

## Reader 3: tests and evidence

Close reader 3 (tests and evidence), ilp-import-hardening, subject `git diff fb03739` plus untracked IH2 files.

**Verdict:** approve, with no blocking findings. There is one completeness item for the IH2 record before it is committed, and one minor hardening item.

### Findings

**C1, completeness: the IH2 draft names an evidence file that does not exist.**
- Where: the draft record `<scratch>/IH2/004-draft.md` lists `evidence/IH2/full-suite.txt` (sha256 placeholder FULLSUITE).
- What I ran: `ls .gnd-planning/milestones/ilp-import-hardening/evidence/IH2/`
- What I saw: only `dynamic-query-successor.json`, `gate.txt`, `red.txt` and `repair-red.txt`.
- Expected: the file exists before the record is written. Actual: it is absent; the draft says the run happened on `<host>`.
- What to do before committing:
  - Copy the file in and rewrite its paths to `<repo>` before hashing. A remote pytest log will carry `<home-root>/...` paths.
  - Re-run `tests/test_ih0_review.py::test_t8_this_milestone_directory_is_private_clean`, which scans the milestone directory with `rglob` and catches them.

**H1, hardening (minor): a private hostname is in repository text.**
- Where:
  - `notes/plan-review-r1-reader-1.md:61` (committed) contains "`<host>`".
  - The IH2 draft's Boundary section names "`<host>`" too.
- What I ran: `grep -rnE "<home-root>|<home-root>|/private/|/var/folders|<user>|<user>|<user>|@…|<host>" .gnd-planning/milestones/ilp-import-hardening tests/fixtures/ilp_import_hardening`
- What I saw: only that one hit. `git grep -l <host>` finds no other file in the repo.
- Why it gets through: the private-clean check (`_private_hits`) covers home roots, the user name and downstream names. It does not cover host names.
- Expected (by the milestone's privacy intent): the draft says "a second macOS host". Actual: it names the machine.

### Checked and found true

1. **Evidence digests.**
   - Every `path`/`sha256` pair in 002-phase-IH0.md (12 entries) and 003-phase-IH1.md (9 entries) matches the current bytes. I checked them by script with hashlib; `shasum -a 256` gives the same values.
   - 001-plan-gate's plan digest `d7802da6…` and IH0 spec digest `ed8dd3dc…` match.
   - The IH2 spec r1 digest `897c5ae6…` cited in the draft matches.
2. **Red claims, run in scratch worktrees with the new test file copied in.**
   - **IH0, at `cbc97b2`:** `src`, `tools` and `tests` are identical to `fb03739` (empty `git diff --stat`). Result: 16 failed, 5 passed. These are exactly the 16 FAILED and 4 control PASSED ids in `evidence/IH0/red.txt`, plus the later t8 privacy test, which passes as the record says.
   - **IH1, at `d9b274c`:** 8 failed, 5 passed. These are the 7 failures in red.txt plus T13 (red with `rule 0: support-mismatch`, as claimed). The passes are T4, T5 with its two swapped-tuple checks, and T12; the record says T12 passes at the parent.
   - **IH2, at `4389b61` with the fixtures copied:**
     - 5 failed, 4 passed.
     - T1, T5 and T3 fail with exactly the messages in red.txt.
     - T6 fails with exit 70 (`internal: … checker says 'warning'`) and T8 with `support-mismatch`, matching `repair-red.txt` case 1.
     - T4 (both parameters), T7 and the comparison-tool test pass, as claimed.
   - **IH2 mutants, built on the current `ilp_amie.py`:**
     - Full code: 9 passed.
     - Primitives branch removed: only T6 fails, with exit 70.
     - Subject-only check: only T8 fails, with `support-mismatch`.
     - Both match `repair-red.txt` cases 2 and 3.
3. **Tests that cannot fail.** None found.
   - T5's monkeypatch of `ilp_amie.count` takes effect: it raised "reached the count" at the parent.
   - IH1 T2's wrappers are proven live by its red run, and the T5 tuple pin has self-checks against swapped tuples.
   - The T4 and T7 controls are admissions by design, and the records disclose them.
   - The RF6 dynamic-inventory test is live. I added `primitives.get(str(covered))` to `relation_table` in a scratch worktree. The successor chain stayed valid, but `test_dynamic_candidate_inventory_is_complete_and_live` and `test_dynamic_duplicate_inventory_row_is_refused` failed.
4. **Privacy.** No `<home-root>` (two spellings), `/private/`, `/var/folders` path, user name or email appears in the evidence, notes or IH2 fixtures. The only hit is H1's host name.
5. **RF6 chain.**
   - `DYNAMIC_SUCCESSORS` ends with IL-close, then IH0, IH1, IH2, in that order.
   - Each successor's `predecessor` path and `predecessor_sha256` match the previous file's bytes; I checked by script.
   - `tests/test_rf6_query_policy.py` passes: 17 passed in the scratch worktree with IH2's bytes overlaid. The working-tree run is the one below.
6. **R1 in `tests/test_il_close.py`.**
   - It still asserts `returncode == 3` and that no proposal is written.
   - Only the asserted name changed: `support-mismatch` became `rule 0: own-reference-join:`. This matches the IH-D1 (b) ruling in 001-plan-gate.md.
   - It is red at `4389b61` with the new assertion and green now.
7. **Working-tree run.** `uv run pytest -q -o addopts='' -p no:cacheprovider` over test_ih2_ownref, test_ih1_counting, test_ih0_review, test_rf6_query_policy, test_il_close and test_ilp_amie: 186 passed, 1 skipped.
8. **IH2 gate list.** It is IH1's 21 files plus `tests/test_ih2_ownref.py`, which makes 22. It records the comparison tool and ruff with exit 0. The docs table row for `own-reference-join` is present.

### Suspected, not reproduced

- The draft's claim that within one family "one reference primitive means one primitive's raw values" is the checker's value equality. The draft says itself that this was observed, not proved, and I did not test it beyond T7.
- `reference_primitives` may cost exponential time on large diamond lattices. The draft records this and it was not measured; I did not measure it either.

I removed all scratch worktrees (`git worktree list` shows none from r3), and the worktree's status is unchanged. Scratch files are under `<scratch>/close/r3/`.

---

## Reader 4: does the milestone meet its plan, and do the records tell the truth?

**Verdict: approve with changes. The milestone is not yet closeable.**
- The code meets plan predicates 1 to 3.
- Every recorded digest I checked matches the bytes on disk. That covers 23 files: the specs, reviews, triage, evidence and both test files.
- No home paths, user names or emails appear in the IH planning text, fixtures or docs.
- What blocks the close is the work the close must still supply: the IH2 record, the IH2 full suite, the IH-R3 CI run, the question sweep, the PR and acceptance.
- I found one behaviour change that no record or doc discloses (H1 below).

Checks I ran:
- `tests/test_ih2_ownref.py`, `test_ih1_counting.py`, `test_ih0_review.py`, `test_il_close.py` and `test_ilp_amie.py`: 169 passed, 1 skipped.
- Probes under `<scratch>/close/r4/`: the runner `run.sh`, and probes `p1/` and `p2/`. The parent `4389b61` was extracted with `git archive` to `parent/src`.

### Findings

**H1. Hardening: IH2's review repair refuses rules that `4389b61` admitted. Nothing records or documents this.**
- **Where:** `src/gnd/export/ilp_amie.py`, `mapped`, the `len(seen) > 1` branch.
- **Probe `p1`:** the IH2 diamond model (`director` under `manager`, Integer, and `staff`, String) plus two fact types `directs` and `heads`, both played by `director`. The rule is `?a f_directs ?b => ?a f_heads ?b`.
  - At `4389b61`: exit 0, "holds on 1 of 1 head pairs". The checker agreed.
  - In the working tree: exit 3, `rule 0: own-reference-join: variable ?a joins references of Integer and String in one family`. Yet `?a` touches only `director`.
- **Why it happens:** `reference_primitives` gives `director` the union {Integer, String}. So any variable touching `director`, even only `director`, is refused.
- **What it contradicts:**
  - the docs table row, "a variable joining a subtype that has its own reference scheme with its supertype";
  - the release-note bullet;
  - IH2-D1's stated reason for choosing (a) over (b): not refusing joins "wholly inside … one family, which count correctly today".
- **The record half-discloses it:** the draft's Boundary says only that the refusal is conservative "even where no value collides". It does not say that rules admitted at IH1's head are now refused. The IH2 review's "no rule admitted today can now be refused" was true only before the repair, and the repairs carry no review opinion.
- **The refusal may be defensible:** `director`'s values may be either primitive.
- **Fix:** either narrow the check to variables that span types whose primitive sets differ, or disclose the case. Disclosing means three edits:
  - the docs row: any join through a type whose reference is ambiguous;
  - the release note;
  - the IH2 record's What shipped and Boundary, with the `p1` evidence.

**C1. Completeness: a suspicion was dropped without a row.**
- The IH0 triage assigns "a mapped AMIE rule that fails whole-model validation is reported as 'invalid model', with no rule index" to IH1.
- IH1's spec (line 30) calls it "Out of scope, carried".
- `003-phase-IH1.md`'s open-question table lists only IH1-Q1. The close sweep must give it an ID and a target.

**C2. Completeness: the release-note wording is wider than the facts.**
- `docs/release-notes.md`, the IH2 bullet, says "Such a join was reported as a false `support-mismatch`". For R1's differing primitives (Integer against String), the old `support-mismatch` was a true refusal, because the checker does not join those values. Only the same-primitive case was false.
- The IH1-D4 bullet names `covers-nothing` and `support-mismatch` but not `does-not-hold`.
- The section is dated 2026-10-29, but IH1 and IH2 landed on 2026-10-30.

**C3. Completeness: the docs row's wording is loose.**
- The AMIE mapping row and the family prose speak of "a subtype that has its own reference scheme".
- The code also refuses a value-type subtype declared `inherits_reference: false` (probe `p2`: before, a false `support-mismatch`; now `own-reference-join`, which is better). It also refuses joins between an own-reference sibling and an inheriting sibling. Neither is "own reference scheme … with its supertype".

**C4. Completeness: two departures from the plan's homes are not recorded.**
- Plan §3 names `tests/test_ih_*.py` and fixtures under `tests/fixtures/ilp_learners/`. The actual homes are `tests/test_ih0_review.py` and its siblings (the `test_ih_*` glob does not match them) and `tests/fixtures/ilp_import_hardening/ih2/`.
- The IH2 spec names the new fixture directory, but no record notes the departure from the plan.

**C5. Completeness: a hostname in planning text.**
- "`<host>`" appears in `notes/plan-review-r1-reader-1.md:61` (committed) and in the IH2 draft (line 195).
- It is not a home path, user name or email, so it does not fail the rule as written. The owner may want "a second macOS host" instead.

**Records checked and found honest:**
- Every delegated approval is labelled as the agent's ruling under `process-milestone … auto`, never as the owner's reading: README, `003`, the IH2 draft.
- IH0's "Start IH0 taken as approval" is labelled as such.
- The refuted premises are recorded without editing earlier records: IL `009` line 212 in IH0, and spec r1's Design 1 and 3 in IH2.
- The unreviewed repairs, the 3.14 full suites and the scope of the one-reviewer reviews are disclosed.
- IH1's "H2, fixed: `hold()` no longer uses `_REFUSAL`" is literally true. `_REFUSAL` survives only in `_first_refusal`, for the clause index.

**Docs claims checked:**
- **Step 2 threshold text** (Popper `ge_`/`le_`; rules column; LLM and neutral not checked): matches `ilp_popper.check_thresholds` and `ilp_rules.check_columns`.
- **AMIE table and order:** the `own-reference-join` row is last and agrees with `MAPPING_REFUSALS`. The pins are IH1 T5 and IH2 T3.
- **`population-mismatch` before parsing:** asserted by IH1 T9 per its spec. I did not run it alone.
- **`opaque` and `too-large` export refusals:** match `EXPORT_REFUSALS`.
- **Counting order prose:** matches `count_mined_rules`.

### Predicate table

| Predicate / criterion | Status |
|---|---|
| IH0: four readers over IL's nine merges (`src`, `tools`), reproduction, triage | met (`002`, triage, reviews 1–4, digests verified) |
| IH0: blocking findings fixed with a red regression | none were blocking; FR1 fixed by T6, red at `cbc97b2` (`red.txt`) |
| IH0: other findings fixed, assigned or carried | met. E, F, J to IH1 (done); G, K, L as IH0-Q1 to Q3; LLM and Popper binary/infix fixes held by owner ruling (IH0-D4) |
| IH0: focused gate | met, after the RF6 repair in `35cdc63` |
| IH1: public entry; `tools` free of `_mined_inputs` | met (grep; T1) |
| IH1: `relation_table` and `pairs` built once | met (T2); IH1-D3 changed the signature, owner-ruled |
| IH1: `provenance` in `ilp_amie`; no `gnd.discover` import | met (grep; T6) |
| IH1: entry raises only mapping refusals and `too-large`; non-holding rules counted | met (T3) |
| IH1: `facts-mismatch` first, red against a mutant | met (T4, `mutant.txt`) |
| IH1: refusal order pinned to the docs (IH-R4) | met (T5) |
| IH1: IH-R2 byte preservation; `adapter_version` 2 | met within the gate and the reviewer's harness; the D4 and D5 changes were owner-approved |
| IH1: RF6 successor and arch tests | met |
| IH2: fixture red at IH1's head | met (T1, `red.txt`) |
| IH2: (b) new name before any count | met (T1, T5, T6, T8), but over-refuses (H1) |
| IH2: R1 exits 3 with the moved name | met (`test_il_close.py` diff) |
| IH2: no golden moves; version 2 | met (T4; the comparison tool exits 0) |
| §5: docs refusal table and release-note bullet | present; wording gaps H1, C2, C3 |
| Per phase: approval, checks, one review, refactoring review, record | IH0 and IH1 met. IH2: committed record **missing** (draft has placeholders) |
| Close: question sweep | **not yet** |
| Close: IH-R3 local CI on the PR head, clean clones, 3.13 and 3.11, `evidence/close/ci-run.txt` | **not yet**; requires IH2 committed first |
| Close: four-reader review (IH-D6 (a)) | in progress |
| Close: PR; owner acceptance recorded separately | **not yet** |

**What the close must still supply:**
- the committed IH2 record, with every placeholder filled: GATE, FULLEXIT, FULL, GATEBODY, FULLBODY and the digests;
- `evidence/IH2/full-suite.txt`, which the draft cites and which does not exist yet;
- a commit of the untracked IH2 files;
- `evidence/close/ci-run.txt`: the candidate, regression and installed legs on 3.13 and 3.11;
- the question sweep;
- the close-review synthesis;
- the PR and acceptance;
- a README update ("Next action").

### Question inventory, with proposed dispositions

| Row | Proposed |
|---|---|
| IL4-Q1 remainder (own-reference joins) | **resolved** by refusing them by name (IH-D1 (b)): T1, T2 (= R1), T6, T8. Spelling them apart instead stays IH2-Q1 |
| IL-close-Q1 (one rendering pass) | **resolved**: IH1 T2 and `render_tables` |
| IL4-Q3 remainder (provenance) | **resolved**: IH1 T6 |
| `hold()` private import | **resolved**: IH1 T1; the alias is kept per plan §2 |
| IL `009` "milestone diff as a whole" | **partly resolved**: IH0 covered `src` and `tools`. IL's tests and docs were never reviewed (IH-D2): **accepted residual**, stated in the close |
| IH0-Q1 (negated off-threshold named differently) | **accepted residual**: both exit 3 by name |
| IH0-Q2 (work report omits threshold rendering, K; `p6` not rerun) | **defer**, to the next milestone that changes export bounds; name it |
| IH0-Q3 (`llm` `adapter_version` unread) | **defer**, to the milestone owning IL5-Q5/Q6 (`gnd.agents`), or accept |
| IH0-Q4 (one home for the threshold check) | **resolved** by the IH0-D4 ruling (o) |
| IH0-D4 held fixes (LLM threshold check; Popper binary/infix) | **accepted residual, owner-ruled**; the close lists it as a standing gap |
| FR1's reverse subtype case, not run | accepted residual, or one cheap test |
| "invalid model" without a rule index (C1) | **give it an ID**; defer to the next mined-import change |
| "No total work ceiling across rules"; IH1's count-before-check timing not measured | **accepted residual**: bounded per rule (IL4-D7) |
| IH1-Q1 (mined learner check ignores the tuple form) | **accepted residual**: latent, no mined entry uses it |
| IH2-Q1 (spell the diamond apart, adapter version 3) | **defer**, to the milestone that needs IH-D1 (a); name it |
| IH2: resolver cost; other family-mixing paths not built | **accepted residual** |
| H1 (over-refusal of diamond-only joins) | **new**: fix or disclose before the close |
| IH-D3 / IL6-Q3; IL1-Q6, IL2-Q2, IL3-Q3, IL-close-Q2 | **deferred** to the evaluation milestone, as already recorded |

### Suspected, not verified

- **Popper infix comparisons:** the IH0 triage holds "an infix comparison" among Popper's unchecked spellings. The docs' step 2 names only the binary atom as unchecked. I did not confirm whether the Popper reader admits an infix constant.
- **`director` with mixed-primitive values:** a population can probably hold `director` values of either primitive, which would justify refusing H1's case. I did not build that population.
- **IH1 T9:** I did not run it in isolation. It passed within the 169.
