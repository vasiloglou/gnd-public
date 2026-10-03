import os

import pytest

from gnd.exp import session_store


def test_discard_requires_the_owned_parent_coordinate(tmp_path):
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'input.txt').write_bytes(b'caller bytes')
    store = session_store.SessionStore(tmp_path / 'store', run_id='store')
    inside = store.root / '.staging' / 'outside'
    inside.mkdir()
    (inside / 'input.txt').write_bytes(b'other staged bytes')
    info = inside.stat()
    store._discard_owned_staging_directory(outside, (info.st_dev, info.st_ino))
    assert (outside / 'input.txt').read_bytes() == b'caller bytes'
    assert (inside / 'input.txt').read_bytes() == b'other staged bytes'

def test_cleanup_move_after_open_preserves_caller_bytes(tmp_path, monkeypatch):
    store = session_store.SessionStore(tmp_path / 'store', run_id='store')
    source = store.root / '.staging' / 'owned'
    source.mkdir()
    (source / 'copy.txt').write_bytes(b'owned copy')
    info = source.stat()
    identity = (info.st_dev, info.st_ino)
    outside = tmp_path / 'caller-root'
    original = os.fstat
    reached = []

    def move(fd):
        result = original(fd)
        if not reached and (result.st_dev, result.st_ino) == identity:
            reached.append(True)
            source.rename(outside)
            (outside / 'caller.txt').write_bytes(b'caller bytes')
            source.mkdir()
            (source / 'racer.txt').write_bytes(b'replacement bytes')
        return result
    monkeypatch.setattr(session_store.os, 'fstat', move)
    store._discard_owned_staging_directory(source, identity)
    assert reached
    assert (outside / 'caller.txt').read_bytes() == b'caller bytes'
    assert (source / 'racer.txt').read_bytes() == b'replacement bytes'

@pytest.mark.parametrize('fault', ['exchange', 'clear', 'replacement'])
def test_private_cleanup_claim_failure_preserves_bytes(fault, tmp_path, monkeypatch):
    store = session_store.SessionStore(tmp_path / 'store', run_id='store')
    source = store.root / '.staging' / 'owned'
    source.mkdir()
    (source / 'copy.txt').write_bytes(b'owned copy')
    info = source.stat()
    identity = (info.st_dev, info.st_ino)
    original = session_store._exchange_paths_atomic
    reached = []

    def exchange(*args):
        if not reached:
            reached.append(True)
            if fault == 'exchange':
                raise OSError('injected claim failure')
            if fault == 'replacement':
                source.rename(tmp_path / 'saved')
                source.mkdir()
                (source / 'caller.txt').write_bytes(b'caller replacement')
        return original(*args)

    def clear(fd):
        reached.append(True)
        raise OSError('injected clear failure')
    monkeypatch.setattr(session_store, '_exchange_paths_atomic', exchange)
    if fault == 'clear':
        monkeypatch.setattr(session_store, '_clear_directory_fd', clear)
    store._discard_owned_staging_directory(source, identity)
    assert reached
    assert not list((store.root / '.staging').glob('cleanup-*'))
    if fault == 'replacement':
        assert (source / 'caller.txt').read_bytes() == b'caller replacement'
        assert (tmp_path / 'saved' / 'copy.txt').read_bytes() == b'owned copy'
    else:
        assert (source / 'copy.txt').read_bytes() == b'owned copy'

def test_private_claim_moved_before_clear_is_refused(tmp_path, monkeypatch):
    store = session_store.SessionStore(tmp_path / 'store', run_id='store')
    source = store.root / '.staging' / 'owned'
    source.mkdir()
    (source / 'copy.txt').write_bytes(b'owned copy')
    info = source.stat()
    identity = (info.st_dev, info.st_ino)
    original = os.fstat
    reached = []
    outside = tmp_path / 'moved-claim'

    def move(fd):
        opened = original(fd)
        if not reached and (opened.st_dev, opened.st_ino) == identity:
            private = next(source.parent.glob('cleanup-*'))
            private.rename(outside)
            private.mkdir()
            (private / 'caller.txt').write_bytes(b'replacement caller bytes')
            reached.append(True)
        return opened
    monkeypatch.setattr(session_store.os, 'fstat', move)
    store._discard_owned_staging_directory(source, identity)
    assert reached
    assert (outside / 'copy.txt').read_bytes() == b'owned copy'
    assert (source / 'caller.txt').read_bytes() == b'replacement caller bytes'
