from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from gnd import patterns, transition
from gnd.model import compile_operation, load_model
from gnd.population import load_population

CORPUS = Path(__file__).parent / "fixtures/public-transition-contract"
MODEL = CORPUS / "v2_expense.orm.yaml"

def test_an_external_client_can_reproduce_the_operations_digest_from_bytes() -> None:
    """The reason this digest is canonical JSON rather than `repr`.

    An author writing a steps.json by hand, in another language, must be able to
    produce this value from the model file alone. So it is computed here WITHOUT
    calling the function under test -- sorted keys, `(",", ":")`, UTF-8, and
    sha256 -- and the two must agree.
    """
    raw = YAML(typ="safe").load(MODEL.read_text(encoding="utf-8"))
    payload = json.dumps(
        raw["operations"],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    independent = "sha256:" + hashlib.sha256(payload).hexdigest()
    assert independent == transition.operations_digest(load_model(MODEL).operations)


def test_the_digest_is_unchanged_by_compilation() -> None:
    """Trace compilation attaches nothing to the operations section.

    This is the pin that made the ``operation["compiled"]`` design fail: writing
    the compiled obligations into those dicts moved this digest, so every
    committed steps.json stopped matching its own model. The obligations live in
    a private side table now, and the loaded section is byte-for-byte as
    authored.
    """
    model = load_model(MODEL)
    before = transition.operations_digest(model.operations)
    assert model.compiled_obligations("reimburse_expense"), "nothing compiled -- wrong pin"
    assert transition.operations_digest(model.operations) == before
    assert all("compiled" not in operation for operation in model.operations), (
        "compilation wrote into the operations section"
    )


def test_the_pre_digest_hashes_file_bytes() -> None:
    """Provenance, not equivalence: reproducible with `sha256sum` by a client
    that has never seen this code."""
    path = CORPUS / "walks" / "pinned-pre" / "pre.pop.yaml"
    expected = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    assert transition.population_file_digest(path) == expected
    walk = json.loads((CORPUS / "walks" / "pinned-pre" / "steps.json").read_text())
    assert walk["pre_digest"] == expected, (
        "the committed fixture and the shipped function disagree about what pre_digest hashes"
    )


def test_unbound_term_error_is_unreachable_from_a_loaded_walk() -> None:
    """Two guards stand in front of it, and this asserts BOTH still stand.

    An atom naming an undeclared parameter is refused at authoring time
    (`semantic:op-term-ref`), and a walk whose bindings are not exactly the
    declared set is refused at load time (`transition:bindings-mismatch`). The
    exception therefore stays an internal assertion rather than a runtime path
    with an exit code -- but "unreachable" is only honest if something breaks
    when a guard is removed.
    """
    with pytest.raises(patterns.UnboundTermError):
        patterns.resolve_term("$missing", {"present": 1})

    model = load_model(MODEL)
    operation = next(op for op in model.operations if op["id"] == "approve_expense")
    declared = {p["name"] for p in operation["parameters"]}
    document = json.loads((CORPUS / "walks" / "missing-binding" / "steps.json").read_text())
    supplied = set(document["steps"][0]["bindings"])
    assert supplied != declared, "the fixture no longer omits a parameter"
    with pytest.raises(transition.TransitionLoadError) as raised:
        transition.validate_steps(document, model)
    assert [issue.rule_id for issue in raised.value.issues] == ["transition:bindings-mismatch"]


def test_compilation_is_existential_and_guarded_by_the_sole_asserter_rule() -> None:
    """Both halves of the compilation rule, on the corpus model.

    Existential: `pre_submitted` shares only `expense` with the asserted fact
    type and compiles anyway -- under the universal reading NOTHING compiles in
    this 13-operation model and finding class 8 ships unobservable.

    The guard: an obligation compiles only when exactly one operation asserts
    the fact type its claim generalizes over, because that is what makes the
    claim follow at all.
    """
    model = load_model(MODEL)
    compiled = {
        entry["obligation"]: entry
        for op in model.operations
        for entry in model.compiled_obligations(str(op["id"]))
    }
    assert compiled["pre_submitted"]["subset"] == {
        "of": "expense_reimbursed",
        "in": "expense_submitted_to_workday",
    }
    assert "transition-only" in compiled["pre_settled"]

    crowded = dict(next(op for op in model.operations if op["id"] == "reimburse_expense"))
    entries = compile_operation(
        crowded, {"asserters": {"expense_reimbursed": 2}, "retracted": set()}
    )
    reasons = [e.get("transition-only") for e in entries if e["obligation"] == "pre_submitted"]
    assert reasons and "more than one" in reasons[0], (
        "the sole-asserter guard did not fire: a claim generalizing over a fact "
        "type two operations assert does not follow from either of them"
    )


def test_a_duplicated_ground_fact_is_not_a_frame_delta() -> None:
    """Sets, not multisets.

    A declared post carrying one ground fact twice differs from the computed
    final state in COUNT and not in content. Counting it as an undeclared assert
    would fail a walk for the way its population was written down.
    """
    grading = [
        transition.FrameGrading(
            fact_type="expense_is_urgent",
            modality="alethic",
            reason="all-alethic",
            operations=["flag_expense"],
        )
    ]
    computed = {"expense_is_urgent": [{"expense": 41}]}
    declared = load_population(
        CORPUS / "walks" / "clean-walk" / "pre.pop.yaml", model=load_model(MODEL)
    )
    declared.facts["expense_is_urgent"] = [{"expense": 41}, {"expense": 41}]
    assert transition._frame_verdicts(grading, computed, declared) == []

    declared.facts["expense_is_urgent"] = [{"expense": 41}, {"expense": 42}]
    verdicts = transition._frame_verdicts(grading, computed, declared)
    assert [v.direction for v in verdicts] == ["undeclared-assert"], (
        "a genuinely different fact must still be a delta -- otherwise this test "
        "would pass over a comparison that reports nothing at all"
    )


def test_an_unloadable_intermediate_is_band_4_and_the_walk_continues(monkeypatch) -> None:
    """The spec deferred this case to "the harness" and the harness never got it.

    Found by auditing finding-class coverage against the corpus after the
    adversarial review: every other class is pinned by a walk, and this one was
    pinned by a test asserting that a STRING appears in the source -- which
    cannot fail if the behaviour is wrong. A declared branch with no case that
    can fail it is this milestone's defining defect, and this was one.

    Three claims, all of which a wrong implementation breaks differently:
    the verdict is `unchecked` at band 4 and NOT exit 3, because exit 3 means
    refused before evaluation began and this is mid-walk; the reason code says
    which of the two `unchecked` causes it was; and the walk CONTINUES, so a
    later step is still evaluated rather than the run being abandoned.
    """
    from gnd import population as population_module

    # The real inputs load first, at the real cap: the case under test is an
    # intermediate state that cannot be re-loaded, not a walk whose own
    # populations were refused -- that is exit 3, and a different claim.
    model = load_model(MODEL)
    walk = json.loads((CORPUS / "walks" / "clean-walk" / "steps.json").read_text())
    pre = load_population(CORPUS / "walks" / "clean-walk" / "pre.pop.yaml", model=model)
    post = load_population(CORPUS / "walks" / "clean-walk" / "post.pop.yaml", model=model)

    monkeypatch.setattr(population_module, "MAX_POPULATION_BYTES", 10)
    report = transition.evaluate(model, pre, post, walk["steps"])

    assert len(report.steps) == len(walk["steps"]), (
        "the walk stopped at the unloadable state instead of continuing"
    )
    unloadable = [
        verdict
        for step in report.steps
        for verdict in step.verdicts
        if verdict.kind == "intermediate-unloadable"
    ]
    assert len(unloadable) == len(walk["steps"])
    for verdict in unloadable:
        assert verdict.verdict == "unchecked"
        assert verdict.modality == "alethic"
        assert verdict.reason_code == "transition:intermediate-state-unloadable"
    assert all(step.intermediate.verdicts == [] for step in report.steps), (
        "a state that could not be loaded must not carry constraint verdicts"
    )
    assert transition.band(report) == 4, (
        "an unexaminable state is band 4 -- not 3, which would claim the run was "
        "refused before it began, and not 0, which would claim it was checked"
    )
