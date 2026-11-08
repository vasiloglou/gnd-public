# Codex review of the RR3 implementation

Reviewer: Codex (`gpt-6-sol`, `model_reasoning_effort=xhigh`, `--sandbox read-only`, prompt on stdin), 2026-11-08. Reviewed bytes: `git diff b3071a79 62ba6fd4` (the `docs/releasing.md` edit, its test, the three unapplied patches, the stale-text check, the dossier and the check record). Dispositions are in the record, [`004-phase-RR3.md`](../004-phase-RR3.md). Verbatim output follows.

```text
DISPOSITION: revise

ID: J1  
SEVERITY: blocking  
LOCATION: docs/releasing.md:44  
QUOTE: “records the exact source commit, independent artifact hashes, observed profiles and selected regression results”  
PROBLEM: Compared with `git show 12daa5b7:docs/releasing.md` lines 33–36, this drops the requirement to record target-only contributor realpaths and the statement that candidate sign-off requires those results. The claim that no normative step was lost is false.  
FIX: Restore both requirements in route-neutral wording.

ID: J2  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/rule-check-release/evidence/RR3/stale-text-check.sh:29  
QUOTE: `git grep ... > "$HITS"`  
PROBLEM: The script uses `set -u` but never checks the exit status of `git grep` or the later `grep`. A search error, or an empty `HITS` file after publication, can reach the clean exit at line 37.  
FIX: Distinguish zero matches from search errors, fail on errors, and require the expected nonempty hit set.

ID: J3  
SEVERITY: hardening  
LOCATION: .gnd-planning/milestones/rule-check-release/evidence/RR3/stale-text-check.sh:31  
QUOTE: `PUBLICATION_DATE/<DATE>`  
PROBLEM: Normalisation makes an unreplaced `PUBLICATION_DATE` match the allowlist. The saved T5 run confirms the checker exits 0 with the placeholder still present. The D2 pytest guard fails, but the claimed property of this script is false.  
FIX: Reject `PUBLICATION_DATE` before date normalisation.

ID: J4  
SEVERITY: hardening  
LOCATION: .gnd-planning/milestones/rule-check-release/evidence/RR3/stale-text-check.sh:30  
QUOTE: `grep -i -E 'not published|prepared'`  
PROBLEM: This does not check the release-notes opening as classified in spec §6.2. An opening that still calls 0.1.0 the latest published release, with those two words removed, is invisible to the checker.  
FIX: Check the expected publication-state opening and 0.2.0 heading directly.

ID: J5  
SEVERITY: hardening  
LOCATION: .gnd-planning/milestones/rule-check-release/evidence/RR3/stale-text-check.sh:27  
QUOTE: “Observed in release acceptance of the 0.2.0 candidate built from `7c0f4d0e`”  
PROBLEM: This row is allowlisted for either route. D3 and dossier action 6 require it to be dropped or reworded if the workflow publishes its own build, so the checker can accept the wrong support row for that route.  
FIX: Make the support-row check depend on the selected publication route and build identity.

ID: J6  
SEVERITY: hardening  
LOCATION: .gnd-planning/milestones/rule-check-release/evidence/RR3/dossier.md:99  
QUOTE: “The changes since `7c0f4d0e` are tests and planning files.”  
PROBLEM: At HEAD, the changes also include `docs/releasing.md` (39 insertions, 24 deletions). The sentence is unqualified even though it describes a future workflow build after RR3 lands.  
FIX: Date and scope the observation to the checked `main` commit, then reassess the changed files before any workflow dispatch.

ID: J7  
SEVERITY: completeness  
LOCATION: .gnd-planning/milestones/rule-check-release/evidence/RR3/checks-T1-T7.txt:16  
QUOTE: “T5 liveness … exit 1”  
PROBLEM: Spec §8 requires the RR3-tree T5 run to print the stale hits. The record gives only `exit 1`, including on the rerun at lines 57–59, so it does not show that required behavior.  
FIX: Retain the checker’s stale-hit output for that run.

ID: J8  
SEVERITY: completeness  
LOCATION: .gnd-planning/milestones/rule-check-release/evidence/RR3/dossier.md:16  
QUOTE: “Comparison wheel | built from the sdist; identical to the release wheel”  
PROBLEM: M1 §A calls for all three artifact filenames and SHA-256 values. This row omits the comparison wheel’s path and filename and gives its hash only by reference.  
FIX: Record `comparison/get_nick_done-0.2.0-py3-none-any.whl` and its full SHA-256 value.

CHECKED AND FOUND TRUE

- Each of the three unapplied patches passes `git apply --check` individually.
- The frozen workflow and `tests/test_release_preparation.py` are unchanged; the worktree is clean.
- The D2 and D5 additions can fail: the saved mutant runs show failures for an unreplaced date and an old install pin.
- The incident wording and official service references in `docs/releasing.md` are unchanged.

COULD NOT DO

- Run pytest or apply patches in a scratch tree under the read-only constraint; I inspected the retained run record instead.
- Independently verify the outside-git artifact sizes and retained copies, or the dated remote PyPI and GitHub observations.
```
