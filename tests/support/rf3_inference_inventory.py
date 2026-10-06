"""RF3 successor to the frozen inference import inventory; no answers edited."""
from __future__ import annotations

import ast

FORBIDDEN = {
    'check', 'check_partial', 'check_with_anchors_partial',
    '_python_extension_calculator', '_exact_extension_calculator',
    '_evaluate_stratified_extensions', 'structured_extension_view',
    'structured_extension_facts', '_compare', '_typed_comparison_values',
    'compare_terms', 'evaluate_term', 'guarded_operand_evaluator',
    'materialize_scalar', 'produce_witness', '_joined_bindings',
    '_partial_bindings', '_clause_bindings',
}
FORBIDDEN |= {name.removeprefix('_') for name in FORBIDDEN}


def inference_imports(inventory, extra=None):
    predecessor = inventory.inference_imports(extra)
    closure = set(predecessor['closure'])
    details = list(predecessor['details'])
    # The original graph already reads every actual module, including new homes.
    # Its details filter predates extensions, so widen that one filter here.
    for source, path in inventory.modules().items():
        text = path.read_text()
        if extra and source in extra:
            text += '\n' + extra[source]
        for node in ast.walk(ast.parse(text)):
            if (source in closure and isinstance(node, ast.ImportFrom)
                    and node.module == 'gnd.extensions'):
                details.append({'source': source, 'line': node.lineno,
                                'module': node.module, 'names': [a.name for a in node.names]})
    return {
        'predecessor': predecessor,
        'closure': predecessor['closure'],
        'details': details,
        'potential_inference_imports': [
            row for row in details if set(row['names']) & FORBIDDEN
            or row['module'] == 'gnd.witness.producer'
        ],
    }
