







from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path
from typing import Annotated, Any, get_args, get_origin

import pytest
from support.digests import sha256_bytes as _sha256

from gnd.exp.session_contract import (
    DataDrivenContract,
    SessionContractError,
    read_session_contract,
)
from gnd.exp.session_store import (
    AttemptRecord,
    BestAttemptIdentity,
    CandidateInventory,
    LaunchIntent,
    SessionOutcome,
    SessionResult,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS = REPO_ROOT / "tests" / "fixtures" / "phase4_reference" / "session.json"

REFERENCE_SHAPES = {
    "session-exact-all-required-acceptance": (
        SessionOutcome.accepted,
        (True,),
        1,
    ),
    "session-missing-required-output": (
        SessionOutcome.verifier_failure,
        (False,),
        None,
    ),
    "session-malformed-exit-mismatch": (
        SessionOutcome.verifier_failure,
        (True,),
        None,
    ),
    "session-alethic-indeterminate-deontic-warning": (
        SessionOutcome.budget_exhausted,
        (True,),
        1,
    ),
    "session-same-score-different-candidate": (
        SessionOutcome.budget_exhausted,
        (True, True),
        1,
    ),
    "session-a-b-a-oscillation": (
        SessionOutcome.oscillation,
        (True, True, True),
        1,
    ),
    "session-attempt-wall-exhaustion-descendant-cleanup": (
        SessionOutcome.budget_exhausted,
        (False,),
        None,
    ),
    "session-stdout-stderr-flood": (
        SessionOutcome.agent_failure,
        (False,),
        None,
    ),
    "session-declared-output-differs-from-expectation": (
        SessionOutcome.budget_exhausted,
        (True,),
        1,
    ),
    "session-declared-output-never-produced": (
        SessionOutcome.budget_exhausted,
        (True,),
        1,
    ),
}



EXPECTED_OUTPUT_CASES = {
    "session-declared-output-differs-from-expectation",
    "session-declared-output-never-produced",
}

EDGE_MODELS = {
    model.__name__: model
    for model in (
        DataDrivenContract,
        LaunchIntent,
        AttemptRecord,
        CandidateInventory,
        BestAttemptIdentity,
        SessionResult,
    )
}


def _bound(path: str, data: bytes, *, media_type: str) -> dict[str, Any]:
    return {
        "path": path,
        "media_type": media_type,
        "encoding": "utf-8",
        "sha256": _sha256(data),
        "size_bytes": len(data),
    }


def _expected(
    path: str,
    data: bytes,
    *,
    media_type: str,
    output_id: str,
    candidate_path: str,
    comparison: str = "exact-bytes",
) -> dict[str, Any]:


    return {
        **_bound(path, data, media_type=media_type),
        "output_id": output_id,
        "candidate_path": candidate_path,
        "comparison": comparison,
    }


def _contract_document(root: Path) -> dict[str, Any]:
    inputs = root / "inputs"
    expected = root / "expected"
    inputs.mkdir(parents=True)
    expected.mkdir()
    input_bytes = b'{"request":"hello"}\n'
    expected_bytes = b'{"response":"world"}\n'
    model_bytes = (REPO_ROOT / "tests/fixtures/skeleton/model.orm.yaml").read_bytes()
    (inputs / "case.json").write_bytes(input_bytes)
    (expected / "case.json").write_bytes(expected_bytes)
    (root / "model.orm.yaml").write_bytes(model_bytes)
    return {
        "schema_version": 1,
        "experiment_id": "EXP-001-session",
        "max_attempts": 2,
        "wall_seconds": 30.0,
        "cases": [
            {
                "case_id": "required-case",
                "role": "required",
                "inputs": [
                    _bound(
                        "inputs/case.json",
                        input_bytes,
                        media_type="application/json",
                    )
                ],
                "expected_outputs": [
                    _expected(
                        "expected/case.json",
                        expected_bytes,
                        media_type="application/json",
                        output_id="required-output",
                        candidate_path="output.json",
                    )
                ],
                "verify": {
                    "command": "check",
                    "model": _bound("model.orm.yaml", model_bytes, media_type="application/yaml"),
                    "subject": "candidate/output.json",
                },
            },
            {
                "case_id": "diagnostic-case",
                "role": "diagnostic",
                "inputs": [
                    _bound(
                        "inputs/case.json",
                        input_bytes,
                        media_type="application/json",
                    )
                ],
                "expected_outputs": [
                    _expected(
                        "expected/case.json",
                        expected_bytes,
                        media_type="application/json",
                        output_id="diagnostic-output",
                        candidate_path="extracted.population.json",
                    )
                ],
                "verify": {
                    "command": "verify",
                    "model": _bound("model.orm.yaml", model_bytes, media_type="application/yaml"),
                    "subject": "candidate/extracted.population.json",
                },
            },
        ],
    }


def _constraint_contract_document(root: Path) -> dict[str, Any]:
    inputs = root / "inputs"
    inputs.mkdir(parents=True)
    input_bytes = b'{"request":"write a population"}\n'
    model_bytes = (REPO_ROOT / "tests/fixtures/skeleton/model.orm.yaml").read_bytes()
    (inputs / "case.json").write_bytes(input_bytes)
    (root / "model.orm.yaml").write_bytes(model_bytes)
    return {
        "schema_version": 2,
        "experiment_id": "EXP-001-session",
        "max_attempts": 2,
        "wall_seconds": 30.0,
        "cases": [
            {
                "case_id": "required-case",
                "role": "required",
                "inputs": [
                    _bound("inputs/case.json", input_bytes, media_type="application/json")
                ],
                "acceptance": {
                    "mode": "constraint-satisfaction",
                    "coverage": [{"fact_type": "movie_has_title", "min_facts": 2}],
                },
                "verify": {
                    "command": "check",
                    "model": _bound(
                        "model.orm.yaml", model_bytes, media_type="application/yaml"
                    ),
                    "subject": "population.yaml",
                },
            }
        ],
    }


def _v2_exact_contract_document(root: Path) -> dict[str, Any]:
    document = _contract_document(root)
    document["schema_version"] = 2
    for case in document["cases"]:
        case["acceptance"] = {
            "mode": "exact-bytes",
            "expected_outputs": case.pop("expected_outputs"),
        }
    return document


def _write_contract(root: Path, document: dict[str, Any]) -> Path:
    path = root / "session.contract.json"
    path.write_text(json.dumps(document, ensure_ascii=False, allow_nan=True), encoding="utf-8")
    return path


def _read(root: Path, document: dict[str, Any]) -> DataDrivenContract:
    return read_session_contract(
        _write_contract(root, document),
        experiment_root=root,
        experiment_id="EXP-001-session",
    )


def test_valid_contract_loads_with_a_fixed_nonempty_required_denominator(
    tmp_path: Path,
) -> None:
    contract = _read(tmp_path, _contract_document(tmp_path))

    assert contract.schema_version == 1
    assert contract.experiment_id == "EXP-001-session"
    assert contract.max_attempts == 2
    assert contract.wall_seconds == 30.0
    assert [case.case_id for case in contract.cases] == [
        "required-case",
        "diagnostic-case",
    ]
    assert [case.case_id for case in contract.required_cases] == ["required-case"]


def test_v1_dispatch_normalizes_to_exact_acceptance_without_changing_wire_shape(
    tmp_path: Path,
) -> None:
    document = _contract_document(tmp_path)

    contract = _read(tmp_path, document)

    assert contract.cases[0].acceptance.mode == "exact-bytes"
    assert contract.model_dump(mode="json") == document


def test_v2_constraint_acceptance_loads_without_an_expected_output(tmp_path: Path) -> None:
    document = _constraint_contract_document(tmp_path)

    contract = _read(tmp_path, document)

    case = contract.cases[0]
    assert contract.schema_version == 2
    assert case.acceptance.mode == "constraint-satisfaction"
    assert case.expected_outputs == ()
    assert contract.model_dump(mode="json") == document


def test_v2_exact_acceptance_retains_the_exact_output_contract(tmp_path: Path) -> None:
    document = _v2_exact_contract_document(tmp_path)

    contract = _read(tmp_path, document)

    case = contract.cases[0]
    assert case.acceptance.mode == "exact-bytes"
    assert case.expected_outputs == case.acceptance.expected_outputs
    assert contract.model_dump(mode="json") == document


@pytest.mark.parametrize(
    ("document_factory", "mutation", "needle"),
    [
        pytest.param(
            _v2_exact_contract_document,
            lambda doc: doc["cases"][0]["acceptance"].update(expected_outputs=[]),
            "expected_outputs",
            id="v2-exact-requires-output",
        ),
        pytest.param(
            _contract_document,
            lambda doc: doc["cases"][0].update(
                acceptance={"mode": "exact-bytes", "expected_outputs": []}
            ),
            "acceptance",
            id="v1-forbids-v2-acceptance",
        ),
        pytest.param(
            _v2_exact_contract_document,
            lambda doc: doc["cases"][0].update(expected_outputs=[]),
            "expected_outputs",
            id="v2-forbids-v1-output-field",
        ),
    ],
)
def test_contract_versions_dispatch_to_separate_closed_readers(
    tmp_path: Path, document_factory, mutation, needle: str
) -> None:
    document = document_factory(tmp_path)
    mutation(document)

    with pytest.raises(SessionContractError) as caught:
        _read(tmp_path, document)

    rendered = " ".join(f"{issue.path} {issue.message}" for issue in caught.value.issues)
    assert needle.lower() in rendered.lower()


@pytest.mark.parametrize(
    ("mutation", "needle"),
    [
        pytest.param(
            lambda doc: doc["cases"][0]["acceptance"].update(mode="equivalent"),
            "mode",
            id="unknown-mode",
        ),
        pytest.param(
            lambda doc: doc["cases"][0]["acceptance"].update(coverage=[]),
            "coverage",
            id="missing-floor",
        ),
        pytest.param(
            lambda doc: doc["cases"][0]["acceptance"]["coverage"].append(
                {"fact_type": "movie_has_title", "min_facts": 3}
            ),
            "duplicate",
            id="duplicate-fact-type",
        ),
        pytest.param(
            lambda doc: doc["cases"][0]["acceptance"]["coverage"][0].update(
                fact_type="unknown_fact"
            ),
            "unknown model fact type",
            id="unknown-fact-type",
        ),
        pytest.param(
            lambda doc: doc["cases"][0]["acceptance"]["coverage"][0].update(
                min_facts=0
            ),
            "min_facts",
            id="floor-below-one",
        ),
        pytest.param(
            lambda doc: doc["cases"][0]["verify"].update(command="verify"),
            "requires verifier command 'check'",
            id="verify-command-forbidden",
        ),
        pytest.param(
            lambda doc: doc["cases"][0].update(expected_outputs=[]),
            "expected_outputs",
            id="legacy-output-field-forbidden",
        ),
    ],
)
def test_v2_constraint_acceptance_union_is_closed_before_launch(
    tmp_path: Path, mutation, needle: str
) -> None:
    document = _constraint_contract_document(tmp_path)
    mutation(document)

    with pytest.raises(SessionContractError) as caught:
        _read(tmp_path, document)

    rendered = " ".join(f"{issue.path} {issue.message}" for issue in caught.value.issues)
    assert needle.lower() in rendered.lower()


@pytest.mark.parametrize(
    ("target", "field", "value"),
    [
        pytest.param("root", "unexpected", True, id="root"),
        pytest.param("case", "executable", "codex", id="case-executable"),
        pytest.param("input", "argv", ["--danger"], id="input-argv"),
        pytest.param("verify", "shell", "rm -rf x", id="verify-shell"),
        pytest.param("verify", "environment", {"TOKEN": "secret"}, id="verify-environment"),
    ],
)
def test_unknown_nested_keys_and_process_injection_are_rejected(
    tmp_path: Path, target: str, field: str, value: Any
) -> None:
    document = _contract_document(tmp_path)
    nodes = {
        "root": document,
        "case": document["cases"][0],
        "input": document["cases"][0]["inputs"][0],
        "verify": document["cases"][0]["verify"],
    }
    nodes[target][field] = value

    with pytest.raises(SessionContractError) as caught:
        _read(tmp_path, document)

    assert caught.value.issues
    assert any(field in issue.path for issue in caught.value.issues)


@pytest.mark.parametrize(
    ("mutation", "needle"),
    [
        pytest.param(lambda doc: doc.update(schema_version=3), "schema_version", id="version"),
        pytest.param(lambda doc: doc.update(max_attempts=0), "max_attempts", id="attempt-zero"),
        pytest.param(lambda doc: doc.update(wall_seconds=0.0), "wall_seconds", id="wall-zero"),
        pytest.param(
            lambda doc: doc.update(wall_seconds=float("inf")), "wall_seconds", id="wall-infinite"
        ),
        pytest.param(
            lambda doc: doc.update(wall_seconds=float("nan")), "wall_seconds", id="wall-nan"
        ),
        pytest.param(
            lambda doc: doc["cases"].append(copy.deepcopy(doc["cases"][0])),
            "duplicate",
            id="duplicate-case",
        ),
        pytest.param(
            lambda doc: [case.update(role="diagnostic") for case in doc["cases"]],
            "required",
            id="no-required",
        ),
        pytest.param(
            lambda doc: doc["cases"][0].update(role="held-out"),
            "role",
            id="open-role-vocabulary",
        ),
        pytest.param(
            lambda doc: doc["cases"][0]["verify"].update(command="run"),
            "command",
            id="new-verifier-vocabulary",
        ),
    ],
)
def test_contract_nonvacuity_identity_and_bounds_are_closed(
    tmp_path: Path, mutation, needle: str
) -> None:
    document = _contract_document(tmp_path)
    mutation(document)

    with pytest.raises(SessionContractError) as caught:
        _read(tmp_path, document)

    rendered = " ".join(f"{issue.path} {issue.message}" for issue in caught.value.issues).lower()
    assert needle.lower() in rendered


def test_experiment_identity_is_bound_by_the_caller_not_trusted_from_bytes(
    tmp_path: Path,
) -> None:
    document = _contract_document(tmp_path)
    document["experiment_id"] = "EXP-999-other"

    with pytest.raises(SessionContractError) as caught:
        _read(tmp_path, document)

    assert any("experiment_id" in issue.path for issue in caught.value.issues)


@pytest.mark.parametrize(
    "unsafe",
    [
        "/absolute/input.json",
        "../escape.json",
        "a/../../escape.json",
        "C:\\Windows\\input.json",
        "C:drive-relative.json",
        "\\\\server\\share\\input.json",
        "nul\x00byte.json",
        "",
        "   ",
    ],
)
def test_unsafe_digest_bound_paths_are_rejected(tmp_path: Path, unsafe: str) -> None:
    document = _contract_document(tmp_path)
    document["cases"][0]["inputs"][0]["path"] = unsafe

    with pytest.raises(SessionContractError):
        _read(tmp_path, document)


def test_symlinked_ancestor_is_rejected_even_when_target_bytes_match(
    tmp_path: Path,
) -> None:
    document = _contract_document(tmp_path)
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    data = b'{"request":"outside"}\n'
    (outside / "case.json").write_bytes(data)
    inputs = tmp_path / "inputs"
    (inputs / "case.json").unlink()
    inputs.rmdir()
    inputs.symlink_to(outside, target_is_directory=True)
    document["cases"][0]["inputs"][0] = _bound(
        "inputs/case.json", data, media_type="application/json"
    )

    with pytest.raises(SessionContractError) as caught:
        _read(tmp_path, document)

    assert any("symlink" in issue.message.lower() for issue in caught.value.issues)


@pytest.mark.parametrize("field", ["sha256", "size_bytes"])
def test_every_committed_input_is_recomputed_before_use(tmp_path: Path, field: str) -> None:
    document = _contract_document(tmp_path)
    document["cases"][0]["inputs"][0][field] = "f" * 64 if field == "sha256" else 999

    with pytest.raises(SessionContractError) as caught:
        _read(tmp_path, document)

    assert any(field in issue.path for issue in caught.value.issues)


def test_valid_contract_carries_where_and_how_each_expectation_is_compared(
    tmp_path: Path,
) -> None:
    contract = _read(tmp_path, _contract_document(tmp_path))

    declared = contract.cases[0].expected_outputs
    assert [output.output_id for output in declared] == ["required-output"]
    assert [output.candidate_path for output in declared] == ["output.json"]
    assert [output.comparison for output in declared] == ["exact-bytes"]
    assert set(type(declared[0]).model_fields) == {
        "path",
        "media_type",
        "encoding",
        "sha256",
        "size_bytes",
        "output_id",
        "candidate_path",
        "comparison",
    }


def test_duplicate_expected_output_id_inside_one_case_is_refused(tmp_path: Path) -> None:
    document = _contract_document(tmp_path)
    case = document["cases"][0]
    case["expected_outputs"].append(copy.deepcopy(case["expected_outputs"][0]))

    with pytest.raises(SessionContractError) as caught:
        _read(tmp_path, document)

    rendered = " ".join(f"{issue.path} {issue.message}" for issue in caught.value.issues).lower()
    assert "duplicate" in rendered
    assert "required-output" in rendered


@pytest.mark.parametrize(
    "unsafe",
    [
        "/absolute/output.json",
        "../escape.json",
        "a/../../escape.json",
        "C:\\Windows\\output.json",
        "C:drive-relative.json",
        "\\\\server\\share\\output.json",
        "nul\x00byte.json",
        "   ",
    ],
)
def test_unsafe_expected_output_candidate_path_is_refused_by_position(
    tmp_path: Path, unsafe: str
) -> None:
    document = _contract_document(tmp_path)
    document["cases"][0]["expected_outputs"][0]["candidate_path"] = unsafe

    with pytest.raises(SessionContractError) as caught:
        _read(tmp_path, document)

    assert any(
        issue.path == "cases.0.expected_outputs.0.candidate_path"
        for issue in caught.value.issues
    )


@pytest.mark.parametrize(
    "mutation",
    [
        pytest.param(
            lambda output: output.pop("comparison"),
            id="omitted",
        ),
        pytest.param(
            lambda output: output.update(comparison="semantic-equivalence"),
            id="undeclared-equivalence",
        ),
        pytest.param(
            lambda output: output.update(comparison=None),
            id="null",
        ),
    ],
)
def test_comparison_semantics_cannot_arrive_as_a_silent_default(
    tmp_path: Path, mutation
) -> None:
    document = _contract_document(tmp_path)
    mutation(document["cases"][0]["expected_outputs"][0])

    with pytest.raises(SessionContractError) as caught:
        _read(tmp_path, document)

    assert any("comparison" in issue.path for issue in caught.value.issues)


@pytest.mark.parametrize("field", ["sha256", "size_bytes"])
def test_every_committed_expectation_is_recomputed_before_use(
    tmp_path: Path, field: str
) -> None:
    document = _contract_document(tmp_path)
    document["cases"][0]["expected_outputs"][0][field] = "f" * 64 if field == "sha256" else 999

    with pytest.raises(SessionContractError) as caught:
        _read(tmp_path, document)

    assert any(
        issue.path == f"cases.0.expected_outputs.0.{field}" for issue in caught.value.issues
    )


def test_tampered_expectation_bytes_still_fail_integrity_validation(tmp_path: Path) -> None:
    document = _contract_document(tmp_path)
    (tmp_path / "expected" / "case.json").write_bytes(b'{"response":"tampered"}\n')

    with pytest.raises(SessionContractError) as caught:
        _read(tmp_path, document)

    assert any(
        issue.path.startswith("cases.0.expected_outputs.0.") for issue in caught.value.issues
    )


def test_declared_oversize_input_is_rejected_before_a_controller_reads_it(
    tmp_path: Path,
) -> None:
    document = _contract_document(tmp_path)
    
    
    document["cases"][0]["inputs"][0]["size_bytes"] = 10 * 1024 * 1024 + 1

    with pytest.raises(SessionContractError) as caught:
        _read(tmp_path, document)

    assert any("size_bytes" in issue.path for issue in caught.value.issues)


def _without_annotated(annotation: Any) -> Any:
    while get_origin(annotation) is Annotated:
        annotation = get_args(annotation)[0]
    return annotation


def _runtime_field_path_exists(model: type[Any], expression: str) -> bool:


    annotation: Any = model
    parts = expression.split(".")
    for position, raw_part in enumerate(parts):
        annotation = _without_annotated(annotation)
        origin = get_origin(annotation)
        if origin is dict:
            return position == len(parts) - 1 and bool(raw_part) and not raw_part.endswith("[]")
        fields = getattr(annotation, "model_fields", None)
        if fields is None:
            return False
        many = raw_part.endswith("[]")
        name = raw_part.removesuffix("[]")
        field = fields.get(name)
        if field is None:
            return False
        annotation = _without_annotated(field.annotation)
        if many:
            origin = get_origin(annotation)
            if origin not in {list, tuple, set, frozenset}:
                return False
            arguments = get_args(annotation)
            if not arguments:
                return False
            annotation = arguments[0]
    return True


def _expected_digest_edges(
    row: dict[str, Any], attempts: list[dict[str, Any]], best_attempt: int | None
) -> set[tuple[str, str, str, str]]:
    contract_path = row["expected_evidence"]["session_contract_path"]
    edges = {
        (blob["path"], contract_path, "DataDrivenContract", "cases[].inputs[].sha256")
        for blob in row["input_blobs"]
    }
    
    
    
    
    expected_blobs = row.get("expected_output_blobs", [])
    edges.update(
        (
            blob["path"],
            contract_path,
            "DataDrivenContract",
            "cases[].expected_outputs[].sha256",
        )
        for blob in expected_blobs
    )
    edges.update(
        (
            blob["path"],
            attempt["candidate_inventory_path"],
            "CandidateInventory",
            "files[].sha256",
        )
        for blob in expected_blobs
        for attempt in attempts
    )
    for attempt in attempts:
        manifest = attempt["attempt_manifest_path"]
        inventory = attempt["candidate_inventory_path"]
        launch = attempt["launch_intent_path"]
        edges.update(
            {
                (contract_path, launch, "LaunchIntent", "contract_sha256"),
                (launch, manifest, "AttemptRecord", "launch_intent.sha256"),
                (
                    inventory,
                    manifest,
                    "AttemptRecord",
                    "candidate_inventory_sha256",
                ),
                (
                    attempt["agent_stdout_path"],
                    manifest,
                    "AttemptRecord",
                    "agent_stdout.sha256",
                ),
                (
                    attempt["agent_stderr_path"],
                    manifest,
                    "AttemptRecord",
                    "agent_stderr.sha256",
                ),
                (
                    attempt["feedback_path"],
                    manifest,
                    "AttemptRecord",
                    "feedback.sha256",
                ),
            }
        )
        edges.update(
            (
                snapshot,
                inventory,
                "CandidateInventory",
                "files[].sha256",
            )
            for snapshot in attempt["candidate_snapshot_paths"]
        )
        edges.update(
            (
                payload,
                manifest,
                "AttemptRecord",
                "raw_verifier_payloads[].sha256",
            )
            for payload in attempt["verifier_payload_paths"]
        )
    terminal_manifest = attempts[-1]["attempt_manifest_path"]
    edges.add(
        (
            terminal_manifest,
            row["expected_evidence"]["result_path"],
            "SessionResult",
            "referenced_evidence_digests.attempt_manifest_sha256",
        )
    )
    if best_attempt is not None:
        selected = attempts[best_attempt - 1]
        best_path = row["expected_evidence"]["best_path"]
        edges.update(
            {
                (
                    selected["attempt_manifest_path"],
                    best_path,
                    "BestAttemptIdentity",
                    "attempt_manifest_sha256",
                ),
                (
                    selected["candidate_inventory_path"],
                    best_path,
                    "BestAttemptIdentity",
                    "candidate_sha256",
                ),
            }
        )
    return edges


def _corpus_errors(rows: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(rows, list):
        return ["corpus must be a list"]
    ids = [row.get("case_id") for row in rows if isinstance(row, dict)]
    if len(ids) != len(set(ids)):
        errors.append("duplicate case id")
    if set(ids) != set(REFERENCE_SHAPES) or len(rows) != len(REFERENCE_SHAPES):
        errors.append("case id universe differs from the exact ten")
    for row in rows:
        if not isinstance(row, dict):
            errors.append("row is not an object")
            continue
        allowed = {
            "case_id",
            "input_blobs",
            "expected_output_blobs",
            "machine_label",
            "expected_evidence",
            "assertions",
            "semantic_label_reference",
        }
        if set(row) - allowed:
            errors.append(f"{row.get('case_id')}: unknown row field")
        if ("expected_output_blobs" in row) != (row.get("case_id") in EXPECTED_OUTPUT_CASES):
            errors.append(f"{row.get('case_id')}: expected-output commitment is misplaced")
        for group in ("input_blobs", "expected_output_blobs"):
            blobs = row.get(group)
            if blobs is None and group == "expected_output_blobs":
                continue
            if not isinstance(blobs, list) or not blobs:
                errors.append(f"{row.get('case_id')}: no committed {group} blob")
                continue
            for blob in blobs:
                required = {
                    "path",
                    "media_type",
                    "encoding",
                    "size_bytes",
                    "sha256",
                    "bytes",
                }
                if set(blob) != required:
                    errors.append(f"{row.get('case_id')}: recipe-only or open blob")
                    continue
                try:
                    raw = blob["bytes"].encode(blob["encoding"])
                except (AttributeError, LookupError, UnicodeError):
                    errors.append(f"{row.get('case_id')}: invalid committed bytes")
                    continue
                if len(raw) != blob["size_bytes"]:
                    errors.append(f"{row.get('case_id')}: stale byte count")
                if _sha256(raw) != blob["sha256"]:
                    errors.append(f"{row.get('case_id')}: stale {group} digest")
        label = row.get("machine_label", {})
        if set(label) != {"owner", "disposition"} or label.get("owner") != "test-engineer":
            errors.append(f"{row.get('case_id')}: machine label is not test-owned")
        case_id = row.get("case_id")
        shape = REFERENCE_SHAPES.get(case_id)
        if shape is None:
            continue
        disposition, verifier_attempts, best_attempt = shape
        if label.get("disposition") != disposition.value:
            errors.append(f"{case_id}: disposition is not a SessionOutcome")
        if case_id == "session-same-score-different-candidate":
            if row.get("assertions") != [
                "distinct-candidate-digests-are-not-recurrence"
            ]:
                errors.append(f"{case_id}: missing separate non-recurrence assertion")
        elif "assertions" in row:
            errors.append(f"{case_id}: unexpected supplemental assertion")
        if case_id == "session-alethic-indeterminate-deontic-warning":
            if row.get("semantic_label_reference") != (
                "labels/session-alethic-indeterminate-deontic-warning.md"
            ):
                errors.append(f"{case_id}: semantic label forward reference changed")
        elif "semantic_label_reference" in row:
            errors.append(f"{case_id}: unexpected semantic label reference")

        evidence = row.get("expected_evidence", {})
        if set(evidence) != {
            "session_contract_path",
            "attempts",
            "best_path",
            "result_path",
            "digest_edges",
        }:
            errors.append(f"{case_id}: open or incomplete evidence shape")
            continue
        if evidence["session_contract_path"] != "session.contract.json":
            errors.append(f"{case_id}: wrong session contract path")
        if evidence["result_path"] != "result.json":
            errors.append(f"{case_id}: wrong terminal result path")
        expected_best = "best.json" if best_attempt is not None else None
        if evidence["best_path"] != expected_best:
            errors.append(f"{case_id}: wrong best pointer cardinality or path")

        attempts = evidence["attempts"]
        if not isinstance(attempts, list) or len(attempts) != len(verifier_attempts):
            errors.append(f"{case_id}: wrong attempt cardinality")
            continue
        attempt_fields = {
            "index",
            "launch_intent_path",
            "attempt_manifest_path",
            "candidate_inventory_path",
            "candidate_snapshot_paths",
            "agent_stdout_path",
            "agent_stderr_path",
            "feedback_path",
            "verifier_payload_paths",
        }
        for index, (attempt, has_verifier) in enumerate(
            zip(attempts, verifier_attempts, strict=True), start=1
        ):
            if not isinstance(attempt, dict) or set(attempt) != attempt_fields:
                errors.append(f"{case_id}: attempt {index} evidence shape is open")
                continue
            prefix = f"attempts/{index:04d}"
            expected_paths = {
                "index": index,
                "launch_intent_path": f"launches/{index:04d}.json",
                "attempt_manifest_path": f"{prefix}/attempt.json",
                "candidate_inventory_path": f"{prefix}/candidate.inventory.json",
                "candidate_snapshot_paths": [f"{prefix}/candidate/population.yaml"],
                "agent_stdout_path": f"{prefix}/agent.stdout",
                "agent_stderr_path": f"{prefix}/agent.stderr",
                "feedback_path": f"{prefix}/feedback.json",
                "verifier_payload_paths": (
                    [f"{prefix}/verifier/{case_id}.json"] if has_verifier else []
                ),
            }
            if attempt != expected_paths:
                errors.append(f"{case_id}: attempt {index} paths differ from the run tree")

        known_paths = {
            blob["path"]
            for group in ("input_blobs", "expected_output_blobs")
            for blob in row.get(group, [])
            if isinstance(blob, dict)
        }
        known_paths.update({"session.contract.json", "result.json"})
        if best_attempt is not None:
            known_paths.add("best.json")
        for attempt in attempts:
            if not isinstance(attempt, dict) or set(attempt) != attempt_fields:
                continue
            known_paths.update(
                value
                for key, value in attempt.items()
                if key.endswith("_path") and isinstance(value, str)
            )
            known_paths.update(attempt["candidate_snapshot_paths"])
            known_paths.update(attempt["verifier_payload_paths"])

        raw_edges = evidence["digest_edges"]
        if not isinstance(raw_edges, list):
            errors.append(f"{case_id}: digest graph is not a list")
            continue
        edges: set[tuple[str, str, str, str]] = set()
        for edge in raw_edges:
            if not isinstance(edge, dict) or set(edge) != {"from", "to", "model", "field"}:
                errors.append(f"{case_id}: digest edge shape is open")
                continue
            model = EDGE_MODELS.get(edge["model"])
            if model is None or not _runtime_field_path_exists(model, edge["field"]):
                errors.append(f"{case_id}: digest edge does not resolve in runtime models")
            if edge["from"] not in known_paths or edge["to"] not in known_paths:
                errors.append(f"{case_id}: digest edge names a nonexistent evidence path")
            edges.add((edge["from"], edge["to"], edge["model"], edge["field"]))
        if len(edges) != len(raw_edges):
            errors.append(f"{case_id}: duplicate digest edge")
        if edges != _expected_digest_edges(row, attempts, best_attempt):
            errors.append(f"{case_id}: incomplete or stale digest graph")
    return errors


def test_reference_corpus_has_exactly_ten_reproducible_test_owned_cases() -> None:
    rows = json.loads(CORPUS.read_text(encoding="utf-8"))
    assert _corpus_errors(rows) == []


@pytest.mark.parametrize(
    "mutation",
    [
        pytest.param(
            lambda rows: (
                rows[0]["input_blobs"][0].update(recipe="generate alpha")
                or rows[0]["input_blobs"][0].pop("bytes")
            ),
            id="recipe-only",
        ),
        pytest.param(lambda rows: rows[0].update(input_blobs=[]), id="missing-committed-blob"),
        pytest.param(lambda rows: rows.append(copy.deepcopy(rows[0])), id="duplicate-id"),
        pytest.param(
            lambda rows: rows.append({**copy.deepcopy(rows[0]), "case_id": "session-extra"}),
            id="extra-id",
        ),
        pytest.param(
            lambda rows: rows[0]["expected_evidence"]["digest_edges"].pop(),
            id="incomplete-evidence",
        ),
        pytest.param(
            lambda rows: rows[-1]["expected_output_blobs"][0].update(sha256="0" * 64),
            id="stale-expected-output-digest",
        ),
        pytest.param(
            lambda rows: rows[-1].pop("expected_output_blobs"),
            id="uncommitted-expectation",
        ),
        pytest.param(
            lambda rows: rows[0].update(
                expected_output_blobs=copy.deepcopy(rows[-1]["expected_output_blobs"])
            ),
            id="misplaced-expectation",
        ),
        pytest.param(
            lambda rows: next(
                edge
                for edge in rows[-1]["expected_evidence"]["digest_edges"]
                if edge["field"] == "files[].sha256"
                and edge["from"] == "expected/population.yaml"
            ).update(field="cases[].inputs[].sha256"),
            id="expected-output-edge-relabelled",
        ),
    ],
)
def test_reference_corpus_mutations_cannot_weaken_exactness(mutation) -> None:
    rows = json.loads(CORPUS.read_text(encoding="utf-8"))
    mutation(rows)
    assert _corpus_errors(rows), "the mutation must make the corpus invalid"


def _pathless_expected(
    data: bytes,
    *,
    media_type: str,
    output_id: str,
    candidate_path: str,
) -> dict[str, Any]:






    return {
        "media_type": media_type,
        "encoding": "utf-8",
        "sha256": _sha256(data),
        "output_id": output_id,
        "candidate_path": candidate_path,
        "comparison": "exact-bytes",
    }


def test_an_exact_expectation_needs_no_committed_answer_key(tmp_path: Path) -> None:










    document = _v2_exact_contract_document(tmp_path)
    answer = b'{"facts": []}\n'
    for case in document["cases"]:
        case["acceptance"]["expected_outputs"] = [
            _pathless_expected(
                answer,
                media_type="application/json",
                output_id="population",
                candidate_path="population.json",
            )
        ]

    shutil.rmtree(tmp_path / "expected", ignore_errors=True)
    contract = _read(tmp_path, document)

    declared = contract.cases[0].expected_outputs[0]
    assert declared.path is None
    assert declared.size_bytes is None
    assert declared.sha256 == _sha256(answer)
    assert declared.comparison == "exact-bytes"

    
    assert not (tmp_path / "expected").exists()
    leaked = [
        path
        for path in tmp_path.rglob("*")
        if path.is_file() and path.read_bytes() == answer
    ]
    assert leaked == [], f"the answer survives on disk at {leaked}"


def test_a_pathless_expectation_may_not_declare_a_size(tmp_path: Path) -> None:


    document = _v2_exact_contract_document(tmp_path)
    for case in document["cases"]:
        expectation = _pathless_expected(
            b'{"facts": []}\n',
            media_type="application/json",
            output_id="population",
            candidate_path="population.json",
        )
        expectation["size_bytes"] = 14
        case["acceptance"]["expected_outputs"] = [expectation]

    with pytest.raises(SessionContractError):
        _read(tmp_path, document)


def test_a_committed_expectation_still_proves_its_digest(tmp_path: Path) -> None:







    document = _contract_document(tmp_path)
    contract = _read(tmp_path, document)
    declared = contract.cases[0].expected_outputs[0]
    assert declared.path is not None
    assert declared.size_bytes is not None

    (tmp_path / declared.path).write_bytes(b"tampered\n")
    with pytest.raises(SessionContractError):
        _read(tmp_path, document)
