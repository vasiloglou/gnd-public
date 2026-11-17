# RV3 release hand-over review

| Id | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|
| F1 | Scratch output omitted commands and control exits | yes | hardening | fixed | ee3173eb342621f7452c326f97a2650f6b5402ca | Rehearsal runner records frozen source, date, automatic exit 1, marker controls, patch check and three post-adjustment gates. |
| F2 | Shell snippets left prerequisite variables unbound | yes | hardening | fixed | ee3173eb342621f7452c326f97a2650f6b5402ca | Resolve both paths from the dossier checkout, read the actual date and handle exit 1 before the patch. All five shell blocks parse in bash. |
| F3 | Release notes link pointed to the frozen prepared page | yes | hardening | fixed | ee3173eb342621f7452c326f97a2650f6b5402ca | Link to the main documentation so the separate publication PR can update the linked page. |
| F4 | Dossier omitted the tested post-adjustment commands | yes | completeness | fixed | ee3173eb342621f7452c326f97a2650f6b5402ca | RV3 owns the hand-over instructions. The focused tests, strict build and link verification appear in the dossier and test runner. |
| F5 | Tag and release steps omitted receipts and attachment verification | yes | hardening | fixed | ee3173eb342621f7452c326f97a2650f6b5402ca | Record owner receipts, check the peeled ref, and compare and verify the downloaded attachment checksum file. Scratch copies equal the accepted hashes and a changed sdist fails. |
| F6 | Remote snapshot left outputs unlabeled | yes | completeness | fixed | ee3173eb342621f7452c326f97a2650f6b5402ca | Add labels for audit targets, the compared workflow refs and the rehash host. Preserve the observed output. |
| F7 | Dossier omitted the first build profile | yes | completeness | fixed | ee3173eb342621f7452c326f97a2650f6b5402ca | Show both RV2 profiles explicitly in the hand-over. |
