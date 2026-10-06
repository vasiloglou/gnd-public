# RF9 repair successor

Owner-decided2026-10-06: "you have my approval to fix the issues", followed by
"continue". This is separately authorized implementation of RF9-F1–F9, based on
26dbff6abe53d020d6a933e48d99915089f52054. The original review and015 remain
historical. No RF10 or plan rewrite is inferred. Process-phase governs the repair
record016; the explicit fix instruction supplies the implementation gate.

## Obligations and rulings

| Source / rule | Repair obligation and discharge |
|---|---|
| RF9 F1/F7, blocking/hardening | Bind accepted patch-session terminal result to reconstructed final feedback and attempt count/identity; guard absent best; real session mutations |
| RF9 F2, blocking | Keep RF7 literal-True semantics; update stale RF6 assertion and include True/false/truthy controls |
| RF9 F3, blocking evidence | Count literal getattr fact_types/roles; successor exact inventory with named existing exemptions; dirty new-read control |
| RF9 F4, hardening | Runtime profile selection cannot mutate equality; shared immutable profile table removes per-contract lazy-cache state |
| RF9 F5, hardening | Remove only the single cache extension after validated best selection; reject extra/moved assignment; explicit changed replay-body successor |
| RF9 F6, hardening | Shared output moves outside entry package; old module explicit aliases; scans/patch owners follow physical home; parent initialization inventory used by layering |
| RF9 F8, hardening | Resolve Model/Population digest type hints without a runtime values→population cycle |
| RF9 F9, hardening | AST import parser recognizes from-import and aliases within existing offline roots; actual closure dirty probe |
| RF-R1/R2/R3 | Approval selects the named correctness repairs. Honest outputs/digests stay pinned; original RF1 fixtures unchanged; red cases precede code |
| RF-R4/R5/R6, SM2/3 | Output move atomic with shim, lookup-owner and scan changes; add shim inventory; retain original qualifications and moved-body byte semantics |
| RF-R7/R8 | units.json and distribution authority test unchanged; retain manifest predecessor rows/hash/mode for target adaptations; no certificate or source-owned OQ transfer |
| RF-R9/R10/R11, SM4 | Budgets below; no new command/flag/schema/family; complete map, zero allowances, focused direct and affected gates |
| Prior013/014/015 | RF7 semantics preserved; source-owned import-walk OQ remains open; prior budget misses/close work stay separate |

Standing rules: totality is checked at result/AST boundaries; existing IO caps
remain applied at reads. New AST work is linear in parsed source nodes and uses
existing bounded source sets. Validation order is retained except the explicit
terminal-integrity check before cache publication. Each shared import/query rule
has one parser/walk, all cases use it. Historical prose/results remain tied to old
bytes; new report/record cite current successors. Runtime experiments, not prose,
settle acceptance/ranking and annotation behavior.

## Design and implementability

F1/F7: `session_replay.reconstruct(store, contract, *, allow_terminal=False,
policy_sha256=None)` retains its signature. For terminal patch sessions, validate
result version, count, best identity and accepted disposition against the last
reconstructed operator feedback. This avoids requiring a custom-ranked best
candidate to be the terminal accepted candidate. Honest custom-ranking sessions
are a positive control. `close._declared_case_findings` raises a caught ValueError
when best_record is absent, retaining structured finding behavior.

F4: `DataDrivenContract.profile` returns the existing immutable table entry for
its current version without writing a per-contract PrivateAttr. Direct construction,
validation, copying, dumping and JSON schema retain existing wire semantics.

F8: Model is available from the documents leaf; the population digest annotation
uses a module-qualified ForwardRef at runtime, resolved when the historical
population API is imported. No runtime population dependency is added to values.
Test concrete get_type_hints results on the two supported Python minors.

F6: move exact output helper definitions to `gnd.output` (semantics); keep
`gnd.commands._output` as explicit identity aliases, including historical imported
bindings. Lane services import the new defining home. Physical source/patch helpers
use a new current-home map while the original RF5 evidence stays frozen. The
architecture tool exposes deduplicated implicit parent edges and includes them in
layer checks; explicit SCC metrics remain identifiable, with a separate combined
SCC diagnostic rather than silently redefining historical counts.

F3: `reads(..., include_literal_getattr=True)` counts fixed getattr on fact_types
and roles. Historical attribute/get-only metric explicitly excludes the new form.
A successor policy adds reasoned rows for existing reads and measures the same
expanded grammar on the original base; prior policy remains immutable evidence.
F5: predecessor-body normalization recognizes the validated tail position and
single occurrence, not an arbitrary assignment. Intentional replay repair carries
an exact successor AST observer, with dirty early/repeated writes rejected.
F9: `_imports(source)` uses AST Import/ImportFrom, includes base and possible
child names and resolves local relative imports during closure walking. Existing
root/policy scope is preserved; parse failure cannot report clean. Dynamic imports
remain outside this static guarantee and are stated as a limit.

All requirements are implementable using existing helpers and retained data;
no schema additions or unavailable acceptance input is required. The probe corpus
is executable pytest cases with honest and mutated siblings, authored RED before
production. This is the corpus-first instrument for the changed predicate; the
owner's named fix approval supplies delegated corpus/spec decisions, not a claim
that the owner personally inspected new artifact bytes. No optional spec panel.

## Verification selection and budgets

1. RED: new `tests/test_rf9_repairs.py` cases for F1–F9 plus the existing F2 node;
   emit exact commands, failures and source identity before production edits.
2. Direct: new repair cases, test_rf6_index, test_rf6_query_policy,
   test_rf8_structure, selected offline scan nodes and test_gnd_arch.
3. Impact: RF8 session/profile/store/replay/close/judgment controls; RF1 session
   and helper/CLI pins; RF5 relocation/handler/scan controls and relevant population
   digest consumers. Exact file/node selections and exits are retained per gate.
4. Metadata: map/allowances, old alias identities, original frozen control hashes,
   migration adaptation identity, lint and git diff --check.
5. One native read-only adversarial diff review; at most one repair review if a
   confirmed substantive review defect requires changes. One reviewer is one
   reviewer; no maintained panel handoff. Prompt on stdin, existing native auth.
6. Broad default/historical/evidence/census/provider-oracle/proof/distribution and
   certification work stays on explicit owner or separately scoped CI cadence.
   Changed historical opinions become unavailable; focused successors do not
   recertify source-owned or release units.

Budgets:80 touched source/test/planning paths;2000 added production lines,
2000 added tests/probes,1500 added non-evidence prose;1000 moved production lines.
These are bounded repair ceilings, not improvements inferred from audit numbers.
No repeated review loop. The source-owned import-walk ledger question stays open
although the explicitly approved target guard is repaired. The migration ledger,
original authority guard and RF1 golden bytes stay unchanged. No release, merge
or milestone close is authorized. Existing PR#10 remains the delivery surface.
