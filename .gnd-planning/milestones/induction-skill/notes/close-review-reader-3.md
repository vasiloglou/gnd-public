# Close review, reader 3 -- the code bytes that carried no review opinion

Retained text of the reader's returned report, over candidate `9b69ca5f`. Local edits: this heading; the report's own first heading demoted one level; scratch paths read `<scratch>`. Dispositions: [close-review-disposition.md](close-review-disposition.md).

### Reader 3 report: open-questions sweep, plan amendments, protocol and authority, privacy

Clone: `<scratch>/reader-3/repo` at `9b69ca5f`.

## 1. Digest check

All four digests match:
- `notes/induction-skill-plan.md`: 535679f6…9873
- `notes/close-sweep.md`: fb224396…800b
- `002-phase-IS1.md`: 81b010ef…2ed5e
- `005-phase-IS2.md`: 70b885fe…bb3a

The first 493 lines of the plan are byte-identical to the approved r3 at `e74d882` (sha256 46e8e6c8…b0e7). The milestone diff to the plan adds 39 lines and changes nothing else.

## 2. Findings

| Id | file:line | What is wrong | Reproduction | Class | Suggested fix |
|---|---|---|---|---|---|
| R3-F1 | close-sweep.md:39; plan:516-525 | IS2-Q2 is marked **closed** by `4e1ae32c`, "measured in the close record". That measurement (the full installed docs check over both origins) is still running and the close record does not exist yet. | `ls .gnd-planning/milestones/induction-skill/` shows no 006 record. The brief says the check is still running. | blocking (until the result is in) | Keep the row "closed" only if the close record shows exit 0 for both origins with the verbatim output. Otherwise mark it carried. |
| R3-F2 | close-sweep.md:21 | The row says the nine conversations do not record "the neutral export offered after the absent-learner stop". They do. | `absent-learner/.../turn-01.jsonl`: the agent stops with "no learner named popper is installed" and offers "1. **Neutral export only.**". `turn-02.jsonl` line 7 runs `gnd export ilp … --target neutral --out export-neutral`, and line 9 keeps "EXPORTED 8 examples and 60 facts…". The other named branches really are absent: `--target amie`, `mined-rules`, `--target llm`, `expected-state` and `Exit code 6` each have 0 hits across the recordings. | completeness | Drop that item from the list, or say "recorded but not shown on the page" (replays.json has no absent-learner entry). |
| R3-F3 | close-sweep.md:57 | The sweep says record 002 "executed none and argued none needed". Record 002:186 says "**None executed.** One refactor was seen and deferred", which is IS1-Q3 (`EXPECTED_RELATIVE_LINKS`). The format requires the close to confirm that every deferred refactor has a named target, and only 005's deferral is confirmed. | Quoted lines. | completeness | State that 002 deferred one refactor, IS1-Q3, now carried to #319. |
| R3-F4 | close-sweep.md:29 | IS1-Q2 is "carried to #318", but #318 item 4 omits part of IS1 round 2. It lacks F3's test half (the summary test misses a restored Score section, and a forbidden phrase that spans a line break). It also lacks parts of F6 (extra reaction rows filtered out, pipeless tables rejected) and of F7 (a fenced heading accepted, `## Learn ##` rejected). | `gh issue view 318`, item 4, lists only "table and comment visibility, link-definition titles, the handoff link, keyword reversals, … path, install and identity patterns". Compare IS1-r2 FINDINGS rows F3, F6 and F7, and 002:217 ("F3 (test) and F4 to F10"). | completeness | Add the missing cases to #318 (an owner-approved gh write), or name them in the sweep row as uncarried with a target. |
| R3-F5 | close-sweep.md:31 | IS1-Q4 is retired because "the structure-guard question belongs to that milestone". The seeded-routes-and-identifiers close (007) does not record that question: SI1 merged while a structure-guard file was red. So the question now has no home. | `grep -n -i 'structure.guard\|guard list' seeded-routes-and-identifiers/00{6,7}*.md` finds no such question. 007:95 only notes that the link is pinned. | completeness | Carry the question with a named owner, or give a reason that stands on its own. |
| R3-F6 | close-sweep.md:41 | IS2-Q4's local-path commit `1cbbc18d` is also an ancestor of the close branch, and the sweep covers only PR 317's squash merge. The row is "accepted" with no owner named. If the PR is already pushed, the home-directory paths are public on GitHub. | `git merge-base --is-ancestor 1cbbc18d 9b69ca5f` succeeds. `1cbbc18d` adds 16 home or scratch path lines: 14 in `phase-IS2-r1/review.md`, 1 in its diff.patch, 1 in a test. Later commits `8d76814f` and `e8f51123` also touch such lines, though the candidate tree is clean (see section 3). | hardening | Say that the close PR must also be squash-merged, or rebased onto main after 317. Name who accepted the residual: public exposure is the owner's call, not a delegated one. |
| R3-F7 | close-sweep.md:9-10 | "The owner chose these dispositions on 2026-11-26 ("yes do the first")" attributes every disposition to the owner. The quote is ambiguous, and no committed receipt quotes the question it answered. Every other receipt (`owner-statements*.txt`, `c0-owner-reaction.txt`) quotes the whole question and marks the reading as the author's. Filing #318 and #319 was a GitHub write, which records 002 and 005 say needs "the owner's word". | `grep -rn "do the first"` finds only close-sweep.md. `evidence/close/` is uncommitted. | hardening (blocking if no receipt is committed) | Commit `evidence/close/owner-statements.txt` with the question quoted whole, the answer, and "That reading is the author's". Otherwise record the dispositions as a delegated close ruling. |
| R3-F8 | close-sweep.md:22, 51 | Three rows are "carried" with no next owner: the plan §4 limitations, the "skill holds on Haiku" finding, and IS2-Q4. Row 21's owner, "a later recording milestone", does not exist. The format says carried rows name the next owner. | Quoted rows. | completeness | Recast the stated limitations as retired ("stated limitation, not a question"), or name an owner or issue for each. |
| R3-F9 | spec IS2 §13 F2 (lines 260-267); 005 | A test launched a paid Haiku run (USD 0.084) before any gate record existed. That breaks plan IS2-C1 ("Before any paid run … a new IS-scoped gate record is written") and the §6 control. Neither the sweep nor 005's open questions or refuted premises list it. | Spec IS2:260-267; record 003, "cost ceiling" row. | completeness | Add a refuted-control row ("a gate record precedes every paid call") disposed as retired: the repair is that T6 fails if any subprocess starts. |
| R3-F10 | spec IS2 §15 lines 396-400 | Haiku's departures that no check measures are not swept. The actor sentence was read as covering only proposals, and `recheck` wrote files although the skill says a re-check writes nothing. Both may mean a skill sentence needs wording work. | Quoted spec lines. | completeness | Fold them into the "holds on Haiku" row, with an owner. |
| R3-F11 | 005:105; 004 (cost-ceiling row) | "D11's USD 10 ceiling" credits the figure to the owner's ruling. The D11 receipt quotes only "approved D11", and plan D10/D11 names no figure. The author declared USD 10 in record 003. The owner first saw it at C1 (owner-statements-c1). | `owner-statements.txt`; plan:476. | hardening | In the close record, say the ceiling was declared by the author under the owner's D11 approval, and was shown to the owner at C1. |
| R3-F12 | plan:503-514 (A1) | A1 is accurate as far as it goes, but incomplete. Run 3 is "no (ruled)" as run of record; the run of record (inv. 1) is `rendering-rejected`. The prior wording's #51/P1..P3 half is not answered. The reference says the shipped rendering is run 3's. | `docs/reference/ilp-bridge.md:615-617, 633-635`. | hardening | Add: "run 1, the run of record, was refused at the rendering; runs 2 and 3 used later renderings, and the shipped rendering is run 3's." |
| R3-F13 | plan:531-532 | §11 says "The close record's question sweep carries each of them", but the sweep marks three of them **retired** (close-sweep:50, 52, 53). The sweep is also a note, not yet the close record. | Quoted. | completeness | Say "dispositions each of them". |

## 3. What checked out

- **A1 against the reference.** A1 matches "Comparing the learners": three popper 5.0.1+578a4e2 runs on refunds, and inv. 3 is `completed`/`admitted`, with 1 clause, import exit 0 and 1 admitted. SKILL.md:119 says "The ILP bridge reference records the Popper runs". Both amendments keep the prior wording and give the raising record and the date. 002:224-228 names the plan repair for the close.
- **Other refuted plan premises.** D8: the census pin changed mechanism, recorded at spec r4 §12 and swept in row 001. The `said` rule, the done table and the 12 MiB budget are spec or code text; the C2 receipt confirms "Raise cap to 13 MiB". None needs a plan amendment.
- **Inherited rows (001 and IK6-Q1).** Their citations say what the cited files say: the spec r4 ledger shows #54 merged, and 002 IS1-C6, IS1-C8 and records 003/004 match.
- **IS2-Q1 and #318.** The eleven deferred round-2 findings (F1-F3, F5-F10, F12, F13) all appear in #318. IS1-Q1 and IS1-Q3 match #319. The IS1-Q2 partial discharge exists: `test_q2_every_proposal_command_carries_the_actor_and_time_once` and `test_q2_the_amie_export_is_its_own_line`.
- **Delegated rulings.** IS1 spec §13, IS2 spec §12 and §15, and README all label them "delegated (auto=true)" and state "not the owner's reading". C1, C2 and D11 are owner rulings with receipts. Records 003 and 004 authorize only their runs and exclude merge and publication.
- **Privacy, milestone diff `6bbbee81..9b69ca5f` (160 files, including 46 recording files and the replays).** 0 hits for the real home path, the local user name, or the downstream-app names that the repo rule forbids naming. The only emails are `noreply@anthropic` and `fictional-handle@example.invalid`. Every `/Users/…` hit is a synthetic test fixture (`/Users/someone`, `/Users/example`, `/Users/...`). No token patterns, only the needle literals `sk-ant-` and `sk-or-`. Recordings use `<workspace>/<tmp>/<home>/<repo>/<plugin>` markers. The only account name is in the repository's own public URL, which `pyproject.toml` already carries. `uv run pytest -q -p no:randomly tests/test_plan_app_docs.py tests/test_ik6_walk.py`: 137 passed.

## 4. What the close record must still contain

- `006-milestone-close.md`, the name commit `4e1ae32c` already cites, with scope `milestone-close`.
- References to records 001 to 005.
- The close ruling (delegated or owner) as its own gate, citing plan sha256 535679f6… and the sweep's digest.
- The full default lane and the installed docs check for both origins, verbatim.
- The slow cadence `-m "evidence or census"`, whose trigger in both 002:27 and 005:27 is "the milestone close". Run it or record it as not run.
- The distribution-lane files edited but never run: `tests/test_public_distribution.py` (18→19, and the 13 MiB budget) and `tests/test_release_acceptance.py` (13 MiB). Both are `pytestmark = distribution`, an opt-in lane that D20 did not select, and auto=true does not authorize it. Record an owner selection, or name them as unrun.
- The review-helper status: 13 files unreviewed, including the close's own `tools/check_installed_docs.py`.
- The owner-statement receipt from R3-F7.
- A README update.
- Owner acceptance, recorded separately (plan §4 Close).
- No merge or publication.

## 5. Verification limits

- I did not read `evidence/close/` (uncommitted, in SOURCE) or the PR 317 remote state, so I could not see whether `1cbbc18d` is already public.
- I did not run the installed docs check or the full lanes.
- Code-level review of `4e1ae32c` was brief. The wheel declares one extra, `synth`, so "every extra" means `synth`.
- I could not verify the "fix the inputs first" branch claim in the recordings.

VERDICT: APPROVE_WITH_FIXES
