# IL2 adversarial review: one local reviewer agent

**One reviewer is one reviewer.** One local reviewer agent read
`git diff 65fd6df bf15642`, with the brief retained at
`evidence/IL2/review-brief.md`. Its report is below. The author then
reproduced every finding before believing it, and the disposition follows the
report.

**What the reviewer could not do:** it did not run ILASP (the brief forbade
it) or the full suite. It ran targeted pytest files and the existing scratch
clingo read-only.

**Edited evidence.** The report is the agent's returned text, byte for byte,
except that its scratch directory's absolute path is replaced by `<scratch>`
and the worktree's by `<repo>` (IL-R10). The raw return was not retained in
the repository.

## Report (as returned)

IL2 adversarial diff review (`git diff 65fd6df bf15642`, branch claude/il2). I edited no tracked file. Every scratch output, including export dirs, import --out paths and probe scripts, is under
<scratch>/il2-review/
I refer to that directory as `$S` below. `CL` is the scratch clingo Python (`.../scratchpad/il1-live/venv/bin/python -m clingo`). The worktree is `<repo>`. I did not run ILASP and did not download anything. Targeted run: `uv run pytest -q -p no:randomly tests/test_rf6_query_policy.py tests/test_ilp_asp.py tests/test_ilp_learners.py` gives 123 passed.

## Findings

**1. BLOCKING. `extract_hypothesis` drops every hypothesis line whose head is not `wrong`, so a learned constraint is never seen by the reader and a partial hypothesis can be admitted.**
- **Where:** src/gnd/export/ilp_asp.py:163 (`_RULE = wrong\b.*\.`) and :178-182.
- **What goes wrong:** only lines matching `wrong … .` are kept. ILASP's default search space includes constraints, and the probe's `-s` listed `:- p(V1).` (IL2-F5).
  - A hypothesis `{wrong :- A.  :- B.}` is extracted as `wrong :- A.` alone.
  - `run_ilasp.py` then computes clingo coverage over that truncated text. So the coverage cross-check agrees with GND, and the clause is admitted, although ILASP's hypothesis means something else: the constraint removes answer sets.
  - A constraint-only hypothesis becomes `import: none` instead of the named refusal.
- **Contradiction:** this contradicts spec §14 IL2-F5 (spec line 673): "a learned constraint is refused `asp-constraint`". The `asp-constraint` branch, and any `p :- …` head-shape branch, cannot be reached on the live path.
- **Reproduction:** `uv run python $S/extract.py`
- **Observed:**
  - `constraint-first` → `'wrong :- f_refund_amount(V1,V2), gt_t_amount(V2,500).\n'`
  - `constraint-after` → the same rule
  - `constraint-only` → `''`
  - `other-head` (`p :- …` then `wrong :- p.`) → `'wrong :- p.\n'`
  - `wrong :- a(V1). % penalty 1` → `''`
- **Docstring:** it says "`UNSATISFIABLE` anywhere", but the code tests for a whole line equal to `UNSATISFIABLE`.
- **Expected:** extract the whole hypothesis block after the last `%%` line (every rule, whatever its head) and hand it to `parse_hypothesis`, which refuses `:- …` as `asp-constraint` and `p :- …` as `head-shape`. Either that, or correct F5.

**2. HARDENING. The reader treats ASP symbolic constants and strings as the same thing.**
- **Where:**
  - `ilp_asp.py:361`: a bare `web` is read as the string "web".
  - `ilp_rewrite.py:247` (check 9): for a boolean role, a quoted `"true"`/`"false"` becomes a boolean.
- **What goes wrong:** in ASP, `web ≠ "web"` and `"true" ≠ true`. The renderer writes strings quoted and booleans bare. So an admitted clause can match facts that ILASP's rule never matches.
  - The approved constants table (`web` → string) and the doc row encode this mismatch, so a fix is an owner decision.
  - It is not reachable under the rendered bias, because `const(…)` is offered only for integer comparison types.
- **Reproduction 1:** `uv run python $S/diverge.py $S $CL` gives:
  - `[bare-constant] wrong :- f_refund_amount(V1,V2), f_refund_channel(V1,cash).`: clingo covers `[]`; GND covers `['north','east','harbor','market','station']` (coverage-mismatch with clingo's record).
  - The quoted control `"cash"` agrees, and imports with exit 0.
- **Reproduction 2:** `uv run python $S/bool.py`. Both `f_order_flag(V1,"true")` and `f_order_flag(V1,true)` rewrite to `"flag": true`, while clingo derives only the bare-`true` rule (`['f_order_flag(1,true)','f_order_of(1)','r']`).
- **Expected:** read a bare symbolic constant as distinct from a string, by refusing it or giving it a separate reading. Do not apply check 9's Popper boolean coercion to ILASP's quoted strings.

**3. HARDENING. `_name` is lexed as a variable, but in ASP it is a constant.**
- **Where:** `ilp_asp.py:57`, `(?P<var>[A-Z_][A-Za-z0-9_']*)`.
- **What goes wrong:** clingo identifiers are `_*[a-z]…`, so `_cash` is a constant there. GND reads it as the variable `_cash`.
- **Reproduction:** `$S/diverge.py`, case `underscore-constant`, `wrong :- f_refund_amount(V1,V2), f_refund_channel(V1,_cash), f_refund_amount(V3,V2), f_refund_channel(V3,_cash).`
  - clingo covers `[]`; GND covers all 8 weeks.
  - In `$S/c1.lp`, `c :- f(1,_web).` is not derived beside `f(1,"web")`.
- **Expected:** lex `_+[a-z]…` as a constant (then refuse it or read it per finding 2). Only `_` and `_*[A-Z]…` are variables.

**4. HARDENING. Block comments `%* … *%` are read as line comments, so body literals vanish.**
- **Where:** `ilp_asp.py:53`, `(?P<comment>%[^\n]*)`.
- **Reproduction:** `$S/p1.py`, case `blockcomment`, `wrong :- f_refund_amount(V1,V2) %* *% , gt_t_amount(V2,500)\n.`, parses to a body of `f_refund_amount` only.
  - In `$S/diverge.py`, case `block-comment`, clingo covers harbor, market, airport and station (it keeps `gt_t_amount`), while GND covers all 8.
  - `$S/c1.lp`: `e :- f(V,W) %* *% , W = 99` is not derived by clingo.
- **Expected:** recognise `%*…*%` (and refuse an unterminated one), or refuse `%*` by name.

**5. HARDENING. Comparison atoms are copied without checking them against the comparison relation the task actually defines.**
- **Where:** `ilp_asp.py:46` and `:413`; the checker accepts any comparison the neutral form declares.
- **What goes wrong:** the task defines only `gt_`/`lt_` as `gt_t(X,C) :- dom_t(X), thr_t(C), X > C`. The neutral form also declares `ge_t_amount` and `le_t_amount`. In `$S/diverge.py`:
  - `ge_t_amount(V2,500)` is undefined in ASP: clingo `[]`; GND covers 5 weeks.
  - Swapped arguments `gt_t_amount(500,V2)`: clingo `['south']`; GND covers 7 weeks.
  - An off-threshold constant `gt_t_amount(V2,501)`, where `thr_t` rejects 501: clingo `[]`; GND covers 4 weeks.
- **IL2-D8's premise does not hold for ASP:** the boundary says an out-of-set value "cannot change admission", but here the ASP meaning differs. Only the clingo-computed coverage record catches it.
- **Expected:** for `ilasp`, accept only the rendered names (`gt`/`lt` of rendered types) with shape `(var, rendered threshold)`, or record these as boundary rows for ILASP.

**6. HARDENING. Integers outside clingo's 32-bit range are rendered, and read back, with a different meaning.**
- **Where:** `ilp_asp.py:71`/`:127`/`:132` (rendering) and `:44`/`:375` (the reader accepts 32 digits).
- **Reproduction 1:** `uv run python $S/bigint.py $S/refunds-export/neutral.json $S/bigint.lp && $CL -m clingo --outf=2 $S/bigint.lp`. With one refund amount set to 3000000000:
  - the task carries `thr_t_amount(3000000000).`, `#constant(t_amount, 3000000000).` and `f_refund_amount(101,3000000000).`;
  - clingo silently wraps it to `dom_t_amount(-1294967296)`, and `wrong :- f_refund_amount(V1,V2), gt_t_amount(V2,500)` is not derived, although GND's > 500 holds.
- **Reproduction 2:** `$S/diverge.py`, case `int-overflow`, `gt_t_amount(V2,4294967796)`: clingo covers 4 weeks (the value wraps to 500); GND covers `[]`.
- **Leading zeros:** the reader also accepts a leading-zero integer `0500` (read as 500), which clingo rejects as a syntax error (`$S/p1.py` `leading0`; clingo on `$S/c1.lp` at first).
- **Expected:** refuse at render (`unrepresentable`) any integer outside [-2^31, 2^31-1], and refuse such integers and leading zeros in the reader.

**7. HARDENING (latent). T9 and `run_ilasp.py` derive the refusal name differently.**
- **Where:** tests/test_ilp_asp.py:335 (`refusal.split(": ")[1]`) and run_ilasp.py:232 (`split(": ")[1]` only for `clause …`, otherwise `split(":")[0]`).
- **Reproduction:** for `unparsable: line 1, column 30: nesting deeper than 4`, the script records `refused:unparsable` but T9 expects `refused:line 1, column 30`.
- **Effect:** a correct future record of any non-clause refusal (`unparsable`, `learner-mismatch`, a schema failure) would fail T9.
- **Expected:** one shared parse.
- **Also:** T9 accepts a null process for any invocation whose note mentions IL2-F6. It is not tied to invocation 1.

**8. COMPLETENESS. T12 does not check the constants table, although spec §8 T12 says it must ("every refusal name and constants row").**
- **Where:** tests/test_ilp_asp.py:257-264.
- **Reproduction:** `uv run python $S/t12.py`. With the doc's boolean row deleted and `web` changed to "refused", T12's assertion still passes (`True`).
- **Expected:** compare the doc's constants rows to a table exported by the reader.

**9. COMPLETENESS. T6 cannot fail several declared cap branches.**
- **Missing cases:**
  - No case exactly at a cap (32 rules, 16 literals, depth 4, 32 digits). Tightening any cap by one still passes u4/u5/u8/u9.
  - No "input over 1 MiB" case for `--target ilasp` (the T6 row lists it).
  - The cap's name is never asserted, only `unparsable: line N, column`.
- **What I checked by hand that holds:** at-cap inputs parse; one over each cap gives exit 3 with the cap's message (`$S/p1.py`). An import of 1,048,576 bytes exits 0, and 1,048,577 bytes exits 3 "exceeds the 1048576-byte cap" (`$S/caps.py`).

**10. HARDENING (minor). Primed variables are a grammar mismatch between the reader and the clause schema.**
- **What goes wrong:** the reader lexes `V'` as a variable (`ilp_asp.py:57`), but gnd-ilp-clauses/1 rejects it. The import exits 3 with a schema failure ("… is not valid under any of the given schemas"), not `unparsable` with line and column.
- **Reproduction:** `uv run python $S/prime.py $S` (cases `prime`, `two-primes`).
- **Expected:** refuse `'` in the reader with line and column.

**11. COMPLETENESS (minor). The milestone README is stale at bf15642.**
- `.gnd-planning/milestones/ilp-learners/README.md:17` still says "IL2: spec r1 … is a draft awaiting its owner gate".
- `:55` says "Next action: the owner's ruling at the IL2 gate".
- The open-gates list still names IL2-D1/D2, which §13 records as ruled.

## What held
- **Reader totality:** no traceback on any hostile input I tried. Cases (`$S/p1.py`):
  - empty or comment-only input (0 clauses; the import then gives exit 3 with a schema "clauses: []" refusal);
  - CRLF; NUL; non-ASCII outside strings and U+00A0;
  - an unterminated string, a trailing backslash, a backslash before a newline, an unknown escape;
  - `not`×100000 and 6-deep nested aggregates (depth cap); `f(`×1000;
  - function terms; `..`; conditional literals; a quoted head; a stray `#`; left-guarded aggregates; `#sum+`; non-UTF-8 input (exit 3 "not UTF-8").
- **Refusals:** every refusal-table row exits 3 with its name (the corpus passes). `not` and aggregates reach the checker's `negation-as-failure` and `aggregate`.
- **Threading:** `X` freshness holds (`X`, `X0`, … are skipped correctly: `x-many` gives `X3`). Anonymous `_` stays fresh in the checker. `_V2` is a variable in both GND and clingo. The quoted-string escapes `\\ \" \n` round-trip.
- **Rendering:**
  - deterministic: T1 is byte-identical under hash seeds 0 and 1;
  - thresholds equal `ilp_popper.thresholds`; booleans are excluded from integer domains; a control character other than newline is refused `unrepresentable`;
  - the refunds export's E is `1acb8010…8a5e`, which matches invocation 1;
  - clingo over the rendered background plus each context plus the T3 rule covers exactly harbor, market, airport and station, the same as GND (the `control-rule` case is admitted with exit 0).
- **Registry and surfaces:** the registry, both CLI choices and both schema enums agree (T2). `tools/gnd_layers.json` has the module.
- **Goldens:** only the 9 inventoried RF1 goldens moved (`$S/golden.py`, `$S/golden2.py`). After normalising the choices string and the help sentence, every file equals its predecessor. tree.json differs only in the two `target` actions.
- **RF6 delta:** honest. Its predecessor is the IL1 file, whose SHA-256 matches. All 52 added rows are `src/gnd/export/ilp_asp.py` and none were removed; 6582 + 52 = 6634 distinct rows and 8250 + 55 = 8305 occurrences.
- **IL2-D8 (Popper):** the leading-zero, `m0` and `m0…` refusals are correct; T10 covers them.
- **Evidence consistency:**
  - raw-stdout.txt is 712 bytes, as the note says, and re-extracts to hypothesis.las;
  - hypothesis.las's SHA-256 is `980756ff…e50f`, equal to run.json `clauses_sha256`;
  - import-stderr.txt matches the outcome `refused:empty-antecedent` with exit 3;
  - the null process is accepted only with the IL2-F6 note and `completed`.
- **run_ilasp.py:** `environment(ilasp=False)` now omits `PYTHONHOME` and `DYLD_FRAMEWORK_PATH` (IL2-F6 fix 1). The evaluator reads clingo's JSON `Result` and exits on anything other than SAT or UNSAT.
- **No leaks:** no home path, user name or scratch path appears in the committed IL2 evidence (grepped for `/Users/`, `/private/tmp`, `claude-501`, `scratchpad` and the user name).
- **T9 can fail:** it fails on extraction drift, an import exit change, or a refusal-text change.

## Disposition (the author's, 2026-10-27)

**Every finding reproduced.** The author re-ran the reviewer's scratch
scripts (`extract.py`, `diverge.py`, `p1.py`, `prime.py`, `t12.py`) at
bf15642 and saw the reported outputs.

**Triage first (review-convergence).** Findings 2 to 6 were already refused
end to end whenever the run record carries clingo's coverage, as
`run_ilasp.py`'s does: GND and clingo disagree, so the import exits 3
`coverage-mismatch`. Finding 1 was not, because clingo evaluated the same
truncated text GND read. That makes finding 1 the one blocker; the others
make the reader refuse by name what it used to leave to the cross-check.

| # | Class | Disposition | Regression (red at bf15642, green after) |
|---|---|---|---|
| 1 | blocking | **Fixed.** The extractor takes every non-blank line after the last `%%` line, whatever its head. A learned constraint now reaches the reader and is refused `asp-constraint`; a `p :- …` rule `head-shape`. Invocation 1 re-extracts to the same bytes. | `test_r1_…` (4 cases), `test_r1_a_trailing_comment_…` |
| 2 | hardening | **Owner decision IL2-D13** (spec §14): the approved constants table reads `web` as a string, so changing it returns that answer to the gate. Unreachable under the rendered bias; refused today by `coverage-mismatch`. | none until ruled |
| 3 | hardening | **Fixed (reader only, IL-R9).** `_cash` is refused `unparsable`: "an underscore-prefixed constant". `_V2` stays a variable. | `test_r3_to_r10_…[underscore-constant]`; `test_r6_…[underscore-variable]` admits |
| 4 | hardening | **Fixed (reader only).** `%*` is refused `unparsable`: "a block comment". | `[block-comment]` |
| 5 | hardening | **Fixed in part (reader only).** `ge_`/`le_` are refused "a comparison the renderer never writes"; a `gt_`/`lt_` atom must be (variable, integer). **Not fixed:** an integer that is not a rendered threshold. The reader has no export to check it against; this stays a boundary row, guarded by `coverage-mismatch` only. | `[ge]`, `[le]`, `[swapped]`, `[two-variables]`, `[unary]` |
| 6 | hardening | **Reader side fixed:** an integer outside [-2^31, 2^31-1] is refused "outside clingo's 32-bit integer range", a leading zero "a leading zero". **Export side: owner decision IL2-D14**, because it changes the rendering (IL-R9). | `[int-over]`, `[int-under]`, `[leading-zero]`; `test_r6_…` admits both bounds and 0 |
| 7 | hardening | **Fixed.** `ilp_asp.refusal_name` is the one parse, used by `run_ilasp.py` and T9. T9 accepts a null process only for invocation 1. | `test_r7_…` |
| 8 | completeness | **Fixed (test only).** `test_r8_the_constants_table_matches_the_reader` parses each spelling in the doc's table and checks its reading's type. Proved by mutation: it fails with the boolean row deleted, and with `web` read as "refused". | the two mutations |
| 9 | completeness | **Closed (tests only).** One over each cap names its cap; each cap is admitted at its bound; a 1 MiB + 1 byte hypothesis exits 3 with the byte cap. These pass at bf15642 too: they are coverage, not regressions. The 32-digit cap is now reached only past the 32-bit range, so it has a one-over case and no at-bound case. | `test_r9_…` |
| 10 | hardening | **Fixed (reader only).** A primed identifier is refused `unparsable` with line and column. | `[prime]`, `[prime-2]` |
| 11 | completeness | **Fixed.** The README states IL2's status, the open decisions and the next action. | none (prose) |

**The red run.** With the bf15642 `ilp_asp.py` restored and the new tests in
place, `uv run pytest -q -p no:randomly tests/test_ilp_asp.py -k test_r` gave
`18 failed, 13 passed`: every `test_r1`, `test_r3_to_r10` and `test_r7` case
failed. With the fix it gave `31 passed`.

**Re-running the reviewer's divergence script** after the fixes: the
underscore constant, block comment, `ge_`, swapped arguments and overflowing
integer are now refused `unparsable` by the reader. The bare constant and the
off-threshold constant are still refused only by `coverage-mismatch`
(IL2-D13 and the finding 5 boundary row).
