Retained reviewer final message verbatim except declared machine-path replacement with <worktree>/<home>. One reviewer is one reviewer. Input HEAD e404262; native read-only review exited0.

## Finding

**Medium · blocking for the RF6-C1 evidence claim.** The query-policy scanner recognizes `.fact_types` and literal `.get("fact_types"/"roles")`, but not subscription reads ([test_rf6_query_policy.py:21](<worktree>/tests/test_rf6_query_policy.py:21)). I reproduced this without editing files: adding a synthetic `model["fact_types"]` read produced no count, and the 299-occurrence policy assertion still passed. An actual `document["fact_types"]` read exists at [rai_import.py:232](<worktree>/src/gnd/rai_import.py:232), with no separate subscription inventory found. The **299 ≤ 310 < 320** result holds for the scanner’s declared scope, but the check cannot establish the spec’s full direct-read and separate-inventory criterion ([phase-RF6a-spec.md:40](<worktree>/.gnd-planning/milestones/code-refactoring/notes/phase-RF6a-spec.md:40)). A repair needs a regression observed red on these pre-fix bytes.

## Claims checked that held

Read-only probes confirmed cache refresh after nested mutation, detached snapshot results, live-row historical aliases and `SimpleNamespace` shapes, both primitive policies, canonical constraint reference order, and the range alias. The source and direct tests show six registry paths, including registry-only fake-family extension. The layer map covers the three new homes; recorded metrics show no wrong-way edges or unresolved dynamic imports. Source-observer tests include an omission negative control.

I checked that all 167 mutation row IDs and expected-red answers remain unchanged. The retained report records six killed affected mutants; I did not replay that lane. Retained gate outputs report **744 passed, one historical metric deselected; 552 passed, one configured exclusion; and 40 direct passed on each of local Python 3.11 and 3.13**. These are recorded results, not gates rerun in this review.

Direct index tests lack an explicit two-parent `supertype_closure` case and committed mutation cases for `rejected_proposals` and `deontic_notes`; targeted read-only probes found no cache failure for the latter two. I ran no broad or prohibited lane. Old certificates remain unavailable, there is no new human source-control attestation, and RF6b is outside this review. The same-module family extraction and routing are one behavioral unit. One reviewer is one reviewer.
