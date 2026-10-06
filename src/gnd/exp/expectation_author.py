"""Answer-free exact-expectation authoring for data-driven sessions."""

from __future__ import annotations

import json
import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from gnd import input_policy as _rf7_input
from gnd.artifacts import (
    DEFAULT_MAX_DEPTH,
    DEFAULT_MAX_FILES,
    DEFAULT_MAX_TOTAL_BYTES,
    ArtifactError,
    LeafSnapshot,
    inventory_tree,
    publish_leaf_atomic,
    read_regular_bounded,
    remove_regular_if_unchanged,
)
from gnd.exp.session_contract import (
    LEGACY_SESSION_CONTRACT_VERSION,
    MAX_SESSION_CONTRACT_BYTES,
    MAX_SESSION_INPUT_BYTES,
    DataDrivenContract,
    SessionContractError,
    read_session_contract,
)

CONTRACT_FILENAME = "session.contract.json"


class ExpectationAuthorError(Exception):
    """An authoring input or contract mutation was refused."""


class SurvivingAnswerError(ExpectationAuthorError):
    """One or more regular files still contain the produced answer bytes."""

    def __init__(self, paths: list[str]):
        self.paths = tuple(paths)
        super().__init__("answer bytes survive at: " + ", ".join(paths))


@dataclass(frozen=True)
class AuthoredExpectation:
    """The pathless expectation that was published."""

    experiment_root: Path
    case_id: str
    output_id: str
    candidate_path: str
    sha256: str
    contract_path: Path
    deleted_source: str


def _source_relative(root: Path, source: str | Path) -> str:
    supplied = Path(source)
    if supplied.is_absolute():
        try:
            relative = supplied.absolute().relative_to(root.absolute())
        except ValueError as error:
            raise ExpectationAuthorError(
                "--from must name a file inside the experiment root"
            ) from error
        value = relative.as_posix()
    else:
        value = supplied.as_posix()
    if value == CONTRACT_FILENAME:
        raise ExpectationAuthorError(
            f"--from may not name the contract itself ({CONTRACT_FILENAME})"
        )
    return value


def _render_contract(document: object, *, compact: bool) -> bytes:
    try:
        options: dict[str, object] = {
            "ensure_ascii": False,
            "allow_nan": False,
        }
        if compact:
            options["separators"] = (",", ":")
        else:
            options["indent"] = 2
        rendered = json.dumps(document, **options)
    except (TypeError, ValueError) as error:  # pragma: no cover - source JSON was closed
        raise ExpectationAuthorError(f"contract could not be rendered as strict JSON: {error}") from error
    return (rendered + "\n").encode("utf-8")


def _replace_expectation(
    document: dict[str, object],
    *,
    case_id: str,
    output_id: str,
    candidate_path: str,
    sha256: str,
    media_type: str,
    encoding: str,
) -> None:
    cases = document.get("cases")
    if not isinstance(cases, list):  # the real loader should have rejected this already
        raise ExpectationAuthorError("contract cases are not an array")
    selected = [case for case in cases if isinstance(case, dict) and case.get("case_id") == case_id]
    if not selected:
        raise ExpectationAuthorError(f"contract declares no case {case_id!r}")
    case = selected[0]
    if document.get("schema_version") == LEGACY_SESSION_CONTRACT_VERSION:
        outputs = case.get("expected_outputs")
    else:
        acceptance = case.get("acceptance")
        if not isinstance(acceptance, dict) or acceptance.get("mode") != "exact-bytes":
            raise ExpectationAuthorError(
                f"case {case_id!r} does not use exact-bytes acceptance"
            )
        outputs = acceptance.get("expected_outputs")
    if not isinstance(outputs, list):
        raise ExpectationAuthorError(f"case {case_id!r} has no expected-output array")

    values = {
        "media_type": media_type,
        "encoding": encoding,
        "sha256": sha256,
        "output_id": output_id,
        "candidate_path": candidate_path,
        "comparison": "exact-bytes",
    }
    for index, output in enumerate(outputs):
        if isinstance(output, dict) and output.get("output_id") == output_id:
            expectation = {
                key: values[key]
                for key in output
                if key in values
            }
            expectation.update(
                (key, value) for key, value in values.items() if key not in expectation
            )
            outputs[index] = expectation
            break
    else:
        outputs.append(values)


def _validate_staged_contract(
    root: Path,
    data: bytes,
    *,
    experiment_id: str,
) -> DataDrivenContract:
    descriptor, temporary = tempfile.mkstemp(prefix=".gnd-expectation-", dir=root)
    staged = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        return read_session_contract(
            staged,
            experiment_root=root,
            experiment_id=experiment_id,
        )
    finally:
        try:
            staged.unlink()
        except FileNotFoundError:
            pass


def _remaining_bound_paths(contract: DataDrivenContract) -> set[str]:
    paths: set[str] = set()
    for case in contract.cases:
        paths.update(bound.path for bound in case.inputs)
        paths.add(case.verify.model.path)
        paths.update(
            output.path for output in case.expected_outputs if output.path is not None
        )
    return paths


def _scan_answer_copies(
    root: Path,
    answer: bytes,
    answer_sha256: str,
    *,
    root_identity: tuple[int, int],
) -> list[str]:
    inventory = inventory_tree(
        root,
        max_files=DEFAULT_MAX_FILES,
        max_file_bytes=MAX_SESSION_INPUT_BYTES,
        max_total_bytes=DEFAULT_MAX_TOTAL_BYTES,
        max_depth=DEFAULT_MAX_DEPTH,
        expected_root=root_identity,
    )
    matches: list[str] = []
    for entry in inventory.files:
        if entry.size_bytes != len(answer) or entry.sha256 != answer_sha256:
            continue
        observed, _ = read_regular_bounded(
            root,
            entry.path,
            max_bytes=MAX_SESSION_INPUT_BYTES,
            expected_root=root_identity,
        )
        if observed == answer:
            matches.append(entry.path)
    return matches


def _rollback_contract(
    root: Path,
    original: bytes,
    published: LeafSnapshot,
    *,
    root_identity: tuple[int, int],
) -> None:
    try:
        publish_leaf_atomic(
            root,
            CONTRACT_FILENAME,
            original,
            expected=published,
            expected_root=root_identity,
        )
    except ArtifactError as rollback_error:
        raise ArtifactError(
            "authored contract could not be rolled back after final verification: "
            f"{rollback_error}"
        ) from rollback_error


def author_expectation(
    experiment_root: str | Path,
    *,
    experiment_id: str,
    case_id: str,
    output_id: str,
    candidate_path: str,
    source: str | Path,
    media_type: str,
    encoding: str,
) -> AuthoredExpectation:
    """Publish one pathless exact expectation and erase its source bytes.

    Validation and copy detection happen before mutation.  The disposable
    source is then identity-checked and removed before the contract CAS, so no
    failure can publish the new digest while leaving the source answer beside
    it.  The published contract is loaded through the production reader and
    the whole tree is scanned once more before success is returned.
    """

    root = Path(experiment_root).absolute()
    try:
        root_info = root.lstat()
    except OSError as error:
        raise ArtifactError(f"experiment root {root} could not be inspected: {error}") from error
    if stat.S_ISLNK(root_info.st_mode) or not stat.S_ISDIR(root_info.st_mode):
        raise ArtifactError(f"experiment root {root} must be a real directory")
    root_identity = (root_info.st_dev, root_info.st_ino)
    source_relative = _source_relative(root, source)

    contract_path = root / CONTRACT_FILENAME
    original, original_snapshot = read_regular_bounded(
        root,
        CONTRACT_FILENAME,
        max_bytes=MAX_SESSION_CONTRACT_BYTES,
        expected_root=root_identity,
    )
    try:
        answer, answer_snapshot = read_regular_bounded(
            root,
            source_relative,
            max_bytes=MAX_SESSION_INPUT_BYTES,
            expected_root=root_identity,
        )
    except ArtifactError as error:
        raise ExpectationAuthorError(f"--from {source_relative!r} was refused: {error}") from error

    try:
        document = _rf7_input.loads(
            original,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON number {token!r} is forbidden")
            ),
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        RecursionError,
    ) as error:
        raise SessionContractError(f"contract could not be decoded: {error}") from error
    if not isinstance(document, dict):
        raise ExpectationAuthorError("session contract must be a JSON object")
    _replace_expectation(
        document,
        case_id=case_id,
        output_id=output_id,
        candidate_path=candidate_path,
        sha256=answer_snapshot.sha256,
        media_type=media_type,
        encoding=encoding,
    )
    compact = b"\n" not in original.rstrip(b"\r\n")
    authored = _render_contract(document, compact=compact)
    staged_contract = _validate_staged_contract(
        root,
        authored,
        experiment_id=experiment_id,
    )
    if source_relative in _remaining_bound_paths(staged_contract):
        raise ExpectationAuthorError(
            f"--from {source_relative!r} remains bound elsewhere in the authored contract"
        )

    copies = _scan_answer_copies(
        root,
        answer,
        answer_snapshot.sha256,
        root_identity=root_identity,
    )
    unexpected = [path for path in copies if path != source_relative]
    if unexpected:
        raise SurvivingAnswerError(unexpected)
    if copies != [source_relative]:
        raise ExpectationAuthorError(
            f"--from {source_relative!r} changed or disappeared before deletion"
        )

    remove_regular_if_unchanged(
        root,
        source_relative,
        expected=answer_snapshot,
        expected_root=root_identity,
    )
    copies = _scan_answer_copies(
        root,
        answer,
        answer_snapshot.sha256,
        root_identity=root_identity,
    )
    if copies:
        raise SurvivingAnswerError(copies)

    published = publish_leaf_atomic(
        root,
        CONTRACT_FILENAME,
        authored,
        expected=original_snapshot,
        expected_root=root_identity,
    )
    try:
        read_session_contract(
            contract_path,
            experiment_root=root,
            experiment_id=experiment_id,
        )
        copies = _scan_answer_copies(
            root,
            answer,
            answer_snapshot.sha256,
            root_identity=root_identity,
        )
        if copies:
            raise SurvivingAnswerError(copies)
    except (ArtifactError, ExpectationAuthorError, SessionContractError):
        _rollback_contract(
            root,
            original,
            published,
            root_identity=root_identity,
        )
        raise

    return AuthoredExpectation(
        experiment_root=root,
        case_id=case_id,
        output_id=output_id,
        candidate_path=PurePosixPath(candidate_path).as_posix(),
        sha256=answer_snapshot.sha256,
        contract_path=contract_path,
        deleted_source=source_relative,
    )
