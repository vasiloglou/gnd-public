---
milestone: literature-identity
station: phase-LI5-reserved-input-freeze
skill: "n/a -- repository development under process-phase"
scope: phase-LI5-reserved-input-freeze
date: 2026-11-15
gate:
  command: "ruling: delegated approval (auto=true) of the reserved scoring inputs before answer-key access"
  exit: "n/a -- ruling"
evidence:
  - path: src/gnd/examples/literature/lineage_run.py
    sha256: a00b0cfabb5c5d05b4f0fb87e00ff24c860422fde08fb21b7c07dd1eb1ce34b1
---

# Claim

**Delegated approval (auto=true), 2026-11-15.** The milestone chat authorizes
this LI5 measurement control. The path rules and table are already frozen
in commit 3463cdd1 and [021](021-phase-LI5-rule-freeze.md). The scorer now
uses the checked model, population and record snapshots for each proof
request. This protects the exact bytes already verified by composition.

Four public reserved documents were annotated without the answer key.
The independent input preparation produced six statements and one same
decision. The prepared annotations and composed run remain local.
Their exact SHA-256s are:

| Artifact | SHA-256 |
|---|---|
| Reserved annotations | `5ac192e69b15f7a9c08570068a4f941a9948dc7b65ee360bb763541688172f19` |
| Reserved composition record | `cd2a83c87fdc80a25cea7794567a17a4ced90f24725951336ffd8e9d3471efe7` |

The score will bind these hashes and the matching reserved key hash
and report only aggregate counts. The named rule and policy files keep
their original freeze. The selected review instrument is one Claude Code
phase reviewer on stdin. The reserved sample size remains three cases.
