---
milestone: release-0.3.0
station: "phase RN3"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RN3
date: 2026-11-11
source_base: b913d43e
gates:
  - command: "ruling: owner approved .gnd-planning/milestones/release-0.3.0/notes/phase-RN3-spec.md sha256 aa5cbbcf535d741da7b58d17575a5483852113b60c42c79478a72818d752dde7 (r1 at 6618e643), D1 to D5 as recommended"
    exit: "n/a -- ruling"
  - command: "git apply --check of the three patches on a scratch clone of b913d43e, in both orders"
    exit: 0
    output: "11 files changed, 31 insertions(+), 34 deletions(-), both orders"
  - command: "scratch, all three patches, date replaced: uv run pytest -q tests/test_release_version.py tests/test_release_docs.py tests/test_marketplace_plugins.py tests/test_plan_app_docs.py"
    exit: 0
  - command: "scratch, same tree: sh stale-text-check.sh token"
    exit: 0
    output: "no stale release-state text (20 allowlisted hits, route token, build 4c07c0e6, published 2026-11-12)"
  - command: "thirteen controls of evidence/RN3/checks.txt (placeholder left, RELEASED hunk dropped, unpatched tree, a pin left, main patch alone, README pin left, added checkout sentence, competing opening, two date mismatches, usage error)"
    exit: "1 each, 2 for the usage error"
  - command: "uv run pytest -q tests/test_development_scaffold.py tests/test_release_version.py tests/test_release_docs.py tests/test_release_preparation.py (repository, after the last planning file)"
    exit: 0
  - command: "git status --porcelain outside .gnd-planning"
    exit: 0
    output: "empty: no patch is applied"
  - command: "codex exec --ephemeral --config model_reasoning_effort=\"xhigh\" --sandbox read-only --color never --skip-git-repo-check - (review of evidence/RN3 at aa806c76, prompt on stdin)"
    exit: 0
    output: "DISPOSITION: revise; H1 to H9, all fixed"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request"
  reason: "excluded for this milestone by the owner (RN-D11, 2026-11-10)"
evidence:
  - path: .gnd-planning/milestones/release-0.3.0/notes/phase-RN3-spec.md
    sha256: 79ca108f3c7aa726f7e4578393d32d511047f7cc6e5acbf91eb0e9f059060d69
  - path: .gnd-planning/milestones/release-0.3.0/notes/phase-RN3-codex-review.md
    sha256: 5e7c785be5c5b7fa313ded386a80e150deba37e43baae058880bcb93fcf4d4bf
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN3/dossier.md
    sha256: a9293370a267d1d4fa437cf13851f8227e8b083f72a49850c0ecd6310086a332
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN3/github-release-notes.md
    sha256: fd58493914af4ef9ad50de6a4c2c2a34f64dd7f7ac3ca8d2ffefbb22de904df1
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN3/post-publication.patch
    sha256: 9462e05fb2f44176b712d046c252a20682d298a827d3af1b053e9e8534ae67ac
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN3/post-publication-tag.patch
    sha256: 09c7d5bb96e8b1f0ea715371db1a8f09ccee9742520c559b116181ef4dcd1b52
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN3/post-publication-release-files.patch
    sha256: 5c73f6dff76598b74059c887bdf31e5563e2eb5022b40ec3aa47ef5d486bfe0a
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN3/stale-text-check.sh
    sha256: 0e601187bbfdd7b07864b12bfa7565b080dbaff7b8a14977c425e760094cb514
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN3/checks.txt
    sha256: dedfd6a856116675005932ae55b6472db5853d1981dfc0d978d1ca24b345d9e4
---

# Claim

The 0.3.0 publication is handed over and nothing is published.
`evidence/RN3/` holds:

- a [dossier](evidence/RN3/dossier.md) naming the candidate (commit
  `4c07c0e6`, wheel `143890ee…751b`, sdist `5e40d9e3…4c42`), its results,
  what was not measured, and each owner action with its command;
- three post-publication patches, prepared and not applied, and a
  [stale-text check](evidence/RN3/stale-text-check.sh);
- a draft [GitHub release body](evidence/RN3/github-release-notes.md).

On a scratch clone of main `b913d43e` the three patches apply in either
order; the patched and dated tree passes the release tests and the check; and
every control fails. The repository's tracked files outside `.gnd-planning/`
are unchanged.

## What shipped

Planning and evidence files only. `docs/releasing.md` is not edited: its
inventory (spec §13, finding 6) has seven hits and none is stale. One is
incomplete and is listed for the owner: line 17 says "This is how 0.1.0 was
published", and 0.2.0 went the same way.

## What the patches change, once applied

- Install pins move to 0.3.0 in `README.md`, `docs/index.md`,
  `docs/installation.md` and `docs/marketplace-plugins.md`; `RELEASED` gains
  0.3.0.
- The release notes and the compatibility page state the publication with
  its date; the "prepared, not published" wording goes.
- `docs/support.md` gets a row for the observed 0.3.0 profile; the 0.2.0 row
  stays (D1).
- The two shared-expense pages say the feature is in 0.3.0 and name the pip
  route their commands need (D2, review H3).
- `docs/explanation/ossie.md` says what an import leaves omitted (D3).
- The tag patch and the release-files patch move the `v0.2.0` tag sentence,
  the release link and the wheel file name.

## Gate output (verbatim)

Ruling, owner, 2026-11-11, in this session, answering "Merge PR 165 and
approve the RN3 spec as recommended?":

    Merge and approve

From [checks.txt](evidence/RN3/checks.txt), the positive case:

    ## T3, T4: all three, date replaced
    133 passed in 0.47s
    pytest exit 0
    no stale release-state text (20 allowlisted hits, route token, build 4c07c0e6, published 2026-11-12)
    check exit 0

## Adversarial review

One reviewer is one reviewer: Codex (gpt-6.1-sol, xhigh, read-only) over
`evidence/RN3/` at `aa806c76`, disposition `revise`, 9 findings
([retained output](notes/phase-RN3-codex-review.md)); dispositions in the
spec §14. Two would have failed in the owner's hands: the tag commands ran
in a directory that is not a repository (H1), and the reworded pages allowed
an install route their own commands cannot use (H3). Five were ways the
check could pass on stale text (H4 to H8). All are fixed; the reviewer's
counterexamples are now controls. The fixes were not re-reviewed.

The reviewer confirmed: all three patches apply and both orders give the
same tree; no stale pin, tag name or wheel name survives the patches; the
dossier's identities equal the committed `SHA256SUMS` and the retained
files; the upload names exactly the two release files and no command embeds
a credential; the release body's three links exist at `4c07c0e6`; all 34
cases of `tests/test_release_version.py` pass on the patched tree.

## Refactoring review

None needed, argued from what the phase touched: documents, patches and one
shell script under the milestone's evidence. **Deferred, with a target:** the
stale-text check is rewritten by hand at each release (0.2.0, 0.3.0); the
next release-preparation milestone could turn it into a parameterized script
or a test. The same goes for the hand-made patches.

## Boundary -- what this phase does NOT establish

- **No dossier command was run.** The upload, tag and release commands are
  text; the first time they run is in the owner's hands.
- Nothing is uploaded, tagged or published; PyPI and the remote were not
  touched. The last availability observation is RN2's (15:08:14Z).
- The patches were made against main `b913d43e`. A later change to the same
  lines makes them fail `git apply --check`.
- The check's allowlist is the text of today's patched tree. A page edited
  between now and publication changes the hits.
- The date in every check is a stand-in (2026-11-12); the real one is set at
  publication.
- One reviewer is one reviewer; its fixes were not re-reviewed.
- The dossier records no target-only contributor realpaths, and no
  repository content and history review.

## Open questions

- **The owner's publication decisions:** the upload, the tag, the GitHub
  release and its body, announcements. None is assumed.
- `docs/releasing.md` line 17 names only 0.1.0 as published by token upload.
- Carried, all listed in the dossier's section C: redaction and Ossie
  export; undocumented Ossie literals; full query budgets; structure guards
  outside focused gates; the unfiled fixtures-refactor issue.

## Refuted premises

- The spec expected two tag sentences to patch; one page already names no
  version.
- The spec's reworded prerequisite for the shared-expense pages (install as
  the installation page shows) was wrong for the route that page shows
  first.
- The first check script was presented as failing on stale text; the review
  showed five kinds it passed.
