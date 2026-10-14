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
        shipped = {line.strip() for line in (ROOT / EXCERPT_SOURCES[domain][name]).read_text().splitlines()}
        lines = [line.strip() for line in excerpt.splitlines() if line.strip() and line.strip() != '...']
        assert len(lines) >= 3, name
        for line in lines:
            assert line in shipped, (name, line)
    unmarked = re.findall(r'(?<!-->\n)```python\n(.*?)\n```', section, flags=re.DOTALL)
    # Illustrative python fences in step 3 are either marked excerpts or runnable blocks.
    for block in unmarked:
        assert block in {e for _, e in marked} or 'print(' in block, block[:80]


@pytest.mark.parametrize('domain', ['bookrec', 'expense'])
@pytest.mark.parametrize('artifact', ['task', 'transcript', 'candidate', 'feedback'])
def test_recorded_excerpt_refuses_changed_bytes(tmp_path, domain, artifact):
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
    command = [sys.executable, '-c', code] if language == 'python' else ['bash', '-c', code]
    result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True, timeout=30, check=False)
    assert result.returncode != 0, f'{domain}/{artifact}: excerpt accepted changed bytes'
    assert 'AssertionError' in result.stderr, result.stderr
