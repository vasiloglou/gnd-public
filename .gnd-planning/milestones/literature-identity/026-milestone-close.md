---
milestone: literature-identity
station: milestone-close
skill: "n/a -- repository development under process-milestone, not a gnd-solve station over a domain model"
scope: milestone-close
date: 2026-11-15
gates:
  - command: "uv run pytest -q tests/test_li0_witness_wire.py tests/test_li1_literature_corpus.py tests/test_li1_assurance_report.py tests/test_li2_resolution.py tests/test_li3_diagnostics.py tests/test_li4_assertions.py tests/test_li5_lineage.py --tb=short"
    exit: 0
  - command: "uv run pytest -q tests/test_li5_lineage.py --tb=short"
    exit: 0
  - command: "uv run pytest -q tests/test_li5_lineage.py tests/test_li4_assertions.py tests/test_li2_resolution.py tests/test_witness_composition.py tests/test_public_why_not.py tests/test_checker_families.py tests/test_fu3_derived_ring.py tests/test_public_v71_witness_corpus.py --tb=short"
    exit: 0
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
  - command: "uv run --isolated --offline --locked --group docs zensical build --strict"
    exit: 0
  - command: "uv run ruff check"
    exit: 0
  - command: "uv run python -m gnd.examples.literature.lineage_run score MODEL DEVELOPMENT-RUN DEVELOPMENT-KEY"
    exit: 0
  - command: "uv run python -m gnd.examples.literature.lineage_run score MODEL FIRST-RESERVED-RUN LOCAL-KEY"
    exit: 1
  - command: "uv run python -m gnd.examples.literature.lineage_run score MODEL CORRECTED-RESERVED-RUN LOCAL-KEY"
    exit: 0
  - command: "uv run pytest -q tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap --tb=short"
    exit: 0
  - command: "uv run python tools/run_gnd_review_panel.py .gnd-planning/milestones/literature-identity/evidence/close/r1-request.json --out <scratch>/close-panel-r1 --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "uv run gnd review finalize <scratch>/close-panel-r1 <scratch>/close-synthesis-r1.json --out <scratch>/close-panel-review-r1.md"
    exit: 0
  - command: "ruling: delegated (auto=true) refused .gnd-planning/milestones/literature-identity/notes/literature-identity-plan.md sha256 4f496a6b47f17cf6fe166821e75e924b43857153b391b05825a3f1e46084c1b5"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/literature-identity/001-plan-gate.md
    sha256: b0608d5b2f4fd9963da52cda3f5010173fb15799bb58e93d6816d0b0cc5be891
  - path: .gnd-planning/milestones/literature-identity/003-phase-LI0.md
    sha256: 244a24a819e672b0d193aab6fd7e1414c11750bf1ff3c8a2750a37ef4a81c2e0
  - path: .gnd-planning/milestones/literature-identity/006-phase-LI1.md
    sha256: e9a7ab4e0bdd089c2943b2348d1888202bc52b5da5c2e596c1d80eab7c0d900f
  - path: .gnd-planning/milestones/literature-identity/010-phase-LI2.md
    sha256: bbe773213fcb85eca205aaf5be34abf23a64cbb4024764d0403c8660e26766cb
  - path: .gnd-planning/milestones/literature-identity/014-phase-LI3.md
    sha256: d015fed959b00badef9adf21a982e244734d9778fbfed94ab0bc0b986c5fd0f0
  - path: .gnd-planning/milestones/literature-identity/018-phase-LI4.md
    sha256: fcd0ce69fc70587868c59dc4307efc82580342c0ffd12e94e41c1e92302502e0
  - path: .gnd-planning/milestones/literature-identity/021-phase-LI5-rule-freeze.md
    sha256: 7b4d42679496de9026b2acb7300db41c3dc9e66cc5168c1f9dd4ce989e027572
  - path: .gnd-planning/milestones/literature-identity/022-phase-LI5-reserved-input-freeze.md
    sha256: 792bfb417cd3b4ceb36041789677f3104dd4aaeb8981f86325f82cc55d63cbf5
  - path: .gnd-planning/milestones/literature-identity/023-phase-LI5-reserved-input-amendment.md
    sha256: 5b2c11314bb1b5b271be6e2a7d560509841d0efd4b7c639aff43443fe18596c5
  - path: .gnd-planning/milestones/literature-identity/024-phase-LI5.md
    sha256: 7830e0ec14dcaa41d874598a8ef5e396f66ef129a396e8a52ee2115ef4434ae1
  - path: .gnd-planning/milestones/literature-identity/notes/literature-identity-plan.md
    sha256: 4f496a6b47f17cf6fe166821e75e924b43857153b391b05825a3f1e46084c1b5
  - path: .gnd-planning/milestones/literature-identity/notes/close-results.md
    sha256: 56e641fe1e7e15681a19418ff1af84506576d51db2cb34cbf68b04f99dd211bd
  - path: .gnd-planning/milestones/literature-identity/notes/close-delta.md
    sha256: ef2157bdf39929d4ce2b1079b801d6e648379238a61aae2763637f39d54b2910
  - path: .gnd-planning/milestones/literature-identity/evidence/LI5/development-score.json
    sha256: 0b66ac5b8a19141273b700b57c31bf257215004b3c0e1669971b50e6d6c76dfe
  - path: .gnd-planning/milestones/literature-identity/evidence/LI5/reserved-first.json
    sha256: 822e3c3c4a61eaafa698f0579bc54330e4777c574a319a715514285de914c182
  - path: .gnd-planning/milestones/literature-identity/evidence/LI5/reserved-corrected.json
    sha256: ff55d9ec11a1257896b347864b96236fdc679dd307b11b37b0342076a3556ebf
  - path: .gnd-planning/milestones/literature-identity/025-panel.md
    sha256: 49c9e203e7abf86de2d0e58670c0699e8262d7b44cf247cd79fc38d6e75d4668
  - path: .gnd-planning/milestones/literature-identity/evidence/close/r1-request.json
    sha256: 59e523f84ab020fe93585e5c8f65490f302e89015b3df89db44ae96b36c1dae9
  - path: .gnd-planning/milestones/literature-identity/evidence/close/r1-summary.json
    sha256: 8927b378bd7cd218e5c8da91217a2334f30c9291516c085d5efb1b00b7e20028
  - path: .gnd-planning/milestones/literature-identity/evidence/close/r1-synthesis.json
    sha256: 9d0cd7e2b349bccc65788413826ac22f8716407068a150c8d0eb309a52afe8b8
  - path: .gnd-planning/milestones/literature-identity/evidence/close/r1.md
    sha256: 5841e95b80e68e1a35761f6d4e3a561a3e3969f9c1dc361b7d326572c07a9bd9
---

# Claim

The LI0–LI5 implementation and review records are in place. The
delegated close ruling withholds milestone acceptance because the first
reserved run missed its sole supported path under L1.

## Gate output

The first consolidated milestone gate exited 0 with
`200 passed in 356.11s (0:05:56)`. The reproduced focused gate below
began on the clean source and test tree at `5d6e9038`. It includes the
final LI5 assertions.

```text
........................................................................ [ 35%]
........................................................................ [ 70%]
............................................................             [100%]
204 passed in 314.28s (0:05:14)
```

The late LI5 gate exited 0 with `10 passed in 54.54s`. The last
affected-consumer gate exited 0 with
`602 passed in 655.66s (0:10:55)`, and the structure lane exited 0
with `679 passed, 2 deselected in 317.66s (0:05:17)`. The
final scoped reference-closure check exited 0 with `1 passed in 0.69s`.
Ruff exited 0 with `All checks passed!`. The strict docs build exited
0 with `No issues found`. See [LI5](024-phase-LI5.md) for the full affected,
structure, lint and documentation commands and for the score invocation
and artifact mapping.

Phase evidence is bound in [LI0](003-phase-LI0.md),
[LI1](006-phase-LI1.md), [LI2](010-phase-LI2.md), [LI3](014-phase-LI3.md),
[LI4](018-phase-LI4.md) and [LI5](024-phase-LI5.md). The
[close results](notes/close-results.md) map the exit predicates to
actual fixtures and controls. The [close delta](notes/close-delta.md)
binds the issue criterion trace and successor partition. The planned
workflow gates are evidenced by these records. The phase evidence digests
were checked against their record commits. The three pre-gate spec
digests in 002, 004 and 007 resolve against a6f1db34, c53d7d56 and
b4f4cdb4 respectively.

| L1 measurement | Supported kept | False excluded | Score exit |
|---|---:|---:|---:|
| Public development | 3/3 | 5/5 | 0 |
| First reserved score, after rule and input freezes | 0/1 | 2/2 | 1 |
| Same reserve after the recorded input correction | 1/1 | 2/2 | 0 |

C6's reserve custody and pre-scoring freeze are documented in
[021](021-phase-LI5-rule-freeze.md) and [022](022-phase-LI5-reserved-input-freeze.md).
The separate [input correction ruling](023-phase-LI5-reserved-input-amendment.md)
explains the missing architecture-level endpoint and preserves the
encoder qualification, original score and same key, model and policy
digests. The corrected run is a smoke demonstration on the repaired
input. The first reserved measurement controls independent acceptance.

## Independent close review

The [panel record](025-panel.md) binds the maintained standard GND
panel against the plan, results and dispositions at `5d6e9038`.
The runner and finalizer both exited 0. Six schema-valid responses
met the project bar of four. Claude, Codex and Qwen raised the
first-run L1 gap as a concern. Gemini approved without concerns.
The finalizer retained six agreed groups, twelve divergent
concerns and six recommended fixes. The panel record gives each
disposition and the unchanged-artifact and seat evidence.

The close results and delta incorporate the review findings as
evidence clarifications. The amended plan has the same digest
as the reviewed plan. A second round would review those citations
without producing independent reserved evidence. One round was
used under the two-round limit.

## Delegated close ruling (auto=true)

On 2026-11-15, under the owner's current request to run
`process-milestone literature-identity auto=true`, accept the §11
recording of the LI2 timing clarification, phase evidence, and named
carryovers in the exact amended plan cited above. Refuse milestone
acceptance of those bytes. L1 requires the supported path to survive
on the reserved set, and the first reserved run exited 1. The
post-feedback result supplies neither an independent pass nor a
basis to change L1. The advisory panel met the review bar and
does not supply the missing L1 measurement.

The delegated scope was LI2–LI5 and this close, with previous owner
rulings retained. The close instrument was the standard maintained GND
panel through the repository launcher, with a maximum of two rounds.
Phase diffs used the separately selected Claude Code instrument.

## Open-questions sweep

The [criterion trace and disposition ledger](notes/close-delta.md)
sweeps 001, 003, 006, 010, 011, 014, 018 and 024. The LI1
stage floors, LI2 schema identifiers and T20 interpretation, LI3
threshold, recurrence, budget and example-only scope, and LI5
path-policy and exit questions are resolved with their cited phase
evidence. W3 verifies one existing version-2 certificate byte golden
and 228 model identities. Other certificate suites verify behavior,
leaving broader byte-for-byte compatibility unmeasured. The first
reserve remains open for literature-identity acceptance pending an
independent measurement under an approved corpus. Existing C6 and L1 evidence stays linked to its original
conditions. The close makes no new corpus ruling.

The document evidence layout goes to literature-interop, the
safe-reader symlink question to repository maintenance, and the
serializer consolidation to a code-refactoring successor. These
targets have no assigned person. The part 4 date control remains
with LX4. Parts 5–8 and 10 follow the approved partition, and part
10's P3 awaits its own ruling.

## Refuted premises

The LI2 full-wire version of the 200-by-200-by-20,000 timing
exercise exceeds the bounded decision wire. [010](010-phase-LI2.md)
records the executable coverage-layer measurement and separate
end-to-end controls. Plan §11 preserves this distinction.

The first reserved annotations did not supply the architecture
endpoint for a true path. The score in [reserved-first](evidence/LI5/reserved-first.json)
refutes the original full-retention expectation. The corrected result
supports the revised input under the frozen rules but cannot repair
the first measurement as acceptance evidence.

## Refactoring review

The individual phase records assessed their touched targets. The
three outstanding refactor or maintenance questions have target areas
and boundaries in the sweep. Serializer consolidation must preserve
the LI0 golden identities. The named evidence layout and symlink
follow-ups carry their ownership and current constraints.

## Boundary

The public benchmark uses reconstructed author labels and a small
declared corpus. The LI3 sample is synthetic and the reserve contains
three chains. Reading coverage is assigned to LD3. The host owns
host-scale evaluation. The panel is advisory. The rule and policy
digests and aggregate scores are in history, with the key and local
reserved inputs retained outside Git. This record supplies no
authority for merge, publication, certification or successor work.
