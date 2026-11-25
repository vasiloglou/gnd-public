"""Verify all phase evidence at its cited commit or the tested repair head."""
import hashlib
from pathlib import Path
import subprocess
import sys

from ruamel.yaml import YAML

root = Path(__file__).resolve().parents[2]
tree = sys.argv[1]
yaml = YAML(typ="safe")
count = 0
for path in sorted(root.glob("00*-phase-*.md")):
    metadata = yaml.load(path.read_text().split("---", 2)[1])
    for item in metadata["evidence"]:
        revision = item.get("commit", tree)
        data = subprocess.check_output(["git", "show", f'{revision}:{item["path"]}'])
        assert hashlib.sha256(data).hexdigest() == item["sha256"], (path.name, item["path"])
        count += 1
    print(path.name, len(metadata["evidence"]), "evidence digests match")
print(count, "evidence digests match")
