---
milestone: rule-check-release
station: "phase-RR3"
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-RR3
date: 2026-11-08
gates:
  - command: "T1 at ff189c25, scratch worktree: git apply --check of each patch alone (post-publication, post-publication-tag, post-publication-release-files)"
    exit: 0
    output: "exit 0, exit 0, exit 0"
  - command: "T6, the RR3 tree: uv run pytest -q -o addopts='' tests/test_release_docs.py tests/test_release_preparation.py tests/test_release_version.py"
    exit: 0
    output: "35 passed"
  - command: "T2, all three patches applied, PUBLICATION_DATE replaced by 2026-11-09: uv run pytest -q -o addopts='' tests/test_release_version.py tests/test_release_docs.py tests/test_marketplace_plugins.py"
    exit: 0
    output: "29 passed"
  - command: "T5, sh stale-text-check.sh token, on all three patches with the date filled in"
    exit: 0
    output: "no stale release-state text (16 allowlisted hits, route token, build 7c0f4d0e)"
  - command: "T5 liveness, sh stale-text-check.sh token, on the RR3 tree (expected to fail)"
    exit: 1
    output: "30 stale lines and both missing published-state lines printed"
  - command: "T5 controls (expected to fail): placeholder kept; route workflow 25f58b5e with the 7c0f4d0e support row; notes opening reverted; undated 0.2.0 heading; main patch only"
    exit: 1
    output: "each exit 1, printing the placeholder lines, the support row, the missing opening, the missing heading, and the four tag and release-file lines respectively; the support row reworded for 25f58b5e gives exit 0"
  - command: "T5 usage and search errors (expected to fail): no argument; workflow with a 7-hex commit; run outside any repository"
    exit: 2
    output: "usage, usage, 'search error (128)'"
  - command: "T3, T3b, T4, T7 mutants (expected to fail)"
    exit: 1
    output: "T3: test_notes_and_compatibility_do_not_claim_publication and test_install_pins_name_a_published_version fail; T3b: test_pins_name_the_declared_version_once_released fails; T4: test_no_publication_date_placeholder_once_released fails; T7: test_releasing_procedure_states_both_routes fails"
  - command: "V2: install pins and RELEASED on the RR3 tree"
    exit: 0
    output: "five pins, all get-nick-done==0.1.0; RELEASED = {\"0.1.0\"}"
  - command: "V3 (2026-11-08T06:22:02Z, read-only): git diff 12daa5b7 HEAD -- .github; environments; release.yml runs; GitHub releases; remote tags; PyPI JSON"
    exit: 0
    output: "0 lines; [\"github-pages\"]; 0; [\"v0.1.0\"]; refs/tags/v0.1.0 only; ['0.1.0'] -- each equal to the O3/O5 baseline"
  - command: "V5: python3 scripts/components_index.py changed --base origin/main"
    exit: 0
    output: "14 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
slow_cadence:
  command: "none"
  trigger: "n/a"
  reason: "every RR3 check runs in seconds; the slow acceptance file is RR2's (RL-D8)"
evidence:
  - path: .gnd-planning/milestones/rule-check-release/notes/phase-RR3-spec.md
    sha256: 7760b5f15ee98d22489a9c223432987bad447987ed163049144082f5d6e9bef5
  - path: .gnd-planning/milestones/rule-check-release/notes/phase-RR3-codex-review.md
    sha256: 05a8dfd70b13eea29ea8a55b5d4fa679fe9abba59680fa9caac5944679c3a0a3
  - path: .gnd-planning/milestones/rule-check-release/notes/phase-RR3-codex-review-impl.md
    sha256: ce6f68cb19d92a8a3c5a246c28fc05544c2c3ba17db6018c10f60bd426916427
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR3/dossier.md
    sha256: 64035c5565d1ab0fb483f465626bb168ee14bbcf2fa2df4c6af09771830ce7cc
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR3/post-publication.patch
    sha256: 4f48aa32eb989b54d1ad87bf2fa45a431c15d0969838f05888fcccb94f400a7a
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR3/post-publication-tag.patch
    sha256: 31670a50cc7bf5f225901236fec6d2172170a19fb41766b9aff6f9ee8463f8cb
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR3/post-publication-release-files.patch
    sha256: 8b1f151904f6768556e9071c2f572fc20556c38df61ec43249de7bebedcaaf1b
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR3/stale-text-check.sh
    sha256: bf3d00a9e817cf72751d8532f307d7f5fb8f16f3119eff3b1a24adfea5a3abc6
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR3/checks-runner.sh
    sha256: cfc25ef322e29937399bacecbec55a455eadcbe26c43aa53b81d48f7e3d6f9d4
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR3/checks-T1-T7.txt
    sha256: 9b8c2185a83b588c7a4c51ef2f2f9c441be85a312063bd62100e9ab93ecd13b4
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR3/v3-v5.txt
    sha256: b0cf1836fe2fdfd247db99778ee8580a04d84a8cf785c8c6a1197fd7063059a4
  - path: docs/releasing.md
    sha256: ec5d085c60ec51570c4aa5eb85a7834ee6ef27f51ae1c37b80ec23e133b3f34e
  - path: tests/test_release_docs.py
    sha256: cc372e1051e67b5cb1dc52c65280906251ca8c9e20093551512bea64b8f92a12
---

# Claim

The 0.2.0 publication is handed over and nothing is published.

- **The dossier** ([`evidence/RR3/dossier.md`](evidence/RR3/dossier.md))
  lists:
  - the candidate's identity (RR3-C1): main `7c0f4d0e`, the three files with
    full hashes, the build tools and the retained copies;
  - its results and what was not measured;
  - each owner action with dated evidence that it is still open (RR3-C2).
- **Three post-publication patches** exist as files and are not applied
  (RR3-C3, V2):
  - the main patch, always applied;
  - the tag patch, applied if a `v0.2.0` tag is made;
  - the release-files patch, applied if the GitHub release carries the files.

  Together they cover every hit of the RR3 search. The stale-text check
  accepts the patched tree only with the publication date filled in and the
  support row naming the build that was actually published.
- **`docs/releasing.md`** states both publication routes, each conditional
  (RR3-C4, D1):
  - a token upload of the retained files, as 0.1.0 shipped;
  - `release.yml` with `publish=true`, which builds `main` at dispatch.

  Neither route is configured or invoked. Every procedure requirement of the
  old text is kept; the realpaths and sign-off sentence, dropped in the first
  draft, are restored (J1).
- **The served-file check is cited, not copied** (RR3-C5): the dossier's
  section E and `releasing.md` point to the workflow step "Compare served
  PyPI files and exercise a fresh index install".

## What shipped

- **M3** `docs/releasing.md`, plus `tests/test_release_docs.py::test_releasing_procedure_states_both_routes`
  (T7, red before the edit). Commits `ed8fc100` and `ff189c25` (J1).
- **M2** [`post-publication.patch`](evidence/RR3/post-publication.patch),
  [`post-publication-tag.patch`](evidence/RR3/post-publication-tag.patch),
  [`post-publication-release-files.patch`](evidence/RR3/post-publication-release-files.patch).
  Commits `c84c9a49` and `7f213a11`. The main patch also carries the D2 and D5
  tests in `tests/test_release_version.py`.
- **M4** [`stale-text-check.sh`](evidence/RR3/stale-text-check.sh): the
  allowlisted RR3 search.
  - It takes the route (`token`, or `workflow <8-hex commit>`).
  - It exits 1 on stale text, on a `PUBLICATION_DATE` left in place, or on
    notes without the dated 0.2.0 opening and heading.
  - It exits 2 on usage or search errors, or on an empty search.
- **M1** the dossier (`62ba6fd4`, review fixes in `ff189c25`).
- **Evidence:**
  - [`checks-T1-T7.txt`](evidence/RR3/checks-T1-T7.txt): its last section
    is the gate of record, with full output;
  - [`checks-runner.sh`](evidence/RR3/checks-runner.sh), the script that
    produced it;
  - [`v3-v5.txt`](evidence/RR3/v3-v5.txt).

## Gate output (verbatim)

From the gate-of-record section of `evidence/RR3/checks-T1-T7.txt`:

    ### T5 all three patches, date filled, route token (expect exit 0)
    $ stale-text-check.sh token
    no stale release-state text (16 allowlisted hits, route token, build 7c0f4d0e)
    exit 0

    ### T5 same tree, route workflow with another build (expect exit 1 on the 7c0f4d0e row, J5)
    $ stale-text-check.sh workflow 25f58b5e
    stale release-state text:
    stale: docs/support.md:| macOS 27 arm64, Python 3.11, uv 0.10.10 | Observed in release acceptance of the 0.2.0 candidate built from `7c0f4d0e` |
    exit 1

## Execution findings

- **The first T5 rerun was invalid and is not retained.** The runner stored
  the check command in one zsh variable, which zsh does not word-split, so
  every check call failed with exit 127. The run was stopped. The runner now
  uses a function, and that rerun is the gate of record. This is the same
  zsh trap as the earlier `$PY` failure.
- **T2's count changed from 154 to 29.** The first T2 ran a wider file
  selection than spec §8 names. The gate of record runs exactly the spec's
  three files.
- **T6 gives 35 passed, where the first run gave 34 passed and 1 deselected.**
  The runner passes `-o addopts=''`, so the `distribution`-marked test in
  `tests/test_release_preparation.py` also runs. It passed.
- **T5 is stricter than spec §8 states (J3, J5).**
  - With all three patches applied, the check exits 0 only once the date is
    filled in and the route is named.
  - With the placeholder still in place it exits 1, as T4's pytest guard
    already did.
- **The package inputs are unchanged since the candidate.** Since `7c0f4d0e`,
  `src`, `pyproject.toml`, `LICENSE` and `NOTICE` have not changed, both at
  `origin/main` `25f58b5e` and at this branch. `docs/releasing.md` is not in
  the package: `pyproject.toml` has no `readme` key. The dossier scopes this
  observation and gives the command to rerun before any dispatch (J6).

## Adversarial review

One reviewer, Codex, read each part. Each review is one reviewer's opinion.

- **Spec r1:** `revise`, findings Q1 to Q8, all accepted, repaired in r2
  ([review](notes/phase-RR3-codex-review.md); dispositions in spec §12).
- **The implementation** (`git diff b3071a79 62ba6fd4`): `revise`, findings
  J1 to J8 ([review](notes/phase-RR3-codex-review-impl.md)); dispositions
  below. Each finding was reproduced before it was fixed.

| Finding | Disposition | Applied |
|---|---|---|
| J1 `releasing.md` dropped the realpaths and the sign-off requirement | accepted, reproduced against `12daa5b7` lines 33-36 | both restored, route-neutral; T7 now asserts them |
| J2 search errors and an empty search could pass | accepted | `git grep` status checked (>1 is exit 2); an empty search is exit 2. Shown outside a repository: `search error (128)`, exit 2 |
| J3 the placeholder was normalised into a pass | accepted, reproduced in the old T5 record (exit 0 with the placeholder) | the placeholder is rejected before dates are normalised; T5 with the placeholder kept now exits 1 |
| J4 the notes opening was checked only by two words | accepted | the dated opening sentence and exactly one dated `## 0.2.0` heading are required; two mutants exit 1 |
| J5 the support row was allowlisted for either route | accepted | the check takes the route; the row must name `7c0f4d0e` under `token`, or the given commit under `workflow` |
| J6 "tests and planning files" was unqualified and false at HEAD | accepted, reproduced (`docs/releasing.md` changed) | the dossier names the package inputs, the commit observed, and the rerun command |
| J7 the T5 liveness output was not retained | accepted | the gate-of-record run keeps every checker line |
| J8 the comparison wheel lacked a path and hash | accepted | the dossier row gives the path and the full sha256 |

The repaired bytes carry no review opinion of their own.

## Refactoring review

None executed. The stale-text check and its runner are evidence scripts
under `evidence/RR3/`, not tracked tooling, and duplicate nothing in
`scripts/` or `tests/`. The search pattern is stated twice: in the spec's §3.1
search and in the check. That is deliberate: the check reproduces the
approved search verbatim. The only test change is three assertions in one
existing test.

## Boundary -- what this phase does NOT establish

- **Nothing is published.** No upload, tag, GitHub release, environment,
  publisher registration, workflow dispatch or announcement was made. V3 at
  06:22:02Z matches the O3/O5 baseline. Publisher registration on PyPI's side
  cannot be read and is not audited.
- **No route is chosen** (RL-D5). The dossier states each route's open
  preconditions; the choice is the owner's.
- **The patches are verified against this branch's tree only.** If `main`
  moves before they are applied, `git apply --check` may fail; the dossier
  says how to regenerate a hunk.
- **The 0.2.0 version availability was observed at 06:22:02Z.** It must be
  checked again immediately before any upload (dossier action 2).
- **The stale-text check covers the RR3 search and the notes opening.** It
  does not judge prose outside that search.

## Open questions

- **The owner's publication decisions:** route, tag, GitHub release
  attachments and announcements (dossier §D). None is assumed.
- **Follow-up, outside this phase:** three pages still say the repository is
  private, though V3 observed it public:
  - `README.md:69-70`;
  - `docs/installation.md:64-65`;
  - `docs/support.md:6`.

  The RR3 search does not cover them. The tag patch rewrites
  `installation.md:65` and keeps "While the repository is private" (that
  line is in the check's allowlist). Fixing the wording first means
  regenerating that hunk and updating the allowlist line.
- **Carried from RR1 and RR2, unchanged:**
  - the deferred version-independent fixtures refactor;
  - the two load-sensitive timing tests;
  - the 0.1.0 control's dependency on PyPI.

## Refuted premises

- **Spec F1 r1 said a workflow build has "new bytes"** (review Q2). Only a hash
  comparison can say. The package inputs are in fact unchanged so far (J6).
- **The first T5 design assumed date normalisation was harmless.** It hid a
  placeholder that was left in place (J3).
