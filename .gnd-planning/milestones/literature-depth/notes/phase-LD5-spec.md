# LD5 · Verdicts on derived claims

The approved literature-depth plan assigns the final part 8 deliverable.
The prior phase supplies the release, two independently replayable source
supports, the authored occurrence reviews, an observed predicate transition,
and both edition identities. Verify all of these against LD4's final bytes
before freezing the first answer corpus.

## Spec decisions for the implementability sweep

- Reuse the example-level release and public witness/check routes. The core
  judgment wire format continues to address source assertion occurrences.
- Separate the consumer's trusted verdict and its exact claim/support inputs
  from the candidate snapshot. The verifier validates both the supplied
  verdict bytes and the declared population, review and witness bindings.
  A frozen synthetic verdict originates in the fixture and is bound by its
  independently supplied raw digest. A fresh verifier computes only the
  effective support outcome. It does not grant a replacement opinion.
- Bind global claim, decision, rule, resolution and definition identities
  outside any particular support. A changed global dependency requires
  revalidation of all affected supports. Bind individual source occurrence,
  scoped review and witness byte identity to each vote. Verify each support
  independently through LD4, avoiding a whole-release live gate that would
  throw out the still-valid support when its peer goes stale.
- Use the before/after semantic transition verified by LD4. The changed
  definition preserves the asserted occurrence and role values. The original
  receipt and witness both fail against the revised model. A replacement
  pinned receipt and new independently replayed witness restore only the
  reviewed support. Resolution decisions and rules are unchanged in this
  transition. Do not categorize a changed semantic definition as a rule-only
  comparison.
- The current fixture supplies two explicit approvals for one derived
  ancestor target, a package-owned rejection of one exact support, and a
  double rejection. An explicit no-support terminal outcome explains why
  each support was rejected, stale or unavailable. Positive outcomes include
  exactly the still-valid supporting receipts.

## Corpus-first controls

Establish exact supported, one valid, zero valid, and re-reviewed outcomes.
Mutate claim, occurrence, decision bytes, rule, resolution edition and
review freshness separately. Verify definition-change invalidation even
with the same role tuple. Rehash captured data with the replacement claimed
only by the submitting artifact and refuse when it disagrees with the
consumer's independent decision pin. Test duplicate or empty expected
support lists, malformed deeply nested and oversized bounded documents,
bad ordering and untrusted artifact paths. Compare the installed fresh
and replayed example outcomes against the frozen answer corpus.

## Entry points and evidence

Run `gnd.examples.literature.verdict` against the completed LD4 release.
`run RELEASE --out DIR` verifies the five fixture scenarios and captures their
report. `replay RELEASE DIR` recomputes it from the same independently pinned
source opinions. `evaluate RELEASE --case ID [--edition current|revised]`
returns the selected decision and its source-level explanations. The report
distinguishes a supported claim, a completed evaluation with zero support
and a shared binding that requires revalidation. Malformed inputs refuse at
exit 3. The runner and replay return exit 0 for a complete valid demonstration.

Read consumer-pinned opinion bytes before payload selection, with an exact
bounded case and source roster. Bind released claim bytes and actual rule,
decisions, resolution edition, definition and interpretation artifacts locally.
Bind exact occurrence, review and witness identities per source. A stale local
proof leaves the other independently replayed support available. Shared
staleness invalidates all selected opinions for that edition.
The installed LD4 renewed witness showed public witness and replay exit 0
under the revised definition, with the old witness refusing at exit 3.
The separately captured renewed opinion binds those exact bytes. The other
support retains its previous review and is stale in the revised edition.

## Verification

Verify frozen outcomes, mutated bindings, retained replay and hostile
opinion documents. Run the ordinary affected literature and structural
selections, strict component validation and an installed public example.
One separately authorized independent diff review follows verification.
Part 10 remains deferred.

## Review corrections

The [delegated amendment](phase-LD5-amendment.md) binds the revised opinion
fixture. The claim pin covers the declared target and its published proof
status. A separate identity covers the resolution edition carried by the
release, while the decision pin still covers the exact decision artifact.
The current and revised opinions each pin their model bytes. Updating the
published support list consistently leaves the peer support independently
eligible. Zero verified approvals with stale evidence requires revalidation.
The unsupported exit requires that the verified opinions reject both
supports. A missing manifest or incomplete demonstration refuses without
publishing a result. The renewed verification recomputes the pinned rule
from the original and revised models.
