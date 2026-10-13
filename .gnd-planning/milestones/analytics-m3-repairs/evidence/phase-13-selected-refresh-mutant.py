"""Inject an owned scope only around the actual selected-refresh dispatch."""
import inspect
import pytest
from gnd import transition as walk

source = inspect.getsource(walk._evaluate_to_state)
start = source.index('            refreshed = structured_extension_view(')
end = source.index('            extensions = refreshed.facts', start)
block = source[start:end]
mutated = (source[:start] +
           '            with calculation_scope(model, asserted_population):\n' +
           ''.join('    ' + line if line.strip() else line for line in block.splitlines(keepends=True)) +
           source[end:])
exec(compile(mutated, '<selected-refresh-owned-scope-mutant>', 'exec'), walk.__dict__)
raise SystemExit(pytest.main(['tests/test_m3_transition_preparation.py', '-q', '-k',
                             'selected_dynamic_refresh_runs_after_shared_initial_owner_ends']))
