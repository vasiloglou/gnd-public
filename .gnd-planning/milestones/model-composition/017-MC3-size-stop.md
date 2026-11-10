---
milestone: model-composition
station: "MC3 mandatory size pause"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: MC3-size-stop
date: 2026-11-10
gate:
  command: "measurement: git gross Python additions plus new helper and extracted retained validation-policy lines"
  exit: "n/a -- size observation, owner ruling pending"
evidence:
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/size-stop.json
    sha256: 75e888fdd79db317be85ad7bceda30d76c0a600dd80fb881eb233e8176e7bc1a
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/017-source-manifest.json
    sha256: be4438ee1db89e9d3149bd6d6b3b5d18ff63f15696b62cb41ba908fb538aebad
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/017-paused-source.patch.json
    sha256: 01e0972562ffd9c84f2a26ae512c95efe5fbc80650a0c5304f471fc7832730ba
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/017-paused-spec.md
    sha256: aeef7beb1d61ec78908a96bf65f0916bb47142e9431e4bbf6c91a45ef01a3ed1
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/loader-impact-fixed.json
    sha256: 67f125f5a83ff2d80f1ed5fac379ba69e6e59df19e15307c61db385750e55af0
---

# Claim

MC3 reaches615 conservative runtime lines against its600 stop; implementation pauses for an explicit owner ruling. Test/support additions total251 against900. The owner was asked to raise the stops to1400/1400; no answer is inferred.

## Measurement

    tracked_added_runtime: 308
    new_untracked_runtime: 257
    retained_moved_runtime: 50
    runtime_conservative: 615
    test_support_added: 251

The base is5a083f469d0a14271c3417401c6ae2fd046a165a. Git numstat counts gross added Python lines under src/tests. The new untracked helper is counted in full. The two extracted validation-policy homes retain50 physical lines that git treats as context; add only those lines not already counted in added hunks, so no moved line is counted twice. size-stop.json identifies every such line. The patch and per-file manifest retain the actual partial source for later review/reconstruction.

## Authority and current state

Plan0.7 says “A phase pauses for the owner past1.5 times its estimate.” The approved MC3 spec fixes that at600 source/900 test-support. MC1's1100/1900 exception names MC1 only. The milestone auto delegation does not silently override this explicit stop.

The new schema, private historical/analysis loader, ownership helper and authored attachment replay are partial and uncommitted. Existing loader/reference/evolve-loading selection is229 passed in17.30s after correcting a rejected analysis-collector regression. The initial feature harness was33 failed/3 retained-control passes before runtime edits. Preview/publication/CAS/finalization wiring, CLI flag/output, discover/ILP writers, full adversarial tests, catalog/source successors, normative grammar and independent review remain incomplete. No passing MC3 candidate, phase completion or merge is claimed.

## Boundary

This is an observed limit, not a phase acceptance or an automatic owner ruling. No further implementation crosses the stop until the owner's actual answer. The proposed1400/1400 is a scoped budget request, not permission to expand features. MC2's fixed-head merge and the revised business-page reaction remain separate pending asks. No milestone close, certification or publication is established.

## Open questions

- Owner: raise MC3's stop to1400 source/1400 test-support, or keep the present stop and choose a plan amendment/reduction.
- Once ruled, preserve this snapshot and ruling before resuming the approved required scope; count again after each lane.
