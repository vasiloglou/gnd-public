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

    def visit_Assign(self, node):
        if ast.unparse(node) == 'store._best_identity = identity':
            return None  # New private cache: separately checked against ResumeState.
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


def predecessor_body(node):
    return ast.dump(PredecessorBody().visit(node), include_attributes=False)
