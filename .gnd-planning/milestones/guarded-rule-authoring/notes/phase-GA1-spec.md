# GA1 · Generate guarded rule cases · draft r1

**Awaiting owner review.** The plan and first-phase gates are pending.

## 2. Provenance

[Plan r2](guarded-rule-authoring-plan.md), [GR-D8](https://github.com/vasiloglou/gnd-public/issues/179),
and the predecessor's [close](../../guarded-rule-workflows/006-milestone-close.md).
No independent review has run.

## 3. Obligations

| Criterion | Discharge |
|---|---|
| A1 and GR-D8 | §6 targeted paired cases and checker confirmation |
| A2 and the synth oracle invariant | §6 independent labels, named local refusals and bounded search |
| A3 | §§6 and 8 mixed-model and measure compatibility |
| Project standing rules | §4 and the public route gates |

## 4. Standing rules

Keep capped reads and total guard admission. Bound search and test that
budget independently of file size. Apply validation before generation and
check target outcomes before keeping cases. Use one atom walk and the
existing synth binding identities. Give the manifest one normative home
in the synth guide. Discriminate active pass from vacuity with a positive
antecedent count and test a rule that cannot be falsified.

## 5. Goal

The opt-in synth command returns a pair with checker verdicts fail or
warning (by modality) and active pass, respectively, for served guards.
An unserved guard produces a reason keyed by declared ID. Other served
constraints still produce their cases on the mixed fixture.

## 6. Design

| Component | Decision |
|---|---|
| `synth.service`, `synth.guarded` | Adapt the CLI orchestration and independent guarded matching |
| `synth.pool`, `synth.values`, `synth.constructive` | Reuse typed assignment and population construction |
| `check.snapshot_decision` and GW0 | Reuse ordinary checker confirmation and authoritative antecedent count |

Propose `gnd synth MODEL --out DIR --guarded-cases [--seed N]`. Build a
typed seed for the antecedent preserving repeated roles and literals.
For atom and exists use a missing witness in the failure and construct a
witness in the pass. For absence add the forbidden fact in the failure
and omit it in the pass. For comparison search legal typed operands on
either side of the predicate. Independently verify the target rule and
its antecedent, then use the checker to confirm the two outcomes. A case
manifest records rule ID, kind, population path, binding count, target
verdict, other findings and per-rule refusal reason. Use seed and declared rule order to make the corpus reproducible.
Propose at most 128 candidate attempts per rule within the existing
guarded-oracle work limit. Finish the corpus in the existing staged-output
path before exposing it. The proposed report shape is:

```json
{
  "schema_version": "gnd-guarded-cases/1",
  "model_digest": "sha256:…",
  "rules": [
    {
      "rule_id": "same_area",
      "cases": [
        {"kind": "failing", "population": "cases/0000.fail.json", "binding_count": 1, "verdict": "fail"},
        {"kind": "passing", "population": "cases/0000.pass.json", "binding_count": 1, "verdict": "pass"}
      ],
      "reason": null
    }
  ]
}
```

An unserved rule has an empty case array and a closed reason. Proposed
reasons are `missing-id`, `unsupported-shape`, `antecedent-unreachable`,
`no-failing-case`, `no-passing-case`, and `search-limit`. A missing ID
uses a null ID with its positional reference. Only admit one complete
pair per served rule. Preserve checker/oracle disagreement as quarantine
under exit 6. A written mixed report with some unavailable rules exits 0.
Invalid input exits 3 and a generator invariant failure exits 5.

For mixed models, keep ordinary supported constraints independently
scorable on an explicitly bound scope. The case report identifies the
input model, the scoped model and unavailable guarded expectations.
The existing measure path retains its full-expectation requirement.

## 7. Decisions

| Decision | Proposed contract |
|---|---|
| A | Separate opt-in case manifest. Existing synth behavior keeps its independent full-expectation contract. |
| B | Bound attempts and report a local reason for each unavailable rule. Preserve disagreement quarantine. |
| C | Publish scoped ordinary cases with both digests and an explicit retained positional-reference map. Pin exact corpus paths and consumption before implementation. |

## 8. Tests

Verify matched pass and target fail for all four consequents and both
modalities. Exercise typo-preserving construction, disjoint roles, vacuity,
unsupported guards, exhaustion, oracle/checker disagreement and stable
artifact digests. Verify mandatory and ring cases on the same mixed model
as an unserved guard. Verify existing synth and measure controls under the
default lane. Pin exact focused commands before the spec gate. The
expected bands are 0 for produced pairs and honest partial availability,
3 for malformed input, 5 for generator invariant failure, and 6 for
checker/oracle disagreement. Add a targeted malformed and a known
unreachable antecedent fixture to distinguish refusal from exhaustion.

## 9. Out of scope

Discovery, AMIE import, and replacing author-supplied intent examples.

## 10. Size

Estimate 250–450 runtime lines plus fixtures, schema and focused tests.

## 11. Approval instrument

Approve the exact spec and a small corpus with a separate expected-outcome
key before implementation.
