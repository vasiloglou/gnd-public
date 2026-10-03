

from __future__ import annotations

import copy
import json
import subprocess
import sys

from jsonschema import Draft202012Validator
from support.v62_phase2_corpus import FIXTURE, population, steps

from gnd import transition as transition_module
from gnd.api import _run_transition_raw, transition
from gnd.report import load_report_schema

MODEL = FIXTURE / "models/dynamic.orm.yaml"
CANARY = "SECRET-TICKET-314159"


def _find_properties(value, key: str) -> list[dict]:
    found = []
    if isinstance(value, dict):
        if key in value.get("properties", {}):
            found.append(value["properties"][key])
        for child in value.values():
            found.extend(_find_properties(child, key))
    elif isinstance(value, list):
        for child in value:
            found.extend(_find_properties(child, key))
    return found


def test_q04_step_model_omits_empty_changes_and_refuses_empty_rows() -> None:
    assert "derived_changes" in transition_module.StepResult.model_fields
    step = transition_module.StepResult(index=1, operation="x", bindings={})
    assert "derived_changes" not in step.model_dump()
    change_type = transition_module.StepResult.model_fields["derived_changes"].annotation
    assert change_type is not None
    derived_change = transition_module.DerivedChange
    try:
        derived_change(fact_type="ready")
    except ValueError:
        pass
    else:
        raise AssertionError("an empty derived delta must be refused")

    payload = transition(
        MODEL,
        population("pre_open"),
        steps(),
        population("post_resolved"),
        unredacted=True,
    )
    dirty = copy.deepcopy(payload)
    dirty["transition"]["steps"][0]["derived_changes"] = [
        {"fact_type": "ready", "added": [], "removed": []}
    ]
    assert list(Draft202012Validator(load_report_schema()).iter_errors(dirty))


def test_q01_q02_q03_schema_admits_optional_nonempty_changes() -> None:
    schema = load_report_schema()
    validator = Draft202012Validator(schema)
    payloads = (
        _run_transition_raw(
            MODEL, population("pre_open"), steps(), population("post_resolved")
        ).payload,
        _run_transition_raw(MODEL, population("pre_open"), steps(), None).payload,
        transition(MODEL, population("pre_open"), steps(), population("post_resolved")),
    )
    assert [payload["schema_version"] for payload in payloads] == [7, 8, 9]
    assert all(not list(validator.iter_errors(payload)) for payload in payloads)
    occurrences = _find_properties(schema, "derived_changes")
    assert len(occurrences) >= 1
    for row in occurrences:
        assert row["type"] == "array"
        assert row["items"]


def test_p02_empty_changes_preserve_legacy_shape() -> None:
    payload = transition(
        MODEL,
        population("pre_open"),
        steps(),
        post=None,
        unredacted=True,
    )
    final_step = payload["transition"]["steps"][2]
    assert "derived_changes" not in final_step


def test_p03_projected_changes_contain_marker_and_no_canary() -> None:
    payload = transition(
        MODEL,
        population("pre_open"),
        steps(),
        population("post_resolved"),
    )
    encoded = json.dumps(payload["transition"]["steps"][0]["derived_changes"], sort_keys=True)
    assert CANARY not in encoded
    assert '"redacted": true' in encoded


def test_q05_text_summary_is_deterministic_and_value_free() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "gnd",
            "check",
            str(MODEL),
            "--pre",
            str(population("pre_open")),
            "--steps",
            str(steps()),
            "--post",
            str(population("post_resolved")),
        ],
        capture_output=True,
        check=False,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "DERIVED resolvable: +1 -0" in completed.stdout
    assert "DERIVED ready: +1 -0" in completed.stdout
    summary_lines = [line for line in completed.stdout.splitlines() if line.startswith("DERIVED ")]
    assert summary_lines
    assert all(CANARY not in line for line in summary_lines)


def test_q05_unredacted_transition_renderer_prints_the_same_summaries(capsys) -> None:
    result = _run_transition_raw(
        MODEL, population("pre_open"), steps(), population("post_resolved")
    )
    assert result.report is not None
    from gnd.cli import _print_transition

    _print_transition(result.report, [])
    assert "DERIVED resolvable: +1 -0" in capsys.readouterr().out
