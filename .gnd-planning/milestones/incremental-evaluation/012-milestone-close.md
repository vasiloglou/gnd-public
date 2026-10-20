---
milestone: incremental-evaluation
station: milestone-close
skill: process-milestone -- repository development
scope: milestone-close
date: 2026-10-20
gate:
  command: "UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache uv run --offline python .gnd-planning/milestones/incremental-evaluation/evidence/IE6/audit.py"
  exit: 0
  output: "data-only IE6 audit exit 0"
  note: "Pre-close data-only audit; --close subsequently checks final acceptance subjects. Runtime gates are retained in011."
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner selection or separately configured CI
  reason: affected focused gates selected; broad historical/native/provider/certification lanes unselected
evidence:
  - path: .gnd-planning/milestones/incremental-evaluation/001-plan-gate.md
    sha256: a313752da6f5b30fa2a569afeabb0aca76e8b3f05653ba1a2f9b39a1fdff7ea7
  - path: .gnd-planning/milestones/incremental-evaluation/002-execution-delegation.md
    sha256: 7f776af776a3713f2ed2a71a7eb02dc8654b2d3e6e7b52668392e159494530fd
  - path: .gnd-planning/milestones/incremental-evaluation/003-phase-IE0.md
    sha256: de134aeb35b382308aa1ea6ad503c99a224e490f2095ad1671ceb7998bc03eb8
  - path: .gnd-planning/milestones/incremental-evaluation/004-phase-IE1.md
    sha256: 7d9a0e0e7b4a64c55ac9e5ef323b1fee7df84b909c3d10ce5bd00d469fee0008
  - path: .gnd-planning/milestones/incremental-evaluation/005-phase-IE2.md
    sha256: 5517d4b8478899ed23b7a4d4aeeb4cd33e82232581d20212488b2d40ddb2ec63
  - path: .gnd-planning/milestones/incremental-evaluation/006-phase-IE3.md
    sha256: 104f520c84ff4498b65a65c352000e45763c22ac5e2485501c7961bc10d71880
  - path: .gnd-planning/milestones/incremental-evaluation/007-phase-IE4.md
    sha256: a2adde0c2211f0c4c2599570d9743ebfef39e7915d0212339cc197387b2aae89
  - path: .gnd-planning/milestones/incremental-evaluation/008-phase-IE5.md
    sha256: 30435297ec1d6843e5fa28ce60d2c5616d209741e41bd5b1bb639b96e52e511b
  - path: .gnd-planning/milestones/incremental-evaluation/009-milestone-close.md
    sha256: 8298e7d6b182fef3659ddca3918a9ad0fbf0a0c871ebce0fe4ec39f9e830d902
  - path: .gnd-planning/milestones/incremental-evaluation/010-IE6-reopening-gate.md
    sha256: fb874c5175b43b89426befc2b4af3d6a326e1765a3dfea5e542639f8075d9abf
  - path: .gnd-planning/milestones/incremental-evaluation/011-phase-IE6.md
    sha256: ca66e6cda6ec611f9a192bf55fd266f91dc60eca38be7b6f45c8ae100a0c7380
  - path: .gnd-planning/milestones/incremental-evaluation/notes/incremental-evaluation-plan.md
    sha256: 57146d5e2dc58c663a6209e981fb1758ed981bc019afdfdef489e326d33a5a29
  - path: .gnd-planning/milestones/incremental-evaluation/notes/close-question-sweep.md
    sha256: a7081284c13e51a79656cc48d41f9a6a060a28e0f68290907b894f8a3e475161
  - path: .gnd-planning/milestones/incremental-evaluation/notes/IE6-close-question-sweep.md
    sha256: 60b89fd51b329aaef5c7023dbc106ab9dffbacba9864ad1a2af3eb7f94197b68
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/acceptance.json
    sha256: 468263778e8a87a3791716b6b5660e08534c2588c3ec85490fc2e408920039c5
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/final-identities.json
    sha256: df2fce64521425d8c5d998e6f7955454998d8d2e4c2625090b7625f391bc7746
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/audit.py
    sha256: a20fa6766c18c45ec49ac2a43badd4e6bb66f57770efe749e750bc212e5bc3d7
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/measurement.json
    sha256: 23a17c57b7c771042b3c84148b93bb3fb119a0d952bd3169b79aac47931c2405
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/revision-comparison.json
    sha256: c56628ae2204d8f633cdbbb9fe546d1126e244487d9a7e63cd3f74d919522954
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/wheel-manifest.json
    sha256: 02d1ad4c2f81d6c8c2b333d6c5feda4b7c17388d05d94b7dc319cae76beabaff
  - path: .gnd-planning/PROJECT.md
    sha256: efa6a09c5b6e6239389c06ca813441c9344e7101bf0e11ba21cbab10dbdb510a
  - path: .gnd-planning/milestones/incremental-evaluation/README.md
    sha256: dd148b512e86985db50ad7a7b340c8a365248ea40b0e1dfb053760d05746fa3c
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6-close/correctness.md
    sha256: 9c5e9032a9fefcdfc88d608985079d31f854f7aa36ff313c297577c0ba789e13
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6-close/measurement.md
    sha256: 93e7cedcaed3d68dc8cafe52217a90c0530be3c36983d9af71a9e2a528e21cc2
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6-close/structure.md
    sha256: 0f8405fd8d227874e7ee84f14f1bccb22c91a2927c63706ba44df8975d35e7d8
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6-close/protocol.md
    sha256: dc22fc5fd00b3ae25482babd1cd01d4739a08cc4fcc35ae2f33ea7a565369453
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6-close/disposition.md
    sha256: d44271405b46fda0dabd3cf2f7189554bc37f639174a93cb708902f53ae46f26
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6-close/phase-audit.txt
    sha256: 4eae341da3641fe31222dce5f755ce5358643e47014ce15a3c86ba182c63219c
---

# Renewed local milestone close with carryovers

All seven phases IE0–IE6 are locally accepted. This successor close incorporates
IE6 without rewriting historical009 or claiming its audit describes current code.
Records003–008 retain earlier phase gates;010 authorizes the bounded reopening and
011 records the completed performance phase. Separate delegated exact-byte
acceptance is evidence/IE6-close/acceptance.json. Named auto delegation002 and the
owner's request to add and implement this phase supply the ruling authority;
reviews and tests supply evidence, not authority. This is delegated approval,
not the owner's personal reading. PR33 remains open; no merge is performed.

## Exit predicates and evidence

The original seven exit predicates remain discharged within their recorded scope:
baseline/differential oracle (003), conservative invalidation (004), component and
finding reuse/session API (005–006), counted work and parity (005–008,011),
observation/feedback (007), integration/lifetime/docs (008,011), and gates/reviews/
records (001–012). IE6 adds bounded reductions in repeated policy accounting; it
does not replace any original safety predicate or turn informational timings into
a weakened correctness gate. Full live signature hashing, exact equality, mutable
and code guards, private clones, combined caps and atomic commit remain.

Final current runtime gate retained in011: 486 passed in211.02s (0:03:31).
Documentation gate: 3 passed in1.07s. Scoped lint: All checks passed!
These are retained executions, not new test runs by close readers. The separate
integrated oracle preserves complete reports/exits/branches and ordered outermost
calculation requests, with the frozen body denominator4878 and session bodies179.
Final installed candidate uses explicit Python3.11.15, an offline fresh venv and
outside-checkout smoke/CLI;273 wheel Python members match current source. The
failed implicit3.14 offline install remains disclosed.011 contains exact commands,
artifact digests, wheel identity and interpreter limits; no new installation claim
is made here. Temporary wheel/archive availability is weaker than committed bytes.

Final revision comparison uses A=archived session+receipts, B=IE6 session+receipts,
C=IE6 full+receipts. Three samples per arm, ABC/BCA/CAB rotation, complete replay,
startup/import excluded and loading included, no counters/profiler in timed arms:

|Workload|Old session A (s)|IE6 session B (s)|Full receipts C (s)|Observed session median decrease|
|---|---:|---:|---:|---:|
|Reporter|9.594056|9.030647|8.496214|5.87%|
|Course|2.410517|1.991713|0.855150|17.37%|
|Localized|0.574453|0.540538|0.422638|5.90%|

All new session medians remain slower than full receipts. Reporter new-session
range0.891714s exceeds the0.563408s median decrease. These small shared-host
samples establish an observed difference, not reliability or universal gain.
The separately executed integrated oracle uses different ABC meanings and is not
combined with these samples. Historical IE5 absolute timings establish no causal
speedup comparison. Initial exploratory revision results are retained but superseded:
their identity guard missed a legacy helper and packaged course input. Reproduced
mutation negatives and the repaired2876-entry maps/driver guard support the final
repeat. No runtime bytes or timing target changed during that correction.

## Independent review and dispositions

Four distinct local renewed-close readers reviewed committed subject202710d and
the successor question sweep: correctness, measurement, structure and protocol.
Each returns close-with-carryovers; exact opinions, original response hashes,
declared root sanitation and disposition are retained in evidence/IE6-close.
One initial four-reader round, no confirmation round or surviving blocker.
These opinions are separate from the four amendment-plan readers and the one
Astra CLI phase reviewer plus one bounded confirmation. None is relabeled as a
six-model panel. Close readers used static/data-only inspection, not candidate
imports, tests, benchmarks, providers or credentials. Their subjects and limits
exclude this final012, navigation and separate ruling bytes.

The protocol and identity audit authenticates58 phase acceptance subjects, both
revision maps and driver, integrated ordered parity/body counts/lifetime cleanup,
wheel archive manifest, and unchanged009 history. The --close extension checks
four distinct retained opinions and final close acceptance subject digests.
Its stdout is retained separately as evidence/IE6-close/final-audit.txt. Exact
phase-audit output, produced before this close record, is:

```
identity corruption negative live
phase identities: 58 match; current measurement maps verified
complete ordered parity and frozen bodies 4878/179 verified; close clears retained state
both revision maps/driver identities match; all timed census/exits valid
wheel archive manifest verified; historical009 unchanged; machine-home scan clear
data-only IE6 audit exit 0
```

## Open-questions sweep and refactoring review

notes/IE6-close-question-sweep.md carries all18 inherited rows and IE-Q2..Q10 by
reference to the original sweep. IE-Q1 bookkeeping overhead is partly addressed;
framework maintainer owns remaining constraint-policy setup, extension planning
and combined snapshot freezing under explicit future selection. IE6-Q1 hashability,
Q2 metaclass equality, Q3 descendant counter liveness and Q7 measurement identities
have reproduced discriminating regressions and repaired gates. Q4 interpreter and
Q5 footprint scope are accepted bounded claims;Q6 preserves reporter/owner lanes.
No question is silently promoted to resolved by timing improvement. Reporter owns
supplying/admitting the offered547-program workload and downstream acceptance;
owner separately selects delivery dates, wider lanes and merge/publication.

Refactors EXECUTED: existing accounting traversal returns verified immutable
size/node/depth summaries;_measure retains its size/None interface, uses identity
for builtin fast paths and still separately measures private clones. No new module,
import home, query/layer allowance, family dispatch, public signature, wire or
shim/discovery change. Per-phase refactor dispositions remain in003–008/011.
All deferred setup/freezing and prior structural items retain named owners in the
two sweeps. Close itself needs no runtime refactor; only evidence/navigation changes.

## Refuted premises and boundaries

Body savings alone do not establish wall-time savings. Borrowed class handles
inside normalized tuples can change hashability; unsafe one-time hashing was
withdrawn before repair. Tuple membership can invoke metaclass equality; new
fast paths use identity. Root-only counters can miss descendant rescans; actual
mutant evidence strengthens the instrument. Identity lists must cover helpers and
packaged data as well as Python source. RED/GREEN history remains explicit.

No general speedup, superiority to full receipts,547-program acceptance, delivery
date, default activation, proportional row-delta recursion, persistent/portable
cache, RSS bound, broad historical/native/provider acceptance, certification,
production publication or PR merge. Projected retained cache bytes exclude caller,
returned and observer memory. Admission/adaptation/final report composition remain
fresh; counted work is not every Python instruction. This named milestone stops
here; closing it does not start another performance phase.
