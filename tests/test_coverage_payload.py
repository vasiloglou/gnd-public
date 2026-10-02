"""Payload and element-address guards for ``gnd coverage``."""

from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from gnd import resolve_version
from gnd.address import (
    constraint_address,
    fact_type_address,
    operation_address,
    parse_address,
    positional_constraint_ref,
)
from gnd.coverage import (
    MAX_EVIDENCE_BYTES,
    CoverageInputError,
    build_coverage,
    build_payload,
    canonical_payload,
    read_evidence_document,
    read_json_document,
    render_coverage,
)
from gnd.model import load_model
from gnd.transition import model_digest

FIXTURES = Path(__file__).parent / "fixtures" / "coverage"


def test_declared_element_addresses_round_trip() -> None:
    expected = {
        operation_address("submit"): ("operation", "submit"),
        fact_type_address("invoice_has_total"): ("fact_type", "invoice_has_total"),
        constraint_address("one_total"): ("constraint", "one_total"),
    }
    for text, (element_class, identifier) in expected.items():
        parsed = parse_address(text)
        assert parsed is not None
        assert parsed.text == text
        assert parsed.element_class == element_class
        assert parsed.addressing == "declared-id"
        assert parsed.identifier == identifier


def test_positional_constraint_addresses_round_trip_byte_exactly() -> None:
    inline = positional_constraint_ref("invoice_has_total", 2)
    top_level = positional_constraint_ref(None, 7)
    assert inline == "fact_types[invoice_has_total].constraints[2]"
    assert top_level == "constraints[7]"

    parsed_inline = parse_address(inline)
    parsed_top = parse_address(top_level)
    assert parsed_inline is not None
    assert parsed_inline.addressing == "positional"
    assert parsed_inline.fact_type_id == "invoice_has_total"
    assert parsed_inline.index == 2
    assert parsed_top is not None
    assert parsed_top.addressing == "positional"
    assert parsed_top.fact_type_id is None
    assert parsed_top.index == 7


def test_parse_address_is_total_over_hostile_strings() -> None:
    hostile = (
        "",
        "operation:",
        " operation:x",
        "operation: x",
        "fact_types[x].constraints[-1]",
        "fact_types[].constraints[0]",
        "constraints[not-an-int]",
        "constraints[" + "9" * 10_000 + "]",
        "\x00",
        "not-an-address",
    )
    assert [parse_address(text) for text in hostile] == [None] * len(hostile)


@pytest.mark.parametrize(
    ("relative", "kind"),
    (
        ("mixed/evidence/check.json", "check"),
        ("mixed/evidence/verify.json", "verify"),
        ("mixed/evidence/conformance.json", "conformance"),
        ("mixed/evidence/transition.json", "transition"),
    ),
)
def test_each_evidence_reader_accepts_its_shipped_payload(relative: str, kind: str) -> None:
    # v5.1 Phase 3: the reader that owns the version logic also returns how a
    # check/verify source names its model, so no indexer re-derives it. Every
    # shipped fixture predates the model-bound wire and is classified unbound;
    # conformance and transition have no binding to classify.
    document, binding = read_evidence_document(FIXTURES / relative, kind=kind)  # type: ignore[arg-type]
    assert document["tool"] == "gnd"
    assert binding == ("legacy-unbound" if kind in {"check", "verify"} else None)


@pytest.mark.parametrize(
    "raw",
    (
        b"9" * 10_000,
        ("[" * 2_000 + "0" + "]" * 2_000).encode(),
        b'{"schema_version":3,"value":NaN}',
        b"[]",
        b"",
        b"\xff",
    ),
    ids=("long-integer", "deep-nesting", "nan", "array", "empty", "non-utf8"),
)
def test_json_reader_is_total_over_hostile_bytes(tmp_path: Path, raw: bytes) -> None:
    path = tmp_path / "hostile.json"
    path.write_bytes(raw)
    with pytest.raises(CoverageInputError):
        read_json_document(path, kind="check")


def test_json_reader_checks_the_cap_before_reading(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "large.json"
    path.write_bytes(b"x")
    original_stat = Path.stat

    def oversized_stat(candidate: Path):  # type: ignore[no-untyped-def]
        result = original_stat(candidate)
        values = list(result)
        values[6] = MAX_EVIDENCE_BYTES + 1
        return type(result)(values)

    def forbidden_read(_candidate: Path) -> bytes:
        raise AssertionError("read_bytes ran after the stat cap refused the file")

    monkeypatch.setattr(Path, "stat", oversized_stat)
    monkeypatch.setattr(Path, "read_bytes", forbidden_read)
    with pytest.raises(CoverageInputError, match="over the"):
        read_json_document(path, kind="check")


def test_reader_refuses_wrong_version_and_wrong_declared_shape(tmp_path: Path) -> None:
    wrong_version = tmp_path / "wrong-version.json"
    wrong_version.write_text(json.dumps({"schema_version": 999}), encoding="utf-8")
    with pytest.raises(CoverageInputError, match="schema_version"):
        read_json_document(wrong_version, kind="check")

    with pytest.raises(CoverageInputError):
        read_evidence_document(FIXTURES / "mixed/evidence/conformance.json", kind="check")
    with pytest.raises(CoverageInputError):
        read_evidence_document(FIXTURES / "mixed/evidence/check.json", kind="conformance")


def test_transition_reader_refuses_an_inconsistent_evaluated_state(tmp_path: Path) -> None:
    """A schema-valid contradiction is malformed evidence, not an indexer crash."""

    document = json.loads(
        (FIXTURES / "refused/evidence/transition-refused.json").read_text(encoding="utf-8")
    )
    document["transition"]["evaluated"] = True
    source = tmp_path / "inconsistent-transition.json"
    source.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(CoverageInputError, match="evaluated true requires"):
        read_evidence_document(source, kind="transition")

    populated = json.loads(
        (FIXTURES / "mixed/evidence/transition.json").read_text(encoding="utf-8")
    )
    populated["transition"]["evaluated"] = False
    source.write_text(json.dumps(populated), encoding="utf-8")

    with pytest.raises(CoverageInputError, match="evaluated false requires"):
        read_evidence_document(source, kind="transition")

    missing_fact_type = json.loads(
        (FIXTURES / "mixed/evidence/transition.json").read_text(encoding="utf-8")
    )
    missing_fact_type["transition"]["frame_verdicts"] = [
        {
            "family": "frame",
            "locator": "frame_verdicts[0]",
            "kind": "frame-delta",
            "modality": "alethic",
            "verdict": "fail",
            "message": "schema-valid row with no fact_type",
            "reason_code": None,
            "direction": "undeclared-assert",
        }
    ]
    source.write_text(json.dumps(missing_fact_type), encoding="utf-8")

    with pytest.raises(CoverageInputError, match=r"frame_verdicts\[0\].*fact_type"):
        read_evidence_document(source, kind="transition")


def _build_tree(name: str, *, include: set[str] | None = None):  # type: ignore[no-untyped-def]
    tree = FIXTURES / name
    answer = json.loads((tree / "expected.json").read_text(encoding="utf-8"))
    args = answer["arguments"]

    def values(flag: str) -> list[Path]:
        return [tree / args[index + 1] for index, item in enumerate(args) if item == flag]

    selected = include or {
        "--experiments",
        "--check",
        "--verify",
        "--conformance",
        "--transition",
    }

    return build_coverage(
        load_model(tree / args[0]),
        model_path=args[0],
        experiments=values("--experiments") if "--experiments" in selected else [],
        check=values("--check") if "--check" in selected else [],
        verify=values("--verify") if "--verify" in selected else [],
        conformance=values("--conformance") if "--conformance" in selected else [],
        transition=values("--transition") if "--transition" in selected else [],
    )


def test_all_three_element_classes_share_the_matching_and_status_policy() -> None:
    result = _build_tree("mixed")
    rows = {row.address: row for row in result.elements}
    expected = json.loads((FIXTURES / "mixed/expected.json").read_text(encoding="utf-8"))["answer"][
        "element_status"
    ]
    assert {address: rows[address].status for address in expected} == expected
    assert {
        rows["operation:attach_review_note"].element_class,
        rows["fact_type:work_item_has_note"].element_class,
        rows["constraint:one_state_per_item"].element_class,
    } == {"operation", "fact_type", "constraint"}
    assert all(
        rows[address].status == "corroborated"
        for address in (
            "operation:attach_review_note",
            "fact_type:work_item_has_note",
            "constraint:one_state_per_item",
        )
    )


def test_declared_ids_match_every_constraint_not_only_the_first() -> None:
    rows = {row.address: row for row in _build_tree("mixed").elements}
    for address in ("constraint:one_state_per_item", "constraint:one_priority_per_item"):
        assert rows[address].addressing == "declared-id"
        assert rows[address].status == "corroborated"


def test_positional_claims_are_retained_and_reported_unstable() -> None:
    result = _build_tree("positional")
    claimed = [row for row in result.elements if row.claims]
    assert {row.address for row in claimed} == {
        "fact_types[borrower_has_name].constraints[0]",
        "constraints[0]",
    }
    assert all(
        row.addressing == "positional"
        for row in result.elements
        if row.element_class == "constraint"
    )
    assert {row["address"] for row in result.unstable_addresses} == {
        "fact_types[borrower_has_name].constraints[0]",
        "constraints[0]",
    }


def test_reordering_constraints_observably_retargets_a_positional_claim(
    tmp_path: Path,
) -> None:
    source = FIXTURES / "mixed"
    tree = tmp_path / "mixed"
    shutil.copytree(source, tree)
    model = load_model(tree / "v2_operations.orm.yaml")
    reordered = model.model_copy(deep=True)
    constraints = reordered.fact_types[0]["constraints"]
    constraints[0], constraints[1] = constraints[1], constraints[0]
    result = build_coverage(
        reordered,
        model_path="v2_operations.orm.yaml",
        experiments=[tree / "experiments"],
        check=[],
        verify=[],
        conformance=[],
        transition=[],
    )
    claims = {row.address for row in result.elements if row.claims}
    assert "constraint:one_state_per_item" in claims
    assert "fact_types[work_item_has_state].constraints[1]" not in claims


def test_unmatched_exemptions_and_both_conclusion_states_are_visible() -> None:
    result = _build_tree("mixed")
    assert len(result.unmatched_covers) == 1
    assert result.unmatched_covers[0]["address"] == "constraint:no_such_constraint"
    assert len(result.covers_exemptions) == 1
    all_claims = [claim for row in result.elements for claim in row.claims]
    assert {claim.conclusions for claim in all_claims} == {
        "conclusions-present",
        "no-conclusions",
    }


def test_each_evidence_kind_quotes_its_own_vocabulary() -> None:
    result = _build_tree("mixed")
    rows = {row.address: row for row in result.elements}
    note_sources = {item.source for item in rows["fact_type:work_item_has_note"].evidence}
    assert note_sources == {"check", "verify", "conformance", "transition"}
    conformance = next(
        item
        for item in rows["fact_type:work_item_has_note"].evidence
        if item.source == "conformance"
    )
    assert len(conformance.quote["unchecked"]) == 6
    constraint = rows["constraint:one_state_per_item"]
    assert {item.source for item in constraint.evidence} == {"check", "verify"}
    assert {item.quote["verdict"] for item in constraint.evidence} == {"vacuous"}


def test_vacuous_unchecked_and_fail_are_evidence_not_grades() -> None:
    positional = _build_tree("positional")
    verdicts = [
        item.quote
        for row in positional.elements
        for item in row.evidence
        if row.element_class == "constraint"
    ]
    assert {quote["verdict"] for quote in verdicts} == {"fail", "unchecked", "vacuous"}
    assert {quote["reason_code"] for quote in verdicts if quote["verdict"] == "unchecked"} == {
        "subtype-derivation-only",
        "textual-not-mechanical",
    }

    refused = _build_tree("refused")
    assert all(
        item.quote["verdict"] == "fail"
        for row in refused.elements
        for item in row.evidence
        if row.element_class == "constraint"
    )
    assert len(refused.refused_sources) == 1
    assert not any(item.source == "transition" for row in refused.elements for item in row.evidence)


def _payload(name: str) -> dict[str, object]:
    return build_payload(_build_tree(name), gnd_version=resolve_version())


def test_coverage_schema_is_vendored_only() -> None:
    root = Path(__file__).resolve().parent.parent
    assert (root / "src/gnd/coverage.schema.json").is_file()
    assert not (root / "src/gnd/schema/coverage.schema.json").exists()
    assert not (root / "src/gnd/skills/gnd-orm-core/references/coverage.schema.json").exists()
    from test_schema_sync import SCHEMA_PAIRS

    assert "coverage.schema.json" not in SCHEMA_PAIRS


def _assert_forbidden_word_absent(raw: bytes) -> None:
    assert b"evidenced" not in raw


def test_schema_and_all_corpus_payloads_never_say_evidenced(tmp_path: Path) -> None:
    schema_path = Path(__file__).resolve().parent.parent / "src/gnd/coverage.schema.json"
    _assert_forbidden_word_absent(schema_path.read_bytes())
    for name in ("mixed", "positional", "refused"):
        _assert_forbidden_word_absent(canonical_payload(_payload(name)).encode())

    planted = tmp_path / "coverage.schema.json"
    planted.write_bytes(schema_path.read_bytes() + b'\n{"evidenced": true}\n')
    with pytest.raises(AssertionError):
        _assert_forbidden_word_absent(planted.read_bytes())


TOP_KEYS = {
    "schema_version",
    "tool",
    "command",
    "gnd_version",
    "model",
    "sources",
    "census",
    "elements",
    "unmatched_covers",
    "unstable_addresses",
    "covers_exemptions",
}
FORBIDDEN_KEYS = {
    "passed",
    "percent",
    "score",
    "total",
    "ratio",
    "rate",
    "pct",
    "grade",
    "coverage",
    "evidenced",
}


def _walk_keys(value: object):  # type: ignore[no-untyped-def]
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _walk_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


def _assert_quote_shape(evidence: dict[str, object]) -> None:
    quote = evidence["quote"]
    assert isinstance(quote, dict)
    source = evidence["source"]
    if source in {"check", "verify"}:
        expected = (
            {
                "constraint_ref",
                "constraint_type",
                "modality",
                "source",
                "status",
                "verdict",
                "reason_code",
            }
            if "constraint_ref" in quote
            else {"declared", "facts"}
        )
        assert set(quote) == expected
    elif source == "conformance":
        assert set(quote) == {
            "fact_type_id",
            "symbol",
            "relpath",
            "ownership",
            "unchecked",
        }
        assert all(set(item) == {"id", "description"} for item in quote["unchecked"])
    elif "index" in quote:
        assert set(quote) == {"index", "operation", "verdicts"}
        for verdict in quote["verdicts"]:
            assert set(verdict) == {
                "family",
                "locator",
                "kind",
                "modality",
                "verdict",
                "message",
                "reason_code",
                "direction",
                "fact_type",
            }
    elif "operations" in quote:
        assert set(quote) == {"fact_type", "modality", "reason", "operations"}
    else:
        assert set(quote) == {
            "family",
            "locator",
            "kind",
            "modality",
            "verdict",
            "message",
            "reason_code",
            "direction",
            "fact_type",
        }


def _assert_payload_shape(payload: dict[str, object]) -> None:
    assert set(payload) == TOP_KEYS
    assert not (set(_walk_keys(payload)) & FORBIDDEN_KEYS)
    assert set(payload["model"]) == {"path", "version", "digest"}  # type: ignore[arg-type]
    assert set(payload["sources"]) == {  # type: ignore[arg-type]
        # Always present, possibly empty (v5.1 Phase 3): "every source named
        # its model" and "we did not look" are different facts.
        "unbound",
        "experiments",
        "check",
        "verify",
        "conformance",
        "transition",
        "refused",
    }
    assert set(payload["census"]) == {  # type: ignore[arg-type]
        "operation",
        "fact_type",
        "constraint",
    }
    for counts in payload["census"].values():  # type: ignore[union-attr]
        assert set(counts) == {
            "in_model",
            "claimed",
            "corroborated",
            "unclaimed",
            "unclaimed_with_evidence",
        }
    for element in payload["elements"]:  # type: ignore[union-attr]
        assert set(element) == {
            "address",
            "class",
            "addressing",
            "status",
            "claims",
            "evidence",
        }
        assert all(
            set(claim) == {"experiment", "path", "conclusions"} for claim in element["claims"]
        )
        for item in element["evidence"]:
            assert set(item) == {"source", "path", "quote"}
            _assert_quote_shape(item)
    assert all(
        set(row) == {"experiment", "path", "address", "reason"}
        for row in payload["unmatched_covers"]  # type: ignore[union-attr]
    )
    assert all(
        set(row) == {"experiment", "path", "address", "note"}
        for row in payload["unstable_addresses"]  # type: ignore[union-attr]
    )
    assert all(
        set(row) == {"experiment", "path", "exemption"}
        for row in payload["covers_exemptions"]  # type: ignore[union-attr]
    )


def test_payload_key_sets_are_pinned_field_for_field() -> None:
    for name in ("mixed", "positional", "refused"):
        _assert_payload_shape(_payload(name))

    planted = copy.deepcopy(_payload("mixed"))
    planted["percent_covered"] = 0.5
    with pytest.raises(AssertionError):
        _assert_payload_shape(planted)


def test_payloads_validate_and_census_reconciles_to_the_answer_keys() -> None:
    root = Path(__file__).resolve().parent.parent
    schema = json.loads((root / "src/gnd/coverage.schema.json").read_text())
    validator = Draft202012Validator(schema)
    for name in ("mixed", "positional", "refused"):
        payload = _payload(name)
        validator.validate(payload)
        answer = json.loads((FIXTURES / name / "expected.json").read_text())["answer"]
        assert payload["model"]["digest"] == answer["model_digest"]  # type: ignore[index]
        assert payload["census"] == answer["census"]
        for counts in payload["census"].values():  # type: ignore[union-attr]
            assert counts["claimed"] + counts["unclaimed"] == counts["in_model"]
            assert counts["corroborated"] <= counts["claimed"]
            assert counts["unclaimed_with_evidence"] <= counts["unclaimed"]


def _assert_monotonic(before: dict[str, object], after: dict[str, object]) -> None:
    for element_class in ("operation", "fact_type", "constraint"):
        left = before["census"][element_class]  # type: ignore[index]
        right = after["census"][element_class]  # type: ignore[index]
        for key in ("in_model", "claimed", "corroborated", "unclaimed_with_evidence"):
            assert right[key] >= left[key]


def _assert_same_census(left: dict[str, object], right: dict[str, object]) -> None:
    assert left["census"] == right["census"]


def test_adding_evidence_is_census_monotonic_and_fail_still_corroborates(
    tmp_path: Path,
) -> None:
    baseline = build_payload(
        _build_tree("refused", include={"--experiments"}),
        gnd_version=resolve_version(),
    )
    failed = build_payload(
        _build_tree("refused", include={"--experiments", "--check"}),
        gnd_version=resolve_version(),
    )
    _assert_monotonic(baseline, failed)

    passing_path = tmp_path / "all-pass.json"
    passing_document = json.loads((FIXTURES / "refused/evidence/check-all-fail.json").read_text())
    for verdict in passing_document["verdicts"]:
        verdict["verdict"] = "pass"
    passing_path.write_text(json.dumps(passing_document), encoding="utf-8")
    tree = FIXTURES / "refused"
    passing = build_payload(
        build_coverage(
            load_model(tree / "v2_worked_example.orm.yaml"),
            model_path="v2_worked_example.orm.yaml",
            experiments=[tree / "experiments"],
            check=[passing_path],
            verify=[],
            conformance=[],
            transition=[],
        ),
        gnd_version=resolve_version(),
    )
    _assert_same_census(passing, failed)

    defective = copy.deepcopy(failed)
    defective["census"]["constraint"]["corroborated"] -= 1
    with pytest.raises(AssertionError):
        _assert_same_census(passing, defective)


def test_model_digest_uses_the_transition_digest_for_every_payload() -> None:
    for name in ("mixed", "positional", "refused"):
        tree = FIXTURES / name
        answer = json.loads((tree / "expected.json").read_text())
        model = load_model(tree / answer["arguments"][0])
        assert _payload(name)["model"]["digest"] == model_digest(model)  # type: ignore[index]


def test_human_render_groups_classes_and_keeps_loud_sections() -> None:
    rendered = render_coverage(_payload("mixed"))
    assert rendered.index("OPERATIONS CENSUS") < rendered.index("OPERATIONS\n")
    assert rendered.index("OPERATIONS\n") < rendered.index("FACT TYPES\n")
    assert rendered.index("FACT TYPES\n") < rendered.index("CONSTRAINTS\n")
    assert rendered.index("UNMATCHED COVERS") < rendered.index("UNSTABLE ADDRESSES")
    assert rendered.index("UNSTABLE ADDRESSES") < rendered.index("COVERS EXEMPTIONS")
    assert "percent" not in rendered.lower()
    assert "constraint:no_such_constraint" in rendered

    positional = render_coverage(_payload("positional"))
    positional_rows = sum(
        element["addressing"] == "positional"
        for element in _payload("positional")["elements"]  # type: ignore[union-attr]
    )
    assert positional.count("    unstable\n") == positional_rows


def test_conclusions_never_promote_a_claim_and_the_census_agrees_with_the_rows() -> None:
    """D6, made falsifiable -- the guard a mutation found missing.

    Every other ``conclusions-present`` claim in the corpus sits on an element a
    payload already corroborates, where "conclusions corroborate" and
    "conclusions do not corroborate" are indistinguishable. A build that treated
    a CONCLUSIONS.md as evidence produced byte-identical goldens and passed the
    whole suite, which is this milestone's defining defect wearing D6's clothes:
    a declared rule with no case that can fail it.

    Two halves, and both are needed. The BEHAVIOUR half: an element claimed by an
    experiment that carries conclusions, and named by no payload, stays
    ``claimed``. The COUNT half: the per-class ``corroborated`` census equals the
    number of rows actually holding that status -- without it, a census inflated
    independently of the rows goes unnoticed.
    """

    payload = json.loads((FIXTURES / "mixed" / "expected.payload.json").read_text(encoding="utf-8"))
    rows = {row["address"]: row for row in payload["elements"]}

    discriminator = rows["operation:flag_work_item"]
    conclusions = {claim["conclusions"] for claim in discriminator["claims"]}
    assert conclusions == {"conclusions-present", "no-conclusions"}, (
        "the D6 discriminator must carry BOTH conclusion states on one element, "
        "so the rule is tested rather than the fixture's shape"
    )
    assert not discriminator["evidence"], "no payload may name the discriminator element"
    assert discriminator["status"] == "claimed", (
        "a CONCLUSIONS.md is written by the same author as the covers row it sits "
        "beside; treating one as evidence for the other is self-corroboration"
    )

    for tree in ("mixed", "positional", "refused"):
        document = json.loads(
            (FIXTURES / tree / "expected.payload.json").read_text(encoding="utf-8")
        )
        for element_class, counts in document["census"].items():
            observed = sum(
                row["status"] == "corroborated"
                for row in document["elements"]
                if row["class"] == element_class
            )
            assert counts["corroborated"] == observed, (
                f"{tree}/{element_class}: census says {counts['corroborated']} "
                f"corroborated and the element rows say {observed}"
            )
