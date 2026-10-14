"""PA5R D7: readability and claim gate for the PyRel learning path."""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FULL = ['docs/pyrel-apps.md', 'docs/bookrec/07-native.md', 'docs/expense/04-native.md']
CHAPTERS = FULL[1:]
SNOWFLAKE_ONLY = ['README.md', 'docs/index.md', 'docs/tour.md', 'docs/agents/export-and-review.md',
                  'docs/agents/index.md']
BANNED = ['covers_fact_types', 'nonowned', 'bounded profile', 'operational failure', 'exit 70', 'receipt',
          'binding digest', 'admission', 'certified', 'enterprise-ready', 'production']
RUNTIME = 'PyRel 1.30.1 with DuckDB 1.5.5'
MEANING = 'a passing check means the supplied facts satisfy the modeled rules'
BOUNDARY = ('outside this tutorial', 'outside the applications runtime', 'not yet supported by gnd export')


def prose(path):
    """Paragraphs of reader prose: no code, comments, markup, headings or tables."""
    text = (ROOT / path).read_text()
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    paragraphs = []
    for block in re.split(r'\n\s*\n', text):
        lines = [re.sub(r'<[^>]+>', '', line).strip() for line in block.splitlines()
                 if not line.strip().startswith(('|', '#', '!', '???', '--8<--'))]
        lines = [line for line in lines if line]
        if lines:
            paragraphs.append(' '.join(lines))
    return paragraphs


def tables(path):
    return [line for line in (ROOT / path).read_text().splitlines() if line.startswith('|')]


def sentences(paragraph):
    return re.split(r'(?<=[.!?])\s+', paragraph)


@pytest.mark.parametrize('path', FULL)
def test_plain_words_only(path):
    text = ' '.join(prose(path)).lower()
    for term in BANNED:
        assert term not in text, term
    assert not re.search(r'\bscal', text)
    for paragraph in prose(path):
        for sentence in sentences(paragraph):
            if 'governed' in sentence.lower():
                assert 'if your team' in sentence.lower(), sentence
            assert not re.search(r'\bexit (code )?\d', sentence.lower()), sentence


@pytest.mark.parametrize('path', FULL)
def test_short_paragraphs(path):
    for paragraph in prose(path):
        assert len(paragraph.split()) <= 90, paragraph[:80]


@pytest.mark.parametrize('path', CHAPTERS)
def test_witness_is_explained_on_first_use(path):
    text = ' '.join(prose(path))
    first = re.search(r'witness', text, flags=re.IGNORECASE)
    assert first and re.match(r'witness(es)? \(', text[first.start():], flags=re.IGNORECASE)


@pytest.mark.parametrize('path', CHAPTERS)
def test_exit_codes_only_in_troubleshooting_table(path):
    text = (ROOT / path).read_text()
    section = text[text.index('## Troubleshooting'):text.index('## Next steps')]
    coded = [row for row in tables(path) if 'exit code' in row]
    assert coded and all(row in section for row in coded)
    for row in coded:   # every coded row carries a plain cause and a plain fix
        cells = [cell.strip() for cell in row.strip('|').split('|')]
        assert len(cells) == 3 and all(len(cell.split()) >= 3 for cell in cells[1:]), row


@pytest.mark.parametrize('path', FULL)
def test_next_steps_link_own_rules_and_agent_sessions(path):
    text = (ROOT / path).read_text()
    steps = text[text.index('## Next steps'):]
    assert 'model-from-text.md' in steps and 'dev-session.md' in steps
    assert 'separate session contract' in ' '.join(steps.split())


@pytest.mark.parametrize('path', FULL)
def test_required_claims_present(path):
    text = ' '.join(prose(path))
    assert RUNTIME in text
    assert MEANING in text.lower()


@pytest.mark.parametrize('path', CHAPTERS)
def test_distinctions_survive_plain_wording(path):
    text = ' '.join(prose(path)).lower()
    for phrase in ('warning', 'unknown', 'is not the same as a passing check'):
        assert phrase in text, phrase


@pytest.mark.parametrize('path', FULL + SNOWFLAKE_ONLY)
def test_snowflake_is_context_or_boundary(path):
    for paragraph in prose(path) + tables(path):
        if 'snowflake' not in paragraph.lower():
            continue
        assert any(phrase in paragraph.lower() for phrase in BOUNDARY), paragraph[:120]
        for sentence in sentences(paragraph):
            low = sentence.lower()
            if 'snowflake' in low and ('runs on' in low or 'deploy' in low):
                assert 'pyrel itself' in low, sentence


EXCERPT_SOURCES = {
    'bookrec': {'native_query.py': 'src/gnd/examples/bookrec/extension/bookrec/native_query.py',
                'rules_in_pyrel.py': 'src/gnd/examples/bookrec/rules_in_pyrel.py'},
    'expense': {'native_query.py': 'src/gnd/examples/expense/native_query.py',
                'rules_in_pyrel.py': 'src/gnd/examples/expense/rules_in_pyrel.py'},
}


@pytest.mark.parametrize('domain,path', [('bookrec', 'docs/bookrec/07-native.md'), ('expense', 'docs/expense/04-native.md')])
def test_step_three_excerpts_come_from_shipped_files(domain, path):
    """Every marked excerpt in step 3 is verbatim lines of the shipped file it names."""
    text = (ROOT / path).read_text()
    section = text[text.index('## 3.'):text.index('## 4.')]
    marked = re.findall(r'<!-- gnd-excerpt source=([A-Za-z_./-]+) -->\s*\n```python\n(.*?)\n```', section, flags=re.DOTALL)
    assert {name for name, _ in marked} == set(EXCERPT_SOURCES[domain]), 'step 3 shows the query and the hand-written rules'
    for name, excerpt in marked:
        shipped = [line.strip() for line in (ROOT / EXCERPT_SOURCES[domain][name]).read_text().splitlines()]
        lines = [line.strip() for line in excerpt.splitlines() if line.strip() and line.strip() != '...']
        assert len(lines) >= 3, name
        position = 0
        for line in lines:
            assert line in shipped[position:], (name, line)
            position = shipped.index(line, position) + 1
    unmarked = re.findall(r'(?<!-->\n)```python\n(.*?)\n```', section, flags=re.DOTALL)
    # Illustrative python fences in step 3 are either marked excerpts or runnable blocks.
    for block in unmarked:
        assert block in {e for _, e in marked} or 'print(' in block, block[:80]


@pytest.mark.parametrize('domain', ['bookrec', 'expense'])
@pytest.mark.parametrize('artifact', ['task', 'transcript', 'candidate', 'feedback'])
@pytest.mark.parametrize('optimized', [False, True])
def test_recorded_excerpt_refuses_changed_bytes(tmp_path, domain, artifact, optimized):
    """Each excerpt must refuse a changed artifact before printing its contents."""
    import shutil
    import subprocess
    import sys

    page = ROOT / ('docs/bookrec/07-native.md' if domain == 'bookrec' else 'docs/expense/04-native.md')
    chapter = page.read_text().split('### 5a. A recorded session', 1)[1].split('### 5b.', 1)[0]
    blocks = re.findall(r'<!-- gnd-run expect=0 output=stdout -->\s*```(python|sh)\n(.*?)\n```', chapter, re.DOTALL)
    needle = {'task': 'TASK-conflict.md', 'transcript': 'stdout =',
              'candidate': 'candidate =', 'feedback': 'feedback ='}[artifact]
    language, code = next((language, code) for language, code in blocks if needle in code)
    folder = 'bookrec-native' if domain == 'bookrec' else 'expense-native-demo'
    home = tmp_path / folder / 'recordings'
    shutil.copytree(ROOT / 'src/gnd/examples' / domain / 'recordings', home)
    subject = 'recommendation.population.json' if domain == 'bookrec' else 'approvals.population.json'
    relative = {'task': 'TASK-conflict.md', 'transcript': 'agent.stdout',
                'candidate': subject, 'feedback': 'feedback.json'}[artifact]
    target = home / relative if artifact == 'task' else home / 'codex-conflict-1/attempt-0001' / relative
    # Whitespace preserves JSON meaning and changes the committed bytes.
    target.write_text(target.read_text() + '\n')
    command = [sys.executable, *(['-O'] if optimized else []), '-c', code] if language == 'python' else ['bash', '-c', code]
    result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True, timeout=30, check=False)
    assert result.returncode != 0, f'{domain}/{artifact}: excerpt accepted changed bytes'
    assert 'AssertionError' in result.stderr or 'ValueError' in result.stderr, result.stderr


def test_expense_recorded_task_is_shown_in_full(tmp_path):
    import shutil
    import subprocess
    import sys

    page = (ROOT / 'docs/expense/04-native.md').read_text()
    code = next(code for code in re.findall(r'```python\n(.*?)\n```', page, re.DOTALL)
                if 'task = Path(' in code)
    home = tmp_path / 'expense-native-demo/recordings'
    shutil.copytree(ROOT / 'src/gnd/examples/expense/recordings', home)
    result = subprocess.run([sys.executable, '-c', code], cwd=tmp_path,
                            capture_output=True, text=True, check=False, timeout=30)
    assert result.returncode == 0, result.stderr
    assert result.stdout == (home / 'TASK-conflict.md').read_text()


@pytest.mark.parametrize('domain', ['bookrec', 'expense'])
def test_reordered_excerpt_is_refused(tmp_path, monkeypatch, domain):
    import shutil

    page = CHAPTERS[0] if domain == 'bookrec' else CHAPTERS[1]
    target = tmp_path / page
    target.parent.mkdir(parents=True)
    text = (ROOT / page).read_text()
    pattern = r'(<!-- gnd-excerpt source=rules_in_pyrel.py -->\s*```python\n)(.*?)(\n```)'
    match = re.search(pattern, text, re.DOTALL)
    lines = match[2].splitlines()
    replacement = '\n'.join(reversed(lines))
    target.write_text(text[:match.start(2)] + replacement + text[match.end(2):])
    for source in EXCERPT_SOURCES[domain].values():
        destination = tmp_path / source
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, destination)
    monkeypatch.setattr(__import__(__name__), 'ROOT', tmp_path)
    with pytest.raises(AssertionError):
        test_step_three_excerpts_come_from_shipped_files(domain, page)


@pytest.mark.parametrize('path', CHAPTERS)
@pytest.mark.parametrize('operation', ['preview', 'apply'])
def test_evolution_commands_preserve_failure_in_reader_shell(tmp_path, path, operation):
    import os
    import subprocess

    text = (ROOT / path).read_text()
    code = next(code for code in re.findall(r'```sh\n(.*?)\n```', text, re.DOTALL)
                if f'gnd evolve {operation} ' in code)
    fake = tmp_path / 'gnd'
    fake.write_text('#!/bin/sh\nprintf "  breaking: false\\n  affected: example\\n  conformance-exit: 0\\n"\nexit 42\n')
    fake.chmod(0o755)
    env = dict(os.environ, PATH=str(tmp_path) + os.pathsep + os.environ['PATH'])
    result = subprocess.run(['bash', '-c', code], cwd=tmp_path, env=env,
                            capture_output=True, text=True, check=False)
    assert result.returncode == 42, result.stdout + result.stderr


@pytest.mark.parametrize('kind', ['transition', 'population'])
def test_recorded_replay_refuses_drift_under_optimized_python(tmp_path, kind):
    import shutil
    import subprocess
    import sys

    page = (ROOT / 'docs/agents/recorded-sessions.md').read_text()
    blocks = re.findall(r'```python\n(.*?)\n```', page, re.DOTALL)
    if kind == 'transition':
        code = next(code for code in blocks if 'replayed = api.transition(' in code)
        shutil.copytree(ROOT / 'src/gnd/examples/approvals/recordings', tmp_path / 'approvals/recordings')
        (tmp_path / 'walk/cand').mkdir(parents=True)
        stub = 'from gnd import api; api.transition = lambda *a, **k: {"exit_code": 99}\n'
    else:
        code = next(code for code in blocks if 'replayed_exit = api.check(' in code)
        stub = 'from gnd import api; api.check = lambda *a, **k: {"exit_code": 99}\n'
    result = subprocess.run([sys.executable, '-O', '-c', stub + code], cwd=tmp_path,
                            capture_output=True, text=True, check=False, timeout=30)
    assert result.returncode != 0, result.stdout
    assert 'recorded verifier exit mismatch' in result.stderr, result.stderr
