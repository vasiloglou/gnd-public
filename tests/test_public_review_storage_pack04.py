import hashlib
import json
import os

import pytest
from support import public_review_storage as storage
from test_public_review_storage_pack02 import _entry, _pack

# Historical migration accounting/storage; current product assertions remain in default tests.
pytestmark = pytest.mark.evidence


@pytest.mark.parametrize("mutation", ["none", "missing_fourth", "unexpected_fifth", "corrupt_fourth", "swapped_partition", "duplicate_member", "changed_member_pin"])
def test_four_default_pack_partitions_remain_closed(mutation, tmp_path, monkeypatch):
    root = tmp_path.resolve()
    entries = [_entry(f"part-{index}-case-map.jsonl.gz", f"original-{index}\n") for index in range(4)]
    names = tuple(f"reviewed-leaves-{index:02d}.json.gz" for index in range(1, 5))
    documents = [_pack([entry]) for entry, _ in entries]
    pins = {name: (hashlib.sha256(raw).hexdigest(), 1) for name, raw in zip(names, documents, strict=True)}
    leaves = {entry["path"]: entry["sha256"] for entry, _ in entries}
    partitions = {name: (entry["path"],) for name, (entry, _) in zip(names, entries, strict=True)}
    if mutation == "swapped_partition":
        partitions[names[0]], partitions[names[3]] = partitions[names[3]], partitions[names[0]]
    elif mutation == "duplicate_member":
        documents[3] = documents[0]
        pins[names[3]] = (hashlib.sha256(documents[3]).hexdigest(), 1)
        partitions[names[3]] = partitions[names[0]]
    elif mutation == "changed_member_pin":
        leaves[entries[3][0]["path"]] = "0" * 64
    for name, raw in zip(names, documents, strict=True):
        (root / name).write_bytes(raw)
    monkeypatch.setattr(storage, "PACK_PINS", pins)
    monkeypatch.setattr(storage, "LEAF_PINS", leaves)
    monkeypatch.setattr(storage, "PACK_LEAVES", partitions)
    if mutation == "missing_fourth":
        (root / names[3]).unlink()
    elif mutation == "unexpected_fifth":
        (root / "reviewed-leaves-05.json.gz").write_bytes(documents[3])
    elif mutation == "corrupt_fourth":
        (root / names[3]).write_bytes(documents[3] + b"changed")
    if mutation == "none":
        previous = os.umask(0o077)
        try:
            with storage.migration_view(root) as logical:
                assert len(tuple(logical.iterdir())) == 4
                for entry, raw in entries:
                    assert (logical / entry["path"]).read_bytes() == raw
                    assert (logical / entry["path"]).stat().st_mode & 0o777 == 0o644
        finally:
            os.umask(previous)
    else:
        with pytest.raises(ValueError), storage.migration_view(root):
            pass


def test_previous_three_fixed_packs_and_leaf_pins_are_unchanged():
    old = {'reviewed-leaves-01.json.gz': ('1f1c2d6d87a9c62d60e6e8428d6cb06424be923788d5d5d5a4ebd9c264383493', 64), 'reviewed-leaves-02.json.gz': ('ff6f083bf0269a58e423f3d7a333fa768e68f35416eab6bd542c633f8397b897', 128), 'reviewed-leaves-03.json.gz': ('f399f46cb3ecd8ef326464ca729f61baabdbee8857bc4119897a8c61b8ec6b88', 64)}
    assert {name: storage.PACK_PINS[name] for name in old} == old
    names = tuple(name for pack in old for name in storage.PACK_LEAVES[pack])
    assert len(names) == len(set(names)) == 256
    old_leaves = {name: storage.LEAF_PINS[name] for name in names}
    assert hashlib.sha256(json.dumps(old_leaves, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == '3842fa8a144a8e8932257036b483110878388f3ae524c4b14b8ca4c8618646f1'
    assert storage.FILE_CAP == 1048576 and storage.EXPANDED_CAP == 2097152
