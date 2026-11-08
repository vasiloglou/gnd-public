# Phase RR1: candidate content (version, lock, manifests, notes)

## 1. Status

**Approved (o, 2026-11-07); implementation under way.** The owner approved this spec as pushed to PR 125 at commit `302c98ed` (spec sha256 `0a41e5eaabe3aa618e539dd4ed828aa835a17af8d770b206a5065f1f0204af52`, draft r3). Ruling, answering "PR 125: approve the RR1 spec so the release prep can start?": **"approved all"**, relayed to this session by the session that started it. It covers the two items the draft left for the gate, taken as proposed: D5 is ruled "prepared, not published" with a link to `docs/releasing.md`, and T2's consequence (the distribution file's four literals run at RR2, not RR1) stands. It is not a review opinion, it approves no publication and no RR2 spec, and the approved bytes carry the Codex review of r1 only. `auto=false`. This status line is the only edit to the approved file.

History: r2 carried the repairs after the Codex review of r1; r3 recorded experiment E1 (§12), the owner's rulings on D2 and on the opt-in lanes (§7), and the per-file classification and moved-digest list (§13). It could not be approved until (a) [done] the plan gate passed on 2026-11-07 (plan r2 approved) and RL-D1 was ruled: 0.2.0, and (b) [done] experiment E1 (§6) ran over the full default lane (§12) and D2 carried its ruling (§7). The numbers below that depend on RL-D1 use the ruled `0.2.0` and are marked `<V>`.

## 2. Provenance

- Plan r1 [rule-check-release-plan.md](rule-check-release-plan.md) §4 RR1,
  completion predicates 1 and 2, obligations O9 to O15, risks R1 to R3.
  The plan has not been reviewed and is not owner-approved; nothing here is
  approved by it.
- Issue 118. AGENTS.md ("Release preparation does not enable a production
  publisher").
- Base: main `12daa5b7`. A scratch-copy probe of 2026-11-07 (plan O9) supplies
  the only measurement in this draft; it is partial and is not E1.
- One reviewer (Codex) read r1 of this spec with the plan at dbf98447 ([record](../evidence/plan-review-r1/codex-review.md)); r2 repairs P4, P9, P10 and P11 and carries no review opinion.

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| plan RR1-C1 | `pyproject.toml` carries the ruled version; `uv lock --check`; three manifests | M1-M3, T1 |
| RR1-C2 | a test fails for each of four drift mutants | T1 (M1..M4 mutants) |
| RR1-C3 | no test names the old version as its own literal, except the `RELEASED` record | M4, T2, T3 |
| RR1-C4 | E1 list plus grep inventory before code, each classified and handled by the ruled method; opt-in lanes named exclusions | §6 E1, §12, §13, D2, D6, M5 |
| RR1-C5 | release notes, compatibility and support text true and unpublished, gated by a test | M6, M7, M8, T7 |
| RR1-C6 | full default lane, no failure the merge base lacks | V3 |
| RR1-C7 | README and installation pins unchanged, visibly | M9, T3 |
| RR1-C8 | plugin users get a route while the plugin is newer than the runtime | M10 |
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
covered; the owner ruled them excluded (D6), so RR1's record names them as
exclusions and any version-bearing site that only an opt-in lane reads stays
unmeasured.

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
| M5 | per D2 (§13) | M5a: `tests/support/rf1_pins.py` compares `gnd_version` as a placeholder (method a). M5b to M5n: re-record the 14 sites of §13 (method b), each at the digests of `evidence/e1/moved-digests.md`. No edit to `src/` | 1 helper (about 8 lines); 28 re-recorded files, of which 11 are gzip containers repacked with their pinned digest |
| M6 | `docs/release-notes.md` | opening paragraph replaced; one `## <V> (prepared, not published)` section whose first block is the rule-check items of issue 118 (report version 15 with `--rule-ids`, `remedy`, the acyclic extent; `--baseline`; `--allow-vacuous`; `source: tool-output` with `producer`), then the twelve existing `Unreleased:` sections demoted to `###` subsections with their dates, in order | about 200, mostly moves |
| M7 | `docs/compatibility.md` | line 3: "Current 0.1.0 metadata is provisional" replaced by the state: 0.1.0 is published; `<V>` is prepared and not published; availability observed on 2026-11-07 | 3 |
| M8 | `docs/support.md` | profile rows say the prepared package is not signed off and no profile is yet observed for it | 4 |
| M9 | `README.md`, `docs/installation.md`, `docs/index.md` | none. The `==0.1.0` pins stay | 0 |
| M10 | `docs/marketplace-plugins.md` | one paragraph under "Updates": until `<V>` is published, install the runtime from the repository at a commit, as the tutorials say, because the plugin on `main` is newer than the PyPI runtime | about 6 |

### The new test, exact surface

`tests/test_release_version.py`:

```python
def declared_version() -> str: ...                 # tomllib over pyproject.toml
def assert_versions_agree(declared: str, lock: str, manifests: dict[str, str], notes: list[str]) -> None: ...   # raises AssertionError on any disagreement; every drift test calls it
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
- `test_notes_and_compatibility_do_not_claim_publication`: while `declared_version()` is not in `RELEASED`, its notes heading contains "not published" and `docs/compatibility.md` contains "not published" (T7)
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
| D2 | How E1's moved bytes are handled (plan RL-D9) | methods (a), (b), (c) above, possibly different per site | **Ruled (o, 2026-11-07): "Split (a)+(b) (Recommended)"** (answering "Release RR1 decision D2 (PR 125): the 0.2.0 bump turns 47 tests red because 32 saved reference outputs record version 0.1.0. How should they be handled?", relayed by the session that started this one). Meaning, as relayed: (a) normalize the version in the one RF1 pin helper `tests/support/rf1_pins.py`; (b) regenerate the committed outputs whose purpose is to equal the current command's output, listing every moved digest in the spec before any code (plan rule 6); no (c). The other pin-style failures are classified by the same rule in §13 |
| D3 | The unreleased notes' shape (plan RL-D3) | one version section with `###` subsections gives readers one "what's new" at the cost of moving about 200 lines; renaming in place moves none but leaves twelve unrelated headings | **Ruled (o, 2026-11-07): as proposed** (plan RL-D3, relayed by the session that started this one): one section |
| D4 | Pins stay at 0.1.0 until publication (plan RL-D4) | flipping the pins now tells users to install a file that does not exist; holding the flip until publication leaves the pins stale for the wait (a prepared patch bounds it) | **Ruled (o, 2026-11-07): as proposed** (plan RL-D4, relayed by the session that started this one): pins stay at 0.1.0 |
| D5 | Release-notes wording of the opening: "prepared, not published" with a link to `docs/releasing.md` | readings: that wording, or a plain "not yet released"; neither changes an exit code, both are gated by T7 | **Ruled (o, 2026-11-07): "approved all"** (the spec approval, relayed), taken as proposed: "prepared, not published" with a link to `docs/releasing.md` |
| D6 | Does RR1 run the opt-in lanes (`evidence`, `census`) on both versions? | readings: run them on the base and on the bumped tree (costs two lane runs and may add sites to M5) or record them as excluded (leaves any version-bearing site in those lanes unmeasured; `tests/test_public_distribution.py` is among them, so T2 cannot run in RR1) | **Ruled (o, 2026-11-07): "Record as excluded (Recommended)"** (answering "Should RR1 also run the opt-in test lanes (evidence, census) on both versions, or record them as not measured?", relayed by the session that started this one) |

At first write every row was open. D1 to D6 are ruled (their rows).

## 8. Tests

| ID | File, case | Expected |
|---|---|---|
| T1 | `tests/test_release_version.py::test_lock_manifests_and_notes_agree_with_pyproject` | exit 0 on the RR1 tree |
| T1m | `test_drift_is_refused` x4 (pyproject, lock entry, one manifest, notes heading each mutated to a different version) | each raises `AssertionError` from the agreement function; the control (no mutation) passes, proving the harness can pass |
| T2 | `tests/test_public_distribution.py` (the four sites) | **not run in RR1** (D6: opt-in lanes excluded). Checked by `ruff` and the RR1-C3 grep; the cases run at RR2. The owner sees this consequence at the gate |
| T3 | `test_install_pins_name_a_published_version` | exit 0; a mutant pin `==<V>` fails it |
| T7 | `test_notes_and_compatibility_do_not_claim_publication` and its mutant (a heading `## 0.2.0` without the status, a compatibility page saying "is published") | exit 0 on the tree; the mutant fails |
| T4 | `tests/test_marketplace_plugins.py` (existing, including its `999.0.0` mutation) | exit 0 |
| T5 | `tests/test_release_docs.py`, `tests/test_release_preparation.py` | exit 0 (links in the changed notes resolve; workflow shape untouched) |
| T6 | the 14 files of §13 and `tests/test_rf1_pin_harness.py` | exit 0 after M5 |
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
- V2: `uv run pytest -q tests/test_release_version.py tests/test_marketplace_plugins.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_induced_provenance.py tests/test_fidelity_payload.py --tb=short` plus the E1 list. `tests/test_public_distribution.py` is **not run in RR1**: its cases need the `distribution` or `evidence` lane, which `project.md` forbids bringing into an ordinary gate, and the owner ruled the opt-in lanes excluded (§7, D6). M4's four literals are checked here by `uv run ruff check` and by the RR1-C3 grep (no `0.1.0` literal left in the file); the file's cases run at RR2, where RL-D8 selects the one acceptance file and lane.
- V3: `~/close-shards/close-shards.sh <run> <sha>` on beast-3 (present on 2026-11-07; arguments unresolved until read at the time).
- V4: `uv run ruff check`.
- V5: `python3 scripts/components_index.py changed --base main --strict`.
- V6: `git diff --stat origin/main -- .github` is empty.

## 12. E1 results (2026-11-07, appended; the experiment is the one recorded in §6)

Retained in [evidence/e1](../evidence/e1/README.md). Appended after the plan gate,
before any code.

**Measured.** Base `12daa5b7`: 17,819 passed, 0 failed, 2 errors (the known
`tests/test_public_optional.py` pair). The same tree with exactly M1 to M3: 17,772
passed, **47 failed**, the same 2 errors. Every failure is new at the bump. About
11 minutes per run on beast-3 (six shards, the longest shard 11:05).

**The 47, by file** (the failing node ids are in `failed-bumped.txt`):

| File | Failures | What moves |
|---|---|---|
| `tests/test_rf1_semantic_pins.py` | 24 | extract and synth outputs compared byte for byte with the RF1 goldens (`tests/support/rf1_pins.py:166`, "RF1 pin changed"); the goldens record `"gnd_version": "0.1.0"` |
| `tests/test_public_extract_controls.py` | 5 | pre-phase extract bundles, legacy codegen tree and set-family fidelity bytes |
| `tests/test_object_type_description.py` | 4 | digests of outputs compared with the base commit |
| `tests/test_public_coverage_goldens.py` | 3 | `gnd coverage` payload goldens |
| `tests/test_public_measurement_publication.py` | 2 | committed measurement payloads (`gnd_version` at byte 4673) |
| `tests/test_public_book_runtime.py`, `tests/test_public_book_skills.py` | 1 + 1 | the live conformance payload and walkthrough citations (`'0.2.0' == '0.1.0'`) |
| `tests/test_tp2_shared_fact_types.py`, `tests/test_rf2_pre_move_pins.py`, `tests/test_public_measure_corpus.py`, `tests/test_public_legacy_codegen_pins.py`, `tests/test_public_expense_current.py`, `tests/test_ik6_walk.py`, `tests/test_fidelity_stub_gate.py` | 1 each | pinned output bytes or digests of one command's output |

The cause is one: `resolve_version()` is written into the output of `extract`,
`synth`, `measure`, `fidelity`, `coverage`, `codegen` and the conformance payload,
and 32 committed fixture files plus several recorded digests hold the old string.
This is a finding about the spec, not a defect: M1 to M3 alone leave the default
lane red, so M5 is real work.

**Two further findings.**

1. `uv lock` (not `--check`) also removed an unrelated `zensical` wheel line
   (`manylinux2014_armv7l`) from `uv.lock`. M3 is therefore a one-line edit of the
   `get-nick-done` entry, verified by `uv lock --check`, not a regeneration.
2. The inventory (57 files at the base) classifies as: **version sites** (M1 to M3:
   `pyproject.toml`, three manifests); **stale on publication** (`README.md`;
   `docs/installation.md`, `docs/index.md`, `docs/marketplace-plugins.md`;
   `docs/pyrel-apps.md`, three tutorials and three how-to pages; `docs/compatibility.md`;
   `docs/release-notes.md`) handled by M6 to M9 and RR3's patch; **tests that
   hold the literal** (`tests/test_public_distribution.py` four sites, M4;
   `tests/test_induced_provenance.py` and `tests/test_fidelity_payload.py`: their
   `0.1.0` is a fixture's own value, not the live one, and neither failed at the
   bump, so they stay); **committed fixtures that record `gnd_version`** (32 files,
   the 47 failures' source, D2); **historical** (`docs/development/candidate.md`,
   describing the 0.1.0 candidate); **unrelated**: `src/gnd/codegen/emit.py:818`
   (the version a generated project gets), `tutorials/runtimes/uv.lock` and
   `src/gnd/examples/release_governance/runtime-environment/uv.lock` (a third-party
   `gravis 0.1.0`), and a recorded agent stdout under `src/gnd/examples/expense`.

**What this changes for D2.** Method (c) (fix the version in the test
environment) is not a small edit: `resolve_version` is imported by name into a
dozen modules (`from gnd import resolve_version`), so a patch must reach every
importer or add a test-only override of the single home, which rule 2 of the plan
forbids as an addition. Methods (a) and (b) remain. The 47 split into two
mechanisms, which may take different methods:

- *Comparison against a frozen golden*: the 24 `test_rf1_semantic_pins.py`
  failures go through one helper (`tests/support/rf1_pins.py:166`), so normalizing
  the version there (a) is one edit, keeps the retained bytes, and stops pinning
  the version. Whether the other pin-style failures (`test_object_type_description.py`,
  `test_rf2_pre_move_pins.py`, `test_tp2_shared_fact_types.py`) share a helper was
  not checked; `test_object_type_description.py` does not import `rf1_pins`, so
  each needs its own look before D2 is ruled.
- *Committed outputs of a command that must reproduce byte for byte* (coverage,
  measurement, roundtrip artifacts, legacy codegen pins, expense current): the
  recorded bytes are the claim, so regenerating them (b) moves every digest
  recorded downstream; normalizing (a) weakens a claim that this release is
  exactly what the bytes document.

**Recommendation as written at E1 (the owner has since ruled it as recommended, §7 D2 and D6; §13 holds the classification the ruling required):** (a) in the one RF1 helper, (b) for the
committed outputs whose purpose is that they equal the current command's output
(listing each moved digest in the spec before code, as plan rule 6 requires), and
no (c). The opt-in lanes (`evidence`, `census`) are not measured, and the owner
ruled them excluded.

## 13. Classification of the 47 and the moved digests (2026-11-07, appended before any code)

**How this was measured.** The M5 edit was applied to a scratch copy of main
`12daa5b7` with M1 to M3 (never to this repository). Each failing test was
reproduced there first, then fixed by the method below, then the full default
lane ran on beast-3 over the result (§13.4). Retained in
[evidence/e1](../evidence/e1/README.md): [moved-digests.md](../evidence/e1/moved-digests.md)
(every changed file and every recorded digest, old and new),
[m5-text-edits.diff.txt](../evidence/e1/m5-text-edits.diff.txt) (the edits to text
files; the seven gzip containers are listed by digest, not diffed) and
[gz-archives-naming-0.1.0.txt](../evidence/e1/gz-archives-naming-0.1.0.txt).

**The rule used for D2** (the owner's, §7): (a) when the test compares against a
frozen golden whose subject is not the version, and a placeholder on both sides
makes the comparison blind to the version without touching retained bytes;
(b) when the test's purpose is to equal the current command's output, or when
the pinned value is a digest of bytes that carry the version (a placeholder
cannot reach into a digest, and a digest of a file that holds a digest cascades).
No (c).

### 13.1 Per-file classification

| Test file (failures) | What it compares | Method | What moves |
|---|---|---|---|
| `test_rf1_semantic_pins.py::test_extract` (16) | extract output text against 16 `sem-extract` goldens | **(a)** | `assert_golden` in `tests/support/rf1_pins.py` compares with every `gnd_version` value replaced by a placeholder on both sides (about 8 lines, M5a). The 16 goldens keep `0.1.0` |
| `test_rf1_semantic_pins.py::test_synth` (8) | the sha256 of every file a synth run writes, against 8 `sem-synth` goldens | **(b)**, not (a) | A placeholder cannot reach a digest: files the synth run writes (`*.meta.json`) embed the version. 8 goldens re-recorded, plus their 8 lines in `tests/fixtures/rf1-pins/goldens.sha256` and the manifest's pinned digest in `test_rf1_pin_harness.py` (a cascade E1 could not see: that test passes at the bump and fails after re-recording) |
| `test_tp2_shared_fact_types.py` (1) | runs `test_rf1_semantic_pins.py` in a subprocess | follows the two rows above | nothing of its own |
| `test_object_type_description.py` (4) | rows 4 and 5 of `ik1-baseline.json`: the sha256 of `.gnd-codegen.json` and of the conformance payload, per model | **(b)** | 8 recorded digests. The test already replaces `gnd_version` in row 5 and still fails, because both files carry the sha256 of `artifacts.json`, which embeds the version, so (a) cannot reach it |
| `test_rf2_pre_move_pins.py::test_measure_output_bytes` (1) | sha256 and size of a `gnd measure` output | **(b)** through the existing successor file | `measure-successor.json`: `after.sha256` moves, the size does not (`0.1.0` and `0.2.0` have the same length), and the `reason` gains one sentence. The `before` pin stays |
| `test_ik6_walk.py::test_t2` (1) | sha256 of four files the tutorial walk writes | **(b)** | 4 digests in `ik6-walk/goldens.json` (`measure.json`, `discovered.json`, `discover-report.json`, `discovered.preview.json`; the E1 failure message showed three of them) |
| `test_fidelity_stub_gate.py` (1) | a committed `setfam.artifacts.json` against a fresh `gnd extract` | **(b)** | that one file, `tests/fixtures/roundtrip/artifacts/setfam.artifacts.json`; its test message names the regeneration |
| `test_public_extract_controls.py` (5) | extract, codegen and fidelity outputs against an answer key bound to base commit `5c0d7a8` | **(b)** | the key inside `public-extract-controls/workspace.json.gz`: 6 digests (two `artifacts.json`, the legacy `.gnd-codegen.json` and its `artifacts.json` copy, two fidelity outputs). The stdout digests do not move (stdout carries no version) |
| `test_public_coverage_goldens.py` (3) | `gnd coverage` payload bytes | **(b)** | 3 `expected.payload.json` rows inside `public-coverage-goldens/corpus.json.gz`; sizes unchanged |
| `test_public_measurement_publication.py` (2) | `gnd measure` over a committed corpus against 2 committed payloads | **(b)** | the two payload files, one line each |
| `test_public_measure_corpus.py` (1) | a relocated corpus against a committed payload | **(b)** | one member of `public-measure-corpus/workspace.json.gz` |
| `test_public_legacy_codegen_pins.py` (1) | codegen output against the "pre-v5" answer tree | **(b)** | two documents inside `public-legacy-codegen/closure.json.gz` (`.gnd-codegen.json` and `artifacts/legacy-derived.artifacts.json`), plus the container and the inner digest pinned in the test |
| `test_public_book_runtime.py` (1), `test_public_book_skills.py` (1) | codegen and conformance output of the `bookrec` example | **(b)** | five members of `public-book-runtime/workspace.json.gz` (the project's `.gnd-codegen.json` and `artifacts.json`, the conformance evidence, and the two EXP-007 candidate copies), the sha256 citation of that evidence in `WALKTHROUGH.md` inside `public-book-skills/workspace.json.gz`, and both containers' pinned digests |
| `test_public_expense_current.py` (1) | live conformance payload against the committed one | **(b)** | one member, `conformance/post-conversion.json`, `gnd_version` only; the project is not regenerated. `baseline.json` and `post-evolution.json` are pinned to commit `9c7a464` and keep `0.1.0` |

(a) therefore covers **16 of the 47**, not the 24 the E1 table read as one
mechanism; the other 31 are (b). Every other row of the table is a command output
whose purpose is to equal the current output, or a digest over such bytes.

### 13.2 What changed in the picture E1 gave

1. **E1's inventory missed version strings inside gzip archives.** `git grep` does not
   read them. 12 tracked archives under `tests/fixtures` hold `0.1.0`
   ([the list](../evidence/e1/gz-archives-naming-0.1.0.txt)): 6 moved
   (`public-book-runtime`, `public-coverage-goldens`, `public-expense-current`,
   `public-extract-controls`, `public-legacy-codegen`, `public-measure-corpus`);
   6 stay (`public-binding-graphs`, `public-extract-boundary`,
   `public-fidelity-scope`, `public-legacy-readers`, `public-redaction-reports`,
   `public-version-graph`), whose `0.1.0` is a recorded fixture value that no live
   output is compared with (none of their tests failed at the bump). A seventh
   container, `public-book-skills`, holds no version but cites the digest of a
   moved file. The 32-file count in the owner's question named text fixtures only.
2. **Every difference is the version or a digest that covers it.** For every
   changed output the new bytes equal the old bytes once the `gnd_version` value
   and 64-hex digests are masked; the one exception is the sentence added to the
   RF2 `reason` on purpose. The labels "pre-v5 bytes", "pre-phase controls" and
   "base commit" on the re-recorded pins therefore still hold in substance, and
   the spec records here that they now carry `0.2.0`.
3. **One more cascade appeared only by running the lane on the changed tree**
   (`test_rf1_pin_harness.py::test_golden_manifest`). Others may exist; the closing
   full-lane run at the RR1 tree (V3) is the check, and RR1's record reports any
   further site it finds.

### 13.3 Moved digests

Everything is in [moved-digests.md](../evidence/e1/moved-digests.md): 31 changed files (7
gzip containers, 24 others), each with its old and new sha256, and below them
the digests and members recorded inside those files. The size of M5: 31 files,
about 450 lines changed in text files, one 8-line helper change, no change under
`src/`. The value `0.2.0` is the only input; a later change of version moves
these digests again, which is the cost of method (b) the owner accepted.

### 13.4 The lane at the changed tree

The scratch tree is main `12daa5b7` plus M1 to M3 plus the M5 edit above. The same
six-shard default lane, on the same machine and with the same script as E1
([lane-m5-summary.txt](../evidence/e1/lane-m5-summary.txt)): **17,819 passed, 0 failed,
2 errors**, the same `tests/test_public_optional.py` pair the base has. The base
passed 17,819 and the bumped tree without M5 passed 17,772 with 47 failures, so
M5 restores all 47 and no test was dropped. An earlier scratch run without the
repository's git history showed a spurious failure in `test_ik6_skill_census.py`
(the scratch copy had no history); the run recorded here used a clone with the
full history. The one cascade that run revealed (`test_rf1_pin_harness.py`) is
§13.1's second row.

Limits, stated first. This is the **default lane** only (D6: `evidence`, `census`
and `distribution` are excluded, and any version-bearing site only they read
stays unmeasured). It is a scratch tree, not the RR1 tree: RR1's own V3 repeats the
run at its closing tree, after the rebase of V1, and reports any site this run
did not have. The scratch edit was made by a script that re-recorded each pin from
the command's own output; the implementation may differ in form, not in the
digests listed.
