

















from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS = REPO_ROOT / "tests" / "fixtures" / "migration"
SCRIPT = REPO_ROOT / "src" / "gnd" / "skills" / "gnd-adopt" / "scripts" / "verify_migration.py"
SCHEMA = REPO_ROOT / "src" / "gnd" / "skills" / "gnd-adopt" / "migration.schema.json"

ANSWER_KEY = json.loads((CORPUS / "expected.json").read_text(encoding="utf-8"))
CASES: dict[str, dict] = ANSWER_KEY["cases"]
DECLARED_ASSERTIONS: list[str] = ANSWER_KEY["declared_assertions"]

EXIT_OK = 0
EXIT_ASSERTION_FAILED = 1
EXIT_REFUSED = 3



CAP_BYTES = 10 * 1024 * 1024


def _require_script() -> None:

    if not SCRIPT.exists():
        pytest.fail(
            f"{SCRIPT.relative_to(REPO_ROOT)} does not exist. This corpus is "
            "committed RED by design (spec section 11): the fixtures and their "
            "expected outcomes are authored and approved BEFORE any "
            "implementation file. Turn cases green one lane at a time and name "
            "them in each commit."
        )


def run_script(*args: str) -> subprocess.CompletedProcess[str]:

    _require_script()
    return subprocess.run(
        ["uv", "run", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )


def run_case(name: str, *, migration: Path | None = None) -> subprocess.CompletedProcess[str]:
    case_dir = CORPUS / name
    doc = migration or (case_dir / "model.migration.json")
    return run_script(
        "--migration", str(doc),
        "--model", str(CORPUS / "base" / "v2_migration_corpus.orm.yaml"),
        "--requirements", str(CORPUS / "base" / "REQUIREMENTS.md"),
        "--root", str(CORPUS),
    )


def reported_assertions(stdout: str, stderr: str) -> list[str]:

    found = []
    for line in (stdout + stderr).splitlines():
        head, sep, _ = line.partition(":")
        token = head.strip()
        if sep and token in DECLARED_ASSERTIONS:
            found.append(token)
    return found







@pytest.mark.parametrize("name", sorted(CASES))
def test_corpus_case_exits_as_its_answer_key_says(name: str) -> None:

    expected = CASES[name]
    result = run_case(name)
    assert result.returncode == expected["exit"], (
        f"{name}: expected exit {expected['exit']}, got {result.returncode}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


@pytest.mark.parametrize("name", sorted(n for n in CASES if CASES[n]["assertion"]))
def test_corpus_case_names_the_assertion_it_failed(name: str) -> None:






    expected = CASES[name]
    result = run_case(name)
    reported = reported_assertions(result.stdout, result.stderr)
    assert expected["assertion"] in reported, (
        f"{name}: expected assertion {expected['assertion']} to be reported; "
        f"reported {reported or 'nothing'}.\nstdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


@pytest.mark.parametrize(
    "name", sorted(n for n in CASES if "assertions" in CASES[n])
)
def test_corpus_case_reports_exactly_its_expected_assertion_set(name: str) -> None:







    expected = set(CASES[name]["assertions"])
    result = run_case(name)
    reported = set(reported_assertions(result.stdout, result.stderr))
    assert reported == expected, (
        f"{name}: reported {sorted(reported)}, expected exactly "
        f"{sorted(expected)}.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


@pytest.mark.parametrize(
    "name", sorted(n for n in CASES if "message_names" in CASES[n])
)
def test_corpus_case_message_names_the_offending_thing(name: str) -> None:

    expected = CASES[name]
    result = run_case(name)
    assert expected["message_names"] in (result.stdout + result.stderr), (
        f"{name}: output never names {expected['message_names']!r}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


@pytest.mark.parametrize(
    "name", sorted(n for n in CASES if "stdout_last_line" in CASES[n])
)
def test_a6_prints_the_count_on_the_success_path(name: str) -> None:




    expected = CASES[name]
    result = run_case(name)
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert lines, f"{name}: no stdout at all"
    assert lines[-1] == expected["stdout_last_line"], (
        f"{name}: last stdout line is {lines[-1]!r}, "
        f"expected {expected['stdout_last_line']!r}"
    )


def test_a6_prints_the_count_on_a_failure_path_too() -> None:

    result = run_case("c02-root-digest-drift")
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert any(line.startswith("model-elements: ") for line in lines), (
        "A6 requires the count on EVERY exit path. A count printed only when "
        "everything passes cannot tell an operator that a failed migration "
        "carried zero elements.\n"
        f"stdout:\n{result.stdout}"
    )


def test_the_assertion_order_is_pinned_by_source_order() -> None:





    expected = CASES["c17-multi-violation"]
    result = run_case("c17-multi-violation")
    reported = reported_assertions(result.stdout, result.stderr)
    assert reported, f"c17 reported no assertion.\nstdout:\n{result.stdout}"
    assert reported[0] == expected["first_reported"], (
        f"c17: first reported assertion is {reported[0]}, "
        f"expected {expected['first_reported']}. The declared order is "
        f"{DECLARED_ASSERTIONS}."
    )
    
    
    
    c30 = run_case("c30-order-a2-before-a3")
    ordered = reported_assertions(c30.stdout, c30.stderr)
    assert ordered and ordered[0] == "A2b", (
        f"c30: first reported is {ordered[0] if ordered else 'nothing'}, "
        "expected A2b before A3"
    )


def test_the_document_cannot_choose_the_yardstick_it_is_measured_by() -> None:








    result = run_case("c16-id-source-redirect")
    assert result.returncode == EXIT_REFUSED, (
        "an unknown field is refused, never silently ignored.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "requirements_artifact" in (result.stdout + result.stderr), (
        "the refusal must name the field so the author learns it did nothing"
    )







def _write(tmp_path: Path, payload: str | bytes) -> Path:
    target = tmp_path / "model.migration.json"
    if isinstance(payload, bytes):
        target.write_bytes(payload)
    else:
        target.write_text(payload, encoding="utf-8")
    return target


@pytest.mark.parametrize(
    ("label", "payload"),
    [
        
        
        
        ("long-integer-literal", '{"schema_version": ' + "9" * 100_000 + "}"),
        ("deep-nesting", "[" * 10_000 + "]" * 10_000),
    ],
)
def test_a0_refuses_hostile_bytes_without_a_traceback(
    tmp_path: Path, label: str, payload: str
) -> None:






    doc = _write(tmp_path, payload)
    result = run_case("c01-clean", migration=doc)
    assert result.returncode == EXIT_REFUSED, (
        f"{label}: expected exit {EXIT_REFUSED}, got {result.returncode}"
    )
    assert "Traceback" not in result.stderr, (
        f"{label}: a traceback out of a function that promises totality is a "
        f"contradiction of the shipped contract.\nstderr:\n{result.stderr}"
    )


def test_a0_refuses_a_document_one_byte_past_the_cap(tmp_path: Path) -> None:

    filler = "x" * (CAP_BYTES - len('{"pad": ""}') + 1)
    doc = _write(tmp_path, '{"pad": "' + filler + '"}')
    assert doc.stat().st_size > CAP_BYTES
    result = run_case("c01-clean", migration=doc)
    assert result.returncode == EXIT_REFUSED


def test_a0_applies_the_cap_to_the_read_not_after_it(tmp_path: Path) -> None:







    doc = tmp_path / "model.migration.json"
    with doc.open("wb") as handle:
        handle.write(b'{"pad": "')
        handle.write(b"x" * (CAP_BYTES * 4))
        handle.write(b'"}')
    result = run_case("c01-clean", migration=doc)
    assert result.returncode == EXIT_REFUSED
    match = re.search(r"bytes_read=(\d+)", result.stdout + result.stderr)
    assert match, (
        "the script must report the byte count it consumed; the token alone "
        "is forgeable (adversarial review) -- a whole-file reader could print "
        "it while having read four caps' worth"
    )
    consumed = int(match.group(1))
    assert consumed <= CAP_BYTES + 1, (
        f"the script consumed {consumed} bytes from a file four caps large; "
        "the cap was applied after the read, not to it"
    )


AGGREGATE_CAP_BYTES = 32 * 1024 * 1024
MAX_ARTIFACTS = 64


def _minimal_migration(roots: list[dict], tmp_path: Path) -> Path:

    req = tmp_path / "REQUIREMENTS.md"
    req.write_text("- [x] **CAP-01**: bounded.\n", encoding="utf-8")
    model = tmp_path / "v2_model.orm.yaml"
    model.write_text("version: 2\n", encoding="utf-8")
    import hashlib
    doc = {
        "schema_version": 1,
        "framework": "gsd",
        "roots": [{"path": "REQUIREMENTS.md",
                   "sha256": hashlib.sha256(req.read_bytes()).hexdigest()}] + roots,
        "mapping": [{"id": "CAP-01", "closed": True, "disposition": "model-element",
                     "artifact": "REQUIREMENTS.md", "anchor": "bounded.",
                     "model_elements": [{"kind": "object_type", "id": "x"}]}],
        "not_carried": [],
        "model": {"path": "v2_model.orm.yaml",
                  "sha256": hashlib.sha256(model.read_bytes()).hexdigest()},
    }
    target = tmp_path / "model.migration.json"
    target.write_text(json.dumps(doc), encoding="utf-8")
    return target


def _run_capped(tmp_path: Path, migration: Path) -> subprocess.CompletedProcess[str]:
    return run_script(
        "--migration", str(migration),
        "--model", str(tmp_path / "v2_model.orm.yaml"),
        "--requirements", str(tmp_path / "REQUIREMENTS.md"),
        "--root", str(tmp_path),
    )


def test_a0_bounds_the_whole_run_and_not_only_each_document(tmp_path: Path) -> None:





    import hashlib
    roots = []
    for index in range(4):
        blob = tmp_path / f"blob{index}.bin"
        blob.write_bytes(b"x" * (9 * 1024 * 1024))
        roots.append({"path": blob.name,
                      "sha256": hashlib.sha256(blob.read_bytes()).hexdigest()})
    migration = _minimal_migration(roots, tmp_path)
    result = _run_capped(tmp_path, migration)
    assert result.returncode == EXIT_REFUSED, (
        f"exit {result.returncode}; every file is under the per-document cap, "
        "so only an aggregate budget can refuse this run.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "bytes_read" in (result.stdout + result.stderr)


def test_a0_bounds_the_number_of_cited_artifacts(tmp_path: Path) -> None:

    roots = [
        {"path": f"ghost{index}.md", "sha256": "0" * 64}
        for index in range(MAX_ARTIFACTS + 8)
    ]
    migration = _minimal_migration(roots, tmp_path)
    result = _run_capped(tmp_path, migration)
    assert result.returncode == EXIT_REFUSED, (
        f"exit {result.returncode}; {MAX_ARTIFACTS + 8} cited documents must "
        "trip the artifact-count cap before the ghosts are even opened.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "documents" in (result.stdout + result.stderr)







@pytest.mark.slow
def test_anchor_search_stays_shaped_under_an_input_the_document_controls(
    tmp_path: Path,
) -> None:









    import hashlib
    import time

    def build(anchor_count: int, workdir: Path) -> Path:
        workdir.mkdir()
        lines = [
            f"- [x] **PERF-{index:05d}**: requirement {index} holds a distinct sentence."
            for index in range(anchor_count)
        ]
        filler = "filler " * 100
        req = workdir / "REQUIREMENTS.md"
        req.write_text(
            "\n".join(line + "\n" + filler for line in lines), encoding="utf-8"
        )
        model = workdir / "v2_model.orm.yaml"
        model.write_text("version: 2\n", encoding="utf-8")
        doc = {
            "schema_version": 1,
            "framework": "gsd",
            "roots": [{"path": "REQUIREMENTS.md",
                       "sha256": hashlib.sha256(req.read_bytes()).hexdigest()}],
            "mapping": [
                {"id": f"PERF-{index:05d}", "closed": True,
                 "disposition": "open-question", "artifact": "REQUIREMENTS.md",
                 "anchor": f"requirement {index} holds a distinct sentence."}
                for index in range(anchor_count)
            ],
            "not_carried": [],
            "model": {"path": "v2_model.orm.yaml",
                      "sha256": hashlib.sha256(model.read_bytes()).hexdigest()},
        }
        target = workdir / "model.migration.json"
        target.write_text(json.dumps(doc), encoding="utf-8")
        return target

    def timed(anchor_count: int, name: str) -> float:
        workdir = tmp_path / name
        migration = build(anchor_count, workdir)
        start = time.perf_counter()
        result = run_script(
            "--migration", str(migration),
            "--model", str(workdir / "v2_model.orm.yaml"),
            "--requirements", str(workdir / "REQUIREMENTS.md"),
            "--root", str(workdir),
        )
        elapsed = time.perf_counter() - start
        
        
        
        assert result.returncode == EXIT_ASSERTION_FAILED, result.stdout + result.stderr
        return elapsed

    small = timed(500, "small")
    large = timed(2000, "large")
    ratio = large / small
    
    
    
    assert ratio < 16.0, (
        f"anchor search scaled x{ratio:.1f} when anchors and artifact grew x4 "
        "-- outside the declared sum-of-products bound"
    )







def _declared_assertions_in_script() -> list[str]:
    _require_script()
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "ASSERTIONS":
                    return [str(v) for v in ast.literal_eval(node.value)]
    pytest.fail(
        "the script must declare its assertion ids in a module-level "
        "ASSERTIONS literal. Without it the coverage roll-up below has nothing "
        "to compare the corpus against, and 'every declared branch has a case' "
        "becomes a claim nobody can check."
    )
    raise AssertionError("unreachable")


def test_every_declared_assertion_has_a_case_that_reds_it() -> None:






    declared = _declared_assertions_in_script()
    assert set(declared) == set(DECLARED_ASSERTIONS), (
        f"the script declares {sorted(declared)} and the answer key declares "
        f"{sorted(DECLARED_ASSERTIONS)}. A drift here means one of them is "
        "describing a tool that does not exist."
    )
    covered = {case["assertion"] for case in CASES.values() if case["assertion"]}
    covered |= {"A0"} if ANSWER_KEY["generated_not_committed"].get("A0") else set()
    uncovered = sorted(set(declared) - covered)
    assert not uncovered, (
        f"declared assertions with no case that can fail them: {uncovered}. "
        "A declared branch without a failing case does not ship."
    )


def test_the_coverage_rollup_can_itself_fail() -> None:







    declared = set(DECLARED_ASSERTIONS)
    covered = {case["assertion"] for case in CASES.values() if case["assertion"]}

    
    assert declared - (covered | {"A9-unexercised"}) == declared - covered
    assert "A9-unexercised" not in covered, (
        "control is vacuous: the fabricated assertion is already covered"
    )
    assert sorted((declared | {"A9-unexercised"}) - covered) == ["A9-unexercised"], (
        "T-20's comparison does not notice an assertion with no case"
    )

    
    victim = "A4"
    thinned = {
        name: case for name, case in CASES.items() if case["assertion"] != victim
    }
    thinned_cover = {case["assertion"] for case in thinned.values() if case["assertion"]}
    assert victim not in thinned_cover, (
        f"removing every {victim} case left {victim} still counted as covered, "
        "so T-20 cannot detect a corpus that lost a case"
    )







def test_the_pep723_header_declares_exactly_the_expected_dependencies() -> None:

    _require_script()
    text = SCRIPT.read_text(encoding="utf-8")
    assert text.startswith("# /// script"), "the PEP 723 header must open the file"
    header = text.split("# ///")[1]
    assert 'ruamel.yaml==0.19.1' in header, "A5 parses the model"
    assert 'jsonschema==4.26.0' in header, "D15: the script enforces BY LOADING the schema"


def test_the_script_validates_by_loading_the_schema_not_by_restating_it() -> None:






    _require_script()
    assert SCHEMA.exists(), f"{SCHEMA.relative_to(REPO_ROOT)} does not exist"
    text = SCRIPT.read_text(encoding="utf-8")
    assert SCHEMA.name in text, (
        "the script must load migration.schema.json rather than restate its "
        "requireds inline"
    )


def test_the_script_enforces_a_mutated_schema_differently() -> None:








    import shutil
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        skill_dir = Path(tmp) / "gnd-adopt"
        shutil.copytree(SCRIPT.parent.parent, skill_dir)
        mutated_schema = skill_dir / "migration.schema.json"
        text = mutated_schema.read_text(encoding="utf-8")
        assert '"history"' in text
        mutated_schema.write_text(
            text.replace('"superseded", "history"', '"superseded"'), encoding="utf-8"
        )
        result = subprocess.run(
            ["uv", "run", str(skill_dir / "scripts" / "verify_migration.py"),
             "--migration", str(CORPUS / "c10-unclosed-history" / "model.migration.json"),
             "--model", str(CORPUS / "base" / "v2_migration_corpus.orm.yaml"),
             "--requirements", str(CORPUS / "base" / "REQUIREMENTS.md"),
             "--root", str(CORPUS)],
            capture_output=True, text=True, cwd=REPO_ROOT, check=False,
        )
        assert result.returncode == EXIT_REFUSED, (
            f"exit {result.returncode}: the mutated schema did not change the "
            "verdict, so the script is not enforcing by loading it.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        assert "history" in (result.stdout + result.stderr)


def test_a_symlink_under_root_cannot_reach_outside_it(tmp_path: Path) -> None:






    import hashlib
    outside = tmp_path / "outside.md"
    outside.write_text("secret bytes the run must never open\n", encoding="utf-8")
    root = tmp_path / "root"
    root.mkdir()
    req = root / "REQUIREMENTS.md"
    req.write_text("- [x] **X-01**: contained.\n", encoding="utf-8")
    model = root / "v2_model.orm.yaml"
    model.write_text("version: 2\n", encoding="utf-8")
    (root / "sneaky.md").symlink_to("../outside.md")
    doc = {
        "schema_version": 1, "framework": "gsd",
        "roots": [
            {"path": "REQUIREMENTS.md", "sha256": hashlib.sha256(req.read_bytes()).hexdigest()},
            {"path": "sneaky.md", "sha256": hashlib.sha256(outside.read_bytes()).hexdigest()},
        ],
        "mapping": [{"id": "X-01", "closed": True, "disposition": "open-question",
                     "artifact": "REQUIREMENTS.md", "anchor": "contained."}],
        "not_carried": [],
        "model": {"path": "v2_model.orm.yaml",
                  "sha256": hashlib.sha256(model.read_bytes()).hexdigest()},
    }
    migration = root / "model.migration.json"
    migration.write_text(json.dumps(doc), encoding="utf-8")
    result = run_script(
        "--migration", str(migration), "--model", str(model),
        "--requirements", str(req), "--root", str(root),
    )
    assert result.returncode == EXIT_REFUSED, (
        f"exit {result.returncode}: the symlink was followed out of --root.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "sneaky.md" in (result.stdout + result.stderr)


def test_a5_does_not_count_a_null_constraint(tmp_path: Path) -> None:

    import hashlib
    root = tmp_path
    req = root / "REQUIREMENTS.md"
    req.write_text("- [x] **X-01**: anchored.\n", encoding="utf-8")
    model = root / "v2_model.orm.yaml"
    model.write_text(
        "version: 2\nfact_types:\n  - id: broken\n    constraints: [null]\n",
        encoding="utf-8",
    )
    doc = {
        "schema_version": 1, "framework": "gsd",
        "roots": [{"path": "REQUIREMENTS.md",
                   "sha256": hashlib.sha256(req.read_bytes()).hexdigest()}],
        "mapping": [{"id": "X-01", "closed": True, "disposition": "model-element",
                     "artifact": "REQUIREMENTS.md", "anchor": "anchored.",
                     "model_elements": [{"kind": "constraint", "fact_type": "broken", "index": 0}]}],
        "not_carried": [],
        "model": {"path": "v2_model.orm.yaml",
                  "sha256": hashlib.sha256(model.read_bytes()).hexdigest()},
    }
    migration = root / "model.migration.json"
    migration.write_text(json.dumps(doc), encoding="utf-8")
    result = run_script(
        "--migration", str(migration), "--model", str(model),
        "--requirements", str(req), "--root", str(root),
    )
    assert result.returncode == EXIT_ASSERTION_FAILED
    assert "A5" in reported_assertions(result.stdout, result.stderr), (
        f"a null constraint entry was counted as addressable.\n"
        f"stdout:\n{result.stdout}"
    )


def test_the_script_reaches_no_network_and_imports_no_gnd() -> None:

    _require_script()
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    banned = {
        "gnd", "httpx", "requests", "aiohttp", "urllib", "socket", "http",
        "ftplib", "telnetlib", "anthropic", "openai", "google",
    }
    seen: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            seen.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            seen.add(node.module.split(".")[0])
    offending = sorted(seen & banned)
    assert not offending, (
        f"the bundled script imports {offending}. It must run on a machine "
        "where gnd is absent and must reach no network."
    )


def test_the_cap_literal_has_one_home() -> None:

    _require_script()
    text = SCRIPT.read_text(encoding="utf-8")
    assert str(CAP_BYTES) in text or "10 * 1024 * 1024" in text, (
        f"the harness asserts a cap of {CAP_BYTES} and the script does not "
        "name it. Two caps that disagree make every T-13 row meaningless."
    )







def test_the_answer_key_is_not_reachable_from_the_entry_point() -> None:




    readme = (CORPUS / "README.md").read_text(encoding="utf-8")
    for name, case in CASES.items():
        assert f"exit {case['exit']}" not in readme, (
            f"README states an expected exit for {name}"
        )
        if case["assertion"]:
            assert f"{case['assertion']}:" not in readme, (
                f"README names the assertion id for {name}"
            )


def test_every_committed_case_directory_appears_in_the_answer_key() -> None:

    on_disk = {
        path.name
        for path in CORPUS.iterdir()
        if path.is_dir() and path.name != "base"
    }
    assert on_disk == set(CASES), (
        f"on disk but unanswered: {sorted(on_disk - set(CASES))}; "
        f"answered but absent: {sorted(set(CASES) - on_disk)}"
    )


def test_the_base_model_validates() -> None:

    result = subprocess.run(
        [sys.executable, "-m", "gnd", "validate", str(CORPUS / "base" / "v2_migration_corpus.orm.yaml")],
        capture_output=True, text=True, cwd=REPO_ROOT, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
