"""pytest plugin (TP2): every iter_fact_types_shared row refuses writes for the whole session.

Used by tests/test_tp2_shared_fact_types.py::test_review_f1_frozen_rows_on_anchored_and_partial_paths
to cover readers the TP2 workloads never reach."""
from gnd.model_index import ModelIndex

hits = {"rows": 0}


def _refuse(*_a, **_k):
    raise TypeError("a shared fact-type row was written")


class FrozenDict(dict):
    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = update = __ior__ = _refuse


class FrozenList(list):
    __setitem__ = __delitem__ = __iadd__ = __imul__ = _refuse
    append = clear = extend = insert = pop = remove = reverse = sort = _refuse


def freeze(value):
    if isinstance(value, dict):
        return FrozenDict({k: freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return FrozenList(freeze(v) for v in value)
    return value


_original = ModelIndex.iter_fact_types_shared


def _frozen(self):
    for row in _original(self):
        hits["rows"] += 1
        yield freeze(row)


ModelIndex.iter_fact_types_shared = _frozen


def pytest_terminal_summary(terminalreporter):
    terminalreporter.write_line(f"tp2-freeze-all: {hits['rows']} shared rows served frozen")
