"""Version-7 orchestration and read-only reconstruction of its exact evidence."""

from __future__ import annotations

import asyncio
import json  # noqa: F401 -- historical compatibility binding
import stat
import tempfile
import time
from pathlib import Path

from gnd.agents import InvocationStatus
from gnd.artifacts import (
    ArtifactError,
    canonical_json_bytes,
    publish_directory_once,
    publish_leaf_atomic,
    read_regular_bounded,
)
from gnd.artifacts import (
    sha256_hex as _sha,
)
from gnd.exp.session_contract import (
    TransitionAcceptance,
)
from gnd.exp.session_eval import (
    AttemptEvaluation,
    best_key,
    case_decision,
    contract_accepts,
    normalized_verifier_signature,
    ranking_observations,
)
from gnd.exp.session_patch import (
    PatchRefusal,
    proposal_mode,
    read_patch_document,
)
from gnd.exp.session_records import (
    AttemptRecord,
    BestAttemptIdentity,
    SessionResult,
    WalkFloorResult,
    _collect_candidate,
)
from gnd.exp.session_replay import _entry as _entry  # noqa: PLC0414 -- compatibility re-export
from gnd.exp.session_replay import (
    _evaluate as _evaluate,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_replay import (
    _feedback as _feedback,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_replay import _model as _model  # noqa: PLC0414 -- compatibility re-export
from gnd.exp.session_replay import _project as _project  # noqa: PLC0414 -- compatibility re-export
from gnd.exp.session_replay import _read as _read  # noqa: PLC0414 -- compatibility re-export
from gnd.exp.session_replay import (
    reconstruct as reconstruct,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_store import SessionStore


def _copy_files(files, root, executable=()):
    root.mkdir(parents=True, exist_ok=True)
    for name, raw in files.items():
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        if name in executable:
            destination.chmod(0o755)


async def run(
    contract,
    *,
    contract_sha256,
    adapter_policy,
    prompt,
    candidate_root,
    run_root,
    verifier,
    declared_invoker,
    redaction=None,
    **unused,
):
    from gnd.exp.declared_invocation import declared_effective_prompt
    from gnd.exp.session_control import _decide_disposition, _validated_declared_invocation_proof

    if (
        adapter_policy.policy.policy_id != contract.adapter.policy_id
        or adapter_policy.model != contract.adapter.parameters.model
    ):
        raise ValueError("declared adapter policy does not match the session contract")
    candidate = Path(candidate_root).absolute()
    experiment = candidate.parent
    store = SessionStore(run_root, run_id=Path(run_root).name, contract_id=contract.experiment_id)
    if contract.profile.judgments:
        from gnd.exp.session_judgments import prepare

        prepare(contract, experiment, store.root)
    state = reconstruct(store, contract, policy_sha256=adapter_policy.policy_sha256)
    seen = {
        (p.candidate_sha256, p.normalized_verifier_signature): p.first_attempt_index
        for p in state.seen_recurrence_pairs
    }
    best = None if store.best_record() is None else (store.best_record(), store.best_identity().attempt_manifest_sha256)
    feedback_raw = state.prior_feedback_bytes
    wall = state.accounted_wall_seconds
    if state.next_attempt_index > contract.max_attempts or wall >= (contract.wall_seconds or 60):
        raise ValueError("retained run has exhausted its controller budget")
    if (
        state.next_attempt_index > 1
        and _collect_candidate(candidate)[0]
        != _collect_candidate(store.attempt_path(state.next_attempt_index - 1) / "candidate")[0]
    ):
        raise ValueError("resume inbox differs from the preceding immutable candidate")
    for index in range(state.next_attempt_index, contract.max_attempts + 1):
        started = time.monotonic()
        inventory, original = _collect_candidate(candidate)
        before = {f.entry.path: f.data for f in original}
        feedback_sha = None if feedback_raw is None else _sha(feedback_raw)
        effective = declared_effective_prompt(
            prompt,
            policy_kind=adapter_policy.policy.kind,
            feedback_bytes=feedback_raw,
            feedback_sha256=feedback_sha,
        )
        store.publish_declared_launch_intent(
            attempt_index=index,
            contract_sha256=contract_sha256,
            policy_id=adapter_policy.policy.policy_id,
            policy_kind=adapter_policy.policy.kind,
            policy_sha256=adapter_policy.policy_sha256,
            model_sha256=None
            if adapter_policy.model is None
            else _sha(adapter_policy.model.encode()),
            base_prompt_sha256=_sha(prompt.encode()),
            controller_prompt_sha256=_sha(prompt.encode()),
            effective_prompt_sha256=_sha(effective.encode()),
            feedback_sha256=feedback_sha,
            candidate_root=candidate,
            schema_version=contract.profile.launch_version,
            judgment_policy_sha256={
                c.case_id: c.judgment_gate.policy.sha256
                for c in contract.cases
                if c.judgment_gate is not None
            },
        )
        timeout = min(10.0, (contract.wall_seconds or 60) - wall)
        invocation = await asyncio.wait_for(
            declared_invoker(
                adapter_policy,
                prompt=prompt,
                cwd=candidate,
                timeout_seconds=timeout,
                feedback_bytes=feedback_raw,
                feedback_sha256=feedback_sha,
            ),
            timeout=timeout,
        )
        invocation = _validated_declared_invocation_proof(
            invocation,
            policy=adapter_policy,
            prompt=prompt,
            feedback_bytes=feedback_raw,
            feedback_sha256=feedback_sha,
        )
        edit = None
        proposal_raw = None
        refusal = None
        with tempfile.TemporaryDirectory(prefix="gnd-v7-base-") as temporary:
            base = Path(temporary).resolve()
            executable = {f.entry.path for f in original if f.entry.executable}
            _copy_files(before, base, executable)
            mode = "complete" if index == 1 else "patch"
            if contract.candidate_edits is not None:
                patch_path = contract.candidate_edits.patch_path
                observation = {}
                try:
                    leaf_stat = (candidate / patch_path).lstat()
                    observation = {
                        "observed_leaf_size_bytes": leaf_stat.st_size,
                        "leaf_kind": "regular"
                        if stat.S_ISREG(leaf_stat.st_mode)
                        else "symlink"
                        if stat.S_ISLNK(leaf_stat.st_mode)
                        else "special",
                    }
                    proposal_raw = _read(candidate, patch_path)
                    after = {
                        f.entry.path: f.data
                        for f in _collect_candidate(candidate)[1]
                        if f.entry.path != patch_path
                    }
                    protected_modes = {
                        f.entry.path: f.entry.executable
                        for f in _collect_candidate(candidate)[1]
                        if f.entry.path != patch_path
                    }
                    if after != before or protected_modes != {
                        f.entry.path: f.entry.executable for f in original
                    }:
                        raise PatchRefusal("protected", "producer changed protected inbox bytes")
                    proposal = read_patch_document(proposal_raw)
                    mode = proposal_mode(proposal, contract)
                    staged = store.stage_patch_candidate(
                        attempt_index=index,
                        base_root=base,
                        base_sha256=inventory.tree_sha256,
                        proposal_raw=proposal_raw,
                        contract=contract,
                    )
                except (ArtifactError, ValueError, OSError) as error:
                    refusal = (
                        error.reason
                        if isinstance(error, PatchRefusal)
                        else "limit"
                        if any(t in str(error) for t in ("cap", "exceed", "limit"))
                        else "path"
                    )
                    staged = store.stage_candidate(attempt_index=index, candidate_root=base)
                edit = {
                    "mode": mode,
                    "patch_path": patch_path,
                    "patch_raw_sha256": None if proposal_raw is None else _sha(proposal_raw),
                    "base_candidate_sha256": None if index == 1 else inventory.tree_sha256,
                    "result_candidate_sha256": None if refusal else staged.inventory.tree_sha256,
                    "refusal": refusal,
                }
            else:
                staged = store.stage_candidate(attempt_index=index, candidate_root=candidate)
            raw_payloads, results = {}, []
            verifier_failed = False
            deadline_expired = False
            rejected = {}
            if refusal is not None and proposal_raw is None:
                rejected["proposal"] = {
                    "refusal": refusal,
                    "truncated": True,
                    "non_replayable": True,
                    **observation,
                }
            if refusal is None and invocation.status is InvocationStatus.succeeded:
                for case in contract.cases:
                    try:
                        if contract.profile.judgments:
                            from gnd.exp.session_judgments import verify_authority

                            verify_authority(contract, experiment, store.root)
                        exit_code, raw = await asyncio.wait_for(
                            verifier(case, staged.snapshot_path),
                            timeout=max(
                                0.0,
                                (contract.wall_seconds or 60) - wall - (time.monotonic() - started),
                            ),
                        )
                        raw_payloads[case.case_id] = bytes(raw)
                        results.append(
                            _evaluate(
                                case,
                                bytes(raw),
                                exit_code,
                                staged.snapshot_path,
                                experiment,
                                staged.inventory.tree_sha256,
                                contract_sha256,
                                store.root,
                            )
                        )
                    except (ValueError, OSError, TypeError, KeyError, RuntimeError) as error:
                        rejected[case.case_id] = {
                            "failure": type(error).__name__,
                            "process_exit": exit_code if case.case_id in raw_payloads else None,
                        }
                        verifier_failed = True
                        deadline_expired = deadline_expired or isinstance(error, TimeoutError)
            evaluation = AttemptEvaluation(
                attempt_index=index,
                candidate_sha256=staged.inventory.tree_sha256,
                contract_sha256=contract_sha256,
                results=tuple(sorted(results, key=lambda r: r.case_id)),
            )
            accepted = contract_accepts(contract, evaluation) if results else False
            signature = normalized_verifier_signature(
                contract,
                evaluation,
                schema_version=7
                if any(isinstance(c.acceptance, TransitionAcceptance) for c in contract.cases)
                else 4,
            )
            pair = staged.inventory.tree_sha256, signature
            prior = seen.get(pair)
            elapsed = time.monotonic() - started
            wall += elapsed
            decision = _decide_disposition(
                invocation=invocation,
                accepted=accepted,
                explicit_wall_expiry=deadline_expired,
                wall_bound_hit=wall >= (contract.wall_seconds or 60),
                verifier_failed=verifier_failed or len(results) != len(contract.cases),
                recurrence_disposition=None
                if prior is None
                else "stagnation"
                if prior == index - 1
                else "oscillation",
                recurrence_first_seen=prior,
                attempt_bound_hit=index == contract.max_attempts,
            )
            disposition = "agent-failure" if refusal is not None else decision.value
            operator, projected = _feedback(
                contract, evaluation, invocation, disposition, experiment, redaction
            )
            operator["run_id"] = projected["run_id"] = store.run_id
            operator_raw, feedback_raw = (
                canonical_json_bytes(operator),
                canonical_json_bytes(projected),
            )
            files = {
                "candidate/" + f.entry.path: f.data
                for f in _collect_candidate(staged.snapshot_path)[1]
            }
            if index == 1 and contract.candidate_edits is not None:
                files.update({"base/" + name: raw for name, raw in before.items()})
            files.update(
                {
                    "feedback.json": feedback_raw,
                    "operator-feedback.json": operator_raw,
                    "agent.stdout": invocation.stdout,
                    "agent.stderr": invocation.stderr,
                }
            )
            if proposal_raw is not None:
                files["patch.proposal.json"] = proposal_raw
            raw_entries = []
            for case_id, raw in sorted(raw_payloads.items()):
                # Only validated payloads may become current evidence.
                if not any(r.case_id == case_id for r in results):
                    continue
                name = f"verifier/{case_id}.json"
                files[name] = raw
                raw_entries.append({**_entry(name, raw), "case_id": case_id})
            rejection_digests = {}
            for case_id, failure in rejected.items():
                name = f"rejected/{case_id}.json"
                files[name] = canonical_json_bytes(failure)
                rejection_digests[name] = _sha(files[name])
                if case_id in raw_payloads:
                    name = f"rejected/{case_id}.raw"
                    files[name] = raw_payloads[case_id]
                    rejection_digests[name] = _sha(files[name])
            launch_name = f"launches/{index:04d}.json"
            launch_raw = _read(store.root, launch_name)
            rankings = ranking_observations(contract, evaluation)
            eligible = (
                refusal is None
                and invocation.status is InvocationStatus.succeeded
                and len(results) == len(contract.cases)
                and not verifier_failed
            )
            judgment_evidence = {}
            for r in results:
                if r._judgment_files is not None:
                    files.update(r._judgment_files[0])
                    judgment_evidence[r.case_id] = r._judgment_files[1]
            record = AttemptRecord(
                schema_version=contract.profile.attempt_version,
                feedback_schema_version=contract.profile.feedback_version,
                judgment_evidence=judgment_evidence,
                run_id=store.run_id,
                attempt_index=index,
                elapsed_seconds=elapsed,
                invocation=invocation,
                launch_intent=_entry(launch_name, launch_raw),
                candidate_inventory=staged.inventory,
                candidate_inventory_sha256=_sha(canonical_json_bytes(staged.inventory)),
                candidate_snapshot="candidate",
                agent_stdout=_entry("agent.stdout", invocation.stdout),
                agent_stderr=_entry("agent.stderr", invocation.stderr),
                raw_verifier_payloads=tuple(raw_entries),
                evaluation=evaluation,
                feedback=_entry("feedback.json", feedback_raw),
                operator_feedback=_entry("operator-feedback.json", operator_raw),
                best_eligible=eligible,
                candidate_edit=edit,
                ranking=rankings,
                redaction=redaction,
                evidence_digests={
                    "evaluation": _sha(canonical_json_bytes(evaluation)),
                    "feedback": _sha(feedback_raw),
                    **rejection_digests,
                },
                assurance_receipts=(),
            )
            record_raw = canonical_json_bytes(record)
            files["attempt.json"] = record_raw
            try:
                publish_directory_once(
                    store._attempts_root,
                    f"{index:04d}",
                    files,
                    manifest_name="attempt.json",
                    max_files=22000,
                    max_total_bytes=240 * 1024 * 1024,
                    executable_paths={
                        "candidate/" + f.path for f in staged.inventory.files if f.executable
                    }
                    | ({"base/" + name for name in executable} if index == 1 else set()),
                    expected_root=store._directory_identities[store._attempts_root],
                )
            except BaseException:
                store._discard_staged(index, staged)
                raise
            if contract.candidate_edits is not None and refusal is None:
                # The producer inbox is a disposable full copy of the committed snapshot.
                import os

                from gnd.artifacts import _clear_directory_fd, _open_root, _write_new_file_at

                fd = _open_root(candidate)
                try:
                    _clear_directory_fd(fd)
                    for leaf in _collect_candidate(staged.snapshot_path)[1]:
                        _write_new_file_at(
                            fd,
                            tuple(leaf.entry.path.split("/")),
                            leaf.data,
                            mode=0o755 if leaf.entry.executable else 0o644,
                        )
                finally:
                    os.close(fd)
            store._discard_staged(index, staged)
            if eligible and (
                best is None
                or best_key(contract, evaluation) < best_key(contract, best[0].evaluation)
            ):
                best = record, _sha(record_raw)
                identity = BestAttemptIdentity(
                    attempt_index=index,
                    attempt_manifest_sha256=best[1],
                    candidate_sha256=evaluation.candidate_sha256,
                )
                publish_leaf_atomic(
                    store.root,
                    "best.json",
                    canonical_json_bytes(identity),
                    expected=None
                    if not (store.root / "best.json").exists()
                    else read_regular_bounded(store.root, "best.json", max_bytes=1024 * 1024)[1],
                    expected_root=store._directory_identities[store.root],
                )
            if not (contract.profile.judgments and verifier_failed):
                reconstruct(store, contract, policy_sha256=adapter_policy.policy_sha256)
            if disposition != "retry":
                result = SessionResult(
                    schema_version=contract.profile.result_version,
                    judgment_admission=None
                    if not contract.profile.judgments or best is None
                    else {
                        r.case_id: bool(
                            r._judgment_report
                            and r._judgment_report["judgment_policy"]
                            and r._judgment_report["judgment_policy"]["admission"]
                        )
                        for r in best[0].evaluation.results
                        if r._judgment_report is not None
                    },
                    run_id=store.run_id,
                    disposition=disposition,
                    terminal_reason="proposal refused: " + str(refusal)
                    if refusal
                    else decision.reason,
                    attempt_count=index,
                    best_attempt=None if best is None else best[0].attempt_index,
                    best_attempt_manifest_sha256=None if best is None else best[1],
                    best_candidate_sha256=None
                    if best is None
                    else best[0].candidate_inventory.tree_sha256,
                    referenced_evidence_digests={"attempt_manifest_sha256": _sha(record_raw)},
                    acceptance_modes=tuple(sorted({c.acceptance.mode for c in contract.cases})),
                    redaction=redaction,
                    contract_sha256=contract_sha256,
                    walk_floors=tuple(
                        WalkFloorResult(
                            case_id=c.case_id,
                            role=c.role.value,
                            required_ops=len(c.acceptance.walk.required_ops),
                            forbidden_ops=len(c.acceptance.walk.forbidden_ops),
                            discharged=best is not None
                            and any(
                                r.case_id == c.case_id and case_decision(c, r).accepted
                                for r in best[0].evaluation.results
                            ),
                        )
                        for c in sorted(contract.cases, key=lambda c: c.case_id)
                        if isinstance(c.acceptance, TransitionAcceptance)
                        and c.acceptance.walk is not None
                    ),
                    ranking_policy=None
                    if contract.ranking is None
                    else tuple(r.model_dump(mode="json") for r in contract.ranking),
                    best_ranking=None if best is None else best[0].ranking,
                )
                publish_leaf_atomic(
                    store.root,
                    "result.json",
                    canonical_json_bytes(result),
                    expected_root=store._directory_identities[store.root],
                )
                return result
            seen.setdefault(pair, index)
    raise RuntimeError("positive attempt bound exhausted without terminal result")


# Preserve the historical public qualification of moved objects.
_copy_files.__module__ = "gnd.exp.session_v7"
run.__module__ = "gnd.exp.session_v7"
