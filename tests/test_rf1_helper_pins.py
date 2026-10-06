"""RF1 lane L-HELP: every helper-family site pinned per variant (spec 6.4).

Each site is called through its own signature on the shared inputs in
tests/fixtures/rf1-pins/cases.json, and the golden records the output or the
exception per input. Sites that cannot be called directly are listed in
PINNED_VIA with the node that pins them through a caller.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from pathlib import Path

import pytest
from support.rf1_pins import build, inputs, load_cases, observe, raised, scrub
from support.rf7_pins import assert_golden

from gnd import (
    architecture,
    artifacts,
    assurance,
    assurance_evidence,
    assurance_inheritance,
    cli,
    coverage,
    diff,
    install,
    judgments,
    model,
    model_verbalization,
    population,
    popvalidate,
    proof_bridge,
    references,
    transition,
)
from gnd.codegen import emit as codegen_emit
from gnd.codegen import manifest as codegen_manifest
from gnd.conformance import currency, structural
from gnd.conformance import report as conformance_report
from gnd.evolve import models as evolve_models
from gnd.evolve import service as evolve_service
from gnd.exp import (
    adapter_policy,
    conclusions,
    junit,
    session_contract,
    session_eval,
    session_store,
    spec,
    tests_runner,
)
from gnd.export import pyrel_runtime, souffle
from gnd.extract import anchors
from gnd.extract import manifest as extract_manifest
from gnd.fidelity import match as fidelity_match
from gnd.fidelity import report as fidelity_report
from gnd.measure import promote, score
from gnd.measure import report as measure_report
from gnd.recovery import inventory, verify
from gnd.review import request, runner
from gnd.synth import assemble, poolfile, provenance, values

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / ".gnd-planning/milestones/code-refactoring/evidence/metrics-RF0.json"
CASES = load_cases()

# Sites reached only through a caller: site -> the RF1 node that pins them.
PINNED_VIA = {
    "gnd.cli:canonical": "tests/test_rf1_semantic_pins.py::test_extract",
    "gnd.exp.session_store:descend": "tests/test_rf1_session_pins.py::test_session",
    "gnd.declared_adapter:reject_constant": "tests/test_rf1_helper_pins.py::test_helper[strict_json|gnd.declared_adapter:_bundle_rows]",
    "gnd.declared_adapter:reject_duplicates": "tests/test_rf1_helper_pins.py::test_helper[strict_json|gnd.declared_adapter:_bundle_rows]",
    "gnd.exp.adapter_policy:reject_constant": "tests/test_rf1_helper_pins.py::test_helper[strict_json|gnd.exp.adapter_policy:_strict_document]",
    "gnd.exp.adapter_policy:reject_duplicates": "tests/test_rf1_helper_pins.py::test_helper[strict_json|gnd.exp.adapter_policy:_strict_document]",
    "gnd.exp.session_eval:reject_constant": "tests/test_rf1_helper_pins.py::test_helper[strict_json|gnd.exp.session_eval:_strict_object]",
    "gnd.exp.session_eval:reject_duplicate_pairs": "tests/test_rf1_helper_pins.py::test_helper[strict_json|gnd.exp.session_eval:_strict_object]",
    "gnd.exp.session_store:reject_constant": "tests/test_rf1_helper_pins.py::test_helper[strict_json|gnd.exp.session_store:_strict_object_bytes]",
    "gnd.exp.session_store:reject_duplicates": "tests/test_rf1_helper_pins.py::test_helper[strict_json|gnd.exp.session_store:_strict_object_bytes]",
    "gnd.exp.session_eval:model_validate_json": "tests/test_rf1_session_pins.py::test_session",
    "gnd.exp.session_store:model_validate_json": "tests/test_rf1_session_pins.py::test_session",
    "gnd.exp.session_judgments:entry": "tests/test_rf1_session_pins.py::test_session",
    "gnd.exp.session_v7:_entry": "tests/test_rf1_session_pins.py::test_session",
}
# Sites no RF1 node can detect, owed by the phase that moves them (RF-R3).
# artifacts.directory_identity is nested in tree_sha256_from_directory; a fixed
# tree never exercises its identity-change refusal (review finding RF1-07).
OWED = {"gnd.artifacts:directory_identity": "RF4"}
# helper-families.md classifies these as trivial constructors, not a family.
NOT_A_FAMILY = {
    "gnd.exp.junit:__init__",
    "gnd.exp.tests_runner:__init__",
    "gnd.exp.session_patch:__init__",
    "gnd.json_input:__init__",
}


def _table(function: Callable, group: str, adapt: Callable = lambda f, v: f(v)) -> dict:
    return {name: observe(adapt, function, value) for name, value in inputs(group)}


def _models() -> list[tuple[str, model.Model]]:
    return [(path, model.load_model(ROOT / path)) for path in CASES["corpus"]["models"]]


def _per_model(function: Callable) -> dict:
    return {path: observe(function, loaded) for path, loaded in _models()}


def _validation_error():
    from pydantic import BaseModel, ValidationError

    class Inner(BaseModel):
        value: int

    class Outer(BaseModel):
        name: str
        inner: Inner

    try:
        Outer.model_validate({"inner": {"value": "x"}, "extra": 1})
    except ValidationError as error:
        return error
    raise AssertionError("expected a ValidationError")


def _paths(function: Callable) -> dict:
    return _table(function, "path_strings")


def _tree(base: Path) -> Path:
    root = base / "tree"
    (root / "d" / "sub").mkdir(parents=True)
    (root / "d" / "existing").write_bytes(b"old\n")
    (root / "file").write_bytes(b"file\n")
    (root / "link_to_d").symlink_to("d")
    (root / "link_file").symlink_to("file")
    return root


def _fd_result(result):
    if isinstance(result, int) and not isinstance(result, bool):
        os.close(result)
        return "<fd>"
    return result


def _scenario(tmp_path: Path, kind: str, call: Callable[[Path, str], object]) -> dict:
    observed = {}
    for index, name in enumerate(CASES["tree_scenarios"][kind]):
        root = _tree(tmp_path / f"s{index}")
        outcome = observe(lambda root=root, name=name: _fd_result(call(root, name)))
        target = root / name
        after = None
        if target.is_file() and not target.is_symlink():
            after = target.read_bytes().decode()
        observed[name] = {"outcome": outcome, "target_after": after}
    return scrub(observed, {str(tmp_path.resolve()): "<tmp>", str(tmp_path): "<tmp>"})


def _parts(name: str) -> tuple[str, ...]:
    return tuple(name.split("/"))


def _open_dir(root: Path) -> int:
    return os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))


def _with_root_fd(root: Path, call: Callable[[int], object]):
    descriptor = _open_dir(root)
    try:
        return call(descriptor)
    finally:
        os.close(descriptor)


def _stat_tuple(values) -> os.stat_result:
    return os.stat_result(tuple(values) + (0,) * (10 - len(values)))


STATS = {
    "same": ([0o40755, 11, 3, 1, 0, 0, 64, 0, 0, 5], [0o40755, 11, 3, 1, 0, 0, 64, 0, 0, 5]),
    "other-inode": ([0o40755, 11, 3, 1, 0, 0, 64, 0, 0, 5], [0o40755, 12, 3, 1, 0, 0, 64, 0, 0, 5]),
    "other-device": ([0o40755, 11, 3, 1, 0, 0, 64, 0, 0, 5], [0o40755, 11, 4, 1, 0, 0, 64, 0, 0, 5]),
}


def _pairs(function: Callable) -> dict:
    return {
        name: observe(function, _stat_tuple(left), _stat_tuple(right)) for name, (left, right) in STATS.items()
    }


def _identity(function: Callable) -> dict:
    stat = os.stat_result((0o40755, 11, 3, 1, 0, 0, 64, 1, 2, 5) + (1, 2, 5_000_000_000))
    return {"fixed": observe(function, stat)}


def _file_inputs(tmp_path: Path, function: Callable, *, expected_stat: bool = False) -> dict:
    """A FIFO is offered only to the O_NONBLOCK reader: the other readers block on it
    (RF1 implementation finding F1), and a hang cannot be pinned."""
    root = tmp_path / "files"
    root.mkdir()
    (root / "regular").write_bytes(b"gnd\n")
    (root / "empty").write_bytes(b"")
    (root / "link").symlink_to("regular")
    (root / "dir").mkdir()
    names = ["regular", "empty", "link", "dir", "missing"]
    if expected_stat and hasattr(os, "mkfifo"):
        os.mkfifo(root / "fifo")
        names.append("fifo")
    observed = {}
    for name in names:
        path = root / name
        if expected_stat:
            try:
                stat = os.lstat(path)
            except OSError as error:
                observed[name] = raised(error)
                continue
            observed[name] = observe(function, path, stat)
        else:
            observed[name] = observe(function, path)
    return scrub(observed, {str(tmp_path.resolve()): "<tmp>", str(tmp_path): "<tmp>"})


def _strict(function: Callable, *, extra: dict | None = None) -> dict:
    table = _table(function, "strict_json")
    for name, value in (extra or {}).items():
        table[name] = observe(function, value)
    return table


def _yaml_files(tmp_path: Path, function: Callable) -> dict:
    observed = {}
    for name, text in inputs("yaml"):
        path = tmp_path / f"{name}.yaml"
        path.write_text(text, encoding="utf-8")
        observed[name] = observe(function, path)
    return scrub(observed, {str(tmp_path.resolve()): "<tmp>", str(tmp_path): "<tmp>"})


def _json_file(tmp_path: Path, function: Callable) -> dict:
    observed = {}
    for name, raw in inputs("strict_json"):
        path = tmp_path / f"{name}.json"
        path.write_bytes(raw)
        observed[name] = observe(function, path)
    over = tmp_path / "over-cap.json"
    over.write_bytes(b'{"a":"' + b"x" * coverage.MAX_EVIDENCE_BYTES + b'"}')
    observed["over-cap"] = observe(function, over)
    checked = tmp_path / "check-v1.json"
    checked.write_text(json.dumps({"schema_version": 1, "verdicts": []}))
    observed["schema-version-1"] = observe(function, checked)
    return scrub(observed, {str(tmp_path.resolve()): "<tmp>", str(tmp_path): "<tmp>"})


def _content_digests() -> dict:
    observed = {}
    for model_path, population_path in CASES["corpus"]["checker_pairs"]:
        loaded = model.load_model(ROOT / model_path)
        observed[population_path] = observe(
            lambda population_path=population_path, loaded=loaded: population._content_digest(
                population.load_population(ROOT / population_path, model=loaded)
            )
        )
    return observed


def _rates(function: Callable) -> dict:
    return {name: observe(function, *value) for name, value in inputs("rates")}


OVER_CAP = b'{"a":"' + b"x" * session_eval.MAX_VERIFIER_PAYLOAD_BYTES + b'"}'


def _sites(tmp_path: Path) -> dict[str, Callable[[], object]]:
    """family|site -> a zero-argument observation producing that site's table."""
    canonical = {
        "gnd.artifacts:canonical_json_bytes": artifacts.canonical_json_bytes,
        "gnd.artifacts:canonical_json_text": artifacts.canonical_json_text,
        "gnd.assurance_inheritance:_canonical": assurance_inheritance._canonical,
        "gnd.cli:_canonical_payload": cli._canonical_payload,
        "gnd.cli:_evolve_json_bytes": cli._evolve_json_bytes,
        "gnd.codegen.emit:_canonical": codegen_emit._canonical,
        "gnd.conformance.report:canonical": conformance_report.canonical,
        "gnd.coverage:canonical_payload": coverage.canonical_payload,
        "gnd.evolve.models:_canonical_json": evolve_models._canonical_json,
        "gnd.extract.anchors:_canonical": anchors._canonical,
        "gnd.fidelity.report:canonical": fidelity_report.canonical,
        "gnd.measure.report:_canonical": measure_report._canonical,
        "gnd.model_verbalization:_canonical": model_verbalization._canonical,
        "gnd.review.request:_canonical_json": request._canonical_json,
        "gnd.synth.poolfile:_canonical_bytes": poolfile._canonical_bytes,
    }
    sites: dict[str, Callable[[], object]] = {
        f"canonical_json|{site}": (lambda f=f: _table(f, "canonical")) for site, f in canonical.items()
    }
    sites["canonical_json|gnd.artifacts:canonical_json_bytes[exact_numbers]"] = lambda: _table(
        artifacts.canonical_json_bytes, "canonical", lambda f, v: f(v, exact_numbers=True)
    )
    sites["canonical_json|gnd.proof_bridge:_canonical"] = lambda: _table(proof_bridge._canonical, "sorted_set")
    sites["canonical_json|gnd.assurance:_sorted_set"] = lambda: _table(assurance._sorted_set, "sorted_set")
    sites["canonical_json|gnd.transition:_canonical"] = lambda: _table(
        transition._canonical, "transition_canonical", lambda f, v: f(v, "$.operations")
    )

    for site, f in {
        "gnd.artifacts:sha256_hex": artifacts.sha256_hex,
        "gnd.assurance_evidence:_sha": assurance_evidence._sha,
        "gnd.diff:_digest": diff._digest,
        "gnd.export.souffle:digest": souffle.digest,
        "gnd.install:_sha256": install._sha256,
        "gnd.recovery.verify:_sha256": verify._sha256,
    }.items():
        sites[f"sha256_hex|{site}"] = lambda f=f: _table(f, "bytes")
    sites["sha256_hex|gnd.codegen.manifest:digest_text"] = lambda: _table(codegen_manifest.digest_text, "text")
    sites["sha256_hex|gnd.extract.anchors:_digest"] = lambda: _table(anchors._digest, "hex_candidates")
    sites["sha256_hex|gnd.judgments:digest"] = lambda: _table(judgments.digest, "hex_candidates")
    sites["sha256_hex|gnd.measure.promote:_digest"] = lambda: _file_inputs(tmp_path, promote._digest)
    sites["sha256_hex|gnd.population:_content_digest"] = _content_digests
    sites["sha256_hex|gnd.synth.poolfile:_sha256"] = lambda: _table(poolfile._sha256, "pool_payload")

    sites["model_digest|gnd.conformance.currency:model_digest"] = lambda: {
        path: observe(currency.model_digest, ROOT / path) for path in CASES["corpus"]["models"]
    }
    sites["model_digest|gnd.population:_model_digest"] = lambda: _per_model(population._model_digest)
    sites["model_digest|gnd.references:reference_model_digest"] = lambda: _per_model(references.reference_model_digest)
    sites["model_digest|gnd.synth.provenance:model_digest"] = lambda: _per_model(provenance.model_digest)
    sites["model_digest|gnd.transition:model_digest"] = lambda: _per_model(transition.model_digest)

    sites["file_digest|gnd.evolve.service:_tree_sha256"] = lambda: _tree_digest(tmp_path)
    sites["file_digest|gnd.evolve.service:final_record_file_sha256"] = lambda: _table(
        evolve_service.EvolutionService.final_record_file_sha256, "canonical", lambda f, v: f(None, v)
    )
    sites["file_digest|gnd.exp.tests_runner:_digest_regular_path"] = lambda: _file_inputs(
        tmp_path, tests_runner._digest_regular_path, expected_stat=True
    )
    sites["file_digest|gnd.synth.provenance:_sha256_file"] = lambda: _file_inputs(tmp_path, provenance._sha256_file)
    sites["file_digest|gnd.transition:population_file_digest"] = lambda: _file_inputs(
        tmp_path, transition.population_file_digest
    )

    sites["strict_json|gnd.coverage:read_json_document"] = lambda: _json_file(
        tmp_path, lambda p: coverage.read_json_document(p, kind="check")
    )
    sites["strict_json|gnd.exp.adapter_policy:_strict_document"] = lambda: _strict(adapter_policy._strict_document)
    sites["strict_json|gnd.exp.session_eval:_strict_object"] = lambda: _strict(
        session_eval._strict_object, extra={"over-cap": OVER_CAP}
    )
    sites["strict_json|gnd.exp.session_store:_strict_object_bytes"] = lambda: _strict(
        lambda raw: session_store._strict_object_bytes(raw, label="rf1")
    )
    sites["strict_json|gnd.review.request:_strict_json_object"] = lambda: _strict(
        lambda raw: request._strict_json_object(raw, label="rf1")
    )
    sites["strict_json|gnd.review.runner:_strict_json"] = lambda: _strict(
        lambda raw: runner._strict_json(raw, subject="rf1")
    )
    sites["strict_json|gnd.declared_adapter:_bundle_rows"] = lambda: _strict(
        lambda raw: _bundle_rows(raw.decode("utf-8", "surrogateescape"))
    )
    sites["strict_json|gnd.review.request:_reject_duplicate_object_pairs"] = lambda: {
        "unique": observe(request._reject_duplicate_object_pairs, [("a", 1), ("b", 2)]),
        "duplicate": observe(request._reject_duplicate_object_pairs, [("a", 1), ("a", 2)]),
    }

    sites["iso_datetime|gnd.popvalidate:_is_datetime"] = lambda: _table(popvalidate._is_datetime, "iso_datetime")
    sites["iso_datetime|gnd.synth.values:_parse_datetime"] = lambda: _table(
        values._parse_datetime, "iso_datetime", lambda f, v: f(v, "rf1", {})
    )

    error = _validation_error()
    sites["validation_issues|gnd.exp.conclusions:_validation_issues"] = lambda: observe(
        conclusions._validation_issues, error
    )
    sites["validation_issues|gnd.exp.spec:_validation_issues"] = lambda: observe(spec._validation_issues, error)
    sites["validation_issues|gnd.extract.manifest:_validation_issues"] = lambda: observe(
        extract_manifest._validation_issues, error, "rf1:rule"
    )
    sites["validation_issues|gnd.exp.session_contract:_pydantic_issues"] = lambda: {
        str(version): observe(session_contract._pydantic_issues, error, schema_version=version) for version in (1, 3, 8)
    }
    sites["validation_issues|gnd.exp.session_eval:_schema_issues"] = lambda: {
        "empty": observe(session_eval._schema_issues, {}),
        "wrong-types": observe(session_eval._schema_issues, {"schema_version": "x", "verdicts": 3}),
    }
    sites["validation_issues|gnd.population:_schema_issues"] = lambda: {
        "empty": observe(population._schema_issues, {}),
        "wrong-types": observe(population._schema_issues, {"model_id": 3, "facts": "x"}),
    }

    sites["yaml_guard|gnd.architecture:_preflight_yaml"] = lambda: _table(
        architecture._preflight_yaml, "yaml", lambda f, v: f(v, source="rf1.yaml")
    )
    sites["yaml_guard|gnd.architecture:_load_yaml"] = lambda: _table(
        architecture._load_yaml, "yaml", lambda f, v: f(v, source="rf1.yaml")
    )
    sites["yaml_guard|gnd.export.pyrel_runtime:_load_yaml"] = lambda: _yaml_files(tmp_path, pyrel_runtime._load_yaml)
    sites["yaml_guard|gnd.model:yaml_stream_guard_error"] = lambda: _yaml_files(tmp_path, model.yaml_stream_guard_error)
    sites["yaml_guard|gnd.recovery.inventory:_load_yaml_static"] = lambda: _table(
        inventory._load_yaml_static, "yaml"
    )

    sites["safe_filesystem|gnd.cli:_evolve_reject_unsafe_spelling"] = lambda: _paths(
        lambda v: cli._evolve_reject_unsafe_spelling(v, label="rf1")
    )
    sites["safe_filesystem|gnd.evolve.models:_unsafe_project_path"] = lambda: _paths(evolve_models._unsafe_project_path)
    sites["safe_filesystem|gnd.install:_reject_unsafe_relpath"] = lambda: _paths(
        lambda v: install._reject_unsafe_relpath(v, source="rf1")
    )
    sites["safe_filesystem|gnd.install:safe_destination"] = lambda: _safe_destination(tmp_path)
    sites["safe_filesystem|gnd.artifacts:_safe_fs_coordinate"] = lambda: _table(
        artifacts._safe_fs_coordinate, "coordinates"
    )
    sites["safe_filesystem|gnd.conformance.structural:_safe_coordinate"] = lambda: _table(
        structural._safe_coordinate, "coordinates"
    )
    sites["safe_filesystem|gnd.conformance.structural:_directory_identity"] = lambda: _identity(
        structural._directory_identity
    )
    sites["safe_filesystem|gnd.exp.junit:_same_inode"] = lambda: _pairs(junit._same_inode)
    sites["safe_filesystem|gnd.exp.tests_runner:_same_inode"] = lambda: _pairs(tests_runner._same_inode)
    sites["safe_filesystem|gnd.artifacts:_descend"] = lambda: _scenario(
        tmp_path, "descend", lambda root, name: _with_root_fd(root, lambda fd: artifacts._descend(fd, _parts(name)))
    )
    sites["safe_filesystem|gnd.install:_descend"] = lambda: _scenario(
        tmp_path, "descend", lambda root, name: install._descend(root, _parts(name), create=False)
    )
    sites["safe_filesystem|gnd.install:_descend[create]"] = lambda: _scenario(
        tmp_path, "descend", lambda root, name: install._descend(root, _parts(name), create=True)
    )
    sites["safe_filesystem|gnd.recovery.inventory:_descend"] = lambda: _scenario(
        tmp_path, "descend", lambda root, name: _with_root_fd(root, lambda fd: inventory._descend(fd, _parts(name)))
    )
    sites["safe_filesystem|gnd.artifacts:_open_root"] = lambda: _scenario(
        tmp_path, "open_root", lambda root, name: artifacts._open_root(root / name)
    )
    sites["safe_filesystem|gnd.artifacts:_write_new_file"] = lambda: _scenario(
        tmp_path, "write", lambda root, name: artifacts._write_new_file(root / name, b"new\n", root=root)
    )
    sites["safe_filesystem|gnd.exp.session_store:_write_new_file"] = lambda: _scenario(
        tmp_path, "write", lambda root, name: session_store._write_new_file(root / name, b"new\n", root=root)
    )
    sites["safe_filesystem|gnd.artifacts:_write_new_file_at"] = lambda: _scenario(
        tmp_path,
        "write",
        lambda root, name: _with_root_fd(root, lambda fd: artifacts._write_new_file_at(fd, _parts(name), b"new\n")),
    )
    sites["safe_filesystem|gnd.install:_atomic_write"] = lambda: _scenario(
        tmp_path, "write", lambda root, name: install._atomic_write(root, name, b"new\n")
    )
    sites["safe_filesystem|gnd.export.pyrel_runtime:write_new"] = lambda: _scenario(
        tmp_path, "write", lambda root, name: pyrel_runtime.write_new(root / name, "new\n")
    )

    sites["identical_candidate|gnd.fidelity.match:_rate"] = lambda: _rates(fidelity_match._rate)
    sites["identical_candidate|gnd.measure.score:_rate"] = lambda: _rates(score._rate)
    for site, f in {
        "gnd.popvalidate:_object_types_by_id": popvalidate._object_types_by_id,
        "gnd.synth.assemble:_object_types_by_id": assemble._object_types_by_id,
        "gnd.synth.poolfile:_object_types_by_id": poolfile._object_types_by_id,
        "gnd.popvalidate:_role_object_types": popvalidate._role_object_types,
        "gnd.synth.assemble:_role_object": assemble._role_object,
    }.items():
        sites[f"identical_candidate|{site}"] = lambda f=f: _per_model(f)
    return sites


def _bundle_rows(content: str):
    from gnd import declared_adapter

    return declared_adapter._bundle_rows(content)


def _tree_digest(tmp_path: Path) -> dict:
    root = tmp_path / "digest-tree"
    (root / "a" / "b").mkdir(parents=True)
    (root / "a" / "b" / "f.txt").write_bytes(b"gnd\n")
    (root / "top.txt").write_bytes(b"top\n")
    linked = tmp_path / "digest-linked"
    linked.mkdir()
    (linked / "real.txt").write_bytes(b"x\n")
    (linked / "alias.txt").symlink_to("real.txt")
    observed = {
        "plain": observe(evolve_service._tree_sha256, root),
        "relative": observe(evolve_service._tree_sha256, root, relative="a"),
        "with-symlink": observe(evolve_service._tree_sha256, linked),
        "missing": observe(evolve_service._tree_sha256, tmp_path / "absent"),
    }
    return scrub(observed, {str(tmp_path.resolve()): "<tmp>", str(tmp_path): "<tmp>"})


def _safe_destination(tmp_path: Path) -> dict:
    root = _tree(tmp_path / "dest")
    observed = {name: observe(install.safe_destination, root, value) for name, value in inputs("path_strings")}
    for name in ("link_to_d/x", "link_file", "d/existing", "file/x"):
        observed[f"tree:{name}"] = observe(install.safe_destination, root, name)
    return scrub(observed, {str(tmp_path.resolve()): "<tmp>", str(tmp_path): "<tmp>"})


def _site_ids() -> list[str]:
    return sorted(_sites(Path("/nonexistent-rf1")))


SITE_IDS = _site_ids()


@pytest.mark.parametrize("site", SITE_IDS)
def test_helper(site, tmp_path):
    observed = _sites(tmp_path)[site]()
    assert_golden("helpers", site, {"site": site, "observed": observed})


def _metric_sites() -> set[str]:
    metrics = json.loads(METRICS.read_text())
    found = set()
    for family in metrics["duplicates"]["families"]:
        found.update(site["site"].rsplit(":", 1)[0] for site in family["sites"])
    for group in metrics["duplicates"]["ast_identical"]:
        found.update(site.rsplit(":", 1)[0] for site in group["sites"])
    return found


def test_helper_coverage():
    """T-HELP-COV: every RF0 family site and identical-candidate site is pinned or routed."""
    pinned = {site.split("|", 1)[1].split("[", 1)[0] for site in SITE_IDS}
    missing = sorted(_metric_sites() - pinned - set(PINNED_VIA) - set(OWED) - NOT_A_FAMILY)
    assert missing == []
    assert len(SITE_IDS) == len(set(SITE_IDS))


def test_case_manifest_builds():
    for group, descriptors in CASES["inputs"].items():
        for name, descriptor in descriptors.items():
            build(descriptor)
            assert group and name
