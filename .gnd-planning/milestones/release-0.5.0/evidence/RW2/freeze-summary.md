# RW2-C0: the freeze at `85d076ba`

Main `85d076ba384e67b1f992cfd6b9a596ca01b3d4e7` is the merge of the probes
pull request (283) on the owner's word. Main did not move between that merge
and the builds. Checked on 2026-11-25.

| Check | Result |
|---|---|
| The notes cover the freeze commit | [RW1's table](../RW1/notes-reconciliation.md) was checked again with `git diff v0.4.0 85d076ba` over the shipped paths: 144 files, of which four are the version edits the table leaves out and 140 are placed. Since RW1's last check the only shipped file that changed is `docs/release-notes.md` (one sentence, row R16). No row is added |
| 0.5.0 is free on PyPI | read at 16:32 UTC and again after the lane finished, minutes before the first build (the build's files are stamped 16:47 UTC): the index lists 0.1.0, 0.2.0, 0.3.0 and 0.4.0, and `/pypi/get-nick-done/0.5.0/json` answers 404 |
| Six-shard default lane on beast-3 | 22,020 passed, 0 failed, 2 errors, 13 skipped. RW1's lane at `4a73af2e` had 21,998 passed and the same two errors; the 22 more are the controls the probes pull request added to `tests/test_acceptance_controls.py` |
| The tutorials runtime environment | present: `relationalai` 1.30.1 and `duckdb` 1.5.5 import in `tutorials/runtimes/.venv` (Python 3.13.12) |

The lane used [e1-shards.sh](../RW1/e1-shards.sh) in `base` mode: a clean
clone of the commit, uv 0.13.7 and Python 3.13.18, as in RW1. The two errors
are the RC-02 setup errors of `tests/test_public_optional.py`.

## The two oracle lanes, at `85d076ba`

Run on the planning machine in a checkout whose HEAD was the freeze commit
and whose tracked files were unchanged.

| Lane | Command | Result |
|---|---|---|
| `pyrel_oracle` (owner's selection of 2026-11-23) | `uv run pytest -q -m pyrel_oracle tests/test_rp5_literature_rules.py tests/test_rp4_role_value.py tests/test_rp3_number.py tests/test_rp1_external_uniqueness.py tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_derivations.py tests/test_pyrel_rules_plans.py --tb=short -p no:cacheprovider` | exit 0; `345 passed, 156 deselected in 397.32s (0:06:37)` |
| `ossie_oracle` (owner's selection of 2026-11-25) | `GND_OSSIE_ORACLE_ROOT=<scratch> uv run pytest -q -m ossie_oracle tests/test_ossie_external_oracle.py -k 'not consumer' -p no:cacheprovider` | exit 0; `91 passed, 1 deselected in 45.30s` |

The Ossie oracle root was found on the planning machine in another
session's scratch folder: `ossie/` at `ee89dbdc2844d8b7d293ed42c8613928bb99505f`,
`converters/` at `83ddc294c8840f5f497a2bdbec2348a128fc2254`, and environments
`a` and `b`. The lane's own `check_pins` accepted it. Whether it is the root
the Ossie milestone used is not known: that session is archived and was not
asked. The consumer test needs the RelationalAI environments `c` and `d`,
which the root lacks, and was deselected, as in the Ossie milestone's runs.

## Lane output

The script's standard output with uv's package install lines removed.

```text
E1 scratch directory: /private/tmp/gnd-rw1-e1-base.8DBTrQ
uv 0.13.7 (316c827e0 2026-11-03 aarch64-apple-darwin)
ProductName:		macOS
ProductVersion:		27.0.1
BuildVersion:		26A434
85d076ba384e67b1f992cfd6b9a596ca01b3d4e7
warning: `build_system.requires = ["uv-build>=0.10.10,<0.11.0"]` does not contain the current uv version 0.13.7
Python 3.13.18

Shard 0 exit 0
4344 passed, 49 deselected in 579.41s (0:09:39)

Shard 1 exit 0
2849 passed, 238 deselected in 619.25s (0:10:19)

Shard 2 exit 0
4204 passed, 219 deselected, 1 warning in 654.17s (0:10:54)

Shard 3 exit 0
3649 passed, 13 skipped, 104 deselected in 919.37s (0:15:19)

Shard 4 exit 0
3778 passed, 256 deselected in 500.77s (0:08:20)

Shard 5 exit 1
ERROR tests/test_public_optional.py::test_base_wheel_refuses_missing_synth_extra_and_still_checks
ERROR tests/test_public_optional.py::test_declared_synth_extra_is_seeded_and_loader_valid
3196 passed, 184 deselected, 2 errors in 651.16s (0:10:51)
```
