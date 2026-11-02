# Close reader 3 -- protocol, evidence and record integrity

Retained text of the reader's returned report, lightly edited for layout.
Scratch paths read `<scratch>`.

**Verdict: approve**, with hardening repairs to fold into the close record.
Nothing blocking: every evidence digest matches the committed bytes, both red
corpora reproduce, anonymity, layering and RF6 hold, no record calls a single
reviewer a panel, and nothing claims merge, publication, certification or owner
acceptance.

## Findings

**H1 (hardening, reproduced). The NM4 record and its gate file cite an
unreachable commit.** `004-phase-NM4.md` and `evidence/NM4/final-gate.txt` say
"After the commit (8bc5039)". The reflog shows 8bc5039 was amended into
eb9839a 28 s later; `git branch -a --contains 8bc5039` is empty. The amend
changed only the record, README and final-gate.txt, so the census result still
holds for eb9839a (re-run at HEAD: ik6, il6, anonymity, disclosure_docs,
rf1_layering, rf6 = 70 passed). NM3 was also amended (b3bafb0 → 420114e,
README only); nothing committed cites b3bafb0.

**H2 (hardening, partly reproduced). The red-corpus commit 9fe2685 was
staged after implementation.** At 9fe2685, `phase-NM3-spec.md:3` already says
"implemented, record [003-phase-NM3.md]", a record that appears only in
420114e. So the commit order does not demonstrate corpus-first; that rests on
`corpus-red.txt`. Archiving 9fe2685 and running it against the 23e4a99 source
reproduces all 75 recorded failures, none missing (plus 44 `test_t1_census`
cases that call `git show` and fail only because the scratch copy is not a
repository). The red state is real; the commit chronology is retroactive.
NM2's red harness 2f96c17 reproduces exactly: 29 failed, 4 passed.

**H3 (hardening). Approval-before-code is not git-evidenced for NM1 and NM4,
and no approval digest is checkable.** The NM1 spec and its (s1) approval
arrive in the same commit as the implementation (acfb9ae); likewise NM4 (s4,
eb9839a). All four "approved bytes" digests are "before this tag" and those
bytes were never committed; reconstructions of the NM2 spec did not match. The
plan-review snapshots verify (r1 ec9cea0e/e3855ca5, r2 211d9e01/1b739a57).
NM2 and NM3 approvals precede their implementation commits.

**C1 (completeness). Open questions needing a close disposition:** NM2-Q2,
NM3-Q1 (owned by the close); NM4-Q1 (ambiguous owner); NM2-Q3 (an unnamed later
pass, no issue). Resolved: NM2-Q1 by D1 (a); NM1-Q1..Q3 by the NM3 spec, though
the NM3 record's "Carried" line omits them.

**C2 (completeness). Predicates 3 and 6 are partly evidenced.** Predicate 3
lacks the `fidelity` three-mode run, real `souffle`/`lake` runs and leak runs
for validate, transition and judgments (disclosed in the NM2 record).
Predicate 6 lacks the sweep and the PR (close work). The broad suite had not
run.

**C3 (completeness). Stale plan lines at HEAD.** The plan's line 10 says
execution "has not occurred"; §4 NM1 says the spec is "awaiting its owner gate".
The specs say the plan is "repaired at milestone close"; it has not been yet.

**C4 (completeness, reproduced). Commit grammar slips** against
`review-and-record.md`: 23e4a99, 420114e and eb9839a lack the record path on its
own closing line; the eb9839a subject (~93 chars) and 9fe2685's (67) exceed 65;
420114e and eb9839a carry no gate exit in the body.

**C5 (completeness). One changed file is not digest-bound:**
`tests/support/pyrel_application_successors.py` (NM2, census chain).

## Verified as sound

- All 64 evidence bindings in records 001-004 match `git show <commit>:<path>`
  at the commit that added the record; later-changed files are re-bound by the
  later record, except C5.
- Every quoted gate output equals its `final-gate.txt`.
- Approvals s1-s5 and the plan's a1, o1, o2, p1, p2 are each quoted with
  question, date and rulings.
- Refuted premises are recorded for every phase.
- `tests/test_why_not_anonymity.py` passes; its base fb03739 is an ancestor of
  33c260e, and it scans commit messages; a grep of messages and the diff finds
  0 hits.
- `gnd_layers.json` allow-list length 0; only `gnd.disclosure` added (in
  `checking`); the RF6 allow-list untouched; the one entry-point exception is
  pre-declared in the NM2 spec and disclosed.
- No single reviewer is called a panel; every phase says "not pushed".
