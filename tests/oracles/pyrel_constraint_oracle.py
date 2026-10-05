# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["relationalai==1.30.1", "ruamel.yaml==0.19.1"]
# ///
"""Isolated oracle entry point; shares only the independent export compiler.

No GND package import: execute the source resource directly so the checker and
its dependency environment cannot enter the oracle. Source mutations copy this
same repository layout under scratch in the agreement tests.
"""
import runpy
import sys
from pathlib import Path

_RUNTIME_PATH = Path(__file__).resolve().parents[2] / "src/gnd/export/pyrel_runtime.py"
_runtime = runpy.run_path(str(_RUNTIME_PATH))
run = _runtime["run"]


def main() -> int:
    parser = _runtime["_UsageParser"](description=__doc__)
    parser.add_argument("model", type=Path)
    parser.add_argument("population", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mode", choices=("select", "require"), default="select")
    args = parser.parse_args()
    import json
    result = run(args.model, args.population, args.mode)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
