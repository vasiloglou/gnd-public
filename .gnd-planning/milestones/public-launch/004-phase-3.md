---
milestone: public-launch
station: "phase-3"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-3
date: 2026-10-03
gate:
  command: "uv run pytest -q tests/test_guarded_corpus.py tests/test_v70_phase3_successors.py tests/test_public_correspondence_projection.py tests/test_public_correspondence_runtime.py tests/test_public_v72_semantic_owners.py tests/test_public_v72_semantic_owner_inputs.py --tb=short"
  exit: 0
  output: "353 passed, 1 deselected in 18.04s"
slow_gate:
  command: "uv run pytest -q -ra --tb=short"
  exit: 0
  output: "11355 passed, 1 skipped, 400 deselected, 1 warning in 3426.54s (0:57:06)"
  note: "Owner-selected full target default suite; macOS result recorded below. Historical/native/provider lanes remain separately selected."
evidence:
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/attempts.json
    sha256: 9c0a267c01693ce9c03652420bba250061cbd8d618d5bc7c7b5cf99c45f1919d
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/authored-line-accounting.json
    sha256: 61404450f853d50c833ebd0fdb73c1a727feb7e39b6959cbfdd68359990869cb
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/benchmark-observations.json
    sha256: b075ff93c604d55099f476b67023bdc63081f5ba3226d5c5046b2787201e3c56
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/candidate.json
    sha256: 550b2c171c19d9049b820891aeab3f0ae97f2cc4c78d9344706af74ffeefd856
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/candidate.txt.gz
    sha256: 71a3a7dab7f0f746251313f401a8a262c99a633b5092dfb95aa03972b3962ac8
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/macos-installed.txt.gz
    sha256: 72345b75c6b6396f9e255ca021191bac217b3fe98ac12808d3926bdb839a923a
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/macos-regression.txt.gz
    sha256: 12fb05168ca77d65dde40e36551c8590588643f7449e389e9ea36bb4ac909c84
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/main-protection.json
    sha256: d009520e51228cd79a4a65dee6b2892bf2740b8f7df7e30ce5db6d1c6f2711c8
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/occurrence-identity-red.txt
    sha256: 51dbaf7b097e04069fac9030d944f5128fe659ef8cd1d00cb137cf217f469ffe
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/occurrence-instrument-controls.txt
    sha256: d474504b2f6b3a856129874c440327228c3d1d1b9c565ae6d647055e091b3878
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/occurrence-lint.txt
    sha256: 82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/occurrence-repair-311.txt
    sha256: 46470200f5f0c7e9d44916bc2c8204d9d210ee27e58b5cc3ffd159b74ca123f1
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/occurrence-repair-green.txt
    sha256: 57bd69347c3a40cd13064d575edd39fed9f659fbe02f71d21f99a9541e179348
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/phase2.txt.gz
    sha256: ba655e466b0d4e63baad15de0ee8ebb946e72b6faa57eafb9e0221c3187e3647
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/qualification-measurements.json
    sha256: b0f4ead10d75292f7a16f1c11a7d75849e05989a7c0ed1a76a7bac768f64364e
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/run.json
    sha256: abe010f6ed27b75552998ccec3573d27f8524eb77c6935a6ad14ff033794a738
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/ubuntu-installed.txt.gz
    sha256: b6f52ad6c096e5afb14f489bb2cc25ac24bfadf7002538e461920d22ca01ad65
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/ubuntu-regression.txt.gz
    sha256: 4a7391166e2d8b4f9362a51435dbc9013ba98917b135d32f191f465c6162f83c
  - path: .gnd-planning/milestones/public-launch/notes/phase-3-family-selection.md
    sha256: 78c620c74ef5a477ab50e82180a7f3764bee8986c40af4934f2c431fdd09e0bf
  - path: .gnd-planning/milestones/public-launch/notes/phase-3-source-delta.md
    sha256: 982107198d3c1f97ad58fdca929b97946ac5e86cad630eed8f36e211c64ed113
  - path: .gnd-planning/milestones/public-launch/notes/phase-3-review-disposition.md
    sha256: 4b09783bdab5fac266544aa1ae172a2cc83bc06048ee7c58746ec91e0be63510
  - path: .gnd-planning/milestones/public-launch/notes/phase-3-benchmark-amendment.md
    sha256: c7062489f5807b0667e85352c732f9d52a19511e12c3554c2f38bf1e6b09b457
  - path: .gnd-planning/milestones/public-launch/notes/phase-3-resumption-approval.json
    sha256: d7baf0b6be12b8d4e57718afac891566ea7bcf636e24c7d65428d24d478e85a1
  - path: .gnd-planning/milestones/public-launch/notes/phase-3-codex-review.md
    sha256: 4b97e4f37676d48086422f35918bbc8827bc7dacd5c7de019c77169a6f1fba5e
  - path: .gnd-planning/milestones/public-launch/notes/phase-3-codex-followup.md
    sha256: 92f91262e55803944943a2bc0512e1287105d234dc57a436bc4c1c2f1e36b03e
  - path: .github/workflows/development.yml
    sha256: c33d3fcd53d7e7e0a4f4b1167a785338b852714a5b732b7307393f8ea1fbb5d7
  - path: tests/test_release_acceptance.py
    sha256: d0ce2f128a49c6c04dfb91ff464aae62759435e1aeae79b88ac6b83c77748bbc
  - path: tests/test_guarded_corpus.py
    sha256: 4b0ead718400d05852a0010d39d1fbfa37a3f8cd59a1d1291552de90ab559b9b
  - path: src/gnd/correspondence.py
    sha256: 11b07bf147abf2432417910cc193371d92f14f36d47cdbbe28854b1085dc63c1
  - path: src/gnd/semantic_adapter.py
    sha256: 3f883b4fe4289886af08a1803b31ec6ee7d22c486b6fa208999585fde4e4b4d5
  - path: AGENTS.md
    sha256: 157e12b3e7f13d8b3040696b65bcec5536a0a6722c7f88b4d2ad208b569c7da8
  - path: CONTRIBUTING.md
    sha256: 845ac49cddf86c772e04d24936b987e06ccad4ad3502c64388d2215f88205991
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/completion-bounds.json
    sha256: 1da999ee24216a7c6129ad9567db6348f063833f78614f9141b60d118f0368a9
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/origin-regression-red.txt.gz
    sha256: 0bddbf4a61df7bab86feef0332b3d876fe1b20bc113ffc07879d13cb2e0d2938
  - path: .gnd-planning/milestones/public-launch/evidence/phase-3-qualified/qualified-evidence-sha256.json
    sha256: da1f275f896af50dcf4f8ff148318732f9e06d6a284baa397fc501df6584a0fa
---

# Phase 3 candidate acceptance

Acceptance passed for target commit c63b90cc3b26c89487e72d7f054a30b387824442,
GitHub run 37158889273. The completion commit adds records and retained evidence;
it is not a new qualified candidate. PR 1 remains the delivery route.

## What shipped

The target retains current regression families, fixtures, package resources,
installer controls and both skill discovery roots. Historical accounting stays
identifiable outside the ordinary default selection; collection is not execution.
The retained-artifact runner tests release and sdist-built wheels in isolated
installations, with import-origin, resource, optional-refusal and contributor checks.
The workflow builds once and checks the same artifacts on both platforms.
Main requires a PR and strict phase2 checks, enforced for administrators, with
force pushes and deletion disabled and no standing PR bypass. Owners retain
GitHub settings authority. The repository remains private and the PR unmerged.

The owner-approved benchmark amendment uses nine alternating paired measurements,
medians, relative MAD at most 10%, and median20k <= max(2.2*median10k, 0.2).
The multiplier supplies 10% engineering tolerance above ideal doubling. Every
sample retains the two-second limit and exact verdict/binding-count checks.
Normal GC, workloads and bounded subprocess execution remain. This is a noisy
performance guard, not a statistical confidence interval or asymptotic proof.

## Gate output (verbatim)

Focused command in gate, exit 0:
353 passed, 1 deselected in 18.04s

Local Python 3.11: uv run --python 3.11 pytest -q tests/test_guarded_corpus.py tests/test_v70_phase3_successors.py --tb=short, exit 0:
124 passed, 1 deselected in 12.47s

Full default target command: uv run pytest -q -ra --tb=short, exit 0 on both profiles:
macOS: 11356 passed, 400 deselected, 1 warning in 1557.65s (0:25:57)
Ubuntu: 11355 passed, 1 skipped, 400 deselected, 1 warning in 3426.54s (0:57:06)

Retained installed command: GND_CANDIDATE_DIR="$PWD/candidate" uv run pytest -q -o addopts='' tests/test_release_acceptance.py -s --tb=short, exit 0:
macOS: 10 passed in 866.25s (0:14:26)
Ubuntu: 10 passed in 1582.25s (0:26:22)
Each platform/origin passed 1803 behavior and 85 contributor cases. Four selected
historical/slow cases were expressly deselected; no unexpected installed skip.
The one Ubuntu full-suite skip is the case-alias inventory control on a
case-sensitive filesystem; it executes on macOS. The serialization warning is
from a deliberately malformed-feedback control. Raw job logs retain details.

uv run ruff check tests/test_guarded_corpus.py tests/test_release_acceptance.py src/gnd/correspondence.py src/gnd/semantic_adapter.py, exit 0:
All checks passed!

Acceptance-runner and scaffold controls, exit 0:
17 passed, 1 deselected in 3.94s

## Measurements and candidate identity

Observed profiles: Ubuntu 24.04.5 x86_64, Python 3.11.16; macOS 26.6.2 ARM64, Python 3.13.15; uv 0.10.10.
All six jobs, including the required phase2 aggregate, succeeded.
Wheel and comparison wheel SHA-256:
21287a865e2487db98684097e44ff7f15d9dbc9b0657fc955bf43ab52a97c870
Sdist SHA-256:
a0698f1eb0dd5134f1cac005488efe2ea8fe036f07c4d82410eb7a0d8876ff67
The retained candidate directory is candidate/ci-37158889273 in the target;
GitHub retention is 30 days. P4 must inspect these actual bytes for sign-off.

macOS timing medians: [0.08957795800006352, 0.17883958300001268]; relative MAD:
[0.05113841733235959, 0.022085435079250527]; ratio 1.9964686290335605.
Ubuntu timing medians: [0.2202607709999711, 0.45051988499994877]; relative MAD:
[0.0028595559576975378, 0.010895461362288167]; ratio 2.0453932080352515.
Raw samples are retained. Synthetic controls discriminate jitter, dispersion,
non-finite/incomplete samples, limits, non-linear growth and incorrect reports.

Before records: tracked bytes 16579248 < 64 MiB; largest ordinary blob 584130
< 1 MiB; wheel payload 5594803 < 12 MiB; planning Markdown 258728 < 2 MiB.
Conservative authored-line upper bound 946 < combined 960 before final records.
Sixteen packaged skills; each discovery root has sixteen generated links and two
real unmanaged skills. Of 231 common package files, 230 match source exactly;
only target correspondence.py differs. Source runtime was not changed by this work.

## Findings and review

Attempts 1–5 remain failed/canceled, with original candidate identities and logs.
Missing checkout inputs, fake-Souffle ambient dependency and orphan-pipe scheduling
were reproduced and repaired. The owner accepted both legitimate failure labels
without removing cleanup/termination/no-late-write guarantees. Attempt 4 missed
an ideal-doubling threshold by 1.428059 ms (0.42%); the benchmark contract was
explicitly amended before implementation, rather than interpreting that run as green.

One reviewer is one reviewer. One independent read and one follow-up exhausted
the two-call budget; this is not a panel. The reviewer could not establish full
suite success from a read-only review. Reproduced instrument findings and their
pre-fix controls remain in the review disposition. Later benchmark/identity repairs
carry focused and hosted execution evidence, not another independent opinion.

Attempt 5 exposed a real provenance regression from scalar interning. Equal,
immutable values did not preserve occurrence identity: downstream origin lookup
uses object identity. Two original end-to-end assertions and the new distinct-
occurrence control reproduced red. The adapter was restored byte-for-byte; the
original assertions were unchanged. The replacement attempt is disclosed as an
agent correction under existing repair authorization, not a new human approval.

## Refactoring review

Refactors EXECUTED: correspondence binding construction reuses validated initial
candidates and shared-position joins while retaining duplicates, ordering,
canonical identities and work charges. Reference-evaluator parity, exact-work
boundaries and original admission/provenance controls pass. Scalar interning was
removed entirely. No additional runtime refactor is proposed for this phase.

## Boundary — what this phase does NOT establish

“retaining historical evidence does not recertify moved code; public CI does not
silently expand to every historical or live lane.” Observed profiles are not a
universal platform promise. Current default/installed execution does not discharge
historical broad-suite reds, live provider/native success or assurance claims.
No certification was requested or run; old certificates remain bound to old bytes
and assurance for changed evidence is unavailable. Reviewer agreement is not proof.
The final records/evidence commit has no new full qualification; acceptance binds
only the stated candidate commit and artifact hashes. P4 sign-off, P5 publication,
visibility changes, source retirement and authority transfer remain separate.

## Open questions

All 218 imported IDs, states, owners and triggers remain unchanged.
OQ-V72-P1-ARTIFACT-COPIES and OQ-V70-CLOSE-BROAD-REDS remain source-held.
OQ-PUBLIC-LAUNCH-P2-BUILD-PROFILE is answered only for these observed profiles.
P4 owns retained-candidate sign-off; P5 owns publication, PL-D5/PL-D10 and any
release/version decision. Source retains unit and publisher ownership until an
explicit handoff. No question closes merely because tests moved or passed.

## Refuted premises

The zero-runtime estimate was false: the target join allocation needed a bounded
repair. Scalar immutability/equality did not justify shared occurrence objects;
the provenance reds refuted it and the adapter restoration removes that premise.
Three-sample ideal doubling was too fragile to interpret a 0.42% miss as useful
regression evidence. More samples and declared tolerance improve the instrument;
they do not retroactively accept the old failure. Historical completion-count
accounting was not a valid current acceptance prerequisite under approved r3.
