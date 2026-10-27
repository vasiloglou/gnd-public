# Phase PL16 adversarial review (one Claude subagent), retained verbatim

Reviewer: one general-purpose Claude subagent, read-only on src/, tests/ and docs/, scratch in the session scratchpad pl16-review/. One reviewer is one reviewer. The report below is unedited.

---

## PL16 adversarial review: REVISE

Two blocking defects in core.py both break standing rule 1 ("anything else counts as a failed attempt, with the reason fed back"):
- **F1:** a malformed plan checked by GND gets no reason back to the bot.
- **F2:** a binding value with two spaces in it crashes the PyRel backend.

The two backends agree on every well-formed plan I wrote, and the `--emit-post` output matches GND's post.

**What I reviewed.** The files changed while I was reviewing: core.py went through four versions (6dd03565 → 5df61b65 → e102893d → 5d13933a). In that time the author added declines, notes, the dynamic-rule view, `parse_answer`, exit-70 handling and the interpreter check. All findings below were re-run on the final version.
- `src/gnd/examples/plan_apps/core.py`: sha256 `5d13933aab1cfdb9161b97f1fa8186a2dbf71d75315ac51cc113908aaa2d47b0`
- `src/gnd/export/pyrel_rules.py`: sha256 `b4ccec5f1b7e138df67f6653035e291ab1d4653ea6f71abf96280db6a2480d24`
- `tests/test_plan_apps.py` at the end: `55b44f0c…`. Default lane: 40 passed. The `pyrel_oracle` lane passed 10/10 on an earlier version of the test file.

**Setup for the repros.**
- `S=<scratch>/pl16-review`
- `$S/both.py EXAMPLE PLAN [STATE]` runs `core.check` on both backends and compares the exit codes, the (check, status) sets and the post-states.
- The 70 hand-written plans are in `$S/plans/`; their results are in `$S/out/*.txt`.
- `export GND_PYREL_PYTHON=$PWD/tutorials/runtimes/.venv/bin/python`

---

### Blocking

**F1. A plan GND refuses as malformed (exit 3) reaches the bot with no failures.** core.py:155
- Cause: `check_gnd` tests `if not transition:`. On exit 3, GND's report still contains a non-empty `transition` dict (`evaluated: false`, every field null), so that branch is skipped and `report["issues"]` is never read.
- Effect: unknown operations, missing or extra bindings, wrong types (`course: 101`, `amount: "1450"`, `1450.0`), list values, bad dates (`2024-02-30`) and empty plans all come back as `{exit: 3, failures: []}`. The bot gets nothing to repair from, while the PyRel backend does report the reason.
- Repro: `uv run python src/gnd/examples/plan_apps/course/app.py ask q --bot "python3 $S/bot_unknown.py $S/seen_f1.json" --attempts 2`
  - output: `gnd check: exit 3` twice, no failure lines, then `no plan was accepted in 2 attempts`
  - what the bot saw: `[{"plan": [{"op": "teleport", ...}], "failures": []}]`
  - direct check: `check_gnd(...)` returns `{'exit': 3, 'failures': [], 'post': None}`, although the report holds `transition:unknown-operation` in `issues`.
- Fix: branch on `transition.get("evaluated") is False` or `report["exit_code"] == 3`, and turn `issues` into failures. Add one test per refusal kind on the GND backend.

**F2. The PyRel output parser splits on two spaces, so a value containing two spaces breaks it.** core.py:217–221
- (a) Crash. Repro: `ask q --bot "python3 $S/bot_2sp.py" --backend pyrel --attempts 1`, where the bot binds `course: "PHIL  101"`.
  - The witness `{"course": "PHIL  101", ...}` is split mid-string, and `json.loads(parts[3])` raises an uncaught `json.decoder.JSONDecodeError: Unterminated string`.
  - The app dies with a traceback. GND reports the same plan as `pre_offered violated`.
- (b) Spurious failure. Repro: `app.py check $S/plans/course__two_spaces_ok.json --backend pyrel`, where the student is `"maya  lee"`.
  - Output: `exit 0` plus a bogus failure line `step 1  enroll(student='maya  lee', ...)`. The step-header skip fails because `parts[1]` no longer ends with `)`.
  - The test-2 comparison then differs from GND (`pyrel-only {("enroll(student='maya", "lee', ...)")}`).
- Fix: split with `maxsplit=3` and match the step header with a regex on `^step \d+  \w+\(`. Better still, have the generated program write a machine-readable verdict file (like `--emit-post`) instead of re-parsing human-readable text. Add tests for both cases.

---

### Hardening

**F3. A plan that empties a fact type can never be accepted.** core.py:329, 424
- Dropping or cancelling the last fact of a type makes rules vacuous, so both backends return exit 2. `ask` and `execute` accept only exit 0, so the operations the models offer cannot complete. The bot gets "vacuous" feedback it cannot act on.
- Repro: `course/app.py ask "Drop Omar's CS101." --bot "python3 $S/bot_drop.py" --out $S/f3.json` gives `gnd check: exit 2`, three vacuous lines, and no file written.
  - Same on both backends: `course__drop_ok`, `course__drop_term_omar`, `lease__cancel_other`.
- Fix: treat exit 2 as accepted, perhaps with a note, or decide and document this explicitly.

**F4. `--emit-post` crashes with exit 1 when the path exists or its directory is missing.** pyrel_rules.py:1881, 1899
- `open(path, 'x')` raises after the report is printed. The uncaught traceback exits 1, which reads as "violated" on an accepted plan, contrary to the program's own rule that a crash must not read as exit 1.
- Repro: `$P -I $S/lease_rules.py --pre src/gnd/examples/plan_apps/lease/state.pop.json --steps $S/lease_a2.steps.json --emit-post $S/exists.json` gives `FileExistsError`, exit 1. With `$S/nodir/x.json`: `FileNotFoundError`, exit 1.
- Fix: catch `OSError`, print to stderr and return a distinct code (e.g. 73). There is no direct test of `--emit-post` anywhere in `tests/`; add one, including these cases.

**F5. Publishing problems surface only after the whole loop.** core.py:245–255, 329
- `ask --out EXISTING` runs every attempt, then exits 1 with "already exists". That exit code is indistinguishable from "no plan accepted".
- `--out` in a missing directory: `mkstemp` raises `FileNotFoundError` with a traceback.
- If `os.link` fails in a race, the `.plan-app-*.json` temp file is left behind (no try/finally).
- `execute` without `--out` checks the plan first, then errors.
- Repro: `lease/app.py ask q --out $S/exists.json` and `--out $S/nodir/x.json`.
- Fix: validate `--out` (absent, parent exists) before the loop; wrap link/unlink in try/finally; give publish failures a distinct exit code.

**F6. The CLI crashes on bad input to `check`/`execute`.** core.py:415
- `app.py check` with no plan: `TypeError ... NoneType`.
- A plan file `{"steps": 5}`: `TypeError: 'int' object is not iterable`.
- `ask` with no question sends `"question": null` to the bot.
- Fix: require the positional argument and run plan files through `parse_answer`.

**F7. Clinic model: a refill never updates `last_refill`.** That breaks rules.md's "since the last refill", both inside one plan and across chained states.
- `clinic__dup_refill` (warfarin on 03-10 and 03-12, interval 7 days) is accepted on both backends.
- From the executed state `$S/chain_clinic_g1.json`, refilling warfarin on 2024-03-11 (one day after the 03-10 refill) is accepted: `both.py clinic $S/clinic_next_day.json $S/chain_clinic_g1.json` gives `AGREE 0 0`.
- Fix: make `refill_drug` retract and re-assert `last_refill`, or compare refills with each other.

**F8. Trip model: `within_budget` holds vacuously when a trip has no activities (or no hotels).** Its antecedent needs both `hotel_total` and `activity_total`.
- Repro with budget 800 (`$S/trip800.pop.json`): `both.py trip $S/plans/trip__hotels_only_900.json $S/trip800.pop.json` accepts 900 EUR of hotels on both backends.
- It cannot be triggered with the shipped Lisbon data (maximum hotel spend is exactly 900), but the rule as written does not state "together stay within budget".
- Fix: total each side with a 0 default, or add hotel-only and activity-only rules.

**F9. Course model: `no_retake` is a static exclusion `enrolls(s,c)` / `passed(s,c)`.**
- Recording a grade for a course the student is enrolled in is refused (`course__grade_enrolled`: `no_retake violated [["omar","CS101"]]`), although rules.md only forbids *enrolling* after passing.
- The ordinary record-a-grade flow is impossible without dropping the course first.

**F10. The `rules` view and "the rule in PyRel:" come from a different program than the one that checks.**
- core.py:75 renders `lqp`, where `.require(...)` executes. The PyRel backend (core.py:209) runs `duckdb`, where those lines are only comments (`#   rule: ...`) and the executed code is `found[...] = rows(m.where(..., <negated check>).select(...))`.
- So the docstring at core.py:70, "the code is exactly what runs", is false for the PyRel backend.
- The view also omits step checks (assert-redundant, retract-target, create-freshness), the helper relations the rules refer to (e.g. `management_chain_reverse`), and the textual rule.
- Fix: say which program is shown, or show the duckdb violation query; list the step checks too.

**F11. Remaining loop gaps in core.py.**
- `check_pyrel` does not catch `subprocess.TimeoutExpired` (line 212), so it crashes instead of failing the attempt.
- The PyRel refusal message passes the plan's temp path to the bot.
- The program is re-rendered every attempt; spec §6.1 says "cached per model digest".
- There is no bound on plan length: a 3000-step bot answer was accepted after 51 s on GND and printed 3000+ lines.

---

### Completeness

- **C1. Access:** rules.md says Frank's wiki access was "approved by Erin", but state.pop.json records `approver: dana`. Erin manages Frank, so the documented fact would itself violate `approver_outside_the_chain`.
- **C2. Lease:** spec §6.3 lists "value ranges", but the model has no value constraint.
- **C3. Unknown entities pass silently:**
  - unknown trips (`trip__unknown_trip`, hotel for "madrid");
  - unpriced activities (`trip__unknown_activity`, "surfing" costs nothing);
  - unknown leases (`lease__unknown_lease`, 5 due on 1999-01-01).

  Rules.md does not forbid these, but a reader might expect it to.
- **C4. `admit` has no observable effect.** Admitting "zed" publishes no instance on either backend (neither GND's `computed_post` nor `--emit-post` carries `instances`), and admitting zed twice in one plan is accepted on both.
- **C5. Stand-in bots carry hidden answers:**
  - access hard-codes `APPROVERS = ["carol", "erin"]` and never derives "outside the chain" from `reports_to`;
  - trip hard-codes the replacement `oceanarium` and the extra `belem-walk`;
  - course hard-codes its elective order and ignores `offered` in the state.

  Clinic and lease repair purely from witnesses. Course parses GND's precondition message with a regex, because GND precondition failures carry no structured witness. The PyRel witness for preconditions is the full bindings, while GND names the atom; PL15-Q2 is only met in text on GND.
- **C6. Test gaps:**
  - nothing covers GND exit-3 feedback (F1), the parser (F2), `--emit-post` directly (F4), bot timeout (spec test 5 says "or times out"), or exit 2;
  - `test_the_pyrel_backend_agrees...` compares only the *set* of (check, status), not where or witnesses;
  - `test_rules_prints_each_rule...` checks only that `.require(` appears, not that every rule id does;
  - there is no record of mutation testing (spec test 6).
- **C7. RF7:** the plan_apps allow-list entries are right: core.py and the five bots use `json.load`, the app.py files do not. But `tests/test_rf7_structure.py::test_complete_routing_and_dirty_controls` fails, and the failure is not caused by PL16:
  - `src/gnd/population_shape.py:298` already calls `json.loads` at HEAD;
  - stray untracked `src/gnd/examples/bookrec/*.population.rules.py` would also fail it.

  The new untracked `tools/plan_app_bot.py` is outside this phase.

---

### Scenarios where the backends agree

These agree on exit and (check, status). Wherever both accepted, the posts are equal, including derived facts.

- **Shipped attempts:** all 13 documented attempts, the five full `ask` runs on each backend, and a chained second `ask` from the executed state on each backend.
  - The PyRel posts are byte-identical to GND's (sorted keys), and `gnd check` exits 0 on each PyRel post.
- **Course:**
  - drop / drop_term on missing facts (retract-target);
  - enroll twice (assert-redundant warning);
  - retake; 6+ courses with 22 credits (`credit_cap`, `term_load`, `pre_offered`);
  - `record_grade` twice (`one_grade`);
  - `change_grade` (dynamic rule violated; same grade accepted with a warning);
  - admit an existing student (create-freshness); admit then enroll a new student;
  - enroll then drop.
- **Access:**
  - self-approval; direct manager; outside approver (frank);
  - revoke (ok and missing); revoke then re-grant;
  - approve twice; two approvers; grant again; a new person.
- **Clinic:**
  - interval boundary 03-08 ok / 03-07 early;
  - leap-year 03-20 early; 60 days ok / 61 days warning;
  - not prescribed; same day twice; 9999-12-31 (warning only);
  - interacting drugs on different days.
- **Trip:**
  - night on the end day / the day before the start;
  - two hotels in one night; budget exactly at the limit (890 = 890) accepted, 925 refused;
  - activity twice; porto over budget.
- **Lease:**
  - due on the start day / the end day (warning) / after the end;
  - exactly a week before the end (ok) / inside the last week (warning);
  - wrong amount; two payments on one day; cancel (ok and missing); schedule then cancel.

The only divergences are F1 (all exit-3 cases: the exits agree, GND gives no reason) and F2.
