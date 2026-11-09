"""The unattended-growth guidance in gnd-model-from-text, held to the code.

Reference: src/gnd/skills/gnd-model-from-text/references/unattended-growth.md.
The reference makes two kinds of claim that can drift: what `--policy additive`
admits, and that its reply shape is enough to build a model that passes
`gnd validate --document`. The translator below is a test-only reading of the
reply shape's mapping table, not a shipped API.
"""

from __future__ import annotations

import copy
import hashlib
import io
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

import pytest
import test_evolve_additive_policy as policy
from ruamel.yaml import YAML
from support.cli_runner import run_main

REPO_ROOT = Path(__file__).resolve().parent.parent
REFERENCE = REPO_ROOT / "src/gnd/skills/gnd-model-from-text/references/unattended-growth.md"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "unattended-growth"
DOCUMENT = FIXTURES / "policy.txt"
REPLY = FIXTURES / "reply.json"


def _span(raw: bytes, quote: str, occurrence: int | None = None) -> dict[str, Any]:
    """The host's job: locate a verbatim quote in the NFC text; refuse a missing or ambiguous one."""
    text = unicodedata.normalize("NFC", raw.decode("utf-8"))
    starts = [m.start() for m in re.finditer(re.escape(quote), text)]
    if occurrence is None:
        assert len(starts) == 1, f"quote {quote!r} must occur exactly once, found {len(starts)}"
        start = starts[0]
    else:
        start = starts[occurrence]
    end = start + len(quote)
    return {
        "document_sha256": hashlib.sha256(raw).hexdigest(),
        "start": start,
        "end": end,
        "excerpt_sha256": hashlib.sha256(text[start:end].encode("utf-8")).hexdigest(),
    }


_SOURCE_BY_BASIS = {"text-cue": "llm-inferred", "rows": "sample", "library": "common-sense"}


def _translate(reply: dict[str, Any], raw: bytes) -> dict[str, Any]:
    digest = hashlib.sha256(raw).hexdigest()

    def spans(entry: dict[str, Any]) -> list[dict[str, Any]]:
        return [_span(raw, entry["quote"], entry.get("quote_occurrence"))]

    object_types: list[dict[str, Any]] = []
    for entry in reply["object_types"]:
        element = {k: v for k, v in entry.items() if k != "quote"}
        element["provenance"] = {"spans": spans(entry)}
        object_types.append(element)
    by_id = {element["id"]: element for element in object_types}
    for link in reply["subtype_links"]:
        subtype = by_id[link["subtype"]]
        subtype["subtype_of"] = [link["supertype"]]
        subtype["inherits_reference"] = link["inherits_reference"]
        subtype["provenance"]["spans"].append(_span(raw, link["quote"]))
        subtype["provenance"]["rationale"] = link["rationale"]

    fact_types: list[dict[str, Any]] = []
    for entry in reply["fact_types"]:
        element = {k: v for k, v in entry.items() if k not in {"quote", "rows"}}
        element["sample_population"] = [row["values"] for row in entry["rows"]]
        element["provenance"] = {
            "spans": spans(entry),
            "sample_spans": [{"row": i, "span": _span(raw, row["quote"])} for i, row in enumerate(entry["rows"])],
        }
        fact_types.append(element)

    top_level: list[dict[str, Any]] = []
    for entry in reply["constraints"]:
        constraint = copy.deepcopy(entry["constraint"])
        constraint.update(
            source=_SOURCE_BY_BASIS[entry["basis"]], status="proposed", modality="deontic",
            rationale=entry["rationale"],
        )
        if entry["basis"] == "library":
            constraint["provenance"] = {"library_entry": entry["library_entry"]}
        else:
            constraint["provenance"] = {"spans": spans(entry)}
            if entry["basis"] == "text-cue":
                constraint["provenance"]["rationale_world_fact"] = entry["cue"]
        if entry["host"] == "model":
            top_level.append(constraint)
        else:
            next(f for f in fact_types if f["id"] == entry["host"]).setdefault("constraints", []).append(constraint)

    return {
        "version": 1,
        "model_id": "unattended-growth-example",
        "source": {"kind": "prose", "mode": "unattended", "reviewer": "none",
                   "documents": [{"sha256": digest, "label": reply["document"]}]},
        "object_types": object_types,
        "fact_types": fact_types,
        "constraints": top_level,
    }


def _validate(model: dict[str, Any], tmp_path: Path) -> tuple[int, dict[str, Any]]:
    buffer = io.StringIO()
    YAML().dump(model, buffer)
    path = tmp_path / "model.orm.yaml"
    path.write_text(buffer.getvalue(), encoding="utf-8")
    result = run_main(["validate", str(path), "--document", str(DOCUMENT), "--format", "json"])
    return result.returncode, json.loads(result.stdout)


def test_the_reply_shape_builds_a_model_that_validates(tmp_path: Path) -> None:
    """Subtype link, uniqueness, mandatory, enumeration and a library hit, all `proposed` and `deontic`."""
    reply = json.loads(REPLY.read_text(encoding="utf-8"))
    model = _translate(reply, DOCUMENT.read_bytes())
    exit_code, payload = _validate(model, tmp_path)
    assert exit_code == 0, payload.get("issues")
    constraints = [c for f in model["fact_types"] for c in f.get("constraints", [])] + model["constraints"]
    assert {(c["status"], c["modality"]) for c in constraints} == {("proposed", "deontic")}
    assert {c["source"] for c in constraints} == {"llm-inferred", "common-sense"}


def test_a_quote_the_document_does_not_contain_is_dropped_not_guessed() -> None:
    with pytest.raises(AssertionError, match="exactly once"):
        _span(DOCUMENT.read_bytes(), "a sentence the document never says")
    with pytest.raises(AssertionError, match="exactly once"):
        _span(DOCUMENT.read_bytes(), "Policy P-17")


def test_the_reference_example_has_the_fixture_reply_shape() -> None:
    text = REFERENCE.read_text(encoding="utf-8")
    block = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
    assert block, "the reference no longer carries its JSON reply example"
    example = json.loads(block.group(1))
    reply = json.loads(REPLY.read_text(encoding="utf-8"))
    assert set(example) == set(reply)
    for key in ("object_types", "fact_types", "subtype_links", "constraints", "open_questions"):
        assert example[key], key
        assert set(example[key][0]) <= set(reply[key][0]) | {"quote_occurrence"}, key


# --- the additive-policy statements -----------------------------------------------------------


def test_additive_admits_a_new_supertype_but_not_the_link_on_an_existing_type() -> None:
    document = policy._doc()
    customer = policy._object(document, "customer")
    supertype = {"id": "party", "name": "Party", "kind": "entity", "reference": copy.deepcopy(customer["reference"])}
    linked = {**copy.deepcopy(customer), "subtype_of": ["party"], "inherits_reference": True}
    add = policy._op("add", policy._element("object_types", "party"), after=supertype, operation_id="add")
    link = policy._op("modify", policy._element("object_types", "customer"), before=customer, after=linked,
                      operation_id="link")
    assert policy._direct_issues((add,), populated=frozenset()) == ()
    issues = policy._direct_issues((add, link), populated=frozenset())
    assert [issue.cell for issue in issues] == ["object_types.modify"]
    assert "inherits_reference" in issues[0].detail and "subtype_of" in issues[0].detail


def test_additive_admits_a_new_subtype_of_an_existing_type() -> None:
    document = policy._doc()
    vip = {"id": "vip", "name": "Vip", "kind": "entity", "subtype_of": ["customer"], "inherits_reference": True}
    add = policy._op("add", policy._element("object_types", "vip"), after=vip, operation_id="add")
    assert policy._direct_issues((add,), populated=frozenset({policy.POPULATED})) == ()
    assert policy._object(document, "customer").get("subtype_of") is None


def test_additive_admits_a_constraint_with_the_fact_type_that_adds_it() -> None:
    fact = copy.deepcopy(policy.NEW_FACT)
    constraint = {"type": "uniqueness", "roles": ["order"], "source": "llm-inferred", "status": "proposed",
                  "modality": "deontic", "rationale": "r",
                  "provenance": {"rationale_world_fact": "w"}}
    add_object = policy._op("add", policy._element("object_types", "region"), after=policy.NEW_OBJECT,
                            operation_id="object")
    add_fact = policy._op("add", policy._element("fact_types", fact["id"]), after=fact, operation_id="fact")
    add_constraint = policy._op("add", policy._constraint_locator(fact["id"], None, "uniqueness"), after=constraint,
                                operation_id="constraint")
    assert policy._direct_issues((add_object, add_fact, add_constraint)) == ()
    # The same constraint on the populated fact type the fixture already holds is refused.
    refused = policy._op("add", policy._constraint_locator(policy.POPULATED, None, "uniqueness"), after=constraint,
                         operation_id="late")
    assert [i.cell for i in policy._direct_issues((refused,))] == ["constraint.populated.add"]


# --- UG4-D4: the procedure names only commands and options that exist --------

_CODE_SPAN = re.compile(r"`([^`\n]+)`")
_FLAG = re.compile(r"(?<![\w-])--[a-z][a-z-]*")
#: The commands the procedure drives; every option it names belongs to one of them.
_COMMANDS = (("validate",), ("evolve", "preview"), ("evolve", "apply"))


def _parsers() -> dict[tuple[str, ...], Any]:
    import test_rf1_cli_pins as pins

    with pytest.MonkeyPatch.context() as monkeypatch:
        found: dict[str, Any] = {}
        pins._walk(pins._root(monkeypatch), ("gnd",), found)
    return {tuple(path.split()[1:]): parser for path, parser in found.items()}


def _options(parser: Any) -> set[str]:
    return {option for action in parser._actions for option in action.option_strings}


def _drift(text: str) -> list[str]:
    """Every `gnd ...` span whose command or options do not exist, and every option no driven command has."""
    parsers = _parsers()
    known = set().union(*(_options(parsers[command]) for command in _COMMANDS))
    problems = []
    for span in _CODE_SPAN.findall(text):
        words = span.split()
        if words[:1] == ["gnd"]:
            command = next((key for key in (tuple(words[1:3]), tuple(words[1:2])) if key in parsers), None)
            if command is None:
                problems.append(f"no such command: {span}")
                continue
            problems += [f"{span}: {flag}" for flag in _FLAG.findall(span) if flag not in _options(parsers[command])]
        else:
            problems += [f"{span}: {flag}" for flag in _FLAG.findall(span) if flag not in known]
    return problems


def test_ug4_the_procedure_names_only_options_that_exist() -> None:
    text = REFERENCE.read_text(encoding="utf-8")
    assert _drift(text) == []
    for shipped in ("source-document", "--require-documents", "--check-population", "--shape-report"):
        assert shipped in text, shipped


def test_ug4_the_guard_can_fail() -> None:
    """Mutation control: a misspelt option and an unknown command are both reported."""
    text = REFERENCE.read_text(encoding="utf-8")
    assert "--require-documents" in text
    assert _drift(text.replace("--require-documents", "--require-document", 1))
    assert _drift(text + "\n`gnd evolv preview --policy additive`\n")
    assert _drift(text + "\n`--check-populations FILE`\n")
