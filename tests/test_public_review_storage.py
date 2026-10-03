import base64
import gzip
import hashlib
import json
import os

import pytest
from support.public_migration import load_case_map
from support.public_review_storage import migration_view

# Historical migration accounting/storage; current product assertions remain in default tests.
pytestmark = pytest.mark.evidence


def packed(entries):
    return gzip.compress(json.dumps({'format': 'lossless-reviewed-leaves-v1', 'entries': entries}).encode(), mtime=0)


def entry(name, raw):
    return {'path': name, 'sha256': hashlib.sha256(raw).hexdigest(), 'raw_base64': base64.b64encode(raw).decode()}


def test_compressed_case_map_and_originals_are_raw_exact_and_loader_compatible(tmp_path):
    subject = tmp_path.resolve()
    row = {'source_node': 'source-case-00000', 'source_sha256': 'a' * 64}
    raw = gzip.compress(json.dumps(row).encode(), mtime=0)
    originals = b'[{"immutable":"original authored projection"}]\n'
    (subject / 'reviewed-leaves-01.json.gz').write_bytes(packed([entry('sample-case-map.jsonl.gz', raw), entry('sample-originals.json', originals)]))
    with migration_view(subject, expected_packs={'reviewed-leaves-01.json.gz': (hashlib.sha256((subject / 'reviewed-leaves-01.json.gz').read_bytes()).hexdigest(), 2)}) as root:
        assert (root / 'sample-case-map.jsonl.gz').read_bytes() == raw
        assert (root / 'sample-originals.json').read_bytes() == originals
        assert load_case_map(root / 'sample-case-map.jsonl.gz') == (row,)


@pytest.mark.parametrize('mutation', ['traversal', 'duplicate', 'digest', 'physical_collision', 'symlink', 'fifo', 'compressed_cap', 'expanded_cap', 'raw_cap'])
def test_transport_refuses_unsafe_or_corrupt_storage(mutation, tmp_path):
    subject = tmp_path.resolve()
    item = entry('sample-originals.json', b'original bytes')
    entries = [item]
    if mutation == 'traversal': item['path'] = '../sample-originals.json'
    if mutation == 'duplicate': entries.append(dict(item))
    if mutation == 'digest': item['sha256'] = '0' * 64
    if mutation == 'raw_cap': entries = [entry('sample-originals.json', b'x' * 1048577)]
    raw = packed(entries)
    if mutation == 'compressed_cap': raw = b'x' * 1048577
    if mutation == 'expanded_cap': raw = gzip.compress(b'x' * 2097153, mtime=0)
    (subject / 'reviewed-leaves-01.json.gz').write_bytes(raw)
    if mutation == 'physical_collision': (subject / item['path']).write_bytes(b'physical copy')
    if mutation == 'symlink': (subject / 'bad').symlink_to(subject / 'reviewed-leaves-01.json.gz')
    if mutation == 'fifo': os.mkfifo(subject / 'bad')
    with pytest.raises((ValueError, OSError)), migration_view(subject, expected_packs={'reviewed-leaves-01.json.gz': (hashlib.sha256(raw).hexdigest(), len(entries))}):
        pass


@pytest.mark.parametrize('mutation', ['unapproved_pack', 'pin', 'missing_pack', 'count'])
def test_closed_pack_roster_and_pins_refuse(mutation, tmp_path):
    subject = tmp_path.resolve()
    raw = packed([entry('sample-originals.json', b'exact')])
    pins = {'reviewed-leaves-01.json.gz': (hashlib.sha256(raw).hexdigest(), 1)}
    (subject / 'reviewed-leaves-01.json.gz').write_bytes(raw)
    if mutation == 'unapproved_pack': (subject / 'reviewed-leaves-02.json.gz').write_bytes(raw)
    elif mutation == 'missing_pack': (subject / 'reviewed-leaves-01.json.gz').unlink()
    elif mutation == 'count': pins['reviewed-leaves-01.json.gz'] = (hashlib.sha256(raw).hexdigest(), 2)
    else: pins['reviewed-leaves-01.json.gz'] = ('0' * 64, 1)
    with pytest.raises(ValueError), migration_view(subject, expected_packs=pins):
        pass


def test_restrictive_umask_cannot_change_recovered_leaf_bytes_or_modes(tmp_path):
    subject = tmp_path.resolve()
    raw = packed([entry('sample-originals.json', b'exact approved bytes')])
    pins = {'reviewed-leaves-01.json.gz': (hashlib.sha256(raw).hexdigest(), 1)}
    (subject / 'reviewed-leaves-01.json.gz').write_bytes(raw)
    previous = os.umask(0o077)
    try:
        with migration_view(subject, expected_packs=pins) as root:
            path = root / 'sample-originals.json'
            assert path.read_bytes() == b'exact approved bytes'
            assert path.stat().st_mode & 0o777 == 0o644
    finally:
        os.umask(previous)
