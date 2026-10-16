# CS0 — Reproduce and approve compiled snapshot semantics

Awaiting owner review, 2026-10-13. `auto=false`. No production implementation.

## Provenance

Derives from the complete compiled-snapshot-obligations plan r1, merged by the
owner's request in PR #17. Plan SHA-256:
`0f4391027a48854b64e5d6d63d3f1393a2608583db3c67a1caff9656b5262516`.
Runtime inspection/diagnosis baseline: `ab879dc5758123367be748744bbbd331e012f1e3`.
Issue #16 and its public downstream-apps reproduction at `efc9c0e` are inputs. No panel
opinion or prior certificate covers this spec. The plan's review instrument
remains an owner selection; no provider invocation is inferred.

Applicable carryovers: RF9 repair records 016 and 017 retain their semantic
admission restrictions, exact defining-home observations, frozen historical
evidence and zero-allowance layering boundary. RF6's ModelIndex/family-dispatch
and RF7's strict value/JSON policies remain binding. Their open questions,
shim retirement and historical budgets retain their existing owners; this phase
neither transfers nor resolves them.

## Obligations — harvest

| Source | Obligation | Discharge |
|---|---|---|
| Plan CS0-C1 | String-role comparison, numeric control, correct derived claims, walk failure through public interfaces | Baseline diagnosis and corpus cases N1/P1 below |
| Plan CS0-C2 | Pin current behavior and red successor expectations for the absent obligation | Proposed portable fixture and separate answer key; tests below |
| Plan CS0-C3 | Inventory compiled/retained entries; rule on CS-D1–D5, interfaces, schemas, coverage and limits | Design and decision table |
| Plan CS0-C4 | Retain commands/results/digests; return a non-reproduction to owner | Baseline JSON identifies command, source, external input hashes and limits |
| Plan section 9, CS0 | Public reproduction and admitted controls match narrated baseline; successor expectations demonstrated red for omission | Selected reproduction gate and targeted compatibility controls |
| Plan section 0 | CS-R1–R6 | Standing rules below |
| Plan section 5 | Canonical ORM docs, schema description and affected trace statements | Future CS2 pin-site list below; no skill edit in CS0 |
| Plan section 6 | Provenance, missed failure, coverage, projection, batch activation, compiler soundness, equivalence and layers | Corpus/design boundary and CS1 handoff |
| Plan section 7 | No full-walk replacement, compiler broadening, external app changes, publication or certification | Out-of-scope section |
| Plan section 10 | CS-D1–D6, all presently proposals | Owner table below |
| RF9 016/017 and AGENTS | Frozen evidence, current semantic policies, actual homes, no new layer allowances, PR-only changes | Portable inputs, compatibility controls and CS1 design constraints |

CS0 has no residual paragraph and no earlier phase record in this milestone.
The paid-for rules and the full plan were read sequentially; no delegation was
invoked without owner authorization.

## Standing rules

- **CS-R1 / explicit contract:** the proposed keyword is opt-in; the existing
  operations-invisible snapshot control must remain unchanged.
- **CS-R2 / one evaluation home:** CS1 must share a checking-layer evaluator
  across the routes rather than import the higher transition lane into checker.
- **CS-R3 / stable compiler:** compiler guards and in-memory side tables remain
  unchanged; copied fixtures never add generated constraints to authored models.
- **CS-R4 / honest outcomes:** known false compiled subsets fail; missing coverage
  is unchecked, not an empty relation; transition-only obligations stay outside
  the opt-in contract.
- **CS-R5 / stable identities:** use a source locator including operation,
  precondition and compiled projection index; typed identity and every role pair
  are obligations of CS1.
- **CS-R6 / approval and evidence:** this spec records proposals, not rulings.
  No production edits precede approval. No publication or recertification.
- **Totality:** use public loaders in the diagnostic and bounded fixture readers;
  malformed inputs must be admitted/refused before checking, never disguised as
  a compiled failure. No arbitrary downloaded driver was executed.
- **Algorithmic bounds:** CS0 inspects a fixed two-case corpus. CS1 must measure
  its new evaluator's work limit independently of file-size caps.
- **Validation order:** public model/population admission precedes checking.
  CS1 must preserve model/reference/population refusal order before evaluating
  compiled obligations.
- **Complete policy traversal:** inventory every operation and all its compiled
  entries, not only filter_compare or operations occurring in a supplied walk.
- **One normative home:** canonical semantics remain in packaged
  `representation-format.md`; public docs link there. No documentation change in
  this phase pretends that current defaults already evaluate operations.
- **Measurement:** the baseline has both a rejected string-role case and an
  admitted numeric-role control; answers cannot be inferred from exit 2 alone.

## Goal

Approve a portable reproduction and the exact successor contract. A baseline
driver exits 0 only if N1 exposes the missing numeric failure through public
single/batch checks while the walk rejects it, P1 has no walk failures, and both
snapshots have zero failed derivations. The successor failure expectation is
explicitly red before any runtime implementation. CS0 alone does not fix #16.

## Design

### Baseline diagnostic — already measured, read-only

`evidence/CS0/baseline.json` retains a summary of a diagnostic using the reviewed
public downstream-apps model-building functions from pinned source, packaged expense
data and public `api.check`, `api.transition` and batch CLI routes. It writes only
temporary workspaces outside the repository. Temporary input/driver bytes are
identified by hashes and are explicitly outside history. The retained summary
contains no expense rows or private data.

N1: category is a string role. Walk: exit 1, step 2, `pre_numeric` failure.
Single: exit 2, 0 failures, 0 unchecked, 0 warnings, 0 failed derivations.
Batch: exit 2, no failing constraints. Trace lists `filter_compare.pre_numeric`.

P1: amount is a numeric role. Walk: exit 2, no failed preconditions. Single/batch:
exit 2, no failed constraints or derivations. Both have unrelated vacuous
constraints, so a numeric control is not promised band 0.

### Portable corpus — proposed CS0 write set after approval

`tests/fixtures/compiled-snapshot/README.md`: case stories and public commands.
`model.orm.json`: bounded, self-contained model retaining the issue's operation,
role metadata and correct structured derivations without a downstream-apps import.
`nonnumeric.pop.json`, `numeric.pop.json`, `pre.pop.json`, `steps.json`:
admitted snapshot/control/walk inputs using portable model coordinates.
`expected.json`: separate current/successor answers. Separate the narrative
entry point from the answer key to permit a later blind reader.
`tests/test_compiled_snapshot_obligations.py`: public API/CLI reproduction and
fixture admission/digest controls, initially pinning baseline observations.

Each fixture must be narrated and inspectable before runtime implementation.
Do not import private transition/checker evaluators to construct expected answers.
External app files remain unchanged. The numerical reference's primitive and
actual fact/role bindings must determine the answer, not fixture ordering.

### Proposed successor interface, settled here for CS1

```python
api.check(model, population, *, compiled_operations: bool = False, ...)
checker.check(model, population, *, compiled_operations: bool = False, ...)
batch.check_population_directory(model_path, populations_dir,
                                *, compiled_operations: bool = False)
```

Existing keyword arguments retain their current meanings. CLI activation:
`gnd check MODEL POP --compiled-operations --format json` and
`gnd check MODEL --populations DIR --compiled-operations --format json`.
Combining this snapshot option with `--pre`/`--steps`/`--post` is usage exit 64.
It is not an option on validate, diff, verify or transition.

The caller explicitly declares compiled operational implications to be standing
obligations of the checked population. This does not establish provenance.
Defaults retain current behavior. All eligible compiled entries are evaluated;
retained transition-only entries are excluded, with that boundary documented.

Use existing verdict fields and schema versions: `constraint_type` accepts an
unrestricted string, so `compiled-subset` is representable without a wire-schema
bump. `constraint_ref` is the compiler's full source locator, for example
`$.operations[id=filter_compare].compiled[2]`, whose message names
`filter_compare.pre_numeric`. References must not collide with existing
positional authored-constraint references. Preserve source/status from the
original precondition. Batch failure IDs use exactly the single report IDs.
CS1 must validate this proposal against schemas and every composed report route;
if it cannot carry the semantics faithfully, return to the gate.

Missing coverage on either participating relation yields an explicit unchecked
row, reason `compiled-obligation-uncovered`; alethic unchecked implies band 4
unless a stronger refusal/failure wins. Empty covered antecedent is vacuous;
nonempty matched antecedent passes; known unmatched antecedent fails alethically
or warns deontically. Existing band precedence is unchanged. Computed derived
relations and bound references use the existing effective-view/unavailability
contracts; unknown inputs cannot be treated as missing facts.

CS1 will approve the exact work ceiling and availability reason identities from
a measured bounded evaluator design before implementing it. This CS0 proposal
does not claim a work limit has already been measured. Existing walk handling of
coverage and clean/vacuous rows remains pinned separately.

Do not simply append rows after semantic projection: projection, band, counts,
redaction, branch capture and assurance applicability must consume the same
approved obligation inventory. Unsupported assurance must remain unavailable;
adding a new scope is not a certificate.

## Decisions — all awaiting owner ruling

| ID | Proposed answer and cost | Owner ruling |
|---|---|---|
| CS-D1 | Implement opt-in compiled snapshot checks. Defaults keep band 2 for N1; activated checks become band 1 with the named failure. A default-on change breaks an existing explicit compatibility contract. | Pending |
| CS-D2 | `compiled_operations=True` / `--compiled-operations`; caller asserts standing obligations. No inferred provenance and no ignored activation. | Pending |
| CS-D3 | Missing coverage becomes unchecked/band 4 in this mode; no walk policy change. Exact counted-work budget is a required CS1 gate decision, not an invented CS0 number. | Pending |
| CS-D4 | Reuse current report schemas with qualified compiler locators and `compiled-subset`; schema/branch/projection tests must prove faithful representation before shipping. | Pending |
| CS-D5 | Agreement covers eligible compiled subset obligations only. Temporal, dynamic, effects, frame and intermediate-state claims remain walk obligations. | Pending |
| CS-D6 | No paid/provider panel invoked. Plan review selection and its retained pending bar need an owner disposition before implementation. | Pending |
| CS0-D7 | Corpus-first: approve the narrated fixture/answer-key instrument before CS1. The temporary diagnostic is evidence for choosing it, not a committed regression corpus. | Pending |
| CS0-D8 | Default `auto=false`; an explicit milestone-scoped `auto=true` instruction may delegate later phase gates while retaining spec-before-implementation, reviews and evidence. | Pending |

## Tests and verification selection

Future paths below are proposed, not existing/passing tests. Each run uses the
default lane exclusions; the owner previously stopped broad CI to focus on
failures. That is not authorization for a new full replay here.

| Obligation | Disposition / command or evidence | Expected / input boundary / invalidation |
|---|---|---|
| CS0-C1/C4 baseline | run: diagnostic command retained in baseline JSON | Diagnostic exited 0 with N1 walk 1/snapshot 2/batch 2 and P1 no walk failures; current source + pinned app + packaged example. Different inputs invalidate it. |
| CS0-C1/C2 portable fixture | run after gate: `uv run pytest -q tests/test_compiled_snapshot_obligations.py --tb=short` | Exit 0 for current-behavior fixture assertions and valid loader/derivation controls. Fixture/model changes invalidate the result. |
| CS0-C2 successor failure | run after corpus creation: the N1 opt-in case in an isolated red probe | Expected pre-fix failure is missing activation/evaluation, never fixture load refusal. Record exact command and exit before CS1. |
| CS0-C3 default/digest compiler boundary | run after gate: `uv run pytest -q tests/test_model_v2.py::test_operations_are_invisible_to_snapshot_checking tests/test_public_transition_contract.py::test_the_digest_is_unchanged_by_compilation tests/test_public_transition_contract.py::test_compilation_is_existential_and_guarded_by_the_sole_asserter_rule --tb=short` | Exit 0. Current loader/compiler, identity helpers and fixture changes invalidate these narrow controls. |
| Full regression / installed candidate | cadence: separately selected CI | Not selected by this spec. Prior results do not establish new runtime correctness. |
| Certification / provider oracles | cadence: explicit owner selection only | No new certification or external provider evidence. |

The CS1 branch corpus must distinguish pass, fail, warning, unchecked and vacuity;
missing coverage on either side; repeated variables/all role pairs; multiple
asserted effects; typed identity; duplicates; compiler refusal guards; report
composition and activation conflicts. Corpus reachability and expected answers
are obligations, not an automatic completeness claim.

Future CS2 pin sites: `tests/test_public_transition_trace.py`, CLI check/validate
help, `docs/reference/python-api.md`, `docs/guides/data-and-transitions.md`, and
the canonical packaged ORM representation/schema descriptions. Current numbers
and all conflicting prose sites must be inventoried during that phase's harvest.

## Out of scope

Production runtime edits, codegen/model evolution, a changed snapshot default,
compiler broadening, full-plan equivalence, external app edits, paid reviews
without selection, broad historical tests, certification, package publication,
CI/protection changes, and a claim that issue #16 is already fixed.

## Size

CS0 estimate: 0 production lines; roughly 100–180 test/driver lines and one bounded
model with paired populations, plus this spec and baseline summary. Measure the
actual fixture footprint after authoring rather than copy the app's full model
and quietly exceed this estimate.

## Approval instrument and implementability sweep

Corpus-first is proposed. The portable fixture README and separate answer key
are authored after this spec gate and approved before runtime implementation.
The current two-case read-only diagnostic supports this choice; it does not
substitute for approval of the future golden fixture bytes.

The contract is implementable as an explicit new checking mode: the current
compiler supplies eligible subset/role-pair/source locators; report schemas admit
the proposed labels; current public routes can accept a keyword/flag without
altering their defaults. Missing-coverage and projection composition require
explicit work in CS1. Work ceilings and unknown-derived outcomes are flagged for
that phase's gate rather than asserted as already settled. No criterion depends
on an optional external app run or certificate. Production edits remain gated.

## Delegated owner decisions — 2026-10-13

The owner answered “Approve and delegate the remaining gates and local reviews”
to the question naming this spec, opt-in design, auto=true, four local subagent
reviewers in place of the pending plan panel, commits and a runtime-fix PR.
This is delegated approval, not a claim of human reading of later artifact bytes.
The submitted spec SHA-256 was
`ae2025b628b39be5c3682874a1de6fa847e4058a323be38a2ca503ddb4d7d6c4`.
CS-D1/D2/D4/D5/D6 and CS0-D7/D8 are accepted as proposed under that delegation.
CS-D3's exact work limit is settled in the CS1 spec before implementation.
The portable corpus preserves all 11 operations in the bounded 88,667-byte
public model rather than silently reducing compiler guards. The two baseline
assertions pass; activation successors fail because the keyword does not exist.

Four local readers found no blocking defect in the opt-in approach. They required
disposition of dynamic-derived eligibility, explicit derived-unavailable controls,
activation through anchor/admission routes, and compiler-locator witness redaction.
CS1 owns those findings. These are four local same-model readers, not the maintained
six-seat provider panel or model-diverse consensus. No paid review ran.
