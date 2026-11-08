# ROF2 changed-bytes census (2026-11-07, head e1fb6a18)

Two runs of the same 122 test files (`census-files.txt`), each against a
scratch copy of `src/gnd` placed first on `PYTHONPATH`:

- base: an unmodified copy;
- probe: the same copy with `gnd.output._print_projected_text` changed to print
  `ROF2_CENSUS_PROJECTED_JSON_TEXT` and exit 99 before anything else.

A test red only under the probe executed the JSON-as-text printer that ROF2
replaces. `census_diff.py` (run from the directory holding the two raw logs)
produced `census-diff.txt`; the summaries are the logs' pass/fail lines. The
classification of the nine tests is in the ROF2 spec, section 11.
