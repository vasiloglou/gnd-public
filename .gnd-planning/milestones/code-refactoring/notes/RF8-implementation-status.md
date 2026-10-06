# RF8 implementation — pending independent review

Historical pre-review status, superseded by014-phase-RF8.md on2026-10-06. Original claims and rejected transmission below are retained; the missing sentinel/cache findings are recorded in the completion record.

2026-10-06. This is an implementation status note, not a completion record.

Base: de4eed6ec143fdf03a39ab7a64b95a4e4013d24a.
Atomic move: a3e7c83. Verified production source:6a0875097ae3547bf829c3818606487cc63b4060.
Spec and amendments:phase-RF8-spec.md; original delegated-approved bytes are retained
in evidence/RF8/approved-spec.md with matching approval.json SHA.

Implemented immutable SessionProfile, closed reader dispatch/capabilities and runtime
wire selection; original v2 capture and wire/schema meanings remain. Shared evidence,
controller, environment, reconstruction and execution homes remove every measured
runtime SCC. The session_v7 shim is58lines and preserves original definitions plus47
imported bindings. Old qualification, publisher patch ownership and physical source
observers are controlled. SessionStore.best_identity()/best_record() expose validated
reconstructed selection; the compatibility _v7_best tuple remains.

## Selected evidence
All commands/results are retained separately under evidence/RF8; counts overlap,
so they must not be summed as an aggregate acceptance result.

| Gate | Result |
|---|---|
| Corrected pre-move RF1 session matrix |28passed31.27s|
| Atomic move session + metadata |29passed29.90s|
| Profile RF1 session matrix |28passed28.93s|
| G1 final profile/contract/dispatcher |84passed0.99s|
| Real best identity over v7/v8 retained evidence |2passed1.88s|
| Native3.11 final profile + all session replays |42passed30.58s|
| Native3.13 final profile + all session replays |42passed30.21s|
| Focused session/store/close/judgment consumers |515passed; exact descendant observer initially ps sandbox refusal, permitted retry1passed4.26s|
| Focused remaining CLI/helper/semantic/artifact/skill/scaffold pins |427passed2deselected36.75s|
| Final structure/layer/source controls |91passed16.36s|
| Lint |exit0 All checks passed!|

G2-complete-final retains the final source/mapping/source-scan controls and dirty
siblings. metrics-final.json:227modules, no module-level/runtime multi-module SCC,
no wrong-way or CLI entry violation. Frozen controls bind432 inputs in one counted list: original RF1 files and the
source-owned ledger/test.

The artifact primitive-name guard excluded from the passing G5 selection fails on
exact de4eed6 original source/test too: safefs.read_regular_file_bytes is treated as
a redefinition of an artifact-owned name. Original failure and archived predecessor
red remain evidence; its ownership ruling stays with milestone close. The other G5
deselection is configured lane policy. No blanket source exemption was added.

The initial v3 failures were a test runner PATH error: resolving the venv interpreter
symlink selected an interpreter without pytest. Before production edits, retaining the
venv bin path made both v3 cases green; all28 cases then passed. No answers recaptured.

## Budgets and boundaries
RF0 compare:3246 addedsource lines,2243 moved;1003 nonrelocated, including303
blanklines excluded from moved accounting. The original650 ceiling was missed and
explicitly re-targeted to1100; original90 touchedfile ceiling was missed and re-targeted
to120. Both misses remain for milestone close. Moved4000/test1600/doc1600 ceilings,
SCC0 and shim60 targets remain unchanged. Current budget.json binds measurements;
final record must recalculate touchedfiles including itself before completion.

Refactors EXECUTED: directed session dependencies, shared immutable version profile,
public reconstructed identity, exact compatibility/source observer homes. Existing
absolute prompt-path digest dependence and characterized missing-result resume refusals
remain RF1-OQ4/RF1-OQ2, owned by a session portability/controller successor; RF1-OQ7
original support debt remains untouched. RF7 strict input contracts remain binding.

No broad historical/evidence/census/proof/distribution/provider panel/certification
run, release, merge, shim retirement or source-owned authority transfer is claimed.
Local normalized replays cannot establish raw timing/nonces/producer equality or Linux,
installed or release acceptance. One reviewer is one reviewer; none has run for RF8 yet.

## Required review is pending
The native Codex high-effort read-only review was rejected before launch by automatic
approval review: RF8 phase approval did not explicitly authorize repository source/diff
transmission to the external Codex provider. The bounded prompt is retained at
 evidence/RF8/review-prompt.txt; existing native authentication would be used without
reading/sourcing any credential environment file. The owner has been asked to authorize
RF8 initial review plus at most one repair review. Authorization remains pending.

Required remaining work: run the independent review after authorization, reproduce
and triage findings, repair with proven pre-fix regression cases when required, perform
bounded repair review if warranted, write014-phase-RF8.md with computed hashes and
final gates, then push/update the existing draft PR. Completion is not established by
this status note or the implementation commits.
