"""Offline enforcement, the C6 sidecar binding, and publication pinning (Task 2).

Three import scans at three scopes, each commented with its decision; the C6
binding rejections; and the byte-for-byte re-measure proof. Together these make
D-18's "the deterministic lane needs no secrets" mechanically true rather than
aspirational: published numbers are computed offline from committed artifacts,
and two runs over one corpus reproduce byte-for-byte.
"""

from __future__ import annotations

import ast
import hashlib
import inspect
import json
import os
import re
from pathlib import Path

import pytest

from gnd.cli import main
from gnd.measure import report as measure_report
from gnd.measure import service as patched_service

REPO_ROOT = Path(__file__).resolve().parent.parent
GND_SRC = REPO_ROOT / "src" / "gnd"
MEASURE_SRC = GND_SRC / "measure"
EXTRACT_SRC = GND_SRC / "extract"
FIDELITY_SRC = GND_SRC / "fidelity"
#: Scan-4 roots (R-04'): the extraction lane's closure walk starts here.
#: A tuple so plan 04 can EXTEND it with the fidelity lane rather than
#: renaming the scan or re-scoping scans 1-3 — which plan 04 did:
#: ``src/gnd/fidelity/`` joined in the same posture (T-02.1-15). The fidelity
#: number is computed from committed case directories, so a network import
#: reachable from it would mean a published rate depended on a live call.
EXTRACTION_LANE_ROOTS = (EXTRACT_SRC, FIDELITY_SRC)
EXP_SRC = GND_SRC / "exp"
CODEGEN_SRC = GND_SRC / "codegen"
#: Scan-5 roots (plan 03-01): the generation lane's closure walk starts here.
#: A NEW, separately-named scan rather than an extension of EXTRACTION_LANE_ROOTS
#: or a re-scoping of scans 1-3 — R-04' forbids re-scoping an owner-decided guard
#: without a decision (G-3), and the generation lane is a different claim: codegen
#: and the experiment primitive derive from committed artifacts, so a network
#: import reachable from them would mean a conformance verdict depended on a live
#: call. Later plans in this phase APPEND their package roots to this tuple.
#: ``src/gnd/codegen/`` joined at plan 03-03, in the same posture and in the
#: commit that created the package — G-02's no-provider-client rule binds
#: ``src/gnd/``, and the emitter is the one lane with a standing temptation to
#: reach for a client (it writes an "agent" project). ``src/gnd/conformance/``
#: joined at plan 03-05, likewise in the commit that created it: a conformance
#: result is a claim about committed artifacts, and a network call anywhere in
#: its closure would mean a recorded "the code still matches the model" was not
#: reproducible from the repository. Scans 1-4 untouched.
CONFORMANCE_SRC = GND_SRC / "conformance"
EVOLUTION_SRC = GND_SRC / "evolve"
GENERATION_LANE_ROOTS = (EXP_SRC, CODEGEN_SRC, CONFORMANCE_SRC, EVOLUTION_SRC)
MODEL_EVOLVE_SKILL_FILES = (
    GND_SRC / "skills" / "gnd-model-evolve" / "SKILL.md",
    GND_SRC / "skills" / "gnd-model-evolve" / "references" / "evolution-contract.md",
)
MODEL = REPO_ROOT / "tests" / "fixtures" / "models" / "full_vocabulary.orm.yaml"

#: Network libraries: a distinct class from the provider CLIENTS below. The
#: metrics lane must reach none of these — offline is the whole guarantee.
_NETWORK_LIBS = ("httpx", "requests", "aiohttp", "urllib.request", "socket")
#: Provider clients (D-20): an embedded client, never the skill-run proposer.
#: Widened in phase 02.1 beyond ("anthropic", "openai") — 01.2 D-13: a guard
#: narrower than its rule reports green over exactly the gap it was hardened
#: to close, and five widely-installed clients were absent from the tuple.
_PROVIDER_CLIENTS = (
    "anthropic",
    "openai",
    "google.generativeai",
    "cohere",
    "mistralai",
    "litellm",
    "ollama",
)

def _imports(source: str, *, package: str | None = None) -> set[str]:
    """All static import spellings, including local/lazy and from-import children."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                if package is None:
                    continue  # External forbidden names cannot be relative imports.
                parts = package.split(".")
                if node.level > len(parts):
                    raise ValueError("relative import climbs above its package")
                prefix = ".".join(parts[:len(parts) - node.level + 1])
                base = ".".join(part for part in (prefix, base) if part)
            if base:
                names.add(base)
                names.update(base + "." + alias.name for alias in node.names if alias.name != "*")
    return names


def _package(path: Path) -> str:
    return ".".join(("gnd", *path.relative_to(GND_SRC).parent.parts))


def _forbidden_hit(source: str, needles: tuple[str, ...]) -> list[str]:
    imported = _imports(source)
    hits: list[str] = []
    for needle in needles:
        for name in imported:
            if name == needle or name.startswith(needle + "."):
                hits.append(needle)
    return sorted(set(hits))


# --------------------------------------------------------------------------- #
# scan 1 — the measure/-scoped import direction (owner-rescoped to the metrics lane)
# --------------------------------------------------------------------------- #


def test_measure_lane_imports_no_provider_or_network_module() -> None:
    """No module under ``src/gnd/measure/`` imports a provider or network module.

    An AST-over-source scan, not a convention — it can fail. The two scans
    are scoped to the METRICS lane ONLY. It deliberately
    does NOT scan ``src/gnd/synth/``: the owner's correction rescoped enforcement
    to the metrics lane, and the development (generation) lane may be live and
    nondeterministic. The natural refactor is to "harden" the scan tree-wide —
    that would re-impose the scoping the owner explicitly withdrew, so do not.
    """
    offenders: dict[str, list[str]] = {}
    for path in sorted(MEASURE_SRC.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        hits = _forbidden_hit(source, _PROVIDER_CLIENTS + _NETWORK_LIBS)
        if hits:
            offenders[str(path.relative_to(REPO_ROOT))] = hits
    assert not offenders, (
        f"the metrics lane imports a provider/network module: {offenders}. "
        f"Published numbers are computed OFFLINE from committed artifacts (D-18)."
    )


# --------------------------------------------------------------------------- #
# scan 2 — the tree-wide D-20 provider-client scan (packaging, both lanes)
# --------------------------------------------------------------------------- #


def test_no_provider_client_anywhere_in_the_package() -> None:
    """No module anywhere under ``src/gnd/`` (excluding the bundled skills tree,
    which ships PEP 723 scripts, not package code) imports a provider client.

    This one IS tree-wide, because D-20 is packaging: the proposer is a skill run
    by the terminal agent, never an embedded client, and that stands in BOTH
    lanes. Distinct from scan 3 below, which matches network LIBRARIES rather
    than clients.
    """
    offenders: dict[str, list[str]] = {}
    for path in sorted(GND_SRC.rglob("*.py")):
        if "skills" in path.relative_to(GND_SRC).parts:
            continue
        source = path.read_text(encoding="utf-8")
        hits = _forbidden_hit(source, _PROVIDER_CLIENTS)
        if hits:
            offenders[str(path.relative_to(REPO_ROOT))] = hits
    assert not offenders, (
        f"a provider client is embedded in the package: {offenders}. The proposer "
        f"is a skill run by the terminal agent, never an embedded client (D-20)."
    )


# --------------------------------------------------------------------------- #
# scan 3 — the network-library CLOSURE scan (Claude-MEDIUM), distinct from scan 2
# --------------------------------------------------------------------------- #


def _module_path(dotted: str) -> Path | None:
    """Map a ``gnd.a.b`` dotted name to its source file under src/gnd/, or None."""
    if not dotted.startswith("gnd"):
        return None
    parts = dotted.split(".")[1:]  # drop leading 'gnd'
    if not parts:
        return GND_SRC / "__init__.py"
    as_module = GND_SRC.joinpath(*parts).with_suffix(".py")
    if as_module.is_file():
        return as_module
    as_package = GND_SRC.joinpath(*parts) / "__init__.py"
    if as_package.is_file():
        return as_package
    # A `from gnd.a import name` where `name` is a symbol, not a submodule: fall
    # back to the package/module the symbols live in.
    return _module_path('.'.join(dotted.split('.')[:-1]))


def test_no_network_library_is_reachable_from_the_measure_lane() -> None:
    """Walk ``gnd.measure``'s transitive import closure and assert no module in it
    imports a network library (Claude-MEDIUM).

    The metrics lane reads ground truth from ``gnd.synth.provenance`` sidecars, so
    ``synth/`` is in ``measure/``'s closure — and a network library added to the
    UNPOLICED ``synth/`` would enter that closure and be caught by NEITHER scan 1
    (which reads only measure/ source) nor scan 2 (which matches provider clients,
    not network libraries). This scan closes that gap: it follows every intra-gnd
    import from measure/ and checks each reached module for a network-library
    import. It keeps scan 1's measure/-only comment intact by being a SEPARATE,
    third scope.
    """
    seen: set[Path] = set()
    queue: list[Path] = [p for p in MEASURE_SRC.rglob("*.py")]
    reached_via_synth = False
    offenders: dict[str, list[str]] = {}

    while queue:
        path = queue.pop()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        source = path.read_text(encoding="utf-8")
        hits = _forbidden_hit(source, _NETWORK_LIBS)
        if hits:
            offenders[str(path.relative_to(REPO_ROOT))] = hits
        for dotted in _imports(source, package=_package(path)):
            if not dotted.startswith("gnd"):
                continue
            target = _module_path(dotted)
            if target is not None and target not in seen:
                if "synth" in target.relative_to(GND_SRC).parts:
                    reached_via_synth = True
                queue.append(target)

    assert not offenders, (
        f"a network library is reachable from the metrics lane: {offenders}. An "
        f"unpoliced synth network import would enter measure/'s closure and be "
        f"caught by neither the measure/-scoped scan nor the D-20 client scan."
    )
    assert reached_via_synth, (
        "the closure scan never reached src/gnd/synth/ — the very module the "
        "Claude-MEDIUM caveat is about. The scan is not exercising its purpose; "
        "check that gnd.measure still imports the synth provenance sidecars."
    )


# --------------------------------------------------------------------------- #
# scan 4 — the extraction-lane network-library CLOSURE scan (R-04', A4)
# --------------------------------------------------------------------------- #


def test_no_network_library_is_reachable_from_the_extraction_lane() -> None:
    """Walk the extraction lane's transitive import closure and assert no
    module in it imports a network library.

    A NEW, separately-named scan rooted at ``src/gnd/extract/`` (A4): scan 1
    is measure/-scoped and its docstring forbids re-scoping it tree-wide, scan
    2 matches provider CLIENTS only, and scan 3's closure is rooted at
    ``gnd.measure`` — so ``httpx`` imported by the new extraction lane was
    caught by NONE of them (RESEARCH P-5's measured gap). This scan mirrors
    scan 3's walk with its own root list, which plan 04 extends with the
    fidelity lane.

    Mutation check (recorded): adding ``import urllib.request`` to
    ``src/gnd/extract/refscheme.py`` reds THIS scan while scans 1-3 stay
    green — the exact gap P-5 measured.

    Self-check: the walk must reach ``src/gnd/popvalidate.py`` — the module
    the lane genuinely imports (refscheme's path 1 delegates its reference
    walk there). A closure walk that never leaves its root is not exercising
    its purpose (G-3).
    """
    seen: set[Path] = set()
    queue: list[Path] = [
        path for root in EXTRACTION_LANE_ROOTS for path in root.rglob("*.py")
    ]
    assert queue, "the extraction lane has no modules — the scan root is wrong"
    reached_via_popvalidate = False
    offenders: dict[str, list[str]] = {}

    while queue:
        path = queue.pop()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        source = path.read_text(encoding="utf-8")
        hits = _forbidden_hit(source, _NETWORK_LIBS)
        if hits:
            offenders[str(path.relative_to(REPO_ROOT))] = hits
        for dotted in _imports(source, package=_package(path)):
            if not dotted.startswith("gnd"):
                continue
            target = _module_path(dotted)
            if target is not None and target not in seen:
                if target.name == "popvalidate.py":
                    reached_via_popvalidate = True
                queue.append(target)

    assert not offenders, (
        f"a network library is reachable from the extraction lane: {offenders}. "
        f"The lane derives and validates OFFLINE (R-04'''); the executing agent "
        f"running the skill is the only place a model is ever called."
    )
    assert reached_via_popvalidate, (
        "the closure scan never reached src/gnd/popvalidate.py — the module "
        "the extraction lane genuinely imports. The scan is not exercising "
        "its purpose; check that gnd.extract.refscheme still delegates its "
        "reference walk to popvalidate."
    )


# --------------------------------------------------------------------------- #
# scan 5 — the generation-lane network-library CLOSURE scan (plan 03-01)
# --------------------------------------------------------------------------- #


def test_no_network_library_is_reachable_from_the_generation_lane() -> None:
    """Walk the generation lane's transitive import closure and assert no module
    in it imports a network library.

    A FIFTH, separately-named scan rooted at ``GENERATION_LANE_ROOTS``. Scan 1 is
    ``measure/``-scoped and its docstring forbids re-scoping it tree-wide, scan 2
    matches provider CLIENTS only, scan 3's closure is rooted at ``gnd.measure``,
    and scan 4's roots are the extraction/fidelity lanes — so ``httpx`` imported
    by ``src/gnd/exp/`` would be caught by NONE of them. Scans 1-4 keep their
    owner-decided scopes and are not touched (R-04').

    Why the generation lane needs its own offline guarantee: an experiment's
    conclusions and a conformance verdict are computed from committed artifacts.
    A network call anywhere in that closure would mean a recorded conclusion
    depended on something no reviewer can reproduce from the repository.

    Mutation check (recorded): adding ``import urllib.request`` to
    ``src/gnd/exp/spec.py`` reds THIS scan while scans 1-4 stay green. Plan
    03-03 recorded the same mutation against ``src/gnd/codegen/emit.py``.

    Self-check: the walk must LEAVE its root and reach ``src/gnd/model/`` — the
    module the lane genuinely imports (``ValidationIssue`` and the untrusted-YAML
    event budget). A closure walk that never leaves its root is a scan over one
    directory wearing a closure's name (G-3).

    Second self-check (plan 03-03): EVERY root must exist. ``rglob`` over a
    missing directory yields nothing and raises nothing, so a renamed or
    not-yet-created package would silently drop out of the scan while the
    aggregate ``queue`` stayed non-empty from its siblings — a guard that keeps
    reporting green over exactly the lane it stopped covering.
    """
    for root in GENERATION_LANE_ROOTS:
        assert root.is_dir(), (
            f"scan-5 root {root} does not exist; rglob over a missing directory "
            f"is silent, so this lane would be dropped from the closure walk "
            f"without any test going red"
        )
    seen: set[Path] = set()
    queue: list[Path] = [
        path for root in GENERATION_LANE_ROOTS for path in root.rglob("*.py")
    ]
    assert queue, "the generation lane has no modules — the scan root is wrong"
    reached_outside_the_roots = False
    offenders: dict[str, list[str]] = {}

    while queue:
        path = queue.pop()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        source = path.read_text(encoding="utf-8")
        hits = _forbidden_hit(source, _NETWORK_LIBS)
        if hits:
            offenders[str(path.relative_to(REPO_ROOT))] = hits
        for dotted in _imports(source, package=_package(path)):
            if not dotted.startswith("gnd"):
                continue
            target = _module_path(dotted)
            if target is not None and target not in seen:
                if not any(root in target.parents for root in GENERATION_LANE_ROOTS):
                    reached_outside_the_roots = True
                queue.append(target)

    assert not offenders, (
        f"a network library is reachable from the generation lane: {offenders}. "
        f"Codegen and the experiment primitive derive from COMMITTED artifacts; "
        f"a live call in this closure makes a recorded conclusion irreproducible."
    )
    assert {GND_SRC / "model" / name for name in ("__init__.py", "_validation.py", "_operations.py")} <= seen, (
        "the closure scan never reached src/gnd/model/ — the module the "
        "generation lane genuinely imports. The scan is not exercising its "
        "purpose; check that gnd.exp still sources ValidationIssue from gnd.model."
    )
    assert reached_outside_the_roots, (
        "the closure walk never left GENERATION_LANE_ROOTS — a scan over one "
        "directory is not a closure scan, and would report green over exactly "
        "the transitive import it was written to catch."
    )
    assert (GND_SRC / "declared_adapter.py") not in seen, (
        "the deterministic generation closure reached the live declared-adapter edge"
    )


def test_g01_g04_declared_network_edge_has_one_module_home() -> None:
    declared = GND_SRC / "declared_adapter.py"
    source = declared.read_text(encoding="utf-8")
    assert "asyncio.open_connection" in source
    offenders = []
    for path in sorted(GND_SRC.rglob("*.py")):
        if path != declared and "asyncio.open_connection" in path.read_text(encoding="utf-8"):
            offenders.append(str(path.relative_to(REPO_ROOT)))
    assert offenders == []
    for path in sorted(EXP_SRC.rglob("*.py")):
        assert "gnd.declared_adapter" not in path.read_text(encoding="utf-8")


def test_model_evolve_skill_is_offline_and_preserves_write_authority() -> None:
    """Both packaged workflow resources remain local, staged, and non-regenerative."""

    documents: dict[str, str] = {}
    for path in MODEL_EVOLVE_SKILL_FILES:
        assert path.is_file(), f"missing packaged evolution resource: {path}"
        documents[path.name] = path.read_text(encoding="utf-8")
    combined = "\n".join(documents.values())
    lowered = combined.lower()

    assert "http://" not in lowered and "https://" not in lowered
    # Prose is not Python source. Check explicit import lines in the resource;
    # Python-source guards still use the strict AST parser without fallback.
    imports = '\n'.join(re.findall(r'^\s*((?:from \S+ import|import) [^\n]+)$', combined, re.MULTILINE))
    assert not _forbidden_hit(imports, _PROVIDER_CLIENTS + _NETWORK_LIBS)
    assert "gnd evolve preview" in lowered
    assert "gnd evolve apply" in lowered
    assert "gnd evolve finalize" in lowered
    for boundary in (
        "no code generation",
        "no automatic repair",
        "no implicit rollback",
        "no continuous synchronization",
        "no global registry",
    ):
        assert boundary in lowered


def test_public_evolution_handlers_are_thin_offline_service_delegates() -> None:
    """The CLI may route files and render claims, never become another proposer."""

    from gnd import cli

    handlers = (
        cli._cmd_evolve_preview,
        cli._cmd_evolve_apply,
        cli._cmd_evolve_finalize,
    )
    source = "\n".join(inspect.getsource(handler) for handler in handlers)
    assert "EvolutionService" in source
    for method in (".preview(", ".apply(", ".finalize("):
        assert method in source
    assert not _forbidden_hit(source, _PROVIDER_CLIENTS + _NETWORK_LIBS)
    for forbidden in (
        "_cmd_codegen",
        "gnd.codegen",
        "subprocess",
        "--provider",
        "--model-id",
        "--api-key",
    ):
        assert forbidden not in source
    assert not hasattr(cli, "parser"), "the shipped CLI must not grow an exported parser() API"


# --------------------------------------------------------------------------- #
# a generated corpus for the C6 and pinning tests
# --------------------------------------------------------------------------- #


@pytest.fixture
def corpus(tmp_path: Path) -> Path:
    """A tiny reproducible conforming corpus, generated with a fixed seed."""
    out = tmp_path / "corpus"
    code = main(
        ["synth", str(MODEL), "--out", str(out), "--seed", "7", "--seeds", "3", "--format", "json"]
    )
    assert code == 0, "generating the corpus failed"
    return out


def _first_population(corpus: Path) -> tuple[Path, Path]:
    index = json.loads((corpus / "index.json").read_text(encoding="utf-8"))
    entry = index["populations"][0]
    # index.json entries are CORPUS-ROOT-RELATIVE (CR-01): joining them to the
    # corpus root is the only resolution `gnd measure` performs.
    pop = corpus / entry["population"]
    sidecar = pop.with_suffix(".meta.json")
    return pop, sidecar


def _measure_payload(corpus: Path, tmp_path: Path) -> dict:
    out = tmp_path / "payload.json"
    assert main(["measure", str(MODEL), "--populations", str(corpus), "--format", "json", "--out", str(out)]) == 0
    return json.loads(out.read_text(encoding="utf-8"))


def test_measurement_bytes_ignore_absolute_vs_relative_invocation_paths(
    corpus: Path, tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(REPO_ROOT)
    # The detached-checkout failure reproduced at eaa672a when the imported
    # package and the invoked checkout had different roots. Simulate that split
    # directly so this guard can fail without depending on one machine's venv.
    monkeypatch.setattr(
        measure_report,
        "__file__",
        str(tmp_path / "installed" / "gnd" / "measure" / "report.py"),
    )
    absolute_out = tmp_path / "absolute.json"
    relative_out = tmp_path / "relative.json"

    assert main(
        [
            "measure",
            str(MODEL),
            "--populations",
            str(corpus),
            "--format",
            "json",
            "--out",
            str(absolute_out),
        ]
    ) == 0
    assert main(
        [
            "measure",
            os.path.relpath(MODEL, REPO_ROOT),
            "--populations",
            os.path.relpath(corpus, REPO_ROOT),
            "--format",
            "json",
            "--out",
            str(relative_out),
        ]
    ) == 0

    assert relative_out.read_bytes() == absolute_out.read_bytes()
    payload = json.loads(relative_out.read_text(encoding="utf-8"))
    assert payload["model"] == MODEL.relative_to(REPO_ROOT).as_posix()


@pytest.mark.parametrize(
    "malformed",
    [
        None,
        [],
        {"populations": "not-an-array", "not_derivable": []},
        {
            "populations": [
                {
                    "sidecar": "case.meta.json",
                    "seed": 1,
                    "band": 0,
                    "class": "conforming",
                    "case_kind": "conforming",
                }
            ],
            "not_derivable": [],
        },
        {
            "populations": [
                {
                    "population": "case.json",
                    "sidecar": "case.meta.json",
                    "seed": "one",
                    "band": 0,
                    "class": "conforming",
                    "case_kind": "conforming",
                    "surprise": True,
                }
            ],
            "not_derivable": [],
        },
    ],
    ids=("scalar", "list", "non-list-populations", "missing-field", "wrong-and-extra"),
)
def test_measure_rejects_a_malformed_closed_index(
    corpus: Path, malformed: object
) -> None:
    (corpus / "index.json").write_text(json.dumps(malformed), encoding="utf-8")

    code = main(["measure", str(MODEL), "--populations", str(corpus), "--format", "json"])

    assert code == 3, "malformed corpus metadata must not masquerade as alethic exit 1"


@pytest.mark.parametrize("duplicate_field", ["population", "sidecar"])
def test_measure_rejects_duplicate_normalized_index_paths_without_touching_artifacts(
    corpus: Path, duplicate_field: str
) -> None:
    index_path = corpus / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    original_artifacts = {
        path.relative_to(corpus): path.read_bytes()
        for path in corpus.rglob("*")
        if path.is_file() and path != index_path
    }
    duplicate = dict(index["populations"][1])
    duplicate[duplicate_field] = index["populations"][0][duplicate_field]
    index["populations"].append(duplicate)
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")

    code = main(["measure", str(MODEL), "--populations", str(corpus), "--format", "json"])

    assert code == 3
    assert {
        path.relative_to(corpus): path.read_bytes()
        for path in corpus.rglob("*")
        if path.is_file() and path != index_path
    } == original_artifacts


@pytest.mark.parametrize(
    ("field", "fabricated"),
    [
        ("seed", 999),
        ("band", 0),
        ("class", "boundary"),
        ("case_kind", "boundary"),
        ("operator", "fabricated-operator"),
        ("boundary_side", "fabricated-side"),
        ("epsilon", "fabricated-epsilon"),
        ("target", "constraints[999]"),
        ("predicted_verdict", "unchecked"),
        ("violates_target", "constraints[999]"),
        ("violates", ["constraints[999]"]),
        ("isolating", True),
        ("isolation_verified", True),
        ("baseline_seed", 999),
    ],
)
def test_measure_rejects_unbound_index_metadata(
    corpus: Path, field: str, fabricated: object
) -> None:
    index_path = corpus / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["populations"][0][field] = fabricated
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")

    assert main(["measure", str(MODEL), "--populations", str(corpus)]) == 3


def test_measure_rejects_unbound_not_derivable_metadata(corpus: Path) -> None:
    index_path = corpus / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["not_derivable"] = [
        {
            "constraint_ref": "constraints[999]",
            "family": "value",
            "operator": "fabricated-operator",
            "mechanism": "fabricated-mechanism",
        }
    ]
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")

    assert main(["measure", str(MODEL), "--populations", str(corpus)]) == 3


# --------------------------------------------------------------------------- #
# the payload validates against the vendored schema, and carries no accuracy
# --------------------------------------------------------------------------- #


def test_payload_validates_against_the_vendored_schema(corpus: Path, tmp_path: Path) -> None:
    from jsonschema import Draft202012Validator

    from gnd.measure.report import load_measurement_schema

    schema = load_measurement_schema()
    Draft202012Validator.check_schema(schema)
    payload = _measure_payload(corpus, tmp_path)
    Draft202012Validator(schema).validate(payload)
    # The partition invariant holds on every per_constraint row, checkable by
    # summing the six counters printed in the payload.
    for row in payload["per_constraint"]:
        assert sum(row["cells"].values()) == row["n"]


def test_payload_carries_no_aggregate_accuracy_number(corpus: Path, tmp_path: Path) -> None:
    """D-01 forbids a blended accuracy figure; the schema is closed
    (additionalProperties false), so no field can smuggle one in. Confirm the
    obvious names are absent and lanes.llm reads not-applicable-phase-2."""
    payload = _measure_payload(corpus, tmp_path)
    flat = json.dumps(payload).lower()
    for forbidden in ("accuracy", "overall_rate", "verifier_accuracy", "blended"):
        assert forbidden not in flat, f"the payload leaked an aggregate figure: {forbidden}"
    assert payload["lanes"]["llm"] == "not-applicable-phase-2"
    assert payload["lanes"]["deterministic"] == "run"


def test_evidence_excerpt_names_a_corpus_population_and_matches_check(
    corpus: Path, tmp_path: Path
) -> None:
    """Every per_constraint row's D-22 evidence names a population present in
    corpus[], and the excerpt's verdict matches that population's actual check
    output for that constraint (spot-asserted for one row).

    The published path is CORPUS-ROOT-RELATIVE (F-05), so a reader resolves it
    against the corpus they were given — which is the point: the payload names
    the population without naming the machine it was measured on.
    """
    from gnd.checker import check
    from gnd.model import load_model
    from gnd.population import load_population

    payload = _measure_payload(corpus, tmp_path)
    corpus_paths = {entry["path"] for entry in payload["corpus"]}
    for row in payload["per_constraint"]:
        assert row["evidence"]["population"] in corpus_paths
        assert not Path(row["evidence"]["population"]).is_absolute()

    row = payload["per_constraint"][0]
    evidence = row["evidence"]
    model = load_model(MODEL)
    population = load_population(str(corpus / evidence["population"]), model=model)
    report = check(model, population)
    actual = next(v for v in report.verdicts if v.constraint_ref == row["constraint_ref"])
    assert actual.verdict == evidence["verdict"]["verdict"]
    assert actual.message == evidence["verdict"]["message"]


def test_text_render_puts_coverage_before_rates(corpus: Path, tmp_path: Path) -> None:
    """The text form renders coverage before the rates and n beside them."""
    from gnd.measure.report import render_measurement

    payload = _measure_payload(corpus, tmp_path)
    text = render_measurement(payload)
    # For the first constraint block, coverage appears before false_pass.
    cov_index = text.index("coverage=")
    fp_index = text.index("false_pass=")
    assert cov_index < fp_index


# --------------------------------------------------------------------------- #
# C6 — the binding is checked, not trusted
# --------------------------------------------------------------------------- #


def test_a_stale_population_exits_3(corpus: Path, tmp_path: Path) -> None:
    """A population edited after emission (its bytes no longer match the sidecar's
    population_sha256) exits 3 at measure time, before scoring."""
    pop, _ = _first_population(corpus)
    pop.write_text(pop.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    code = main(["measure", str(MODEL), "--populations", str(corpus), "--format", "json"])
    assert code == 3


def test_a_swapped_sidecar_exits_3(corpus: Path) -> None:
    """A sidecar swapped next to a DIFFERENT population (its `population` field no
    longer names this file) exits 3."""
    index = json.loads((corpus / "index.json").read_text(encoding="utf-8"))
    first = (corpus / index["populations"][0]["population"]).with_suffix(".meta.json")
    second = (corpus / index["populations"][1]["population"]).with_suffix(".meta.json")
    # Overwrite the first sidecar with the second's content — it now names the
    # wrong population.
    first.write_text(second.read_text(encoding="utf-8"), encoding="utf-8")
    code = main(["measure", str(MODEL), "--populations", str(corpus), "--format", "json"])
    assert code == 3


def test_a_wrong_model_sidecar_exits_3(corpus: Path) -> None:
    """A sidecar whose recorded model_digest does not match the model measured
    against exits 3 — a wrong-model sidecar cannot silently corrupt every rate."""
    _, sidecar_path = _first_population(corpus)
    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    sidecar["model_digest"] = "deadbeef" * 8
    sidecar_path.write_text(json.dumps(sidecar, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    code = main(["measure", str(MODEL), "--populations", str(corpus), "--format", "json"])
    assert code == 3


def test_a_sidecar_claiming_a_violation_passes_correctly_exits_3(
    corpus: Path, capsys
) -> None:
    """CR-03, end to end: a hand-edited `{violated, pass}` expectation is REFUSED.

    Reachable in principle without hand editing — the conforming class composed
    ground truth from the witness and the expected verdict from the checker, and
    the convergence gate that would catch the contradiction is restricted to
    alethic constraints — and `classify` used to score it `correct` because the
    observation happened to equal the expectation. It is an ill-formed sidecar,
    so it lands in band 3 beside the other C6 binding failures, never in a rate.
    """
    _, sidecar_path = _first_population(corpus)
    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    ref = next(iter(sidecar["expectations"]))
    sidecar["expectations"][ref] = {
        "ground_truth": "violated", "expected_verdict": "pass", "reason": None
    }
    sidecar_path.write_text(json.dumps(sidecar, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # Re-bind population_sha256 so the C6 digest check passes and the refusal
    # under test is the SCORING one, not the binding one.
    code = main(["measure", str(MODEL), "--populations", str(corpus), "--format", "json"])
    assert code == 3
    assert "inconsistent expectation" in capsys.readouterr().out


# --------------------------------------------------------------------------- #
# WR-02 — index.json is a manifest, and it is reconciled and hashed
# --------------------------------------------------------------------------- #


def test_a_pruned_index_is_refused_rather_than_measured_on_a_narrower_denominator(
    corpus: Path,
) -> None:
    """WR-02: dropping entries from index.json quietly narrows every rate.

    The measured set is whatever the index lists, the index is covered by no
    digest, and nothing compared it against the files actually present — so
    deleting entries published the same ``false_pass_rate 0.0`` on a smaller
    denominator and exited 0. T-02-25's claim that ``corpus[]`` enumerates the
    committed tree so an unexplained file is visible was not what the code did.
    """
    index_path = corpus / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    assert len(index["populations"]) > 1
    dropped = index["populations"].pop()
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    code = main(["measure", str(MODEL), "--populations", str(corpus), "--format", "json"])
    assert code == 3, "a pruned index still published rates on a reduced denominator"
    assert Path(dropped["population"]).name  # the file is still on disk, hence "unlisted"


def test_a_quarantined_case_is_not_treated_as_an_unlisted_population(corpus: Path) -> None:
    """The other half: quarantine is RETAINED outside the corpus by design (C1),
    so its sidecar must not trip the reconciliation."""
    quarantine = corpus / "quarantine"
    quarantine.mkdir(parents=True, exist_ok=True)
    _pop, sidecar = _first_population(corpus)
    (quarantine / sidecar.name).write_text(sidecar.read_text(encoding="utf-8"), encoding="utf-8")

    assert main(["measure", str(MODEL), "--populations", str(corpus), "--format", "json"]) == 0


def test_the_payload_records_the_index_digest(corpus: Path, tmp_path: Path) -> None:
    """WR-02 / IN-02: the manifest that decides what was measured, and that feeds
    three published counters, is inside the pinning trail."""
    payload = _measure_payload(corpus, tmp_path)
    expected = hashlib.sha256((corpus / "index.json").read_bytes()).hexdigest()
    assert payload["manifest"] == {"path": "index.json", "sha256": expected}


def test_a_corpus_spanning_two_pool_digests_is_refused(corpus: Path) -> None:
    """WR-02: ``pool_source`` is a LABEL, so checking it alone let a payload span
    two distinct pools while reading as one — which ``_merge_index`` makes easy,
    since it unions entries across invocations."""
    _pop, sidecar_path = _first_population(corpus)
    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    sidecar["pool_sha256"] = "f" * 64
    sidecar_path.write_text(json.dumps(sidecar, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # The C6 pool-digest recompute catches this one first (exit 3), so assert the
    # report-layer refusal directly on the same shape.
    from gnd.checker import check as real_check
    from gnd.measure.report import (
        MeasuredPopulation,
        MixedCorpusError,
        build_measurement_report,
    )
    from gnd.model import load_model
    from gnd.population import load_population
    from gnd.synth.provenance import read_sidecar

    model = load_model(str(MODEL))
    measured = []

    index = json.loads((corpus / "index.json").read_text(encoding="utf-8"))
    for offset, entry in enumerate(index["populations"][:2]):
        population_path = corpus / entry["population"]
        meta = population_path.with_suffix(".meta.json")
        card = read_sidecar(meta, verify_population_hash=False)
        card = card.model_copy(update={"pool_sha256": f"{offset}" * 64})
        measured.append(
            MeasuredPopulation(
                population_path=str(population_path),
                population_sha256=card.population_sha256,
                sidecar_path=str(meta),
                sidecar_sha256="x",
                sidecar=card,
                report=real_check(model, load_population(str(population_path), model=model)),
            )
        )
    with pytest.raises(MixedCorpusError, match="pool digest"):
        build_measurement_report(model, str(MODEL), measured, gnd_version="test")


def test_a_constraint_with_no_verdict_anywhere_is_refused(corpus: Path, monkeypatch) -> None:
    """WR-01: a constraint the checker never emits a verdict for cannot vanish.

    Observations are collected by walking ``report.verdicts``, so a constraint
    with no verdict produced no ``per_constraint`` row and left the measurement
    with no signal at all — while ``coverage_fraction`` (computed from sidecars,
    not verdicts) still read 1.0 and the run exited 0. The partition invariant
    cannot catch it: it guards ``sum(cells) == n`` WITHIN a row, and a missing
    constraint has no row.

    Reproduced exactly as the reviewer did — drop every verdict whose ref ends
    ``constraints[0]``.
    """
    from gnd.checker import CheckReport
    from gnd.checker import check as real_check

    def check_dropping_constraint_zero(model, population):
        report = real_check(model, population)
        return CheckReport(
            verdicts=[v for v in report.verdicts if not v.constraint_ref.endswith("constraints[0]")],
            coverage=report.coverage,
        )

    monkeypatch.setattr(patched_service, "check", check_dropping_constraint_zero)
    code = main(["measure", str(MODEL), "--populations", str(corpus), "--format", "json"])
    assert code == 70, "an unmeasured constraint left every rate silently"


def test_a_constraint_that_vanishes_from_SOME_populations_is_refused(
    corpus: Path, monkeypatch
) -> None:
    """F-4: the WR-01 reconciliation's missing half.

    ``declared - scored`` is SET-based, so a constraint scored on some
    populations and not others is invisible to it — and the partition invariant
    is no help either, because 36 observations partition perfectly into 36
    cells. The verifier reproduced it on the ring corpus: the row went
    ``n=72 -> n=36``, every rate still read 0.0, ``coverage_fraction`` still read
    1.0, and the run still exited 0. Half the evidence gone under an unchanged
    number.

    Dropping the verdict on every SECOND population, so the constraint keeps a
    row (WR-01 stays green) on half the census.
    """
    from gnd.checker import CheckReport
    from gnd.checker import check as real_check

    seen: dict[str, int] = {"n": 0}

    def check_dropping_constraint_zero_on_alternate_populations(model, population):
        report = real_check(model, population)
        seen["n"] += 1
        if seen["n"] % 2:
            return report
        return CheckReport(
            verdicts=[v for v in report.verdicts if not v.constraint_ref.endswith("constraints[0]")],
            coverage=report.coverage,
        )

    monkeypatch.setattr(patched_service, "check", check_dropping_constraint_zero_on_alternate_populations)
    code = main(["measure", str(MODEL), "--populations", str(corpus), "--format", "json"])
    assert code == 70, "a rate over half the evidence reads exactly like a rate over all of it"


def test_the_census_invariant_holds_on_the_real_corpus(corpus: Path) -> None:
    """The control on F-4's guard: with the real checker EVERY row's ``n`` equals
    the population count, so the guard cannot be satisfied by a report that
    counts nothing.

    This is the invariant 02-VERIFICATION found holding on all four committed
    payloads and asserted nowhere.
    """
    payload = _measure_payload(corpus, Path(corpus).parent)
    population_count = len(payload["corpus"])
    assert population_count > 1
    assert {row["n"] for row in payload["per_constraint"]} == {population_count}


def test_the_reconciliation_is_against_the_model_not_the_corpus(corpus: Path) -> None:
    """The control: with the real checker, every declared constraint has a row.

    Without this the guard above could be satisfied by a report that never
    reconciles anything.
    """
    from gnd.model import load_model
    from gnd.synth.assemble import _constraint_iter_with_ref

    payload = _measure_payload(corpus, Path(corpus).parent)
    declared = {ref for ref, _c, _ft in _constraint_iter_with_ref(load_model(str(MODEL)))}
    assert {row["constraint_ref"] for row in payload["per_constraint"]} == declared


# --------------------------------------------------------------------------- #
# publication pinning — byte-for-byte re-measure, and a perturbation is seen
# --------------------------------------------------------------------------- #


def test_two_measures_over_one_corpus_are_byte_identical(corpus: Path, tmp_path: Path) -> None:
    """The owner's pinning promise made mechanical: no timestamp, canonical key
    order, sorted lists — so two runs agree to the byte."""
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    assert main(["measure", str(MODEL), "--populations", str(corpus), "--format", "json", "--out", str(a)]) == 0
    assert main(["measure", str(MODEL), "--populations", str(corpus), "--format", "json", "--out", str(b)]) == 0
    assert a.read_bytes() == b.read_bytes()
    # And no timestamp field leaked into the payload.
    payload = json.loads(a.read_text(encoding="utf-8"))
    assert "generated_at" not in payload
    assert "timestamp" not in json.dumps(payload)


def test_a_perturbed_population_changes_the_payload(corpus: Path, tmp_path: Path) -> None:
    """Perturbing one population (and re-binding its sidecar so C6 still passes)
    changes a corpus[] hash, hence the payload — the pinning trail SEES its
    inputs, so the byte-for-byte promise is not satisfied by a payload that
    ignores them."""
    before = tmp_path / "before.json"
    assert main(["measure", str(MODEL), "--populations", str(corpus), "--format", "json", "--out", str(before)]) == 0

    pop, sidecar_path = _first_population(corpus)
    # Reformat the population bytes (different whitespace, same structure/verdicts),
    # then re-bind the sidecar's population_sha256 so the C6 check still passes.
    doc = json.loads(pop.read_text(encoding="utf-8"))
    pop.write_text(json.dumps(doc, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
    new_sha = hashlib.sha256(pop.read_bytes()).hexdigest()
    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    sidecar["population_sha256"] = new_sha
    sidecar_path.write_text(json.dumps(sidecar, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    after = tmp_path / "after.json"
    assert main(["measure", str(MODEL), "--populations", str(corpus), "--format", "json", "--out", str(after)]) == 0
    assert before.read_bytes() != after.read_bytes(), (
        "a perturbed population did not change the payload — the corpus hashes do "
        "not see their inputs, so the byte-for-byte promise is hollow."
    )


# --------------------------------------------------------------------------- #
# the exit-code allocation is disjoint, with 5 and 6 in place and 7-9 headroom
# --------------------------------------------------------------------------- #


def test_the_allocated_exit_codes_are_disjoint_with_seven_to_nine_unallocated() -> None:
    """5 and 6 are allocated; 7, 8 and 9 remain unallocated headroom.

    6 carries TWO context-specific names — EXIT_QUARANTINE (generation layer) and
    EXIT_CHECKER_DEFECT (measurement layer) — for ONE meaning: "the checker
    disagreed with independent ground truth". Same value, same meaning, so the
    space is not double-allocated. 65/66 belong to the bundled fallback validator
    (EX_DATAERR / EX_NOINPUT).
    """
    from gnd import cli

    assert cli.EXIT_QUARANTINE == cli.EXIT_CHECKER_DEFECT == 6, (
        "the two names for the checker-defect signal must share the value 6"
    )

    # The original band and lifecycle subset, mapped to a single
    # MEANING each. 6 appears once (its two names share the meaning).
    allocated = {
        0: "band: accepted",
        1: "band: violated",
        2: "band: inadequate",
        3: "band: ill-formed",
        4: "band: indeterminate",
        cli.EXIT_GENERATOR: "generator invariant failed",
        cli.EXIT_CHECKER_DEFECT: "checker disagreed with ground truth",
        cli.EXIT_DRIFT: "assets drift",
        cli.EXIT_COLLISION: "unmanaged file blocked a write",
        cli.EXIT_NO_INSTALL: "no install manifest",
        cli.EXIT_USAGE: "usage error",
        65: "fallback: EX_DATAERR",
        66: "fallback: EX_NOINPUT",
        cli.EXIT_INTERNAL: "internal error",
        cli.EXIT_IO: "IO error",
    }
    assert set(allocated) == {0, 1, 2, 3, 4, 5, 6, 10, 11, 12, 64, 65, 66, 70, 74}
    # No value carries two DIFFERENT meanings (the dict keys are values, so this
    # is a count check: 15 distinct meanings over 15 distinct values).
    assert len(set(allocated.values())) == len(allocated)
    for headroom in (7, 8, 9):
        assert headroom not in allocated, f"{headroom} must remain unallocated headroom"
