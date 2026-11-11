# OS2 corpus and spec gate

**Delegated approval (auto=true), 2026-11-10.** The named milestone
execution request delegates this ruling. Approved spec SHA-256
`a7dc1f578bc04569755466f0b1257cd395ae9cb9a4273f84a1d091bca92b5051`.
Approved corpus manifest SHA-256
`fe9be1b58a5b260cff7f85f25742674cdff2e9491bf956ce25b711240e2c2f99`.

The owner selected the independent Claude Code review of r1 at
`0dd646d3` and the local pinned parser for OS2. The
[verbatim review](notes/phase-OS2-corpus-review.md) confirmed all 20
r1 verdicts and required discriminating controls. The
[r2 disposition](notes/phase-OS2-spec.md#r2-review-disposition-and-supported-shapes)
narrows the approved shapes, addresses C1–C8 and retains the r1 history.
The r2 checker replay exits 0 with 29 matched cases. The selected parser
probe reports ten accepted authored groups and two rejected controls.
The frequency duplicate and mandatory empty cases demonstrate why their
source forms remain extensions. The pinned parser's corrected derived
chain is included in the approved placements.

The ruling permits implementation and the selected local parser replay.
The phase diff's independent review remains a distinct gate.
