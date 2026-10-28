# IL3 adversarial review (step 4)

**One reviewer is one reviewer.** One local agent read `git diff e30eec8
620f394` on 2026-10-28 under the brief in
[`evidence/IL3/review-brief.md`](../evidence/IL3/review-brief.md). Its report
follows as returned. The only edit replaces the repository and scratch paths
with `<repo>` and `<scratch>`. The reviewer edited no tracked file, ran no
learner and no run script, and wrote only under `<scratch>/il3-review/`.

## The report

### IL3 adversarial review: `git diff e30eec8 620f394`, branch claude/il3

I found one blocking defect: a 46-byte rule-set file made the import run for
277 s at 1.9 GB before it refused. There are four hardening findings and
three completeness findings. The targeted gate subset passes: 630 passed. I
edited no tracked file. Everything I wrote is under `<scratch>/il3-review/`,
and I passed `--basetemp` there for pytest. I did not run the learner or the
run scripts.

#### Findings

**1. Blocking: the reader is not bounded. The arity digits in a column name
make it allocate without limit.** `src/gnd/export/ilp_rules.py:43` takes the
arity as `[1-9][0-9]*` with no bound beyond the 160-character name cap.
`_clause` at `:129` then builds `range(1, arity)` argument dicts before any
schema check.
- In-process repro (`<scratch>/il3-review/arity.py`):
  `parse_ruleset("[[p__1__<A>__gt_t_x__5=1]]")` takes 0.01 s at A=10^4,
  0.49 s at 10^6 and 4.99 s at 10^7. An arity of 140 nines gives a
  157-character name the grammar accepts, and would ask for 10^140 dicts.
- CLI repro: the file `[[f_refund_amount__2__5000000__gt_t_amount__450=1]]`
  (46 bytes) with a matching run.json, run through `gnd import ilp-rules ...
  --target rules`, gave `277.01 real, 1941422080 maximum resident set size`,
  then exit 3 "clauses … fails gnd-ilp-clauses/1". The jsonschema step also
  walks all 5M arguments. With arity 3 the same import takes 1.9 s at 70 MB.
- A large enough arity ends in MemoryError, which is not caught as
  `IlpError`, or runs for a practically unbounded time.
- **Expected:** standing rule 1 (totality) and rule 2 ("the reader is linear
  in characters"). Bound the arity and the position, for example with the
  clause schema's limit of at most 16 atom arguments, and refuse `unparsable`
  before building the clause. Add a T7 case for it.

**2. Hardening: the renderer writes column names its own schema and reader
refuse.** `ilp_rules.py:71-73` checks the round trip through `_column`, which
does not apply `MAX_NAME`.
- Repro: `<scratch>/il3-review/longmodel.py` builds a copy of refunds with a
  59-character fact type and object type and one 26-digit amount. `gnd export
  ilp … --target rules` exits 0.
- `<scratch>/il3-review/check_schema.py` on the result reports `1 schema
  errors: columns/37/name … longest name 161`, against
  `ilp-features.schema.json`'s `maxLength: 160`. `parse_ruleset` of that name
  gives `unparsable: … longer than 160 characters` (`names.py`).
- So T1b's "validates" property holds only for the two goldens.
- **Expected:** `render` should refuse by a documented name, or the cap
  should cover every name the renderer can write. Thresholds above 2^53−1 are
  not admissible by the clause schema anyway, so a renderer-side bound is
  natural.

**3. Hardening: the `rules` export refuses with the undocumented name
`name`, with a misleading meaning.**
- A 33-digit observed integer (`longmodel.py … 33`) gives exit 3 `name:
  column '…__m999…' does not read back as itself`. `--target popper` on the
  same input exits 0.
- A fact-type id shaped like a column name, such as predicate
  `f_a__1__2__gt_t_x`, gives `name: column
  'f_a__1__2__gt_t_x__1__2__gt_t_amount__1' does not read back as itself`.
- `name` is not in `EXPORT_REFUSALS`. `ilp-bridge.md:114` defines `name` as
  "an id longer than the export's name bound", which is neither case.
- **Expected:** a listed and documented refusal, or a grammar the renderer
  cannot violate. The fact-type id regex `[a-z][a-z0-9_]{0,58}` allows
  `__<n>__<n>__gt_t_` inside ids.
- The reader itself does not misread anything: every name the renderer does
  write round-trips (300 random trials below).

**4. Hardening: `live_common.termination` is not the ruled mapping.**
- At `live_common.py:63-71`, every status other than `succeeded` maps to
  `rendering-rejected`.
- §6 maps only `failed` to `rendering-rejected`. IL5's ruled
  `run_llm.termination` maps `spawn-failed` and `cleanup-failed` to
  `completed`.
- Repro output:
  - `spawn-failed live_common=rendering-rejected IL5=completed`
  - `cleanup-failed live_common=rendering-rejected IL5=completed`
- The docstring claims "IL-R9's closed list". Because the import still runs
  whenever `extract_ruleset` finds a line, a `cleanup-failed` run can be
  recorded as `rendering-rejected` + `admitted`.
- Related: `import_outcome` turns a non-3 exit, such as an internal 70, into
  `refused:internal`. The spec defines `refused:<name>` only for exit 3.
- **Expected:** an explicit ruled row for these statuses, or a refusal to
  record them.

**5. Hardening: the RF6 direct-read scanner is bypassed rather than
satisfied.**
- `ilp_rules.py:49,75` reads `predicate[_ROLES]` with `_ROLES = "roles"`.
- Repro with `tests/test_rf6_query_policy.reads`:
  - `p["roles"]` gives `{('x.py','f',"p['roles']"): 1}`
  - `_R="roles"; p[_R]` gives `{}`
- The delta's claim of "no exception widening" is literally true, and IL3-F4
  discloses it. But this is the escape pattern
  `test_literal_subscription_cannot_escape_direct_read_policy` exists to
  stop, and IL5's precedent projects through a field tuple, not a disguised
  subscript.
- **Expected:** a counted policy row, or a scanner that resolves module
  constants. This is an owner call. Not a code defect.

**6. Completeness: T9 cannot fail on most of `outcome.json`.**
- Repro `<scratch>/il3-review/mut/test_t9_mutations.py` runs T9 against a
  mutated copy of invocation-1 with `LIVE_ROOT` monkeypatched. Result:
  `5 passed`, meaning every mutation survived:
  - `limits.timeout_seconds` set to 6000;
  - `-I` removed from `argv`;
  - `licence` emptied;
  - a junk line appended to `raw-stdout.txt` (T9 checks stderr bytes against
    `stderr_observed_bytes`, but never stdout's);
  - the learner version changed to 9.9 in both outcome.json and
    run-meta.json.
- T9 also replays with `outcome["import_args"]` as committed, without
  comparing them to `run_rules.IMPORT_ARGS`.
- **Expected:** assert the limits, argv, import arguments and licence against
  the script's constants. Assert the stdout byte count and the learner line
  against `raw-stdout.txt`.

**7. Completeness: the accept-at-the-bound side of every reader cap is
untested.**
- Repro `<scratch>/il3-review/mut2/test_reader_mutants.py` runs all T4, T7
  and T8 cases against source mutants. These survive:
  - the rules cap at 31;
  - the conditions cap at 15;
  - `len(name) >= MAX_NAME`;
  - `len(digits) >= MAX_DIGITS`;
  - `_RULE_LIST` without leading `\s*`.
- A control mutant that drops `=1` is killed.
- T7's "161-character name" is actually 169 characters
  (`tests/test_ilp_rules.py:211`).
- Directly (`edges.py`), the code itself holds: 32 rules OK and 33 refused;
  17 conditions refused; a 160-character name OK and 161 refused; 32 digits
  and `m`+32 digits OK, 33 refused.
- **Expected:** at-bound acceptance cases and an exact 161-character name.

**8. Completeness: surfaces and docs drift.**
- The `gnd export ilp --target` help (`src/gnd/commands/export.py:109-110`)
  still says "popper (…), neutral, or ilasp (…)" with no `rules`. It is now
  pinned in the three new per-version goldens.
- The `gnd import ilp-rules` CLAUSES help still says "Popper's printed
  program, or gnd-ilp-clauses/1 JSON".
- The docs row says "a line starting with `if`". The code also refuses
  leading whitespace, including NBSP, any case, and `if\t` as
  `ordered-rule-list` (`edges.py`: "leading ws if", "nbsp if" and "if-tab" all
  give ordered-rule-list).
- A ruleset.txt with a trailing newline, the normal editor output, gives
  `unparsable: … text after the rule set`. This is documented only as "one
  line".
- outcome.json omits the pandas and numpy versions the §6 retained list asks
  for ("the versions"). The Python version in run-meta is a hard-coded
  string, not an observed one.

#### What held
- **Reader grammar and totality**, apart from finding 1: about 35 hostile
  inputs in `edges.py` gave only `IlpError` exit 3. These included unicode
  digits in values and names, `= 1`, `=TRUE`, a double space around `V`,
  `[[]]`, `[True^…]`, nesting, uppercase predicates, `=10`, `=1.0x`, `>0.50`
  and `=1.00`.
- **Polarity:**
  - `=1` versus `=1.0`/`=10` is resolved by the `]^`/end lookahead;
  - the row order is right, per rule: `[a=1^b=0]` gives negation-as-failure
    and `[[a=1] V [True]]` gives `clause 1: empty-antecedent`;
  - 16 conditions give propositional-conjunction.
- **Feature table:** `oracle.py` ran 300 random neutral forms, each with two
  predicates, three integer positions over two types, a boolean and a string.
  It found 0 cell mismatches against an existential oracle. Every column read
  back through `parse_ruleset` to the same predicate, arity, position,
  comparison and threshold, including negative thresholds. Multi-digit
  position and arity (`f_p__12__103__…__m7`) parse correctly.
- **Two hash seeds and the `MAX_FEATURES`/`MAX_CELLS` bounds:** T1 and T3
  cover both, at the bound and one over.
- **Binding and admission:** the import checks the clauses SHA, the export E
  (computed for the import's target), the learner name, the coverage shape and
  the per-clause set equality with GND's verdicts. It is all-or-nothing,
  which i3, i7 and T6 exercise.
- **Registry, choices, enums and schema inventories agree.** The RF1
  manifest lists exactly the golden files, every SHA verifies, and
  `MANIFEST_SHA256` equals `shasum goldens.sha256` (f7d210f1…). Only the
  listed goldens moved; py311 differs from py313 only in the usage wrap.
- **Gate subset:** `test_ilp_rules`, `test_ilp_learners`, `test_rf1_cli_pins`,
  `test_rf1_pin_harness`, `test_rf1_layering`, `test_gnd_arch`,
  `test_rf6_query_policy`, `test_public_built_inventory`, `test_schema_sync`,
  `test_ilp_bridge`, `test_ilp_asp` and `test_ilp_llm`: 630 passed.
- **Evidence consistency:**
  - `extract_ruleset(raw-stdout)` equals `ruleset.txt`, which has no trailing
    newline;
  - run.json's coverage equals the learner's COVERS line (5 ids), so it comes
    from the learner (IL-R4);
  - `clauses_sha256` matches;
  - the import report shows reported 5 and covered 5, support 4/5 with
    `south` as the counterexample, and agrees with proposal.json;
  - the stdout byte count of 142 matches.
- **No private data:** no home path, user name, email or scratch path appears
  in IL3 evidence or `live_common.py`.
- **Sanitizer:** byte-for-byte the IL2 and IL5 sanitizer.

## Reproduction and disposition (the author, 2026-10-28)

Every finding was reproduced before it was believed:
- **1:** `parse_ruleset` built a 10^6-argument atom in 0.26 s.
- **2:** the reviewer's long-model script gave a 161-character column name
  that failed the table's own schema.
- **3:** a 33-digit value gave the undocumented refusal `name`.
- **4:** `live_common.termination` mapped `spawn-failed` and `cleanup-failed`
  to `rendering-rejected`.
- **6 and 7:** by the new tests below.
- **8:** by reading the help and the docs.

Before the fixes, the new regression tests gave:
- 9 failed and 8 passed in the first run;
- after a control case was added to the T9 tamper test (its first form
  failed for an unrelated reason: the replay directory did not exist), 5
  tamper cases failed and the control and `import-args` passed;
- on the pre-fix renderer and reader, the three new export cases and two
  arity cases failed;
- the `9 × 140` arity case did not finish (it was stopped). That is finding 1
  itself.

| # | Triage | Disposition |
|---|---|---|
| 1 | blocking | **Fixed.** `MAX_ARITY = 64`, the clause schema's argument cap for an atom (not 16, which is the cap on an aggregate's arguments). A name whose arity has more than two digits or exceeds 64 is not a column name, so the reader refuses it `unparsable` before any clause is built. Tests `test_r1_*`: 65, 5,000,000 and 140 nines refused; 64 read. |
| 2 | hardening | **Fixed.** The renderer refuses `column-name` when a name would exceed 160 characters. `column-name` joins `EXPORT_REFUSALS` and the docs. Test `test_r2_r3_*` (59-character ids and a 26-digit value). |
| 3 | hardening | **Fixed.** The same `column-name` refusal replaces `name` for a threshold over 32 digits and for an id that does not read back as itself. Tests `test_r2_r3_*` (a 33-digit value; `f_a__1__2__gt_t_x`). Refusing a value Popper accepts is a narrowing that applies only to `rules`, and it is documented. |
| 4 | hardening | **Fixed.** `live_common.termination` maps exactly the ruled statuses (`succeeded`, `failed`, `timed-out`) and stops with "unruled process status" for any other. The raw files are already written, but no outcome is recorded. `refusal_for_exit` names only exit 3 a refusal; any other non-zero import exit stops the script. Tests `test_r4_*`. Invocation 1 (`succeeded`, exit 0) is unaffected. |
| 5 | hardening | **For the owner** (open question IL3-Q1). The neutral form is not the model, but the scanner cannot tell. A counted policy row would widen an RF6 exception, which is a ruling the author cannot make. IL5's `_project` reads through a key tuple of the same kind. |
| 6 | completeness | **Fixed.** T9 asserts the limits, argv, import arguments and licence against the script's own constants (`LIMITS`, `RECORDED_ARGV`, `IMPORT_ARGS`, `LICENCE`). It also asserts the stdout byte count against `stdout_observed_bytes` and the learner against `raw-stdout.txt`. Test `test_r6_*`: a control passes, and six tampered copies each fail. |
| 7 | completeness | **Fixed.** `test_r7_*` accepts 32 rules, 16 conditions (refused as a conjunction, not by the cap), a 160-character name, and 32-digit and `m`+32-digit thresholds. It refuses an exact 161-character name. It refuses `  if` and `\tIf` as rule lists. |
| 8 | completeness | **Fixed in part.** Both help texts now name `rules` (test `test_r8_*`), and the RF1 goldens moved with them under 3.11, 3.13 and 3.14. The docs say "any case, after any leading spaces" and "no trailing newline". **Not fixed:** outcome.json lacks the pandas and numpy versions. Invocation 1's bytes stay as recorded; the versions are fixed by `downloads.json`, because the venv was installed offline from those files only. The record states this. |
