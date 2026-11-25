# Phase SI4 — Prepare the 0.5.2 GitHub tag

## 1. Status

Approved by delegated ruling on 2026-11-25. GitHub merged [PR #294](https://github.com/vasiloglou/gnd-public/pull/294)
at `a9acbc4d5873c9892d59598a7a5569bf2e3556ed` on the owner's instruction,
“merge it”. All three implementation phases are recorded and on main.

## 2. Provenance and scope

Plan r2 D4, SI4-C1, and docs/releasing.md (Tag-only versions). The owner
selected a 0.5.2 GitHub tag. The source preparation phase covers the release
metadata and documentation pull request. The owner keeps the merge and tag.

## 3. Obligations

| Obligation | Discharge |
|---|---|
| SI4-C1, five matching versions | Update the pyproject, editable uv.lock entry, .claude-plugin/plugin.json, .claude-plugin/marketplace.json, and .codex-plugin/plugin.json. |
| Tag-only release procedure | Add 0.5.2 to TAGGED, fold the three Unreleased notes into the 0.5.2 section, include the GitHub install command, and update the opening and compatibility paragraphs. |
| Existing install pins | Keep their package-index value at 0.5.0. |
| Required tests and review | Run the version, release text and release docs tests, release_text.py check, lint and the selected phase diff reviewer. |

## 4. Implementation notes

Use the existing release tooling's version paragraph guidance. Parse or
edit the editable package entry specifically so resolved dependencies do
not change. Retain the previous release headings. Use 2026-11-25 as the planned tag date, matching the current
New York date. Reconcile it before tagging if the tag moves to a later day. The dedicated phase PR is based on main after the product merge.

## 5. Verification

- Run the release version, release text and release docs files with the
  default lane selection.
- Run `uv run python tools/release_text.py check` to validate the tag-only
  metadata and published-version paragraphs.
- Verify the changed files and inspect the independent Claude Code Opus
  phase review. Record the answers under SI4 and open the tag-preparation PR.

## 6. Close dependency

The milestone close records the owner's v0.5.2 tag on the proper merge
commit, runs the configured full default lane and light close review, and
disposes the remaining questions. It has a separate delegated close ruling.

## Approval record

The merged baseline's `release_text.py check` reported that 0.5.1 is tag-only
and 0.5.0 is the latest published version. GitHub had no v0.5.2 tag when
preparation began. The tag-only procedure uses the existing release
generators and tests in place of creating a new version tool. It adds no
runtime input handling or model query. The version field update is checked
in all five locations and the release note headings and install guidance
remain covered by the existing tests.

Delegated approval (auto=true), 2026-11-25. Approved SI4 spec through
the previous paragraph at SHA-256 `eb14bb3e35b4b6a5e251ed2117fa42360230fc43e17fe9d6bfe2deb91a094e7a`. Source: the owner's named
milestone delegation and subsequent merge and close instructions. Scope:
tag-only source preparation, focused tests, and opening the SI4 pull request.
Instrument: spec and release-tool assertions. Budget: one independent diff
review through the owner's selected Claude Code Opus, with a second only
over repairs if needed. The release PR's merge and the tag have separate
owner gates.

The owner then replied “go ahead” on 2026-11-25 to the stated separate
SI4 release-preparation PR merge and `v0.5.2` tag gates. This authorizes
merging that PR and pushing the annotated tag on its merge commit.
