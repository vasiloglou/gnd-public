# Carried checker, export and codegen defects, 2026-10-27

The induced-knowledge close (`milestones/induced-knowledge/012-milestone-close.md`,
"Open questions carried forward") sent five pre-existing defects to GND issues.
The owner asked for all of them to be fixed. [spec.md](spec.md) reproduces each one on
`main` at `077f46e` and states the rulings. The owner approved spec r1 with CD-1 to CD-6
as recommended on 2026-10-27; the spec's gate record binds the r1 bytes. Its
"Implementation findings" section records what changed after approval and why.

## Outcome

| # | Carried as | On `main` | After |
|---|---|---|---|
| 1 | IK4-Q4 | `gnd check` exits 70, "witness ... has no admissible origin", whenever one number is spelled `4` and `4.0`. Affects `mandatory`, `mandatory-disjunctive`, single-role `exclusive-or` and object-scope `value`. No derivation is needed | The verdict exit (0 or 1). A role-less witness takes its spelling from origins of the rule's subject object-type universe, first unused in population order |
| 2 | IK3-Q1 | An opaque roster cell is reported as `role-unresolved` ("role ... does not exist"); the two sibling families report `subject-type-ambiguous` | `unchecked`, reason `opaque-value`, scope `applicability:opaque:n-a:opaque-value`, with the frequency rule's message |
| 3 | FIFO hang | `gnd check` hangs on a FIFO population, `--pre`, `--steps` or `--post` | Exit 3, `population file '<path>' is not a regular file` / `steps file <path> is not a regular file` (a redacted walk report shows the type only) |
| 4 | `export pyrel --rules` | Exit 70 `export failed: 'id'` on `pyrel-oracle/basics`, both targets | Exit 0; id-less model-level rules are `constraints_<i>`; a taken default is exit 3 |
| 5 | IK1-Q4 | A reading, `summary` or model file name forges a role line in the runtime `__doc__` | A docstring holding any escape other than `\\` and `\'` is emitted raw, so runtime text keeps the source's lines |

## Behaviour changes to know

- **Non-regular inputs.** A population that is not a regular file is refused
  with exit 3 by every command that loads it through `load_population`. That
  covers a FIFO, a directory, and a pipe such as `<(cat ...)` or `/dev/stdin`
  (review R5). A model path was already refused this way. The message for a
  directory changes from `[Errno 21] Is a directory` to "not a regular file";
  the exit stays 3.
- **CD-4 narrowed (review R2), for the owner's confirmation.** CD-4 read "raw
  when the docstring has a backslash". The neutralizer writes every `'` as `\'`,
  so that rule turned any apostrophe into a raw literal and showed `\'` at
  runtime. The implemented rule leaves `\\` and `\'` in a plain literal, where
  they decode to the one character they escape. With that rule, every model
  without other escapes keeps its bytes. That includes `examples/plan_apps/access`
  ("Employee's"), checked against `077f46e`: the same `tools.py` apart from the
  banner path line.

## Commits

- `344f35a` spec r1; `5243bb5` owner approval.
- `49bd0d2` regressions committed red: 22 failed and 1 passed (the directory
  control), [evidence/red.txt](evidence/red.txt).
- The fix commit, and this record.

## RF controls

- **RF6 exact query policy:** unchanged. The fix routes model reads through the
  family cursors, `universe.role_object_type` and `ModelIndex`, so no query
  exception is added.
- **RF6 dynamic-syntax census:** 30 occurrences in 28 rows are added, all
  annotations and positional index reads, and none is removed. They are
  registered as [dynamic-query-successor.json](dynamic-query-successor.json)
  (SHA-256 `0aad03b251e79aa668bbd0f6bde49af7cb22176cdc70623aa7ab710731f9e09a`).
  It chains after `induced-knowledge/evidence/evolve-loading/dynamic-query-successor.json`
  and is listed in `tests/support/pyrel_application_successors.py`. If another
  branch appends a successor first, this link must be re-chained when it merges.
- **RF5:** no pinned command handler changed. No RF1 mutation snippet,
  golden or IK1 T7 baseline moved.

## Gate

- **Full default suite:** 84 failed, 15,805 passed, 3 skipped, 786 deselected.
  - 83 of the failures also fail on unmodified `077f46e`, with the same
    interpreter, in a scratch checkout:
    - `test_public_tests_mode_corpus` (77);
    - `test_rf1_session_pins` `[3]` (2);
    - `test_public_book_runtime` (2);
    - `test_doctor_uninstall` (1);
    - `test_incremental_performance` (1).
  - The 84th was this change's own stem-escape regression after R2. It was
    corrected, and then `test_carried_defects.py`, `test_rf6_query_policy.py`
    and `test_rf9_repairs.py` passed together (90).
  - Every `tests/test_rf*.py` passes except the two pre-existing session pins.
- **Opt-in `pyrel_oracle` lane** (`test_pyrel_rules*.py`): 251 passed. It ran
  against the main checkout's `tutorials/runtimes/.venv` through a temporary,
  uncommitted link, now removed. It includes the new `basics` pass and fail cases.
- **Lint:** `ruff check` on every touched Python file passes.

## Review

One independent reviewer agent read the diff, the spec and the regressions,
and wrote only to scratch. It confirmed the regressions are red on base and
found:

| # | Severity | Finding | Disposition |
|---|---|---|---|
| R1 | blocking | Scoped spelling choice was quadratic (32,000 occurrences took 33.75 s) | Fixed with a per-bucket cursor (0.41 s); a regression bounds 40,000 occurrences |
| R2 | should-fix | Every apostrophe triggered a raw docstring, so runtime text showed `\'` | Fixed by narrowing the raw trigger (see above); regression added |
| R3 | should-fix | Spec's oracle-lane case for `basics` missing | Added; the lane helper maps `constraints_<i>` and compares frequency as one list |
| R4 | minor | Cross-type tests passed without the type filter | A foreign-spelling-first case added for all four families |
| R5 | minor | Piped population input now refused | Recorded above (CD-5 as ruled) |
| R6 | minor, not reproduced | Spellings may swap between an `instances:` occurrence and a fact occurrence of one value | Accepted residual: the multiset of spellings is right; `main` exited 70 |

The reviewer also confirmed:
- **Item 1** changes no other family's verdicts or witnesses.
- **Item 4**, across 664 model × target renders, changes no previously working
  program and newly renders 32 that failed.
- **Item 3** keeps exits for missing, directory and over-cap inputs.
- **Item 2** does not misfire on an opaque cell outside the rule.

## Not covered

- `O_NONBLOCK` behaviour was exercised on macOS only.
- Derived and semiderived origins in an ambiguous spelling bucket are covered
  only by the IK4 floats regression.
- The PyRel `lqp` program was rendered and parsed, not run on an engine.
