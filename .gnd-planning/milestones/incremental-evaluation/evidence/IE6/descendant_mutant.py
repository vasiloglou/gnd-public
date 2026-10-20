import inspect
import textwrap

import pytest

from gnd import incremental_state as state

code=textwrap.dedent(inspect.getsource(state.ReuseState.reuse))
code=code.replace('previous = self._candidate.get(key, self._prior.get(key))','for child in policy_key:\n            _measure(child, self._max_bytes)\n        previous = self._candidate.get(key, self._prior.get(key))')
namespace=dict(vars(state))
exec(compile(code,'<descendant-work-mutant>','exec'),namespace)  # noqa: S102 -- explicit test-only mutant
state.ReuseState.reuse=namespace['reuse']
raise SystemExit(pytest.main(['-q','tests/test_incremental_performance.py::test_prepared_policy_tree_is_measured_once_for_many_misses','tests/test_incremental_performance.py::test_raw_policy_warm_hits_do_not_repeat_admission_tree_walk']))
