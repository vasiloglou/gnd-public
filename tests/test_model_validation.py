"""Model validation tests — full D-01 vocabulary (layer 1) and semantic rules (layer 2).

Layer 1: the full-vocabulary fixture passes the extended meta-schema; unknown
constraint types and missing ``modality`` are rejected structurally with
pointed paths.

Layer 2: each semantic rule group has one invalid fixture rejected with a
``ValidationIssue`` whose ``rule_id`` names the rule and whose path/message
names the offending element id. The D-03 modality-policy fixture loads
successfully but carries a WARNING-severity issue (``Model.warnings``).
"""

from __future__ import annotations

import inspect
import re
from pathlib import Path

import pytest
from pydantic import ValidationError as PydanticValidationError
from ruamel.yaml import YAML
from support.cli_runner import run_gnd_text as _run_cli

from gnd import model as model_module
from gnd.model import (
    MAX_MODEL_BYTES,
    Model,
    ModelLoadError,
    ModelValidationError,
    ValidationIssue,
    load_model,
)

MODELS = Path(__file__).parent / "fixtures" / "models"
FULL_VOCABULARY = MODELS / "full_vocabulary.orm.yaml"
GUARDED_MINIMAL = MODELS / "guarded_minimal.orm.yaml"
INVALID = MODELS / "invalid"
SKELETON_MODEL = Path(__file__).parent / "fixtures" / "skeleton" / "model.orm.yaml"
CHECKER_FIXTURES = Path(__file__).parent / "fixtures" / "checker"
REPRESENTATION_FORMAT = (
    Path(__file__).parent.parent
    / "src"
    / "gnd"
    / "skills"
    / "gnd-orm-core"
    / "references"
    / "representation-format.md"
)

#: Every Halpin ORM 2 constraint family D-01 requires syntax for.
ALL_FAMILIES = {
    "uniqueness",
    "mandatory",
    "mandatory-disjunctive",
    "value",
    "frequency",
    "ring",
    "subset",
    "equality",
    "exclusion",
    "exclusive-or",
    "value-comparison",
    "cardinality",
    "subtype-partition",
    "guarded",
    "textual",
}


def test_normative_semantic_rule_inventory_matches_registration_order():
    section = REPRESENTATION_FORMAT.read_text(encoding="utf-8").split(
        "### Layer 2 — semantic", maxsplit=1
    )[1].split("Errors abort the load", maxsplit=1)[0]
    documented = re.findall(r"\| `(semantic:[^`]+)` \|", section)
    registered = []
    # Current rules may own multiple named refusals. These are exact exceptions,
    # not a blanket relaxation of registration/documentation agreement.
    extra = {
        "_rule_temporal_language": {
            "semantic:guarded-binding-type", "semantic:temporal-comparison-type",
            "semantic:temporal-site",
        },
        "_rule_depends_on": {"semantic:depends-on-ref"},
    }
    multi = {
        "_rule_derivation_unstratified": [
            "semantic:derivation-unstratified",
            "semantic:derivation-recursive-value-invention",
        ],
    }
    assert [rule.__name__ for rule in model_module._SEMANTIC_RULES[:5]] == [
        "_rule_temporal_language", "_rule_id_unique", "_rule_role_ref",
        "_rule_cross_ref", "_rule_depends_on",
    ]
    seen_extra = set()
    seen_multi = set()
    for rule in model_module._SEMANTIC_RULES:
        identifiers = list(dict.fromkeys(re.findall(r'rule_id="([^\"]+)"', inspect.getsource(rule))))
        if rule.__name__ in extra:
            assert set(identifiers) == extra[rule.__name__]
            seen_extra.add(rule.__name__)
        else:
            if rule.__name__ in multi:
                assert set(identifiers) == set(multi[rule.__name__])
                identifiers = multi[rule.__name__]
                seen_multi.add(rule.__name__)
            else:
                assert len(identifiers) == 1, rule.__name__
            registered.extend(identifiers)
    assert seen_extra == set(extra)
    assert seen_multi == set(multi)
    assert documented == registered


def _load_yaml(path: Path):
    yaml = YAML(typ="rt")
    with open(path, encoding="utf-8") as handle:
        return yaml.load(handle)


def _dump_yaml(doc, path: Path) -> Path:
    yaml = YAML(typ="rt")
    with open(path, "w", encoding="utf-8") as handle:
        yaml.dump(doc, handle)
    return path


# --- D-01: the full vocabulary is expressible and validates clean ---


def test_full_vocabulary_loads_clean():
    model = load_model(FULL_VOCABULARY)
    assert model.object_types and model.fact_types and model.constraints


def test_full_vocabulary_exercises_every_family():
    # The full-vocabulary and guarded fixtures together cover every family.
    seen: set[str] = set()
    for fixture in (FULL_VOCABULARY, GUARDED_MINIMAL):
        doc = _load_yaml(fixture)
        for fact_type in doc["fact_types"]:
            for constraint in fact_type.get("constraints") or []:
                seen.add(str(constraint["type"]))
        for constraint in doc["constraints"]:
            seen.add(str(constraint["type"]))
    assert seen == ALL_FAMILIES, f"missing families: {ALL_FAMILIES - seen}"


def test_explicit_fact_type_arity_must_match_role_count(tmp_path):
    doc = _load_yaml(FULL_VOCABULARY)
    fact_type = doc["fact_types"][0]
    fact_type["arity"] = len(fact_type["roles"]) + 1
    path = _dump_yaml(doc, tmp_path / "bad_explicit_arity.orm.yaml")

    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)
    assert any(
        issue.rule_id == "semantic:fact-type-arity" for issue in excinfo.value.issues
    )


def test_omitted_fact_type_arity_remains_implicit(tmp_path):
    doc = _load_yaml(FULL_VOCABULARY)
    doc["fact_types"][0].pop("arity", None)
    assert load_model(_dump_yaml(doc, tmp_path / "implicit_arity.orm.yaml")).fact_types


@pytest.mark.parametrize("rule", [None, ""])
def test_derived_fact_type_requires_non_empty_derivation_rule(tmp_path, rule):
    doc = _load_yaml(FULL_VOCABULARY)
    fact_type = doc["fact_types"][0]
    fact_type["derivation"] = "derived"
    if rule is None:
        fact_type.pop("derivation_rule", None)
    else:
        fact_type["derivation_rule"] = rule
    path = _dump_yaml(doc, tmp_path / "missing_fact_derivation.orm.yaml")
    with pytest.raises(ModelValidationError):
        load_model(path)


@pytest.mark.parametrize("invalid_bound", [{"min": -1}, {"max": 1.5}])
def test_count_bounds_are_non_negative_integers(tmp_path, invalid_bound):
    doc = _load_yaml(FULL_VOCABULARY)
    constraint = next(
        item
        for item in doc["constraints"]
        if item["type"] in ("frequency", "cardinality")
    )
    constraint["bound"] = invalid_bound
    path = _dump_yaml(doc, tmp_path / "bad_count_bound.orm.yaml")
    with pytest.raises(ModelValidationError):
        load_model(path)


def test_count_bound_minimum_cannot_exceed_maximum(tmp_path):
    doc = _load_yaml(FULL_VOCABULARY)
    constraint = next(
        item
        for item in doc["constraints"]
        if item["type"] in ("frequency", "cardinality")
    )
    constraint["bound"] = {"min": 3, "max": 2}
    path = _dump_yaml(doc, tmp_path / "inverted_count_bound.orm.yaml")
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)
    assert any(
        issue.rule_id == "semantic:count-bound-order" for issue in excinfo.value.issues
    )


def test_full_vocabulary_has_external_uniqueness_and_scoped_frequency():
    doc = _load_yaml(FULL_VOCABULARY)
    top = doc["constraints"]
    assert any(
        c["type"] == "uniqueness" and c.get("scope") == "external" for c in top
    ), "external uniqueness must appear top-level"
    assert any(
        c["type"] == "frequency" and c.get("scope") == "external" for c in top
    ), "external frequency must appear top-level"
    inline = [c for ft in doc["fact_types"] for c in ft.get("constraints") or []]
    assert any(
        c["type"] == "frequency" and c.get("scope") == "internal" for c in inline
    ), "internal frequency must appear inline"


def test_deontic_notes_round_trip_without_data_loss(tmp_path):
    doc = _load_yaml(FULL_VOCABULARY)
    doc["deontic_notes"] = [
        {"text": "must retain", "rationale": "schema and runtime must agree"}
    ]
    model = load_model(_dump_yaml(doc, tmp_path / "notes.orm.yaml"))

    assert model.model_dump()["deontic_notes"] == [
        {"text": "must retain", "rationale": "schema and runtime must agree"}
    ]


def test_semantic_warnings_survive_alongside_semantic_errors(tmp_path):
    doc = _load_yaml(CHECKER_FIXTURES / "misc.orm.yaml")
    doc["fact_types"][0]["roles"][0]["object_type"] = "missing_type"
    path = _dump_yaml(doc, tmp_path / "error_and_warning.orm.yaml")

    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)
    assert any(issue.severity == "error" for issue in excinfo.value.issues)
    assert any(
        warning.rule_id == "semantic:textual-alethic"
        for warning in excinfo.value.warnings
    )

    result = _run_cli("validate", str(path))
    assert result.returncode == 3
    assert "semantic:textual-alethic" in result.stdout
    assert "semantic:role-ref" in result.stdout


def test_direct_model_rejects_unknown_top_level_fields():
    with pytest.raises(PydanticValidationError, match="extra"):
        Model(
            version=1,
            object_types=[],
            fact_types=[],
            schema_only_field="would otherwise be discarded",
        )


def test_cli_validate_full_vocabulary_exits_0():
    result = _run_cli("validate", str(FULL_VOCABULARY))
    assert result.returncode == 0, result.stdout + result.stderr


# --- layer-1 structural rejections ---


def test_unknown_constraint_type_rejected(tmp_path):
    doc = _load_yaml(FULL_VOCABULARY)
    doc["constraints"].append(
        {
            "type": "made-up-family",
            "source": "user-supplied",
            "status": "confirmed",
            "modality": "alethic",
            "provenance": {"user_note": "nonsense"},
        }
    )
    path = _dump_yaml(doc, tmp_path / "unknown_type.orm.yaml")
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)
    assert any(
        "$.constraints" in issue.path and issue.rule_id.startswith("jsonschema:")
        for issue in excinfo.value.issues
    ), f"unknown constraint type must fail layer 1 at $.constraints: {excinfo.value.issues}"


def test_missing_modality_rejected(tmp_path):
    doc = _load_yaml(FULL_VOCABULARY)
    del doc["constraints"][0]["modality"]
    path = _dump_yaml(doc, tmp_path / "no_modality.orm.yaml")
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)
    assert any(
        "$.constraints" in issue.path for issue in excinfo.value.issues
    ), f"missing modality must fail layer 1, pointed at the constraint: {excinfo.value.issues}"


def test_missing_modality_cli_exits_3(tmp_path):
    doc = _load_yaml(FULL_VOCABULARY)
    del doc["fact_types"][0]["constraints"][0]["modality"]
    path = _dump_yaml(doc, tmp_path / "no_modality_inline.orm.yaml")
    result = _run_cli("validate", str(path))
    assert result.returncode == 3, result.stdout + result.stderr


def test_constraint_typo_field_rejected(tmp_path):
    doc = _load_yaml(FULL_VOCABULARY)
    doc["fact_types"][0]["constraints"][0]["rolez"] = ["employee"]
    path = _dump_yaml(doc, tmp_path / "typo_field.orm.yaml")
    with pytest.raises(ModelValidationError):
        load_model(path)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("fact_id", "fact\npass=9_fail=0", id="fact-id-control-character"),
        pytest.param("role_name", "BadRole", id="role-name-uppercase"),
    ],
)
def test_identifiers_follow_lower_snake_case_grammar(tmp_path, field, value):
    doc = _load_yaml(FULL_VOCABULARY)
    if field == "fact_id":
        doc["fact_types"][0]["id"] = value
    else:
        doc["fact_types"][0]["roles"][0]["role_name"] = value
    path = _dump_yaml(doc, tmp_path / "bad_identifier.orm.yaml")
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)
    assert any(issue.rule_id == "jsonschema:pattern" for issue in excinfo.value.issues)


@pytest.mark.parametrize("mode", ["unit-based", "external"])
def test_unresolvable_reference_modes_forbid_value_type(tmp_path, mode):
    doc = _load_yaml(FULL_VOCABULARY)
    object_type = next(
        item
        for item in doc["object_types"]
        if item.get("kind") == "entity" and not item.get("subtype_of")
    )
    reference = {"mode": mode, "value_type": "employee_id"}
    if mode == "unit-based":
        reference.update({"unit": "person", "measure_type": "count"})
    object_type["reference"] = reference
    path = _dump_yaml(doc, tmp_path / "hybrid_reference.orm.yaml")
    with pytest.raises(ModelValidationError):
        load_model(path)


def test_value_constraint_rejects_multiple_forms(tmp_path):
    doc = _load_yaml(FULL_VOCABULARY)
    constraint = next(c for c in doc["constraints"] if c["type"] == "value")
    constraint["allowed"] = [5]
    constraint["range"] = {"min": 10, "max": 20}
    constraint.pop("ranges", None)
    path = _dump_yaml(doc, tmp_path / "ambiguous_value.orm.yaml")
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)
    assert any(issue.rule_id == "jsonschema:oneOf" for issue in excinfo.value.issues)


def test_cardinality_scope_rejects_other_scope_target(tmp_path):
    doc = _load_yaml(FULL_VOCABULARY)
    constraint = next(c for c in doc["constraints"] if c["type"] == "cardinality")
    if constraint["scope"] == "object":
        constraint["role_ref"] = {"fact_type": "employee_works_on_project", "role": "employee"}
    else:
        constraint["object_type"] = "employee"
    path = _dump_yaml(doc, tmp_path / "ambiguous_cardinality.orm.yaml")
    with pytest.raises(ModelValidationError):
        load_model(path)


def _append_range_constraint(doc, object_type, bounds):
    doc["object_types"].append(object_type)
    doc["constraints"].append(
        {
            "type": "value",
            "object_type": object_type["id"],
            "range": bounds,
            "source": "user-supplied",
            "status": "confirmed",
            "modality": "alethic",
            "provenance": {"user_note": "range endpoint regression"},
        }
    )


@pytest.mark.parametrize(
    ("primitive", "bounds"),
    [
        pytest.param("String", {"min": "A", "max": "Z"}, id="character-range"),
        pytest.param(
            "Date",
            {"min": "2026-01-01", "max": "2026-12-31"},
            id="date-range",
        ),
    ],
)
def test_string_range_endpoints_load_for_matching_primitive(tmp_path, primitive, bounds):
    doc = _load_yaml(FULL_VOCABULARY)
    _append_range_constraint(
        doc,
        {"id": "range_value", "name": "RangeValue", "kind": "value", "primitive": primitive},
        bounds,
    )
    path = _dump_yaml(doc, tmp_path / "string_range.orm.yaml")
    assert load_model(path).constraints


@pytest.mark.parametrize(
    ("primitive", "bounds"),
    [
        pytest.param("Integer", {"min": 1, "max": "10"}, id="mixed-endpoints"),
        pytest.param("Date", {"min": "2025-02-29"}, id="invalid-date"),
        pytest.param("String", {"min": 1}, id="number-for-string"),
    ],
)
def test_range_endpoints_must_match_resolved_primitive(tmp_path, primitive, bounds):
    doc = _load_yaml(FULL_VOCABULARY)
    _append_range_constraint(
        doc,
        {"id": "range_value", "name": "RangeValue", "kind": "value", "primitive": primitive},
        bounds,
    )
    path = _dump_yaml(doc, tmp_path / "bad_range.orm.yaml")
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)
    assert any(
        issue.rule_id == "semantic:value-range-type" for issue in excinfo.value.issues
    )


@pytest.mark.parametrize(
    ("primitive", "bounds", "list_form"),
    [
        pytest.param("Integer", {"min": 10, "max": 1}, True, id="numeric-ranges-entry"),
        pytest.param(
            "Date",
            {"min": "2026-12-31", "max": "2026-01-01"},
            False,
            id="date",
        ),
        pytest.param(
            "DateTime",
            {"min": "2026-01-02T00:00:00Z", "max": "2026-01-01T00:00:00Z"},
            False,
            id="datetime",
        ),
    ],
)
def test_value_range_minimum_cannot_exceed_maximum(
    tmp_path, primitive, bounds, list_form
):
    doc = _load_yaml(FULL_VOCABULARY)
    _append_range_constraint(
        doc,
        {"id": "ordered_range", "name": "OrderedRange", "kind": "value", "primitive": primitive},
        bounds,
    )
    if list_form:
        constraint = doc["constraints"][-1]
        constraint["ranges"] = [constraint.pop("range")]
    path = _dump_yaml(doc, tmp_path / "inverted_value_range.orm.yaml")

    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)

    assert any(
        issue.rule_id == "semantic:value-range-order" for issue in excinfo.value.issues
    )


@pytest.mark.parametrize("constraint_type", ["mandatory-disjunctive", "exclusive-or"])
def test_single_role_disjunction_requires_same_declared_subject_type(
    tmp_path, constraint_type
):
    doc = _load_yaml(FULL_VOCABULARY)
    references = []
    seen_types = set()
    for fact_type in doc["fact_types"]:
        for role in fact_type.get("roles") or []:
            object_type = role["object_type"]
            if object_type not in seen_types:
                references.append(
                    {"fact_type": fact_type["id"], "role": role["role_name"]}
                )
                seen_types.add(object_type)
            if len(references) == 2:
                break
        if len(references) == 2:
            break
    common = {
        "type": constraint_type,
        "source": "user-supplied",
        "status": "confirmed",
        "modality": "alethic",
        "provenance": {"user_note": "disjunctive subject regression"},
    }
    if constraint_type == "mandatory-disjunctive":
        common["role_refs"] = references
    else:
        common["role_seqs"] = [[reference] for reference in references]
    doc["constraints"].append(common)
    path = _dump_yaml(doc, tmp_path / "mixed_subjects.orm.yaml")

    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)
    assert any(
        issue.rule_id == "semantic:disjunctive-subject-type"
        for issue in excinfo.value.issues
    )


def _ambiguous_join_document():
    return {
        "version": 1,
        "object_types": [
            {"id": "person", "kind": "value", "primitive": "String"},
            {"id": "code", "kind": "value", "primitive": "String"},
            {"id": "number", "kind": "value", "primitive": "Integer"},
        ],
        "fact_types": [
            {
                "id": "f1",
                "reading": "{left} and {right} use {code}",
                "roles": [
                    {"object_type": "person", "role_name": "left"},
                    {"object_type": "person", "role_name": "right"},
                    {"object_type": "code", "role_name": "code"},
                ],
            },
            {
                "id": "f2",
                "reading": "{person} has {number}",
                "roles": [
                    {"object_type": "person", "role_name": "person"},
                    {"object_type": "number", "role_name": "number"},
                ],
            },
        ],
        "constraints": [
            {
                "type": "uniqueness",
                "scope": "external",
                "role_refs": [
                    {"fact_type": "f1", "role": "code"},
                    {"fact_type": "f2", "role": "number"},
                ],
                "source": "user-supplied",
                "status": "confirmed",
                "modality": "alethic",
                "provenance": {"user_note": "ambiguous join regression"},
            }
        ],
    }


def test_cross_fact_join_rejects_duplicate_same_type_anchors(tmp_path):
    path = _dump_yaml(_ambiguous_join_document(), tmp_path / "ambiguous_join.orm.yaml")
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)
    assert any(
        issue.rule_id == "semantic:join-anchor-ambiguous"
        for issue in excinfo.value.issues
    )


@pytest.mark.parametrize(
    "reading",
    [
        "{Country} identifies {Person}",
        "{Unrelated} identifies {Country}",
    ],
)
def test_reading_placeholder_labels_must_follow_role_object_type_order(tmp_path, reading):
    doc = {
        "version": 1,
        "object_types": [
            {"id": "person", "name": "Person", "kind": "value", "primitive": "String"},
            {"id": "country", "name": "Country", "kind": "value", "primitive": "String"},
        ],
        "fact_types": [
            {
                "id": "person_identifies_country",
                "reading": reading,
                "roles": [
                    {"object_type": "person", "role_name": "person"},
                    {"object_type": "country", "role_name": "country"},
                ],
            }
        ],
    }
    path = _dump_yaml(doc, tmp_path / "reading-role-order.orm.yaml")

    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)

    matching = [
        issue
        for issue in excinfo.value.issues
        if issue.rule_id == "semantic:reading-placeholders"
    ]
    assert len(matching) == 1
    assert "position 0" in matching[0].message


def test_llm_inferred_requires_world_fact(tmp_path):
    doc = _load_yaml(FULL_VOCABULARY)
    for constraint in doc["constraints"]:
        if constraint.get("source") == "llm-inferred":
            del constraint["provenance"]
            break
    path = _dump_yaml(doc, tmp_path / "no_world_fact.orm.yaml")
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)
    assert any("$.constraints" in issue.path for issue in excinfo.value.issues)


# --- layer-2 semantic rules: one invalid fixture per rule group ---

SEMANTIC_CASES = [
    ("duplicate_id.yaml", "semantic:id-unique", "person_id"),
    ("bad_role_ref.yaml", "semantic:role-ref", "ghost"),
    ("bad_cross_ref.yaml", "semantic:cross-ref", "nonsmoker"),
    ("reading_placeholders.yaml", "semantic:reading-placeholders", "person_smokes"),
    ("duplicate_role_names.yaml", "semantic:role-names-distinct", "person_knows_person"),
    # CR-03: the SAME rule, over two roles of DIFFERENT object types. The rule
    # used to bucket by object_type, so this fixture validated clean at exit 0
    # and the fact type's declared role SET had one member for two roles —
    # which made popvalidate's R5 accept a fact filling only one of them and
    # restored CONTEXT.md probe #1 (see the fixture's header for the trace).
    (
        "duplicate_role_names_cross_type.orm.yaml",
        "semantic:role-names-distinct",
        "movie_has_title",
    ),
    ("bad_subtype_ref.yaml", "semantic:subtype-ref", "ghost"),
    ("missing_external_uc.yaml", "semantic:external-ref-uc", "enrolment"),
    ("bad_reference_value_type.yaml", "semantic:reference-value-type", "person_name"),
    ("explicit_not_confirmed.yaml", "semantic:status-source", "person_smokes"),
    ("rejected_in_active.yaml", "semantic:status-source", "rejected"),
]


@pytest.mark.parametrize(("fixture", "rule_id", "fragment"), SEMANTIC_CASES)
def test_semantic_rule_rejections(fixture, rule_id, fragment):
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(INVALID / fixture)
    matching = [issue for issue in excinfo.value.issues if issue.rule_id == rule_id]
    assert matching, (
        f"expected {rule_id}, got {[i.rule_id for i in excinfo.value.issues]}"
    )
    assert any(fragment in issue.path or fragment in issue.message for issue in matching), (
        f"issue must name '{fragment}' in path or message: {matching}"
    )


def test_at_least_8_distinct_semantic_rule_ids():
    rule_ids = {rule_id for _, rule_id, _ in SEMANTIC_CASES} | {"semantic:modality-policy"}
    assert len(rule_ids) >= 8, f"only {len(rule_ids)} distinct semantic rule_ids: {rule_ids}"


# --- WR-01: plain-string references must resolve (semantic:string-ref) ---


def _first_inline(doc, constraint_type):
    for fact_type in doc["fact_types"]:
        for constraint in fact_type.get("constraints") or []:
            if constraint["type"] == constraint_type:
                return fact_type, constraint
    raise AssertionError(f"no inline {constraint_type} constraint in fixture")


def _mutate_mandatory_role(doc):
    _, constraint = _first_inline(doc, "mandatory")
    constraint["role"] = "no_such_role"


def _mutate_uniqueness_roles(doc):
    _, constraint = _first_inline(doc, "uniqueness")
    constraint["roles"] = ["no_such_role"]


def _mutate_frequency_roles(doc):
    _, constraint = _first_inline(doc, "frequency")
    constraint["roles"] = ["no_such_role"]


def _mutate_value_comparison_operands(doc):
    _, constraint = _first_inline(doc, "value-comparison")
    constraint["role_a"] = "no_such_role"
    constraint["role_b"] = "also_missing"


def _mutate_subtype_partition_subtype(doc):
    constraint = next(
        c for c in doc["constraints"] if c["type"] == "subtype-partition"
    )
    constraint["subtypes"] = ["no_such_subtype"]


def _mutate_value_object_type(doc):
    constraint = next(c for c in doc["constraints"] if c["type"] == "value")
    constraint["object_type"] = "no_such_object_type"


STRING_REF_MUTATIONS = [
    pytest.param(_mutate_mandatory_role, "no_such_role", id="mandatory-role"),
    pytest.param(_mutate_uniqueness_roles, "no_such_role", id="uniqueness-roles"),
    pytest.param(_mutate_frequency_roles, "no_such_role", id="frequency-roles"),
    pytest.param(
        _mutate_value_comparison_operands, "no_such_role", id="value-comparison-operands"
    ),
    pytest.param(
        _mutate_subtype_partition_subtype, "no_such_subtype", id="subtype-partition-subtypes"
    ),
    pytest.param(_mutate_value_object_type, "no_such_object_type", id="value-object-type"),
]


@pytest.mark.parametrize(("mutate", "fragment"), STRING_REF_MUTATIONS)
def test_string_ref_typos_rejected(tmp_path, mutate, fragment):
    doc = _load_yaml(FULL_VOCABULARY)
    mutate(doc)
    path = _dump_yaml(doc, tmp_path / "string_ref_typo.orm.yaml")
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)
    matching = [i for i in excinfo.value.issues if i.rule_id == "semantic:string-ref"]
    assert matching, f"expected semantic:string-ref, got {excinfo.value.issues}"
    assert any(fragment in i.message for i in matching), (
        f"issue must name '{fragment}': {matching}"
    )


def test_value_comparison_literal_operand_still_allowed(tmp_path):
    """One role operand + one literal operand is a supported checker shape and
    must NOT be rejected by semantic:string-ref."""
    doc = _load_yaml(FULL_VOCABULARY)
    _, constraint = _first_inline(doc, "value-comparison")
    constraint["role_b"] = "2100-01-01"
    path = _dump_yaml(doc, tmp_path / "literal_operand.orm.yaml")
    model = load_model(path)
    assert model.fact_types


def test_tagged_value_comparison_operands_load(tmp_path):
    doc = _load_yaml(FULL_VOCABULARY)
    _, constraint = _first_inline(doc, "value-comparison")
    original_role = constraint["role_a"]
    constraint["role_a"] = {"role": original_role}
    constraint["role_b"] = {"literal": "001"}
    path = _dump_yaml(doc, tmp_path / "tagged_operands.orm.yaml")
    assert load_model(path).fact_types


# --- CR-01: ring constraints require a compatible binary host fact type ---


def _ring_constraint() -> dict:
    return {
        "type": "ring",
        "variant": "irreflexive",
        "source": "user-supplied",
        "status": "confirmed",
        "modality": "alethic",
        "provenance": {"user_note": "regression fixture for semantic:ring-binary"},
    }


def test_ring_on_incompatible_binary_rejected(tmp_path):
    doc = _load_yaml(FULL_VOCABULARY)
    target = next(
        ft for ft in doc["fact_types"] if ft["id"] == "employee_works_on_project"
    )
    target.setdefault("constraints", []).append(_ring_constraint())
    path = _dump_yaml(doc, tmp_path / "ring_incompatible.orm.yaml")
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)
    matching = [i for i in excinfo.value.issues if i.rule_id == "semantic:ring-binary"]
    assert matching, f"expected semantic:ring-binary, got {excinfo.value.issues}"
    assert any("employee_works_on_project" in i.path for i in matching)


def test_ring_on_non_binary_rejected(tmp_path):
    doc = _load_yaml(FULL_VOCABULARY)
    ternary = next(ft for ft in doc["fact_types"] if len(ft.get("roles") or []) != 2)
    ternary.setdefault("constraints", []).append(_ring_constraint())
    path = _dump_yaml(doc, tmp_path / "ring_non_binary.orm.yaml")
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)
    assert any(
        issue.rule_id == "semantic:ring-binary" for issue in excinfo.value.issues
    ), f"expected semantic:ring-binary, got {excinfo.value.issues}"


# --- CORE-06 / D-13 clause 3: role-sequence preconditions, at MODEL load ---
#
# Both are defects of the MODEL, so they must fail at `gnd validate` before any
# population exists. Each fixture is otherwise well formed and trips exactly one
# of the two rules, so neither can pass by accidentally tripping the other or
# semantic:cross-ref.

ROLE_SEQ_ARITY = INVALID / "role_seq_arity.orm.yaml"
ROLE_SEQ_TYPE_COMPAT = INVALID / "role_seq_type_compat.orm.yaml"


def test_role_sequences_of_unequal_length_rejected():
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(ROLE_SEQ_ARITY)
    matching = [
        issue
        for issue in excinfo.value.issues
        if issue.rule_id == "semantic:role-seq-arity"
    ]
    assert matching, (
        f"expected semantic:role-seq-arity, got "
        f"{[i.rule_id for i in excinfo.value.issues]}"
    )
    assert all(issue.path == "$.constraints[0]" for issue in matching), (
        f"the issue path must name the offending constraint, got "
        f"{[i.path for i in matching]}"
    )
    assert all("equal arity" in issue.message for issue in matching), matching


def test_role_sequences_incompatible_at_a_position_rejected():
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(ROLE_SEQ_TYPE_COMPAT)
    matching = [
        issue
        for issue in excinfo.value.issues
        if issue.rule_id == "semantic:role-seq-type-compat"
    ]
    assert matching, (
        f"expected semantic:role-seq-type-compat, got "
        f"{[i.rule_id for i in excinfo.value.issues]}"
    )
    assert all(issue.path == "$.constraints[0]" for issue in matching), (
        f"the issue path must name the offending constraint, got "
        f"{[i.path for i in matching]}"
    )
    assert all("position 0" in issue.message for issue in matching), (
        f"the message must name WHICH position is incompatible: {matching}"
    )


def test_unequal_arity_is_reported_by_one_rule_not_two():
    """Sequences of different lengths have no comparable positions, so the
    position-wise rule stands down and the arity rule owns the defect. One
    defect, one name — otherwise a single mistake reads as two."""
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(ROLE_SEQ_ARITY)
    assert not [
        issue
        for issue in excinfo.value.issues
        if issue.rule_id == "semantic:role-seq-type-compat"
    ], excinfo.value.issues


def test_position_wise_rule_terminates_on_a_subtype_cycle(tmp_path):
    """T-01.1-07. `semantic:subtype-acyclic` does not exist — an `a <-> b`
    subtype cycle still validates at exit 0 today — so every traversal of the
    subtype graph must carry its own guard. This rule adds no second traversal:
    it reuses `_ancestor_closure`, whose cycle safety is therefore load-bearing
    here rather than defensive. A regression that replaced it with a naive walk
    would hang instead of failing, so this test asserts termination.
    """
    doc = {
        "version": 1,
        "source": {"kind": "text-conversation"},
        "object_types": [
            {
                "id": "a",
                "name": "A",
                "kind": "entity",
                "subtype_of": ["b"],
                "inherits_reference": True,
                "derivation": "asserted",
            },
            {
                "id": "b",
                "name": "B",
                "kind": "entity",
                "subtype_of": ["a"],
                "inherits_reference": True,
                "derivation": "asserted",
            },
        ],
        "fact_types": [
            {
                "id": "a_exists",
                "reading": "{A} exists",
                "roles": [{"object_type": "a", "role_name": "a"}],
            },
            {
                "id": "b_exists",
                "reading": "{B} exists",
                "roles": [{"object_type": "b", "role_name": "b"}],
            },
        ],
        "constraints": [
            {
                "type": "equality",
                "role_seq_a": [{"fact_type": "a_exists", "role": "a"}],
                "role_seq_b": [{"fact_type": "b_exists", "role": "b"}],
                "source": "user-supplied",
                "status": "confirmed",
                "modality": "alethic",
                "provenance": {"user_note": "cycle-termination fixture"},
            }
        ],
    }
    path = _dump_yaml(doc, tmp_path / "subtype_cycle.orm.yaml")

    # Terminates, and `a` and `b` are mutually reachable so they ARE compatible
    # under the one shared predicate — no false rejection either.
    model = load_model(path)
    assert not [
        w for w in model.warnings if w.rule_id.startswith("semantic:role-seq-")
    ], model.warnings


def test_setfam_sequence_constraints_are_not_falsely_rejected():
    """Blast-radius guard: all four of setfam's sequence-bearing constraints are
    matched-arity and position-wise compatible, so the two new rules must add no
    rejection to the in-tree fixtures they now scan."""
    model = load_model(CHECKER_FIXTURES / "setfam.orm.yaml")
    assert not [
        warning
        for warning in model.warnings
        if warning.rule_id.startswith("semantic:role-seq-")
    ], model.warnings


# --- D-20: alethic constraints in a never-checkable family (WARNING only) ---


def test_alethic_textual_constraint_warns_and_still_loads():
    """An alethic `textual` constraint makes its model permanently
    indeterminate — no population can ever reach exit 0. D-20 accepts that as
    correct and surfaces it at AUTHORING time. It must never become an error:
    that would reject every existing model carrying one."""
    model = load_model(CHECKER_FIXTURES / "misc.orm.yaml")
    warnings = [w for w in model.warnings if w.rule_id == "semantic:textual-alethic"]
    assert warnings, f"expected semantic:textual-alethic warning, got {model.warnings}"
    assert all(w.severity == "warning" for w in warnings)
    assert any("deontic" in w.message for w in warnings), (
        "the warning must point the author at the remedy, not merely complain"
    )
    assert any("exit 0" in w.message for w in warnings), (
        "the warning must state the consequence: this model can never be accepted"
    )


def test_alethic_textual_model_still_validates_at_exit_0():
    result = _run_cli("validate", str(CHECKER_FIXTURES / "misc.orm.yaml"))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "semantic:textual-alethic" in result.stdout
    assert "WARNING at" in result.stdout


def test_deontic_textual_constraint_does_not_warn(tmp_path):
    """The rule keys on MODALITY, not on the family alone — a deontic textual
    constraint is feedback-only and leaves the exit band untouched, so warning
    about it would be noise."""
    doc = _load_yaml(FULL_VOCABULARY)
    for constraint in doc["constraints"]:
        if constraint.get("type") == "textual":
            constraint["modality"] = "deontic"
    path = _dump_yaml(doc, tmp_path / "deontic_textual.orm.yaml")
    model = load_model(path)
    assert not [
        w for w in model.warnings if w.rule_id == "semantic:textual-alethic"
    ], model.warnings


# --- D-03: modality-policy WARNING (load succeeds, warning surfaced) ---


def test_modality_policy_fixture_loads_with_warning():
    model = load_model(INVALID / "modality_policy_warning.yaml")
    warnings = [w for w in model.warnings if w.rule_id == "semantic:modality-policy"]
    assert warnings, f"expected semantic:modality-policy warning, got {model.warnings}"
    assert all(w.severity == "warning" for w in warnings)
    assert any("deontic" in w.message for w in warnings), (
        "warning must explain the deontic-until-confirmed policy"
    )


def test_validation_issue_severity_defaults_to_error():
    issue = ValidationIssue(path="$", message="m", rule_id="semantic:x")
    assert issue.severity == "error"


def test_cli_validate_prints_warning_and_exits_0():
    result = _run_cli("validate", str(INVALID / "modality_policy_warning.yaml"))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "WARNING at" in result.stdout
    assert "semantic:modality-policy" in result.stdout


# --- WR-05: size cap and alias guard on model loading ---


def test_model_size_cap_enforced(tmp_path):
    path = tmp_path / "huge.orm.yaml"
    with open(path, "wb") as handle:
        handle.truncate(MAX_MODEL_BYTES + 1)
    with pytest.raises(ModelLoadError) as excinfo:
        load_model(path)
    assert "cap" in str(excinfo.value)


def test_model_yaml_aliases_rejected(tmp_path):
    path = tmp_path / "aliased.orm.yaml"
    path.write_text(
        "version: 1\nobject_types: &a []\nfact_types: *a\n", encoding="utf-8"
    )
    with pytest.raises(ModelLoadError) as excinfo:
        load_model(path)
    assert "alias" in str(excinfo.value)


def test_common_sense_constraint_requires_auditable_provenance(tmp_path):
    path = tmp_path / "missing-common-sense-provenance.orm.yaml"
    path.write_text(
        """version: 1
object_types:
  - {id: age, kind: value, primitive: Integer}
fact_types: []
constraints:
  - type: value
    object_type: age
    range: {min: 0}
    source: common-sense
    status: proposed
    modality: deontic
    rationale: Ages are non-negative.
""",
        encoding="utf-8",
    )

    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)

    assert any(
        issue.rule_id == "jsonschema:required" and "provenance" in issue.message
        for issue in excinfo.value.issues
    )


def test_model_load_error_cli_exits_3(tmp_path):
    path = tmp_path / "aliased.orm.yaml"
    path.write_text(
        "version: 1\nobject_types: &a []\nfact_types: *a\n", encoding="utf-8"
    )
    result = _run_cli("validate", str(path))
    assert result.returncode == 3, result.stdout + result.stderr


# --- no regression: reference models stay clean ---


def test_full_vocabulary_warns_only_about_its_alethic_textual_constraint():
    """This test asserted `model.warnings == []` until D-20 landed.

    It is REPORTED, not loosened: `full_vocabulary.orm.yaml` carries an alethic
    `textual` constraint ("Each Employee who heads a Department must be a
    PermanentEmployee"), so under D-20 the fixture genuinely is permanently
    indeterminate and the new warning is a true statement about it. The fixture
    keeps its modality — it exists to exercise the full vocabulary, and
    rewriting it to deontic would have silenced the finding rather than
    recording it.

    The gate is not weakened: every OTHER semantic rule must still leave this
    model warning-free, which is what the reference-models-stay-clean test was
    protecting.
    """
    model = load_model(FULL_VOCABULARY)
    unexpected = [w for w in model.warnings if w.rule_id != "semantic:textual-alethic"]
    assert unexpected == [], (
        f"the full-vocabulary reference model must carry no warning other than "
        f"the D-20 textual-alethic one: {unexpected}"
    )
    assert [w.rule_id for w in model.warnings] == ["semantic:textual-alethic"], (
        f"expected exactly one D-20 warning, got {model.warnings}"
    )


def test_skeleton_model_loads_with_no_warnings():
    model = load_model(SKELETON_MODEL)
    assert model.warnings == []
