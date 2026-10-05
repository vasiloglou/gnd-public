from __future__ import annotations

from pathlib import Path

import pytest

from gnd.exp.session_contract import SessionContractError, read_session_contract


def test_c16_contract_reader_retains_the_one_mebibyte_cap(tmp_path: Path) -> None:
    path = tmp_path / 'session.contract.json'
    path.write_bytes(b' ' * (1024 * 1024 + 1))
    with pytest.raises(SessionContractError):
        read_session_contract(path, experiment_root=tmp_path, experiment_id='EXP-061-walk-floor')
