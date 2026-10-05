"""Bind exact original receipt builder code to the shared canonical globals.

Split migrated modules retain the original helper code, defaults and signature.
The shared namespace is required for original monkeypatch controls to exercise
actual builder dependencies; no outputs, helper bodies or limits are replaced.
"""
from types import FunctionType

import test_public_derivation_parity_tools as original


def bind_original_receipt_builder(parity):
    for name in ("_pyrel_extensions", "_souffle_extensions", "_souffle_version"):
        setattr(parity, name, getattr(original, name))
    for name in ("_recorded_disposition", "_build_receipt"):
        source = getattr(original, name)
        rebound = FunctionType(
            source.__code__, vars(parity), source.__name__,
            source.__defaults__, source.__closure__,
        )
        rebound.__kwdefaults__ = source.__kwdefaults__
        rebound.__annotations__ = source.__annotations__
        rebound.__doc__ = source.__doc__
        rebound.__module__ = parity.__name__
        setattr(parity, name, rebound)
