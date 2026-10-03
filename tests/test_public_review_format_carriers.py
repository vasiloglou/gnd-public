"""Review format guards over synthetic retained runs; no stored private evidence."""

from pathlib import Path

import pytest
from test_review_report import _run

from gnd.artifacts import canonical_json_bytes
from gnd.review.adapters import ReviewerId
from gnd.review.request import canonical_review_request, parse_reviewer_response_with_salvage
from gnd.review.runner import PanelRun, ReviewerEnvelope, canonical_panel_run, load_panel_run

REPOSITORY = Path(__file__).resolve().parent


def _write_synthetic_run(root: Path, version: int) -> None:
    # This is modelled process evidence, not a claim that a reviewer was invoked.
    legacy = _run((ReviewerId.claude,))
    envelopes = []
    for envelope in legacy.envelopes:
        if envelope.response is not None and version >= 2:
            payload = envelope.response.model_dump_json().encode()
            parsed = parse_reviewer_response_with_salvage(
                payload,
                expected_reviewer=envelope.reviewer_id.value,
                allowed_artifact_paths=("plan.md",),
            )
            envelope = ReviewerEnvelope.model_validate(
                envelope.model_dump(mode="python") | {"response_salvage": parsed.salvage}
            )
        envelopes.append(envelope)
    run = PanelRun.model_validate(
        legacy.model_dump(mode="python")
        | {"schema_version": version, "envelopes": tuple(envelopes)}
    )
    root.mkdir()
    (root / "request.json").write_bytes(canonical_review_request(run.request))
    for envelope in run.envelopes:
        directory = root / "reviewers" / envelope.reviewer_id.value
        directory.mkdir(parents=True)
        (directory / "envelope.json").write_bytes(canonical_json_bytes(envelope))
        for process, output_name, error_name in (
            (envelope.capability, "capability.stdout", "capability.stderr"),
            (envelope.invocation, "stdout", "stderr"),
        ):
            if process is None:
                output, error = b"", b""
            elif output_name == "capability.stdout":
                output, error = b"read-only mode supported\n", b"capability probe stderr\n"
            else:
                output, error = envelope.response.model_dump_json().encode(), b""
            (directory / output_name).write_bytes(output)
            (directory / error_name).write_bytes(error)
        if envelope.response is not None:
            (directory / "response.json").write_bytes(canonical_json_bytes(envelope.response))
    (root / "run.json").write_bytes(canonical_panel_run(run))
    # Cross-check every retained stream and nested record through the real loader.
    assert canonical_panel_run(load_panel_run(root)) == (root / "run.json").read_bytes()


@pytest.fixture(autouse=True)
def _synthetic_repository(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for version in (1, 2, 3):
        _write_synthetic_run(tmp_path / f"public-run-v{version}", version)
    monkeypatch.setitem(globals(), "REPOSITORY", tmp_path)


def test_a_schema_version_two_run_must_carry_a_salvage_record_for_every_success(
    tmp_path: Path,
) -> None:
    """Without the version bump, validation could not tell pre-salvage evidence
    from new evidence whose required record went missing.
    """

    from gnd.review.runner import PANEL_RUN_SCHEMA_VERSION, PanelRun

    assert PANEL_RUN_SCHEMA_VERSION >= 2

    run = load_panel_run(REPOSITORY / "public-run-v1")
    assert run.schema_version == 1

    for version in (2, PANEL_RUN_SCHEMA_VERSION):
        document = run.model_dump(mode="python") | {"schema_version": version}
        with pytest.raises(Exception, match="salvage record"):
            PanelRun.model_validate(document)


def test_a_schema_version_one_run_may_not_carry_a_salvage_record() -> None:
    """The other half of the version invariant: v1 means pre-salvage evidence,
    so a v1 run carrying a record is as refused as a v2 run missing one.
    """

    from gnd.review.runner import PanelRun

    run = load_panel_run(REPOSITORY / "public-run-v2")
    assert run.schema_version == 2

    with pytest.raises(Exception, match="predates the salvage record"):
        PanelRun.model_validate(run.model_dump(mode="python") | {"schema_version": 1})


def test_falsifying_a_salvage_record_changes_the_run_digest() -> None:
    """Load-bearing in the note's §8: the loader binds the record to the run, so
    a forged record is not silent against a synthesis that cites the run digest.
    """

    from gnd.review.runner import PanelRun

    run = load_panel_run(REPOSITORY / "public-run-v2")
    envelope = next(e for e in run.envelopes if e.response_salvage is not None)
    forged = ReviewerEnvelope.model_validate(
        envelope.model_dump(mode="python")
        | {
            "response_salvage": envelope.response_salvage.model_dump(mode="python")
            | {"preamble_lines": 3, "complete": False}
        }
    )
    tampered = PanelRun.model_validate(
        run.model_dump(mode="python")
        | {"envelopes": tuple(forged if e is envelope else e for e in run.envelopes)}
    )

    assert canonical_panel_run(tampered) != canonical_panel_run(run)


def test_a_measured_era_success_must_carry_its_evidence_resolution() -> None:
    """v4 introduced engagement measurement; every later writer retains it.

    A measured-era success without the
    measurement is evidence with its record missing, and earlier versions must
    refuse to carry a record their writer could not have produced.
    """

    from gnd.review.runner import PANEL_RUN_SCHEMA_VERSION, PanelRun

    assert PANEL_RUN_SCHEMA_VERSION >= 4

    run = load_panel_run(REPOSITORY / "public-run-v3")
    assert run.schema_version == 3

    with pytest.raises(Exception, match="evidence resolution"):
        PanelRun.model_validate(run.model_dump(mode="python") | {"schema_version": 4})
