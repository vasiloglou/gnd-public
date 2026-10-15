# Phase PL3 independent review: the deterministic agent loop

| | |
|---|---|
| Reviewer | one Claude subagent (same model family as the author), read-only except this file |
| Date | 2026-10-14 |
| Branch / HEAD | `codex/pyrel-agent-loop` @ `ad85288d918a28bc6281b600b003384511431d34` |
| Spec | `notes/phase-PL3-spec.md`; plan §0 (PL-R2, PL-R5, PL-R8), §2 "Agent loop" |
| Verdict | **approve** (no blocking finding; 5 hardening notes, 5 completeness notes) |

Reviewed bytes (`shasum -a 256`, untracked files):

```
fa9dd95bcd75012c84bdd853c22637afd43f4bf92bc90819023b0fae7e25803d  src/gnd/examples/bookrec/stand_in_agent.py
23ef45f64fd8aff72e46cf2918b0c2ddf69f506cb9c607ded7a0a465bcdaffbe  src/gnd/examples/expense/stand_in_agent.py
02b516a4958f66d11cb0b444adb76755953796411f86a0952d68e0715f51e612  tests/test_pyrel_stand_in_sessions.py
```

## 1. What was run

| Command | Result |
|---|---|
| `uv run pytest -q tests/test_pyrel_stand_in_sessions.py` | 4 passed, 2 deselected (2.72 s) |
| `uv run pytest -q tests/test_pyrel_stand_in_sessions.py -m pyrel_oracle` | 2 passed, 4 deselected (11.09 s); interpreter `tutorials/runtimes/.venv/bin/python` |
| `uv run ruff check` on the three files | All checks passed |
| `uv run ruff format --check` on the three files | 3 files would be reformatted (see C5; not enforced by the repo) |
| `uv run pytest -q tests/test_rf7_structure.py` | 1 failed, 1 passed, at `src/gnd/population_shape.py:298` (pre-existing, see C4) |
| Scratch replay of both sessions outside pytest (same contract/policy as `_session`) | bookrec and expense: exit 0, `attempt_count 2`, `disposition accepted`; attempt-1 `offending_facts` equal the pinned witnesses |
| `check_proposal` on the bookrec attempt-2 candidate | exit 0, accepted, exactly one `warning` (`preferred_genre`, `{"$b":"cosmos","$g":"science","$u":"ada"}`) |
| `execute_application(..., query_args=('report','',''))` on the expense attempt-2 candidate | exit 0, accepted, `calculation.report == {"approved": 2, "submitted": 3, "total_eur": 2260}` |
| Direct stdin feeds of the scripts (missing seed, malformed base64, non-JSON feedback, foreign pair, role-swapped pair, non-integer `$e`) | reproductions quoted under the findings |

## 2. Verified correct (priority order of the brief)

**P1 Repair logic vs. the feedback schema.** The reader path
`required[0].acceptance.violations[*].offending_facts` matches
`ConstraintAcceptanceFeedback.violations: tuple[ConstraintViolationFeedback]`
(`src/gnd/exp/session_eval.py:728-738, 800-806`) and the live attempt-1
`feedback.json` (schema 4) produced in the scratch replay. Facts are emitted
through `_sorted_untrusted_facts` (`session_eval.py:2177`) as plain dicts, so
`isinstance(fact, dict)` holds. `offending_pairs` sorts `str(v)` over
`fact.values()`, so it is independent of dict key order and of value type; the
witness `{"$b":"night","$u":"ada"}` and the row `{"user":"ada","book":"night"}`
both reduce to `('ada','night')`. Violations are listed only when
`payload_exit == 1` and the verdict is `fail`/`warning`
(`session_eval.py:2302-2318`), so the deontic `preferred_genre` warning that
attempt 2 provokes (ada/cosmos is science, Ada prefers fantasy) is **not** in
attempt-2 feedback (`payload_exit 0`), and the test's
`second[...]['violations'] == []` is sound. For the shipped inputs attempt 1
fires only `constraints[1]` (`counts: fail 1, pass 4`), so no other violation
can be mistaken for the age rule. Oscillation/stagnation: each script is a pure
function of the previous attempt's feedback; with the shipped inputs it
converges at attempt 2 (reproduced); under any other feedback it either repeats
a candidate (GND terminates with `stagnation`, `session.py:208-211`) or runs out
of `max_attempts 3`. No unbounded loop is possible.

**P2 Candidate integrity.** `json.dumps(seed, indent=2)` of a `json.loads`
result is structurally identical (ASCII-only seeds, integers, strings; key
order is irrelevant since `_preserve_source` compares with `sort_keys=True`
dumps and `Counter`s of row dumps, `src/gnd/export/applications.py:_preserve_source`).
The source is YAML-safe-loaded (`pyrel_runtime._parse_document`) and the
candidate JSON-parsed; for these seeds the two parses agree. `population.covers`
is carried verbatim. Confirmed by the passing `pyrel_oracle` test and by the
scratch `check_proposal` run (accepted with one warning; attempt-1 candidate
refused with `[[{"$b":"night","$u":"ada"}]]`).

**P3 Determinism and cwd.** `candidate_root = root / "candidate"`
(`src/gnd/commands/exp.py:170`) is passed once to `run_session`
(`exp.py:357`); the declared adapter runs the command with `cwd=candidate` on
every attempt (`src/gnd/declared_adapter.py:659-668`); snapshots are only
handed to verifiers (`exp.py:324`). So `../input/seed.population.json`
resolves on attempt 1 and attempt 2 alike (reproduced). Output is byte-stable
across runs (`best_candidate_sha256` identical between the pytest run and the
scratch replay is not asserted, but the scripts have no nondeterministic input).

**P4 Test strength.** If attempt 1 were accepted, `attempt_count == 2` and
`first['disposition'] == 'retry'` fail. If the repair introduced a violating
row, `result['disposition'] == 'accepted'` and `violations == []` fail.
`accepted_rows` pins the exact row list. The stdin message carries
`feedback_base64: null` on attempt 1 (`declared_adapter.py:362`), so the
`if encoded` branch for missing feedback is exercised by every session test.

**P5 Standing rules.** One reader function each (one walk). Missing/empty
feedback is tolerated (`None`, absent, `""`). Seed read is uncapped but the
spec binds inputs to the shipped seeds and GND caps the candidate and prompt
bytes independently.

**P6 ruff.** `ruff check` clean.

## 3. Findings

Severity: low unless stated. Class: hardening = behaviour outside the shipped
inputs; completeness = test/spec coverage. None is blocking.

### H1 Pair match is rule-blind and role-blind (hardening, low)

`src/gnd/examples/bookrec/stand_in_agent.py:28-32, 49`. `offending_pairs`
folds every violation of every constraint into sorted value tuples and the
repair deletes any recommendation whose values coincide, without looking at
`constraint_ref`/`$u`/`$b`. Scenario: a reader-local rule change (PL-R5
allows this via `gnd evolve`) or any violation naming a *seed* recommendation
deletes a handed fact and leaves `ada/night` in place.

Reproduction (direct feed, feedback naming `unread_only` on ada/map):

```
$ echo '{"feedback_base64":"<b64 of {"required":[{"acceptance":{"violations":[{"constraint_ref":"constraints[0]","offending_facts":[{"$u":"ada","$b":"map"}]}]}}]}>"}' | python3 stand_in_agent.py
$ # recommendation.population.json ->
[{'user': 'ben', 'book': 'night'}, {'user': 'ada', 'book': 'night'}, {'user': 'ada', 'book': 'cosmos'}]
```

A role-swapped fact `{"$u":"night","$b":"ada"}` likewise drops `ada/night`
(same root cause). Not reachable with the shipped inputs (attempt 1 fires only
`constraints[1]`). Suggested: match on `fact.get("$u")`/`fact.get("$b")` as the
expense script does with `$e`, or filter on `constraint_ref`.

### H2 `int(fact["$e"])` is not total (hardening, low)

`src/gnd/examples/expense/stand_in_agent.py:33`. A non-numeric `$e` raises:

```
ValueError: invalid literal for int() with base 10: 'E-102'
```

Only reachable if the reader changes the expense identifier type. Suggested
`if isinstance(fact.get("$e"), int)`.

### H3 Malformed feedback is a traceback (hardening, informational)

Both scripts, line 42. `feedback_base64` that is not base64 or not JSON
raises (`binascii.Error` / `JSONDecodeError`), exit 1, which GND records as
`agent-failure` (exit 15). GND never emits such bytes and the spec requires
tolerance of missing/empty feedback only; acceptable for a tutorial script.

### H4 Missing seed gives a bare traceback (hardening, low)

`bookrec/stand_in_agent.py:43`, `expense/stand_in_agent.py:44`. With the
contract rebound to a seed outside `input/`, the reader sees:

```
$ gnd exp run EXP-003-recommend-ada --adapter-policy agent.policy.json   # exit 15
{"...","disposition":"agent-failure","terminal_reason":"agent exited 1"}
$ tail -1 EXP-003-recommend-ada/runs/run-0001/attempts/0001/agent.stderr
FileNotFoundError: [Errno 2] No such file or directory: '../input/seed.population.json'
```

The stderr is retained and the path is named, so it is recoverable, but a
one-line `sys.exit("stand-in: expected the seed at ../input/seed.population.json next to the candidate directory")`
would save the reader a trip into `attempts/0001/`. (Moving the seed without
rebinding the contract is refused earlier by GND's digest-bound inputs;
UNREPRODUCED here.)

### H5 Uncapped seed read (hardening, informational)

Both scripts read the seed with `Path.read_text` and no byte cap. Spec §4
rule 2 argues inapplicability (inputs are the shipped seeds); GND caps the
prompt and candidate independently. No action required.

### C1 "missing_feedback" is not tested where the name says (completeness, low)

`tests/test_pyrel_stand_in_sessions.py:88-92`.
`test_stand_in_version_probe_and_missing_feedback` only runs `--version`. The
missing-feedback branch is exercised indirectly (attempt 1 of the session test
receives `feedback_base64: null`), but a direct `{}`-on-stdin case against a
temp `input/seed.population.json` would make the name true and give the
`if encoded` branch a failing case of its own.

### C2 Spec §5 promises not pinned by the oracle test (completeness, low)

`tests/test_pyrel_stand_in_sessions.py:117-120`. The spec promises
`check_proposal` accepts bookrec "with one warning" and `report` on the
expense candidate prints `2 approved`. Both hold (verified: one
`preferred_genre` warning; `calculation.report.approved == 2`) but the test
asserts only `accepted`. PL5 pages will print these numbers; pinning
`sum(status=='warning') == 1` and `calculation['report']['approved'] == 2`
here prevents a silent drift between the test and the page.

### C3 Comment overclaims the leak check (completeness, informational)

`tests/test_pyrel_stand_in_sessions.py:83-85`. "The feedback never carries
the answer" is one substring check. It is meaningful: attempt-1 feedback
contains neither `cosmos`, `finance` nor `team-lead` (verified on the live
bytes; the only data echoed are the offending bindings in `message` and
`offending_facts`). Reword to "the repaired value does not appear in the
attempt-1 feedback".

### C4 Spec §8 row 4 claims `tests/test_rf7_structure.py` passes (completeness, low)

It fails on this tree at `src/gnd/population_shape.py:298` (`json.loads`),
a pre-existing residual recorded in `002-phase-PL1.md:66` and
`pyrel-applications/014-milestone-close.md:83`. The two stand-ins are already
in the test's allowlist (lines 27-28, tracked at HEAD), so PL-R8 is
discharged for this phase; the PL3 record should cite the residual rather than
"pass".

### C5 `ruff format` would reformat all three files (informational)

Blank line after the module docstring in both scripts; single quotes and long
lines in the test. `ruff check` is clean, the repo does not run
`ruff format --check` anywhere (no reference in CI, tests or CONTRIBUTING),
and 64 existing test files use single quotes. No action unless the owner
adopts the formatter.

## 4. Verdict

**Approve.** The loop does what the spec and plan §2 require: a deterministic
first attempt that obeys the bad request, a refusal whose `offending_facts`
equal the pinned PL-R5 witnesses, a repair driven only by the closed feedback,
and an accepted candidate that the PyRel application also accepts
(`check_proposal` with one warning; `report` with 2 approved). No model call
(PL-R2). The hardening notes concern inputs the phase does not ship; H1 and C2
are the two worth a follow-up line in PL5 or the PL3 record.
