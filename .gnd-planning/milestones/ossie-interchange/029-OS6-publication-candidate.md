# OS6 contribution ready for publication decision

The upstream branch `codex/convert-ontology-requires` is local at
`977cbb942c5458374192bb798a8a20320cca06f0`. Its verified Git bundle
has SHA-256
`d8ad2f02b18ff669a825686aedf8e50067cc46a19b60761ec5a7c924b609848e`.
The independent Claude Code review read the diff at `0f00f798`.
One reviewer is one reviewer. The retained local review has SHA-256
`e5fac8f7a786a63be8e1dc89b981a8727a34757ad8929cbf0ffb28c240213dca`.

| Review finding | Disposition |
|---|---|
| SDK type failures and literal compatibility | Numeric-to-string comparisons and mixed enumerations reproduced unvalidated metamodel requirements. The converter now refuses incompatible literals before emission and translates SDK diagnostics to scoped warnings. |
| Scope in warnings | Warnings identify the owning relationship, concept or ontology and report at the caller. |
| Repeated role players | The unnamed default role supplies the bare concept binding. Other repeated player references require an unambiguous role name. An entity self-relationship reproduced an unbound decompiled variable. Repeated entity scopes now warn and skip. |
| Source and role evidence | The test binds both comparison operands to their original value-tuple positions. Entity-anchored conjunction, comparison, enumeration, unary predicate and EXISTS controls round-trip through source. The Flights snapshot retains its two route requirements. |
| Unsupported inputs and warning tests | The tests check the reasons and scopes for literal-only comparisons, naked references, unsupported ontology and value scopes, and incompatible literals. Raw formulas follow their existing compatibility path. |

The post-review upstream RelationalAI suite passed all 40 tests. The
[reviewed replay](evidence/OS6/reviewed/consumer-limitations.json) exits 0
and has SHA-256
`def7d6b48da061def1b816d152b94acf92eabf170725b95694edac9951d3206c`.
It retained 36 matching intact conversions and the original two refusals
with the same diagnostics. Six isolated formulas add a scoped
metamodel requirement and the other two warn. The pinned decompiler
emits zero requirements for those eight controls. The GND focused gate
passed 335 tests with 49 deselections.

The prepared upstream PR title is “Convert scoped ontology requires
into PyRel requirements”. The exact title and body remain in local
review files. Their respective SHA-256 digests are
`c4110353aacad806f501f5af4d8626f2309a1f9aafca53e03d5625d1628fd3b6` and
`c3838d423e01de1210b2eb255aabe741d9098f2cdad4c7001f74ddbcccf14c65`.
The owner's publication choice is the remaining OS6 gate.
