from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if sys.argv[1:] == ["--version"]:
        print("phase6-fake-agent 1")
        return 0
    prompt = sys.argv[1] if len(sys.argv) > 1 else json.load(sys.stdin)["prompt"]
    Path("agent-observation.json").write_text(
        json.dumps({"prompt": prompt}, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

