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

    for entry in reply.get("derived_fact_types", ()):   # the acceptance replay builds replies without it
        # A derived fact type is the model's own fact type shape with a structured rule. It
        # holds no rows: its facts follow from the rule, so there is nothing to sample.
        assert isinstance(entry["derivation_rule"], dict), "an opaque rule is an open question, not a proposal"
        assert "rows" not in entry
        element = {k: v for k, v in entry.items() if k not in {"quote", "rationale"}}
        element["provenance"] = {"spans": spans(entry), "rationale": entry["rationale"]}
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
    # Issue 104, ask 4: a derived fact type travels in the same reply, with its quote.
    (derived,) = [f for f in model["fact_types"] if f.get("derivation") == "derived"]
    assert derived["id"] == "policy_is_covered" and isinstance(derived["derivation_rule"], dict)
    assert len(derived["provenance"]["spans"]) == 1 and "sample_population" not in derived


def test_a_derived_fact_type_without_its_quote_does_not_validate(tmp_path: Path) -> None:
    """The quote is what `gnd validate --document` holds a derived fact type to, like any element."""
    reply = json.loads(REPLY.read_text(encoding="utf-8"))
    model = _translate(reply, DOCUMENT.read_bytes())
    (derived,) = [f for f in model["fact_types"] if f.get("derivation") == "derived"]
    del derived["provenance"]["spans"]
    exit_code, payload = _validate(model, tmp_path)
    assert exit_code != 0
    assert any("policy_is_covered" in json.dumps(issue) for issue in payload["issues"]), payload["issues"]


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
    for key in ("object_types", "fact_types", "subtype_links", "constraints", "derived_fact_types", "open_questions"):
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

#: Inline code spans, which may wrap across lines, and the lines of fenced blocks.
_CODE_SPAN = re.compile(r"(?<!`)`([^`]+)`(?!`)")
_FENCE = re.compile(r"^```[^\n]*\n(.*?)^```", re.DOTALL | re.MULTILINE)
#: The commands the procedure drives; every option it names belongs to one of them.
_COMMANDS = (("validate",), ("evolve", "preview"), ("evolve", "apply"))


def _parsers() -> dict[tuple[str, ...], Any]:
    import test_rf1_cli_pins as pins

    with pytest.MonkeyPatch.context() as monkeypatch:
        found: dict[str, Any] = {}
        pins._walk(pins._root(monkeypatch), ("gnd",), found)
    return {tuple(path.split()[1:]): parser for path, parser in found.items()}


def _actions(parser: Any) -> dict[str, Any]:
    return {option: action for action in parser._actions for option in action.option_strings}


def _invocations(text: str) -> list[str]:
    """Every code span and every fenced line, whitespace-normalized (a span may wrap)."""
    fenced = [line for block in _FENCE.findall(text) for line in block.splitlines()]
    unfenced = _FENCE.sub("", text)
    return [" ".join(chunk.split()) for chunk in (*_CODE_SPAN.findall(unfenced), *fenced) if chunk.strip()]


def _option_problems(span: str, words: list[str], actions: dict[str, Any]) -> list[str]:
    problems = []
    for index, word in enumerate(words):
        if not word.startswith("--"):
            continue
        action = actions.get(word)
        if action is None:
            problems.append(f"{span}: unknown option {word}")
            continue
        value = words[index + 1] if index + 1 < len(words) else None
        # A value the reference spells literally (lowercase, not a placeholder) must be one the option accepts.
        if action.choices is not None and value is not None and value.islower() and value not in action.choices:
            problems.append(f"{span}: {word} does not accept {value}")
    return problems


def _drift(text: str) -> list[str]:
    """Every `gnd ...` invocation whose command, options or literal choices do not exist, and every
    bare option that none of the driven commands has."""
    parsers = _parsers()
    known = {option: action for command in _COMMANDS for option, action in _actions(parsers[command]).items()}
    problems = []
    for span in _invocations(text):
        words = span.split()
        if words[:1] == ["gnd"]:
            command = next((key for key in (tuple(words[1:3]), tuple(words[1:2])) if key in parsers), None)
            if command is None:
                problems.append(f"no such command: {span}")
                continue
            problems += _option_problems(span, words, _actions(parsers[command]))
        elif words[0].startswith("--"):
            problems += _option_problems(span, words, known)
    return problems


def test_ug4_the_procedure_names_only_options_that_exist() -> None:
    text = REFERENCE.read_text(encoding="utf-8")
    assert _drift(text) == []
    spans = _invocations(text)
    # Non-vacuity: the wrapped preview command and the gate's commands are among the checked spans.
    assert "gnd evolve preview --policy additive --check-population FILE" in spans
    assert any(span.startswith("gnd validate") and "--require-documents" in span for span in spans)
    for shipped in ("source-document", "--require-documents", "--check-population", "--shape-report"):
        assert shipped in text, shipped


@pytest.mark.parametrize(("old", "new", "suffix"), [
    ("--require-documents", "--require-document", ""),                        # a misspelt option
    ("additive --check-population FILE`", "additive --check-populations FILE`", ""),  # inside a wrapped span
    ("--policy additive --shape-report", "--policy banana --shape-report", ""),        # a value the option refuses
    (None, None, "\n`gnd evolv preview --policy additive`\n"),                       # an unknown command
    (None, None, "\n```bash\ngnd validate MODEL --require-documentz\n```\n"),      # inside a fenced block
    (None, None, "\n`gnd evolve apply --shape-report`\n"),                           # an option of the wrong command
])
def test_ug4_the_guard_can_fail(old: str | None, new: str | None, suffix: str) -> None:
    """Mutation control (review finding 2): each planted drift is reported."""
    text = REFERENCE.read_text(encoding="utf-8")
    if old is not None:
        assert old in text, old
        text = text.replace(old, new, 1)
    assert _drift(text + suffix)


# --- GO4 (#227): what a reply carries for an element the model already has ------------------------
# Spec: .gnd-planning/milestones/growth-round-outcomes/notes/phase-GO4-spec.md (§8, T1-T3).


def _section(text: str, heading: str) -> list[str]:
    """The lines of one ``## heading`` section, by its heading line."""
    lines = text.splitlines()
    start = lines.index(f"## {heading}") + 1
    end = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start:end]


def _table_rows(lines: list[str]) -> dict[str, str]:
    """A markdown table's rows by their first cell; a row is one line of `|`-separated cells."""
    rows = {}
    for line in lines:
        if line.startswith("| ") and not line.startswith("|---"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            rows[cells[0]] = " | ".join(cells[1:])
    return rows


def _reply_rule_problems(text: str) -> list[str]:
    section = _section(text, "The reply shape")
    rows = _table_rows(section)
    elements, sample_rows = rows.get("`object_types`, `fact_types`", ""), rows.get("`rows`", "")
    prose = "\n".join(line for line in section if not line.startswith("|"))
    problems = []
    if "New elements only" not in elements or "is not repeated here" not in elements:
        problems.append("the element row does not say a reply repeats no element the model has")
    if "ids that already exist are reused" in elements:
        problems.append("the element row keeps the old, ambiguous wording")
    if "`open_questions` entry" not in sample_rows or "fact_types.modify" not in sample_rows:
        problems.append("the rows row does not route rows for an existing fact type to open_questions")
    if "is never repeated in\n`object_types` or `fact_types`" not in prose:
        problems.append("the reply-shape prose does not state the rule")
    block = prose.split("```json\n", 1)[1].split("\n```", 1)[0]
    example = json.loads(block)
    added = {entry["id"] for entry in example["fact_types"] + example["derived_fact_types"]}
    hosts = {entry["host"] for entry in example["constraints"]} - {"model"}
    if not hosts - added:
        problems.append("the example names no fact type the model already has")
    return problems


def test_go4_t1_the_reply_shape_states_the_rule_and_shows_it() -> None:
    assert _reply_rule_problems(REFERENCE.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize(("old", "new"), [
    ("is not repeated here", "is repeated here"),
    ("New elements only, in the model's own element shapes", "The model's own element shapes, ids that already exist are reused"),
    ("Rows for a new fact type only", "Rows for a new fact type only"),
    ("are an `open_questions` entry: the additive policy refuses", "are appended: the additive policy refuses"),
    ("is never repeated in\n`object_types` or `fact_types`", "may be repeated in\n`object_types` or `fact_types`"),
    ('{"host": "policy_has_holder"', '{"host": "policy_expires_on_expiry_date"'),
], ids=["element-row", "old-wording", "noop-control", "rows-row", "prose", "example"])
def test_go4_t2_the_guard_fails_when_the_rule_is_removed(old: str, new: str) -> None:
    text = REFERENCE.read_text(encoding="utf-8")
    assert old in text
    problems = _reply_rule_problems(text.replace(old, new, 1))
    assert bool(problems) == (old != new), problems


@pytest.mark.parametrize("example", ["growth", "seeded_growth"])
def test_go4_t3_the_packaged_examples_repeat_no_existing_element(example: str) -> None:
    """GO4-C3: no round adds an element its before-model already has, and none
    changes an existing fact type (a restated fact type with rows would)."""
    from gnd.evolve import read_evolution_proposal_document
    from gnd.model import parse_model_document

    directory = REPO_ROOT / "src/gnd/examples" / example
    first = directory / ("model.orm.yaml" if example == "growth" else "root.orm.yaml")
    before = parse_model_document(first.read_bytes(), source=first)
    for name in ("round-1.proposal.json", "round-2.proposal.json"):
        proposal = read_evolution_proposal_document(json.loads((directory / name).read_text(encoding="utf-8")))
        existing = {(collection, entry.get("id")) for collection in ("object_types", "fact_types")
                    for entry in before.get(collection) or []}
        for operation in proposal.operations:
            locator = operation.locator
            if getattr(locator, "collection", None) in ("object_types", "fact_types"):
                key = (locator.collection, locator.element_id)
                assert operation.kind.value == "add" and key not in existing, (name, operation.reference())
        before = parse_model_document(proposal.candidate_model.text.encode("utf-8"), source=first)
