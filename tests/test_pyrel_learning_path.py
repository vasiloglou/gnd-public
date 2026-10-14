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


@pytest.mark.parametrize('path,source', [
    ('docs/bookrec/07-native.md', 'src/gnd/examples/bookrec/extension/bookrec/native_query.py'),
    ('docs/expense/04-native.md', 'src/gnd/examples/expense/native_query.py')])
def test_step_three_excerpt_comes_from_shipped_query(path, source):
    text = (ROOT / path).read_text()
    section = text[text.index('## 3.'):text.index('## 4.')]
    excerpt = re.search(r'```python\n(.*?)\n```', section, flags=re.DOTALL).group(1)
    shipped = {line.strip() for line in (ROOT / source).read_text().splitlines()}
    lines = [line.strip() for line in excerpt.splitlines() if line.strip() and line.strip() != '...']
    assert len(lines) >= 3
    for line in lines:
        assert line in shipped, line
