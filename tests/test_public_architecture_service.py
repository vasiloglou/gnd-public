"""Architecture service regressions over fresh generic example projects."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest
from test_public_generated_examples import create_project

CONTRACT_RELPATH = "architecture.contract.yaml"
ARCHITECTURE_FINDING_KINDS = (
    "contract-unreadable",
    "contract-missing",
    "declared-module-missing",
    "declared-symbol-missing",
    "symbol-shape-mismatch",
    "declared-artifact-missing",
    "artifact-path-mismatch",
    "artifact-reference-unfound",
    "entry-point-module-missing",
    "entry-point-flag-unfound",
    "contract-fact-type-unknown",
)


@pytest.fixture(autouse=True)
def _public_architecture_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from gnd.conformance import service as service_module
    workspace = tmp_path / "workspace"
    for case, destination in (("expense", "expense-tracker"), ("bookrec", "bookrec")):
        _, root = create_project(case, tmp_path / "generated")
        project = workspace / "examples" / destination / "project"
        project.parent.mkdir(parents=True)
        shutil.move(str(root), project)
        shutil.copy2(project / "model.orm.yaml", project.parent / "model.orm.yaml")
        if case == "bookrec":
            contract_path = project / CONTRACT_RELPATH
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["modules"][0]["symbols"].append({"name": "missing_architecture_control", "parameters": []})
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
    monkeypatch.chdir(workspace)
    expense = service_module.run_conformance(Path("examples/expense-tracker/model.orm.yaml"), Path("examples/expense-tracker/project"))
    bookrec = service_module.run_conformance(Path("examples/bookrec/model.orm.yaml"), Path("examples/bookrec/project"))
    assert expense.exit_code == 0
    assert bookrec.exit_code == 13
    assert any(row["kind"] == "declared-symbol-missing" for row in bookrec.payload["findings"])


@pytest.mark.parametrize("red_call", [1, 2])
def test_service_union_retains_asymmetric_architecture_findings(
    monkeypatch: pytest.MonkeyPatch,
    red_call: int,
) -> None:
    from gnd.conformance import Finding
    from gnd.conformance import service as service_module
    from gnd.conformance.architecture import ArchitectureResult

    forced = Finding(
        kind="contract-unreadable",
        target=CONTRACT_RELPATH,
        message=f"forced asymmetric finding on call {red_call}",
    )
    calls = 0

    def alternating(*args: Any, **kwargs: Any) -> ArchitectureResult:
        nonlocal calls
        calls += 1
        return ArchitectureResult(findings=(forced,) if calls == red_call else ())

    monkeypatch.setattr(service_module, "check_architecture", alternating)
    result = service_module.run_conformance(
        Path("examples/expense-tracker/model.orm.yaml"),
        Path("examples/expense-tracker/project"),
    )
    assert calls == 2
    assert result.exit_code == 13
    assert [row for row in result.payload["findings"] if row["message"] == forced.message]


@pytest.mark.parametrize(("failure_call", "ran"), [(1, False), (2, True)])
def test_service_architecture_io_keeps_band_74_and_honest_ran_state(
    monkeypatch: pytest.MonkeyPatch,
    failure_call: int,
    ran: bool,
) -> None:
    from gnd.conformance import ConformanceError
    from gnd.conformance import service as service_module
    from gnd.conformance.architecture import ArchitectureResult

    calls = 0

    def fail_selected(*args: Any, **kwargs: Any) -> ArchitectureResult:
        nonlocal calls
        calls += 1
        if calls == failure_call:
            raise ConformanceError("forced architecture IO")
        return ArchitectureResult()

    monkeypatch.setattr(service_module, "check_architecture", fail_selected)
    result = service_module.run_conformance(
        Path("examples/expense-tracker/model.orm.yaml"),
        Path("examples/expense-tracker/project"),
    )
    assertion = next(row for row in result.payload["assertions"] if row["id"] == "architecture")
    assert calls == failure_call
    assert result.exit_code == 74
    assert assertion["ran"] is ran
    assert "architecture-io" in result.payload["error"]


@pytest.mark.parametrize("kind", ARCHITECTURE_FINDING_KINDS)
def test_every_architecture_finding_kind_reuses_service_band_13(
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    """S-04: the fourth assertion adds no finding-specific exit band."""
    from gnd.conformance import Finding
    from gnd.conformance import service as service_module
    from gnd.conformance.architecture import ArchitectureResult

    forced = Finding(
        kind=kind,
        target="forced-review-target",
        message=f"forced {kind}",
    )
    monkeypatch.setattr(
        service_module,
        "check_architecture",
        lambda *args, **kwargs: ArchitectureResult(findings=(forced,)),
    )
    result = service_module.run_conformance(
        Path("examples/expense-tracker/model.orm.yaml"),
        Path("examples/expense-tracker/project"),
    )
    assert result.exit_code == 13
    assert any(row["kind"] == kind for row in result.payload["findings"])


def test_silenced_architecture_mutation_reds_bookrec_and_preserves_expense(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """M-01 receipt: the real control distinguishes silence from correctness."""
    from dataclasses import replace

    from gnd.conformance import service as service_module

    real_check = service_module.check_architecture

    def silenced(*args: Any, **kwargs: Any) -> Any:
        return replace(real_check(*args, **kwargs), findings=())

    monkeypatch.setattr(service_module, "check_architecture", silenced)
    expense = service_module.run_conformance(
        Path("examples/expense-tracker/model.orm.yaml"),
        Path("examples/expense-tracker/project"),
    )
    bookrec = service_module.run_conformance(
        Path("examples/bookrec/model.orm.yaml"),
        Path("examples/bookrec/project"),
    )
    assert expense.exit_code == 0
    assert bookrec.exit_code == 0


def test_always_firing_architecture_mutation_reds_expense_and_keeps_bookrec_red(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """M-02 receipt: unconditional detection cannot masquerade as correctness."""
    from dataclasses import replace

    from gnd.conformance import Finding
    from gnd.conformance import service as service_module

    real_check = service_module.check_architecture
    forced = Finding(
        kind="contract-unreadable",
        target=CONTRACT_RELPATH,
        message="forced M-02 finding",
    )

    def always_firing(*args: Any, **kwargs: Any) -> Any:
        result = real_check(*args, **kwargs)
        return replace(result, findings=(*result.findings, forced))

    monkeypatch.setattr(service_module, "check_architecture", always_firing)
    expense = service_module.run_conformance(
        Path("examples/expense-tracker/model.orm.yaml"),
        Path("examples/expense-tracker/project"),
    )
    bookrec = service_module.run_conformance(
        Path("examples/bookrec/model.orm.yaml"),
        Path("examples/bookrec/project"),
    )
    assert expense.exit_code == 13
    assert bookrec.exit_code == 13

