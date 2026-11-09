# Milestone close review (Codex), retained verbatim

- Instrument: one reviewer in a different tool, selected by the owner for the close ("One Codex reviewer", 2026-11-09, relayed by the session that started this one). This replaces the plan's panel bar for the close, as at the rule-check-adoption close. One reviewer is one reviewer.
- Command: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin, 89,831 tokens, exit 0.
- Reviewed bytes: the draft close as committed at `71df1b99` (the head of PR 143): `005-milestone-close.md`, the plan with the draft §12, the README, the four earlier records and the evidence they cite. The prompt said the closing full lane was running separately and was not yet in the record.
- The output below is unedited. The trailing "codex exit=0" line comes from the driver.
- Triage: [005-milestone-close.md](../005-milestone-close.md), "Close review".

## Reviewer output (verbatim)

DISPOSITION: revise

ID: L1
SEVERITY: blocking
LOCATION: .gnd-planning/milestones/rule-check-release/005-milestone-close.md:109
QUOTE: **as amended (§12)**
PROBLEM: The table treats predicates 6 and 7 as amended, but plan §12:459 says the amendment is a draft, and the close record itself says it applies only under the close ruling (line 164).
FIX: Mark both rows as proposed readings pending the owner’s §12 and close rulings.

ID: L2
SEVERITY: blocking
LOCATION: .gnd-planning/milestones/rule-check-release/005-milestone-close.md:110
QUOTE: the rest holds once the close review runs
PROBLEM: Predicate 7 also requires every open question to be disposed. The record still proposes two residuals and awaits a target for the fixtures refactor (lines 149, 151, 157, 196–197). The review alone cannot satisfy it.
FIX: Say predicate 7 remains pending those dispositions and the close review.

ID: L3
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/rule-check-release/005-milestone-close.md:109
QUOTE: no phase uploaded or changed anything
PROBLEM: The cited remote check records the current environments and workflow runs (evidence/close/remote-state-2026-11-09.txt:3–10); it does not audit repository settings or PyPI publisher configuration. The dossier explicitly calls release authority “not auditable here” (evidence/RR3/dossier.md:68–70). Plan §12:471 makes the same stronger claim.
FIX: State the observed `.github` diff, environment list and run count; leave settings and publisher configuration unverified.

ID: L4
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/rule-check-release/005-milestone-close.md:137
QUOTE: ## Open-questions sweep
PROBLEM: The sweep omits the dossier’s owner checks for exclusive release authority and confirmation that every breaking change has a migration note. The dossier marks authority open and the migration list incomplete (evidence/RR3/dossier.md:68–79); the close contract requires raised questions to be dispositioned (milestone-record-format.md:186–190).
FIX: Add a sweep row giving each check its evidenced status or a reason it is retired from this milestone.

ID: L5
SEVERITY: completeness
LOCATION: .gnd-planning/milestones/rule-check-release/README.md:8
QUOTE: This milestone prepares a release and does not publish one: no upload, tag, GitHub release, `pypi` environment or publisher registration, and issue 118 stays open until a published release is verified.
PROBLEM: The same README says 0.2.0 is published and issue 118 is closed (lines 5, 31–37); the close record confirms both (005-milestone-close.md:67–73).
FIX: Make this a historical description of the three preparation phases, then state the present publication and issue status.

ID: L6
SEVERITY: completeness
LOCATION: .gnd-planning/milestones/rule-check-release/005-milestone-close.md:27
QUOTE: exit: "PENDING -- instrument not selected"
PROBLEM: The owner has now selected “One Codex reviewer.” The pending-instrument statements at lines 132–135 and 193–194, and README.md:40, are stale.
FIX: Record the owner’s selection; add this review’s disposition when incorporating it. Keep the close ruling pending.

ID: L7
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/rule-check-release/005-milestone-close.md:14
QUOTE: command: "predicate 6, read-only (2026-11-09T03:27:33Z, tree afc5bd8f): git diff 12daa5b7 HEAD -- .github; environments; release.yml runs; gh release list; v0.2.0 assets; remote tags; PyPI version JSON, simple index and project JSON; issue 118 state; package inputs since 7c0f4d0e"
PROBLEM: This is a shorthand for several checks with one exit. The draft also uses both `gate` and `gates` (lines 9–13) and has no verbatim gate-output section. The format requires `gates` for multiple selected gates, each with its own command and exit, and verbatim output (milestone-record-format.md:59–61, 76–79, 106–108).
FIX: Use one `gates` list with the exact recorded commands and exits, citing the retained remote-state output. Keep the relayed CI result explicitly labelled as lacking logs.

ID: L8
SEVERITY: completeness
LOCATION: .gnd-planning/milestones/rule-check-release/005-milestone-close.md:141
QUOTE: closed: yes, one row (RR3 patch), on main by PR 140 (`c239ad8e`)
PROBLEM: The close relies on the current support row and release notes (also line 154), but its evidence list binds neither current document by path and SHA-256. The close skill requires artifact hashes (process-milestone/SKILL.md:137–142).
FIX: Add hashes for the current post-publication documents used to establish those close claims.

CHECKED AND FOUND TRUE:
- HEAD is 71df1b99; git history contains the cited PR 137, 140 and 133 merges.
- All eight SHA-256 values listed in the draft’s evidence block match the checked files.
- The draft’s relative Markdown links resolve; the retained publication evidence reports wheel and sdist hashes matching the dossier.
codex exit=0
