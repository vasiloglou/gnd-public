# Export boundary

The [workflow](../SKILL.md) exports explicitly requested finite witnesses or the bounded standalone program
profile below.
A request is `{ "version": 1, "targets": [{ "fact_type": "id", "tuple":
[{ "primitive": "String", "value": "source-value" }] }] }`.
Tuple order follows the model's role order. Duplicate requests retain their
positions. All results must be proved for exit 0.

Exit bands: 0 every tuple proved; 1 invalid proof; 2 missing, unknown or unsupported;
3 malformed/stale input; 4 bounded work refusal. Batch precedence is 3,4,1,2,0.
Refusal never becomes domain falsity. Ordinary checking emits no witness.

`gnd witness-view CERT --json` removes values and value-bearing digests by default.
`--raw` explicitly exposes the certificate. `--expand` counts repeated visits and
always produces a non-replayable view. Views cannot be fed to replay.

The proof producer is the production evaluator with an opt-in grounded trace.
Replay runs a separate finite inference kernel. Agreement does not establish
source truth, extension completeness or an assurance upgrade.


## Standalone Souffle program: souffle-relational-v1

`gnd export souffle MODEL POP --reference-root ROOT` renders offline and returns
counts only. `--raw --out NEW_DIR` publishes exact raw source copies, program.dl,
fixed facts, symbols.json, origins.json and manifest.json. Existing destinations
are refused. `gnd export souffle-verify BUNDLE --json` checks a closed version-1
manifest, its exact roster, sizes/hashes, source identities and deterministic
re-emission of every program/data/map byte. A digest detects changes, not forgery
of an entirely new bundle. Verification retains one descriptor-bound snapshot.

`gnd export souffle-run BUNDLE --executable souffle --json` explicitly selects
POSIX Souffle 2.5, 64-bit, with the preprocessor disabled. Default results redact
extension values, paths and digests. `--raw` returns typed extension rows.
`gnd export souffle-witness BUNDLE --targets REQUEST --executable souffle --raw
--out NEW_CERT` maps finite positive native explanations, collapses input helpers,
and runs the independent replay kernel before publication. Replay remains a
separate command. Neither native output nor optional tool presence starts a run
from ordinary validate/check. No provider or network is used.

The export supports complete fixed/candidate base relations, range-restricted
positive recursive clauses, stratified negation, constants/repeated variables and
nonrecursive distinct count (group + over + of contribution keys), with optional
count-result comparisons to integral literals. No zero group is invented for empty
input. Count output uses the same integral encoding for downstream joins.
All supplied derivation clauses are classified; opaque/partial/unknown/asserted
 derived input, unsupported arithmetic, non-count aggregate or filter fragments
refuse the entire export. Constraints and operations are explicitly excluded.
Negative, aggregate, Duration and truncated explanations cannot become proof
axioms; only the positive finite Phase 3 fragment is mapped.

Public relations/variables/helpers use generated ASCII ordinals. Semantic columns
are symbols: String s: plus lowercase UTF-8 hex; Boolean b:0/b:1; Integer/integral
Number n:decimal:1; Date d:canonical-ISO; Duration u:nonnegative-decimal. Supplied
integer values never enter native arithmetic; only bounded internal count values
do. Boolean/Duration/Date identities stay distinct. No normalization or rounding.
Source ordinals retain candidate/reference occurrence origins. All payload paths
are generated and confined; unsupported input never publishes a success bundle.

The closed manifest keys are version=1, kind=souffle-derivation-program,
support_profile=souffle-relational-v1, encoding=souffle-token-v1, assurance=none,
binding, input_formats, excluded, files and limits. Binding includes model_digest,
candidate_digest, model_raw_sha256, candidate_raw_sha256 and sorted references
(id/raw_sha256). Files are sorted path/bytes/sha256 records, excluding the manifest.
Input formats have exactly model/candidate json|yaml. Excluded has exactly
constraint_evaluation=all, constraint_ids and operations=all. Symbol maps have
version/encoding/relations/rules; relation entries have fact_type/symbol/input/
roles/derived, roles name/object_type/primitive; rules symbol/native_rule/kind/
fact_type/clause_index. Origin maps have version/rows with input/source_ordinal/
fact_type/origin, and origin kind/reference_id/fact_index. Unknown keys, duplicate
keys, nonfinite/deep JSON, bool versions/sizes, escaping/unlisted/nonregular files
and rehashed foreign programs are refused.

Export result keys: version=1, kind=souffle-export-result, exit_code, status,
reason, assurance=none, counts (fact_types/clauses/input_rows/encoded_cells/
emission_visits). Run adds tool, elapsed_seconds, extensions with kind
souffle-run-result. Tool has path/sha256/version/word_size/native_exit. Bands:
0 exported/verified/completed; 2 fragment-unsupported; 3 input-invalid (including
occupied destination); 4 work-limit/write-failed/tool failure. Native reasons are
tool-absent, tool-platform-unsupported, tool-version-unsupported, tool-timeout,
tool-error, output-partial, output-invalid, output-limit. Provenance retains the
Phase 3 envelope/bands, including 1 for a well-shaped false proof.

Fixed maxima (callers may lower positive integer ceilings): 10 MiB/document,
40 MiB/bundle, depth64, 256 fact types, 64 roles/relation, 1,024 clauses,
4,096 atom/filter sites, 100,000 input rows, 400,000 encoded cells,
4,096 UTF-8 bytes/scalar, 128 numeric digits, 1,000,000 emission visits,
10 MiB combined native output, 100,000 native rows and 30 seconds for version
query plus execution. Input shape excess is 3; work/native excess is 4. Structural
emission charge sums fact types, roles, clauses, atom/negation/filter sites, head
terms, input rows and cells. Native process groups are bounded and killed on
exhaustion; temporary disk overshoot between monitoring polls remains residual.
Raw copies/outputs contain source values. No source truth, full constraint
verdict, completeness, judge trust, independent adoption or assurance is inferred.

Native identity hashing uses a retained no-follow regular-file descriptor and
checks unchanged identity after query/execution; privilege-changing executable
modes are refused. This is local file evidence, not tool authentication or a
hard guarantee against uninterruptible host I/O.

## Finite Lean model lane

`gnd export lean MODEL POP --toolchain leanprover/lean4:vMAJOR.MINOR.PATCH
[--reference-root ROOT] [--raw --out NEW_DIR] [--json]` renders offline. Default
feedback contains counts/status only. Raw bundles contain all source values and
occurrence origins. Publication is create-once and manifest-last. Verify with
`gnd export lean-verify NEW_DIR --json`: retained bytes must reproduce every
closed payload, identity, source map and proposition exactly, even after rehash.

Profile `lean-finite-acyclic-v1` accepts value-only String, Boolean, Integer, Date
and Duration carriers, fully covered base relations, fixed disjoint references,
positive acyclic unions/joins/projections/constants/repeated variables, local
one-role mandatory, internal occurrence uniqueness, single-relation subset
projections, and positive guarded scalar/Date ± Duration comparisons. It refuses
entity/subtype/transition models, recursion, negation/aggregate/filter/arithmetic
clauses, textual/semiderived/asserted-derived/partial inputs, Number/Float/DateTime,
opaque values, joined subset, relational/existential guarded consequents and all
other active constraints, including deontic unsupported constraints. Strings have
only equality/inequality. Boolean and Integer never share carrier identities.

Each type's explicit finite carrier includes instances, fact cells and typed rule
literals. Date arithmetic uses exact Gregorian ordinal days and can return
unchecked at range exhaustion. Mandatory quantifies the declared finite extent;
uniqueness counts occurrences; subset has set inclusion. Guard empty joins are
vacuous. A definite violated binding dominates unchecked; otherwise unchecked
dominates satisfied. Alethic holds alone enter hard; deontic observations remain
policy outcomes. These predicates differ from current checking in wholly empty
mandatory relations and mixed temporal failure/overflow; no snapshot-equivalence
claim follows. Source strings never enter Lean names, comments or imports.

Definitions declare symbolic candidate-owned extents/base relations and fixed
references. With U fixed carriers, R references, WT well-typed interpretations,
NE nonempty candidate-owned extent, and H hard alethic holds: concrete witness is
WT(P0) ∧ NE(P0) ∧ H(P0); satisfiability is ∃ P, WT(P) ∧ NE(P) ∧ H(P).
Alethic redundancy is ∀ P, WT(P) → H_without_c(P) → holds_c(P).
Deontic-policy entailment uses H(P) instead. Universal queries admit empty P;
concrete satisfaction never proves redundancy. No candidate-owned nonempty extent
means no satisfiable witness. These are finite-carrier claims, not unrestricted
ORM entailment, source truth, completeness or assurance.

The bundle contains Definitions.lean with no sorry/axioms, ProofObligations.lean
with explicitly UNPROVED sorry templates, obligations.json, source-map.json,
manifest.json, lean-toolchain and raw inputs/model.json, candidate.json and sorted
reference-N.json. Semantic binding hashes use the existing sha256: identities;
raw/carrier hashes are bare hex. Obligation addresses are raw RFC6901 pointers;
active entries have unproved predicates/queries, inactive entries are inventoried
not-applicable. Export/verify results use version1, assurance none, proof_status
unproved and counts. Exit0 exported/verified; 2 fragment-unsupported; 3 input-invalid;
4 work-limit/write-failed/tool failure. Refusal never publishes a success directory.

`gnd export lean-compile BUNDLE [--executable LAKE] [--elaborate-stubs] --json`
verifies first, copies only verified modules and the release pin to a private
workspace, and explicitly runs pinned lake env lean. The caller provisions a
cached release separately; no project hooks/lakefiles or downloads are selected.
Tool identity/version and definition/stub attempts/statuses/times are separate
feedback. Missing tool, mismatched version, timeout, rejection and output excess
are exit4. Compiled status and successful stub elaboration preserve unproved;
there is no automatic discharge or call from ordinary validate/check.

Ceilings can only be lowered positive integers: 10 MiB/document, 40 MiB/bundle,
depth64, 128 object types, 256 fact types, 16 roles, 1,024 clauses/constraints,
4,096 carrier values, 100,000 input rows, 4,096 UTF-8 bytes/scalar, 128 digits,
1,000,000 charged prospective visits, 10 MiB combined native output and 30 seconds
for identity/version/compile/stubs together. Input shape excess is3; work/native
excess is4. Process groups are killed on exhaustion, with monitoring-poll disk
overshoot retained as a residual. Verification and compilation are not tool
or judge authentication. No higher assurance is emitted.
