# Phase RN3 output review (Codex), retained verbatim

- Instrument: one reviewer in a different tool. One reviewer is one reviewer.
- Command: `codex exec --ephemeral --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin, exit 0. Model: gpt-6.1-sol (the tool's configured default).
- Reviewed bytes: `evidence/RN3/` at commit aa806c76, with the approved spec.
- What the reviewer could not do: write files, so it could not run the check on patched files or the publication steps (its own list at the end).
- The output below is unedited (it contains no home-directory path); the trailing "codex exit" line is the driver's.

## Reviewer output (verbatim)

DISPOSITION: revise

ID: H1
SEVERITY: medium
LOCATION: .gnd-planning/milestones/release-0.3.0/evidence/RN3/dossier.md:94
QUOTE: git tag -a v0.3.0 4c07c0e6a623263048cb675d237046ebb239cb32 -m "get-nick-done 0.3.0"
PROBLEM: Following the preceding commands leaves the owner in ~/gnd-release/0.3.0/4c07c0e6/candidate. That directory is not a Git repository; I confirmed that git rev-parse fails there. Both tag commands therefore fail when followed sequentially.
FIX: Run both commands with git -C pointing to the repository checkout, or explicitly change to that checkout first.

ID: H2
SEVERITY: medium
LOCATION: .gnd-planning/milestones/release-0.3.0/evidence/RN3/dossier.md:62
QUOTE: Repository: visibility `public`, default branch `main`.
PROBLEM: The owner checklist omits the repository content/history review required before upload by docs/releasing.md:50–52. Observing visibility and the default branch does not discharge that review. The dossier also omits the target-only contributor realpaths expressly required by docs/releasing.md:44–46.
FIX: Add an explicit pre-upload content/history review action and record or link the required contributor realpath evidence.

ID: H3
SEVERITY: medium
LOCATION: .gnd-planning/milestones/release-0.3.0/evidence/RN3/post-publication.patch:182
QUOTE: +**Before you start.** Install GND 0.3.0 or later, as the
PROBLEM: The replacement prerequisite, also added to the commands page at patch line 59, permits the installation page’s default uv tool installation. However, docs/how-to/shared-expense-policies-commands.md:18 immediately uses python -c with import gnd to copy package resources. Installing a CLI with uv tool install does not make its modules importable by the current Python interpreter. The documented default route can therefore fail before copying any files. [uv’s tools guide](https://docs.astral.sh/uv/guides/tools/) confirms this isolation.
FIX: Tell readers on both pages to use the activated Python virtual-environment installation route, so python and gnd use the same installation.

ID: H4
SEVERITY: medium
LOCATION: .gnd-planning/milestones/release-0.3.0/evidence/RN3/stale-text-check.sh:19
QUOTE: PATTERN='0\.1\.0|0\.2\.0|0\.3\.0|next release|not published|not signed off|prepared 0|newer than|unreleased (feature|example)|development checkout for'
PROBLEM: The pattern misses “This feature requires the development checkout.” outside release-notes.md. Adding that exact stale sentence to the fully patched shared-expense commands page leaves the evaluated check successful with the same 19 allowlisted hits. Only release-notes.md receives the separate search for this wording.
FIX: Search for development-checkout requirements throughout README.md and docs/, then explicitly allowlist legitimate conditional or historical occurrences.

ID: H5
SEVERITY: medium
LOCATION: .gnd-planning/milestones/release-0.3.0/evidence/RN3/stale-text-check.sh:66
QUOTE: grep -q -E '^Version 0\.3\.0, published on [0-9]{4}-[0-9]{2}-[0-9]{2}, is the latest release; 0\.2\.0 and$' "$NOTES" ||
PROBLEM: This checks for the sentence anywhere, not at the opening. Prepending “Version 0.2.0 is the latest release.” to the fully patched notes still passes the evaluated check. The main search excludes the notes, and the first-14-lines search does not recognize this stale statement. This directly contradicts the header’s opening-state guarantee.
FIX: Validate the actual opening paragraph and reject competing latest-release statements there.

ID: H6
SEVERITY: medium
LOCATION: .gnd-planning/milestones/release-0.3.0/evidence/RN3/stale-text-check.sh:61
QUOTE: sed -i.bak -E 's/[0-9]{4}-[0-9]{2}-[0-9]{2}/<DATE>/g' "$HITS"
PROBLEM: Date normalization masks a stale publication date. With the notes dated 2026-11-11, changing compatibility.md’s 0.3.0 publication date to 2026-11-08 still passes. Separately, changing only the notes heading to 2026-11-08 also passes because the opening and heading dates are never compared. These inconsistent publication statements cannot all be true.
FIX: Extract the publication date once and require the opening, heading and compatibility statement to agree before normalization.

ID: H7
SEVERITY: medium
LOCATION: .gnd-planning/milestones/release-0.3.0/evidence/RN3/stale-text-check.sh:53
QUOTE: git grep -i -E "$PATTERN" -- README.md docs ':!docs/release-notes.md' | sed -E 's/^([^:]+):/\1:/' > "$HITS"
PROBLEM: The search’s exit status is discarded by the pipeline. Under /bin/sh, a producer that emits valid hits and exits 2 followed by this successful sed yields pipeline status 0; I confirmed that behavior. Partial output containing the README pin can pass the subsequent guards and allow a search error to become success. The pipelines at lines 59, 60 and 62 similarly discard upstream errors.
FIX: Capture search output without a pipeline, inspect each search status, and return 2 for errors before processing its output.

ID: H8
SEVERITY: low
LOCATION: .gnd-planning/milestones/release-0.3.0/evidence/RN3/stale-text-check.sh:56
QUOTE: { echo "README.md has no 0.3.0 install pin: are the post-publication patches applied?" >&2; exit 2; }
PROBLEM: Leaving only the README pin at 0.2.0 returns 2, although this is stale text, not a usage or search error. It also exits before reporting other accumulated problems. The header promises exit 1 for stale text or a missing published-state line.
FIX: Record the missing pin as a problem and exit 1 through the normal reporting path. Reconcile the spec/checks.txt expectation accordingly.

ID: H9
SEVERITY: low
LOCATION: .gnd-planning/milestones/release-0.3.0/evidence/RN3/dossier.md:118
QUOTE: Then `sh stale-text-check.sh token` must exit 0 and
PROBLEM: The script header requires execution from the repository root, but stale-text-check.sh does not exist there. It is under the RN3 evidence directory. The stated command therefore cannot run from the required directory.
FIX: Give the repository-relative invocation: sh .gnd-planning/milestones/release-0.3.0/evidence/RN3/stale-text-check.sh token.

Checked and found true

- All three individual git apply --check commands succeed at aa806c76. In-memory application confirms both requested orders match exactly and produce identical trees.
- Independent searching found no additional surviving stale version pins, tag names, wheel names or publication-state replacements in README.md and docs/.
- The retained artifacts’ actual sizes and SHA256 values match the dossier, RN2 record and committed SHA256SUMS. The shasum verification prints three OK lines.
- The upload names exactly the release wheel and sdist. The checksum attachment covers those two filenames. No command uploads the comparison wheel or embeds a credential.
- The proposed tag names the correct candidate commit.
- The shared-expense resources are present in the retained wheel.
- The Ossie omission sentence agrees with exporter/importer behavior. The support row agrees with RN2. The compatibility and release-notes additions are consistent with the stipulated publication state.
- All three release-body link targets exist at 4c07c0e6; its feature summary agrees with the candidate’s release notes.
- All 34 cases in test_release_version.py pass against the in-memory patched tree. Restoring an old pin or leaving a date placeholder produces the expected failure.
- Shell syntax checking passes. The fixed-string, whole-line allowlist semantics are correct; no BSD/GNU portability defect was identified in the mktemp or sed -i.bak forms.
- The repository remains unchanged.

Could not check

- Full checker execution against physical patched files: temporary-file creation and in-place editing are forbidden. Counterexamples were evaluated in memory using the actual sed/grep filters; pipeline behavior was checked directly.
- Publication transport, served-file comparison, fresh PyPI installation and future tag URLs: nothing has been published, and no publishing actions were authorized.
- Account-side ownership/release authority or the independent beast-3 run: only the retained evidence was available for review.
codex exit 0
