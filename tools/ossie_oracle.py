"""Run the pinned standalone Ossie validator and parser without runtime dependencies.

Supply a scratch root with the OS0 checkouts and isolated a/ (validator) and
b/ (parser) environments. The caller prepares these once via the OS0 receipt.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

OSSIE_COMMIT = "ee89dbdc2844d8b7d293ed42c8613928bb99505f"
CONVERTERS_COMMIT = "83ddc294c8840f5f497a2bdbec2348a128fc2254"
SCHEMA_SHA256 = "c94c6ee9831a65aac52c52353072c2480c04c43a49139ed8ebafc90a2d9b9588"
_PARSE = (
    "import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); "
    "from ossie_ontology.parser import OssieParser; "
    "OssieParser().parse(Path(sys.argv[2]))"
)


@dataclass(frozen=True)
class OssieOracle:
    root: Path

    def check_pins(self) -> None:
        for repo, commit in (("ossie", OSSIE_COMMIT), ("converters", CONVERTERS_COMMIT)):
            result = subprocess.run(
                ["git", "-C", str(self.root / repo), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
                timeout=15,
            )
            assert result.stdout.strip() == commit, repo
            subprocess.run(
                ["git", "-C", str(self.root / repo), "diff", "--quiet", "HEAD", "--"],
                check=True,
                timeout=15,
            )
        schema = self.root / "ossie/ontology/ontology.json"
        assert hashlib.sha256(schema.read_bytes()).hexdigest() == SCHEMA_SHA256

    def validate(self, path: Path) -> subprocess.CompletedProcess[str]:
        return self._run(
            self.root / "a/bin/python",
            self.root / "ossie/validation/validate.py",
            "--schema",
            self.root / "ossie/ontology/ontology.json",
            path,
        )

    def parse(self, path: Path) -> subprocess.CompletedProcess[str]:
        return self._run(
            self.root / "b/bin/python",
            "-I",
            "-c",
            _PARSE,
            self.root / "converters/ontology/src",
            path,
        )

    def _run(self, *args: Path | str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(arg) for arg in args],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            cwd=self.root,
            env={"PATH": os.defpath, "HOME": str(self.root), "PYTHONUTF8": "1"},
        )


_CONVERT = r"""
import importlib.metadata
import os
import socket
import sys
from pathlib import Path

checkout, document, output = map(Path, sys.argv[1:])
os.environ["RAI_CONFIG_FILE_PATH"] = str(checkout / "relationalai/tests/config/raiconfig.yaml")
sys.path[:0] = [str(checkout / "ontology/src"), str(checkout / "relationalai/src")]


def refuse_connection(event, args):
    if event in {"socket.connect", "socket.getaddrinfo"}:
        raise RuntimeError("ossie-oracle: offline socket refused")


sys.addaudithook(refuse_connection)
try:
    socket.getaddrinfo("example.invalid", 443)
except RuntimeError as error:
    assert str(error) == "ossie-oracle: offline socket refused"
else:
    raise AssertionError("offline socket control was inactive")

assert importlib.metadata.version("relationalai") == "1.39.0"
from ossie_ontology.parser import OssieParser
from ossie_relationalai import OssieToRelationalAIConverter, declared_table
from relationalai.semantics.metamodel.pyrel_codegen import to_pyrel

model = OssieToRelationalAIConverter.convert(
    OssieParser().parse(document),
    table_provider=declared_table,
)
source = to_pyrel(model.base_model().to_metamodel()).encode("utf-8")
if len(source) > 10 * 1024 * 1024:
    raise ValueError("ossie-oracle: generated source exceeds size cap")
output.write_bytes(source)
"""


def convert_offline(
    oracle: OssieOracle,
    document: Path,
    output: Path,
    *,
    checkout: Path | None = None,
    python: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    """Emit PyRel source in the isolated process, without executing that source."""
    source = checkout or oracle.root / "converters"
    config = source / "relationalai/tests/config/raiconfig.yaml"
    assert hashlib.sha256(config.read_bytes()).hexdigest() == (
        "bd5ee17aa037bfcf87de1f0800e7fa737e2f922ba62facc351414ace26b15276"
    )
    return oracle._run(
        python or oracle.root / "c/bin/python", "-I", "-c", _CONVERT,
        source.resolve(), document.resolve(), output.resolve(),
    )
