# Independent PA5R diff review

Try to refute PA5R. Read amendment A2 (notes/plan-amendment-a2.md and
010-plan-amendment-a2.md), the PA5R spec (notes/phase-PA5R-spec.md, including its
findings F1–F10), and the working-tree diff against HEAD (git diff, plus the new
untracked files listed below). One reviewer is one reviewer. Read/search only;
read-only git diff/show/status/log are allowed. Do not run Python, tests, native
tools, providers or agents. Do not open .env files, credentials or .agents/skills.
Make no file edits. This is the one initial pass; at most one bounded repair pass
may follow for reproduced blocking findings.

New untracked files: docs/pyrel-apps.md, tests/test_pyrel_learning_path.py,
tests/test_pyrel_native_seam.py, tests/test_pyrel_proposal_check.py,
tests/test_tutorial_output_blocks.py, evidence/PA5R/* (including
pyrel-successor.json, preexisting-failures.txt, run transcripts and screenshots).

Producer claims to test:

- The public seam (NativeApp/open_app/run_app in src/gnd/export/pyrel_runtime.py)
  preserves admission, coverage, limits, version pin and the exit protocol; both
  native_query.py files use only it plus relationalai; outputs are identical to
  the committed checkpoints (F1).
- check_proposal keeps PA-R1/R5: the PyRel checker (not gnd.api) decides; the
  proposal is digest-bound and preserved-source-checked before checking;
  nothing is published on refusal. _check_and_publish is shared, not duplicated.
- format_result is total and never reports acceptance the result does not carry.
- The runner output grammar cannot pass a page whose output differs, keeps the
  old block shape, marker-count invariant, skip semantics and receipts.
- Both chapters and the overview satisfy A2 D4 (ten steps, keep-list: six
  figures with captions, exact witnesses, input-unchanged, completion vs
  acceptance, warning/unknown) and D7; the D0 pages no longer overclaim Snowflake.
- Pre-existing failures (F3) are genuinely pre-existing, and the rf2 successor (F2)
  is an honest, authenticated delta rather than a hidden pin rewrite.

Second job, the junior-reader pass: read docs/pyrel-apps.md, then
docs/bookrec/07-native.md and docs/expense/04-native.md as a junior Python
developer who knows a little PyRel and nothing about GND. List every place you
would get stuck or misunderstand, and list every claim the pages make with the
evidence (file:line) that supports it, or "unsupported".

Report: verdict; numbered findings with severity (blocking / hardening /
completeness), file:line evidence and the smallest repair; the junior-reader
stuck list; the claim table; reading bounds; refactoring suggestions.
