# Phase RW1: candidate content (version, lock, manifests, notes)

## 1. Status

**r6, resumed. E1 is to run again; no second ruling, and no
implementation.** r5 was held on the owner's ruling of 2026-11-24 that the
release also waits for ossie-relational-bundle (plan §13) (o). That
milestone's five phases and its close record are on main at `e8359685`
(§2). r6 rewrites the facts that main changed, tagged `(m2)`: the
dependency, the E1 base, the inventory, the notes outline, the
reconciliation counts and D4. §12 keeps the first measurement as it was
written. The [plan](release-0.5.0-plan.md) is r5: r2 approved by delegated
ruling ([plan gate](../001-plan-gate.md)), with §12 to §14 added. This spec
gets two rulings: the first approves the E1 measurement, the second binds
the handling E1 shows to be needed. Both are recorded in §7.

## 2. Provenance

This spec derives from the plan r3 and from the predecessor phase
[RV1](../../release-0.4.0/005-phase-RV1.md) and
[its spec](../../release-0.4.0/notes/phase-RV1-spec.md), whose method it
repeats. No review has run over these bytes. r2 and r3 described main at
`0bfded71` and were blocked. r4 rewrites the facts against main `c62a32b8`,
tagged `(m)` where a clause changed because main changed. Earlier tags stay:
`(p1)` for the plan's panel round and `(o)` for an owner ruling.

The dependency, observed at `c62a32b8` with `git log --first-parent` and
`git ls-tree`:

| Milestone | Close record on main |
|---|---|
| literature-host-interfaces | [006-milestone-close.md](../../literature-host-interfaces/006-milestone-close.md) |
| reviewed-vocabulary-growth | [007-milestone-close.md](../../reviewed-vocabulary-growth/007-milestone-close.md) |
| pins-and-review-check | [004-close.md](../../pins-and-review-check/004-close.md) |
| ossie-relational-bundle (m2) | [021-milestone-close.md](../../ossie-relational-bundle/021-milestone-close.md), observed at `e8359685` |

The fourth row is not like the other three (m2). That record's "Close
ruling" section says the owner directed the merge of its pull request and
that an explicit ruling that the milestone is closed is not recorded. The
owner's words for this dependency were that the release waits "so that I can
include it" (plan §13). The milestone's five phases and its notes are on
main, so the release can include it. Plan §14 records that reading as this
milestone's own and what it does not claim.

Also merged since the plan was written, and so in this release: all of
growth-round-outcomes and literature-reading-reference, and the pull
requests 254, 255, 257, 262, 265 and 267. Since r5: pull requests 264, 266
and 270 to 274 (ossie-relational-bundle) and 268 (a tooling sync that
changes no shipped file) (m2).

One thing differs from RV1 at the start: RV1 expected the bump to move
nothing and measured 37 moved results. This spec expects movement and names
where (§6, E1).

## 3. Obligations (step 0 harvest)

| Row | Obligation | Source | Discharged in |
|---|---|---|---|
| RW1-C1 | version 0.5.0 in `pyproject.toml`, the lock entry and three manifests | plan §4 | M1 to M3, T1 |
| RW1-C2 | E1 and the grep inventory are appended here before code, each entry classified, under a second ruling | plan §4, W8 | E1, §12, M5 |
| RW1-C3 | one 0.5.0 notes section; every user-visible change since `v0.4.0` is noted or reasoned; no `Unreleased:` section is left for work the candidate contains | plan §2, predicate 3, W6, W7 | M4, M6, T4, the reconciliation table |
| RW1-C4 | compatibility, support and plugin pages say 0.5.0 is prepared and not published; the pins stay at 0.4.0 | plan §4 | M7 to M9, T2, T3 |
| RW1-C5 | `tests/test_release_version.py` and `tools/release_text.py check` exit 0 | plan §4 | T1 to T5 |
| RW1-C6 | the full default lane has no failure the E1 base run lacks | plan §4, W10 | T7 |
| RW1-C7 | the lint gate. The plan asked for "no finding the base lacks" and a search for ten added findings; plan §12 records that `uv run ruff check` exits 0 on main, so the gate is exit 0 and the search has no subject (m) | plan §4, §12 | T8 |
| structure guards | a change outside `.gnd-planning/` runs them | `project.md` | T6 |
| component index | its check runs before a pull request | `project.md`, "Component index" | T9 |
| W15 | the notes say no RelationalAI engine ran the programs | plan §1 | M6, the PyRel block |
| R1 | the bump moves results or recorded bytes | plan §6 | E1, D2 |
| R3 | main says 0.5.0 before PyPI | plan §6 | M6 to M9, T2 |
| R10 | the notes read as if RelationalAI enforcement was verified | plan §6 | M6; the review brief names it |
| RR1 finding | `uv lock` regeneration once dropped an unrelated wheel line | rule-check-release RR1 record, by way of the RV1 spec | M3 edits the one line by hand; `uv lock --check` |
| plan §12 | the expected base result is taken from a measurement, not assumed | plan §12 | E1 "Expected" |

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
  messages stays in `docs/runtimes/pyrel.md`. A bullet that an earlier phase
  already wrote under an `Unreleased:` heading moves with its wording
  unchanged (m).
- `project.md` rules 1 to 4: this phase adds no consumer of untrusted input,
  no input-proportional work, no validation boundary and no policy walk.
- AGENTS.md, "General solutions, not pattern-matched ones": this phase adds
  no matcher. If D2 (a) changes a test comparison, it uses
  `tests/support/recorded_version.py`, the reader the repository already
  has, and adds no second one.

## 5. Goal

On the RW1 tree, all of the following hold:

- `uv run pytest -q tests/test_release_version.py` exits 0 with the declared
  version 0.5.0;
- `uv lock --check` exits 0;
- `uv run python tools/release_text.py check` exits 0;
- the focused gate of §8 exits 0;
- the six-shard default lane lists no failing test id that the E1 base run
  lacks;
- `uv run ruff check` exits 0.

## 6. Design

The phase builds no capability, so there is no reuse table. The one reuse
decision is in §4: `tests/support/recorded_version.py`.

### E1: the bump's effect (recorded before it runs)

- **What it measures:** which default-lane test ids change result when only
  the version changes, and which generated outputs change bytes. Two runs on
  beast-3, six round-robin shards over C-sorted `tests/test_*.py`, default
  marker filter:
  1. the base: the commit the bump is applied to (p1). That is the commit of
     this branch that records the renewed first ruling: main `e8359685`
     plus this milestone's planning-only commits (m2). Its hash is written in §12 with the
     results, because a spec cannot name the commit that contains it;
  2. a scratch tree of the same commit with 0.5.0 in `pyproject.toml`, the
     lock line and the three manifests, and nothing else changed.
- **Expected, base (m):** no failure, and the two known
  `test_public_optional` setup errors (RC-02). This is not a guess from the
  records alone: the lane at `c227c004` was measured (plan §12: 19 failed),
  and pull requests 254, 257 and 267 repaired main after it. Their own runs
  report no failure; none was repeated here, so the base run is also the
  first check of that claim. The first E1 confirmed it at `cfe5f00e` (§12).
  At `e8359685` the expectation is the same (m2); the Ossie milestone's
  close record reports its own files green and one red guard,
  `tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap`,
  which it calls known. If the base run shows it, it is a base failure and
  not this phase's.
- **Expected, bumped:** the release-version checks fail until M4 and M6 to
  M9 exist. `test_lock_manifests_and_notes_agree_with_pyproject` fails
  because the newest version heading is still 0.4.0;
  `test_notes_and_compatibility_do_not_claim_publication` and
  `test_support_and_plugin_pages_state_the_prepared_version` fail because no
  page names 0.5.0. The four consumers RV1 repaired
  (`tests/test_li1_assurance_report.py`,
  `tests/test_li1_literature_corpus.py`,
  `tests/test_expense_receipts_example.py`, `tests/test_release_text.py`)
  are expected to stay green, because RV1 made them compare through the
  recorded version. The unknown is every test added since 0.4.0 that reads
  the version. Seven files under `tests/fixtures/lh1-reading/` and the test
  files `test_lh1_reading_host.py`, `test_ir1_judgments_includes.py` and
  `vg3_cases.py` name 0.4.0 (m); so may the count example, the flatten
  record, the seeded-growth example and the reference set. Each id that
  moves is listed. The first E1 moved five ids, all in
  `tests/test_release_version.py` (§12). The Ossie milestone added tests of
  exported bytes and of documentation; whether any reads the version is what
  the second run shows (m2).
- **What it cannot measure:** opt-in lanes (D3), and anything an installed
  wheel shows (RW2).
- **Liveness:** the bumped tree with no notes change must turn at least
  `test_lock_manifests_and_notes_agree_with_pyproject` red. If it does not,
  the instrument is not reading the bump. A runner or setup failure supplies
  no E1 result.

The instrument is [e1-shards.sh](../evidence/RW1/e1-shards.sh), RV1's
[script](../../release-0.4.0/evidence/RV1/e1-shards.sh) with the commit and
the mode (`base` or `bumped`) made arguments and the version strings moved
on. The record carries the diff of the two scripts. It clones the public
repository, so the base commit is pushed before E1 runs.

### Inventory (observed at `c62a32b8` and again at `e8359685`; classified after E1) (m) (m2)

Outside planning and the lock, 29 tracked files name 0.4.0, the same 29 at
both commits:

- `pyproject.toml` and the 3 manifests;
- `README.md`;
- 10 pages under `docs/`: `bookrec/08-guarded-rules.md`,
  `bookrec/09-suggested-rules.md`, `compatibility.md`,
  `expense/05-receipts.md`, `index.md`, `installation.md`,
  `literature/index.md`, `marketplace-plugins.md`, `release-notes.md`,
  `support.md`;
- 1 skill reference:
  `src/gnd/skills/gnd-orm-core/references/provenance-and-modality.md`;
- 7 fixture files under `tests/fixtures/lh1-reading/`;
- 6 test files: `test_ir1_judgments_includes.py`,
  `test_lh1_reading_host.py`, `test_recorded_version.py`,
  `test_release_acceptance.py`, `test_release_version.py`, `vg3_cases.py`.

Each is classified as one of:

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
| M6 | `docs/release-notes.md` | edit the opening paragraph; replace the five `Unreleased:` headings (m2) by one `## 0.5.0 (prepared, not published)` section; add the blocks below | about 60 new, about 135 moved |
| M7 | `docs/compatibility.md` | 0.5.0 is prepared and not published, with the date availability was observed | 3 |
| M8 | `docs/support.md` | a row saying no profile is observed for 0.5.0 | 1 |
| M9 | `docs/marketplace-plugins.md` | the plugin on `main` is 0.5.0, prepared and not published; install the runtime from the same commit. The pins are untouched | about 4 |

### Notes blocks (M6), proposed outline (m)

Main has five `Unreleased:` sections holding 26 bullets (m2), written by
the phases that shipped them. They become one section with these `###` blocks.
A moved bullet keeps its wording. New text is drafted at implementation from
each milestone's close record and reference pages; it goes into the record,
and the review reads it.

1. `### PyRel rules programs for literature-style models` (the headline, D4),
   linking `runtimes/pyrel.md`. New text, from the
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
2. `### Include roots on more routes`: the four bullets on judgments,
   `gnd flatten`, the PyRel export of include roots and unencodable include
   paths, moved.
3. `### Unattended growth from a reviewed vocabulary`, linking
   `unattended-growth.md`: the nine bullets of reviewed-vocabulary-growth
   and growth-round-outcomes, moved (growth from a reviewed vocabulary,
   sample and common-sense constraints, seeded roots, the seeded example,
   one parse per text, operation outcomes, the reply shape, the admitted
   part of a round, the round summary).
4. `### The literature examples from a host`: the admission and reading
   bullets and the three literature-reading-reference bullets, moved.
5. `### Aggregate COUNT certificates`, linking the count contract reference.
   New text, from the
   [COUNT close](../../aggregate-count-certificates/006-milestone-close.md):
   `gnd witness-count` and `gnd replay-count`, the certified zero for a
   covered empty group, and the packaged example.
6. `### Ossie relational files` (m2), linking `explanation/ossie.md` and
   the how-to page: the four bullets of ossie-relational-bundle, moved
   (tables beside the ontology, your own tables, larger files, where to
   read more). Its place in the section follows D4.
7. `### Other changes`: `gnd check` on large vocabularies, the frontmatter
   fences, the literature pages of PR 213, and anything the reconciliation
   finds.

Any change in behavior from 0.4.0 that a user's script could notice is
written as such in its block, as `docs/compatibility.md` requires (W19).

### Reconciliation table (filled at implementation)

One row per user-visible change, not per pull request, built by reading
`git diff v0.4.0 <base> -- src docs README.md PYPI.md pyproject.toml LICENSE NOTICE .claude-plugin .codex-plugin .agents/plugins`
file by file, leaving out this phase's own version edits (p1). At
`c62a32b8` that diff holds 125 files (+6,612, −486), 103 of them under
`src`; 46 first-parent commits separate `v0.4.0` from it (m). At
`e8359685` it holds 140 files (+10,079, −601), 115 of them under `src`, and
56 first-parent commits (m2); the 25 files the Ossie milestone touched get
their rows at implementation. Changes that
are tests only, planning only or internal get a reason instead of a note.
The table goes into `evidence/RW1/notes-reconciliation.md`. It names every
file of the diff once, so a file with no row is visible as a gap.

### Normative order

None is added. The heading carries "not published" while 0.5.0 is not in
`RELEASED`, and that rule's one home is `tests/test_release_version.py`.

## 7. Decisions

| ID | Question | Readings and cost | Ruling |
|---|---|---|---|
| D1 | Version (plan RW-D1) | -- | open; proposed: 0.5.0, from the owner's request |
| D2 | If E1 moves a result or a recorded byte | (a) fix the comparison so the test reads the recorded version and no committed byte moves; (b) re-record that file with its digests listed. (a) is what RV1 did. Either way the list is written before code | open; proposed: (a) |
| D3 | Opt-in lanes in E1 (plan RW-D8) | excluded from E1, or run on both trees. `pyrel_oracle` is RW2's question, not E1's | open; proposed: excluded |
| D4 | The headline block for 0.5.0 | (a) the PyRel rules block, linking `runtimes/pyrel.md`: the one block where 0.5.0 gives a different result from 0.4.0 on the same input, and the plan's RW-D3 proposal; (b) unattended growth from a reviewed vocabulary; (c) the literature examples from a host. The owner made the release wait for the milestones behind (b) and (c), which may mean one of them is the release's point. Changing it later costs one test line and the order of two blocks. (d) (m2) the Ossie relational files, linking `explanation/ossie.md`: the milestone the owner held the release for last, with the words "so that I can include it", and the one that changes what a default `gnd export ossie` run writes | open; put to the owner before the second ruling, because r5's close said so; proposed: (a) or (d) |
| D5 | The base commit of E1 | closed by plan §11 (p1): the commit the bump is applied to, for both runs | closed |
| D6 | Does a moved bullet keep its issue links and wording? (m) | yes: each was reviewed in its own phase, and rewording it here would be an unreviewed second home for the same statement. The cost is a section whose blocks differ in style | open; proposed: yes |

Rulings are appended below this line, each with its date, source and the
SHA-256 of the spec bytes it covers.

> **First ruling: delegated approval (auto=true), 2026-11-24.** Approved
> draft r4 of this spec at SHA-256
> c6139c66b2717f11d3b391c9b67636b8273a7cb2f63b4e2125577ea8af8e9365 (commit
> `09335d8a`) for the E1 measurement only. Source: the owner's request
> "Release 0.5.0" and the owner's selection of delegated approval on
> 2026-11-23; the owner's two dependency rulings (plan §11 and §12) are met
> on main at `c62a32b8`. Decisions: D1 0.5.0; D3 opt-in lanes excluded from
> E1; D5 as closed. D2, D4 and D6 wait for the second ruling. Instrument:
> this prose; no spec review was called for. Budget: two six-shard lanes on
> beast-3. No implementation file changes under this ruling. This ruling is
> not the owner's reading of the spec.

> **First ruling, renewed: delegated approval (auto=true), 2026-11-25.**
> Approved draft r6 of this spec at SHA-256
> a56efcc9ea2f3f38b81b929fd5e8d7a661f6192e0d04705a63733cca192e847e (commit
> `b25bb2d8`) for the E1 measurement only, at the resumed base. Source: the
> owner's request "Release 0.5.0" and the owner's selection of delegated
> approval on 2026-11-23; the four milestones of plan §11 to §13 are on
> main at `e8359685` (plan §14, with the limit it states for the fourth).
> Decisions: D1, D3 and D5 as in the first ruling. D2 and D6 wait for the
> second ruling; D4 is put to the owner first. Instrument: this prose; no
> spec review was called for. Budget: two six-shard lanes on beast-3. No
> implementation file changes under this ruling. This ruling is not the
> owner's reading of the spec.

## 8. Tests

| ID | Case | Expected |
|---|---|---|
| T1 | `tests/test_release_version.py::test_lock_manifests_and_notes_agree_with_pyproject` and `test_drift_is_refused` | exit 0; each mutant raises `AssertionError` |
| T2 | `test_install_pins_name_a_published_version`, `test_a_pin_to_the_next_version_is_refused_until_it_is_released` | exit 0 with pins at 0.4.0; a `==0.5.0` pin fails |
| T3 | `test_notes_and_compatibility_do_not_claim_publication`, `test_support_and_plugin_pages_state_the_prepared_version` and their mutants | exit 0; mutants fail |
| T4 | `test_notes_section_names_the_headline_change` with M4, and `test_a_notes_section_without_its_headline_is_refused` | exit 0; mutants fail. A control run with the headline block moved second must fail, shown once in the record |
| T5 | `uv run python tools/release_text.py check`; `tests/test_release_text.py`; `tests/test_recorded_version.py`; `tests/test_package_description.py` | exit 0 |
| T6 | the structure guards of `project.md` as that page lists them on the RW1 tree; `tests/test_marketplace_plugins.py`, `tests/test_release_docs.py`, `tests/test_release_preparation.py`; the strict docs build | exit 0 |
| T7 | six-shard default lane on beast-3 at the RW1 tree | failing ids are only those of the E1 base run |
| T8 | `uv run ruff check` | exit 0 (m) |
| T9 | `python3 scripts/components_index.py changed --base <E1 base> --strict` | 0 to fix (m) |

Each test name above was checked against `tests/test_release_version.py` at
`c62a32b8`. That file, `tools/release_text.py` and the three status pages
are unchanged between `c62a32b8` and `e8359685` (m2).

### Verification selection

| Kind | Selection |
|---|---|
| Plan-mandated | the plan §9 row for RW1: the seven focused files, the consumers E1 names, the structure guards, `release_text.py check`, the lint gate, the strict docs build, the full default lane on beast-3 |
| Direct | T1 to T5 |
| Impact closure | T6, T9, and every test id E1 lists as moved |
| Broad lanes | the full default lane is selected by the plan (T7). `evidence`, `census`, `pyrel_oracle` and the other opt-in lanes are not run (D3) |

### Implementability

- Every requirement has a command that can fail and can pass: T1 to T4 have
  mutants, T7 compares two id lists, T8 and T9 have exits.
- RW1-C3 as the plan words it ("every user-visible change") cannot be
  proved by a test. It is shown by the reconciliation table, which names
  every file of the diff, and is read by the reviewer. That limit is stated
  in the record.
- The notes cannot be both "the bullets as their phases wrote them" and
  uniform in style. D6 chooses the first.

## 9. Out of scope for this phase

- Building or installing a wheel, and `tests/test_release_acceptance.py`
  (RW2).
- The install pins and `RELEASED` (publication stage).
- Any upload, tag or release.
- Any change under `src/`, unless D2 (a) needs one in a test helper.
- New product behavior, and rewording a bullet another phase wrote.

## 10. Size

The estimate is:

- 5 config lines;
- about 60 new notes lines, and about 135 (m2) existing notes lines moved under
  new headings with their wording unchanged;
- about 8 other docs lines;
- 1 test line;
- M5, unknown until E1. RV1's M5 came to about 90 test lines.

The total of new or changed lines without M5 is about 74; the moved lines
are counted apart because a diff shows them twice. The second ruling states
the total with M5; past 1.5 times that total, the phase pauses.

## 11. Approval instrument

This prose, plus §12 once E1 has run. Corpus-first is not used: the phase
changes no serialized format, exit code or validation predicate.

## Verification commands

```bash
uv lock --check
uv run pytest -q tests/test_release_version.py tests/test_recorded_version.py tests/test_release_text.py tests/test_marketplace_plugins.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_package_description.py --tb=short
uv run python tools/release_text.py check
uv run ruff check
uv run --group docs zensical build --strict
uv run python tools/check_docs.py site
python3 scripts/components_index.py changed --base <E1 base> --strict
```

The structure-guard command is the one in `project.md`. E1 and T7 run
[e1-shards.sh](../evidence/RW1/e1-shards.sh) on beast-3 over SSH.

## 12. E1 results at `cfe5f00e` (a measurement, not yet the basis of a ruling)

E1 ran on 2026-11-24 under the first ruling, at the commit that records it:
`cfe5f00e`, which is main `c62a32b8` plus this milestone's planning-only
commits. The [summary](../evidence/RW1/e1-summary.md) has both lanes' output.

| Lane | Passed | Failed | Errors | Skipped |
|---|---|---|---|---|
| base | 21,354 | 0 | 2 | 13 |
| bumped | 21,349 | 5 | 2 | 13 |

- **Base, against the prediction.** No failure and the two RC-02 errors, as
  predicted. This is also the first full default lane this milestone ran on
  main after the repairs of pull requests 254, 257 and 267.
- **Bumped, against the prediction.** The five failures are all in
  `tests/test_release_version.py`:
  `test_lock_manifests_and_notes_agree_with_pyproject`,
  `test_agreement_control_passes_on_an_unmutated_copy`,
  `test_drift_is_refused[notes]`,
  `test_notes_and_compatibility_do_not_claim_publication` and
  `test_support_and_plugin_pages_state_the_prepared_version`. The spec named
  three of them; the other two read the same notes heading through a copied
  tree. The liveness condition holds.
- **Nothing else moved.** The ten files added since 0.4.0 that name 0.4.0
  in tests or fixtures did not change a result, and neither did the four
  consumers RV1 repaired. At this commit M5 is empty and D2 has no subject.
  The 0.4.0 bump moved 37 results; this one moves 5.
- **Not measured:** which generated outputs change bytes. No test that
  compares generated bytes changed result, and no byte comparison was run.

These results describe `cfe5f00e`. The phase is held (§1), so they are not
the basis of the second ruling: ossie-relational-bundle will add tests and
shipped files, and E1 runs again at the commit the bump is applied to.

Prepared while E1 ran, for the tree as it is at `c62a32b8`, and to be
redone with the spec:

- [notes-reconciliation.md](../evidence/RW1/notes-reconciliation.md): the
  125 shipped files that differ from `v0.4.0`, each in one row, with the
  note or the reason for none. Built from which pull request changed each
  file and the bullets already in the notes; five entry-point diffs were
  read line by line, the rest were not.
- [old-version-probes.md](../evidence/RW1/old-version-probes.md): two inputs
  on which 0.4.0's DuckDB rules program reports a rule satisfied and
  `gnd check` reports a failure. The notes' PyRel block would cite them.

## 13. E1 at the resumed base (m2)

E1 runs again under the renewed first ruling of §7, at the commit that
records it. Its results are appended here before the second ruling.
