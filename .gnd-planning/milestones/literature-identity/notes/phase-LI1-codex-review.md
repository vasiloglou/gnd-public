# Adversarial review: LI1 @ 4c261d29 (base 547acaf1)

> **Edited for retention.** The absolute path of the reviewer's checkout was
> replaced with `<repo>`, and `/tmp` in finding 4's command is kept as the
> reviewer typed it. The text is otherwise verbatim. The trailing `codex exit
> 0` line is the launcher's, not the reviewer's.

**Instrument.** `codex exec --ephemeral --model gpt-6-sol --config
model_reasoning_effort="xhigh" --sandbox read-only --color never
--skip-git-repo-check -`, with the prompt on stdin. It exited 0.

**Scope.** One reviewer is one reviewer. The reviewer did not run pytest or
the builder, because both write files. It reproduced findings 1–3 and 5 in
memory and ran finding 4's command.

## Review (verbatim)

## Findings

1. **A run can omit composed output and still pass.** [Freshness checks only the sources present in the record](<repo>/src/gnd/examples/literature/assurance_report.py:589); it never compares them with `run.json`. In memory, I removed `posex` from the composition manifest, then ran `gnd.composition.compose()` and `verify_composition()`. Both accepted the 11-source result against a run declaring 12 sources. The composed output lost two asserted facts, while its seven derived rows remained. With the unchanged reference route outcomes, the harness’s five active scoring functions all returned `pass` (exit rule: 0). This is an **in-memory reproduction**; I did not write a run to test the full CLI.

2. **Refused routes can leave a stage marked `pass`.** Supplying `_validity()` with 12 R1 results of `exit=4, payload=None` produced `pass`, agreement 12/12 and `refused_units=0`. Supplying `_freshness()` with 12 R2 results of `exit=3, payload=None` produced `pass`, precision and recall 25/25. These in-memory calls break amendment A3’s per-stage refusal rule. [Validity](<repo>/src/gnd/examples/literature/assurance_report.py:450) compares exits alone; [freshness](<repo>/src/gnd/examples/literature/assurance_report.py:542) does not count those route refusals.

3. **Malformed shapes can get the wrong refusal reason.** I substituted a corpus document with `"split":[]`, then an answer assertion with `"support":[]`, through an in-memory `read_json` override. In each case `score()` returned exit 3 with `reason:"internal"` rather than `input:schema`. The unchecked set-membership operations in [shape validation](<repo>/src/gnd/examples/literature/assurance_report.py:183) raise `TypeError`.

4. **The CLI can print a traceback.** Running `.venv/bin/python -B -m gnd.examples.literature.assurance_report /does-not-exist /does-not-exist /does-not-exist --out /tmp` exited 1 with an `IsADirectoryError` traceback. The [output write](<repo>/src/gnd/examples/literature/assurance_report.py:757) is outside the exception handler.

5. **The “CLI only” claim has a metadata exception.** The routes use subprocess CLI calls, but [_gnd_version()](<repo>/src/gnd/examples/literature/assurance_report.py:615) calls `gnd.resolve_version()` directly. Replacing that function in memory with one returning a sentinel made `_gnd_version()` return the sentinel.

## Checked without another defect

- Direct status probes confirmed zero-denominator failure, refused-unit failure, and inclusive exact `9/10` comparison. Source inspection confirmed the 4 MiB primary JSON cap is applied during the read.
- All nine committed report goldens agree with their approved expectation files; each mutation golden names its required failing stage. I did **not** rerun the mutations.
- The literal routes contain none of the forbidden flags or combinations. Two in-memory double-fault probes returned the specified earlier reasons: `input:schema` and `corpus:digest-mismatch`.
- Gold builds-on rows and supported assertions match 8-for-8. I read every development passage against its assertion label and found no clear omitted builds-on claim.
- Pure builder regeneration matched committed document, answer-key and gold-population bytes. The held-out key was absent and its committed digests agreed. I did not run pytest or the full rebuilding builder because those write files.

## Triage and disposition

Each finding was reproduced before any change. Each fix carries a
regression test that fails against the code at `4c261d29`. The red run gave
7 failed and 1 passed: the eighth case, a population `source` given as an
object, was already refused and stays as a control.

| # | Finding | Reproduced | Class | Disposition |
|---|---|---|---|---|
| R1 | A composition that leaves out a run source still passes | Yes, end to end through the CLI: with posex removed from the manifest and the run recomposed, `gnd compose` composed 36 facts from 11 sources, and the report exited 0 | blocking | Freshness now requires the composition record to name exactly the run's sources. Otherwise the unit is `composition:sources-differ`, and the run exits 1. Test: `test_composition_missing_a_source_fails` |
| R2 | A route that prints no report still counts | Yes, with a stand-in gnd that breaks one route. Broken R1 left validity `pass` and the run exited 0. Broken R2 left freshness `pass`, and the run exited 1 only through source binding | blocking (validity), hardening (freshness) | An unreported route (no exit or no readable payload) is a refused unit, so the stage fails under A3. This covers validity's R1 and freshness's anchor sidecar, which binds a vocabulary digest only R2 can check. The extraction sidecar is not tied to R3: every digest it binds is checked on raw bytes by the harness, and `gnd fidelity`'s exit-3 refusal is plain text, so tying it to R3 would mark measured units refused and move M3's approved freshness numbers. Tests: `test_unreported_route_is_refused[R1]`, `[R2]` |
| R3 | A field of the wrong type is refused as `internal` | Yes: `split: []` gave `internal` | hardening | A `TypeError`, `KeyError` or `AttributeError` raised during shape checking is `input:schema`. Test: `test_shape_type_errors_refuse_as_schema` (three cases, one a control) |
| R4 | An unwritable `--out` prints a traceback | Yes: exit 1, with an `IsADirectoryError` traceback | hardening | The write is inside the process boundary's handler. A failure reports `output:unwritable` at exit 3. Test: `test_cli_unwritable_out_has_no_traceback` |
| R5 | The version comes from importing gnd | Yes (`from gnd import resolve_version`) | completeness | The version is read from the fidelity route's payload, and the harness imports no gnd module. Test: `test_harness_reads_gnd_only_through_the_cli` |

**What the fixes did to the approved cases.** Nothing. The nine
regenerated report goldens differ from `4c261d29` only in
`harness_sha256`, and the expectation files are byte-identical.
