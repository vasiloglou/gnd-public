"""Version-7 orchestration and read-only reconstruction of its exact evidence."""

from __future__ import annotations

import json  # noqa: F401 -- historical compatibility binding

from gnd import input_policy as _rf7_input
from gnd.admission_validation import constraint_annotations, validate_reference_transport
from gnd.artifacts import (
    canonical_json_bytes,
    read_regular_bounded,
)
from gnd.artifacts import (
    sha256_hex as _sha,
)
from gnd.exp.session_contract import (
    ConstraintSatisfactionAcceptance,
    TestsAcceptance,
    TransitionAcceptance,
    read_session_contract,
)
from gnd.exp.session_eval import (
    AttemptEvaluation,
    AttemptFeedback,
    _case_feedback,
    best_key,
    contract_accepts,
    normalized_verifier_signature,
    observe_expected_outputs,
    ranking_observations,
    validate_tests_payload,
    validate_transition_payload,
    validate_verifier_payload,
)
from gnd.exp.session_patch import (
    apply_candidate_patch,
    proposal_mode,
    read_patch_document,
)
from gnd.exp.session_records import (
    AttemptRecord,
    BestAttemptIdentity,
    ResumeState,
    SessionResult,
    _collect_candidate,
    _evidence_entry,
)
from gnd.model import load_model_bytes
from gnd.population import load_population
from gnd.references import bind_references


def _read(root, relative):
    return read_regular_bounded(root, relative, max_bytes=10 * 1024 * 1024)[0]


def _entry(path, raw):
    return _evidence_entry(path, raw)


def _model(case, experiment):
    if case.verify is None:
        return None, None
    bound = case.verify.model
    raw = _read(experiment, bound.path)
    if len(raw) != bound.size_bytes or _sha(raw) != bound.sha256:
        raise ValueError("bound verifier model changed")
    model = load_model_bytes(raw, source=bound.path)
    references = None
    if model.reference_populations:
        references = bind_references(model, root=experiment / case.reference_root)
        model._references = references
    return model, references


def _evaluate(case, raw, process_exit, snapshot, experiment, digest, contract_sha, run_root=None):
    if isinstance(case.acceptance, TestsAcceptance):
        return validate_tests_payload(
            raw,
            case_id=case.case_id,
            role=case.role.value,
            process_exit=process_exit,
            required_tests=case.acceptance.required_tests,
            candidate_sha256=digest,
            contract_sha256=contract_sha,
        )
    model, refs = _model(case, experiment)
    from gnd.payloads import current_payload_schema_version
    from gnd.terms import uses_temporal

    version = (
        (13 if uses_temporal(model) else 10)
        if isinstance(case.acceptance, ConstraintSatisfactionAcceptance)
        else (8 if case.verify.post is None else 7)
        if isinstance(case.acceptance, TransitionAcceptance)
        else current_payload_schema_version(model)
    )
    if len(raw) > 10 * 1024 * 1024:
        raise ValueError("verifier transport exceeds byte cap")
    payload = _rf7_input.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("verifier transport must be an object")  # noqa: TRY004 - public refusal seam
    if refs is not None:
        validate_reference_transport(
            payload, model=model, references=refs, expected_version=14 if version == 13 else 12
        )
    elif "report" in payload:
        raise ValueError("unselected reference wrapper")
    inner = payload.get("report", payload)
    args = {
        "case_id": case.case_id,
        "role": case.role.value,
        "process_exit": process_exit,
        "expected_model": case.verify.model.path,
        "candidate_sha256": digest,
        "contract_sha256": contract_sha,
        "evidence_candidate_sha256": digest,
        "evidence_contract_sha256": contract_sha,
        "expected_schema_version": version,
    }
    encoded = canonical_json_bytes(inner) if "report" in payload else bytes(raw)
    if isinstance(case.acceptance, TransitionAcceptance):
        steps = _rf7_input.loads(_read(snapshot, case.verify.steps))
        result = validate_transition_payload(
            encoded, expected_post=case.verify.post, submitted_steps=steps, **args
        )
    else:
        result = validate_verifier_payload(
            encoded,
            expected_command=case.verify.command,
            expected_subject=case.verify.subject,
            **args,
        )
    # Bind the original wrapper/transport bytes, never only the nested projection.
    result = result.model_copy(update={"raw_payload_sha256": _sha(raw)})
    model, refs = _model(case, experiment)
    if inner.get("admission") is not None and process_exit not in {3, 70}:
        from gnd.admission_validation import validate_admission_payload

        population = load_population(snapshot / case.verify.subject, model=model)
        metrics = validate_admission_payload(
            payload, model=model, candidate=population, references=refs
        )
        result.__pydantic_private__["_admission_metrics"] = metrics
    if refs is not None:
        owned = dict(refs._owners)
        result = result.model_copy(
            update={"coverage": {ft: row for ft, row in result.coverage.items() if ft not in owned}}
        )
    observations = observe_expected_outputs(
        case, {f.entry.path: f.entry.sha256 for f in _collect_candidate(snapshot)[1]}
    )
    result = result.model_copy(update={"expected_outputs": observations})
    if case.judgment_gate is not None:
        from gnd.exp.session_judgments import evaluate

        result = evaluate(case, result, payload, model, refs, snapshot, experiment, run_root)
    return result


_HIDDEN = object()


def _project(node, hidden):
    if isinstance(node, dict):
        if node.get("constraint_ref") in hidden:
            return _HIDDEN
        return {k: v for k, raw in node.items() if (v := _project(raw, hidden)) is not _HIDDEN}
    if isinstance(node, list):
        return [v for raw in node if (v := _project(raw, hidden)) is not _HIDDEN]
    return node


def _feedback(contract, evaluation, invocation, disposition, experiment, redaction):
    by_case = {c.case_id: c for c in contract.cases}
    operator, candidate_rows = [], []
    for result in sorted(evaluation.results, key=lambda r: r.case_id):
        hidden = set()
        case = by_case[result.case_id]
        row = _case_feedback(
            result,
            case=case,
            schema_version=7 if isinstance(case.acceptance, TransitionAcceptance) else 4,
        ).model_dump(mode="json", by_alias=True)
        model, _ = _model(case, experiment)
        details = {r.constraint_ref: r for r in result.verdict_feedback}
        findings = []
        for verdict in result.verdicts:
            annotation = constraint_annotations(model)[verdict.constraint_ref]
            owner = annotation.get("owner", "candidate")
            if owner != "candidate":
                hidden.add(verdict.constraint_ref)
            detail = details.get(verdict.constraint_ref)
            findings.append(
                {
                    **verdict.model_dump(mode="json"),
                    "owner": owner,
                    "allowed_fixes": annotation.get("allowed_fixes", []),
                    "message": "" if detail is None else detail.message,
                    "offending_facts": [] if detail is None else list(detail.offending_facts),
                }
            )
        row["constraint_findings"] = findings
        operator.append(row)
        candidate_rows.append(_project(row, hidden))
    context = {
        "base_candidate_sha256": evaluation.candidate_sha256,
        "artifacts": []
        if contract.candidate_edits is None
        else [a.model_dump(mode="json") for a in contract.candidate_edits.artifacts],
        "allowed_fixes": ["add-fact", "replace-fact", "delete-fact", "replace-artifact"],
    }
    common = {
        "schema_version": contract.profile.feedback_version,
        "run_id": experiment.name if not evaluation.results else None,
        "contract_id": contract.experiment_id,
        "contract_sha256": evaluation.contract_sha256,
        "source_attempt_index": evaluation.attempt_index,
        "candidate_sha256": evaluation.candidate_sha256,
        "case_payload_sha256s": [
            [r.case_id, r.raw_payload_sha256]
            for r in sorted(evaluation.results, key=lambda r: r.case_id)
        ],
        "normalized_verifier_signature": normalized_verifier_signature(
            contract,
            evaluation,
            schema_version=7
            if any(isinstance(c.acceptance, TransitionAcceptance) for c in contract.cases)
            else 4,
        ),
        "process_exit": invocation.exit_code,
        "payload_exit": [
            [r.case_id, r.payload_exit] for r in sorted(evaluation.results, key=lambda r: r.case_id)
        ],
        "acceptance_ready": contract_accepts(contract, evaluation),
        "disposition": disposition,
        "redaction": None if redaction is None else redaction.model_dump(mode="json"),
        "candidate_edit_context": context,
    }
    outputs = []
    for audience, rows in (
        ("operator", operator),
        ("candidate", candidate_rows),
    ):
        outputs.append(
            {
                **common,
                "audience": audience,
                "required": [r for r in rows if r["role"] == "required"],
                "diagnostic": [r for r in rows if r["role"] == "diagnostic"],
            }
        )
    if contract.profile.judgments:
        from gnd.exp.session_judgments import feedback

        outputs[0]["judgments"] = feedback(evaluation.results)
        outputs[1]["judgments"] = feedback(evaluation.results)
    return outputs


def reconstruct(store, contract, *, allow_terminal=False, policy_sha256=None):
    """Reject partial, stale or tampered evidence before another invocation."""
    store._assert_store_layout()
    if (store.root / "result.json").exists() and not allow_terminal:
        raise ValueError("terminal runs cannot resume")
    if any(store._staging_root.iterdir()):
        raise ValueError("unpublished staging state exists")
    experiment = store.root.parent.parent
    contract_path = experiment / "session.contract.json"
    if not contract_path.is_file():
        if not any(store._attempts_root.iterdir()) and not any(store._launches_root.iterdir()):
            store._best_identity = None
            store._v7_best = None
            return ResumeState(1, None, (), 0.0, None, None)
        raise ValueError("retained run requires its bound contract")
    if contract.profile.judgments:
        from gnd.exp.session_judgments import verify_authority

        verify_authority(contract, experiment, store.root)
    current = read_session_contract(
        contract_path, experiment_root=experiment, experiment_id=contract.experiment_id
    )
    bound_wall = current.wall_seconds
    if (
        contract.wall_seconds is not None
        and bound_wall is not None
        and contract.wall_seconds <= bound_wall
    ):
        current = current.model_copy(update={"wall_seconds": contract.wall_seconds})
    if current.model_dump(mode="json") != contract.model_dump(mode="json"):
        raise ValueError("resume contract differs from bound bytes")
    contract_sha = _sha(contract_path.read_bytes())
    directories = sorted(store._attempts_root.iterdir())
    launches = sorted(store._launches_root.iterdir())
    if len(launches) != len(directories):
        raise ValueError("uncommitted launch intent exists")
    best = None
    prior = None
    wall = 0.0
    pairs = {}
    for index, directory in enumerate(directories, 1):
        if directory.name != f"{index:04d}":
            raise ValueError("attempt sequence has a gap")
        raw = _read(store._attempts_root, f"{directory.name}/attempt.json")
        document = _rf7_input.loads(raw)
        document["invocation"]["stdout"] = _read(directory, document["agent_stdout"]["path"])
        document["invocation"]["stderr"] = _read(directory, document["agent_stderr"]["path"])
        record = AttemptRecord.model_validate(document)
        if (
            canonical_json_bytes(record) != raw
            or record.attempt_index != index
            or record.run_id != store.run_id
            or record.evaluation.contract_sha256 != contract_sha
        ):
            raise ValueError("attempt canonical identity differs")
        for leaf in (
            record.agent_stdout,
            record.agent_stderr,
            record.feedback,
            record.operator_feedback,
            *record.raw_verifier_payloads,
        ):
            content = _read(directory, leaf.path)
            if _sha(content) != leaf.sha256 or len(content) != leaf.size_bytes:
                raise ValueError("retained evidence leaf differs")
        launch_raw = _read(store.root, record.launch_intent.path)
        if _sha(launch_raw) != record.launch_intent.sha256:
            raise ValueError("launch evidence differs")
        from gnd.exp.session_records import DeclaredLaunchIntent

        launch = DeclaredLaunchIntent.model_validate_json(launch_raw)
        if (
            launch.schema_version != (contract.profile.launch_version)
            or launch.contract_sha256 != contract_sha
            or launch.feedback_sha256 != record.invocation.feedback_sha256
            or launch.policy_sha256 != record.invocation.policy_sha256
            or (policy_sha256 is not None and launch.policy_sha256 != policy_sha256)
        ):
            raise ValueError("launch/invocation binding differs")
        inventory, _ = _collect_candidate(directory / record.candidate_snapshot)
        if inventory != record.candidate_inventory:
            raise ValueError("snapshot inventory differs")
        edit = record.candidate_edit
        if (edit is None) != (contract.candidate_edits is None):
            raise ValueError("proposal declaration/evidence differs")
        if edit is not None and (
            edit.patch_path != contract.candidate_edits.patch_path
            or (edit.refusal is None and edit.result_candidate_sha256 != inventory.tree_sha256)
        ):
            raise ValueError("proposal path/result identity differs")
        if edit is not None and edit.patch_raw_sha256 is not None:
            proposal = _read(directory, "patch.proposal.json")
            if _sha(proposal) != edit.patch_raw_sha256:
                raise ValueError("retained proposal differs")
            if edit.refusal is None:
                base = (
                    (directory.parent / f"{index - 1:04d}/candidate")
                    if index > 1
                    else directory / "base"
                )
                base_hash = _collect_candidate(base)[0].tree_sha256
                parsed_proposal = read_patch_document(proposal)
                mode = proposal_mode(parsed_proposal, contract)
                if edit.mode != mode:
                    raise ValueError("proposal mode differs from replayed edits")
                if edit.base_candidate_sha256 != (None if index == 1 else base_hash):
                    raise ValueError("proposal base identity differs")
                files = apply_candidate_patch(
                    parsed_proposal,
                    contract=contract,
                    base_root=base,
                    base_sha256=base_hash,
                    allow_initial_seed=index == 1,
                )
                if files != {
                    f.entry.path: f.data for f in _collect_candidate(directory / "candidate")[1]
                }:
                    raise ValueError("proposal reconstruction differs")
        results = []
        for leaf in record.raw_verifier_payloads:
            case = next(c for c in contract.cases if c.case_id == leaf.case_id)
            observed = next(r for r in record.evaluation.results if r.case_id == leaf.case_id)
            results.append(
                _evaluate(
                    case,
                    _read(directory, leaf.path),
                    observed.process_exit,
                    directory / "candidate",
                    experiment,
                    inventory.tree_sha256,
                    contract_sha,
                    store.root,
                )
            )
        rebuilt = AttemptEvaluation(
            attempt_index=index,
            candidate_sha256=inventory.tree_sha256,
            contract_sha256=contract_sha,
            results=tuple(results),
        )
        if rebuilt.model_dump(mode="json") != record.evaluation.model_dump(
            mode="json"
        ) or ranking_observations(contract, rebuilt) != [
            r.model_dump(mode="json") for r in record.ranking
        ]:
            raise ValueError("retained evaluation or ranking differs")
        if contract.profile.judgments:
            from gnd.exp.session_judgments import replay

            replay(record, rebuilt, directory)
            expected_pins = {
                c.case_id: c.judgment_gate.policy.sha256
                for c in contract.cases
                if c.judgment_gate is not None
            }
            if launch.judgment_policy_sha256 != expected_pins:
                raise ValueError("launch judgment authority differs")
        record = record.model_copy(update={"evaluation": rebuilt})
        operator_raw = _read(directory, record.operator_feedback.path)
        projected_raw = _read(directory, record.feedback.path)
        operator = AttemptFeedback.model_validate_json(operator_raw)
        AttemptFeedback.model_validate_json(projected_raw)
        expected_operator, expected_projected = _feedback(
            contract, rebuilt, record.invocation, operator.disposition, experiment, record.redaction
        )
        expected_operator["run_id"] = expected_projected["run_id"] = store.run_id
        if (
            canonical_json_bytes(expected_operator) != operator_raw
            or canonical_json_bytes(expected_projected) != projected_raw
        ):
            raise ValueError("feedback differs from reconstructed evaluation")
        for name, digest in record.evidence_digests.items():
            if name not in {"evaluation", "feedback"} and (
                not name.startswith("rejected/") or _sha(_read(directory, name)) != digest
            ):
                raise ValueError("retained rejection evidence differs")
        if (
            record.evidence_digests.get("evaluation") != _sha(canonical_json_bytes(rebuilt))
            or record.evidence_digests.get("feedback") != _sha(projected_raw)
            or record.candidate_inventory_sha256 != _sha(canonical_json_bytes(inventory))
        ):
            raise ValueError("retained evidence identity differs")
        if record.best_eligible and (
            best is None or best_key(contract, rebuilt) < best_key(contract, best[0].evaluation)
        ):
            best = record, _sha(raw)
        feedback = _read(directory, record.feedback.path)
        if record.invocation.feedback_sha256 != (None if prior is None else _sha(prior)):
            raise ValueError("retry stdin feedback chain differs")
        prior = feedback
        signature = normalized_verifier_signature(
            contract,
            rebuilt,
            schema_version=7
            if any(isinstance(c.acceptance, TransitionAcceptance) for c in contract.cases)
            else 4,
        )
        pairs.setdefault((inventory.tree_sha256, signature), index)
        wall += record.elapsed_seconds
    identity = (
        None
        if best is None
        else BestAttemptIdentity(
            attempt_index=best[0].attempt_index,
            attempt_manifest_sha256=best[1],
            candidate_sha256=best[0].candidate_inventory.tree_sha256,
        )
    )
    pointer = store.root / "best.json"
    if pointer.exists() != (identity is not None):
        raise ValueError("best pointer presence differs")
    if identity is not None and _rf7_input.loads(_read(store.root, "best.json")) != identity.model_dump(
        mode="json"
    ):
        raise ValueError("best pointer differs from reconstructed rank")
    from gnd.exp.session_records import RecurrencePair

    if allow_terminal and (store.root / "result.json").exists():
        terminal = SessionResult.model_validate_json(_read(store.root, "result.json"))
        if (
            terminal.schema_version != contract.profile.result_version
            or terminal.attempt_count != len(directories)
            or terminal.best_attempt != (None if identity is None else identity.attempt_index)
            or terminal.best_attempt_manifest_sha256
            != (None if identity is None else identity.attempt_manifest_sha256)
            or terminal.best_candidate_sha256
            != (None if identity is None else identity.candidate_sha256)
            or ((terminal.disposition == "accepted") != (operator.disposition == "accepted"))
            or (terminal.disposition == "accepted"
                and not contract_accepts(contract, record.evaluation))
        ):
            raise ValueError("terminal result differs from reconstructed attempt evidence")
    if contract.profile.judgments and allow_terminal and (store.root / "result.json").exists():
        terminal = SessionResult.model_validate_json(_read(store.root, "result.json"))
        observed = (
            None
            if best is None
            else {
                r.case_id: bool(
                    r._judgment_report
                    and r._judgment_report["judgment_policy"]
                    and r._judgment_report["judgment_policy"]["admission"]
                )
                for r in best[0].evaluation.results
                if r._judgment_report is not None
            }
        )
        if (
            terminal.schema_version != 7
            or terminal.judgment_admission != observed
            or terminal.best_attempt != (None if identity is None else identity.attempt_index)
            or terminal.best_attempt_manifest_sha256
            != (None if identity is None else identity.attempt_manifest_sha256)
        ):
            raise ValueError("terminal judgment identity differs")
    store._v7_best = best
    store._best_identity = identity
    return ResumeState(
        len(directories) + 1,
        identity,
        tuple(
            RecurrencePair(
                candidate_sha256=p[0], normalized_verifier_signature=p[1], first_attempt_index=i
            )
            for p, i in pairs.items()
        ),
        wall,
        prior,
        None if prior is None else _sha(prior),
    )




# Preserve the historical public qualification of moved objects.
_read.__module__ = "gnd.exp.session_v7"
_entry.__module__ = "gnd.exp.session_v7"
_model.__module__ = "gnd.exp.session_v7"
_evaluate.__module__ = "gnd.exp.session_v7"
_project.__module__ = "gnd.exp.session_v7"
_feedback.__module__ = "gnd.exp.session_v7"
reconstruct.__module__ = "gnd.exp.session_v7"
