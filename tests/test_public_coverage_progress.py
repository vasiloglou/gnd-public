"""Partial migration accounting cannot masquerade as phase acceptance."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from support.public_migration import (
    MigrationRefusal,
    load_case_map,
    strict_json,
    validate_case_map,
    validate_progress_counts,
)
from support.public_review_storage import migration_view

# Historical migration accounting/storage; current product assertions remain in default tests.
pytestmark = pytest.mark.evidence

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = None


@pytest.fixture(scope="module", autouse=True)
def historical_migration_view():
    # Historical archives must not be loaded by ordinary test collection.
    global MIGRATION
    with migration_view(ROOT / ".gnd-planning/milestones/public-launch/migration") as view:
        MIGRATION = view
        yield
    MIGRATION = None


def reviewed_rows():
    return tuple(row for name in ('b10-private', 'b10-private-mutations', 'b100-live-loopback-http-controls', 'b101-live-local-command-adapter', 'b102-live-local-policy-regressions', 'b103-private-v62-matrix-contract', 'b104-private-v62-retention-publication', 'b105-private-v62-checker-proof-bridge', 'b106-private-v62-publication-partition', 'b107-private-v62-dispatch-corpus-instrument', 'b108-private-v71-installed-corpus-instrument', 'b109-live-inheritance-successor-constants', 'b110-live-aggregate-dispatch-controls', 'b111-live-aggregate-public-corpus-controls', 'b112-live-aggregate-wrong-digest', 'b113-optional-aggregate-near-cap-work', 'b114-live-runtime-fixture-vocabulary', 'b115-private-example-context-routing', 'b117-live-json-giant-totality', 'b118-private-phase-record-cadence', 'b119-private-current-git-helper-instrument', 'b12-inline', 'b12-next10-adapter', 'b12-next11-synth-scope', 'b12-next13-assurance', 'b12-next19-floats', 'b12-next2-scaling-synth', 'b12-next22-redaction', 'b12-next33', 'b12-next38', 'b12-next43', 'b12-report-scaling', 'b12-static57', 'b120-private-helper-duplication-census', 'b121-private-historical-lane-policy', 'b122-live-assurance-cache-controls', 'b13-architecture-inline', 'b13-codegen', 'b13-dependency', 'b13-generated', 'b13-inline', 'b13-private', 'b13-private-runner', 'b13-private-scope', 'b14-corpus-authoring6', 'b14-inline', 'b14-synthetic14', 'b14-synthetic19', 'b14-synthetic19diff', 'b14-synthetic25', 'b14-synthetic26', 'b14-synthetic5recursion', 'b14-synthetic9corpus', 'b15-dynamic', 'b15-next34', 'b15-next4', 'b15-next6', 'b15-private-attack18', 'b15-private-census6', 'b15-private-development5', 'b15-private-nonvacuity9', 'b15-private-registry-identity4', 'b15-provenance2', 'b15-shape3', 'b16-adversarial46', 'b16-api14', 'b16-architecture27', 'b16-batch21', 'b16-coverage40', 'b16-external19', 'b16-import22', 'b16-inline16', 'b16-model30', 'b16-offline30', 'b16-private-instrument23', 'b16-publication6', 'b16-reference1', 'b16-review32', 'b16-skills32', 'b16-solve-successors6', 'b16-solve53', 'b16-transition15', 'b16-witness16', 'b17-comparison5', 'b17-counting6', 'b17-coverage5', 'b17-disjunctive7', 'b17-feedback4', 'b17-json2', 'b17-mandatory8', 'b17-ring8', 'b17-session23', 'b18-adapter10', 'b18-applicability4', 'b18-bridge9', 'b18-comparison2', 'b18-partition9', 'b18-set10', 'b19-evaluator5', 'b19-pyrel-contract8', 'b19-pyrel11', 'b20-evidence-reader6', 'b20-private-currency6', 'b20-private-runner3', 'b20-private-sources4', 'b20-report6', 'b20-runtime-identity2', 'b21-inheritance1', 'b21-private-citation6', 'b21-private-inherited-comparison6', 'b21-private-inherited-writer3', 'b21-private-matrix6', 'b21-private-retention2', 'b21-private-sandbox-hardening6', 'b22-private-corpus-receipt3', 'b22-private-mutations4', 'b22-private-release-builder5', 'b22-release-reader4', 'b23-private-branch61-2', 'b23-private-branch62-3', 'b23-private-evidence61-3', 'b23-private-evidence62-2', 'b23-private-limits2', 'b23-private-matrix61-5', 'b23-private-walk5', 'b24-private-legacy-proof4', 'b24-private-mandatory-refinement7', 'b24-private-mixed-closure5', 'b24-private-modular-closure3', 'b24-private-mutations2', 'b24-private-nagini-provider2', 'b24-private-private-seats3', 'b24-private-scaling2', 'b25-private-profiles3', 'b25-private-published-proof3', 'b25-private-refinement4', 'b26-private-currency5', 'b26-private-distribution2', 'b26-private-recert61-1', 'b26-private-recert62-1', 'b26-proof-isolation2', 'b27-private-basis6', 'b27-private-corpus6', 'b27-private-legacy3', 'b27-private-scaling1', 'b28-private-corpus9', 'b28-private-replay15', 'b287-integrated-reviewed-metadata', 'b29-private-closure1', 'b29-private-manifest4', 'b29-private-replay16', 'b29-private-witness5', 'b294-integrated-reviewed-metadata', 'b295-private-installed-harness', 'b3-extra', 'b3-initial', 'b3-reviewed', 'b30-policy1', 'b30-private-finite1', 'b30-private-inheritance4-2', 'b30-private-inheritance5-1', 'b30-private-isolation2', 'b30-private-recert2', 'b30-private-skills1', 'b308-architecture-book-publication', 'b31-contract3', 'b31-private-cache1', 'b310-planning-frontmatter-local', 'b313-semantic-foundation-local', 'b314-phase4-selectors', 'b32-private-accounting', 'b32-private-branch', 'b32-private-comparator', 'b32-private-contract', 'b32-private-matrix', 'b32-private-record', 'b326-preferred-five', 'b329-admission-ir', 'b33-private-artifacts5', 'b33-private-manifest4', 'b334-adapter-dimension-mutants', 'b335-transition-scaling-optional', 'b338-current-campaign-instruments', 'b34-private-assurance4', 'b34-private-v4contract', 'b342-coverage-goldens', 'b347-private-instruments45-49', 'b35-private-source5', 'b35-private-stories3', 'b356-private-instruments50-52', 'b36-optional-witness11', 'b361-private-instruments53-55', 'b361-public-json-boundary', 'b365-private-instruments56-58-61-80', 'b367-public-v71-full-judgments', 'b367-public-v71-phase4-corpus', 'b367-public-v71-successor-guards', 'b37-adapter6', 'b370-public-v71-phase4-full450', 'b371-public-source-case-01710', 'b371-public-source-case-02320', 'b371-public-source-case-04806', 'b371-public-source-case-04829', 'b371-public-source-case-04846', 'b371-public-source-case-04889', 'b38-cost3', 'b39-execution8', 'b4-artifacts', 'b4-core', 'b4-population', 'b4-synth', 'b4-transition', 'b40-feedback6', 'b40-transport4', 'b41-private-cleanliness1', 'b41-private-map3', 'b41-private-setup3', 'b43-private-correspondence2', 'b43-private-evidence5', 'b43-private-guarded5', 'b43-private-installed2', 'b44-private-answerinstrument1', 'b44-report1', 'b45-classification3', 'b45-optional-opaque1', 'b46-private-fm01', 'b47-private-recertification-corpus', 'b47-private-v71-planning', 'b48-feedback-surfaces', 'b49-private-phase1-runner', 'b5-codegen', 'b5-install-conformance', 'b5-terms', 'b50-production-trace', 'b51-walk-floor', 'b52-private-derivation-corpus', 'b53-aggregation-admission', 'b54-private-phase1-corpus', 'b54-private-phase2-corpus', 'b55-private-planning-registry', 'b56-private-planning-corpus', 'b57-private-evidence-binding', 'b58-generated-dependencies', 'b58-report-digest-pairing', 'b59-private-source-corpus', 'b6-doctor', 'b6-recovery', 'b6-reports', 'b6-sessions', 'b60-private-phase4-corpus', 'b60-private-phase5-corpus', 'b61-private-symbol-pins-0', 'b61-private-symbol-pins-1', 'b61-private-symbol-pins-2', 'b61-private-symbol-pins-3', 'b61-private-symbol-pins-4', 'b61-private-symbol-pins-5', 'b61-private-symbol-pins-6', 'b61-private-symbol-pins-7', 'b63-private-phase1-proof', 'b63-private-phase2-proof', 'b63-private-proof-processes', 'b63-private-transition-formal', 'b64-private-correspondence-publisher', 'b65-live-evidence-origins', 'b66-private-aggregate-dispositions', 'b66-private-transition-matrix', 'b67-live-policy-cases', 'b68-live-admission-schema', 'b69-private-plan-discipline', 'b7-private', 'b7-reference', 'b70-live-frontmatter-declarations', 'b71-private-identity-migration', 'b73-private-transition-source-pins', 'b74-live-transition-contract', 'b75-live-transition-review-controls', 'b76-live-session-driver', 'b77-live-walk-floor-contract', 'b78-private-composition-corpus', 'b78-private-judgment-corpus', 'b78-private-term-corpus', 'b79-live-composition-digest-1', 'b79-live-composition-digest-3', 'b8-direct', 'b8-expanded', 'b80-private-installed-instrument', 'b81-live-lean-export-successors', 'b82-optional-lean-successors', 'b83-live-derivation-evaluator-controls', 'b84-private-derivation-corpus-identity', 'b85-private-recertification-contract', 'b86-live-patch-publication-identity', 'b87-optional-pyrel-constraint-oracle', 'b88-private-v3-recertification-contract', 'b89-live-souffle-successors', 'b9-fixes', 'b9-launcher-existing', 'b9-portable', 'b9-updater', 'b90-live-souffle-input-contract', 'b91-private-souffle-corpus-instrument', 'b92-live-adapter-literal-controls', 'b93-live-adapter-primitive-controls', 'b94-live-adapter-structural-controls', 'b96-private-adapter-census-selection', 'b97-live-adapter-reference-opaque-controls', 'b98-live-emitter-trust-controls', 'b99-live-local-adapter-policy')
                 for row in load_case_map(MIGRATION / f"{name}-case-map.jsonl.gz"))


def private_policy():
    policy, = load_case_map(MIGRATION / "retained-private-policy.json.gz")
    return policy["originals"]


def original_identities():
    raw = (MIGRATION / "original-identities.json").read_bytes()
    progress = strict_json((MIGRATION / "progress.json").read_text())
    assert hashlib.sha256(raw).hexdigest() == progress["original_identities_sha256"]
    originals = strict_json(raw.decode())
    assert len(originals) == 5331
    assert set(originals) == {f"source-case-{index:05d}" for index in range(5331)}
    return originals


def test_partial_slices_refuse_complete_original_accounting():
    rows = reviewed_rows()
    originals = original_identities()
    selected = {node for row in rows for node in row["target_nodes"]}
    with pytest.raises(MigrationRefusal, match="missing-original"):
        validate_case_map(rows, originals=originals, collected=selected, retained_private=private_policy())


def test_progress_retains_unresolved_cases_and_refuses_handoff():
    rows = reviewed_rows()
    originals = original_identities()
    progress = json.loads((MIGRATION / "progress.json").read_text())
    assert len(rows) == len({row["source_node"] for row in rows}) == 5067
    assert {row["source_node"] for row in rows} <= set(originals)
    validate_progress_counts(progress, rows, original_count=len(originals))
    assert progress["reviewed_dispositions"] == len(rows)
    assert progress["unresolved_definitions"] == len(originals) - len(rows) == 264
    assert progress["status"] == "incomplete"
    assert progress["handoff_authorized"] is False
    collection, = load_case_map(MIGRATION / "collection.json.gz")
    selected = {item["node"] for item in collection["selected"]}
    observed = selected | {item["node"] for item in collection["deselected"]}
    assert all(set(row["target_nodes"]) <= selected for row in rows
               if row["selection"] == "default")
    validate_case_map(rows, originals={row["source_node"]: originals[row["source_node"]]
                                     for row in rows}, collected=observed, retained_private=private_policy())


def test_static_target_selectors_resolve_to_actual_test_definitions():
    import ast
    definitions = {}
    for row in reviewed_rows():
        for node in row["target_nodes"]:
            relative, name = node.split("::", 1)
            name = name.split("[", 1)[0]
            if relative not in definitions:
                tree = ast.parse((ROOT / relative).read_text())
                definitions[relative] = {item.name for item in tree.body
                                         if isinstance(item, ast.FunctionDef)}
            assert name in definitions[relative]
