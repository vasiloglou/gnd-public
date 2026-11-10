"""Measure the normal GND route and the proposed Ossie include refusal."""

import json
import subprocess
import sys
from pathlib import Path

from gnd.errors import ModelValidationError
from gnd.model import parse_model_document
from gnd.model._includes import guard_document, include_reason

census, output = map(Path, sys.argv[1:])
observations = []
for name in census.read_text().splitlines():
    data = Path(name).read_bytes()
    document = parse_model_document(data, source=name)
    args = ["-m", "gnd", "validate", name]
    result = subprocess.run(
        [sys.executable, *args], capture_output=True, text=True, timeout=15, check=False
    )
    try:
        guard_document(document, "export.ossie")
    except ModelValidationError as error:
        guard = include_reason(error)
        assert guard == "include:unsupported-route", guard
    else:
        guard = None
    assert bool(guard) == ("includes" in document)
    observations.append(
        {
            "command": ["python", *args],
            "exit": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "export_include_guard": guard,
        }
    )
output.write_text(json.dumps(observations, indent=2) + "\n")
print(
    f"Measured GND admission for {len(observations)} models, including "
    f"{sum(bool(item['export_include_guard']) for item in observations)} include guards."
)
