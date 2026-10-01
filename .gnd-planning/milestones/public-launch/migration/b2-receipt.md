# B2 receipt — source-owned coherent package

Reviewed runtime checkpoint: 081e3a8402f1de4f7eef271887db2fae147982d7.
Reviewed CI profile checkpoint: 3da7be7f76049a723303589f6de0f5d3658c5b87.
[B2 manifest](b2-files.json) SHA-256 `9d19ae337c5b75e5ae4d615674a3685f1301b124a25a5d573ee25cb34319efe0`. Manifest includes 328
selected paths; self plus this receipt and final numbered record are excluded
from their own digest graph. Completion record/commit pins these late artifacts.
B1 manifest and its immutable phase record/receipt are retained unchanged.

Source: vasiloglou/gnd, accepted runtime pin ac4be67afdddde0b2b2095a6cd383bc13852758c,
recorded high-water d8ac975e080a428fd7e32aea493cad722e54f7d1. Source-private observer
verified the exact 230 runtime Git blobs and source/target bytes, plus lock and
config origin identities; affected committed/working/untracked deltas were empty.
The target config is an explicit adaptation, runtime and lock are exact imports.
Source originals/obligations remain canonical and no unit is transferred.

[Hosted CI](https://github.com/vasiloglou/gnd-public/actions/runs/36929617118)
succeeded at the reviewed profile checkpoint, Python 3.11.16 / uv 0.10.10,
43 default and 32 selected package cases. First run 36928728485 at 081e3a8 failed
strict sdist metadata checks under uv 0.12.21; failure retained privately with
digests. The correction narrows to the measured tool profile, not the archive
allowlist. Local final 75-case gate also exited 0. One reviewer, not a panel;
scoped full/repair/profile reading found no remaining blocker after reproduction.

All 12 units remain source-owned; original 218 question states retained. Before
handoff, discharge actually triggered obligations or obtain an explicit ruling.
No target publisher/release/visibility/upload is enabled. P3 full tests/workflows
and P4 final contributor/artifact profile remain pending. Missing original 4,001
assurance files are an approved omission verified by actual reader behavior;
synthetic authentication controls have no positive proof coverage and never ship.

Rollback: revert named B2 commits only after inspecting unrelated work. Retain
this receipt and original source pin; no reset, force push or two-way sync.
New source deltas require a new attribution receipt rather than editing B1/B2.
New authoritative work becomes canonical here only after an accepted unit handoff.
