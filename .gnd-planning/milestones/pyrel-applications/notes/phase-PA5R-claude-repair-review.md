Retained the one bounded Claude Code repair review (claude -p --permission-mode plan, prompt notes/phase-PA5R-repair-review-prompt.md). Raw SHA-256 e9f9f3cf900dc03bd0538aafd8768676551ee41662a07ad8c0f829e12afb0f98 at evidence/PA5R/claude-repair-review-raw.md; text below is verbatim. No third pass. One reviewer is one reviewer.

# PA5R bounded repair review

## Verdict

**The code repairs hold. The evidence and one record claim are wrong.**

- **Resolved in code and pages:** B1, B2, B4 and B5, plus hardening items H1–H5, H7 and H8.
- **B3** is closed by a delegated ruling. I accept it, but it should be shown to the owner (see below).
- **H6** was declined. That is acceptable.
- **H9 is not resolved.** The triage says a transcript from a clean HEAD was kept, but `evidence/PA5R/preexisting-failures.txt` is four lines of prose. Nothing else mentions `50eba83`.
- **The final evidence is stale.** `tools/run_tutorials.py` and `tests/test_tutorial_output_blocks.py` were last changed at 22:34:13, after every "final" transcript (the latest is 22:33:59). `focused-default-final.txt` actually records the failing H6 attempt, not the final tree.

I found no new blocking defect in the code.

## Resolution per finding

| Id | Resolved? | Evidence |
|---|---|---|
| B1 | Yes | `cli.py:55-56` refuses `--proposal` unless the backend is `pyrel`. A test covers it, though its name `test_gnd_backend_proposal_preserves_input` no longer fits what it checks. |
| B2 | Yes | `04-native.md:53-90` matches chapter 2's setup (`02-application.md:13-50`) word for word, plus `native_query.py`. Conformance is not run on the page. |
| B3 | By ruling | `04-native.md:233-235` still sets a JSON path in code. The override is recorded at spec line 191. |
| B4 | Yes | New `_list`/`_text` helpers at `applications.py:303-309`, used by `format_result` from `:317`. The three shapes from the first review and two proposal shapes are tested. I found no remaining crash on JSON-shaped input. |
| B5 | Yes | Every app command runs in `( cd … && … )`. The chapters say how to run Python blocks (`07:34-36`, `04:33-35`), and the overview says to stay in the folder (`:52`). |
| H1 | Yes | `run_tutorials.py:162-166` sets the status only after both the exit-code and output checks. |
| H2 | Yes | The size cap moved into `_check_and_publish` (`applications.py:149-150`). |
| H3 | Yes | Reasons are flattened to one line. `07-native.md:260` now has a correct coverage row. The "could not be decided" row is reachable (`pyrel_runtime.py:1828-1829`, exit 2). |
| H4 | Yes, with drift | `pyrel_runtime.py:1650` makes a deep copy. `kind=` was dropped, but spec line 85 still lists it. |
| H5 | Yes | `04-native.md:234,237` reads and prints the old value from the model. |
| H6 | Declined | The runner discards text after unchecked commands (`run_tutorials.py:34`). The PA5R pages are guarded by `test_native_chapters_show_output_for_every_block`. |
| H7 | Yes | The D7 gate now checks exit-code rows for a plain cause and fix, and checks next-steps links on all three pages. |
| H8 | Yes | "enterprise data" is gone. "not yet supported" is honest, since the exporter returns 64. |
| H9 | No | Only prose is kept, and the concern that the rf7 test stops at the first offending file is not addressed. |

## New findings

- **N1, medium (evidence):** no transcript covers the current runner or test bytes. Re-run the default lane and the BookRec/Expense groups, and rename or replace `focused-default-final.txt` (its lines 93-142 show the H6 failures).
- **N2, medium (record accuracy):** spec line 202 claims a clean-HEAD transcript was kept. It wasn't.
- **N3, low:** at `applications.py:283`, `document['facts'][name]` raises `KeyError` (exit 70) when the owned relation is missing from both the input and the proposal. It should be a clean exit 3.
- **N4, low:** with `--proposal`, the CLI (`cli.py:49-56`) still requires `recommend|complete`, then ignores it. `--user`, `--limit` and `--preferred-only` are silently ignored too. The page shows `recommend --proposal` (`07:132`).
- **N5, low:** the toolkit table in `pyrel-apps.md:62-75` leaves out `app.has`, `app.check_work` and `app.derivations`, which both shipped queries use. "Ends with two lines" is also inaccurate.
- **N6, low:** totals print two ways: "2260 EUR total" (`04:138`) and "EUR 2260 total" (`04:291`).
- **N7, low:** the 9-character status column misaligns `incomplete` and `unsupported` rows.

## Remaining junior stuck points (none blocking)

1. Pasting a Python block after `"$GND_TUTORIAL_GND_PYTHON" -` needs Ctrl-D, and the pages never say so (`07:35`, `04:35`). A heredoc would avoid it.
2. A bare `gnd codegen` (`04:57`) gives "command not found" if the reader skipped the PATH step. There is no troubleshooting row for that.
3. `Published: ../ada.json` is relative to the subshell's folder. From the work folder, the file is at `bookrec-native/ada.json` (`07:114`).
4. `recommend --proposal` reads as if it computes recommendations.
5. Re-running a chapter fails at the copy step (`FileExistsError`). Only "output already exists" is covered.
6. Expense step 3 never explains `aggregates` or `app.ref`.

## Opinions on B3 and H6

- **B3: acceptable to proceed, but not settled by the ruling alone.** A2 D2 banned JSON-path edits even in its fallback. The fallback's condition was also not met, since `gnd evolve` can make the change. So the ruling overrides an explicit A2 sentence because the evolve path is costly, not because it is impossible. It is recorded with the prior answer under the auto=true delegation. List it as an owner-visible exception at milestone close. A shipped one-operation evolve proposal file would not be a sixth model, so that option stays open.
- **H6: acceptable.** Refusing stray text would break two existing pages, and on the PA5R pages every marked command must show checked output anyway.

## Reading bounds

- **Read in full:**
  - The spec, the initial review, and A2 D2 with its gate record.
  - The diffs of `applications.py`, both CLIs, the seam, the BookRec query, the runner, the D0 pages and `zensical.toml`.
  - All three pages, the Expense query and chapter 2's setup.
  - Three new test files: `test_pyrel_learning_path.py`, `test_pyrel_proposal_check.py` and `test_tutorial_output_blocks.py`.
  - The evidence listing, `preexisting-failures.txt`, `repair-red.txt`, the `focused-*-final` tails, `pyrel-successor.json`, and file modification times.
- **Not read:** `test_pyrel_native_seam.py`, the other test diffs, the receipt JSON contents and the query `.txt` twins. The 12 screenshots are present but I did not view them.
- **Not done:** nothing was run, so the successor hash was not recomputed.

The report is also saved in the plan file `~/.claude/plans/bounded-pa5r-repair-peppy-nebula.md`.
