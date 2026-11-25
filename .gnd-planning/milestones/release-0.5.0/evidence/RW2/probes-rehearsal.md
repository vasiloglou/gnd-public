# RW2: rehearsal of the probe functions before the probes pull request

Run on 2026-11-25 on the planning machine, on the working tree of the probes
branch (main `8dcfe0e7` plus the RW2 commits). This is a rehearsal. It does
not use a retained candidate, a built wheel or the source-checkout denial;
the acceptance run on beast-3 is the evidence.

## The five probe functions

[rehearse_probes.py](rehearse_probes.py) imports
`tests/test_release_acceptance.py` and calls each new function with:

- the candidate: the working tree installed editable (`gnd 0.5.0`);
- the published wheel: `published_wheel(..., '0.4.0')`, which downloads the
  0.4.0 wheel from PyPI and checks its SHA-256 against the pin in the test
  file (`gnd 0.4.0`);
- the checkout: a `git archive` of HEAD with the working tree's test file;
- an empty sandbox prefix. CPython 3.13 ran the harness; the 0.4.0
  environment used the same interpreter.

```text
published 0.4.0: gnd 0.4.0
candidate stand-in: gnd 0.5.0
test_installed_rw2_include_roots: passed
test_installed_rw2_pyrel_rules: passed
test_installed_rw2_count_certificates: passed
test_installed_rw2_ossie_relational: passed
test_installed_rw2_seeded_growth: passed
failures: 0
```

Control, the same harness with `--swap`: the 0.4.0 interpreter stands in for
the candidate, and every probe must fail.

```text
test_installed_rw2_include_roots: FAILED (AssertionError): gnd judgments check ... exit 3
test_installed_rw2_pyrel_rules: FAILED (AssertionError): gnd export pyrel ... exit 3
test_installed_rw2_count_certificates: FAILED (AssertionError): the packaged count_fixture is absent
test_installed_rw2_ossie_relational: FAILED (AssertionError): the packaged physical-binding.json is absent
test_installed_rw2_seeded_growth: FAILED (AssertionError): the packaged seeded_growth is absent
failures: 5
```

The second block gives each failure's cause in words; the harness printed
the assertion's first line, which for the last three is a traceback of the
resource copy.

## The five families files

[rehearse_families.py](rehearse_families.py) is the gate program of
`installed_pytest`. It ran each file from the archive checkout with
`python -I`, in a fresh Python 3.11 environment holding the working tree
(editable, with the `synth` extra), `pytest==9.1.1` and `duckdb==1.5.5`, the
packages the acceptance run installs.

| File | Result |
|---|---|
| `test_vg3_unattended_includes.py` | 46 passed, no skip |
| `test_go2_operation_outcomes.py` | 40 passed, no skip |
| `test_lh1_reading_host.py` | 98 passed, no skip |
| `test_lh2_reading_replay.py` | 30 passed, no skip |
| `test_lr3_reference_set.py` | 22 passed, no skip |

Not shown here: that each passes with the package installed from a wheel and
reads of the source checkout denied.

## Not rehearsed

`test_installed_0_3_0_regressions` with its new five-file assertion, the four
RV2 probes without their 0.3.0 controls, and the candidate identity tests.
They need a retained candidate. Collection of the whole file: 33 tests.
