"""FU5 (issue 114): the three unused RF6b cycle helpers are retired."""
from __future__ import annotations

import importlib

import pytest
from support.rf9_ci_sources import retired_names

RETIRED = ('_find_cycle', '_dfs_cycle', '_ring_component_violations')


def test_record_lists_exactly_the_three_helpers():
    assert retired_names() == {('gnd.checker', name) for name in RETIRED}


def test_retired_from_imports_fail():
    with pytest.raises(ImportError):
        from gnd.checker import _find_cycle
    with pytest.raises(ImportError):
        from gnd.checker import _dfs_cycle
    with pytest.raises(ImportError):
        from gnd.checker import _ring_component_violations
    with pytest.raises(ImportError):
        from gnd.checker._core import _find_cycle  # noqa: F401
    with pytest.raises(ImportError):
        from gnd.checker._core import _dfs_cycle  # noqa: F401
    with pytest.raises(ImportError):
        from gnd.checker._core import _ring_component_violations  # noqa: F401


@pytest.mark.parametrize('module', ['gnd.checker', 'gnd.checker._core'])
@pytest.mark.parametrize('name', RETIRED)
def test_retired_attribute_lookup_fails(module, name):
    with pytest.raises(AttributeError):
        getattr(importlib.import_module(module), name)


@pytest.mark.parametrize('module', ['gnd.checker', 'gnd.checker._core'])
def test_listed_name_bound_again_fails_the_guard(monkeypatch, module):
    monkeypatch.setattr(importlib.import_module(module), '_find_cycle', lambda pairs: None,
                        raising=False)
    with pytest.raises(AssertionError, match='retired name still bound'):
        retired_names()
