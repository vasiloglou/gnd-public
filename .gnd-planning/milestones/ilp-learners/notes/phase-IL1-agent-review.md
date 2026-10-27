# IL1 adversarial review: one local reviewer agent

**One reviewer is one reviewer.** One local reviewer agent read
`git diff 5576a4e ed54e65`, with the brief retained at
`evidence/IL1/review-brief.md`. Its report is below. The author then
reproduced findings before believing them, and the disposition follows the
report.

**What the reviewer could not do:** it did not run Popper (the brief forbade
it) or the full suite; it ran targeted pytest files and the existing scratch
SWI and clingo read-only.

**Edited evidence.** The report is the agent's returned text, byte for byte,
except that its scratch directory's absolute path is replaced by `<scratch>`
(IL-R10). The raw return was not retained in the repository.

## Report (as returned)

IL1 adversarial review: `git diff 5576a4e ed54e65`, branch `claude/il1-learner-registry`

I found 2 defects that block, 4 hardening items and 5 completeness items. I edited no tracked file; `git status` shows only the untracked review-brief.md that was already there. All scratch output is under `<scratch>/il1-review/`, called `$S` below.

The gate files all pass: `test_ilp_learners` plus `test_ilp_bridge` give 143 passed, and the other gate files give 516 passed. I did not run Popper. I did run the existing scratch `swipl` binary and the `clingo` Python module from the scratch venv, read-only, to check finding 2 and the SWI escape forms.

## Findings

**1. Blocking: the new octal handling turns a malformed quoted atom into a traceback (exit 1) instead of exit 3. This is a regression.**
- **Where:** `src/gnd/export/ilp_popper.py:324-326`, which then crashes at `:319` (`following = body[position + 1]`).
- **Cause:** The tokenizer and `_unquote` read `\1\\` differently.
  - The tokenizer's octal alternative cannot close the atom, so it backtracks to the `\\.` reading: `\1`, then `\\`.
  - `_unquote` always takes the octal reading `\1\`. That leaves a lone trailing backslash, and `body[position+1]` is out of range.
- **Reproduction:**
  ```
  printf '%s\n' "wrong(A):- f_order_amount(A,B,C),f_customer_blocked(A,'\\1\\\\')." > $S/corp/oct.popper.pl
  uv run gnd import ilp-rules $S/corp/orders.orm.yaml $S/corp/oct.popper.pl --labels $S/corp/m.labels.json --reported-coverage $S/corp/oct.run.json --target popper --out $S/corp/oct.out.json --format json
  ```
  It prints a traceback ending in `IndexError: string index out of range`, and the exit is 1. Calling `parse_program` directly gives the same result.
- **Base comparison:** The same input on the 5576a4e source (run from `git archive` with `PYTHONPATH`) gives `IlpError unparsable: line 1, column 55: an unknown escape in a quoted atom`.
- **Expected:** exit 3 `unparsable` with an octal or escape message. The fix is either for `_unquote` to refuse when no character follows the closing backslash, or for `_TOKEN` and `_unquote` to agree on one reading.
- **Missing test:** add a T4b case for `'\1\\'`.

**2. Blocking for adapter 2's purpose: every threshold predicate is invisible to Popper v5.0.1's background-knowledge analysis, so Popper bans them all. This explains IL1-F9.**
- **Where:** `ilp_popper.py:132`, the line that renders `name(A) :- integer(A), A op v.`
- **Mechanism:**
  - Popper's `bkcons.get_bk_cons` loads bk.pl into clingo, an ASP solver.
  - If bk.pl grounds there, Popper sets `datalog=True` and runs `deduce_recalls`.
  - In clingo, `integer/1` is an ordinary predicate with no facts, so every threshold has 0 groundings.
  - `deduce_recalls` then emits `:- body_literal(Rule,gt_t_amount__500,_,(_,)), #count{...} > 0.` for each threshold, which forbids any rule from using it.
  - Adapter 1's bk.pl failed to ground in clingo (`A > B` is unsafe), so its constraints were skipped entirely.
- **Reproduction** (scratch venv python, clingo only, not Popper):
  ```
  $PY -I $S/clingo_probe.py $S/seed1/popper/bk.pl
  ```
  - On the adapter-2 refunds bk.pl it prints `grounded: datalog=True`, then `f_refund_amount 20`, `gt_t_amount__500 0`, `lt_t_amount__1500 0`, `gt_t_amount__35 0`.
  - On the adapter-1 bk.pl at `$S/base-export` it prints `ground FAILURE -> datalog=False`.
- **What it settles:** The source path is `bkcons.py:290-330` and `:105-144` in the scratch Popper. SWI confirms that `wrong(A):- f_refund_amount(A,B,C),gt_t_amount__500(C).` covers exactly harbor, market, airport and station, as IL1-F9 says. So `NO SOLUTION` comes from the rendering, not from the data or the bias limits. That answers F9's open question.
- **Why the tests miss it:** A1-T2 checks threshold predicates only under SWI, never under the clingo grounding Popper also runs.
- **Expected:** a rendering that is datalog-safe in both engines. For example, ground facts `gt_t_amount__120(V).` for each observed value V greater than 120 of that type. This is equivalent over the exported domain and never raises.
- **Process note:** this is a rendering change, so under IL-R9 it needs an owner amendment. A1-D4 allows IL1 to close with the outcome recorded, but the record should state this cause.

**3. Hardening: a comparison between operands of incompatible types is admitted when written infix, but refused when written as the declared predicate.**
- **Where:** `ilp_rewrite.py:89-90`. 9b only types an operand through a declared comparison predicate, and the validator (check 10) does not catch the infix form either.
- **Reproduction:** I built a fixture with integer value type `quantity`: `$S/corp/q.orm.yaml` and `q.labels.json`, plus `pops/qn1.yaml` with quantity facts. Then:
  - `wrong(A):- f_order_amount(A,B,C),f_order_quantity(A,B,D),C > D.` gives **exit 0**, and the proposal holds the constraint `$v_c <= $v_d` (amount ≤ quantity).
  - The same clause with `gt_t_amount(C,D)` gives `type-confused-join: variable D joins amount and quantity`. This came from `$S/p2.py`.
- **Context:** this was not a regression; IK5 admitted it too. But D13 intends a comparison to carry a type.
- **Expected:** both spellings get the same answer. For example, treat the two variable operands of any comparison as one join site set.

**4. Hardening: `extract_program` is fragile in two ways.**
- **Where:** `ilp_popper.py:65` and `:365`, and `:373`.
- **The prefix pattern is not anchored.** `_ELAPSED` removes the first `\d+s ` anywhere in a line. On a rule line without a prefix this rewrites a constant: `extract_program(BANNER+"\nwrong(A):- f(A,'3s x').\n")` returns `"wrong(A):- f(A,'x').\n"`. Popper always prefixes and v5.0.1 prints no constants, so this is latent. The fix is to anchor the pattern with `^`.
- **Rules after an interleaved line are silently dropped.** One non-rule line between rule lines truncates the program: a two-rule block with a `Warning:` line between them returns only the first rule. There is no refusal, and run.json is then built from the truncated program. The spec chose "first maximal run", so this is by design, but a truncation is never reported.
- **Expected:** anchor the prefix, and stop only at the closing line of stars, or flag rule lines that appear after the run.

**5. Hardening: the threshold parser accepts names the renderer never writes.**
- `gt_t_amount__007(C)` maps to C > 7.
- `lt_t_amount__m0(C)` maps to C < 0.
- `ge_t_amount__7(C)` maps to C ≥ 7, though `ge` is never rendered.
- A value outside the rendered threshold set is accepted.
- In each case the meaning matches the name, so nothing is mistranslated. But a Popper import can admit a constant that was never in Popper's bias.
- A side point: the column in the over-long-value refusal points at the `(`, not at the name (`:248`).
- **Expected:** optionally refuse leading zeros, `m0`, and values not in the export's threshold set.

**6. Hardening: the service never enforces `Learner.exports` or `contract`.**
- **Where:** `ilp_service.py:162` and `:180`.
- **Reproduction:** register a monkeypatched `llm` entry with `exports=False` and call `_cmd_export_ilp(..., target="llm")`. It returns 0 and writes an `export.json` with `"target": "llm"`, which is outside the schema enum.
- **Context:** today only the literal argparse choices, pinned by T2, prevent this.
- **Expected:** `_cmd_export_ilp` refuses an entry with `exports=False`.

**7. Completeness: SWI 10.0.2's escapes `\a \b \v \f \r` are refused as unparsable.**
- **Where:** `ilp_popper.py:52` (`_ESCAPES`).
- **Gap against the spec:** §6 says the pinned SWI's `writeq` output for code points 0–31 and 127 is recorded at the gate, and every form missing from `_ESCAPES` is added. Neither was recorded or done.
- **Recorded output** (`swipl -g "forall(between(0,31,C),...writeq...)"`):
  - code points 7, 8, 11, 12, 13 are written as `'\a' '\b' '\v' '\f' '\r'`;
  - other controls are written as `'\xN\'`, including `'\x7F\'` for 127;
  - SWI writes no octal at all.
- **Effect:** `parse_program("wrong(A):- f(A,B,'x\\r').")` gives `unparsable ... an unknown escape`.
- **Expected:** add these to `_ESCAPES`, with T4 cases. Check 9's `constant-spelling` would then refuse them by name.

**8. Completeness: several tests cannot fail on the code they cover.**
- **T9 replay** (`tests/test_ilp_learners.py:461`): both recorded programs are empty, so the import-replay branch has never executed.
- **T9 termination check** (`:443`): for exit 0, `expected_termination` is `outcome["termination"]` itself, which is a tautology.
- **T9 on invocation 1:** it only asserts that the digest is different. Independently, the 5576a4e code reproduces invocation 1's E, `dc0031e5…`, so the record is right; the test just doesn't show it.
- **`extract_program`:** its success path (banner, prefix stripping, last banner, maximal run) has no test at all, because T9's logs have no banner.
- **T5c** (`:309`): asserts `pairs == 0`, so it cannot detect pair blow-up. Measured worst case: 32 clauses of 16 atoms, one variable at 240 compatible types, gives 917,760 pairs in 0.13 s. So the check is bounded, but the test does not show it.
- **Subtype joins** (`:272`): tested only with hand-built closures. If `type_closures` dropped supertypes, no test would fail. I checked `type_closures` on `tests/fixtures/adversarial/models/subtype_mandatory.orm.yaml` and it gives `car → {car, vehicle}`, which is correct.
- **J3/J4** (`:212`): they only assert that "type-confused-join" is absent from stderr; spec T5b says exit 0. Both actually end in `coverage-mismatch`, after 9b, so they do exercise 9b.

**9. Completeness: one change to the approved corpus is not in the IL1-A1 inventory.** The approved corpus test T3 was edited (`adapter_version="1"` added to the fake entry) because of IL1-F8. The edit is harmless, but it is not listed.

## What held
- **Threshold meaning:**
  - `gt` and `lt` map to `>` and `<`, and the consequent is negated correctly; `lt_t_amount__m5` decodes to −5.
  - Decoding after the last `__` is unique, including type ids that contain `__` or `__m5`.
  - Mapped atoms take the comparison's declared type, so check 5 and 9b both apply: threshold of another type gives type-confused-join; threshold on an entity variable gives comparison-type; constant or `_` argument gives comparison-type; threshold on the example variable gives example-variable.
  - Threshold names cannot collide with fact predicates, which all start with `f_` and have at least two arguments.
- **Check 9b:** `_` is excluded, siblings that share a supertype are admitted, unrelated types are refused, and the work is bounded.
- **Parser totality:** these all give named exit 3 or parse correctly:
  - octal escapes of 1, 7, 8 and 100,000 digits;
  - surrogate and out-of-range values;
  - unclosed escapes;
  - a 200,000-digit threshold value;
  - 200,000-character names;
  - 5,000-deep nesting;
  - NUL characters;
  - a zero-argument threshold;
  - a threshold with a nested argument.
- **Thresholds and determinism:**
  - Rank selection matches round-half-up exactly for n = 33…3999, with 32 distinct values and the minimum and maximum always kept.
  - Booleans are excluded.
  - Exports under `PYTHONHASHSEED` 1 and 987 are byte-identical.
  - The adapter version is "2" for popper and "1" for neutral.
- **Registry:** `ilp_service` names no learner; the CLI choices and both schema enums equal the registry tuples.
- **Golden movement:** exactly the listed inventory moved. 19 run records changed their `export_sha256` only; `expected.json` changed digest lines only; X1 changed bk.pl, bias.pl and export.json. Every exit and refusal is unchanged.
- **Evidence:**
  - Invocation 2's recorded byte counts (stderr 138, stdout 12) match the raw files.
  - No home path, user name, `***` mask or scratch path is in any tracked milestone file. T8 passes, and the untracked review-brief.md is clean too.
  - The gate test set passes.

## Disposition (author, 2026-10-27)

| # | Class | Reproduced | Disposition |
|---|---|---|---|
| 1 | blocking | yes: `parse_program` raises `IndexError` on `'\1\\'` | **fixed**: `_unquote` refuses a backslash that ends a quoted atom, `unparsable … a backslash ends a quoted atom`; regression `test_r1_…` observed red on ed54e65 |
| 2 | blocking for adapter 2 | yes: the clingo probe over invocation 2's own `bk.pl` grounds (`datalog=True`) with 0 atoms per threshold predicate, and over adapter 1's fails to ground; Popper's `bkcons.get_bk_cons`/`deduce_recalls` (installed v5.0.1 source) then emits `#count{…} > 0` for each zero-recall predicate | **not fixed in step 4.** It explains IL1-F9: Popper bans every threshold predicate. A fix changes the rendering, so under IL-R9 it is an owner amendment, and a third run needs a new ruling. Put to the owner |
| 3 | hardening | by reading: `check_join_types` types a comparison operand only through a declared comparison predicate (`declared is not None`); IK5 admitted the infix form too | **deferred**, open question: making infix and predicate spellings agree changes IK5 behaviour |
| 4 | hardening | (a) yes; (b) by design (spec §15 "first maximal run") | (a) **fixed**: `_ELAPSED` anchored with `^`; regression `test_r4_…` observed red on ed54e65. (b) recorded; no change |
| 5 | hardening | yes, by the reviewer's cases | **deferred**: each accepted name means what it says, so no mistranslation; refusing values outside the export's threshold set needs the export at parse time |
| 6 | hardening | not reproduced by the author | **deferred**: argparse's literal choices, pinned by T2, keep a non-exporting target out today |
| 7 | completeness, an unmet spec §6 obligation | yes: SWI 10.0.2 `writeq` writes code points 7, 8, 11, 12, 13 as `\a \b \v \f \r` and every other control as `\xN\`, octal never; recorded by the author with the scratch SWI | **fixed**: the five escapes added to `_ESCAPES`; `test_r7_…` over the recorded writeq forms, observed red on ed54e65 for 7, 8, 11, 12, 13 |
| 8 | completeness | yes | **partly fixed**: T9's exit-0 termination is now derived from elapsed time against Popper's timeout, not from the outcome itself; `extract_program`'s success path has `test_r4_…`. **Deferred:** T9's import replay branch has never run (both recorded programs are empty), T5c's pair count and a `type_closures` subtype test |
| 9 | completeness | yes | recorded: the approved T3 test gained `adapter_version="1"` on its fake entry (IL1-F8); not in the A1 inventory, which lists fixtures only |

**What the author did not reproduce:** finding 6, and finding 3 beyond code
reading. They are deferred, not believed.
