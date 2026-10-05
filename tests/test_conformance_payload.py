"""The conformance payload's honest scope is a SCHEMA fact (G-08, G-15, R-13′).

The claim defended here is not "the report mentions what it did not check" —
prose in a payload is a promise, and a promise is what a CI job skips. The claim
is that ``conformance.schema.json`` makes the dishonest alternative *impossible
to represent*: ``unexamined`` is required with ``minItems: 0`` so a payload that
omitted it is invalid, ``limits`` is required with three members no edit may
remove, every assertion carries ``ran`` so a check that could not run can never
be mistaken for one that passed, and every object is closed so no verdict field
and no rate field can exist at any depth.

Two of the tests below are SCHEMA MUTATIONS rather than assertions about a
payload. That distinction is the whole point of the file: asserting that the
builder emits ``unexamined`` only restates the builder, while removing
``required`` from a copy of the schema and watching a key-less payload become
valid proves the schema is what is doing the work.

**Written to survive plan 03-06's widening without relaxation.** That plan adds
assertion #3 — a new ``assertions`` member, a new ``findings`` kind, and the
removal of the non-required limit it closes — with a stated no-bump
disposition. So every assertion here is a SUBSET or a ``contains`` claim, never
an exact set equality over the assertion ids, the finding kinds, the limits, or
the schema's required key list.
"""

from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from gnd import resolve_version
from gnd.cli import main
from gnd.codegen.emit import emit_project, write_project
from gnd.codegen.manifest import (
    INTEGRITY_LIMITS,
    CodegenManifest,
    build_manifest,
    manifest_path,
    read_manifest,
    render_manifest,
)
from gnd.conformance.architecture import ArchitectureResult, check_architecture
from gnd.conformance.currency import check_currency, model_digest
from gnd.conformance.integrity import check_integrity
from gnd.conformance.report import (
    CONFORMANCE_SCHEMA_VERSION,
    LIMITS,
    build_conformance_payload,
    canonical,
    load_conformance_schema,
)
from gnd.conformance.structural import check_structural
from gnd.model import load_model

REPO_ROOT = Path(__file__).resolve().parent.parent
FULL_VOCABULARY = REPO_ROOT / "tests" / "fixtures" / "models" / "full_vocabulary.orm.yaml"
SCHEMA_PATH = REPO_ROOT / "src" / "gnd" / "conformance.schema.json"


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #


def _project(tmp_path: Path) -> tuple[Path, Path]:
    """``(model_path, project_root)`` — a real generated project."""
    model_path = tmp_path / "model.orm.yaml"
    shutil.copyfile(FULL_VOCABULARY, model_path)
    root = tmp_path / "project"
    model = load_model(str(model_path))
    project = emit_project(model, str(model_path), skill_name=root.resolve().name)
    write_project(
        project,
        str(root),
        manifest_text=render_manifest(build_manifest(project, str(model_path))),
    )
    return model_path, root


def _payload(model_path: Path, root: Path) -> dict[str, Any]:
    """A payload from all four assertions having run.

    ``structural`` joined at plan 03-06. It is passed here rather than left to
    its ``None`` default because this helper feeds the tests that assert every
    assertion reports ``ran: true`` — a fixture that quietly omitted the third
    would make those tests pass over a payload in which the anti-tautology gate
    never ran, which is the exact reading R-13′ exists to prevent.
    """
    manifest = read_manifest(manifest_path(root))
    return build_conformance_payload(
        model_path,
        manifest,
        check_integrity(root, manifest),
        check_currency(model_path, manifest),
        structural=check_structural(
            load_model(str(model_path)), root, manifest, model_path=model_path
        ),
        architecture=check_architecture(
            load_model(str(model_path)), root, manifest, model_path=model_path
        ),
        actual_model_sha256=model_digest(model_path),
        gnd_version=resolve_version(),
    )


def _validator() -> Draft202012Validator:
    return Draft202012Validator(load_conformance_schema())


def _json_run(argv: list[str], capsys: pytest.CaptureFixture[str]) -> tuple[int, Any]:
    """Run the CLI in JSON mode and parse whatever it printed."""
    capsys.readouterr()
    code = main([*argv, "--format", "json"])
    out = capsys.readouterr().out
    return code, json.loads(out)


def _json_strings(value: Any, path: str = "$") -> list[tuple[str, str]]:
    strings: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            strings.append((f"{path}.<key>", str(key)))
            strings.extend(_json_strings(nested, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            strings.extend(_json_strings(nested, f"{path}[{index}]"))
    elif isinstance(value, str):
        strings.append((path, value))
    return strings


def _assert_operator_neutral(payload: Any, *, forbidden: tuple[str, ...]) -> None:
    leaks = [
        (path, value, marker)
        for path, value in _json_strings(payload)
        for marker in forbidden
        if marker in value
    ]
    assert not leaks, "operator coordinate leaked at " + "; ".join(
        f"{path} contains {marker!r}: {value!r}" for path, value, marker in leaks
    )


# --------------------------------------------------------------------------- #
# the schema itself
# --------------------------------------------------------------------------- #


def test_the_schema_is_a_valid_draft_2020_12_schema() -> None:
    Draft202012Validator.check_schema(load_conformance_schema())


def test_the_schema_lives_at_the_module_root_not_under_src_gnd_schema() -> None:
    """A runtime OUTPUT contract, not an interchange format (``report.py:22-28``).

    ``src/gnd/schema/`` holds the formats the gnd-orm-core skill documents
    authoring rules for; nobody authors a conformance payload by hand.
    """
    assert SCHEMA_PATH.is_file()
    assert not (REPO_ROOT / "src" / "gnd" / "schema" / "conformance.schema.json").exists()


def test_the_packaged_schema_is_byte_identical_to_the_source_copy() -> None:
    """``load_conformance_schema`` resolves through ``importlib.resources``, so
    this is the source-tree half of the installed-wheel guarantee that
    ``tests/test_distribution.py`` proves from the built artifact."""
    assert load_conformance_schema() == json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_unexamined_and_limits_are_required_at_the_top_level() -> None:
    schema = load_conformance_schema()
    assert {
        "architecture",
        "unexamined",
        "limits",
        "findings",
        "assertions",
        "error",
    } <= set(schema["required"])
    assert schema["properties"]["unexamined"]["minItems"] == 0, (
        "minItems 0 is the point: present-and-empty, never absent (G-08)"
    )


def test_no_verdict_field_and_no_rate_field_exists_at_any_depth() -> None:
    """G-15/D-01 as a structural property of the contract.

    A reviewer confirms the third payload family does not blend by reading the
    schema — every object is closed, so nothing below can be added at runtime
    either.
    """
    schema = load_conformance_schema()

    names: set[str] = set()

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "properties" and isinstance(value, dict):
                    names.update(value)
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(schema)

    # Self-check: the walk must have COLLECTED something, and something it was
    # supposed to collect. A guard over an empty set reports green forever.
    assert "unexamined" in names and len(names) > 20, (
        f"the property walk collected {len(names)} names; it is not inspecting "
        f"the schema and proves nothing"
    )

    forbidden = {
        "verdict",
        "verdicts",
        "band",
        "acceptance_ready",
        "counts",
        "outcome",
        "exit_code",
        "rate",
        "numerator",
        "denominator",
        "precision",
        "recall",
        "publishable",
        "calibration",
        "per_fact_type",
    }
    assert not (names & forbidden), (
        f"the conformance payload carries verdict- or rate-family fields "
        f"{sorted(names & forbidden)}; no GND output may carry two claim "
        f"families (G-15, D-01)"
    )


def _open_objects(schema: Any) -> list[str]:
    """Every object node that DECLARES a shape without closing it.

    ``contains`` subtrees are deliberately skipped: they are MATCHERS, not shape
    declarations — ``{"required": ["id"], "properties": {"id": {"const": …}}}``
    must match an item that carries other keys too, so closing one would make
    the required-member guard match nothing and silently stop protecting the
    limit it names.
    """
    found: list[str] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, dict):
            if node.get("type") == "object" and node.get("additionalProperties") is not False:
                found.append(path)
            for key, value in node.items():
                if key == "contains":
                    continue
                walk(value, f"{path}/{key}")
        elif isinstance(node, list):
            for index, item in enumerate(node):
                walk(item, f"{path}/{index}")

    walk(schema, "#")
    return found


def test_every_shape_declaring_object_in_the_schema_is_closed() -> None:
    """``additionalProperties: false`` everywhere a shape is declared, or the
    no-verdict/no-rate closure above is advisory rather than enforced."""
    schema = load_conformance_schema()
    assert not _open_objects(schema), (
        f"open objects in conformance.schema.json: {_open_objects(schema)}"
    )

    # Self-check: the walk must be able to FIND an open object, or it is a
    # guard that reports green over a file it never inspected properly.
    holed = copy.deepcopy(schema)
    del holed["$defs"]["finding"]["additionalProperties"]
    assert "#/$defs/finding" in _open_objects(holed), (
        "the closure walk cannot detect an opened object and proves nothing"
    )


# --------------------------------------------------------------------------- #
# the mutations that prove the schema is load-bearing
# --------------------------------------------------------------------------- #


def test_the_unexamined_requirement_is_load_bearing(tmp_path: Path) -> None:
    """MUTATION. Remove ``required`` for ``unexamined`` from a COPY of the
    schema and a payload lacking the key becomes valid — so this test pins the
    SCHEMA rather than restating the builder.

    Without this, a future edit could drop the key from ``required`` and every
    other test in this file would still pass, because the builder would keep
    emitting it right up until the day something stopped.
    """
    model_path, root = _project(tmp_path)
    payload = _payload(model_path, root)
    schema = load_conformance_schema()

    assert Draft202012Validator(schema).is_valid(payload)

    stripped = copy.deepcopy(payload)
    del stripped["unexamined"]
    assert not Draft202012Validator(schema).is_valid(stripped), (
        "a payload with no `unexamined` key validated; the requirement is "
        "decorative, and a reader could not tell 'nothing was skipped' from "
        "'the skipping was not reported'"
    )

    relaxed = copy.deepcopy(schema)
    relaxed["required"] = [key for key in relaxed["required"] if key != "unexamined"]
    assert Draft202012Validator(relaxed).is_valid(stripped), (
        "the key-less payload is invalid for some OTHER reason too, so the "
        "test above did not prove `required` is what rejected it"
    )


def test_an_empty_unexamined_list_is_valid_and_an_absent_one_is_not(
    tmp_path: Path,
) -> None:
    """G-08's exact wording: present-and-empty is a FACT, absent is a DEFECT."""
    model_path, root = _project(tmp_path)
    manifest = read_manifest(manifest_path(root))
    derived_only = CodegenManifest(
        manifest_version=manifest.manifest_version,
        gnd_version=manifest.gnd_version,
        model=manifest.model,
        files=[entry for entry in manifest.files if entry.ownership == "derived"],
    )
    payload = build_conformance_payload(
        model_path,
        derived_only,
        check_integrity(root, derived_only),
        check_currency(model_path, derived_only),
        actual_model_sha256=model_digest(model_path),
        gnd_version=resolve_version(),
    )

    assert payload["unexamined"] == [], "a derived-only project skipped something"
    assert "unexamined" in payload
    _validator().validate(payload)


def test_the_architecture_block_requirement_is_load_bearing(tmp_path: Path) -> None:
    """P-01. Removing the required block, not another rule, admits its absence."""
    model_path, root = _project(tmp_path)
    payload = _payload(model_path, root)
    schema = load_conformance_schema()

    stripped = copy.deepcopy(payload)
    del stripped["architecture"]
    assert not Draft202012Validator(schema).is_valid(stripped)

    relaxed = copy.deepcopy(schema)
    relaxed["required"] = [key for key in relaxed["required"] if key != "architecture"]
    assert Draft202012Validator(relaxed).is_valid(stripped)


def test_the_architecture_assertion_requirement_is_load_bearing(tmp_path: Path) -> None:
    """P-02. The fourth row is contains-required rather than builder convention."""
    model_path, root = _project(tmp_path)
    payload = _payload(model_path, root)
    schema = load_conformance_schema()

    stripped = copy.deepcopy(payload)
    stripped["assertions"] = [row for row in stripped["assertions"] if row["id"] != "architecture"]
    assert not Draft202012Validator(schema).is_valid(stripped)

    relaxed = copy.deepcopy(schema)
    relaxed["properties"]["assertions"]["allOf"] = [
        guard
        for guard in relaxed["properties"]["assertions"]["allOf"]
        if guard["contains"]["properties"]["id"]["const"] != "architecture"
    ]
    assert Draft202012Validator(relaxed).is_valid(stripped)


def test_a_required_limit_cannot_be_dropped_to_flatter_the_result(
    tmp_path: Path,
) -> None:
    """MUTATION. The five permanent limits are ``contains``-required, so a
    payload that quietly stopped publishing the co-edit blind spot is invalid.

    An ADDED limit needs no such protection — it only ever makes the result look
    weaker — which is why the array stays open (``fidelity.schema.json``'s
    ``unquantified_biases`` idiom).
    """
    model_path, root = _project(tmp_path)
    payload = _payload(model_path, root)
    validator = _validator()
    validator.validate(payload)

    for dropped in (
        "manifest-co-edit",
        "extension-unexamined",
        "green-is-not-correctness",
        "structural-surface-only",
        "architecture-static-only",
    ):
        mutated = copy.deepcopy(payload)
        mutated["limits"]["unchecked"] = [
            limit for limit in mutated["limits"]["unchecked"] if limit["id"] != dropped
        ]
        assert not validator.is_valid(mutated), (
            f"a payload that dropped the {dropped!r} limit validated"
        )

    # An ADDITION stays valid — plan 03-06 must be able to widen without a bump.
    widened = copy.deepcopy(payload)
    widened["limits"]["unchecked"].append(
        {"id": "some-future-bound", "description": "discovered later"}
    )
    validator.validate(widened)


def test_an_assertion_that_did_not_run_is_representable_and_never_looks_green(
    tmp_path: Path,
) -> None:
    """R-13′. ``ran: false`` with zero findings must be tellable apart from a
    clean run, and the ``error`` field is what tells them apart."""
    model_path, _ = _project(tmp_path)
    payload = build_conformance_payload(
        model_path,
        None,
        None,
        None,
        actual_model_sha256=None,
        gnd_version=resolve_version(),
        error="no codegen manifest at the target",
    )
    _validator().validate(payload)
    assert all(not assertion["ran"] for assertion in payload["assertions"])
    assert payload["error"]
    assert payload["findings"] == []
    assert payload["unexamined"] == [], "still present, still empty"
    assert payload["architecture"] == {
        "contract": None,
        "declared": None,
        "scanned": [],
    }


# --------------------------------------------------------------------------- #
# the payload's own claims
# --------------------------------------------------------------------------- #


def test_a_clean_payload_validates_and_reports_all_assertions_as_having_run(
    tmp_path: Path,
) -> None:
    model_path, root = _project(tmp_path)
    payload = _payload(model_path, root)
    _validator().validate(payload)

    ids = {assertion["id"] for assertion in payload["assertions"]}
    assert ids == {"integrity", "currency", "structural", "architecture"}
    assert all(assertion["ran"] for assertion in payload["assertions"])
    assert payload["findings"] == []
    assert payload["error"] is None
    assert payload["schema_version"] == CONFORMANCE_SCHEMA_VERSION


def test_the_partition_audit_trail_adds_up_from_the_payload_alone(
    tmp_path: Path,
) -> None:
    """``len(examined) + len(unexamined) == project.recorded_files``, checkable
    by a reader counting the printed arrays — so a file cannot be dropped from
    the report by appearing in neither."""
    model_path, root = _project(tmp_path)
    payload = _payload(model_path, root)
    assert (
        len(payload["examined"]) + len(payload["unexamined"])
        == payload["project"]["recorded_files"]
    )
    assert payload["examined"] and payload["unexamined"], (
        "the fixture exercises only one side of the partition"
    )
    relpaths = [entry["relpath"] for entry in payload["examined"]] + [
        entry["relpath"] for entry in payload["unexamined"]
    ]
    assert len(set(relpaths)) == len(relpaths), "a file appears in both lists"


def test_a_drifted_payload_validates_and_names_the_file(tmp_path: Path) -> None:
    model_path, root = _project(tmp_path)
    manifest = read_manifest(manifest_path(root))
    target = min(
        relpath for relpath, entry in manifest.entries().items() if entry.ownership == "derived"
    )
    edited = root / target
    edited.write_text(edited.read_text(encoding="utf-8") + " ", encoding="utf-8")

    payload = _payload(model_path, root)
    _validator().validate(payload)
    assert [finding["target"] for finding in payload["findings"]] == [target]
    finding = payload["findings"][0]
    assert finding["recorded_sha256"] and finding["actual_sha256"]
    assert finding["recorded_sha256"] != finding["actual_sha256"]


def test_two_runs_over_one_unchanged_project_produce_byte_identical_payloads(
    tmp_path: Path,
) -> None:
    """No timestamp anywhere: a recorded conformance result is re-derivable."""
    model_path, root = _project(tmp_path)
    first = canonical(_payload(model_path, root))
    second = canonical(_payload(model_path, root))
    assert first == second, "two conformance runs over one project disagreed"
    for stamp in ("generated_at", "timestamp", "created_at", '"date"'):
        assert stamp not in first, f"the payload carries a {stamp} field"


def test_the_published_limits_quote_the_manifest_module_verbatim() -> None:
    """Plan 03-04 published ``INTEGRITY_LIMITS`` as importable DATA so this
    payload could carry it rather than paraphrase it — a paraphrase is where a
    limit quietly softens."""
    descriptions = [limit["description"] for limit in LIMITS]
    for published in (INTEGRITY_LIMITS[0], INTEGRITY_LIMITS[2]):
        assert published in descriptions, (
            f"a published integrity limit was reworded rather than carried: {published[:60]}…"
        )


def test_architecture_binding_counts_and_scanned_roster_are_exact(tmp_path: Path) -> None:
    """P-05. A valid all-empty skeleton has zeroes, not null declaration state."""
    model_path, root = _project(tmp_path)
    architecture = _payload(model_path, root)["architecture"]

    assert architecture["contract"]["relpath"] == "architecture.contract.yaml"
    assert len(architecture["contract"]["sha256"]) == 64
    assert architecture["declared"] == {
        "modules": 0,
        "symbols": 0,
        "artifacts": 4,
        "artifact_requirements": 0,
        "entry_points": 0,
        "smoke_rows": 0,
    }
    assert architecture["scanned"] == ["architecture.contract.yaml"]


def test_pre_v4_absence_is_explicit_and_adds_its_conditional_limit(
    tmp_path: Path,
) -> None:
    """P-04. Ran-and-absent is distinct from a check that did not run."""
    model_path, root = _project(tmp_path)
    manifest = read_manifest(manifest_path(root))
    payload = build_conformance_payload(
        model_path,
        manifest,
        check_integrity(root, manifest),
        check_currency(model_path, manifest),
        structural=check_structural(
            load_model(str(model_path)), root, manifest, model_path=model_path
        ),
        architecture=ArchitectureResult(contract_absent=True),
        actual_model_sha256=model_digest(model_path),
        gnd_version=resolve_version(),
    )

    _validator().validate(payload)
    architecture_assertion = next(
        row for row in payload["assertions"] if row["id"] == "architecture"
    )
    assert architecture_assertion == {
        "id": "architecture",
        "ran": True,
        "findings": 0,
    }
    assert payload["architecture"] == {
        "contract": None,
        "declared": None,
        "scanned": [],
    }
    assert "architecture-contract-absent" in {
        limit["id"] for limit in payload["limits"]["unchecked"]
    }


def test_architecture_widening_preserves_every_prior_payload_field(tmp_path: Path) -> None:
    """P-06. Supplying a clean assertion changes only its block and row."""
    model_path, root = _project(tmp_path)
    manifest = read_manifest(manifest_path(root))
    loaded = load_model(str(model_path))
    structural = check_structural(loaded, root, manifest, model_path=model_path)
    integrity = check_integrity(root, manifest)
    currency = check_currency(model_path, manifest)
    common = {
        "structural": structural,
        "actual_model_sha256": model_digest(model_path),
        "gnd_version": resolve_version(),
    }
    without = build_conformance_payload(model_path, manifest, integrity, currency, **common)
    with_architecture = build_conformance_payload(
        model_path,
        manifest,
        integrity,
        currency,
        architecture=check_architecture(loaded, root, manifest, model_path=model_path),
        **common,
    )

    without_prior = copy.deepcopy(without)
    with_prior = copy.deepcopy(with_architecture)
    del without_prior["architecture"]
    del with_prior["architecture"]
    without_prior["assertions"] = [
        row for row in without_prior["assertions"] if row["id"] != "architecture"
    ]
    with_prior["assertions"] = [
        row for row in with_prior["assertions"] if row["id"] != "architecture"
    ]
    assert canonical(without_prior) == canonical(with_prior)


# --------------------------------------------------------------------------- #
# G-15: the other two families are UNTOUCHED
# --------------------------------------------------------------------------- #


def test_the_verdict_payload_gained_no_conformance_member() -> None:
    """Conformance is a third family, not a fourth command in the verdict
    family (G-15).

    The version pin below reads 3, not 2, and the change is deliberate. This
    fence was written to stop the CONFORMANCE plan from reshaping a payload it
    does not own, and that is still exactly what it does: the ``command`` enum
    is the assertion that matters and it is unchanged. Phase 2 of v2.0 moved the
    version to 3 for a reason internal to the verdict family — the always-present
    ``transition`` block — so pinning 2 forever would have made this fence assert
    "no plan may ever evolve the verdict payload", which is not what G-15 says
    and not a rule anyone agreed to.
    """
    from gnd.report import PAYLOAD_SCHEMA_VERSION, load_report_schema

    report_schema = load_report_schema()
    assert PAYLOAD_SCHEMA_VERSION == 3, (
        "the verdict payload's version moved; if a CONFORMANCE change moved it, "
        "revert that -- conformance owns its own schema and payload"
    )
    for name in ("legacy_reference_report", "temporal_admission_report"):
        assert set(report_schema["$defs"][name]["properties"]["command"]["enum"]) == {
            "check", "validate", "verify",
        }, "conformance was fed through the verdict payload's command enum"
    assert report_schema["$defs"]["diff_reference_report"]["properties"]["command"] == {
        "const": "diff",
    }
    def forbid_conformance_member(value):
        if isinstance(value, dict):
            assert "conformance" not in value.get("properties", {})
            for nested in value.values():
                forbid_conformance_member(nested)
        elif isinstance(value, list):
            for nested in value:
                forbid_conformance_member(nested)
    forbid_conformance_member(report_schema)


def test_the_conformance_schema_is_deliberately_absent_from_schema_pairs() -> None:
    """``tests/test_schema_sync.py``'s docstring forbids the "fix": a runtime
    OUTPUT contract has no canonical twin in gnd-orm-core, so pairing it would
    expand that skill's remit to a document no model author ever writes."""
    from test_schema_sync import SCHEMA_PAIRS

    runtime_contracts = {
        "conformance.schema.json",
        "report.schema.json",
        "fidelity.schema.json",
        "measurement.schema.json",
        "pool.schema.json",
    }
    assert not (set(SCHEMA_PAIRS) & runtime_contracts), (
        f"a runtime OUTPUT contract was added to SCHEMA_PAIRS: "
        f"{sorted(set(SCHEMA_PAIRS) & runtime_contracts)}"
    )
    assert SCHEMA_PAIRS, "SCHEMA_PAIRS is empty, so this guard proves nothing"


def test_every_vendored_runtime_schema_is_covered_by_the_wheel_guard() -> None:
    """The packaging obligation, asserted from the source tree so it reds in the
    fast lane rather than only under ``-m distribution``.

    ``fidelity.schema.json`` was MISSING from ``VENDORED_SCHEMAS`` before this
    plan — a shipped runtime contract with no packaging guard at all, closed
    here because this task was already standing in front of the tuple.
    """
    from support.runtime_schema_inventory import VENDORED_SCHEMAS

    on_disk = {f"gnd/{path.name}" for path in (REPO_ROOT / "src" / "gnd").glob("*.schema.json")}
    assert on_disk, "no vendored runtime schemas found; the glob is wrong"
    missing = on_disk - set(VENDORED_SCHEMAS)
    assert not missing, (
        f"vendored runtime schema(s) with no packaging guard: {sorted(missing)}. "
        f"A schema that does not ship breaks the runtime for every installed "
        f"user, and only the built artifact shows it."
    )


# --------------------------------------------------------------------------- #
# every CLI exit path emits a schema-valid payload
# --------------------------------------------------------------------------- #


def test_the_clean_path_emits_a_schema_valid_payload(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    model_path, root = _project(tmp_path)
    code, payload = _json_run(["conformance", str(model_path), str(root)], capsys)
    assert code == 0
    _validator().validate(payload)
    assert payload["findings"] == []


def test_the_drift_path_emits_a_schema_valid_payload(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    model_path, root = _project(tmp_path)
    manifest = read_manifest(manifest_path(root))
    target = min(
        relpath for relpath, entry in manifest.entries().items() if entry.ownership == "derived"
    )
    edited = root / target
    edited.write_text(edited.read_text(encoding="utf-8") + " ", encoding="utf-8")

    code, payload = _json_run(["conformance", str(model_path), str(root)], capsys)
    assert code == 13
    _validator().validate(payload)
    assert [finding["target"] for finding in payload["findings"]] == [target]


def test_the_missing_manifest_path_emits_a_schema_valid_payload(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The internal-error path is a payload too, and it reports ``ran: false``
    rather than an empty findings list that would read as a pass."""
    model_path = tmp_path / "model.orm.yaml"
    shutil.copyfile(FULL_VOCABULARY, model_path)
    root = tmp_path / "not-a-project"
    root.mkdir()

    code, payload = _json_run(["conformance", str(model_path), str(root)], capsys)
    assert code == 66
    _validator().validate(payload)
    assert payload["error"]
    assert not any(assertion["ran"] for assertion in payload["assertions"])


def test_the_missing_model_path_emits_a_schema_valid_payload(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    model_path, root = _project(tmp_path)
    model_path.unlink()
    code, payload = _json_run(["conformance", str(model_path), str(root)], capsys)
    assert code == 66
    _validator().validate(payload)
    assert payload["error"]
    assert payload["model"]["actual_sha256"] is None


def test_the_unparseable_manifest_path_emits_a_schema_valid_payload(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    model_path, root = _project(tmp_path)
    manifest_path(root).write_text("{ not json", encoding="utf-8")
    code, payload = _json_run(["conformance", str(model_path), str(root)], capsys)
    assert code == 3
    _validator().validate(payload)
    assert payload["error"]


@pytest.mark.parametrize(
    ("scenario", "expected_exit", "expected_ran"),
    [
        ("missing-manifest", 66, (False, False, False, False)),
        ("missing-model", 66, (True, False, False, False)),
        ("malformed-manifest", 3, (False, False, False, False)),
        ("malformed-model", 3, (True, True, False, False)),
        ("integrity-io", 74, (False, True, True, True)),
        ("model-io", 74, (True, False, True, True)),
    ],
)
def test_conformance_failures_are_operator_neutral_and_invocation_independent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    scenario: str,
    expected_exit: int,
    expected_ran: tuple[bool, bool, bool, bool],
) -> None:
    from gnd.conformance import ConformanceError
    from gnd.conformance import integrity as integrity_module
    from gnd.conformance import service as service_module
    from gnd.conformance.service import run_conformance

    workspace = (
        tmp_path / "operator-home-sentinel" / "operator-user-sentinel" / "operator-root-sentinel"
    )
    workspace.mkdir(parents=True)
    model_path, root = _project(workspace)
    raw_error_sentinel = "lower-level-path-sentinel"

    if scenario == "missing-manifest":
        manifest_path(root).unlink()
    elif scenario == "missing-model":
        model_path.unlink()
    elif scenario == "malformed-manifest":
        manifest_path(root).write_text("{not-json\n", encoding="utf-8")
    elif scenario == "malformed-model":
        model_path.write_text("version: 1\nnot: a model\n", encoding="utf-8")
    elif scenario == "integrity-io":
        from gnd.artifacts import ArtifactError

        manifest = read_manifest(manifest_path(root))
        derived = next(item for item in manifest.files if item.ownership == "derived")
        real_read = integrity_module.read_regular_bounded_at

        def failing_read(root_fd: int, relpath: str, **kwargs: Any):
            if relpath == derived.relpath:
                raise ArtifactError(f"{raw_error_sentinel}: {relpath}")
            return real_read(root_fd, relpath, **kwargs)

        monkeypatch.setattr(integrity_module, "read_regular_bounded_at", failing_read)
    elif scenario == "model-io":

        def failing_model_digest(path: str | Path) -> str:
            raise ConformanceError(f"{raw_error_sentinel}: {path}")

        monkeypatch.setattr(service_module, "model_file_sha256", failing_model_digest)
    else:  # pragma: no cover - parameter list is the closed scenario set
        raise AssertionError(scenario)

    absolute = run_conformance(model_path, root)
    monkeypatch.chdir(workspace)
    relative = run_conformance(Path("model.orm.yaml"), Path("project"))

    assert absolute.exit_code == relative.exit_code == expected_exit
    assert absolute.payload == relative.payload
    _validator().validate(absolute.payload)
    assert tuple(assertion["ran"] for assertion in absolute.payload["assertions"]) == expected_ran
    assert absolute.payload["error"]
    _assert_operator_neutral(
        absolute.payload,
        forbidden=(
            workspace.as_posix(),
            "operator-home-sentinel",
            "operator-user-sentinel",
            "operator-root-sentinel",
            raw_error_sentinel,
        ),
    )


def test_two_cli_runs_over_one_unchanged_project_print_identical_bytes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    model_path, root = _project(tmp_path)
    capsys.readouterr()
    assert main(["conformance", str(model_path), str(root), "--format", "json"]) == 0
    first = capsys.readouterr().out
    assert main(["conformance", str(model_path), str(root), "--format", "json"]) == 0
    second = capsys.readouterr().out
    assert first == second and first.strip(), "two CLI runs disagreed byte-for-byte"


@pytest.mark.parametrize(
    ("high_band", "low_band", "expected_exit", "expected_cause", "excluded_cause"),
    [
        ("io", "missing", 74, "file-io", "missing-model"),
        ("io", "malformed", 74, "file-io", "invalid-model"),
        ("drift", "missing", 66, "missing-model", None),
        ("drift", "malformed", 3, "invalid-model", None),
    ],
)
def test_compound_failures_select_error_from_the_same_precedence_band(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    high_band: str,
    low_band: str,
    expected_exit: int,
    expected_cause: str,
    excluded_cause: str | None,
) -> None:
    from gnd.artifacts import ArtifactError
    from gnd.conformance import integrity as integrity_module
    from gnd.conformance.service import run_conformance

    model_path, root = _project(tmp_path)
    manifest = read_manifest(manifest_path(root))
    derived = next(item for item in manifest.files if item.ownership == "derived")
    if high_band == "io":
        real_read = integrity_module.read_regular_bounded_at

        def failing_read(root_fd: int, relpath: str, **kwargs: Any):
            if relpath == derived.relpath:
                raise ArtifactError("injected descriptor read failure")
            return real_read(root_fd, relpath, **kwargs)

        monkeypatch.setattr(integrity_module, "read_regular_bounded_at", failing_read)
    else:
        target = root / derived.relpath
        target.write_bytes(target.read_bytes() + b"\n# drift\n")

    if low_band == "missing":
        model_path.unlink()
    else:
        model_path.write_text("version: 1\nnot: a model\n", encoding="utf-8")

    result = run_conformance(model_path, root)

    assert result.exit_code == expected_exit
    assert expected_cause in result.payload["error"]
    if excluded_cause is not None:
        assert excluded_cause not in result.payload["error"]


@pytest.mark.parametrize(
    ("scenario", "expected_exit"),
    [
        ("clean", 0),
        ("drift", 13),
        ("missing-manifest", 66),
        ("missing-model", 66),
        ("malformed-manifest", 3),
    ],
)
def test_conformance_cli_is_a_byte_exact_renderer_of_the_reusable_service(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    scenario: str,
    expected_exit: int,
) -> None:
    from gnd.conformance.report import canonical, render_conformance
    from gnd.conformance.service import run_conformance

    model_path, root = _project(tmp_path)
    if scenario == "drift":
        manifest = read_manifest(manifest_path(root))
        derived = next(item for item in manifest.files if item.ownership == "derived")
        target = root / derived.relpath
        target.write_bytes(target.read_bytes() + b"\n# drift\n")
    elif scenario == "missing-manifest":
        manifest_path(root).unlink()
    elif scenario == "missing-model":
        model_path.unlink()
    elif scenario == "malformed-manifest":
        manifest_path(root).write_text("{not-json\n", encoding="utf-8")

    expected = run_conformance(model_path, root)
    assert expected.exit_code == expected_exit
    for output_format, rendered in (
        ("json", canonical(expected.payload)),
        ("text", render_conformance(expected.payload)),
    ):
        capsys.readouterr()
        assert (
            main(
                [
                    "conformance",
                    str(model_path),
                    str(root),
                    "--format",
                    output_format,
                ]
            )
            == expected_exit
        )
        assert capsys.readouterr().out == rendered + "\n"


def test_conformance_cli_preserves_service_io_exit_and_payload_without_translation(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from gnd.conformance.report import canonical, render_conformance
    from gnd.conformance.service import ConformanceServiceResult, run_conformance

    model_path = tmp_path / "model.orm.yaml"
    shutil.copyfile(FULL_VOCABULARY, model_path)
    root = tmp_path / "unreadable-project"
    root.mkdir()
    payload = run_conformance(model_path, root).payload
    expected = ConformanceServiceResult(payload=payload, exit_code=74)
    calls: list[tuple[str, str]] = []

    def io_result(model: str, project: str) -> ConformanceServiceResult:
        calls.append((model, project))
        return expected

    monkeypatch.setattr("gnd.conformance.service.run_conformance", io_result)
    for output_format, rendered in (
        ("json", canonical(payload)),
        ("text", render_conformance(payload)),
    ):
        capsys.readouterr()
        assert (
            main(
                [
                    "conformance",
                    str(model_path),
                    str(root),
                    "--format",
                    output_format,
                ]
            )
            == 74
        )
        assert capsys.readouterr().out == rendered + "\n"
    assert calls == [(str(model_path), str(root)), (str(model_path), str(root))]


def test_text_renderer_names_integrity_scope_when_architecture_scanned_an_extension(
    tmp_path: Path,
) -> None:
    """Review regression: integrity-unexamined never means all-conformance-unread."""
    from ruamel.yaml import YAML

    from gnd.conformance.report import render_conformance
    from gnd.conformance.service import run_conformance

    model_path, root = _project(tmp_path)
    contract_path = root / "architecture.contract.yaml"
    contract = YAML(typ="safe").load(contract_path.read_text())
    contract["modules"] = [{"path": "public_extension.py", "symbols": [
        {"name": "identity", "parameters": ["value"]},
    ]}]
    (root / "public_extension.py").write_text("def identity(value):\n    return value\n")
    with contract_path.open("w") as stream:
        YAML().dump(contract, stream)
    result = run_conformance(model_path, root)
    rendered = render_conformance(result.payload)
    assert result.exit_code == 0
    assert "unexamined by integrity: 4 file(s) not digest-gated" in rendered
    assert "conformance says NOTHING about" not in rendered
    assert rendered.count("architecture.contract.yaml") >= 2


def test_error_schema_describes_retained_observations_during_command_io() -> None:
    """C-46 may retain ran:true observations while the command selects band 74."""
    schema = load_conformance_schema()
    description = schema["properties"]["error"]["description"]
    expected = json.loads(
        (
            REPO_ROOT
            / "tests"
            / "fixtures"
            / "architecture"
            / "static"
            / "expected.json"
        ).read_text(encoding="utf-8")
    )["cases"]["C-46-root-race-band-74"]
    assert expected["service_architecture_ran"] is True
    assert expected["exit"] == 74
    assert "command-wide" in description
    assert "retained successful assertion observations" in description
