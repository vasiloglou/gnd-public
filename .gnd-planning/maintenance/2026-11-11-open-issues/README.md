# The open issues after the 0.3.0 close, 2026-11-11

The owner asked for every open issue except 170 to be addressed. Nine were
open: 169 and 171 to 177, which the release-0.3.0 close filed
(`milestones/release-0.3.0/007-milestone-close.md`), and 104, which the
unattended-model-growth close left to the owner. This note records what
happened to each one. The close records are history and stay as written.

Base: `main` at `793618f1`. Issue 170 (the two full query-policy budgets) is
not touched: no change here adds a direct model read.

## Rulings

Four issues needed a decision. The owner made each one on 2026-11-11, from the
choices put to them in the session:

| Issue | Question | Owner's choice |
|---|---|---|
| 169 | What `gnd export ossie` does with a fact type marked `redact` | "Keep, and say so": no exported byte changes; the command prints a value-free note |
| 172 | How the version-bearing recorded files stop moving at each release | "Normalize per group", in its own pull request |
| 176 | Whether the 0.1.0 negative control in release acceptance is retired | "Retire it" |
| 104 | What to do on GitHub after the remaining gap is fixed | "Post and close": post the follow-up comment and close the issue once the fix is merged |

## Outcome

| Issue | Outcome |
|---|---|
| 169 | Decided and built. `redact` stays what the format reference defines: it withholds population values from reports. An export carries the model's own text and no population, so nothing is removed. `gnd export ossie` prints one note on standard error with the number of fact types that declare `redact`, on the fact type or on a role. The note names no fact type and no value, and the exit stays 0. The disclosure reference, the Ossie explanation page and the format reference say so |
| 171 | The twelve guard files are named in the gate rules of `project.md`, in one command, for every phase or maintenance pass that changes a file outside `.gnd-planning/`. `tests/test_gate_guard_list.py` fails when a named file is missing or the two copies of the page differ |
| 172 | Not in this change. It is done on its own branch and pull request, as ruled |
| 173 | The format reference defines the import report (`gnd-ossie-import-loss/1`, its five members and its three row kinds) and all 29 `ossie-import:<rule>` refusals. A test reads the rule names from the code and compares them with the table |
| 174 | `docs/releasing.md` says that every release through 0.3.0 was published by a token upload |
| 175 | `pyproject.toml` declares `readme = "PYPI.md"`. `PYPI.md` is a short description written for the PyPI page: every link is absolute and it names no version. The wheel metadata and the sdist carry it. It takes effect at the next release |
| 176 | `tools/release_text.py` replaces the shell check and the hand-made patches. `check` runs in the default lane (`tests/test_release_text.py`); `publish` makes the edits that recur at every release and lists what a person still has to rewrite. The 0.1.0 control is retired; acceptance keeps one negative control, against the release before the candidate. `docs/releasing.md` describes the step |
| 177 | `uv run ruff check` exits 0 over the whole repository. The gate rules name it as the lint gate |
| 104 | The reply shape now gives the entry shape of a derived fact type, with its quote, and the guidance test builds one and validates it. Posting the follow-up and closing the issue wait for the merge |

## What to know

- **Lint exclusions (177).** 141 of the 186 findings were in scripts under
  `.gnd-planning/` that milestones retained as evidence. Records bind many of
  them by SHA-256, so they were not edited: `.gnd-planning/**` is excluded from
  lint, for the reason `pyproject.toml` already gives for experiment attempts.
  20 more were in `scripts/components_index.py`, which dev-tools delivers and
  `.devtools-receipt.json` binds; it is excluded, and its lint fix belongs in
  dev-tools. One finding is a file that is a byte copy of another and sorts
  differently in its own directory; it has a per-file exemption. The other 24
  findings, in `tests/` and `tools/`, are fixed.
- **Generated paragraphs (176).** The first paragraph of the release notes and
  the version paragraph of the compatibility page are now written by the tool.
  Their words are unchanged; their line breaks moved once.
- **Replay of the two past publications (176).** `publish` was run on the tree
  before each real post-publication commit. For 0.3.0 (`32a363c5`) it produced
  every recurring edit of that commit, apart from line breaks, and listed
  exactly the lines that commit rewrote by hand. For 0.2.0 (`2c08cdf5`) it
  stopped without writing, because the support page of that time had no row
  for the prepared version; `tests/test_release_version.py` has required that
  row since 0.3.0.
- **Retired control (176).** `test_published_0_1_0_lacks_rule_check` and its
  download are removed. The rule-check probes P1 to P5 stay as regressions.
  Its record is `milestones/rule-check-release/` (phase RR2).
- **104, what is still prose.** The checks table and the cue tables of the
  unattended procedure are still inspected text with no executable check, and
  there is still no schema file for the reply (owner ruling UG-D5 of the
  unattended-model-growth milestone). Both were accepted at that close.

## Gate

- **Full default lane:** 19,051 passed, 0 failed, 2 errors. Six round-robin
  shards over the sorted `tests/test_*.py` on beast-3 (macOS 27.0.1, 18 cores,
  Python 3.13.18, uv 0.13.7, not the 0.10.10 that `release.yml` pins), with
  `uv sync --locked --group dev` and `uv run pytest -q --tb=line -p
  no:cacheprovider`, on a scratch commit of this change's tree. The 2 errors
  are `tests/test_public_optional.py::test_base_wheel_refuses_missing_synth_extra_and_still_checks`
  and `::test_declared_synth_extra_is_seeded_and_loader_valid`, the two known on
  `main` (`milestones/release-0.3.0/evidence/e1/README.md`). `main` at the
  0.3.0 record had 19,016 passed; this change adds 35 tests.
- **Structure and inventory guards**, the command the gate rules now name:
  `679 passed, 2 deselected`, on this session's machine, before the change and
  after it.
- **Lint:** `uv run ruff check` over the whole repository: `All checks passed!`
- **Component index:** `python3 scripts/components_index.py changed --base main
  --strict`: 0 to fix, 0 warnings. The `export.ossie` entry is updated; the
  entries of `cli.export_command` and `infra.disclosure` were reread and stand.
- **Built package** (`distribution` lane, one file):
  `uv run pytest -q -o addopts='' tests/test_public_built_inventory.py`: 17
  passed. `twine check` passes on the wheel and the sdist.

## After the merge

The owner asked for both pull requests to be merged ("merge everything",
2026-11-11). Pull request 186 (issue 172) merged as `b53b208a` and pull
request 185 as `dc7348e4`. The owner then asked for the issues to be closed:
104 is closed with the comment below, and 169 and 171 to 177 are closed with
a note each. Issue 170 stays open.

Checks on `main` at `dc7348e4`, which holds both changes:

- **Full default lane:** 19,062 passed, 0 failed, 2 errors, in six shards on
  beast-3 (macOS 27.0.1, Python 3.13.18, uv 0.13.7). The run was on a trial
  merge whose tree is identical to `dc7348e4`. The 2 errors are the two
  `tests/test_public_optional.py` errors known on `main`. 19,016 before, plus
  35 tests from pull request 185 and 11 from 186.
- **Release acceptance:** `GND_CANDIDATE_DIR=<candidate> uv run pytest -q -o
  addopts='' tests/test_release_acceptance.py`: 16 passed, on this session's
  machine (macOS, Python 3.14.3), with a candidate built from `dc7348e4`:
  wheel sha256 `0a194e8b…8b4f`, sdist `23bc2761…ce65`, the comparison wheel
  identical to the release wheel.
- **An earlier acceptance run** on the branch of pull request 185, before the
  merge, ended 15 passed and 1 failed:
  `test_installed_behavior_families[release]` reached its 1,200-second limit
  while another test job loaded the machine. The `[comparison]` case of the
  same test passed on a byte-identical wheel, and the test passed in the run
  above. It is recorded here as a timeout under load, not as a defect.

This section replaces the first item of "Not covered" below: release
acceptance has now run. The opt-in lanes and the documentation site build are
still not run.

## Issue 104: the comment to post after the merge

The owner ruled "Post and close". The text below replaces the follow-up that
`milestones/unattended-model-growth/notes/ug4-issue-followups.md` drafted and
never posted; that note is history and stays as written.

> Follow-up to the disposition above.
>
> - Item 5, second option, is on main (PR 147). `gnd evolve preview --policy
>   additive --check-population FILE` admits a new constraint, or a change to
>   one whose differing keys all strengthen, weaken or are admitted, on a fact
>   type that already holds facts, when the constraint is `proposed` and
>   `deontic`, `FILE` holds facts for every populated fact type it ranges over
>   and none has sample rows, and the constraint's own verdict over `FILE` is
>   `pass`. The admission holds relative to `FILE`; the constraint stays
>   advisory. `apply` repeats the option and refuses a changed file (exit 11).
>   Rules: the evolution contract, "Population check".
> - A round can declare its own source document inside `evolve` (PR 149), and
>   the unattended-growth procedure says when to use the population check
>   (PR 151).
> - Item 4: the reply shape now gives the entry shape of a derived fact type,
>   with its quote (PR 185). It is the model's fact type shape with a
>   structured rule and no rows. The guidance test builds one, and
>   `gnd validate --document` admits the model.
> - Still inspected prose, as the milestone close accepted: the checks table
>   (item 3) and the cue tables (item 1) have no executable check, and the
>   reply shape has no schema file.
>
> Records: `.gnd-planning/milestones/unattended-model-growth/007-close.md` and
> `.gnd-planning/maintenance/2026-11-11-open-issues/README.md`.

## Not covered

- Release acceptance (`tests/test_release_acceptance.py`) reads the committed
  tree and a built candidate. It was not run on this change before its commit.
- The opt-in lanes (`ossie_oracle`, `pyrel_oracle`, `network`) were not run.
- The documentation site build was not run.
- The PyPI page itself changes only when the next release is published.
