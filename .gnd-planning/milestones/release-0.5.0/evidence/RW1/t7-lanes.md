# RW1 T7: the full default lane on the RW1 tree

Three runs on beast-3 on 2026-11-25 with [e1-shards.sh](e1-shards.sh) in
`base` mode, which tests a clean clone of the named commit and changes
nothing in it. Same machine, uv 0.13.7 and Python 3.13.18 as E1
([e1-summary.md](e1-summary.md)).

| Commit | What it is | Passed | Failed | Errors | Skipped |
|---|---|---|---|---|---|
| `cc8cdb65` | the bump and notes as first committed | 21,992 | 3 | 2 | 13 |
| `1d8536de` | with review finding F1 repaired and the two notes readers changed | 21,994 | 1 | 2 | 13 |
| `4a73af2e` | with the round-2 repair and main `3998d371` merged | 21,998 | 0 | 2 | 13 |

- **`cc8cdb65`.** Two failures the E1 base run lacks, both in
  `tests/test_ossie_docs.py`:
  `test_r1_f6_the_release_note_states_the_bound_as_the_cli_takes_it` and
  `test_the_release_note_states_the_exits_by_their_constants`. They read the
  notes section by the heading `## Unreleased: Ossie relational files`,
  which the rewrite removed. E1 could not show them: it changes the version
  fields and not the notes. The third failure is the base's.
- **`1d8536de`.** The same ids as the E1 base run at `4968631e`: one
  failure, `tests/test_plan_app_docs.py::test_plain_short_prose_without_exit_codes[share-an-ossie-ontology.md]`,
  and the two RC-02 setup errors.
- **`4a73af2e`.** No failure. Main `3998d371` (pull request 275) repaired the
  base failure and added tests of its own (21,998 passed against 21,994). The two errors are RC-02's.

The commit that carries this file and the phase record differs from
`4a73af2e` in files under `.gnd-planning/` only.

The output below is each run's standard output with uv's package install
lines removed. Nothing else was edited.

```text
===== cc8cdb65
E1 scratch directory: /private/tmp/gnd-rw1-e1-base.6HTzpZ
uv 0.13.7 (316c827e0 2026-11-03 aarch64-apple-darwin)
ProductName:		macOS
ProductVersion:		27.0.1
BuildVersion:		26A434
cc8cdb6594cc75a2ee42fe7db89281bc344b3abc
warning: `build_system.requires = ["uv-build>=0.10.10,<0.11.0"]` does not contain the current uv version 0.13.7
Python 3.13.18

Shard 0 exit 1
FAILED tests/test_ossie_docs.py::test_r1_f6_the_release_note_states_the_bound_as_the_cli_takes_it
FAILED tests/test_ossie_docs.py::test_the_release_note_states_the_exits_by_their_constants
2 failed, 4319 passed, 49 deselected in 753.42s (0:12:33)

Shard 1 exit 0
2849 passed, 238 deselected in 769.19s (0:12:49)

Shard 2 exit 0
4204 passed, 219 deselected, 1 warning in 828.61s (0:13:48)

Shard 3 exit 1
FAILED tests/test_plan_app_docs.py::test_plain_short_prose_without_exit_codes[share-an-ossie-ontology.md]
1 failed, 3648 passed, 13 skipped, 104 deselected in 1103.63s (0:18:23)

Shard 4 exit 0
3778 passed, 256 deselected in 645.01s (0:10:45)

Shard 5 exit 1
ERROR tests/test_public_optional.py::test_base_wheel_refuses_missing_synth_extra_and_still_checks
ERROR tests/test_public_optional.py::test_declared_synth_extra_is_seeded_and_loader_valid
3194 passed, 174 deselected, 2 errors in 820.87s (0:13:40)

===== 1d8536de
E1 scratch directory: /private/tmp/gnd-rw1-e1-base.KpnIxL
uv 0.13.7 (316c827e0 2026-11-03 aarch64-apple-darwin)
ProductName:		macOS
ProductVersion:		27.0.1
BuildVersion:		26A434
1d8536deb8318d1de17174055551a95d0331ec70
warning: `build_system.requires = ["uv-build>=0.10.10,<0.11.0"]` does not contain the current uv version 0.13.7
Python 3.13.18

Shard 0 exit 0
4321 passed, 49 deselected in 638.06s (0:10:38)

Shard 1 exit 0
2849 passed, 238 deselected in 692.35s (0:11:32)

Shard 2 exit 0
4204 passed, 219 deselected, 1 warning in 740.93s (0:12:20)

Shard 3 exit 1
FAILED tests/test_plan_app_docs.py::test_plain_short_prose_without_exit_codes[share-an-ossie-ontology.md]
1 failed, 3648 passed, 13 skipped, 104 deselected in 1058.93s (0:17:38)

Shard 4 exit 0
3778 passed, 256 deselected in 533.98s (0:08:53)

Shard 5 exit 1
ERROR tests/test_public_optional.py::test_base_wheel_refuses_missing_synth_extra_and_still_checks
ERROR tests/test_public_optional.py::test_declared_synth_extra_is_seeded_and_loader_valid
3194 passed, 174 deselected, 2 errors in 740.94s (0:12:20)

===== 4a73af2e
E1 scratch directory: /private/tmp/gnd-rw1-e1-base.IF9lsw
uv 0.13.7 (316c827e0 2026-11-03 aarch64-apple-darwin)
ProductName:		macOS
ProductVersion:		27.0.1
BuildVersion:		26A434
4a73af2eafe18bc7556dc8607b37dfe5a1fe65e3
warning: `build_system.requires = ["uv-build>=0.10.10,<0.11.0"]` does not contain the current uv version 0.13.7
Python 3.13.18

Shard 0 exit 0
4322 passed, 49 deselected in 681.34s (0:11:21)

Shard 1 exit 0
2849 passed, 238 deselected in 693.03s (0:11:33)

Shard 2 exit 0
4204 passed, 219 deselected, 1 warning in 743.70s (0:12:23)

Shard 3 exit 0
3649 passed, 13 skipped, 104 deselected in 1008.86s (0:16:48)

Shard 4 exit 0
3778 passed, 256 deselected in 564.60s (0:09:24)

Shard 5 exit 1
ERROR tests/test_public_optional.py::test_base_wheel_refuses_missing_synth_extra_and_still_checks
ERROR tests/test_public_optional.py::test_declared_synth_extra_is_seeded_and_loader_valid
3196 passed, 174 deselected, 2 errors in 740.02s (0:12:20)
```
