"""MC1 per-observable compatibility producer; run against baseline and candidate.

Archive execution accepts a git-produced manifest. Ordinary execution inventories
tracked models itself. A candidate never regenerates historical expected answers.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess
from pathlib import Path


def observe(call):
    try:
        return {"value": call()}
    except Exception as error:  # noqa: BLE001 -- observe each historical refusal
        return {"refusal": type(error).__name__, "path": getattr(error, "path", None),
                "issues": [{"rule_id": i.rule_id, "path": i.path}
                           for i in getattr(error, "issues", [])]}


def collect(paths):
    from gnd.cli import main
    from gnd.model import load_model
    from gnd.values import _model_digest, model_identity, reference_model_digest

    rows = {}
    for path in paths:
        row = {}
        try:
            model = load_model(path)
        except Exception as error:  # noqa: BLE001 -- observe each historical refusal
            row["load"] = {"refusal": type(error).__name__, "path": getattr(error, "path", None),
                           "issues": [{"rule_id": i.rule_id, "path": i.path}
                                      for i in getattr(error, "issues", [])]}
        else:
            row["load"] = {"value": "loaded"}
            for name, call in (
                ("model_dump", model.model_dump),
                ("model_dump_json", model.model_dump_json),
                ("model_digest", lambda model=model: _model_digest(model)),
                ("model_identity", lambda model=model: model_identity(model)),
                ("reference_model_digest", lambda model=model: reference_model_digest(model)),
            ):
                row[name] = observe(call)
        def cli(path=path):
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = main(["validate", path, "--identity"])
            return {"exit": code, "stdout": stdout.getvalue(), "stderr": stderr.getvalue()}
        row["validate_identity"] = observe(cli)
        # Normalize each result with identical portable encoding; surrogate code
        # points and non-JSON historical scalar values remain representable.
        rows[path] = json.loads(json.dumps(row, ensure_ascii=True, default=repr))
    return rows


def tracked_paths():
    return subprocess.check_output(
        ["git", "ls-files", "*.orm.yaml", "*.orm.json"], text=True).splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    paths = args.manifest.read_text().splitlines() if args.manifest else tracked_paths()
    paths = sorted(p for p in paths if p.endswith((".orm.yaml", ".orm.json")))
    rows = collect(paths)
    args.out.write_text(json.dumps(rows, indent=2, ensure_ascii=True) + "\n")
    loaded = sum(r["load"] == {"value": "loaded"} for r in rows.values())
    identity_refused = sum("refusal" in r.get("model_identity", {}) for r in rows.values())
    print(f"models={len(rows)} loaded={loaded} load_refused={len(rows)-loaded} "
          f"loaded_identity_refused={identity_refused}")


if __name__ == "__main__":
    main()
