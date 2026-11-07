# Milestone close review (Codex), retained verbatim

- Instrument: one reviewer in a different tool, selected by the owner for the close ("One reviewer (Codex)", 2026-11-06), waiving the plan's panel bar. One reviewer is one reviewer.
- Command: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin, 116,293 tokens, exit 0.
- Reviewed bytes: the uncommitted close draft (012-milestone-close.md with its gate filled, plan with section 15) over dfce332e, the six phase records, README and the code.
- The output below is unedited; the trailing "codex exit=0" line is the driver's.

## Reviewer output (verbatim)

DISPOSITION: revise

ID: K1
SEVERITY: blocking
LOCATION: .gnd-planning/milestones/rule-check-adoption/012-milestone-close.md:134
QUOTE: Exact-term derived rings under version 15 | 007 | retired: moot under `--baseline`, which refuses structured-derivation models (RC3 spec, RC-D11)
PROBLEM: The refusal applies only to `--baseline`. `--rule-ids` still accepts structured-derivation models (008-phase-RC3.md:180), while RC2 explicitly leaves derived-ring extent untested (007-phase-RC2.md:218-223). The code can retain a version-7 cycle row when extent calculation finds no group (src/gnd/correspondence.py:1255-1264). The record therefore cannot retire this question or claim predicate 2 without qualification.
FIX: Give the `--rule-ids` case a named deferred target or resolve it with evidence; qualify predicate 2 if the owner accepts that limit.

ID: K2
SEVERITY: blocking
LOCATION: .gnd-planning/milestones/rule-check-adoption/012-milestone-close.md:133
QUOTE: Component index drift | 007 (I5) | resolved for this milestone: RC2-RC6 each recorded `0 to fix`, and at this close `components_index.py changed --base 508d6bec --strict` gives `271 file(s) differ; 0 to fix, 0 warning(s), 22 to reread`, exit 0
PROBLEM: `0 to fix` does not dispose of the 22 manual rereads. The component-index instructions require opening each flagged entry against its changed code (.codex/skills/components/SKILL.md:224-228); the close supplies no list or review of those 22 and says RC1 predates the check.
FIX: Record the reread disposition for all 22 entries, or carry the outstanding entries to a named target.

ID: K3
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/rule-check-adoption/012-milestone-close.md:93
QUOTE: The closing tree's failures are the two `tests/test_public_optional.py` uv-version pins, the same list (same sha256) as every phase base since RC2.
PROBLEM: RC3 and RC4 bases each also had a session-driver failure (008-phase-RC3.md:159-163; 009-phase-RC4.md:126-130), and the RC6 base had one too (011-phase-RC6.md:127-130). Their full failing lists were not identical to the closing list.
FIX: Say the same two uv-pin errors occurred in every base since RC2; distinguish the intermittent additional failures.

ID: K4
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/rule-check-adoption/012-milestone-close.md:16
QUOTE: so the two lanes differ only by the milestone's commits.
PROBLEM: The first-parent history from 508d6bec to dfce332e also contains unrelated PRs 102, 105 and 106. PR 102 includes the discovery-root test fix credited at close lines 95-98. The merge-base comparison is useful, but it does not isolate milestone commits.
FIX: Name the intervening PRs and limit the comparison claim to the observed failing-test sets.

ID: K5
SEVERITY: completeness
LOCATION: .gnd-planning/milestones/rule-check-adoption/012-milestone-close.md:143
QUOTE: They are applied as plan §15, keeping the prior wording
PROBLEM: Section 15 corrects O17’s table entry, but the same refuted “SCC code exists twice” premise remains in the plan’s implementability sweep (notes/rule-check-adoption-plan.md:556). The approved wording is preserved, yet that occurrence has no stated amendment.
FIX: Add a §15 amendment for the implementability-sweep sentence.

ID: K6
SEVERITY: completeness
LOCATION: .gnd-planning/milestones/rule-check-adoption/012-milestone-close.md:165
QUOTE: Merge, and the closing of issues 92-97, are the owner's.
PROBLEM: That range includes issue 95, which the plan and the close sweep assign to a separate milestone (notes/rule-check-adoption-plan.md:13-16; 012-milestone-close.md:137).
FIX: Name only issues 92, 93, 94, 96 and 97.

ID: K7
SEVERITY: completeness
LOCATION: .gnd-planning/milestones/rule-check-adoption/012-milestone-close.md:48
QUOTE: All six phases of rule-check-adoption (RC1-RC6) are on main
PROBLEM: Git history supports this claim, but README.md:8-11 still says RC6 is unmerged, and README.md:41-42 still directs the reader to open its PR. The milestone’s status file contradicts the close record.
FIX: Update the README status and next action before closing.

I checked the six phase records, approved plan and gate record, retained suite summaries and hashes, relevant tests, and the current implementation. Predicates 1, 3, 4, 5 and 6 have supporting code and focused evidence. The dfce332e scaffold fix matches the reported failure, and the closing suite’s two remaining errors match its evidence file.
codex exit=0

## Triage (driving agent, 2026-11-07)

Every finding was checked against the files it cites; all seven are accurate.

| ID | Disposition |
|---|---|
| K1 | qualified: predicate 2 holds for asserted rings; derived rings under `--rule-ids` deferred to issue 119 (owner ruling "File an issue") |
| K2 | resolved: all 22 entries reread against `git diff 508d6bec HEAD` (subagent, checked by the driving agent): 16 accurate, 6 stale (subsystem.check, cli.checking_command, model.address, check.service, check.snapshot_decision, infra.report_payloads), corrected in `dev/components/COMPONENTS.md`; index regenerated, `--check` exit 0 |
| K3 | fixed: the two uv-pin errors are in every base since RC2; RC3, RC4 and RC6 bases also had the intermittent session-driver failure |
| K4 | fixed: the intervening PRs 102, 105, 106 are named; the comparison is of failing-test sets |
| K5 | fixed: plan section 15 also amends the implementability-sweep sentence |
| K6 | fixed: issues 92, 93, 94, 96 and 97 only |
| K7 | fixed: README status and next action |

The corrected record was not re-reviewed.
