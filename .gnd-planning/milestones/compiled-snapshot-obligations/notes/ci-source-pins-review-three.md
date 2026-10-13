# Bounded CI source-pin diagnosis

2026-10-13. Static review at PR #19 candidate `f446dc1`. No production or test
edits and no broad test execution. Seven reported RF4/RF5/RF6 failures are
historical body-equality claims invalidated by the approved opt-in change, not
evidence that the original refactor changed those historical bytes.

## Repair contract

Create a separately named milestone-owned successor artifact. Do not rewrite
RF4/RF5/RF6 predecessor captures, RF7 definition-successors or RF9-ci-repair
body-successors. Extend current test support to resolve exact historical
kind/old-module/name keys from both old and new ledgers, reject duplicate matches,
and bind original-before plus current-after hashes. Require defining-home and
nonempty reason fields. Unknown bodies must continue to use the original equality
predicate. Preserve facade identity, metadata, pickling and source-scan checks.

RF4 `_run_check_raw` has an additional issue: its current local import inventory
adds `compose`. `test_moved_algorithm_preserves_base_body` asserts import equality
before querying successors. For the exact new successor, assert both full
before/after inventories, rather than bypassing the import control. The old
inventory is `[AnchorError, AnchorSidecar, MAX_DOCUMENT_BYTES, bind_anchors,
bind_population, read_anchor_sidecar, read_regular_path, resolve_context,
validate_anchor_sidecar]`; the new sorted inventory inserts `compose` after
`bind_population`. `_run_check` retains `[build_admission, wire_verdicts]`.
Historical successors and all unnamed rows retain the original import predicate.

RF5 hashes below use `portable_dump`, with current `ReaderSeam` applied before
dumping the after node. This preserves RF7's exact decoder substitution and avoids
hash differences from CPython 3.11/3.13 empty-field serialization. Do not hash
native `ast.dump` on one interpreter and expect another interpreter to match.

RF6b uses exact decorated definition source slices, as its current test does.
Merge frozen RF7 rows with the new ledger only in test lookup; assert uniqueness
for `(module, name)` instead of `next(...)` silently selecting the first row.

## Exact measured hashes

RF4 before nodes come from approval base
`387aada2f5fad7289481bbc2e15c8dba629d8ce0:src/gnd/api.py`.
RF4 algorithm hashes strip only imports and use `portable_dump`.

| Kind / identity / defining home | Before algorithm SHA-256 | Current algorithm SHA-256 |
|---|---|---|
| RF4 / gnd.api._run_check_raw / gnd.checking_service | 8b45191d46cc36c68b2c9fc2146483943194be26e6e395f0874f7dd150cd9ed0 | 49b7fd2a06e94bb8348dd2ac3d64119aab1ea99a1518e706bef2fb64e0082e13 |
| RF4 / gnd.api._run_check / gnd.checking_service | 1fb1b13344d99516894cadbf3f09c7749439bfa7c19364e0391d1dd790b7f0d5 | b74bf1b6005c34ffee01cd2fe2a7d513d7cc6f0d39a9be66677d32311c868e8e |
| RF5 / gnd.cli._cmd_check / gnd.commands.checking | c7cc18aaaeae035be2dcf89962f6d8eee795d846461f706b71c580c14a1464d1 | 0055d26439ce60b60b7849af2565799f28b2ea226766b688d4fd585bf5222954 |
| RF5 / gnd.cli._cmd_check_batch / gnd.commands.checking | 9524f7ccdca5ef73b656ad7aef21f7bb09dc07fc922345e538ad88bd84e4c292 | 53a7b94ef988803347205e2c96a75659a40fb5779584ea942dfeb013d79df319 |
| RF5 / gnd.cli._print_trace / gnd.output | 283ff90debd22afeca14c52a212b762b55016da7cc072e059a06f580fbc1c8da | 679b87cf35897b8d04dec6dbcd21afad21af20b9b82e85ed2efe2b7f320d2b3a |

RF5 predecessors are exact definitions in the unchanged
`code-refactoring/evidence/RF5/predecessor-cli.py.txt`.

| Kind / identity / defining home | Original raw SHA-256 | Current raw SHA-256 |
|---|---|---|
| RF6b / gnd.model.compile_operation / gnd.model._operations | e3b8c9a958b3397ca9e5409e24b7ce9287e88b9933437d92c301e92fa08b853f | cc838958c39a8449b036e9f68be34c2b55b3daeb9730ace5b0998a47d7fe87d6 |
| RF6b / gnd.checker.check / gnd.checker._core | e2d73e23de3da792f005b89a03e385f041715aeead37906475badf24023d6630 | 6a8da7606f0924c83fdac4e1563f95ee381b91361f8164329f32a5e0681b1978 |

Reasons should distinguish API/service forwarding and admission refusal (RF4),
CLI single/batch option forwarding (RF5 commands), explicit trace activation
wording (RF5 trace), compiler provenance docstring clarification without guard
broadening (RF6 compile_operation), and default-preserving checker opt-in
composition (RF6 check).

## Required focused validation

Run the seven affected parameter nodes on both Python 3.11 and 3.13 plus the
successor-lookup integrity controls. Add a discriminating countercheck showing
an unrecorded body edit and an unrecorded import edit still fail. Do not treat
hash rebinding as semantic proof: retain issue regression controls and report
this as explicit current-source maintenance, without recertifying frozen RF
evidence. This review does not establish passing tests or resolve unrelated CI
failures.

## Authorized implementation and focused verification

The root explicitly delegated these test/evidence repairs after the diagnosis.
Created `evidence/CI/source-successors.json` with eight exact rows and extended
only the four owned RF4/RF5/RF6 test/support files. No production write or commit.
Historical RF4/RF5/RF6/RF7/RF9 evidence remains untouched.

The eighth row follows the root's separately reproduced assurance-scope repair:
`gnd.assurance._phase3_target`, defining home `gnd.assurance.core`. Its original
algorithm hash is
`2718e6ed73a01e0716f25b15511a619f3ebdc721100423dde1df112d21ad8afd`;
current hash is
`ceee6e9f5060af3720af21829a1b3b8277815fb9a329097717536b6addd0db2e`.
It excludes new compiled-subset scopes from the historical frozen proof
denominator. Its import inventories are both empty.

Current successor lookup rejects duplicate keys and unchained predecessors. For
a chained successor it validates the current-before against the frozen-after
and returns the original-before/current-after pair. Mutation controls show
unrecorded AST and import edits remain distinguishable, unknown identities do
not acquire an override, duplicate current/frozen rows fail, and a broken chain
fails. RF5 keeps the exact ReaderSeam and portable dump; RF6 keeps exact raw-body,
identity and pickling assertions.

Focused command, run using each existing isolated environment's interpreter:

```sh
python -m pytest -q tests/test_rf4_peripheral.py tests/test_rf5_commands.py tests/test_rf6_packages.py --tb=short
```

Python 3.11: `1421 passed in 23.52s`, exit 0.
Python 3.13: `1421 passed in 19.04s`, exit 0.
Ruff on the four changed test/support files: `All checks passed!`
Their `git diff --check` exited 0.
Streams are temporary `/private/tmp/gnd-ci-sourcepins-311.log` and
`/private/tmp/gnd-ci-sourcepins-313.log`; they are not claimed as committed
historical evidence. Initial runs each had one `_phase3_target` failure after
the root's concurrent production repair; the eighth successor discharges it.

The successor artifact SHA-256 is
`961dc2211eb9700ac25147ff38d855310cf8741d081ad1a2b2fdff219ca70eaf`.
These focused results establish the named current-source gate maintenance,
not a new certificate, full replay or external application acceptance.
