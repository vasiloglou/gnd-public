










































from __future__ import annotations

from pathlib import Path

import pytest

from gnd.exp.paths import (
    EvidencePathError,
    evidence_path_issue,
    resolve_evidence_path,
)

FIELD = "evidence"


@pytest.fixture
def experiment(tmp_path: Path) -> Path:

    root = tmp_path / "EXP-001-probe"
    (root / "sub").mkdir(parents=True)
    (root / "SPEC.md").write_text("---\nid: EXP-001-probe\n---\n", encoding="utf-8")
    (root / "ok.txt").write_text("evidence\n", encoding="utf-8")
    (root / "sub" / "deep.txt").write_text("evidence\n", encoding="utf-8")
    (tmp_path / "escape.txt").write_text("outside\n", encoding="utf-8")
    (tmp_path / "out.txt").write_text("outside\n", encoding="utf-8")
    return root / "SPEC.md"







def test_a_relative_file_beside_the_spec_is_accepted(experiment: Path) -> None:
    resolved = resolve_evidence_path(experiment, "ok.txt", field=FIELD)
    assert resolved == (experiment.parent / "ok.txt").resolve()
    assert resolved.is_file()


def test_a_nested_relative_file_is_accepted(experiment: Path) -> None:
    resolved = resolve_evidence_path(experiment, "sub/deep.txt", field=FIELD)
    assert resolved == (experiment.parent / "sub" / "deep.txt").resolve()







def test_a_parent_escaping_evidence_pointer_is_refused(experiment: Path) -> None:

    with pytest.raises(EvidencePathError) as caught:
        resolve_evidence_path(experiment, "../escape.txt", field=FIELD)
    message = str(caught.value)
    assert FIELD in message and "../escape.txt" in message


def test_a_pointer_climbing_out_through_a_child_is_refused(experiment: Path) -> None:

    with pytest.raises(EvidencePathError) as caught:
        resolve_evidence_path(experiment, "a/../../out.txt", field=FIELD)
    message = str(caught.value)
    assert FIELD in message and "a/../../out.txt" in message


def test_a_posix_absolute_evidence_pointer_is_refused(experiment: Path) -> None:







    with pytest.raises(EvidencePathError) as caught:
        resolve_evidence_path(experiment, "/usr/bin/env", field=FIELD)
    message = str(caught.value)
    assert FIELD in message and "/usr/bin/env" in message


def test_a_symlink_component_is_refused(experiment: Path) -> None:

    (experiment.parent / "link").symlink_to(experiment.parent / "sub")
    with pytest.raises(EvidencePathError) as caught:
        resolve_evidence_path(experiment, "link/deep.txt", field=FIELD)
    message = str(caught.value)
    assert FIELD in message and "link/deep.txt" in message







def test_a_windows_absolute_evidence_pointer_is_refused(experiment: Path) -> None:
























    value = "C:\\evil"

    issue = evidence_path_issue(FIELD, value)
    assert issue is not None, (
        "the LEXICAL half accepted a Windows-absolute pointer — containment "
        "cannot substitute for it (RESEARCH §6.2 measured ACCEPT)"
    )
    assert issue.path == FIELD
    
    
    assert repr(value) in issue.message
    assert "absolute" in issue.message.lower()

    with pytest.raises(EvidencePathError) as caught:
        resolve_evidence_path(experiment, value, field=FIELD)
    assert FIELD in str(caught.value) and repr(value) in str(caught.value)


def test_a_non_escaping_dot_dot_is_still_refused(experiment: Path) -> None:








    with pytest.raises(EvidencePathError) as caught:
        resolve_evidence_path(experiment, "sub/../ok.txt", field=FIELD)
    message = str(caught.value)
    assert FIELD in message and "sub/../ok.txt" in message


def test_an_empty_evidence_pointer_is_refused_lexically_before_any_filesystem_call() -> None:








    issue = evidence_path_issue(FIELD, "")
    assert issue is not None
    assert issue.path == FIELD
    assert "empty" in issue.message.lower()


def test_a_whitespace_only_evidence_pointer_is_refused_lexically() -> None:

    issue = evidence_path_issue(FIELD, "   ")
    assert issue is not None
    assert issue.path == FIELD
    assert "empty" in issue.message.lower()


def test_a_lexically_legal_pointer_yields_no_issue_without_touching_the_disk() -> None:





    assert evidence_path_issue(FIELD, "missing.txt") is None
    assert evidence_path_issue(FIELD, "sub/deep.txt") is None







def test_an_evidence_pointer_naming_a_directory_is_refused(experiment: Path) -> None:







    with pytest.raises(EvidencePathError) as caught:
        resolve_evidence_path(experiment, "sub", field=FIELD)
    message = str(caught.value)
    assert FIELD in message and "'sub'" in message
    assert "directory" in message.lower()


def test_a_missing_evidence_file_is_refused(experiment: Path) -> None:

    with pytest.raises(EvidencePathError) as caught:
        resolve_evidence_path(experiment, "missing.txt", field=FIELD)
    message = str(caught.value)
    assert FIELD in message and "missing.txt" in message
    assert "not exist" in message.lower() or "does not" in message.lower()


def test_an_empty_evidence_pointer_is_refused_by_resolution_too(experiment: Path) -> None:









    with pytest.raises(EvidencePathError) as caught:
        resolve_evidence_path(experiment, "", field=FIELD)
    assert FIELD in str(caught.value)







def test_the_error_carries_validation_issues(experiment: Path) -> None:
    with pytest.raises(EvidencePathError) as caught:
        resolve_evidence_path(experiment, "../escape.txt", field=FIELD)
    issues = caught.value.issues
    assert issues, "EvidencePathError carried no ValidationIssue records"
    assert all(issue.path == FIELD for issue in issues)
    assert all(issue.rule_id.startswith("experiment:") for issue in issues)


def test_the_lexical_half_is_the_shipped_one_not_a_third_path_notion() -> None:






    from gnd.extract import manifest

    assert "manifest_path_issue" in manifest.__all__
    assert manifest.manifest_path_issue("f", "C:\\evil", "r") is not None
    assert manifest.manifest_path_issue("f", "ok.txt", "r") is None
