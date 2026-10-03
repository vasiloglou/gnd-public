"""Closed Souffle schema and grounded proof input controls."""
import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

CORPUS = Path(__file__).resolve().parents[1] / "tests/fixtures/v71/phase6"
SCHEMA = json.loads((CORPUS / "wire.schema.json").read_bytes())

def test_closed_schema_rejects_wrong_version_and_extra_field():
    validator = Draft202012Validator(SCHEMA)
    good = json.loads((CORPUS / "dispatch/golden/manifest.json").read_bytes())
    validator.validate(good)
    for mutation in [{"version": True}, {"version": 1.5}, {"unlisted": "value"}]:
        dirty = copy.deepcopy(good)
        dirty.update(mutation)
        assert list(validator.iter_errors(dirty))


def test_native_input_tree_has_grounded_leaves():
    for domain in ["dispatch", "release"]:
        tree = json.loads((CORPUS / domain / "native-proof.json").read_bytes())
        pending = [tree["proof"]]
        leaves = []
        while pending:
            node = pending.pop()
            if "children" in node:
                assert "rule-number" in node
                pending.extend(node["children"])
            else:
                leaves.append(node["axiom"])
        assert len(leaves) == 3
        assert all(v.startswith("i0(") and "subproof" not in v for v in leaves)


