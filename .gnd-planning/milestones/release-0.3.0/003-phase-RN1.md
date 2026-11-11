---
milestone: release-0.3.0
station: "phase RN1"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RN1
date: 2026-11-11
source_base: d7317d25
gates:
  - command: "ruling: owner approved .gnd-planning/milestones/release-0.3.0/notes/phase-RN1-spec.md sha256 89312abe14c8a1dfa360632c0b9d9add3be02406ac5a2d10af22e4ae6ff7eba8 (r3 at e34059b4), D6 as recommended"
    exit: "n/a -- ruling"
  - command: "uv run pytest -q tests/test_fidelity_stub_gate.py tests/test_ik6_walk.py tests/test_object_type_description.py tests/test_public_book_runtime.py tests/test_public_book_skills.py tests/test_public_coverage_goldens.py tests/test_public_expense_current.py tests/test_public_extract_controls.py tests/test_public_legacy_codegen_pins.py tests/test_public_measure_corpus.py tests/test_public_measurement_publication.py tests/test_rf1_semantic_pins.py tests/test_rf2_pre_move_pins.py tests/test_tp2_shared_fact_types.py tests/test_rf1_pin_harness.py tests/test_rf1_cli_pins.py tests/test_release_version.py tests/test_marketplace_plugins.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_development_scaffold.py tests/test_plan_app_docs.py tests/test_disclosure_docs.py --tb=short -p no:cacheprovider (at 73884f6c, before the review)"
    exit: 0
    output: "679 passed, 2 deselected in 248.04s (0:04:08)"
  - command: "the 14 version-bearing test files on main d7317d25 with only the version changed (scratch)"
    exit: 1
    output: "31 failed, 242 passed in 171.11s (0:02:51)"
  - command: "sha256 of each of the 30 re-recorded files against the New column of evidence/e1/moved-digests.md"
    exit: 0
    output: "30 listed; 0 mismatch"
  - command: "uv lock --check"
    exit: 0
    output: "Resolved 32 packages"
  - command: "e1-shards.sh rn1end on beast-3: the default lane, six round-robin shards, at d78e576cd4fd5a83e452e26589953b645bcae33e"
    exit: "1 (the 2 known tests/test_public_optional.py errors only)"
    output: "19016 passed, 0 failed, 2 errors"
  - command: "uv run --group docs zensical build --strict; uv run python tools/check_docs.py site (at 7fba7d9e)"
    exit: 0
    output: "No issues found; 16461 local links/assets/anchors checked"
  - command: "python3 scripts/components_index.py changed --base d7317d25 --strict"
    exit: 0
    output: "50 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
  - command: "git diff --stat d7317d25 HEAD -- .github"
    exit: 0
    output: "0 lines"
  - command: "git ls-remote --tags origin"
    exit: 0
    output: "refs/tags/v0.1.0 75eda93f; refs/tags/v0.2.0 d84ad6d5, peeled 7c0f4d0e"
  - command: "codex exec --ephemeral --config model_reasoning_effort=\"xhigh\" --sandbox read-only --color never --skip-git-repo-check - (diff review over d7317d25..73884f6c outside .gnd-planning, prompt on stdin)"
    exit: 0
    output: "DISPOSITION: revise; F1 to F7, all reproduced and fixed"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request"
  reason: "excluded for this milestone by the owner (RN-D11, 2026-11-10)"
evidence:
  - path: .gnd-planning/milestones/release-0.3.0/notes/phase-RN1-spec.md
    sha256: b1dd9ce8b7985107f07c82ac15189626e38662619e3addf199981205a38a3bfe
  - path: .gnd-planning/milestones/release-0.3.0/notes/phase-RN1-codex-review.md
    sha256: f000732523b12f9b7b5c8de468cb96a2098971c82da9a2f4a95c2e745eb926c1
  - path: .gnd-planning/milestones/release-0.3.0/evidence/e1/moved-digests.md
    sha256: 4d586e43256f7a5c2abf5f1c083903dc41df9673cf24cfbddf917f09432a7683
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN1/rerecord.py
    sha256: 4bbafb2540d57572e1381c263792a7d452754d9384619b9a3d9b923f478705c1
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN1/lane-d78e576c.txt
    sha256: 2d27ec2eca0b1247c814b7a1d36559115287f4e26f331dfc472948d564d90294
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN1/lane-40af7c87.txt
    sha256: 6bc4ce7f21b735588ee14d9554ebfae301d1fd0582ddf12b44166ba581df32db
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN1/lane-a46952b5.txt
    sha256: a4b45f78402060a501326a0cedce9ba165535506a1663effc06e602f93b98504
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN1/lane-73884f6c.txt
    sha256: 0af4d587afa79f1975f3ee7bec02fed0e07edb124b85cebc03e703801464bdc2
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN1/lane-scratch-m5.txt
    sha256: 84531315ce1d66cecbfd14f228a5c86ae99ddeadb92631c3e3ccc5075bb269f1
  - path: pyproject.toml
    sha256: 1673853884c80c05200a8ceac023414773b14b6ce43c6656318957a6aac6a0e9
  - path: uv.lock
    sha256: 2e2614c5a639652005aa48677b12c2fa93af44f3b81c8c1ecbdc7e1b3b0bd517
  - path: .claude-plugin/plugin.json
    sha256: de2738c17b77912dc33419578f2eea4476131dcce53b76d218c43dd826e54e8b
  - path: .codex-plugin/plugin.json
    sha256: 88d2fd66427f98363adaf0884ad5039cce33b39aeed1999623be88128a7d7725
  - path: .claude-plugin/marketplace.json
    sha256: 6c99581c30a395f892b208d657fbcc4c15c27849ba6b614a291db8e9cdb52593
  - path: docs/release-notes.md
    sha256: c9c4ada8484bd16cb3cd58f2e82befc727f8811cdd73d6a1f0be0e2a7c3a1bb6
  - path: docs/compatibility.md
    sha256: 2da555cc7e1ab57003882462e04402d91f6a58332726ed0161427fbd70b71308
  - path: docs/support.md
    sha256: 9d372ad4fcea20096b871874db8ae68042ef0c791e5c1ff797b1a44ac7a95020
  - path: docs/marketplace-plugins.md
    sha256: d9614a6d765ae4831205915f9a2e609f3bac5228b89b9003a393adfbbd053501
  - path: docs/how-to/grow-a-model.md
    sha256: 06994b2408ad2e7c8a42a8862a803852ec77d750092e20c89d852a052361291c
  - path: tests/test_release_version.py
    sha256: c9a7333dc5a93f621b2b27e08a8bf6362c88037365408f1d9ed8ccb031c7ebfd
  - path: tests/test_development_scaffold.py
    sha256: a5c6f5556287aef9eb3c7c1e806234d41edabfc6d26eced1223292bd6b49ee7d
---

# Claim

At `d78e576c` the repository declares version 0.3.0 in `pyproject.toml`, the
lock entry and the three plugin manifests; the release notes have one
`0.3.0 (prepared, not published)` section that opens with Apache Ossie
interchange; the compatibility, support and plugin pages say 0.3.0 is
prepared and not published; install pins still name 0.2.0; and the six-shard
default lane has no failure: 19,016 passed and the 2 known
`tests/test_public_optional.py` errors. The two tests that were red on main
(plan N20, N26) pass.

Nothing is built, installed or published. The phase is on the topic branch
`claude/release-0.3.0-rn1` (PR 163), not on main.

## What shipped

- **Version.** `pyproject.toml`, the `uv.lock` entry, three manifests.
- **Re-recorded pins.** 30 files (22 fixtures, 8 test files with one or two
  digest literals each), produced by the retained script; each file's sha256
  equals the digest measured before the phase.
- **Release notes.** The 0.3.0 section: the Ossie block, then the changes
  since 0.2.0, with additions listed in the table below.
- **Pages.** `docs/compatibility.md`, `docs/support.md`,
  `docs/marketplace-plugins.md`.
- **The two red tests.** Two paragraphs of `docs/how-to/grow-a-model.md`
  split with no word changed; two retained ossie spec snapshots registered
  with their origins and digests.
- **New checks** in `tests/test_release_version.py`: the declared version's
  notes open with its headline block and link it; while the version is
  unpublished the support page has its row and the plugin page says so, gives
  the repository route and makes no publication claim. Ten mutant cases.

## Notes reconciliation (plan RN1-C3)

Changes since `v0.2.0` and the note that covers each. "Added" marks text this
phase wrote; the rest was already in the Unreleased section.

| Change | Note in the 0.3.0 section |
|---|---|
| Ossie export and import, their files, flags, scope, disclosure | "Apache Ossie interchange" (added) |
| An Ossie import restores what the export kept; omissions stay omitted | same block (added after review F1) |
| Shared vocabulary includes; composed validation and checking | "Shared definitions, project-owned policies" |
| Model format version 5; 0.2.0 cannot read it; `include:unsupported-route` | same block (added, F2) |
| `repin-include`, include snapshots in previews, `--previous-include` | same block (added, F2) |
| `gnd verbalize model`, `gnd.api.verbalize_model` | same block (added, F4) |
| Canonical model identity, `--identity`, either identity accepted | "Model identity a caller can recompute" |
| Plain text for redaction and temporal models | its own block |
| `--check-population` | "Constraints admitted on clean data" |
| Inline constraints count every fact type they reach (stricter than 0.2.0) | same block (added, F3) |
| Unchecked span count, `--require-documents` | "Unchecked source spans are counted" |
| `source-document` operation; 0.2.0 cannot read such a proposal | "A growth round can declare its source document" |
| Unattended procedure: acting on a shape match | same block (added, F5) |
| `gnd discover` on an unattended model; text walk on a reference model; retired private helpers; test timing | "Fixes and internal changes" |
| Prepared-policy reuse on Python 3.14 | "Fixes" (added) |
| Null `derivations` in coverage, sessions and the redaction diff | "Fixes" (added) |
| Role names in three packaged examples | "Fixes" (added) |
| Disclosure reference lists the Ossie commands | "Fixes" (added) |
| Entry-point, query-policy and reader routing repairs of RN0 | none: no behavior change (RN0 record) |

Every command-line option added since `v0.2.0` (read from the diff of
`src/gnd/commands`) is named in the notes.

## Gate output (verbatim)

Ruling, owner, 2026-11-11, in this session, answering "Approve the RN1 spec,
with the redaction sentence in the notes (D6) as recommended?":

    Approve, start RN1

The lane at `d78e576c`, from [lane-d78e576c.txt](evidence/RN1/lane-d78e576c.txt):

    rn1end shard0: 3682 passed, 53 deselected in 465.65s (0:07:45) (shard exit=0)
    rn1end shard1: 2940 passed, 152 deselected in 420.57s (0:07:00) (shard exit=0)
    rn1end shard2: 2833 passed, 130 deselected in 328.35s (0:05:28) (shard exit=0)
    rn1end shard3: 4083 passed, 88 deselected in 825.05s (0:13:45) (shard exit=0)
    rn1end shard4: 2652 passed, 282 deselected in 257.72s (0:04:17) (shard exit=0)
    rn1end shard5: 2826 passed, 145 deselected, 1 warning, 2 errors in 587.81s (0:09:47) (shard exit=1)
    ERROR tests/test_public_optional.py::test_base_wheel_refuses_missing_synth_extra_and_still_checks
    ERROR tests/test_public_optional.py::test_declared_synth_extra_is_seeded_and_loader_valid

Three earlier lanes are retained beside it. At `73884f6c` (before the review
fixes): the 2 known errors only. At `a46952b5` and at `40af7c87`: the 2 known
errors and `tests/test_development_scaffold.py`, each time because a planning
file this phase had just written held text shaped like a link (the retained
review, then the spec note about it). The focused gate was rerun on the final
tree and exits 0 with 682 passed.

## Adversarial review

One reviewer is one reviewer: Codex (gpt-6.1-sol, xhigh, read-only) over
`d7317d25..73884f6c` outside `.gnd-planning/`, disposition `revise`, 7
findings ([retained output](notes/phase-RN1-codex-review.md)). Each was
reproduced before it was accepted; the dispositions are in the spec's "Review
findings" section.

- **F1 (blocking).** The notes said an import with its sidecar restores the
  original model. For a model with populations it does not. **This sentence
  was in the notes text the owner approved.** It now says what is restored
  and what stays omitted.
- **F2, F3 (blocking).** Two incompatibilities with 0.2.0 had no note: model
  format version 5, and a stricter additive rule.
- **F4, F5.** `gnd verbalize model` and a packaged procedure step had no note.
- **F6, F7.** The two new checks accepted three inputs they should refuse;
  each is now a mutant case that was accepted at `73884f6c` and is refused.

The reviewer confirmed: the five version sites and the single lock change;
all 30 file digests; the seven containers decompressed independently, with
changes limited to version values and digest references and historical
members untouched; the eight test files differ only in digest literals; pins
still at 0.2.0 and no publication claim; the Ossie block's file names, flags,
pinned commit and scope; the two paragraph splits change no word; both
snapshot digests and origins. It could not regenerate digest-only outputs or
run the lanes. The fixes after it were not re-reviewed.

## Refactoring review

None executed. The phase touched version literals, recorded outputs, docs and
one test module; it moved no structure. **Deferred, with a target (owner
ruling RN-D7):** the 30-file re-record recurs at every release until recorded
outputs stop carrying the version; carried to an issue, which is not yet
filed. `evidence/RN1/rerecord.py` now makes the edit a one-command step with
its own refusal of any non-version change.

## Boundary -- what this phase does NOT establish

- Nothing is built or installed. Whether the wheel carries the Ossie schema
  files, and whether 0.3.0 is still free on the package index on a later day,
  are RN2's to show.
- The re-record's capture ran under Python 3.14 only. The 3.11 and 3.13 legs
  of the RF1 pins were not run.
- Five gzip containers were re-recorded by moving the version inside the
  stored document; the owning tests compare those bytes with the live command
  and pass, which is the only check that the bytes equal live output.
- Completeness of the notes rests on one reviewer's read of the diff since
  `v0.2.0`, this session's check of the added command-line options, and the
  table above. No one has read all 107 changed source files line by line
  against the notes.
- The opt-in lanes did not run (RN-D11). The opt-in `ossie_oracle` lane did
  not run (D7, still open).
- One reviewer is one reviewer, and its fixes were not re-reviewed.
- The lane ran on one machine (beast-3, macOS 27.0.1, uv 0.13.7).

## Open questions

- **D7, for the owner, before RN2:** the path for `GND_OSSIE_ORACLE_ROOT`, or
  a ruling that the Ossie oracle lane is not run for 0.3.0.
- **The carried refactor's issue (RN-D7)** is not filed; filing it is an
  outward action the owner has not yet asked for.
- **Redaction and Ossie export** (from RN0): the notes now state the behavior;
  whether it should change is undecided.
- **`docs/explanation/ossie.md`** says an import "restores those details when
  the sidecar is present". It is true of the sidecar's details and silent on
  omitted populations; the notes are now more exact than the page.
- RN2's spec is not written. It starts when this branch is on main.

## Refuted premises

- The spec said one paragraph of `grow-a-model.md` was over the limit; there
  were two.
- The approved notes text said an import restores the original model.
- The spec's reconciliation method (present notes plus the pull-request list)
  missed four changes inside pull requests that already had a note.
- "The scaffold test passes" was claimed twice from a run made before the
  last planning file was written.
