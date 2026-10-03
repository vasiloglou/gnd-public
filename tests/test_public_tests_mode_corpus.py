"""The Phase 3 tests-mode corpus, driven through the promised public surfaces.

The fixtures are the approval instrument.  This harness supplies mechanics only:
it expands the closed recipes under ``tmp_path``, calls the CLI, and compares the
observation with ``expected.json``.  It deliberately does not restate case verdicts.
"""

from __future__ import annotations

import base64
import codecs
import contextlib
import errno
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import socket
import stat
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from gnd.checker import band, check
from gnd.cli import main
from gnd.exp.session_contract import read_session_contract
from gnd.measure.score import withholds_acceptance
from gnd.model import load_model
from gnd.population import load_population

HERE = Path(__file__).resolve().parent
# Complete reviewed corpus, packed to keep the public path inventory bounded.
_PUBLIC_CORPUS_ARCHIVE = HERE / "fixtures" / "public-tests-mode" / "workspace.json.gz"
_PUBLIC_CORPUS_RAW = _PUBLIC_CORPUS_ARCHIVE.read_bytes()
assert len(_PUBLIC_CORPUS_RAW) <= 64 * 1024
assert (
    hashlib.sha256(_PUBLIC_CORPUS_RAW).hexdigest()
    == "d52c7d3079c5441679fbdd0e733f8b661664b901e3f23facc923b452d0ce9a27"
)
with gzip.GzipFile(fileobj=io.BytesIO(_PUBLIC_CORPUS_RAW)) as _public_stream:
    _public_expanded = _public_stream.read(512 * 1024 + 1)
assert len(_public_expanded) <= 512 * 1024
_public_document = json.loads(_public_expanded)
assert _public_document["schema"] == 1
assert len(_public_document["members"]) == 344
_PUBLIC_CORPUS_TEMP = tempfile.TemporaryDirectory(prefix="gnd-public-tests-mode-")
CORPUS = Path(_PUBLIC_CORPUS_TEMP.name)
_public_seen = set()
for _public_member in _public_document["members"]:
    _public_relative = Path(_public_member["path"])
    assert not _public_relative.is_absolute()
    assert ".." not in _public_relative.parts
    assert _public_relative.as_posix() not in _public_seen
    _public_seen.add(_public_relative.as_posix())
    _public_bytes = base64.b64decode(_public_member["bytes_base64"], validate=True)
    assert len(_public_bytes) <= 100 * 1024
    assert hashlib.sha256(_public_bytes).hexdigest() == _public_member["sha256"]
    _public_bytes.decode("utf-8")
    assert _public_member["mode"] in (0o644, 0o755)
    _public_destination = CORPUS / _public_relative
    _public_destination.parent.mkdir(parents=True, exist_ok=True)
    _public_destination.write_bytes(_public_bytes)
    _public_destination.chmod(_public_member["mode"])
BASE = CORPUS / "base"
CASES = CORPUS / "cases"
EXPECTED = json.loads((CORPUS / "expected.json").read_text(encoding="utf-8"))
EXPECTED_BY_CASE = {entry["case"]: entry for entry in EXPECTED}

# One home: phase-3-spec.md section 5, "Rule and reason registry".
REASON_REGISTRY = frozenset(
    {
        "contract:shape",
        "tests:required-id",
        "tests:required-limit",
        "tests:protected-limit",
        "tests:protected-uncovered",
        "tests:protected-symlink",
        "tests:protected-digest",
        "tests:argv-echo-mismatch",
        "tests:argv-echo-divergent",
        "tests:results-path-relative",
        "cli:test-argv-required",
        "cli:test-argv-forbidden",
        "cli:work-covers-required",
        "kind:author-expectation-tests",
        "tests:copy-bytes",
        "tests:copy-entries",
        "tests:copy-depth",
        "tests:copy-special",
        "tests:results-preexisting",
        "tests:results-missing",
        "tests:results-path-symlink",
        "tests:results-path-type",
        "tests:child-timeout",
        "tests:child-signal",
        "tests:child-nonzero",
        "tests:descendant-survived",
        "tests:results-too-large",
        "tests:results-encoding",
        "tests:results-dtd",
        "tests:results-xml-limit",
        "tests:results-xml-malformed",
        "tests:junit-collision",
        "tests:junit-duplicate",
        "tests:junit-outcome",
        "tests:junit-summary",
        "tests:required-absent",
        "tests:required-not-passing",
        "tests:protected-mutated",
        "tests:directory-snapshot-moved",
        "tests:experiment-dir-moved",
        "tests:verifier-io",
    }
)

EXPERIMENT_ID = "EXP-303-tests-mode"
RESULT_PATH = "results/results.xml"
MAX_CONTRACT_BYTES = 1 * 1024 * 1024

PASS_XML = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<testsuite tests="1" failures="0" errors="0" skipped="0">'
    '<testcase classname="test_gate" name="test_pass"/>'
    "</testsuite>"
)


def _canonical_argv(argv: list[str]) -> bytes:
    return json.dumps(argv, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _base36(value: int) -> str:
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    out = "0"
    if value:
        chars: list[str] = []
        while value:
            value, digit = divmod(value, 36)
            chars.append(digits[digit])
        out = "".join(reversed(chars))
    return out


def _spec(kind: str) -> str:
    return (
        "---\n"
        f"id: {EXPERIMENT_ID}\n"
        f"kind: {kind}\n"
        "title: Phase 3 tests-mode corpus\n"
        "questions:\n"
        "  - id: Q1\n"
        "    text: Did the declared test observation hold?\n"
        "follows: []\n"
        "---\n\n"
        f"# {EXPERIMENT_ID}\n"
    )


def _remove(path: Path) -> None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return
    if stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode):
        shutil.rmtree(path)
    else:
        path.unlink()


def _safe_candidate_path(candidate: Path, relative: str) -> Path:
    pure = Path(relative)
    assert not pure.is_absolute() and ".." not in pure.parts
    return candidate / pure


def _write_candidate(
    candidate: Path,
    directive: dict[str, Any],
) -> None:
    target = _safe_candidate_path(candidate, directive["path"])
    target.parent.mkdir(parents=True, exist_ok=True)
    if "source" in directive:
        prefix, _, relative = directive["source"].partition(":")
        assert prefix == "base" and relative
        target.write_bytes((BASE / relative).read_bytes())
    else:
        target.write_text(directive["text"], encoding="utf-8")


def _tests_acceptance(document: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for case in document.get("cases", []):
        acceptance = case.get("acceptance")
        if isinstance(acceptance, dict) and acceptance.get("mode") == "tests":
            found.append(acceptance)
    return found


def _bound_file(root: Path, bound: dict[str, Any], protected_mode: str) -> None:
    relative = bound.get("path")
    if not isinstance(relative, str):
        return
    source = (BASE if protected_mode == "base" else root) / relative
    try:
        data = source.read_bytes()
    except (FileNotFoundError, IsADirectoryError, OSError):
        return
    bound["sha256"] = _digest(data)
    if "size_bytes" in bound:
        bound["size_bytes"] = len(data)


def _finalize_contract(
    document: Any,
    root: Path,
    candidate: Path,
    argv: list[str],
    *,
    protected_mode: str,
    echo_mode: str,
) -> None:
    if not isinstance(document, dict):
        return

    # Existing v1/v2 bindings and the non-tests v3 branch are experiment-relative.
    def visit(value: Any) -> None:
        if isinstance(value, dict):
            if "path" in value and "sha256" in value:
                _bound_file(root, value, "actual")
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(document)
    actual_echo = _digest(_canonical_argv(argv))
    for acceptance in _tests_acceptance(document):
        for protected in acceptance["protected"]:
            _bound_file(candidate, protected, protected_mode)
        if echo_mode == "actual":
            acceptance["test_argv_sha256"] = actual_echo
        elif echo_mode == "wrong":
            acceptance["test_argv_sha256"] = "f" * 64
        elif echo_mode == "divergent":
            acceptance["test_argv_sha256"] = actual_echo
        elif echo_mode == "preserve":
            pass
        else:  # pragma: no cover - the recipe vocabulary meta-test closes this branch
            raise AssertionError(f"unknown echo mode {echo_mode!r}")
    if echo_mode == "divergent":
        tests = _tests_acceptance(document)
        assert len(tests) >= 2
        tests[1]["test_argv_sha256"] = _digest(_canonical_argv(["different"]))


def _encoded_document(directive: dict[str, Any]) -> bytes:
    declaration = directive["declaration"]
    body = (
        f'<?xml version="1.0" encoding="{declaration}"?>'
        '<testsuite tests="1"><testcase classname="test_gate" name="test_pass"/>'
        "</testsuite>"
    )
    if directive["document"] == "doctype":
        body = body.split("?>", 1)[0] + "?><!DOCTYPE testsuite []>" + body.split("?>", 1)[1]
    codec = directive["codec"]
    bom = b""
    if directive.get("bom"):
        bom = codecs.BOM_UTF16_LE if codec == "utf-16le" else codecs.BOM_UTF16_BE
    return bom + body.encode(codec)


def _result_bytes(size: int) -> bytes:
    prefix = b'<?xml version="1.0" encoding="UTF-8"?><testsuite tests="1"><!--'
    suffix = b'--><testcase classname="test_gate" name="test_pass"/></testsuite>'
    padding = size - len(prefix) - len(suffix)
    assert padding >= 0
    return prefix + (b"x" * padding) + suffix


def _regular_byte_total(root: Path) -> int:
    total = 0
    for path in root.rglob("*"):
        info = path.lstat()
        if stat.S_ISREG(info.st_mode):
            total += info.st_size
    return total


def _entry_total(root: Path) -> int:
    return sum(1 for _ in root.rglob("*"))


class _Materialized:
    def __init__(self, name: str, root: Path, argv: list[str], lane: str):
        self.name = name
        self.root = root
        self.argv = argv
        self.lane = lane
        self.injections: list[dict[str, Any]] = []


def _materialize(name: str, tmp_path: Path) -> _Materialized:
    case_dir = CASES / name
    document: Any = json.loads((case_dir / "contract.json").read_text(encoding="utf-8"))
    argv = json.loads((case_dir / "argv.json").read_text(encoding="utf-8"))
    recipe = json.loads((case_dir / "materialize.json").read_text(encoding="utf-8"))
    assert isinstance(argv, list) and all(isinstance(word, str) for word in argv)

    root = tmp_path / "source" / EXPERIMENT_ID
    candidate = root / "candidate"
    root.mkdir(parents=True)
    shutil.copytree(BASE, candidate)
    (root / "SPEC.md").write_text(
        _spec("work" if recipe["lane"].startswith("author") else "data-driven"),
        encoding="utf-8",
    )
    materialized = _Materialized(name, root, argv, recipe["lane"])

    for directive in recipe["directives"]:
        operation = directive["op"]
        if operation == "write-file":
            if directive["path"].startswith("authoring/"):
                target = root / directive["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(directive["text"], encoding="utf-8")
            else:
                _write_candidate(candidate, directive)
        elif operation == "delete":
            _remove(_safe_candidate_path(candidate, directive["path"]))
        elif operation == "symlink":
            target = _safe_candidate_path(candidate, directive["path"])
            if directive.get("replace"):
                _remove(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(directive["target"])
        elif operation == "fifo":
            target = _safe_candidate_path(candidate, directive["path"])
            os.mkfifo(target)
        elif operation == "socket":
            target = _safe_candidate_path(candidate, directive["path"])
            channel = socket.socket(socket.AF_UNIX)
            try:
                # Darwin's sockaddr_un limit counts the supplied spelling.
                # Resolve the same fixture through a short cwd-relative name.
                with contextlib.chdir(candidate):
                    channel.bind(directive["path"])
            except PermissionError:
                # Some managed macOS sandboxes disable AF_UNIX bind entirely.
                # Keep materialization total and inject the same lstat kind at
                # the copy boundary; ordinary CI takes the live-socket branch.
                target.write_text("socket stat fallback\n", encoding="utf-8")
                materialized.injections.append(
                    {"op": "stat-injection", "path": directive["path"], "kind": "socket"}
                )
            finally:
                channel.close()
        elif operation == "write-encoded":
            target = _safe_candidate_path(candidate, directive["path"])
            target.write_bytes(_encoded_document(directive))
        elif operation == "required-series":
            count = directive["count"]
            tests = _tests_acceptance(document)
            assert len(tests) == 1
            tests[0]["required_tests"] = [
                f"test_gate.py::test_{index:05d}" for index in range(count)
            ]
            rows = "".join(
                f'<testcase classname="test_gate" name="test_{index:05d}"/>'
                for index in range(count)
            )
            (candidate / "result-source.bin").write_text(
                f'<testsuite tests="{count}">{rows}</testsuite>', encoding="utf-8"
            )
        elif operation == "long-selector":
            selector = "x" * directive["length"]
            acceptance = _tests_acceptance(document)[0]
            acceptance["required_tests"] = [f"test_gate.py::{selector}"]
            (candidate / "result-source.bin").write_text(
                f'<testsuite tests="1"><testcase classname="test_gate" '
                f'name="{selector}"/></testsuite>',
                encoding="utf-8",
            )
        elif operation == "protected-series":
            count = directive["count"]
            acceptance = _tests_acceptance(document)[0]
            rows = [acceptance["protected"][0]]
            empty_digest = _digest(b"")
            series_root = candidate / "p"
            series_root.mkdir()
            for index in range(1, count):
                relative = f"p/{_base36(index)}"
                (candidate / relative).write_bytes(b"")
                # Compact rows are required for D5's branch to fit inside the
                # pre-existing 1 MiB outer contract envelope.
                rows.append({"path": relative, "sha256": empty_digest})
            acceptance["protected"] = rows
        elif operation == "experiment-pointer":
            declared = root / directive["path"]
            declared.write_text("experiment artifact\n", encoding="utf-8")
            (candidate / "experiment-target.txt").write_text(str(declared), encoding="utf-8")
        elif operation == "set-results-path":
            value = directive["value"]
            paths = {
                "absolute": str(Path(os.sep) / "results.xml"),
                "relative": RESULT_PATH,
                "..": "results/../results.xml",
                ".": "results/./results.xml",
                "safe": "results/safe/results.xml",
                "": "",
            }
            chosen = paths[value]
            for acceptance in _tests_acceptance(document):
                acceptance["results_path"] = chosen
            if "--junitxml" in argv:
                argv[argv.index("--junitxml") + 1] = chosen
        elif operation == "result-bytes":
            (candidate / "result-source.bin").write_bytes(_result_bytes(directive["size"]))
        elif operation == "xml-depth":
            depth = directive["depth"]
            source = "<a>" * (depth - 1)
            source += '<testcase classname="test_gate" name="test_pass"/>'
            source += "</a>" * (depth - 1)
            (candidate / "result-source.bin").write_text(source, encoding="utf-8")
        elif operation == "xml-elements":
            count = directive["count"]
            source = '<root><testcase classname="test_gate" name="test_pass"/>'
            source += "<x/>" * (count - 2)
            source += "</root>"
            (candidate / "result-source.bin").write_text(source, encoding="utf-8")
        elif operation == "xml-text":
            units = directive["units"]
            source = "<root>" + ("x" * units)
            source += '<testcase classname="test_gate" name="test_pass"/></root>'
            (candidate / "result-source.bin").write_text(source, encoding="utf-8")
        elif operation == "hostile-result":
            (candidate / "result-source.bin").write_bytes(bytes.fromhex(directive["hex"]))
        elif operation == "fill-copy-bytes":
            remaining = directive["total"] - _regular_byte_total(candidate)
            assert remaining >= 0
            with (candidate / "copy-cap.bin").open("wb") as stream:
                stream.truncate(remaining)
        elif operation == "fill-copy-entries":
            filler = candidate / "entries"
            filler.mkdir()
            remaining = directive["total"] - _entry_total(candidate)
            assert remaining >= 0
            for index in range(remaining):
                (filler / _base36(index)).write_bytes(b"")
            assert _entry_total(candidate) == directive["total"]
        elif operation == "deep-dirs":
            current = candidate
            for _ in range(directive["depth"]):
                current /= "d"
            current.mkdir(parents=True)
        elif operation in {"stat-injection", "io-injection"}:
            materialized.injections.append(directive)
        elif operation == "hostile-contract":
            document = directive["document"]
        elif operation == "finalize-contract":
            _finalize_contract(
                document,
                root,
                candidate,
                argv,
                protected_mode=directive["protected"],
                echo_mode=directive["echo"],
            )
        else:  # pragma: no cover - test_recipe_vocabulary closes this branch
            raise AssertionError(f"unknown materialization operation {operation!r}")

    contract_bytes = (
        json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    assert len(contract_bytes) <= MAX_CONTRACT_BYTES, (
        f"{name}: materialized contract is {len(contract_bytes)} bytes"
    )
    (root / "session.contract.json").write_bytes(contract_bytes)
    return materialized


class _OSProxy:
    def __init__(self, wrapped: Any, replacements: dict[str, Any]):
        self._wrapped = wrapped
        self._replacements = replacements

    def __getattr__(self, name: str) -> Any:
        if name in self._replacements:
            return self._replacements[name]
        return getattr(self._wrapped, name)


@contextlib.contextmanager
def _injected_faults(
    fixture: _Materialized,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[None]:
    """Install only the two harness-level observations named by section 8.

    The imports are optional while Phase 3 is red: the shipped tree has neither
    new module, and absence must remain an ordinary observed mismatch.
    """

    for directive in fixture.injections:
        if directive["op"] == "stat-injection":
            try:
                from gnd.exp import tests_runner
            except ImportError:
                continue
            real_lstat = tests_runner.os.lstat

            def injected_lstat(
                path: Any,
                *args: Any,
                _real_lstat: Any = real_lstat,
                _directive: dict[str, Any] = directive,
                **kwargs: Any,
            ) -> os.stat_result:
                # B023: bind the loop variables at definition time -- a later
                # iteration must not retarget an already-installed injection.
                observed = _real_lstat(path, *args, **kwargs)
                if (
                    isinstance(path, (str, os.PathLike))
                    and Path(path).name == Path(_directive["path"]).name
                ):
                    values = list(observed)
                    kind = stat.S_IFSOCK if _directive["kind"] == "socket" else stat.S_IFCHR
                    values[stat.ST_MODE] = kind | 0o600
                    return os.stat_result(values)
                return observed

            monkeypatch.setattr(
                tests_runner,
                "os",
                _OSProxy(tests_runner.os, {"lstat": injected_lstat}),
            )
        elif directive["op"] == "io-injection":
            try:
                from gnd.exp import junit
            except ImportError:
                continue

            def injected_read(*_args: Any, **_kwargs: Any) -> bytes:
                raise OSError(errno.EIO, "tests-mode corpus descriptor read")

            if hasattr(junit, "_read_result_bytes"):
                monkeypatch.setattr(junit, "_read_result_bytes", injected_read)
            else:
                monkeypatch.setattr(junit, "os", _OSProxy(junit.os, {"read": injected_read}))
    yield


def _run_main(argv: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(argv)
    except SystemExit as error:
        code = int(error.code or 0)
    return int(code), stdout.getvalue(), stderr.getvalue()


def _json_documents(root: Path) -> list[Any]:
    documents: list[Any] = []
    for path in root.rglob("*.json"):
        try:
            if path.stat().st_size > 2 * 1024 * 1024:
                continue
            documents.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
    return documents


def _strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from _strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _strings(child)


def _record_dispositions(documents: list[Any]) -> set[str]:
    found: set[str] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            disposition = value.get("disposition")
            if isinstance(disposition, str):
                found.add(disposition)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    for document in documents:
        visit(document)
    return found


def _assert_results_read_back(root: Path) -> None:
    """Every terminal document this corpus PRODUCES must parse strictly.

    ``TestsSessionResult`` is the reader `gnd exp close` uses to judge a work
    experiment's latest run, and it enforces more than field shape: an
    ``accepted`` document must be one the writer could have produced (a launch
    digest, no refusal reason, feedback rows, and every required test in its
    row's passing set). A reader that strict is only safe if it agrees with the
    writer on real output, and the corpus is where real output exists — 44
    executed cases across accepting, refusing and verifier-failure paths,
    single- and multi-case contracts, required and diagnostic rows.

    Checked HERE rather than in a test of its own so the agreement is measured
    over every case the corpus already runs, at no additional runtime, and so a
    writer change that the reader does not follow reds immediately.
    """
    from gnd.exp.tests_runner import TestsSessionResult

    for path in sorted(root.rglob("runs/*/result.json")):
        raw = path.read_bytes()
        if json.loads(raw).get("acceptance_modes") != ["tests"]:
            continue  # the data-driven store's own result, read by SessionResult
        TestsSessionResult.model_validate_json(raw)


def _run_fixture(
    fixture: _Materialized,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[int, set[str], set[str], str]:
    if fixture.lane == "reader":
        contract = read_session_contract(
            fixture.root / "session.contract.json",
            experiment_root=fixture.root,
            experiment_id=EXPERIMENT_ID,
        )
        wire = json.loads((fixture.root / "session.contract.json").read_text(encoding="utf-8"))
        assert contract.model_dump(mode="json") == wire
        assert contract.schema_version == wire["schema_version"]
        assert [case.case_id for case in contract.cases] == ["exact"]
        return 0, set(), {"parsed"}, ""

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    adapter = bin_dir / "codex"
    shutil.copyfile(BASE / "adapter.py", adapter)
    adapter.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ.get("PATH", ""))
    monkeypatch.setenv("GND_CORPUS_CANARY", "must not cross the child allowlist")

    if fixture.lane.startswith("init"):
        out = tmp_path / "created"
        argv = [
            "exp",
            "init",
            EXPERIMENT_ID,
            "--out",
            str(out),
            "--kind",
            "work",
            f"--session-contract={fixture.root / 'session.contract.json'}",
        ]
        if fixture.lane == "init-control":
            argv.append('--covers={"operation":"gate"}')
    elif fixture.lane.startswith("author"):
        if fixture.lane == "author-control":
            (fixture.root / "SPEC.md").write_text(_spec("data-driven"), encoding="utf-8")
        argv = [
            "exp",
            "author-expectation",
            str(fixture.root),
            "--case",
            "gate" if fixture.lane == "author" else "exact",
            "--output-id",
            "target",
            "--candidate-path",
            "target.txt",
            "--from",
            str(fixture.root / "authoring/answer.json"),
        ]
    else:
        argv = ["exp", "run", str(fixture.root), "--adapter", "codex"]
        argv.extend(f"--test-argv={word}" for word in fixture.argv)

    with _injected_faults(fixture, monkeypatch):
        code, stdout, stderr = _run_main(argv)
    documents = _json_documents(fixture.root)
    if fixture.lane.startswith("init") and code == 0:
        created_spec = (tmp_path / "created" / EXPERIMENT_ID / "SPEC.md").read_text(
            encoding="utf-8"
        )
        if fixture.name == "test-only-work-without-covers":
            assert re.search(
                r"^covers_exemption:\s*['\"]?tests-only['\"]?\s*$",
                created_spec,
                flags=re.MULTILINE,
            )
        if fixture.name == "test-only-work-with-covers":
            assert "covers_exemption" not in created_spec
    _assert_results_read_back(fixture.root)
    haystack = "\n".join([stdout, stderr, *[text for doc in documents for text in _strings(doc)]])
    reasons = {reason for reason in REASON_REGISTRY if reason in haystack}
    dispositions = _record_dispositions(documents)
    if fixture.lane.startswith("init") and code == 0:
        dispositions.add("initialized")
    if fixture.lane.startswith("author") and code == 0:
        dispositions.add("accepted")
    return code, reasons, dispositions, stdout + stderr


def _case_parameters() -> list[Any]:
    parameters: list[Any] = []
    for entry in EXPECTED:
        # A quarter-gigabyte copy belongs outside the repository's default lane.
        marks = pytest.mark.slow if entry["case"] == "copy-bytes-over-cap" else ()
        parameters.append(pytest.param(entry, id=entry["case"], marks=marks))
    return parameters


@pytest.mark.parametrize("expected", _case_parameters())
def test_case_observation_matches_the_answer_key(
    expected: dict[str, Any],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _materialize(expected["case"], tmp_path)
    code, reasons, dispositions, transcript = _run_fixture(fixture, tmp_path, monkeypatch)
    wanted_reason = {expected["reason"]} if expected["reason"] is not None else set()
    wanted_disposition = expected["disposition"]
    observed = (
        code,
        reasons,
        wanted_disposition in dispositions if wanted_disposition is not None else not dispositions,
    )
    wanted = (expected["exit"], wanted_reason, True)
    assert observed == wanted, (
        f"{expected['case']}: observed exit/reasons/disposition-presence {observed}, "
        f"wanted {wanted}; dispositions={sorted(dispositions)}\n{transcript[:4000]}"
    )


def _control_parameters() -> list[Any]:
    names = sorted({entry["sibling"]["name"] for entry in EXPECTED if entry["sibling"] is not None})
    return [
        pytest.param(
            name,
            id=name,
            # The at-cap sibling performs the same quarter-gigabyte copy.
            marks=pytest.mark.slow if name == "copy-bytes-at-cap" else (),
        )
        for name in names
    ]


@pytest.mark.parametrize("name", _control_parameters())
def test_named_sibling_or_control_accepts(
    name: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _materialize(name, tmp_path)
    code, reasons, dispositions, transcript = _run_fixture(fixture, tmp_path, monkeypatch)
    wanted = (
        "initialized"
        if fixture.lane.startswith("init")
        else ("parsed" if fixture.lane == "reader" else "accepted")
    )
    assert code == 0 and not reasons and wanted in dispositions, (
        f"{name}: control did not accept; exit={code}, reasons={sorted(reasons)}, "
        f"dispositions={sorted(dispositions)}\n{transcript[:4000]}"
    )


def _json_scalar_deltas(left: Any, right: Any) -> int:
    if left == right:
        return 0
    if isinstance(left, dict) and isinstance(right, dict) and left.keys() == right.keys():
        return sum(_json_scalar_deltas(left[key], right[key]) for key in left)
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return 1
        return sum(_json_scalar_deltas(a, b) for a, b in zip(left, right, strict=True))
    return 1


@pytest.mark.parametrize(
    "entry",
    [entry for entry in EXPECTED if (entry["sibling"] or {}).get("kind") == "minimal"],
    ids=lambda entry: entry["case"],
)
def test_minimal_siblings_have_one_contiguous_serialized_delta(entry: dict[str, Any]) -> None:
    left_dir = CASES / entry["case"]
    right_dir = CASES / entry["sibling"]["name"]
    assert sorted(path.relative_to(left_dir) for path in left_dir.rglob("*") if path.is_file()) == [
        path.relative_to(right_dir) for path in sorted(right_dir.rglob("*")) if path.is_file()
    ]
    differing = []
    for relative in sorted(
        path.relative_to(left_dir) for path in left_dir.rglob("*") if path.is_file()
    ):
        left_bytes = (left_dir / relative).read_bytes()
        right_bytes = (right_dir / relative).read_bytes()
        if left_bytes != right_bytes:
            differing.append((relative, left_bytes, right_bytes))
    assert len(differing) == 1, (
        f"{entry['case']} -> {entry['sibling']['name']} differs in "
        f"{[str(row[0]) for row in differing]}, not one serialized file"
    )
    relative, left_bytes, right_bytes = differing[0]
    left_json = json.loads(left_bytes)
    right_json = json.loads(right_bytes)
    assert _json_scalar_deltas(left_json, right_json) == 1, (
        f"{entry['case']} -> {entry['sibling']['name']} does not isolate the named "
        f"serialized token {entry['sibling']['token']!r} in {relative}"
    )
    prefix = os.path.commonprefix([left_bytes, right_bytes])
    suffix = os.path.commonprefix([left_bytes[::-1], right_bytes[::-1]])
    assert len(prefix) + len(suffix) < max(len(left_bytes), len(right_bytes))


def test_answer_key_reasons_are_registered() -> None:
    used = {entry["reason"] for entry in EXPECTED if entry["reason"] is not None}
    assert used <= REASON_REGISTRY


def test_corpus_rows_and_named_controls_are_complete() -> None:
    rows = {entry["case"] for entry in EXPECTED}
    siblings = {entry["sibling"]["name"] for entry in EXPECTED if entry["sibling"] is not None}
    directories = {path.name for path in CASES.iterdir() if path.is_dir()}
    assert len(EXPECTED) == 71
    assert len(rows) == len(EXPECTED)
    assert directories == rows | siblings
    for name in directories:
        assert {path.name for path in (CASES / name).iterdir()} == {
            "argv.json",
            "contract.json",
            "materialize.json",
        }


def test_recipe_vocabulary_is_closed() -> None:
    allowed = {
        "write-file",
        "delete",
        "symlink",
        "fifo",
        "socket",
        "write-encoded",
        "required-series",
        "long-selector",
        "protected-series",
        "experiment-pointer",
        "set-results-path",
        "result-bytes",
        "xml-depth",
        "xml-elements",
        "xml-text",
        "hostile-result",
        "fill-copy-bytes",
        "fill-copy-entries",
        "deep-dirs",
        "stat-injection",
        "io-injection",
        "hostile-contract",
        "finalize-contract",
    }
    observed = set()
    for recipe in CASES.glob("*/materialize.json"):
        document = json.loads(recipe.read_text(encoding="utf-8"))
        observed.update(directive["op"] for directive in document["directives"])
    assert observed == allowed


def _bundle_paths(root: Path) -> list[Path]:
    """The corpus's own committed bytes, never a build artifact.

    ``base/test_gate.py`` is a candidate project's test file; anything that
    imports it drops ``__pycache__/*.pyc`` beside it, and a guard about corpus
    CONTENT must not be failable by a ``.pyc``. Collection is already refused
    in ``tests/fixtures/conftest.py``; this is the second lock.
    """
    if not root.is_dir():
        return [root]
    return [
        path
        for path in root.rglob("*")
        if "__pycache__" not in path.parts and path.suffix != ".pyc"
    ]


def test_blind_bundle_has_only_regular_small_utf8_text() -> None:
    for path in [CORPUS / "README.md", BASE, CASES]:
        paths = _bundle_paths(path)
        for item in paths:
            info = item.lstat()
            assert not stat.S_ISLNK(info.st_mode), item
            if item.is_file():
                assert stat.S_ISREG(info.st_mode), item
                assert info.st_size <= 100 * 1024, item
                item.read_text(encoding="utf-8")


def test_blind_bundle_contains_no_adjudication() -> None:
    files = [CORPUS / "README.md"]
    files.extend(path for root in (BASE, CASES) for path in _bundle_paths(root) if path.is_file())
    text = "\n".join(path.read_text(encoding="utf-8") for path in files)
    assert all(reason not in text for reason in REASON_REGISTRY)
    assert "disposition" not in text
    assert "will be refused" not in text.lower()
    assert re.search(r"\bexit\s+\d+\b", text, flags=re.IGNORECASE) is None


def test_declared_argv_is_machine_neutral_and_matches_results_path() -> None:
    for case_dir in CASES.iterdir():
        argv = json.loads((case_dir / "argv.json").read_text(encoding="utf-8"))
        for word in argv:
            assert not Path(word).is_absolute(), (case_dir.name, word)
            assert ("/" + "Users") not in word and ("$" + "HOME") not in word
        document = json.loads((case_dir / "contract.json").read_text(encoding="utf-8"))
        if "--junitxml" not in argv or not isinstance(document, dict):
            continue
        acceptances = _tests_acceptance(document)
        if acceptances:
            # set-results-path recipes transform both fields together at runtime.
            assert argv[argv.index("--junitxml") + 1] == acceptances[0]["results_path"]


@pytest.mark.parametrize(
    "case_name,child_node",
    [
        ("happy", "test_gate.py::test_pass"),
        ("parametrized-id", "test_gate.py::test_pair[left-right]"),
        ("env-canary", "test_gate.py::test_env_canary"),
        ("symlink-preserved", "test_gate.py::test_symlink_preserved"),
    ],
    ids=["test_pass", "test_pair", "test_env_canary", "test_symlink_preserved"],
)
def test_public_nested_gate_execution_context(
    case_name: str,
    child_node: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Record exact child execution rather than infer it from projected feedback."""
    fixture = _materialize(case_name, tmp_path)
    original_gate = (BASE / "test_gate.py").read_bytes()
    assert (fixture.root / "candidate" / "test_gate.py").read_bytes() == original_gate
    if case_name == "symlink-preserved":
        link = fixture.root / "candidate" / "observed-link"
        assert link.is_symlink() and os.readlink(link) == "target.txt"
    code, reasons, dispositions, transcript = _run_fixture(fixture, tmp_path, monkeypatch)
    assert code == 0 and not reasons and "accepted" in dispositions, transcript
    assert os.environ["GND_CORPUS_CANARY"] == "must not cross the child allowlist"
    records = sorted((fixture.root / "runs").glob("*/launches/*.json"))
    assert len(records) == 1
    launch = json.loads(records[0].read_bytes())
    assert launch["argv"] == ["python", "-m", "pytest", child_node, "--junitxml", RESULT_PATH]
    child = launch["child"]
    assert child["spawned"] and child["status"] == "succeeded"
    assert child["return_code"] == 0 and child["signal"] is None
    assert not child["timed_out"] and child["process_group_cleaned"]
    assert "GND_CORPUS_CANARY" not in {entry["name"] for entry in child["environment"]}
    assert (fixture.root / "candidate" / "test_gate.py").read_bytes() == original_gate


# Existing public skeleton bytes preserve the complete original vacuity fixture.
FIXTURES = Path(__file__).parent / "fixtures"


def test_a_deontic_vacuous_constraint_withholds_acceptance_and_exits_two() -> None:
    """A population making a DEONTIC constraint vacuous must still be projected as
    withholding acceptance, and the run must exit 2 — ``has_vacuous`` is not
    modality-filtered, unlike its two siblings (checker.py:118-120). The harness
    must not assume the symmetry the other two predicates have.

    ``skeleton/population.vacuous.yaml`` empties the fact types, so the model's
    top-level DEONTIC value constraint (``constraints[0]``) reports ``vacuous``.
    """
    model = load_model(FIXTURES / "skeleton" / "model.orm.yaml")
    population = load_population(FIXTURES / "skeleton" / "population.vacuous.yaml", model=model)
    report = check(model, population)

    deontic_vacuous = [
        v for v in report.verdicts if v.verdict == "vacuous" and v.modality == "deontic"
    ]
    assert deontic_vacuous, "the fixture must exercise a deontic vacuous verdict"
    # The projection withholds acceptance because of the deontic vacuous verdict.
    assert withholds_acceptance("vacuous", "deontic") is True
    assert any(withholds_acceptance(v.verdict, v.modality) for v in report.verdicts)
    # And the run exits 2 (inadequate), NOT 0.
    assert band(report) == 2
