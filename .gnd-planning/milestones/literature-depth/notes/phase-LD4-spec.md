# LD4 · Semantic revision and release evidence

The [approved plan](literature-depth-plan.md#ld4--semantic-revision-and-current-release-evidence)
assigns issue #193 part 8 criteria 1–7 to this phase. LD1 supplies the
source-scoped example pattern. LD3 supplies typed coverage, measured fidelity
and the dependency-key worklist. LI2 supplies verified composition and sense
resolution, LI4 supplies saved assertion-review semantics, and LI5 supplies
independently replayable ancestor witnesses. Part 10 stays deferred.

## Decisions

| ID | Contract |
|---|---|
| D1 | Put the fixture workflow in `gnd.examples.literature.revision`. A `run READING_RUN --out DIR` publishes separate `before` and `after` directories in a new root. Both retain their own source, model, assertion review, population, composition, witness, claim and policy-bound manifest. A bounded `status` reports changed artifact and dependent identities. `replay DIR` recomputes the public routes from retained inputs. `replay DIR --snapshot before` independently verifies the original witness and reading evidence even when the new release is unavailable. Exit 0 establishes the requested current result. Exit 3 identifies an incomplete, stale or invalid selection. |
| D2 | The consumer selects a policy and SHA-256 independently from each release manifest. The policy controls exact artifact paths, kinds, cardinalities and dependency edges. A release manifest supplies only the policy identity, snapshot identity and one SHA-256 per exact artifact path. Validate the trusted policy and its closed graph first, the candidate roster second and bounded raw evidence third. Traverse the graph once to propagate direct changes. |
| D3 | Use the original public W-flat and W-resolved source bundles. Compose and check each release and witness the same five targets. OpenCap Monocular→VampNet, OpenCap Monocular→DMD and WHAM→DMD are the three cross-sense paths that the identity split removes. OpenCap Monocular→WHAM and VampNet→DMD remain proved. Independently replay the original witness and keep its snapshot reproducible after migration. |
| D4 | Join composition record fact occurrences by source ID, original fact type and original fact index. Use canonical resolution decisions for role rewrites. A historical mention of WHAM with no source occurrence has two possible senses and enters the rereading list. Re-derivation detects a forged migration map even if candidate checksums have been updated. |
| D5 | Verify the LD3 run before admitting stronger absence. Keep its exact stages, typed coverage, closure, scope and qualifying fidelity with the release. Use LD3's worklist over the same opened sections and changed vocabulary key. Compare the preview with the actual LD3 revisit. The covered absence becomes stale and its earlier range enters rereading. Keep the separately declared unrelated coverage current. |
| D6 | A public reviewed evolve transaction changes the asserted ancestry predicate's reading with unchanged fact roles and source population. Additive preview refuses. Ordinary preview and exact reviewed apply succeed. Definition digests bind review receipts, so the old review is stale and a review of the new definition can replace it. Bind the canonical LI2 resolution edition and exact rule artifact separately. A separate unchanged-vocabulary fixture exercises rule-only edition comparison. |
| D7 | Retain two source-qualified certificates for one legitimate ancestor claim, including an explicitly labelled synthetic independent corroborating source. Each certificate must pass public witness and independent replay, carry its own source occurrence and current review identity, and bind both edition identities. LD5 can invalidate these support identities separately. |

## Standing rules

- Authenticate policy bytes before candidate parsing. Require exactly the
  independent policy roster and a closed acyclic graph before payload use.
  Test combined omission, duplicate or empty candidate rows, invalid policy
  pins, oversize inputs, untrusted paths and hostile JSON.
- Read bounded regular files from rooted snapshot directories. Bound graph
  nodes and total edges. Use one graph walk for all artifact kinds. A timed
  hostile roster covers the layer's input cost.
- Compare actual public proof and replay outcomes before and after the split.
  Compute occurrence movements from composition records and the scope
  worklist from the authenticated LD3 inputs. The packaged fixture README
  owns the workflow invocation and manifest vocabulary. Public route contracts
  continue to own their outputs.

## Corpus-first controls

| ID | Observable acceptance |
|---|---|
| T1 | Fresh and replay produce the exact query roster, three lost and two preserved proofs, and the same original witness identity. |
| T2 | Changing each required artifact kind independently stales its transitive dependents and leaves unrelated evidence current. Missing coverage with an identically edited candidate roster, duplicate and empty inventories each refuse. |
| T3 | Invalid policy pins fail before candidate interpretation. Hostile JSON, overlong relative paths, symlinks and excessive graphs refuse within the reader budget. |
| T4 | Source-qualified occurrence mappings reflect the actual records; source-free WHAM yields both choices and a reread entry. A rehashed forged map fails semantic replay. |
| T5 | Compare worklists for one actual LD3 vocabulary key. Affected coverage is stale, unrelated coverage is current and both original claim and reading evidence remain replayable. |
| T6 | Observe additive preview exit 3, ordinary preview and reviewed apply exit 0, stale review despite unchanged occurrence, a successful replacement review and a separate rule-only comparison. |
| T7 | Individually replay both support certificates for the handoff, with distinct source coordinates and current reviews. |
| T8 | Run affected focused and structure gates, strict component validation and a standalone installed example. Retain one separately authorized independent phase diff review. No optional spec panel is selected. |

## Implementability sweep

The public whale probe composed both snapshots, returned five and two proofs
respectively and replayed the original witness at exit 0. The composition
record carries original source occurrence coordinates. A separate local
evolution probe preserved roles and verified the additive refusal and exact
ordinary apply. A separate rule-only probe over the same vocabulary and
population returned one head-only violation. LD3 already exposes its bounded
replay and shared section selection. A second authored same-fact source is
admissible as an ordinary independent source bundle. These probes inform the
frozen corpus and carry no review or release authority.

## Review corrections

The after manifest records raw pins for the prior composition and population.
The policy graph follows the actual producers from source resolution to
canonical decisions and from evolution proposal to evolved model. The two
single-source certificates share the verified resolution edition and exact
rule without depending on each other's source files. The migration computes
coverage invalidation from actual changed occurrences and uses the existing
LD3 section-selection rule for the affected key.

The workflow retains the old reading sources, model inputs and saved review
inputs in both snapshots. Their trusted pins allow prior replay after the
packaged source is unavailable. A scope review also pins its interpretation
policy, so a new candidate manifest cannot transfer old consent. The public
rule-edition comparator rejects a changed vocabulary. The additive preview
control identifies the exact predicate-reading operation.
