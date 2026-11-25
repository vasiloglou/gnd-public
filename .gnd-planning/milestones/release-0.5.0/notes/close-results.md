# release-0.5.0: the completion predicates against the evidence

Written for the close on 2026-11-25, at main `75c9ef52`. Each row names the
evidence that would fail if the predicate were false. The predicates are the
plan's, as amended by its §15.

| # | Predicate (short) | Result | Evidence |
|---|---|---|---|
| 1 | The source version is 0.5.0, and the lock, manifests and notes agree; `tests/test_release_version.py` exits 0 | **holds at the milestone's commits** | RW1 set 0.5.0 in five places (002); the release-version tests passed in every focused gate and every lane, at RW1's commit, at the candidate commit `85d076ba` and at the pages commit `6e980af9`. Main now declares 0.5.1, a tag-only version the owner had cut after the publication (plan §15, R6); `tests/test_release_version.py` passes there too, with 0.5.1 in `TAGGED` |
| 2 | Every file that names 0.4.0 and every test the bump moves is listed before code from an inventory and a measurement, classified, and handled under a second ruling | **holds, with a refuted premise** | the RW1 spec's inventory (29 files) and two E1 runs (`evidence/RW1/e1-summary.md`); the second ruling (RW1 spec §7). E1 could not see the notes' own readers; two such tests failed at RW1's first commit and were repaired (002; plan §15, R1) |
| 3 | One 0.5.0 notes section covers every user-visible change since `v0.4.0`; no `Unreleased:` section for work the candidate holds | **holds, as far as a table and reviewers can show** | `evidence/RW1/notes-reconciliation.md` places all 140 shipped files that differ from `v0.4.0`, rechecked at the freeze (`evidence/RW2/freeze-summary.md`: 144 files, the four more being the version edits); the two RW1 review rounds and the two RW2 probe rounds read the notes (002, 003). "Every user-visible change" is not provable by a test; the table was built mostly from pull-request attribution |
| 4 | A candidate built from a named main commit installs outside the checkout and carries the selected probes, each failing on the hash-pinned 0.4.0 wheel | **holds** | candidate from `85d076ba` (004); six probes, each with a 0.4.0 control, rehearsed on the editable tree to pass, and to fail with 0.4.0 in the candidate's place (003), and passed in the acceptance run on both wheels (004) |
| 5 | `tests/test_release_acceptance.py` exits 0 over the retained files, output recorded | **holds** | `evidence/RW2/acceptance-summary.txt`: 33 passed, Python 3.11.18, uv 0.10.10, beast-3 |
| 6 | A dossier states identity, evidence, what was not measured and every owner act; the `publish` invocation is rehearsed and not applied | **holds** | `evidence/RW3/dossier.md`; the rehearsal on a disposable clone (`evidence/RW3/scratch-verification.txt`); main kept its prepared pages until PR 287 |
| 7 | No phase uploaded, tagged, released, created the `pypi` environment or changed `.github/`; audited by `git diff` and three remote snapshots | **holds** | `evidence/close/audit.txt`: `.github/` unchanged since `v0.4.0`. Snapshots: baseline W4 (plan §1), hand-over (`evidence/RW3/pre-publication-state.txt`), after publication (`evidence/publication/post-publication-state.txt`) and at close (`evidence/close/remote-state.txt`). The only new tags are `v0.5.0` (publication act 4) and `v0.5.1` (after the milestone); the only new release is v0.5.0; the environments are still `github-pages` only; `release.yml` has no run. Each act is tied to the owner's words in `evidence/publication/owner-statements.txt` |
| 8 | The owner has published; served files compared, a fresh index install exercised, post-publication page edits on main, a publication record binds the receipts | **holds** | 006: the served wheel and sdist have the retained digests; a fresh index install printed `gnd 0.5.0`; PR 287 moved the pages; the receipts are under `evidence/publication/` |
| 9 | Each phase has an approved spec, a record with verbatim focused-gate output and one independent reviewer; the close disposes of every open question | **holds, with stated limits** | RW1 (002), RW2 (003, 004) and RW3 (005) each have a spec approved by delegated ruling, the owner's rulings on the decisions the plan left to the owner, verbatim gate output and Codex review rounds; the [sweep](close-question-sweep.md) disposes of every question. `evidence/close/phase-review-status.txt` lists the bytes changed after the last round that read them: RW1's and RW3's last repairs, the RW2 spec's amendment, and two RW1 evidence files. The lanes and rehearsals are their instrument |

## Lanes

| Commit | What it is | Passed | Failed | Errors | Skipped |
|---|---|---|---|---|---|
| `4968631e` | E1 base, the resumed RW1 | 21,994 | 1 | 2 | 13 |
| `4a73af2e` | RW1, with main `3998d371` merged | 21,998 | 0 | 2 | 13 |
| `85d076ba` | the freeze and candidate commit | 22,020 | 0 | 2 | 13 |
| `6e980af9` | the published pages | 22,033 | 0 | 2 | 13 |
| `75c9ef52` | main at the close | 22,057 | 0 | 2 | 13 |

The two errors in every row are RC-02's. The E1 base failure was in a page
of the Ossie milestone, repaired on main by pull request 275 before the
candidate.

## Outside the milestone, recorded for completeness

On 2026-11-25, after the publication, the owner asked for issue 286 to be
fixed and 0.5.1 cut as a GitHub tag only. Pull request 289 fixed it
(three Codex rounds on the change, one on the pull request, all findings
fixed, the last two rounds approving; full lane 22,057 passed, 0 failed) and
was merged; tag `v0.5.1` peels to its merge commit `eb93128a`, and 0.5.1 is
not on PyPI. Pull request 290 retained the pull-request review. The close
does not claim 0.5.1 as this milestone's deliverable.
