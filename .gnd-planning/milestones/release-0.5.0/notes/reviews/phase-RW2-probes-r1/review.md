<!-- Edited by review_tool.py sanitize: 1 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
F1 (medium) — [tests/test_release_acceptance.py:906](<repo>/tests/test_release_acceptance.py:906): `readme_commands` accepts commands that the README no longer documents correctly.

The substring check accepts this replacement for the COUNT example’s first command:

```sh
other-gnd check model.orm.yaml population.json
```

It also accepts `# gnd check model.orm.yaml population.json`. P4 subsequently executes its hardcoded `gnd` command, so the README regression remains undetected. This contradicts C4.

I reproduced this in memory using both actual packaged README texts: replacing their first commands with another executable or a shell comment still returned all five COUNT commands and all eight growth commands. Removing the command from its shell block and retaining it only in a trailing HTML comment also passed. Each should fail. Validate documented command entries and executable tokens instead of arbitrary substrings.

All eight SHA-256 hashes matched the brief.

What I checked and found true:

- **C1:** Reading all six probe rows against §6 found the specified candidate results and controls represented, including P6’s explicitly shared behavior control. Nonempty guards, exact lists and required dictionary entries prevent the identified assertions from passing vacuously.
- **C2:** Comparison with `d5641d1d`, including an AST comparison of assertions, confirmed that retiring the four 0.3.0 controls removed no candidate assertion.
- **C3:** `program_constants` successfully read actual generated programs for both rules modes and the supported default include-root mode. P3’s content assertions and flattening-digest comparisons passed. Additional nested JSON, Unicode, quotes, backslashes and multiline literals parsed correctly; a trailing `raise` remained unexecuted.
- **C5:** The corrected release-note sentence agrees with the supplied 0.4.0 measurements, including its explicit role-scoped-value refusal.
- **C6:** The new probes obtain the specified examples, READMEs and binding file through installed-package resources. The two checkout fixtures used by P3 are explicitly permitted by the spec.

Other matcher checks passed: `written(...).startswith(out)` retained an unexpected Unicode filename for the exact-list assertion to reject; the `INCLUDE seed ` predicate handled CRLF and Unicode text, excluded `seedling`, and counted duplicate lines; resource-path splitting resolved both configured example directories. The README matcher rejected complete removal and equivalent doubled whitespace, confirming its dependence on literal formatting.

I could not independently rerun retained-wheel acceptance, the published 0.4.0 controls, or the source-denial families lane. Those runs create environments and scratch files, which this read-only review forbids. Executed checks used the existing editable environment and in-memory inputs; the supplied rehearsal results were reviewed as recorded evidence.

VERDICT: CHANGES_REQUESTED