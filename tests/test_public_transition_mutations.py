"""The mutation-pair rule: every exit-0 walk has a one-token sibling that is not.

Section 8's independence pass, mechanized half. The corpus proves the checker
reports what the fixtures say it should; it cannot prove the checker would
NOTICE if the fixture were wrong. A walk that exits 0 because nothing was
evaluated looks exactly like a walk that exits 0 because everything held.

So for every exit-0 walk, one token of its declared post-state (or, where that
cannot bite, one token of its bindings) is changed, and the mutant MUST exit
nonzero. This is the cheapest available approximation of the false-pass
measurement that trace-synth would give -- and it is an approximation, which the
milestone record states in its own vocabulary rather than dressing up.

The mutation is chosen by rule, not by hand: delete one fact of a fact type this
walk's frame grading makes ALETHIC, so the undeclared retract is a hard failure
rather than a warning. Walks with no alethic-graded touched fact type get a
named override, with the reason -- a deontic-only walk cannot be broken by a
frame mutation at all, which is the frame grading working as designed.
"""


from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML
from test_public_transition_walks import MODEL, WALKS

from gnd import transition
from gnd.cli import main
from gnd.model import load_model

YAML_RT = YAML(typ="rt")


BINDING_OVERRIDES: dict[str, tuple[str, Any, str]] = {
    "dynamic-untouched-silent": (
        "expense",
        44,
        (
            "every fact type this walk touches is deontic-graded, so no frame "
            "mutation can produce a failure. Expense 44 is a draft, so "
            "submitting it breaks pre_approved -- an alethic precondition"
        ),
    ),
}


def _exit_zero_walks() -> list[str]:
    names = []
    for directory in sorted(WALKS.iterdir()):
        expected = directory / "expected.json"
        if expected.is_file() and json.loads(expected.read_text())["exit"] == 0:
            names.append(directory.name)
    return names


EXIT_ZERO = _exit_zero_walks()


def _alethic_fact_types(name: str) -> list[str]:
    model = load_model(MODEL)
    document = json.loads((WALKS / name / "steps.json").read_text())
    grading = transition._frame_grading(model, document["steps"])
    return [entry.fact_type for entry in grading if entry.modality == "alethic"]


def _mutate(name: str, workspace: Path) -> str:
    """Copy the walk, change ONE token, and say what changed."""
    source = WALKS / name
    shutil.copytree(source, workspace)

    if name in BINDING_OVERRIDES:
        role, value, why = BINDING_OVERRIDES[name]
        document = json.loads((workspace / "steps.json").read_text())
        original = document["steps"][0]["bindings"][role]
        document["steps"][0]["bindings"][role] = value
        (workspace / "steps.json").write_text(json.dumps(document, indent=2) + "\n")
        return f"bindings[{role}] {original!r} -> {value!r} ({why})"

    post = YAML_RT.load((workspace / "post.pop.yaml").read_text())
    for fact_type in _alethic_fact_types(name):
        facts = (post.get("facts") or {}).get(fact_type) or []
        if facts:
            removed = facts.pop(0)
            with (workspace / "post.pop.yaml").open("w", encoding="utf-8") as handle:
                YAML_RT.dump(post, handle)
            return f"deleted {fact_type} fact {dict(removed)} from the declared post"
    pre = YAML_RT.load((workspace / "pre.pop.yaml").read_text())
    for fact_type in _alethic_fact_types(name):
        borrowed = (pre.get("facts") or {}).get(fact_type) or []
        if borrowed:
            post.setdefault("facts", {}).setdefault(fact_type, []).append(dict(borrowed[0]))
            with (workspace / "post.pop.yaml").open("w", encoding="utf-8") as handle:
                YAML_RT.dump(post, handle)
            return f"added an undeclared {fact_type} fact to the declared post"
    pytest.fail(
        f"{name}: no alethic-graded fact type could be mutated and no override "
        f"is recorded -- the walk's green cannot be distinguished from a vacuous "
        f"green, which is exactly what this rule exists to detect"
    )
    return ""


@pytest.mark.parametrize("name", EXIT_ZERO)
def test_every_clean_walk_has_a_one_token_sibling_that_fails(
    name: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    workspace = tmp_path / name
    what_changed = _mutate(name, workspace)
    code = main(
        [
            "check",
            str(MODEL),
            "--pre", str(workspace / "pre.pop.yaml"),
            "--steps", str(workspace / "steps.json"),
            "--post", str(workspace / "post.pop.yaml"),
            "--format", "json",
        ]
    )
    capsys.readouterr()
    assert code != 0, (
        f"{name} still exits 0 after {what_changed}. Either the mutation does not "
        f"bite -- in which case this walk's green says less than it appears to -- "
        f"or the evaluator is not looking at what the walk claims to pin."
    )


def test_the_pass_covers_every_clean_walk_and_the_corpus_has_some() -> None:
    """A parametrized test over an empty list is a green that means nothing."""
    assert len(EXIT_ZERO) >= 15, f"only {len(EXIT_ZERO)} exit-0 walks found"
    assert set(BINDING_OVERRIDES) <= set(EXIT_ZERO), (
        "an override names a walk that is not exit-0 any more -- it would then "
        "silently stop being exercised"
    )

