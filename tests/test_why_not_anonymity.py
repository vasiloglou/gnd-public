"""WN1 T17: files added by the derivation-why-not milestone name no downstream application.

Only SHA-256 digests of the normalized forbidden tokens are committed, so the
test itself names nothing. The tokens come from the owner's standing rule and
the downstream names in issue #66 (WN1 gate, item 2).
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "fb037390eef37015ef5244f841e2b5399940193a"
FORBIDDEN = frozenset({
    "056383fda2d7ac0404a022ddbc187ebea369e6fdd0ffb479de7322366dd871eb",
    "615617073e571553aab0eb7edefdfd68284bf02966692afeff82a451f1b7a4e5",
    "a68485e82be8c60e0af5c748a97aebc200bf9d01fd2cf524e57215135a7e0997",
    "88d62362a6aba53bddf48356a809e12b3f2fc95b63250883295b1a7de373f7f5",
    # The same names with their separators removed, for camel-cased spellings.
    "b9f3e817dbf9539fc43523a639eee23030afc4fc1be1eae4b42962889bea2c3a",
    "e9eb87c32c4f8d872eb8db64b994e56db871012bbec5d71736cffff54d51a020",
    "de133b134738e65fa6f4dc4087838a17118c3f62dad65e1b65ee3bc97d7ac43a",
})
# Test-only: the planted control token "zz-planted-name" and its stripped form.
CONTROL = {hashlib.sha256(b"zz-planted-name").hexdigest(), hashlib.sha256(b"zzplantedname").hexdigest()}
TOKEN = re.compile(r"[a-z0-9][a-z0-9_-]*")


def _forms(token: str) -> set[str]:
    """The token, every contiguous run of its hyphen/underscore parts, and its
    punctuation-stripped form, so a compound or a camel-cased name is caught."""
    parts = [part for part in re.split(r"[-_]", token) if part]
    forms = {token, "".join(parts)}
    for start in range(len(parts)):
        for end in range(start + 1, len(parts) + 1):
            forms.add("-".join(parts[start:end]))
    return forms


def _digests(text: str) -> set[str]:
    normalized = " ".join(text.lower().split())
    return {
        hashlib.sha256(form.encode()).hexdigest()
        for token in TOKEN.findall(normalized) for form in _forms(token)
    }


def _hits(files, forbidden):
    return [
        path for path in files
        if _digests(path.read_text(encoding="utf-8", errors="replace")) & forbidden
    ]


def _added_files() -> list[Path]:
    def git(*args: str) -> list[str]:
        out = subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout
        return [line for line in out.splitlines() if line]

    names = set(git("diff", "--name-only", "--diff-filter=A", BASE, "HEAD"))
    names.update(git("ls-files", "--others", "--exclude-standard"))
    return sorted(ROOT / name for name in names if (ROOT / name).is_file())


def test_added_files_name_no_downstream_application():
    files = _added_files()
    assert any("derivation-why-not" in str(path) for path in files)
    assert _hits(files, FORBIDDEN) == []


def test_the_scan_catches_a_planted_token(tmp_path):
    forbidden = FORBIDDEN | CONTROL
    for spelling in ("Zz-Planted-Name", "zz-planted-name-v2", "zz-planted-name_fork",
                     "ZzPlantedName", "zz-planted-name.git"):
        planted = tmp_path / "note.md"
        planted.write_text(f"See the {spelling} repository.\n")
        # Through the same listing the real scan uses; this file and the review
        # note quote the control token, so only membership is asserted.
        files = [*_added_files(), planted]
        assert planted in _hits(files, forbidden), spelling
    clean = tmp_path / "clean.md"
    clean.write_text("zz planted name, said apart.\n")
    assert _hits([clean], forbidden) == []
