# Inline restatements of the skill inventory, 2026-11-23

A maintenance pass, not a milestone. It takes OQ2 of
[pins-and-review-check](../../milestones/pins-and-review-check/004-close.md),
which the owner asked to fix on 2026-11-23 ("fix OQ2 too").

PF1 gave the packaged-skill inventory one home, `tests/test_packaged_skills.py`,
and a guard against a test binding it again. A guard on names cannot see a
bare number. Four places still restated the inventory as one:

| Site | Before | After |
|---|---|---|
| `tests/test_development_scaffold.py`, `check_twins` | `assert len(names) == 18` | `assert names == EXPECTED_SKILL_NAMES`: the same names, not only as many |
| `tests/test_marketplace_plugins.py`, `check_bundle` | `assert len(expected) == 18` | `assert expected == EXPECTED_SKILL_NAMES` |
| `tests/test_release_acceptance.py` (distribution lane) | `... == 18` SKILL.md files in a retained wheel | `... == len(EXPECTED_SKILL_NAMES)` |
| `tests/fixtures/rf5-handlers/answers.json`, case `install` | the recorded output `placed 71 file(s)` | `placed <skill-file-count> file(s)`; `tests/test_rf5_handler_pins.py` fills the token from `EXPECTED_SKILL_FILE_COUNT` before comparing. The observed output is compared as it is |

Left as they are, by reading: the `== 18` decision pin inside the home
(`tests/test_packaged_skills.py:93`); `tests/test_public_distribution_runtime.py`,
which pins a released wheel (plan D5); `tests/test_public_tests_mode_corpus.py:846`,
whose `71` counts corpus rows, not skill files. The historical digest of
`answers.json` in `code-refactoring/evidence/RF5/handler-corpus-frozen.json`
describes older bytes, as it already did after PR 254; no test reads it.

## Checks, 2026-11-23

- `uv run pytest -q -p no:cacheprovider tests/test_rf5_handler_pins.py tests/test_rf5_commands.py tests/test_marketplace_plugins.py tests/test_development_scaffold.py tests/test_inventory_pin_home.py --tb=short`: 448 passed, 1 deselected.
- The token is live: with the count set to 72 the filled `install` answer differs from the 71-file output.
- The guard command of `project.md`: 866 passed, 2 deselected. `uv run ruff check`: all checks passed. `python3 scripts/components_index.py changed --base origin/main --strict`: 0 to fix.
- `tests/test_release_acceptance.py` runs only from a checkout of a candidate's source commit (`GND_CANDIDATE_DIR`), so it was not run here. Its changed assertion was checked directly on the retained 0.4.0 wheel: 18 SKILL.md files, `len(EXPECTED_SKILL_NAMES)`.

## Not established

- No reviewer has read this change.
- A future literal elsewhere (a test, a fixture, a document) is still invisible to the name guard.
