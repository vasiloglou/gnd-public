"""Original patch staging cleanup, failure, and publication identity guards."""
import shutil
from pathlib import Path

import pytest
from test_public_v72_session_staging_support import (
    _exact_session_materializer,  # noqa: F401 -- pytest fixture
)

from gnd.artifacts import canonical_json_bytes
from gnd.exp import session_store


@pytest.mark.parametrize("domain", ["dispatch", "release"])
@pytest.mark.parametrize("variant", ["clean", "replacement"])
def test_staged_source_cleanup(domain, variant, tmp_path):
    from tests.support.v71_session_cases import base_files, bundle, patch_contract, proposal

    b = bundle(domain, tmp_path.resolve())
    base, digest, _ = base_files(b)
    store = session_store.SessionStore(tmp_path / "stage", run_id="stage")
    doc = proposal(
        b,
        [
            {"op": "replace-artifact", "artifact": "candidate.pop.json", "value": b["population"]},
            {"op": "replace-artifact", "artifact": "notes.json", "value": {"note": "replaced"}},
        ],
        None,
    )
    staged = store.stage_patch_candidate(
        attempt_index=1,
        base_root=base,
        base_sha256=digest,
        proposal_raw=canonical_json_bytes(doc),
        contract=patch_contract(b),
    )
    source = staged._source_root
    if variant == "replacement":
        source.rename(source.with_name("preserved-original"))
        source.mkdir()
        (source / "racer.txt").write_bytes(b"preserve racer")
    store._discard_staged(1, staged)
    assert not staged._staging_path.exists()
    if variant == "clean":
        assert not source.exists()
    else:
        assert (source / "racer.txt").read_bytes() == b"preserve racer"
    assert base.is_dir(), "caller-owned candidate root is not a cleanup target"

@pytest.mark.parametrize("domain", ["dispatch", "release"])
def test_patch_stage_creation_failure_cleans_owned_input(domain, tmp_path, monkeypatch):
    from tests.support.v71_session_cases import base_files, bundle, patch_contract, proposal

    b = bundle(domain, tmp_path.resolve())
    base, digest, _ = base_files(b)
    store = session_store.SessionStore(tmp_path / "stage-failure", run_id="stage-failure")
    doc = proposal(
        b,
        [
            {"op": "replace-artifact", "artifact": "candidate.pop.json", "value": b["population"]},
            {"op": "replace-artifact", "artifact": "notes.json", "value": {"note": "replaced"}},
        ],
        None,
    )

    def refuse(**kwargs):
        assert kwargs["candidate_root"].is_dir()
        raise ValueError("phase5 injected snapshot creation failure")

    monkeypatch.setattr(store, "stage_candidate", refuse)
    with pytest.raises(ValueError, match="injected snapshot creation failure"):
        store.stage_patch_candidate(
            attempt_index=1,
            base_root=base,
            base_sha256=digest,
            proposal_raw=canonical_json_bytes(doc),
            contract=patch_contract(b),
        )
    assert not list((store.root / ".staging").iterdir())
    assert base.is_dir()

@pytest.mark.parametrize("domain", ["dispatch", "release"])
def test_patch_source_replaced_after_publication_is_refused(domain, tmp_path, monkeypatch):
    from tests.support.v71_session_cases import base_files, bundle, patch_contract, proposal

    b = bundle(domain, tmp_path.resolve())
    base, digest, _ = base_files(b)
    store = session_store.SessionStore(tmp_path / "stage-race", run_id="stage-race")
    doc = proposal(
        b,
        [
            {"op": "replace-artifact", "artifact": "candidate.pop.json", "value": b["population"]},
            {"op": "replace-artifact", "artifact": "notes.json", "value": {"note": "replaced"}},
        ],
        None,
    )
    original = session_store.publish_directory_once
    reached = []

    def swap(root, relative, files, **kwargs):
        result = original(root, relative, files, **kwargs)
        path = Path(root) / relative
        saved = path.with_name("original-private-source")
        path.rename(saved)
        shutil.copytree(saved, path)
        reached.append(path)
        return result

    monkeypatch.setattr(session_store, "publish_directory_once", swap)
    with pytest.raises(ValueError):
        store.stage_patch_candidate(
            attempt_index=1,
            base_root=base,
            base_sha256=digest,
            proposal_raw=canonical_json_bytes(doc),
            contract=patch_contract(b),
        )
    assert reached
    assert (reached[0] / "candidate.pop.json").is_file()
