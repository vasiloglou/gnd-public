"""Run with the freshly installed wheel's Python, from the source checkout."""
import hashlib
import json
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import gnd
from gnd import api
from gnd.model import ModelLoadError, ModelValidationError, load_model


def verify_fixture_parity():
    count = 0
    for path in sorted(Path("tests/fixtures").rglob("*.orm.yaml")):
        try:
            model = load_model(path)
        except (ValueError, OSError, ModelLoadError, ModelValidationError):
            continue
        assert api.verbalize_model(model, for_growth=True) == api.verbalize_model(
            path, for_growth=True
        ), path
        count += 1
    assert count > 0
    print(f"Path and loaded-model pairs with identical bytes: {count}")


def verify_installed_example():
    package = Path(gnd.__file__).resolve().parent
    assert package.is_relative_to(Path(sys.prefix).resolve())
    with tempfile.TemporaryDirectory() as temp:
        example = Path(temp).resolve() / "example"
        shutil.copytree(package / "examples/seeded_growth", example)
        guide = (example / "README.md").read_text()
        cli = Path(sys.executable).with_name("gnd")
        root = example / "root.orm.yaml"
        view = api.verbalize_model(root, for_growth=True).encode("utf-8")
        assert subprocess.check_output([cli, "verbalize", "model", root, "--for-growth"]) == view
        print(f"Installed CLI/API bytes: {len(view)}. SHA-256: {hashlib.sha256(view).hexdigest()}")
        code = guide.split("```python\n", 1)[1].split("\n```", 1)[0]
        result = json.loads(subprocess.check_output([sys.executable, "-c", code], cwd=example))
        assert result["inspected_ids"] == ["work_has_version"]
        assert result["reversed_binding_supported"] is False
        assert [r["decision"] for r in result["decisions"]] == ["reuse", "defer"]
        assert result["direct_lookup"]["shown"][0]["id"] == "work_has_version"
        commands = 0
        for block in guide.split("```bash\n")[1:]:
            for line in block.split("\n```", 1)[0].splitlines():
                if line.startswith("gnd "):
                    subprocess.run([cli, *shlex.split(line)[1:]], cwd=example, check=True,
                                   stdout=subprocess.PIPE)
                    commands += 1
        assert commands == 8
        print(f"Packaged commands passed: {commands}. Direct, retry, defer and reversal verified.")


if __name__ == "__main__":
    verify_fixture_parity()
    verify_installed_example()
