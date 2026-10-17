"""Show each TP1 review successor red against its mutant. Run from the repository root.

Each mutant edits one source file in place, runs the matching test, and restores the
file's exact bytes in a finally block.
"""
import subprocess
from pathlib import Path

MUTANTS = [
    ("checking_service._run_check", "src/gnd/checking_service.py", "@_index_scoped\ndef _run_check(", "def _run_check(", "api.check"),
    ("api._run_transition", "src/gnd/api.py", "@_index_scoped\ndef _run_transition(", "def _run_transition(", "api.transition"),
    ("batch.check_population_directory", "src/gnd/batch.py", "@_index_scoped\ndef check_population_directory(", "def check_population_directory(", "batch"),
    ("population.load_population_bytes", "src/gnd/population.py", "@_index_scoped\ndef load_population_bytes(", "def load_population_bytes(", "load_population_bytes"),
    ("checker._core._check_dispatch", "src/gnd/checker/_core.py", "@_index_scoped\ndef _check_dispatch(", "def _check_dispatch(", "checker.check"),
    ("D3: uncacheable snapshots not stored", "src/gnd/model_index.py", "        if scope is not None:\n            scope[id(model)]", "        if scope is not None and index.digest is not None:\n            scope[id(model)]", "f2_uncacheable"),
]
for label, path, old, new, selector in MUTANTS:
    file = Path(path)
    original = file.read_bytes()
    text = original.decode()
    assert text.count(old) == 1, label
    try:
        file.write_text(text.replace(old, new))
        node = (f"tests/test_tp1_index_scope.py::test_review_f1_each_entry_point_opens_its_own_scope[{selector}"
                if "D3" not in label else "tests/test_tp1_index_scope.py")
        args = ["uv", "run", "pytest", "-q", node] if "D3" not in label else \
            ["uv", "run", "pytest", "-q", node, "-k", selector]
        if not node.endswith("]") and "D3" not in label:
            args[-1] = node + "]"
        result = subprocess.run(args, capture_output=True, text=True)
        verdict = "KILLED" if result.returncode != 0 else "SURVIVED"
        print(f"{verdict:8s} {label}: {result.stdout.strip().splitlines()[-1]}")
    finally:
        file.write_bytes(original)
