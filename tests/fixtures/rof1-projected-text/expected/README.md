# ROF1 corpus answer key

The expected results for the cases in `../README.md`, kept apart so a reader
can work out the answers from the stories alone.

## How it was written

- `reports/<case>.json` is today's `--format json` report for the same
  invocation (main `12daa5b7`). The text must be a rendering of exactly these
  rows; the JSON output itself must not change (the test pins these bytes).
- `<case>.txt` is the report's rows rendered with the **plain** route's own
  renderer (`gnd.output._print_report`), preceded by the header and followed
  or replaced by issue and `OK:` lines per the spec's section 6 layout.
  `derive_answers.py` is the script; it must run against the source of main
  `12daa5b7` (PYTHONPATH), where the plain renderer predates this phase, so
  nothing in it calls code this phase adds.
- The header `REDACTION <mode>: <fact_type.role>, …` is printed when the
  report carries redaction declarations, and omitted for the temporal-only
  route (plan decision D2, ruled 2026-11-07).
- `exits.json` gives each case's exact arguments, exit code and report
  version.
- Honest limit: the corpus does not exercise `WARNING at …` lines (no fixture
  model here produces a model warning); the spec's T4c pins that line at
  payload level.
