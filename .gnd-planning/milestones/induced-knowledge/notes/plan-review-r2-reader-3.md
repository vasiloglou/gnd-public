# Confirmation reader 3 — protocol, authority, compatibility and privacy

Plan r2 SHA-256 `d1a40a89eecad01e7e4dc72e969beb4c548297c1967df0d268c6776c18207c85`
and IK1 spec r2 SHA-256 `4f4cb8b580c680e5523d6cf1f4a4752abe3d76099a19c713620c51e8e5d3cac1`
— both match at HEAD `b554f3f` and equal the `evidence/plan-review-r2/` snapshots.

**Verdict: request-changes** (protocol/authority/compatibility/privacy). One
r2-introduced finding has an observable blocking consequence for IK1's gate
(C3-F1); the rest are textually fixable.

## Round-1 findings

| ID | Status | Citations |
|---|---|---|
| R3-F1 PR #35 status / T7 baseline | partial | plan L5–7, L111, L132, L358 now "open" with IK1 fallback; T7 pinned at `a22ccde` (spec L150–154, L178) but conflicts with IK1-D4 merge-first (C3-F1). README L13 still "was fixed in PR #35"; PROJECT.md L144 "fixed separately" |
| R3-F2 diff schema version | resolved | D12; spec L116–135; T8, T10, T12 |
| R3-F3 absent-description coverage | resolved | spec L139–140; T7 seven outputs; T11 |
| R3-F4 evidence privacy | resolved | IK-R11 L100; block shape L186–193; IK2-C1 L315; IK4-C3 L331 |
| R3-F5 issue names downstream app | resolved | IK-O20 L150; D13 L484; L408 |
| R3-F6 issue notes | resolved | IK-O18/O19 L148–149; L360–361 |
| R3-F7 spec section order | resolved | spec §§1–11 match the contract order |
| R3-F8 docs/skill row | resolved | spec L42, L144–148; plan L311, L370–373 |
| R3-F9 D7 status | partial | plan L9–14, L478 and spec L17 correct; README L16–20 lists D8–D13 pending and "Plan bytes are unchanged"; PROJECT.md L145–147 "Draft r1 only: no review" with D7 pending — misstates review status and D7 authority |

## New findings

- **C3-F1** (correctness/compatibility, high — blocks IK1's spec gate, not the
  plan; r2-introduced: yes). T7 compares to SHA-256 captured at `a22ccde`, "never
  regenerated" (spec L150–154), while IK1-D4 (L166) proposes merging PR #35 first.
  #35's commit `9137bd7` changes `model_verbalization.py` `_constraint_cnl` for
  `allowed` value constraints, which `tests/fixtures/models/full_vocabulary.orm.yaml`
  L357–359 contains. On a post-#35 base, T7's verbalization digest for
  full_vocabulary differs with no IK1 defect, and the no-regeneration rule blocks
  IK1. Reproduce: `git show 9137bd7 -- src/gnd/model_verbalization.py`; grep
  `allowed:` in that fixture. Fix: capture the baseline at the actual IK1 base
  commit, named at the IK1 gate.
- **C3-F2** (authority, medium; r2-introduced: yes). D12 recorded "owner-accepted
  (o)" for "v2 only with annotations" (plan L483; spec L164), but the round-1
  disposition theme E offered no single proposed answer ("bump to gnd-diff/2 only
  when annotations present, or bump always — rule required"). "Accepted the
  proposed answers for D8–D13" (L11–12) cannot establish which D12 reading was
  accepted. Record the owner's actual D12 choice with date, or keep D12 proposed.
- **C3-F3** (protocol, medium; r2-introduced: yes). "Untagged text is unchanged from
  r1" (L16–17) is false: D2 (L473) gained "confirmed only per D9"; D1–D6 lost
  their r1 cost readings (r1 L285–290); D6 (L477), IK-R8 (L97) and IK-O9–O12
  (L139–142) were reworded. Readers and the owner rely on tags to find unreviewed
  text, and D1–D6 still require ruling with their costs gone. Reproduce: diff
  `evidence/plan-review-r1/induced-knowledge-plan.md` against r2.
- **C3-F4** (protocol, low; r2-introduced: yes). Plan L426–428 widens the declared
  budget to "defects introduced by r2"; the disposition's budget was restricted to
  reproduced blocking findings. Two declarations of one budget disagree;
  review-convergence.md requires declaration before round two. Defensible, but
  should be recorded as an owner amendment.
- **C3-F5** (authority, low; r2-introduced: yes). The acceptance of "proposed
  repairs" (plan L11–13, L112; spec L14) cites no digest/commit of the accepted
  disposition; start-milestone asks for dates/scope/hashes for actual approval. Cite
  disposition commit `642cade` or its SHA-256.
- **C3-F6** (completeness, low; r2-introduced: no). README and PROJECT.md
  induced-knowledge section stale (as under R3-F1/R3-F9); PROJECT.md's "no review"
  misstates review status.

Privacy: no downstream names, host paths or email addresses in the plan or spec (grep).

Counts: 6 new findings, 5 r2-introduced.

## Limits

One advisory lens, approves no bytes; no tests; PR #35 effects on T7 codegen or
conformance payloads unchecked; the owner's actual words on D8–D13 not seen, so
C3-F2 rests on the disposition text. No files created or modified.
