"""UG close: flag-free parity capture (UG-R1). Run once per tree, from that tree's root:

    uv run python <this file> OUT.json

Captures, with no new option: `gnd validate MODEL --format json|text` for every tracked
*.orm.yaml; `gnd validate --document` over the MG5 fixture and its document; and the
growth example's two rounds (preview with the tutorial's flags, preview without a policy,
apply of round 1) plus the bookrec genre preview, in a scratch copy. Streams are
normalized by replacing the scratch root with <ws> and the tree root with <repo>.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd().resolve()
sys.path.insert(0, str(ROOT / "tests"))
from support.cli_runner import run_main


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def norm(data: bytes, ws: Path | None = None) -> bytes:
    text = data.decode("utf-8", "replace")
    if ws is not None:
        text = text.replace(str(ws), "<ws>")
    return text.replace(str(ROOT), "<repo>").encode("utf-8")


def row(argv: list[str], ws: Path | None = None) -> dict:
    result = run_main(argv)
    return {"exit": result.returncode, "stdout": sha(norm(result.stdout, ws)), "stderr": sha(norm(result.stderr, ws))}


def main(out: str) -> None:
    rows: dict[str, dict] = {}
    models = subprocess.run(["git", "ls-files", "*.orm.yaml"], capture_output=True, text=True, check=True).stdout.split()
    for model in sorted(models):
        for fmt in ("json", "text"):
            rows[f"validate {fmt} {model}"] = row(["validate", model, "--format", fmt])
    for fmt in ("json", "text"):
        rows[f"validate --document {fmt} unattended/conforming"] = row(
            ["validate", "tests/fixtures/unattended/conforming.orm.yaml", "--document",
             "tests/fixtures/unattended/source.txt", "--format", fmt])
    with tempfile.TemporaryDirectory() as scratch:
        ws = Path(scratch).resolve() / "growth"
        shutil.copytree(ROOT / "src/gnd/examples/growth", ws)
        (ws / "records").mkdir()
        common = ["--workspace", str(ws), "--records", str(ws / "records")]
        for n in (1, 2):
            for name, flags in (("policy", ["--policy", "additive", "--populated", "order_arrives_via_channel",
                                            "--shape-report"]), ("plain", [])):
                out_file = ws / f"round-{n}.{name}.preview.json"
                key = f"evolve preview round-{n} {name}"
                rows[key] = row(["evolve", "preview", str(ws / "model.orm.yaml"), str(ws / f"round-{n}.proposal.json"),
                                 *common, "--out", str(out_file), *flags], ws)
                rows[key]["preview"] = sha(norm(out_file.read_bytes(), ws)) if out_file.exists() else None
            if n == 1:
                rows["evolve apply round-1 policy"] = row(
                    ["evolve", "apply", str(ws / "model.orm.yaml"), str(ws / "round-1.proposal.json"), "--preview",
                     str(ws / "round-1.policy.preview.json"), *common, "--policy", "additive", "--populated",
                     "order_arrives_via_channel"], ws)
                rows["evolve apply round-1 policy"]["model"] = sha((ws / "model.orm.yaml").read_bytes())
        book = Path(scratch).resolve() / "bookrec"
        shutil.copytree(ROOT / "src/gnd/examples/bookrec", book)
        (book / "records").mkdir(exist_ok=True)
        out_file = book / "preview.json"
        rows["evolve preview bookrec genre"] = row(
            ["evolve", "preview", str(book / "model.orm.yaml"), str(book / "genre-proposal.json"), "--workspace",
             str(book), "--records", str(book / "records"), "--out", str(out_file), "--format", "json"], book)
        rows["evolve preview bookrec genre"]["preview"] = sha(norm(out_file.read_bytes(), book)) if out_file.exists() else None
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    Path(out).write_text(json.dumps({"tree": head, "rows": rows}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(head, len(rows), "rows")


if __name__ == "__main__":
    main(sys.argv[1])
