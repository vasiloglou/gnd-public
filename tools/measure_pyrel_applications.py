"""Execute the frozen application corpus through public standalone PyRel exports."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

from gnd.export.emit import render_pyrel

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests/fixtures/pyrel_applications"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measure(mode: str, python: Path) -> dict:
    matrix = json.loads((CORPUS / "matrix.json").read_text())
    answers = json.loads((CORPUS / "answers.json").read_text())
    if mode == "baseline":
        names = [next(n for n, c in matrix["cases"].items()
                      if c["model"] == "src/gnd/examples/" + m)
                 for m in matrix["models"]]
        names += [n for n in matrix["cases"] if n.endswith("-extra")]
    else:
        names = list(matrix["cases"])
    records = []
    with tempfile.TemporaryDirectory(prefix="pa-native-") as directory:
        scratch = Path(directory)
        env = {k: v for k, v in os.environ.items()
               if k in {"PATH", "HOME", "TMPDIR", "SYSTEMROOT"}}
        env["RAI_BUILD_DIR"] = str(scratch / "build")
        env["PYTHONUTF8"] = "1"
        versions = subprocess.run(
            [str(python), "-c", ("from importlib.metadata import version; "
             "import json,sys; print(json.dumps({'python':sys.version.split()[0],"
             "'relationalai':version('relationalai'),'duckdb':version('duckdb')}))")],
            cwd=scratch, env=env, capture_output=True, text=True, timeout=30, check=True)
        runtime = json.loads(versions.stdout)
        assert runtime["relationalai"] == "1.30.1" and runtime["duckdb"] == "1.5.5"
        programs = {}
        for name in names:
            case = matrix["cases"][name]
            model, population = ROOT / case["model"], ROOT / case["population"]
            if case["model"] not in programs:
                program = scratch / f"audit-{len(programs)}.py"
                program.write_text(render_pyrel(model))
                programs[case["model"]] = program
            program = programs[case["model"]]
            output = scratch / f"{name}.json"
            argv = [str(python), str(program), str(population), "--out", str(output)]
            if mode == "acceptance":
                argv.append("--accept")
            result = subprocess.run(argv, cwd=scratch, env=env, capture_output=True,
                                    text=True, timeout=60, check=False)
            with output.open("rb") as handle:
                raw = handle.read(4 * 1024 * 1024 + 1)
            assert len(raw) <= 4 * 1024 * 1024, "native report exceeds cap"
            report = json.loads(raw)
            report.pop("model", None)
            report.pop("population", None)
            verdicts = {row["constraint_ref"]: row["status"] for row in report["verdicts"]}
            verdicts.update({row["derivation_ref"]: row["status"]
                             for row in report.get("derivations", [])})
            expected = {"pass": "satisfied", "fail": "violated", "warning": "warning"}[case["expected"]]
            matched = verdicts.get(case["target"]) == expected
            if mode == "successor" and case["expected"] == "warning":
                # Legacy reports have no modality; this is another actual omission.
                matched = verdicts.get(case["target"]) == "warning"
            records.append({"case": name, "target": case["target"],
                            "expected": expected, "matches": matched,
                            "process_exit": result.returncode, "report": report,
                            "model_sha256": digest(model), "population_sha256": digest(population),
                            "program_sha256": digest(program),
                            "gnd_observed_exit": answers[name]["observed_gnd_exit"]})
            print(f"{name}: exit={result.returncode} target={verdicts.get(case['target'])}", flush=True)
    return {"schema_version": 1, "mode": mode, "runtime": runtime,
            "matrix_sha256": digest(CORPUS / "matrix.json"),
            "answers_sha256": digest(CORPUS / "answers.json"),
            "lock_sha256": digest(ROOT / "tutorials/runtimes/uv.lock"),
            "cases": records, "matched": sum(r["matches"] for r in records),
            "denominator": len(records)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("baseline", "successor", "acceptance"), required=True)
    parser.add_argument("--python", type=Path, default=ROOT / "tutorials/runtimes/.venv/bin/python")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = measure(args.mode, args.python.absolute())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    if args.mode == "baseline":
        assert any(v["status"] == "unsupported" for c in result["cases"]
                   for v in c["report"]["verdicts"]), "baseline omission no longer present"
        return 0
    return 0 if result["matched"] == result["denominator"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
