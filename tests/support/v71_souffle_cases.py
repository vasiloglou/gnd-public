"""Bounded generic fixture helpers for public fake-tool controls."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "tests/fixtures/v71/phase6"

def load(path):
    return json.loads(Path(path).read_bytes())


def write(path, document):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes((json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode())


def source(domain, variant, root):
    target = root / "source"
    shutil.copytree(CORPUS / domain / variant, target)
    return target


def token(value, primitive):
    """Independent fixture encoding for simulated native output only."""
    if primitive == "String":
        return "s:" + value.encode().hex()
    if primitive == "Boolean":
        return "b:1" if value else "b:0"
    if primitive in {"Integer", "Number"}:
        return f"n:{value}:1"
    if primitive == "Date":
        return "d:" + value
    if primitive == "Duration":
        return "u:" + str(value)
    raise AssertionError("no fixture codec for " + primitive)


def expected_extensions(domain, variant):
    return load(CORPUS / domain / "extensions.json")[variant]


def csv_files(domain, variant):
    model = load(CORPUS / domain / variant / "model.orm.json")
    primitive = {t["id"]: t["primitive"] for t in model["object_types"]}
    expected = expected_extensions(domain, variant)
    return {
        f"r{i}.csv": "".join(
            "\t".join(
                token(v, primitive[role["object_type"]])
                for v, role in zip(row, fact["roles"], strict=True)
            )
            + "\n"
            for row in expected[fact["id"]]
        )
        for i, fact in enumerate(model["fact_types"])
        if fact.get("derivation")
    }


def fake_tool(root, domain, variant="base", scenario="valid", proof=None):
    files = csv_files(domain, variant)
    if scenario == "partial":
        files = {}
    if scenario == "arity":
        files["r2.csv"] = "s:41\n"
    if scenario == "token":
        files["r2.csv"] = "evil:value\ts:41\n"
    if scenario == "extra":
        files["unlisted.csv"] = "arbitrary\n"
    if scenario == "output-limit":
        files["r2.csv"] = "x" * 12000
    script = root / ("fake-" + scenario)
    version = (
        "Version: 7.0\nWord size: 64 bits\n"
        if scenario == "bad-version"
        else "Version: 2.5\nWord size: 64 bits\n"
    )
    text = "#!" + sys.executable + "\nimport sys,time,json\nfrom pathlib import Path\n"
    text += f"FILES={files!r}\nVERSION={version!r}\nPROOF={proof!r}\n"
    text += "if '--version' in sys.argv:\n print(VERSION,end='');sys.exit(0)\n"
    if scenario == "timeout":
        text += "time.sleep(3)\n"
    if scenario == "error":
        text += 'print("native failure",file=sys.stderr);sys.exit(7)\n'
    text += "out=Path(sys.argv[sys.argv.index('-D')+1])\nfor name,data in FILES.items():\n (out/name).write_text(data)\n"
    if scenario == "error-with-output":
        text += "sys.exit(7)\n"
    text += "if '-t' in sys.argv:\n sys.stdin.read()\n print(PROOF if isinstance(PROOF,str) else json.dumps(PROOF))\n"
    script.write_text(text)
    script.chmod(0o700)
    return script


