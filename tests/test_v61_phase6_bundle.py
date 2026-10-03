from __future__ import annotations

import base64
import json
from pathlib import Path

import pytest

from gnd.declared_adapter import CandidateBundleError, apply_candidate_bundle


def test_b01_bundle_creates_one_file(tmp_path: Path) -> None:
    content = json.dumps({'schema_version': 1, 'files': [{'path': 'answer.json', 'content_base64': base64.b64encode(b'{}\n').decode('ascii')}]})
    apply_candidate_bundle(content, candidate_root=tmp_path)
    assert (tmp_path / 'answer.json').read_bytes() == b'{}\n'

def test_b04_traversal_refuses_before_write(tmp_path: Path) -> None:
    content = json.dumps({'schema_version': 1, 'files': [{'path': '../escape', 'content_base64': ''}]})
    with pytest.raises(CandidateBundleError):
        apply_candidate_bundle(content, candidate_root=tmp_path)
    assert list(tmp_path.iterdir()) == []

def test_b01_b03_multifile_overwrite_and_omission(tmp_path: Path) -> None:
    (tmp_path / 'keep.txt').write_text('keep', encoding='utf-8')
    (tmp_path / 'replace.txt').write_text('old', encoding='utf-8')
    content = json.dumps({'schema_version': 1, 'files': [{'path': 'replace.txt', 'content_base64': base64.b64encode(b'new').decode()}, {'path': 'nested/new.bin', 'content_base64': base64.b64encode(b'\x00\xff').decode()}]})
    apply_candidate_bundle(content, candidate_root=tmp_path)
    assert (tmp_path / 'replace.txt').read_bytes() == b'new'
    assert (tmp_path / 'nested/new.bin').read_bytes() == b'\x00\xff'
    assert (tmp_path / 'keep.txt').read_text(encoding='utf-8') == 'keep'

@pytest.mark.parametrize('content', ['{"schema_version":1,"schema_version":1,"files":[]}', '{"schema_version":1,"files":[{"path":"/absolute","content_base64":""}]}', '{"schema_version":1,"files":[{"path":"C:/drive","content_base64":""}]}', '{"schema_version":1,"files":[{"path":"bad","content_base64":"%%%"}]}', '{"schema_version":1,"files":[{"path":"same","content_base64":""},{"path":"same","content_base64":""}]}'])
def test_b04_b07_semantic_refusals_write_nothing(tmp_path: Path, content: str) -> None:
    with pytest.raises(CandidateBundleError):
        apply_candidate_bundle(content, candidate_root=tmp_path)
    assert list(tmp_path.iterdir()) == []

def test_b07_symlink_destination_is_refused(tmp_path: Path) -> None:
    outside = tmp_path.parent / 'outside-phase6.txt'
    outside.write_text('outside', encoding='utf-8')
    (tmp_path / 'link').symlink_to(outside)
    content = json.dumps({'schema_version': 1, 'files': [{'path': 'link', 'content_base64': ''}]})
    with pytest.raises(CandidateBundleError, match='symlink'):
        apply_candidate_bundle(content, candidate_root=tmp_path)
    assert outside.read_text(encoding='utf-8') == 'outside'
