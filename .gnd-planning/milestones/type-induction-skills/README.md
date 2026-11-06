# type-induction-skills

Planning opened 2026-11-04 for the owner's rulings on CT-close-Q1 and
CT-close-Q2 from the
[composition-and-type-induction close](../composition-and-type-induction/007-milestone-close.md):
duplicate detection and multi-valued modelling for the `fact-type` discover
family move to skills; the CLI stays deterministic and supplies evidence.

**Status: closed 2026-11-05 ([close record](007-milestone-close.md)),
accepted by the owner ("Merge, accept as is").** TS1–TS3 merged (PRs
#88–#90); TS4, TS5 and the close merged as PR #91. Predicate 6 is accepted as
two folders (TS-close-Q1); the optional re-recording (TS-close-Q2) was not
authorized. The paragraphs after the links are the history as written.

- [Plan gate record](001-plan-gate.md)
- [Canonical plan (r1, approved)](notes/type-induction-skills-plan.md)
- [TS1 spec (r2, approved)](notes/phase-TS1-spec.md)
- [TS1 record](002-phase-TS1.md)
- [TS2 spec (r1, approved)](notes/phase-TS2-spec.md)
- [TS2 record](003-phase-TS2.md)
- [TS3 spec (r1, approved)](notes/phase-TS3-spec.md)
- [TS3 record](004-phase-TS3.md)
- [TS4 spec (r1, delegated approval)](notes/phase-TS4-spec.md)
- [TS4 record](005-phase-TS4.md)
- [TS5 spec (r1, delegated approval)](notes/phase-TS5-spec.md)
- [TS5 record](006-phase-TS5.md)
- [Close record](007-milestone-close.md)

Phases:
- TS1: type evidence (`--type-evidence`);
- TS2: judgement files and rendering, including many-to-many with a spanning
  uniqueness;
- TS3: packaged skill `gnd-judge-fact-types` (semantic duplicate judge);
- TS4: packaged skill `gnd-model-multivalued` (variant of the
  `rai-orm-from-schema` dialect conventions);
- TS5: documentation and a how-to;
- close.

(Superseded: the close record disposes TS-D0 to TS-D11.)

TS1 spec r2 (2026-11-05) re-reads its lines on main `b733b2a`; the CT4-Q1
ruling (008) omits digests under `customer`, so groups are keyed `g<n>`
instead. TS1 shipped `--type-evidence`; its open questions (TS-Q3, the CT4
DateTime kind, plan repairs) are in the record. PR #88 merged as
`7b171bb2`. TS2 spec r1 drafted 2026-11-05 on the owner's relayed "go
ahead"; it records two refuted plan premises (P1, the judgement record
cannot sit on an induced constraint; P2, a `functional` shapes verdict can
never be accepted). TS2 spec r1 approved by the owner `(a2)` 2026-11-05 (prose, D1–D10 as
proposed). TS2 implemented and recorded ([record](003-phase-TS2.md)); one
review, five findings fixed, 31 of 31 mutations killed. PR #89 merged as
`b4ef8cbf`. TS3 spec r1 drafted 2026-11-05 on the owner's "go ahead"; it
records refuted premise P3 (TS3-C4's "TS5 fixture" cannot precede TS3) and
finds the live IL6 skill census breaks on any new skill (D4). TS3 spec r1 approved by
the owner `(a3)` 2026-11-05 (prose, D1–D9 as proposed, one paid Sonnet
recorded run). TS3 implemented and recorded ([record](004-phase-TS3.md)): one paid
Sonnet run matched the key; one review, eight findings fixed. The recording
binds the pre-review skill bytes (TS3-Q3). PR #90 merged as `1668a58e`.

**2026-11-05: the owner invoked `process-milestone type-induction-skills
auto`** (delegated approval for this milestone's spec and close rulings; paid
calls, merge and publication stay the owner's). TS4 spec r1 recorded as
delegated approval `(d4)`; the owner separately authorized two paid Sonnet
runs (TS4, and re-recording TS3). TS4 implemented and recorded
([record](005-phase-TS4.md)): one review, four findings fixed; the TS4
recording matched its key (one recorder false positive, R1, corrected); the
TS3 re-recording passed all ten checks (TS3-Q3 resolved). TS5 spec r1
recorded as delegated approval `(d5)`; the how-to was shown at checkpoint
DC-TS5 and the owner answered "Looks good, continue". TS5 recorded
([record](006-phase-TS5.md)): one review, five findings fixed. Next: the
close.
