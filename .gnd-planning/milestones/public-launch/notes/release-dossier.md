# Release dossier — preparation only

Origin: source public-launch r1/r2/r3 and approved phase-4 preparation spec;
this is a concise target successor, not imported historical assurance.

Phase 3 acceptance is recorded in ../004-phase-3.md for its exact candidate.
Phase 4.1 prepares revised documentation/resources. Phase 4 candidate sign-off pending. Package version 0.1.0 is
provisional; service ownership/version availability must be checked at freeze.
Release operator: repository owner. No publisher identity/environment configured
by this phase. TestPyPI omitted by delegated D6; service boundary untested.

Build tool: uv 0.10.10. Proposed profiles: Ubuntu/Python 3.11 and macOS/Python 3.13.
Preparation smoke results and hashes are in the preparation record; they are not
final regression acceptance. Phase 3 candidate hashes remain in its acceptance record. Phase 4.1 artifact
hashes will be recorded separately; none inherits the earlier acceptance. Release wheel and sdist
will be promoted unchanged; comparison wheel is separately identified.

License: Apache-2.0 owned code; NOTICE and scanner attribution retained. No fresh
certification: absent/stale assurance is unavailable. Trial target five, no
participants recruited and no trial success observed. No outreach or access
scope selected. Public URLs still require final availability checks.

Final acceptance checklist: selected behavior families; both wheel origins;
measured support matrix; no-key examples; target-only contributor exercise with
module/tool/both-root resolved paths; source commit and three artifact hashes;
full payload/history/service surface disclosure check; version and release
identity decisions. Publication is a later separately authorized step.

## Prepared input handoff — 2026-10-03

Prepared product commit: `5059dba` (full identity in the preparation record).
Focused gate: 98 passed, 1 deselected; both preparation wheel origins install
and run examples; staged package/fixture closure: 45 passed. These are preparation
results. The recorded artifact hashes are provisional smoke identities, not
accepted candidate files. Artifacts were temporary and are not retained for
promotion; the final candidate must be built once before resumed Phase 3 validates its
exact artifacts. Candidate sign-off follows those checks.
Historical note: Phase 3 was paused at preparation. Its later acceptance is
recorded in ../004-phase-3.md. The current sequence includes Phase 4.1 before
final candidate sign-off.
