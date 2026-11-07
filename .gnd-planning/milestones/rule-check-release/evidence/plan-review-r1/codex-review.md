# Plan review over r1 (Codex), retained verbatim

- Instrument: one reviewer in a different tool, selected by the owner (RL-D0, "Approve all as proposed (Recommended)", 2026-11-07, relayed by the session that started this one). One reviewer is one reviewer; the project's plan-review bar is the maintained panel.
- Command: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin, exit 0.
- Reviewed bytes: notes/rule-check-release-plan.md, sha256 52797ddbd830d752d600271805746b3de7424736191b494d53546b7fccd4f034, and notes/phase-RR1-spec.md, sha256 2e21de4797090fead0681c604ba0d479ab528ac33118270a7eefdbe99779e899, both at commit dbf98447.
- What the reviewer could not do: run the test suite or fetch external pages (its own statement at the end).
- The output below is unedited (it contains no home-directory path); the trailing "codex exit" line is the driver's.

## Reviewer output (verbatim)

DISPOSITION: revise

ID: P1  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/rule-check-release-plan.md:307  
QUOTE: “after it merges, new work adds a fresh `Unreleased:` section above the version's section”  
PROBLEM: RL-D2 requires FU2 and FU3 on main before RR2, but RR1 writes the 0.2.0 notes before they land. Following this instruction leaves changes included in the candidate outside its promised single version section.  
FIX: After FU2 and FU3 merge, reconcile their notes into the 0.2.0 section before building the candidate.

ID: P2  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/rule-check-release-plan.md:27  
QUOTE: “Every artifact whose bytes move with the version is listed from a measurement before code”  
PROBLEM: E1 measures only the default test lane. `tests/test_public_distribution.py` is wholly marked `distribution` and contains four literal 0.1.0 assertions; the spec explicitly excludes opt-in lanes from E1. A green E1 cannot establish “every artifact” or RR1-C4’s “no recorded byte moves unlisted.”  
FIX: Add a tracked-file inventory and select the relevant opt-in artifact checks, or narrow the completion claim and list the exclusions.

ID: P3  
SEVERITY: completeness  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/rule-check-release-plan.md:257  
QUOTE: “the post-publication patch (pins in README and installation, compatibility sentence, release-notes status, support rows, `v0.1.0` sentence in installation)”  
PROBLEM: The patch list misses install pins in `docs/index.md:144` and `docs/marketplace-plugins.md:10`. `docs/pyrel-apps.md:39-41` and six tutorial/how-to pages also tell readers to use a checkout until the next release. The O9 inventory says six docs contain `0.1.0`; `git grep` at its stated baseline finds thirteen.  
FIX: Correct the inventory and make the prepared patch cover every instruction made stale by publication.

ID: P4  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR1-spec.md:137  
QUOTE: “`RELEASED = {"0.1.0"}`, a tuple in this test file that the publication-day patch edits”  
PROBLEM: RR1-C3 says no test file names the old version as its own literal, yet the proposed new test does. RR3-C3 also omits this test from its publication-day patch, so moving the install pin to 0.2.0 would fail T3.  
FIX: State explicitly that historical published-version data is exempt from RR1-C3, and include its update in the prepared patch with a failing post-publication mutant.

ID: P5  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/rule-check-release-plan.md:172  
QUOTE: “an unknown option, a lower report version or a refusal), proving the probe can tell the releases apart”  
PROBLEM: The first proposed probe combines `--rule-ids`, report version 15 and `remedy`. The 0.1.0 source has no `--rule-ids`; its option refusal occurs before either output field is tested. The same masking affects the proposed acyclic-extent comparison. This distinguishes command availability, not each claimed carried behavior.  
FIX: Give each field and behavior an independently checked expected value and a negative control that reaches the comparable behavior; add a current-candidate mutant where 0.1.0 cannot reach it.

ID: P6  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/rule-check-release-plan.md:311  
QUOTE: “the close diffs `.github/`, `docs/releasing.md` procedure steps and settings against the base”  
PROBLEM: A git diff cannot inspect GitHub environments, repository settings, PyPI publisher registration or uploads, yet completion predicate 6 claims none changed. The implementability sweep also says no credential is needed, while its `git fetch` and proposed GitHub environment checks concern a repository the docs describe as private.  
FIX: Define dated read-only remote checks and their access requirement, or limit predicate 6 to actions and repository bytes this milestone can audit.

ID: P7  
SEVERITY: hardening  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/rule-check-release-plan.md:145  
QUOTE: “Observe at plan time (O3) and again in the dossier on the publication day; the freeze records both”  
PROBLEM: `docs/compatibility.md:3-5` requires version availability *before candidate freeze*. RR2 freezes a candidate before any publication day, and publication is outside this milestone. Neither proposed observation guarantees availability at RR2 freeze.  
FIX: Recheck availability at candidate freeze; require another check immediately before any later upload.

ID: P8  
SEVERITY: hardening  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/rule-check-release-plan.md:361  
QUOTE: “token upload of the owner's chosen files, as for 0.1.0, or `release.yml` with a validated Trusted Publisher and the `pypi` environment; the plan chooses neither”  
PROBLEM: The normative procedure in `docs/releasing.md:9-25` instructs creation of a Trusted Publisher and protected environment as the route to publication. RR3-C4 promises only a stale phase-wording edit “without changing a normative step,” leaving the dossier’s token route at odds with the stated one-home procedure.  
FIX: Make `docs/releasing.md` state the authorized routes conditionally, without configuring or invoking either one.

ID: P9  
SEVERITY: completeness  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR1-spec.md:158  
QUOTE: “D1 has since been ruled, the rest are open.”  
PROBLEM: D3 and D4 in the same table are marked ruled. The table also omits the cost of each reading for D3–D5 required by `spec-note-contract.md:74-84`. The proposed drift tests invoke an “agreement function” absent from the exact surface in §6, and T2’s lane command remains unresolved. The draft correctly blocks its own gate, but it does not yet meet the contract for that gate.  
FIX: Correct the decision status and costs; name the agreement function and exact T2 command and cases before submitting RR1 for approval.

ID: P10  
SEVERITY: completeness  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR1-spec.md:169  
QUOTE: “exit 0 (links in the changed notes resolve; workflow shape untouched)”  
PROBLEM: RR1-C5 also requires truthful candidate wording and no sentence claiming publication. `tests/test_release_docs.py` checks links, while `tests/test_release_preparation.py` checks workflow shape; neither fails on a false publication claim in the edited notes, compatibility page or support page.  
FIX: Add content assertions and a false-publication mutant for those documents, or name an explicit diff review as the criterion’s gate.

ID: P11  
SEVERITY: hardening  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/rule-check-release-plan.md:299  
QUOTE: “this widens no gap that is not already there”  
PROBLEM: Once RR1 merges, the plugin manifests would say 0.2.0 while the published runtime and the install commands still say 0.1.0. `docs/marketplace-plugins.md:63-65` explicitly tells users to keep those versions aligned. The existing skills/runtime feature gap does not make this new version mismatch disappear.  
FIX: Describe the temporary mismatch in installation guidance and give plugin users an actionable route until publication.

CHECKED AND FOUND TRUE

- At baseline `12daa5b7`, `uv.lock:100` and all three named manifests say 0.1.0; the marketplace test checks both plugin manifests and has a version mutant.
- `release.yml` has two builds, retained hashes and acceptance, and gates its upload job on `publish=true` on main. A later workflow run builds its own bytes.
- The release notes have twelve `Unreleased:` headings, and `v0.1.0..12daa5b7` contains 526 commits.
- FU2 and FU3 concern the population header and acyclic extent behaviors used to justify RL-D2.
- I could not run the test suite. I also could not independently recheck the dated PyPI/GitHub observations or the live issue text; the attempted external fetches failed.
codex exit=0
