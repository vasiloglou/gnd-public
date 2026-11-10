# Plan gate: ossie-interchange r3

Date: 2026-11-10. `auto=false`.

**Owner approval `(a1)`.** In this planning session, asked "Approve plan r3
at the plan gate, or run a second light-panel round first?", the owner
answered: "Approve r3". It approves this plan at r3, without a second panel
round.

| Artifact | SHA-256 (r3, before this gate's tags) |
|---|---|
| `notes/ossie-interchange-plan.md` | `4c8656bb98979e043f93455ad946430d3936a1ab26aac5a6c82ef36070e92d5d` |
| `notes/phase-OS0-spec.md` (draft r3, not approved here) | `5c9894a246a132058c478ae7e947ff29be8921bc57bb88c59e6aa3c4d79573aa` |

After approval the plan received only status edits and `(a1)` tags.

## Plan review

One round. The maintained light panel (`gnd review panel-light`, effort
`high`, bound per run for Claude and Codex only) reviewed **r2**
(`fb6fc6fe…2d68`) on 2026-11-10: 5 of 6 seats succeeded, Qwen timed out, and
every successful seat asked for revision (Gemini blocked). Finalization
exited 0; see [PANEL-REVIEW.md](evidence/plan-review-r2/PANEL-REVIEW.md).
The owner directed "Apply fixes as r3"; r3 applies all 19 prioritized fixes,
tagged `(p2 F1)`–`(p2 F19)`.

**r3 itself has not been reviewed.** The owner approved it knowing that, as
the question stated. The panel's opinion describes r2's bytes, not r3's.

## What the approval settles

- §10 rulings OD0–OD8, given by the owner on 2026-11-10 and tagged `(o)`,
  stand as ruled. OD2, OD4's exception list, E6's counts and the
  `relationalai` target version are settled from OS0's measurements, as §10
  says.
- The phase set OS0–OS6 and close, with the dependency list of §4.

## What the approval does not settle

- **The OS0 spec.** It has its own owner gate. Its D2 (commit evidence under
  `evidence/OS0/`) is still open.
- **OD6 confirmation.** The plan makes an explicit owner confirmation of the
  OD6 reading a precondition of the OS1 spec gate (p2 F12).
- **OS6 publication.** Pushing to a fork and the upstream PR text each need
  their own owner approval; the milestone may close with the PR opened or
  with publication declined.
- **Retained panel output.** Codex's stderr echoed the disposable panel
  worktree's scratch path (username already redacted to `***` at capture).
  At the owner's direction ("Sanitize, note it") it was replaced by
  `<panel-tree>` with an edit header; before and after digests are in
  [SANITIZATION.md](evidence/plan-review-r2/SANITIZATION.md). The run and
  synthesis digests are unchanged, but re-running finalize over the
  committed run now refuses on that file's digest.

## Boundary

- Approval of the plan is not approval of the OS0 spec or any later phase's
  spec. Each has its own owner gate, and no code is written before an OS1
  spec is approved.
- No auto mode, commit, push, merge, release, publication or certification
  is authorized by this gate.
