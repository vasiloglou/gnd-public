# OB5 spec gate

**Owner ruling, 2026-11-25.** `auto=false`.

The owner was shown the [OB5 spec](notes/phase-OB5-spec.md) r1 and asked "Do
you approve the spec with all ten as proposed, or all except running the
validator (H7)?" The owner answered:

> ok

| Item | Value |
|---|---|
| Spec read at the gate | [phase-OB5-spec.md](notes/phase-OB5-spec.md) r1, sha256 `7f6eea49e4d8d4906c63e2abff34cdf55a5065c3180cae3ebfc034567de35215` |
| Base | main at `6758d224` |
| Review state | no review has run over the spec |

## Reading of the answer

The question offered two choices, and both approve the spec. They differ only
on H7. "ok" does not say which, so it is recorded as approval of what the two
choices share. H7 is an opt-in gate, which runs only on an explicit owner
request for a named subject, and "ok" is not that.

## Rulings

| Item | Ruling |
|---|---|
| H1 | **Approved.** Prose spec, then a viewable checkpoint of the built pages before the review. |
| H2 | **Approved.** Two how-to pages. |
| H3 | **Approved.** The example binding is a packaged file in the refunds example. |
| H4 | **Approved.** The how-to commands run in the tutorial runner. |
| H5 | **Approved.** The release-note section and its four bullets. |
| H6 | **Approved.** README, index page and CLI reference. |
| H7 | **Open.** The oracle lane is not run. The pages say only that GND checks the files against the pinned Ossie schemas. Asked again at the checkpoint. |
| H8 | **Approved.** OB1-Q1 goes to the close sweep. |
| H9 | **Approved.** One Codex round over the diff, after the checkpoint. |
| H10 | **Approved.** No second review of OB4's fixes; this rules OB4-Q2. |
