"""ROF4 (report-output-fidelity): accept either model identity where one is matched (issue 111).

The corpus under tests/fixtures/rof4-accept-identities is the phase's approval
instrument; its README tells each case, expected/cases.json holds the answers and
expected/identities.json the identities. Written before the implementation: every
case that supplies the canonical identity at a site that has two identities is
refused today, and so are the helper, source-scan, example and documentation tests.
The legacy, wrong and reference cases, and the corpus self-check, pass now.
"""

from __future__ import annotations

import ast
import hashlib
import importlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest
from support.cli_runner import run_main
from support.repository import REPO_ROOT

from gnd.model import load_model, load_model_bytes
from gnd.population import load_population
from gnd.transition import transition_model_identity

CORPUS = REPO_ROOT / "tests" / "fixtures" / "rof4-accept-identities"
EXPECTED = CORPUS / "expected"
IDENTITIES = json.loads((EXPECTED / "identities.json").read_text())
ANSWERS = json.loads((EXPECTED / "cases.json").read_text())
CASES = {row["case"]: row for row in ANSWERS["cases"]}
WRONG = IDENTITIES["wrong"]
APPROVALS = REPO_ROOT / "src" / "gnd" / "examples" / "approvals"
CANONICAL_EXAMPLE = APPROVALS / "plan-draft-2.canonical.steps.json"
SEEDS = (7, 8)


# --------------------------------------------------------------------------- #
# spellings and runs
# --------------------------------------------------------------------------- #


def _identity(model: str, spelling: str) -> str:
    row = IDENTITIES["models"][model]
    if spelling == "wrong":
        return WRONG
    if spelling == "dropped_references":
        return row["dropped_references"]
    return row[spelling]


def _bare(value: str) -> str:
    return value.removeprefix("sha256:")


def _sidecar_identity(model: str, spelling: str) -> str:
    if spelling.startswith("prefixed-"):
        return _identity(model, spelling.removeprefix("prefixed-"))
    return _bare(_identity(model, spelling))


def _workdir(root: Path) -> Path:
    work = root / "run"
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(CORPUS / "models", work / "models")
    return work


def _write_json(path: Path, document: object) -> None:
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _model_path(case: dict) -> str:
    return IDENTITIES["models"][case["model"]]["path"]


def _run(case: dict, root: Path) -> dict:
    """Run one case in a fresh copy of the models; the paths it prints are the same every run."""
    work = _workdir(root)
    site = case["site"]
    artifact = CORPUS / case["artifact"]
    if site == "S1":
        steps = json.loads(artifact.read_text())
        steps["model_digest"] = _identity(case["model"], case["spelling"])
        _write_json(work / "steps.json", steps)
        result = run_main(
            ["check", _model_path(case), "--pre", case["pre"], "--steps", "steps.json", "--format", "json"],
            cwd=work,
        )
        payload = json.loads(result.stdout)
        return {"exit": result.returncode, "payload": payload, "report": payload.get("report", payload)}
    if site in {"S2", "S3"}:
        from gnd.admission_validation import AdmissionValidationError, validate_admission_payload

        payload = json.loads(artifact.read_text())
        target = payload if site == "S2" else payload.get("report", payload)
        target["model_digest"] = _identity(case["model"], case["spelling"])
        model = load_model(work / _model_path(case))
        candidate = load_population(work / case["candidate"], model=model)
        try:
            metrics = validate_admission_payload(payload, model=model, candidate=candidate)
        except AdmissionValidationError as error:
            return {"error": str(error)}
        return {"metrics": metrics}
    if site == "S4":
        report = json.loads(artifact.read_text())
        report["model_digest"] = _identity(case["model"], case["spelling"])
        _write_json(work / "check.json", report)
        result = run_main(["coverage", _model_path(case), "--check", "check.json", "--format", "json"], cwd=work)
        return {"exit": result.returncode, "stdout": result.stdout.decode(), "stderr": result.stderr.decode()}
    if site in {"S5", "S7"}:
        shutil.copytree(artifact, work / "corpus")
        for seed, spelling in zip(SEEDS, case["spellings"], strict=True):
            sidecar = work / "corpus" / "conforming" / f"model.orm.conforming.seed{seed}.meta.json"
            document = json.loads(sidecar.read_text())
            document["model_digest"] = _sidecar_identity(case["model"], spelling)
            _write_json(sidecar, document)
        result = run_main(["measure", _model_path(case), "--populations", "corpus", "--format", "json"], cwd=work)
        return {"exit": result.returncode, "stdout": result.stdout.decode(), "stderr": result.stderr.decode()}
    if site == "S6":
        certificate = json.loads(artifact.read_text())
        binding = certificate["binding"]
        binding["model_digest"] = _identity(case["model"], case["spelling"])
        edit = case.get("binding_edit")
        if edit == "wrong-candidate":
            binding["candidate_digest"] = WRONG
        elif edit == "extra-key":
            binding["extra"] = "x"
        elif edit == "missing-key":
            del binding["references"]
        _write_json(work / "witness.json", certificate)
        result = run_main(
            ["replay", _model_path(case), "models/dependencies/patched.pop.json", "witness.json", "--raw", "--json"],
            cwd=work,
        )
        payload = json.loads(result.stdout)
        return {"exit": result.returncode, "payload": payload}
    raise AssertionError(f"unknown site {site}")


def _fill(template: str, case: dict, supplied: str) -> str:
    legacy = IDENTITIES["models"][case["model"]]["legacy"]
    return template.format(
        supplied=supplied,
        supplied_bare=_bare(supplied),
        legacy=legacy,
        legacy_bare=_bare(legacy),
        source="check.json",
        corpus="corpus",
    )


def _supplied(case: dict) -> str:
    if "spellings" in case:
        return _sidecar_identity(case["model"], case["spellings"][0])
    return _identity(case["model"], case["spelling"])


def _comparable(case: dict, observed: dict) -> object:
    """What two runs of one site must agree on byte for byte."""
    site = case["site"]
    if site in {"S2", "S3"}:
        return observed
    if site in {"S1", "S6"}:
        return json.dumps(observed["payload"], sort_keys=True)
    return observed["stdout"]


def _check(case: dict, observed: dict) -> None:
    expect = case["expect"]
    site = case["site"]
    if site in {"S2", "S3"}:
        if expect.get("admitted"):
            assert "metrics" in observed, f"{case['case']} refused: {observed.get('error')}"
        else:
            assert observed == {"error": expect["error"]}
        return
    assert observed["exit"] == expect["exit"], f"{case['case']}: {observed}"
    if site == "S1":
        report = observed["report"]
        assert report["outcome"] == expect["outcome"]
        if "rule_id" in expect:
            issues = [i for i in report["issues"] if i["rule_id"] == expect["rule_id"]]
            assert [i["message"] for i in issues] == [_fill(expect["message"], case, _supplied(case))]
    elif site == "S4":
        if expect.get("binding") == "model-bound":
            # Model-bound: indexed as check evidence, not listed as an unbound source.
            sources = json.loads(observed["stdout"])["sources"]
            assert (sources["check"], sources["unbound"]) == (["check.json"], [])
        else:
            assert _fill(expect["message"], case, _supplied(case)) in observed["stdout"] + observed["stderr"]
    elif site in {"S5", "S7"}:
        if "model_digest" in expect:
            assert json.loads(observed["stdout"])["model_digest"] == _fill(expect["model_digest"], case, WRONG)
        else:
            assert json.loads(observed["stdout"])["error"] == _fill(expect["message"], case, _supplied(case))
    elif site == "S6":
        assert observed["payload"]["reason"] == expect["reason"]


def _walk_rows(document: object):
    if isinstance(document, dict):
        yield document
        for value in document.values():
            yield from _walk_rows(value)
    elif isinstance(document, list):
        for value in document:
            yield from _walk_rows(value)


# --------------------------------------------------------------------------- #
# the corpus checks itself (passes before the implementation)
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("name", sorted(IDENTITIES["models"]))
def test_corpus_identities_are_the_models_identities(name: str) -> None:
    row = IDENTITIES["models"][name]
    model = load_model(CORPUS / row["path"])
    assert transition_model_identity(model) == row["legacy"]
    printed = run_main(["validate", row["path"], "--identity"], cwd=CORPUS).stdout.decode().splitlines()[0]
    assert printed == f"MODEL IDENTITY {row['canonical']} (identity_version {row['canonical_version']})"
    assert (row["legacy"] == row["canonical"]) == bool(model.reference_populations)


def test_the_dropped_references_value_is_the_plain_twin_of_the_reference_model() -> None:
    from ruamel.yaml import YAML

    from gnd.values import model_identity

    document = YAML(typ="safe").load((CORPUS / "models/reference/model.orm.yaml").read_text())
    document.pop("reference_populations")
    twin = load_model_bytes(json.dumps(document).encode(), source="twin.orm.json")
    assert model_identity(twin) == IDENTITIES["models"]["reference"]["dropped_references"]


def test_every_artifact_is_pinned_with_the_legacy_identity() -> None:
    def pinned(path: str) -> list[str]:
        document = json.loads((CORPUS / path).read_text())
        return [row["model_digest"] for row in _walk_rows(document) if "model_digest" in row]

    approvals = IDENTITIES["models"]["approvals"]["legacy"]
    assert set(pinned("artifacts/s1-approvals.steps.json")) == {approvals}
    assert set(pinned("artifacts/s3-approvals.check.json")) == {approvals}
    assert set(pinned("artifacts/s1-reference.steps.json")) == {IDENTITIES["models"]["reference"]["legacy"]}
    assert set(pinned("artifacts/s2s3-reference.check.json")) == {IDENTITIES["models"]["reference"]["legacy"]}
    assert set(pinned("artifacts/s4-nonstructured.check.json")) == {IDENTITIES["models"]["nonstructured"]["legacy"]}
    assert set(pinned("artifacts/s6-dependencies.witness.json")) == {IDENTITIES["models"]["dependencies"]["legacy"]}
    for seed in SEEDS:
        assert set(pinned(f"artifacts/s5s7-corpus/conforming/model.orm.conforming.seed{seed}.meta.json")) == {
            _bare(approvals)
        }
    assert (CORPUS / "artifacts/s1-approvals.steps.json").read_bytes() == (
        APPROVALS / "plan-draft-2.steps.json"
    ).read_bytes()


def test_every_case_is_told_in_the_readme_and_named_once() -> None:
    readme = (CORPUS / "README.md").read_text()
    assert len(CASES) == len(ANSWERS["cases"])
    for site in sorted({row["site"] for row in ANSWERS["cases"]}):
        assert f"({site}" in readme or f", {site})" in readme or f" {site})" in readme, site


# --------------------------------------------------------------------------- #
# T2-T7: the cases, site by site
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("name", sorted(CASES))
def test_case(name: str, tmp_path: Path) -> None:
    case = CASES[name]
    observed = _run(case, tmp_path)
    _check(case, observed)
    twin = case["expect"].get("same_payload_as")
    if twin:
        baseline = _run(CASES[twin], tmp_path)
        assert _comparable(case, observed) == _comparable(CASES[twin], baseline)


# --------------------------------------------------------------------------- #
# T1: one helper, called at the seven sites and nowhere else
# --------------------------------------------------------------------------- #

SITES = {
    ("transition.py", "verify_digests"),
    ("admission_validation.py", "validate_reference_transport"),
    ("admission_validation.py", "_validate"),
    ("coverage.py", "_report_binding"),
    ("measure/service.py", "_cmd_measure"),
    ("witness/kernel.py", "replay_witness"),
    ("measure/report.py", "build_measurement_report"),
}
# Exact coherence (X1, X2) and the in-process marker (P1): they keep one value.
EXACT = {
    ("assurance/transport.py", "consume_receipt"),
    ("model/__init__.py", "resolve_context"),
    ("population.py", "matches_validation_marker"),
}
# Copy or produce an identity (C1) and the generated plan's constant (G1).
COPIES = {
    ("export/souffle_runtime.py", "map_proof"),
    ("witness/io.py", "identity"),
    ("export/lean.py", "render_lean"),
    ("export/souffle.py", "render_souffle"),
    ("witness/producer.py", "produce_witness"),
    ("export/pyrel_rules.py", "_plan_constants"),
}
DIGEST_FUNCTIONS = {
    "transition_model_identity",
    "reference_model_digest",
    "validated_model_sha256",
    "_model_digest",
    "model_identity",
}
SOURCE = REPO_ROOT / "src" / "gnd"


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _functions():
    for path in sorted(SOURCE.rglob("*.py")):
        relative = path.relative_to(SOURCE).as_posix()
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                yield relative, node


def _calls(function: ast.AST, name: str) -> bool:
    return any(isinstance(n, ast.Call) and _call_name(n.func) == name for n in ast.walk(function))


def _compares_a_computed_digest(function: ast.AST) -> bool:
    def digest_call(node):
        return isinstance(node, ast.Call) and _call_name(node.func) in DIGEST_FUNCTIONS

    bound = {
        target.id
        for node in ast.walk(function)
        if isinstance(node, ast.Assign) and digest_call(node.value)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    for node in ast.walk(function):
        if isinstance(node, ast.Compare) and any(isinstance(op, (ast.Eq, ast.NotEq)) for op in node.ops):
            sides = [node.left, *node.comparators]
            if any(digest_call(s) or (isinstance(s, ast.Name) and s.id in bound) for s in sides):
                return True
    return False


def test_t1_the_seven_sites_call_the_helper_and_nothing_else_does() -> None:
    callers = {
        (path, fn.name)
        for path, fn in _functions()
        if path != "values.py" and _calls(fn, "model_identity_matches")
    }
    assert callers == SITES


def test_t1_only_the_exact_sites_still_compare_a_computed_digest() -> None:
    comparing = {(path, fn.name) for path, fn in _functions() if _compares_a_computed_digest(fn)}
    assert comparing == {("model/__init__.py", "resolve_context"), ("population.py", "matches_validation_marker")}


def test_t1_exact_copy_and_plan_sites_are_unchanged() -> None:
    functions = {(path, fn.name): fn for path, fn in _functions()}
    for key in EXACT | COPIES:
        assert key in functions, key
        assert not _calls(functions[key], "model_identity_matches"), key
    transport = (SOURCE / "assurance/transport.py").read_text()
    assert 'document["model_digest"] != payload.get("model_digest")' in transport
    rules = (SOURCE / "export/pyrel_rules.py").read_text()
    assert "if document['model_digest'] != MODEL_DIGEST:" in rules
    assert "model_identity_matches" not in rules


def test_t1_consumers_never_call_the_canonical_identity_directly() -> None:
    direct = {
        (path, fn.name)
        for path, fn in _functions()
        if path != "values.py" and any(_calls(fn, name) for name in ("model_identity", "model_identity_bytes"))
    }
    # Only the producer (gnd validate --identity) reads the canonical bytes itself.
    assert direct <= {("output.py", "_print_model_identity")}


# --------------------------------------------------------------------------- #
# T7, T9: the helper
# --------------------------------------------------------------------------- #


def _helper(name: str = "model_identity_matches"):
    function = getattr(importlib.import_module("gnd.values"), name, None)
    assert function is not None, f"gnd.values.{name} does not exist yet"
    return function


def _corpus_model(name: str):
    return load_model(CORPUS / IDENTITIES["models"][name]["path"])


def test_t9_the_helper_names_which_identity_matched() -> None:
    matches = _helper()
    model = _corpus_model("approvals")
    legacy = IDENTITIES["models"]["approvals"]["legacy"]
    canonical = IDENTITIES["models"]["approvals"]["canonical"]
    assert matches(legacy, model) == "legacy-repr"
    assert matches(canonical, model) == "canonical-v2"
    assert matches(_bare(legacy), model, prefixed=False) == "legacy-repr"
    assert matches(_bare(canonical), model, prefixed=False) == "canonical-v2"
    for refused in (
        WRONG,
        _bare(legacy),
        _bare(canonical),
        legacy.upper(),
        "sha256:" + _bare(canonical).upper(),
        "",
        "sha256:",
        None,
        123,
        legacy.encode(),
        {"model_digest": legacy},
    ):
        assert matches(refused, model) is None, refused
    for refused in (legacy, canonical, _bare(WRONG), ""):
        assert matches(refused, model, prefixed=False) is None, refused


def test_t9_accepted_identities_lists_legacy_first() -> None:
    accepted = _helper("accepted_model_identities")
    row = IDENTITIES["models"]["approvals"]
    assert accepted(_corpus_model("approvals")) == (row["legacy"], row["canonical"])
    assert accepted(_corpus_model("approvals"), prefixed=False) == (_bare(row["legacy"]), _bare(row["canonical"]))
    reference = IDENTITIES["models"]["reference"]["legacy"]
    assert accepted(_corpus_model("reference")) == (reference,)


def test_t7_a_reference_model_has_one_identity() -> None:
    matches = _helper()
    model = _corpus_model("reference")
    row = IDENTITIES["models"]["reference"]
    assert matches(row["legacy"], model) == "canonical-v1"
    assert matches(row["dropped_references"], model) is None
    assert matches(WRONG, model) is None


def test_t7_a_model_without_a_canonical_identity_matches_by_legacy_only() -> None:
    from gnd.values import _model_digest

    matches = _helper()
    surrogate = load_model(REPO_ROOT / "tests/fixtures/rof3-model-identity/models/surrogate.orm.json")
    legacy = "sha256:" + _model_digest(surrogate)
    assert matches(legacy, surrogate) == "legacy-repr"
    assert matches(WRONG, surrogate) is None
    assert matches(IDENTITIES["models"]["approvals"]["canonical"], surrogate) is None
    assert _helper("accepted_model_identities")(surrogate) == (legacy,)


# --------------------------------------------------------------------------- #
# T13: the legacy path never computes the canonical identity
# --------------------------------------------------------------------------- #

LEGACY_CASES = sorted(
    name
    for name, row in CASES.items()
    if row.get("spelling") == "legacy" or row.get("spellings") == ["legacy", "legacy"]
)


def test_t13_legacy_pins_never_compute_the_canonical_identity(tmp_path, monkeypatch) -> None:
    from gnd import values

    calls = []

    def refuse(model, version=None):
        calls.append(model)
        raise values.ModelIdentityError("$", "patched out by the laziness test")

    monkeypatch.setattr(values, "model_identity", refuse)
    for name in LEGACY_CASES:
        _check(CASES[name], _run(CASES[name], tmp_path))
    assert calls == [], f"{len(calls)} canonical walks on the legacy path"
    # The patch is on the path the helper takes: a canonical pin reaches it.
    observed = _run(CASES["S1-approvals-canonical"], tmp_path)
    assert calls, "the canonical case never computed the canonical identity"
    assert observed["exit"] == 3


# --------------------------------------------------------------------------- #
# T10: the shipped pins and the shipped canonical example
# --------------------------------------------------------------------------- #

SHIPPED = ANSWERS["shipped_pins"]


@pytest.mark.parametrize("steps", sorted(SHIPPED["exits"]))
def test_t10_shipped_pins_exit_as_at_the_base(steps: str) -> None:
    argv = ["check", SHIPPED["model"], "--pre", SHIPPED["pre"], "--steps", f"src/gnd/examples/approvals/{steps}"]
    if steps in SHIPPED["post"]:
        argv += ["--post", SHIPPED["post"][steps]]
    result = run_main([*argv, "--format", "json"], cwd=REPO_ROOT)
    assert b"model-digest-mismatch" not in result.stdout
    assert result.returncode == SHIPPED["exits"][steps]


def test_t10_the_canonical_example_differs_from_draft_two_only_in_its_pin() -> None:
    assert CANONICAL_EXAMPLE.exists(), "the shipped canonical example does not exist yet"
    draft = json.loads((APPROVALS / "plan-draft-2.steps.json").read_text())
    example = json.loads(CANONICAL_EXAMPLE.read_text())
    assert example == {**draft, "model_digest": IDENTITIES["models"]["approvals"]["canonical"]}
    readme = (APPROVALS / "README.md").read_text()
    assert "plan-draft-2.canonical.steps.json" in readme


def test_t10_the_quoted_pin_in_the_task_text_is_untouched() -> None:
    task = (APPROVALS / "recordings" / "TASK.md").read_bytes()
    assert hashlib.sha256(task).hexdigest() == ANSWERS["frozen"]["src/gnd/examples/approvals/recordings/TASK.md"]


# --------------------------------------------------------------------------- #
# T11: documentation
# --------------------------------------------------------------------------- #

DOCS = (
    "src/gnd/skills/gnd-orm-core/references/representation-format.md",
    "src/gnd/schema/steps.schema.json",
    "src/gnd/skills/gnd-orm-core/references/steps.schema.json",
    "docs/reference/formats.md",
    "docs/guides/data-and-transitions.md",
    "docs/agents/plans.md",
)


@pytest.mark.parametrize("path", DOCS)
def test_t11_the_docs_say_either_identity(path: str) -> None:
    text = (REPO_ROOT / path).read_text(encoding="utf-8")
    assert "either identity" in text.lower(), path


def test_t11_the_rule_has_one_home_and_the_guide_names_the_producer() -> None:
    home = (REPO_ROOT / DOCS[0]).read_text(encoding="utf-8")
    rows = [line for line in home.splitlines() if line.startswith("|") and "`model_digest`" in line]
    assert any("either identity" in row.lower() for row in rows), "the digest table's model_digest row"
    guide = (REPO_ROOT / "docs/guides/data-and-transitions.md").read_text(encoding="utf-8")
    assert "gnd validate" in guide and "--identity" in guide
    plans = (REPO_ROOT / "docs/agents/plans.md").read_text(encoding="utf-8")
    assert "legacy" in plans.lower()


# --------------------------------------------------------------------------- #
# T12: frozen bytes
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("path", sorted(ANSWERS["frozen"]))
def test_t12_recorded_refusals_and_quotes_keep_their_bytes(path: str) -> None:
    assert hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest() == ANSWERS["frozen"][path]


def test_t12_the_generated_plan_keeps_the_legacy_constant() -> None:
    from gnd.export.pyrel_rules import render

    program = render(APPROVALS / "model.orm.yaml", "duckdb")
    row = IDENTITIES["models"]["approvals"]
    assert f"MODEL_DIGEST = {row['legacy']!r}" in program
    assert row["canonical"] not in program


# --------------------------------------------------------------------------- #
# T8: a generated Pyrel plan refuses what gnd check accepts (ruling D7)
# --------------------------------------------------------------------------- #


@pytest.mark.pyrel_oracle
def test_t8_the_generated_plan_refuses_the_canonical_example(tmp_path) -> None:
    from ruamel.yaml import YAML
    from test_pyrel_rules_families import NATIVE

    from gnd.export.pyrel_rules import render

    assert run_main(
        ["check", "model.orm.yaml", "--pre", "state.pop.yaml", "--steps", CANONICAL_EXAMPLE.name],
        cwd=APPROVALS,
    ).returncode == 0
    program = tmp_path / "rules.py"
    program.write_text(render(APPROVALS / "model.orm.yaml", "duckdb"))
    pre = tmp_path / "state.pop.json"
    pre.write_text(json.dumps(YAML(typ="safe").load((APPROVALS / "state.pop.yaml").read_text())))
    run = subprocess.run(
        [str(NATIVE), "-I", str(program), "--pre", str(pre), "--steps", str(CANONICAL_EXAMPLE)],
        capture_output=True, text=True, timeout=300, check=False,
    )
    assert run.returncode == 3
    assert "transition:model-digest-mismatch" in run.stderr


def test_the_answers_name_every_site_and_spelling() -> None:
    sites = {row["site"] for row in ANSWERS["cases"]}
    assert sites == {"S1", "S2", "S3", "S4", "S5", "S6", "S7"}
    spellings = {row.get("spelling") for row in ANSWERS["cases"]} | {
        s for row in ANSWERS["cases"] for s in row.get("spellings", ())
    }
    assert spellings - {None} == set(ANSWERS["spellings"])
