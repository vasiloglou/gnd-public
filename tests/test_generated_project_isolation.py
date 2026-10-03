












from __future__ import annotations

from pathlib import Path

import pytest
from support.generated_project import (
    REPO_ROOT,
    generate_project,
    seed_smoke_row,
)
from support.isolated_run import (
    build_wheelhouse,
    create_isolated_venv,
    import_origin,
    run_in_isolation,
)

CORPUS_MODEL = "tests/fixtures/v51-generated-project/alpha/model.orm.yaml"


@pytest.fixture(scope="session")
def wheelhouse(tmp_path_factory: pytest.TempPathFactory) -> Path:

    destination = tmp_path_factory.mktemp("wheelhouse")
    build_wheelhouse(destination)
    return destination


@pytest.fixture
def outsider(tmp_path: Path):

    return generate_project(CORPUS_MODEL, tmp_path / "alpha", package="model")


                                                                               
                                   
                                                                               


def test_the_generated_tree_is_outside_the_checkout(outsider) -> None:


    assert outsider.is_outside(REPO_ROOT)
    assert not outsider.root.is_relative_to(REPO_ROOT)
    assert outsider.smoke_module.name == "test_architecture_smoke_v51_alpha.py"













                                                                               
                                                           
                                                                               


def test_the_smoke_module_runs_on_only_its_declared_dependencies(
    outsider, tmp_path: Path, wheelhouse: Path
) -> None:










    seed_smoke_row(outsider)
    python = create_isolated_venv(
        outsider, venv_root=tmp_path / "venv", wheelhouse=wheelhouse
    )
    result = run_in_isolation(outsider, python=python)
    output = result.stdout + result.stderr

    assert result.returncode == 0, output
    assert "ModuleNotFoundError" not in output
                                                                           
    assert "2 passed" in output, f"the seeded row did not execute:\n{output}"
    assert "skipped" not in output, f"a skipped row proves nothing:\n{output}"


def test_the_checkout_is_not_importable_inside_that_venv(
    outsider, tmp_path: Path, wheelhouse: Path
) -> None:



    python = create_isolated_venv(
        outsider, venv_root=tmp_path / "venv", wheelhouse=wheelhouse
    )
    origin = import_origin(python, "gnd", cwd=outsider.root)

    assert origin, "gnd did not resolve at all inside the isolated venv"
    resolved = Path(origin).resolve()
    assert not resolved.is_relative_to(REPO_ROOT / "src"), (
        f"gnd imported from the development tree ({resolved}); the venv is not "
        f"isolated and T1.2a proves nothing"
    )
    assert resolved.is_relative_to((tmp_path / "venv").resolve())


def test_the_venv_carries_only_what_the_project_declared(
    outsider, tmp_path: Path, wheelhouse: Path
) -> None:


    python = create_isolated_venv(
        outsider, venv_root=tmp_path / "venv", wheelhouse=wheelhouse
    )
    installed = _installed_distributions(python, outsider.root)

    assert "get-nick-done" in installed
    assert "pytest" in installed
    for absent in ("anthropic", "openai", "ruff", "hypothesis", "polyfactory"):
        assert absent not in installed, (
            f"{absent} reached the isolated venv, which declares only the "
            f"project's own test-time dependencies"
        )


                                                                               
                                                   
                                                                               


def test_conformance_exits_zero_over_the_generated_project(outsider) -> None:


    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "gnd",
            "conformance",
            CORPUS_MODEL,
            str(outsider.root),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_a_second_codegen_writes_nothing(outsider) -> None:



    before = {
        path: path.stat().st_mtime_ns
        for path in sorted(outsider.root.rglob("*"))
        if path.is_file()
    }
    generate_project(CORPUS_MODEL, outsider.root, package="model")
    after = {
        path: path.stat().st_mtime_ns
        for path in sorted(outsider.root.rglob("*"))
        if path.is_file()
    }
    assert after == before


def _installed_distributions(python: Path, cwd: Path) -> set[str]:
    import subprocess

    probe = (
        "import importlib.metadata as m, sys;"
        "sys.stdout.write('\\n'.join(sorted(d.metadata['Name'].lower() "
        "for d in m.distributions() if d.metadata['Name'])))"
    )
    result = subprocess.run(
        [str(python), "-c", probe], cwd=cwd, check=False, capture_output=True, text=True
    )
    return set(result.stdout.split())
