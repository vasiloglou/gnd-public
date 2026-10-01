"""One model-identity rule, one home, one ruled semantics.

v5.1 Phase 1 §6.5 (O5, D-P1.3, r2 A4). Two copies existed and DISAGREED --
measure anchored on the invocation root, fidelity on the installed checkout --
while fidelity's docstring claimed to be "unchanged" from measure's. A reader
comparing two payloads would have blamed the models rather than the anchors.

The cases below are behavioural: they run the function from real directories
rather than asserting that two modules import the same object (though T1.5a
asserts that too, because it is the cheapest guard against a third copy
appearing).
"""

from __future__ import annotations

import contextlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

from gnd.model_identity import stable_model_identifier

REPO_ROOT = Path(__file__).resolve().parents[1]


@contextlib.contextmanager
def working_directory(path: Path):
    """The invocation root IS the input to this rule, so tests must move."""
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def test_there_is_exactly_one_definition() -> None:
    """T1.5a. The falsifier is reintroducing a second body: import both
    re-exports and they must be the SAME object, not merely equal strings."""
    from gnd.fidelity import report as fidelity_report
    from gnd.measure import report as measure_report

    assert measure_report.stable_model_identifier is stable_model_identifier
    assert fidelity_report.stable_model_identifier is stable_model_identifier

    # The re-exports stay published: existing imports keep working (D-P1.3).
    assert "stable_model_identifier" in measure_report.__all__
    assert "stable_model_identifier" in fidelity_report.__all__

    # One home holds the body. A second `def` anywhere else reds this. Scanned
    # on the FILESYSTEM rather than through `git grep`, which sees only tracked
    # files -- a second copy would be caught the moment it is written, not the
    # moment it is committed.
    definitions = sorted(
        path.relative_to(REPO_ROOT).as_posix()
        for path in (REPO_ROOT / "src").rglob("*.py")
        if "def stable_model_identifier" in path.read_text(encoding="utf-8")
    )
    assert definitions == ["src/gnd/model_identity.py"], definitions


def test_a_model_below_the_invocation_directory_keeps_its_relative_label(
    tmp_path: Path,
) -> None:
    """T1.5b. The falsifier is anchoring on `__file__`: from a temp invocation
    root the installed checkout is not an ancestor, so the label would collapse
    to the basename and the useful relative path would be lost."""
    model = tmp_path / "nested" / "model.orm.yaml"
    model.parent.mkdir(parents=True)
    model.write_text("version: 1\n", encoding="utf-8")

    with working_directory(tmp_path):
        assert stable_model_identifier(str(model)) == "nested/model.orm.yaml"
        assert stable_model_identifier("nested/model.orm.yaml") == "nested/model.orm.yaml"


def test_a_model_outside_the_invocation_directory_falls_back_to_its_basename(
    tmp_path: Path,
) -> None:
    """T1.5c. The payload names the model, never the machine: an absolute path
    would leak a home directory into committed evidence."""
    outside = tmp_path / "elsewhere" / "model.orm.yaml"
    outside.parent.mkdir(parents=True)
    outside.write_text("version: 1\n", encoding="utf-8")
    invocation = tmp_path / "invoked-from"
    invocation.mkdir()

    with working_directory(invocation):
        label = stable_model_identifier(str(outside))

    assert label == "model.orm.yaml"
    assert os.sep not in label
    assert str(tmp_path) not in label


def test_the_label_is_the_same_from_another_checkout(tmp_path: Path) -> None:
    """T1.5d -- a different installation directory, and the reason the contract ruled
    the invocation root wins.

    Two callers run the identical command from the identical directory; one has
    GND importable from a DIFFERENT checkout. Under the old fidelity anchor the
    labels differed, because the installed location was an input. It is not one.
    """
    project = tmp_path / "work"
    (project / "models").mkdir(parents=True)
    model = project / "models" / "model.orm.yaml"
    model.write_text("version: 1\n", encoding="utf-8")

    with working_directory(project):
        from_here = stable_model_identifier("models/model.orm.yaml")

    other_checkout = tmp_path / "another-checkout"
    other_checkout.mkdir()
    probe = (
        "import sys, os;"
        f"os.chdir({str(project)!r});"
        "from gnd.model_identity import stable_model_identifier as s;"
        "sys.stdout.write(s('models/model.orm.yaml'))"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=other_checkout,
        check=False,
        capture_output=True,
        text=True,
        env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"},
    )

    assert from_here == "models/model.orm.yaml"
    assert result.stdout == from_here, (
        f"the label moved with the INSTALLATION location: {result.stdout!r} vs "
        f"{from_here!r}\n{result.stderr}"
    )


@pytest.mark.parametrize(
    "spelling",
    ["models/model.orm.yaml", "./models/model.orm.yaml", "models/../models/model.orm.yaml"],
)
def test_the_label_is_independent_of_path_spelling(tmp_path: Path, spelling: str) -> None:
    """The rule's stated purpose. Three spellings of one file, one label."""
    (tmp_path / "models").mkdir()
    (tmp_path / "models" / "model.orm.yaml").write_text("version: 1\n", encoding="utf-8")

    with working_directory(tmp_path):
        assert stable_model_identifier(spelling) == "models/model.orm.yaml"
