# Phase RR2: candidate build and installed acceptance

## 1. Status

**Draft r1, awaiting owner review (2026-11-08).** Nothing in this spec is
approved. No test, build or docs edit of RR2 has been made; the only commands
run were read-only observations and scratch measurements (§3.1). Approving this
spec is also the explicit lane selection of RL-D8 (D4). `auto=false`.

## 2. Provenance

- Plan r2 (approved 2026-11-07, [001-plan.md](../001-plan.md)):
  [rule-check-release-plan.md](rule-check-release-plan.md) §2 "What carries
  means", §4 RR2-C0 to RR2-C7, completion predicates 3 and 4, conflicts C1 and
  C2, risks R2, R4, R5 and R8, rulings RL-D2, RL-D5, RL-D6, RL-D7 and RL-D8.
- The RR1 record [002-phase-RR1.md](../002-phase-RR1.md), its open questions:
  T2 (the distribution file) runs here; the notes are reconciled with FU3 and
  any other change before the build.
- RL-D2's condition holds: rule-check-followups FU2 merged as `1e63aeb5` and
  FU3 as `df5753bf` (PR 128, 2026-11-08). The branch merged main at `df5753bf`
  in commit `0b9f2f17`. FU4 has started; RL-D2 says FU4 and FU5 do not gate.
- Expected values come from `docs/reference/rule-check-report.md` and the
  how-to `docs/how-to/adopt-rules-with-a-baseline.md` (RC6, gated by its
  `gnd-run` replays), never from the output being tested. 0.1.0 values are
  scratch measurements of the PyPI-served 0.1.0 (§3.1), marked **O**.
- No review has read these bytes.

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| RR2-C0 | before any build, the notes of every change in the candidate are in the 0.2.0 section; no `Unreleased:` section for candidate work; PyPI availability rechecked at the freeze | M1, V1 |
| RR2-C1 | wheel, sdist and comparison wheel built by `release.yml`'s two `uv build` commands from `git archive` of the candidate commit; SHA256SUMS verifies; tool versions recorded | M3 (B1), V2 |
| RR2-C2 | a second independent build compared by hash; a difference is explained, not blocking (RL-D7) | M3 (B2), V3 |
| RR2-C3 | `GND_CANDIDATE_DIR=… uv run pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short`, verbatim summary | V4 |
| RR2-C4 | the five carries probes of plan §2 from the installed wheel, each field with its own expected value, each probe with an availability control on 0.1.0 and a candidate behavior mutant, inside `tests/test_release_acceptance.py` | M2, T1, T2 |
| RR2-C5 | `uvx --from <wheel>` works; limits recorded | V5 |
| RR2-C6 | observed profile (OS, Python, uv) recorded; no other profile claimed (RL-D6) | V2, V4 |
| RR2-C7 | the run does not read the source checkout (macOS sandbox) | existing `test_installed_optional_refusals`; T1 and T2 run under the same `prefix` |
| RR1 open question / RL-D8 | `tests/test_public_distribution.py` (the four `VERSION` sites RR1 changed) runs here | D4, V6 |
| predicate 3 | candidate carries every item of issue 118; the same probes fail or are absent on 0.1.0 | T1, T2 |
| predicate 4 | release acceptance passes over the retained files, verbatim | V4 |
| predicate 6 | nothing enables publication | V7 |
| plan C1 / RL-D8 | only the selected files run with `-o addopts=''` | D4 |
| plan C2 | availability at the freeze | V1 |
| plan R2 | sibling `Unreleased:` sections | M1, V1 |
| plan R4 / O7 | candidate evidence is not the published file's evidence | §9, record |
| plan R5 | probes cannot tell releases apart | T2 |
| plan R8 | sandboxed run may not run here | D5 |
| O22 / AGENTS.md | component index | V8 |

### 3.1 Observations for this draft (read-only or scratch, 2026-11-08)

- **O-a.** PyPI JSON (`2026-11-08T04:32Z`): releases `['0.1.0']` only. 0.1.0
  wheel sha256 `cc91decaf86d081fa023179792646900ac8f23c3cd1758e339006a4dab1ac183`,
  sdist `f47abb4505969ab69a9a7cdf5da9e071ff511b1b50f1b728154699f55c3a8f86`. 0.2.0 is free.
- **O-b.** Repository: environments `['github-pages']`; no `release.yml` run;
  merge commit, squash and rebase merges are all allowed (`gh api`).
- **O-c.** `uv build --sdist` over `git archive HEAD` holds only `src/`,
  `pyproject.toml`, `LICENSE`, `NOTICE` and `PKG-INFO` (1434 `src` members,
  2,220,814 bytes). So the packaged bytes depend on those paths only, not on
  tests, docs or planning.
- **O-d.** Tools: this Mac has uv 0.10.10 (the workflow's pin), uv-managed
  Python 3.14.3, macOS 26.6.2 arm64, `/usr/bin/sandbox-exec`. beast-3 has
  macOS 27.0.1 arm64, uv 0.13.7 and `sandbox-exec`.
- **O-e.** On the shipped example `src/gnd/examples/rule_check` (copied to
  scratch), 0.1.0 from the index (`uvx --from get-nick-done==0.1.0`) and the
  current tree (`uv run gnd`, version 0.2.0):

| Run | 0.1.0 | current tree |
|---|---|---|
| `check model head --rule-ids --format json` | exit 64, `unrecognized arguments: --rule-ids` | exit 1, `schema_version` 15 |
| same with `--baseline base` / `--allow-vacuous` | exit 64, `unrecognized arguments` | exit 1 / exit 1 |
| plain `check model head` | exit 3: `$.constraints[0]` `jsonschema:unevaluatedProperties` "('remedy' was unexpected)" (four such issues) | exit 1, `schema_version` 7 |
| plain check, `remedy` lines removed, head population | exit 3: `$.population` "('producer' was unexpected)", `$.population.source` "'tool-output' is not one of ['agent-output', 'synthetic', 'fixture']" | exit 1, version 7, acyclic row `[['api','auth','api']]` |
| plain check, `remedy` removed, `source: fixture` without `producer` | exit 1, version 7 | exit 1, version 7; `counts` and every verdict's (outcome, offending facts) equal 0.1.0's |
| `source: fixture` with `producer` (candidate only) | — | exit 3, `$.population.source` `jsonschema:const` "'tool-output' was expected" |
| `no_import_loops` without `id` and `remedy`, `--rule-ids` | — | exit 1; `address` `fact_types[component_imports_component].constraints[0]`, `positional`, `remedy` null |
| `fixed` against `base`, `--baseline` | — | exit 2; with `--allow-vacuous` exit 0, `allow_vacuous` true, `outcome` `accepted`, `assurance.assurance_level` `none` |
| `head` against `head` as base | — | exit 2 |

  One run of `--baseline` with `--format json` in the first sweep exited 64;
  three reruns of the same command exited 1. It was not reproduced and has no
  explanation yet; T1 asserts the exit, so a recurrence fails the gate.

## 4. The standing rules, bound to this phase

| Rule | Binding here |
|---|---|
| plan 0.1 prepare, never publish | RR2 builds and installs locally only: no upload, no tag, no GitHub release, no workflow dispatch, no environment. V7 diffs `.github/` against the base (empty) and repeats O-a and O-b |
| plan 0.2 one home for the version | the probes read the installed version from `gnd --version` and compare it with `pyproject.toml` at the candidate commit; no new version literal (the 0.1.0 wheel hash in M2 is historical data, like `RELEASED`) |
| plan 0.3 no instruction names an unpublished version | RR2 edits no install text; M1 edits only the notes' 0.2.0 section. `tests/test_release_version.py` stays green (V1) |
| plan 0.4 evidence belongs to exact bytes | every result names the candidate commit `C` and the SHA256SUMS lines; a rebuild is a new candidate and repeats V2 to V6 (D1) |
| plan 0.5 carrying is shown by running | T1 runs `gnd` from the installed wheel; T2 runs the 0.1.0 wheel |
| plan 0.6 measure | O-c and O-e were measured before this design; V3 measures reproducibility |
| plan 0.7 frozen surfaces | `release.yml`, `tests/test_release_preparation.py` and the dependency freeze are unchanged; `tests/test_release_acceptance.py` gains tests and changes no existing line except imports |
| plan 0.8 stop rule | the plan's 60 test lines become about 150 (§10); the owner rules at this gate, and RR2 pauses past 225 |
| project.md 1 totality | inapplicable: the new tests read files this test writes and JSON `gnd` prints; a parse failure fails the test |
| project.md 2 input cap | inapplicable: no work proportional to untrusted input |
| project.md 3 validation order | inapplicable: no new boundary with two rejecting checks |
| project.md 4 one walk | inapplicable: no policy over element kinds |
| project.md 5 one home | the procedure stays in `docs/releasing.md` and `release.yml`; RR2 cites them and copies neither. Expected values cite the reference page and the how-to |
| project.md 6 measurement | O-c, O-e; V3 |

## 5. Goal

At the candidate commit `C`: the 0.2.0 notes section names every change in `C`
and `docs/release-notes.md` has no `## Unreleased` heading (V1 prints 0). Two
builds of `git archive C` produce wheel, sdist and comparison wheel whose
`SHA256SUMS` check exits 0, and their hashes are compared (V3). Over the
retained candidate, `uv run pytest -q -o addopts='' tests/test_release_acceptance.py
--tb=short` exits 0 with the new carries tests T1 and T2 inside it.
`tests/test_public_distribution.py` under the same override exits 0.
`uvx --from <wheel> gnd --version` prints `gnd 0.2.0` and exits 0. Nothing is
published.

## 6. Design

### Reuse table

| Capability | Searches | Found | Decision |
|---|---|---|---|
| install a retained wheel outside the checkout, sandboxed | `components_index.py search installed wheel candidate acceptance` | `tests/test_release_acceptance.py` fixtures `candidate`, `installed`, helper `run` | reuse: T1 takes the `installed` fixture |
| inputs that exercise every issue-118 item | `components_index.py search rule check example baseline`; `git grep rule_check docs` | the packaged example `gnd/examples/rule_check` (model with four `id`+`remedy` rules, `base`, `head`, `fixed` populations, `source: tool-output` + `producer`) and the how-to that replays it | reuse: copy it from the installed wheel, as the how-to does |
| fetch a published file and check its hash | `git grep pypi.org/pypi` | `release.yml`'s served-file comparison (inline Python in the workflow) | adapt the method, not the code (the workflow is frozen and not importable) |
| build steps | — | `release.yml` `prepare` job | reuse its two commands verbatim (M3) |

### Modules

**M1. `docs/release-notes.md`, 0.2.0 section (about 8 lines).** RR2-C0. The
changes merged into the branch since the notes were written are FU2
(`1e63aeb5`) and FU3 (`df5753bf`). FU2 changed library behavior, so it gets one
bullet in the rule-check block: "**Population headers stay valid when
copied**: `Population.model_copy(update=…)` re-checks that a `producer` comes
only with `source: tool-output` and is a 1 to 200 character string, and a
population combined with its reference populations keeps its own `label`
(issues 115, 116)." FU3 added tests only and changed no runtime byte (its
record: "test-only"), so it gets no entry. A later change on main
that is in `C` gets the same treatment before `C` is fixed; one that lands
after `C` keeps its own `Unreleased:` section above 0.2.0 (plan R2).

**M2. `tests/test_release_acceptance.py` (about 150 added lines).** Two tests,
four helpers, one fixture, one constant. Exact surface:

```python
# The wheel PyPI serves for the published 0.1.0 (O-a), historical data like
# RELEASED in tests/test_release_version.py: the negative control installs it.
PUBLISHED_WHEEL_SHA256 = {'0.1.0': 'cc91decaf86d081fa023179792646900ac8f23c3cd1758e339006a4dab1ac183'}

def copy_example(python, prefix, env, cwd, dest: Path) -> Path
    """Copy gnd/examples/rule_check out of the installed wheel into dest (sandboxed)."""
def gnd_json(python, prefix, env, cwd, *args, expected: int) -> dict
    """Run `python -I -m gnd check *args --format json`, assert the exit, parse stdout."""
def edit(path: Path, old: str, new: str) -> None
    """Replace exactly one occurrence of old, or fail (mutants never miss their target)."""
def by_address(report: dict) -> dict[str, dict]

@pytest.fixture(scope='module')
def published_0_1_0(tmp_path_factory) -> tuple[Path, Path, dict]
    """Fetch the 0.1.0 wheel URL from https://pypi.org/pypi/get-nick-done/0.1.0/json,
    download it, require sha256 == PUBLISHED_WHEEL_SHA256['0.1.0'], install it in a
    fresh venv outside the checkout; return (outside, python, env)."""

def test_installed_rule_check_carries(installed)          # T1, both wheels
def test_published_0_1_0_lacks_rule_check(installed, published_0_1_0)  # T2
```

Both tests run every `gnd` call under the `installed` fixture's `prefix` (the
macOS sandbox that denies reads of the source checkout's parent) with
`cwd=outside`, so RR2-C7 covers them as it covers the existing tests.

**Expected values, T1 (candidate).** Inputs: the example copied from the
installed wheel. Sources: reference page lines (R:n) and how-to lines (H:n).

| Probe | Run | Field | Expected | Source |
|---|---|---|---|---|
| version | `python -I -m gnd --version` | stdout | `gnd ` + `[project] version` of the checkout's `pyproject.toml` | plan rule 2 |
| P1 `--rule-ids` | `check model head --rule-ids` | exit | 1 | H:83 |
| | | `schema_version` | 15 | R:1 |
| | | `address` of the four rules | `constraint:no_import_loops`, `constraint:no_legacy_components`, `constraint:every_component_has_an_owner`, `constraint:no_draft_releases` | R:43, H:89-97 |
| | | `addressing` | `declared-id` for all four | R:44 |
| | | `remedy` of `no_import_loops` | `Break the loop: move the shared code into a lower component both can import.` | H:91 |
| | | `novelty`, `row_novelty`, `baseline` | `null`, `null`, `null` | R:46-47, R:66 |
| P1 mutant | model with `no_import_loops`'s `id` and `remedy` lines removed (`edit`) | that verdict's `address`, `addressing`, `remedy` | `fact_types[component_imports_component].constraints[0]`, `positional`, `null` | R:43-45 |
| P2 `--baseline` | `check model head --baseline base` | exit | 1 | H:121 |
| | | `baseline` block | `new` 2, `standing` 4, `resolved` 2, `positional_keyed` 0, `undecided` 0, `population_sha256` `d816aea7caf713a67837f1361c4a2676a91a5aac82ba7167bf1ef88106fd5fcd` | H:165-171 |
| | | `novelty` | `no_import_loops` `new`; `no_legacy_components` `standing`; `every_component_has_an_owner` `standing` | H:128-135 |
| | | `row_novelty` of `no_import_loops` by row | `[api,auth]` and `[auth,api]` `standing`; `[search,util]` and `[util,search]` `new` | H:173-176 |
| P2 mutant | `--baseline head` (the head as its own base) | exit; `baseline.new`; every `novelty` that is not `null` | 2; 0; `standing` | R:46, R:92-94 |
| P3 `--allow-vacuous` | `check model fixed --baseline base` | exit | 2 | H:188 |
| | same with `--allow-vacuous` | exit; `allow_vacuous`; `assurance.assurance_level` | 0; `true`; `none` | H:223, R:67, R:97-101 |
| P4 acyclic extent | `check model head --rule-ids` | `no_import_loops` `offending_facts` as a set | `{[api,auth], [auth,api], [search,util], [util,search]}` | H:173-176, R:52-56 |
| | | its `message` ends | `2 strongly connected groups (sizes 2, 2) hold 4 edges.` | R:56, H:90 |
| P4 control (same rule, no flag) | `check model head` (version 7) | that verdict's `offending_facts` | one cycle, `[[api, auth, api]]` (O-e) | R:52-54 "instead of version 7's single cycle" |
| P4 control (disjoint loop) | `check model fixed --rule-ids` | rows; message | `{[api,auth], [auth,api]}`; ends `1 strongly connected group (size 2) holds 2 edges.` The two rows equal their values under `head`, which adds the separate `search`/`util` loop | R:56-58, H:195 |
| P5 `tool-output` + `producer` | plain `check model head` | exit; `issues` | 1; `[]` | population-format.md:45-46 |
| P5 mutant | `head` with `source: tool-output` changed to `source: fixture`, `producer` kept | exit; issue path and `rule_id` | 3; `$.population.source`, `jsonschema:const` | population-format.md:46 ("Any other source with a `producer` is refused at load"); O-e |

**Expected values, T2 (0.1.0 controls, measured O-e).** The inputs are the
candidate's example, copied by the candidate's interpreter into T2's own
directory.

| Probe | 0.1.0 run | Expected | What it shows |
|---|---|---|---|
| P1, P2, P3 availability | `check model head` with `--rule-ids`, with `--baseline base`, with `--allow-vacuous` | exit 64, stderr names the flag in `unrecognized arguments` | the flags are new (and nothing more) |
| P2 `remedy` availability | plain `check model head` | exit 3; an issue at `$.constraints[0]` with `rule_id` `jsonschema:unevaluatedProperties` naming `remedy` | the field is new |
| P5 availability | plain check, model without `remedy` lines, `head` population | exit 3; issues at `$.population` (naming `producer`) and `$.population.source` | `tool-output` and `producer` are new |
| comparable default | plain check, model without `remedy`, `source: fixture`, no `producer` | 0.1.0 and candidate both exit 1 with `schema_version` 7, equal `counts`, and equal (outcome, `offending_facts`) per verdict, including the acyclic row `[[api, auth, api]]` | without the flags nothing changed (R:6-7) |

The P4 behavior has no 0.1.0 control that reaches it, because 0.1.0 cannot run
version 15; its controls are the candidate's own version-7 run and the
disjoint-loop run in T1, as plan §2 allows ("a mutant of the candidate that
reaches the same code").

**M3. The build (no tracked script; commands recorded verbatim in the
record).** In a fresh directory outside every checkout:

```sh
git -C <repo> archive C | tar -x -C src          # B1 here, B2 on beast-3 (D5)
cd src && uv build --out-dir ../candidate/release
mkdir -p ../candidate/source && tar -xzf ../candidate/release/*.tar.gz -C ../candidate/source
uv build --wheel ../candidate/source/* --out-dir "$PWD/../candidate/comparison"
rm -f ../candidate/release/.gitignore ../candidate/comparison/.gitignore
echo C > ../candidate/SOURCE_COMMIT; python --version > ../candidate/BUILD_PROFILE; uv --version >> ../candidate/BUILD_PROFILE
cd ../candidate && shasum -a 256 release/* comparison/* > SHA256SUMS && shasum -a 256 -c SHA256SUMS
```

These are `release.yml`'s `prepare` steps with three differences, stated in the
record: the source is `git archive C`, not a checkout (O-c shows the packaged
inputs are tracked files only); `SOURCE_COMMIT` is written, not read from
`git rev-parse`; `shasum -a 256` replaces `sha256sum` (macOS), with the same
output format. B1 is the candidate; B2 is the reproducibility comparison only.

### Normative order

1. M1 and M2 are committed; the focused default gate passes; the review runs and its fixes are committed. The last of these commits is `C`.
2. V1 at `C`: no `## Unreleased` heading; PyPI still lists only 0.1.0.
3. B1 and B2 build `C` (V2, V3).
4. V4 runs the acceptance over B1's files from a clean worktree whose `HEAD` is `C` (the file archives `HEAD`). Then V5 and V6.
5. The record commit follows `C` and changes no packaged path (`src/`, `pyproject.toml`, `LICENSE`, `NOTICE`); V8 checks that.

A change to a packaged path after `C` makes a new candidate and repeats steps 2 to 4 (plan rule 4).

## 7. Decisions

| ID | Question | Readings | Cost of each |
|---|---|---|---|
| D1 | Which commit is the candidate, given RR1 and RR2 are on unmerged PR 125? | (a) **`C` on the PR 125 branch.** The owner merges PR 125 with a merge commit, so `C` becomes an ancestor of main; after the merge a read-only `git merge-base --is-ancestor C origin/main` is recorded (RR3). (b) The owner merges PR 125 after M1 and M2; RR2 builds from that main merge commit and records in a new PR | (a): one merge; a squash or rebase merge would leave `C` off main, and the record would then name a commit main lacks (same packaged bytes only if `src/`, `pyproject.toml`, `LICENSE`, `NOTICE` match, O-c). (b): matches RR2-C1's words "named main commit" exactly; adds an owner merge mid-phase and a second PR. If FU4 merges before PR 125, the merge commit contains FU4, so its notes must be folded in first: another commit, review and wait. Neither changes an exit code |
| D2 | Where are the retained candidate files kept? | (a) **Outside git**: B1's directory at `~/gnd-release/0.2.0/<C short>/` on this Mac, with a copy on beast-3; the record commits `SHA256SUMS`, `SOURCE_COMMIT` and `BUILD_PROFILE`. (b) Commit the wheel, sdist and comparison wheel (about 6.5 MB) under `evidence/RR2/` | (a) follows 0.1.0's practice (`candidate/ci-…` kept outside history, `public-launch/004-phase-3.md:149`); if both copies are lost, a later upload needs a rebuild, a new candidate under rule 4. (b) keeps the exact files, but adds them to the public history permanently, and a token upload would take files from a git checkout |
| D3 | Where does the 0.1.0 control run? | (a) **Inside `tests/test_release_acceptance.py`** (T2): the wheel is fetched from PyPI and checked against `PUBLISHED_WHEEL_SHA256`, so every later prepare run repeats it. (b) A one-off script whose output is recorded | (a) adds one hash literal (historical data) and a fetch from `files.pythonhosted.org`; the file already needs the index for dependencies. If PyPI ever removed 0.1.0, T2 would fail with a clear message. (b) leaves later prepare runs without the control, so plan R5 holds only once |
| D4 | RL-D8: which invocations may override `addopts`? | **Exactly two**, selected by approving this spec: V4, `tests/test_release_acceptance.py` (RR2-C3), and V6, `tests/test_public_distribution.py` (RR1's T2: the four sites that now read `VERSION` from `pyproject.toml`). Or: only V4, and the distribution file stays unrun | Two: about 3 minutes more, and RR1's T2 is discharged. One: RR1-C3's four rewritten assertions are never executed before release, and the record says so |
| D5 | Hosts and tools | (a) **B1 on this Mac** (uv 0.10.10, the workflow's pin). **B2 and V4 on beast-3**, with uv 0.10.10 run as `uvx --from uv==0.10.10 uv` and placed first on `PATH` for V4, and Python 3.11 (the workflow's) for the test environment. V4 here only if beast-3 is unreachable. (b) Everything on this Mac | (a) gives B2 a different host for reproducibility, and moves the long sandboxed run off a machine whose own sandbox may refuse nested `sandbox-exec` (plan R8). The observed profile is beast-3's: macOS 27.0.1, arm64, Python 3.11, uv 0.10.10. (b) uses one profile, and V4 may fail for a reason unrelated to the candidate |

## 8. Tests

| ID | File, case | Expected |
|---|---|---|
| T1 | `tests/test_release_acceptance.py::test_installed_rule_check_carries[release]`, `[comparison]` | passes: every row of the T1 table, including its four mutant or control rows |
| T2 | `tests/test_release_acceptance.py::test_published_0_1_0_lacks_rule_check[release]`, `[comparison]` | passes: every row of the T2 table |
| T3 (red first) | T1 and T2 over a candidate directory assembled from the 0.1.0 wheel and sdist (`release/`, `comparison/`, `SHA256SUMS`) | T1 fails at its first `gnd_json` (exit 64, expected 1); the run is recorded before the real candidate is built, to show T1 can fail |
| T4 | the existing tests of the same file | unchanged and pass (V4) |
| T5 | `tests/test_public_distribution.py` | exit 0 (V6, D4) |
| T6 | `tests/test_release_version.py`, `tests/test_release_docs.py`, `tests/test_release_preparation.py` after M1 | exit 0 (V1) |

Every branch of the T1 and T2 tables has an assertion that can fail it. The
two mutants (P1, P5), the self-baseline (P2) and the disjoint loop (P4) are
the candidate behavior controls; the T2 rows are the availability controls.

## 9. Out of scope for this phase

- Upload, tag, GitHub release, `pypi` environment, publisher registration,
  `release.yml` dispatch (with or without `publish`). The prepare job on
  GitHub for an Ubuntu profile (RL-D6) needs its own request.
- Any profile other than D5's. The index install form (`uvx --from
  get-nick-done==0.2.0`) cannot run before publication.
- Claims about the bytes a later publication uploads (O7, R4): under the
  workflow route they are that run's own build.
- `docs/releasing.md`, the dossier and the post-publication patch (RR3).
- FU4, FU5 and every other milestone's content.

## 10. Size

Estimate at write time: about 150 added test lines (plan: 60; the per-probe
controls that review P5 added after the estimate account for the difference),
about 8 notes lines, about 200 record and evidence lines. The plan's stop rule
(1.5 times) is applied to 150 if the owner accepts it here.

## 11. Approval instrument

This prose. The expected values are tables in §6 with their sources. No
fixture corpus: the inputs are the packaged example, which the how-to already
replays.

## Verification commands

- **V1** (at `C`): `grep -c '^## Unreleased' docs/release-notes.md` prints 0;
  `uv run pytest -q tests/test_release_version.py tests/test_release_docs.py
  tests/test_release_preparation.py --tb=short` exits 0; PyPI JSON lists only
  `0.1.0` (dated).
- **V2**: M3 for B1; `shasum -a 256 -c SHA256SUMS` exits 0; `BUILD_PROFILE`
  verbatim.
- **V3**: M3 for B2 on beast-3; per-file hash comparison with B1 recorded; a
  difference is explained (RL-D7), not blocking.
- **V4**: in a clean worktree at `C` on beast-3, `uv sync --locked --group dev
  --python 3.11`, then `GND_CANDIDATE_DIR=<B1 copy> uv run pytest -q -o
  addopts='' tests/test_release_acceptance.py --tb=short`; summary line
  verbatim, exit 0.
- **V5**: `uvx --from <B1 wheel> gnd --version` prints `gnd 0.2.0`, exit 0.
  Limits: dependencies come from the index; the index form is untried.
- **V6**: same worktree, `uv run pytest -q -o addopts=''
  tests/test_public_distribution.py --tb=short`, exit 0.
- **V7**: `git diff <base> C -- .github/` is empty; O-a and O-b repeated.
- **V8**: `scripts/components_index.py changed --base origin/main` reports 0 to
  fix; `uv run ruff check tests/test_release_acceptance.py`; `git diff --stat C
  <record commit> -- src pyproject.toml LICENSE NOTICE` is empty.
