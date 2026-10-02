"""Population loader tests: both validation layers wired into the ONE loader (D-11).

Layer 1 (D-10): the population interchange format has its own Draft 2020-12
schema (``src/gnd/schema/population.schema.json``). ``load_population`` validates
the parsed document against it BEFORE constructing :class:`Population`, raising
:class:`PopulationValidationError` with pointed ``json_path`` errors — the same
unified :class:`ValidationIssue` record shape the model loader uses.

Layer 2 (CORE-04): model-relative structural conformance, run only when a
``model`` is supplied. The layer-1 rejection tests below deliberately load
WITHOUT a model — that is the shape they are testing, they raise before any
model could matter, and D-02 explicitly keeps ``model`` optional because loading
a population before a model is resolved is legitimate. What makes that safe is
the D-02 marker: a population loaded without a model is refused by ``check()``,
which ``test_check_refuses_a_population_loaded_without_a_model`` asserts.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
from pydantic import ValidationError as PydanticValidationError

from gnd.checker import UnvalidatedPopulationError, check
from gnd.model import Model, load_model
from gnd.population import (
    MAX_POPULATION_BYTES,
    Population,
    PopulationLoadError,
    PopulationValidationError,
    load_population,
)

FIXTURES = Path(__file__).parent / "fixtures" / "skeleton"

MODEL = FIXTURES / "model.orm.yaml"
POP_GOOD_YAML = FIXTURES / "population.good.yaml"
POP_GOOD_JSON = FIXTURES / "population.good.json"


def _write(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


# --- valid documents load (YAML and JSON alike) ---


def test_valid_yaml_loads():
    population = load_population(POP_GOOD_YAML, model=load_model(MODEL))
    assert population.model == "model.orm.yaml"
    assert population.source == "fixture"
    assert population.facts["movie_has_title"]


def test_valid_json_loads():
    population = load_population(POP_GOOD_JSON, model=load_model(MODEL))
    assert population.source == "fixture"
    assert population.instances == {"movie": [1, 2]}


def test_yaml_json_parity():
    model = load_model(MODEL)
    assert load_population(POP_GOOD_YAML, model=model) == load_population(
        POP_GOOD_JSON, model=model
    )


# --- WR-04: parity must hold on REJECTION too, not only on acceptance ---
#
# Parity is asserted on the EXIT CODE, not on the exception type. The two front
# ends legitimately reject through different mechanisms — ruamel raises
# DuplicateKeyError from its constructor, the JSON hook raises
# PopulationLoadError, a type mismatch raises PopulationValidationError — and
# D-11's claim is about what a CALLER observes, which is the band.

FLOAT_MODEL = (
    Path(__file__).parent / "fixtures" / "adversarial" / "models" / "float_range.orm.yaml"
)


def _parity_pair(tmp_path, yaml_fact: str, json_fact: str):
    """The same logical document in both renderings, as raw TEXT — the defects
    under test are PARSER-level, so neither side may be built from a dict."""
    yaml_path = _write(
        tmp_path,
        "pair.yaml",
        "population:\n  model: float_range.orm.yaml\n  source: agent-output\n"
        f"facts:\n  reading_has_celsius:\n    - {yaml_fact}\n",
    )
    json_path = _write(
        tmp_path,
        "pair.json",
        '{"population": {"model": "float_range.orm.yaml", "source": "agent-output"}, '
        f'"facts": {{"reading_has_celsius": [{json_fact}]}}}}',
    )
    return yaml_path, json_path


def _band(path) -> int:
    import gnd.cli

    return gnd.cli.main(["check", str(FLOAT_MODEL), str(path), "--format", "json"])


def test_a_duplicate_role_key_is_rejected_by_both_front_ends(tmp_path, capsys):
    """ruamel rejects a duplicate mapping key; `json.load` silently keeps the
    LAST one. Logically identical documents therefore produced OPPOSITE
    outcomes — exit 3 as YAML, exit 0 as JSON with one of the two values
    discarded, no issue and no warning. An agent emitting a duplicated role was
    told its output was accepted."""
    yaml_path, json_path = _parity_pair(
        tmp_path,
        '{ reading: "R1", celsius: 1.0, reading: "R2" }',
        '{"reading": "R1", "celsius": 1.0, "reading": "R2"}',
    )
    assert _band(yaml_path) == 3, "the YAML side must reject (it always did)"
    assert _band(json_path) == 3, (
        "the JSON side silently collapsed the duplicate and exited 0 — the "
        "divergence WR-04 names"
    )
    capsys.readouterr()


@pytest.mark.parametrize(
    ("yaml_literal", "json_literal"),
    [(".nan", "NaN"), (".inf", "Infinity"), ("-.inf", "-Infinity")],
    ids=["nan", "inf", "-inf"],
)
def test_non_finite_numbers_are_rejected_by_both_front_ends(
    tmp_path, capsys, yaml_literal, json_literal
):
    """CR-04's parity half. `json.load`'s default `parse_constant` accepts all
    three tokens and jsonschema's `"type": "number"` admits them, so the JSON
    front end fed a NaN into the same false pass its YAML sibling allowed —
    `celsius` here carries an alethic range, and a NaN satisfied it."""
    yaml_path, json_path = _parity_pair(
        tmp_path,
        f'{{ reading: "R1", celsius: {yaml_literal} }}',
        f'{{"reading": "R1", "celsius": {json_literal}}}',
    )
    assert _band(yaml_path) == 3
    assert _band(json_path) == 3
    capsys.readouterr()


# --- invalid shape classes are rejected with pointed json_path errors ---


def test_missing_population_header_rejected(tmp_path):
    path = _write(tmp_path, "no_header.yaml", "facts: {}\n")
    with pytest.raises(PopulationValidationError) as excinfo:
        load_population(path)
    issues = excinfo.value.issues
    assert issues, "schema rejection must carry ValidationIssue records"
    assert any(issue.path == "$" for issue in issues)
    assert all(issue.rule_id.startswith("jsonschema:") for issue in issues)


def test_missing_population_source_rejected(tmp_path):
    path = _write(
        tmp_path,
        "no_source.yaml",
        "population:\n  model: model.orm.yaml\nfacts: {}\n",
    )
    with pytest.raises(PopulationValidationError) as excinfo:
        load_population(path)
    assert any(
        "$.population" in issue.path and "source" in issue.message
        for issue in excinfo.value.issues
    ), f"error must point at $.population and name 'source': {excinfo.value.issues}"


def test_bad_source_enum_rejected(tmp_path):
    path = _write(
        tmp_path,
        "bad_source.yaml",
        "population:\n  model: model.orm.yaml\n  source: guesswork\nfacts: {}\n",
    )
    with pytest.raises(PopulationValidationError) as excinfo:
        load_population(path)
    assert any("$.population.source" in issue.path for issue in excinfo.value.issues)


def test_facts_not_mapping_rejected(tmp_path):
    path = _write(
        tmp_path,
        "facts_list.yaml",
        "population:\n  model: m\n  source: fixture\nfacts:\n  - oops\n",
    )
    with pytest.raises(PopulationValidationError) as excinfo:
        load_population(path)
    assert any(issue.path == "$.facts" for issue in excinfo.value.issues)


def test_facts_value_not_list_rejected(tmp_path):
    path = _write(
        tmp_path,
        "facts_scalar_value.yaml",
        "population:\n  model: m\n  source: fixture\nfacts:\n  movie_has_title: { movie: 1 }\n",
    )
    with pytest.raises(PopulationValidationError) as excinfo:
        load_population(path)
    assert any("$.facts.movie_has_title" in issue.path for issue in excinfo.value.issues)


def test_facts_item_not_mapping_rejected(tmp_path):
    path = _write(
        tmp_path,
        "facts_scalar_item.yaml",
        "population:\n  model: m\n  source: fixture\nfacts:\n  movie_has_title: [1, 2]\n",
    )
    with pytest.raises(PopulationValidationError) as excinfo:
        load_population(path)
    assert any("$.facts.movie_has_title[0]" in issue.path for issue in excinfo.value.issues)


def test_unknown_top_level_key_rejected(tmp_path):
    path = _write(
        tmp_path,
        "typo_key.yaml",
        "population:\n  model: m\n  source: fixture\nfacts: {}\nfactz: {}\n",
    )
    with pytest.raises(PopulationValidationError):
        load_population(path)


def test_json_documents_are_schema_validated_too(tmp_path):
    path = _write(tmp_path, "no_source.json", '{"population": {"model": "m"}, "facts": {}}')
    with pytest.raises(PopulationValidationError) as excinfo:
        load_population(path)
    assert any("$.population" in issue.path for issue in excinfo.value.issues)


# --- error-hierarchy and size-cap invariants ---


def test_validation_error_is_a_load_error():
    assert issubclass(PopulationValidationError, PopulationLoadError)


def test_size_cap_still_enforced(tmp_path):
    path = tmp_path / "huge.yaml"
    with open(path, "wb") as handle:
        handle.truncate(MAX_POPULATION_BYTES + 1)
    with pytest.raises(PopulationLoadError) as excinfo:
        load_population(path)
    assert "cap" in str(excinfo.value)


def test_yaml_aliases_rejected_before_expansion(tmp_path):
    """WR-05 (T-01-02): the byte cap does not bound alias amplification — a
    well-under-cap aliased document must be rejected before node construction."""
    path = tmp_path / "aliased.yaml"
    path.write_text(
        "population:\n"
        "  model: m.orm.yaml\n"
        "  source: fixture\n"
        "facts:\n"
        "  ft_a: &bomb [{r: '1'}]\n"
        "  ft_b: *bomb\n",
        encoding="utf-8",
    )
    with pytest.raises(PopulationLoadError) as excinfo:
        load_population(path)
    assert "alias" in str(excinfo.value)


# --- CORE-04 layer 2: model-relative structural conformance ---


def _movie_model() -> Model:
    """The probe-#1 shape: one binary fact type declaring `movie` and `title`."""
    return Model(
        version=1,
        object_types=[
            {"id": "movie", "name": "Movie", "kind": "entity"},
            {"id": "title", "name": "Title", "kind": "value", "primitive": "String"},
        ],
        fact_types=[
            {
                "id": "movie_has_title",
                "reading": "{Movie} has title {Title}",
                "roles": [
                    {"object_type": "movie", "role_name": "movie"},
                    {"object_type": "title", "role_name": "title"},
                ],
            }
        ],
    )


def _movie_population(tmp_path: Path, facts_block: str, name: str = "pop.yaml") -> Path:
    return _write(
        tmp_path,
        name,
        "population:\n  model: m.orm.yaml\n  source: agent-output\n" + facts_block,
    )


def test_layer2_rejects_a_fact_omitting_a_declared_role(tmp_path):
    path = _movie_population(
        tmp_path, "facts:\n  movie_has_title:\n    - { title: A }\n"
    )
    with pytest.raises(PopulationValidationError) as excinfo:
        load_population(path, model=_movie_model())
    assert any(
        issue.rule_id == "population:missing-role" for issue in excinfo.value.issues
    ), f"expected population:missing-role, got {excinfo.value.issues}"


def test_layer2_does_not_run_without_a_model(tmp_path):
    """D-02 deliberately keeps `model` optional: loading a population before a
    model is resolved is legitimate. The guarantee comes from the marker, not
    from forcing the parameter."""
    path = _movie_population(
        tmp_path, "facts:\n  movie_has_title:\n    - { title: A }\n"
    )
    population = load_population(path)
    assert population.validated_against is None


def test_layer2_runs_after_the_alias_guard(tmp_path):
    """T-01.1-05 ordering: an aliased document must trip the parse-event guard,
    NOT produce a layer-2 issue list. Layer 2 must never be the reason a
    billion-laughs document gets parsed."""
    path = _write(
        tmp_path,
        "aliased_with_model.yaml",
        "population:\n"
        "  model: m.orm.yaml\n"
        "  source: agent-output\n"
        "facts:\n"
        "  movie_has_title: &bomb [{ title: A }]\n"
        "  nope: *bomb\n",
    )
    with pytest.raises(PopulationLoadError) as excinfo:
        load_population(path, model=_movie_model())
    assert "alias" in str(excinfo.value)
    assert not isinstance(excinfo.value, PopulationValidationError), (
        "the alias guard must fire before layer 2, so this is not a validation "
        "error with an issue list"
    )


def test_layer2_runs_after_the_size_cap(tmp_path):
    path = tmp_path / "huge_with_model.yaml"
    with open(path, "wb") as handle:
        handle.truncate(MAX_POPULATION_BYTES + 1)
    with pytest.raises(PopulationLoadError) as excinfo:
        load_population(path, model=_movie_model())
    assert "cap" in str(excinfo.value)
    assert not isinstance(excinfo.value, PopulationValidationError)


def test_layer2_never_opens_the_population_model_header(tmp_path):
    """T-01.1-01 / T-01-05: `population.model` is attacker-controlled metadata
    naming a path. Layer 2 reads it as opaque data; nothing resolves it."""
    absent = tmp_path / "definitely-absent" / "secret.orm.yaml"
    path = _write(
        tmp_path,
        "header_path.yaml",
        f"population:\n  model: {absent}\n  source: agent-output\n"
        "facts:\n  movie_has_title:\n    - { movie: 1, title: A }\n",
    )
    population = load_population(path, model=_movie_model())
    assert population.model == str(absent)
    assert not absent.exists(), "the loader must not have created or required it"


# --- D-02: the validated_against marker makes skipping layer 2 impossible ---


def test_check_refuses_a_population_built_through_the_public_constructor():
    model = _movie_model()
    population = Population(model="m.orm.yaml", source="agent-output")
    with pytest.raises(UnvalidatedPopulationError):
        check(model, population)


def test_check_refuses_a_population_loaded_without_a_model(tmp_path):
    """The reason the layer-1 rejection tests above may load without a model:
    such a population cannot be checked."""
    path = _movie_population(
        tmp_path, "facts:\n  movie_has_title:\n    - { movie: 1, title: A }\n"
    )
    population = load_population(path)
    with pytest.raises(UnvalidatedPopulationError):
        check(_movie_model(), population)


def test_check_accepts_a_population_loaded_with_its_model(tmp_path):
    model = _movie_model()
    path = _movie_population(
        tmp_path, "facts:\n  movie_has_title:\n    - { movie: 1, title: A }\n"
    )
    population = load_population(path, model=model)
    assert population.validated_against is model
    assert check(model, population).verdicts is not None


def test_check_refuses_a_different_but_equal_model(tmp_path):
    """Identity, never equality: Pydantic compares by field values, so two
    independent loads of the same file compare equal. Accepting that would let
    a population validated against one model be checked against another."""
    first, second = _movie_model(), _movie_model()
    assert first == second, "the two models must be equal for this test to bite"
    path = _movie_population(
        tmp_path, "facts:\n  movie_has_title:\n    - { movie: 1, title: A }\n"
    )
    population = load_population(path, model=first)
    with pytest.raises(UnvalidatedPopulationError):
        check(second, population)


def test_marker_cannot_be_forged_through_the_constructor():
    model = _movie_model()
    population = Population(
        model="m.orm.yaml", source="agent-output", _validated_against=model
    )
    assert population.validated_against is None, (
        "a _validated_against kwarg must be silently ignored, never honoured"
    )
    with pytest.raises(UnvalidatedPopulationError):
        check(model, population)


def test_marker_is_invisible_to_model_dump(tmp_path):
    """The marker must never round-trip into a serialized population file."""
    model = _movie_model()
    path = _movie_population(
        tmp_path, "facts:\n  movie_has_title:\n    - { movie: 1, title: A }\n"
    )
    population = load_population(path, model=model)
    dumped = population.model_dump()
    assert "_validated_against" not in dumped
    assert "validated_against" not in dumped
    assert "_validated_against" not in population.model_dump_json()


def test_deep_copy_fails_closed(tmp_path):
    """Pitfall 3: a deep copy deep-copies the referenced Model, so `is` no
    longer holds. That direction is correct — document it, do not defeat it."""
    model = _movie_model()
    path = _movie_population(
        tmp_path, "facts:\n  movie_has_title:\n    - { movie: 1, title: A }\n"
    )
    population = load_population(path, model=model)

    assert population.model_copy().validated_against is model, (
        "a shallow copy keeps the marker's identity"
    )
    with pytest.raises(UnvalidatedPopulationError):
        check(model, copy.deepcopy(population))


# --- CR-01: the marker attests to CONTENT, not merely to a model object ---
#
# Every test below loads a CONFORMING population cleanly and then mutates it,
# which is precisely the Phase 2 DATA-01 workflow (load conforming, inject a
# violation, re-check). Before CR-01 each of these produced
# `pass=2 fail=0 warning=0 unchecked=0 vacuous=0` at exit 0 with
# "Each movie must play the 'movie' role in 'movie_has_title' — satisfied."
# over facts layer 2 never saw: CONTEXT.md probe #1, restored verbatim.


def _loaded_conforming(tmp_path):
    model = _movie_model()
    path = _movie_population(
        tmp_path,
        "facts:\n  movie_has_title:\n    - { movie: 1, title: A }\n"
        "    - { movie: 2, title: B }\n",
    )
    return model, load_population(path, model=model)


def test_population_is_frozen_against_attribute_assignment(tmp_path):
    """The COMMON mutation is an immediate error, not a silent pass. This is the
    first of the two CR-01 mechanisms; on its own it is not sufficient (see the
    nested-mutation and model_copy tests below), which is why the digest exists."""
    _, population = _loaded_conforming(tmp_path)
    with pytest.raises(PydanticValidationError) as excinfo:
        population.facts = {"movie_has_title": [{"title": "A"}]}
    assert "frozen" in str(excinfo.value).lower()


def test_check_refuses_a_population_whose_nested_facts_were_mutated(tmp_path):
    """`frozen=True` does NOT freeze the nested containers, so this route stays
    open to attribute-level immutability alone — the digest is what closes it."""
    model, population = _loaded_conforming(tmp_path)
    check(model, population)  # accepted before the mutation — must not raise

    population.facts["movie_has_title"].append({"title": "C"})  # omits `movie`

    with pytest.raises(UnvalidatedPopulationError) as excinfo:
        check(model, population)
    assert "content has changed" in str(excinfo.value)


def test_check_refuses_a_population_mutated_through_model_copy_update(tmp_path):
    """`model_copy(update=...)` replaces fields while PRESERVING private
    attributes, so the copy carried a valid-looking marker over content layer 2
    never saw. The docstring that reasoned about `model_copy()` and
    `model_copy(deep=True)` did not consider this third form."""
    model, population = _loaded_conforming(tmp_path)
    forged = population.model_copy(
        update={"facts": {"movie_has_title": [{"title": "A"}, {"title": "B"}]}}
    )
    assert forged.validated_against is model, (
        "the model reference alone still looks valid — which is the defect"
    )
    with pytest.raises(UnvalidatedPopulationError):
        check(model, forged)


def test_check_refuses_a_population_whose_roster_or_covers_were_mutated(tmp_path):
    """The digest covers every field layer 2 validated, not only `facts`."""
    model, population = _loaded_conforming(tmp_path)
    population.covers.append("movie_has_title")
    with pytest.raises(UnvalidatedPopulationError):
        check(model, population)


def test_model_is_frozen_against_attribute_assignment(tmp_path):
    model, _ = _loaded_conforming(tmp_path)
    with pytest.raises(PydanticValidationError) as excinfo:
        model.constraints = []
    assert "frozen" in str(excinfo.value).lower()


def test_check_refuses_a_population_after_nested_model_mutation(tmp_path):
    """The marker binds model content, not only the Model object's identity."""
    model, population = _loaded_conforming(tmp_path)
    check(model, population)

    model.fact_types[0]["roles"].append(
        {"object_type": "title", "role_name": "required_after_validation"}
    )

    assert not population.matches_validation_marker(model)
    with pytest.raises(UnvalidatedPopulationError):
        check(model, population)


def test_an_unmutated_shallow_copy_still_checks(tmp_path):
    """The guard must not fail CLOSED on identical content: `model_copy()` is a
    legitimate operation and its digest is equal by construction."""
    model, population = _loaded_conforming(tmp_path)
    assert check(model, population.model_copy()).counts()["fail"] == 0


def test_restoring_the_original_content_restores_the_marker(tmp_path):
    """The digest attests to CONTENT. Content restored ⇒ marker valid again —
    stating the property precisely so a future reader does not mistake it for
    a one-shot tripwire."""
    model, population = _loaded_conforming(tmp_path)
    original = list(population.facts["movie_has_title"])
    population.facts["movie_has_title"].append({"title": "C"})
    with pytest.raises(UnvalidatedPopulationError):
        check(model, population)
    population.facts["movie_has_title"][:] = original
    assert check(model, population).counts()["fail"] == 0


def test_unvalidated_error_message_states_there_is_no_bypass():
    """The message is the only guidance a harness author gets at exit 70."""
    with pytest.raises(UnvalidatedPopulationError) as excinfo:
        check(_movie_model(), Population(model="m.orm.yaml", source="agent-output"))
    message = str(excinfo.value)
    assert "load_population(path, model=model)" in message
    assert "no bypass" in message
    assert "deep" in message.lower()


def test_warnings_field_defaults_empty_and_is_public(tmp_path):
    """Unlike the marker, warnings are user-facing output and belong in the
    payload — the same channel Model.warnings uses."""
    model = _movie_model()
    path = _movie_population(
        tmp_path, "facts:\n  movie_has_title:\n    - { movie: 1, title: A }\n"
    )
    population = load_population(path, model=model)
    assert population.warnings == []
    assert "warnings" in population.model_dump()
