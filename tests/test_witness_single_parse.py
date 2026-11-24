"""One witness command parses each model text once per reader.

`gnd witness`, `gnd replay` and `gnd why-not` parsed the model's bytes for the
include guard and again to load them; a composed command also parsed them for
the projection guard, the path guard and a second load. The witness entry
points now run in GO1's parse scope (`gnd.model._parsing.parse_scope`), so the
same bytes under the same reader are parsed once. The scope's write check,
switched on for every test by the autouse fixture in conftest.py, holds that
no witness path writes into a shared document.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import pytest
from support.cli_runner import run_main

from gnd.artifacts import canonical_json_bytes
from gnd.model import _parsing

ROOT = Path(__file__).resolve().parents[1]
DISPATCH = ROOT / "tests/fixtures/v71/phase3/dispatch"
WHY = ROOT / "tests/fixtures/why_not/claims"
LITERATURE = ROOT / "src/gnd/examples/literature"
LINEAGE_MODEL = LITERATURE / "lineage/model.orm.yaml"


@contextmanager
def _parses() -> Iterator[Counter]:
    seen: Counter = Counter()
    real = _parsing._parse_model_document

    def counting(data: bytes, *, source):
        seen[bytes(data)] += 1
        return real(data, source=source)

    with mock.patch.object(_parsing, "_parse_model_document", counting):
        yield seen


ROOTED = {
    "witness": ["witness", DISPATCH / "model.orm.yaml", DISPATCH / "candidate.pop.json",
                "--targets", DISPATCH / "targets.json", "--raw"],
    "replay": ["replay", DISPATCH / "model.orm.yaml", DISPATCH / "candidate.pop.json",
               DISPATCH / "direct.witness.json", "--raw"],
    "why-not": ["why-not", WHY / "model.orm.json", WHY / "gap.pop.json", "--fact-type", "credited"],
}


@pytest.mark.parametrize("name", list(ROOTED))
def test_a_rooted_witness_command_parses_each_model_text_once(name: str) -> None:
    argv = [str(part) for part in ROOTED[name]]
    expected = run_main(argv)
    with _parses() as seen:
        result = run_main(argv)
    assert (result.returncode, result.stdout) == (expected.returncode, expected.stdout)
    assert seen and max(seen.values()) == 1, sorted(seen.values())


@pytest.fixture(scope="module")
def lineage(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from gnd.examples.literature.lineage_run import assemble

    run = tmp_path_factory.mktemp("lineage") / "development"
    assemble(LITERATURE, LINEAGE_MODEL, LITERATURE / "lineage/development-input.json", run)
    return run


def test_a_composed_witness_and_its_replay_parse_each_model_text_once(lineage: Path, tmp_path: Path) -> None:
    target = tmp_path / "target.json"
    target.write_bytes(canonical_json_bytes({"version": 1, "targets": [
        {"fact_type": "lineage_ancestor",
         "tuple": [{"primitive": "String", "value": value} for value in ("WhAM", "bidirectional transformer")]}]}))
    proof = tmp_path / "proof.json"
    composed = ["--composition", str(lineage / "composition.json"), "--raw"]
    with _parses() as seen:
        made = run_main(["witness", str(LINEAGE_MODEL), str(lineage / "composed.population.json"),
                         "--targets", str(target), *composed, "--out", str(proof)])
    assert made.returncode == 0, made.stdout + made.stderr
    assert seen and max(seen.values()) == 1, sorted(seen.values())
    with _parses() as seen:
        replayed = run_main(["replay", str(LINEAGE_MODEL), str(lineage / "composed.population.json"),
                             str(proof), *composed, "--json"])
    assert replayed.returncode == 0
    assert seen and max(seen.values()) == 1, sorted(seen.values())
