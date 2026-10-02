from __future__ import annotations

import ast
from pathlib import Path

from support.digests import sha256_bytes, sha256_file

REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_HELPER_NAMES = {"_sha256", "_sha256_bytes", "_sha256_file"}


def test_shared_digest_helpers_hash_bytes_and_files(tmp_path: Path) -> None:
    payload = b"gnd\n"
    expected = "e669a3e2d6d0fe70c8a20b73fce2d427c6fbd70add1b94b9094f19d0e5049a90"
    path = tmp_path / "payload.bin"
    path.write_bytes(payload)

    assert sha256_bytes(payload) == expected
    assert sha256_file(path) == expected
    assert sha256_bytes(payload + b"x") != expected
    path.write_bytes(payload + b"x")
    assert sha256_file(path) != expected


def test_test_modules_do_not_reintroduce_local_sha256_wrappers() -> None:
    offenders: list[str] = []
    for path in sorted((REPO_ROOT / "tests").glob("test_*.py")):
        tree = ast.parse(path.read_bytes(), filename=str(path))
        names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name in LOCAL_HELPER_NAMES
        }
        if names:
            offenders.append(f"{path.relative_to(REPO_ROOT)}: {', '.join(sorted(names))}")

    assert offenders == []
