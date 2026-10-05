"""Public constraint-session acceptance controls with offline fake adapters.

Every case enters through ``gnd.cli.main(["exp", "run", ...])`` and uses the
real ``gnd check`` verifier.  The only agent executables are local fixtures in
the test's temporary directory; provider credentials and config roots are
removed from their inherited environment.
"""


from __future__ import annotations

import base64
import hashlib
import json
import os
import stat
from pathlib import Path
from typing import Any, Literal

import pytest

from gnd import cli
from gnd.cli import main
from gnd.exp.session_eval import ASSURANCE_FEEDBACK_SCHEMA_VERSION

CASE_ID = "constraint-acceptance"


EXPERIMENT_ID = "EXP-703-constraint-acceptance"


FACT_TYPE = "person_has_name"


ANSWER_METADATA_KEYS = {
    "expected_outputs",
    "expected_path",
    "expected_sha256",
    "expected_size_bytes",
    "observed_sha256",
}


MODEL_BYTES = b"""version: 1
source:
  kind: text-conversation
  confidence: standard
  mode: guided
object_types:
  - id: person
    name: Person
    kind: entity
    reference: {mode: popular, value_type: person_id}
  - id: person_id
    name: PersonId
    kind: value
    primitive: Integer
  - id: name
    name: Name
    kind: value
    primitive: String
fact_types:
  - id: person_has_name
    reading: "{Person} has name {Name}"
    roles:
      - {object_type: person, role_name: person}
      - {object_type: name, role_name: name}
    constraints:
      - type: uniqueness
        roles: [person]
        source: explicit
        status: confirmed
        modality: alethic
        provenance:
          user_quote: "Each person has at most one name."
      - type: mandatory
        role: person
        source: explicit
        status: confirmed
        modality: alethic
        provenance:
          user_quote: "Every person has a name."
"""


def _canonical(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _bound(path: str, data: bytes, media_type: str) -> dict[str, Any]:
    return {
        "path": path,
        "media_type": media_type,
        "encoding": "utf-8",
        "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
    }


def _population(*rows: dict[str, Any], people: tuple[int, ...]) -> bytes:
    return _canonical(
        {
            "population": {
                "model": "model.orm.yaml",
                "source": "agent-output",
                "covers": [FACT_TYPE],
            },
            "instances": {"person": list(people)},
            "facts": {FACT_TYPE: list(rows)},
        }
    )


SATISFYING_A = _population(
    {"person": 1, "name": "Ada"},
    {"person": 2, "name": "Grace"},
    people=(1, 2),
)


SATISFYING_B = _population(
    {"person": 11, "name": "Lin"},
    {"person": 12, "name": "Margaret"},
    people=(11, 12),
)


VIOLATED = _population(
    {"person": 1, "name": "Ada"},
    {"person": 1, "name": "Augusta"},
    people=(1,),
)


EMPTY = _population(people=())


NEAR_EMPTY = _population({"person": 1, "name": "Ada"}, people=(1,))


ILL_FORMED = _population({"person": 1}, people=(1,))


def _sanitize_adapter_environment(
    monkeypatch: pytest.MonkeyPatch,
    bin_dir: Path,
) -> None:
    for name in (
        "CODEX_HOME",
        "CLAUDE_CONFIG_DIR",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_AUTH_TOKEN",
        "CLAUDE_CODE_OAUTH_TOKEN",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")


def _write_producing_agent(executable: Path, produced: bytes) -> None:
    encoded = base64.b64encode(produced).decode("ascii")
    executable.write_text(
        f"""#!/usr/bin/env python3
import base64
import pathlib
import sys

if "--version" in sys.argv:
    print("offline-constraint-agent 1.0")
    raise SystemExit(0)
sys.stdin.buffer.read()
pathlib.Path("population.json").write_bytes(base64.b64decode({encoded!r}))
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)


def _write_retry_agent(
    executable: Path,
    *,
    repaired: bytes,
    expected_branch: Literal["violations", "population_issues"],
) -> None:
    encoded = base64.b64encode(repaired).decode("ascii")
    forbidden = sorted(ANSWER_METADATA_KEYS)
    executable.write_text(
        f"""#!/usr/bin/env python3
import base64
import hashlib
import json
import pathlib
import re
import sys

if "--version" in sys.argv:
    print("offline-feedback-agent 1.0")
    raise SystemExit(0)

counter = pathlib.Path(".attempt-count")
attempt = int(counter.read_text()) + 1 if counter.exists() else 1
counter.write_text(str(attempt))
feedback = sys.stdin.buffer.read()
if attempt == 1:
    if feedback:
        raise SystemExit(31)
    raise SystemExit(0)

prompt = sys.argv[-1]
match = re.search(r"Current attempt feedback SHA-256: ([0-9a-f]{{64}})", prompt)
if match is None or hashlib.sha256(feedback).hexdigest() != match.group(1):
    raise SystemExit(32)
retained = list(pathlib.Path("..").glob("runs/*/attempts/0001/feedback.json"))
if len(retained) != 1 or feedback != retained[0].read_bytes():
    raise SystemExit(33)

document = json.loads(feedback)
if document.get("schema_version") != {ASSURANCE_FEEDBACK_SCHEMA_VERSION} or document.get("disposition") != "retry":
    raise SystemExit(34)
if document.get("source_attempt_index") != 1 or len(document.get("required", [])) != 1:
    raise SystemExit(35)
acceptance = document["required"][0]["acceptance"]
if acceptance.get("mode") != "constraint-satisfaction":
    raise SystemExit(36)
branches = {{
    "violations",
    "population_issues",
    "vacuity_findings",
    "unchecked_alethic",
    "coverage_gaps",
}}
if set(acceptance) != branches | {{"mode"}}:
    raise SystemExit(37)
if not acceptance[{expected_branch!r}]:
    raise SystemExit(38)
if any(acceptance[branch] for branch in branches - {{{expected_branch!r}}}):
    raise SystemExit(39)

def reject_answer_metadata(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in {forbidden!r} or key.startswith("expected_"):
                raise SystemExit(40)
            reject_answer_metadata(nested)
    elif isinstance(value, list):
        for nested in value:
            reject_answer_metadata(nested)
    elif isinstance(value, str) and "expected/" in value:
        raise SystemExit(41)

reject_answer_metadata(document)
pathlib.Path("feedback-consumed.bin").write_bytes(feedback)
pathlib.Path("population.json").write_bytes(base64.b64decode({encoded!r}))
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)


def _make_experiment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    initial: bytes,
    produced: bytes | None,
    adapter: Literal["claude", "codex"],
    mode: Literal["constraint-satisfaction", "exact-bytes"] = "constraint-satisfaction",
    min_facts: int = 2,
    max_attempts: int = 1,
    retry_branch: Literal["violations", "population_issues"] | None = None,
    expected: bytes = SATISFYING_A,
) -> Path:
    assert (
        main(
            [
                "exp",
                "init",
                EXPERIMENT_ID,
                "--out",
                str(tmp_path),
                "--kind",
                "data-driven",
                "--question",
                "Q1=Did the public session meet its declared acceptance relation?",
            ]
        )
        == 0
    )
    root = tmp_path / EXPERIMENT_ID
    candidate = root / "candidate"
    candidate.mkdir()
    (candidate / "population.json").write_bytes(initial)
    (root / "model.orm.yaml").write_bytes(MODEL_BYTES)
    input_bytes = b'{"task":"produce a checked person population"}\n'
    input_path = root / "input" / "task.json"
    input_path.parent.mkdir()
    input_path.write_bytes(input_bytes)

    if mode == "constraint-satisfaction":
        acceptance: dict[str, Any] = {
            "mode": mode,
            "coverage": [{"fact_type": FACT_TYPE, "min_facts": min_facts}],
        }
    else:
        expected_path = root / "expected" / "population.json"
        expected_path.parent.mkdir()
        expected_path.write_bytes(expected)
        acceptance = {
            "mode": mode,
            "expected_outputs": [
                {
                    **_bound("expected/population.json", expected, "application/json"),
                    "output_id": "population",
                    "candidate_path": "population.json",
                    "comparison": "exact-bytes",
                }
            ],
        }

    contract = {
        "schema_version": 2,
        "experiment_id": EXPERIMENT_ID,
        "max_attempts": max_attempts,
        "wall_seconds": 10.0,
        "cases": [
            {
                "case_id": CASE_ID,
                "role": "required",
                "inputs": [_bound("input/task.json", input_bytes, "application/json")],
                "acceptance": acceptance,
                "verify": {
                    "command": "check",
                    "model": _bound("model.orm.yaml", MODEL_BYTES, "application/yaml"),
                    "subject": "population.json",
                },
            }
        ],
    }
    (root / "session.contract.json").write_bytes(_canonical(contract))

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for adapter_id in ("claude", "codex"):
        executable = bin_dir / adapter_id
        if retry_branch is None:
            _write_producing_agent(executable, produced if produced is not None else initial)
        else:
            assert produced is not None
            _write_retry_agent(
                executable,
                repaired=produced,
                expected_branch=retry_branch,
            )
    _sanitize_adapter_environment(monkeypatch, bin_dir)
    return root


def _run(
    root: Path,
    adapter: str,
    capsys: pytest.CaptureFixture[str],
) -> tuple[int, dict[str, Any]]:
    exit_code = main(["exp", "run", str(root), "--adapter", adapter])
    output = capsys.readouterr().out.splitlines()
    return exit_code, json.loads(output[-1])


def _attempt_path(root: Path, rendered: dict[str, Any], index: int) -> Path:
    return root / "runs" / rendered["run_id"] / "attempts" / f"{index:04d}"


def _verifier(
    root: Path,
    rendered: dict[str, Any],
    index: int = 1,
) -> dict[str, Any]:
    return json.loads((_attempt_path(root, rendered, index) / "verifier" / f"{CASE_ID}.json").read_bytes())


def _feedback(
    root: Path,
    rendered: dict[str, Any],
    index: int = 1,
) -> tuple[bytes, dict[str, Any]]:
    raw = (_attempt_path(root, rendered, index) / "feedback.json").read_bytes()
    return raw, json.loads(raw)


def _assert_answer_free(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            assert key not in ANSWER_METADATA_KEYS
            assert not key.startswith("expected_")
            _assert_answer_free(nested)
    elif isinstance(value, list):
        for nested in value:
            _assert_answer_free(nested)
    elif isinstance(value, str):
        assert "expected/" not in value


@pytest.mark.parametrize(
    ("adapter", "satisfying"),
    [("claude", SATISFYING_A), ("codex", SATISFYING_B)],
)
def test_two_byte_distinct_constraint_satisfiers_each_exit_zero(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    adapter: Literal["claude", "codex"],
    satisfying: bytes,
) -> None:
    assert SATISFYING_A != SATISFYING_B
    root = _make_experiment(
        tmp_path,
        monkeypatch,
        initial=NEAR_EMPTY,
        produced=satisfying,
        adapter=adapter,
    )

    exit_code, rendered = _run(root, adapter, capsys)

    assert exit_code == 0
    assert rendered["disposition"] == "accepted"
    assert rendered["attempt_count"] == 1
    payload = _verifier(root, rendered)
    assert payload["exit_code"] == 0
    assert payload["acceptance_ready"] is True
    assert payload["coverage"][FACT_TYPE]["facts"] == 2


@pytest.mark.parametrize(
    ("initial", "branch", "first_band"),
    [(VIOLATED, "violations", 1), (ILL_FORMED, "population_issues", 3)],
)
def test_band_specific_feedback_is_consumed_byte_exactly_before_repair(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    initial: bytes,
    branch: Literal["violations", "population_issues"],
    first_band: int,
) -> None:
    root = _make_experiment(
        tmp_path,
        monkeypatch,
        initial=initial,
        produced=SATISFYING_A,
        adapter="codex",
        max_attempts=2,
        retry_branch=branch,
    )

    exit_code, rendered = _run(root, "codex", capsys)

    assert exit_code == 0
    assert rendered["disposition"] == "accepted"
    assert rendered["attempt_count"] == 2
    assert _verifier(root, rendered, 1)["exit_code"] == first_band
    assert _verifier(root, rendered, 2)["exit_code"] == 0
    feedback_bytes, feedback = _feedback(root, rendered)
    acceptance = feedback["required"][0]["acceptance"]
    assert feedback["schema_version"] == ASSURANCE_FEEDBACK_SCHEMA_VERSION
    assert acceptance["mode"] == "constraint-satisfaction"
    assert acceptance[branch]
    _assert_answer_free(feedback)
    consumed = _attempt_path(root, rendered, 2) / "candidate" / "feedback-consumed.bin"
    assert consumed.read_bytes() == feedback_bytes


def test_globally_empty_population_retains_band_two_and_parent_exit_fifteen(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = _make_experiment(
        tmp_path,
        monkeypatch,
        initial=EMPTY,
        produced=EMPTY,
        adapter="claude",
    )

    exit_code, rendered = _run(root, "claude", capsys)

    assert exit_code == cli.EXIT_SESSION_NOT_ACCEPTED == 15
    assert rendered["disposition"] == "budget-exhausted"
    payload = _verifier(root, rendered)
    assert payload["exit_code"] == 2
    assert payload["acceptance_ready"] is False
    _, feedback = _feedback(root, rendered)
    assert feedback["schema_version"] == ASSURANCE_FEEDBACK_SCHEMA_VERSION
    assert feedback["required"][0]["acceptance"]["vacuity_findings"]
    _assert_answer_free(feedback)


def test_band_zero_below_a_floor_retains_band_and_exits_fifteen_with_gap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = _make_experiment(
        tmp_path,
        monkeypatch,
        initial=NEAR_EMPTY,
        produced=NEAR_EMPTY,
        adapter="codex",
        min_facts=2,
    )

    exit_code, rendered = _run(root, "codex", capsys)

    assert exit_code == cli.EXIT_SESSION_NOT_ACCEPTED == 15
    assert rendered["disposition"] == "budget-exhausted"
    payload = _verifier(root, rendered)
    assert payload["exit_code"] == 0
    assert payload["acceptance_ready"] is True
    _, feedback = _feedback(root, rendered)
    acceptance = feedback["required"][0]["acceptance"]
    assert acceptance["coverage_gaps"] == [
        {
            "fact_type": FACT_TYPE,
            "required": 2,
            "observed": 1,
            "checker_declared": True,
        }
    ]
    _assert_answer_free(feedback)


@pytest.mark.parametrize(
    ("produced", "expected_exit", "expected_state"),
    [(SATISFYING_A, 0, "matched"), (SATISFYING_B, 15, "differs")],
)
def test_schema_v2_exact_mode_retains_byte_identity_control(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    produced: bytes,
    expected_exit: int,
    expected_state: str,
) -> None:
    root = _make_experiment(
        tmp_path,
        monkeypatch,
        initial=NEAR_EMPTY,
        produced=produced,
        adapter="codex",
        mode="exact-bytes",
        expected=SATISFYING_A,
    )

    exit_code, rendered = _run(root, "codex", capsys)

    assert exit_code == expected_exit
    assert _verifier(root, rendered)["exit_code"] == 0
    _, feedback = _feedback(root, rendered)
    acceptance = feedback["required"][0]["acceptance"]
    assert feedback["schema_version"] == ASSURANCE_FEEDBACK_SCHEMA_VERSION
    assert acceptance == {
        "mode": "exact-bytes",
        "outputs": [{"output_id": "population", "state": expected_state}],
    }
    _assert_answer_free(feedback)

