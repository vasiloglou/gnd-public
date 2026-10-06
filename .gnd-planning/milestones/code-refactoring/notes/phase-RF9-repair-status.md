# RF9 repair checkpoint — independent review pending

2026-10-06. Owner authorization selects fixes for all nine RF9 findings, through
existing draft PR10. Corpus/spec commit2759da3 precedes implementationf5979ca.
The required review has not run: automatic approval review rejected sending the
repair source/diff to the native Codex provider because this payload/destination
was not explicitly authorized. A bounded initial-review + at-most-one-repair-review
transmission authorization is pending. No credential environment file was read.

## Completed implementation and verification

| Finding | Concrete repair / current controls |
|---|---|
| F1 | Terminal version/count/best identity and final feedback/contract acceptance binding; forged-result and independently forged feedback negatives; honest custom-ranked acceptance positive; refusal preserves caches |
| F2 | RF6 assertion agrees with RF7 literal-True restriction; truthy/strict aligned negatives and literal-True positive |
| F3 | Literal getattr counted, four reasoned existing exemptions, exact policy dirty control; expanded354 <=365 <375 at exact RF6 base; original299 <=310 <320 metric separately retained |
| F4 | Immutable global profile selection avoids per-contract cache mutation; equality, serialization and copied-version controls pass on Python3.11/3.13 |
| F5 | Only one validated-tail cache write is normalized; early/moved/repeated dirty writes remain visible; intentional replay-body successor is exact |
| F6 | Exact output body move, 25 identity aliases, observed new-home patch effect, mandatory source scan, seven fresh service imports; implicit parent edges included in layering |
| F7 | Missing reconstructed best gives a finding; genuine launched/no-eligible predecessor crashes and current refusal passes |
| F8 | Legacy digest annotations resolve concrete Model/Population on both supported minors without values-to-population runtime cycle |
| F9 | AST static-import spellings/aliases/children and relative imports; malformed Python refusal and actual generation-runtime dirty closure control |

Current focused gate480passed, session impact278passed1warning, replay pins28passed,
independent contract-refusal branch1passed, native minor controls4passed each.
Commands, exits and output summaries are in evidence/RF9-repair/gates.json;
intermediate instrument/environment failures and corrected siblings are retained.
Metadata and lint passed. All432 frozen controls are unchanged; the322-line output
move is byte exact. All18 target manifest adaptations retain predecessor/source
fields and bind current content/mode. units.json and the distribution guard stay
unchanged. The desktop environment mismatch is reproduced on exact26dbff6 and
passes after changing only LANG/LC_ALL/TERM; no golden was changed.

The repair implementation CI run37500909232 was refused before steps for account
payment/spending limits (ci-status.json); this is subject-specific and cannot be
claimed as passing CI or a result on later documentation/test commits.

## Remaining work after transmission authorization

Run the committed bounded prompt on stdin using native Codex gpt-6-sol/xhigh in
read-only mode; retain the sanitized assessment and actual exit. Reproduce and
triage every actionable finding before changes; at most one substantive repair
review is authorized by the declared budget, once explicitly selected. One
reviewer is one reviewer. Finish the branch-table/refactoring review and append
016-phase-RF9-repair.md with SHA-256 bindings, then update and push draft PR10.
Original015 remains historical; do not rewrite the frozen plan or invent RF10.

Source-owned OQ-V52-P1-IMPORTWALK-1, original budget reconciliation, RF1 carried
questions and shim retirement remain with their existing owners. The seven
combined package-initialization SCCs are diagnostics, not a zero-cycle result.
No broad replay, source-owned transfer, certification, milestone close, release,
merge or publication is established by these repairs.
