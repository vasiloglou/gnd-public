# Literature identity close results

The reviewed milestone is scoped to issue #193 parts 9, 1, 2, 3 and 4.
The approved plan gate and phase records bind their own evidence.
The close asks whether these measured implementations establish the
named exit predicates at the approved public scale. The panel reviewed
these notes as of `5d6e9038`. [Record 025](../025-panel.md) lists the
evidence clarifications made after that run.

| Predicate | Phase record | Observed evidence |
|---|---|---|
| LI0 version-1 and missing-model-ID witness intake | [003](../003-phase-LI0.md) | Witness and why-not accept their valid inputs, and replay succeeds. W3 pins one version-2 certificate and 228 model identity values. Other certificate consumers have behavior checks with no byte golden |
| LI1 public corpus, reporting and output-drop guard | [006](../006-phase-LI1.md) | The corpus holds the approved public floors. The LI1 and LI2 reference reports exit 0. See the measured fractions below. Reduced output fails its floor. Coverage is deferred to LD3 |
| LI2 verified identity decision | [010](../010-phase-LI2.md) | Cross-source joins over the asserted keys of host-selected object types require same connectivity (LI2 D2 and B1). Different and unresolved controls and stale replay are tested. The false merge lowers measured precision to 3/4 and exits 1 |
| LI3 example diagnostics | [014](../014-phase-LI3.md) | Four pinned spelling pairs across three candidate kinds. The shared-work control suppresses the flow-matching homonym. Seed 193 samples 100 of 216 synthetic emissions, uniformly within strata. The corpus author supplied the labels. In [011](../011-phase-LI3-spec-gate.md) and [012](../012-phase-LI3-corpus-gate.md), the ceiling is set to 1/5 before measurement. Family 3/52, homonym 1/24 and synonym 2/24 are below it |
| LI4 contextual statement and saved opinion admission | [018](../018-phase-LI4.md) | The reference produces 7 of 10 supported and 3 of 10 admitted original findings. The wrong-predicate co-occurrence is rejected. Four non-admitted polarity and attribution pairs remain distinct, and the two conflicting experiment contexts survive. Missing condition, stale or malformed input, unpinned opinion and forged report controls are tested. Exact raw input is retained |
| LI5 qualified paths and witnesses | [024](../024-phase-LI5.md) | Development 3/3 supported and 5/5 false excluded. The reserved first pass kept 0/1 supported and excluded 2/2 false. The recorded input correction retained the qualified source passage and reused the exact key, rules, table and scorer. Its second score kept 1/1 and excluded 2/2. Independent L1 acceptance remains unmet. The corrected input supplies only the measured smoke demonstration |

The proof control follows witness source coordinates back to the accepted
assertions and composition decision indexes. A changed source coordinate
fails replay with proof-invalid (1). A changed record fails with
binding-stale (3). Cyclic and acyclic checks each exit 0, with a warning only on the cycle
and both edges retained. Witnesses on unreviewed and unresolved
steps exit 2. Transfer is witnessed with both conditions present.
A missing interface on either direct or transitive transfer exits 2.
A missing assumption leaves the lineage witness available and makes
the transfer witness exit 2. The [L2, L3, L4 and L6 controls](../024-phase-LI5.md)
cover exclusions for `evaluated-as`, `compared-against`, `inspired-by`
and `taxonomic-membership`.

The consolidated direct milestone gate is `200 passed in 356.11s (0:05:56)`. Per-phase
impact lists, review dispositions and digest evidence remain in their
records. The close panel is independent of the phase readers.

## Assurance reference floors

The preserved [LI1 reference](https://github.com/vasiloglou/gnd-public/blob/d09189ca/src/gnd/examples/literature/expected/reference.report.json)
at `d09189ca` and [LI2 reference](../../../../src/gnd/examples/literature/expected/reference.report.json)
at `4735730d` both exit 0. The scored values below are identical across
these runs except that LI2 activates identity. A dash means the report
does not emit that metric for the stage.

| Stage | Agreement | Precision | Recall | Abstention |
|---|---:|---:|---:|---:|
| Model/population validity | 12/12 | — | — | — |
| Source binding | — | 39/39 | 39/39 | — |
| Semantic support | — | 8/8 | 8/8 | 0/12 |
| Identity decisions, LI2 only | — | 3/3 | 3/3 | 0/6 |
| Derivation | — | 7/7 | 7/7 | 0/1 |
| Freshness | — | 25/25 | 25/25 | — |

Coverage stays `not-measured`, owned by literature-depth LD3.

## Reserved smoke measurement

The [rule freeze](../021-phase-LI5-rule-freeze.md) commits the model and
path policy before the key was opened. The [input precommit](../022-phase-LI5-reserved-input-freeze.md)
binds the annotation and composed record prepared from the four public
reserved source documents. The initial failed result is retained at
[reserved-first](../evidence/LI5/reserved-first.json). The
[correction ruling](../023-phase-LI5-reserved-input-amendment.md)
binds the revised annotation decision and preserves prior bytes and
counts. The [corrected result](../evidence/LI5/reserved-corrected.json)
is evidence of a working fixed-rule route after correcting the input's
architecture endpoint. Both result objects bind the same key, rule and path-policy digests.
The corrected annotation and composition were digested in the corrected
score, after the first score was known. One corrected calculation
preceded the later same-input verifier replay. Both original scores used
`lineage_run.py` from `6034518d`, SHA-256
`a00b0cfabb5c5d05b4f0fb87e00ff24c860422fde08fb21b7c07dd1eb1ce34b1`.
The admission-marker repair in [024](../024-phase-LI5.md) changed that
digest to `15ff3ddc3d483fcdaed71ccfcc059facecb102282a674ce109d967085353706b`.
The repaired verifier replayed the corrected score byte-for-byte. The key
and both annotation sets remain local.

The first miss leaves the original L1 acceptance predicate open. The
[close panel](../025-panel.md) independently examined the distinction
between that first run and the corrected-input smoke exercise.

## Evidence boundaries

The public corpus is the owner-approved reconstruction. Its labels
are author readings, and the diagnostics sample uses synthetic examples.
Host-scale sets and the reading-coverage stage have their own future
owners. The close review is advisory. The delegated close ruling is
recorded separately.
