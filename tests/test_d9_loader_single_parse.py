"""D9: loading a model parses its bytes once (growth-round-outcomes plan H9, D9).

`_load_model_at` parses the root bytes to see whether they declare includes;
a model without includes is then validated from that same document rather
than from a second parse. Sharing the document is safe only while validation
never writes into it, so every committed model fixture is checked for that,
whether it loads or is refused.
"""

from __future__ import annotations

import contextlib
from collections import Counter
from pathlib import Path
from unittest import mock

import pytest

from gnd.errors import ModelLoadError, ModelValidationError, ReferenceInputError
from gnd.model import _load_model_document as load_model_document
from gnd.model import _parsing, load_model, load_model_bytes

FIXTURES = Path(__file__).parent / "fixtures"
MODELS = sorted(
    path for pattern in ("*.orm.yaml", "*.orm.json") for path in FIXTURES.rglob(pattern)
)
#: The refusals a committed fixture meets; any other exception fails the test.
REFUSED = (ModelLoadError, ModelValidationError, ReferenceInputError)


def _counting_parses() -> tuple[Counter, mock._patch]:
    seen: Counter = Counter()
    real = _parsing._parse_model_document

    def counting(data: bytes, *, source):
        seen[bytes(data)] += 1
        return real(data, source=source)

    return seen, mock.patch.object(_parsing, "_parse_model_document", counting)


def test_d9_there_are_model_fixtures_to_read() -> None:
    assert len(MODELS) > 100


@pytest.mark.parametrize("path", MODELS, ids=lambda p: str(p.relative_to(FIXTURES)))
def test_d9_validation_never_writes_into_the_document(path: Path) -> None:
    data = path.read_bytes()
    try:
        document = _parsing.parse_model_document(data, source=path)
    except ModelLoadError:
        pytest.skip("not a parseable model document")
    before = _parsing._snapshot(document)
    with contextlib.suppress(*REFUSED):
        load_model_document(document)
    assert _parsing._snapshot(document) == before


@pytest.mark.parametrize("path", MODELS, ids=lambda p: str(p.relative_to(FIXTURES)))
def test_d9_load_model_parses_the_root_bytes_once(path: Path) -> None:
    data = path.read_bytes()
    seen, patch = _counting_parses()
    with patch, contextlib.suppress(*REFUSED):
        load_model(path)
    assert seen[data] <= 1


def test_d9_load_model_bytes_is_unchanged_by_the_split() -> None:
    path = FIXTURES / "v70-phase3" / "model.orm.yaml"
    data = path.read_bytes()
    from_bytes = load_model_bytes(data, source=path)
    from_document = load_model_document(_parsing.parse_model_document(data, source=path))
    assert from_document.model_dump() == from_bytes.model_dump()
    assert load_model(path).model_dump() == from_bytes.model_dump()
