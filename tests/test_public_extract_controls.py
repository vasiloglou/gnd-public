"""Current extraction/roundtrip controls against complete retained synthetic fixtures."""
from __future__ import annotations

import base64
import gzip
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path, PurePosixPath

import pytest
from support.cli_runner import run_main
from support.digests import sha256_bytes as _sha256


def _workspace():
    fixture = Path(__file__).parent / "fixtures/public-extract-controls/workspace.json.gz"
    assert fixture.is_file() and not fixture.is_symlink()
    raw = fixture.read_bytes()
    assert len(raw) <= 32768 and hashlib.sha256(raw).hexdigest() == 'a6bc0f1bf35016ac8a72c49b125de9792a9a842e5562b5aee4d1dacd389aa00e'
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        expanded = stream.read(131073)
    assert len(expanded) <= 131072
    payload = json.loads(expanded)
    assert payload["schema_version"] == 1 and len(payload["members"]) == 18
    holder = tempfile.TemporaryDirectory(prefix="gnd-public-extract-controls-")
    root = Path(holder.name).resolve()
    for name, member in payload["members"].items():
        path = PurePosixPath(name)
        assert path.parts and not path.is_absolute() and ".." not in path.parts and path.as_posix() == name
        data = base64.b64decode(member["data"], validate=True)
        assert len(data) <= 65536 and hashlib.sha256(data).hexdigest() == member["sha256"]
        assert member["mode"] == 420
        target = root.joinpath(*path.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        target.chmod(member["mode"])
    return holder, root
_HOLDER, REPO_ROOT = _workspace()
CONTROL_PATH = REPO_ROOT / "tests/fixtures/v51-extraction-boundary/answers/pre-phase-controls.json"
CONTROLS = json.loads(CONTROL_PATH.read_text(encoding="utf-8"))
BASE_COMMIT = "5c0d7a85f118adca1729a38bd04b8a9877505958"
ROUNDTRIP = REPO_ROOT / "tests/fixtures/roundtrip"
SETFAM_MODEL = REPO_ROOT / "tests/fixtures/checker/setfam.orm.yaml"


def _tree_digests(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): _sha256(path.read_bytes())
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _run(arguments: list[str], *, cwd: Path = REPO_ROOT) -> tuple[int, str]:
    result = run_main(arguments, cwd=cwd, capture_stderr=False)
    return result.returncode, result.stdout.decode("utf-8", errors="surrogatepass")


def _normalized_stdout(stdout: str, temporary_root: Path) -> str:
    return stdout.replace(str(temporary_root), "<tmp>")


def test_control_answer_key_is_bound_to_the_phase_base() -> None:
    assert CONTROLS["schema_version"] == 1
    assert CONTROLS["base_commit"] == BASE_COMMIT
    assert [row["id"] for row in CONTROLS["commands"]] == [
        "full-vocabulary-extract",
        "legacy-opaque-extract",
        "legacy-opaque-codegen",
        "setfam-faithful-fidelity",
        "setfam-hoover-fidelity",
    ]


@pytest.mark.parametrize(
    ("control_id", "model", "out_name"),
    [
        (
            "full-vocabulary-extract",
            "tests/fixtures/models/full_vocabulary.orm.yaml",
            "full-vocabulary",
        ),
        (
            "legacy-opaque-extract",
            "tests/fixtures/phase3-consumers/legacy-derived.orm.yaml",
            "legacy-extract",
        ),
    ],
)
def test_pre_phase_extract_bundles_are_byte_identical(
    control_id: str, model: str, out_name: str, tmp_path: Path
) -> None:
    expected = next(row for row in CONTROLS["commands"] if row["id"] == control_id)
    out = tmp_path / out_name
    code, stdout = _run(["extract", model, "--out", str(out)])
    assert code == expected["exit"] == 0
    assert _sha256(_normalized_stdout(stdout, tmp_path).encode("utf-8")) == expected[
        "stdout_sha256"
    ]
    assert _tree_digests(out) == expected["files"]


def test_legacy_opaque_codegen_tree_is_byte_identical(tmp_path: Path) -> None:
    expected = next(
        row for row in CONTROLS["commands"] if row["id"] == "legacy-opaque-codegen"
    )
    out = tmp_path / "legacy-codegen"
    code, stdout = _run(
        [
            "codegen",
            "tests/fixtures/phase3-consumers/legacy-derived.orm.yaml",
            "--out",
            str(out),
        ]
    )
    assert code == expected["exit"] == 0
    assert _sha256(_normalized_stdout(stdout, tmp_path).encode("utf-8")) == expected[
        "stdout_sha256"
    ]
    assert _tree_digests(out) == expected["files"]


@pytest.mark.parametrize("case_name", ["faithful", "hoover"])
def test_pre_phase_setfam_fidelity_is_byte_identical(
    case_name: str, tmp_path: Path
) -> None:
    expected = next(
        row
        for row in CONTROLS["commands"]
        if row["id"] == f"setfam-{case_name}-fidelity"
    )
    cases = tmp_path / f"{case_name}-cases"
    shutil.copytree(ROUNDTRIP / case_name, cases / case_name)
    code, stdout = _run(
        [
            "fidelity",
            str(SETFAM_MODEL),
            "--cases",
            str(cases),
            "--artifacts",
            str(ROUNDTRIP / "artifacts"),
            "--format",
            "json",
        ]
    )
    assert code == expected["exit"] == 0
    assert _sha256(stdout.encode("utf-8")) == expected["output_sha256"]


def test_roundtrip_fixture_roster_and_bytes_are_exact() -> None:
    assert _tree_digests(ROUNDTRIP) == CONTROLS["roundtrip_files"]

