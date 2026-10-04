"""Current codegen/checker contracts and retained synthetic BookRec application controls."""
from __future__ import annotations

import base64
import copy
import gzip
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

import pytest
from jsonschema import Draft202012Validator
from public_example_helpers import guarded_binding_counts, ref_to_id
from ruamel.yaml import YAML

from gnd.conformance.report import load_conformance_schema
from gnd.report import legacy_report_projection, load_report_schema

_sha256 = lambda raw: hashlib.sha256(raw).hexdigest()
def _workspace():
    fixture = Path(__file__).parent / "fixtures/public-book-runtime/workspace.json.gz"
    assert fixture.is_file() and not fixture.is_symlink()
    with fixture.open("rb") as stream:
        compressed = stream.read(64 * 1024 + 1)
    assert len(compressed) <= 64 * 1024
    assert _sha256(compressed) == '3a283c40932686e11aef8966a31f567c11f249d6af34a807cc6f90ae668ad172'
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
        expanded = stream.read(256 * 1024 + 1)
    assert len(expanded) <= 256 * 1024
    payload = json.loads(expanded)
    assert payload["schema_version"] == 1 and len(payload["members"]) == 46
    holder = tempfile.TemporaryDirectory(prefix="gnd-public-book-runtime-")
    root = Path(holder.name)
    members = {}
    for value, member in payload["members"].items():
        relative = PurePosixPath(value)
        assert relative.parts and not relative.is_absolute() and ".." not in relative.parts
        assert relative.as_posix() == value
        data = base64.b64decode(member["data"], validate=True)
        assert len(data) <= 64 * 1024 and _sha256(data) == member["sha256"]
        destination = root.joinpath(*relative.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        assert member["mode"] in {0o644, 0o755}
        destination.chmod(member["mode"])
        members[value] = data
    return holder, root, members
_HOLDER, REPO_ROOT, _MEMBERS = _workspace()
BOOKREC = REPO_ROOT / "examples/bookrec"
PROJECT = BOOKREC / "project"
MODEL_PATH = BOOKREC / "model.orm.yaml"
P001_PROJECT_RELPATH = "examples/bookrec/project"
EXP007 = BOOKREC / "EXP-007-bookrec-layout-gate"
SMOKE_MODULE = "test_architecture_smoke_bookrec.py"
RATED_GUARD = "recommendation_excludes_rated_books"
MINOR_ADULT_GUARD = "recommendation_excludes_adult_books_for_minors"
GENRE_GUARD = "recommendation_matches_preferred_genre"
ELIGIBILITY_COMPLETENESS_GUARD = "recommendation_covers_every_eligible_book"
BOOKREC_GUARDS = {RATED_GUARD, MINOR_ADULT_GUARD, GENRE_GUARD}
BOOKREC_DERIVED_FACT_TYPES = {"book_is_blocked_for", "book_is_eligible"}
REPORT_VALIDATOR = Draft202012Validator(load_report_schema())
CONFORMANCE_VALIDATOR = Draft202012Validator(load_conformance_schema())
JsonObject = dict[str, Any]
def _git_blob(commit: str, relative: str) -> bytes:
    assert commit == "HEAD"
    assert relative in _MEMBERS
    return _MEMBERS[relative]
def _materialize_git_tree(commit: str, prefix: str, destination: Path) -> None:
    assert commit == "HEAD" and prefix == P001_PROJECT_RELPATH
    pure_prefix = PurePosixPath(prefix)
    paths = sorted(p for p in _MEMBERS if p.startswith(prefix + "/"))
    assert len(paths) == 15
    for relative in paths:
        suffix = PurePosixPath(relative).relative_to(pure_prefix)
        target = destination.joinpath(*suffix.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(_git_blob(commit, relative))
def _python_census():
    entries = []
    roots = (P001_PROJECT_RELPATH + "/model/", P001_PROJECT_RELPATH + "/bookrec/")
    for relative in sorted(p for p in _MEMBERS if p.endswith(".py") and p.startswith(roots)):
        path = REPO_ROOT / relative
        assert path.is_file() and not path.is_symlink(), relative
        data = path.read_bytes()
        entries.append({"path": relative, "sha256": _sha256(data), "lines": len(data.decode("utf-8").splitlines())})
    return entries

def _read_json(path: Path) -> JsonObject:
    """Read one committed JSON object."""
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def _json_object_from_bytes(value: bytes, *, label: str) -> JsonObject:
    """Parse one pinned JSON object without consulting a moving workspace path."""
    parsed = json.loads(value)
    assert isinstance(parsed, dict), label
    return parsed


def _read_model(path: Path = MODEL_PATH) -> JsonObject:
    """Read a model as the YAML mapping used by the independent helper."""
    value = YAML(typ="safe").load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def _canonical_json_bytes(value: object) -> bytes:
    """Render the canonical population encoding required from BookRec."""
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def _run_gnd_json(*args: str) -> tuple[int, JsonObject]:
    """Run GND through the required subprocess interface and parse stdout."""
    completed = subprocess.run(
        [sys.executable, "-m", "gnd", *args, "--format", "json"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert completed.stdout, completed.stderr
    payload = json.loads(completed.stdout)
    assert isinstance(payload, dict)
    return completed.returncode, payload


def _run_check(model_path: Path, population_path: Path) -> tuple[int, JsonObject]:
    """Run ``gnd check`` and require a schema-valid report."""
    code, report = _run_gnd_json("check", str(model_path), str(population_path))
    REPORT_VALIDATOR.validate(report)
    return code, report


def _guard_verdicts(
    model: Mapping[str, Any],
    report: Mapping[str, Any],
    expected_ids: set[str] = BOOKREC_GUARDS,
) -> JsonObject:
    """Resolve positional verdict references to stable guarded IDs."""
    ids = ref_to_id(model)
    resolved = {
        ids[str(verdict["constraint_ref"])]: verdict
        for verdict in report["verdicts"]
        if str(verdict["constraint_ref"]) in ids
        and ids[str(verdict["constraint_ref"])] in expected_ids
    }
    assert set(resolved) == expected_ids
    return resolved


def _census_is_under_limit(entries: Sequence[Mapping[str, Any]]) -> bool:
    """Apply the strict T4.7 total-line predicate."""
    return sum(int(entry["lines"]) for entry in entries) < 1000


def _run_bookrec(
    *,
    model: Path,
    input_path: Path,
    output_path: Path,
    user: str = "u-minor",
    limit: str = "3",
    isolated: bool = False,
    environment: Mapping[str, str] | None = None,
    fake_gnd_dir: Path | None = None,
    timeout: float = 10,
) -> subprocess.CompletedProcess[str]:
    """Invoke the SHIPPED CLI, from the committed layout, as a subprocess."""
    command = [sys.executable]
    if isolated:
        command.append("-S")
    command.extend(
        [
            "-m",
            "bookrec.cli",
            "recommend",
            "--model",
            str(model),
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--user",
            user,
            "--limit",
            limit,
        ]
    )
    process_environment = os.environ.copy()
    if environment:
        process_environment.update(environment)
    if fake_gnd_dir is not None:
        # Measured: a directory on PYTHONPATH holding a `gnd` package wins over
        # this repository's editable install, for both importlib.util.find_spec
        # and `python -m gnd`.  It is passed PER CALL and never globally,
        # because the same mechanism defeats the `-S` isolation the
        # "gnd executable absent" row depends on.
        process_environment["PYTHONPATH"] = str(fake_gnd_dir)
    else:
        process_environment.pop("PYTHONPATH", None)
    return subprocess.run(
        command,
        cwd=PROJECT,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=process_environment,
    )


def _install_fake_gnd(root: Path) -> Path:
    """Write a checker double into a scratch dir and return that dir.

    It goes on PYTHONPATH rather than into the project, so the committed tree is
    never written to by a test.
    """
    package = root / "gnd"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "__main__.py").write_text(
        """from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys
Path(os.environ["FAKE_GND_CAPTURE"]).write_text(
    json.dumps(sys.argv[1:]), encoding="utf-8"
)
if os.environ.get("FAKE_GND_DELEGATE_REAL") == "1":
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    completed = subprocess.run(
        [sys.executable, "-m", "gnd", *sys.argv[1:]],
        check=False,
        capture_output=True,
        env=environment,
    )
    sys.stdout.buffer.write(completed.stdout)
    sys.stderr.buffer.write(completed.stderr)
    raise SystemExit(completed.returncode)
sys.stdout.write(os.environ["FAKE_GND_STDOUT"])
raise SystemExit(int(os.environ["FAKE_GND_EXIT"]))
""",
        encoding="utf-8",
    )
    return root


def _all_nonvacuous_pass(
    model: Mapping[str, Any],
    population: Mapping[str, Any],
    report: Mapping[str, Any],
    constraint_ids: set[str],
) -> bool:
    """Require both structured pass verdicts and independently nonempty joins."""
    verdicts = _guard_verdicts(model, report, constraint_ids)
    counts = guarded_binding_counts(model, population)
    return all(
        verdicts[constraint_id]["verdict"] == "pass" and counts[constraint_id] > 0
        for constraint_id in constraint_ids
    )


class _Intercepted(Exception):
    """Raised to stop a subprocess at the boundary being observed."""


def test_exp007_gate_is_green_when_run_now(tmp_path: Path) -> None:
    """P4-25, the LIVE half. Retained evidence is not a runnable gate.

    The adversarial reviewer deleted the sealed smoke module from the candidate
    and the acceptance row still passed, because it read the old result.json and
    reran only `exp close`. A row that reads yesterday's verdict cannot fail on
    today's bytes.

    This copies the experiment WITHOUT runs/, executes the exact bound argv, and
    asserts a fresh exit 0 with the required set actually reported passing. No
    agent is launched -- tests mode runs the committed suite.
    """
    import shutil as _shutil

    scratch = tmp_path / "EXP-007-bookrec-layout-gate"
    _shutil.copytree(EXP007, scratch, ignore=_shutil.ignore_patterns("runs"))
    assert not (scratch / "runs").exists()

    argv = ["python3", "-m", "pytest", "-p", "no:randomly",
            f"project/{SMOKE_MODULE}", "--junit-xml=results/junit.xml", "-q"]
    # The argv is the one the contract binds by echo digest, not a re-invention.
    acceptance = _read_json(scratch / "session.contract.json")["cases"][0]["acceptance"]
    assert acceptance["test_argv_sha256"] == hashlib.sha256(
        json.dumps(argv, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    completed = subprocess.run(
        [sys.executable, "-m", "gnd", "exp", "run", str(scratch), "--adapter", "claude",
         *[f"--test-argv={word}" for word in argv]],
        cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=300,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr

    result = _read_json(scratch / "runs" / "run-0001" / "result.json")
    assert result["disposition"] == "accepted"
    (feedback,) = result["feedback"]
    assert set(feedback["passing"]) == set(acceptance["required_tests"])
    assert feedback["reason"] is None


def test_gate_node_ids_are_measured_in_the_shape_the_gate_runs_in(tmp_path: Path) -> None:
    """P4-34 (corrected). The node id is a property of the SURROUNDINGS.

    The panel-repair round measured this in a scratch tree with no pyproject
    under project/, got the `project/` prefix, and pinned it. Measured again in
    the real shape -- outside any repository, with the generated project's
    create-once pyproject.toml present -- rootdir lands on project/ and the ids
    collapse to the BARE BASENAME. Phase 3 said exactly this about the gate and
    the repair over-corrected it.

    So the candidate anchors its own rootdir, and this row measures both shapes
    rather than asserting either.
    """
    import shutil as _shutil

    for anchored in (False, True):
        scratch = tmp_path / ("anchored" if anchored else "bare")
        _shutil.copytree(EXP007 / "candidate", scratch)
        if not anchored:
            (scratch / "pytest.ini").unlink()

        collected = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:randomly",
             f"project/{SMOKE_MODULE}"],
            cwd=scratch, check=False, capture_output=True, text=True,
            env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"},
        )
        ids = [line for line in collected.stdout.splitlines() if "::test_smoke" in line]
        assert len(ids) == 3, collected.stdout

        if anchored:
            assert all(line.startswith(f"project/{SMOKE_MODULE}::") for line in ids), ids
        else:
            assert all(line.startswith(f"{SMOKE_MODULE}::") for line in ids), ids

    # And the contract cites the anchored form, which is the one it pins.
    acceptance = _read_json(EXP007 / "session.contract.json")["cases"][0]["acceptance"]
    assert all(rid.startswith(f"project/{SMOKE_MODULE}::") for rid in acceptance["required_tests"])
    assert (EXP007 / "candidate" / "pytest.ini").is_file()


@pytest.mark.parametrize(
    ("label", "when"),
    [("pre-existing", "lane-a"), ("in-run", "runner")],
    ids=["pre-existing-mutation-refuses-in-lane-a", "in-run-mutation-is-protected-mutated"],
)
def test_protected_seal_reds_at_the_boundary_that_owns_it(
    tmp_path: Path, label: str, when: str
) -> None:
    """P4-06a / P4-06c. One row per boundary, because there are three.

    The r1 spec asserted `tests:protected-mutated` at exit 15 for a PRE-EXISTING
    mutation. Measured: that reason is emitted at exactly one site, after the
    child ran. A mutation already present is refused in lane A at exit 3 with no
    run directory at all. One row could not have pinned both, and the one that
    was written pinned neither.
    """
    import shutil as _shutil

    scratch = tmp_path / "EXP-007-bookrec-layout-gate"
    _shutil.copytree(EXP007, scratch, ignore=_shutil.ignore_patterns("runs"))
    sealed = scratch / "candidate" / "project" / "architecture.contract.yaml"

    if when == "lane-a":
        sealed.write_bytes(sealed.read_bytes() + b"\n# mutated before the run\n")
    extra: list[str] = []
    if when == "runner":
        # The mutation must come from a file that is NOT itself sealed, or lane A
        # catches it at read time and the in-run boundary is never reached.
        saboteur = scratch / "candidate" / "test_saboteur.py"
        saboteur.write_text(
            "from pathlib import Path\n"
            "def test_rewrites_a_sealed_file():\n"
            "    p = Path(__file__).parent / 'project' / 'architecture.contract.yaml'\n"
            "    p.write_bytes(p.read_bytes() + b'# mutated during the run\\n')\n",
            encoding="utf-8",
        )
        extra = ["test_saboteur.py"]

    argv = ["python3", "-m", "pytest", "-p", "no:randomly",
            f"project/{SMOKE_MODULE}", *extra, "--junit-xml=results/junit.xml", "-q"]
    if extra:
        # The contract binds the argv by echo digest, so a scratch run with an
        # extra word has to re-bind it. That the echo is checked at all is its
        # own guard and it fired here before this line existed.
        contract_path = scratch / "session.contract.json"
        document = _read_json(contract_path)
        document["cases"][0]["acceptance"]["test_argv_sha256"] = hashlib.sha256(
            json.dumps(argv, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        contract_path.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n")
    completed = subprocess.run(
        [sys.executable, "-m", "gnd", "exp", "run", str(scratch), "--adapter", "claude",
         *[f"--test-argv={word}" for word in argv]],
        cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=300,
    )
    combined = completed.stdout + completed.stderr

    if when == "lane-a":
        assert completed.returncode == 3, combined
        assert "tests:protected-digest" in combined or "protected" in combined, combined
        assert not (scratch / "runs").exists(), "an agent must not start on a broken seal"
    else:
        assert completed.returncode == 15, combined
        result = _read_json(scratch / "runs" / "run-0001" / "result.json")
        assert result["disposition"] != "accepted"
        assert "protected-mutated" in json.dumps(result), result


def test_the_two_p002_dogfood_reds_fail_at_distinct_exact_boundaries() -> None:
    """Exclude a shared generic red standing in for derivation and completeness."""
    model_relative = Path("examples/bookrec/model.orm.yaml")
    witness = {"book": "b-safe-fantasy", "user": "u-minor"}
    fixture_root = REPO_ROOT / "tests" / "fixtures" / "v5-phase4-bookrec" / "populations"
    complete = _read_json(fixture_root / "complete.population.json")
    cases = {
        "derivation-incomplete": (
            Path("examples/bookrec/populations/derivation-incomplete.population.json"),
            Path("examples/bookrec/evidence/derivation-incomplete-check.json"),
        ),
        "completeness-missing": (
            Path("examples/bookrec/populations/completeness-missing.population.json"),
            Path("examples/bookrec/evidence/completeness-missing-check.json"),
        ),
    }
    replayed: dict[str, JsonObject] = {}
    populations: dict[str, JsonObject] = {}
    for label, (population_relative, report_relative) in cases.items():
        population = _read_json(REPO_ROOT / population_relative)
        approved = _read_json(fixture_root / f"{label}.population.json")
        approved_live = copy.deepcopy(approved)
        approved_live["population"]["model"] = "../model.orm.yaml"
        assert population == approved_live, label

        expected_fixture = copy.deepcopy(complete)
        expected_fixture["population"]["label"] = "violating"
        missing_fact_type = (
            "book_is_eligible"
            if label == "derivation-incomplete"
            else "recommendation"
        )
        expected_fixture["facts"][missing_fact_type].remove(witness)
        assert approved == expected_fixture, label

        committed = _read_json(REPO_ROOT / report_relative)
        REPORT_VALIDATOR.validate(committed)
        code, report = _run_check(model_relative, population_relative)
        assert code == committed["exit_code"] == 1, label
        # Project today's authenticated wire to the frozen Phase 2 evidence.
        bound = legacy_report_projection(report, 4)
        assert bound == committed, label
        replayed[label] = report
        populations[label] = population

    derivation_report = replayed["derivation-incomplete"]
    assert [
        (row["derivation_ref"], row["verdict"])
        for row in derivation_report["derivations"]
    ] == [
        ("derivation:book_is_blocked_for", "pass"),
        ("derivation:book_is_eligible", "fail"),
    ]
    derivation_failures = [
        row for row in derivation_report["derivations"] if row["verdict"] == "fail"
    ]
    assert derivation_failures == [
        {
            "derivation_ref": "derivation:book_is_eligible",
            "derivation": "derived",
            "modality": "alethic",
            "verdict": "fail",
            "message": "The derivation claim for 'book_is_eligible' differs from its extension.",
            "findings": [
                {
                    "kind": "derived-extension-incomplete",
                    "message": (
                        "The derived extension of 'book_is_eligible' is incomplete — "
                        'missing {"book":"b-safe-fantasy","user":"u-minor"}.'
                    ),
                    "witness": witness,
                }
            ],
            "reason_code": None,
        }
    ]
    derivation_guards = _guard_verdicts(
        _read_model(),
        derivation_report,
        BOOKREC_GUARDS | {ELIGIBILITY_COMPLETENESS_GUARD},
    )
    assert set(derivation_guards) == BOOKREC_GUARDS | {
        ELIGIBILITY_COMPLETENESS_GUARD
    }
    assert {row["verdict"] for row in derivation_guards.values()} == {"pass"}

    completeness_report = replayed["completeness-missing"]
    assert [
        (row["derivation_ref"], row["verdict"])
        for row in completeness_report["derivations"]
    ] == [
        ("derivation:book_is_blocked_for", "pass"),
        ("derivation:book_is_eligible", "pass"),
    ]
    completeness_guards = _guard_verdicts(
        _read_model(),
        completeness_report,
        BOOKREC_GUARDS | {ELIGIBILITY_COMPLETENESS_GUARD},
    )
    assert set(completeness_guards) == BOOKREC_GUARDS | {
        ELIGIBILITY_COMPLETENESS_GUARD
    }
    assert {
        guard_id: row["verdict"]
        for guard_id, row in completeness_guards.items()
    } == {
        RATED_GUARD: "pass",
        MINOR_ADULT_GUARD: "pass",
        GENRE_GUARD: "pass",
        ELIGIBILITY_COMPLETENESS_GUARD: "fail",
    }
    completeness_verdict = completeness_guards[ELIGIBILITY_COMPLETENESS_GUARD]
    assert completeness_verdict["verdict"] == "fail"
    assert completeness_verdict["offending_facts"] == [
        {"$b": witness["book"], "$u": witness["user"]}
    ]
    assert [
        verdict for verdict in completeness_report["verdicts"] if verdict["verdict"] == "fail"
    ] == [completeness_verdict]

    missing_derivation = populations["derivation-incomplete"]["facts"]
    missing_recommendation = populations["completeness-missing"]["facts"]
    assert witness not in missing_derivation["book_is_eligible"]
    assert witness in missing_derivation["recommendation"]
    assert witness in missing_recommendation["book_is_eligible"]
    assert witness not in missing_recommendation["recommendation"]


def test_current_codegen_is_idempotent_and_conformance_matches_its_payload(
    tmp_path: Path,
) -> None:
    """Exclude a merely historical green payload or a second codegen that moves bytes."""
    import ast

    manifest = _read_json(PROJECT / ".gnd-codegen.json")
    current_model_digest = _sha256(MODEL_PATH.read_bytes())
    assert manifest["model"] == {
        "path": "examples/bookrec/model.orm.yaml",
        "sha256": current_model_digest,
    }
    for entry in manifest["files"]:
        if entry["ownership"] == "derived":
            assert entry["sha256"] == _sha256((PROJECT / entry["relpath"]).read_bytes())

    # SKILL.md names the generated project from the output directory basename,
    # so reproduce the committed basename while keeping every byte in scratch.
    scratch = tmp_path / PROJECT.name

    def snapshot(root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file() and "__pycache__" not in path.parts
        }

    snapshots: list[dict[str, bytes]] = []
    outputs: list[str] = []
    for _ in range(2):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "gnd",
                "codegen",
                "examples/bookrec/model.orm.yaml",
                "--out",
                str(scratch),
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert completed.returncode == 0, completed.stderr
        snapshots.append(snapshot(scratch))
        outputs.append(completed.stdout)
    assert snapshots[0]
    assert snapshots[1] == snapshots[0]
    assert "0 written" in outputs[1]
    fresh_manifest = _json_object_from_bytes(
        snapshots[0][".gnd-codegen.json"], label="fresh .gnd-codegen.json"
    )
    assert fresh_manifest["manifest_version"] == manifest["manifest_version"]
    assert fresh_manifest["gnd_version"] == manifest["gnd_version"]
    assert fresh_manifest["model"] == manifest["model"]
    assert [
        entry for entry in fresh_manifest["files"] if entry["ownership"] == "derived"
    ] == [entry for entry in manifest["files"] if entry["ownership"] == "derived"]
    for entry in manifest["files"]:
        if entry["ownership"] == "derived":
            assert snapshots[0][entry["relpath"]] == (
                PROJECT / entry["relpath"]
            ).read_bytes()

    # The fresh-target branch above cannot prove the existing-project promise:
    # it has no authored extension tree to preserve. Materialize the committed
    # project from Git, rerun codegen over that copy, and byte-compare the whole
    # tree -- including extension files that are intentionally absent from the
    # manifest because GND never placed them.
    committed_copy = tmp_path / "committed-copy" / PROJECT.name
    _materialize_git_tree("HEAD", P001_PROJECT_RELPATH, committed_copy)
    committed_before = snapshot(committed_copy)
    assert committed_before == {
        relative: _git_blob("HEAD", f"{P001_PROJECT_RELPATH}/{relative}")
        for relative in committed_before
    }

    planned_paths = {entry["relpath"] for entry in manifest["files"]}
    extension_leaves = sorted(
        {
            entry["relpath"]
            for entry in manifest["files"]
            if entry["ownership"] == "extension"
        }
        | (set(committed_before) - planned_paths - {".gnd-codegen.json"})
    )
    assert extension_leaves == [
        "architecture.contract.yaml",
        "bookrec/__init__.py",
        "bookrec/cli.py",
        "bookrec/recommender.py",
        "pyproject.toml",
        "references/gnd-model-notes.md",
        "test_architecture_smoke_bookrec.py",
    ]

    copied_run = subprocess.run(
        [
            sys.executable,
            "-m",
            "gnd",
            "codegen",
            "examples/bookrec/model.orm.yaml",
            "--out",
            str(committed_copy),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert copied_run.returncode == 0, copied_run.stderr
    assert "0 written, 3 skipped" in copied_run.stdout
    assert "preserved authored extension architecture.contract.yaml" in (
        copied_run.stdout
    )
    assert "preserved authored extension pyproject.toml" in copied_run.stdout
    # v5.1 Phase 1 migrated this tree: the stale `..._model.py` the OLD rule
    # emitted is gone, and `..._bookrec.py` -- which already bore the name the
    # discriminator now derives -- is the create-once survivor, left untouched.
    assert "test_architecture_smoke_model.py" not in copied_run.stdout
    assert not (committed_copy / "test_architecture_smoke_model.py").exists()
    assert snapshot(committed_copy) == committed_before
    assert {
        relative: (committed_copy / relative).read_bytes()
        for relative in extension_leaves
    } == {relative: committed_before[relative] for relative in extension_leaves}

    # Mutation control: an authored manifest-owned extension is create-once.
    # A one-byte-divergent copy must remain divergent, while every other leaf
    # stays byte-exact and codegen still reports that it wrote nothing.
    authored_copy = tmp_path / "authored-copy" / PROJECT.name
    _materialize_git_tree("HEAD", P001_PROJECT_RELPATH, authored_copy)
    authored_relative = "references/gnd-model-notes.md"
    authored_path = authored_copy / authored_relative
    authored_bytes = authored_path.read_bytes() + b"\n"
    authored_path.write_bytes(authored_bytes)
    expected_authored = dict(committed_before)
    expected_authored[authored_relative] = authored_bytes
    assert expected_authored != committed_before

    authored_run = subprocess.run(
        [
            sys.executable,
            "-m",
            "gnd",
            "codegen",
            "examples/bookrec/model.orm.yaml",
            "--out",
            str(authored_copy),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert authored_run.returncode == 0, authored_run.stderr
    assert "0 written, 4 skipped" in authored_run.stdout
    assert f"preserved authored extension {authored_relative}" in authored_run.stdout
    assert snapshot(authored_copy) == expected_authored

    asserted_fact_types = {
        "recommendation",
        "user_rated_book",
        "user_is_minor",
        "book_rated_adult",
        "book_has_genre",
        "user_prefers_genre",
    }
    for tools_path in (PROJECT / "model" / "tools.py", scratch / "model" / "tools.py"):
        syntax = ast.parse(tools_path.read_text(encoding="utf-8"))
        constructors = {
            node.name for node in syntax.body if isinstance(node, ast.FunctionDef)
        }
        assert constructors == asserted_fact_types
        assert constructors.isdisjoint(BOOKREC_DERIVED_FACT_TYPES)

    code, current = _run_gnd_json("conformance", str(MODEL_PATH), str(PROJECT))
    committed = _read_json(
        BOOKREC / "evidence" / "conformance-post-eligibility-extension.json"
    )
    CONFORMANCE_VALIDATOR.validate(committed)
    assert code == 0
    assert current == committed
    assert committed["model"]["actual_sha256"] == current_model_digest
    assert committed["model"]["recorded_sha256"] == current_model_digest
    assert committed["findings"] == []
    assert {row["id"]: row for row in committed["assertions"]} == {
        assertion: {"id": assertion, "ran": True, "findings": 0}
        for assertion in ("integrity", "currency", "structural", "architecture")
    }


def test_shipped_bookrec_python_is_under_one_thousand_lines() -> None:
    """Exclude a partial census, changed source bytes, or a non-strict size gate."""
    expected = [
        {
            "path": "examples/bookrec/project/bookrec/__init__.py",
            "sha256": "0eb6d042aa48b57d5670e1c2405fb14be56e56052145b9b7f560829d9814a0e9",
            "lines": 1,
        },
        {
            "path": "examples/bookrec/project/bookrec/cli.py",
            "sha256": "45a52059e92893f8c06d6bff3634b2a230caee751f4055d0f3702cde1d6d6a63",
            "lines": 240,
        },
        {
            "path": "examples/bookrec/project/bookrec/recommender.py",
            "sha256": "55d82ec7447cd42eab01e9131bc1d1eb2b1dde3d5c8b2aa5bef6be474bbbe1f7",
            "lines": 156,
        },
        {
            "path": "examples/bookrec/project/model/__init__.py",
            "sha256": "2b0b408789ff1bf1c779383e61af70c3fda0ba8170c60304cda252412d19fd06",
            "lines": 22,
        },
        {
            "path": "examples/bookrec/project/model/tools.py",
            "sha256": "4d92dfa889ec1d78458501243c17df84e195c413583350d076d9efc85014e0e0",
            "lines": 90,
        },
    ]
    census = _python_census()

    assert census == expected
    assert sum(entry["lines"] for entry in census) == 509
    assert _census_is_under_limit(census)

    planted = [*census, {"path": "negative-control.py", "sha256": "0" * 64, "lines": 1000}]
    assert not _census_is_under_limit(planted)


def test_cli_emits_canonical_complete_population_and_delegates_the_check(
    tmp_path: Path,
) -> None:
    """Exclude hand-authored output, altered checker JSON, or failed publication."""
    # P4-12. The CLI runs from the COMMITTED layout. No copy, no relocation --
    # so the artifact is resolved exactly where a user's checkout has it.
    fake_gnd = _install_fake_gnd(tmp_path / "checker-double")

    seed_path = BOOKREC / "populations" / "seed.population.json"
    seed = _read_json(seed_path)
    output_path = tmp_path / "published.population.json"
    capture_path = tmp_path / "checker-argv.json"
    completed = _run_bookrec(
        model=MODEL_PATH,
        input_path=seed_path,
        output_path=output_path,
        fake_gnd_dir=fake_gnd,
        environment={
            "FAKE_GND_CAPTURE": str(capture_path),
            "FAKE_GND_DELEGATE_REAL": "1",
        },
    )

    assert completed.returncode == 0
    checker_payload = json.loads(completed.stdout)
    REPORT_VALIDATOR.validate(checker_payload)
    output_bytes = output_path.read_bytes()
    output = json.loads(output_bytes)
    artifact = _read_json(PROJECT / "artifacts" / "model.artifacts.json")
    expected_header = dict(artifact["header_template"])
    expected_header["covers"] = sorted(
        {
            *expected_header["covers"],
            "book_is_blocked_for",
            "book_is_eligible",
        }
    )
    expected_header["label"] = "conforming"
    expected_recommendations = [
        {"user": "u-minor", "book": "b-earthsea"},
        {"user": "u-minor", "book": "b-gormenghast"},
        {"user": "u-bo", "book": "b-solaris"},
        {"user": "u-cy", "book": "b-earthsea"},
        {"user": "u-cy", "book": "b-redroom"},
        {"user": "u-dee", "book": "b-gormenghast"},
        {"user": "u-dee", "book": "b-redroom"},
        {"user": "u-eli", "book": "b-solaris"},
    ]

    assert output_bytes == _canonical_json_bytes(output)
    assert list(output) == ["facts", "instances", "population"]
    assert output["population"] == expected_header
    assert output["instances"] == {}
    assert list(output["facts"]) == sorted(expected_header["covers"])
    assert output["facts"]["recommendation"] == expected_recommendations
    for fact_type in (
        "user_rated_book",
        "user_is_minor",
        "book_rated_adult",
        "book_has_genre",
        "user_prefers_genre",
    ):
        assert output["facts"][fact_type] == seed["facts"][fact_type]
    assert output["facts"]["book_is_blocked_for"] == [
        {"book": "b-redroom", "user": "u-minor"}
    ]
    assert output["facts"]["book_is_eligible"] == [
        {"book": "b-earthsea", "user": "u-cy"},
        {"book": "b-earthsea", "user": "u-minor"},
        {"book": "b-gormenghast", "user": "u-dee"},
        {"book": "b-gormenghast", "user": "u-minor"},
        {"book": "b-redroom", "user": "u-cy"},
        {"book": "b-redroom", "user": "u-dee"},
        {"book": "b-solaris", "user": "u-bo"},
        {"book": "b-solaris", "user": "u-eli"},
    ]
    real_code, real_report = _run_check(MODEL_PATH, output_path)
    assert real_code == real_report["exit_code"] == 0
    normalized_checker = dict(checker_payload)
    normalized_checker["population"] = real_report["population"]
    assert normalized_checker == real_report
    assert [
        (row["derivation_ref"], row["verdict"])
        for row in real_report["derivations"]
    ] == [
        ("derivation:book_is_blocked_for", "pass"),
        ("derivation:book_is_eligible", "pass"),
    ]
    current_guards = _guard_verdicts(
        _read_model(),
        real_report,
        BOOKREC_GUARDS | {ELIGIBILITY_COMPLETENESS_GUARD},
    )
    assert set(current_guards) == BOOKREC_GUARDS | {
        ELIGIBILITY_COMPLETENESS_GUARD
    }
    assert {row["verdict"] for row in current_guards.values()} == {"pass"}
    assert _all_nonvacuous_pass(
        _read_model(),
        output,
        real_report,
        BOOKREC_GUARDS | {ELIGIBILITY_COMPLETENESS_GUARD},
    )

    checker_argv = json.loads(capture_path.read_text(encoding="utf-8"))
    assert checker_argv[0:2] == ["check", str(MODEL_PATH)]
    temporary_path = Path(checker_argv[2])
    assert temporary_path.parent == output_path.parent
    assert temporary_path.name.startswith(f".{output_path.name}.")
    assert temporary_path.suffix == ".tmp"
    assert checker_argv[3:] == ["--format", "json"]
    assert checker_payload["population"] == str(temporary_path)

    blocked_path = tmp_path / "must-not-publish.population.json"
    blocked_capture = tmp_path / "blocked-checker-argv.json"
    blocked_stdout = (BOOKREC / "evidence" / "completeness-missing-check.json").read_text(
        encoding="utf-8"
    )
    blocked = _run_bookrec(
        model=MODEL_PATH,
        fake_gnd_dir=fake_gnd,
        input_path=seed_path,
        output_path=blocked_path,
        environment={
            "FAKE_GND_CAPTURE": str(blocked_capture),
            "FAKE_GND_STDOUT": blocked_stdout,
            "FAKE_GND_EXIT": "1",
        },
    )
    assert blocked.returncode == 1
    assert blocked.stdout == blocked_stdout
    assert not blocked_path.exists()
    assert not Path(json.loads(blocked_capture.read_text(encoding="utf-8"))[2]).exists()


def test_bookrec_input_boundary_is_total_and_bounded(tmp_path: Path) -> None:
    """Exclude an undocumented exit, leaked traceback, unbounded input, or slow join."""
    seed_path = BOOKREC / "populations" / "seed.population.json"
    seed = _read_json(seed_path)

    malformed_path = tmp_path / "malformed.json"
    malformed_path.write_text("{not json", encoding="utf-8")
    oversized_path = tmp_path / "oversized.json"
    oversized_path.write_bytes(b" " * (1024 * 1024 + 1))
    missing_path = tmp_path / "missing-fact.json"
    missing = copy.deepcopy(seed)
    del missing["facts"]["book_has_genre"]
    missing_path.write_text(json.dumps(missing), encoding="utf-8")
    blocker = tmp_path / "not-a-directory"
    blocker.write_text("blocks child creation", encoding="utf-8")

    # This literal table is the boundary's documentation.  Adding a refusal
    # branch without adding a row here leaves the public exit contract incomplete.
    hostile_cases = [
        ("malformed JSON", malformed_path, tmp_path / "malformed.out", "u-minor", "3", MODEL_PATH, False, 2),
        ("input over 1 MiB", oversized_path, tmp_path / "oversized.out", "u-minor", "3", MODEL_PATH, False, 2),
        ("missing required fact map", missing_path, tmp_path / "missing.out", "u-minor", "3", MODEL_PATH, False, 2),
        ("unknown user", seed_path, tmp_path / "unknown.out", "u-unknown", "3", MODEL_PATH, False, 3),
        ("limit below 1", seed_path, tmp_path / "limit-low.out", "u-minor", "0", MODEL_PATH, False, 2),
        ("limit above 100", seed_path, tmp_path / "limit-high.out", "u-minor", "101", MODEL_PATH, False, 2),
        ("unwritable output", seed_path, blocker / "output.json", "u-minor", "3", MODEL_PATH, False, 4),
        ("model absent", seed_path, tmp_path / "model-absent.out", "u-minor", "3", tmp_path / "absent.orm.yaml", False, 4),
        ("gnd executable absent", seed_path, tmp_path / "gnd-absent.out", "u-minor", "3", MODEL_PATH, True, 4),
    ]
    for name, input_path, output_path, user, limit, model, isolated, expected_exit in hostile_cases:
        completed = _run_bookrec(
            model=model,
            input_path=input_path,
            output_path=output_path,
            user=user,
            limit=limit,
            isolated=isolated,
            timeout=5,
        )
        assert completed.returncode == expected_exit, (name, completed.stderr)
        assert "Traceback" not in completed.stderr, name
        assert not output_path.exists(), name

    performance = copy.deepcopy(seed)
    original_ratings = performance["facts"]["user_rated_book"]
    performance["facts"]["user_rated_book"] = [
        *original_ratings,
        *[
            {"user": f"u-perf-{index:05d}", "book": "b-hobbit"}
            for index in range(10_000 - len(original_ratings))
        ],
    ]
    assert len(performance["facts"]["user_rated_book"]) == 10_000
    performance_path = tmp_path / "ten-thousand-ratings.json"
    performance_path.write_bytes(_canonical_json_bytes(performance))
    assert performance_path.stat().st_size < 1024 * 1024

    performance_output = tmp_path / "performance.out.json"
    capture = tmp_path / "performance-checker-argv.json"
    fake_gnd_dir = _install_fake_gnd(tmp_path / "performance-checker")
    started = time.perf_counter()
    completed = _run_bookrec(
        model=MODEL_PATH,
        input_path=performance_path,
        output_path=performance_output,
        environment={
            "FAKE_GND_CAPTURE": str(capture),
            "FAKE_GND_STDOUT": "{}\n",
            "FAKE_GND_EXIT": "0",
        },
        fake_gnd_dir=fake_gnd_dir,
        timeout=5,
    )
    elapsed = time.perf_counter() - started
    assert completed.returncode == 0, completed.stderr
    assert "Traceback" not in completed.stderr
    assert performance_output.is_file()
    assert json.loads(capture.read_text(encoding="utf-8"))[0] == "check"
    assert elapsed < 2, elapsed


def test_the_relocation_helper_is_gone() -> None:
    """P4-11. T4.4's observable half, stated as an absence that can fail.

    `_runtime_copy` did not merely copy the package: it relocated
    artifacts/model.artifacts.json to a runtime root, manufacturing the layout
    the defective line assumed. An absence test that cannot fail is this
    milestone's defining defect wearing its most convincing disguise, so this
    row pins the absence three ways -- the name is gone, no tree copy of the
    project remains, and the CLI runner names the committed project as cwd.
    """
    source = Path(__file__).read_text(encoding="utf-8")
    # Needles are ASSEMBLED, never written literally: a literal needle in this
    # file would match itself and the row could never fail.
    helper = "_runtime" + "_copy("
    committed_cwd = "cwd=" + "PROJECT,"
    # The invariant is that the PROJECT is never copied -- not that this module
    # never copies anything. Copying a scratch experiment is legitimate and
    # banning it outright would be a guard that forbids the wrong thing.
    project_copies = [
        needle for needle in ("copy" + "tree(PROJECT", "copy" + "2(PROJECT", "copy" + "tree(\n        PROJECT")
        if needle in source
    ]

    assert helper not in source
    assert project_copies == []
    assert committed_cwd in source

    # The controls: each predicate can fire on the code this row replaced.
    original = (
        '    runtime = root / "bookrec-runtime"\n'
        '    shutil.copy' + 'tree(PROJECT / "bookrec", runtime / "bookrec")\n'
        '    shutil.copy' + '2(PROJECT / "artifacts" / "model.artifacts.json", runtime)\n'
    )
    assert [n for n in ("copy" + "tree(PROJECT", "copy" + "2(PROJECT") if n in original]
    assert committed_cwd not in source.replace(committed_cwd, "cwd=relocated,")


def test_the_cli_runner_resolves_the_committed_project_at_runtime(monkeypatch) -> None:
    """P4-11, the RUNTIME half -- source needles alone are an evadable oracle.

    The adversarial reviewer relocated the project through
    `getattr(shutil, "copy" + "tree")`, ran from the copy, left `# cwd=PROJECT,`
    in a comment, and every named row stayed green. A guard that infers runtime
    behaviour from source text can always be walked around by spelling the
    source differently.

    This intercepts the actual subprocess boundary and asserts the resolved cwd
    IS the committed project directory.
    """
    seen: list[Path] = []

    def intercept(command, **kwargs):
        seen.append(Path(kwargs["cwd"]).resolve())
        raise _Intercepted

    monkeypatch.setattr(subprocess, "run", intercept)
    with pytest.raises(_Intercepted):
        _run_bookrec(
            model=MODEL_PATH,
            input_path=BOOKREC / "populations" / "seed.population.json",
            output_path=Path("/dev/null"),
        )

    assert seen == [PROJECT.resolve()]
    assert (seen[0] / "bookrec" / "recommender.py").is_file()
    assert (seen[0] / "artifacts" / "model.artifacts.json").is_file()
    # And it is the tracked tree: git knows the file the CLI will import.
    assert seen[0] == (REPO_ROOT / "examples" / "bookrec" / "project").resolve()

