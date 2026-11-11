# Ossie interchange close amendment after panel review

2026-11-10. [Plan r3](ossie-interchange-plan.md) retains the original
predicate wording. The [reviewed draft amendment](close-amendments.md)
and [close candidate](../031-close-candidate.md) remain as reviewed.
[Record 032](../032-panel.md) accounts for all panel findings.
The separate [delegated amendment ruling](../033-close-readiness.md)
governs these changes.

| Original requirement in r3 | Effective acceptance scope and provenance |
|---|---|
| Predicate 1, one ontology for every census example | The [OS0 tracked roster](../evidence/OS0/revised/census.txt) comprises 37 packaged examples and four gnd-model-from-text examples, including nested YAML and JSON. Require schema and pinned validator/parser acceptance for all 38 standalone exports. The other three inputs receive the named whole-input include refusal under predicate 7. [OS0](../006-phase-OS0.md), [OS1](../009-phase-OS1.md). |
| Predicates 2 and 3, extension route and one disposition for every census pointer | Require repeatable YAML/JSON and report bytes and a source identity in the exact-document-bound sidecar. Each pointer of each admitted export has one disposition. The three rejected include inputs exit before product report generation. OS0's census inventory of those inputs is measurement evidence. In E1 both pinned consumers accepted the baseline and refused concept and relationship extension controls. [E1](../evidence/OS0/E1.json), [OS1](../009-phase-OS1.md). |
| Predicate 4, render every expressible formula kind with semantic controls | Limit rendering to the shapes in the table below. Preserve other rule shapes in the sidecar. The pinned parser checks syntax and scope. The authored population verdicts measure agreement with the pinned prose. [OS2](../014-phase-OS2.md). |
| Predicate 5, GND diff for restored identity | Preserve refusal order and caps and compare full authored JSON values after removing exactly the frozen refused population subtrees, including for the four temporal models. Apply GND diff digest equality to the other 34. [OS3](../020-phase-OS3.md). |
| Predicate 6, convert every intact export | Attempt all 38 original exported documents in the offline lane before any edits for isolation. Require the measured declaration matches on 36 and retain the two diagnosed refusals. [OS4](../021-phase-OS4.md). |
| Predicate 9 and OS6-C2, generated source requirements for the replayed GND formula kinds | Record the owner-approved upstream PR at the tested commit. Require emitted source for the tested entity-scoped controls and Flights and scoped metamodel requirements for six isolated value-tuple formulas. Record the omitted generated source for those six, and the warnings for ontology-level count and value-concept enumeration. Retain the no-require consumer finding for GND census output. [OS6 amendment](../027-OS6-spec-amendment.md), [OS6 phase](../030-phase-OS6.md). |

## Formula coverage

The [authored expected verdicts](../evidence/OS2/corpus-r2/expected.json)
were approved at `a0c0ac7d` before the renderer at `337267e8`.
The 29 cases include the following satisfying and violating controls.

| Rendered family | Admitted form | Satisfying / violating case |
|---|---|---|
| Guard | Relationship comparison with a scalar literal | `guard-pass` / `guard-fail` |
| Subset | Relationship requires the matching named relationship | `subset-pass` / `subset-fail` |
| Equality | Two reciprocal relationship subset expressions | `equality-pass` / `equality-fail`, `equality-forward-fail` |
| Exclusion | Relationship requires absence of the named matching relationship | `exclusion-pass` / `exclusion-fail` |
| Irreflexive ring | Relationship requires different role values | `ring-pass` / `ring-fail` |
| Value enumeration | Concept requires a disjunction of literal equalities | `value-pass` / `value-fail` |
| Cardinality | Ontology-level comparison of a bound count with a numeric literal | `cardinality-pass` / `cardinality-fail` |
| Positive binary derivation | Relationship `derived_by` through one positive two-edge path | `derivation-pass` / `derivation-fail`, `derivation-missing-fail` |

The renderer's primitive participant and single-clause admission checks
limit these forms. Mandatory and frequency have authored counterexamples
and remain in the sidecar. Out-of-shape participants, operators, and
derivations also use the sidecar. The census observed 18 requires and one
derived expression. The corpus checks authored cases and the parser
checks syntax and scope.

## Import and offline evidence

The [OS3 spec](phase-OS3-spec.md) orders capped bytes, bounded decoding,
vendored schema, name graph, sidecar header and document binding,
optional report binding, pointer restoration, GND admission, and
publication. The import tests cover hostile syntax, each reader's cap,
compound-fault precedence including binding before reconstruction, final
admission, and the exact CLI refusal `ossie-import:schema` on exit 3.
Scaled lookup and distinct-ancestry budget controls each enforce a
four-second bound. GND diff calls `require_non_temporal` in
`src/gnd/diff.py` before model comparison. The census test compares the
complete restored JSON value to the source value minus exactly the
listed population subtrees and checks the report's exact pointer set.
This checks every retained field in the temporal inputs.

The [OS4 report](../evidence/OS4/reviewed/consumer-limitations.json)
binds converter `83ddc294c8840f5f497a2bdbec2348a128fc2254` and
RelationalAI 1.39.0. The wheel SHA-256 is
`33cbf6bc1a2ad598ffa4960bc0ddada1eab0a719de61ad6cc48ab378845126c7`.
The AST comparison covers concepts, relationship/property names,
supertypes, and identifier edges. The two intact refusals are the
composition derivation chain and inherited library-subtype identifier.
The isolation controls are separate. The consumer report owns these
observations and the missing source requirements. The export report
depends on GND input and output alone. [E3 and E3b](../evidence/OS0/README.md)
record identical offline source on Flights and refunds for 1.39.0 and
2.0.1. The later gates use the converter's 1.39.0 pin.

The [OS6 replay](../evidence/OS6/reviewed/consumer-limitations.json)
binds SDK 1.39.0 and contribution
`977cbb942c5458374192bb798a8a20320cca06f0`. Both consumer runs
observe 17 input requirements across the 36 successful census rows and
zero generated `require` calls. The `no-require-in-emitted-source`
finding remains. The [upstream PR](https://github.com/apache/ossie-converters/pull/162)
is open at the tested commit. Its Flights snapshot and synthetic
entity-anchored cases show generated source requirements. The six
value-tuple compilation controls supply metamodel evidence.

## Documentation

The [Ossie explanation](../../../../docs/explanation/ossie.md) limits
the claim to ontology concepts, relationships and supported formulas.
It excludes semantic models, mappings and query interfaces, describes
the deliberate `Duration` mapping, and calls PyRel optional with a
link to its explanation. The [refunds walkthrough](../../../../docs/how-to/share-an-ossie-ontology.md)
checks the recovered model digest. The Fable opening in GND commit
`6547f97b` describes why teams would use the same ontology across tools.
