# RF9 cumulative code review

Review complete; repairs remain open. The most serious confirmed defect is a
pre-existing acceptance-integrity hole: a real failing v7 work session can pass
the work-acceptance gate after only its terminal claim is changed. RF8 also
introduced a model-equality side effect, and RF3 broke selected runtime annotation
resolution. Four verification weaknesses and one stale test limit the milestone's
current evidence. The missing-best helper failure below has a narrower reproduced
boundary than the external reviewer proposed.

Subject: d440b2e37449ef46647d18c491c46d9bb8d3e851.
Pre-refactor source: f5a83186f7c2215ac2b2afb0a010c2294eaa433a.
RF9 changes only planning and review evidence. No source, tests, tools, frozen
fixtures or ownership units were repaired. Severity indicates consequence;
blocking/hardening indicates relevance to a future repair/acceptance decision.
No milestone acceptance or merge recommendation follows from review completion.

## Findings and disposition

### RF9-F1 — P1 / blocking: terminal acceptance is not bound to case acceptance

**Sites:** `src/gnd/exp/close.py:953` and `:1185`;
`src/gnd/exp/session_replay.py:478`; `session_records.py:788`.
**Origin:** pre-existing, independently observed through the exact f5a8318 close
module with current compatibility dependencies. Both original and final replay
omit this v7 terminal-disposition revalidation. This is separate from RF1-OQ2's
missing-result CLI resume refusal.

A real local v7 work session with two failing candidates exits15, disposition
stagnation, with a selected attempt for which `contract_accepts` is false. The
original work gate returns `unaccepted-session`. Changing only `result.json`
fields `disposition` and `terminal_reason` to an accepted claim makes
`_work_findings` return `[]`. Attempts, feedback, best pointer and their digests
are unchanged. The typed result reader accepts the changed document. With no
walk floors, the close path checks identity without checking required snapshot
case acceptance. Expected: an accepted terminal claim must be justified by its
retained evaluation and termination semantics. Observed: the gate trusts the
claim after identity validation. An invalid extra `reason` field is correctly
refused, so this is not a bypass using an invalid wire document.

**Evidence:** `evidence/RF9/reproductions.py`, result `C_terminal_acceptance` in
`reproductions.json`; Area C also independently isolated the gate in memory.
The primary used real local producer/session files. This proves the work gate,
not exit0 from a complete close command with every other experiment obligation.
**Target:** session acceptance-integrity successor; recompute/bind terminal
acceptance, with unchanged honest acceptance and forged-terminal rejection cases.
No production fix is authorized by this review.

### RF9-F2 — P2 / blocking: an RF6 test contradicts approved RF7 semantics

**Site:** `tests/test_rf6_index.py:36`.
**Origin:** stale assertion introduced by the RF7 transition; the stricter
production behavior is approved and is not a regression.

The fixture uses `inherits_reference: "yes"` and expects the `truthy` primitive
variant to return `String`. RF7 requires literal `True`; both variants return
None. The exact existing node exits1 with `1 failed in 0.06s`. Expected: the test
should express the approved restriction and retain a positive literal-True case.
Observed: it asserts the superseded answer. This is a current focused failure,
not an inference that a broad suite has run or failed.

**Evidence:** `evidence/RF9/stale-test.txt`; Area C direct probe.
**Target:** RF7 affected-test successor. Adapt the fixture/expectations and cover
both allowed and refused values; do not restore truthiness to satisfy this test.

### RF9-F3 — P2 / blocking evidence claim: RF6 exact query inventory has a hole

**Sites:** `tests/test_rf6_query_policy.py:21` and `:92`.
**Origin:** new RF6 exactness claim over pre-existing production reads.

The direct scanner misses fixed `getattr`; the dynamic scanner explicitly
excludes literal selectors. Adding `return getattr(model, "fact_types", ())`
to an in-memory source copy changes neither inventory, and both exact-policy
assertions still pass. Four current omitted expressions existed at f5a8318:
`src/gnd/synth/guarded.py:184`, `conformance/structural.py:275`,
`conformance/structural.py:792`, and `conformance/architecture.py:431`.
Expected: each live query read is counted and routed or reasoned. Observed:
a supported Python spelling is invisible. No wrong production query answer was
established; the exhaustive-inventory claim is unsupported.

**Evidence:** `reproductions.json` / `D_literal_getattr_inventory`, including
predecessor expression comparison and both successful dirty-policy assertions.
**Target:** RF6 query-policy successor; count literal getattr, classify existing
sites and add a dirty sibling that necessarily changes/refuses the inventory.

### RF9-F4 — P2 / hardening: serialization changes contract equality

**Site:** `src/gnd/exp/session_contract.py:1075`, especially `:1085`.
**Origin:** RF8 runtime profile cache; direct comparison against the exact
pre-RF8 de4eed6 contract module preserves equality.

Construct two valid normalized contracts using validated v2 field values through
`DataDrivenContract(**fields)`. They initially compare equal. Calling
`model_dump(mode="json")` on only one populates its private `_profile`, after
which they compare unequal; serializing both restores equality. Serialized wire
bytes are identical. Pydantic includes private attributes in equality. Expected:
serialization does not alter semantic equality of otherwise identical contracts.
Observed: lazy cache initialization alters it. Usual `model_validate` already
populates the cache; this narrower direct-construction API path is the confirmed
trigger, not a demonstrated CLI failure.

**Evidence:** `reproductions.json` / `primary_contract_equality`.
**Target:** session-profile successor; ensure cache lifecycle does not affect
contract equality, with direct construction, copy and serialization controls.

### RF9-F5 — P2 / hardening: RF8 body observer hides an early identity-cache write

**Sites:** `tests/support/rf8_sources.py:22`;
`tests/test_rf8_structure.py:57`; actual write `session_replay.py:502`.
**Origin:** RF8 observer normalization.

The predecessor transform removes any exact `store._best_identity = identity`
assignment irrespective of position/count. An extra assignment inserted in an
in-memory AST immediately after identity construction, before pointer/terminal
checks, changes raw AST but preserves the recorded predecessor hash. An unrelated
assignment is detected. Expected: only the explicitly authorized cache extension
at its validated location is normalized. Observed: an early cache mutation can
be hidden. That mutation could expose unvalidated identity following refusal.
Current production writes after validation; this finding proves masking by the
moved-body predicate, not that all tests accept the mutant or that the defect is
present in current runtime code.

**Evidence:** `reproductions.json` / `D_early_cache_observer`.
**Target:** RF8 physical-observer successor; constrain location/cardinality and
include an early-write dirty control plus refusal-state runtime assertions.

### RF9-F6 — P2 / hardening: graph omits implicit package-parent execution

**Sites:** `src/gnd/codegen/service.py:7` and six other service imports retained in
`reproductions.json`; `tools/gnd_arch.py:324`; `tools/gnd_layers.json:194`.
**Origin:** RF5 service placement exposes an existing AST-instrument limitation.

Seven lane services import infrastructure-mapped `gnd.commands._output`; Python
also executes parent `gnd.commands`, mapped as entry. A fresh process importing
`gnd.codegen.service` has `gnd.commands` in `sys.modules`. All seven parent edges
are absent from the explicit graph, which reports zero wrong-way edges.
Expected: a runtime dependency guarantee accounts for parent initialization.
Observed: the metric covers explicit imports only. The parent initializer is
currently only a docstring, sampled orders succeeded, and no hidden harmful cycle
or command failure was established. The explicit zero-SCC result remains valid
within its instrument's scope.

**Evidence:** `reproductions.json` / `B_parent_package_edges` and
`architecture-comparison.json`.
**Target:** architecture-policy successor; model parent initialization or place
shared output under a suitable package, then test this route without blanket
layer exemptions.

### RF9-F7 — P2 / hardening, limited reach: missing best crashes declared-case helper

**Site:** `src/gnd/exp/close.py:966`.
**Origin:** pre-existing; old code unpacks a None tuple, new code dereferences None.

After moving a temporary run's attempts, launches and best pointer aside,
reconstruction succeeds with no best. The typed forged result still names one.
Calling `_declared_case_findings` on these real files raises AttributeError in
current code and TypeError in the exact f5a8318 close module. Expected: return a
structured mismatch finding. Observed: exceptions escape the OSError/ValueError
catch. **The outer work gate correctly refuses this empty-launch fixture before
calling the helper.** The broader reviewer claim of a full close traceback has
therefore not been established; a launched run with no eligible attempt was not
produced here. This is a reproduced local defensive-code defect with an explicit
unverified reachability boundary.

**Evidence:** `reproductions.json` / `C_terminal_acceptance.no_best_gate_crash`.
**Target:** session acceptance-integrity successor alongside F1; guard absence
before dereference and test a genuine launched/no-eligible case before claiming
end-to-end regression coverage.

### RF9-F8 — P3 / hardening: moved digest helpers lose runtime annotation resolution

**Sites:** `src/gnd/values.py:151`, `:216`; compatibility aliases in
`src/gnd/population.py:60`.
**Origin:** RF3 relocation.

`typing.get_type_hints(gnd.population._content_digest)` and the corresponding
`_model_digest` call now raise NameError for Population/Model. Both resolved in
the exact f5a8318 population module. The moved definitions only import those names
under TYPE_CHECKING. Expected: preserved callable annotation introspection.
Observed: old aliases point to function globals missing the referenced names.
Digest execution itself is unchanged. The similar reference-model helper issue
already present at baseline was excluded.

**Evidence:** `reproductions.json` / `A_annotation_resolution`.
**Target:** compatibility/typing successor; restore supported introspection without
reintroducing the removed dependency cycle.

### RF9-F9 — P2 / hardening: legacy offline scan misses from-import form

**Sites:** `tests/test_measure_offline.py:80` and `:300`.
**Origin:** pre-existing, source-owned import-walk debt; not RF2–RF8 regression.

The regex records `urllib` for `from urllib import request`, never matching the
forbidden `urllib.request`. An in-memory addition of that import and a deferred
`request.urlopen(...)` expression to session_runtime.py is visited and the actual
generation-lane scan still passes. A sibling `import urllib.request` is detected.
No network call is executed, and no planted network call was found in current
source. Expected: both forms are forbidden by the offline guarantee. Observed:
one spelling evades the guard. The regex AST is identical at f5a8318.

**Evidence:** `reproductions.json` / `D_offline_import_guard`; primary visited the
mutated file once (the independent reviewer reported twice in its own harness).
**Target:** source-owned OQ-V52-P1-IMPORTWALK-1 successor. This review neither
transfers that unit's authority nor rewrites its original tests or certificate.

## Review coverage and measured improvement

| Area | Confirmed scope | Gaps |
|---|---|---|
| A behavior | Selected CLI dispatch/refusals, aliases, digest variants, pickling, three live handler lookups; annotation regression | Every successful command/encoder, provider execution, platforms |
| B architecture | Fixed-base/current explicit graph, seven implicit parent edges, 16 registry hooks and current family sets | Harmful implicit cycles, installed-package/import-order completeness |
| C state/input | Focused cache/resolver/profile/replay/close paths; feedback tamper hypothesis rejected by validation | Full wire/legacy replay matrix, every checker/synthesis consumer, races |
| D evidence | Selected RF1/2/3/5/7/8 observers/normalizers; three dirty-control blind spots | Every golden/test, broad/installed/release suites |
| Primary | Nine findings above at their stated boundaries; unchanged 432 controls; 625 old direct bindings in 12 modules | Binding existence is not full behavior/introspection coverage |

All four assessments were separate native Codex gpt-6-sol/xhigh contexts. One
reviewer is one reviewer; four shared-provider readings are not model-diverse
consensus, the maintained panel, certification, or milestone-close review.
Area C's first execution failed on capacity before a final return; one unchanged
source retry completed it. No repair-review round ran. Raw returns are retained
in the four `phase-RF9-<area>-review.md` notes with declared path substitutions.
Primary reproductions outrank candidate wording; F7 explicitly narrows C's claim.

Current metrics and their predecessor comparison are in
`evidence/RF9/architecture-comparison.json`: same current AST instrument, each
revision's own layer map; baseline entry-point policy is absent (null, not zero).
Modules increased from148 to227; explicit runtime SCCs fell from5 to0 and explicit
wrong-way edges from27 to0. Private import sites increased from242 to670;
AST-identical candidate groups fell from15 to12. The largest module shrank from
9088 lines (cli) to4890 lines (model._validation). Module sizes, private imports and duplicate candidate
groups are retained as measurements, not automatic quality scores. Compatibility
facades account for some private imports; identical AST groups require semantic
review. F6 limits any broader runtime-graph interpretation. The committed initial
local status described explicit graph results without this qualification; this
report supersedes that wording and the earlier pending-provider status.

## Open work and review boundary

F1/F2/F3 block their respective acceptance, focused-test or exact-inventory claims;
F4–F9 are hardening work with the qualifications above. RF9 is complete as a review
with findings, not complete as a repair program. Each target above is proposed
successor work requiring the owner's repair instruction. No repair phase number
is invented or automatically executed.

Existing RF1-OQ2/OQ4/OQ6/OQ7, source-owned ledger questions, RF6b/RF7/RF8 original
budget misses, shim retirement, historical-body/ownership reconciliation and
milestone-close obligations remain open under their prior owners. No old
certificate is reused for changed bytes. No production publication or merge ran.
Focused local controls do not establish Linux, installed/release, timing, race,
provider-oracle, broad historical or certification correctness. Exact probe exits
are evidence of reproduced counterexamples, not a passing product test suite.
