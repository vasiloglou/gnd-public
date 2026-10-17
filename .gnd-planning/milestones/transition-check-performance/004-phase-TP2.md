---
milestone: transition-check-performance
station: phase-TP2
skill: n/a -- repository development, not a gnd-solve station
scope: phase-TP2
date: 2026-10-16
gate:
  command: "uv run pytest -q tests/test_tp2_shared_fact_types.py tests/test_tp1_index_scope.py tests/test_transition_cost_workload.py tests/test_rf6_index.py tests/test_rf1_layering.py tests/test_public_transition_contract.py"
  exit: 0
  output: "88 passed (3.14.3, 3.11.15, 3.13.12) before the review successor; TP2 file with successor 6 passed on all three"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner selection
  reason: focused gate plus 813 affected-consumer tests and a 41-suite frozen-row run cover the change
---

# Claim

TP2 is complete under the owner-approved spec ([spec](notes/phase-TP2-spec.md), "TP2
approved", 2026-10-16). The implementer was Codex CLI, as the owner selected. The session
reviewed the diff, fixed the test guard, and ran every gate.

**What changed:** GND's 8 internal fact-type readers use the new non-copying
`ModelIndex.iter_fact_types_shared()`. The public `fact_types` and `iter_fact_types()` still
return detached copies.

**Results on the reporter replay:**

- `deepcopy_nodes`: 2,760,394 → 115,294.
- Every TP0 digest is identical.

## Gates

- **Focused gate:** 88 passed on 3.14.3, 3.11.15 and 3.13.12. The TP2 file, including the
  review successor, gave 6 passed on all three.
- **Affected consumers:** 249 passed, and 564 passed with 16 deselected.
- **Frozen-row run:** 41 suites, 756 passed, 62,026 rows served frozen.
- **Lint:** All checks passed!

## Measurements

| Counter (reporter replay) | TP1 | TP2 |
|---|---|---|
| `deepcopy_nodes` | 2,760,394 | 115,294 |
| `model_index_key_paths` | 26 | 26 |
| `checker_runs` | 25 | 25 |

**Wall time:** the in-process A/B (`evidence/TP2/ab_shared.py`) measured 2.82 s with
copying and 2.59 s with shared rows, −8.4%. TP1 and TP2 together, measured in-process:
about −35%, against a planned ceiling of −38% for TP1 + TP2.

## Independent review

One local reader ([notes](notes/phase-TP2-claude-review.md)). **One reviewer is one
reviewer.** Accept, nothing blocking. The reader traced all 8 readers: none writes, and
none lets a row escape the call. 12 mutants were tried. F1 (completeness) was fixed with
a successor test that its mutant kills. F2 and F3 are recorded in the spec findings.

## Refactoring review

**None needed.** The change is one accessor and 8 token swaps. The review noted (F3) that
the internal accessor is not underscored. Renaming it now would only change naming
convention, so it is left as an open question for milestone close.

## Boundary and open questions

- **The protection is a docstring contract plus tests.** Only the docstring stops an
  internal caller writing into a shared row; the tests check the 8 current readers and
  the suites that reach them.
- **Copy sites left as they are** (about 4% of nodes; spec §6). That includes the copies
  of operations, which guard `model.operations`.
- **Open, for milestone close:** an underscore name for the internal accessor (F3).
- **Next:** TP3, receipt-bound pre-state reuse (25 → 19 checker runs).

## Evidence hashes

[
  {"path": "src/gnd/model_index.py", "sha256": "c820a107ee8591e561c05745c863af9afcc6c095eeced5913e3027ea6ea8f540"},
  {"path": "src/gnd/checker/_core.py", "sha256": "886892aa7e111e8fa58d0b4241fa1f1cc62c347a84e6c8c022c01bdbc3d19c51"},
  {"path": "src/gnd/compiled_obligations.py", "sha256": "9ac13c82bb3a62376a9d7e2cef1dc312d9aca84b24a9fe71d735fa1d2d7bc05e"},
  {"path": "src/gnd/universe.py", "sha256": "5cb7d07bf0cd5b99bae0e4128300b98a0ba81e61cfc7923d67eb2f672ad9b0cc"},
  {"path": "tests/test_tp2_shared_fact_types.py", "sha256": "b5a85e24634b4a8854e5ba6bd2882050efc65aa565a5665d0ff96a24831fa799"},
  {"path": "tests/_tp2_freeze_plugin.py", "sha256": "5f078ba7a62ac747cc9595bfedfa1a15e86a0db04c344100a06e1f6ca322b13a"},
  {"path": ".gnd-planning/milestones/transition-check-performance/notes/phase-TP2-spec.md", "sha256": "717f7cfb3f5d8784afbbd30fc684e9ed8bc3dee14002ba060dbfe627cfa2e937"},
  {"path": ".gnd-planning/milestones/transition-check-performance/notes/phase-TP2-claude-review.md", "sha256": "14ec895c8f00e1d062831da5a7bb9170354e77cc3fba58dc082817d3b0fffd52"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP2/ab_shared.py", "sha256": "ae0ec0ff0e6b607f564de87956876e18d417b409c723ad502ea73f65a6af7225"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP2/ab_shared.txt", "sha256": "eed0420ff41eb302b1fce742fae486923044cabb98eba00afbcd40825e122a8f"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP2/consumers-1.txt", "sha256": "e000d0087364e95f9dfc178a24cd51f5e0509620198d6382d4279ed06e9a6930"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP2/consumers-2.txt", "sha256": "1598fb17724c96e5c49e8510329d5886fa8c323e7a2f9a2489b25ce6c48668a2"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP2/counters.json", "sha256": "8754858f42cd2824a6e3887002d52e6b2f9c96ef6187c05c2087b0a7ce76a4f9"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP2/digests.json", "sha256": "d736d4d75fd82b7c5fd42102515d6b43eb21946326eaa3ebfd6a5223a1d4ca1c"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP2/gate-py3.11.txt", "sha256": "715550ddd24ec760fd99b6151e3d09e1936d3f17eacecd1a5c81db2b9b7f9dd0"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP2/gate-py3.13.txt", "sha256": "2e25359070be40526c1af80da83c8797193fec83db21906d2065710be0723f2a"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP2/gate-py3.14.txt", "sha256": "3978f4578df26702a302d52ed1fa275a3d672e54c97990886f46a0f7485d5502"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP2/lint.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP2/review-mutants.txt", "sha256": "f2e3769a1a8610abfaa89834aae8c60670ab1492156af9e0085a40d44d326c63"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP2/timings.json", "sha256": "b70aa389209be2748c618fd6516e77cc8c0c88a72ce48e796b714ea0f13c60b4"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP2/tp2-file-py3.11.txt", "sha256": "83c67247758051e1d70a9458779e386b03a869bd24a655c8bfc39d14cc17a791"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP2/tp2-file-py3.13.txt", "sha256": "9af820608ed2ac237eed171c5ab65d036abc3dd5153c492c931800b7e82a01c3"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP2/tp2-file-py3.14.txt", "sha256": "c4cdf2c603d438447f7585b762716d2d427bddb8e303c40b12663257b9bb55b7"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP2/tp2_freeze_all.py", "sha256": "9323c4446c098f45cee46d7be8d1867b82bcef5a04f87cbe250ae5d33655f0da"}
]
