"""Tutorial commands are the test input, including expected deliberate failures."""
import importlib.util
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = load_tool('run_tutorials')
links = load_tool('check_docs')
installed_docs = load_tool('check_installed_docs')


def test_installed_origin_uses_path_components(tmp_path):
    root = tmp_path / 'project'
    venv = tmp_path / 'project-candidate' / 'venv'
    installed_docs.check_origin(str(venv / 'lib/gnd/__init__.py'), venv, root)
    with pytest.raises(AssertionError):
        installed_docs.check_origin(str(root / 'src/gnd/__init__.py'), venv, root)


@pytest.mark.parametrize('group', ['quickstart', 'release', 'bookrec', 'expense', 'api', 'walkthrough'])
def test_documented_learning_path(group, tmp_path):
    pages = runner.groups(ROOT)[group]
    assert pages
    if group in {'bookrec', 'expense'}:
        assert len(pages) == (6 if group == 'bookrec' else 3)
    python = Path(os.environ.get('GND_TUTORIAL_PYTHON', sys.executable)).absolute()
    assert runner.run_pages(pages, tmp_path, python) > 0


@pytest.mark.parametrize('body', [
    'Nothing executable here.',
    '<!-- gnd-run expect=0 -->\n```python\n\n```',
    '<!-- gnd-run expect=zero -->\n```python\nprint(1)\n```',
])
def test_missing_or_malformed_block_rejected(tmp_path, body):
    page = tmp_path / 'doc.md'
    page.write_text(body)
    with pytest.raises(AssertionError):
        list(runner.blocks(page))


@pytest.mark.parametrize('code', ['raise SystemExit(1)', 'assert 2 + 2 == 5'])
def test_wrong_exit_or_output_assertion_rejected(tmp_path, code):
    page = tmp_path / 'doc.md'
    page.write_text(f'<!-- gnd-run expect=0 -->\n```python\n{code}\n```')
    with pytest.raises(AssertionError, match='expected 0, got 1'):
        runner.run_pages([page], tmp_path, Path(sys.executable))


def test_shell_does_not_hide_earlier_failure(tmp_path):
    page = tmp_path / 'doc.md'
    page.write_text('<!-- gnd-run expect=0 -->\n```sh\nfalse\ntrue\n```')
    with pytest.raises(AssertionError):
        runner.run_pages([page], tmp_path, Path(sys.executable))


@pytest.mark.parametrize('bad', ['missing.html', '#absent', '../outside.html'])
def test_link_checker_rejects_invalid_targets(tmp_path, bad):
    (tmp_path / 'index.html').write_text('<h1 id="here">Hi</h1><a href="#here">ok</a>')
    assert links.check_site(tmp_path) == 1
    (tmp_path / 'index.html').write_text(f'<a href="{bad}">bad</a>')
    with pytest.raises(AssertionError):
        links.check_site(tmp_path)


def test_missing_site_rejected(tmp_path):
    with pytest.raises(AssertionError):
        links.check_site(tmp_path)


def test_rendered_markdown_fence_leak_rejected(tmp_path):
    (tmp_path / 'index.html').write_text('<p>```python gnd-run expect=0</p>')
    with pytest.raises(AssertionError, match='unrendered Markdown fence'):
        links.check_site(tmp_path)
