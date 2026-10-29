# IL-close: the review of the code predicate 7 names

One reviewer is one reviewer. The owner asked, on 2026-10-29, for "an
independent review of the milestone code that never had a review opinion (the
code named under predicate 7) before I accept the close". A single
general-purpose agent reviewed it the same day, judging HEAD (`3c01567`) and
reproducing each finding before reporting it. It wrote only under the session
scratch directory, written `<scratch>` below, edited no repository file and
ran no learner.

**Scope.** The commits that landed after their phase's review:

| Commit | What | Its phase review covered |
|---|---|---|
| `16cbbe1` | IL1's review fixes | `5576a4e..ed54e65` (IL1) |
| `c03ff94` | IL1 amendment 2: Popper adapter 3, ground threshold facts | the same |
| `b906749` | IL1's refactor | the same |
| `58704ed` | IL2's review fixes | `65fd6df..bf15642` (IL2) |
| `b8caf6c` | IL2-D13/D14 code and step 5 refactors | the same |

Predicate 7 named the last four; `16cbbe1` also landed after IL1's review, so
it was added. Records `004` to `008` name no unreviewed code. This review did
not read the rest of the milestone diff (`07f4d45^..HEAD`).

## The report

### Review of 16cbbe1, c03ff94, b906749, 58704ed and b8caf6c, judged at HEAD

I found no blocking defect. There are two hardening findings and one
docs/code mismatch, all reproduced. I edited no repository files. The probe
scripts are in `<scratch>/review-p7/` (`probe1.py`, `probe2.py`, `fuzz.py`).
Run each with `uv run python <path>` from the worktree.

#### Findings

**1. Hardening. The Popper target has no 32-bit integer refusal, though its `bk.pl` is grounded in clingo.**
- **Originating commit:** b8caf6c (IL2-D14 was implemented only in `ilp_asp._term`). The exposure comes from c03ff94: amendment 2's ground threshold facts are what Popper's clingo grounding reads.
- **Location:** `src/gnd/export/ilp_popper.py:87-92` (`_term`), `:135-141` (fact and threshold-fact lines).
- **Reproduction:** `probe2.py` builds a neutral form with amounts 5, 3000000000 and -2147483649.
  - The Popper render writes them all without refusal: `f_r('e1',3000000000).`, `gt_t_amount__5(3000000000).`, `lt_t_amount__3000000000(-2147483649).`, `gt_t_amount__m2147483649(5).`
  - The ILASP render of the same input refuses: `unrepresentable: 3000000000 is outside clingo's 32-bit integer range (IL2-D14)`.
- **Why it matters:** the docs (lines 66-68) and `test_a2_t3_clingo_grounds_every_threshold` both establish that Popper v5.0.1 analyses `bk.pl` in clingo. The IL2-D14 ruling records that clingo silently wraps such integers. So Popper's grounding, recall deduction and pointless-relation query would see wrapped values.
- **Expected:** the same `unrepresentable` refusal for `--target popper`, or a documented ruling that Popper is out of D14's scope. The spec scopes D14 to ILASP, and the docs say nothing about Popper.
- **Fix:** move the range check into a shared helper, used by `export_value` or by both adapters' `_term`. Add a Popper test with 2^31 and -2^31-1.

**2. Hardening. The Popper parser accepts threshold names the renderer never writes.**
- **Originating commit:** c03ff94. b906749 kept the behaviour.
- **Location:** `ilp_popper.py:314-326` (`_comparison`). The popper entry in `ilp_learners.py` has no `vet` (`vet=None`).
- **Reproduction (`probe1.py`):**
  - `gt_t_amount__501(V2)` parses to `{'predicate': 'gt_t_amount', 'args': [V2, {'const': 501}]}`, with no threshold at 501.
  - `gt_t_amount__99999999999(V2)` parses to const 99999999999. That is outside 32 bits, and no export could contain it.
  - A `gt` at the maximum is also accepted. The renderer omits it (empty extension), so Popper's bias never declared it.
- **What is inconsistent:**
  - The parser already refuses `__m0` and leading zeros as "a threshold name the renderer never writes". Values that were never rendered pass that same test.
  - ILASP refuses the same situation as `off-threshold` because the learner "could not have learned it from the export" (docs lines 296-299). For Popper it is just as true: the predicate is not in `bias.pl`.
  - Coverage-mismatch does not catch it: `> 501` usually covers the same examples as `> 500`.
  - `ge`/`le` names are read on purpose (docs line 77). Only the never-rendered values are the defect.
- **Fix:** add a popper `vet` that refuses `off-threshold` for any threshold atom outside the rendered names from `threshold_rows(neutral)`, plus a test.

**3. Completeness (docs disagree with code). The ILASP extractor stops at the first blank line.**
- **Originating commit:** 58704ed.
- **Location:** `ilp_asp.py:181-186`, against `docs/reference/ilp-bridge.md:317-319` ("every non-blank line after ILASP's last `%%` line"). The commit message says the same as the docs.
- **Reproduction:** `extract_hypothesis("%%%%\n%% Total : 1s\n%%%%\nwrong :- p(V1).\n\n:- q(V1).\n")` returns `'wrong :- p(V1).\n'`. The constraint after the blank line is dropped silently, which is the IL2-F8 failure mode in a different shape. The docstring ("first maximal run") matches the code; the docs do not.
- **Fix:** either take every non-blank line, so a second block reaches the reader and is refused, or correct the docs and the docstring. Add a test with a blank-separated second block. Today no test can tell the two behaviours apart.

#### Not reproduced (no clingo run)
- **Underscore-digit identifiers in the ASP reader** (58704ed, IL2-F9 gap): `_1`, `__` and `_9a` are read as variables (`f_r(_1)` gives `{'var': '_1'}`, verified). By clingo's lexer grammar (identifiers and variables are `_*` followed by a letter), clingo reads `_1` as an anonymous variable followed by a number, which is a syntax error. That is "read differently by clingo", but I did not execute clingo.
- **The value -2147483648:** the reader and the export both accept it. If clingo lexes it as unary minus applied to 2147483648, that token overflows first. Not verified.
- **Left-guarded aggregate, outside these commits:** `2 < #count{…}` is refused as `builtin-comparison`, not by the aggregate refusal name.

#### Outside scope
At HEAD, `tests/test_ilp_learners.py::test_t8_the_milestone_directory_is_private_clean` fails. A home-directory token sits in `.gnd-planning/milestones/ilp-learners/009-milestone-close.md:158`, from 3c01567. Focused run: 249 passed, 1 failed (this test).

#### What held
- **Totality:** 200,000 random inputs each to `parse_program`, a quoted-atom variant, `parse_hypothesis`, `parse_hypothesis` with a `wrong :- ` prefix, `extract_hypothesis` and `extract_program`. No non-`IlpError` exception and no exit code other than 3.
- **Octal fix (16cbbe1):** `'\1\\'` gives exit 3, "a backslash ends a quoted atom".
- **Quoting round trip:** `quote()` → parser was exact over 50,000 random strings with controls, backslashes, quotes and non-ASCII. The `\a\b\v\f\r` escapes are covered by the corpus.
- **Log prefix:** the elapsed-seconds prefix is anchored, applied once per line, and banner detection works after it is stripped.
- **Threshold naming:**
  - `m` for negatives, `__m0` and leading zeros refused, values longer than 32 digits refused.
  - The value is read after the last `__`, so type ids containing `__` parse correctly.
  - The rank formula gives distinct ranks and keeps the minimum and maximum; empty extensions are omitted.
- **32-bit bound on ILASP:** export and reader agree. 2^31-1 and -2^31 are accepted; 2^31 and -2^31-1 are refused on both paths. Thresholds are covered because they are drawn from the context values, which are checked.
- **IL2-D13:**
  - Bare `web` is refused unparsable, while bare `true`/`false` are read as booleans.
  - A quoted `"true"` on a boolean role is refused only where `boolean_strings=False`, which is ILASP alone. This is wired at the single `rewrite` call site (`ilp_service.py:354`).
  - The Prolog/ASP difference this creates matches the docs.
- **Refactors in b8caf6c:** `observed_integers`, `COMPARISON_NAME` and `refusal_name` are textually identical moves, so behaviour is preserved.

(The "Outside scope" paragraph is retained with the token it quoted replaced
by "a home-directory token": the quoted token is the one IL-R10's privacy test
refuses.)

## Reproduction and triage (the author)

Each finding was reproduced from the reviewer's probes before any fix: the
probes' output matched the report line for line. Each fix has a regression
test in `tests/test_il_close.py` (R7 to R9), shown red against `3c01567` in
`evidence/IL-close/p7-red.txt` (7 failed; the one pass is R8's control that a
rendered threshold is not refused). At `3c01567` the three never-rendered
thresholds reached re-evaluation: `gt_t_amount__501` was stopped only by
`coverage-mismatch`, and the other two by `covers-nothing`, so a run record
reporting their coverage would have admitted them.

| # | Class | Disposition |
|---|---|---|
| 1 | hardening | **fixed, R7**: `gnd.export.ilp.clingo_integer` is the one range check, and both adapters spell integers with it. The Popper export refuses an integer outside clingo's range `unrepresentable`, with ILASP's message (IL2-D14). Every input the Popper export accepted before renders to the same bytes, so its adapter version stays 3 |
| 2 | hardening | **fixed, R8**: the Popper entry gains `vet=ilp_popper.check_thresholds`, which refuses a `gt_` or `lt_` threshold name `bias.pl` does not declare as `clause K: off-threshold`. It reads the names the parser mapped from the clause text, because the strict clauses schema keeps no trace of a name: the binary spelling `gt_t_amount(C,80)` that the approved IK5 corpus pins (I2, F12) is unchanged. So the vet hook now receives the clause text as well; ILASP's check ignores it. This discharges IL1-Q3's out-of-set half, which `009` carried |
| 3 | completeness, taken | **fixed, R9**: the extractor takes every non-blank line after the last `%%` line, as IL2-F8, `003`, the commit and the docs all record. Completeness is deferred by default; it is taken because the gap is IL2-F8's silent drop in another shape and the fix is one line. IL2's `test_extract_takes_one_run_after_the_last_banner` pinned the first-run behaviour; it is renamed `test_extract_takes_every_line_after_the_last_banner` and now expects the third rule (ILC-F9). All three retained ILASP logs end with the hypothesis and a blank line, so each re-extracts to the same bytes |
| outside scope | privacy | **fixed**: the token in `009` is reworded. The close gate's `test_ilp_learners` T8 is green again |
| not reproduced 1 | — | **carried, IL-close-Q2**: whether clingo reads `_1` as the reader does needs a clingo run, which no owner ruling covers here |
| not reproduced 2 | — | **carried, IL-close-Q2**: the same for `-2147483648` |
| not reproduced 3 | — | **not a defect here**: the refusal still names the construct and exits 3; outside these commits |

**ILC-F9 (an IL2 test's expectation moved).** The moved assertion is not in an
owner-approved corpus; it pinned code that disagreed with the recorded IL2-F8
fix. It is returned to the owner with this record, as ILC-F5 and ILC-F6 were.

**IL-close-Q2 (carried).** Run clingo 5.x over `f(_1).` and `f(-2147483648).`
and refuse in the ASP reader whatever it reads differently. Target: the same
milestone as IL2-Q2's rerun.

## Refactoring review

**Refactors EXECUTED:** the 32-bit range check moved from `ilp_asp._term` to
`gnd.export.ilp.clingo_integer`, so the two adapters share one home and one
message. Behaviour-preserving for ILASP: its message and exit are unchanged and
its tests pass unchanged. The ASP *reader* keeps its own `_INT_RANGE`: it
refuses `unparsable` with a line and column, a different contract.
