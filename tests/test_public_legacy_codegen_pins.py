from __future__ import annotations

import atexit
import contextlib
import gzip
import hashlib
import io
import json
import tempfile
from pathlib import Path

from support.recorded_version import tree_as_recorded

from gnd.cli import main

# Issue 172: the version these outputs were recorded at. A version bump does not re-record them.
RECORDED_AT = "0.3.0"


def _public_legacy_codegen():
    packed=(Path(__file__).parent/"fixtures/public-legacy-codegen/closure.json.gz").read_bytes()
    assert len(packed)<=65536
    assert hashlib.sha256(packed).hexdigest()=='3070a95babc6641bd33b99036b7eaf0e725d77c64f21232d3eaacc688f0b49b6'
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw=stream.read(65537)
    assert len(raw)<=65536
    assert hashlib.sha256(raw).hexdigest()=='841a5b565a7d4a930cb15d7a66bcb1627276180927f0aebf89d7968854ed8926'
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
    # Issue 172: the answer tree was recorded at RECORDED_AT. The fresh tree is compared as
    # written at that version: its version fields, and the manifest's digest of the one file
    # that carries one, checked against that file before it is re-derived.
    generated = tree_as_recorded(_tree_bytes(out), RECORDED_AT)
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

