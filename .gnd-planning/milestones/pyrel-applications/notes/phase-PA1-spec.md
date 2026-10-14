# PA1 — Guarded checking and explicit acceptance

Status: PA0 completed at a55128d; delegated spec gate follows after final implementability sweep.

## Provenance and obligations

Whole effective draft r1, delegated plan gate 001, PA0 spec/answer corpus and
preparation 002. Owner auto=true persists; Claude Code is selected for phase
reviews. No optional spec panel or broad suite is selected.

| Source | Obligation | Discharge |
|---|---|---|
| PA1-C1 | 3 BookRec and 7 expense guarded rules, satisfied/violated witnesses | PA0 targets, full guarded witness normalization in native successor lane |
| PA1-C2 | Presence/absence/comparisons, literals/shared/repeated refs, duplicates, typed scalars, malformed/empty/unknown/unsupported/error/budgets | Named direct admission/native controls |
| PA1-C3 | Advisory warning versus strict failure, fail-closed unknown/error, bindings and legacy compatibility | acceptance_document and --accept; legacy public tests |
| PA1-C4 | Standalone GND-free optional runtime, zero layer allowances | Export/native isolated run; AST/layer checks |
| §9 | Guarded/coverage/modality/refusal/schema/standalone gates | Verification ledger below |
| §0 PA-R1–R8 | Independent PyRel, full coverage, meaning, opt-in acceptance, staged input bindings, optional bounded local runtime, one translation home, limited evidence | Existing standalone runtime plus opt-in subclass/profile functions; no application publisher yet |
| §5 | Goldens/report clients/runtime copies/runner markers | Preserve baseline reports and runtime locks; new profile tested separately |
| §6 | False acceptance, unknown empties, Python bool queries, shared policy fallback, warnings, forged claims, isolation, budgets | Concrete native controls and unsupported derived-model refusal |
| §10 | PA-D2–D5 fixed in PA0 | No silent contract weakening; record any amendment below |
| PA0 and RF/public-launch carryovers | Historical receipts/shims/source authority do not transfer; actual lookup and primitive policies retained | Production change only in existing independent runtime, no GND query-layer import |

## Standing rules, goal and design

Totality: profile admission maps arbitrary malformed JSON shapes to ExportInputError
without a traceback at the CLI. Bounds: counts before engine construction, native
results capped and caller wall timeout declared. Validation order: parse, shape,
profile/coverage/work admission, local execution, composition, exclusive report
write. Complete traversal: one _constraint_entries walk. Normative home: PA0
contract; profile docs cite it. Runtime facts are measured by native controls.

Goal: every baseline guarded positive/negative target runs in native PyRel with
exact normalized variable witnesses; unknown/error states have accepted=false;
legacy default report behavior is unchanged. Complete derivations stay unsupported
until PA2; acceptance cannot credit their supplied claims.

Existing home `src/gnd/export/pyrel_runtime.py` gains an opt-in ApplicationOracle
subclass and profile functions (estimate 350 lines). No new mandatory dependency,
module, family registry entry, broad evaluator fallback or import of GND.
Generated exports copy these bytes as before. Legacy PyrelOracle/evaluate_document
and default report schema/exit behavior stay unchanged.

Exact public signature, result schema/status precedence and ceilings are those
in PA0's approved contract. Add `--accept` to program_main. In this mode raw
population read and its hash use one bounded read; model hash uses exact embedded
UTF-8 model text. Size/profile refusal is incomplete (2), malformed input 3,
engine failure 70, warning/accepted 0 and violated alethic 1. Embedded named
remote connections refuse acceptance; local DuckDB is explicitly selected.

The admitted acceptance families are inline uniqueness, inline mandatory,
object-type value enums, unary projected subset, and guarded. Other family shapes
remain unsupported. Every fact type must be explicitly covered and listed,
including known empty lists; profile constraints never substitute unknown data.
String/Boolean/Integer values and role identity remain native typed columns.
Integer scalars are limited to ±(2**53-1) as in PA0. Unsupported derived declarations
are incomplete in PA1, not accepted from supplied facts.

Guarded translation validates a single bounded conjunction and consequent before
building native fragments. Each variable has one compatible primitive/ref;
literals remain typed. Negative consequent atom uses native not_; absence checks
presence; comparisons negate the declared native operator. Literals in comparisons
are bound through native unary relations so no Python comparison decides policy.
No-variable antecedents use a native marker projection and report an empty witness
binding on failure. Native witness dictionaries are deduplicated and sorted by
canonical JSON key/order. Known empty antecedent relation is vacuous; a nonempty
set of relations whose conjunction has zero bindings is satisfied, matching GND's
clean-zero-bindings branch. Incomplete consequent coverage precedes either case.

Legacy implemented families run in the same native engine after profile admission.
Their existing row witnesses remain distinct from guarded variable dictionaries.
Existing logical row duplication behavior for uniqueness is retained; guarded
binding duplicates are logical tuple duplicates and produce one witness.

## Decisions and corpus approval instrument

Corpus-first: PA0's frozen hand-narrated expected target outcomes are inherited
by exact matrix/answer hashes, not regenerated. Add separately named direct
branch cases; do not change approved answer meanings. Exact native measured
GND vacuum/zero-binding distinctions are pinned; any differing application-wide
acceptance interpretation is explicit, not an audit-exit inference.

Pending delegated rulings after PA0 completion: adopt this design and the PA0
schema/ceilings; no optional spec panel; one initial Claude read-only diff review
plus at most one reproduced-blocker repair pass. Source/test estimate 350/250 lines;
fixture budgets remain PA0's ceilings. No production edit before this gate.

## Tests and verification selection

| Gate | Disposition / command / expected exit | Boundary / invalidation |
|---|---|---|
| Direct admission/format/branches | run: `.venv/bin/python -m pytest -q tests/test_pyrel_application_acceptance.py tests/test_pyrel_application_corpus.py --tb=short` (0) | New profile/CLI/corpus controls; any relevant bytes change |
| Native guarded control/witness lane | run: `.venv/bin/python tools/measure_pyrel_applications.py --mode acceptance --stage guarded --out .gnd-planning/milestones/pyrel-applications/evidence/PA1/native.json` (0) | Frozen baseline/strict/currency targets; complete model excluded only until PA2, named denominator |
| Legacy/consumers/layers | run: `.venv/bin/python -m pytest -q tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_public_pyrel_export_runtime_optional.py tests/test_public_pyrel_export_runtime_support.py tests/test_external_runtime_tutorials.py tests/test_rf1_layering.py --tb=short` (0) | Legacy interfaces/export isolation/query budget and layer map |
| Broad historical/native oracle/proof/census | cadence: explicitly selected CI or owner request | Outside bounded profile impact |

Declared direct branches: all eight comparison spellings; literal/repeated/shared
variables; partial bindings; empty and clean-zero joins; uncovered antecedent and
consequent; malformed binding; unknown fact/role; unbound variable; conflicting
primitive; unsupported consequent/derivation; duplicate rows; boolean-in-integer;
out-of-range integer; fact/constraint/role/row/join/result ceilings; native exception;
raw model/population binding; warning/strict composition; existing report exit zero.
Each has a positive/discriminating native or admission control.

## Out of scope, size and implementability

No BookRec/expense publisher or query, derivation support, tutorial graphics,
installed candidate, complete model acceptance or certification. Existing native
relationship/not_/query APIs supply the fragment; PyRel booleans are expression
objects. Conservative preflight counts bound work before execution; hard wall
execution is an application caller responsibility, implemented in PA3/PA4.
No new module means no layer-map home to register; existing allowance zero stays.

## PA0 completion carryovers and final implementability sweep

004-phase-PA0.md completes the hard prerequisite. Effective plan is original r1
plus reviewed A1/003. PA0 final matrix/answers/approval snapshot is inherited
unchanged; 137 cases, 117 outside complete mode for the PA1 native stage.
Every native verdict must include id/type/modality/witnesses/reason; verifier
checks exact row placement and full report bindings/status/exit. A1's two
source disagreements remain deferred to PA2 execution, not trusted claims in PA1.

Additional focused consumers: RF2 standalone source-byte pin; RF1 exact resolver,
valid-temporal and PyRel yaml/write helper nodes; RF7 primitive ambiguity;
registry imports; RF6 exact live query and dynamic candidate inventories.
Original RF9 successor/allow-list bytes stay frozen. New authenticated phase
successors bind exact predecessors and newly introduced source reads; preserve
the original 365 direct-read ceiling and zero layer allowances. No blanket
standalone-module waiver or old golden recapture is approved. Existing public
ModelIndex/PyrelOracle names and definitions remain their actual lookup homes.

Known vacuity is visible and withholds application acceptance (overall incomplete
2); a zero join among nonempty covered relations is satisfied. Unsupported/missing
coverage precedes vacuity. This matches the frozen acceptance interpretation and
does not promote vacuous GND reports to acceptance. Independent native report
arithmetic controls in PA4 can still exercise zero/empty query results separately.

Raw declaration ceilings also include 64 object types, bounding unused entity
concept construction before native import; the original per-fact/constraint/row
ceilings remain. The profile is in-memory DuckDB/select only: named connections,
require mode and persisted database options refuse rather than silently changing
execution context. Version 1.30.1/DuckDB 1.5.5 is checked before profile execution.

Initial 350-line production estimate is revised before implementation to 650
source lines and 400 direct test lines: typed binder/literal relations, all-shape
admission, full output schema/refusals and focused source-pin successor routing
are explicit work. No runtime fact remains a decision substituted for measurement;
small native join/negation/integer probes ran successfully before implementation.
Corpus-first uses the already committed RED profile measurements and approved
full native key, with new direct branches authored before production changes.

## Delegated approval (auto=true), 2026-10-13

Approve specification prefix 5acb1a6342ddf92e796b2e76e1b9f2723b7c64b9921adb10edf2791339fc9bbb after the final implementability sweep.
Authorization: owner's named whole-milestone auto=true; PA0 completion a55128d.
Instrument: committed PA0 full native answer key and red profile receipts, plus
new direct boundary controls authored before runtime changes (15 failed because
acceptance_document is absent). Optional spec panel omitted. Claude Code is the
owner-selected independent phase reviewer; one initial plus at most one repair
pass, with convergence measured before round two. Budget: 650 production and
400 test lines; all existing ceilings stay explicit. Additions to literal-query
and rendered-source pins are authenticated successors, not historical recaptures.
Unknown coverage/unsupported/work refusal and vacuity cannot publish; known
nonempty zero joins are satisfied. No derived or application query support is
credited to PA1. Native GND-free execution is mandatory at the phase gate.

## Implementation findings (2026-10-13)

- F1: with zero constraints, a constructor/version failure left an empty status
  set and incorrectly composed accepted. A direct seeded backend failure control
  failed before the fix (empty-constraint-pre-fix.txt, 41 passed/1 failed).
  Constructor failure now returns runtime_failure/70 even with no verdict rows.
- F2: the module-level native not_ convenience function rejects multiple models
  in one interpreter. The native direct table reproduced errors on cases 16,17,20
  after prior comparison models. Guarded atom negation now uses self.m.not_;
  the same 27-case table then passed. Legacy evaluator bytes stay unchanged.
- The initial 117-case frozen guarded acceptance run matched every full report
  before these additional branch controls. Its generated-program digest is
  historical; final current-byte run is separately named, not overwritten.
- Exact standalone query reads rose from 354 to 356, below original ceiling365.
  Chained authenticated PA1 successors retain RF9/compiled-snapshot evidence and
  pin exact direct/dynamic candidate counts and changed rendered-source bytes.

Verification ledger clarification: the mandatory native direct command is
`.venv/bin/python -m pytest -q -m pyrel_oracle tests/test_pyrel_application_native.py --tb=short`.
It explicitly selects this new phase-owned optional file only, preserving all
default exclusions for the ordinary focused gate. Additional real native legacy
controls compare both basics_pass and basics_fail reports field-for-field with
unchanged historical answer files; violation audit exit remains0.
The result cap has both a seeded parent boundary and a real101x101 native join.

## Delegated test-budget amendment (auto=true), 2026-10-13

Approve preceding specification bytes SHA-256 2837e39592435746e512dbe348b752bd6ae8dfa464b59141c726e9f908b48b0e.
Original400 test-line estimate is exceeded by exact inventory:241 admission/CLI
lines,158 native controls and62 authenticated successor helper lines (461total),
plus focused consumer routing. Raise test budget to550lines; source budget650
remains (364added runtime lines). The added tests implement declared branches
and legacy native report compatibility; no new product scope or corpus meaning.
Instrument remains corpus-first and one selected Claude reviewer. Prior ruling
is retained; this is an agent ruling under named owner delegation.

## First review triage and scoped repair decisions (2026-10-13)

Claude returned8 findings plus test-completeness observations. Keep the review
verbatim with its disclosed read-only data-parsing deviation. One reviewer is
one reviewer. Parent controls reproduced raw TypeError/missing-role admission,
unexpected-status false acceptance, uncounted consequent work and missing-output
66; repeated-call native controls reproduced mandatory/subset model ambiguity.
Vacuity tests additionally check the premise through public GND; their initial
fixture errors (dict API and duplicate cross-kind id) are retained separately,
not claimed as reproduced vacuity defects. Final valid fixture run is separate.

Triaging before repair: F1 false acceptance and F6 unexpected-status acceptance
are blocking. F2 repeated-call API, F3 malformed-shape totality, F4 explicit size
contract, F5 output-error mapping, F7 conservative work and F8 context refusal
reports are owned hardening within the declared PA1 interfaces. Missing semantic
cases are completeness where they extend coverage of already declared branches;
add bounded cases now, defer arbitrary new ORM fragments. Frozen answers stay.

Approve these scoped repairs under existing auto=true before production edits:
- Admit only top-level guarded/object-value/unary-subset; unsupported inline
  variants refuse2. Inline uniqueness/mandatory retain host-first known-empty
  vacuity; top-level value scoped to exact role object types is vacuous when all
  subject facts are empty even when a roster supplies allowed values. No GND
  import is used. This does not narrow any shipped model or corpus expectation.
- Override legacy mandatory/subset negation in ApplicationOracle only, preserving
  historical PyrelOracle definitions. Admit consumed shape types explicitly;
  missing mandatory role and unhashable object/role selectors are malformed3.
- Accept only recognized successful statuses; unknown native status refuses2.
  Conservative guarded work includes consequent relation multiplicity.
- Size refusal is incomplete2. CLI ceiling measures exact raw UTF8 bytes; the
  dictionary API additionally bounds canonical JSON structural size, because
  hashes/raw reads are caller-owned. The API does not prove a raw byte ceiling.
  CLI refusal before complete raw admission emits a reason on stderr and no
  report, since an unread full population cannot have an honest exact digest.
  This early-size exception is explicit; no partial digest is substituted.
- For admitted raw inputs but unsupported execution context (require/named/
  persistent/explicit config), write a full bound incomplete report with reason,
  without native execution. Missing output parent is operational70.

Test budget rises to750lines for reproduced reviewer regressions and branch
completeness; source650 remains. This is a delegated amendment, not a human
reading or a claim that tests prove universal equivalence. At most one repair
review remains. Final current-byte affected gates and native corpus rerun follow.

### Reproduction correction before repair

F1's claimed top-level/inline value GND-vacuity premise is **disproved**:
public check returns pass for allowed roster-backed values and the inline value
example populated through another relation. The first scope-reading argument
was false; no top-level value semantic change will be made. The previous
proposal to mark that roster-backed case vacuous is revoked before implementation.
Inline guarded/subset examples are ill_formed under the public GND schema,
not vacuous. Only mandatory host-empty actually returns GND vacuous/native
violated; it already fails closed but disagrees with the declared empty-host
convention. Fix mandatory host vacuity; explicitly refuse inline guarded/value/
subset outside the profile's top-level fragment. These technical refusals do not
claim that GND marks every such example vacuous. Keep the passed roster control
as a rebuttal pin. F1 is now an owned admission/vacuity hardening disposition;
F6 unknown status is the actually reproduced false-acceptance blocker.
All fixture-authoring errors and final concrete runs remain separately named.

Delegated repair gate (auto=true): approve corrected preceding spec bytes SHA-256 e034e0cebd232fa32375ff3da037f268ab2fecaaaea7d8c20adec4475b0b14c6, under the named whole-milestone authorization. Prior decisions stay visible; the reproduction correction supersedes the proposed value-vacuity change. Budget650source/750tests; Claude one bounded repair review remains.

## Convergence ledger before the sole repair review

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| 1 | Claude Code |8numbered findings; completeness observations tracked separately|7/8 (F2 exposed historical convenience-negation behavior)|1/8 (F6 actually reproduced unknown-status acceptance; F1's claimed value-vacuity counterexamples disproved)|medium-high reviewer ceiling; reproduced false-acceptance finding6 rated low-medium by reviewer|hold, repair owned admission/API/interface boundaries|

The permitted next review is exactly one bounded repair reading. Retain its
opinions over reviewed bytes; reproduce findings and repair owned blockers with
red controls. No third review round is authorized by this phase budget. Parent
red11controls and native red5controls/1 rebuttal-pass are retained against exact
pre-review-runtime.py bytes. Parent final80passed; native final18passed (including
older controls and new semantic completeness cases). The final current-byte
focused/corpus reruns are separately named and pending when this row is authored.

## Final repair review disposition

The sole repair review refuted none of the7repair claims, found no blocker,
and returned1Low admission concern plus2non-action notes. Convergence round2:
Claude1numbered finding,0blocking/1total,0self-inflicted/1total, severityLow,
verdict non-hold. No third review will run. The reviewer disclosed a no-op
Python command despite no-execution; retain this independence limitation.

L1 is owned hardening in profile admission: an unrelated String object type
can populate a unary superset and be accepted despite GND's role type-compatibility
error. Reproduce via public GND plus native execution; red control names the
exact semantic:role-seq-type-compat rule. Add a bounded refusal unless both
projected roles have exactly the same declared object_type. Shared-ancestor
and unrelated primitive-compatible subset types remain unsupported in this
profile; no shipped model or frozen answer is narrowed. Source remains the
standalone resolver; no GND validation import or GND policy fallback.

N1 receives a direct embedded-model oversize priority test (2 before reading
missing population). Early no-report reasoning is about an unadmitted full input
pair, including the unread population when the embedded model is too large.
N2 grammar-shape refusals2 versus malformed consumed selectors3 are intentional;
all withhold acceptance. No further format/domain expansion is added.
Test budget850lines accounts for owned L1/N1 controls and focused consumer routing;
source650 unchanged. Final owned bytes will carry fresh focused/native/source-pin
controls, not an opinion claimed from another nonexistent review.

Delegated L1 gate (auto=true), 2026-10-13: approve preceding spec SHA-256 76da4ce002d5bb3e59495c3c442ef0179e61c1174bc9f533995fe4a09d7e3388 under named milestone delegation, exact-type projected subset restriction and budgets as above. Prior review opinions and byte bindings remain historical.

Final branch audit: frozen positive/negative and distinct uniqueness controls
cover all shipped admitted rows; new native cases cover grammar/scalars/empty/
actual join-result bounds; parent controls cover preflight caps, raw binding,
malformed selectors, unsupported contexts, output failures and composition.
Library canonical structure caps and caller-owned hashes are not a proof of
raw reads; the standalone CLI actually bounds and binds them. The GND-free
native interpreter has no importable GND installation. New profile API repeated
calls are measured; the untouched legacy library's module-level negation
ambiguity is deferred to a named future pyrel-legacy-runtime-maintenance milestone
(owner: GND maintainers), while one-shot legacy report goldens are current.
Complete derivations remain unsupported until PA2. Two A1 source disagreements
are not yet credited by this phase, nor are application queries/publication,
compiled-schema universality, tutorials, wheel installation or certification.
