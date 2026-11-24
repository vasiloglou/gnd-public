"""OB4: `gnd export ossie --physical-binding` against its owner-approved corpus.

The corpus (tests/fixtures/physical_binding), its refusal table and the packaged
schema were approved at the OB4 corpus gate before any binding reader existed.
"""

from __future__ import annotations

import json

import pytest
from support import ossie_relational_corpus as relational
from support import physical_binding_corpus as corpus

CASES = corpus.cases()
ROWS = corpus.refusal_rows()


def _render(case, output_format="yaml", **extra):
    from gnd.export.ossie import render_ossie

    return render_ossie(
        corpus.model_path(case), output_format=output_format,
        physical_binding=corpus.CORPUS / case / "binding.json", **extra,
    )


def _argv(model, out, *extra):
    return ["export", "ossie", str(model), "--out", str(out), *extra]


@pytest.mark.parametrize("case", CASES)
def test_t1_yaml_equals_the_approved_files(case):
    bundle = _render(case)
    directory = corpus.CORPUS / case
    assert bundle.semantic_model == (directory / "expected.semantic_model.yaml").read_bytes()
    assert bundle.mapping == (directory / "expected.mapping.yaml").read_bytes()


@pytest.mark.parametrize("case", CASES)
def test_t1_extension_parses_to_the_readable_copy(case):
    mapping = relational.load_yaml_bytes(_render(case).mapping)
    (extension,) = mapping["custom_extensions"]
    expected = json.loads((corpus.CORPUS / case / "expected.extension.json").read_text(encoding="utf-8"))
    assert json.loads(extension["data"]) == expected


def _write_refusal(row, directory):
    """The row's binding file under ``directory``; a directory for the not-a-file row."""
    path = directory / "binding.json"
    data = corpus.refusal_bytes(row)
    if data is None:
        path.mkdir()
    else:
        path.write_bytes(data)
    return path


@pytest.mark.parametrize("row", ROWS, ids=[row["id"] for row in ROWS])
def test_t4_each_bad_binding_is_refused_by_its_rule(row, tmp_path, capsys):
    from gnd import cli

    binding = _write_refusal(row, tmp_path)
    model = corpus.model_path(row.get("base", "V1"))
    out = tmp_path / "out"
    out.mkdir()
    assert cli.main(_argv(model, out / "o.yaml", "--physical-binding", str(binding))) == 3
    captured = capsys.readouterr()
    assert row["rule"] in captured.err, captured.err
    assert "Traceback" not in captured.err
    assert not list(out.iterdir())
