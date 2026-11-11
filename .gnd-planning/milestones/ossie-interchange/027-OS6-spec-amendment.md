# OS6 compiled requirements and source boundary

Delegated approval (auto=true), 2026-11-10, under the named milestone.
This amends OS6-C2 of the [approved phase spec](024-OS6-spec-gate.md)
after the authorized offline replay refuted the assumed SDK source
behavior. The original criterion is retained in the milestone plan
for the close record.

The RelationalAI 1.39.0 source generator needs an entity anchor in a
requirement's domain. The original isolated GND formulas use value
roles, a value concept, or ontology scope. The stock decompiler emits
none of their requirements. Compiling a primitive concept membership
as a domain produces a cast. Such a cast does not supply a finite
instance relation for enumeration or global counting.

The amended gate measures both the metamodel and emitted PyRel. Each
supported relationship formula must add exactly one scoped requirement
relative to the no-formulas control. Global cardinality and value
concept enumeration must emit a warning and add no requirement.
Preserve the decompiler omission in the consumer report. Positive
controls require actual emitted PyRel for an entity-anchored scalar
comparison and enumeration. Rebuilding the emitted source must
preserve both requirements. The Flights snapshot must contain the two
entity-anchored route requirements.

The original OS4 consumer evidence and its pinned converter remain the
basis for the product compatibility claim. The local contribution uses
the same SDK and records a separate converter commit. The publication
choice and independent review are unchanged.
