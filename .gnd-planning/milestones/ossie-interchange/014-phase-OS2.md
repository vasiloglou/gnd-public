# OS2 formula projections

Completed under the delegated gate for ossie-interchange. The
[approved spec and corpus](011-OS2-spec-gate.md) at `a0c0ac7d` preceded
the renderer at `337267e8`.

## Independent review

Claude Code read the [candidate source](notes/phase-OS2-claude-review.md)
and then the [exact candidate diff](notes/phase-OS2-claude-diff-review.md)
from `a0c0ac7d` to `337267e8`. One reviewer is one reviewer. Both
responses concern the same candidate bytes. The reviewer ran no gates.

| Finding | Class and disposition |
|---|---|
| Source governance fields reported as formula semantics | Blocking. `owner` and `allowed_fixes` now remain extension pointers. |
| Entities, subtype participants and multiple clauses projected beyond the corpus | Blocking. Formula admission now covers the corpus's primitive participants without a hierarchy, and one positive derivation clause. The access app's entity cardinality moves to the extension. |
| Lowercase reserved-looking roles and facts | Hardening control. The pinned lexer looks up exact token text. The parser accepts `count` and `exists` as names and refuses `COUNT` in the same role position. |
| Comparison polarity | Hardening. Only IR `compare` nodes can emit a guard, ring comparison or cardinality bound. An injected alternative kind exercises fallback. |
| Possible crash for derived-on-derived input | Refuted by `lower_rule_atom`, which retains the source fact ID and uses the admitted role order. A derived-on-derived test confirms extension fallback. |
| PyRel preprocessing and role order | PyRel's dialect preflight covers plan-specific names, temporal and subtype universes, and its own derivation subset. Ossie separately admits reviewed local shapes. PyRel's `_unswapped` introduces helper relations for its target. The Ossie test reverses authored roles on guard and chain facts, uses internal determinants, and verifies identical projected formulas. |
| Per-scope parser coverage, atomic equality, and work bound | Hardening. The pinned validator admits the combined corpus. The pinned parser rejects a corrupt formula at each of the four emitted locations. A one-direction equality failure checks rollback. Scaled guard, subset, value, cardinality, ring and derivation cases use one source index. |
| Shared lowering and bookkeeping | Hardening. Direct IR assertions cover guarded, equality and ring requirements. Id-less rules receive separate path-based internal IDs. The exact parity replay covers the `plays` cache in existing consumers. |
| Additional completeness suggestions | The source schema is closed for admitted rule fields. Listing rows describe the requirement's witness vocabulary. The existing bound remains covered by the mixed structural work test. Unsupported operators, strings and partially lowered groups stay in the sidecar. |

Six targeted regressions failed on the archived candidate and passed after
repair. The focused gate from [record 012](012-OS2-renderer-candidate.md)
passed with 191 tests and 299 deselections. The selected pinned validator and
parser lane passed 48 tests. All 29 authored checker verdicts still match.
The 162 PyRel render and refusal observations match the archived base bytes.
The [reviewed census](evidence/OS2/implementation/census-formulas-reviewed.json)
contains 18 requires and one derived expression across 38 eligible inputs.

## Refactoring review

One indexed requirement context owns the admitted source. The adapter binds
source and projected roles by identity and commits a formula group only
after every placement succeeds. PyRel keeps its strict wrapper and existing
diagnostic order. The existing pointer walk owns extension and formula
dispositions. The candidate's material findings have executable controls,
so another review round is unnecessary for this phase. The repairs carry
the local verification above. The upstream parser lane measures syntax and
declaration admission. The corpus and pinned prose supply the semantic
boundary. No Ossie formula execution claim is made.
