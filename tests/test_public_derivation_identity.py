"""Exact scalar identity byte goldens at the production checker boundary."""
from gnd.checker import _identity_token


def test_scalar_identity_goldens_and_tuple_order_are_discriminating():
    values = [
        ("λ", b'["string","\xce\xbb"]'),
        (1, b'["number",[1,1]]'),
        (1.0, b'["number",[1,1]]'),
        (-0.0, b'["number",[0,1]]'),
        (True, b'["boolean",true]'),
    ]
    assert [(_identity_token(value), expected) for value, expected in values] == [
        (expected, expected) for _value, expected in values
    ]
    assert _identity_token(True) != _identity_token(1)
    assert _identity_token(1) == _identity_token(1.0)
    left = (_identity_token("a"), _identity_token("b"))
    assert left != tuple(reversed(left))
