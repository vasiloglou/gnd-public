---
milestone: pyrel-applications
station: ci-repair
skill: "n/a -- repository development, owner-directed repair outside a numbered phase"
scope: ci-repair
date: 2026-10-13
source_base: b3fdcba
---
# CI repair before the merge path

Owner direction, 2026-10-13, in chat: "Fix, finish, then merge" -- fix the six
failures found by the local CI mirror (011 addendum), finish the milestone, then
merge PR #21. This repair is owner-directed and recorded here rather than inside
a phase spec. One more failure was found while repairing: PA5R's query-row swap
broke four tests in tests/test_rf6_query_policy.py, which were outside PA5R's
focused selection. That is a PA5R miss, repaired here.

| Failure | Repair |
|---|---|
| test_doctor_uninstall (3) | process-milestone and start-milestone pinned as repository-local skills (LOCAL_SKILL_NAMES, LOCAL_SKILL_FILES, UNMANAGED_ROOT_ENTRIES); the local-skill test walks all three |
| test_rf7_structure | pyrel_runtime.py deduplicates rows by canonical text while keeping the original values; no json.loads remains. Witness key order is preserved by sorting |
| test_rf9_repairs (2) | reads the effective policy (base plus authenticated phase successors), as test_rf6_query_policy already does |
| test_rf6_query_policy (4, PA5R regression) | PA5R query-successor.json and dynamic-query-successor.json chained from PA4; PHASES includes PA5R; the separate render-only chain is folded in |

Emitted program bytes changed again (rf7 repair); evidence/PA5R/pyrel-successor.json
"after" is 60a263a1.../98872 bytes.

## Gates (verbatim)

- tests/test_rf6_query_policy.py tests/test_rf9_repairs.py tests/test_rf2_pre_move_pins.py tests/test_rf7_structure.py: exit 0, "67 passed".
- tests/test_doctor_uninstall.py with the venv on PATH (as CI has): exit 0, "80 passed". Without it, the PATH-verdict test fails in this shell only.
- Native pyrel_oracle suites: "1 failed, 94 passed"; the failure is the pre-existing ring disagreement (open question in 011), not in CI's default lane.

## Evidence

- evidence/PA5R/query-successor.json: bdc2c2014b921fb7da9d1088bd6bc566730fcc759c92ad1fe9d2d14fec293490
- evidence/PA5R/dynamic-query-successor.json: 34498d014a78622010d0028bf793fe46caa51fcb2530b72747a12f05a37d71cd
- evidence/PA5R/pyrel-successor.json: 527dc501b608dacc659d407912a2d9673c2ec18477f76dcd4d0f8585d0e9d1ee

## Boundary

No model, corpus, answer or checker-semantics change. Full-suite confirmation runs
in the local CI mirror on the final commit before push.

## Addendum after the PA6 repair reading (2026-10-13)

- Gate transcripts: evidence/ci-repair-gates.txt (23d457dcaf9e95247a08d57662a9c322ce28169d9d92e1a3d16befbae43a28a0).
- Provenance correction: this repair rewrote one closed PA5R file and created another under evidence/PA5R.
  evidence/PA5R/pyrel-successor.json "after" moved from 56c4e7c2... to 60a263a1...
  (the rf7 dedupe change), and evidence/PA5R/dynamic-query-successor.json, created
  here, also carries rows that come from this repair (_derive canonical[key],
  guarded witnesses[key]). Their reason text names PA5R only. Both are superseded
  as PA5R-only evidence: they describe PA5R plus this repair. 011 binds
  pyrel-successor.json at e8f81f84... (pre-repair); current bytes are 527dc501...
  dynamic-query-successor.json was created here and is not bound by 011. A split
  into separate PA5R and ci-repair links remains an open question for the close.
- The full suite on the final merged commit runs in the local CI mirror before push.
