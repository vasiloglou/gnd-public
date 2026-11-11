# E1: what the 0.3.0 version bump moves (run 2026-11-11 UTC)

Experiment E1 of [the RN1 spec](../../notes/phase-RN1-spec.md), run as the spec
recorded it before running. The files here are the retained outputs;
home-directory paths in test ids were replaced by `<scratch>` (edited,
declared here).

- **Base ref.** main `2490dd77`, untouched (`e1-base`).
- **Bumped ref.** `2490dd77` plus exactly M1 to M3: `pyproject.toml`, the three
  manifests and a one-line edit of the `get-nick-done` entry of `uv.lock`
  (`e1-bumped`, scratch commit `d5e4bfa7`, not in this repository).
  `uv lock --check` exits 0 on it.
- **Instrument.** A copy of the predecessor's `close-shards.sh` with the bundle
  path changed: six round-robin shards over the sorted `tests/test_*.py`,
  `uv sync --locked --group dev`, `uv run pytest -q --tb=line -p
  no:cacheprovider`, on beast-3 (18 cores, macOS 27.0.1), the two runs one
  after the other, finished 2026-11-11T04:05:08Z. Default lane only. uv on
  beast-3 is 0.13.7, not the 0.10.10 that `release.yml` pins.
- **Result.** Base: 18,971 passed, 26 failed, 2 errors
  ([failed-base.txt](failed-base.txt)). Bumped: 18,936 passed, 61 failed, the
  same 2 errors ([failed-bumped.txt](failed-bumped.txt)). The 35 ids that fail
  only at the bump are in [new-at-bump.txt](new-at-bump.txt); no base failure
  disappears. Per-shard lines: [summary.txt](summary.txt).
- **The 35.** Four are `tests/test_release_version.py` cases that fail because
  the notes have no 0.3.0 heading yet (M6 supplies it). The other 31 are the
  same test ids as the 31 method-(b) failures of the 0.2.0 bump (predecessor
  RR1 spec §13.1); the two `test_public_measurement_publication.py` ids differ
  only in the scratch path inside the parameter. The 16 `test_extract` ids
  that failed at the 0.2.0 bump do not fail now: the placeholder comparison
  added then holds.
- **Liveness.** The instrument shows a nonzero result at the bump (35) and the
  base list is its zero end.
- **Inventory.** [inventory-0.2.0-at-2490dd77.txt](inventory-0.2.0-at-2490dd77.txt):
  line counts per tracked text file outside planning and `uv.lock` that names
  `0.2.0` (20 files). [gz-archives-naming-0.2.0.txt](gz-archives-naming-0.2.0.txt):
  the 3 tracked gzip fixtures whose first decompression layer names `0.2.0`;
  nested members were not opened, and the 0.2.0 bump re-recorded 7 containers.
- **Not covered (stated first, as recorded).** The opt-in lanes (RN-D11), and
  anything that needs a network, a paid tool or a reserved split. One run per
  tree on one machine.

## The base lane is red by 26, not by 2

The plan (N20, N26) knew of two red tests on main. The base run shows 26
failures and the 2 known `tests/test_public_optional.py` errors. Twenty-four
were reproduced on this session's machine at `2490dd77`; the other two are
N20 and N26.

Attribution, by running the 12 affected test files at two earlier commits on
this session's machine:

| Commit | Result |
|---|---|
| `483b49ea` (the 0.2.0 close merge, PR 144) | 706 passed, 0 failed |
| `54a47612` (PR 158, model-composition close; the commit before the Ossie plan) | 6 failed: N20 and five `tests/test_rf5_commands.py::test_relocated_algorithm_and_qualification_are_unchanged` cases (`_cmd_evolve_apply`, `_cmd_evolve_preview`, `_cmd_validate`, `_evolve_emit_claim`, `_evolve_error_exit`) |
| `2490dd77` (main) | 26 failed: those 6 and 20 more, first present after PR 160 and PR 161 |

The 20 by test, with the first assertion line each printed:

| Test file (failures) | What the assertion says |
|---|---|
| `test_conformance_payload.py` (1) | `gnd/ossie-loss-report.schema.json` is a vendored runtime schema with no packaging guard |
| `test_development_scaffold.py` (1) | N26 |
| `test_disclosure_mode.py` (2) | the leaf table counts 52, pinned 50 |
| `test_packaged_skills.py` (1) | the skill routing graph is not the pinned inventory |
| `test_rf5_commands.py` (2) | 61 parser paths, pinned 59; the entrypoint import rule lists new imports |
| `test_rf5_review_regressions.py` (1) | 7 where 1 is pinned |
| `test_rf6_query_policy.py` (5) | direct model reads in `src/gnd/export/ossie.py` and `src/gnd/ossie_import.py` are not in the exact query-policy list; 315 against 309 |
| `test_rf7_structure.py` (2), `test_rf8_structure.py` (1) | `src/gnd/export/ossie.py` has no layer home; lazy imports from `gnd.commands` to `gnd.ossie_import` and `gnd.safefs` are not allowed by the map |
| `test_rf9_repairs.py` (2) | the same query-policy list |
| `test_rof4_accept_identities.py` (2) | `export/ossie` calls the model identity at a site not in the exact list |

These are the repository's structure and inventory guards (AGENTS.md,
"Refactoring dependency homes" and "Model queries and family dispatch"). This
experiment shows that they fail and since when. It does not show which are
stale pins and which are real violations of the rule each one guards.
