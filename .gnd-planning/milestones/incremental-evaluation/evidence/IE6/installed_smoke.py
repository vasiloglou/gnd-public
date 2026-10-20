import json
from importlib.resources import files

from gnd import api
from gnd.examples.plan_apps.core import Example, steps_document
from gnd.model import load_model
from gnd.population import load_population

root = files("gnd") / "examples" / "plan_apps" / "course"
model = load_model(root / "model.orm.json")
pre = load_population(root / "state.pop.json", model=model)
plan = json.loads((root / "plans" / "attempt-3.steps.json").read_text())
steps = steps_document(Example(root), plan["steps"])
session = api.EvaluationSession(model)
first, first_feedback = session.check_with_feedback(pre, attempt=1)
first_walk = session.transition(pre, steps)
observed = session.observe(pre, {"passed": [*pre.facts["passed"],
                            {"student": "maya", "course": "STAT210"}]})
second, second_feedback = session.check_with_feedback(observed, attempt=2)
second_walk = session.transition(observed, steps)
session.close()

print({"checks": [first["exit_code"], second["exit_code"]], "walks": [first_walk["exit_code"], second_walk["exit_code"]], "attempts": [first_feedback["attempt"], second_feedback["attempt"]]})

import hashlib
import sys
from pathlib import Path

from gnd import evaluation_feedback, extensions, incremental_state
from gnd.artifacts import canonical_json_bytes

prefix = Path(sys.prefix).resolve()
for module in (api, evaluation_feedback, extensions, incremental_state):
    assert Path(module.__file__).resolve().is_relative_to(prefix), module.__file__
assert 'EvaluationSession' in api.__all__
owner = api.EvaluationSession(model)
assert canonical_json_bytes(owner.check(pre)) == canonical_json_bytes(api.check(model, pre))
assert canonical_json_bytes(owner.check(pre)) == canonical_json_bytes(api.check(model, pre))
assert owner.stats()['hits'] > 0
payload, receipt = owner.check_with_receipt(pre)
assert receipt.reusable and receipt.report.verdicts
before = owner.transition(pre, steps, pre_receipt=receipt)
receipt.report.verdicts[0].message = 'public mutation'
assert canonical_json_bytes(owner.transition(pre, steps, pre_receipt=receipt)) == canonical_json_bytes(before)
wire = canonical_json_bytes(first_feedback)
assert evaluation_feedback.SessionFeedback.model_validate_json(wire).attempt == 1
try:
    evaluation_feedback.SessionFeedback.model_validate_json(wire.replace(b'"schema_version":1', b'"schema_version":2,"schema_version":1'))
except ValueError:
    pass
else:
    raise AssertionError('duplicate version accepted')
owner.close()
wheel = Path('/private/tmp/gnd-ie6-dist/get_nick_done-0.1.0-py3-none-any.whl')
print(json.dumps({'wheel_sha256': hashlib.sha256(wheel.read_bytes()).hexdigest(),
                  'interpreter': sys.executable,
                  'modules': {module.__name__: module.__file__ for module in (api, evaluation_feedback, extensions, incremental_state)},
                  'public_surface': 'session check/receipt/transition/observe/feedback/close; strict wire; receipt detachment',
                  'boundary': 'fresh offline wheel environment; bounded public/doc smoke, no full/native/certification'}, sort_keys=True))
