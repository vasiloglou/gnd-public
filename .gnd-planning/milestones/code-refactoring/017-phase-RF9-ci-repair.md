---
milestone: code-refactoring
station: phase-RF9-ci-repair
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RF9-ci-repair
date: 2026-10-06
source_base: d6f1e8aeacab902914e22b2dab799b65f879fdda
source_subject: a390599c1a8fe8bdf13596e2f71805b6a94e109d
gate:
  command: "/private/tmp/rf2-py311/bin/python -m pytest -q tests/test_public_classification_scaling.py tests/test_rf6_packages.py tests/test_rf9_ci_repairs.py tests/test_rf1_pin_harness.py tests/test_rf3_core.py tests/test_rf4_peripheral.py tests/test_public_construction_site_guards.py tests/test_measure_offline.py tests/test_public_adapter_literal_controls.py tests/test_public_v72_reader_boundaries.py tests/test_rf8_structure.py tests/test_v6_phase2_adapter_mutations.py --tb=short"
  exit: 0
  output: "1418 passed in 73.60s (0:01:13); 1418 passed in 68.85s (0:01:08)"
slow_gate:
  command: "uv run pytest -q -ra --tb=short"
  exit: 0
  output: "13944 passed, 400 deselected, 1 warning in 2083.37s (0:34:43); 13944 passed, 400 deselected, 1 warning in 2019.50s (0:33:39)"
  note: "Fresh detached source_subject clones; both minors on macOS. This is the failure-driven replay of the owner's selected CI gate."
evidence:
  - {path: .gnd-planning/milestones/code-refactoring/016-phase-RF9-repair.md, sha256: 7e2eeb7b67ed5924f79c6cb2498349ab183aab208641c07c5c550786728291c2}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF9-ci-repair-spec.md, sha256: 3aa9b70bc4e3a574424a456c6de5dcdafe7e01a3238fb857dbc7879baa5bc61c}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF9-ci-repair-codex-review.md, sha256: ffe5859950a9ebe8217309c6b0b329d8a681ca621e03139b9527ae50a32c8b40}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF9-ci-repair-codex-repair-review.md, sha256: bd68603840a7f0ed0e7f4492072f759100824b10a6f3069cba2ce9884173af24}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/frozen-controls.json, sha256: 633603f69199c82cde226e4adef6da1d10018ba27b85a9cd9da8ce5b416703ba}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/approval.json, sha256: 9f0e10693836b26a10fbd3e9d2e98969bd14d12fb2b0d6997ac668c9c6b451ca}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/baseline-report.md, sha256: f39f7df3bbe3321bbe0d9b2229d9b12f462d513f96886543fc6b4522df407c55}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/corpus-red.txt, sha256: 223267204c647167568492d66c3ed412e809b71ff61385a56fb76e9e863173b1}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/body-successors.json, sha256: c51b6ca8b877b329385de725b18eb42b43368bb44dfb1f70f1d3e91905b15457}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/pyrel-successor.json, sha256: 4776709998b7e5c3b641f80c5f2c2199854a1cc2aa4115e2bb340078cd68745d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/mutation-retargets.json, sha256: 7bff4b3302a2899b28cf02b9a8d9ca6135e257b74bd5e1b4c46c2dac5bd9e863}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/mutations-status.json, sha256: b2f20c64c388b5d8921d011510992bde42fd7ddbda13bf7c487c7d48e45c6b57}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/mutation-mutation-report.json, sha256: 757c6733661ba6201abaabe7e1d02d1b24b2bbd192368acb20bd05630c124010}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/final-neighbor-status.json, sha256: 532d02655c5ab4f0c302dc56ba541f369cde8649f70695e6e406004b87b6c630}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/final-neighbor-311.txt, sha256: 28d0ca54dd6ed3ce8a936e1a5c27d542a2d1bcdcc0911a7e1b8d1558180a3188}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/final-neighbor-313.txt, sha256: c96cb81a15124244bb5623d4d3ab8eefeb9670a051734d110b661076b631cc35}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/production-source-identity.json, sha256: 44b76a1a0adab45b29777dcacec0506b0cf937508f05e3d86a1702d21b74f025}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/manifest-adaptations.json, sha256: 72195941d0c7472cbec144ad0a0deebefc0402e803d2273dc49860ab396a502f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/metadata-checks.py, sha256: 7a80c105022e459eeb7ce843a73237305042f6502096771f8564b3889f6d6806}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/metadata-final.txt, sha256: 80ac32db8ced69d4d424a0a66e25c533b290ec5bf88e9adc9819239b6fd4864e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/ci-status.json, sha256: c9afb1dbb5acc51b8531967b8209540f68b5e2c1f6823db839671ccef964a5fe}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/ci-output.txt, sha256: 3faea777be02cfbe6f2846691ce1e133ab5f9d38103dfe1c1d153354d8286084}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/budget.json, sha256: f734f3f87470c5ffcca0a295e79b01f798e3c68f39f16c6a8ed09fa7c4f469fb}
---

# Claim

The selected full local CI replay exits0 for both Python 3.11 and3.13 on macOS.
Record 017 is an RF9 repair successor to 016, with delegated approval from the
owner's “do repairs” instruction and explicit native-provider authorization.
The tested commit is named above; the subsequent record/evidence commit changes
no production, test, tool, dependency or skill bytes.

## What shipped

The model facade delegates three mutable counters to their defining validation
home; unknown names still refuse. Pool loading maps shared strict-input refusals
to PoolValidationError, preserving ordinary malformed JSON and schema/coherence
order. The artifact reader is an explicit same-object compatibility import.

Current observers resolve actual package, encoder, patch and semantic-owner homes.
RF4/RF6 bodies and PyRel output use authenticated named successors rather than
rewritten originals. Cross-minor AST serialization changes only empty-list field
spelling on a copy. Two reader observers share the exact RF9 reconstruct successor.
Twenty-seven adaptation rows preserve original source/baseline fields; 432 frozen
controls, the units ledger and distribution-authority guard remain unchanged.

RF7's loose DateTime/fractional-offset and JSON overflow refusals stay enforced.
Reachable instant arithmetic mutants remain killed; the now-unreachable offset
microseconds dimension is retained as refusal coverage, without arithmetic credit.
Eight moved mutation sites preserve historical IDs/expected-red meanings and
have 8/8 kills at 733389d, with passing unmutated controls. No 167-row replay is claimed.

The Markdown guard shares one container-aware fence reader for Python bodies and
outside-fence fallback lines. Titled/tilde/quoted/list Python, nested containers,
non-Python text fences, body indentation, unmatched closes and malformed code have
named controls. The classification scaling test resets/reads the physical counter,
retaining the public classify call and its original work/time limits.

## Gate output (verbatim)

Current affected gate, exact argv and file hashes in final-neighbor-status.json:

    1418 passed in 73.60s (0:01:13)
    1418 passed in 68.85s (0:01:08)

Full default, platform and installed artifacts at source_subject:

    13944 passed, 400 deselected, 1 warning in 2083.37s (0:34:43)
    13944 passed, 400 deselected, 1 warning in 2019.50s (0:33:39)
    160 passed, 1 deselected in 46.30s
    160 passed, 1 deselected in 50.13s
    10 passed in 869.83s (0:14:29)
    10 passed in 809.36s (0:13:29)

Lint over every changed source/test/tool path and the identity gate:

    All checks passed!
    432 frozen controls unchanged; exact27 adaptations; 241 production files identical to733389d; current observer identities match.

ci-status.json retains all 23 command vectors/exits/durations for each attempt,
raw log digests, artifact digests and build profiles. ci-output.txt declares
operator-path sanitization and collection-node-list omission. Other gate streams
are retained; raw hashes refer to the original temporary streams. The failed
733389d suites each had 3 failures/13,890 passes from a facade-counter shadow;
counter-sequence-red.txt reproduces it before the test isolation fix.

## Measured criteria

Current graph: 228 modules, runtime/module-only SCCs 0, wrong-way edges 0, allowances 0.
Raw private imports 680; 479 exact inventoried identity reexports are accounted
separately. Fixed 32-module RF3 cohort: raw 289/coupling 9 <= 60; fixed 162-module RF4
cohort: raw 549/coupling 89 < 198. No raw-count reduction or combined-SCC claim.
Production additions 18; no production move. Final exact footprint/other additions
are in budget.json: original 80-path ceiling and delegated 90-path evidence amendment
are both retained, with the original exceedance reported rather than erased.

## Adversarial and refactoring review

One reviewer is one reviewer. The initial native assessment of ed188dd found the
titled-fence bypass, reproduced RED and fixed at 8c13d32. The one repair assessment
of 8c13d32 confirmed that fix and reproduced two neighboring container/text-fence
defects. Four exact cases landed RED before a390599; additional positive/negative
neighbors pass locally. The two-assessment budget is exhausted: final successor
bytes have local RED/GREEN evidence, not a third native opinion. The unsupported
model launch failed before assessment and is retained separately. Native review
could run focused cases; it did not establish the full current CI result.

Refactors EXECUTED: shared portable AST serialization, reader-successor selection,
exact compatibility inventory and Markdown/fallback extraction remove duplicated
answers inside test observers. Their refusal/dirty controls exercise the same
selected boundaries. No additional product refactor is needed for the narrow
counter, shared pool refusal and identity-export repairs. The previously deferred
combined package-initializer SCC design remains a milestone-close question.

## Boundary -- what this result did NOT establish

No Linux run, remote required-CI success, certification, publication, merge or
milestone close. The default 400 exclusions remain; historical/provider/proof/
census lanes were not independently selected. The fence reader is a bounded
source observer, not a general Markdown renderer or arbitrary Python security
sandbox. Pool byte-cap plain ValueError remains outside this named repair scope.
Explicit graph SCCs and combined initializer diagnostics are distinct. Original
phase bodies, goldens, before hashes and source-owned authority units stay historical.
GitHub's existing run 37504512801 was refused before jobs started because account
payments failed or the spending limit needs adjustment; local gates do not repair
that account setting. Final push/check status is reported separately.

## Open questions

RF1-OQ2/OQ4/OQ6/OQ7, RF7-R5 private ParserError, RF-D5 shim retirement, prior phase
budget misses, and ARTIFACT-COPIES/CANONJSON/IMPORTWALK/HELPER-TAIL retain their
original owners. Combined package reexport SCC interpretation -> code-refactoring
milestone close, as in 016. This repair neither transfers ownership nor recertifies.

## Refuted premises

Type-params-only AST normalization was insufficient: 3.13 omits all empty-list
fields by default. A package integer snapshot was not a live compatibility alias;
resetting that facade in scaling tests also hid actual measured work. Import-line
regexes missed compound/titled/container imports, while scanning all Markdown lines
falsely refused harmless text fences. Fixed original cohort metrics cannot compare
unfiltered widened inventories. RED/GREEN and before/after provenance are retained
in the cited evidence instead of replacing historical answers.
