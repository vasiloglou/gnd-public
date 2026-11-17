# Findings ledger for RV1

| Id | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|
| F1 | docs/expense/05-receipts.md:22 | yes | hardening | deferred | | RV3 owns the publication-time rewrite. Its actual-page scratch run must remove the receipts wording explicitly because the current checker misses it. The version inventory also identifies both BookRec pages. |
| F2 | docs/release-notes.md:56 | yes | hardening | fixed | ac4b96afc4a5ba269b395b9eb5434f0c489966a9 | The release-note placement control failed on the reviewed diff and passed with the 0.3.1 carryover in the upgrade paragraph. Strict docs and the full default lane ran after the change. |
| F3 | docs/release-notes.md:5 and docs/compatibility.md:5 | yes | completeness | deferred | | RV3 regenerates both paragraphs through the existing publication helper. |
