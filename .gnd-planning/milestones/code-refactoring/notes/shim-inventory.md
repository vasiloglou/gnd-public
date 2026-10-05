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
