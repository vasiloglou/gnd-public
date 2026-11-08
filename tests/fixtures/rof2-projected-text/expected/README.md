# ROF2 corpus answer key

The expected results for the cases in `../README.md`, kept apart so a reader
can work out the answers from the stories alone.

## How it was written

- `reports/<case>.json` is the base's `--format json` report for the same
  invocation (branch `claude/plan-report-output-fidelity-6d5b5d`, `src/`
  identical at `e1fb6a18` and `f1a57836`). The text must be a rendering of
  exactly these rows; the JSON output itself must not change (the test pins
  these bytes).
- `<case>.txt` is the report's rows rendered with the **plain** routes' own
  renderers at the base: `gnd.output._print_transition` for a walk,
  `gnd.output.render_check_rows` for the check layout,
  `gnd.output._print_admission_text` for the admission trailer, and the
  extraction line as `_cmd_verify` spells it. A refused case is the plain
  route's `ERROR at …` lines. `derive_answers.py` is the script; it must run
  with the base source first on `PYTHONPATH`, where `_print_transition` still
  reads walk objects, so nothing in it calls code ROF2 adds.
- The header `REDACTION <mode>: <fact_type.role>, …` is printed when the
  report carries redaction declarations and omitted when it carries none (the
  temporal walk; plan D2, applied on every projected route).
- The reason suffix (ROF1-O1, extended to walk lines by ROF2 D3) is applied
  to a row's message before rendering. No row in this corpus has a
  `reason_code`, so it changes no answer here; the spec pins that branch at
  payload level.
- A computed end state is one JSON line, as the plain route prints it (ROF2
  D4); its redacted cells are markers in `applied` mode.
- `exits.json` gives each case's exact arguments, exit code and report
  version.
- Honest limits: no `WARNING at …` line (no model here produces a model
  warning); no `[finding]` line under a derivation; the computed end state
  line and the refused case's message carry digests and paths, which pin this
  corpus's exact model bytes.
