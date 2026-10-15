"""PL18: replays of recorded sessions on the docs pages are rendered from committed recordings and stay in step."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REPLAYS = ROOT / 'docs/assets/replays'
TABLE = json.loads((REPLAYS / 'replays.json').read_text(encoding='utf-8'))
PAGES = [*(ROOT / 'docs/tutorials').glob('*.md'), *(ROOT / 'docs/how-to').glob('*.md')]


@pytest.mark.parametrize('name', sorted(TABLE))
def test_each_replay_is_a_fresh_render_of_its_recording(name):
    entry = TABLE[name]
    command = [sys.executable, str(ROOT / 'tools/render_replay.py'), *[str(ROOT / s) for s in entry['sources']],
               '--title', entry['title'], '--out', str(REPLAYS / f'{name}.svg'),
               '--transcript', str(REPLAYS / f'{name}.txt'), '--check']
    for said in entry.get('said', []):
        command += ['--said', said]
    run = subprocess.run(command, capture_output=True, text=True, timeout=60, check=False)
    assert run.returncode == 0, run.stderr


@pytest.mark.parametrize('name', sorted(TABLE))
def test_each_replay_is_accessible_and_small(name):
    svg = (REPLAYS / f'{name}.svg').read_text(encoding='utf-8')
    assert 'role="img"' in svg and '<title id=' in svg and '<desc id=' in svg and 'class="gnd-figure"' in svg
    assert '@media (prefers-reduced-motion: reduce)' in svg and 'animation:none' in svg
    assert len(svg.encode()) < 60 * 1024
    ident = re.search(r'<svg [^>]*id="([^"]+)"', svg).group(1)
    assert re.fullmatch(r'[a-z0-9-]+', ident), ident   # the style rules select on it


def test_every_replay_on_a_page_is_listed_and_followed_by_its_transcript():
    used = set()
    for page in PAGES:
        text = page.read_text(encoding='utf-8')
        for name in re.findall(r'--8<-- "docs/assets/replays/([\w.-]+)\.svg"', text):
            used.add(name)
            after = text.split(f'replays/{name}.svg"', 1)[1][:400]
            assert '??? note "Transcript of the replay' in after and f'replays/{name}.txt' in after, (page, name)
            label = re.search(r'aria-label="([^"]+)"[^>]*>\s*--8<-- "docs/assets/replays/' + re.escape(name), text)
            assert label and TABLE[name]['title'].replace('"', '&quot;') in label.group(1), (page, name)
    assert used == set(TABLE)


def test_replay_figures_are_raw_html_so_the_svg_is_not_rewritten():
    for page in PAGES:
        for figure in re.findall(r'<figure class="gnd-replay"[^>]*>', page.read_text(encoding='utf-8')):
            assert 'markdown=' not in figure, page


@pytest.mark.parametrize('name', sorted(TABLE))
def test_each_replay_is_named_after_the_run_it_replays(name):
    source = TABLE[name]['sources'][0]
    session = re.fullmatch(r'src/gnd/examples/plan_apps/recordings/([\w.-]+)/(\w+)/run-(\d)/session\.txt', source)
    skill = re.fullmatch(r'src/gnd/examples/plan_apps/skill-sessions(-evolve)?/claude-(\w+)/run-(\d)/turn-01\.jsonl',
                         source)
    if session:
        model, example, run = session.groups()
        assert name == f'{example}-{model}-run-{run}', (name, source)
        assert f'run {run})' in TABLE[name]['title']
    else:
        assert skill, source
        evolve, model, run = skill.groups()
        skill_name = 'model-evolve' if evolve else 'model-from-text'
        assert name == f'course-{skill_name}-{model}-run-{run}' and f'run {run})' in TABLE[name]['title']
