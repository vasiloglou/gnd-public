Retained text of the reader's report. Local paths read `<repo>`, `<scratch>`.

# Close review, reader 4: protocol, evidence and records

Milestone `model-growth-guardrails`, HEAD `2ed15f8` (MG3 `41be029`, MG4
`9e36e70`, MG5 `7961119`, MG6 `2ed15f8`; MG1 `92dc3f8`, MG2 `d8e8a3a` merged
earlier). Repository treated read-only; every probe wrote under this
scratchpad (`.../scratchpad/close/`).

## Verdict

**approve-with-fixes.** The evidence chain is sound: every front-matter
path+sha256 in records 002-007 resolves, all mismatches are explained stale
MG2 rows superseded by MG3, all 30 recorded mutants are re-killed on a HEAD
copy, the docs gates reproduce exactly, and no downstream name leaks. One
finding (F1) must be ruled before the close can be accepted; the rest are
record hygiene.

## Findings

### F1 (blocking, protocol): MG-R1 exception taken without the owner ruling the plan requires

Plan §0 MG-R1: "Any other phase that cannot keep this lists the exception and
stops for an owner ruling." MG5 accepted review R-F2 as "the one MG-R1
exception" as an agent disposition (MG5 spec, Review dispositions; record
006 Refuted premises). It is not tagged as a delegated ruling and there is
no owner ruling. process-milestone's auto delegation does not "waive stricter
scope limits", and MG-R1 names the owner explicitly.

Reproduction (HEAD vs `git archive 9b069e2` tree, repo `.venv` python with
`PYTHONPATH` set to each tree's `src`): `tests/fixtures/evolve-policy/base.orm.yaml`
with `provenance.spans` added to its one induced constraint, no
`source.mode`. `gnd validate` exits **3 at 9b069e2, 0 at HEAD**; the
unpatched control exits 0 on both. A model that does not use the new mode
changes its validation result.

Fix: put the exception to the owner at the close (keep, or gate `spans` on
induced provenance behind `mode: unattended`) and record the ruling with its
quote. Alternatively record explicitly that the delegation covers MG-R1's
owner ruling. Agent judgment should not settle that.

### F2 (hardening, records): the operator's home directory is in committed evidence

The review-and-record contract ("Retained evidence has a trap") says to
sanitize absolute paths and to declare the edit. No other milestone under
`.gnd-planning` contains `<home-path>` (`grep -rl ... --exclude-dir=model-growth-guardrails` gives 0). This one has it in four files:
- `evidence/MG3/review-probes/probe_mg3.py:4` and `probe_mg3_cap.py:4`
  (`REPO = Path("<home-path>")`). This also makes the
  probes unrunnable anywhere else, and they target the live worktree rather
  than a copy.
- `notes/phase-MG5-claude-review.md:4` and `:284`, and
  `notes/phase-MG3-claude-review.md:10-11`, which hold scratchpad paths
  containing the username.

Reproduce: `grep -rn "<user>\|/Users/" .gnd-planning/milestones/model-growth-guardrails`.
Fix: replace each with a placeholder (`<repo>`, `<scratch>`), add a "sanitized"
header note to each review, and derive `REPO` from `__file__` or argv in the
probes. Records 004/006 cite the review files by sha256, so those rows must
be re-hashed in the close record, or left as historical with a note.

### F3 (hardening, evidence): delegated-approval digests cannot be verified; amendment `(d2)` names no bytes

- Each `(d1)` (MG3 `722f3112…`, MG4 `d0a753ff…`, MG5 `91d26570…`, MG6
  `a2c20f5a…`) and the owner `(s1)` digests (MG1 `4cddaa52…`, MG2 `f04f2cf6…`)
  are "before this tag". Those bytes were never committed. A scan of all 110
  unreachable blobs found none with these digests, and no rule says how to
  strip a tag to recover them. They are claims, not checkable evidence.
- process-milestone requires a delegated approval to carry an "exact
  SHA-256". MG3 amendment r2 `(d2)` (spec §"Amendment r2") gives none for
  the amended bytes. It names invalidated claims and rechecks but not its new
  bytes, which the skill also requires for a repair.
- MG6 `(d1)` gives no budget or paid-call statement, unlike MG3 to MG5
  (the skill lists budget among the required fields). The spec's Size
  section partly covers it.

Fix: in the close record, state that these digests are unverifiable and
treat the committed spec digests in records 004-007 as the binding bytes.
For future gates, commit or retain the pre-tag bytes (for example under
`evidence/<phase>/approved-spec.md`). Add the r2 digest, or "r2 = the bytes
recorded in 004", to `(d2)`.

### F4 (hardening, evidence): mutant results are claims; the tables hold only definitions

`evidence/MG3|MG4|MG5/mutants.json` have keys `file, id, new, old, tests`
and no result. "KILLED" appears only in the records and in the MG5 runner
script. **Reproduced here:** on a `git archive HEAD` copy with
`PYTHONDONTWRITEBYTECODE=1` and `PYTHONPATH=<copy>/src`, each `old` text
occurs exactly once, and all 30 mutants (10, 9, 11) are KILLED. The
unmutated control is `135 passed` over the three test files (exit 0). The
claims hold. Fix: commit a results file with each mutant's id, outcome and
last pytest line.

### F5 (completeness, predicate 6): MG6 disposition table misses files the C1 grep finds

On a `git archive 7961119` tree, grepping `docs`, `src/gnd/skills` and
`README.md` for `evolve preview|evolve apply|gnd extract|verbalize_rules|one-shot|One-shot|unattended|source\.mode|mvp-fast`
(excluding `docs/assets/replays`) finds files that name the model-from-text
modes but have no row:
- `src/gnd/skills/gnd-model-from-code/SKILL.md:144` ("One-shot auto-confirm path")
- `src/gnd/skills/gnd-model-from-code/references/recovery-contract.md:30`
- `src/gnd/skills/gnd-orm-core/references/constraint-inference.md:228,252`
- `src/gnd/skills/gnd-orm-core/references/halpin-posture.md:193`
- `src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json` (the schema
  twin, which carries `unattended`)

The likely disposition for each is "no change". Predicate 6 still asks for a
recorded row, and T1 says coverage was "asserted at record time" without the
grep being recorded. Fix: add the rows, and record the exact grep and its
file count in the spec.

### F6 (completeness, predicate 7 / close): items the close must still carry

- No PR exists for the branch (`gh pr list --head claude/process-milestone-model-growth-4cac43 --state all` is empty). Predicate 7 needs one.
- MG6-C2 is not met: DC1 is missed (recorded honestly) and DC2 owner viewing
  is pending. The close must report this as an unmet criterion, not just a
  boundary.
- Question sweep. The register targets "milestone close" for MG2-Q2 (plan
  repair: constraint RENAME cells pre-empted), MG3-Q1, MG3-Q2, MG4-Q1,
  MG4-Q2, MG5-Q1, MG5-Q2, MG5-Q3 and MG6-Q1. MG1-Q3 goes to a later
  refactoring pass and MG1-Q4 is an accepted residual. The inherited
  O20/O21/O23/O27 rows also need a disposition. O22 is refuted by MG6 R-F1:
  the plan text still asserts it and needs the same plan-repair note as
  MG2-Q2. The other refuted premises (MG1 F1/F2/F6/rule 4, MG2 F1/F6/R-F2,
  MG3 §2.3 shape, MG4 §2.4, MG5 §2.5 and corpus counts) are recorded
  consistently. None is contradicted by a later record.
- The plan still says `auto=false` (header, §0 MG-R7, §8). The change to
  delegated approval exists only in README and the spec headers. The close
  should record it as the effective protocol change: date, the invocation
  text, and from which phase.

### F7 (completeness, records): stale or inaccurate record text

- Record 006 and the MG5 commit body say `tests/test_unattended_mode.py` has
  "87 cases". At HEAD, and at `7961119` (file sha256 unchanged), `uv run pytest --collect-only -m "" tests/test_unattended_mode.py` collects **76**. The other
  counts match: MG2 75, MG3 37, MG4 22.
- MG6 spec Design still says the proposals are generated by
  `evidence/MG6/build_growth_example.py`. F2 moved the script to `tools/`.
- README "Pending: the remaining MG-D rows (plan §10) and MG1 spec D1..D5"
  is stale. 001 accepted the §10 proposals and MG1 `(s1)` ruled D1 to D5.
- The MG3 commit `41be029` record row said the IL6 result was "in the
  commit body", but the body does not contain it. The MG4 commit patched
  record 004 with the result (`9 passed in 6.09s`). That is a
  historical-record edit; the close should note it.

### F8 (completeness, commit grammar)

- MG6 subject `docs(MG6): grow a model by additions, dispositions and one release note` is **71 characters**. The grammar allows at most 65
  (review-and-record.md "The commit"). The other subjects are 47 to 61.
- Every phase subject is a noun phrase, not the required imperative.
  MG1 and MG2 set the same precedent, so this is a low priority.
- No backticks or em-dashes in any of the six messages. The record path is
  the last line of each. That part conforms.

## Evidence check (records 002-007 front matter vs HEAD)

| Record | Rows | Result |
|---|---|---|
| 002 MG1 | 10 | all match HEAD |
| 003 MG2 | 14 | 10 match; 4 **stale, not defects**: `evolve/models.py`, `service.py`, `cli_service.py`, `evolution-contract.md` equal their bytes at `d8e8a3a` and were changed by MG3, whose record 004 lists the new digests (they match HEAD) |
| 004 MG3 | 14 | all match HEAD (record edited once in `9e36e70`: IL6 row only) |
| 005 MG4 | 13 | all match |
| 006 MG5 | 15 | all match |
| 007 MG6 | 10 | all match; DC2 copy byte-equal to `docs/how-to/grow-a-model.md` |

Other digests: `MANIFEST_SHA256` at each commit matches what the specs state
(MG3 `983d5097…`, MG4 `c72e5fb7…`, MG5/HEAD `e5690132…`). Parity tables:
MG1 282 models; MG2 and MG3 8 fixtures with before == after (same digest);
MG4 238 models, byte-identical; MG5 322 shared and identical plus one new
row (the conforming fixture). These agree with the record claims. Baseline chain: no `src/gnd` validation or
extract file changed between `1446f90` and `9b069e2`, so the MG4/MG5
baselines at `9b069e2` stand in for `1446f90` as predicates 4/5 require.

Anonymity: `git diff 1446f90 HEAD`, all commit messages since `1446f90`, and
the milestone directory: 0 matches for downstream application names.

## What I ran

- sha256 of every front-matter evidence path at HEAD and at the record's
  adding commit; unreachable-blob scan for the pre-tag approval digests.
- 30 mutants on a `git archive HEAD` copy (`PYTHONDONTWRITEBYTECODE=1`), plus
  the unmutated control.
- `zensical build --strict` (`No issues found`) and `tools/check_docs.py site`
  (`13393 ... checked`, exit 0) in that copy. In the repo,
  `uv run python tools/run_tutorials.py --group growth`: `10 tutorial blocks passed`, exit 0.
- The MG-R1 probe (F1) against HEAD and a `9b069e2` archive.
- The focused gates of records 002-006, the MG6 pytest set and the IL6 census,
  each on HEAD with `-p no:cacheprovider` (results below).
- Disposition grep at `7961119`; commit-message checks; `gh pr list`.

Focused gates on HEAD. Each exit is pytest's own, and each count equals the record's:

| Gate | Recorded | HEAD |
|---|---|---|
| 002 MG1 | 701 passed, 30 deselected | 701 passed, 30 deselected, exit 0 |
| 003 MG2 | 1895 passed | 1895 passed, exit 0 |
| 004 MG3 | 1941 passed | 1941 passed, exit 0 |
| 005 MG4 | 1533 passed | 1533 passed, exit 0 |
| 006 MG5 | 3006 passed, 57 deselected | 3006 passed, 57 deselected, exit 0 |
| 007 MG6 pytest set | 127 passed, 1 deselected | 127 passed, 1 deselected, exit 0 |
| IL6 census | 9 passed | 9 passed, exit 0 |

`git status --porcelain` was empty after every run.

## What I did not run

- The full `tools/run_tutorials.py` (only the `growth` group); the slow
  `-m "evidence or census"` lanes; RF1 golden recapture (it needs
  `uv run --python X`, which is forbidden here); parity recaptures (I
  checked the committed tables, not fresh captures); the review probes in
  `evidence/*/review-probes/` (the MG3 ones hard-code the worktree path).
- No check of the owner quotes `(o1)`, `(p1)`, `(a1)`, `(s1)` or of the
  auto invocation against the session transcript. They are taken as written.
