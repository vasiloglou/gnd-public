# LX4 · extraction and checking roots for literature evidence

Status: delegated approval (auto=true), 2026-11-15. See [010](../010-phase-LX4-spec-gate.md). The prerequisite is the [LX3 result](../009-phase-LX3.md).

## Obligations

| Source | Requirement | Evidence |
|---|---|---|
| LX4.a | Two separately identified roots pin the same two vocabulary files and catalog. Extraction verification precedes source rebinding. The checking root evaluates an added temporal clause. | T1, T2, T4 |
| LX4.b | Run optional publication-order advice using the LI5 path policy and a separate table of work dates. Include 2026 to 2019, equality and the rejected PINNs to Bayesian PINNs candidate. Preserve check and proof results when advice is omitted. | T6, T7 |
| LX4.c, plan links | One example chains actual extraction, authenticated rebind, catalog-assisted resolution, composition, check, witness and replay. The manifest verifier independently checks links. Apply the plan's unsupported-combination table. | T1, T3–T5, T8 |
| LI1 carryover | Run fidelity over the very same extracted populations, extraction sidecars and document bytes. Measure additional materialized copies by artifact kind. | T9 |
| LI5 | Use its public lineage relation policy and fixtures only. Claim neither a new semantic admission nor a reserve measurement. | T6 |
| Plan §§0, 5, 7, 9, 10 | Apply the recorded rule set, document the model split and the advisory route, retain isolated exit bands, run the selected tests, decide X2 and X4. | Design, decisions and gates |

## Standing rules

- **Totality.** Bound example JSON and subprocess work with existing cap and timeout helpers. Strictly parse closed records and fail with input exit 3 on bad or changed evidence before publishing a verified integration manifest.
- **Input-bounded work.** Read a bounded snapshot per manifest coordinate. Use indexed work IDs for date resolution and one source pass for rebind verification.
- **Validation order.** Validate input shape and expected bindings, authenticate both roots and extraction index, verify source evidence and rebinds, then rederive composition before checking or running the advisory report. Parse certificate shape before catalog and proof claims in the product replay route. Test an invalid rebind together with a control that would fail the temporal clause.
- **One policy walk.** The resolver, artifact-index verifier, source-anchor binder, LI2 route and replay kernel own their existing checks. The example walks one rebind definition and uses LI5's path policy at the advisory boundary.
- **One normative home.** Document the model split and rebind in the documents guide, and the optional date contract in the example. Cross-link to the existing composition, fidelity, proof and pathway contracts.
- **Measure representation.** Test actual bytes and surfaced exit codes. The shared evidence layout reports physical materialization and path aliases separately.

## Design trajectory

| Capability | Existing home | Use |
|---|---|---|
| Pinned model concepts and root snapshot | Model includes and LX1 projection | Two standalone vocabulary files shared by two authored roots. Root identities are independently bound. Include resolver validates each pin. |
| Source extraction and header provenance | `gnd extract`, `gnd verify`, the extraction artifact-index verifier | Execute the installed public routes. The fixture provides deterministic saved fact responses for actual source documents. Generate the population header from the extraction artifact index. Bind the extraction sidecar and source spans. |
| Source rebind | Existing population wire, anchor binder and canonical JSON | Change header coordinates for the checking root. Rebind sidecar population digest to precisely those bytes. Require matching pinned vocabulary/catalog identity and equal shape-address vocabulary before allowing the transfer. |
| Catalog and checking | `gnd compose`, `gnd check --composition --sources` | Candidate alias renames to a catalog identity. Exact re-derived candidate source evidence precedes checks. Temporal guarded date_add uses the current evaluator. |
| Fidelity and artifact naming | `gnd fidelity`, `gnd.extract.service` | Let the fidelity route reuse the authenticated flattened bundle for this rooted input. Preserve the unsupported-route refusal when an authored include has no trusted indexed bundle. Preserve its existing matching and census. Use one shared per-document directory and materialize both required document names. |
| Date policy | LI5 `lineage/path-policy.json` | Use the existing chainable and non-chaining relationship vocabulary. Sidecar edge rows name work IDs independently of method labels. The rejected candidate is present only in the proposals. |
| Finite proof | `gnd witness` and `gnd replay` | Prove an asserted candidate target and a catalog occurrence using the same checking-model record. LX3 already exercises a single derived proof joining both types. |

The extraction root may declare plain Date roles. The checking root adds a
guarded ordering clause comparing submitted date plus one day to published
date. It also adds a catalog membership rule if the source alias needs
resolution before it can be evaluated. The static model-ID, shape and catalog
checks precede rebind. Use a catalog population with no model_id so the exact
file is valid for both pinned roots.

## Public fixture and wire

- `python -m gnd.examples.literature.interop run --out RUN [--dates]`
  runs the integrated fixture with a bounded local CLI. Use a stable run-relative
  coordinate for each output that includes a path. An atomic run directory
  makes partial work recognizable. Both original authored roots, pinned
  reference files, vocabulary files, and input fixture evidence remain
  identifiable.
- `python -m gnd.examples.literature.interop verify RUN`
  re-authenticates the exact input/output digests, recomputes rebinds,
  re-derives composition, reruns check and replays the retained witness.
  All rebind validation precedes semantic checking or advice.
- `python -m gnd.examples.literature.interop dates RUN [--out REPORT]`
  checks the run binding and emits a separate result. When run includes
  `--dates`, the integration manifest binds that same result and inputs.

Rebind record, canonical JSON `literature-rebind/1`: `schema`, `source`,
`extraction_root_sha256`, `checking_root_sha256`, `includes` (id, sha256),
`references` (id, raw_sha256), `artifact_index_sha256`, `document_sha256`,
`extraction_population_sha256`, `extraction_sidecar_sha256`,
`extraction_anchors_sha256`, `rebound_population_sha256`,
`rebound_anchors_sha256`. Digest fields use the unprefixed raw SHA-256.
One verifier recomputes the canonical record and both artifacts from
the authenticated extraction and the checking root.

Integration record, canonical JSON `literature-interop/1`: root and
artifact index digests, per-source rebind digests, resolution/manifest digest
as applicable, composed population and record digests, check, proof, replay
and fidelity digests, verified layout counts, and optional advice inputs and
report digest. Re-derive each dynamic binding before accepting the result.
The semantic check carries the composition record digest and catalog roster.

Advisory uses `literature-publication-dates/1` rows
`{work, role, precision, value}` and a `literature-candidate-edges/1` set of
`{id, relation, descendant_work, ancestor_work}`. The eligible predicates
come directly from LI5's public path policy. In `literature-date-advice/1`,
each row names both works, roles/status and known dates; rows have `pass`,
`advisory` or `unresolved` and explicit reason where needed. Exact matching
year precision is in scope. Equal years at like precision pass; missing
work links, missing/alternative-role dates, conflicting dates and mixed
precision are unresolved. Duplicate identical dates do not introduce
conflict. Non-chainable data is outside the denominator. The report binds
raw edge, date and policy digests. Use PINNs work `doi:10.1016/j.jcp.2018.10.045`
and Bayesian PINNs work `doi:10.1016/j.jcp.2020.109913`, publishing years
2019 and 2021 as specified by issue #193. Synthetic 2026 and same-year
controls have clearly synthetic identifiers. Dates are evidence for this
advisory only.

The fidelity case uses `document.md`, `source.population.json`,
`document.manifest.json`, `extracted.population.json` and
`extracted.population.extraction.json`. Composition reads the same document bytes at its required per-source `document.txt` name. Its `population.json` and
`population.json.anchors.json` carry the checking coordinates and therefore
have distinct bytes. Count the additional inodes by route across the fixed
source roster and verify both readers access the same document bytes.
Use independent saved expected facts for the fidelity source populations.

## Decisions to record

| ID | Decision | Ruling |
|---|---|---|
| D1 | Rooted example with two checking-bound digest-verified sources. The concrete temporal guard is separate from the example’s publication-order advice. | Delegated (auto=true) |
| D2 | Root and rebind record fields above bind the example and have no production publication semantics. | Delegated (auto=true) |
| D3 | Publication-year comparison uses LI5 chainable predicates and saved proposed work IDs. Report statuses do not enter check or replay. | Delegated (auto=true) |
| D4 | Reuse the authenticated-flat bundle for fidelity and count actual physical copies. Preserve legacy fidelity inputs. | Delegated (auto=true) |
| D5 | Corpus-first with a separate expected wire and exit file. Phase diff has its separate independent review gate. | Delegated (auto=true) |

## Corpus

| ID | Expected |
|---|---|
| T1 | Installed routes extract, verify every source, rebind, compose, check, witness, replay and fidelity exit 0. Each source lineage remains candidate only. |
| T2 | A positive check has its added temporal verdict pass. A separately valid checking root with a larger allowance over the same dates yields temporal failure exit 1. Extract against checking root exits 3 with `temporal:consumer-unsupported`. |
| T3 | Rebind carries the same include/file and catalog ID/hash sets. Both resolved roots have independently bound authored hashes and distinguishable population header identities. |
| T4 | Mutate each rebind component independently. Exit 3 for a stale record, either root, include pin, extraction index, document, old population, extraction or anchor sidecar or rebound source. Pair it with a temporal-failure input to establish refusal before evaluation. Separately valid roots with different pins or catalog refuse fresh rebind. |
| T5 | Fresh check plus replay accept stored output. Stale population, resolution evidence, record or witness, and falsified manifest with repinned report, refuse at the corresponding boundary. |
| T6 | 2026 to 2019 plus equal year pass, 2019 to 2021 is the single advisory, unrelated unresolved/conflict/missing/mixed/alternative cases are named. The non-chainable control does not enter the census. |
| T7 | Compare with dates omitted using exact check signature, violation totals and witness/replay. Forge the report's dates input under fixed bindings and refuse. |
| T8 | Validate include forbidden nesting/reference/unattended, direct unrooted witness and explicit overrides by reusing LX1–LX3 public controls. Keep catalog outside candidate-only extraction data. |
| T9 | Fidelity runs both cases and scores expected rows against the original extract. Check shared layout identities and added file census. A forged flattened bundle or index fails fidelity. |

Initial direct/focused selection: LX4, LX1–LX3, LI5 lineage, public temporal
counterexamples, composition example, applicable fidelity and model include
guards, replay/proof and schema consumers. Project structure, scoped and
whole-tree Ruff, strict component check and installed package data controls.
Full and historical lanes follow their documented selection.

## Implementability seen

A scratch version of the two roots used the same Date vocabulary and catalog,
but different model IDs. Vocabulary digests were equal. Extraction passed on
the first and refused on the temporal root. On the checking root, compose,
check, witness v4 and replay each passed. Increasing only the guarded allowance
made check fail with one temporal violation. The saved LI1 layout currently
copies raw documents into a fidelity directory. Fidelity itself already checks
both sides of the digest chain but its current command has an include guard
before the indexed bundle reader. Rooted fidelity must re-enter through that
same authenticated bundle.

An exact LI2 same decision over two candidate anchor spans also composed with
the pinned LX3 catalog. Both candidate lineage entries stamped decision 0.
Use the corresponding alias and catalog key in the literature fixture.
Source coordinates and input digests come from the rebound stage. Its
identity decision comes from the separately authored fixture.

The fidelity implementability probe ran original-root extraction and verify
with real source-anchor files successfully. The predecessor fidelity
guard refused the include root. Running the existing matcher after letting
observation continue past that guard returned 0 on the original extraction
and document files. Rooted fidelity should get these inputs only through
the existing authenticated indexed bundle; the probe patched the guard
only in memory.

Use the issue's specific PINNs and Bayesian PINNs works with published-volume
years (2019 and 2021). Source the edge from issue #193 and the two work IDs
from https://doi.org/10.1016/j.jcp.2018.10.045 and
https://doi.org/10.1016/j.jcp.2020.109913. Keep the fictional 2026 control
separately identified.

Using the existing publisher, co-locate fidelity and
composition in the same source folder. The publisher preserves file bytes
but materializes both filename leaves, so this option adds one document
copy per source. Count it directly. The original extraction population and
extraction sidecar are shared by extraction verification and fidelity.
The checking population and source anchors are separate rebind outputs.
The example verifies both readers and measures the copying cost.

The fixture includes a digest-bound LI2 same decision connecting the two
candidate name variants. It uses the asserted candidate and a fixed-catalog
base target at the integrated proof boundary. LX3 separately exercises a
derived proof joining those origin kinds. The rebind materializes candidate
headers only. Temporal checking uses a grounded date_add clause and a
mutated allowance control. The optional date route uses the public LI5
chainability policy without adding the rejected PINN edge to candidate facts.

| Gate | Command |
|---|---|
| Direct and focused | `uv run pytest -q tests/test_lx4_literature_interop.py tests/test_lx1_flattening.py tests/test_lx2_witness_flattening.py tests/test_lx3_catalog_composition.py tests/test_li5_lineage.py tests/test_public_temporal_canonical_counterexamples.py tests/test_composition_example.py tests/test_mc1_guards.py tests/test_extract_manifest.py tests/test_verify_cli.py tests/test_fidelity_payload.py tests/test_fidelity_stub_gate.py tests/test_public_fidelity_scope.py tests/test_packaged_skills.py --tb=short` |
| Structure | `uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short` |
| Lint and components | Whole-tree Ruff with the exact inherited diagnostic comparison, changed-file Ruff and the strict component check based on `d523c14d`. |
| Cadence | Default filters apply. Broad and historical lanes follow their separate triggers. |

## Candidate verification

The packaged run exits 0 for extraction, both source verifies, composition,
temporal check, witness, replay, fidelity and advisory report. The read-only
verification reruns the source, checking, proof and fidelity boundaries.
The added temporal rule passes. The larger allowance control exits 1 and
reports a guarded failure. The supported extraction root can use plain Date
roles. Extraction of the temporal checking root exits 3.

The comparison without advice preserves composition, checking, witness and
replay bytes. The advice contains two passes, one PINN advisory and five
unresolved chainable proposals. The non-chainable proposal stays outside
the census. Both fidelity cases ran. The layout has two additional document
materializations and zero additional original extraction population or
extraction-sidecar materializations. The checking rebind adds two populations
and two anchor files. The provenance controls refuse forged rebinds, altered
advice, an independently valid alternate witness target, and a catalog or
input checksum change.

A control initially accepted a failed fidelity case with a re-pinned
report. The example now requires the census to include both scored sources.
The expanded guard selection also exposed a predecessor null-model
composition guard regression. The raw include guard runs again before
composition verification for that case. The packaged include inventory
adds exactly the two new roots and loads all named entries.

```sh
uv run pytest -q tests/test_lx4_literature_interop.py tests/test_lx1_flattening.py tests/test_lx2_witness_flattening.py tests/test_lx3_catalog_composition.py tests/test_li5_lineage.py tests/test_public_temporal_canonical_counterexamples.py tests/test_composition_example.py tests/test_mc1_guards.py tests/test_mc2_consumers.py tests/test_extract_manifest.py tests/test_verify_cli.py tests/test_fidelity_payload.py tests/test_fidelity_stub_gate.py tests/test_public_fidelity_scope.py tests/test_packaged_skills.py --tb=short
uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short
```

    346 passed in 63.67s (0:01:03)
    679 passed, 2 deselected in 106.29s (0:01:46)

The affected MC2 consumers join the focused command for the composition
guard correction. Scoped Ruff and the strict component gate pass. Whole-tree
Ruff retains the same 188 diagnostics by file, line, code and message.
The offline wheel build contains all 18 interop modules, fixture files
and the reused LI5 policy. The example and its read-only verification both
exit 0 using the wheel installed into a separate environment with the
existing locked dependency directory.

Independent phase diff review is pending.
