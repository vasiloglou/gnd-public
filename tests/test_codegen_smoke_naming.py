














from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from gnd.codegen.identifiers import smoke_discriminator

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS = REPO_ROOT / "tests" / "fixtures" / "v51-generated-project"


def _gnd(*argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "gnd", *argv],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _model_arg(case: str) -> str:







    return f"tests/fixtures/v51-generated-project/{case}/model.orm.yaml"


def _smoke_modules(root: Path) -> set[str]:
    return {path.name for path in root.glob("test_architecture_smoke_*.py")}


                                                                               
                                                
                                                                               


def test_two_models_named_model_orm_yaml_emit_non_colliding_basenames(
    tmp_path: Path,
) -> None:


    roots = {}
    for case in ("alpha", "beta"):
        out = tmp_path / case
        result = _gnd("codegen", _model_arg(case), "--out", str(out))
        assert result.returncode == 0, result.stdout + result.stderr
        roots[case] = out

    names = {case: _smoke_modules(root) for case, root in roots.items()}
    assert names["alpha"] == {"test_architecture_smoke_v51_alpha.py"}
    assert names["beta"] == {"test_architecture_smoke_v51_beta.py"}
    assert names["alpha"].isdisjoint(names["beta"])

                                                                       
    assert (CORPUS / "alpha" / "model.orm.yaml").name == (
        CORPUS / "beta" / "model.orm.yaml"
    ).name
    assert (roots["alpha"] / "model").is_dir() and (roots["beta"] / "model").is_dir()


def test_the_pair_collects_together_under_one_rootdir(tmp_path: Path) -> None:


    for case in ("alpha", "beta"):
        result = _gnd(
            "codegen", _model_arg(case), "--out", str(tmp_path / case)
        )
        assert result.returncode == 0, result.stdout + result.stderr

    collected = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:randomly", "."],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert "import file mismatch" not in collected.stdout + collected.stderr
    assert "test_architecture_smoke_v51_alpha.py" in collected.stdout
    assert "test_architecture_smoke_v51_beta.py" in collected.stdout


























                                                                               
                                                                             
                                                                               















































































def test_a_right_named_smoke_module_is_never_rewritten(tmp_path: Path) -> None:


    root = tmp_path / "alpha"
    assert _gnd(
        "codegen", _model_arg("alpha"), "--out", str(root)
    ).returncode == 0
    module = root / "test_architecture_smoke_v51_alpha.py"
    stamp = module.stat().st_mtime_ns

    again = _gnd("codegen", _model_arg("alpha"), "--out", str(root))
    assert again.returncode == 0, again.stdout + again.stderr
    assert module.stat().st_mtime_ns == stamp


def test_the_refusal_names_only_root_level_smoke_modules(tmp_path: Path) -> None:





    root = tmp_path / "alpha"
    assert _gnd(
        "codegen", _model_arg("alpha"), "--out", str(root)
    ).returncode == 0
    nested = root / "tests"
    nested.mkdir()
    (nested / "test_architecture_smoke_someone_elses.py").write_text("", encoding="utf-8")

    result = _gnd("codegen", _model_arg("alpha"), "--out", str(root))
    assert result.returncode == 0, result.stdout + result.stderr


                                                                               
                                                                          
                                                                               




























@pytest.mark.parametrize("model_id", [None, "", "@1", "urn:x:@2", "::"])
def test_a_model_without_a_usable_id_keeps_the_pre_phase_rule(model_id) -> None:



    assert smoke_discriminator(model_id, package="model") == "model"


def test_a_model_id_less_model_still_generates(tmp_path: Path) -> None:



    model = "tests/fixtures/models/keywords.orm.yaml"
    assert "model_id" not in (REPO_ROOT / model).read_text(encoding="utf-8")
    result = _gnd("codegen", model, "--out", str(tmp_path / "keywords"))
    assert result.returncode == 0, result.stdout + result.stderr
    assert _smoke_modules(tmp_path / "keywords") == {
        "test_architecture_smoke_keywords.py"
    }


                                                                               
                                                                    
                                                                               


def test_the_emitted_module_carries_the_import_separator(tmp_path: Path) -> None:

    from gnd.codegen.emit import render_smoke_module

    lines = render_smoke_module().splitlines()
    assert len(lines) == 4, lines
    assert lines[1] == "from gnd.archsmoke import build_smoke_module"
    assert lines[2] == ""
    assert "build_smoke_module(__file__)" in lines[3]

    module = tmp_path / "test_architecture_smoke_probe.py"
    module.write_text(render_smoke_module(), encoding="utf-8")
    lint = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--select", "I001", str(module)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert lint.returncode == 0, lint.stdout + lint.stderr


                                                                               
                                                                    
                                                                               


















