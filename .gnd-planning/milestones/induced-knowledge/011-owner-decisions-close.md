---
milestone: induced-knowledge
station: owner-gate
skill: process-milestone
scope: milestone-close
date: 2026-10-27
---
# Owner decisions at the close

Close readers one, two and three ([notes/close-reading-one.md](notes/close-reading-one.md),
[two](notes/close-reading-two.md), [three](notes/close-reading-three.md)) raised
five findings that need a ruling. The owner answered in the session on
2026-10-27: "Approve CD1 to CD5 as proposed." (o)

| # | Question | Owner's ruling |
|---|---|---|
| CD1 | Seven retained lines, in seven notes and evidence files from IK1–IK5 and IK4-Q2, carry this machine's username or temporary root inside absolute paths. They are already on main (close reading three, F1 and F1b) | Sanitize the files now: paths become `<repo>`, `<scratch>` or `<tmp>`. The table below binds the old and new bytes. The original bytes stay in main's history, because rewriting it would need a forbidden force-push to main |
| CD2 | IK5-Q6 raised the import work ceiling. IK-R12 moves a bound only on an owner ruling that states its arithmetic | **Ratified:** the import ceiling is P × (1 + K) + K + 2. Checks and verdict reads stay within P × (1 + K); the new K + 2 is the candidate reloads (close spec §9, F2) |
| CD3 | IK4-Q3, IK4-Q4, IK5-Q2 and IK1-Q4 were targeted at the close; the close spec's C-D2 carries them on | **Confirmed:** C-D2 supersedes those earlier "milestone close" targets. Two rows are corrected in the close record: IK1-Q4 is not only pre-existing, because IK1's `summary` also reaches the runtime `__doc__` forge; and IK5-Q5 keeps "and the IK2 block's fit" |
| CD4 | No test emits an `exclusion` candidate, so IK4-C1 and IK4-C3 have no case for that family (close reading one) | Add a successor test with one positive case and an oracle row. The approved IK4 corpus is unchanged |
| CD5 | About fifteen review leftovers and reader residuals have no disposition (close readings two and three) | Carry each to the target the close record names. None is fixed here |

## CD1: sanitized bytes

| File (under `.gnd-planning/milestones/induced-knowledge/`) | SHA-256 before | SHA-256 after |
|---|---|---|
| `evidence/IK4-Q2/regressions-red.txt` | `883ba28571993da4abfd60ef5c44e850810c43affc6a2143d331862e490c9ef2` | `9fac54a068ca56c7fd386f2d04139102430974d385207f3548a4d543853217ec` |
| `evidence/IK5/review-brief.md` | `4cc1de38f9f3a8a56018efc2ea1237d325415f2e5e84dfd49ac471bc7595ad30` | `773babbbb9c47a9b6440de2b36abd32b5bf95def61856d408db2afc24cae9606` |
| `notes/phase-IK1-agent-review.md` | `351a8c1ba74f9adfb3e2a9a19b1ecc681373e77547b6a33c9823871a20714491` | `d86180f094d55c3dc7b86f40b0331d03bc53dc0f515391af687059782fe946e6` |
| `notes/phase-IK2-agent-review.md` | `620398d2ce9b5d8347fe2501c3c8b26f6b12b3c5180f87ca0ab682fe24e2d054` | `718a25751ee16daf021e9837a07579ad22702cc4952d95ae04ad5bec24703cd0` |
| `notes/phase-IK3-agent-review.md` | `65980d5ad091b0b16b358598f3bf1f3c0b7f63b6cbe0e0f8f16a78dc3862580a` | `30b5fe917aa7369374ae145a4dcc929af6b6107cc1bcd9450bcf1aa065567d5b` |
| `notes/phase-IK4-agent-review.md` | `9b7ecb01cbb35f2dca57f7db565db1dcde31db01bfbd7c094fc7c73f55ee3389` | `81b4b901fe313512ab93a8b505f1fa76d3d48d0361b774267ebdb8d74d7f3136` |
| `notes/phase-IK5-agent-review.md` | `da104e4bef2e381fbf55030a72daba3833dc45332758bafbf4aa624134e7d144` | `79aecfe5dd39d4b1590719524d4e83683abdf8b9cac6e5e7768c681f9eb4ae4e` |

The records that bind these files (002, 003, 005, 006, 007 and 009) are not
edited. Their "before" digests are the bytes they describe, and this table is
the bridge to the sanitized bytes.

**Outside this milestone.** 65 retained files from five earlier milestones
still carry the same username in paths (code-refactoring 27, pyrel-applications
23, pyrel-agent-loop 13, analytics-m3-repairs 1, compiled-snapshot-obligations
1). The close record carries them as a separate sanitization task for the owner.

## Boundary

- These rulings decide what the close fixes and carries. They are not the
  close acceptance, which stays separate.
- No merge, release, publication or certification is authorized.
