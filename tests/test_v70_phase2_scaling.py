from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from test_v70_phase2_recursion import _write_model

from gnd.checker import structured_extension_view
from gnd.model import load_model
from gnd.population import load_population_bytes

FIXTURE = Path(__file__).parent / "fixtures/v70-phase2"

ANSWER = json.loads((FIXTURE / "answers.json").read_text())["cases"]["P01"]

GROUPS = ANSWER["groups"]

@pytest.mark.slow
def test_p01_near_ten_mib_population_reaches_fixpoint_under_sixty_seconds(
    tmp_path: Path,
) -> None:
    model_path = _write_model(tmp_path, "base")
    load_model(model_path)

    edges: list[dict[str, str]] = []
    reach: list[dict[str, str]] = []
    for index in range(GROUPS):
        a, b, c, d = (f"{index:05x}{suffix}" for suffix in "abcd")
        edges.extend(
            [
                {"source": a, "target": b},
                {"source": b, "target": c},
                {"source": c, "target": d},
            ]
        )
        reach.extend(
            {"source": source, "target": target}
            for source, target in ((a, b), (a, c), (a, d), (b, c), (b, d), (c, d))
        )
    population = {
        "population": {
            "model": "model.orm.yaml",
            "model_id": "urn:gnd-fixture:v70-phase2-reach@1",
            "source": "fixture",
            "label": "conforming",
            "covers": ["edge", "blocked", "reaches", "open_reach", "visited"],
        },
        "instances": {},
        "facts": {
            "edge": edges,
            "blocked": [],
            "reaches": reach,
            "open_reach": reach,
            "visited": [],
        },
    }
    population_path = tmp_path / "near-cap.pop.json"
    population_path.write_text(json.dumps(population, separators=(",", ":")) + "\n")
    assert ANSWER["min_bytes"] < population_path.stat().st_size < ANSWER["max_bytes"]

    script = (
        "import json,sys,time\n"
        "from gnd.model import load_model\n"
        "from gnd.population import load_population\n"
        "from gnd.checker import structured_extension_view\n"
        "m=load_model(sys.argv[1])\n"
        "p=load_population(sys.argv[2],model=m)\n"
        "start=time.monotonic()\n"
        "v=structured_extension_view(m,p)\n"
        "print(json.dumps({'seconds':time.monotonic()-start,'rows':len(v.facts['reaches'])}))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script, str(model_path), str(population_path)],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    measured = json.loads(result.stdout)
    assert measured["rows"] == ANSWER["rows"] == 6 * GROUPS
    assert measured["seconds"] < ANSWER["max_fixpoint_seconds"]

def test_long_recursive_chain_uses_delta_work(tmp_path: Path) -> None:
    model = load_model(_write_model(tmp_path, "base"))
    document = json.loads((FIXTURE / "pre.pop.json").read_text())
    length = 80
    document["facts"]["edge"] = [
        {"source": str(index), "target": str(index + 1)} for index in range(length)
    ]
    document["facts"]["blocked"] = []
    document["facts"]["reaches"] = []
    document["facts"]["open_reach"] = []
    population = load_population_bytes(
        json.dumps(document).encode(), source="chain.pop.json", model=model
    )
    view = structured_extension_view(model, population)
    assert len(view.facts["reaches"]) == length * (length + 1) // 2
    assert view.work.positive_candidate_rows_emitted < 20_000
    assert view.work.canonical_insertions >= len(view.facts["reaches"])
