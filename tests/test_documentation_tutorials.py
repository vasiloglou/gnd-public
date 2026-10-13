"""Tutorial commands are the test input, including expected deliberate failures."""
import importlib.util
import os
import re
import shlex
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path
from types import SimpleNamespace

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


@pytest.mark.parametrize('command', [
    command
    for line in (ROOT / 'docs/reference/cli.md').read_text().splitlines()
    if line.startswith('| `gnd ')
    for command in re.findall(r'`(gnd [^`]+)`', line)
])
def test_reference_command_routes_exist(command):
    argv = shlex.split(command)[1:]
    argv = argv[:argv.index('...')] if '...' in argv else argv
    result = subprocess.run([sys.executable, '-m', 'gnd', *argv, '--help'],
                            capture_output=True, text=True, timeout=30, check=False)
    assert result.returncode == 0, result.stderr
    assert 'usage:' in result.stdout.lower()


@pytest.mark.parametrize('same_bytes', [True, False])
def test_installed_validator_requires_matching_wheels(tmp_path, monkeypatch, same_bytes):
    root = tmp_path / 'checkout'
    for directory in ('docs', 'tools'):
        (root / directory).mkdir(parents=True)
    (root / 'README.md').write_text('test fixture')
    monkeypatch.setattr(installed_docs, '__file__', str(root / 'tools/check_installed_docs.py'))
    out = tmp_path / 'candidate'

    def fake_run(argv, **kwargs):
        stdout = ''
        if argv[:2] == ['uv', 'build']:
            target = Path(argv[argv.index('--out-dir') + 1])
            target.mkdir()
            with zipfile.ZipFile(target / 'example.whl', 'w') as wheel:
                for domain in ('bookrec', 'expense', 'dispatch', 'release', 'release_governance', 'approvals'):
                    info = zipfile.ZipInfo(f'gnd/examples/{domain}/README.md')
                    content = 'same' if same_bytes or target.name == 'release' else 'changed'
                    wheel.writestr(info, content)
            if target.name == 'release':
                with tarfile.open(target / 'example.tar.gz', 'w:gz') as archive:
                    info = tarfile.TarInfo('example')
                    info.type = tarfile.DIRTYPE
                    archive.addfile(info)
        elif '-c' in argv:
            stdout = str(Path(argv[0]).parent.parent / 'lib/gnd/__init__.py') + '\n'
        elif any(str(arg).endswith('run_tutorials.py') for arg in argv):
            stdout = '1 tutorial blocks passed\n'
        return SimpleNamespace(returncode=0, stdout=stdout, stderr='')

    monkeypatch.setattr(installed_docs.subprocess, 'run', fake_run)
    monkeypatch.setattr(sys, 'argv', ['check_installed_docs.py', '--out', str(out)])
    if same_bytes:
        installed_docs.main()
        assert (out / 'results.json').is_file()
    else:
        with pytest.raises(AssertionError, match='wheel origins differ'):
            installed_docs.main()
        assert not (out / 'results.json').exists()


def test_installed_origin_uses_path_components(tmp_path):
    root = tmp_path / 'project'
    venv = tmp_path / 'project-candidate' / 'venv'
    installed_docs.check_origin(str(venv / 'lib/gnd/__init__.py'), venv, root)
    with pytest.raises(AssertionError):
        installed_docs.check_origin(str(root / 'src/gnd/__init__.py'), venv, root)


@pytest.mark.parametrize('group', ['quickstart', 'release', 'bookrec', 'expense', 'api', 'walkthrough', 'agent-install', 'agent-plans', 'agent-model', 'agent-session', 'agent-recorded', 'runtime-pyrel', 'runtime-souffle', 'runtime-lean', 'runtime-decision'])
def test_documented_learning_path(group, tmp_path):
    pages = runner.groups(ROOT)[group]
    assert pages
    if group in {'bookrec', 'expense'}:
        assert len(pages) == (7 if group == 'bookrec' else 4)
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
