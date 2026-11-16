# Aggregate COUNT certificates

Status — draft r1, awaiting the standard GND plan panel. The owner selected
`auto=true` for this new milestone on 2026-11-16.

## Goal and completion predicates

Produce and independently replay a membership-complete COUNT certificate for
one explicitly selected group in a bounded population. Replay establishes
the exact members satisfying the admitted rule. The five controls from
[issue #193 part 10](https://github.com/vasiloglou/gnd-public/issues/193#part-10-aggregate-certificates-with-membership-completeness)
must pass. The empty group is a successful certificate about that group's
membership in that snapshot. The corresponding existing aggregate query
still has no row. An installed example, member witness instructions and an
independent implementation review complete the delivery.

## 0. Binding design rules

- Reuse the current COUNT contribution identity. Distinguish the ordered
  `over` tuple, the evaluated `of` value and one supporting source occurrence.
  Multiple body occurrences can support one contribution.
- Scope all claims to the consumed model and candidate population. Empty
  claims require the explicit body relation coverage declaration and a typed
  group selector. Missing coverage yields a refusal.
- Replay verifies independently from authenticated input rows. It never calls
  the certificate producer or uses the claimed count to bound the scan.
- Preserve the existing aggregate evaluator, regular witness formats and
  legacy entry points. Protocol, I/O and work limits are independently tested.
- Apply the standing boundedness, validation order, single policy walk,
  normative documentation and regression rules from process-phase.

## 1. Scope, sources and authority

| Source | Obligation | Owner |
|---|---|---|
| #193 part 10 proposal and criteria | Exact membership, omissions and duplicates refused, empty groups, input staleness, bounded work, optional member evidence | AC1 |
| Owner request on 2026-11-16 | New milestone in auto mode. Start with bounded COUNT and preserve existing empty-group row behavior | AC1 |
| Literature-depth close §Open questions | Reopen only the deferred part 10 row under the new milestone | AC1 |
| Representation format §Aggregates | Preserve ordered distinct contributions and the existing nonempty-body group rule | AC1 |

The scope reuses the merged literature work as a prerequisite. It introduces
one public worked example alongside the generic COUNT operation. Auto
delegates the named internal gates. External review authorization remains
specific to this milestone. Issue #193 stays open during this milestone.

## 2. Proposed contract

Use explicit `gnd witness-count` and `gnd replay-count` routes with a
separate versioned certificate. The first slice admits a single, fully
derived COUNT clause with one asserted body relation, no joins across
relations, no negation, no recursion and no arithmetic. The group selector
assigns the projected head variables other than the result. The contribution
is the ordered tuple of `over` variables paired with the variable `of`
value. Model, population, target and typed member identities are authenticated
and canonical. The scope is one group per request.

Replay checks shape and bounds, binds the consumed inputs, then independently
scans the declared-complete relation for that group. It compares the exact
canonical sequence and validates the count and supporting occurrence
coordinates. Empty membership is a separate success outcome over the snapshot.
It creates no aggregate row and cannot turn a missing source into zero.

| Code | Outcome |
|---|---|
| 0 | Exact membership established, including an empty named group |
| 1 | Well-formed proof invalid, including omission, duplicate or substituted occurrence |
| 2 | Rule fragment or coverage unsupported |
| 3 | Malformed input or stale binding |
| 4 | Scan, projection or output work refused under a fixed ceiling |

## 3. Dependencies and artifact homes

Use [the literature-depth close](../../literature-depth/016-milestone-close.md)
from merged PR #203 and the current witness and aggregate contracts. The
component consult found `semantics.extensions` for exact identity and the
existing evaluator, `witness.schema` for typed bounded inputs,
`witness.replay` for staged binding, and `witness.service` for loaders and
artifact I/O. Adapt these facilities. The separate COUNT membership verifier
has its own domain logic because the ordinary proof kernel replays finite
positive inferences and does not prove set completeness. New code uses the
repository's component and dependency-layer registries.

## 4. Phases and criteria

| ID | Readiness | Deliverables |
|---|---|---|
| AC1 | Plan panel and delegated plan ruling, then corpus-first spec gate | Producer, independent replay, compatibility corridor, exact mutation controls, member-witness example and installed smoke |

AC1 records the model and the authored member roster before implementing.
The milestone closes after AC1 and the standard close panel satisfy the
project's review bar. No phase depends on an optional lane.

## 5. Documentation and compatibility

Define the new wire and exits in one witness reference and link it from the
public command guide. The worked example shows an ordinary nonempty count,
an empty named group, and how to request an existing positive witness for an
asserted supporting row. Keep ordinary witness schemas and checker output
unchanged. Update the component index and any layer registration for new
modules.

## 6. Risks and controls

| Risk | Control |
|---|---|
| A self-consistent abbreviated list passes | Remove one member, decrement the supplied count, and require proof-invalid |
| Repeated input proofs inflate the count | Equal contributions with different origins collapse. Distinct `over` bindings with equal `of` values both contribute |
| Missing evidence is treated as empty | Named empty group over explicit coverage succeeds. Removed coverage refuses |
| Input edits preserve the claimed outcome | Change model and population independently. Change an irrelevant bound row and require stale binding |
| The proof hides the cost of completeness | Force the scan limit independently of result size, and separately exercise member and certificate-byte caps |

## 7. Outside this initial milestone

Other aggregates, joins, negation, computed dependencies, references, includes
and composition-record lineage are separate extensions. The certificate
establishes snapshot membership over declared inputs. Scientific or
corpus-wide completeness, release certification and publication have their
own scope.

## 8. Execution and review

Use topic-branch development, an independently authored red corpus, the
standard plan and close panel with the project's four-valid-response bar,
and one independent phase diff review. Each live review retains separate
authorization. The delegated plan, phase and close rulings bind exact bytes.
PR merge remains a separate owner decision.

## 9. Verification

Run the direct tests over public production and replay, ordinary aggregate
semantics and ordinary witness compatibility. Run the repository's default
structural checks, strict component check and lint with explicit inherited
baseline comparison if required. Verify the routes in a fresh installed
wheel. The original baseline fixture already measures checker exit 0,
ordinary aggregate witness exit 2, empty-body omission and duplicate-proof
deduplication. Those measurements are compatibility gates.

Planned focused command after the direct tests exist.

```sh
uv run pytest -q tests/test_count_certificates.py tests/test_v62_phase4_aggregate.py tests/test_li0_witness_wire.py tests/test_witness_composition.py --tb=short
```

## 10. Decisions and open questions

| ID | Proposed disposition |
|---|---|
| D1 | One admitted COUNT fragment first. Expand only with a separate measured reason. |
| D2 | Distinct affirmative empty-membership certificate over an explicitly named group. Preserve ordinary aggregate semantics as the owner specified. |
| D3 | Separate explicit commands and versioned payload to preserve ordinary witness readers. |
| D4 | Use deterministic canonical members with representative positions. Offer individual positive witnesses through ordinary `gnd witness`. |
| D5 | Prove bounded scan work as well as bounded certificate size. |
