# GW1 · Typed constants in mined rules · draft r1

**Awaiting owner review.** Implementation requires the plan and GW1 spec gates.

## 2. Provenance

[Plan r1](guarded-rule-workflows-plan.md) §§0–6 and 8–10,
[GR-D11](https://github.com/vasiloglou/gnd-public/issues/182), and the AMIE-style
miner mapping and counting sections of
[the ILP bridge reference](../../../../docs/reference/ilp-bridge.md).
Baseline `793618f1`. No independent review ran on these bytes.

## 3. Obligations

| Source | Obligation | Discharge |
|---|---|---|
| #182, Asked for | A literal in either role of either atom kind, with role type and export spelling | §6 M1–M2, T1–T3 |
| #182, example and existing mapping table | Admit the category-specific rule whose head relation appears in its body | §6 M2, §7 D1, T1/T4 |
| #182, reserved prefix and counting | Reject a decoded dollar-prefixed string, recompute distinct head pairs, require support equality and full confidence | §6 M1–M3, T2/T5/T6 |
| Plan §§4 and 9, A4 | Preserve old triple bytes and variable-only imports, validate the induced proposal and confirm against the checker | §6 M4, T7–T9 |
| Plan §§0, 5–6 and 8 | Bounded total admission, compatible changes, one contract home, verification and review | §§4, 6 and 8–11 |

## 4. Standing rules bound to GW1

1. **Totality belongs to the function, not the caller.** Keep capped rule and
   run-record reads. Decode hostile tokens with bounded scalar parsing and
   deterministic named refusals. Exercise malformed escapes, hostile counts,
   non-UTF-8 and arbitrary run JSON at the public boundary (T2, T8).
2. **An input cap bounds the document, not the algorithm.** Keep the
   pre-join product cap. Keep head-set construction linear in scanned head
   facts and constant parsing linear in token length. Exercise high fanout and
   large tokens in the mapper/counter layer under a declared test timeout (T6).
3. **Validation order is part of the design.** Pin the existing stage order
   and the literal slot in the mapping refusal table with conflicting invalid
   controls and source-order assertions for unobservable differences (T4/T8).
4. **A policy governing N element kinds is enforced by one walk over all N.**
   Use one role-aware operand conversion across body/head and subject/object,
   and one term-matching rule for all body sites (T1/T5).
5. **Normative prose has exactly one home.** The AMIE mapping/counting section
   of the ILP bridge reference owns the behavior. CLI guidance and component
   descriptions link to it (T9).
6. **Resolve contested representation questions by measurement.** Compare
   independent head-pair fixtures and checker findings, including a
   same-predicate named-category rule and one false binding (T1/T5/T7).

## 5. Goal

A valid AMIE input containing typed constants exits 0, writes an induced
guarded proposal and reports a positive denominator equal to its recomputed
numerator and the supplied support. Invalid constants and non-admissible
counts exit 3 and leave the proposal path absent. Existing variable-only
exports and successful import observations retain their behavior.

## 6. Design

| Capability | Searches and inspected evidence | Reuse |
|---|---|---|
| Typed AMIE rule import | `components_index.py search amie import constant`, `components_index.py search ilp mined rule`; read `ilp_amie.py` and `test_ilp_amie.py` | Adapt `export.mined_rules` |
| Count and guarded proposal admission | Same searches and the indexed callers `ilp_service.py`, `ilp_rewrite.py`, `test_ih1_counting.py` | Reuse `export.ilp_service` and the variable join checker in `export.ilp_rewrite` |
| Learner output extraction | Read `extract_rules` and learner registry callers in the same subsystem | Adapt the existing extraction seam |

**M1 · Operand decoding in `src/gnd/export/ilp_amie.py` (about 65 source
lines).** Add
`_constant(term: str, entry: Relation, role_index: int, *, index: int) -> str | int | bool`.
Check the role's export family prefix followed by a colon. Split at the
first delimiter so a textual payload may contain colons. Use the role's
reference primitive set and the existing kind partition. Refuse ambiguous or
unavailable primitives. Decode text with the inverse of the existing escape
table, integers in the canonical export spelling, and booleans as literal
`true` or `false`. Number inputs follow the export's integer-only spelling.
Validate the result through the existing role primitive validation and
`spell` round-trip. Refuse malformed constants as `constant-atom` and decoded
text beginning with `$` as `constant-spelling`, before insertion into the
guard. The existing printable ASCII rule-line grammar continues to define
the importable token alphabet. The codec change does not rewrite the export.

**M2 · Mapping and extraction in the same module (about 45 source lines).**
Keep the signatures of `mapped`, `parse_rules`, `canonical` and
`extract_rules`. Map an architecture rule to a core with
`"type": "guarded"`, `"antecedent"` and `"consequent": {"atom": ...}`, where
an example atom is
`{"fact_type":"component_in_area","bind":{"component":"$b","area":"cli"}}`.
Treat only `?a` through `?z` as variables after parsing. Literal positions
participate in role validation and canonical duplicate identity. Variable
positions alone participate in reflexivity, head grounding, body connectivity
and cross-role variable compatibility. A single ground body atom is a
connected body. Multiple atoms must connect through variables. The count
works over asserted facts, so propose allowing a shared body/head relation
only when a head role has a constant, subject to all remaining checks. Keep
the existing `recursion` refusal for variable-only heads. Include constant-first
rule lines in learner stdout extraction by recognizing their rule-field
shape and passing them verbatim to the strict parser. Preserve the existing
variable-first path and test headers/progress lines and malformed constants.

**M3 · Counting in the same module (about 25 source lines).** Keep
`count(rule: MinedRule, facts: Mapping[str, list[tuple[str, str]]], index: int, *, limit: int = MAX_JOIN_ROWS) -> Counts`.
Keep the parsed atom tokens in `MinedRule.body` and `MinedRule.head`.
A body constant is an equality filter against the exported token. A head
constant supplies its token directly. Preserve binding and repeated-variable
matching for variable terms. Deduplicate projected head pairs before
membership and provenance. Preflight the product of body relation sizes
using the existing 1,000,000-row cap. Keep the 1 MiB, 256-rule, 4-atom and
18-digit metadata caps. Parse integer literals only after verifying a bounded
canonical token and convert oversized or invalid input to a named refusal.

**M4 · Service and artifacts (up to 25 source lines).** Reuse
`gnd import mined-rules MODEL RULES --population POP --reported RUN --target amie --out PROPOSAL`
with existing text/JSON output and wire schemas. Check paths and output
admission, capped rules and run-record bytes, learner and digest bindings,
model and population, then reproduced facts. Map every rule before counting
any. In each map, check open-world head, unknown predicates, literal
admission, reflexivity, shared predicate, head grounding, variable
connectivity, type compatibility and reference-family compatibility, in
that order. Count all rules before admission checks. Admission order remains
`covers-nothing`, `support-mismatch`, `does-not-hold`, followed by candidate
validation, checker confirmation and proposal write. Preserve existing
derived, opaque, skipped and uncovered input policies and all-or-nothing
writes. Regenerate component descriptions where behavior changed. Check
the report's closed refusal vocabulary before adding `constant-spelling`.
Document any enumerated wire change in the owner-reviewed spec revision.

## 7. Decisions

| ID | Proposed ruling | Consequence |
|---|---|---|
| D1 | Admit an asserted same-predicate rule when its head carries a constant | The example can exit 0. The existing blanket refusal would still exit 3 after decoding is added. Variable-only same-predicate inputs retain exit 3. |
| D2 | Decode within the existing AMIE token grammar using the role family prefix, export escapes and lossless scalar round-trip | Covers the named-category fixture and safe typed values. General quoted or whitespace-bearing token syntax would require an additional miner wire contract. |
| D3 | Preserve `constant-atom` for bad spellings and use `constant-spelling` for the reserved dollar prefix | Both cases exit 3. Consumers can distinguish unsupported lexical form from a string that would be interpreted as a guard variable. |

## 8. Tests

| ID | File and discriminating case | Expected result |
|---|---|---|
| T1 | `tests/test_ilp_amie_constants.py` (new), all four literal positions and the #182 same-predicate rule, checking emitted JSON literals and induced provenance | Import 0, preview valid, independent expected count agrees |
| T2 | Same file, wrong/missing family, wrong primitive, invalid escape, noncanonical integer, dollar-prefixed decoded text, and ambiguous role reference | Exit 3 with the applicable literal reason and absent proposal |
| T3 | Same file, inherited-family prefix, integer/boolean identity, textual colons and supported escapes, constant-first extraction amid progress lines | Valid cases exit 0, proposal literals retain type and spelling |
| T4 | Same file and `tests/test_ilp_amie.py`, competing refusals, variable-only recursion, unbound head variable, literal-only overlap between disconnected atoms, reflexive variable, incompatible join, open-world head | Exit 3 with first applicable reason |
| T5 | Same new file and `tests/test_ih1_counting.py`, several body matches to one head pair, a body literal that excludes a decoy and a head literal with a mismatching fact | Holding control exits 0 with deduplicated counts. Decoys do not count. False control exits 3. |
| T6 | Same new file, denominator zero, wrong support, partial confidence and fanout beyond cap. Compare boundary inputs just below/above an injected cap, with a generous 5-second timeout for the small synthetic test | Exit 3 for each refusal, with no join on the over-cap branch. The below-cap control completes. |
| T7 | Same new file, end-to-end export → import → evolve preview → check with an independently authored wrong-category population | Import and preview exit 0. The guard is active and holds on the evidence. The negative check emits its guarded finding. |
| T8 | `tests/test_ilp_amie.py` and the new file, old export digests, variable-only report observations, malformed/oversized inputs and changed digest bindings | Baseline bytes and bands match. Invalid public invocations use existing refusals. |
| T9 | `tests/test_ilp_amie.py` registry/reference checks, `tests/test_ilp_learners.py` extraction consumers, and `tests/test_ih2_ownref.py` own-reference controls | Focused selection exits 0, with existing refusal parity and docs matching the runtime table |

Proposed focused command (default lane):

```sh
uv run pytest -q tests/test_ilp_amie_constants.py tests/test_ilp_amie.py tests/test_ih1_counting.py tests/test_ih2_ownref.py tests/test_ilp_learners.py tests/test_public_guarded_consequent_matrix.py --tb=short
```

Run affected Ruff and component-index checks. Record commands, exit codes,
counts, generated proposal and diagnostic digests. Keep the native miner
lane outside this gate. A captured-format fixture with truthful run-record
bindings supplies the reader and admission inputs.

## 9. Out of scope for GW1

General recursive Horn rules, new literal syntax in the guarded model, live
AMIE execution and changes to the labelled ILP importer. GW2–GW4 own their
respective user-facing commands.

## 10. Size

Estimate 135–160 source lines, 220–320 test/fixture lines and 35–60
documentation/index lines. Record actual size and any changes to the
refusal or wire contract in the phase record.

## 11. Approval instrument

Owner decision on this spec revision and its three decision rows. GW1
inherits the reviewed plan gate and requires its own approval. Execution
then requires the focused gates, independent diff review, refactoring
review and the phase record under the project protocol.
