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

## Implementation observations and delegated amendments

2026-10-06, under the named repair authorization. Initial artifact approval SHA
in approval.json remains the initial spec identity; this section records the
concrete instrument findings rather than rewriting its history.

- The initial equality case omitted its helper's tmp_path argument; the corrected
  case was rerun RED before production (equality-red.txt). The initial parent-edge
  fixture omitted its required lane declaration; corrected fixture evidence
  separately proves the old scanner misses the entry initializer. Both were
  instrument errors, not product findings.
- A malformed candidate still creates an eligible verifier-refusal attempt.
  The no-best real-session successor instead makes the launched producer exit2;
  its pre-fix baseline crashes, while the repair returns a structured refusal.
- Terminal validation also checks contract_accepts for the reconstructed final
  evaluation, all result-version/count/best-identity fields, and preserves the
  already published cache on refused reconstruction. An honest custom ranking
  selecting an earlier failed best remains accepted when the final attempt meets
  the contract. Regression siblings name these separate branches.
- RF6's primitive-migration base is523cdd1a2ae1ad6ea0e8ca092fe29629dd10607c.
  The expanded grammar measures375 there (371 previous forms +4 literal getattr),
 354 now, ceiling365. The earlier pre-refactor f5a8318 source measures374; it is
  a different source boundary, not the375 baseline. Original attribute/get metric
  stays299 against310/320. The successor's reasoned rows cover all four existing
  literal-getattr reads; original policy bytes stay historical.
- Dynamic query inventory and CLI home-map successors retarget physical output
  definitions. The old output helper bytes move exactly; all25 aliases, observed
  patch effect and source omission negative are explicitly checked. Contrary to
  the review's illustrative wording, the actual map assigned the old child to
  semantics; the implicit entry-package initializer remained the defect.
- The replay integrity branch intentionally changes its body. Its exact successor
  AST hash is retained; the observer normalizes only one cache write at the return
  tail. Dirty moved/early/repeated writes remain observable.
- The parent-edge diagnostic exposes4087 implicit edges and seven combined SCCs
  from package reexports. Zero explicit SCCs and zero wrong-way/entry violations
  hold; no claim of zero combined package-initialization SCCs is made. Existing
  explicit SCC JSON keys stay stable. Seven fresh service imports confirm the
  entry commands package is not initialized.
- Initial legacy session pins inherited LANG, LC_ALL and TERM from the desktop
  environment, unlike their recorded golden environment. Unsetting exactly those
  three names yields28 passing pins; no golden or capture expectation changed.
  Intermediate graph failures came from an added nested SCC key, corrected to a
  separate diagnostic top-level key. Initial and corrected gate logs are retained.
- Lint required sorting the seven changed service import blocks; their migration
  adaptation after-identities were refreshed, preserving every before/source row.
  All18 target adaptations have exact hashes/modes; units.json and the distribution
  authority guard remain unchanged. This is no source-owned handoff or certificate.

The approval corpus's meanings remain unchanged. Helper/fixture repairs and the
additional positive/dirty controls are delegated amendments within RF9-F1–F9;
no review-round or broad-suite budget was expanded.
