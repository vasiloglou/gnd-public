# Compatibility shims

All RF2 shims stay at least until the first public release after RF6; retirement
requires a separately approved phase (RF-D5, owner ruling 2026-10-05).
Nested hook names were never importable: their containing readers remain the
compatibility boundary. Both duplicate-hook variants remain distinct.

| Old name | New home | Phase | Retirement |
|---|---|---|---|
| gnd.conformance.report.canonical | gnd.artifacts.canonical_report_text | RF2 | RF-D5 |
| gnd.coverage.canonical_payload | gnd.artifacts.canonical_report_text | RF2 | RF-D5 |
| gnd.fidelity.report.canonical | gnd.artifacts.canonical_report_text | RF2 | RF-D5 |
| gnd.assurance_evidence._sha | gnd.artifacts.sha256_hex | RF2 | RF-D5 |
| gnd.diff._digest | gnd.artifacts.sha256_hex | RF2 | RF-D5 |
| gnd.install._sha256 | gnd.artifacts.sha256_hex | RF2 | RF-D5 |
| gnd.recovery.verify._sha256 | gnd.artifacts.sha256_hex | RF2 | RF-D5 |
| gnd.review.request._reject_duplicate_object_pairs | gnd.artifacts.reject_json_duplicate_pairs | RF2 | RF-D5 |
| gnd.recovery.report.Sha256 | gnd.artifacts.Sha256 | RF2 | RF-D5 |
| gnd.exp.session_eval.Sha256 | gnd.artifacts.Sha256 | RF2 | RF-D5 |
| gnd.exp.session_store.Sha256 | gnd.artifacts.Sha256 | RF2 | RF-D5 |
| gnd.extract.manifest._validation_issues | gnd.model.issues_from_validation_error | RF2 | RF-D5 |
| gnd.exp.spec._validation_issues | gnd.model.issues_from_validation_error (bound SPEC_RULE_ID) | RF2 | RF-D5 |
| gnd.exp.conclusions._validation_issues | gnd.model.issues_from_validation_error (bound CONCLUSIONS_RULE_ID) | RF2 | RF-D5 |
| gnd.conformance.currency.model_digest | gnd.conformance.currency.model_file_sha256 | RF2 | RF-D5 |
| gnd.conformance.service.model_digest | gnd.conformance.currency.model_file_sha256 | RF2 | RF-D5 |
| gnd.synth.provenance.model_digest | gnd.synth.provenance.validated_model_sha256 | RF2 | RF-D5 |
| gnd.transition.model_digest | gnd.transition.transition_model_identity | RF2 | RF-D5 |
| gnd.coverage.model_digest | gnd.transition.transition_model_identity | RF2 | RF-D5 |
| gnd.cli.EXIT_GENERATOR | gnd.exits.EXIT_GENERATOR | RF2 | RF-D5 |
| gnd.cli.EXIT_QUARANTINE | gnd.exits.EXIT_QUARANTINE | RF2 | RF-D5 |
| gnd.cli.EXIT_CHECKER_DEFECT | gnd.exits.EXIT_CHECKER_DEFECT | RF2 | RF-D5 |
| gnd.cli.EXIT_DRIFT | gnd.exits.EXIT_DRIFT | RF2 | RF-D5 |
| gnd.cli.EXIT_COLLISION | gnd.exits.EXIT_COLLISION | RF2 | RF-D5 |
| gnd.cli.EXIT_NO_INSTALL | gnd.exits.EXIT_NO_INSTALL | RF2 | RF-D5 |
| gnd.cli.EXIT_MODEL_CODE_DRIFT | gnd.exits.EXIT_MODEL_CODE_DRIFT | RF2 | RF-D5 |
| gnd.cli.EXIT_SESSION_NOT_ACCEPTED | gnd.exits.EXIT_SESSION_NOT_ACCEPTED | RF2 | RF-D5 |
| gnd.cli.EXIT_REVIEW_INCONCLUSIVE | gnd.exits.EXIT_REVIEW_INCONCLUSIVE | RF2 | RF-D5 |
| gnd.cli.EXIT_EVOLUTION_OPERATIONS_GATED | gnd.exits.EXIT_EVOLUTION_OPERATIONS_GATED | RF2 | RF-D5 |
| gnd.conformance.service._EXIT_ILL_FORMED | gnd.exits.EXIT_ILL_FORMED | RF2 | RF-D5 |
| gnd.conformance.service._EXIT_MODEL_CODE_DRIFT | gnd.exits.EXIT_MODEL_CODE_DRIFT | RF2 | RF-D5 |
| gnd.conformance.service._EXIT_NO_INPUT | gnd.exits.EXIT_NO_INPUT | RF2 | RF-D5 |
| gnd.conformance.service._EXIT_IO | gnd.exits.EXIT_IO | RF2 | RF-D5 |
| gnd.solve._EXIT_OK | gnd.exits.EXIT_OK | RF2 | RF-D5 |

Nested boundaries: declared_adapter._bundle_rows → reject_json_constant and
reject_json_duplicate_pairs; exp.adapter_policy._strict_document and
exp.session_eval._strict_object → reject_json_constant and
reject_json_duplicate_pairs_result; exp.session_store._strict_object_bytes →
reject_json_constant and reject_json_duplicate_pairs. Reader signatures and
exception boundaries do not change. The old nested functions have no shim.

Patch migration: tests/test_conformance_payload.py patches
conformance.service.model_file_sha256, the real consumer lookup. Its exception
is observed through build_conformance. Source hash/import-scan scopes cover both
original consumers and the new existing homes (artifacts, model, exits).

| gnd.checker._PHASE3_LEGACY_CHECK | gnd.checker.check_legacy | RF3 | RF-D5 |
| gnd.checker._PHASE3_LEGACY_EVALUATE_DERIVATIONS | gnd.checker.evaluate_derivations_legacy | RF3 | RF-D5 |
| gnd.checker._PHASE3_LEGACY_CONSTRAINT_VIEW | gnd.checker.constraint_view_legacy | RF3 | RF-D5 |

## RF3 move units

| gnd.model.ModelLoadError | gnd.errors.ModelLoadError | RF3 | RF-D5 |
| gnd.model.ValidationIssue | gnd.errors.ValidationIssue | RF3 | RF-D5 |
| gnd.model.issues_from_validation_error | gnd.errors.issues_from_validation_error | RF3 | RF-D5 |
| gnd.model.ModelValidationError | gnd.errors.ModelValidationError | RF3 | RF-D5 |
| gnd.population.PopulationLoadError | gnd.errors.PopulationLoadError | RF3 | RF-D5 |
| gnd.population.MAX_SUMMARY_ISSUES | gnd.errors.MAX_SUMMARY_ISSUES | RF3 | RF-D5 |
| gnd.population.PopulationValidationError | gnd.errors.PopulationValidationError | RF3 | RF-D5 |
| gnd.checker.UnvalidatedPopulationError | gnd.errors.UnvalidatedPopulationError | RF3 | RF-D5 |
| gnd.transition.TransitionLoadError | gnd.errors.TransitionLoadError | RF3 | RF-D5 |
| gnd.model.DeonticNote | gnd.documents.DeonticNote | RF3 | RF-D5 |
| gnd.model.Model | gnd.documents.Model | RF3 | RF-D5 |
| gnd.checker._identity_key | gnd.values.identity_key | RF3 | RF-D5 |
| gnd.checker._IdentitySet | gnd.values.IdentitySet | RF3 | RF-D5 |
| gnd.checker._INVALID_LITERAL | gnd.values.INVALID_LITERAL | RF3 | RF-D5 |
| gnd.checker._literal | gnd.values.literal | RF3 | RF-D5 |
| gnd.transition._ISO_TYPES | gnd.values.ISO_TYPES | RF3 | RF-D5 |
| gnd.transition._refuse | gnd.values.refuse | RF3 | RF-D5 |
| gnd.transition._canonical | gnd.values.canonical | RF3 | RF-D5 |
| gnd.population._content_digest | gnd.values.content_digest | RF3 | RF-D5 |
| gnd.population.MODEL_DIGEST_EXCLUDED_FIELDS | gnd.values.MODEL_DIGEST_EXCLUDED_FIELDS | RF3 | RF-D5 |
| gnd.population._model_digest | gnd.values.model_digest | RF3 | RF-D5 |
| gnd.references.reference_model_digest | gnd.values.reference_model_digest | RF3 | RF-D5 |
| gnd.model._fact_type_roles | gnd.universe.fact_type_roles | RF3 | RF-D5 |
| gnd.model._resolved_primitive | gnd.universe.resolved_primitive | RF3 | RF-D5 |
| gnd.model._supertype_parents | gnd.universe.supertype_parents | RF3 | RF-D5 |
| gnd.model._DERIVATION_TERM_CACHE | gnd.universe.DERIVATION_TERM_CACHE | RF3 | RF-D5 |
| gnd.popvalidate._object_types_by_id | gnd.universe.object_types_by_id | RF3 | RF-D5 |
| gnd.popvalidate._identifying_primitive | gnd.universe.identifying_primitive | RF3 | RF-D5 |
| gnd.popvalidate._identifying_id | gnd.universe.identifying_id | RF3 | RF-D5 |
| gnd.popvalidate._resolve_reference | gnd.universe.resolve_reference | RF3 | RF-D5 |
| gnd.popvalidate.resolve_reference_value_type | gnd.universe.resolve_reference_value_type | RF3 | RF-D5 |
| gnd.popvalidate.resolve_primitive | gnd.universe.resolve_primitive | RF3 | RF-D5 |
| gnd.checker.IMPLEMENTED_FAMILIES | gnd.universe.IMPLEMENTED_FAMILIES | RF3 | RF-D5 |
| gnd.checker._RING_VARIANTS | gnd.universe.RING_VARIANTS | RF3 | RF-D5 |
| gnd.checker._is_implemented | gnd.universe.is_implemented | RF3 | RF-D5 |
| gnd.checker._constraint_role_refs | gnd.universe.constraint_role_refs | RF3 | RF-D5 |
| gnd.checker._scope_fact_types | gnd.universe.scope_fact_types | RF3 | RF-D5 |
| gnd.checker._fact_type_by_id | gnd.universe.fact_type_by_id | RF3 | RF-D5 |
| gnd.checker._role_object_type | gnd.universe.role_object_type | RF3 | RF-D5 |
| gnd.checker._descendant_closure | gnd.universe.descendant_closure | RF3 | RF-D5 |
| gnd.checker._denoting_types | gnd.universe.denoting_types | RF3 | RF-D5 |
| gnd.checker._instance_values_of | gnd.universe.instance_values_of | RF3 | RF-D5 |
| gnd.checker._kind_of | gnd.universe.kind_of | RF3 | RF-D5 |
| gnd.checker._instances_of | gnd.universe.instances_of | RF3 | RF-D5 |
| gnd.semantic_registry.applicable_scope_ids | gnd.applicability.applicable_scope_ids | RF3 | RF-D5 |
| gnd.semantic_registry.SURFACES | gnd.branches.SURFACES | RF3 | RF-D5 |
| gnd.semantic_registry.OBLIGATION_KINDS | gnd.branches.OBLIGATION_KINDS | RF3 | RF-D5 |
| gnd.semantic_registry.OUTCOMES | gnd.branches.OUTCOMES | RF3 | RF-D5 |
| gnd.semantic_registry.WITNESS_KINDS | gnd.branches.WITNESS_KINDS | RF3 | RF-D5 |
| gnd.semantic_registry.IR_DIMENSIONS | gnd.branches.IR_DIMENSIONS | RF3 | RF-D5 |
| gnd.semantic_registry.Branch | gnd.branches.Branch | RF3 | RF-D5 |
| gnd.semantic_registry.UnregisteredBranchError | gnd.branches.UnregisteredBranchError | RF3 | RF-D5 |
| gnd.semantic_registry._UNIVERSE | gnd.branches.UNIVERSE | RF3 | RF-D5 |
| gnd.semantic_registry._SNAPSHOT | gnd.branches.SNAPSHOT | RF3 | RF-D5 |
| gnd.semantic_registry._row | gnd.branches.row | RF3 | RF-D5 |
| gnd.semantic_registry._snapshot_rows | gnd.branches.snapshot_rows | RF3 | RF-D5 |
| gnd.semantic_registry._applicability_rows | gnd.branches.applicability_rows | RF3 | RF-D5 |
| gnd.semantic_registry._composition_rows | gnd.branches.composition_rows | RF3 | RF-D5 |
| gnd.semantic_registry._derivation_rows | gnd.branches.derivation_rows | RF3 | RF-D5 |
| gnd.semantic_registry._transition_rows | gnd.branches.transition_rows | RF3 | RF-D5 |
| gnd.semantic_registry._projection_rows | gnd.branches.projection_rows | RF3 | RF-D5 |
| gnd.semantic_registry._feedback_rows | gnd.branches.feedback_rows | RF3 | RF-D5 |
| gnd.semantic_registry._assurance_rows | gnd.branches.assurance_rows | RF3 | RF-D5 |
| gnd.semantic_registry.REGISTRY | gnd.branches.REGISTRY | RF3 | RF-D5 |
| gnd.semantic_registry._BY_ID | gnd.branches.BY_ID | RF3 | RF-D5 |
| gnd.semantic_registry.branch | gnd.branches.branch | RF3 | RF-D5 |
| gnd.semantic_registry.is_registered | gnd.branches.is_registered | RF3 | RF-D5 |
| gnd.semantic_registry.snapshot_branch | gnd.branches.snapshot_branch | RF3 | RF-D5 |
| gnd.semantic_registry.violated_branch | gnd.branches.violated_branch | RF3 | RF-D5 |
| gnd.semantic_registry._TRACES | gnd.branches.TRACES | RF3 | RF-D5 |
| gnd.semantic_registry.capture_branches | gnd.branches.capture_branches | RF3 | RF-D5 |
| gnd.semantic_registry.record_branch | gnd.branches.record_branch | RF3 | RF-D5 |
| gnd.semantic_registry._TIME_RELATIVE | gnd.branches.TIME_RELATIVE | RF3 | RF-D5 |
| gnd.semantic_registry.time_relative_operand | gnd.branches.time_relative_operand | RF3 | RF-D5 |
| gnd.semantic_registry.constraint_variant | gnd.branches.constraint_variant | RF3 | RF-D5 |
| gnd.checker.DerivationKind | gnd.extensions.DerivationKind | RF3 | RF-D5 |
| gnd.checker.DerivationReason | gnd.extensions.DerivationReason | RF3 | RF-D5 |
| gnd.checker.DERIVATION_REASON_CODES | gnd.extensions.DERIVATION_REASON_CODES | RF3 | RF-D5 |
| gnd.checker.EXACT_DERIVATION_REASON_CODES | gnd.extensions.EXACT_DERIVATION_REASON_CODES | RF3 | RF-D5 |
| gnd.checker.DerivationFinding | gnd.extensions.DerivationFinding | RF3 | RF-D5 |
| gnd.checker.DerivationVerdict | gnd.extensions.DerivationVerdict | RF3 | RF-D5 |
| gnd.checker.JoinDisconnectedError | gnd.extensions.JoinDisconnectedError | RF3 | RF-D5 |
| gnd.checker.Scalar | gnd.extensions.Scalar | RF3 | RF-D5 |
| gnd.checker.IdentityCodecVersion | gnd.extensions.IdentityCodecVersion | RF3 | RF-D5 |
| gnd.checker.FactPath | gnd.extensions.FactPath | RF3 | RF-D5 |
| gnd.checker.RowLineage | gnd.extensions.RowLineage | RF3 | RF-D5 |
| gnd.checker._TypedRelation | gnd.extensions.TypedRelation | RF3 | RF-D5 |
| gnd.checker._JoinWork | gnd.extensions.JoinWork | RF3 | RF-D5 |
| gnd.checker._ExactJoinWork | gnd.extensions.ExactJoinWork | RF3 | RF-D5 |
| gnd.checker._FixpointJoinWork | gnd.extensions.FixpointJoinWork | RF3 | RF-D5 |
| gnd.checker._count_term_work | gnd.extensions.count_term_work | RF3 | RF-D5 |
| gnd.checker._ExtensionResult | gnd.extensions.ExtensionResult | RF3 | RF-D5 |
| gnd.checker.RelationUnavailable | gnd.extensions.RelationUnavailable | RF3 | RF-D5 |
| gnd.checker._ExactExtensions | gnd.extensions.ExactExtensions | RF3 | RF-D5 |
| gnd.checker._Wildcard | gnd.extensions.Wildcard | RF3 | RF-D5 |
| gnd.checker._PartialTermFailure | gnd.extensions.PartialTermFailure | RF3 | RF-D5 |
| gnd.checker._PartialExtensions | gnd.extensions.PartialExtensions | RF3 | RF-D5 |
| gnd.checker._PARTIAL_OPAQUE | gnd.extensions.PARTIAL_OPAQUE | RF3 | RF-D5 |
| gnd.checker._symbolic_value | gnd.extensions.symbolic_value | RF3 | RF-D5 |
| gnd.checker._partial_token | gnd.extensions.partial_token | RF3 | RF-D5 |
| gnd.checker._partial_compatible | gnd.extensions.partial_compatible | RF3 | RF-D5 |
| gnd.checker._scalar_primitive_compatible | gnd.extensions.scalar_primitive_compatible | RF3 | RF-D5 |
| gnd.checker._partial_merge | gnd.extensions.partial_merge | RF3 | RF-D5 |
| gnd.checker._partial_row_facts | gnd.extensions.partial_row_facts | RF3 | RF-D5 |
| gnd.checker._partial_binding_shape | gnd.extensions.partial_binding_shape | RF3 | RF-D5 |
| gnd.checker._partial_bindings | gnd.extensions.partial_bindings | RF3 | RF-D5 |
| gnd.checker._partial_negation | gnd.extensions.partial_negation | RF3 | RF-D5 |
| gnd.checker._WITNESS_TRACE | gnd.extensions.WITNESS_TRACE | RF3 | RF-D5 |
| gnd.checker._witness_charge | gnd.extensions.witness_charge | RF3 | RF-D5 |
| gnd.checker._witness_row | gnd.extensions.witness_row | RF3 | RF-D5 |
| gnd.checker._partial_clause_rows | gnd.extensions.partial_clause_rows | RF3 | RF-D5 |
| gnd.checker._ExactExtensionResult | gnd.extensions.ExactExtensionResult | RF3 | RF-D5 |
| gnd.checker.ExtensionCalculator | gnd.extensions.ExtensionCalculator | RF3 | RF-D5 |
| gnd.checker.VariableResolver | gnd.extensions.VariableResolver | RF3 | RF-D5 |
| gnd.checker._RuledFactView | gnd.extensions.RuledFactView | RF3 | RF-D5 |
| gnd.checker._identity_token | gnd.extensions.identity_token | RF3 | RF-D5 |
| gnd.checker._joined_atom_candidates | gnd.extensions.joined_atom_candidates | RF3 | RF-D5 |
| gnd.checker._REFERENCE_PRESENTATION_WORK | gnd.extensions.REFERENCE_PRESENTATION_WORK | RF3 | RF-D5 |
| gnd.checker._joined_bindings | gnd.extensions.joined_bindings | RF3 | RF-D5 |
| gnd.checker._relation_facts | gnd.extensions.relation_facts | RF3 | RF-D5 |
| gnd.checker._relation_roles | gnd.extensions.relation_roles | RF3 | RF-D5 |
| gnd.checker._rows_from_facts | gnd.extensions.rows_from_facts | RF3 | RF-D5 |
| gnd.checker._base_relations | gnd.extensions.base_relations | RF3 | RF-D5 |
| gnd.checker._component_atoms | gnd.extensions.component_atoms | RF3 | RF-D5 |
| gnd.checker._component_product | gnd.extensions.component_product | RF3 | RF-D5 |
| gnd.checker._apply_negation | gnd.extensions.apply_negation | RF3 | RF-D5 |
| gnd.checker._clause_bindings | gnd.extensions.clause_bindings | RF3 | RF-D5 |
| gnd.checker._project_extension | gnd.extensions.project_extension | RF3 | RF-D5 |
| gnd.checker._binding_lineages | gnd.extensions.binding_lineages | RF3 | RF-D5 |
| gnd.checker._project_lineage | gnd.extensions.project_lineage | RF3 | RF-D5 |
| gnd.checker._python_extension_calculator | gnd.extensions.python_extension_calculator | RF3 | RF-D5 |
| gnd.checker._rule_uses_exact_terms | gnd.extensions.rule_uses_exact_terms | RF3 | RF-D5 |
| gnd.checker._aggregate_identity_token | gnd.extensions.aggregate_identity_token | RF3 | RF-D5 |
| gnd.checker._aggregate_bindings | gnd.extensions.aggregate_bindings | RF3 | RF-D5 |
| gnd.checker._model_uses_exact_derivations | gnd.extensions.model_uses_exact_derivations | RF3 | RF-D5 |
| gnd.checker._requires_fixpoint | gnd.extensions.requires_fixpoint | RF3 | RF-D5 |
| gnd.checker._evaluate_stratified_extensions | gnd.extensions.evaluate_stratified_extensions | RF3 | RF-D5 |
| gnd.checker._exact_extension_calculator | gnd.extensions.exact_extension_calculator | RF3 | RF-D5 |
| gnd.checker.exact_extension_envelope | gnd.extensions.exact_extension_envelope | RF3 | RF-D5 |
| gnd.checker.DynamicRefreshWork | gnd.extensions.DynamicRefreshWork | RF3 | RF-D5 |
| gnd.checker.StructuredExtensionView | gnd.extensions.StructuredExtensionView | RF3 | RF-D5 |
| gnd.checker._public_refresh_work | gnd.extensions.public_refresh_work | RF3 | RF-D5 |
| gnd.checker._extension_fact_map | gnd.extensions.extension_fact_map | RF3 | RF-D5 |
| gnd.checker.structured_extension_view | gnd.extensions.structured_extension_view | RF3 | RF-D5 |
| gnd.checker.derivation_claims_against | gnd.extensions.derivation_claims_against | RF3 | RF-D5 |
| gnd.checker._rows_by_identity | gnd.extensions.rows_by_identity | RF3 | RF-D5 |
| gnd.checker._witness | gnd.extensions.witness | RF3 | RF-D5 |
| gnd.checker._derivation_obligation | gnd.extensions.derivation_obligation | RF3 | RF-D5 |
| gnd.checker.evaluate_derivations_legacy | gnd.extensions.evaluate_derivations_legacy | RF3 | RF-D5 |
| gnd.checker.constraint_view_legacy | gnd.extensions.constraint_view_legacy | RF3 | RF-D5 |
| gnd.checker._PHASE3_LEGACY_EVALUATE_DERIVATIONS | gnd.extensions.PHASE3_LEGACY_EVALUATE_DERIVATIONS | RF3 | RF-D5 |
| gnd.checker._PHASE3_LEGACY_CONSTRAINT_VIEW | gnd.extensions.PHASE3_LEGACY_CONSTRAINT_VIEW | RF3 | RF-D5 |
| gnd.checker._exact_derivation_obligation | gnd.extensions.exact_derivation_obligation | RF3 | RF-D5 |
| gnd.checker._evaluate_derivations_dispatch | gnd.extensions.evaluate_derivations_dispatch | RF3 | RF-D5 |
| gnd.checker._constraint_view_dispatch | gnd.extensions.constraint_view_dispatch | RF3 | RF-D5 |
| gnd.checker._evaluate_derivations | gnd.extensions.evaluate_derivations | RF3 | RF-D5 |
| gnd.checker._constraint_view | gnd.extensions.constraint_view | RF3 | RF-D5 |
| gnd.references.MAX_BYTES | gnd.model.MAX_BYTES | RF3 | RF-D5 |
| gnd.references.MAX_SET_BYTES | gnd.model.MAX_SET_BYTES | RF3 | RF-D5 |
| gnd.references.MAX_ENTRIES | gnd.model.MAX_ENTRIES | RF3 | RF-D5 |
| gnd.references._TOKEN | gnd.model.TOKEN | RF3 | RF-D5 |
| gnd.references._BOUND | gnd.model.BOUND | RF3 | RF-D5 |
| gnd.references._COMBINED | gnd.model.COMBINED | RF3 | RF-D5 |
| gnd.references.ReferenceInputError | gnd.model.ReferenceInputError | RF3 | RF-D5 |
| gnd.references.ReferenceOrigin | gnd.model.ReferenceOrigin | RF3 | RF-D5 |
| gnd.references.OccurrenceOrigin | gnd.model.OccurrenceOrigin | RF3 | RF-D5 |
| gnd.references.BoundReferenceContext | gnd.model.BoundReferenceContext | RF3 | RF-D5 |
| gnd.references.BoundPopulationView | gnd.model.BoundPopulationView | RF3 | RF-D5 |
| gnd.references.validate_reference_structure | gnd.model.validate_reference_structure | RF3 | RF-D5 |
| gnd.references._relative | gnd.model.relative | RF3 | RF-D5 |
| gnd.references.retained_root | gnd.model.retained_root | RF3 | RF-D5 |
| gnd.references.validate_declarations | gnd.model.validate_declarations | RF3 | RF-D5 |
| gnd.references._bind_at | gnd.model.bind_at | RF3 | RF-D5 |
| gnd.references.bind_references | gnd.model.bind_references | RF3 | RF-D5 |
| gnd.references.resolve_context | gnd.model.resolve_context | RF3 | RF-D5 |
| gnd.references.bind_population | gnd.model.bind_population | RF3 | RF-D5 |
| gnd.references.candidate_fact_count | gnd.model.candidate_fact_count | RF3 | RF-D5 |
| gnd.references.is_bound_population | gnd.model.is_bound_population | RF3 | RF-D5 |
| gnd.extract.identity.__all__ | gnd.anchor_identity.__all__ | RF3 | RF-D5 |
| gnd.extract.identity._ANCHOR_TRANSLATION | gnd.anchor_identity.ANCHOR_TRANSLATION | RF3 | RF-D5 |
| gnd.extract.identity.anchor_normalize | gnd.anchor_identity.anchor_normalize | RF3 | RF-D5 |
| gnd.extract.identity.lexical_normalize | gnd.anchor_identity.lexical_normalize | RF3 | RF-D5 |
| gnd.extract.identity.identity_key | gnd.anchor_identity.identity_key | RF3 | RF-D5 |
| gnd.extract.anchors.MAX_SIDECAR_BYTES | gnd.anchors.MAX_SIDECAR_BYTES | RF3 | RF-D5 |
| gnd.extract.anchors.MAX_DOCUMENT_BYTES | gnd.anchors.MAX_DOCUMENT_BYTES | RF3 | RF-D5 |
| gnd.extract.anchors._HEX | gnd.anchors.HEX | RF3 | RF-D5 |
| gnd.extract.anchors._NUMBER | gnd.anchors.NUMBER | RF3 | RF-D5 |
| gnd.extract.anchors._INTEGER | gnd.anchors.INTEGER | RF3 | RF-D5 |
| gnd.extract.anchors._DECIMAL | gnd.anchors.DECIMAL | RF3 | RF-D5 |
| gnd.extract.anchors._DATE | gnd.anchors.DATE | RF3 | RF-D5 |
| gnd.extract.anchors._NUMERIC_TOKEN | gnd.anchors.NUMERIC_TOKEN | RF3 | RF-D5 |
| gnd.extract.anchors.AnchorError | gnd.anchors.AnchorError | RF3 | RF-D5 |
| gnd.extract.anchors.AnchorSidecar | gnd.anchors.AnchorSidecar | RF3 | RF-D5 |
| gnd.extract.anchors._pairs | gnd.anchors.pairs | RF3 | RF-D5 |
| gnd.extract.anchors._reject_constant | gnd.anchors.reject_constant | RF3 | RF-D5 |
| gnd.extract.anchors._parse | gnd.anchors.parse | RF3 | RF-D5 |
| gnd.extract.anchors._exact_keys | gnd.anchors.exact_keys | RF3 | RF-D5 |
| gnd.extract.anchors._digest | gnd.anchors.digest | RF3 | RF-D5 |
| gnd.extract.anchors._scalar | gnd.anchors.scalar | RF3 | RF-D5 |
| gnd.extract.anchors.parse_anchor_sidecar | gnd.anchors.parse_anchor_sidecar | RF3 | RF-D5 |
| gnd.extract.anchors.read_anchor_sidecar | gnd.anchors.read_anchor_sidecar | RF3 | RF-D5 |
| gnd.extract.anchors.read_regular_path | gnd.anchors.read_regular_path | RF3 | RF-D5 |
| gnd.extract.anchors.validate_anchor_sidecar | gnd.anchors.validate_anchor_sidecar | RF3 | RF-D5 |
| gnd.extract.anchors._canonical | gnd.anchors.canonical | RF3 | RF-D5 |
| gnd.extract.anchors.vocabulary_digest | gnd.anchors.vocabulary_digest | RF3 | RF-D5 |
| gnd.extract.anchors.canonical_document_text | gnd.anchors.canonical_document_text | RF3 | RF-D5 |
| gnd.extract.anchors.bind_anchors | gnd.anchors.bind_anchors | RF3 | RF-D5 |
| gnd.extract.anchors.write_anchor_sidecar | gnd.anchors.write_anchor_sidecar | RF3 | RF-D5 |
| gnd.extract.anchors._word | gnd.anchors.word | RF3 | RF-D5 |
| gnd.extract.anchors.lexical_ranges | gnd.anchors.lexical_ranges | RF3 | RF-D5 |
| gnd.extract.anchors.recognition_target | gnd.anchors.recognition_target | RF3 | RF-D5 |
| gnd.extract.anchors.recognition_index | gnd.anchors.recognition_index | RF3 | RF-D5 |
| gnd.extract.anchors.recognised_ranges | gnd.anchors.recognised_ranges | RF3 | RF-D5 |
| gnd.extract.refscheme.__all__ | gnd.refscheme.__all__ | RF3 | RF-D5 |
| gnd.extract.refscheme._object_types_by_id | gnd.refscheme.object_types_by_id | RF3 | RF-D5 |
| gnd.extract.refscheme._fact_types_by_id | gnd.refscheme.fact_types_by_id | RF3 | RF-D5 |
| gnd.extract.refscheme._referenced_object_type | gnd.refscheme.referenced_object_type | RF3 | RF-D5 |
| gnd.extract.refscheme._anchors_on | gnd.refscheme.anchors_on | RF3 | RF-D5 |
| gnd.extract.refscheme._unmatchable_reason | gnd.refscheme.unmatchable_reason | RF3 | RF-D5 |
| gnd.extract.refscheme.reference_identity | gnd.refscheme.reference_identity | RF3 | RF-D5 |
| gnd.extract.refscheme.applicable_set | gnd.refscheme.applicable_set | RF3 | RF-D5 |
| gnd.extract.vocabulary.__all__ | gnd.vocabulary.__all__ | RF3 | RF-D5 |
| gnd.extract.vocabulary._PLACEHOLDER | gnd.vocabulary.PLACEHOLDER | RF3 | RF-D5 |
| gnd.extract.vocabulary.reading_text | gnd.vocabulary.reading_text | RF3 | RF-D5 |
| gnd.extract.vocabulary._display | gnd.vocabulary.display | RF3 | RF-D5 |
| gnd.extract.vocabulary._object_type_sentence | gnd.vocabulary.object_type_sentence | RF3 | RF-D5 |
| gnd.extract.vocabulary.render_verbalization | gnd.vocabulary.render_verbalization | RF3 | RF-D5 |
| gnd.report.load_report_schema | gnd.report_schema.load_report_schema | RF3 | RF-D5 |
| gnd.extract.manifest.manifest_path_issue | gnd.manifest_paths.manifest_path_issue | RF3 | RF-D5 |
| gnd.correspondence._scalar_identity | gnd.semantic_rows.scalar_identity | RF3 | RF-D5 |
| gnd.correspondence._canonical_rows | gnd.semantic_rows.canonical_rows | RF3 | RF-D5 |
| gnd.checker._RING_COMPONENTS | gnd.universe.RING_COMPONENTS | RF3 | RF-D5 |

| gnd.model.structured_derivation_ids | gnd.documents.structured_derivation_ids | RF3 | Alias; same object; RF-D5 retirement |
| gnd.model.MAX_YAML_EVENTS | gnd.documents.MAX_YAML_EVENTS | RF3 | Alias; same object; RF-D5 retirement |

## RF4 -- peripheral homes

The exact per-name old/new paths are in [RF4 move inventory](../evidence/RF4/moves.json).
Its identity gate checks every listed name; public spellings strip the leading
underscore, except _json uses decode_json and __all__ uses compat_all.
Installer filesystem closure moves to safefs; artifact/domain variants retain
canonical defining homes and are exposed through distinct public seams.
Agent runner/adapter, assurance, oracle, payload and export/witness service
aliases retain predecessor objects and historical serialized qualifications.
Retirement follows RF-D5: first public release after RF6 plus separate approval.

## RF6a primitive query move

| gnd.universe._resolved_primitive | gnd.model_queries._resolved_primitive | RF6a | First public release after RF6 and separate retirement approval; original historical metadata retained |
| gnd.universe._supertype_parents | gnd.model_queries._supertype_parents | RF6a | First public release after RF6 and separate retirement approval; original historical metadata retained |
| gnd.universe._identifying_primitive | gnd.model_queries._identifying_primitive | RF6a | First public release after RF6 and separate retirement approval; original historical metadata retained |
| gnd.universe._identifying_id | gnd.model_queries._identifying_id | RF6a | First public release after RF6 and separate retirement approval; original historical metadata retained |
| gnd.universe._resolve_reference | gnd.model_queries._resolve_reference | RF6a | First public release after RF6 and separate retirement approval; original historical metadata retained |
| gnd.universe.primitive_for | gnd.model_queries.primitive_for | RF6a | First public release after RF6 and separate retirement approval; original historical metadata retained |

| gnd.synth.value_domain._in_range | gnd.synth.value_domain.in_range | RF6a RF-D8/D10 | First public release after RF6 plus separate retirement approval; unchanged algorithm and metadata |

## RF6b -- model/checker section homes

All predecessor namespace bindings remain explicit aliases. Retirement requires the first public release after RF6 and separate approval (RF-D5).

| Old binding | Section alias home | Phase | Retirement |
|---|---|---|---|
| gnd.model.annotations | gnd.model._validation.annotations | RF6b | RF-D5; original qualification retained |
| gnd.model.TYPE_CHECKING | gnd.model._validation.TYPE_CHECKING | RF6b | RF-D5; original qualification retained |
| gnd.model.json | gnd.model._validation.json | RF6b | RF-D5; original qualification retained |
| gnd.model.math | gnd.model._validation.math | RF6b | RF-D5; original qualification retained |
| gnd.model.re | gnd.model._validation.re | RF6b | RF-D5; original qualification retained |
| gnd.model.Mapping | gnd.model._validation.Mapping | RF6b | RF-D5; original qualification retained |
| gnd.model.dataclass | gnd.model._validation.dataclass | RF6b | RF-D5; original qualification retained |
| gnd.model.UTC | gnd.model._validation.UTC | RF6b | RF-D5; original qualification retained |
| gnd.model.date | gnd.model._validation.date | RF6b | RF-D5; original qualification retained |
| gnd.model.datetime | gnd.model._validation.datetime | RF6b | RF-D5; original qualification retained |
| gnd.model.files | gnd.model._validation.files | RF6b | RF-D5; original qualification retained |
| gnd.model.Path | gnd.model._validation.Path | RF6b | RF-D5; original qualification retained |
| gnd.model.Any | gnd.model._validation.Any | RF6b | RF-D5; original qualification retained |
| gnd.model.Literal | gnd.model.Literal | RF6b | RF-D5; original qualification retained |
| gnd.model.Draft202012Validator | gnd.model._validation.Draft202012Validator | RF6b | RF-D5; original qualification retained |
| gnd.model.YAML | gnd.model._validation.YAML | RF6b | RF-D5; original qualification retained |
| gnd.model.verbalize | gnd.model._validation.verbalize | RF6b | RF-D5; original qualification retained |
| gnd.model.atom_bind | gnd.model._validation.atom_bind | RF6b | RF-D5; original qualification retained |
| gnd.model.atom_has_bind | gnd.model._validation.atom_has_bind | RF6b | RF-D5; original qualification retained |
| gnd.model.DeonticNote | gnd.model._validation.DeonticNote | RF6b | RF-D5; original qualification retained |
| gnd.model.Model | gnd.model._validation.Model | RF6b | RF-D5; original qualification retained |
| gnd.model.ModelLoadError | gnd.model._validation.ModelLoadError | RF6b | RF-D5; original qualification retained |
| gnd.model.ModelValidationError | gnd.model._validation.ModelValidationError | RF6b | RF-D5; original qualification retained |
| gnd.model.ValidationIssue | gnd.model._validation.ValidationIssue | RF6b | RF-D5; original qualification retained |
| gnd.model.issues_from_validation_error | gnd.model._validation.issues_from_validation_error | RF6b | RF-D5; original qualification retained |
| gnd.model.DEFAULT_LIMITS | gnd.model._validation.DEFAULT_LIMITS | RF6b | RF-D5; original qualification retained |
| gnd.model.FLOAT_FUNCTION_ARITY | gnd.model._validation.FLOAT_FUNCTION_ARITY | RF6b | RF-D5; original qualification retained |
| gnd.model.NUMERIC_PRIMITIVES | gnd.model._validation.NUMERIC_PRIMITIVES | RF6b | RF-D5; original qualification retained |
| gnd.model.analyze_term | gnd.model._validation.analyze_term | RF6b | RF-D5; original qualification retained |
| gnd.model.is_function_term | gnd.model._validation.is_function_term | RF6b | RF-D5; original qualification retained |
| gnd.model.term_variables | gnd.model._validation.term_variables | RF6b | RF-D5; original qualification retained |
| gnd.model._DERIVATION_TERM_CACHE | gnd.model._validation._DERIVATION_TERM_CACHE | RF6b | RF-D5; original qualification retained |
| gnd.model._fact_type_roles | gnd.model._validation._fact_type_roles | RF6b | RF-D5; original qualification retained |
| gnd.model._resolved_primitive | gnd.model._validation._resolved_primitive | RF6b | RF-D5; original qualification retained |
| gnd.model._supertype_parents | gnd.model._validation._supertype_parents | RF6b | RF-D5; original qualification retained |
| gnd.model.configure_comment_scanner | gnd.model._validation.configure_comment_scanner | RF6b | RF-D5; original qualification retained |
| gnd.model._PLACEHOLDER | gnd.model._validation._PLACEHOLDER | RF6b | RF-D5; original qualification retained |
| gnd.model.MAX_MODEL_BYTES | gnd.model._validation.MAX_MODEL_BYTES | RF6b | RF-D5; original qualification retained |
| gnd.model.MAX_YAML_EVENTS | gnd.model._validation.MAX_YAML_EVENTS | RF6b | RF-D5; original qualification retained |
| gnd.model.yaml_stream_guard_error | gnd.model._validation.yaml_stream_guard_error | RF6b | RF-D5; original qualification retained |
| gnd.model.structured_derivation_ids | gnd.model._validation.structured_derivation_ids | RF6b | RF-D5; original qualification retained |
| gnd.model._load_meta_schema | gnd.model._validation._load_meta_schema | RF6b | RF-D5; original qualification retained |
| gnd.model._DERIVATION_ARM_KEYS | gnd.model._validation._DERIVATION_ARM_KEYS | RF6b | RF-D5; original qualification retained |
| gnd.model._derivation_rule_hint | gnd.model._validation._derivation_rule_hint | RF6b | RF-D5; original qualification retained |
| gnd.model._layer1_structural | gnd.model._validation._layer1_structural | RF6b | RF-D5; original qualification retained |
| gnd.model._iter_constraints | gnd.model._validation._iter_constraints | RF6b | RF-D5; original qualification retained |
| gnd.model._iter_role_refs | gnd.model._validation._iter_role_refs | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_id_unique | gnd.model._validation._rule_id_unique | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_role_ref | gnd.model._validation._rule_role_ref | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_cross_ref | gnd.model._validation._rule_cross_ref | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_depends_on | gnd.model._validation._rule_depends_on | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_reading_placeholders | gnd.model._validation._rule_reading_placeholders | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_fact_type_arity | gnd.model._validation._rule_fact_type_arity | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_role_names_distinct | gnd.model._validation._rule_role_names_distinct | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_subtype_ref | gnd.model._validation._rule_subtype_ref | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_external_ref_uc | gnd.model._validation._rule_external_ref_uc | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_reference_value_type | gnd.model._validation._rule_reference_value_type | RF6b | RF-D5; original qualification retained |
| gnd.model._temporal_literal_valid | gnd.model._validation._temporal_literal_valid | RF6b | RF-D5; original qualification retained |
| gnd.model._NUMERIC_PRIMITIVES | gnd.model._validation._NUMERIC_PRIMITIVES | RF6b | RF-D5; original qualification retained |
| gnd.model._range_endpoints_valid | gnd.model._validation._range_endpoints_valid | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_value_range_type | gnd.model._validation._rule_value_range_type | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_value_range_order | gnd.model._validation._rule_value_range_order | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_count_bound_order | gnd.model._validation._rule_count_bound_order | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_status_source | gnd.model._validation._rule_status_source | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_string_ref | gnd.model._validation._rule_string_ref | RF6b | RF-D5; original qualification retained |
| gnd.model._ancestor_closure | gnd.model._validation._ancestor_closure | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_ring_binary | gnd.model._validation._rule_ring_binary | RF6b | RF-D5; original qualification retained |
| gnd.model._ROLE_SEQ_FIELDS | gnd.model._validation._ROLE_SEQ_FIELDS | RF6b | RF-D5; original qualification retained |
| gnd.model._constraint_role_seqs | gnd.model._validation._constraint_role_seqs | RF6b | RF-D5; original qualification retained |
| gnd.model._joining_sequences | gnd.model._validation._joining_sequences | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_join_anchor_unambiguous | gnd.model._validation._rule_join_anchor_unambiguous | RF6b | RF-D5; original qualification retained |
| gnd.model._role_object_types | gnd.model._validation._role_object_types | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_role_seq_arity | gnd.model._validation._rule_role_seq_arity | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_role_seq_type_compat | gnd.model._validation._rule_role_seq_type_compat | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_disjunctive_subject_type | gnd.model._validation._rule_disjunctive_subject_type | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_partition_asserts_something | gnd.model._validation._rule_partition_asserts_something | RF6b | RF-D5; original qualification retained |
| gnd.model.NEVER_MECHANICAL_FAMILIES | gnd.model._validation.NEVER_MECHANICAL_FAMILIES | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_anchored_role_and_recogniser | gnd.model._validation._rule_anchored_role_and_recogniser | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_textual_alethic | gnd.model._validation._rule_textual_alethic | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_modality_policy | gnd.model._validation._rule_modality_policy | RF6b | RF-D5; original qualification retained |
| gnd.model._iter_operations | gnd.model._validation._iter_operations | RF6b | RF-D5; original qualification retained |
| gnd.model._operation_parameters | gnd.model._validation._operation_parameters | RF6b | RF-D5; original qualification retained |
| gnd.model._iter_operation_obligations | gnd.model._validation._iter_operation_obligations | RF6b | RF-D5; original qualification retained |
| gnd.model._iter_operation_atoms | gnd.model._validation._iter_operation_atoms | RF6b | RF-D5; original qualification retained |
| gnd.model._iter_operation_terms | gnd.model._validation._iter_operation_terms | RF6b | RF-D5; original qualification retained |
| gnd.model._variable_name | gnd.model._validation._variable_name | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_op_param_ref | gnd.model._validation._rule_op_param_ref | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_op_param_names_distinct | gnd.model._validation._rule_op_param_names_distinct | RF6b | RF-D5; original qualification retained |
| gnd.model._REPORTED_PARAMETER_LIMIT | gnd.model._validation._REPORTED_PARAMETER_LIMIT | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_op_reading_placeholders | gnd.model._validation._rule_op_reading_placeholders | RF6b | RF-D5; original qualification retained |
| gnd.model._atom_reference_issues | gnd.model._validation._atom_reference_issues | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_op_atom_ref | gnd.model._validation._rule_op_atom_ref | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_op_term_ref | gnd.model._validation._rule_op_term_ref | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_op_term_type_compat | gnd.model._validation._rule_op_term_type_compat | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_op_effect_ground | gnd.model._validation._rule_op_effect_ground | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_op_create_param | gnd.model._validation._rule_op_create_param | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_op_create_ref_mode | gnd.model._validation._rule_op_create_ref_mode | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_op_obligation_ids_distinct | gnd.model._validation._rule_op_obligation_ids_distinct | RF6b | RF-D5; original qualification retained |
| gnd.model.IMPORTED_PROVENANCE_FIELDS | gnd.model._validation.IMPORTED_PROVENANCE_FIELDS | RF6b | RF-D5; original qualification retained |
| gnd.model._iter_provenance_bearing | gnd.model._validation._iter_provenance_bearing | RF6b | RF-D5; original qualification retained |
| gnd.model._provenance_bearing_label | gnd.model._validation._provenance_bearing_label | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_imported_provenance | gnd.model._validation._rule_imported_provenance | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_imported_confirmed_reviewed | gnd.model._validation._rule_imported_confirmed_reviewed | RF6b | RF-D5; original qualification retained |
| gnd.model._internal_uniqueness_keys | gnd.model._validation._internal_uniqueness_keys | RF6b | RF-D5; original qualification retained |
| gnd.model.dynamic_subject_is_functional | gnd.model._validation.dynamic_subject_is_functional | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_op_dynamic_functional | gnd.model._validation._rule_op_dynamic_functional | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_op_dynamic_untouched | gnd.model._validation._rule_op_dynamic_untouched | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_op_modality_policy | gnd.model._validation._rule_op_modality_policy | RF6b | RF-D5; original qualification retained |
| gnd.model._iter_guarded_constraints | gnd.model._validation._iter_guarded_constraints | RF6b | RF-D5; original qualification retained |
| gnd.model._iter_guarded_atoms | gnd.model._validation._iter_guarded_atoms | RF6b | RF-D5; original qualification retained |
| gnd.model._iter_guarded_consequent_terms | gnd.model._validation._iter_guarded_consequent_terms | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_guarded_term_ref | gnd.model._validation._rule_guarded_term_ref | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_guarded_role_claim | gnd.model._validation._rule_guarded_role_claim | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_guarded_consequent_ground | gnd.model._validation._rule_guarded_consequent_ground | RF6b | RF-D5; original qualification retained |
| gnd.model._guarded_nested_function_variables | gnd.model._validation._guarded_nested_function_variables | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_guarded_exists_range | gnd.model._validation._rule_guarded_exists_range | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_guarded_exists_where_bound | gnd.model._validation._rule_guarded_exists_where_bound | RF6b | RF-D5; original qualification retained |
| gnd.model._guarded_primitives_compatible | gnd.model._validation._guarded_primitives_compatible | RF6b | RF-D5; original qualification retained |
| gnd.model._guarded_literal_matches_primitive | gnd.model._validation._guarded_literal_matches_primitive | RF6b | RF-D5; original qualification retained |
| gnd.model._guarded_literal_kinds_compatible | gnd.model._validation._guarded_literal_kinds_compatible | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_guarded_comparison_type | gnd.model._validation._rule_guarded_comparison_type | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_guarded_exists_where_type | gnd.model._validation._rule_guarded_exists_where_type | RF6b | RF-D5; original qualification retained |
| gnd.model._DERIVATION_RULE_KEYS | gnd.model._validation._DERIVATION_RULE_KEYS | RF6b | RF-D5; original qualification retained |
| gnd.model.iter_derivation_clauses | gnd.model._validation.iter_derivation_clauses | RF6b | RF-D5; original qualification retained |
| gnd.model._is_structured_rule | gnd.model._validation._is_structured_rule | RF6b | RF-D5; original qualification retained |
| gnd.model._iter_structured_fact_derivations | gnd.model._validation._iter_structured_fact_derivations | RF6b | RF-D5; original qualification retained |
| gnd.model._DERIVATION_ATOM_VISITS | gnd.model._validation._DERIVATION_ATOM_VISITS | RF6b | RF-D5; original qualification retained |
| gnd.model._DERIVATION_WORK | gnd.model._validation._DERIVATION_WORK | RF6b | RF-D5; original qualification retained |
| gnd.model._DERIVATION_CLASSIFICATION_WORK | gnd.model._validation._DERIVATION_CLASSIFICATION_WORK | RF6b | RF-D5; original qualification retained |
| gnd.model._derivation_atoms | gnd.model._validation._derivation_atoms | RF6b | RF-D5; original qualification retained |
| gnd.model._safe_key | gnd.model._validation._safe_key | RF6b | RF-D5; original qualification retained |
| gnd.model._derivation_id | gnd.model._validation._derivation_id | RF6b | RF-D5; original qualification retained |
| gnd.model._derivation_bind | gnd.model._validation._derivation_bind | RF6b | RF-D5; original qualification retained |
| gnd.model._derivation_variable | gnd.model._validation._derivation_variable | RF6b | RF-D5; original qualification retained |
| gnd.model._derivation_positive_variables | gnd.model._validation._derivation_positive_variables | RF6b | RF-D5; original qualification retained |
| gnd.model._aggregate_variables | gnd.model._validation._aggregate_variables | RF6b | RF-D5; original qualification retained |
| gnd.model.AggregateAnalysis | gnd.model._validation.AggregateAnalysis | RF6b | RF-D5; original qualification retained |
| gnd.model.analyze_aggregate | gnd.model._validation.analyze_aggregate | RF6b | RF-D5; original qualification retained |
| gnd.model._derivation_scope_variables | gnd.model._validation._derivation_scope_variables | RF6b | RF-D5; original qualification retained |
| gnd.model._primitive_maps | gnd.model._validation._primitive_maps | RF6b | RF-D5; original qualification retained |
| gnd.model._derivation_variable_primitives | gnd.model._validation._derivation_variable_primitives | RF6b | RF-D5; original qualification retained |
| gnd.model.analyze_declared_aggregate | gnd.model._validation.analyze_declared_aggregate | RF6b | RF-D5; original qualification retained |
| gnd.model.body_components | gnd.model._validation.body_components | RF6b | RF-D5; original qualification retained |
| gnd.model.derivation_dependencies | gnd.model._validation.derivation_dependencies | RF6b | RF-D5; original qualification retained |
| gnd.model.DerivationEdge | gnd.model._validation.DerivationEdge | RF6b | RF-D5; original qualification retained |
| gnd.model.derivation_dependency_edges | gnd.model._validation.derivation_dependency_edges | RF6b | RF-D5; original qualification retained |
| gnd.model.DerivationStability | gnd.model._validation.DerivationStability | RF6b | RF-D5; original qualification retained |
| gnd.model.DerivationClassification | gnd.model._validation.DerivationClassification | RF6b | RF-D5; original qualification retained |
| gnd.model.derivation_dependency_closure | gnd.model._validation.derivation_dependency_closure | RF6b | RF-D5; original qualification retained |
| gnd.model._derivation_dependency_closures | gnd.model._validation._derivation_dependency_closures | RF6b | RF-D5; original qualification retained |
| gnd.model.derivation_classifications | gnd.model._validation.derivation_classifications | RF6b | RF-D5; original qualification retained |
| gnd.model._derivation_components | gnd.model._validation._derivation_components | RF6b | RF-D5; original qualification retained |
| gnd.model.derivation_strata | gnd.model._validation.derivation_strata | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_derivation_term_ref | gnd.model._validation._rule_derivation_term_ref | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_derivation_rule_shape | gnd.model._validation._rule_derivation_rule_shape | RF6b | RF-D5; original qualification retained |
| gnd.model._aggregate_issues | gnd.model._validation._aggregate_issues | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_aggregate_shape | gnd.model._validation._rule_aggregate_shape | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_aggregate_function | gnd.model._validation._rule_aggregate_function | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_aggregate_of_unbound | gnd.model._validation._rule_aggregate_of_unbound | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_aggregate_over_unbound | gnd.model._validation._rule_aggregate_over_unbound | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_aggregate_over_duplicate | gnd.model._validation._rule_aggregate_over_duplicate | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_aggregate_as_not_fresh | gnd.model._validation._rule_aggregate_as_not_fresh | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_aggregate_input_type | gnd.model._validation._rule_aggregate_input_type | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_aggregate_where_scope | gnd.model._validation._rule_aggregate_where_scope | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_aggregate_head_scope | gnd.model._validation._rule_aggregate_head_scope | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_aggregate_head_needs_round | gnd.model._validation._rule_aggregate_head_needs_round | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_derivation_structured_on_object_type | gnd.model._validation._rule_derivation_structured_on_object_type | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_derivation_effect_on_derived | gnd.model._validation._rule_derivation_effect_on_derived | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_derivation_effect_on_semiderived | gnd.model._validation._rule_derivation_effect_on_semiderived | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_derivation_dynamic_dependency_incomplete | gnd.model._validation._rule_derivation_dynamic_dependency_incomplete | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_derivation_role_claim | gnd.model._validation._rule_derivation_role_claim | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_derivation_head_role_claim | gnd.model._validation._rule_derivation_head_role_claim | RF6b | RF-D5; original qualification retained |
| gnd.model._derivation_head_term_issues | gnd.model._validation._derivation_head_term_issues | RF6b | RF-D5; original qualification retained |
| gnd.model._filter_derivation_term_issues | gnd.model._validation._filter_derivation_term_issues | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_term_function_name | gnd.model._validation._rule_term_function_name | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_term_function_arity | gnd.model._validation._rule_term_function_arity | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_term_argument_type | gnd.model._validation._rule_term_argument_type | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_term_non_finite_number | gnd.model._validation._rule_term_non_finite_number | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_term_node_budget | gnd.model._validation._rule_term_node_budget | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_term_depth_budget | gnd.model._validation._rule_term_depth_budget | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_term_shape | gnd.model._validation._rule_term_shape | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_term_unbound | gnd.model._validation._rule_term_unbound | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_derivation_head_term_type | gnd.model._validation._rule_derivation_head_term_type | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_derivation_head_needs_round | gnd.model._validation._rule_derivation_head_needs_round | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_derivation_float_head_unquantized | gnd.model._validation._rule_derivation_float_head_unquantized | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_derivation_term_unbound | gnd.model._validation._rule_derivation_term_unbound | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_term_comparison_type | gnd.model._validation._rule_term_comparison_type | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_derivation_head_unbound | gnd.model._validation._rule_derivation_head_unbound | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_derivation_negate_unbound | gnd.model._validation._rule_derivation_negate_unbound | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_derivation_body_component_unused | gnd.model._validation._rule_derivation_body_component_unused | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_derivation_term_type | gnd.model._validation._rule_derivation_term_type | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_derivation_opaque_dependency | gnd.model._validation._rule_derivation_opaque_dependency | RF6b | RF-D5; original qualification retained |
| gnd.model._derivation_cycles | gnd.model._validation._derivation_cycles | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_derivation_unstratified | gnd.model._validation._rule_derivation_unstratified | RF6b | RF-D5; original qualification retained |
| gnd.model._rule_temporal_language | gnd.model._validation._rule_temporal_language | RF6b | RF-D5; original qualification retained |
| gnd.model._SEMANTIC_RULES | gnd.model._validation._SEMANTIC_RULES | RF6b | RF-D5; original qualification retained |
| gnd.model.semantic_validate | gnd.model._validation.semantic_validate | RF6b | RF-D5; original qualification retained |
| gnd.model.load_model_bytes | gnd.model.load_model_bytes | RF6b | RF-D5; original qualification retained |
| gnd.model._load_model_no_follow | gnd.model._load_model_no_follow | RF6b | RF-D5; original qualification retained |
| gnd.model.load_model | gnd.model.load_model | RF6b | RF-D5; original qualification retained |
| gnd.model._effect_index | gnd.model._operations._effect_index | RF6b | RF-D5; original qualification retained |
| gnd.model._variables_in | gnd.model._operations._variables_in | RF6b | RF-D5; original qualification retained |
| gnd.model._roles_by_variable | gnd.model._operations._roles_by_variable | RF6b | RF-D5; original qualification retained |
| gnd.model._has_literal | gnd.model._operations._has_literal | RF6b | RF-D5; original qualification retained |
| gnd.model.compile_operation | gnd.model._operations.compile_operation | RF6b | RF-D5; original qualification retained |
| gnd.model._attach_compiled_obligations | gnd.model._operations._attach_compiled_obligations | RF6b | RF-D5; original qualification retained |
| gnd.model.hashlib | gnd.model.hashlib | RF6b | RF-D5; original qualification retained |
| gnd.model.os | gnd.model.os | RF6b | RF-D5; original qualification retained |
| gnd.model.weakref | gnd.model.weakref | RF6b | RF-D5; original qualification retained |
| gnd.model.contextmanager | gnd.model.contextmanager | RF6b | RF-D5; original qualification retained |
| gnd.model.artifacts | gnd.model.artifacts | RF6b | RF-D5; original qualification retained |
| gnd.model.reference_model_digest | gnd.model.reference_model_digest | RF6b | RF-D5; original qualification retained |
| gnd.model.MAX_BYTES | gnd.model.MAX_BYTES | RF6b | RF-D5; original qualification retained |
| gnd.model.MAX_SET_BYTES | gnd.model.MAX_SET_BYTES | RF6b | RF-D5; original qualification retained |
| gnd.model.MAX_ENTRIES | gnd.model.MAX_ENTRIES | RF6b | RF-D5; original qualification retained |
| gnd.model._TOKEN | gnd.model._TOKEN | RF6b | RF-D5; original qualification retained |
| gnd.model._BOUND | gnd.model._BOUND | RF6b | RF-D5; original qualification retained |
| gnd.model._COMBINED | gnd.model._COMBINED | RF6b | RF-D5; original qualification retained |
| gnd.model.ReferenceInputError | gnd.model.ReferenceInputError | RF6b | RF-D5; original qualification retained |
| gnd.model.ReferenceOrigin | gnd.model.ReferenceOrigin | RF6b | RF-D5; original qualification retained |
| gnd.model.OccurrenceOrigin | gnd.model.OccurrenceOrigin | RF6b | RF-D5; original qualification retained |
| gnd.model.BoundReferenceContext | gnd.model.BoundReferenceContext | RF6b | RF-D5; original qualification retained |
| gnd.model.BoundPopulationView | gnd.model.BoundPopulationView | RF6b | RF-D5; original qualification retained |
| gnd.model.validate_reference_structure | gnd.model.validate_reference_structure | RF6b | RF-D5; original qualification retained |
| gnd.model._relative | gnd.model._relative | RF6b | RF-D5; original qualification retained |
| gnd.model.retained_root | gnd.model.retained_root | RF6b | RF-D5; original qualification retained |
| gnd.model.validate_declarations | gnd.model.validate_declarations | RF6b | RF-D5; original qualification retained |
| gnd.model._bind_at | gnd.model._bind_at | RF6b | RF-D5; original qualification retained |
| gnd.model.bind_references | gnd.model.bind_references | RF6b | RF-D5; original qualification retained |
| gnd.model.resolve_context | gnd.model.resolve_context | RF6b | RF-D5; original qualification retained |
| gnd.model.bind_population | gnd.model.bind_population | RF6b | RF-D5; original qualification retained |
| gnd.model.candidate_fact_count | gnd.model.candidate_fact_count | RF6b | RF-D5; original qualification retained |
| gnd.model.is_bound_population | gnd.model.is_bound_population | RF6b | RF-D5; original qualification retained |
| gnd.model.BOUND | gnd.model.BOUND | RF6b | RF-D5; original qualification retained |
| gnd.model.COMBINED | gnd.model.COMBINED | RF6b | RF-D5; original qualification retained |
| gnd.model.TOKEN | gnd.model.TOKEN | RF6b | RF-D5; original qualification retained |
| gnd.model.bind_at | gnd.model.bind_at | RF6b | RF-D5; original qualification retained |
| gnd.model.relative | gnd.model.relative | RF6b | RF-D5; original qualification retained |
| gnd.checker.annotations | gnd.checker._core.annotations | RF6b | RF-D5; original qualification retained |
| gnd.checker.math | gnd.checker._core.math | RF6b | RF-D5; original qualification retained |
| gnd.checker.Iterable | gnd.checker._core.Iterable | RF6b | RF-D5; original qualification retained |
| gnd.checker.Mapping | gnd.checker._core.Mapping | RF6b | RF-D5; original qualification retained |
| gnd.checker.Sequence | gnd.checker._core.Sequence | RF6b | RF-D5; original qualification retained |
| gnd.checker.dataclass | gnd.checker._core.dataclass | RF6b | RF-D5; original qualification retained |
| gnd.checker.replace | gnd.checker._core.replace | RF6b | RF-D5; original qualification retained |
| gnd.checker.UTC | gnd.checker._core.UTC | RF6b | RF-D5; original qualification retained |
| gnd.checker.date | gnd.checker._core.date | RF6b | RF-D5; original qualification retained |
| gnd.checker.datetime | gnd.checker._core.datetime | RF6b | RF-D5; original qualification retained |
| gnd.checker.CycleError | gnd.checker._core.CycleError | RF6b | RF-D5; original qualification retained |
| gnd.checker.TopologicalSorter | gnd.checker._core.TopologicalSorter | RF6b | RF-D5; original qualification retained |
| gnd.checker.MappingProxyType | gnd.checker._core.MappingProxyType | RF6b | RF-D5; original qualification retained |
| gnd.checker.Any | gnd.checker._core.Any | RF6b | RF-D5; original qualification retained |
| gnd.checker.Literal | gnd.checker._core.Literal | RF6b | RF-D5; original qualification retained |
| gnd.checker.NamedTuple | gnd.checker._core.NamedTuple | RF6b | RF-D5; original qualification retained |
| gnd.checker.Protocol | gnd.checker._core.Protocol | RF6b | RF-D5; original qualification retained |
| gnd.checker.BaseModel | gnd.checker._core.BaseModel | RF6b | RF-D5; original qualification retained |
| gnd.checker.Field | gnd.checker._core.Field | RF6b | RF-D5; original qualification retained |
| gnd.checker.ValidationInfo | gnd.checker._core.ValidationInfo | RF6b | RF-D5; original qualification retained |
| gnd.checker.model_validator | gnd.checker._core.model_validator | RF6b | RF-D5; original qualification retained |
| gnd.checker.extension_core | gnd.checker._core.extension_core | RF6b | RF-D5; original qualification retained |
| gnd.checker.verbalize | gnd.checker._core.verbalize | RF6b | RF-D5; original qualification retained |
| gnd.checker.derivation_address | gnd.checker._core.derivation_address | RF6b | RF-D5; original qualification retained |
| gnd.checker.positional_constraint_ref | gnd.checker._core.positional_constraint_ref | RF6b | RF-D5; original qualification retained |
| gnd.checker.atom_bind | gnd.checker._core.atom_bind | RF6b | RF-D5; original qualification retained |
| gnd.checker.atom_has_bind | gnd.checker._core.atom_has_bind | RF6b | RF-D5; original qualification retained |
| gnd.checker.UnregisteredBranchError | gnd.checker._core.UnregisteredBranchError | RF6b | RF-D5; original qualification retained |
| gnd.checker.branch | gnd.checker._core.branch | RF6b | RF-D5; original qualification retained |
| gnd.checker.constraint_variant | gnd.checker._core.constraint_variant | RF6b | RF-D5; original qualification retained |
| gnd.checker.record_branch | gnd.checker._core.record_branch | RF6b | RF-D5; original qualification retained |
| gnd.checker.time_relative_operand | gnd.checker._core.time_relative_operand | RF6b | RF-D5; original qualification retained |
| gnd.checker.FAMILIES | gnd.checker._core.FAMILIES | RF6b | RF-D5; original qualification retained |
| gnd.checker.resolve_hook | gnd.checker._core.resolve_hook | RF6b | RF-D5; original qualification retained |
| gnd.checker.Model | gnd.checker._core.Model | RF6b | RF-D5; original qualification retained |
| gnd.checker.UnvalidatedPopulationError | gnd.checker._core.UnvalidatedPopulationError | RF6b | RF-D5; original qualification retained |
| gnd.checker.DERIVATION_REASON_CODES | gnd.checker._core.DERIVATION_REASON_CODES | RF6b | RF-D5; original qualification retained |
| gnd.checker.EXACT_DERIVATION_REASON_CODES | gnd.checker._core.EXACT_DERIVATION_REASON_CODES | RF6b | RF-D5; original qualification retained |
| gnd.checker.DerivationFinding | gnd.checker._core.DerivationFinding | RF6b | RF-D5; original qualification retained |
| gnd.checker.DerivationKind | gnd.checker._core.DerivationKind | RF6b | RF-D5; original qualification retained |
| gnd.checker.DerivationReason | gnd.checker._core.DerivationReason | RF6b | RF-D5; original qualification retained |
| gnd.checker.DerivationVerdict | gnd.checker._core.DerivationVerdict | RF6b | RF-D5; original qualification retained |
| gnd.checker.DynamicRefreshWork | gnd.checker._core.DynamicRefreshWork | RF6b | RF-D5; original qualification retained |
| gnd.checker.ExtensionCalculator | gnd.checker._core.ExtensionCalculator | RF6b | RF-D5; original qualification retained |
| gnd.checker.FactPath | gnd.checker._core.FactPath | RF6b | RF-D5; original qualification retained |
| gnd.checker.IdentityCodecVersion | gnd.checker._core.IdentityCodecVersion | RF6b | RF-D5; original qualification retained |
| gnd.checker.JoinDisconnectedError | gnd.checker._core.JoinDisconnectedError | RF6b | RF-D5; original qualification retained |
| gnd.checker.RelationUnavailable | gnd.checker._core.RelationUnavailable | RF6b | RF-D5; original qualification retained |
| gnd.checker.RowLineage | gnd.checker._core.RowLineage | RF6b | RF-D5; original qualification retained |
| gnd.checker.Scalar | gnd.checker._core.Scalar | RF6b | RF-D5; original qualification retained |
| gnd.checker.StructuredExtensionView | gnd.checker._core.StructuredExtensionView | RF6b | RF-D5; original qualification retained |
| gnd.checker.VariableResolver | gnd.checker._core.VariableResolver | RF6b | RF-D5; original qualification retained |
| gnd.checker.constraint_view_legacy | gnd.checker._core.constraint_view_legacy | RF6b | RF-D5; original qualification retained |
| gnd.checker.derivation_claims_against | gnd.checker._core.derivation_claims_against | RF6b | RF-D5; original qualification retained |
| gnd.checker.evaluate_derivations_legacy | gnd.checker._core.evaluate_derivations_legacy | RF6b | RF-D5; original qualification retained |
| gnd.checker.exact_extension_envelope | gnd.checker._core.exact_extension_envelope | RF6b | RF-D5; original qualification retained |
| gnd.checker.structured_extension_view | gnd.checker._core.structured_extension_view | RF6b | RF-D5; original qualification retained |
| gnd.checker._PARTIAL_OPAQUE | gnd.checker._core._PARTIAL_OPAQUE | RF6b | RF-D5; original qualification retained |
| gnd.checker._PHASE3_LEGACY_CONSTRAINT_VIEW | gnd.checker._core._PHASE3_LEGACY_CONSTRAINT_VIEW | RF6b | RF-D5; original qualification retained |
| gnd.checker._PHASE3_LEGACY_EVALUATE_DERIVATIONS | gnd.checker._core._PHASE3_LEGACY_EVALUATE_DERIVATIONS | RF6b | RF-D5; original qualification retained |
| gnd.checker._REFERENCE_PRESENTATION_WORK | gnd.checker._core._REFERENCE_PRESENTATION_WORK | RF6b | RF-D5; original qualification retained |
| gnd.checker._WITNESS_TRACE | gnd.checker._core._WITNESS_TRACE | RF6b | RF-D5; original qualification retained |
| gnd.checker._ExactExtensionResult | gnd.checker._core._ExactExtensionResult | RF6b | RF-D5; original qualification retained |
| gnd.checker._ExactExtensions | gnd.checker._core._ExactExtensions | RF6b | RF-D5; original qualification retained |
| gnd.checker._ExactJoinWork | gnd.checker._core._ExactJoinWork | RF6b | RF-D5; original qualification retained |
| gnd.checker._ExtensionResult | gnd.checker._core._ExtensionResult | RF6b | RF-D5; original qualification retained |
| gnd.checker._FixpointJoinWork | gnd.checker._core._FixpointJoinWork | RF6b | RF-D5; original qualification retained |
| gnd.checker._JoinWork | gnd.checker._core._JoinWork | RF6b | RF-D5; original qualification retained |
| gnd.checker._PartialExtensions | gnd.checker._core._PartialExtensions | RF6b | RF-D5; original qualification retained |
| gnd.checker._PartialTermFailure | gnd.checker._core._PartialTermFailure | RF6b | RF-D5; original qualification retained |
| gnd.checker._RuledFactView | gnd.checker._core._RuledFactView | RF6b | RF-D5; original qualification retained |
| gnd.checker._TypedRelation | gnd.checker._core._TypedRelation | RF6b | RF-D5; original qualification retained |
| gnd.checker._Wildcard | gnd.checker._core._Wildcard | RF6b | RF-D5; original qualification retained |
| gnd.checker._aggregate_bindings | gnd.checker._core._aggregate_bindings | RF6b | RF-D5; original qualification retained |
| gnd.checker._aggregate_identity_token | gnd.checker._core._aggregate_identity_token | RF6b | RF-D5; original qualification retained |
| gnd.checker._apply_negation | gnd.checker._core._apply_negation | RF6b | RF-D5; original qualification retained |
| gnd.checker._base_relations | gnd.checker._core._base_relations | RF6b | RF-D5; original qualification retained |
| gnd.checker._binding_lineages | gnd.checker._core._binding_lineages | RF6b | RF-D5; original qualification retained |
| gnd.checker._clause_bindings | gnd.checker._core._clause_bindings | RF6b | RF-D5; original qualification retained |
| gnd.checker._component_atoms | gnd.checker._core._component_atoms | RF6b | RF-D5; original qualification retained |
| gnd.checker._component_product | gnd.checker._core._component_product | RF6b | RF-D5; original qualification retained |
| gnd.checker._constraint_view | gnd.checker._core._constraint_view | RF6b | RF-D5; original qualification retained |
| gnd.checker._constraint_view_dispatch | gnd.checker._core._constraint_view_dispatch | RF6b | RF-D5; original qualification retained |
| gnd.checker._count_term_work | gnd.checker._core._count_term_work | RF6b | RF-D5; original qualification retained |
| gnd.checker._derivation_obligation | gnd.checker._core._derivation_obligation | RF6b | RF-D5; original qualification retained |
| gnd.checker._evaluate_derivations | gnd.checker._core._evaluate_derivations | RF6b | RF-D5; original qualification retained |
| gnd.checker._evaluate_derivations_dispatch | gnd.checker._core._evaluate_derivations_dispatch | RF6b | RF-D5; original qualification retained |
| gnd.checker._evaluate_stratified_extensions | gnd.checker._core._evaluate_stratified_extensions | RF6b | RF-D5; original qualification retained |
| gnd.checker._exact_derivation_obligation | gnd.checker._core._exact_derivation_obligation | RF6b | RF-D5; original qualification retained |
| gnd.checker._exact_extension_calculator | gnd.checker._core._exact_extension_calculator | RF6b | RF-D5; original qualification retained |
| gnd.checker._extension_fact_map | gnd.checker._core._extension_fact_map | RF6b | RF-D5; original qualification retained |
| gnd.checker._identity_token | gnd.checker._core._identity_token | RF6b | RF-D5; original qualification retained |
| gnd.checker._joined_atom_candidates | gnd.checker._core._joined_atom_candidates | RF6b | RF-D5; original qualification retained |
| gnd.checker._joined_bindings | gnd.checker._core._joined_bindings | RF6b | RF-D5; original qualification retained |
| gnd.checker._model_uses_exact_derivations | gnd.checker._core._model_uses_exact_derivations | RF6b | RF-D5; original qualification retained |
| gnd.checker._partial_binding_shape | gnd.checker._core._partial_binding_shape | RF6b | RF-D5; original qualification retained |
| gnd.checker._partial_bindings | gnd.checker._core._partial_bindings | RF6b | RF-D5; original qualification retained |
| gnd.checker._partial_clause_rows | gnd.checker._core._partial_clause_rows | RF6b | RF-D5; original qualification retained |
| gnd.checker._partial_compatible | gnd.checker._core._partial_compatible | RF6b | RF-D5; original qualification retained |
| gnd.checker._partial_merge | gnd.checker._core._partial_merge | RF6b | RF-D5; original qualification retained |
| gnd.checker._partial_negation | gnd.checker._core._partial_negation | RF6b | RF-D5; original qualification retained |
| gnd.checker._partial_row_facts | gnd.checker._core._partial_row_facts | RF6b | RF-D5; original qualification retained |
| gnd.checker._partial_token | gnd.checker._core._partial_token | RF6b | RF-D5; original qualification retained |
| gnd.checker._project_extension | gnd.checker._core._project_extension | RF6b | RF-D5; original qualification retained |
| gnd.checker._project_lineage | gnd.checker._core._project_lineage | RF6b | RF-D5; original qualification retained |
| gnd.checker._public_refresh_work | gnd.checker._core._public_refresh_work | RF6b | RF-D5; original qualification retained |
| gnd.checker._python_extension_calculator | gnd.checker._core._python_extension_calculator | RF6b | RF-D5; original qualification retained |
| gnd.checker._relation_facts | gnd.checker._core._relation_facts | RF6b | RF-D5; original qualification retained |
| gnd.checker._relation_roles | gnd.checker._core._relation_roles | RF6b | RF-D5; original qualification retained |
| gnd.checker._requires_fixpoint | gnd.checker._core._requires_fixpoint | RF6b | RF-D5; original qualification retained |
| gnd.checker._rows_by_identity | gnd.checker._core._rows_by_identity | RF6b | RF-D5; original qualification retained |
| gnd.checker._rows_from_facts | gnd.checker._core._rows_from_facts | RF6b | RF-D5; original qualification retained |
| gnd.checker._rule_uses_exact_terms | gnd.checker._core._rule_uses_exact_terms | RF6b | RF-D5; original qualification retained |
| gnd.checker._scalar_primitive_compatible | gnd.checker._core._scalar_primitive_compatible | RF6b | RF-D5; original qualification retained |
| gnd.checker._symbolic_value | gnd.checker._core._symbolic_value | RF6b | RF-D5; original qualification retained |
| gnd.checker._witness | gnd.checker._core._witness | RF6b | RF-D5; original qualification retained |
| gnd.checker._witness_charge | gnd.checker._core._witness_charge | RF6b | RF-D5; original qualification retained |
| gnd.checker._witness_row | gnd.checker._core._witness_row | RF6b | RF-D5; original qualification retained |
| gnd.checker.AggregateAnalysis | gnd.checker._core.AggregateAnalysis | RF6b | RF-D5; original qualification retained |
| gnd.checker.BoundReferenceContext | gnd.checker._core.BoundReferenceContext | RF6b | RF-D5; original qualification retained |
| gnd.checker._derivation_variable | gnd.checker._core._derivation_variable | RF6b | RF-D5; original qualification retained |
| gnd.checker.analyze_declared_aggregate | gnd.checker._core.analyze_declared_aggregate | RF6b | RF-D5; original qualification retained |
| gnd.checker.body_components | gnd.checker._core.body_components | RF6b | RF-D5; original qualification retained |
| gnd.checker.derivation_classifications | gnd.checker._core.derivation_classifications | RF6b | RF-D5; original qualification retained |
| gnd.checker.derivation_dependencies | gnd.checker._core.derivation_dependencies | RF6b | RF-D5; original qualification retained |
| gnd.checker.derivation_strata | gnd.checker._core.derivation_strata | RF6b | RF-D5; original qualification retained |
| gnd.checker.iter_derivation_clauses | gnd.checker._core.iter_derivation_clauses | RF6b | RF-D5; original qualification retained |
| gnd.checker.ModelIndex | gnd.checker._core.ModelIndex | RF6b | RF-D5; original qualification retained |
| gnd.checker.Population | gnd.checker._core.Population | RF6b | RF-D5; original qualification retained |
| gnd.checker.adapt_phase1_slice | gnd.checker._core.adapt_phase1_slice | RF6b | RF-D5; original qualification retained |
| gnd.checker.phase1_refusal_reason | gnd.checker._core.phase1_refusal_reason | RF6b | RF-D5; original qualification retained |
| gnd.checker.MAX_SLICE_CONSTRAINTS | gnd.checker._core.MAX_SLICE_CONSTRAINTS | RF6b | RF-D5; original qualification retained |
| gnd.checker.SliceInput | gnd.checker._core.SliceInput | RF6b | RF-D5; original qualification retained |
| gnd.checker.SliceVerdict | gnd.checker._core.SliceVerdict | RF6b | RF-D5; original qualification retained |
| gnd.checker.phase1_decide | gnd.checker._core.phase1_decide | RF6b | RF-D5; original qualification retained |
| gnd.checker.DEFAULT_LIMITS | gnd.checker._core.DEFAULT_LIMITS | RF6b | RF-D5; original qualification retained |
| gnd.checker.compare_terms | gnd.checker._core.compare_terms | RF6b | RF-D5; original qualification retained |
| gnd.checker.evaluate_term | gnd.checker._core.evaluate_term | RF6b | RF-D5; original qualification retained |
| gnd.checker.is_function_term | gnd.checker._core.is_function_term | RF6b | RF-D5; original qualification retained |
| gnd.checker.materialize_scalar | gnd.checker._core.materialize_scalar | RF6b | RF-D5; original qualification retained |
| gnd.checker.term_variables | gnd.checker._core.term_variables | RF6b | RF-D5; original qualification retained |
| gnd.checker.IMPLEMENTED_FAMILIES | gnd.checker._core.IMPLEMENTED_FAMILIES | RF6b | RF-D5; original qualification retained |
| gnd.checker.resolve_primitive | gnd.checker._core.resolve_primitive | RF6b | RF-D5; original qualification retained |
| gnd.checker.resolve_reference_value_type | gnd.checker._core.resolve_reference_value_type | RF6b | RF-D5; original qualification retained |
| gnd.checker._RING_VARIANTS | gnd.checker._core._RING_VARIANTS | RF6b | RF-D5; original qualification retained |
| gnd.checker._constraint_role_refs | gnd.checker._core._constraint_role_refs | RF6b | RF-D5; original qualification retained |
| gnd.checker._denoting_types | gnd.checker._core._denoting_types | RF6b | RF-D5; original qualification retained |
| gnd.checker._descendant_closure | gnd.checker._core._descendant_closure | RF6b | RF-D5; original qualification retained |
| gnd.checker._fact_type_by_id | gnd.checker._core._fact_type_by_id | RF6b | RF-D5; original qualification retained |
| gnd.checker._instance_values_of | gnd.checker._core._instance_values_of | RF6b | RF-D5; original qualification retained |
| gnd.checker._instances_of | gnd.checker._core._instances_of | RF6b | RF-D5; original qualification retained |
| gnd.checker._is_implemented | gnd.checker._core._is_implemented | RF6b | RF-D5; original qualification retained |
| gnd.checker._kind_of | gnd.checker._core._kind_of | RF6b | RF-D5; original qualification retained |
| gnd.checker._role_object_type | gnd.checker._core._role_object_type | RF6b | RF-D5; original qualification retained |
| gnd.checker._scope_fact_types | gnd.checker._core._scope_fact_types | RF6b | RF-D5; original qualification retained |
| gnd.checker._INVALID_LITERAL | gnd.checker._core._INVALID_LITERAL | RF6b | RF-D5; original qualification retained |
| gnd.checker._IdentitySet | gnd.checker._core._IdentitySet | RF6b | RF-D5; original qualification retained |
| gnd.checker._identity_key | gnd.checker._core._identity_key | RF6b | RF-D5; original qualification retained |
| gnd.checker._literal | gnd.checker._core._literal | RF6b | RF-D5; original qualification retained |
| gnd.checker.Verdict | gnd.checker._reports.Verdict | RF6b | RF-D5; original qualification retained |
| gnd.checker._RING_COMPONENTS | gnd.checker._core._RING_COMPONENTS | RF6b | RF-D5; original qualification retained |
| gnd.checker.ConstraintVerdict | gnd.checker._reports.ConstraintVerdict | RF6b | RF-D5; original qualification retained |
| gnd.checker.CoverageEntry | gnd.checker._reports.CoverageEntry | RF6b | RF-D5; original qualification retained |
| gnd.checker.Phase1Trace | gnd.checker._reports.Phase1Trace | RF6b | RF-D5; original qualification retained |
| gnd.checker.CheckReport | gnd.checker._reports.CheckReport | RF6b | RF-D5; original qualification retained |
| gnd.checker.band | gnd.checker._reports.band | RF6b | RF-D5; original qualification retained |
| gnd.checker.check_legacy | gnd.checker._core.check_legacy | RF6b | RF-D5; original qualification retained |
| gnd.checker._observe_phase1_compatibility | gnd.checker._core._observe_phase1_compatibility | RF6b | RF-D5; original qualification retained |
| gnd.checker._plain_projected_witness | gnd.checker._core._plain_projected_witness | RF6b | RF-D5; original qualification retained |
| gnd.checker._correspondence_message | gnd.checker._core._correspondence_message | RF6b | RF-D5; original qualification retained |
| gnd.checker._value_comparison_message_inputs | gnd.checker._core._value_comparison_message_inputs | RF6b | RF-D5; original qualification retained |
| gnd.checker._compatibility_trace | gnd.checker._core._compatibility_trace | RF6b | RF-D5; original qualification retained |
| gnd.checker._OBJECT_TYPE_SCOPED | gnd.checker._core._OBJECT_TYPE_SCOPED | RF6b | RF-D5; original qualification retained |
| gnd.checker._no_observable_subjects_message | gnd.checker._core._no_observable_subjects_message | RF6b | RF-D5; original qualification retained |
| gnd.checker._JoinSubjectRow | gnd.checker._core._JoinSubjectRow | RF6b | RF-D5; original qualification retained |
| gnd.checker._JOIN_SUBJECT_SEQS | gnd.checker._core._JOIN_SUBJECT_SEQS | RF6b | RF-D5; original qualification retained |
| gnd.checker._joining_subject_sequences | gnd.checker._core._joining_subject_sequences | RF6b | RF-D5; original qualification retained |
| gnd.checker._no_joined_rows_message | gnd.checker._core._no_joined_rows_message | RF6b | RF-D5; original qualification retained |
| gnd.checker._MANDATORY_RELEVANT | gnd.checker._core._MANDATORY_RELEVANT | RF6b | RF-D5; original qualification retained |
| gnd.checker._vacuity_message | gnd.checker._core._vacuity_message | RF6b | RF-D5; original qualification retained |
| gnd.checker.JoinAmbiguousError | gnd.checker._core.JoinAmbiguousError | RF6b | RF-D5; original qualification retained |
| gnd.checker._project | gnd.checker._core._project | RF6b | RF-D5; original qualification retained |
| gnd.checker._identity_counts | gnd.checker._core._identity_counts | RF6b | RF-D5; original qualification retained |
| gnd.checker._join_rows | gnd.checker._core._join_rows | RF6b | RF-D5; original qualification retained |
| gnd.checker._require_joinable | gnd.checker._core._require_joinable | RF6b | RF-D5; original qualification retained |
| gnd.checker._role_seq_tuples | gnd.checker._core._role_seq_tuples | RF6b | RF-D5; original qualification retained |
| gnd.checker._ref_labels | gnd.checker._core._ref_labels | RF6b | RF-D5; original qualification retained |
| gnd.checker._violation_verdict | gnd.checker._core._violation_verdict | RF6b | RF-D5; original qualification retained |
| gnd.checker._orderable | gnd.checker._core._orderable | RF6b | RF-D5; original qualification retained |
| gnd.checker._in_range | gnd.checker._core._in_range | RF6b | RF-D5; original qualification retained |
| gnd.checker._find_cycle | gnd.checker._core._find_cycle | RF6b | RF-D5; original qualification retained |
| gnd.checker._dfs_cycle | gnd.checker._core._dfs_cycle | RF6b | RF-D5; original qualification retained |
| gnd.checker._ring_component_violations | gnd.checker._core._ring_component_violations | RF6b | RF-D5; original qualification retained |
| gnd.checker._COMPARATORS | gnd.checker._core._COMPARATORS | RF6b | RF-D5; original qualification retained |
| gnd.checker._typed_comparison_values | gnd.checker._core._typed_comparison_values | RF6b | RF-D5; original qualification retained |
| gnd.checker._compare | gnd.checker._core._compare | RF6b | RF-D5; original qualification retained |
| gnd.checker._guarded_variable | gnd.checker._core._guarded_variable | RF6b | RF-D5; original qualification retained |
| gnd.checker._FactView | gnd.checker._core._FactView | RF6b | RF-D5; original qualification retained |
| gnd.checker._guarded_bindings | gnd.checker._core._guarded_bindings | RF6b | RF-D5; original qualification retained |
| gnd.checker.structured_extension_facts | gnd.checker._core.structured_extension_facts | RF6b | RF-D5; original qualification retained |
| gnd.checker._guarded_variable_primitives | gnd.checker._core._guarded_variable_primitives | RF6b | RF-D5; original qualification retained |
| gnd.checker._guarded_ground_atom | gnd.checker._core._guarded_ground_atom | RF6b | RF-D5; original qualification retained |
| gnd.checker._guarded_atom_index | gnd.checker._core._guarded_atom_index | RF6b | RF-D5; original qualification retained |
| gnd.checker._PHASE3_LEGACY_CHECK | gnd.checker._core._PHASE3_LEGACY_CHECK | RF6b | RF-D5; original qualification retained |
| gnd.checker._guarded_term_failure | gnd.checker._core._guarded_term_failure | RF6b | RF-D5; original qualification retained |
| gnd.checker._term_unavailable_constraint_verdict | gnd.checker._core._term_unavailable_constraint_verdict | RF6b | RF-D5; original qualification retained |
| gnd.checker._record_aggregate_guarded_outcomes | gnd.checker._core._record_aggregate_guarded_outcomes | RF6b | RF-D5; original qualification retained |
| gnd.checker._partial_constraint_report | gnd.checker._core._partial_constraint_report | RF6b | RF-D5; original qualification retained |
| gnd.checker._check_dispatch | gnd.checker._core._check_dispatch | RF6b | RF-D5; original qualification retained |
| gnd.checker._anchored_verdicts | gnd.checker._core._anchored_verdicts | RF6b | RF-D5; original qualification retained |
| gnd.checker.check_with_anchors | gnd.checker._core.check_with_anchors | RF6b | RF-D5; original qualification retained |
| gnd.checker.check | gnd.checker._core.check | RF6b | RF-D5; original qualification retained |
| gnd.checker.check_partial | gnd.checker._core.check_partial | RF6b | RF-D5; original qualification retained |
| gnd.checker.check_with_anchors_partial | gnd.checker._core.check_with_anchors_partial | RF6b | RF-D5; original qualification retained |
| gnd.checker.effective_view | gnd.checker._core.effective_view | RF6b | RF-D5; original qualification retained |
| gnd.checker._family_message_ring | gnd.checker._core._family_message_ring | RF6b | RF-D5; original qualification retained |
| gnd.checker._family_message_mandatory | gnd.checker._core._family_message_mandatory | RF6b | RF-D5; original qualification retained |
| gnd.checker._family_message_mandatory_disjunctive | gnd.checker._core._family_message_mandatory_disjunctive | RF6b | RF-D5; original qualification retained |
| gnd.checker._family_message_uniqueness | gnd.checker._core._family_message_uniqueness | RF6b | RF-D5; original qualification retained |
| gnd.checker._family_message_value | gnd.checker._core._family_message_value | RF6b | RF-D5; original qualification retained |
| gnd.checker._family_message_frequency | gnd.checker._core._family_message_frequency | RF6b | RF-D5; original qualification retained |
| gnd.checker._family_message_subset | gnd.checker._core._family_message_subset | RF6b | RF-D5; original qualification retained |
| gnd.checker._family_message_exclusive_or | gnd.checker._core._family_message_exclusive_or | RF6b | RF-D5; original qualification retained |
| gnd.checker._family_message_value_comparison | gnd.checker._core._family_message_value_comparison | RF6b | RF-D5; original qualification retained |
| gnd.checker._family_message_cardinality | gnd.checker._core._family_message_cardinality | RF6b | RF-D5; original qualification retained |
| gnd.checker._family_message_subtype_partition | gnd.checker._core._family_message_subtype_partition | RF6b | RF-D5; original qualification retained |
| gnd.checker._family_message_guarded | gnd.checker._core._family_message_guarded | RF6b | RF-D5; original qualification retained |
| gnd.checker._flat_projected_witness | gnd.checker._core._flat_projected_witness | RF6b | RF-D5; original qualification retained |
| gnd.checker._row_projected_witness | gnd.checker._core._row_projected_witness | RF6b | RF-D5; original qualification retained |
| gnd.checker._family_message_default | gnd.checker._core._family_message_default | RF6b | RF-D5; original qualification retained |

## RF8 session compatibility shims

| gnd.exp.session_store._evidence_entry | gnd.exp.session_records._evidence_entry | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._version_validation_error | gnd.exp.session_records._version_validation_error | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._strict_object_bytes | gnd.exp.session_records._strict_object_bytes | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._create_evidence_parent | gnd.exp.session_records._create_evidence_parent | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._write_new_file | gnd.exp.session_records._write_new_file | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store.CandidateFile | gnd.exp.session_records.CandidateFile | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store.CandidateInventory | gnd.exp.session_records.CandidateInventory | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store.EvidenceFile | gnd.exp.session_records.EvidenceFile | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store.VerifierPayloadEvidence | gnd.exp.session_records.VerifierPayloadEvidence | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store.LaunchIntent | gnd.exp.session_records.LaunchIntent | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store.DeclaredLaunchIntent | gnd.exp.session_records.DeclaredLaunchIntent | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._DeclaredLaunchIntentV3 | gnd.exp.session_records._DeclaredLaunchIntentV3 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._DeclaredLaunchIntentV4 | gnd.exp.session_records._DeclaredLaunchIntentV4 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store.DeclaredLaunchIntent | gnd.exp.session_records.DeclaredLaunchIntent | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store.CandidateEdit | gnd.exp.session_records.CandidateEdit | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store.RankingObservation | gnd.exp.session_records.RankingObservation | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._AttemptRecordBase | gnd.exp.session_records._AttemptRecordBase | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._AttemptRecordV1 | gnd.exp.session_records._AttemptRecordV1 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._AttemptRecordV2 | gnd.exp.session_records._AttemptRecordV2 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._AttemptRecordV3 | gnd.exp.session_records._AttemptRecordV3 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._AttemptRecordV4 | gnd.exp.session_records._AttemptRecordV4 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._AttemptRecordV5 | gnd.exp.session_records._AttemptRecordV5 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._AttemptRecordV6 | gnd.exp.session_records._AttemptRecordV6 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._AttemptRecordV7 | gnd.exp.session_records._AttemptRecordV7 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._AttemptRecordV8 | gnd.exp.session_records._AttemptRecordV8 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._AttemptRecordV9 | gnd.exp.session_records._AttemptRecordV9 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store.JudgmentEvidence | gnd.exp.session_records.JudgmentEvidence | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._AttemptRecordV10 | gnd.exp.session_records._AttemptRecordV10 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store.AttemptRecord | gnd.exp.session_records.AttemptRecord | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store.SessionOutcome | gnd.exp.session_records.SessionOutcome | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._SessionResultBase | gnd.exp.session_records._SessionResultBase | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._SessionResultV1 | gnd.exp.session_records._SessionResultV1 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._SessionResultV2 | gnd.exp.session_records._SessionResultV2 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._SessionResultV3 | gnd.exp.session_records._SessionResultV3 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._SessionResultV4 | gnd.exp.session_records._SessionResultV4 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store.WalkFloorResult | gnd.exp.session_records.WalkFloorResult | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._SessionResultV5 | gnd.exp.session_records._SessionResultV5 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._SessionResultV6 | gnd.exp.session_records._SessionResultV6 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._SessionResultV7 | gnd.exp.session_records._SessionResultV7 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store.SessionResult | gnd.exp.session_records.SessionResult | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store.BestAttemptIdentity | gnd.exp.session_records.BestAttemptIdentity | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store.RecurrencePair | gnd.exp.session_records.RecurrencePair | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store.ResumeState | gnd.exp.session_records.ResumeState | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store.StagedCandidate | gnd.exp.session_records.StagedCandidate | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._CollectedFile | gnd.exp.session_records._CollectedFile | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._classify | gnd.exp.session_records._classify | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._collect_candidate | gnd.exp.session_records._collect_candidate | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_store._retained_wire | gnd.exp.session_records._retained_wire | RF8 | RF-D5; original qualification retained |
| gnd.exp.session.verifier_environment | gnd.exp.session_environment.verifier_environment | RF8 | RF-D5; original qualification retained |
| gnd.exp.session._required_evidence_complete | gnd.exp.session_control._required_evidence_complete | RF8 | RF-D5; original qualification retained |
| gnd.exp.session._has_verifier_harness_failure | gnd.exp.session_control._has_verifier_harness_failure | RF8 | RF-D5; original qualification retained |
| gnd.exp.session._declared_evidence_complete | gnd.exp.session_control._declared_evidence_complete | RF8 | RF-D5; original qualification retained |
| gnd.exp.session._agent_failure_reason | gnd.exp.session_control._agent_failure_reason | RF8 | RF-D5; original qualification retained |
| gnd.exp.session._expected_invocation_argv | gnd.exp.session_control._expected_invocation_argv | RF8 | RF-D5; original qualification retained |
| gnd.exp.session._effective_agent_prompt | gnd.exp.session_control._effective_agent_prompt | RF8 | RF-D5; original qualification retained |
| gnd.exp.session._effective_policy_sha256 | gnd.exp.session_control._effective_policy_sha256 | RF8 | RF-D5; original qualification retained |
| gnd.exp.session._policy_bound_prompt | gnd.exp.session_control._policy_bound_prompt | RF8 | RF-D5; original qualification retained |
| gnd.exp.session._validated_invocation_proof | gnd.exp.session_control._validated_invocation_proof | RF8 | RF-D5; original qualification retained |
| gnd.exp.session._validated_declared_invocation_proof | gnd.exp.session_control._validated_declared_invocation_proof | RF8 | RF-D5; original qualification retained |
| gnd.exp.session._budget_reason | gnd.exp.session_control._budget_reason | RF8 | RF-D5; original qualification retained |
| gnd.exp.session._Disposition | gnd.exp.session_control._Disposition | RF8 | RF-D5; original qualification retained |
| gnd.exp.session._decide_disposition | gnd.exp.session_control._decide_disposition | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_v7._read | gnd.exp.session_replay._read | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_v7._entry | gnd.exp.session_replay._entry | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_v7._model | gnd.exp.session_replay._model | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_v7._evaluate | gnd.exp.session_replay._evaluate | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_v7._project | gnd.exp.session_replay._project | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_v7._feedback | gnd.exp.session_replay._feedback | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_v7.reconstruct | gnd.exp.session_replay.reconstruct | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_v7._copy_files | gnd.exp.session_runtime._copy_files | RF8 | RF-D5; original qualification retained |
| gnd.exp.session_v7.run | gnd.exp.session_runtime.run | RF8 | RF-D5; original qualification retained |
