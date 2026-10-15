"""PL16: the example plan apps. A bot answers a question with a plan; GND or the PyRel program GND
generates checks it; a refused plan goes back to the bot with the failures; an accepted plan is executed.

The stand-in bots reproduce each example's documented attempts, so these run without a model provider.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
APPS = ROOT / 'src/gnd/examples/plan_apps'
NATIVE = ROOT / 'tutorials/runtimes/.venv/bin/python'
EXAMPLES = {
    'course': ("Plan Maya's spring semester. She really wants Machine Learning.", [1, 1, 0]),
    'access': ('Give Bob access to payroll; Carol approves.', [1, 1, 0]),
    'lease': ('Set up the rent schedule for this lease.', [1, 0]),
    'clinic': ("Refill Sam's prescriptions today.", [1, 1, 0]),
    'trip': ('Plan three days in Lisbon under 900 EUR.', [1, 1, 0]),
}
# the rule each example's first refusal names
FIRST_REFUSAL = {'course': 'prerequisites_first', 'access': 'preconditions[id=pre_approved]', 'lease': 'due_after_start',
                 'clinic': 'refill_not_early', 'trip': 'within_budget'}


def _app(example, *args, env=None):
    return subprocess.run([sys.executable, str(APPS / example / 'app.py'), *args], capture_output=True, text=True,
                          timeout=900, check=False, env={**os.environ, **(env or {})})


@pytest.mark.parametrize('example', sorted(EXAMPLES))
def test_the_model_is_valid(example):
    run = subprocess.run([sys.executable, '-m', 'gnd', 'validate', str(APPS / example / 'model.orm.json')],
                         capture_output=True, text=True, timeout=120, check=False)
    assert run.returncode == 0, run.stdout + run.stderr


@pytest.mark.parametrize('example', sorted(EXAMPLES))
def test_the_documented_attempts_get_the_documented_verdicts_from_gnd(example):
    exits = [_app(example, 'check', str(APPS / example / f'plans/attempt-{n}.steps.json')).returncode
             for n in range(1, len(EXAMPLES[example][1]) + 1)]
    assert exits == EXAMPLES[example][1]


@pytest.mark.parametrize('example', sorted(EXAMPLES))
def test_ask_repairs_from_feedback_and_executes_on_gnd(tmp_path, example):
    question, exits = EXAMPLES[example]
    out = tmp_path / 'next.pop.json'
    run = _app(example, 'ask', question, '--out', str(out))
    assert run.returncode == 0, run.stdout + run.stderr
    assert run.stdout.count('attempt ') == len(exits)
    assert out.exists()
    from gnd import api
    assert api.check(str(APPS / example / 'model.orm.json'), str(out), unredacted=True)['exit_code'] == 0


def test_a_refused_plan_is_not_executed(tmp_path):
    out = tmp_path / 'next.pop.json'
    run = _app('course', 'execute', str(APPS / 'course/plans/attempt-1.steps.json'), '--out', str(out))
    assert run.returncode == 1 and not out.exists()


def test_the_course_feedback_names_the_rule_the_step_and_the_facts(tmp_path):
    run = _app('course', 'ask', EXAMPLES['course'][0], '--attempts', '2')
    assert 'prerequisites_first  violated' in run.stdout and '"$needs": "MATH220"' in run.stdout
    assert '$.steps[3].preconditions[id=pre_offered]  violated' in run.stdout


@pytest.mark.parametrize('answer,reason', [
    ('print("not json")', 'not a plan'),
    ('import sys; sys.exit(3)', 'exited 3'),
    ('print(\'{"steps": []}\')', 'not a plan'),
])
def test_an_unusable_bot_answer_is_a_failed_attempt_not_a_crash(tmp_path, answer, reason):
    bot = tmp_path / 'bot.py'
    bot.write_text(answer + '\n')
    run = _app('course', 'ask', 'anything', '--bot', f'{sys.executable} {bot}', '--attempts', '2')
    assert run.returncode == 1 and reason in run.stdout and 'no plan was accepted in 2 attempts' in run.stdout


def test_a_bot_that_declines_stops_the_loop_with_its_reason(tmp_path):
    bot = tmp_path / 'bot.py'
    bot.write_text('print(\'{"steps": [], "reason": "Carol manages Bob"}\')\n')
    out = tmp_path / 'next.pop.json'
    run = _app('access', 'ask', 'anything', '--bot', f'{sys.executable} {bot}', '--attempts', '3', '--out', str(out))
    assert run.returncode == 1 and 'the bot made no plan: Carol manages Bob' in run.stdout
    assert run.stdout.count('attempt ') == 1 and not out.exists()


def test_a_plan_may_carry_a_note_for_the_user(tmp_path):
    bot = tmp_path / 'bot.py'
    bot.write_text('print(\'{"steps": [{"op": "enroll", "bindings": {"student": "maya", "course": "MATH220", '
                   '"term": "spring"}}], "note": "CS340 must wait"}\')\n')
    run = _app('course', 'ask', 'anything', '--bot', f'{sys.executable} {bot}', '--attempts', '1')
    assert run.returncode == 0 and '  the bot says: CS340 must wait' in run.stdout, run.stdout


def test_a_missing_pyrel_interpreter_is_named_not_a_traceback():
    run = _app('course', 'check', str(APPS / 'course/plans/attempt-1.steps.json'), '--backend', 'pyrel',
               env={'GND_PYREL_PYTHON': '/nonexistent/python'})
    assert run.returncode == 1 and 'the PyRel interpreter /nonexistent/python is not an executable file' in run.stderr
    assert 'Traceback' not in run.stderr


def test_a_checker_crash_stops_the_loop_instead_of_blaming_the_bot(tmp_path):
    broken = tmp_path / 'python'
    broken.write_text('#!/bin/sh\nexit 70\n')
    broken.chmod(0o755)
    run = _app('course', 'ask', EXAMPLES['course'][0], '--backend', 'pyrel', '--attempts', '3',
               env={'GND_PYREL_PYTHON': str(broken)})
    assert run.returncode == 70 and 'the checker could not check the plan; stopping' in run.stdout
    assert 'attempt 2' not in run.stdout


def test_an_empty_plan_without_a_reason_is_not_a_decline(tmp_path):
    bot = tmp_path / 'bot.py'
    bot.write_text('print(\'{"steps": []}\')\n')
    run = _app('access', 'ask', 'anything', '--bot', f'{sys.executable} {bot}', '--attempts', '2')
    assert run.returncode == 1 and 'no plan was accepted in 2 attempts' in run.stdout


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('example', sorted(EXAMPLES))
def test_the_pyrel_backend_agrees_with_gnd_on_every_attempt(example):
    env = {'GND_PYREL_PYTHON': str(NATIVE)}
    for n, want in enumerate(EXAMPLES[example][1], 1):
        plan = str(APPS / example / f'plans/attempt-{n}.steps.json')
        gnd, pyrel = _app(example, 'check', plan), _app(example, 'check', plan, '--backend', 'pyrel', env=env)
        assert gnd.returncode == pyrel.returncode == want, (n, gnd.stdout, pyrel.stdout)
        checks = lambda out: sorted({tuple(line.split('  ')[1:3]) for line in out.splitlines()[1:]})
        assert checks(gnd.stdout) == checks(pyrel.stdout), (n, gnd.stdout, pyrel.stdout)


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('example', sorted(EXAMPLES))
def test_ask_on_pyrel_executes_the_same_state_as_on_gnd(tmp_path, example):
    question, _ = EXAMPLES[example]
    a, b = tmp_path / 'gnd.pop.json', tmp_path / 'pyrel.pop.json'
    assert _app(example, 'ask', question, '--out', str(a)).returncode == 0
    run = _app(example, 'ask', question, '--backend', 'pyrel', '--out', str(b), env={'GND_PYREL_PYTHON': str(NATIVE)})
    assert run.returncode == 0, run.stdout + run.stderr
    canon = lambda path: {k: sorted(json.dumps(r, sort_keys=True) for r in v)
                          for k, v in json.loads(path.read_text())['facts'].items()}
    assert canon(a) == canon(b)


@pytest.mark.parametrize('example', sorted(EXAMPLES))
def test_rules_prints_each_rule_as_a_pyrel_requirement(example):
    run = _app(example, 'rules')
    assert run.returncode == 0, run.stderr
    assert '.require(' in run.stdout and 'Rules checked on every state' in run.stdout


def test_rules_lists_every_rule_of_the_course_including_the_rule_across_a_step():
    out = _app('course', 'rules').stdout
    for name in ('term_load', 'one_grade', 'prerequisites_first', 'no_retake', 'credit_cap', 'pre_offered', 'grade_final'):
        assert f'  {name}: ' in out, name
    assert 'Once a grade is recorded, it never changes.' in out
    assert '.require(new_grade == old_grade)' in out


def test_a_broken_rule_across_a_step_is_shown_in_pyrel(tmp_path):
    bot = tmp_path / 'bot.py'
    bot.write_text('print(\'{"steps": [{"op": "change_grade", "bindings": '
                   '{"student": "omar", "course": "MATH120", "grade": "A"}}]}\')\n')
    run = _app('course', 'ask', 'anything', '--bot', f'{sys.executable} {bot}', '--attempts', '1')
    assert '$.steps[1].dynamic_rules[0]  violated' in run.stdout, run.stdout
    assert 'the rule in PyRel: m.where(do_change_grade(' in run.stdout, run.stdout


@pytest.mark.parametrize('example', sorted(EXAMPLES))
def test_the_first_refusal_names_the_rule_and_shows_it_in_pyrel(example):
    run = _app(example, 'ask', EXAMPLES[example][0], '--attempts', '1')
    assert FIRST_REFUSAL[example] in run.stdout, run.stdout
    assert 'the rule in PyRel: m.where(' in run.stdout, run.stdout


def test_repeated_failures_are_shown_once_with_their_states():
    sys.path.insert(0, str(APPS))
    from core import grouped
    failures = [{'where': f'state {k}', 'check': 'r', 'status': 'violated', 'witness': [1], 'message': None} for k in (1, 2, 3, 5)]
    failures.insert(2, {'where': 'step 2', 'check': 'p', 'status': 'violated', 'witness': None, 'message': 'm'})
    assert [where for where, _ in grouped(failures)] == ['states 1-3, 5', 'step 2']


def test_attempts_are_bounded():
    run = _app('course', 'ask', 'anything', '--attempts', '6')
    assert run.returncode == 2 and '--attempts must be 1 to 5' in run.stderr


def test_the_pyrel_rule_shown_is_the_one_that_failed():
    lines = _app('course', 'ask', EXAMPLES['course'][0], '--attempts', '1').stdout.splitlines()
    failure = next(i for i, line in enumerate(lines) if 'prerequisites_first  violated' in line)
    assert '.require(passed(step, student, needs))' in lines[failure + 1]


# ---------------------------------------------------------------- review findings (PL16 review F1-F11, C1)

def _core():
    import importlib.util
    spec = importlib.util.spec_from_file_location('plan_apps_core_t', APPS / 'core.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _plan(tmp_path, example, steps):
    core = _core()
    app = core.Example(APPS / example)
    path = tmp_path / 'plan.steps.json'
    path.write_text(json.dumps(core.steps_document(app, steps)))
    return core, app, path


@pytest.mark.parametrize('steps,needle', [
    ([{'op': 'teleport', 'bindings': {'student': 'maya'}}], 'teleport'),
    ([{'op': 'enroll', 'bindings': {'student': 'maya', 'course': 'CS340'}}], 'term'),
    ([{'op': 'enroll', 'bindings': {'student': 'maya', 'course': 101, 'term': 'spring'}}], 'course'),
])
def test_f1_a_plan_gnd_refuses_as_malformed_carries_the_reason(tmp_path, steps, needle):
    core, app, path = _plan(tmp_path, 'course', steps)
    result = core.check(app, app.state, path, 'gnd', None)
    assert result['exit'] == 3 and result['failures'], result
    assert any(needle in (f['message'] or '') for f in result['failures']), result['failures']


def test_f2_the_pyrel_output_parser_keeps_values_with_two_spaces():
    core = _core()
    out = ('step 1  enroll(student=\'maya  lee\', course=\'PHIL  101\', term=\'spring\')\n'
           'step 1  $.steps[1].preconditions[id=pre_offered]  violated  {"course": "PHIL  101", "student": "maya  lee"}\n'
           'state 1  every rule holds\n')
    assert core.parse_pyrel_output(out) == [{
        'where': 'step 1', 'check': '$.steps[1].preconditions[id=pre_offered]', 'status': 'violated',
        'witness': {'course': 'PHIL  101', 'student': 'maya  lee'}, 'message': None}]


def test_f2_an_unparseable_pyrel_line_is_kept_as_a_message_not_a_crash():
    core = _core()
    assert core.parse_pyrel_output('state 1  x  violated  {"broken\n') == [
        {'where': 'state 1', 'check': 'x', 'status': 'violated', 'witness': None, 'message': '{"broken'}]


@pytest.mark.pyrel_oracle
def test_f2_a_value_with_two_spaces_agrees_with_gnd(tmp_path):
    core, app, path = _plan(tmp_path, 'course', [{'op': 'enroll', 'bindings': {
        'student': 'maya', 'course': 'PHIL  101', 'term': 'spring'}}])
    gnd = core.check(app, app.state, path, 'gnd', None)
    pyrel = core.check(app, app.state, path, 'pyrel', str(NATIVE))
    assert gnd['exit'] == pyrel['exit'] == 1
    assert {(f['check'], f['status']) for f in gnd['failures']} == {(f['check'], f['status']) for f in pyrel['failures']}


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('where', ['exists', 'missing-dir'])
def test_f4_emit_post_to_an_unusable_path_is_not_read_as_a_violation(tmp_path, where):
    from gnd.export.pyrel_rules import render
    program = tmp_path / 'rules.py'
    program.write_text(render(APPS / 'lease/model.orm.json', 'duckdb'))
    core, app, plan = _plan(tmp_path, 'lease', json.loads((APPS / 'lease/plans/attempt-2.steps.json').read_text())['steps'])
    target = tmp_path / 'exists.json' if where == 'exists' else tmp_path / 'nodir/x.json'
    if where == 'exists':
        target.write_text('{}')
    run = subprocess.run([str(NATIVE), '-I', str(program), '--pre', str(app.state), '--steps', str(plan),
                          '--emit-post', str(target)], capture_output=True, text=True, timeout=600, check=False)
    assert run.returncode == 74 and 'cannot write the post-state' in run.stderr, (run.returncode, run.stderr)
    if where == 'exists':
        assert target.read_text() == '{}'


@pytest.mark.pyrel_oracle
def test_f4_emit_post_writes_the_after_state(tmp_path):
    from gnd.export.pyrel_rules import render
    program = tmp_path / 'rules.py'
    program.write_text(render(APPS / 'lease/model.orm.json', 'duckdb'))
    core, app, plan = _plan(tmp_path, 'lease', json.loads((APPS / 'lease/plans/attempt-2.steps.json').read_text())['steps'])
    run = subprocess.run([str(NATIVE), '-I', str(program), '--pre', str(app.state), '--steps', str(plan),
                          '--emit-post', str(tmp_path / 'post.json')], capture_output=True, text=True, timeout=600,
                         check=False)
    assert run.returncode == 0, run.stdout + run.stderr
    gnd = core.check(app, app.state, plan, 'gnd', None)['post']
    assert json.loads((tmp_path / 'post.json').read_text())['facts'] == gnd['facts']


@pytest.mark.parametrize('out', ['exists', 'missing-dir'])
def test_f5_an_unusable_out_path_is_refused_before_the_bot_is_asked(tmp_path, out):
    marker = tmp_path / 'asked'
    bot = tmp_path / 'bot.py'
    bot.write_text(f'open({str(marker)!r}, "w").close()\nprint("{{}}")\n')
    target = tmp_path / 'exists.json' if out == 'exists' else tmp_path / 'nodir/x.json'
    if out == 'exists':
        target.write_text('{}')
    run = _app('course', 'ask', 'q', '--bot', f'{sys.executable} {bot}', '--out', str(target))
    assert run.returncode == 2 and not marker.exists(), run.stdout + run.stderr
    assert 'Traceback' not in run.stderr


@pytest.mark.parametrize('args,needle', [
    (['check'], 'needs a plan'),
    (['ask'], 'needs a question'),
])
def test_f6_a_missing_argument_is_a_usage_error(args, needle):
    run = _app('course', *args)
    assert run.returncode == 2 and needle in run.stderr and 'Traceback' not in run.stderr


def test_f6_a_plan_file_that_is_not_a_plan_is_a_usage_error(tmp_path):
    plan = tmp_path / 'p.json'
    plan.write_text('{"steps": 5}')
    run = _app('course', 'check', str(plan))
    assert run.returncode == 2 and 'not a plan' in run.stderr and 'Traceback' not in run.stderr


def test_f11_a_checker_that_does_not_finish_stops_the_loop(tmp_path, monkeypatch):
    core = _core()
    slow = tmp_path / 'python'
    slow.write_text('#!/bin/sh\nsleep 5\n')
    slow.chmod(0o755)
    monkeypatch.setattr(core, 'PYREL_SECONDS', 1)
    _, app, path = _plan(tmp_path, 'course', [{'op': 'enroll', 'bindings': {
        'student': 'maya', 'course': 'MATH220', 'term': 'spring'}}])
    result = core.check(app, app.state, path, 'pyrel', str(slow))
    assert result['exit'] == 70 and 'did not finish' in result['failures'][0]['message']
    assert str(tmp_path) not in json.dumps(result['failures'])


def test_f11_a_plan_longer_than_the_bound_is_a_failed_attempt():
    core = _core()
    steps = [{'op': 'admit', 'bindings': {'student': f's{i}'}} for i in range(core.MAX_STEPS + 1)]
    plan, reason = core.parse_answer(json.dumps({'steps': steps}))
    assert plan is None and f'at most {core.MAX_STEPS} steps' in reason


def test_f10_the_rules_view_says_which_program_it_shows():
    out = _app('course', 'rules').stdout
    assert 'the DuckDB program checks the same rules as violation queries' in out


def test_c1_the_rules_text_agrees_with_the_access_state():
    state = json.loads((APPS / 'access/state.pop.json').read_text())
    approvers = {f['approver'] for f in state['facts']['approved_by'] if f['employee'] == 'frank'}
    rules = (APPS / 'access/rules.md').read_text()
    assert approvers == {'dana'} and 'approved by Dana' in rules
