"""Replay the Fable expense checkpoint through the existing tutorial runner."""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[5]
spec = importlib.util.spec_from_file_location('tutorial_runner', root / 'tools/run_tutorials.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
receipts = []
with tempfile.TemporaryDirectory(prefix='mc4-expense-') as directory:
    count = runner.run_pages(
        [root / 'docs/how-to/shared-expense-policies-commands.md'], Path(directory),
        root / '.venv/bin/python', receipts=receipts, group='model-composition-expense-draft')
Path(sys.argv[1]).write_text(json.dumps({'blocks': count, 'records': receipts}, indent=2) + '\n')
print(f'{count} tutorial blocks passed')
