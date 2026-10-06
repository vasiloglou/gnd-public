"""RF2 predecessor acceptance table for two equivalent digest checks."""
import pytest

from gnd.artifacts import is_sha256_hex
from gnd.assurance import AssuranceBlockV1
from gnd.exp.session_patch import PatchRefusal, _shape


@pytest.mark.parametrize("value,accepted", [("0" * 64, True), ("abcdef" * 10 + "abcd", True),
    (None, True), ("A" * 64, False), ("g" * 64, False), ("0" * 63, False),
    ("0" * 65, False), ("0" * 64 + "\n", False), ("０" * 64, False),
    ("sha256:" + "0" * 64, False), (0, False), (True, False)])
def test_existing_digest_checks_agree(value, accepted):
    assert is_sha256_hex(value) == (accepted and value is not None)
    proposal = {"schema_version": 1, "base_candidate_sha256": value, "operations": []}
    if accepted:
        AssuranceBlockV1(None, scope_digest=value)
        _shape(proposal)
    else:
        with pytest.raises(ValueError, match="invalid assurance identity"):
            AssuranceBlockV1(None, scope_digest=value)
        with pytest.raises(PatchRefusal, match="invalid base digest"):
            _shape(proposal)


@pytest.mark.parametrize("value", [b"0" * 64, [], {}, object()])
def test_predicate_is_total_for_non_strings(value):
    assert is_sha256_hex(value) is False
