# Phase OS2 — Formula projections with reviewed verdicts

## 1. Status

Delegated spec gate, 2026-11-10. The reviewed and repaired corpus is bound
in record 011 before the renderer.

## 2. Provenance

Plan r3 predicate 4 and OS2, the [OS0 revised formula observations](../evidence/OS0/revised/E2.json)
and the [closed OS1 exporter](../009-phase-OS1.md). OD2 retains the
digest-bound sidecar. OS1's confirmed-alethic boundary applies to hard
Ossie formulas. The draft corpus was authored against the pinned Ossie
ontology specification and replayed through GND before any renderer exists.

## 3. Obligations

| Source | Obligation | Instrument |
|---|---|---|
| OS2-C1 | Formulas use the pinned grammar and intended scope | Positive and negative parser controls, exact corpus formula bytes and census oracle |
| OS2-C2 | Hand-derived satisfying and violating expectations for every emitted family | Independent semantic review and corpus commit precede renderer; GND checker matches every named case |
| OS2-C3 | Existing PyRel consumers retain behavior, including refusal order | Focused `test_pyrel_rules.py` and existing selected consumer checks |
| OS2-C4 | One disposition per source pointer and deterministic binding | Full census pointer check and sidecar replay for rendered and fallback cases |
| R7–R9 | Pinned claims, explicit fallback, credential-free default | In-process rendering, constrained output grammar, separately selected local oracle |
| OS0 carryover | Formula probe results apply to individual expressions | Narrow supported lowering, with sidecar retention for each unverified source form |

## 4. Standing rules

1. Totality. OS1's admission remains first. Lower only validated constraint
   and derivation shapes. Unknown IR or unencodable scalar keeps the
   source value in the sidecar. The bounded reader remains one shared path.
2. Work bound. Index fact and concept projections once. Traverse each
   supported requirement group once. Exercise a scaled formula projection.
3. Order. Admission, core projection, whole-group formula lowering,
   schema validation, loss accounting and publication. Existing PyRel
   refusal ordering stays at its current entry point.
4. One walk. Extract the per-constraint lowering seam from the PyRel
   requirement walk. Ossie consumes that seam and the existing normalized
   clause path. OS1's one pointer walk owns every disposition.
5. One home. Representation-format.md owns output semantics. The reviewed
   corpus binds representative expectations to a pinned upstream contract.
6. Measure. The independent reader checks the semantics of candidate
   formulas before the renderer. Syntax acceptance and GND comparisons
   are recorded separately.

## 5. Goal

The committed corpus covers each emitted family with a passing and a
violating named case. GND matches its expected verdicts and the pinned
parser accepts the produced formulas. Formula or clause groups without a
verified lowering retain their complete GND form in the sidecar.

## 6. Design

| Capability | Search and reuse |
|---|---|
| Requirements IR | `rule requirement lower constraint comparison cardinality`; reuse `export.pyrel_rules` requirement dataclasses and existing lowering. Keep the strict PyRel wrapper and its refusal behavior. |
| Structured clauses | `clause atoms normalize derive joins projection`; reuse the normalized clause and atom seams of `export.pyrel_rules`. Their Python source renderer is specific to PyRel. |
| Ontology and wire | `ossie interchange projection report sidecar`; adapt `export.ossie` to expose projected concept/relationship role identities and update the existing disposition map. |
| Verdicts | `validate compare population check report verdict`; reuse `gnd.api.check` against explicit populations. |
| External | Read pinned Ossie formula grammar and `ontology.md` semantics. Reuse the OS1 oracle. Keep provider libraries outside GND runtime. |

The rendering adapter returns a complete formula group for one confirmed
alethic constraint or one eligible derived fact. A partial group never
changes the ontology or disposition. It emits only the following initial
shape candidates. The independent review and pinned parser must validate
each candidate before its shape ships.

| Family | Candidate lowering |
|---|---|
| Guarded | A plain scalar comparison over variables of one fully bound antecedent tuple, scoped to that relationship. |
| Mandatory | Existence of a relationship for the owner concept, when the mandatory role is the projected first role. |
| Frequency | Count of distinct second-role values for one binary owner, with a finite bound. |
| Subset, equality and exclusion | A scoped relationship membership or absence check when each target role binds to the current tuple. Equality emits both directions together. |
| Ring | Irreflexivity as a comparison of two roles of the same binary relationship. |
| Value | Finite scalar enumeration scoped to the declared value type. |
| Cardinality | Count of the named concept at ontology scope. |
| Derived fact | A positive, acyclic chain of two binary relationships with a single join variable and both head roles bound. |

Apply the projected role order and emitted concept/role spelling. Keep
deontic rules, proposals, unresolved helpers, computed operands,
unverified aggregate and recursion forms, and partially representable
groups in the sidecar. A renderer may widen the supported set through a
reviewed corpus addition before shipping the additional form. Literal and
identifier rendering must be admitted by a closed output grammar before
formula placement.

The loss report uses `requires` with reason `formula` for supported
constraint and derivation rule pointers. Its sidecar retains original
source spelling and reconstructible syntax. The exact source constraint
and modality continue to round trip. The ordinary renderer uses no
external parser.

## 7. Decisions

| ID | Proposed ruling |
|---|---|
| D1 | Bind the independently reviewed expected-verdict corpus before implementation. |
| D2 | Keep every unverified source shape recoverable through the sidecar. |
| D3 | Render hard Ossie formulas only from confirmed alethic rules. |
| D4 | Reuse the PyRel requirement IR while keeping its strict entry point and all existing consumer expectations. |

## 8. Tests

The corpus checks nine constraint families and one derivation in both
directions. Its replay exits 0 with 20 matched verdicts. The implementation
gate adds exact formula-placement and scope tests, malformed formula
controls, whole-group fallback, pointer accounting, time bound, the
selected pinned parser lane and focused PyRel regressions.

## 9. Out of scope

Ossie import, PyRel conversion of Ossie documents, and running formulas in a
third-party engine. The plan's semantic instrument is independent review of
the hand-derived verdicts plus the GND comparison.

## 10. Size

One compact model with 20 cases. Implementation estimates depend on the
reviewed grammar shapes. The adapter and focused corpus checks should fit
in several hundred lines.

## 11. Approval instrument

[Corpus r1](../evidence/OS2/corpus-r1/README.md), split from its expected
verdict file. The phase remains before its delegated spec gate.

## R2 review disposition and supported shapes

The independent reader confirmed r1's 20 verdicts and required
discriminating cases. The [approved r2 corpus](../evidence/OS2/corpus-r2/README.md)
adds nine cases and scope/formula pairs, and keeps the r1 artifact intact.

- C1 uses ontology-level `COUNT[Concept]` with a third Account visible in a
  fact. The pinned parser and its ontology-level aggregate fixture confirm
  scope. The projection supports the corpus's object cardinality upper bound.
- C2's global-count counterexample is retained. Frequency stays in the
  sidecar because the duplicate-row witness fails GND frequency but
  satisfies the set-valued Ossie count. Mandatory stays in the sidecar
  because the covered empty relation is vacuous in GND.
- C3 limits derivation lowering to an ordered chain of two binary positive
  atoms. The first atom's last role equals the second's first role. The
  derived head binds the endpoints in its projected order. The renderer
  emits the dotted path without a final argument list. Multi-row, empty,
  missing and spurious claims distinguish its semantics.
- C4 supports confirmed alethic value enums of safely representable strings.
  Both admitted strings now occur in separate passing cases.
- C5 supports a comparison between a scoped integer variable and integer
  literal using the reviewed `<=` shape. The boundary 100 passes.
- C6 limits subset, equality and exclusion to unary same-player scopes.
  The equality cases isolate both directions. The ring form is a
  same-player binary irreflexivity comparison.
- C7 requires projected names and exact role identities. Formulas needing
  unsafe identifier tokens or unknown typed bindings keep the original source.
- C8 pairs each scope and formula and checks the named verdict only.
  Implementation tests cover deontic and proposed rules, unsupported
  operand forms and whole-group fallback.

All added or changed placements retain source spelling through the existing
sidecar. Syntax probes and checker results are separate. The approved
corpus does not claim general execution equivalence for other forms.

## Implementation findings

The new renderer uses projected role identities and the existing per-rule
PyRel lowering. The strict PyRel entry point retains its preflight, iteration
and diagnostic order. The common source index caches value-type participants
and reference rosters. The before/after render comparison covers 162 targets.

The candidate emits 19 requires and one derived_by expression across the 38
eligible census inputs. The corpus renderer reproduces every approved
formula/scope pair. Unsupported, deontic and proposed rules retain their
source fields. The partial cardinality group test prevents an upper bound
from shipping by itself when the lower bound has no approved lowering.

The selected pinned parser accepts all emitted census documents and the
combined corpus. Its malformed emitted-formula control refuses. A distinct
independent review of the implementation diff remains pending.
