"""RF8 unchanged qualification pins and discriminating profile controls."""
import importlib
import inspect
import json
import time
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from gnd.exp.session_contract import V2_SESSION_CONTRACT_VERSION, DataDrivenContract

ROOT = Path(__file__).resolve().parents[1]


def test_old_metadata_is_unchanged():
    rows = json.loads((ROOT / '.gnd-planning/milestones/code-refactoring/evidence/RF8/metadata-base.json').read_text())
    for module, values in rows.items():
        current = importlib.import_module(module)
        for name, expected in values.items():
            obj = getattr(current, name)
            assert {'module': obj.__module__, 'qualname': obj.__qualname__,
                    'signature': str(inspect.signature(obj))} == expected, (module, name)


def test_profile_is_not_wire_state_and_is_built_once(tmp_path, monkeypatch):
    from test_rf1_session_pins import BUILDERS, _contract
    for version, build in BUILDERS.items():
        built = build(tmp_path / str(version), monkeypatch)
        contract = _contract(built)
        before = contract.model_dump(mode='json')
        assert contract.profile is contract.profile
        assert contract.profile.contract_version == version
        assert DataDrivenContract.model_validate(contract) is contract
        assert '_profile' not in before and 'profile' not in before
        assert 'profile' not in DataDrivenContract.model_json_schema()['properties']
        assert contract.model_copy(update={'wall_seconds': 1}).profile == contract.profile
        assert contract.model_dump(mode='json') == before
        with pytest.raises(FrozenInstanceError):
            contract.profile.patch = False


def test_profile_closed_version_table_and_copy():
    from gnd.exp.session_profile import profile_for_version
    for version in range(1, 9):
        p = profile_for_version(version)
        assert p.contract_version == version
        assert p.legacy == (version == 1)
        assert p.tests == (version >= 3)
        assert p.walk == (version >= 5)
        assert p.declared_adapter == (version >= 6)
        assert p.patch == (version >= 7)
        assert p.judgments == (version == 8)
    for value in (None, 0, 9, [], {}, '7'):
        assert profile_for_version(value) is None
    # Preserve the dispatcher's original numeric equality behavior.
    assert profile_for_version(True).contract_version == 1
    assert profile_for_version(7.0).patch
    contract = DataDrivenContract.model_construct(schema_version=7)
    assert contract.profile.patch and not contract.profile.judgments
    successor = contract.model_copy(update={'schema_version': 8})
    assert successor.profile.judgments and not contract.profile.judgments
    assert V2_SESSION_CONTRACT_VERSION == 2


def test_profile_lookup_is_bounded():
    from gnd.exp.session_profile import profile_for_version
    started = time.monotonic()
    for _ in range(100_000):
        assert profile_for_version(8).judgments
    assert time.monotonic() - started < 5


def test_profile_wire_axes_and_legacy_precedence():
    from gnd.exp.session_profile import profile_for_version
    for version, axes in ((7, (3, 8, 9, 6)), (8, (4, 9, 10, 7))):
        p = profile_for_version(version)
        assert (p.launch_version, p.feedback_version, p.attempt_version, p.result_version) == axes
    p = profile_for_version(6)
    for walk, redaction, transition, payloads, expected in (
        (True, True, True, [7, 4], 7), (False, True, True, [7, 4], 6),
        (False, False, True, [7, 4], 5), (False, False, False, [7, 4], 4),
        (False, False, False, [4], 3), (False, False, False, [3], 2),
    ):
        assert p.select_feedback(walk=walk, redaction=redaction,
                                 transition=transition, payload_versions=payloads) == expected
    for walk, redaction, transition, expected in (
        (True, True, True, 5), (False, True, True, 4),
        (False, False, True, 3), (False, False, False, 2),
    ):
        assert p.select_result(walk=walk, redaction=redaction, transition=transition) == expected


def test_new_home_environment_patch_and_best_identity(tmp_path, monkeypatch):
    from gnd.exp import session_environment, tests_runner
    from gnd.exp.session_store import BestAttemptIdentity, SessionStore
    monkeypatch.setattr(session_environment, 'verifier_environment', lambda: {'LANG': 'control'})
    assert tests_runner.tests_environment() == {'LANG': 'control'}
    store = SessionStore(tmp_path / 'store', run_id='store')
    assert store.best_identity() is None
    identity = BestAttemptIdentity(attempt_index=1, attempt_manifest_sha256='a' * 64,
                                   candidate_sha256='b' * 64)
    store._best_identity = identity
    assert store.best_identity() is identity
    assert store.best_record() is None
