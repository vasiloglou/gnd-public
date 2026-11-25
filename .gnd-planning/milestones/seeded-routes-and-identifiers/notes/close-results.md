# Close candidate

Initial release-preparation merge: `4f2945a95fd0e9bd1de0103caa190da7616bb159`, the merge
commit of [PR #311](https://github.com/vasiloglou/gnd-public/pull/311)
on main. It contains [PR #294](https://github.com/vasiloglou/gnd-public/pull/294)
at `a9acbc4d5873c9892d59598a7a5569bf2e3556ed` and the four phase records. The [SI1 repair](../006-phase-SI1.md)
records the link inventory regression exposed by the first default lane and
the narrow test correction in [PR #313](https://github.com/vasiloglou/gnd-public/pull/313).

## Completion predicates

| Plan predicate | Evidence |
|---|---|
| 1, named route outcomes | [SI1](../002-phase-SI1.md) records the tested matrix for the packaged root, the root after both growth rounds and their flat projections. The injected failure reports exit 3 and `flattening:re-entry` without writing outputs. A standalone candidate needing exemptions reports `unattended:flat-without-root`. |
| 2, pin-checked exemptions and ownership | [SI1](../002-phase-SI1.md) records the focused include and growth selections, a second seeded shape, the root-owned-element controls and the fabricated-origin refusals. The approved route computation carries the resolved origins into re-entry. |
| 3, composite identity and compatibility | [SI2](../003-phase-SI2.md) records the preimplementation red fixtures, deterministic tie and fallback controls, production caller checks and the unchanged 436-model identity digest. The counted query guards pass. |
| 4, approved Ossie identifier changes | [SI3](../004-phase-SI3.md) binds the 17 approved ontology deltas out of 414 admitted exports. The pinned parser and validator pass for all 34 changed JSON and YAML outputs. The current and predecessor bound bundles restore their models. Across the same 410 mapped models, unmapped unit links go from 8 to 0, multiple-supertype links from 5 to 0, and four objectification links and two concepts remain. The two populations are reconciled below. |
| 5, tag-only release | [SI4](../005-phase-SI4.md) records the coherent 0.5.2 metadata, 85 passing release tests and the independent approval. The 0.5.0 package-index pins remain. Remote tag verification is recorded below. |
| 6, phase evidence and close gates | The [phase index](../README.md) links the four phase records, including their specs, tests, independent review and repairs. The [audit](../evidence/close/phase-evidence-audit.txt) recomputed all 70 cited phase and repair evidence digests using the cited commit or the reviewed repair head. The [sweep](close-delta.md) gives question dispositions. The default test lane is recorded below. This candidate is the input to the light close panel. |

## Independent phase review coverage

The [review-helper receipt](../evidence/close/phase-review-status.txt)
shows each reviewed file and subsequent drift. SI1, SI2 and SI3 each
have a first independent review and focused verification of later repairs
recorded in the corresponding phase record and findings ledger. Their
first opinions apply to their brief bytes. The SI1 repair-only review
also covers the shipped packaged-skill inventory change. SI4's source
and release-note fold match its approved brief. The SI4 spec's later
addition records the separate owner authorization.

## Seeded route and live runtime evidence

The owner-approved [SI1 spec](phase-SI1-spec.md) gives each of the seven
routes an exit of 0 on the packaged and twice-grown roots. Each written
seeded projection exits 3 with `unattended:flat-without-root` on all seven
routes, including the renamed-file controls. T5's fabricated origins
remain untrusted. The [standalone probe](../evidence/close/standalone-probe.txt)
holds the claimed origin fixed and removes a required owned span. All
seven routes then retain U4 alongside the D1b hint. With valid owned spans,
the ordinary routes exit 0. `flatten` applies its usual root-only contract
and exits 3 with `include:declaration`.

The 13 skips require the pinned native PyRel runtime for guarded clause
execution. Every skipped node is listed in the [PyRel receipt](../evidence/close/pyrel-route-check.txt).
The same run passed all seeded matrix and include-export nodes, including
default PyRel, DuckDB rules and LQP rules. It reported 83 passes and 13 skips.

## Ossie corpus reconciliation

The mapping census checks the same 410 model paths at plan baseline
`f7ee3720`, SI3 baseline `99cf3df2` and tagged merge `9c051d52`. Both
baselines have 17 link rows in 13 models, including the four
out-of-scope objectification links. The tagged tree retains those
four link rows and the two objectification concept rows.

The ontology-only census counts 414 admitted models. Of its four
additional models, three return an ontology without mapping artifacts.
The fourth returns a mapping with zero `identification-differs` rows,
but the source reader used by the mapping census refuses its missing
reference-artifact directory. All four keep identical JSON and YAML
ontology digests. The 17 changed ontology paths cover the 11 models
with the 13 targeted baseline mapping rows and six additional models
whose ontology identifiers changed. The [reconciliation receipt](../evidence/close/ossie-corpus-reconciliation.json)
lists the exact paths, digests, and mapping counts.

## Exact release verification

The owner explicitly authorized merging PR #313 and pushing the
annotated `v0.5.2` tag on its merge commit on 2026-11-25. GitHub merged
PR #313 at `9c051d52a970b82b81940a7125b393f41741013d`. The remote tag
object `9d1021d892feffa22c4f4da802b85f9c966a9415` peels to that exact commit.
[Remote verification and merged-checkout tests](../evidence/close/release-tag.txt).

The corrected full lane ran on the second parent of that merge. The
merge differs from the tested tree in only the two induction-skill
planning documents merged concurrently in [PR #312](https://github.com/vasiloglou/gnd-public/pull/312).
The source, test files, release metadata and dependency lock match the
six-shard run. A focused gate on the merged checkout passed 226 tests
across release metadata, the packaged skill inventory and the scaffold.
0.5.2 shipped as a GitHub tag. Package-index installation guidance
continues to use 0.5.0.

## Initial full default lane on beast-3

The [six-shard runner](../../release-0.5.0/evidence/RW1/e1-shards.sh)
runs the public repository in an isolated clean clone at the exact merge
commit. It uses Python 3.13.18, uv 0.13.7 and the repository's default
pytest marker selection. The six child exits are the test results. The
runner's own exit only establishes completion and reporting.

The separate `tests/test_public_optional.py` diagnostic uses the
required uv 0.10.10 in an isolated temporary environment on the same
host and exact source. Both tests passed in 3.10s. The six raw shard exits and this supplemental result are recorded in the
separate command receipts.

The [initial lane receipt](../evidence/close/initial-default-lane.txt)
records the six exits and their exact summaries. The 22,146 passes include
the Rmap timing node in shard 3. Thirteen guarded PyRel tests skipped on
this host. Shard 0 reported the two uv-version setup errors. Shard 2
reported the one packaged skill link inventory failure. The
[optional-wheel receipt](../evidence/close/optional-wheel.txt) records the
passing targeted run under the required uv version.

## Corrected full default lane on beast-3

The [corrected lane receipt](../evidence/close/corrected-default-lane.txt)
records all six shard exits as 0, with 22,149 passing tests and
13 guarded PyRel skips. It ran the reviewed PR #313 head
`c89e55e614bdd414023b89b47b4f5143ea0dae01`, tree `3cb3428d61e24a0d7b4c74da4f766fbdfec8ce59`,
with uv 0.10.10 and Python 3.13.18. The runner used the same default
repository markers and shard assignment. The [corrected lane receipt](../evidence/close/corrected-default-lane.txt)
records the isolated uv binary placed first on the runner's PATH.
Shard 0 passed both wheel tests with their fixture-required uv 0.10.10.
The fixture still checks for that exact version. Shard 2 passed because
PR #313 added the guide's valid link to the expected inventory. The
guide and its target retain the shipped bytes. The exact-edge assertion
and the repair review's removal, duplication and retargeting controls
preserve the guard. Shard 3 passed its Rmap timing threshold in both
six-shard runs.
