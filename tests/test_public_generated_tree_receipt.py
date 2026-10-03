from __future__ import annotations

from pathlib import Path

import pytest
from support.generated_project import generate_project
from support.public_codegen_receipt import read_receipt

CORPUS_MODEL="tests/fixtures/v51-generated-project/alpha/model.orm.yaml"

@pytest.fixture
def outsider(tmp_path: Path):
    """A project generated into `tmp_path` -- outside the checkout, by design."""
    return generate_project(CORPUS_MODEL, tmp_path / "alpha", package="model")

def test_the_tree_matches_the_committed_receipt(outsider) -> None:
    """T1.1a. Same answer key the corpus gate approved, reached through the
    fixture rather than an inline subprocess call."""
    expected = read_receipt("alpha")
    assert set(outsider.manifest) == set(expected)
    for relpath, digest in expected.items():
        if digest is None:
            continue  # path-embedding file: present-only (IF-P1-3)
        assert outsider.manifest[relpath] == digest, relpath
