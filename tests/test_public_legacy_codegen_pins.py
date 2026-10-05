from __future__ import annotations

import atexit
import contextlib
import gzip
import hashlib
import io
import json
import tempfile
from pathlib import Path

from gnd.cli import main


def _public_legacy_codegen():
    packed=(Path(__file__).parent/"fixtures/public-legacy-codegen/closure.json.gz").read_bytes()
    assert len(packed)<=65536
    assert hashlib.sha256(packed).hexdigest()=='08a1183ed80cc19e8dff070bff1a07a9f27075f9a1ad9c7ed68599c3a27f63d0'
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw=stream.read(65537)
    assert len(raw)<=65536
    assert hashlib.sha256(raw).hexdigest()=='db9a44b726c27f1ee93d11ade814da2f53b2970a0c308d521ca5b6310e00336c'
    documents=json.loads(raw)
    assert set(documents)=={'answers/legacy-codegen/.gnd-codegen.json', 'answers/legacy-codegen/artifacts/legacy-derived.applicable.json', 'answers/legacy-codegen/artifacts/legacy-derived.verbalization.txt', 'legacy-derived.orm.yaml', 'answers/legacy-codegen/references/gnd-legacy-derived-notes.md', 'answers/legacy-codegen/artifacts/legacy-derived.artifacts.json', 'answers/legacy-codegen/SKILL.md', 'answers/legacy-codegen/legacy_derived/__init__.py', 'answers/legacy-codegen/test_architecture_smoke_legacy_derived.py', 'answers/legacy-codegen/artifacts/legacy-derived.projection.schema.json', 'answers/legacy-codegen/legacy_derived/tools.py', 'answers/legacy-codegen/pyproject.toml', 'answers/legacy-codegen/architecture.contract.yaml'}
    temporary=tempfile.TemporaryDirectory(prefix="gnd-public-legacy-codegen-")
    root=Path(temporary.name)
    for name,text in documents.items():
        path=root/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(text,encoding="utf-8")
    return temporary,root

_TEMPORARY,CORPUS=_public_legacy_codegen()
atexit.register(_TEMPORARY.cleanup)
ANSWER=CORPUS/"answers/legacy-codegen"

def _tree_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }

def test_legacy_string_codegen_bytes_are_pinned(tmp_path: Path) -> None:
    # The emitted SKILL.md takes its name from the output directory, so the
    # directory must be named like the captured answer tree to reproduce it.
    out = tmp_path / "legacy-codegen"
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.chdir(CORPUS):
        code = main(["codegen", "legacy-derived.orm.yaml", "--out", str(out)])
    assert code == 0
    generated = _tree_bytes(out)
    expected = _tree_bytes(ANSWER)
    assert sorted(generated) == sorted(expected)
    for relpath, data in expected.items():
        assert generated[relpath] == data, f"{relpath} moved from its pre-v5 bytes"

def test_the_pinned_answer_still_emits_the_legacy_constructor() -> None:
    """The fixture discriminates: it contains the constructor non-emission
    would remove, so this pin fails if A10's boundary is drawn too wide."""

    tools = (ANSWER / "legacy_derived" / "tools.py").read_text(encoding="utf-8")
    assert "def item_ranked(item):" in tools
    assert "def item_seeded(item):" in tools

