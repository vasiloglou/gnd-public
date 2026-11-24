"""OB3: the Ossie semantic model and mapping against their owner-approved corpus.

The corpus (tests/fixtures/ossie_relational) and its hand-derived expected files were
approved at the OB3 corpus gate before any renderer existed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from support import ossie_relational_corpus as corpus

ROOT = Path(__file__).resolve().parents[1]
CASES = corpus.cases()


def _render(number, output_format="yaml"):
    from gnd.export.ossie import render_ossie

    return render_ossie(
        corpus.rmap_case(number), output_format=output_format, document_name=f"ontology.{output_format}"
    )


@pytest.mark.parametrize("number", CASES)
def test_t1_yaml_equals_the_approved_files(number):
    bundle = _render(number)
    directory = corpus.CORPUS / number
    assert bundle.semantic_model == (directory / "expected.semantic_model.yaml").read_bytes()
    assert bundle.mapping == (directory / "expected.mapping.yaml").read_bytes()


@pytest.mark.parametrize("number", CASES)
def test_t1_extension_parses_to_the_readable_copy(number):
    mapping = corpus.load_yaml_bytes(_render(number).mapping)
    (extension,) = mapping["custom_extensions"]
    expected = json.loads((corpus.CORPUS / number / "expected.extension.json").read_text(encoding="utf-8"))
    assert json.loads(extension["data"]) == expected


@pytest.mark.parametrize("number", CASES)
def test_t1_json_equals_the_approved_structure(number):
    bundle = _render(number, "json")
    directory = corpus.CORPUS / number
    semantic = json.loads(bundle.semantic_model)
    mapping = json.loads(bundle.mapping)
    assert semantic == corpus.load_yaml(directory / "expected.semantic_model.yaml")
    expected = corpus.load_yaml(directory / "expected.mapping.yaml")
    # The JSON run names JSON files and binds the JSON bytes, so those members differ.
    assert mapping["ontology_ref"]["iri"] == "./ontology.json"
    assert mapping["semantic_model_ref"]["iri"] == "./ontology.json.semantic_model.json"
    for document in (mapping, expected):
        document.pop("ontology_ref"), document.pop("semantic_model_ref")
    actual_payload = json.loads(mapping.pop("custom_extensions")[0]["data"])
    expected_payload = json.loads(expected.pop("custom_extensions")[0]["data"])
    for key in ("ontology_sha256", "semantic_model_sha256"):
        actual_payload.pop(key), expected_payload.pop(key)
    assert mapping == expected
    assert actual_payload == expected_payload
