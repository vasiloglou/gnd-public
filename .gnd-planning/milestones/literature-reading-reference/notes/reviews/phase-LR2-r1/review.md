<!-- Edited by review_tool.py sanitize: 1 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All ten SHA-256 hashes match the brief.

**1. Findings**

**F1 — P2: T5 does not protect two required README claims.**  
[tests/test_lr2_quote_scope.py:108](<repo>/tests/test_lr2_quote_scope.py:108) checks only `conflict.txt`, “writes no anchor sidecar,” and the reference link. It never checks that verification uses joined attempted sections or that extraction sidecars bind the documents.

I reproduced this without modifying files: monkeypatch the README’s `Path.read_text` result, replacing:

- `the attempted sections of that pass joined with newlines` with `the complete original source files without joining any sections`
- `in an extraction sidecar` with `without an extraction sidecar`

Then invoke `test_t5_the_example_readme_says_what_it_verifies()`. **It still passes.** Incorrect documentation of both behaviors can therefore pass this acceptance test. Extend T5 to cover those LR2-C5 requirements.

**2. Checked and found true**

- The current README accurately describes `reading.py`: joined attempted sections for each pass, `conflict.txt` for the reported conflict, extraction sidecars, and no anchor sidecars.
- In-memory probes through the real parser, binder, and anchored evaluator produced:
  - Whole source: bound, anchored verdict `pass`.
  - First section with matching digest: `anchor:binding-mismatch: source span or excerpt differs`.
  - First section with whole-source digest: `anchor:binding-mismatch: digest differs`.
- The reference correctly describes document scope, metadata labels, and the distinction between anchoring and semantic support. Both literature pages link it.
- T4 and T5 pass on the supplied bytes.
- Reading the draft reply and relevant implementation revealed no additional repository-behavior discrepancy.
- The added slices and branches operate on fixed fixture data; no added matcher improperly parses structured input.

**3. Limits**

I did not run the file-writing CLI tests, packaged replay, or full gate because the brief requires read-only work. The binding probes used memory only. Merge and release status in the draft reply were not externally verified. No files were changed.

VERDICT: CHANGES_REQUESTED