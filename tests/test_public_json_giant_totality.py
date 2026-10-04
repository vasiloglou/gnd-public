import pytest
from support import public_json_giant_observer as CHARACTERIZE

PUBLIC_GIANTS = ["patch-value", "fact-digest", "receipt-init", "receipt-digest"]

@pytest.mark.parametrize("consumer", PUBLIC_GIANTS)
def test_existing_giant_integer_totality(consumer, tmp_path, monkeypatch):
    actual = CHARACTERIZE.observe(
        {"consumer": consumer, "variant": "giant-int"}, tmp_path, monkeypatch
    )
    expected_type = "PatchRefusal" if consumer == "patch-value" else "JudgmentInputError"
    assert actual["kind"] == "refused"
    assert actual["type"] == expected_type
    assert actual["reason"] == "shape"
