"""Runtime artifact identity is stable under installation relocation."""

from pathlib import Path, PurePosixPath
from types import SimpleNamespace

import pytest

from gnd.assurance import evidence as evidence  # noqa: PLC0414 -- compatibility surface


def distribution_at(base: Path):
    package = base / "lib/python3.13/site-packages"
    files = {
        "jsonschema/__init__.py": b"VALUE = 1\n",
        "jsonschema-4.26.0.dist-info/METADATA": b"Name: jsonschema\nVersion: 4.26.0\n",
        "jsonschema-4.26.0.dist-info/entry_points.txt": b"[console_scripts]\njsonschema = jsonschema.cli:main\n",
        "jsonschema-4.26.0.dist-info/RECORD": str(base).encode(),
        "../../../bin/jsonschema": ("#!" + str(base / "bin/python") + "\n").encode(),
    }
    for name, data in files.items():
        path = package / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return SimpleNamespace(
        files=[PurePosixPath(name) for name in files],
        entry_points=[
            SimpleNamespace(group="console_scripts", name="jsonschema", value="jsonschema.cli:main")
        ],
        version="4.26.0",
        locate_file=lambda name: package / str(name),
    )


def test_install_generated_paths_do_not_change_imported_artifact_identity(tmp_path, monkeypatch):
    first = distribution_at(tmp_path / "first")
    second = distribution_at(tmp_path / "second")
    monkeypatch.setattr(evidence.metadata, "distribution", lambda _: first)
    expected = evidence.dependency_identity("jsonschema")
    monkeypatch.setattr(evidence.metadata, "distribution", lambda _: second)
    assert evidence.dependency_identity("jsonschema") == expected


@pytest.mark.parametrize(
    "member",
    [
        "jsonschema/__init__.py",
        "jsonschema-4.26.0.dist-info/METADATA",
        "jsonschema-4.26.0.dist-info/entry_points.txt",
    ],
)
def test_imported_code_and_metadata_remain_identity_inputs(tmp_path, monkeypatch, member):
    distribution = distribution_at(tmp_path / "environment")
    monkeypatch.setattr(evidence.metadata, "distribution", lambda _: distribution)
    before = evidence.dependency_identity("jsonschema")
    distribution.locate_file(member).write_bytes(b"changed\n")
    assert evidence.dependency_identity("jsonschema") != before
