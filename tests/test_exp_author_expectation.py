

from __future__ import annotations

import json
from pathlib import Path

import pytest
from support.digests import sha256_bytes as _sha256

from gnd.artifacts import ArtifactError
from gnd.cli import main
from gnd.exp.session_contract import SessionContractError, read_session_contract
from gnd.exp.session_eval import observe_expected_outputs

REPO_ROOT = Path(__file__).resolve().parent.parent


def _bound(path: str, data: bytes, *, media_type: str) -> dict[str, object]:
    return {
        "path": path,
        "media_type": media_type,
        "encoding": "utf-8",
        "sha256": _sha256(data),
        "size_bytes": len(data),
    }


def _experiment(tmp_path: Path) -> tuple[Path, bytes]:
    experiment_id = "EXP-001-author-expectation"
    assert (
        main(
            [
                "exp",
                "init",
                experiment_id,
                "--out",
                str(tmp_path),
                "--kind",
                "data-driven",
            ]
        )
        == 0
    )
    root = tmp_path / experiment_id
    (root / "candidate").mkdir()
    (root / "input").mkdir()
    input_bytes = b"Produce the exact population.\n"
    (root / "input/brief.md").write_bytes(input_bytes)
    model_bytes = (REPO_ROOT / "tests/fixtures/skeleton/model.orm.yaml").read_bytes()
    (root / "model.orm.yaml").write_bytes(model_bytes)
    document = {
        "schema_version": 2,
        "experiment_id": experiment_id,
        "max_attempts": 2,
        "wall_seconds": 30.0,
        "cases": [
            {
                "case_id": "extract",
                "role": "required",
                "inputs": [
                    _bound("input/brief.md", input_bytes, media_type="text/markdown")
                ],
                "acceptance": {
                    "mode": "exact-bytes",
                    "expected_outputs": [],
                },
                "verify": {
                    "command": "check",
                    "model": _bound(
                        "model.orm.yaml",
                        model_bytes,
                        media_type="application/yaml",
                    ),
                    "subject": "candidate/population.json",
                },
            }
        ],
    }
    contract_bytes = (
        json.dumps(document, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    ).encode("utf-8")
    (root / "session.contract.json").write_bytes(contract_bytes)
    return root, contract_bytes


def _author(root: Path, source: Path) -> int:
    return main(
        [
            "exp",
            "author-expectation",
            str(root),
            "--case",
            "extract",
            "--output-id",
            "population",
            "--candidate-path",
            "population.json",
            "--from",
            str(source),
        ]
    )


def test_author_expectation_happy_path_loads_pathless_and_erases_every_answer_copy(
    tmp_path: Path,
) -> None:
    root, _ = _experiment(tmp_path)
    answer = b'{"fixture": []}\n'
    source = root / "authoring/produced.population.json"
    source.parent.mkdir()
    source.write_bytes(answer)
    (root / "unrelated.txt").write_bytes(b"not the answer\n")

    assert _author(root, source) == 0

    contract = read_session_contract(
        root / "session.contract.json",
        experiment_root=root,
        experiment_id=root.name,
    )
    expectation = contract.cases[0].expected_outputs[0]
    assert expectation.path is None
    assert expectation.size_bytes is None
    assert expectation.sha256 == _sha256(answer)
    assert expectation.output_id == "population"
    assert expectation.candidate_path == "population.json"
    assert expectation.comparison == "exact-bytes"

    scanned = []
    leaked = []
    for path in root.rglob("*"):
        if path.is_file():
            scanned.append(path.relative_to(root).as_posix())
            if path.read_bytes() == answer:
                leaked.append(path.relative_to(root).as_posix())
    assert scanned
    assert leaked == []


def test_author_expectation_failure_after_source_removal_keeps_contract_byte_unchanged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from gnd.exp import expectation_author

    root, original_contract = _experiment(tmp_path)
    source = root / "produced.population.json"
    source.write_bytes(b'{"fixture": []}\n')
    real_scan = expectation_author._scan_answer_copies
    calls = 0

    def fail_second_scan(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise ArtifactError("injected post-delete scan failure")
        return real_scan(*args, **kwargs)

    monkeypatch.setattr(expectation_author, "_scan_answer_copies", fail_second_scan)

    assert _author(root, source) == 74
    assert calls == 2
    assert (root / "session.contract.json").read_bytes() == original_contract


def test_author_expectation_final_reload_failure_rolls_contract_bytes_back(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from gnd.exp import expectation_author

    root, original_contract = _experiment(tmp_path)
    source = root / "produced.population.json"
    source.write_bytes(b'{"fixture": []}\n')
    real_reader = expectation_author.read_session_contract
    calls = 0

    def fail_final_reload(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise SessionContractError("injected final contract reload failure")
        return real_reader(*args, **kwargs)

    monkeypatch.setattr(expectation_author, "read_session_contract", fail_final_reload)

    assert _author(root, source) == 3
    assert calls == 2
    assert (root / "session.contract.json").read_bytes() == original_contract


def test_author_expectation_names_every_preexisting_answer_copy_and_changes_nothing(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root, original_contract = _experiment(tmp_path)
    answer = b'{"fixture": []}\n'
    source = root / "produced.population.json"
    surviving = root / "unexpected/copy.population.json"
    source.write_bytes(answer)
    surviving.parent.mkdir()
    surviving.write_bytes(answer)

    assert _author(root, source) == 3

    output = capsys.readouterr().out
    assert "unexpected/copy.population.json" in output
    assert source.read_bytes() == answer
    assert surviving.read_bytes() == answer
    assert (root / "session.contract.json").read_bytes() == original_contract


def test_authored_contract_round_trips_through_existing_exact_acceptance_path(
    tmp_path: Path,
) -> None:
    root, _ = _experiment(tmp_path)
    answer = b'{"fixture": []}\n'
    source = root / "produced.population.json"
    source.write_bytes(answer)

    assert _author(root, source) == 0
    contract = read_session_contract(
        root / "session.contract.json",
        experiment_root=root,
        experiment_id=root.name,
    )
    case = contract.cases[0]
    candidate = root / "candidate/population.json"
    candidate.write_bytes(answer)
    candidate_digest = _sha256(candidate.read_bytes())
    matched = observe_expected_outputs(case, {"population.json": candidate_digest})

    candidate.write_bytes(b'{"fixture": ["different"]}\n')
    different_digest = _sha256(candidate.read_bytes())
    differs = observe_expected_outputs(case, {"population.json": different_digest})

    assert [entry.state for entry in matched] == ["matched"]
    assert [entry.state for entry in differs] == ["differs"]


def test_author_expectation_replaces_a_bound_output_and_preserves_compact_json(
    tmp_path: Path,
) -> None:
    root, _ = _experiment(tmp_path)
    answer = b'{"fixture": []}\n'
    source = root / "expected/population.json"
    source.parent.mkdir()
    source.write_bytes(answer)
    contract_path = root / "session.contract.json"
    document = json.loads(contract_path.read_bytes())
    document["cases"][0]["acceptance"]["expected_outputs"] = [
        {
            "candidate_path": "old.json",
            "comparison": "exact-bytes",
            "encoding": "utf-8",
            "media_type": "application/json",
            "output_id": "population",
            "path": "expected/population.json",
            "sha256": _sha256(answer),
            "size_bytes": len(answer),
        }
    ]
    contract_path.write_bytes(
        (
            json.dumps(
                document,
                ensure_ascii=False,
                sort_keys=False,
                separators=(",", ":"),
            )
            + "\n"
        ).encode("utf-8")
    )

    assert _author(root, source) == 0

    authored_bytes = contract_path.read_bytes()
    assert b"\n" not in authored_bytes.rstrip(b"\n")
    authored = json.loads(authored_bytes)
    expectation = authored["cases"][0]["acceptance"]["expected_outputs"][0]
    assert list(expectation) == [
        "candidate_path",
        "comparison",
        "encoding",
        "media_type",
        "output_id",
        "sha256",
    ]
    assert expectation["candidate_path"] == "population.json"
    assert "path" not in expectation
    assert "size_bytes" not in expectation
