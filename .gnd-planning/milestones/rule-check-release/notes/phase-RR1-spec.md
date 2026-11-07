# Phase RR1: candidate content (version, lock, manifests, notes)

## 1. Status

**Draft r1, 2026-11-07. Blocked; not ready for an owner gate.** It cannot be
approved until (a) the plan's gate has passed (RL-D1, the version, is ruled: 0.2.0), and (b) experiment E1 (§6) has run over the full default lane
and §7 D2 carries its ruling. The numbers below that depend on RL-D1 use the
ruled `0.2.0` and are marked `<V>`. No code is written. `auto=false`.

## 2. Provenance

- Plan r1 [rule-check-release-plan.md](rule-check-release-plan.md) §4 RR1,
  completion predicates 1 and 2, obligations O9 to O15, risks R1 to R3.
  The plan has not been reviewed and is not owner-approved; nothing here is
  approved by it.
- Issue 118. AGENTS.md ("Release preparation does not enable a production
  publisher").
- Base: main `12daa5b7`. A scratch-copy probe of 2026-11-07 (plan O9) supplies
  the only measurement in this draft; it is partial and is not E1.
- No review round has run over these bytes.

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| plan RR1-C1 | `pyproject.toml` carries the ruled version; `uv lock --check`; three manifests | M1-M3, T1 |
| RR1-C2 | a test fails for each of four drift mutants | T1 (M1..M4 mutants) |
| RR1-C3 | no test names the old version as its own literal | M4, T2 |
| RR1-C4 | moved bytes listed before code, each handled by the ruled method | §6 E1, D2, M5 |
| RR1-C5 | release notes, compatibility and support text true and unpublished | M6, M7, M8, T1 |
| RR1-C6 | full default lane, no failure the merge base lacks | V3 |
| RR1-C7 | README and installation pins unchanged, visibly | M9, T3 |
| plan rule 2 | version written once | M1, T1 |
| plan rule 3 | no instruction names an unpublished version | M9, T3 |
| plan rule 6 | measured before designed | §6 |
| plan R2 | `release-notes.md` conflicts | V1 (rebase before PR) |
| O11 | plugin manifests equal the package version | M2, existing `tests/test_marketplace_plugins.py` |
| O22 / AGENTS.md | component index | V5 |
| project.md rule 5 | one home | §4 |

## 4. The standing rules, bound to this phase

| Rule | Binding here |
|---|---|
| plan 0.1 prepare, never publish | RR1 edits no file under `.github/`, no setting, and runs no upload. V6 diffs `.github/` against the base and expects empty |
| plan 0.2 one home for the version | `pyproject.toml` is the home. `uv.lock`, the manifests and the notes heading are checked against it by T1; the distribution test reads it (M4) |
| plan 0.3 no instruction names an unpublished version | M9 leaves the pins; T3 fails if a pin names a version greater than the one in `pyproject.toml` or the released set recorded in the test |
| plan 0.4 evidence belongs to exact bytes | RR1 produces no candidate; it records the merge-base and closing-tree commits of the full-lane runs |
| plan 0.6 measure | §6 E1 |
| project.md 1 totality | inapplicable: no new reader of untrusted input; T1 reads four tracked files of this repository |
| project.md 2 input cap | inapplicable: no work proportional to document input |
| project.md 3 validation order | inapplicable: no boundary with two rejecting checks |
| project.md 4 one walk | inapplicable: no policy over element kinds |
| project.md 5 one home | the version (above); the release procedure stays in `docs/releasing.md`, which RR1 does not edit |
| project.md 6 measurement | E1, run before D2 is ruled |

## 5. Goal

On the RR1 branch, `uv run pytest -q` over the files of V2 exits 0, `uv lock
--check` exits 0, the six-shard full default lane exits with only the failures
the merge-base run also has, and `grep -rn` finds no tracked file other than
retained evidence that names `0.1.0` as the current version.

## 6. Design

### Reuse table

| Capability | Searches | Found | Decision |
|---|---|---|---|
| resolve the installed version | `components_index.py search release version publish`; `git grep resolve_version` | `infra.version` / `gnd.resolve_version`: reads distribution metadata, `0.0.0.dev+unpackaged` fallback | reuse; no change |
| compare declared versions across files | `components_index.py search wheel sdist build`; `git grep tomllib tests` | `tests/test_marketplace_plugins.py` already reads `pyproject` and compares manifests (lines 22-29) | adapt: the new test reuses its pattern, does not import it |

### E1: the version bump's effect (recorded before it runs)

**Measures.** Which tracked tests fail when only the version changes. **Cannot
measure.** Failures unrelated to the version (the comparison with a merge-base
run separates them), and behavior in the opt-in lanes (`evidence`, `census`,
`distribution`), which the default lane skips.

**Procedure.** On beast-3, with `~/close-shards/close-shards.sh` (six
round-robin shards, uv on PATH): (1) the merge-base tree, untouched; (2) the
same tree with exactly M1 and M2 applied and the environment re-synced. The
moved set is the failures of (2) not in (1). If the script's path or arguments
differ from the rule-check-adoption close, the spec records the command
actually run; unresolved until then.

**Liveness.** The probe of 2026-11-07 already shows the instrument can see a
move: on a scratch copy, 12 cases in four files failed at 0.2.0 and passed 85
of 85 at 0.1.0 (plan O9). E1 must reproduce those 12 or explain why it does
not.

**Limits stated first.** The probe tried 21 of 656 test files, chosen by a
grep for the fixture directories; it is not the list. Opt-in lanes are not
covered; if the owner wants them covered it asks for the lanes by name (the
`evidence or census` command of `project.md`).

**Candidate handling methods for D2** (E1 decides which sites need which):

| Method | What it does | Cost |
|---|---|---|
| (a) normalize | the comparing test replaces the version field with a placeholder in both sides | changes what the test pins (the version no longer pinned); retained bytes stay |
| (b) regenerate | re-record the retained output at the new version | rewrites retained evidence; every digest recorded downstream moves |
| (c) fix the version | the test environment forces the version the retained output was recorded at | adds a test-only override of a documented single home |

### Modules

| # | Path | Change | Lines |
|---|---|---|---|
| M1 | `pyproject.toml` | `version = "0.1.0"` to `"<V>"` (line 6). Nothing else | 1 |
| M2 | `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json` | `"version": "<V>"` | 3 |
| M3 | `uv.lock` | the `get-nick-done` editable entry (line 100) via `uv lock`; no dependency changes (checked by diff) | 1 |
| M4 | `tests/test_public_distribution.py` | lines 250, 255, 286, 331 read `<V>` from `pyproject.toml` (`tomllib`) instead of the literal `0.1.0` | about 10 |
| M5 | per E1 and D2 | the sites E1 lists | unknown until E1 |
| M6 | `docs/release-notes.md` | opening paragraph replaced; one `## <V> (prepared, not published)` section whose first block is the rule-check items of issue 118 (report version 15 with `--rule-ids`, `remedy`, the acyclic extent; `--baseline`; `--allow-vacuous`; `source: tool-output` with `producer`), then the twelve existing `Unreleased:` sections demoted to `###` subsections with their dates, in order | about 200, mostly moves |
| M7 | `docs/compatibility.md` | line 3: "Current 0.1.0 metadata is provisional" replaced by the state: 0.1.0 is published; `<V>` is prepared and not published; availability observed on 2026-11-07 | 3 |
| M8 | `docs/support.md` | profile rows say the prepared package is not signed off and no profile is yet observed for it | 4 |
| M9 | `README.md`, `docs/installation.md` | none. The `==0.1.0` pins stay | 0 |

### The new test, exact surface

`tests/test_release_version.py`:

```python
def declared_version() -> str: ...                 # tomllib over pyproject.toml
def lock_version() -> str: ...                     # the get-nick-done entry of uv.lock
def manifest_versions() -> dict[str, str]: ...     # the three manifest files
def notes_headings() -> list[str]: ...             # '## ' lines of docs/release-notes.md
def pinned_install_versions() -> set[str]: ...     # '==X' after 'get-nick-done' in README.md, docs/installation.md
```

Tests:

- `test_lock_manifests_and_notes_agree_with_pyproject`
- `test_drift_is_refused[pyproject|lock|manifest|notes]`, each building the
  four values from a mutated copy (a tmp tree, not the real files) and
  asserting the agreement function refuses
- `test_install_pins_name_a_published_version`: every pin is `<=` the declared
  version and is in `RELEASED = {"0.1.0"}`, a tuple in this test file that the
  publication-day patch edits (so a pin can only move with the record of what
  is published)

### Normative order

Version: `pyproject.toml` (one home). Release procedure: `docs/releasing.md`
(one home; unchanged here). Release notes are descriptive, not normative; they
cite the reference pages for behavior.

## 7. Decisions

| ID | Question | Readings and cost | Status |
|---|---|---|---|
| D1 | The version (plan RL-D1) | `0.2.0` proposed; `0.1.1` understates; both change only M1-M3, M6-M8 | **Ruled (o, 2026-11-07): 0.2.0** ("0.2.0", answering "Which version should the release carry?") |
| D2 | How E1's moved bytes are handled (plan RL-D9) | methods (a), (b), (c) above, possibly different per site | open, after E1 |
| D3 | The unreleased notes' shape (plan RL-D3) | one version section with `###` subsections (proposed), or flat | open |
| D4 | Pins stay at 0.1.0 until publication (plan RL-D4) | proposed; flipping now publishes a false instruction | open |
| D5 | Release-notes wording of the opening: "prepared, not published" with a link to `docs/releasing.md` | proposed | open |

At first write every row was open; D1 has since been ruled, the rest are open.

## 8. Tests

| ID | File, case | Expected |
|---|---|---|
| T1 | `tests/test_release_version.py::test_lock_manifests_and_notes_agree_with_pyproject` | exit 0 on the RR1 tree |
| T1m | `test_drift_is_refused` x4 (pyproject, lock entry, one manifest, notes heading each mutated to a different version) | each raises `AssertionError` from the agreement function; the control (no mutation) passes, proving the harness can pass |
| T2 | `tests/test_public_distribution.py` (the four sites), run on the evidence lane with the opt-in command the file's own markers need, recorded in the spec when selected | exit 0; unchanged when `<V>` changes again (checked by changing `pyproject` in a tmp copy) |
| T3 | `test_install_pins_name_a_published_version` | exit 0; a mutant pin `==<V>` fails it |
| T4 | `tests/test_marketplace_plugins.py` (existing, including its `999.0.0` mutation) | exit 0 |
| T5 | `tests/test_release_docs.py`, `tests/test_release_preparation.py` | exit 0 (links in the changed notes resolve; workflow shape untouched) |
| T6 | the E1-listed tests | exit 0 after M5 |
| V3 | the six-shard full default lane at the closing tree vs the merge-base run | no failure the merge base lacks |

Branch walk: each agreement (pyproject = lock, = manifests, = notes heading)
is a branch with a mutant that fails it; the pin rule has the `<=` branch
(mutant: a pin above the declared version) and the released-set branch
(mutant: a pin at a version that is declared but not released).

## 9. Out of scope for this phase

The build, any wheel, any acceptance run (RR2); the dossier and the
post-publication patch (RR3); `docs/releasing.md`; `release.yml` and its test;
any publication step; any change to what a command computes. A reviewer must
not ask for them.

## 10. Size

Estimate: about 15 config lines, 60 test lines, 200 notes lines (mostly moved),
M5 unknown. Past 1.5 times the estimate, excluding M5's regenerated or
normalized bytes, the phase pauses for the owner. M5's size is reported
separately once E1 gives it.

## 11. Approval instrument

This prose, after E1 supplies §6's list and D1, D2 are ruled. A fixture corpus
is not used: the checks are equalities over tracked files, and the answer
(the version) is a ruling, not a hidden key.

## Verification commands (unresolved ones marked)

- V1: `git fetch origin && git rebase origin/main` immediately before the PR.
- V2: `uv run pytest -q tests/test_release_version.py tests/test_marketplace_plugins.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_induced_provenance.py tests/test_fidelity_payload.py --tb=short` plus the E1 list. The `tests/test_public_distribution.py` selection is **unresolved**: its cases need the `distribution` or `evidence` lane, which `project.md` forbids bringing into an ordinary gate; the spec names the one command when the owner rules it.
- V3: `~/close-shards/close-shards.sh <run> <sha>` on beast-3 (present on 2026-11-07; arguments unresolved until read at the time).
- V4: `uv run ruff check`.
- V5: `python3 scripts/components_index.py changed --base main --strict`.
- V6: `git diff --stat origin/main -- .github` is empty.
