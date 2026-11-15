# LI4 Contextual assertions and saved opinions

Status: implementable once the delegated corpus gate is recorded (2026-11-15).

## Provenance

Plan r3 sections 0, 2, 4 LI4, 5–9 and the 001 rulings D5 and D7.
LI2 supplies separately verified identity decisions and provides the
span-keyed mention pattern. LI1 establishes separated scored stages and
keeps its previous expected corpus results.

## Obligations

| Source | Obligation | Where exercised |
|---|---|---|
| A1 | A supported conditional assertion retains its condition. Removing the condition fails semantic-support | T1 and T2 |
| A2 | Co-occurring names with a wrong predicate fail admission | T3 |
| A3 | Distinct polarity and attribution outcomes for negation, comparison, speculation, citation. Neither triggers a positive own finding, and distinct experiments retain opposing results | T4 |
| A4 | Missing, abstained, stale and over-limit saved opinions cannot approve | T5–T7 |
| A5 | Use real saved-judgment inputs and invoke the command. Bind raw, policy, receipts and resulting report. Retain raw beside admitted bytes. Harmless receipt drift moves the record; a verdict change moves the population. Missing and forged input refuse | T8–T9 |
| §0 | Total bounded reader, small deterministic write set, refusal order, one admission predicate and one normative home | Design and T9–T10 |
| §§2, 5 | Model a versioned work and its objectified assertion, qualified participants, context and evidence. Document the worked example and point the two named skills to it | Model, documentation, package guards |
| §6 and D7 | Treat stretched as a rejected opinion. Preserve the rubric disposition and source text separately | Receipt corpus and T3 |
| §7 | Hold publication, certification, external-scale evaluation and successor work out of the phase | Scope |
| §§8–9 | Corpus/spec rulings, direct example and judgment controls, guards, independent diff and refactoring review | Verification ledger |
| LI1 residuals | Evidence layouts stay distinct. Source bytes follow the existing safe path contract | Reused artifact reader and scoped output |

## Standing rules

Bound all file reads below the API caps and snapshot the byte inputs before
judgment execution. Model and population shape pass through the shipped
readers. The CLI treats a malformed JSON input or failed binding as exit 3.
A fixed occurrence ceiling follows judgment policy. The example adds a
linear projection test, separate from the subprocess's bounded wall time.

Validate argument routes and all required files, then run the saved-judgment
command over captured bytes, then assemble the per-occurrence selection,
and finally publish output with the admission record as the final marker.
One selector decides projection eligibility for all records. The example
README defines the model pattern and producer result. The saved judgment
contract remains the only home of receipt semantics. The producer accepts the subject and opinion inputs directly. A receipt change comparison
measures the effects on output identities.

The runtime layer map and family dispatch are unchanged because the work
lives in the packaged example. No runtime tolerance is added.

## Goal

Demonstrate contextual scientific assertions and produce a digest-bound
admitted population by running saved judgments over the raw extraction.
The producer exits 0 after producing the admitted projection and audit
record, including recorded nonadmissions. It exits 3 on invalid,
missing or forged inputs and publishes no complete result on refusal.

## Design

| Capability | Search | Reuse |
|---|---|---|
| Saved-judgment binding | saved judgments receipt trust, and policy admission | Reuse gnd judgments check and its frozen receipt contract |
| Atomic publication | atomic tree manifest retention, safe bounded artifact files | Reuse artifacts.publish_directory_once and anchors.read_regular_path |
| Context assertion objectification | objectified assertion external reference, ORM representation reference | Model one statement tuple with an associated assertion entity and identifying facts |
| Independent admission reasoning | literature stage floors, model-population inspection | Project positive eligible statements from verified saved-judgment targets. Keep the producer in the example |

Add the example module assertion_admission.py and examples/literature/assertions/
with model.orm.yaml, raw.population.json, policy.json, receipts.json,
rubric.json and evidence passages. The input is the exact contextual
fixture's model version. The principal asserted fact type
assertion_statement has string roles passage, work, version, predicate,
actor, actor_kind, object, object_kind, qualification, condition, regime,
experiment, polarity and attribution. It is objectified as Assertion,
externally identified by a work and passage through assertion_names_work
and assertion_names_passage. Its URI-like assertion identifiers are
stable strings in those identifying fact types. Participants are tagged
sense or mention. A conditional statement holds condition, regime and
experiment in the statement itself. A qualifier sentinel spells absent
conditions as 'unspecified', rather than inventing a condition. Evidence
documents contain distinct passage snippets, with receipt quote offsets
in UTF-8 bytes. Source text persists separately from opinions. The example
source corpus is synthetic.

The exact route is
`python -m gnd.examples.literature.assertion_admission MODEL RAW POLICY RECEIPTS TRUSTED_ROOT --out DIRECTORY`.
The public producer entry is
`admit(model: Path, raw: Path, policy: Path, receipts: Path, trusted_root: Path, out: Path) -> dict`.
It reads four bounded file snapshots and invokes
`python -m gnd judgments check model.orm.yaml raw.population.json --policy policy.json --receipts receipts.json --trusted-root ROOT --unredacted --format json`
from their scratch directory. A trusted root remains the judgment command's
bound evidence authority. A process exit 0 or 1 with a matching closed
report supplies target opinions. All other exits refuse this producer.
A supplied report cannot enter the route through an input.

For each statement by raw tuple index, semantic support requires the
saved-judgment target's verified admission and, when qualification is
conditional, a concrete condition. Report per-row support separately
from whether the row is eligible as a positive own finding. Positive
eligibility requires asserts and own-finding. Receipts can support an
accurately attributed negative or hearsay statement, which stays in the
retained raw input. Distinct experiments remain distinct rows. Preserve
the original statement order and only the external identity bindings of
selected statements. Project no unrelated fact data into the output.

Output always has raw.population.json, judgment-report.json,
admitted.population.json and admission.json. The closed admission
record schema string is literature-assertion-admission/1. Its fields
are schema, model_sha256, raw_sha256, policy_sha256, receipts_sha256,
judgment_report_sha256, admitted_sha256, and stages. Each of the two
stages semantic-support and positive-own-findings contains the original
statement indexes and closed rejection reasons. The last file is the
bound publication marker. An existing destination refuses before
judgment execution.

## Decisions

| ID | Proposal | Cost |
|---|---|---|
| D1 | Use an example-specific contextual model and stage report. Keep the earlier LI1 wire independent | This gives a separate fixture for the conditional stage and avoids rebinding LI1's owner-approved corpus |
| D2 | Use the actual gnd judgments CLI over captured snapshots. Accept a structured exit 1 so an admitted subset can retain the right rows | All-or-nothing handling loses good assertions alongside known unsupported statements |
| D3 | Preserve true negative and attributed statements as raw, with separate support and eligibility statuses | Conflating the statuses either exaggerates positive evidence or treats accurate extraction as wrong |
| D4 | Use the standard saved-judgment contract limits and capture the exact returned report. The rubric ledger keeps disposition alongside receipt IDs | Moving rubric meanings into the judgment reader would change generic semantics |
| D5 | Corpus-first, one Claude Code diff review, no spec panel | Critical exits and serialized outputs are already specified and can be pinned before source implementation |

## Tests and verification

| Test | Expected |
|---|---|
| T1 validate model and run complete corpus | model exit 0, example exit 0, supported conditional field exact, two opposed experiments retained |
| T2 remove condition while retaining conditional marker and rebinding an approving receipt | semantic-support fails for occurrence. Positive projection excludes it |
| T3 wrong predicate with co-occurring types and a stretched receipt | rejected, absent from positive projection |
| T4 polarity and attribution pairs | all four distinct and absent from positive own findings |
| T5 missing and abstained receipts | distinct reasons, no approved row |
| T6 stale subject or trusted evidence | producer exit 3, no complete output |
| T7 judgment limit | producer reports exit 3, no truncation or fabricated approval |
| T8 change receipt serialization, then change verdict with valid bindings | first moves admission record only, second also moves admitted population |
| T9 missing raw/policy, malformed inputs, supplied report, existing output | exit 3 before publication |
| T10 synthetic projection size | bounded linear selection stays below 10 seconds |
| §9 | Direct assertion, saved-judgment and affected example controls |
| Guard list, Ruff, components check | project hook, using phase base in component check |
| Broad lanes | explicit separate selection only |

## Scope

This phase binds saved opinions to a synthetic worked example.
Lineage, automatic reviews and host-scale datasets are separate work.

## Size

Approximately 170 producer lines, 130 test lines and one model/receipt
fixture. The documentation lives with the example and two skill pointers.

## Approval instrument and implementability sweep

Use corpus-first. The raw tuple contains the exact receipt target index.
No opinion is synthesized to compensate for a missing row. The public
judgment route exposes per-target opinion and mechanical admission in its
0/1 payload, so one accepted occurrence can coexist with an excluded one.
Evidence and subject bytes can both be mutated independently. The app can
bind each input and output before publishing, and a stable relative route
keeps judgment-report bytes portable. The conditional and attribution
checks are separate and each has a discriminating case. The read cap,
occurrence bound, timeout and publication marker are all enforceable with
shipped primitives.
