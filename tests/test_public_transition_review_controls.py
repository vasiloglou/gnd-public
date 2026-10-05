"""Regression tests for the phase-2 adversarial review (codex gpt-5.6-sol, xhigh).

One test per finding, each written to FAIL against the code as reviewed and to
pass after the fix. The review's own reproductions are reproduced here rather
than trusted: a finding believed without being run is a finding that might not
exist.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML

from gnd import transition
from gnd.model import dynamic_subject_is_functional, load_model

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS = REPO_ROOT / "tests" / "fixtures" / "public-transition-contract"
MODEL = CORPUS / "v2_expense.orm.yaml"


# --------------------------------------------------------------------------- #
# 1 (high) -- the `=` operator the schema admits
# --------------------------------------------------------------------------- #


def test_every_operator_the_schema_admits_is_implemented() -> None:
    """The schema's enum is the contract; the evaluator must cover all of it.

    `=` was missing, and the failure mode was the bad one: an unregistered
    operator fell into the same branch as a violated comparison, so a legal rule
    reported a FAILURE on a walk that satisfied it.
    """
    schema = json.loads((REPO_ROOT / "src" / "gnd" / "schema" / "orm-meta.schema.json").read_text())
    op_schema = schema["$defs"]["dynamic_rule"]["properties"]["op"]
    enum = set(schema["$defs"][op_schema["$ref"].removeprefix("#/$defs/")]["enum"])
    assert enum <= set(transition._COMPARISONS), (
        f"the evaluator implements {sorted(transition._COMPARISONS)} but the schema "
        f"admits {sorted(enum)}; missing {sorted(enum - set(transition._COMPARISONS))}"
    )


@pytest.mark.parametrize(
    ("op", "new", "old", "holds"),
    [
        ("=", 500, 500, True),
        ("=", 501, 500, False),
        ("!=", 501, 500, True),
        ("!=", 500, 500, False),
        (">", 501, 500, True),
        (">", 500, 500, False),
        (">=", 500, 500, True),
        (">=", 499, 500, False),
        ("<", 499, 500, True),
        ("<", 500, 500, False),
        ("<=", 500, 500, True),
        ("<=", 501, 500, False),
    ],
)
def test_each_operator_has_a_satisfied_and_a_violated_case(
    op: str, new: int, old: int, holds: bool
) -> None:
    """Both directions per operator. A table with only the failing side cannot
    tell a correct comparison from one that always reports a violation."""
    assert transition._COMPARISONS[op](new, old) is holds


def test_an_unknown_operator_is_not_silently_a_failure() -> None:
    """Layer 1 makes this unreachable, so it must be loud if it ever happens.

    The reviewed code folded "operator not implemented" into the same branch as
    "comparison violated", which is how a missing implementation reports as a
    finding about someone's data.
    """
    with pytest.raises(transition.UnknownComparisonError):
        transition._compare_values("~=", 1, 0)


# --------------------------------------------------------------------------- #
# 2 (high) -- functional subjects, and the roles the subject actually binds
# --------------------------------------------------------------------------- #

_ORDER_MODEL = """
version: 2
model_id: "urn:gnd-fixture:transition-order@1"
source: { kind: explicit, confidence: high }
object_types:
  - { id: a_id, name: AId, kind: value, primitive: Integer }
  - { id: b_id, name: BId, kind: value, primitive: String }
  - { id: v_id, name: VId, kind: value, primitive: Integer }
fact_types:
  - id: f
    reading: "{AId} and {BId} have value {VId}"
    roles:
      - { object_type: a_id, role_name: a }
      - { object_type: b_id, role_name: b }
      - { object_type: v_id, role_name: v }
    constraints:
      - id: one_v_per_a_b
        type: uniqueness
        scope: internal
        roles: [a, b]
        source: explicit
        status: confirmed
        modality: alethic
        provenance: { csdp_step: 4 }
operations:
  - id: bump
    reading: "{AId} is bumped"
    parameters:
      - { name: a, object_type: a_id }
    effects:
      - assert: { fact_type: f, bind: { a: "$a", b: "x", v: 20 } }
    dynamic_rules:
      - id: only_rises
        subject: { fact_type: f, value_role: v, bind: { a: "$a" } }
        op: ">"
        modality: alethic
        source: user-supplied
        status: confirmed
        provenance: { added_at_step: 7d }
    frame: { modality: alethic }
    source: explicit
    status: confirmed
    provenance: { csdp_step: 7, dialogue_turn: 1 }
"""


def test_a_subject_that_does_not_bind_its_uniqueness_key_is_not_functional(tmp_path) -> None:
    """ "Old versus new" presupposes ONE old value.

    A uniqueness key over (a, b) proves the fact type functional in (a, b) --
    it proves nothing about a subject that binds only `a`, which can match two
    facts with two different values. The reviewed code asked whether SOME key
    existed among the non-value roles, so it answered yes, and `_subject_value`
    then returned whichever fact happened to come first: the same fact SET gave
    a finding in one order and none in the other.
    """
    path = tmp_path / "order.orm.yaml"
    path.write_text(_ORDER_MODEL, encoding="utf-8")
    model = load_model(path)
    subject = model.operations[0]["dynamic_rules"][0]["subject"]
    assert dynamic_subject_is_functional(subject, model.fact_types) is False, (
        "a subject binding only `a` under a uniqueness key over (a, b) does not "
        "determine one value, so it cannot be compared old-against-new"
    )
    assert any(warning.rule_id == "semantic:op-dynamic-functional" for warning in model.warnings), (
        "the authoring-time warning must fire for the same reason"
    )


def test_the_corpus_subjects_are_still_functional() -> None:
    """The other direction: the tightened rule must not start refusing subjects
    that genuinely do determine one value, or every corpus band-2 and band-4
    walk changes meaning."""
    model = load_model(MODEL)
    for operation in model.operations:
        for rule in operation.get("dynamic_rules") or []:
            subject = rule["subject"]
            functional = dynamic_subject_is_functional(subject, model.fact_types)
            expected = operation["id"] not in {"tag_expense", "annotate_expense"}
            assert functional is expected, (
                f"{operation['id']}.{rule['id']} changed functionality verdict"
            )


# --------------------------------------------------------------------------- #
# 3 (high) -- a sole asserter cannot prove history
# --------------------------------------------------------------------------- #

_RETRACTING_MODEL = """
version: 2
model_id: "urn:gnd-fixture:transition-retracting@1"
source: { kind: explicit, confidence: high }
object_types:
  - { id: thing_id, name: ThingId, kind: value, primitive: Integer }
fact_types:
  - id: a
    reading: "{ThingId} is a"
    roles:
      - { object_type: thing_id, role_name: x }
  - id: b
    reading: "{ThingId} is b"
    roles:
      - { object_type: thing_id, role_name: x }
operations:
  - id: make_b
    reading: "{ThingId} becomes b"
    parameters:
      - { name: x, object_type: thing_id }
    preconditions:
      - id: need_a
        require:
          - { fact_type: a, bind: { x: "$x" } }
        modality: alethic
        source: explicit
        status: confirmed
        provenance: { csdp_step: 7, dialogue_turn: 1 }
    effects:
      - assert: { fact_type: b, bind: { x: "$x" } }
      - retract: { fact_type: a, bind: { x: "$x" } }
    frame: { modality: alethic }
    source: explicit
    status: confirmed
    provenance: { csdp_step: 7, dialogue_turn: 1 }
"""


def test_an_obligation_whose_required_fact_can_be_retracted_does_not_compile(tmp_path) -> None:
    """A sole asserter of B does not make "every B has an A" DURABLE.

    `make_b` requires A, asserts B and retracts A in the same step. The step is
    entirely legal, and the state it produces -- B present, A gone -- breaks the
    claim the compiler derived from it. Run the same walk twice and the second
    run reports an alethic failure against a state its own operation produced.

    Trace compilation lifts a precondition into a claim about data at rest, and
    that lift is only sound while nothing removes the evidence. The guard now
    requires BOTH: exactly one asserter of the fact type the claim generalizes
    over, and no operation anywhere in the model that retracts the fact type the
    claim requires.
    """
    path = tmp_path / "retracting.orm.yaml"
    path.write_text(_RETRACTING_MODEL, encoding="utf-8")
    model = load_model(path)
    entries = model.compiled_obligations("make_b")
    assert entries, "the obligation vanished entirely -- it should be RETAINED, not dropped"
    entry = entries[0]
    assert "subset" not in entry, (
        "an obligation whose required fact type is retracted by some operation "
        "was compiled into a standing claim its own operation falsifies"
    )
    assert "retract" in str(entry.get("transition-only", "")), entry


def test_the_corpus_obligations_still_compile() -> None:
    """The other direction, on the model the corpus is built from: nothing
    retracts `expense_submitted_to_workday` or `expense_approved_by`, so both
    obligations survive the tightened guard and finding class 8 stays
    observable."""
    model = load_model(MODEL)
    compiled = {
        entry["obligation"]: entry for entry in model.compiled_obligations("reimburse_expense")
    }
    assert "subset" in compiled["pre_submitted"]
    assert "subset" in compiled["pre_has_approver"]


# --------------------------------------------------------------------------- #
# 4 (medium) -- freshness must not depend on the intermediate state loading
# --------------------------------------------------------------------------- #


def test_create_freshness_still_fires_when_the_previous_state_could_not_be_loaded() -> None:
    """A band-4 verdict must not SUPPRESS a band-1 one.

    When an intermediate state cannot be re-loaded the walk continues -- and the
    reviewed code continued with `population=None`, which made every later
    create look fresh. So a walk that re-mints an existing identifier after a
    large intermediate reported only "could not check that state" and lost the
    collision entirely: band 1 disappearing behind band 4 is the wrong direction
    for a finding to move.

    Instance identity now comes from the STATE, which is always available,
    rather than from a Population that may not be.
    """
    model = load_model(MODEL)
    operation = next(op for op in model.operations if op["id"] == "submit_expense_to_workday")
    state = {
        "expense_has_status": [{"expense": 41, "status": "approved"}],
        "expense_submitted_to_workday": [{"expense": 42, "submission": "WD-8000"}],
    }
    step = {
        "op": "submit_expense_to_workday",
        "bindings": {"expense": 41, "submission": "WD-8000", "chain": "c-1"},
    }
    result, _ = transition._evaluate_step(1, step, operation, model, state, None)
    kinds = [verdict.kind for verdict in result.verdicts]
    assert "create-freshness" in kinds, (
        f"re-minting the existing submission WD-8000 produced {kinds} with no "
        f"freshness finding, because the previous state was not a loadable "
        f"Population"
    )


# --------------------------------------------------------------------------- #
# 5 (medium) -- the loader is total over caller-supplied bytes, or it is not
# --------------------------------------------------------------------------- #


def _steps_document(binding_literal: str) -> str:
    """A structurally valid walk whose one binding is a hostile number."""
    zeros = "0" * 64
    return (
        '{"steps_schema": 1, "model": "m", '
        f'"model_digest": "sha256:{zeros}", '
        f'"operations_digest": "sha256:{zeros}", '
        '"steps": [{"op": "x", "bindings": {"n": ' + binding_literal + "}}]}"
    )


@pytest.mark.parametrize(
    ("body", "why"),
    [
        (
            _steps_document("1" * 5000),
            "a 5000-digit integer: json.loads raises ValueError, not JSONDecodeError",
        ),
        (
            _steps_document("NaN"),
            "NaN is not JSON, and json.loads accepts it by default",
        ),
    ],
)
def test_the_steps_loader_refuses_hostile_numbers_rather_than_raising(
    body: str, why: str, tmp_path: Path
) -> None:
    """Totality belongs to the function (design rule 1).

    These bytes reach the loader from a caller and no layer 1 has run over them
    anywhere else in the process, so every malformed shape must produce a
    refusal with a rule id. `json.JSONDecodeError` was caught and `ValueError`
    was not -- and the digit limit raises the latter.
    """
    path = tmp_path / "steps.json"
    path.write_text(body, encoding="utf-8")
    with pytest.raises(transition.TransitionLoadError) as raised:
        transition.read_steps_document(path)
    assert [issue.rule_id for issue in raised.value.issues] == ["transition:steps-shape"], why


def test_an_oversized_steps_file_is_refused_without_being_read_whole(tmp_path: Path) -> None:
    """The cap must bound what is READ, not merely what is accepted.

    Checking `len(raw)` after `read_bytes()` means the whole file is already in
    memory by the time the cap fires -- which is not a cap, it is a report.
    """
    path = tmp_path / "huge.json"
    path.write_text("[" + "0," * (transition.MAX_STEPS_BYTES // 2) + "0]", encoding="utf-8")
    assert path.stat().st_size > transition.MAX_STEPS_BYTES
    with pytest.raises(transition.TransitionLoadError) as raised:
        transition.read_steps_document(path)
    assert [issue.rule_id for issue in raised.value.issues] == ["transition:steps-too-large"]


# --------------------------------------------------------------------------- #
# 7 (low) -- the digest must not silently discard content
# --------------------------------------------------------------------------- #


def test_a_non_string_mapping_key_is_refused_rather_than_coerced() -> None:
    """The date coercion is deliberate and documented; this one is not.

    YAML admits a numeric mapping key, and layer 1 and layer 2 both accept one
    inside `provenance`. Stringifying it made two DIFFERENT operations sections
    hash identically -- `{1: "a", "1": "b"}` and `{"1": "b"}` -- which is not a
    spelling difference, it is content disappearing.
    """
    with pytest.raises(transition.TransitionLoadError) as raised:
        transition.operations_digest([{"id": "op", "provenance": {1: "a", "1": "b"}}])
    assert [issue.rule_id for issue in raised.value.issues] == [
        "transition:operations-digest-unrepresentable"
    ]


# --------------------------------------------------------------------------- #
# 8 (low) -- the tests' own gaps
# --------------------------------------------------------------------------- #


def _threshold_step(op_spelling: str, new_value: int) -> tuple[Any, dict[str, Any], Any]:
    model = load_model(MODEL)
    operation = dict(next(o for o in model.operations if o["id"] == "raise_chain_threshold"))
    rule = dict(operation["dynamic_rules"][0])
    rule["op"] = op_spelling
    operation["dynamic_rules"] = [rule]
    state = {"chain_has_threshold": [{"chain": "c-1", "threshold": 500}]}
    step = {
        "op": "raise_chain_threshold",
        "bindings": {"chain": "c-1", "new_threshold": new_value},
    }
    return model, state, (operation, step)


def test_a_satisfied_dynamic_comparison_is_actually_evaluated() -> None:
    """`threshold-restated` forbids a failure, which is not the same as proving
    the comparison ran.

    The discriminating pair: the SAME unchanged value under `>=` produces no
    verdict and under `>` produces a failure. A rule that was never evaluated
    would be silent in both, and a rule that always fired would fail in both.
    """

    def dynamic(result: Any) -> list[Any]:
        # Restating 500 is also a redundant assert, which is correct and beside
        # this test's point -- the pair being discriminated is the comparison.
        return [v for v in result.verdicts if v.kind == "dynamic-rule"]

    model, state, (operation, step) = _threshold_step(">=", 500)
    satisfied, _ = transition._evaluate_step(1, step, operation, model, state, None)
    assert dynamic(satisfied) == []

    model, state, (operation, step) = _threshold_step(">", 500)
    violated, _ = transition._evaluate_step(1, step, operation, model, state, None)
    assert [v.verdict for v in dynamic(violated)] == ["fail"]


_REPEATED_VARIABLE_MODEL = """
version: 2
model_id: "urn:gnd-fixture:transition-repeated@1"
source: { kind: explicit, confidence: high }
object_types:
  - { id: node_id, name: NodeId, kind: value, primitive: Integer }
fact_types:
  - id: edge
    reading: "{NodeId} links {NodeId}"
    roles:
      - { object_type: node_id, role_name: left }
      - { object_type: node_id, role_name: right }
  - id: loop_seen
    reading: "{NodeId} loops {NodeId}"
    roles:
      - { object_type: node_id, role_name: left }
      - { object_type: node_id, role_name: right }
operations:
  - id: record_loop
    reading: "{NodeId} loop is recorded"
    parameters:
      - { name: x, object_type: node_id }
    preconditions:
      - id: needs_edge
        require:
          - { fact_type: edge, bind: { left: "$x", right: "$x" } }
        modality: alethic
        source: explicit
        status: confirmed
        provenance: { csdp_step: 7, dialogue_turn: 1 }
    effects:
      - assert: { fact_type: loop_seen, bind: { left: "$x", right: "$x" } }
    frame: { modality: alethic }
    source: explicit
    status: confirmed
    provenance: { csdp_step: 7, dialogue_turn: 1 }
"""


def test_a_parameter_occupying_two_roles_produces_every_role_pair(tmp_path) -> None:
    """One parameter, two roles, and the mapping used to keep only the last.

    `edge(left: $x, right: $x)` compiled to a single pair, so a `loop_seen(1,1)`
    fact found a "matching" `edge(2,1)` and the obligation passed over data that
    breaks it.
    """
    path = tmp_path / "repeated.orm.yaml"
    path.write_text(_REPEATED_VARIABLE_MODEL, encoding="utf-8")
    model = load_model(path)
    entry = model.compiled_obligations("record_loop")[0]
    assert set(entry["role_pairs"]) == {
        ("left", "left"),
        ("left", "right"),
        ("right", "left"),
        ("right", "right"),
    }, entry["role_pairs"]


def test_every_eligible_asserted_fact_type_compiles_not_just_the_first(tmp_path) -> None:
    """An operation asserting both B and C from one precondition licenses TWO
    standing claims, and taking the first sorted one silently dropped the
    other -- so a pre-state violating it was never checked."""
    document = YAML(typ="safe").load(_RETRACTING_MODEL)
    document["fact_types"].append(
        {
            "id": "c",
            "reading": "{ThingId} is c",
            "roles": [{"object_type": "thing_id", "role_name": "x"}],
        }
    )
    operation = document["operations"][0]
    operation["effects"] = [
        {"assert": {"fact_type": "b", "bind": {"x": "$x"}}},
        {"assert": {"fact_type": "c", "bind": {"x": "$x"}}},
    ]
    path = tmp_path / "two-asserts.orm.yaml"
    path.write_text(json.dumps(document), encoding="utf-8")
    model = load_model(path)
    compiled = [e for e in model.compiled_obligations("make_b") if e.get("subset")]
    assert {entry["subset"]["of"] for entry in compiled} == {"b", "c"}, compiled
