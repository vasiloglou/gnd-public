"""Station-0 approval corpus for the Phase 5 coverage view.

The fixture narratives and structured answer keys exist before implementation.
The two implementation-produced goldens deliberately do not.  Importing
``gnd.coverage`` is delayed into each case so the committed RED run reports all
six missing-lane/missing-golden observations instead of stopping at one
collection error.
"""

from __future__ import annotations

import gzip
import hashlib
import importlib
import io
import json
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

import pytest
from support.cli_runner import run_main

_COVERAGE_HOLDER = tempfile.TemporaryDirectory(prefix="gnd-public-coverage-goldens-")
CORPUS = Path(_COVERAGE_HOLDER.name)
_PACK = Path(__file__).parent / "fixtures/public-coverage-goldens/corpus.json.gz"
assert _PACK.is_file() and not _PACK.is_symlink()
with _PACK.open("rb") as _stream:
    _wire = _stream.read(65537)
assert len(_wire) <= 65536 and hashlib.sha256(_wire).hexdigest() == '42bd4e2ffe52f182ff4e184cd45d4ed8763a7e741e3998b5dcc2f32e8f25cbe3'
with gzip.GzipFile(fileobj=io.BytesIO(_wire)) as _stream:
    _expanded = _stream.read(524289)
assert len(_expanded) <= 524288
_rows = json.loads(_expanded)
assert isinstance(_rows, list) and len(_rows) == 37
_seen = set()
_total = 0
for _row in _rows:
    assert isinstance(_row, dict) and set(_row) == {"path", "sha256", "bytes", "mode", "utf8"}
    _rel = PurePosixPath(_row["path"])
    assert _rel.parts and not _rel.is_absolute() and "." not in _rel.parts and ".." not in _rel.parts
    assert _row["path"] == _rel.as_posix() and "\\" not in _row["path"] and _row["path"] not in _seen
    assert _rel.parts[0] in {"mixed", "positional", "refused"} and _row["mode"] == 420
    _seen.add(_row["path"])
    _data = _row["utf8"].encode("utf8")
    assert len(_data) == _row["bytes"] <= 131072 and hashlib.sha256(_data).hexdigest() == _row["sha256"]
    _total += len(_data)
    assert _total <= 262144
    _target = CORPUS.joinpath(*_rel.parts)
    _target.parent.mkdir(parents=True, exist_ok=True)
    _target.write_bytes(_data)
    _target.chmod(_row["mode"])
assert _total == 191950

TREES = ("mixed", "positional", "refused")


def _answer(tree: Path) -> dict[str, Any]:
    document = json.loads((tree / "expected.json").read_text(encoding="utf-8"))
    assert document["tree"] == tree.name
    return document


def _assert_station_one_inputs_exist(golden: Path) -> None:
    failures: list[str] = []
    try:
        importlib.import_module("gnd.coverage")
    except ModuleNotFoundError as error:
        if error.name != "gnd.coverage":
            raise
        failures.append("gnd.coverage does not exist (the coverage lane is not implemented)")
    if not golden.is_file():
        failures.append(f"{golden.name} does not exist (the golden is not reviewed yet)")
    assert not failures, f"{golden.parent.name}: " + "; ".join(failures)


def _run(tree: Path, arguments: list[str]) -> tuple[int, str, str]:
    result = run_main(arguments, cwd=tree)
    return (
        result.returncode,
        result.stdout.decode("utf-8", errors="surrogatepass"),
        result.stderr.decode("utf-8", errors="surrogatepass"),
    )


@pytest.mark.parametrize("name", TREES)
def test_coverage_payload_matches_committed_golden_bytes(name: str) -> None:
    tree = CORPUS / name
    golden = tree / "expected.payload.json"
    answer = _answer(tree)
    _assert_station_one_inputs_exist(golden)

    code, stdout, stderr = _run(
        tree,
        ["coverage", *answer["arguments"], "--format", "json"],
    )
    assert code == 0, stderr
    assert stdout.encode("utf-8") == golden.read_bytes()


@pytest.mark.parametrize("name", TREES)
def test_coverage_human_render_matches_committed_golden_text(name: str) -> None:
    tree = CORPUS / name
    golden = tree / "expected.render.txt"
    answer = _answer(tree)
    _assert_station_one_inputs_exist(golden)

    code, stdout, stderr = _run(tree, ["coverage", *answer["arguments"]])
    assert code == 0, stderr
    assert stdout == golden.read_text(encoding="utf-8")
