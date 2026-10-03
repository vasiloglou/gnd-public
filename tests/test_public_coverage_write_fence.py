from __future__ import annotations

import gzip
import hashlib
import io
import json
import shutil
from pathlib import Path

import pytest
from support.cli_runner import run_main

FIXTURES = Path(__file__).parent / "fixtures/coverage"
PUBLIC_FIXTURES = FIXTURES

@pytest.fixture(autouse=True)
def _public_complete_mixed(tmp_path_factory, monkeypatch):
    packed = (Path(__file__).parent / "fixtures/public-coverage-write-fence/additions.json.gz").read_bytes()
    assert len(packed) <= 65536
    assert hashlib.sha256(packed).hexdigest() == '21108987d6da739f1937068ec384f7b35753649d18567bd1e8f3c7d65c0f15fa'
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(65537)
    assert len(raw) <= 65536
    assert hashlib.sha256(raw).hexdigest() == '623ef34c0dcc2c3f0ccacc1b4070875b4054fccbcf3f158b3ad194cc66e509f7'
    additions = json.loads(raw)
    assert set(additions) == {"EXPECTED.md", "expected.render.txt"}
    root = tmp_path_factory.mktemp("complete-coverage-mixed")
    shutil.copytree(PUBLIC_FIXTURES / "mixed", root / "mixed")
    for name, text in additions.items():
        (root / "mixed" / name).write_text(text, encoding="utf-8")
    monkeypatch.setitem(globals(), "FIXTURES", root)

def _run(arguments: list[str], *, cwd: Path | None = None) -> tuple[int, str, str]:
    result = run_main(arguments, cwd=cwd)
    return (
        result.returncode,
        result.stdout.decode("utf-8", errors="surrogatepass"),
        result.stderr.decode("utf-8", errors="surrogatepass"),
    )


def _snapshot(*roots: Path) -> dict[str, str]:
    answer: dict[str, str] = {}
    for root in roots:
        for path in sorted((root, *root.rglob("*"))):
            key = f"{root}:{path.relative_to(root)}"
            if path.is_symlink():
                answer[key] = f"LINK:{path.readlink()}"
            elif path.is_dir():
                answer[key] = "DIR"
            else:
                answer[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    return answer


def _assert_snapshot_unchanged(before: dict[str, str], after: dict[str, str]) -> None:
    assert after == before


def test_full_run_writes_nothing_on_any_in_scope_path(tmp_path: Path) -> None:
    tree = tmp_path / "mixed"
    shutil.copytree(FIXTURES / "mixed", tree)
    before = _snapshot(tmp_path, tree, tree / "experiments")
    answer = json.loads((tree / "expected.json").read_text())
    code, stdout, stderr = _run(["coverage", *answer["arguments"], "--format", "json"], cwd=tree)
    assert code == 0, (stdout, stderr)
    _assert_snapshot_unchanged(before, _snapshot(tmp_path, tree, tree / "experiments"))

    (tree / "coverage.json").write_text("temporary bad build\n", encoding="utf-8")
    with pytest.raises(AssertionError):
        _assert_snapshot_unchanged(before, _snapshot(tmp_path, tree, tree / "experiments"))

