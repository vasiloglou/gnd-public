# IK5 adversarial review: one local reviewer agent

**One reviewer is one reviewer.** One local reviewer agent read
`git diff d0cb831 abc872a`, with the brief retained at
`evidence/IK5/review-brief.md`. Its report is below. The author then
reproduced each finding before believing it, and the disposition follows the
report.

The report is the agent's returned text with its findings, numbering,
severities, reproductions and verdicts kept. Its layout was set as markdown, and
a few sentences were joined or split. It is not a byte copy, and the raw return
was not retained in the repository.

## Report (as returned)

IK5 adversarial review: `git diff d0cb831 abc872a` on claude/ik5-ilp-bridge

No tracked file was edited. All scratch work is under /private/tmp/claude-501/-Users-nikolaosvasiloglou-github-repos-gnd-public--claude-worktrees-recent-commits-95fa1c/16650214-feb5-484f-a716-975b7f732cdd/scratchpad/ik5-review/ (SCR below): the harness is SCR/h.py (incl. `oracle()`, a Prolog-semantics evaluator of a positive clause over neutral.json, used to compare GND's coverage with what a faithful learner computes), test scripts SCR/t1.py–t14.py, mutation runs SCR/mut.py, corpus copies under SCR/work/ and SCR/repro/w/.

Bottom line: meaning preservation of the rewrite held on everything I tried (no admitted clause whose constraint differs from the learned clause through the rewrite itself). The real problems are three tracebacks on hostile input, one admitted proposal that `gnd evolve preview` then refuses, and tests that do not pin the rewrite's operator semantics.

## Findings

**1. BLOCKING — nested aggregates in Popper text crash with a traceback (exit 1); standing rule 1 / T3 "deep" Popper text not met.**
File: src/gnd/export/ilp_popper.py:180-182 and :200-202. An aggregate's goal argument is parsed with `self.literal(MAX_DEPTH - 1)`, which resets depth, so `self.deep(depth + 1)` at :181 never exceeds 4 for `count(count(count(…)))`; the parser accepts unbounded nesting, then the schema validation (ilp_service.py:216) recurses without limit (and at ~400 levels the parser itself does).
Repro: SCR/repro/w/agg.pl = `wrong(A):- f_order_amount(A,B,C),` + `count(`×300 + `f_order_flagged(A,B)` + `)`×300 + `.`
`uv run gnd import ilp-rules SCR/repro/w/orders.orm.yaml SCR/repro/w/agg.pl --labels SCR/repro/w/m.labels.json --reported-coverage SCR/repro/w/i2.run.json --target popper --out SCR/repro/w/agg.out.json`
Observed: `RecursionError: maximum recursion depth exceeded` traceback, exit 1 (50 levels: correctly refused "nesting deeper than 4", exit 3; 400 levels: RecursionError in the parser).
Expected: exit 3 `unparsable … nesting deeper than 4`. Pass the real `depth + 1` into goal arguments.

**2. BLOCKING — a Popper integer with more than 4300 digits crashes with a traceback (exit 1).**
File: ilp_popper.py:213 `int(value)` — Python's int-string conversion limit raises ValueError; a 1 MiB CLAUSES easily holds one.
Repro: SCR/repro/w/bigint.pl = `wrong(A):- f_order_amount(A,B,C),C > 111…1.` (4301 ones), same command as #1.
Observed: `ValueError: Exceeds the limit (4300 digits) for integer string conversion`, exit 1 (also for a 4400-digit negative).
Expected: exit 3 `unparsable` with line/column (or a pre-check on digit count). The neutral path is fine (RF7's long-int policy refuses).

**3. BLOCKING — a lone-surrogate string constant in a neutral clause crashes with a traceback (exit 1).**
File: ilp_service.py:245-251 `_validated` catches only ModelLoadError/ModelValidationError, but `output.add_operations` raises pydantic ValidationError from EvolutionOperation ("surrogates not allowed"); the RF7 JSON reader and the schema both accept `"\ud800"`.
Repro: SCR/repro/w/sur.clauses.json (clause body `f_order_amount(A,B,C)`, `f_order_by(A,B,{"const":"\ud800"})`), SCR/repro/w/sur.run.json binding E and the clause digest correctly;
`uv run gnd import ilp-rules SCR/repro/w/orders.orm.yaml SCR/repro/w/sur.clauses.json --labels SCR/repro/w/m.labels.json --reported-coverage SCR/repro/w/sur.run.json --target neutral --out SCR/repro/w/sur.out.json`
Observed: `pydantic_core._pydantic_core.ValidationError: 1 validation error for EvolutionOperation … surrogates not allowed`, exit 1 (nothing written).
Expected: exit 3, named (refuse non-scalar code points at the clauses read, or catch it as `invalid-guarded`).

**4. HARDENING — the import admits (exit 0) a proposal that `gnd evolve preview` refuses; GND's re-check also read a different constant than evolve does.**
File: discover/output.py:91 (`candidate_text`, "JSON is a YAML subset") reached from ilp_service.py:236-242 and :394-404. A learned string constant containing a raw U+0085 (NEL) is written verbatim into the candidate text; `load_model_bytes` (used for check 10 and re-evaluation) reads it as `"\x85x"`, but evolve's `_parse_model_text` reads it as `" x"`. A raw DEL (U+007F) makes evolve's YAML reader raise `ReaderError: unacceptable character #x007f`.
Repro: SCR/t12.py then SCR/t13.py (population with blocked customers `" x"` and `"\x85x"`; clause `wrong(A):- f_order_by(A,B,C), f_customer_blocked(A,"\u0085x")`).
Observed: import exit 0; operation `after` holds `"\u0085x"`; evolve's parser on the proposal's candidate text gives `{'customer': ' x'}`; `gnd evolve preview` → `EVOLUTION PREVIEW REFUSED (3): declared operations do not equal the canonical candidate model`.
Expected: spec §5 says preview of an admitted proposal exits 0. Either refuse such constants at import (named fragment/spelling refusal) or make `candidate_text` escape them. Safe downstream, but the import claims success. (Root cause is pre-existing IK4 code; IK5 makes it reachable from arbitrary learner text.)

**5. COMPLETENESS (meaning-critical) — the tests do not pin the rewrite's semantics: 13 of 17 meaning/format mutants survive the whole of tests/test_ilp_bridge.py (72 passed).**
Method: SCR/mut.py copies src/gnd to SCR/mut/<name>, applies one mutation, runs pytest with PYTHONPATH there (verified the mutant module is the one imported). Survivors: NEGATE `<`→`>` (instead of `>=`); NEGATE `=`→`=`/`!=`→`!=`; parser `=\=`→`=`; boolean true/false mapping (I-F5) removed; `variable()` reduced to `"$v_"+name.lower()` (non-injective); one shared `$anon`; no `example-variable` check inside comparisons; no arity check on comparison predicates; designation of first instead of last atom (C-F6 not actually pinned); `quote()` without escaping `'`/`\`; `quote()` without control-char escaping; `_unquote` `\n`→`n`; facts sort without its canonical-JSON tiebreak. Killed: constant-spelling, unbound-comparison, unchecked-as-covered, counterexample cap.
The implementation is correct today (SCR/t1.py checks 25 Popper clauses — `<`, `=<`, `>=`, `=`, `\=`, `=:=`, `=\=`, constant on the left, comparison predicate with constant on the left, negative ints, repeated variables in one atom, symmetric joins, boolean/string/entity constants — against the Prolog oracle; all agree), but spec §8's branch-walk claim fails: these branches can be broken without a red test. The corpus uses only `>` comparisons, so the set-equality backstop would not catch the `<` mutant unless an example sits exactly on the boundary value.
Expected: one T5-style case per operator and per Popper operator spelling, plus boolean-role, variable-encoding, `_`, and quoting round-trip cases.

**6. HARDENING/COMPLETENESS — the work counters are tautological, and the 1,000,000-fact bound is unreachable.**
- Import counter (ilp_service.py:417-419): `verdicts = len(populations) * len(cores)` is arithmetic, not counted, and `checks ≤ P` by construction, so `total > ceiling` (→70) can never fire and T9's `0 < total <= ceiling` cannot fail. The real verdict read (:350-352) scans all of `population.report.verdicts` for every (population, clause) pair — O(P·K·V), not "one verdict read per (population, clause)" as spec §4 rule 2 says. Check 10 also reloads the full candidate model K+2 times, which no counter records.
- Export counter: `facts` is capped before it is reported, so that check cannot fail; it is never printed, so T9's "export at or under P + F_max" is not observable.
- Unreachable bound (ilp.py:186 vs :213-215): the smallest possible neutral.json fact entry is 97 bytes (`{"example":"a","predicate":"f_a","values":[1]}` at indent 2), so 1,000,000 facts need ≥ 92.5 MiB > the 64 MiB file cap; the cap always refuses first (at ≤ ~690k facts). The `too-large` facts branch is reachable only by the T3 monkeypatch. The IK5-D14 bounds are mutually inconsistent.

**7. COMPLETENESS — the Popper tokenizer misreads `\xHH\` escapes before a closing quote and has no octal escapes.**
File: ilp_popper.py:34 `(?P<quoted>'(?:[^'\\\n]|\\.)*')` treats the closing `\` of a hex escape as escaping the next character, so `'\x41\'` (valid Prolog for 'A') → `unparsable … unexpected "'"`; `'\x0\'` and `'\x10FFFF\'` give the same error (so T3's "escape-range" case passes for the wrong reason). The renderer's own output (e.g. `'c\x1\\'\\x'` from `quote()` for the value "c\u0001'\x") cannot be read back. SWI's writeq prints control characters as octal `\001\`, which `_unquote` rejects. All exit 3, so nothing silently changes meaning, but a learned constant containing a control character can never be imported.

**8. COMPLETENESS — check 8 ignores `_`, so the refusal name is wrong.**
File: ilp_rewrite.py:55-56 `_vars` drops `_`, so checks 6/8 treat `g(X,B,_)` as ground and designate it; the rewrite then puts an unbound `$anon1` in the absence.
Repro (SCR/t1.py): `wrong(A):- f_order_amount(A,B,_),f_order_link(A,B,_).` → `clause 0: invalid-guarded: ['semantic:guarded-consequent-ground']`, exit 3.
Expected (spec check 8 "every variable of the designated literal"): `non-ground-absence`.

**9. COMPLETENESS — aggregates whose goal is a conjunction, a negation or a comparison are `unparsable`, not `aggregate`.**
`aggregate_all(count,(f(..),g(..)),N)`, `findall(B,\+ f(A,B),L)`, `findall(B,C > 3,L)` → `unparsable` (ilp_popper.py:200-203 accepts only `name(` goals). Spec §6 says aggregates are parsed so they are refused by name. Still exit 3; naming gap only.

## What held

- Meaning preservation: 40 clauses checked against the oracle (SCR/t1.py, t2.py, t3.py, t6.py). Every admitted clause matched the oracle exactly: comparison orientation and negation, constants on either side, atom and infix comparison forms, `=`/`!=`/`=:=`/`=\=`/`\=`, negative integers, repeated variables within one atom, symmetric joins, mixed entity/value joins. Scalar typing: `'7'` ≠ 7, true ≠ 1 at integer and boolean roles, 'true' at a boolean role, string-vs-integer joins. Every disagreement was a refusal, never an admission. The variable encoding is injective over the schema's ASCII grammar; Unicode variables are refused by the grammar; a `$`-leading constant is refused; a string that matches a guarded variable name cannot pass.
- Binding: E is recomputed from MODEL, MANIFEST and target; population bytes are digest-checked on both reads; the candidate is built from the same model bytes. `clauses_sha256` is computed over the very bytes that are parsed. `uniqueItems` blocks repeated reported ids; duplicate manifest ids are refused; the same file under two ids or classes behaves correctly (SCR/t9.py). Vacuous and unknown ids refuse; covers-nothing refuses.
- Loaders: BOM, empty file, UTF-16, non-UTF-8, NUL, floats, Unicode names, doubled quotes, deep `not`/parens, over-long names/variables/arguments, deep JSON (RF7 depth cap), NaN/1e400, a CLAUSES path that is a directory or FIFO (66), and symlinked clauses/run/model/labels (74) all refuse with named exit 3/66/74, not tracebacks. A JSON BOM is accepted by RF7.
- Export: byte-identical under PYTHONHASHSEED 0, 1 and 7 on a five-fact-type model; quoting escapes `\`, `'` and control characters (no break-out); type mismatches in populations are exit 5; a 30-digit integer exports; redaction refuses role-level and fact-type-level redaction, and the taint direction matches GND's policy (a redacted derived role does not taint sources). Duplicate population facts are exported as duplicates (harmless).
- Regressions: the labels.read_population and discover.output.add_operations/proposal refactors are behaviour-preserving by reading (`constraint["type"]` == `candidate.core["type"]`, defaults keep IK4 ids and rationale). test_ilp_bridge.py, test_measure_labels.py and test_discover.py: 213 passed together. test_rf1_cli_pins.py, test_rf5_commands.py, test_public_built_inventory.py and test_rf1_pin_harness.py: 415 passed together. `gnd evolve preview` exits 0 on an admitted repeated-variable proposal from my own model.
- Not checked: whether a real Popper accepts the rendering (e.g. `type(wrong,(ex,))`, missing `direction` declarations for the comparison predicates). This is IK5-D13, open by design. The full RF6, layering and docs suites were not run.

## Disposition (author, 2026-10-26)

**Reproduction.** Findings 1, 2, 3 and 4 were rerun from the reviewer's inputs:
- 1 and 2 give a traceback;
- 3 gives a traceback with the pydantic error;
- 4 gives import exit 0, then preview exit 3.

Finding 8 follows from `_vars` dropping `_`, and its regression test fails
before the fix. Finding 5 was rerun with the reviewer's own mutation harness.

**Triage and action:**

| # | Class | Action |
|---|---|---|
| 1 | blocking | **fixed:** aggregate goal arguments carry the real depth. Regression `test_r1_nested_aggregates_are_bounded` |
| 2 | blocking | **fixed:** an integer literal of more than 32 digits is `unparsable` (the schema's bound is 2^53 − 1). Regression `test_r2_a_huge_integer_is_unparsable` |
| 3 | blocking | **fixed:** check 9 refuses any non-printable character in a string constant, under `constant-spelling`. Check 10 also maps an operation's pydantic error to `invalid-guarded`. Regression `test_r3_r4_…[\ud800]` |
| 4 | hardening | **fixed** at the import by the same check 9 rule (NEL, DEL, U+2028, tab, surrogates). IK4's `candidate_text` is unchanged and stays a boundary item for discover. Regression `test_r3_r4_…` (5 cases) |
| 5 | completeness, meaning-critical | **tests added:** each operator and Popper spelling, injective variables, fresh `_`, comparison refusals, last-atom designation, boolean roles, quoting and escape round-trips, and the facts sort. All 17 of the reviewer's mutants are now killed (`evidence/IK5/mutants.txt`). These tests pin correct behaviour, so they pass on both copies by design |
| 6 | hardening, partial | **fixed:** verdict reads are counted, one per (population, clause), from one ref index per report, and the export prints its work. Regression `test_r6_the_export_reports_its_work`; the import count is coverage. **Recorded:** the bound inconsistency is IK5-Q1, because a bound moves only by owner ruling (IK-R12) |
| 7 | completeness | **tokenizer fixed:** the `\xHH\` escapes that `quote()` writes now read back. Regressions `test_r7_quoted_atoms_round_trip` and `test_r7_prolog_escapes_are_read`. **Octal escapes deferred** (IK5-Q2) |
| 8 | completeness | **fixed:** an atom or comparison holding `_` is never ground, so the refusal is `non-ground-absence` or `unbound-comparison`. Regression `test_r8_an_anonymous_variable_is_never_ground` |
| 9 | completeness | **deferred** (IK5-Q3). It is still exit 3; only the name differs |

**Red on the pre-fix code.** The new tests were run against a copy of
`abc872a`'s `src` (`evidence/IK5/regressions-red.txt`):
- the eleven fix regressions fail there and pass after the fixes;
- the R5 and R6-import tests are coverage, passing on both.
