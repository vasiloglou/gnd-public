import hashlib
import json
import subprocess
from pathlib import Path

from gnd.export.pyrel_rules import render
from gnd.export.pyrel_runtime import ExportInputError

paths = subprocess.check_output(
    [
        "git",
        "ls-files",
        "--",
        ":(glob)tests/fixtures/pyrel-rules*/**/*.orm.json",
        ":(glob)tests/fixtures/pyrel-rules*/**/*.orm.yaml",
        ":(glob)tests/fixtures/pyrel-oracle/*.orm.yaml",
        ":(glob)src/gnd/examples/bookrec/*.orm.yaml",
        ":(glob)src/gnd/examples/expense/*.orm.json",
        ":(glob)src/gnd/examples/plan_apps/*/model.orm.json",
    ],
    text=True,
).splitlines()
observations = {}
for filename in paths:
    for target in ("duckdb", "lqp"):
        key = f"{filename}:{target}"
        try:
            program = render(Path(filename), target)
        except ExportInputError as error:
            observations[key] = {"refused": str(error)}
        else:
            observations[key] = {"sha256": hashlib.sha256(program.encode()).hexdigest()}
print(json.dumps(observations, sort_keys=True, indent=2))
