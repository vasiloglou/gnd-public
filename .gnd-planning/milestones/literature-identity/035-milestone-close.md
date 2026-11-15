---
milestone: literature-identity
station: milestone-close
skill: "n/a -- repository development under process-milestone"
scope: milestone-close
date: 2026-11-15
gates:
  - command: "uv run --no-sync python -m gnd.examples.literature.lineage_run score MODEL BLIND-RUN LOCAL-KEY"
    exit: 0
  - command: "uv run --no-sync python tools/run_gnd_review_panel.py .gnd-planning/milestones/literature-identity/evidence/close/renewed-request.json --out <scratch>/panel-run --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "uv run --no-sync gnd review finalize ../panel-run ../renewed-synthesis.json --out ../renewed-panel.md"
    exit: 0
  - command: "uv run --no-sync pytest -q -p no:cacheprovider tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap --tb=short"
    exit: 0
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-identity/notes/literature-identity-plan.md sha256 04934bb2aab94e55cc3aa5afe340cc1e72a9300c25ab084a9382387fe374049c under the current owner close instruction"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/literature-identity/026-milestone-close.md
    sha256: c7ee151f14cecdc2f26200c0e4fbee9c28d8b7136adced3dd6ebba25bef77ecf
  - path: .gnd-planning/milestones/literature-identity/027-phase-LI5-independent-reserve-spec-gate.md
    sha256: c8a845fcb38f2070cdeccaabe4e4fedbde76a3b2f3872fc926e450fcc9843ac3
  - path: .gnd-planning/milestones/literature-identity/028-phase-LI5-independent-reserve-corpus-gate.md
    sha256: b6b4b86792f039b66f1dc6e62e00425f7edb2106e974dcb331b72c613ff00db5
  - path: .gnd-planning/milestones/literature-identity/029-phase-LI5-independent-reserve-assembly.md
    sha256: 15628e100005d99d44dc14799065a8e42033c9937859a2c96cbf5f5885f95a79
  - path: .gnd-planning/milestones/literature-identity/030-phase-LI5-independent-reserve-freeze.md
    sha256: b497393b933d388d443a4541257986856ff73e3847ee0ac1381356ca568de423
  - path: .gnd-planning/milestones/literature-identity/031-phase-LI5-independent-reserve.md
    sha256: 2651d5c4c92a4b1cacb3f39c8ce7a2e4ca0661cf08a4403dcecb53d54b650f56
  - path: .gnd-planning/milestones/literature-identity/032-main-integration.md
    sha256: 3a5311a303f11a31be38733dd062ce969e93649980823c89989e0d225565ac27
  - path: .gnd-planning/milestones/literature-identity/033-panel.md
    sha256: 25a211b1a8e5fe65e84f3447d495921a986222c5786a53e86329721af9666feb
  - path: .gnd-planning/milestones/literature-identity/034-panel.md
    sha256: d34980846b667d3c863874a8984c27d1fc66a46d7a4885fcef817ee102c3f02e
  - path: .gnd-planning/milestones/literature-identity/notes/literature-identity-plan.md
    sha256: 04934bb2aab94e55cc3aa5afe340cc1e72a9300c25ab084a9382387fe374049c
  - path: .gnd-planning/milestones/literature-identity/evidence/LI5/independent-reserve-v1.json
    sha256: a553f8a67c019bf6700342b3fa212746138fe24d13db579cc4e42f715a3d64ec
  - path: .gnd-planning/milestones/literature-identity/evidence/close/retry-summary.json
    sha256: 5ea3f47eed03d88f1aa421d465ceb9384921bcbfb8e59cf0ecd913e832b233a5
  - path: .gnd-planning/milestones/literature-identity/evidence/close/retry-panel.md
    sha256: bf32488e29f4c4799a69a377274817261616274ba16b7f1ec6136cc0c8b335b0
---

# Claim

Literature-identity is closed on the public-scale LI0–LI5 evidence.
The first executable score on the separately approved fresh reserve
satisfies the independent L1 measurement left open in 026.

## Gate output

[Record 031](031-phase-LI5-independent-reserve.md) binds the exact first
executable fresh-reserve measurement. The score command exited 0 and
recorded `"supported": [1, 1], "excluded": [2, 2]`.

| Measurement | Supported kept | False excluded | Score exit |
|---|---:|---:|---:|
| Original reserve, first score | 0/1 | 2/2 | 1 |
| Original reserve, post-feedback correction | 1/1 | 2/2 | 0 |
| Fresh independent reserve, first score | 1/1 | 2/2 | 0 |

The owner approved the [fresh protocol](027-phase-LI5-independent-reserve-spec-gate.md)
and the [sealed source manifest and key](028-phase-LI5-independent-reserve-corpus-gate.md).
The first blind submission [failed assembly](029-phase-LI5-independent-reserve-assembly.md)
with exit 3 before any score. In the source-only recovery Astra removed
one resolution reference that could not bind to an admitted assertion.
The driver independently checked every statement and the remaining
decision against the first submission and the existing admission
output. The recovered assembly exited 0 and the exact annotation and
composition were [bound before scoring](030-phase-LI5-independent-reserve-freeze.md).
The model, policy, rubric, scorer and new three-case key were frozen.
The original miss and post-score correction remain in the historical
record.

[Integration record 032](032-main-integration.md) binds the 204 milestone
tests and 276 affected guard and consumer tests, plus the passing
scoped lint, component check and strict docs build. The full-tree Ruff
findings matched pre-integration main. LI0, LI1 and LI2–LI5 merged via
PRs [#194](https://github.com/vasiloglou/gnd-public/pull/194),
[#197](https://github.com/vasiloglou/gnd-public/pull/197) and
[#199](https://github.com/vasiloglou/gnd-public/pull/199).
The source and test tree merged to main at `01907899` matched the tested
topic tree. The renewed close adds documentation and advisory evidence.

## Independent close review

The [retry record](034-panel.md) binds the second authorized panel,
its six valid responses, and its advisory dispositions. It meets
the four-reviewer project requirement. The earlier [three-seat
round](033-panel.md) remains separate. Gemini's dissent about using
the executable recovered input remains in both reports. Qwen's
isolation objection was checked using the original OS sandbox
profile and the retained execution logs.

Both Astra commands ran from a separate annotation directory under
`/usr/bin/sandbox-exec -f isolation.sb`. The inner Codex CLI ran
ephemerally, used Astra, recorded the response schema, and had shell,
multi-agent and web tools disabled. The archived stderr digests for
the first and recovery sessions are
`214f0efca5d0859fc507a173385dd6233a1b6b718603fa9a8e40bf5a06ad4107`
and `8d8e96ffec45bf827bce3fb62584a4a582b62ea869b4b1c85299f0c979431c4d`.
The retained logs identify the separate working directory and model.
The outer profile SHA-256 is
`bdc59cb02b6e8446db3a196ce6103299b045c4c730591ef3590a7ffdf8a1df64`.
The post-review probe with that profile exited 0 after reading the
source-only packet and observing access refusal for the repository
checkout, original answer key, and new sealed key. The private files
and raw tool logs remain outside Git.

The removed item was a `same` decision with an endpoint that did
not occur in any admitted assertion for its source. The driver
rebuilt the valid subset with the existing admission path. The
comparison verified that the recovered parsed object was identical
to the original object with exactly that subset in place. The
statement-equality output cited in 030 was from the local comparison.
The JSON exit line was the assembler's actual output. No score,
expected path or key was available to Astra when it made the
correction. The implementation did not change.

The first score binds the model, composition and key in the
tracked aggregate. The adjacent freeze records and a recheck bind
the remaining execution inputs.

| Input | SHA-256 |
|---|---|
| Model, 027 and 031 | `a63b64293edbed71c74d1ded8423c133c328aa4ea02f550bad4fb03c91591279` |
| Path policy, 027 | `cc27412b17b7cc1ca4f6d5da940b74b80528e45d2aa9d5a78dbee4986274c0b7` |
| Assembly and score module, 027 | `15ff3ddc3d483fcdaed71ccfcc059facecb102282a674ce109d967085353706b` |
| Exact private rubric copy, matching 027 | `1c98384795afd57033b0416a6e8dbd6cd3f914a33fadc3510f605394079b0178` |
| Fresh key, 028 and 031 | `6f510056d22ffb6b11c4c94a2ea71ebaef3a38b3e6897518105621a19bde4929` |

The development-side Codex custodian selected the new cases and held
the sealed key. Astra supplied the structured annotation in its own
source-only session. The fixed example producer's internal author
label remains a label on the materialized receipts and decisions.

Development separately retained 3/3 supported and excluded 5/5 false
paths. [024](024-phase-LI5.md) records a separate dirty-input control.
In the fresh run both false targets lacked a required admitted
directed edge. The fresh counts measure end-to-end exclusion over
this corpus. The public development controls supply the evidence
that the score detects an incorrectly accepted path.

## Close ruling

**Delegated close ruling (auto=true), 2026-11-15.** The original
literature-identity delegation and the owner's current instruction
to “merge and close” authorize this close ruling. The owner
separately approved the follow-up protocol, sealed corpus and each
paid review round. The renewed ruling accepts the §11 chronology
amendment at the exact plan digest above.

Accept the pre-score removal of the one inadmissible reference as a
recorded input recovery. The fresh corpus satisfies the independent
measurement called for by 026, with the original first score still
recorded as a miss. The approved threshold is the same. The result
establishes the first score on an executable blind input. The
original fresh submission's assembly refusal remains in history,
and zero-shot assembly was outside this accepted outcome.

Close literature-identity at the approved public fixture scale.
The prior W3 byte-compatibility and other scoped residuals stay
with their recorded evidence and successor assignments.

## Open-questions sweep

[026](026-milestone-close.md) and its [criterion and successor ledger](notes/close-delta.md)
remain the basis for the earlier sweep. The LI5 first-reserve concern in
026, 027 and 028 is addressed by the new measurement, with the original
result retained. Records 029 and 030 supply the pre-score assembly
refusal and recovered input. The extension of the guarded-clause query
successor chain is verified in 032. The panel findings and dispositions
are linked above.

LI0 W3 byte evidence covers one version-2 certificate and 228 model
identities. The other consumer checks establish behavior for their
cases. Keep the broader byte-compatibility evidence as a residual.
The common evidence layout goes to literature-interop, symlink reader
changes to repository maintenance and serializer consolidation to a
code-refactoring successor. The date control stays with LX4. Part 10
is carried with its pending P3 ruling in literature-depth. Host-scale
evaluation and reading coverage remain in their recorded homes.

## Refactoring review

The reserve follow-up reused the frozen admission, composition and
witness routes. Main integration regenerated the combined component
index and applied the exact previously measured query deltas after
their new authenticated predecessor. No fresh-reserve product change
or phase refactoring was needed.

## Boundary

The independent smoke result measures the three declared cases.
The raw private source and score evidence is retained off-branch.
The panel is advisory. This record concerns literature-identity
milestone closure. Publication, certification and successor work keep
their separately recorded authority.
