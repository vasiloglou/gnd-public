# GC1 independent review disposition

The owner selected Claude Code for independent diff review of GC1–GC4.
Two read-only invocations exited 124 without a review. The focused
one-pass invocation supplied the runtime and test diff on stdin, used Opus
at high effort with tools disabled, and exited 0. Its
[response](phase-GC1-claude-review.md) describes candidate `62c45016`.
The reviewer examined only the supplied diff and ran no tests. One reviewer
is one reviewer.

| Finding | Disposition |
|---|---|
| Omitted IR and verbalization excerpts | Both paths occur in the exact committed candidate. The omissions limited the review scope. Targeted tests exercise both. |
| Left-term validation | The report's proposed acceptance defect did not reproduce. Derivation `where` with a unary add returned exit 3 through schema, while an unbound term returned exit 3 with `semantic:term-unbound`. Term analysis already yields semantic IDs. |
| Untyped operand acquires a Date domain | Blocking. The direct runtime regression returned true before the fix. Derivation rules now prepare their operand primitive from the declared binding scope. The generic term evaluator requires type information for a runtime string to compare as a Date. |
| Shared membership identity | Retain the approved single identity implementation. The separate, fixed-seed helper encoding validates both membership operators over legal populated bindings and independently checks their offending subjects. The shared reference and production key remains an evidence limitation. |
| Synthesis candidate spelling | Blocking. A reachable integer member spelled `1500.0` produced `search-limit` before the fix. GC1 now normalizes that spelling for Integer binding sites and rechecks both emitted populations. Existential synthesis preserves the existing unknown precedence, and GC1's separately proven finite Boolean criterion is scoped to direct comparisons. |
| Exporter refusal and precedence | Blocking. The pre-fix Soufflé target exported the model without a refusal. It now refuses guarded and derivation membership explicitly. Lean's existing named refusal passed the added control. PyRel checks reference inputs before its membership capability refusal. |
| Membership work accounting | Hardening within scope. The pre-fix derivation counter reported one operation for a two-member list and one binding. The corrected counter includes preparation and the binding lookup. Compiled clause entries persist across a fixpoint invocation. A deterministic operation-count check accompanies the existing timing bound. |

The review supplied evidence over the candidate. Reproduction and focused
verification supply evidence for the changes made after it.
