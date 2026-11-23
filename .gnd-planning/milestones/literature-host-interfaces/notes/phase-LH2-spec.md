# LH2 spec · replay of a caller run

## 1. Status

owner-decided (2026-11-23) by **delegated approval (auto=true)**: see §7 and
§12. Base commit `0c23f30c` (LH1's record). Prior status: "Draft, 2026-11-23.
Waits for LH1's record (its hard prerequisite) and then for its gate".

## 2. Provenance

Derived from [plan r6](literature-host-interfaces-plan.md) (sha256
`2dc760e5…1528`, approved in `001-plan-gate.md`): Goal (LH2), §0, §2 "LH2",
§3 LH2 row, §4 LH2-C1 to LH2-C7, §5, §9 LH2 row, and D5. It builds on the
LH1 implementation at `83de2846` (`feat(phase-LH1)`), whose spec is
`phase-LH1-spec.md`. Code read on 2026-11-23 at that commit. No review has
run over this spec.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| Goal LH2, §2 LH2 | `replay(folder, fixture=ROOT)` re-derives a `/2` run from its folder and the caller root, with zero producer and reviewer calls; no producer, reviewer, budget or limits argument | §6.1; T1 |
| §2 LH2, R0.5 | every setting and step status is read from the manifest | §6.2; T1, T7 |
| §2 LH2, LH1 fix 3 | the run's files are read under the retained-file cap the run recorded, through a reader local to `reading.py`; `/1` replay keeps `reading._read(folder, name)` | §6.2; T3, T5 |
| §2 LH2 | refuses a response table, receipt table, stage, payload or input whose bytes differ, and a manifest whose settings exceed a ceiling | §6.2; T2, T3, T4 |
| §2 LH2 | `expected_evidence_sha256=` compares the run with the digest `run()` returned; the README says a consistently rewritten folder replays without it | §6.1, §6.4; T2 |
| LH2-C1 | the LH1-C1 run replays byte-identical, same evidence digest, zero calls | T1 |
| LH2-C2 | one changed byte in the response table or a receipt refuses; a consistently rewritten folder refuses when the expected digest is given | T2 |
| LH2-C3 | non-default limits replay with them, including the completing LH1-C14 run at the response ceiling; a setting above its ceiling refuses | T3 |
| LH2-C4 | a changed source, profile, model or include refuses "stale reading input" | T4 |
| LH2-C5 | a `/1` run replays as today; `test_ld3`, `test_ld4`, `test_ld5` pass unedited | T5 |
| LH2-C6 | `score_reading_coverage` scores the caller run when given its root | T6 |
| LH2-C7 | a manifest that claims `skipped` for a step the profile declares refuses | T7 |
| §3 LH2 row, §5 | `assurance_report.py` one pass-through argument; the README; `docs/literature/commands.md`; `docs/release-notes.md`; `dev/components/` | §6.3, §6.4 |
| §9 LH2 row | the focused lane, then `uv run python tools/run_tutorials.py --group literature` | §8 ledger |
| LH1 T14 | LH1's refusal of a `/2` replay is replaced; its test changes with it | §6.1; T8 |

## 4. Standing rules, bound to this phase

| Rule | Bound here |
|---|---|
| R0.1 formats stay | no key added to the stage, attempt or coverage rows; the `/2` manifest is LH1's |
| R0.2 packaged bytes | `/1` replay unchanged; T5 runs `test_ld3`, `test_ld4`, `test_ld5` unedited |
| R0.3 example status | `main()` gains no argument; `replay` on the command line still takes the packaged root |
| R0.4 one loop | replay runs the same `_evaluate` as `run()`; the only branch is where the responses and receipts come from |
| R0.5 settings retained | replay has no settings argument; it reads them from the manifest (T1, T3) |
| R0.7 stable commands judge | the routes are re-run as in the run |
| R0.8 ceilings | a manifest setting above its ceiling refuses (T3) |
| 1 totality | the manifest is a new untrusted input: `_caller_settings` checks every key, type and range before use; T3, T9 |
| 2 time bound | replay is linear in the run's files; T3 replays the LH1-C14 run at the response ceiling within the same 60 s bound |
| 3 validation order | manifest, settings and steps, then the run's files, then the inputs, then re-derivation. T9 pins that a malformed manifest refuses before any run file is read |
| 4 one walk | as R0.4 |
| 5 one home | `reading_fixture/README.md` keeps the protocol; `docs/literature/commands.md` gains a short passage that links to it and restates nothing normative |
| 6 measurement | T2's consistently rewritten folder is produced by a second real run, not by hand |

## 5. Goal

`replay(folder, fixture=root)` over a `/2` folder and its caller root returns
the run's report with zero producer and reviewer calls, or refuses with
`ExampleError` or `ArtifactError`. The plan §9 LH2 row, the guard block and
the whole-repository `uv run ruff check` exit 0.

## 6. Design

Reuse: `examples.literature_reading` (LH1's `_evaluate`, `_read_retained`,
`ReadingInputs`), `infra.artifacts` `read_regular_bounded`. No new component.

### 6.1 Signatures

```python
def replay(folder: Path, *, fixture: Path = FIXTURE, vocabulary_fixture: Path = DEPTH_FIXTURE,
           expected_evidence_sha256: str | None = None) -> dict: ...

def score_reading_coverage(run_dir: Path, expected_rows: list[dict], *, fixture: Path | None = None) -> dict: ...
```

A root with `profile.json` replays a `/2` run; a root without replays a `/1`
run, as today. A `/2` manifest under the packaged root refuses "a caller run
replays against its own root"; a `/1` manifest under a caller root refuses
"a packaged run replays against the packaged root". `expected_evidence_sha256`
applies to both and refuses "reading evidence differs from the expected
digest".

### 6.2 The `/2` replay, in order

1. `run.json`, read with the retained-file ceiling, canonical, format `/2`.
2. `settings` and `steps`: the closed key sets of LH1 §6.5; every limit an
   `int` from 1 to its ceiling, `retained_bytes` included; the document
   budget `null` or from 0 to `max_budget`; `producer` `live` or `saved`;
   `reviewer` `live`, `saved` or `none`; each step `ran` or `skipped`.
3. The artifact roster equals the set a run with those steps writes. Each
   file is read with the recorded `retained_bytes` through
   `_read_run_file(folder, name, max_bytes)`; stage records are read and
   chained before any payload, as for `/1`.
4. `ReadingInputs(fixture, ...)` with the recorded limits, unavailable
   sections and producer and reviewer kinds. A live run's responses come from
   its retained table and its receipts from its retained `reviews.json`;
   neither is added to the inputs. The manifest's `steps` must equal the
   profile's ("reading steps differ from the profile"), and its `inputs` the
   inputs' pins ("stale reading input").
5. `_evaluate` with no producer and no reviewer, the retained responses from
   the payloads, and the recorded settings. The re-derived manifest and
   artifacts must equal the run's ("re-derived reading evidence differs").

### 6.3 Other modules

`assurance_report.score_reading_coverage` passes `fixture` to `replay` when
given. `revision.py` is not edited.

### 6.4 Documents

- `reading_fixture/README.md`, "Drive it from your host": replay of a caller
  run, `expected_evidence_sha256`, and the sentence that without it a
  consistently rewritten folder replays.
- `docs/literature/commands.md`: a short "Drive it from your host" passage
  after Act 3's reading section, linking to the README.
- `docs/release-notes.md`: one entry under a new unreleased heading for the
  reading pair (LH1, LH2).
- `dev/components/COMPONENTS.md`: the reading and assurance entries, then
  `components_index.py write`.

## 7. Decisions

| ID | Question | Proposed | What the other reading costs | Ruling |
|---|---|---|---|---|
| LH2-D1 | How replay tells a `/2` run from a `/1` run | By the root: a root with `profile.json` replays `/2` | Reading the manifest first needs one cap for both formats, which moves the `/1` read path `test_ld3` patches | as proposed (delegated, auto=true, 2026-11-23) |
| LH2-D2 | Where a live run's receipts come from on replay | The retained `reviews.json`, outside the inputs | Adding them to the inputs changes the input pins the run recorded | as proposed (delegated, auto=true, 2026-11-23) |

## 8. Tests

`tests/test_lh2_reading_replay.py`.

| ID | Case | Expected | Criterion |
|---|---|---|---|
| T1 | LH1's plain run and a declared run with a live reviewer, replayed with a producer and reviewer that fail the test if called | report equal to the run's, same `evidence_sha256`, `producer_calls` zero, the folder's bytes unchanged | C1 |
| T2 | one byte changed in `producer-output-table.json`, and in `reviews.json` (manifest digest updated each time); a second run of the same root with other answers, replayed with the first run's digest and without it | refuses; refuses; refuses with the digest, replays without it | C2 |
| T3 | a run with lowered roster and raised input caps; LH1's 63-section run at the response ceiling; a manifest with `route_seconds` 601 | each replays with its settings; the 63-section replay within 60 s; refuses | C3 |
| T4 | after the run, one changed byte in a source, the profile, the model and the include | each refuses "stale reading input" | C4 |
| T5 | the unedited `test_ld3`, `test_ld4`, `test_ld5` | pass | C5 |
| T6 | `score_reading_coverage(run, rows, fixture=root)` with the run's own coverage rows | `status` `pass` | C6 |
| T7 | a manifest that says `calibration: skipped` replayed against the declared profile | refuses "reading steps differ from the profile" | C7 |
| T8 | a `/2` folder under the packaged root; a `/1` folder under a caller root | refuse, each with its message | §6.1 |
| T9 | manifests: not canonical; a settings key missing; an extra key; `retained_bytes` `null`; a limit `True`; a step `maybe`; the artifact roster missing `reviews.json` for a reviewed run. `_read_run_file` fails the test if called | each refuses before any run file is read | rule 1, 3 |

LH1's `test_t14_replay_of_a_caller_run_is_not_yet_available` is replaced by
T8 (the refusal it pinned is the one this phase removes).

Verification-selection ledger:

| Obligation | Disposition | Command | Input boundary | Invalidation |
|---|---|---|---|---|
| plan §9 LH2 row | run | `uv run pytest -q tests/test_lh2_reading_replay.py tests/test_lh1_reading_host.py tests/test_ld3_reading_workflow.py tests/test_ld4_revision.py tests/test_ld5_verdict.py tests/test_li1_assurance_report.py --tb=short`, then `uv run python tools/run_tutorials.py --group literature`, exit 0 each | `reading.py`, `assurance_report.py`, the fixtures, `docs/literature/commands.md` | any edit to those |
| guard block | run | `project.md`'s twelve-file command, exit 0 | the guarded inventories and pages | any scanned file |
| lint | run | `uv run ruff check`, exit 0 | the whole repository | any Python file |
| component index | run | `python3 scripts/components_index.py changed --base 0c23f30c --strict`, exit 0 | `dev/components/` | a changed module |
| broad lanes | cadence | `uv run pytest -q -m "evidence or census"`, explicit request only | historical replays | none |

## 9. Out of scope for this phase

The admission module (LH3, LH4). A replay command-line flag for a caller
root. Retaining a partial run. Any change to `revision.py`'s replay of the
packaged run.

## 10. Size

Estimate: `reading.py` +90 lines; `assurance_report.py` +3; the test module
about 260 lines; the docs about 40 lines.

## 11. Approval instrument

This prose.

## 12. Gate

Delegated approval (auto=true), 2026-11-23, under the owner's
`/process-milestone literature-host-interfaces auto`. Instrument: this prose.
Decisions: LH2-D1 and LH2-D2 as proposed (§7). Budget: one review round over
the phase diff with the review helper (plan D13), a second only if the
convergence rules call for it. Compatibility: `/1` replay unchanged;
`test_ld3`, `test_ld4`, `test_ld5` unedited. Ordering: the milestone
coordinator's GO for LH2 (2026-11-23) concerns file order with
literature-reading-reference and approves nothing. Spec bytes: the SHA-256 is
recorded in the phase record.

Implementability sweep, at `0c23f30c`: `run.json` is read directly with the
retained ceiling and every other run file through `_read_run_file`, so T9 can
forbid the latter while the manifest is checked. A live run's responses for
replay come from its retained table, which holds exactly the attempted
sections; the replay path's comparison of a payload's response with the
table therefore looks each section up and refuses a missing one rather than
indexing it. Every other requirement maps to LH1 code that exists.

## Implementation findings (2026-11-23)

1. **Refuted premise: the retained-file ceiling of plan D4 (64 MiB) cannot be
   read back.** Every JSON reader in the repository goes through
   `gnd.input_policy`, which refuses JSON over `MAX_BYTES`, 10 MiB. LH1's
   63-section run at the response ceiling completed with a 63 MiB payload
   that its own replay could not decode ("invalid example JSON"), which
   contradicts LH1-C14 and LH2-C3. Measured, then repaired in this phase by
   delegated approval (auto=true): `LIMIT_CEILINGS["retained_bytes"]` is
   `gnd.input_policy.MAX_BYTES`, imported, so the two cannot drift; LH1's
   and LH2's ceiling runs use 9 eligible sections at 1 MiB instead of 63;
   the README's table and sentence follow. Widening the shared reader is out
   of scope (R0.7). The plan's D4 row is repaired at milestone close; an
   open-questions row in this phase's record names it.
2. **Replay decodes payloads under the recorded cap.** LH1 decoded a
   payload with the fixed 1 MiB default; `_retained_files`, now shared by
   both formats, decodes each file under the cap it was read with.
3. **The reviewer's kind is a flag in `_evaluate`.** Replay passes no
   reviewer, so `live_review` (from the manifest) decides whether
   `reviews.json` is re-derived from the receipts or copied from the root.
   The run passes the same flag.
4. **Saved and retained receipts share one check.** A live run's retained
   receipts go through the saved receipts' input-time check on replay.
5. **LH1's T14 is replaced by T8**, as §8 says.
