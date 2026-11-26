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
    refunds = re.fullmatch(r'src/gnd/examples/refunds/skill-sessions/([\w-]+)/claude-(\w+)/run-(\d)/turn-01\.jsonl',
                           source)   # induction-skill IS2, spec section 6.4
    if session:
        model, example, run = session.groups()
        assert name == f'{example}-{model}-run-{run}', (name, source)
        assert f'run {run})' in TABLE[name]['title']
    elif refunds:
        conversation, model, run = refunds.groups()
        assert name == f'refunds-{conversation}-{model}-run-{run}' and f'run {run})' in TABLE[name]['title']
    else:
        assert skill, source
        evolve, model, run = skill.groups()
        skill_name = 'model-evolve' if evolve else 'model-from-text'
        assert name == f'course-{skill_name}-{model}-run-{run}' and f'run {run})' in TABLE[name]['title']


def test_each_tool_result_is_drawn_under_its_own_call():
    """induction-skill IS2: a batch of parallel calls was drawn as all calls, then all results, so a result
    appeared under the wrong command."""
    sys.path.insert(0, str(ROOT / 'tools'))
    import render_replay
    calls = [{'type': 'tool_use', 'id': i, 'name': 'Bash', 'input': {'command': f'cmd-{i}'}} for i in ('a', 'b')]
    results = [{'type': 'tool_result', 'tool_use_id': i, 'content': f'out-{i}'} for i in ('a', 'b')]
    stream = '\n'.join([json.dumps({'type': 'assistant', 'message': {'content': calls}}),
                        json.dumps({'type': 'user', 'message': {'content': results}})])
    texts = [text.strip() for _, text in render_replay.stream_lines([stream])]
    assert texts == ['Bash cmd-a', '→ out-a', 'Bash cmd-b', '→ out-b']


def test_a_code_block_in_a_flattened_message_is_marked_not_left_as_a_fence():
    """induction-skill IS2: a message's lines are joined into one, so a code block's fence survives only as
    three backticks in the text, which the site's leaked-fence check reads as an unrendered fence."""
    sys.path.insert(0, str(ROOT / 'tools'))
    import render_replay
    shown = render_replay._short("It ran.\n```text\nBLOCKING (none)\n```\nDone.")
    assert '```' not in shown and shown == 'It ran. [code] text BLOCKING (none) [code] Done.'


@pytest.mark.parametrize('message, kept', [
    ('~~~\n```python\nprint(1)\n```\n~~~', ['python', 'print(1)']),   # review phase-IS2-r1 F8: words were lost
    ('> ```sh\n> ls\n> ```', ['sh', 'ls']),                             # a quoted block kept its backticks
])
def test_a_fence_anywhere_is_marked_and_its_words_stay(message, kept):
    sys.path.insert(0, str(ROOT / 'tools'))
    import render_replay
    shown = render_replay._short(message)
    assert '```' not in shown and '[code]' in shown and all(word in shown for word in kept), shown


def test_results_pair_within_their_own_turn():
    """Review phase-IS2-r1 F8: two turns reusing a call id showed the second turn's result under both calls."""
    sys.path.insert(0, str(ROOT / 'tools'))
    import render_replay

    def turn(command, output):
        return '\n'.join([
            json.dumps({'type': 'assistant', 'message': {'content': [
                {'type': 'tool_use', 'id': 'same', 'name': 'Bash', 'input': {'command': command}}]}}),
            json.dumps({'type': 'user', 'message': {'content': [
                {'type': 'tool_result', 'tool_use_id': 'same', 'content': output}]}})])
    texts = [text.strip() for _, text in render_replay.stream_lines([turn('first', 'one'), turn('second', 'two')])]
    assert texts == ['Bash first', '→ one', 'Bash second', '→ two']
