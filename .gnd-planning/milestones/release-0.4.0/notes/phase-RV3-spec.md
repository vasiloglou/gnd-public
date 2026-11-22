# RV3 publication hand-over

The [RV2 record](../008-phase-RV2.md) establishes the accepted files from
`648cc6e07fc6ea0e4d8791a2a33a0d005f4e106a`. This phase prepares the owner hand-over
under plan §4 and amended predicates 7–8. It uses the existing release
procedure and has no publication authority.

| Criterion | Measurable delivery |
|---|---|
| RV3-C1 | Dossier identifies the two release files and comparison wheel, exact SHA-256, byte sizes, source and build profiles, default/installed results, limitations and the exact retained directory. Rehash the original bundle and record both frozen contributor discovery roots resolving into their own archive. |
| RV3-C2 | Capture dated read-only visibility, default branch, environments, release workflow runs, releases, all tag targets and PyPI state. List each owner action and its required receipt. Copy the published-route procedure by reference. Use the frozen source for the annotated tag and the accepted bytes for upload and the release attachments. State the owner account/content-history checks still due. |
| RV3-C3 | In a disposable clone at the frozen commit, run the publication helper for rehearsal date 2026-11-17, built short SHA 648cc6e0 and profile `macOS 27.0.1 arm64, Python 3.11.18, uv 0.10.10`. Capture its exit and reported stale lines. Add the receipts defect missed by the tool and carry both BookRec paths. Save a supplemental patch against the automatic edit, demonstrate it applies, run release tests and `release_text.py check`, then a strict docs build and site links check on the scratch result. Keep the actual publication date as an input for the separate publication stage. |

The write set is milestone-local planning and evidence. The scratch
repository is disposable. It will contain the proposed publication-page
changes. Main and the hand-over branch keep their prepared pages. No PyPI
upload, Git tag, GitHub release, environment configuration or deployment is
part of this phase. The owner authorizes those acts individually under
RV-D5 and the amended RV-D10. The comparison wheel remains in the receipt.

## Verification selection

Run `tests/test_release_docs.py`, `tests/test_release_preparation.py`,
`tests/test_release_version.py`, and `tests/test_release_text.py`. Run
`tools/release_text.py check` on the prepared tree and the adjusted scratch
tree. Use the strict Zensical build and `tools/check_docs.py site` to check
the scratch page links. In addition to the helper's own stale detection,
assert disappearance of the prepared installation guidance from the receipts
and two BookRec pages. The first tool-only attempt supplies the negative
control for the absence check. Run planning-link verification after adding
the evidence. Confirm no staged workflow or product edit.

Use the existing publication helper and release checks as the instrument.
This adds no untrusted runtime consumer, time-proportional production
algorithm, validation boundary or duplicate policy walk. Authority and
publication procedure stay in the plan and the release procedure. The actual
scratch result, rather than a prediction, supplies the residual edit list.
Default exclusions remain active. One Claude Code Opus reviewer is
authorized for the hand-over diff. Budget is one tool-only and one adjusted
scratch rehearsal, focused checks, and one independent review.
