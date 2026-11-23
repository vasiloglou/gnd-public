"""Time one in-process gnd route over a grown interop copy. Prints one JSON line.

usage: vg1_once.py BUILT SHAPE N ROUTE   (ROUTE: check | judgments | verify | chain)
"""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vg1_grow  # noqa: E402

from gnd import cli  # noqa: E402


def run(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        try:
            code = cli.main(argv)
        except SystemExit as exit_:
            code = exit_.code
    return code, out.getvalue()


def main():
    built, shape, count, route = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3]), sys.argv[4]
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch).resolve() / "case"
        shutil.copytree(built, root)
        rows = vg1_grow.deep_chain(count) if route == "chain" else vg1_grow.extra_rows(shape, count)
        if count:
            vg1_grow.grow(root, rows)
        model, population = str(root / "checking.orm.json"), str(root / "composed.population.json")
        if route in ("check", "chain"):
            argv = ["check", model, population, "--format", "json"]
        elif route == "verify":
            argv = ["verify", model, population, "--no-extraction", "--format", "json"]
        else:
            sys.path.insert(0, str(Path.cwd() / "tests"))
            from test_ir1_judgments_includes import bind  # noqa: PLC0415
            bind(root, "checking.orm.json")
            argv = ["judgments", "check", model, population, "--policy", str(root / "policy.json"),
                    "--receipts", str(root / "receipts.json"), "--trusted-root", str(root), "--format", "json"]
        started = time.perf_counter()
        code, out = run(argv)
        elapsed = time.perf_counter() - started
    try:
        payload = json.loads(out)
        report = payload.get("report", payload)
        verdicts = sorted((v.get("constraint_ref"), v.get("verdict"), v.get("message")) for v in report.get("verdicts") or [])
    except ValueError:
        verdicts = None
    print(json.dumps({"shape": shape, "n": count, "route": route, "exit": code,
                      "seconds": round(elapsed, 3), "verdicts": verdicts}))


if __name__ == "__main__":
    main()
