"""Public fake-reviewer reference controls; no provider or retained private run."""
from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path
from typing import Any

import pytest
from support.digests import sha256_bytes as _sha256
from test_review_bands import _capability_help

from gnd import cli
from gnd.cli import main
from gnd.review.adapters import REVIEWER_IDS, ReviewerId, ReviewerPolicy, reviewer_policies
from gnd.review.runner import load_panel_run

REPO_ROOT = Path(__file__).resolve().parent.parent


REVIEW_CORPUS = REPO_ROOT / "tests" / "fixtures" / "public-review-reference" / "review.json"


REQUIRED_CASE_IDS = (
    "review-quorum-agreed-divergent",
    "review-two-successes-inconclusive",
    "review-failures-excluded-inconclusive",
    "review-prompt-injection-no-write",
)


BEHAVIOR_STATUS = {
    "success": "success",
    "incompatible": "incompatible",
    "missing": "missing",
    "timeout": "timeout",
    "auth": "auth-failure",
    "malformed": "malformed",
}


LEGACY_REVIEWER_IDS = tuple(ReviewerId)


def _corpus() -> list[dict[str, Any]]:
    return json.loads(REVIEW_CORPUS.read_text(encoding="utf-8"))


def _case(case_id: str) -> dict[str, Any]:
    return next(case for case in _corpus() if case["case_id"] == case_id)


def _blob_bytes(blob: dict[str, Any]) -> bytes:
    """Recompute a committed blob's bytes and prove its recorded identity."""

    raw = blob["bytes"].encode(blob["encoding"])
    assert len(raw) == blob["size_bytes"], f"{blob['path']} size_bytes is stale"
    assert _sha256(raw) == blob["sha256"], f"{blob['path']} sha256 is stale"
    return raw


def _script(seats: list[tuple[ReviewerPolicy, str, bytes]]) -> str:
    """One deterministic fake reviewer executable. It never touches the reviewed tree.

    The claude executable carries the claude and glm seats; which one an
    invocation is can only be read from the per-seat projected environment.
    """
    helps = {_capability_help(policy) for policy, _behavior, _response in seats}
    assert len(helps) == 1, "one executable has one help surface"
    capability = helps.pop()
    seat_config = {
        policy.reviewer_id.value: {"behavior": behavior, "response": response}
        for policy, behavior, response in seats
    }
    return f"""#!{sys.executable}
import os
import sys
import time

seat_config = {seat_config!r}
if len(seat_config) == 1:
    reviewer = next(iter(seat_config))
else:
    reviewer = 'glm' if os.environ.get('ANTHROPIC_BASE_URL') == 'https://api.z.ai/api/anthropic' else 'claude'
behavior = seat_config[reviewer]['behavior']
response = seat_config[reviewer]['response']

if '--help' in sys.argv:
    if behavior == 'incompatible':
        sys.stdout.write('usage: reviewer [options]\\nmissing required invocation flag\\n')
    else:
        sys.stdout.write({capability!r})
    raise SystemExit(0)

sys.stdin.buffer.read()

if behavior == 'success':
    os.write(1, response)
elif behavior == 'timeout':
    time.sleep(30)
elif behavior == 'auth':
    sys.stderr.write('authentication required: invalid api key')
    raise SystemExit(7)
elif behavior == 'malformed':
    os.write(1, b'{{"schema_version":1,"reviewer_id":')
else:
    raise SystemExit('unknown corpus behavior ' + behavior)
"""


def _install_fake_reviewers(
    bin_dir: Path,
    behaviors: dict[str, str],
    responses: dict[str, bytes],
) -> None:
    bin_dir.mkdir(parents=True, exist_ok=True)
    groups: dict[str, list[ReviewerPolicy]] = {}
    for policy in reviewer_policies():
        groups.setdefault(policy.executable_name, []).append(policy)
    for name, group in groups.items():
        seats = [
            (
                policy,
                behaviors[policy.reviewer_id.value],
                responses.get(policy.reviewer_id.value, b""),
            )
            for policy in group
        ]
        missing = [policy for policy, behavior, _response in seats if behavior == "missing"]
        if missing and len(missing) < len(group):
            raise AssertionError(
                f"{name!r} is one executable shared by "
                f"{[policy.reviewer_id.value for policy in group]}; "
                "it cannot be missing for one seat only"
            )
        if missing:
            continue
        executable = bin_dir / name
        executable.write_text(_script(seats), encoding="utf-8")
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)


def _sanitize_environment(
    monkeypatch: pytest.MonkeyPatch,
    bin_dir: Path,
    home: Path,
) -> None:
    """Leave the process environment with an absolute fake PATH and no secrets."""

    for name in list(os.environ):
        if name not in {"PATH", "HOME", "TMPDIR", "LANG", "TERM", "USER", "LOGNAME"}:
            monkeypatch.delenv(name, raising=False)
    home.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / "config"))
    monkeypatch.setenv(
        "PATH",
        os.pathsep.join(
            dict.fromkeys([str(bin_dir), str(Path(sys.executable).parent), "/usr/bin", "/bin"])
        ),
    )


def _tree_digests(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root).as_posix()): _sha256(path.read_bytes())
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _published(run_directory: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(run_directory).as_posix()): path.read_bytes()
        for path in sorted(run_directory.rglob("*"))
        if path.is_file()
    }


def _active_successes(case: dict[str, Any]) -> list[str]:
    return [
        reviewer.value
        for reviewer in REVIEWER_IDS
        if case["reviewer_behaviors"][reviewer.value] == "success"
    ]


def _active_inventory(case: dict[str, Any]) -> list[str]:
    paths = {"request.json", "run.json"}
    for entry in case["expected_evidence"]["reviewers"]:
        if entry["reviewer_id"] not in {reviewer.value for reviewer in REVIEWER_IDS}:
            continue
        paths.update(
            {
                entry["capability_stdout_path"],
                entry["capability_stderr_path"],
                entry["stdout_path"],
                entry["stderr_path"],
                entry["envelope_path"],
            }
        )
        if entry["status"] == "success":
            paths.add(entry["response_path"])
    return sorted(paths)


def _prepare(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, case: dict[str, Any]) -> Path:
    """Materialize one corpus row as a repository plus sanitized fake reviewers."""

    repository = tmp_path / "repo"
    repository.mkdir()
    for blob in case["input_blobs"]:
        target = repository / blob["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(_blob_bytes(blob))
    (repository / "request.json").write_bytes(_blob_bytes(case["request_blob"]))

    responses = {
        blob["path"].split("/")[1]: _blob_bytes(blob)
        for blob in case["reviewer_response_blobs"]
    }
    _install_fake_reviewers(tmp_path / "bin", case["reviewer_behaviors"], responses)
    _sanitize_environment(monkeypatch, tmp_path / "bin", tmp_path / "home")
    monkeypatch.chdir(repository)
    return repository


def _panel(run_directory: Path) -> list[str]:
    return [
        "review",
        "panel",
        "request.json",
        "--out",
        str(run_directory),
        # 6s, not 1.5s: the reviewer deadline is shared between the capability
        # probe and the invocation, and one cold fake spawn -- measured over a
        # second -- flips a reviewer to 'timeout', drops quorum, and fails a
        # corpus row for a scheduling reason. The fakes answer in milliseconds,
        # so no e2e test's runtime changes.
        "--reviewer-timeout",
        "6",
        "--overall-timeout",
        "20",
        "--max-output-bytes",
        "65536",
    ]


def test_the_review_corpus_has_exactly_the_four_required_rows() -> None:
    cases = _corpus()
    assert [case["case_id"] for case in cases] == list(REQUIRED_CASE_IDS)
    assert len({case["case_id"] for case in cases}) == 4


@pytest.mark.parametrize("case_id", REQUIRED_CASE_IDS)
def test_every_recorded_digest_recomputes_from_its_committed_blob(case_id: str) -> None:
    """No recipe stands in for bytes. ``_blob_bytes`` re-derives every digest."""

    case = _case(case_id)
    blobs = [case["request_blob"], *case["input_blobs"], *case["reviewer_response_blobs"]]
    if case["synthesis_blob"] is not None:
        blobs.append(case["synthesis_blob"])
    assert blobs, "a corpus row that binds no bytes proves nothing"
    for blob in blobs:
        assert _blob_bytes(blob)


@pytest.mark.parametrize("case_id", REQUIRED_CASE_IDS)
def test_every_row_declares_a_complete_evidence_inventory(case_id: str) -> None:
    case = _case(case_id)
    evidence = case["expected_evidence"]

    assert evidence["normalized_request_path"] == "request.json"
    assert evidence["run_marker_path"] == "run.json"
    assert [entry["reviewer_id"] for entry in evidence["reviewers"]] == [
        reviewer.value for reviewer in LEGACY_REVIEWER_IDS
    ], "the inventory must name every reviewer in fixed order"

    derived = {"request.json", "run.json"}
    for entry in evidence["reviewers"]:
        prefix = f"reviewers/{entry['reviewer_id']}"
        assert entry["capability_stdout_path"] == f"{prefix}/capability.stdout"
        assert entry["capability_stderr_path"] == f"{prefix}/capability.stderr"
        assert entry["stdout_path"] == f"{prefix}/stdout"
        assert entry["stderr_path"] == f"{prefix}/stderr"
        assert entry["envelope_path"] == f"{prefix}/envelope.json"
        derived.update(
            {
                entry["capability_stdout_path"],
                entry["capability_stderr_path"],
                entry["stdout_path"],
                entry["stderr_path"],
                entry["envelope_path"],
            }
        )
        if entry["status"] == "success":
            assert entry["response_path"] == f"{prefix}/response.json"
            derived.add(entry["response_path"])
        else:
            assert entry["response_path"] is None, (
                "a failed reviewer cannot carry a validated response"
            )
    assert sorted(derived) == evidence["run_directory_inventory"]
    assert evidence["tree_integrity"] == {
        "before_field": "reviewed_artifacts_before_sha256",
        "after_field": "reviewed_artifacts_after_sha256",
        "must_be_equal": True,
    }


@pytest.mark.parametrize("case_id", REQUIRED_CASE_IDS)
def test_the_declared_status_of_every_reviewer_follows_from_its_behavior(case_id: str) -> None:
    case = _case(case_id)
    statuses = {
        entry["reviewer_id"]: entry["status"] for entry in case["expected_evidence"]["reviewers"]
    }
    for reviewer, behavior in case["reviewer_behaviors"].items():
        assert statuses[reviewer] == BEHAVIOR_STATUS[behavior]


def test_quorum_rows_carry_at_least_three_distinct_successful_reviewers() -> None:
    quorum_rows = [case for case in _corpus() if case["machine_label"]["quorum_met"]]
    assert {case["case_id"] for case in quorum_rows} == {
        "review-quorum-agreed-divergent",
        "review-prompt-injection-no-write",
    }
    for case in quorum_rows:
        successes = case["machine_label"]["successful_reviewer_ids"]
        assert len(set(successes)) == len(successes) >= 3
        assert case["expected_exit"] == 0
        assert case["expected_evidence"]["synthesis_path"] == "synthesis.json"
        assert case["expected_evidence"]["report_path"] == "PANEL-REVIEW.md"


def test_both_below_quorum_rows_are_inconclusive_and_keep_every_attempt() -> None:
    below = [case for case in _corpus() if not case["machine_label"]["quorum_met"]]
    assert {case["case_id"] for case in below} == {
        "review-two-successes-inconclusive",
        "review-failures-excluded-inconclusive",
    }
    for case in below:
        label = case["machine_label"]
        assert label["disposition"] == "inconclusive-below-quorum"
        assert len(label["successful_reviewer_ids"]) < 3
        assert case["expected_exit"] == cli.EXIT_REVIEW_INCONCLUSIVE
        assert case["expected_evidence"]["synthesis_path"] is None
        assert case["expected_evidence"]["report_path"] is None
        # Every attempt is still on the record, failures included.
        assert len(case["expected_evidence"]["reviewers"]) == 6


def test_the_exactly_two_row_has_two_successes_that_agree() -> None:
    """Agreement cardinality is not quorum: two reviewers who say the same thing
    are still two reviewers (D-20 versus D-21)."""

    case = _case("review-two-successes-inconclusive")
    assert case["machine_label"]["successful_reviewer_ids"] == ["claude", "codex"]
    concerns = [
        json.loads(_blob_bytes(blob))["concerns"] for blob in case["reviewer_response_blobs"]
    ]
    assert len(concerns) == 2
    locations = {entry["evidence"][0]["location"] for group in concerns for entry in group}
    assert len(locations) == 1, "the two successes must cite the same location to agree"


def test_the_failure_row_carries_five_distinct_outcomes() -> None:
    """Timeout, auth failure (twice — the glm seat's absent credential is the
    second), missing CLI, malformed output, and one success — so no combination
    of failures can accidentally retain quorum."""

    case = _case("review-failures-excluded-inconclusive")
    statuses = [entry["status"] for entry in case["expected_evidence"]["reviewers"]]
    assert sorted(statuses) == sorted(
        ["timeout", "auth-failure", "missing", "malformed", "success", "auth-failure"]
    )
    assert len(set(statuses)) == 5


@pytest.mark.parametrize("case_id", REQUIRED_CASE_IDS)
def test_each_corpus_row_runs_through_main_and_publishes_its_declared_evidence(
    case_id: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    case = _case(case_id)
    repository = _prepare(tmp_path, monkeypatch, case)
    before = _tree_digests(repository)
    run_directory = tmp_path / "panel-run"

    exit_code = main(_panel(run_directory))
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == case["expected_exit"]
    successful = _active_successes(case)
    assert payload["command"] == "review panel"
    assert payload["advisory"] is True
    assert payload["required_successes"] == 3
    assert payload["attempted_reviewer_ids"] == [reviewer.value for reviewer in REVIEWER_IDS]
    assert payload["successful_reviewer_ids"] == successful
    assert payload["quorum_met"] is (len(successful) >= 3)

    evidence = case["expected_evidence"]
    published = _published(run_directory)
    assert sorted(published) == _active_inventory(case)

    run = load_panel_run(run_directory)
    assert [envelope.reviewer_id.value for envelope in run.envelopes] == [
        entry["reviewer_id"]
        for entry in evidence["reviewers"]
        if entry["reviewer_id"] in {reviewer.value for reviewer in REVIEWER_IDS}
    ]
    assert [envelope.status.value for envelope in run.envelopes] == [
        entry["status"]
        for entry in evidence["reviewers"]
        if entry["reviewer_id"] in {reviewer.value for reviewer in REVIEWER_IDS}
    ]
    assert run.quorum_met is (len(successful) >= 3)
    assert [reviewer.value for reviewer in run.successful_reviewer_ids] == successful
    assert run.reviewed_artifacts_before_sha256 == run.reviewed_artifacts_after_sha256

    # Every reviewer that succeeded had its exact committed bytes retained raw.
    for blob in case["reviewer_response_blobs"]:
        if blob["path"].split("/")[1] in {reviewer.value for reviewer in REVIEWER_IDS}:
            assert published[blob["path"]] == _blob_bytes(blob)
    # Every reviewer that failed still carries a closed envelope and an issue.
    for envelope in run.envelopes:
        if envelope.status.value == "success":
            assert envelope.response is not None
            continue
        assert envelope.response is None
        assert envelope.issues, f"{envelope.reviewer_id.value} lost its failure reason"

    assert _tree_digests(repository) == before, "the panel changed the reviewed tree"


@pytest.mark.parametrize(
    "case_id", ("review-quorum-agreed-divergent", "review-prompt-injection-no-write")
)
def test_a_quorum_row_finalizes_into_an_advisory_report_and_writes_nothing_else(
    case_id: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    case = _case(case_id)
    repository = _prepare(tmp_path, monkeypatch, case)
    run_directory = tmp_path / "panel-run"
    assert main(_panel(run_directory)) == 0
    capsys.readouterr()
    before = _tree_digests(repository)
    published = _published(run_directory)

    # The committed synthesis binds the run by digest; only that one field is
    # substituted, and the corpus says so in run_digest_binding.
    binding = case["run_digest_binding"]
    synthesis = json.loads(_blob_bytes(case["synthesis_blob"]))
    assert synthesis[binding["field"]] == binding["placeholder"]
    synthesis[binding["field"]] = _sha256(published["run.json"])
    synthesis_path = tmp_path / "synthesis.json"
    synthesis_path.write_text(json.dumps(synthesis, sort_keys=True), encoding="utf-8")

    report_path = tmp_path / "PANEL-REVIEW.md"
    exit_code = main(
        ["review", "finalize", str(run_directory), str(synthesis_path), "--out", str(report_path)]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["command"] == "review finalize"
    assert payload["advisory"] is True
    assert payload["agreed_concern_count"] == len(synthesis["agreed_concerns"])
    assert payload["divergent_concern_count"] == len(synthesis["divergent_concerns"])
    assert payload["prioritized_fix_count"] == len(synthesis["prioritized_fixes"])
    assert payload["successful_reviewer_ids"] == _active_successes(case)

    report = report_path.read_text(encoding="utf-8")
    for heading in (
        "# Panel Review",
        "## Agreed Concerns",
        "## Divergent Views",
        "## Prioritized Fix Plan",
        "## Advisory Boundary",
    ):
        assert heading in report
    assert "no changes were applied to reviewed artifacts" in report

    assert _tree_digests(repository) == before, "finalization changed the reviewed tree"
    assert _published(run_directory) == published, "finalization mutated immutable run evidence"


def test_a_prompt_injection_in_the_reviewed_document_changes_no_reviewed_byte(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The reviewed plan tells the reviewer to overwrite it and to create a new
    file. Three reviewers succeed, the instruction reaches the panel only as
    quoted evidence, and both demands are refused by construction: the panel has
    no writer surface at all."""

    case = _case("review-prompt-injection-no-write")
    plan_blob = next(blob for blob in case["input_blobs"] if blob["path"] == "plan.md")
    assert "IGNORE ALL PREVIOUS INSTRUCTIONS" in plan_blob["bytes"]
    assert "pwned.txt" in plan_blob["bytes"]

    repository = _prepare(tmp_path, monkeypatch, case)
    before = _tree_digests(repository)
    run_directory = tmp_path / "panel-run"

    assert main(_panel(run_directory)) == 0
    capsys.readouterr()

    after = _tree_digests(repository)
    assert after == before
    assert set(after) == {"plan.md", "request.json"}
    assert not (repository / "pwned.txt").exists()
    assert (repository / "plan.md").read_bytes() == _blob_bytes(plan_blob)

    run = load_panel_run(run_directory)
    assert len(run.successful_reviewer_ids) == 3, "the injection row sits on the quorum boundary"
    quoted = [
        evidence.observation
        for envelope in run.envelopes
        if envelope.response is not None
        for concern in envelope.response.concerns
        for evidence in concern.evidence
    ]
    assert any("IGNORE ALL PREVIOUS INSTRUCTIONS" in text for text in quoted), (
        "the malicious text must survive as quoted evidence, not be scrubbed"
    )


def test_kimi_is_an_active_argv_prompt_reviewer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Current fan-out includes Kimi through its documented prompt mode."""

    policies = {policy.reviewer_id.value: policy for policy in reviewer_policies()}
    assert len(policies) == 6
    assert set(policies) == {"claude", "codex", "qwen", "gemini", "kimi", "glm"}
    assert {policy.prompt_transport for policy in policies.values()} == {"stdin", "argv"}
    assert policies["kimi"].prompt_transport == "argv"
    assert policies["kimi"].invocation_argv[-1] == "--prompt"
    assert "stream-json" in policies["kimi"].invocation_argv
    assert ReviewerId("kimi") is ReviewerId.kimi
    assert {policy.capability_proof for policy in policies.values()} == {
        "help-invocation-flags-v1"
    }

    case = _case("review-quorum-agreed-divergent")
    _prepare(tmp_path, monkeypatch, case)
    run_directory = tmp_path / "panel-run"

    exit_code = main(_panel(run_directory))
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert len(payload["attempted_reviewer_ids"]) == 6
    assert payload["attempted_reviewer_ids"][-2] == "kimi"
    assert payload["attempted_reviewer_ids"][-1] == "glm"
    assert len(payload["successful_reviewer_ids"]) == 4
    assert payload["quorum_met"] is True

    run = load_panel_run(run_directory)
    kimi = next(item for item in run.envelopes if item.reviewer_id is ReviewerId.kimi)
    assert kimi.status.value == "incompatible"


