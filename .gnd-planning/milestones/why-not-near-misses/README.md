# why-not-near-misses

Source: [issue #70](https://github.com/vasiloglou/gnd-public/issues/70) (GR-T8),
plus the owner's 2026-11-01 direction to add a general disclosure mode.

- Plan: [notes/why-not-near-misses-plan.md](notes/why-not-near-misses-plan.md),
  r3, **approved by the owner 2026-11-01 `(a1)`** (all §10 decisions ruled).
- First spec: [notes/phase-NM1-spec.md](notes/phase-NM1-spec.md), r3, **approved 2026-11-01 `(s1)`**.
- Reviews: [round 1 disposition](notes/plan-review-r1-disposition.md);
  [round 2 (confirmation) disposition](notes/plan-review-r2-disposition.md):
  all four readers approve with fixes, stop rule applied (ratio 0.82); r3
  applied the repairs with no further round at the owner's direction `(p2)`.
  r3 bytes carry no review opinion.
- Phases: NM1 near-miss kernel, NM2 disclosure mode, NM3 public surface,
  NM4 documentation (checkpoints DC1 after plan approval, DC1b after NM2, DC2
  after NM3), then close.
- Pending decisions: none (NM2 D1-D7 ruled `(s2)`).
- Checkpoint DC1: illustrative drafts in `checkpoints/DC1/` (not in `docs/`),
  shown to the owner 2026-11-01 as a private rendered page. Reaction, quoted:
  "Looks good" (asked "How do the DC1 drafts look?"); no spec amendments.
- NM1: implemented and verified, record [001-phase-NM1.md](001-phase-NM1.md);
  committed on the owner's go-ahead ("yes", 2026-11-01), not pushed.
- NM2 spec: [notes/phase-NM2-spec.md](notes/phase-NM2-spec.md), r1, **approved
  2026-11-01 `(s2)`**.
- NM2: implemented and verified, record [002-phase-NM2.md](002-phase-NM2.md);
  committed 23e4a99 on the owner's go-ahead ("Commit NM2", 2026-11-01), not pushed.
- Checkpoint DC1b: [checkpoints/DC1b/disclosure-mode.md](checkpoints/DC1b/disclosure-mode.md)
  (the how-to, every output from real runs of 23e4a99; the tutorial runner passes
  13/13 blocks) and its rendered page `checkpoints/DC1b/dc1b.html`, shown to the
  owner 2026-11-01 as a private page. Findings: `DisclosureRefused` is not
  exported from `gnd.api` (proposed for NM3); `gnd check` default text output on
  a model with a redacted role prints a banner then JSON (on main before NM2;
  out of scope). Reaction, quoted: "Looks good" (asked "How does the DC1b page
  look?"); no spec amendments.
- NM3 spec: [notes/phase-NM3-spec.md](notes/phase-NM3-spec.md), r1, **approved
  2026-11-01 `(s3)`** ("Approve as proposed"; D1-D5 all (a)).
- NM3: implemented and verified, record [003-phase-NM3.md](003-phase-NM3.md);
  committed as the red corpus 9fe2685 and the following feat(NM3) commit on the
  owner's go-ahead ("Commit NM3", 2026-11-01), not pushed.
- Checkpoint DC2: [checkpoints/DC2/](checkpoints/DC2/), drafts of the new
  `reference/disclosure.md` and `how-to/disclosure-mode.md` and the edits to 15
  existing pages and skill files (`changes.md`), every output from real runs of
  420114e (18 blocks run, 13 outputs re-checked byte for byte by
  `check_outputs.py`); the reference table is generated from
  `gnd.disclosure.SURFACES` by `disclosure_table.py`. Rendered page `dc2.html`,
  shown to the owner 2026-11-01 as a private page. Questions put: NM2-Q1
  (`doccheck` every-mode) and a drift test rather than a build-time generator
  for the table. Reaction, quoted: "Looks good" (asked "How does the DC2 page
  look?"); no amendments. The two questions were not ruled explicitly; the NM4
  spec carries them as decisions with these drafts' choices as the proposals.
- NM4 spec: [notes/phase-NM4-spec.md](notes/phase-NM4-spec.md), r1, **approved
  2026-11-02 `(s4)`** ("Approve as proposed"; D1-D4 all (a)).
- NM4: implemented and verified, record [004-phase-NM4.md](004-phase-NM4.md);
  D5 added and ruled (a) `(s5)` ("Drop the three edits"). Committed on the
  owner's go-ahead ("Commit NM4", 2026-11-02), not pushed; the census suites
  re-run after the commit pass.
- Close: record [005-milestone-close.md](005-milestone-close.md). Four close
  readers approve; their findings are fixed or dispositioned there. The plan
  carries a close note. The reporter note is posted on issue #70 on the
  owner's approval ("approved", 2026-11-02). The broad suite was stopped
  unfinished on the owner's direction; merge authorized by the owner ("yes",
  2026-11-02).
