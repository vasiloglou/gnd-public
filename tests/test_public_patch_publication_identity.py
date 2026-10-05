"""Patch publication must bind exactly one owned directory identity."""
import sys
from pathlib import Path

# Preserve the original tests.support import against this target checkout.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest

from gnd.artifacts import canonical_json_bytes
from gnd.exp import session_store


@pytest.mark.parametrize("binding", ["missing", "repeated"])
def test_patch_source_ambiguous_publication_identity_is_refused(binding, tmp_path, monkeypatch):
    from tests.support.v71_session_cases import base_files, bundle, patch_contract, proposal

    b = bundle("dispatch", tmp_path.resolve())
    base, digest, _ = base_files(b)
    store = session_store.SessionStore(tmp_path / "stage-binding", run_id="stage-binding")
    doc = proposal(
        b,
        [
            {"op": "replace-artifact", "artifact": "candidate.pop.json", "value": b["population"]},
            {"op": "replace-artifact", "artifact": "notes.json", "value": {"note": "seed"}},
        ],
        None,
    )
    original = session_store.publish_directory_once
    reached = []

    def corrupt(root, relative, files, **kwargs):
        result = original(root, relative, files, **kwargs)
        identities = kwargs["_published_identity"]
        assert len(identities) == 1
        identities.clear() if binding == "missing" else identities.append(identities[0])
        reached.append(Path(root) / relative)
        return result

    monkeypatch.setattr(session_store, "publish_directory_once", corrupt)
    with pytest.raises(ValueError, match="did not bind one directory identity"):
        store.stage_patch_candidate(
            attempt_index=1,
            base_root=base,
            base_sha256=digest,
            proposal_raw=canonical_json_bytes(doc),
            contract=patch_contract(b),
        )
    assert reached and (reached[0] / "candidate.pop.json").is_file()
    assert (base / "candidate.pop.json").is_file()

