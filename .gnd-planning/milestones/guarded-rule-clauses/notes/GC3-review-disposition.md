# GC3 independent review disposition

The delegated run used the owner-selected Claude Code Opus reviewer with
high effort. A tool-free session reviewed the exact Python candidate diff
from `84120554` to `20172ace`, with the phase contract on stdin. The result
exited 0. The reviewer assessed the code statically. The executor verified
the published report and ORM schemas and reran the affected tests.

1. **Shared budget.** The candidate's reference path rescanned each
   alternative's relation per binding. Both paths now prepare each
   relation once per alternative and charge candidate rows, binding
   evaluations, joint witness probes and reached term work consistently.
   Tests cover both sides of exact comparison and exists limits and
   compare the wider 6,000-binding population through both evaluators.
2. **Temporal budget.** Existing single-form comparisons already enforce
   10,000 temporal applications across bindings. The disjunction retains
   this sub-ceiling and charges temporal work to the shared ceiling.
   It distinguishes the attempted over-budget application from an unrelated
   unknown that follows an exactly exhausted temporal count.
3. **Diagnostic alignment.** The existing projection keeps order and
   cardinality. The renderer now receives complete binding-and-failure
   objects from the projection that produced the public binding values.
   Projection, report schema and same-relation atom-index tests pass.
4. **Totality and shared walk.** `atom_bind` already guarantees a
   dictionary for malformed input. The direct public admission test confirms
   refusal, and the term walk now visits full disjunctions as well as local
   scopes.
5. **Synthesis.** The disjunction generator uses the same shape refusal for
   function-shaped direct comparisons. The test independently rechecks
   both emitted populations against the public checker.
6. **Validation scope.** Common temporal binding conflicts are emitted once
   at the rule path. Each alternative checks its local conflict against the
   common scope. No alternative may import another's local variables.

The CLI compatibility successor records the opt-in text additions. Legacy
reports retain their diagnostic versions and wire fields. Three older
exists-kernel tests expected a three-element private binding result after
GW0 had added observations as a fourth element. Their assertions now
use the observed interface, including the larger guarded corpus.
