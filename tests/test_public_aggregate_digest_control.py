import hashlib

import pytest


def _assert_sum_digest(value: int, digest: str) -> None:
    assert hashlib.sha256(str(value).encode()).hexdigest() == digest


def test_q02_wrong_digest_negative_control_really_reds() -> None:
    with pytest.raises(AssertionError):
        _assert_sum_digest(6175, "0" * 64)
