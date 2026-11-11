# Plan review over r1 (Codex), retained verbatim

- Instrument: one reviewer in a different tool, selected by the owner (RN-D0, "Approve as proposed", 2026-11-10). One reviewer is one reviewer; the project's plan-review bar is the maintained panel.
- Command: `codex exec --ephemeral --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin, exit 0. Model: gpt-6.1-sol (the tool's configured default, from its own log).
- Reviewed bytes: notes/release-0.3.0-plan.md, sha256 f21e6bce6bd953a8a05423cf7819c7f63df363e968d3516d32cbec231c814a77, and notes/phase-RN1-spec.md, sha256 70418c41774374def54cbf325bd2495ae1019551f83e9e7828ce17ba7f53b7b3. Both were uncommitted working-tree files: these bytes are not in history, so the digests are checkable only against the reviewer's own confirmation below ("Both reviewed SHA-256 values match").
- What the reviewer could not do: write files, run the full suite, reach PyPI, the GitHub environments endpoint or beast-3 (its own list at the end).
- The output below is unedited (it contains no home-directory path); the trailing "codex exit" line is the driver's.

## Reviewer output (verbatim)

DISPOSITION: revise

ID: P1
SEVERITY: high
LOCATION: .gnd-planning/milestones/release-0.3.0/notes/phase-RN1-spec.md:87
QUOTE: “correct them, then repair whatever link the test reports next, listing each”
PROBLEM: M11 edits retained evidence whose exact bytes are already certified by a phase record. ossie-interchange/009-phase-OS1.md:33-34 pins evidence/OS1/spec-r1.md to b17b774364ce381b5ff3173a0b5546b377fec7a2044275ae31c45fc39a853353; I reproduced that digest. Changing even a link invalidates it. The repository already solves this problem through RETAINED_DOCUMENT_ORIGINS in tests/test_development_scaffold.py:73-149: preserve snapshot bytes, verify their digest, and resolve links from their original home.

A complete read-only traversal found four unresolved links across two retained snapshots: three in OS1/spec-r1.md and one in OS0/spec-r4.md. The proposed repair would therefore extend beyond the two initially reported links.
FIX: Preserve both snapshots. Register their original document homes and existing digests in RETAINED_DOCUMENT_ORIGINS, then rerun the reference check.

ID: P2
SEVERITY: medium
LOCATION: .gnd-planning/milestones/release-0.3.0/notes/release-0.3.0-plan.md:46
QUOTE: “patch is prepared and not applied (RN3).”
PROBLEM: The predicates apply simultaneously “on main after merge” (line 26), but predicate 8 requires the post-publication patch to be “on main” if publication occurs (lines 53-55). Publication makes predicate 6 false. This repeats the temporal problem recorded by the predecessor close at 005-milestone-close.md:174, which explicitly distinguishes “yes at RR3” from the subsequently applied patch.

There is another inconsistent ending: RN-D5 says “after publication” (line 339), while predicate 8 permits closing before publication.
FIX: Scope predicate 6 explicitly to the RN3 hand-over checkpoint. Make the pre-publication close branch agree with RN-D5, or require a separate owner amendment to select it.

ID: P3
SEVERITY: medium
LOCATION: .gnd-planning/milestones/release-0.3.0/notes/phase-RN1-spec.md:117
QUOTE: “open”
PROBLEM: D3, D4 and D5 remain open although the plan records their decisions as ruled:
- D3 corresponds to RN-D11, exclusions, ruled at plan line 345.
- D4 corresponds to RN-D10, fix both failures, ruled at line 344.
- D5 corresponds to RN-D3, notes shape, ruled at line 337.

The spec nevertheless retains an alternative that leaves the failures in place (line 118), and its status says it needs another D4 ruling (line 6). D2 also reopens the already selected re-record-versus-refactor method; only per-file handling remains deferred by plan lines 353-354.
FIX: Import the existing dated rulings. Restrict D2 to the post-E1 classifications and handling details. Remove the superseded “leave the failures” branch.

ID: P4
SEVERITY: medium
LOCATION: .gnd-planning/milestones/release-0.3.0/notes/release-0.3.0-plan.md:170
QUOTE: “`gnd evolve preview --policy additive --check-population`”
PROBLEM: This command returns 64: “argument --check-population: expected one argument”. It also needs MODEL, PROPOSAL, --workspace, --records and --out; see src/gnd/commands/evolve.py:34-75.

Likewise, the command at line 172, “gnd validate --document --require-documents”, returns 64, not the stated 3: --document needs a path, and validate needs MODEL.

The intended source-span behavior is reproducible with explicit inputs: the UG3 span-element model plus ledger.txt returns 3 with --require-documents; omitting the flag or supplying ledger.txt and annex.txt returns 0.
FIX: Write complete probe invocations with named fixture inputs and outputs. Specify how the tests materialize the proposal, population, model and documents outside the checkout; the existing UG2/UG3 corpora live under tests/, not the wheel.

ID: P5
SEVERITY: high
LOCATION: .gnd-planning/milestones/release-0.3.0/notes/release-0.3.0-plan.md:176
QUOTE: “Each probe has an availability control on the hash-pinned PyPI 0.2.0 wheel and, where one exists, a behavior mutant on the candidate.”
PROBLEM: Availability controls cannot establish candidate correctness. For example, a candidate validator that ignores includes would still validate the positive include example; 0.2.0 would still reject its version-5 schema. Both observations would satisfy the stated probe while pin verification was broken.

Behavior controls exist for every proposed feature: changed sidecar/ontology bytes, a deliberately wrong identity digest, a changed include pin, a violating population, and complete document coverage versus an unchecked span. Making them optional weakens the predecessor’s explicit two-control requirement at rule-check-release-plan.md:281-284.
FIX: Require a named candidate behavior control for each probe, with explicit assertions and expected exits. Include rejection of a mismatched include pin and refusal of the constraint on violating data.

ID: P6
SEVERITY: medium
LOCATION: .gnd-planning/milestones/release-0.3.0/notes/phase-RN1-spec.md:102
QUOTE: “One row per merged pull request of plan N9”
PROBLEM: A pull-request-level reconciliation can miss multiple externally visible changes within one PR. The current release notes omit:
- PR 68: prepared-policy reuse now rechecks mutable hashability on Python 3.14; src/gnd/incremental_state.py:463-469, commit 1a7411a8.
- PR 136: coverage accepts a schema-valid null derivations collection; src/gnd/coverage.py:852. The same PR also fixes null derivations in transition snapshots and redaction diff projection; src/gnd/exp/session_eval.py:1490-1514 and src/gnd/redaction.py:786.
- The Ossie work repairs role names in three packaged model-authoring examples: issueNumber → issue_number, occurredOn → occurred_on, startDate → start_date, and fullName → full_name. These changes appear in git diff v0.2.0 HEAD -- src/gnd/skills/gnd-model-from-text/examples.

The spec acknowledges the first two PRs need reconciliation, but does not enumerate their separate changes or the example repairs. A generic Ossie note could satisfy the PR row while omitting those repairs.
FIX: Reconcile by user-visible change within each PR. Add the missing fix notes and explicitly classify the packaged-example repairs.

ID: P7
SEVERITY: medium
LOCATION: .gnd-planning/milestones/release-0.3.0/notes/phase-RN1-spec.md:25
QUOTE: “M7 to M9, T2, T3”
PROBLEM: T2/T3 do not establish RN1-C4’s support statement or plugin repository route. tests/test_release_version.py:76-86 rejects positive publication claims; it accepts an empty support page. Its pin helper checks version membership, not installation-route guidance. tests/test_marketplace_plugins.py checks bundle structure, not that page’s instructions.

I exercised the actual helpers in memory: a heading-only release note, empty support text, and a plugin pin at 0.2.0 were accepted. Thus the declared gates cannot fail missing RN1-C3 content or these RN1-C4 requirements. T5’s release-doc test checks links (tests/test_release_docs.py:10-14), not release-note completeness.

RN3-C4 is similarly only an edit restriction: doing nothing cannot fail it even when stale prose remains.
FIX: Name a failing check or reviewable completeness diff for each missing requirement. Give RN3-C4 a required stale-text inventory and disposition, including the no-edit outcome.

ID: P8
SEVERITY: medium
LOCATION: .gnd-planning/milestones/release-0.3.0/notes/release-0.3.0-plan.md:50
QUOTE: “checks (environments, `release.yml` runs, releases, the PyPI simple index).”
PROBLEM: Predicate 7 forbids creating a tag, but none of its remote checks inventories tags. A bare tag can be created without changing environments, workflow runs, GitHub releases or PyPI. The proposed evidence would not detect that violation. The predecessor explicitly added a remote-tag audit after review; see 003-phase-RR2.md:183.
FIX: Record dated remote-tag inventories at baseline and close, including peeled identities. Distinguish observed remote state from claims about which actor performed an action.

ID: P9
SEVERITY: low
LOCATION: .gnd-planning/milestones/release-0.3.0/notes/phase-RN1-spec.md:35
QUOTE: “The standing rules, bound to this phase”
PROBLEM: This section omits named dispositions for plan rule 4, “Evidence belongs to exact bytes”, and rule 5, “Carrying is shown by running”. spec-note-contract.md:40-44 and standing-rules.md:10-13 require every rule to be bound by name or argued inapplicable. Rule 4 has a material subject here: M11’s retained snapshots. Rule 5 belongs to RN2 and can be explicitly marked inapplicable to RN1.
FIX: Add those two dispositions and cite the snapshot-preservation check for rule 4. Also bind the size stop rule explicitly after E1 establishes the estimate.

Checked and found true

- Both reviewed SHA-256 values match the requested bytes. The working tree remained unchanged.
- N4: HEAD and remote main are 2490dd77; PRs 160 and 161 are merged with the stated merge identities; the connected GitHub API returned no open PRs.
- N7: git rev-list --count v0.2.0..HEAD returned 213. The specified package-input diff returned exactly 109 files, 9170 insertions and 675 deletions. The tag peels to 7c0f4d0e.
- N8: one Unreleased section, seven subsections, no Ossie mention.
- N9: the named feature families and four fix PRs are represented in the local history. PR 136 includes the additional snapshot/redaction fixes described in P6.
- N10: the Ossie commands and four schema files exist; neither release test directly exercises installed Ossie interchange.
- N11: ossie_oracle is excluded by pyproject.toml:73.
- N12: the stated grep exclusions produce exactly 20 files with the stated category counts.
- N15: RELEASED and the publication, pin and date-placeholder assertions match the description. M4 is correct: all 22 existing cases passed against an in-memory 0.3.0 tree with RELEASED unchanged and pins at 0.2.0. The synthetic 0.2.0 literals in mutant tests do not require changing.
- N16: acceptance retains the hash-pinned 0.1.0 control and rule-check probes.
- N20: reproduced “assert 141 <= 90”; selection returned 1 failed, 2 passed.
- N26: reproduced the first broken OS1 snapshot link. The complete traversal found the four links described in P1.
- N23: local uv is 0.10.10; both workflow pins agree.
- N25: both stated reader incompatibilities appear in the notes.
- N6, workflow portion: all 104 remote workflow runs were inspected across two API pages; none was release.yml.
- The retained 0.2.0 wheel and sdist match N17’s full hashes. Importing directly from that wheel confirmed all five intended availability distinctions: Ossie export/import, --identity, --check-population and --require-documents return 64; the version-5 include model returns 3. This used retained bytes, not a fresh PyPI download.
- Current identity output returned two lines and exit 0; the pinned sales include model validated with exit 0. The refunds renderer generated ontology, sidecar and loss-report bytes in memory.
- No phase step explicitly uploads, tags, creates a GitHub release or edits a workflow. The publication stage reserves those acts to the owner and requires fresh requests.
- Falsifiers available for completion predicates: 1—version pytest and lock check; 2—grep/E1 classification diff; 3—content reconciliation, with P6/P7 gaps; 4—installed probes, with P4/P5 gaps; 5—retained-candidate acceptance; 6—dossier/patch diff, subject to P2; 7—repository and remote-state comparisons, subject to P8; 8—served hashes, fresh index install and applied-patch diff; 9—spec, gate, review and question-disposition records.
- Named-criterion audit: RN1-C1/C5 have version-test falsifiers; C2 has inventory/E1 comparison; C3/C4 have the gaps in P6/P7; C6 has the base/candidate failing-ID comparison; C7 has the two named test nodes. RN2-C0 uses notes reconciliation and index availability; C1 uses builds/checksums; C2 uses independent hash comparison, with differences intentionally nonblocking under inherited RL-D7; C3 uses acceptance; C4 has P4/P5’s gaps; C5 uses uvx --version; C6 uses recorded profile evidence. RN3-C1/C2 use dossier diffs against candidate evidence and required owner actions; C3 uses patch applicability and stale-text checks; C4 has P7’s no-edit loophole.
- The RN1 spec contains all eleven required sections. T1-T8 map back to phase criteria or the harvested RR1 regression obligations; I found no wholly orphan test entry.

Could not check

- N5: current PyPI versions, file count and 0.3.0 availability. Both public index/JSON fetches failed with “Cache miss”; shell network access is restricted. Historical records do not establish current availability.
- N6, environment portion: gh failed connecting to api.github.com; the connected GitHub tool does not expose the environments endpoint.
- N22’s current beast-3 directory and non-interactive PATH: SSH failed resolving beast-3. The predecessor records support the inherited account, but I could not reproduce its current state.
- N26’s complete “1 failed, 83 passed” file result: only the read-only failing node was executed; other cases require temporary-file writes.
- E1, fresh installations, candidate builds, installed-wheel acceptance and isolated execution of all five future 0.3.0 probes: these require writes and the candidate does not yet exist.
- Owner-ruling provenance outside the supplied repository records, PyPI account settings and exclusive publication authority: no independent evidence was available.
codex exit 0
