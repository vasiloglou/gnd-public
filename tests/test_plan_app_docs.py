"""PL18: the plan-app pages tell the truth about the recordings they show, and read plainly."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
APPS = ROOT / 'src/gnd/examples/plan_apps'
SKILLS = APPS / 'skill-sessions'
TUTORIALS = sorted((ROOT / 'docs/tutorials').glob('*.md'))
PAGES = [*TUTORIALS, *sorted((ROOT / 'docs/how-to').glob('*.md')), ROOT / 'docs/explanation/rules-as-pyrel.md']
BANNED = ['covers_fact_types', 'nonowned', 'bounded profile', 'operational failure', 'exit 70', 'receipt',
          'binding digest', 'admission', 'certified', 'enterprise-ready', 'production']

spec = importlib.util.spec_from_file_location('record_plan_apps_d', ROOT / 'tools/record_plan_apps.py')
recorder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recorder)
RUNS = json.loads((APPS / 'recordings/results.json').read_text(encoding='utf-8'))['runs']


def prose(path):
    text = re.sub(r'```.*?```', '', path.read_text(encoding='utf-8'), flags=re.DOTALL)
    text = re.sub(r'<!--.*?-->|<figure.*?</figure>', '', text, flags=re.DOTALL)
    paragraphs = []
    for block in re.split(r'\n\s*\n|\n(?=\s*(?:- |\d+\. ))', text):   # each list item reads as its own paragraph
        lines = [line.strip() for line in block.splitlines()
                 if line.strip() and not line.strip().startswith(('|', '#', '!', '???', '--8<--'))]
        if lines:
            paragraphs.append(' '.join(lines))
    return paragraphs


@pytest.mark.parametrize('page', PAGES, ids=lambda p: p.name)
def test_plain_short_prose_without_exit_codes(page):
    for paragraph in prose(page):
        assert len(paragraph.split()) <= 90, paragraph[:80]
        lowered = paragraph.lower()
        assert not re.search(r'\bexit (code )?\d', lowered), paragraph[:80]
        for term in BANNED:
            assert term not in lowered, term


@pytest.mark.parametrize('page', TUTORIALS, ids=lambda p: p.name)
def test_tutorials_have_no_python_fences(page):
    assert '```python' not in page.read_text(encoding='utf-8')


# The A1 rule: a page replays the first run, in results.json order, refused on a rule and then accepted, and
# names it; when there is none, the page says so and labels the stand-in's repair as scripted.
REPLAYED = {
    'course-planner.md': ('course', 'llama-3.2-3b/course/run-2'),
    'access-requests.md': ('access', 'llama-3.1-8b/access/run-1'),
    'trip-budget.md': ('trip', 'llama-3.1-8b/trip/run-2'),
    'clinic-refills.md': ('clinic', 'No recorded clinic run was refused on a rule and then accepted'),
    'lease-schedule.md': ('lease', 'No recorded lease run was refused on a date rule and then accepted'),
}


@pytest.mark.parametrize('name', sorted(REPLAYED))
def test_each_page_follows_the_replay_rule(name):
    example, claim = REPLAYED[name]
    page = next(p for p in PAGES if p.name == name).read_text(encoding='utf-8')
    chosen = recorder.replay_choice(RUNS, example)
    if chosen is None:
        assert claim and claim in page and 'scripted' in page
        return
    folder = f"{chosen['model']}/{example}/run-{chosen['run']}"
    replay = f"replays/{example}-{chosen['model']}-run-{chosen['run']}.svg"
    assert replay in page, (name, replay)
    assert claim == folder and f'`{folder}`' in page, (name, folder)


def test_the_skill_sessions_are_bound_and_kept_clean():
    manifest = json.loads((SKILLS / 'manifest.json').read_text(encoding='utf-8'))
    on_disk = {str(p.relative_to(SKILLS)) for p in SKILLS.rglob('*') if p.is_file()} - {'manifest.json', 'README.md'}
    assert set(manifest['files']) == on_disk
    for name, digest in manifest['files'].items():
        data = (SKILLS / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == digest, name
        text = data.decode('utf-8')
        for needle in ('/Users/', '/private/', '/home/', '/var/folders/', 'sk-ant-', 'sk-or-'):
            assert needle not in text, (name, needle)
    results = json.loads((SKILLS / 'results.json').read_text(encoding='utf-8'))
    assert results['gate'] == '.gnd-planning/milestones/pyrel-agent-loop/019-recording-gate-PL18-skills.md'
    assert [(r['model'], r['run']) for r in results['runs']] == [
        ('claude-haiku', 1), ('claude-haiku', 2), ('claude-default', 1), ('claude-default', 2)]
    assert all(r['validate_exit'] == 0 for r in results['runs'])


def test_the_course_page_names_the_first_skill_run_that_validated():
    results = json.loads((SKILLS / 'results.json').read_text(encoding='utf-8'))
    first = next(r for r in results['runs'] if r['validate_exit'] == 0)
    page = (ROOT / 'docs/tutorials/course-planner.md').read_text(encoding='utf-8')
    assert f"skill-sessions/{first['model']}/run-{first['run']}/" in page


def _core():
    spec = importlib.util.spec_from_file_location('plan_apps_core_docs', APPS / 'core.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('name,example', [('access-requests.md', 'access'), ('trip-budget.md', 'trip'),
                                          ('lease-schedule.md', 'lease')])
def test_quoted_rules_are_the_generated_ones_and_the_written_ones(name, example):
    """PL-R3: an excerpt typed on a page must be the generated PyRel line or the text of rules.md."""
    core = _core()
    page = (ROOT / 'docs/how-to' / name).read_text(encoding='utf-8')
    generated = {line for rule in core.pyrel_rules(core.Example(APPS / example)) for line in rule['code']}
    written = (APPS / example / 'rules.md').read_text(encoding='utf-8')
    for block in re.findall(r'```text\n(.*?)```', page, re.DOTALL):
        for line in block.splitlines():
            if line.startswith('m.where('):
                assert line in generated, line
            elif line.startswith('- '):
                assert ' '.join(line[2:].split()) in ' '.join(written.split()), line


def test_the_clinic_runs_table_is_the_recorded_one():
    names = {'claude-haiku': 'Claude Haiku', 'claude-default': 'Claude Code default', 'llama-3.1-8b': 'Llama 3.1 8B',
             'gemma-3-4b': 'Gemma 3 4B', 'llama-3.2-3b': 'Llama 3.2 3B'}
    page = (ROOT / 'docs/tutorials/clinic-refills.md').read_text(encoding='utf-8')
    for model, label in names.items():
        rows = [r for r in RUNS if r['model'] == model and r['example'] == 'clinic']
        counts = [sum(recorder.outcome(r) == k for r in rows)
                  for k in ('first', 'refused', 'declined', 'repaired-format')]
        assert f"| {label} | {' | '.join(map(str, counts))} |" in page, (model, counts)
        assert not any(recorder.outcome(r) == 'repaired-rule' for r in rows)


def test_the_course_page_quotes_haikus_session_as_recorded():
    """The step 2 explanation: the errors and the edits it quotes are the recorded ones."""
    session = (SKILLS / 'claude-haiku/run-1/turn-01.jsonl').read_text(encoding='utf-8')
    events = [json.loads(line) for line in session.splitlines()]
    results = ' '.join(str(p.get('content')) for e in events if e['type'] == 'user'
                       and isinstance(e['message'].get('content'), list) for p in e['message']['content'])
    edits = [p['input'] for e in events if e['type'] == 'assistant' for p in e['message']['content']
             if p.get('type') == 'tool_use' and p['name'] == 'Edit' and p['input']['file_path'].endswith('.yaml')]
    denials = next(e for e in events if e['type'] == 'result')['permission_denials']
    page = (ROOT / 'docs/tutorials/course-planner.md').read_text(encoding='utf-8')
    for line in re.findall(r'^ERROR at .*$', page, re.M):
        assert line in results, line
    for edit in edits:
        before = re.search(r'"(.*)"', edit['old_string']).group(1)
        after = re.search(r'"(.*)"', edit['new_string']).group(1)
        assert f'`{before}` | `{after}`' in page, (before, after)
    assert len(denials) == 4 and 'Four times Haiku chained' in page
