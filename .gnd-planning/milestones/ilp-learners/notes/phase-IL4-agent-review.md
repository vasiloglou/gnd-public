# IL4 adversarial review (step 4)

**One reviewer is one reviewer.** One local agent read `git diff 70266b5
f6ded68` on 2026-10-28 under the brief in
[`evidence/IL4/review-brief.md`](../evidence/IL4/review-brief.md). Its report
follows as returned; `<repo>` and `<scratch>` stand for the repository and
scratch paths. The reviewer edited no tracked file, ran no java, AMIE, live
test or run script, and wrote under `<scratch>/il4-review/`, except one
early pytest run whose `tmp_path` files went to the system temporary
directory (its own process note).

## The report

IL4 adversarial review of `git diff 70266b5 f6ded68`. I found 7 defects: one blocking, three hardening and three completeness. Every one was reproduced. The scripts are under <scratch>/il4-review/ and are run as `uv run python <scratch>/il4-review/X.py` from <repo>. `harness.py` there builds a work directory under <scratch>/il4-review/work/, writes a run record that matches, and runs `python -m gnd import mined-rules`.

### Findings

**1. BLOCKING: a rule whose body falls into disconnected parts passes the mapping and the count, then exits 70 "internal".**
- Where: src/gnd/export/ilp_amie.py:254-296 (`mapped` has no connectivity row) and src/gnd/export/ilp_service.py, the checker cross-check that raises RuntimeError.
- Repro: `<scratch>/il4-review/dangling.py`. The rule `?a f_works_in ?f  ?f f_team_site ?b  ?x f_parks_at ?y => ?a f_based_at ?b` with Support 20, over the staffing fixture.
- Observed: exit 70, `internal: constraints[0] holds by GND's count but the checker says 'unchecked'`.
- Cause: `gnd check` on the same constraint returns `verdict unchecked, reason_code join-disconnected` ("fact types ... share no anchor object type"). GND's count is a cross join, which the checker refuses to evaluate.
- Expected: exit 3 with a named mapping refusal. Either the rule is not closed (`?x` and `?y` occur once, which is outside AMIE's closed-rule language), or the body is disconnected. The internal-defect exit should not be reachable from input.
- Related, not refused either:
  - A connected rule with a variable that occurs once (`... ?a f_parks_at ?y => ...`) is admitted, exit 0. It holds and the checker passes it.
  - A disconnected rule that does not hold is refused `does-not-hold` (20 of 60), so only the holding case reaches exit 70.
- No test covers the exit-70 branch.

**2. HARDENING: a subtype join passes `type-confused-join`, but the count can never confirm it, because spelling uses each role's own object type.**
- Where: ilp_amie.py:64-76 and 117-129 (`spell(object_type, ...)` per role) against `check_join_types` with closures.
- Repro: `<scratch>/il4-review/subtype.py`.
  - Model: `manager subtype_of staff`, `manages(manager, team)`, `works_in(staff, team)`.
  - Population: m1 manages t1 and works in t1; m2 manages t2 and works in t2.
  - Rule: `?a f_manages ?b => ?a f_works_in ?b`.
- Observed: with Support 0 it is refused `rule 0: does-not-hold: 0 of 2 head pairs hold`; with Support 2 it is refused `support-mismatch: ... GND counts 0 of 2`. The export writes `manager:m1` and `staff:m1` as different entities.
- The checker disagrees: the same constraint added to the model gives `gnd check` → `accepted`, `constraints[0] pass`.
- Expected: the count and the checker agree on value identity across subtypes, or the mapping refuses subtype joins by name. The error is conservative (a false refusal, never a false admission).

**3. HARDENING: duplicate rules are detected only when byte-identical.**
- Where: ilp_amie.py:217-220. The key is the printed body and head.
- Repro: `<scratch>/il4-review/reader.py` (cases dup-renamed, dup-permuted) and `<scratch>/il4-review/planted.py`. The planted rule is given three times: as printed, with variables renamed (`?c/?d/?e`), and with the body permuted.
- Observed: exit 0. The proposal has 3 guarded constraints with the same meaning, each with 20 examples.
- Expected: refuse duplicates up to variable renaming and body order. T-live's `_canonical` already defines that equivalence; IL4-F10 shows AMIE renames variables.

**4. HARDENING: the run record does not bind the model or the export, so the same rules, record and population bytes are read under any model.**
- Where: ilp_service.py `_cmd_import_mined_rules`. Only the learner name, the rules SHA and the population SHA are compared; `relations.json` and `export_sha256` are never consulted.
- Repro: `<scratch>/il4-review/modelswap.py`. The fixture model with `based_at`'s roles reordered to (site, staff) and its reading adjusted.
- Observed: the original model gives exit 0. The swapped model gives exit 3 `rule 0: type-confused-join: variable ?b joins site and staff`. That is a mapping refusal name for what is really a binding mismatch.
- Impact: for a relation whose two roles have the same type, a role swap would be named `support-mismatch` or `does-not-hold`, or could be admitted with the reversed meaning (it would still hold, because GND recounts).
- Expected: bind the model or export digest in `gnd-mined-run/1`, or document that the rules are interpreted under whichever model is given.

**5. COMPLETENESS: the export refuses non-control characters as "control character", contradicting the docs.**
- Where: ilp_amie.py:73-75 (`str.isprintable`).
- Repro: `spell("t", "a b", where="x")`. The same holds for U+200B and U+3000.
- Observed: `unrepresentable: x holds a control character the triple export cannot spell`.
- The docs (ilp-bridge.md "The export") and spec §6 say only tab, newline and backslash are escaped and "any other control character" is refused. Non-breaking spaces and other separators are refused too, with a wrong message.
- Expected: refuse only control characters, or document the rule as "non-printable" and fix the message.

**6. COMPLETENESS: the missing-`--labels` stderr for popper/neutral is unchanged only when `--labels` is the only missing argument.**
- Where: src/gnd/commands/export.py `_ilp_inputs` (a post-parse check that runs after argparse).
- Repro: `bash <scratch>/il4-review/cli.sh` compares this branch with `git archive 70266b5` extracted under <scratch>/il4-review/old.

| Argv | Before (70266b5) | Now |
|---|---|---|
| `M --target popper` | `required: --labels, --out` | `required: --out` |
| `M --out o` | `required: --labels, --target` | `required: --target` |
| `--target popper --out o` | `required: model, --labels` | `required: model` |

- All exits are still 64. The single-missing case is identical, which is what T7 tests.
- Expected: either accept this (the spec moved the `unknown_flag` golden) and narrow T7's claim, or include `--labels` in argparse's combined message.

**7. COMPLETENESS: test gaps (branches with no case that can fail).**
- The checker-disagreement exit 70 has no case (see 1).
- Subtype joins: m8 tests only an incompatible join (see 2).
- `body_size_agrees` True has no case; c5 covers False.
- T9's `outcome["learner"] == script.learner(stdout)` cannot fail, because `learner()` ignores stdout and returns a constant.

### What held

- **Reader totality:** a leading `+`, an empty figure, `-0`/`-2` as counts, `?A`, `?aa`, `?r` and `?` as a relation, NBSP and NUL in the rule, CRLF, U+2028, blank and trailing blank lines, an arrow with no head and an empty body are refused; single, double, leading and trailing spaces are accepted; a constant or `=>x` passes the reader and is refused by the mapping. Caps hold at the bound and one over: 256/257 rules, 18/19 digits, 4/5 atoms; near 1 MiB accepted, non-ASCII over 1 MiB of bytes refused. Nothing raised other than IlpError.
- **Mapping order:** open-world-head before unknown-predicate (IL4-F5), constant, reflexive, recursion, unbound-head, join check; variables spelled `$v`, roles in model order.
- **Admitted shapes:** closed 3-atom rules are admitted and pass the checker.
- **Counting:** the bound caps bindings and work (at most 3× the product) and is checked before the join; population typing prevents int/str and bool/"true" collisions (both refused at load, exit 5); escaping is injective.
- **Admission and binding:** examples capped at exactly 256; refs correct beside existing top-level constraints; nothing written on any refusal triggered.
- **Evidence:** rules.txt hashes to reported.json's rules_sha256; the population digest matches; facts.tsv matches the golden (65 lines, AMIE "Loaded 65 facts"); import-stderr.txt matches the outcome; no home path, user name, email or scratch path in evidence/IL4; T-live's `_canonical` is correct up to renaming and body order.
- **Tests and surfaces:** test_ilp_amie (not live) all pass; RF1 pins and harness 154 passed, only the listed goldens moved; RF6, conformance payload, ilp_learners and the built inventory 118 passed. Per-Python golden identity not checked (one interpreter).

## Reproduction and triage (the author)

Every finding was reproduced from the reviewer's scripts before any fix.

| # | Reproduced | Class | Disposition |
|---|---|---|---|
| 1 | exit 70 `internal: … 'unchecked'` | blocking | **fixed**: the mapping refuses `disconnected-body` (the fragment table's existing name) after `unbound-head`, before the join check; a connected body with a lone variable is still admitted. Regressions `test_r1_…` (the first red before the fix) |
| 2 | `does-not-hold: 0 of 2`; `support-mismatch … 0 of 2` | hardening | **deferred, IL4-Q1**: a false refusal only, never a false admission; spelling by a shared root type needs a ruling on multiple supertypes. Documented as a boundary |
| 3 | 3 constraints admitted for one rule | hardening | **fixed**: the reader's duplicate key is `ilp_amie.canonical` (renaming and body order), which T-live now uses too. `test_r3_…`, red before the fix |
| 4 | `type-confused-join` under a role-swapped model | hardening | **documented, IL4-Q2**: binding the export digest changes `gnd-mined-run/1` after the run of record, whose retained `reported.json` would no longer replay. The docs state the rules are read under the given model and can never admit a rule that does not hold there |
| 5 | `control character` for U+00A0 | completeness | **fixed**: message and docs say non-printable. `test_r5_…`, red before the fix |
| 6 | three multi-missing messages differ | completeness | **accepted**: exit 64 unchanged; T7's claim is the single-missing case; recorded in the boundary |
| 7 | as stated | completeness | **fixed**: `test_r7_…` (body size agrees); T9 compares the learner with `LEARNER` and with `reported.json`; the exit-70 branch is unreachable after 1 |
