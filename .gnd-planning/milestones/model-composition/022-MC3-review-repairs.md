---
milestone: model-composition
station: "MC3 reproduced review repairs"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: MC3-review-repairs
date: 2026-11-10
gates:
  - command: ".venv/bin/pytest -q tests/test_mc3_evolution.py -k 'test_review_' --tb=short (before fixes)"
    exit: 1
    result: "4 failed, 89 deselected in 0.69s"
  - command: ".venv/bin/pytest -q tests/test_mc3_evolution.py -k 'test_review_' --tb=short (after fixes)"
    exit: 0
    result: "4 passed, 89 deselected in 0.48s"
evidence:
  - path: .gnd-planning/milestones/model-composition/notes/phase-MC3-codex-review.md
    sha256: f96e364aea458f71340794330c189e4d031ac9acadcffc59d9160389b41de6d0
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/review-parent-probe.json
    sha256: 49f6f1e43fcf9f7261dc807ec26845a34db5946a353eae463605924f99b0b1af
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/review-regressions-red.json
    sha256: 5ad84ec4e2298a3e191a18fbe607129dba882a256fd102d0afc2185752b300e6
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/review-regressions-fixed.json
    sha256: aac9c43c37514eceaf052d69d4d5c417bf04c658d7b62c6c003c8e6cb2f1a2ff
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/review-repair-source-manifest.json
    sha256: 46b97b692bc2c5397c6316da91cf7effcce673895499c3c1ee01990f58b0e1cf
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/review-repair-size.json
    sha256: bcc37f17b0d7db0bd0204746c8d80d30d76b6244c2ae0a9cae4f89f475cf02f2
---

# Claim

Two independently reported input/output defects were reproduced against candidatec93506e2 before changing production code, then repaired under the approved rule0.4. The four regression cases changed from red to green. This is a repair record, not phase completion.

## Review and relevance

One reviewer is one reviewer: Codex CLI0.163.0, gpt-6.1-sol, xhigh, ephemeral/read-only, existing authentication. It executed25 selected checks and small probes; the large gates, real disk publication/recovery, races and cap boundaries were not independently rerun. Read-only restrictions blocked some initial probe transports. Its final response is retained verbatim with a declared added header.

Finding1 is blocking: discover's report could select an included vocabulary for truncation. A parent probe intercepted both writes with exit0 under a canonical temporary root; the first default-temp attempt refused74 before discovery and is retained as a limit. Three direct/hardlink/symlink cases proved that a writer was reached before any dependency-output guard.

Finding2 was labelled hardening by the reviewer but is a blocking contract repair for this MVP: an authenticated historical include path can equal the includer path, and the model CAS was absent from the exclusion tuple. A real-filesystem regression reached the intercepted CAS with the matching live model. Both findings violate the already-approved unconditional input-only rule; neither adds a new feature.

## Repair and boundary

Discover reuses the single exclusion policy over its existing output tuple after verified include loading and before any write. Include-free output admission stays on its previous branch. Evolution adds its model destination to the existing verbalization/stage tuple. No resolver, identity algorithm, query-policy waiver or layer allowance changes. Measured dynamic syntax delta is empty; the prior exact MC3 inventory remains current.

The1400/1400 stop is satisfied by the bound measurement. Current-byte primary and impact verification is being rerun; one repair confirmation remains within the declared review budget. No further independent round, merge, certification or milestone closure is inferred.
