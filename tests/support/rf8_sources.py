"""Exact RF8 physical move and capability substitutions for body observers."""
import ast

_EXPRESSIONS = {
    'contract.profile.patch': 'contract.schema_version in {7, 8}',
    'contract.profile.judgments': 'contract.schema_version == 8',
    'contract.profile.launch_version': '4 if contract.schema_version == 8 else 3',
    'contract.profile.feedback_version': '9 if contract.schema_version == 8 else 8',
    'contract.profile.attempt_version': '10 if contract.schema_version == 8 else 9',
    'contract.profile.result_version': '7 if contract.schema_version == 8 else 6',
}


class PredecessorBody(ast.NodeTransformer):
    def visit_ImportFrom(self, node):
        node.module = {
            'gnd.exp.session_records': 'gnd.exp.session_store',
            'gnd.exp.session_control': 'gnd.exp.session',
        }.get(node.module, node.module)
        return node

    def visit_FunctionDef(self, node):
        # Normalize only the one cache publication at the validated return tail.
        writes = [n for n in ast.walk(node) if isinstance(n, ast.Assign)
                  and ast.unparse(n) == 'store._best_identity = identity']
        if (node.name == 'reconstruct' and len(writes) == 1 and len(node.body) >= 3
                and ast.unparse(node.body[-3]) == 'store._v7_best = best'
                and node.body[-2] is writes[0] and isinstance(node.body[-1], ast.Return)):
            del node.body[-2]
        return self.generic_visit(node)

    def visit_If(self, node):
        # Only the successful missing-contract empty-state cache reset is new.
        test = 'not any(store._attempts_root.iterdir()) and not any(store._launches_root.iterdir())'
        resets = ['store._best_identity = None', 'store._v7_best = None']
        if ast.dump(node.test) == ast.dump(ast.parse(test, mode='eval').body) and [ast.unparse(n) for n in node.body[:2]] == resets:
            node.body = node.body[2:]
        return self.generic_visit(node)

    def visit_Attribute(self, node):
        original = _EXPRESSIONS.get(ast.unparse(node))
        return ast.parse(original, mode='eval').body if original else self.generic_visit(node)


def portable_dump(node):
    """Use the CPython 3.13 default omission of empty list fields on 3.11 too.

    Only serialization changes: a local copy retains all nonempty values. The
    empty-list spelling cannot distinguish any two parsed source bodies.
    """
    import copy

    local = copy.deepcopy(node)
    for child in ast.walk(local):
        child._fields = tuple(field for field in child._fields
                              if not (isinstance(getattr(child, field, None), list)
                                      and getattr(child, field) == []))
    return ast.dump(local, include_attributes=False)


def predecessor_body(node):
    return portable_dump(PredecessorBody().visit(node))


def reader_expected(row):
    if row['function'] != 'reconstruct':
        return row['ast_sha256']
    import json
    from pathlib import Path

    evidence = Path(__file__).resolve().parents[2] / '.gnd-planning/milestones/code-refactoring/evidence'
    successor = json.loads((evidence / 'RF9-repair/reconstruct-successor.json').read_text())
    return successor['ast_sha256']
