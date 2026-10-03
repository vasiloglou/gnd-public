"""Complete original citation parser/cap guards over generic fixture records."""
from __future__ import annotations

import atexit
import base64
import gzip
import hashlib
import io
import json
import tempfile
from pathlib import Path

import pytest
from support.planning_tree import PlanningTreeError, read_citations

ROOT = Path(__file__).resolve().parents[1]
_FIXTURE_WIRE = (ROOT / "tests/fixtures/public-frontmatter-parser/records.json.gz").read_bytes()
assert len(_FIXTURE_WIRE) <= 1048576
assert hashlib.sha256(_FIXTURE_WIRE).hexdigest() == '1b779e3fd87889509b9fc3336df965b42a2e1a675c4f5dcf4ff40a484884fa80'
with gzip.GzipFile(fileobj=io.BytesIO(_FIXTURE_WIRE)) as _stream:
    _FIXTURE_BYTES = _stream.read(2097153)
assert len(_FIXTURE_BYTES) <= 2097152
_DOCUMENT = json.loads(_FIXTURE_BYTES)
assert _DOCUMENT['format'] == 'exact-public-frontmatter-fixtures-v1'
_EXPECTED = ('records/any-key.md', 'records/digestless-rows.md', 'records/evidence-not-a-list.md', 'records/no-fence.md', 'records/questions-carry.md', 'records/questions.md', 'records/well-formed.md', 'records-defective/digest-not-hex.md', 'records-defective/digest-yaml-typed.md', 'records-defective/fenced-broken-yaml.md', 'records-defective/not-a-mapping.md', 'records-defective/path-escape.md')
assert tuple(row['path'] for row in _DOCUMENT['entries']) == _EXPECTED
_TEMP = tempfile.TemporaryDirectory(prefix='gnd-frontmatter-parser-')
atexit.register(_TEMP.cleanup)
_CORPUS = Path(_TEMP.name).resolve()
for _row in _DOCUMENT['entries']:
    _raw = base64.b64decode(_row['raw_base64'], validate=True)
    assert hashlib.sha256(_raw).hexdigest() == _row['sha256']
    _path = _CORPUS / _row['path']
    _path.parent.mkdir(parents=True, exist_ok=True)
    _path.write_bytes(_raw)
    _path.chmod(_row['mode'])
RECORDS = _CORPUS / 'records'
DEFECTIVE = _CORPUS / 'records-defective'

EXPECTED_RAISING_RECORDS = (
    "digest-not-hex.md",
    "path-escape.md",
    "digest-yaml-typed.md",
    "not-a-mapping.md",
    "fenced-broken-yaml.md",
)

def planning_tree():
    """Import the lane under test.

    Deliberately not a module-level import: at the corpus base this raises, and
    raising here makes each case red individually instead of collapsing the
    whole file into one collection error.
    """
    from support import planning_tree as module

    return module


@pytest.mark.parametrize("name", EXPECTED_RAISING_RECORDS)
def test_a9_and_a15_a_defective_record_raises_and_names_itself(name):
    """A9 and A15 -- containment refusal and a present-but-non-hex digest."""
    module = planning_tree()
    with pytest.raises(module.PlanningTreeError) as caught:
        module.read_citations(root=DEFECTIVE / name)
    assert name in str(caught.value)


def test_a8_a_non_record_contributes_nothing_and_the_caller_absorbs_the_raise():
    """A8 -- 101 of the tree's 167 markdown files have no frontmatter fence.

    Only the fence-less shape is a non-record. The fenced-but-broken shapes
    that once sat beside it here now live in ``records-defective/`` and RAISE
    (IF-P3b-17): a fenced document we cannot parse may carry citations we
    cannot see.
    """
    citations = planning_tree().read_citations(root=RECORDS)
    assert not [c for c in citations if c.record.endswith("no-fence.md")]


def test_a7_a_record_over_the_cap_is_refused_by_name(tmp_path):
    """A7 -- the cap is applied to the stat(), not after the read.

    Constructed rather than committed: a megabyte of fixture for one branch is
    not worth the tree it sits in.
    """
    module = planning_tree()
    from gnd.exp.frontmatter import MAX_DOCUMENT_BYTES

    oversize = tmp_path / "oversize.md"
    oversize.write_text("---\nmilestone: fixture\n---\n" + "x" * (MAX_DOCUMENT_BYTES + 1))
    with pytest.raises(module.PlanningTreeError) as caught:
        module.read_citations(root=tmp_path)
    assert "cap" in str(caught.value).lower()


def test_a11_an_over_cap_and_malformed_record_reports_the_cap(tmp_path):
    """A11 -- two-fault ordering, pinned by which message comes back."""
    module = planning_tree()
    from gnd.exp.frontmatter import MAX_DOCUMENT_BYTES

    (tmp_path / "both.md").write_text(
        "---\nevidence:\n  - path: README.md\n    sha256: nope\n---\n"
        + "x" * (MAX_DOCUMENT_BYTES + 1)
    )
    with pytest.raises(module.PlanningTreeError) as caught:
        module.read_citations(root=tmp_path)
    assert "cap" in str(caught.value).lower()

def test_a_fenced_record_that_cannot_be_parsed_is_a_defect_not_a_skip(tmp_path: Path) -> None:
    """A fenced document we cannot parse may carry citations we cannot see.

    The review reproduced the loss: broken YAML inside a fence made
    read_citations return () with no error. Only the fence-less shape is a
    non-record.
    """
    (tmp_path / "broken.md").write_text("---\nevidence:\n  - path: [unclosed\n---\nbody\n")
    with pytest.raises(PlanningTreeError):
        read_citations(root=tmp_path)


def test_the_cap_is_applied_before_the_read_not_after(tmp_path: Path) -> None:
    """The order discriminator the corpus A7 row could not provide.

    An over-cap file with no read permission: stat()-then-cap raises the cap
    refusal without ever opening the file; read-then-cap trips PermissionError
    first and surfaces as could-not-be-read. The two orders are observably
    different on exactly this input, which the review pointed out A7's
    oversize-only fixture never was.
    """
    import os

    from gnd.exp.frontmatter import MAX_DOCUMENT_BYTES

    if os.geteuid() == 0:
        pytest.skip("root reads through chmod 000; the discriminator needs a non-root euid")
    oversize = tmp_path / "unreadable.md"
    oversize.write_text("---\nx: 1\n---\n" + "x" * (MAX_DOCUMENT_BYTES + 1))
    oversize.chmod(0)
    try:
        with pytest.raises(PlanningTreeError) as caught:
            read_citations(root=tmp_path)
        assert "cap" in str(caught.value).lower(), (
            "the refusal must be the cap, proving stat() ran and the read did not"
        )
    finally:
        oversize.chmod(0o644)

