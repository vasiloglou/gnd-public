# Local development CI — failed

Source: `d6f1e8aeacab902914e22b2dab799b65f879fdda` on `claude/rf1-code-refactoring-225109`.
Execution platform: macOS; Python 3.11.15 and 3.13.12, uv 0.10.10.
The Ubuntu matrix leg was not executed. These local observations are not a remote CI success, certification, milestone close, or release sign-off.

Clean detached temporary clones of the exact source commit were used. The original RF worktree was unchanged, apart from its pre-existing untracked `.agents/`. No commit or push was performed. No repository credential environment was loaded.

## Results

Candidate wheel and sdist built once, comparison wheel rebuilt from that sdist. The three nonhidden retained artifacts pass their SHA-256 checks. Both wheels have identical bytes. Installer adoption, doctor, and collection passed on both minors. Collection selected 13,872 of 14,272 tests under the workflow's default exclusions. The selected platform-sensitive gate passed 160 tests (one deselected) on each minor.

| Check | Python 3.11 | Python 3.13 |
|---|---|---|
| Initial full regression, with runner environment caveat below | 69 failed, 13795 passed, 400 deselected, 1 warning, 8 errors in 1816.56s (0:30:16) | 67 failed, 13797 passed, 400 deselected, 1 warning, 8 errors in 1769.91s (0:29:29) |
| Corrected rerun of union of all 77 failed/errored nodes | 56 failed, 13 passed, 8 errors in 38.37s | 54 failed, 15 passed, 8 errors in 38.34s |
| Corrected installed acceptance, both wheels | 2 failed, 8 passed in 884.05s (0:14:44) | 2 failed, 8 passed in 837.08s (0:13:57) |

Each wheel's installed behavior selection completed with **1 failed, 1,802 passed, four deselected and no skips**, on both minors. The sole underlying failure was `tests/test_derivation_rule.py::test_derivation_graph_work_is_bounded_by_counted_operations`. It reads the integer counter through the old `gnd.model` binding while the implementation updates `gnd.model._validation`.

Each wheel's contributor lifecycle selection passed **85 tests** on each minor. Retained candidate identity, its negative controls, optional dependency refusals, and the enforced source-checkout-denial controls passed. Installed behavior failure keeps the combined acceptance result red.

## Runner corrections

The first local driver mistakenly removed `HOME`, `USER`, and `LOGNAME` along with provider variables. Replay evidence records those ordinary environment names, so 13 session/instrument failures were caused by the driver. The corrected driver restored those fields, retained the locale/terminal exclusions used by the existing replay controls, and reran every initial failing or errored node on both minors. All 13 now pass. The full suites were **not** rerun after this environment correction; the corrected table row is a 77-node rerun and must not be described as a fresh full-suite result.

The first local artifact handoff also included two uv-generated hidden `.gitignore` files and hashed five files. The workflow's shell glob and GitHub upload handoff omit them. A corrected download tree contains exactly the same three built artifacts, with a corrected three-file hash list; artifact bytes were not rebuilt or edited. The initial installed setup errors are superseded by the corrected installed runs. Both initial logs remain retained.

## Preliminary triage

These are observed groups, not an approved repair plan or a claim that every failure is a stale test:

- Old module paths, body expectations, mutation anchors and monkeypatch owners no longer follow moved implementations (RF1/RF2/RF3/RF4/RF6 and public extraction/semantic controls).
- Some nonfinite-number and loose DateTime positive tests conflict with RF7 admission restrictions; refusal remains the intended policy and needs controls at the correct boundary.
- The pool loader calls the shared strict JSON reader before mapping its refusal to the documented `PoolValidationError` (six reproduced cases).
- RF9's AST import helper is also called with Markdown evolution resources, causing a reproduced SyntaxError; the Python-source and prose checks need appropriate inputs.
- Producer construction-site fixtures fail their scope-forwarder assertion, producing eight setup errors. Reader byte hashes and closure/negative-control inventories also need current ownership reconciliation.
- Two RF8 body-hash controls fail on Python 3.11 and pass on 3.13; this supported-minor difference persists with the corrected runner.

Historical/frozen authority and retained evidence must remain explicit when selecting repairs; no test or record was changed during this run.

## Confirmed failing files

Counts include failures and setup errors in the corrected Python 3.11 rerun. Python 3.13 differs only in the two RF8 body controls.

| File | Count |
|---|---:|
| `tests/test_artifacts.py` | 1 |
| `tests/test_derivation_rule.py` | 1 |
| `tests/test_measure_offline.py` | 1 |
| `tests/test_poolfile.py` | 6 |
| `tests/test_public_adapter_derivation.py` | 2 |
| `tests/test_public_adapter_literal_controls.py` | 1 |
| `tests/test_public_construction_site_guards.py` | 8 |
| `tests/test_public_correspondence_runtime.py` | 1 |
| `tests/test_public_semantic_composition.py` | 1 |
| `tests/test_public_v72_reader_boundaries.py` | 1 |
| `tests/test_public_v72_semantic_owners.py` | 2 |
| `tests/test_pyrel_export_boundaries.py` | 2 |
| `tests/test_rf1_pin_harness.py` | 1 |
| `tests/test_rf2_helpers.py` | 1 |
| `tests/test_rf2_pre_move_pins.py` | 1 |
| `tests/test_rf2_review_regressions.py` | 1 |
| `tests/test_rf3_core.py` | 1 |
| `tests/test_rf3_moves.py` | 1 |
| `tests/test_rf4_peripheral.py` | 13 |
| `tests/test_rf6_moves.py` | 2 |
| `tests/test_rf6_packages.py` | 3 |
| `tests/test_rf8_structure.py` | 2 |
| `tests/test_v51_phase2_extraction_scope.py` | 2 |
| `tests/test_v6_phase2_adapter.py` | 1 |
| `tests/test_v6_phase2_adapter_mutations.py` | 8 |

## Evidence and exact commands

- [status.json](/private/tmp/gnd-local-ci-20261006-d6f1e8a/status.json)
- [followup-status.json](/private/tmp/gnd-local-ci-20261006-d6f1e8a/followup-status.json)
- [confirmed-failures.json](/private/tmp/gnd-local-ci-20261006-d6f1e8a/confirmed-failures.json)
- [failed-nodes.json](/private/tmp/gnd-local-ci-20261006-d6f1e8a/failed-nodes.json)
- [regression-311.log](/private/tmp/gnd-local-ci-20261006-d6f1e8a/regression-311.log)
- [regression-313.log](/private/tmp/gnd-local-ci-20261006-d6f1e8a/regression-313.log)
- [failed-corrected-311.log](/private/tmp/gnd-local-ci-20261006-d6f1e8a/failed-corrected-311.log)
- [failed-corrected-313.log](/private/tmp/gnd-local-ci-20261006-d6f1e8a/failed-corrected-313.log)
- [installed-corrected-311.log](/private/tmp/gnd-local-ci-20261006-d6f1e8a/installed-corrected-311.log)
- [installed-corrected-313.log](/private/tmp/gnd-local-ci-20261006-d6f1e8a/installed-corrected-313.log)
- [corrected-artifact-hashes.log](/private/tmp/gnd-local-ci-20261006-d6f1e8a/corrected-artifact-hashes.log)

The status JSON files retain each subprocess argument vector, working directory, exit code and duration. The launcher exiting normally is not acceptance: the gate subprocesses returned nonzero. The workflow aggregate therefore fails.

Candidate hashes:

```text
727ead02965ea73417e420314f68199281b0938973982fa4a3ea88f922590de2  comparison/get_nick_done-0.1.0-py3-none-any.whl
727ead02965ea73417e420314f68199281b0938973982fa4a3ea88f922590de2  release/get_nick_done-0.1.0-py3-none-any.whl
28a54173765510de6ddcd367f007b29fce58f2259a34e1a8829bb53119d051c3  release/get_nick_done-0.1.0.tar.gz
```
