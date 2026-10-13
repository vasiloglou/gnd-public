# Local CI assurance/session diagnosis 2

2026-10-13. Read-only production diagnosis at root `f446dc1`; comparison baseline
`ab879dc`. Only this note written. No broad suite or recertification.

## Frozen assurance denominator — introduced by this PR

`tests/test_rf1_semantic_pins.py::test_assurance_blocks` fails solely because
`phase3_scope_ids()` adds seven `snapshot:compiled-subset:n-a:*` rows. Its golden
diff contains clean, vacuous, violated alethic/deontic, uncovered, unavailable and
work-limit additions, with no band/decision/block changes.

Cause: `src/gnd/assurance/core.py:_phase3_target` describes the published Phase 3
roster as frozen but still admits every otherwise-unexcluded snapshot row.
PR 19 adds seven snapshot registry rows; the unchanged broad inclusion picks
them up. The baseline did not contain those registry rows. This is introduced
by this PR, rather than evidence that new scope is certified.

Recommended repair: explicitly exclude compiled-subset from the frozen Phase 3
denominator, matching the existing newer-family exclusions. Keep the historical
golden and certificate bytes unchanged. Add an explicit successor/current test
asserting that compiled branches remain registered while none appears in the
historical denominator and opted-in public results retain assurance level none.
Do not recapture the golden to enlarge the historical proof's scope.

## Session pins — ambient environment, not assurance drift

Bounded current reproduction:

```
.venv/bin/python -m pytest -q tests/test_rf1_semantic_pins.py::test_assurance_blocks 'tests/test_rf1_session_pins.py::test_session_fresh[1]' tests/test_rf2_instrument.py::test_successor_current_case_is_green --tb=short
```

Observed: 3 failed in 2.69s. Independently constructed the RF2 v1 fresh observed
answer and recursively compared it with its retained answer. Executions and
declared inputs were identical; observation differences were only
`attempts/000{1,2}/attempt.json` invocation environment names/provenance. The
current parent exposes LANG, LC_ALL and TERM; those inherited facts make 10
environment records versus the golden's 7. No credential values were read or
printed. This is not an assurance level mismatch.

Confirmed with a bounded controlled launch:

```
env -u LANG -u LC_ALL -u TERM .venv/bin/python -m pytest -q 'tests/test_rf1_session_pins.py::test_session_fresh[1]' 'tests/test_rf1_session_pins.py::test_session_fresh[4]' 'tests/test_rf1_session_pins.py::test_session_fresh[7]' 'tests/test_rf1_session_pins.py::test_session_resume[7]' 'tests/test_rf1_session_pins.py::test_session_reconstruct[7]' tests/test_rf2_instrument.py::test_successor_current_case_is_green --tb=short
```

Observed: 6 passed in 5.73s. These discriminate legacy snapshot, walk and newer
session paths, fresh/resume/reconstruct and the RF2 successor instrument.

`agents._private_environment` explicitly records optional inherited LANG,
LC_ALL and TERM. `git diff --name-only ab879dc` is empty for agents.py,
process.py, exp/, session pin tests, RF2 helper and its successor answers. Thus
the environmental sensitivity predates this PR by unchanged defining/test
homes; this review did not run a separate baseline checkout and does not claim
such a run. Other session versions were not exhaustively replayed here.

Recommended repair: preserve historical environment-sensitive answers and
receipt binding; make the old pin instrument's inherited environment deliberate
and reproducible. An explicit current environment-control test should prove
optional inherited names are still retained when intentionally supplied, and
that they remain bound into invocation evidence. Do not silently normalize away
those evidence fields or blanket-recapture session successors. No production
environment semantic change is warranted by this reproduction.

## Limits

Only the named bounded controls ran. Full local logs were still in progress at
dispatch; this diagnosis does not declare CI green or refute every remaining
failure. Approved no-assurance boundaries and frozen historical authority remain
unchanged. No production edit, provider run or certification performed.

## Authorized test-instrument repair

Under the follow-up delegation, added a module-scoped historical environment
fixture in test_rf1_session_pins.py and exported it to test_rf2_instrument.py.
It removes only LANG, LC_ALL and TERM, restoring their parent state on teardown.
No production loader, inherited-name policy, evidence serialization, historical
golden or RF2 successor answer was changed.

Added an explicit supplied-environment control: deliberately supply those three
names after setup, run the real v1 session, and require all three inherited
records in both attempt invocation ledgers. Deleting each supplied-name record
individually is rejected by the same gate. This preserves evidence sensitivity
rather than normalizing it away. Other outside-environment negative controls are
unchanged.

Red evidence is the initial three-failure probe above. Green full affected-file
runs, with each interpreter's bin explicitly prepended to PATH (the v3 fixture
declares the literal `python` executable):

```
env PATH=/Users/nikolaosvasiloglou/github-repos/gnd-public/.venv/bin:$PATH .venv/bin/python -m pytest -q tests/test_rf1_session_pins.py tests/test_rf2_instrument.py --tb=short
43 passed in 32.61s

env PATH=/private/tmp/gnd-pr19-ci/dev313/bin:$PATH PYTHONPATH=/Users/nikolaosvasiloglou/github-repos/gnd-public/src /private/tmp/gnd-pr19-ci/dev313/bin/python -m pytest -q tests/test_rf1_session_pins.py tests/test_rf2_instrument.py --tb=short
43 passed in 33.53s
```

Ruff on both changed files passes. Initial direct-interpreter runs omitted venv
activation from PATH and returned 41 passed/2 failed on each interpreter, solely
v3 fresh/resume verifier spawn FileNotFoundError. Activating the declared test
interpreter resolves that launcher precondition; no source change was made for
it. Source, goldens, and outside-environment policies remain unmodified.
