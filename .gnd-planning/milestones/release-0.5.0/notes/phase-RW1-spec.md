# Phase RW1: candidate content (version, lock, manifests, notes)

## 1. Status

**Draft r3, blocked; no ruling.** The [plan](release-0.5.0-plan.md) r2 is
approved by delegated ruling ([plan gate](../001-plan-gate.md)); r3 of the
plan adds §12. The §11 RW-D2 ruling held this phase until
literature-host-interfaces and reviewed-vocabulary-growth were merged, and
both are on main at `c227c004`. The owner's ruling in plan §12 (o) now holds
it until pins-and-review-check is merged too. When it is, this spec is
revised against main as it then is (the inventory, the notes outline, the
headline, and E1's expected base result, which plan §12 shows to be wrong)
and gets its two rulings: the first approves the E1 measurement, the second
binds the handling E1 shows to be needed.

## 2. Provenance

This spec derives from the plan r1 (unreviewed) and from the predecessor
phase [RV1](../../release-0.4.0/005-phase-RV1.md) and
[its spec](../../release-0.4.0/notes/phase-RV1-spec.md), whose method it
repeats. No review has run over these bytes. The baseline is main `0bfded71`.
r2 applies the plan's §11 at three sites, tagged `(p1)` for the panel round
and `(o)` for the owner's ruling: the status line, the E1 base and the
reconciliation scope. r3 changes the status line only; every other section
still describes main at `0bfded71`.

One thing differs from RV1 at the start: RV1 expected the bump to move
nothing and measured 37 moved results. This spec expects movement and names
where (§6, E1).

## 3. Obligations (step 0 harvest)

| Row | Obligation | Source | Discharged in |
|---|---|---|---|
| RW1-C1 | version 0.5.0 in `pyproject.toml`, the lock entry and three manifests | plan §4 | M1 to M3, T1 |
| RW1-C2 | E1 and the grep inventory are appended here before code, each entry classified, under a second ruling | plan §4, W8 | E1, §12 (to be appended), M5 |
| RW1-C3 | one 0.5.0 notes section; every user-visible change of W7 is noted or reasoned | plan §2, W6, W7 | M4, M6, T4, the reconciliation table |
| RW1-C4 | compatibility, support and plugin pages say 0.5.0 is prepared and not published; the pins stay at 0.4.0 | plan §4 | M7 to M9, T2, T3 |
| RW1-C5 | `tests/test_release_version.py` and `tools/release_text.py check` exit 0 | plan §4 | T1 to T5 |
| RW1-C6 | the full default lane has no failure the E1 base run lacks | plan §4, W10 | T7 |
| RW1-C7 | the lint findings equal the base's; the ten added since 0.4.0 are located | plan §4, W11, C3 | T8 |
| structure guards | a change outside `.gnd-planning/` runs them | `project.md` | T6 |
| W15 | the notes say no RelationalAI engine ran the programs | plan §1 | M6, the PyRel block |
| R1 | the bump moves results or recorded bytes | plan §6 | E1, D2 |
| R3 | main says 0.5.0 before PyPI | plan §6 | M6 to M9, T2 |
| RR1 finding | `uv lock` regeneration once dropped an unrelated wheel line | rule-check-release RR1 record, by way of the RV1 spec | M3 edits the one line by hand; `uv lock --check` |

## 4. The standing rules, bound to this phase

- Plan rule 1: no command here builds or uploads.
- Plan rule 2: M1 is the only place the version is typed as the version. T1
  checks M2 and M3 against it.
- Plan rule 3: the pin files keep `==0.4.0` (T2).
- Plan rule 4: no committed recorded byte moves. If E1 shows one must, it is
  listed with its old and new digest before code (D2).
- Plan rule 5: not applicable, because nothing is built here.
- Plan rule 6 and `project.md` rule 6: E1 runs before M5.
- Plan rule 7: `release.yml`, `tests/test_release_preparation.py` and the
  dependencies are not edited.
- Plan rule 8: bound to §10's total.
- `project.md` rule 5: each notes block summarizes its milestone's reference
  page and links to it, and adds no rule of its own. The list of refusal
  messages stays in `docs/runtimes/pyrel.md`.
- `project.md` rules 1 to 4: this phase adds no consumer of untrusted input,
  no input-proportional work, no validation boundary and no policy walk.

## 5. Goal

On the RW1 tree, all of the following hold:

- `uv run pytest -q tests/test_release_version.py` exits 0 with the declared
  version 0.5.0;
- `uv lock --check` exits 0;
- `uv run python tools/release_text.py check` exits 0;
- the focused gate of §8 exits 0;
- the six-shard default lane lists no failing test id that the E1 base run
  lacks;
- `uv run ruff check --output-format=json` lists the same findings as on the
  base.

## 6. Design

### E1: the bump's effect (recorded before it runs)

- **What it measures:** which default-lane test ids change result when only
  the version changes, and which generated outputs change bytes. Two runs on
  beast-3, six round-robin shards over C-sorted `tests/test_*.py`, default
  marker filter:
  1. the base: the commit the bump is applied to, named in the first ruling
     (p1). It is not `0bfded71`: main will have the two milestones of plan
     RW-D2 by then (o);
  2. a scratch tree of the same commit with 0.5.0 in `pyproject.toml`, the
     lock line and the three manifests, and nothing else changed.
- **Expected:** the base run has no failure and the two known
  `test_public_optional` setup errors (RC-02). On the bumped tree, the
  release-version checks fail until M4 and M6 to M9 exist. The four consumers
  RV1 repaired (`tests/test_li1_assurance_report.py`,
  `tests/test_li1_literature_corpus.py`,
  `tests/test_expense_receipts_example.py`, `tests/test_release_text.py`)
  are expected to stay green, because RV1 made them compare through the
  recorded version. Tests added since 0.4.0 that print the version are the
  unknown: the count example, the flatten record and the exported PyRel
  programs. Each id that moves is listed.
- **What it cannot measure:** opt-in lanes (D3), and anything an installed
  wheel shows (RW2).
- **Liveness:** the bumped tree with no notes change must turn at least the
  `test_release_version.py` heading check red. If it does not, the
  instrument is not reading the bump. A runner or setup failure supplies no
  E1 result.

The scripts are RV1's [e1-shards.sh](../../release-0.4.0/evidence/RV1/e1-shards.sh)
and `verify-shards.sh`, copied to this milestone's `evidence/RW1/` with the
base commit and the version moved on. The copy is diffed against the
original in the record.

### Inventory (observed at `0bfded71`; classified after E1)

Outside planning and the lock, 20 tracked files name 0.4.0: `pyproject.toml`,
3 manifests, `README.md`, 10 pages under `docs/`, 4 tests and one skill
reference under `src/gnd/skills/gnd-orm-core/references/`. Each is
classified as one of:

- historical: a statement about a past release;
- retained install pin: moves only at publication;
- recorded output: compared through `recorded_version.py`;
- stale: edited here.

Files that still name 0.3.1 or 0.3.0 were classified by RV1; its
[inventory](../../release-0.4.0/evidence/RV1/version-inventory.txt) is
rechecked for entries that the 0.4.0 publication edits changed.

### Modules

| ID | Path | Change | Lines (estimate) |
|---|---|---|---|
| M1 | `pyproject.toml` | `version = "0.5.0"` | 1 |
| M2 | `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json` | `"version": "0.5.0"` | 3 |
| M3 | `uv.lock` | the editable `get-nick-done` line, by hand | 1 |
| M4 | `tests/test_release_version.py` | add a `HEADLINE_BLOCK["0.5.0"]` entry (D4). No other case changes | 1 |
| M5 | files E1 names, if any | handled as D2 rules, with the digests listed before code | unknown until E1 |
| M6 | `docs/release-notes.md` | edit the opening paragraph; rename the `Unreleased:` heading to `## 0.5.0 (prepared, not published)`; add the blocks below | about 60 |
| M7 | `docs/compatibility.md` | 0.5.0 is prepared and not published, with the date availability was observed | 3 |
| M8 | `docs/support.md` | a row saying no profile is observed for 0.5.0 | 1 |
| M9 | `docs/marketplace-plugins.md` | until 0.5.0 is published, install the runtime from the repository. The pins are untouched | about 6 |

### Notes blocks (M6), proposed outline

The exact text is drafted at implementation from each milestone's close
record and reference pages. It goes into the record, and the review reads it.

1. `### PyRel rules programs for literature-style models` (the headline, D4),
   linking `runtimes/pyrel.md`. From the
   [pyrel-rules-coverage close](../../pyrel-rules-coverage/007-milestone-close.md):
   - external uniqueness is exported as a requirement over the shared-entity
     join;
   - anchored rules are listed as not checked and no longer refuse the
     program; exit 4 when a rule is not checked and none is violated;
   - `Number` is typed like `Float`, with the refusals that keep the programs
     from disagreeing with GND beyond 2**53;
   - role-scoped value rules;
   - populations the programs refuse (exit 3), and the cases where 0.4.0's
     programs gave a different result from `gnd check` (rows equal as
     numbers, a refused cell under `--rules lqp`);
   - the limit: the `--rules lqp` programs are verified to compile; no
     RelationalAI engine ran them.
2. `### Include roots on more routes`: the four blocks the section already
   has, unchanged.
3. `### Aggregate COUNT certificates`, linking the count contract reference.
   From the [COUNT close](../../aggregate-count-certificates/006-milestone-close.md):
   `gnd witness-count` and `gnd replay-count`, the certified zero for a
   covered empty group, and the packaged example.
4. `### Other changes`: the literature pages of PR 213, and anything the
   reconciliation finds.

Any change in behavior from 0.4.0 that a user's script could notice is
written as such in its block, as `docs/compatibility.md` requires (W19).

### Reconciliation table (filled at implementation)

One row per user-visible change, not per pull request, built by reading
`git diff v0.4.0 <base> -- src docs README.md PYPI.md pyproject.toml LICENSE NOTICE .claude-plugin .codex-plugin .agents/plugins`
file by file, leaving out this phase's own version edits (p1). Changes
that are tests only, planning only or internal get a reason instead of a
note. The table goes into `evidence/RW1/notes-reconciliation.md`.

### Normative order

None is added. The heading carries "not published" while 0.5.0 is not in
`RELEASED`, and that rule's one home is `tests/test_release_version.py`.

## 7. Decisions

| ID | Question | Readings and cost | Ruling |
|---|---|---|---|
| D1 | Version (plan RW-D1) | -- | open; proposed: 0.5.0, from the owner's request |
| D2 | If E1 moves a result or a recorded byte | (a) fix the comparison so the test reads the recorded version and no committed byte moves; (b) re-record that file with its digests listed. (a) is what RV1 did. Either way the owner sees the list first | open; proposed: (a) |
| D3 | Opt-in lanes in E1 (plan RW-D8) | excluded from E1, or run on both trees. `pyrel_oracle` is RW2's question, not E1's | open; proposed: excluded |
| D4 | The headline block for 0.5.0 | the PyRel rules block, linking `runtimes/pyrel.md`; or the include-roots block; or the COUNT block. The headline is what `HEADLINE_BLOCK` makes a test require | open; proposed: PyRel rules |
| D5 | The base commit of E1 | `0bfded71`, or main when the first ruling is recorded. A later base includes whatever merged meanwhile | closed by plan §11 (p1): the commit the bump is applied to, for both runs |

## 8. Tests

| ID | Case | Expected |
|---|---|---|
| T1 | `tests/test_release_version.py::test_lock_manifests_and_notes_agree_with_pyproject` and `test_drift_is_refused` | exit 0; each mutant raises `AssertionError` |
| T2 | `test_install_pins_name_a_published_version`, `test_a_pin_to_the_next_version_is_refused_until_it_is_released` | exit 0 with pins at 0.4.0; a `==0.5.0` pin fails |
| T3 | `test_notes_and_compatibility_do_not_claim_publication`, `test_support_and_plugin_pages_state_the_prepared_version` and their mutants | exit 0; mutants fail |
| T4 | `test_notes_section_names_the_headline_change` with M4, and `test_a_notes_section_without_its_headline_is_refused` | exit 0; mutants fail |
| T5 | `uv run python tools/release_text.py check`; `tests/test_release_text.py`; `tests/test_recorded_version.py`; `tests/test_package_description.py` | exit 0 |
| T6 | the structure guards of `project.md`; `tests/test_marketplace_plugins.py`, `tests/test_release_docs.py`, `tests/test_release_preparation.py`; the strict docs build | exit 0 |
| T7 | six-shard default lane on beast-3 at the RW1 tree | failing ids are only those of the E1 base run |
| T8 | `uv run ruff check --output-format=json` on the base and on the RW1 tree | the two finding lists are equal; exit 1 on both (plan C3) |

Each test name above was checked against `tests/test_release_version.py` at
`0bfded71`.

## 9. Out of scope for this phase

- Building or installing a wheel, and `tests/test_release_acceptance.py`
  (RW2).
- The install pins and `RELEASED` (publication stage).
- Any upload, tag or release.
- Any change under `src/`, unless D2 (a) needs one in a test helper.
- Repairing the lint findings (RC-01).

## 10. Size

The estimate is:

- 5 config lines;
- about 60 notes lines;
- about 10 other docs lines;
- 1 test line;
- M5, unknown until E1. RV1's M5 came to about 90 test lines.

The total without M5 is about 76 lines. The second ruling states the total
with M5; past 1.5 times that total, the phase pauses.

## 11. Approval instrument

This prose, plus §12 once E1 has run.

## Verification commands

```bash
uv lock --check
uv run pytest -q tests/test_release_version.py tests/test_recorded_version.py tests/test_release_text.py tests/test_marketplace_plugins.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_package_description.py --tb=short
uv run python tools/release_text.py check
uv run ruff check --output-format=json
uv run --group docs zensical build --strict
uv run python tools/check_docs.py site
```

The structure-guard command is the one in `project.md`. E1 and T7 run the
copied shard scripts on beast-3 over SSH.
