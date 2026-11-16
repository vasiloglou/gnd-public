# AC1 · Bounded COUNT membership

Status — implementable once the reviewed plan and delegated corpus gate are
recorded.

## Provenance

The [draft plan](aggregate-count-certificates-plan.md) assigns AC1 all the
acceptance cases for issue #193 part 10. The owner explicitly selected an
empty-membership proof with unchanged aggregate row semantics. The plan
panel has not run.

## Obligations

| Source | Obligation | Discharge |
|---|---|---|
| Part 10 proposal | Bind representative source coordinates and expose individual member witnesses | D4, T1 and T8 |
| Part 10 criteria | Reject omission, duplication and stale inputs. Prove the empty group and bound execution | T2–T7 |
| Plan §§0, 5, 8, 9 | Preserve regular witness and evaluator behavior. Exercise installed public entry points and required reviews | T8 and gates |
| Current aggregate representation | Preserve distinct contribution identity and omit aggregate rows when no body bindings exist | T1 and T4 |

## Standing rules

- The external readers are total over hostile JSON. Cap each read, roster,
  string size, nesting depth and consumed population work before decoding or
  enumeration. Exercise oversized and deeply nested inputs.
- Count attempted row visits even when the result is empty. Deduplicate on
  canonical contribution tokens and do one bounded scan per evaluated group.
- Check request and certificate shape before the model, exact binding before
  proof inference, and input coverage before classifying a group as empty.
- One contribution identity policy governs production and verification.
  Independent replay reconstructs the expected member sequence from inputs
  with the evaluator seam. It does not invoke production.
- Put the wire and refusal order in one public contract. Preserve the existing
  aggregate documentation's empty-row rule.
- Measure omitted-and-adjusted, duplicate and no-group cases through public
  commands and compare them to the frozen oracle.

## Goal

A nonempty or explicitly empty complete membership claim replays at exit 0.
Forged members exit 1, an unsupported rule or coverage exits 2, invalid
input or stale binding exits 3, and bounded work refused during evaluation
exits 4. The original checker and witness compatibility controls retain
their current outputs.

## Design and reuse

| Capability | Search result | Decision |
|---|---|---|
| COUNT contribution identity and arithmetic | `semantics.extensions` | Reuse the exact identity and analysis contract through a narrow reusable seam |
| Bounded typed input and replay stages | `witness.schema`, `witness.replay`, `witness.service` | Reuse admission helpers and compatible typed cells. Add the separate COUNT verification route |
| CLI registration and disclosure | `cli.witness_command`, `witness.command` | Reuse parser, report and explicit raw artifact conventions |

The proposed command interface is
`gnd witness-count MODEL POPULATION --request REQUEST --raw --out CERTIFICATE`
and `gnd replay-count MODEL POPULATION CERTIFICATE [--raw]`.
The first scope admits reference-free, include-free, single-clause derived
COUNT rules with one asserted relation in the body. Each group key, `over`
cell and the `of` cell must unambiguously correspond to a body variable.
Initial types are representable String, Boolean and Integer. All variables
in the head except the fresh count variable belong to the group. The
population explicitly lists the body relation in `covers`. The relation
can have an empty row list.

The draft request is a JSON object with `version: 1`, `fact_type` and
`group`. The group is a mapping from head role names to typed witness
cells. The certificate contains version, exact input binding, the request,
`count`, `status` (`complete` or `empty-group`) and ordered `members`.
Each member has `over`, `of` and `fact_index`. The index picks the first
candidate occurrence producing that exact contribution. Canonical ordering
uses the existing contribution identity. The count equals the number of
distinct contributions. The exact draft wire example and digests belong
in the corpus gate before production code.

At most 100,000 candidate row visits and 10,000 distinct contributions
are proposed. Bound the raw wire by the ordinary 10 MiB witness ceiling,
reuse its depth and scalar limits, and expose smaller injectable limits
for negative controls. A scan refusal yields no usable certificate. Verify
raw model and population bindings through a bounded intake before inspecting
proof claims. Preserve v1–v4 ordinary certificate decoding.

## Decisions

| ID | Draft decision |
|---|---|
| D1 | Keep the proposed restricted rule fragment until wider evaluation needs a new bounded design. |
| D2 | Verify empty membership only for a named group over declared coverage. Existing aggregate rows retain their nonempty-group semantics. |
| D3 | The separate record has its own version and commands. |
| D4 | Canonical member positions select representative assertion rows. Use ordinary witness generation and independent replay when an individual proof is requested. |

## Tests

Author `tests/test_count_certificates.py`, a runnable fixture, and a separate
frozen answer roster before product changes. Gates include the following.

| ID | Expected result |
|---|---|
| T1 | Correct group and exact roster replay at 0. Different `over` values with equal `of` values remain separate. Repeated contributions collapse. |
| T2 | A rewired result with an omitted member and correspondingly reduced count, a duplicated member, or a substituted index exits 1. |
| T3 | Independently change each bound input, including a change that preserves the selected group. Replay exits 3 with stale binding. |
| T4 | Prove an empty named group at 0 and check that the ordinary evaluator still produces no row. Remove the coverage declaration and require exit 2. |
| T5 | An unsupported rule form refuses at 2. Unknown fields, invalid typed group and syntax refuse at 3. |
| T6 | Independently bound empty scans, member volume, wire bytes and nesting. Malformed oversized input exits 3. Exhausted evaluation exits 4 with no output certificate. |
| T7 | With changed input and an invalid proof, the binding fails before inference. An unreadable certificate fails before model use. |
| T8 | An installed wheel produces and replays both group variants. One member's requested positive witness independently replays on the same population. Ordinary witness and aggregate compatibility tests pass. |

## Phase boundary and size

The phase uses portable local fixtures and the named rule fragment. Estimate
250–400 lines of runtime, wire and CLI changes and 200–350 lines of controls
and fixture evidence. These are estimates, with measured size recorded after
implementation.

## Approval instrument

Use a red corpus under `tests/fixtures/count-certificates/` with the
executable example inputs and independent expected membership and exit data.
The spec gate will bind the exact fixture and answer bytes after the plan
panel. The phase diff has its own independent review.
