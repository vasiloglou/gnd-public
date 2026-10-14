"""PA5R D3: tutorial blocks that show a command and its checked output."""
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('output_runner', ROOT / 'tools/run_tutorials.py')
runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)


def page(tmp_path, body):
    path = tmp_path / 'lesson.md'
    path.write_text(body)
    return path


def block(command, expected, *, stream='stdout', exit_code=0, language='sh'):
    return (f'<!-- gnd-run expect={exit_code} output={stream} -->\n```{language}\n{command}\n```\n\n'
            f'```text\n{expected}\n```\n')


def test_matching_output_passes_and_is_recorded(tmp_path):
    receipts = []
    lesson = page(tmp_path, block('echo "Policy check: ACCEPTED"', 'Policy check: ACCEPTED'))
    assert runner.run_pages([lesson], tmp_path / 'work', Path(sys.executable), receipts=receipts) == 1
    assert receipts[0]['output_checked'] is True


def test_mismatched_output_fails_even_with_right_exit(tmp_path):
    lesson = page(tmp_path, block('echo "Policy check: REJECTED"', 'Policy check: ACCEPTED'))
    with pytest.raises(AssertionError, match='output differs'):
        runner.run_pages([lesson], tmp_path / 'work', Path(sys.executable))


def test_stderr_stream_and_python_fences(tmp_path):
    lesson = page(tmp_path, block('import sys; print("refused", file=sys.stderr); sys.exit(1)', 'refused',
                                  stream='stderr', exit_code=1, language='python'))
    assert runner.run_pages([lesson], tmp_path / 'work', Path(sys.executable)) == 1


def test_ellipsis_matches_any_run_of_lines(tmp_path):
    lesson = page(tmp_path, block('printf "a\\nb\\nc\\nd\\n"', 'a\n...\nd'))
    assert runner.run_pages([lesson], tmp_path / 'work', Path(sys.executable)) == 1
    lesson = page(tmp_path, block('printf "a\\nb\\n"', 'a\n...\nd'))
    with pytest.raises(AssertionError, match='output differs'):
        runner.run_pages([lesson], tmp_path / 'work', Path(sys.executable))


def test_normalizes_run_directory_temp_names_and_times(tmp_path):
    command = 'echo "$PWD/out.json gnd-native-checker-ab_12 took 1.25s  "'
    lesson = page(tmp_path, block(command, '<run>/out.json <tmp> took <time>'))
    assert runner.run_pages([lesson], tmp_path / 'work', Path(sys.executable)) == 1


def test_output_marker_without_text_fence_is_refused(tmp_path):
    lesson = page(tmp_path, '<!-- gnd-run expect=0 output=stdout -->\n```sh\necho hi\n```\n')
    with pytest.raises(AssertionError, match='missing or malformed'):
        list(runner.parsed_blocks(lesson))


def test_plain_blocks_keep_their_old_shape(tmp_path):
    lesson = page(tmp_path, '<!-- gnd-run expect=0 -->\n```sh\necho hi\n```\n')
    assert list(runner.parsed_blocks(lesson)) == [('sh', 0, 'echo hi', 'offline')]


@pytest.mark.parametrize('chapter', ['bookrec/07-native.md', 'expense/04-native.md'])
def test_native_chapters_show_output_for_every_block(chapter):
    text = (ROOT / 'docs' / chapter).read_text()
    rows = list(runner.parsed_outputs(ROOT / 'docs' / chapter))
    assert rows and len(rows) == text.count('gnd-run expect=')
    assert all(stream in {'stdout', 'stderr'} and expected for stream, expected in rows)


def test_receipt_status_reflects_output_mismatch(tmp_path):
    receipts = []
    lesson = page(tmp_path, block('echo "REJECTED"', 'ACCEPTED'))
    with pytest.raises(AssertionError):
        runner.run_pages([lesson], tmp_path / 'work', Path(sys.executable), receipts=receipts)
    assert receipts[-1]['status'] == 'failed'


def test_illustrative_text_after_unchecked_command_stays_unchecked(tmp_path):
    # Existing pages (agents/dev-session.md, agents/recorded-sessions.md) show illustrative
    # text after unchecked commands; only output= blocks are compared.
    lesson = page(tmp_path, '<!-- gnd-run expect=0 -->\n```sh\necho hi\n```\n\n```text\nbye\n```\n')
    assert runner.parsed_outputs(lesson) == [(None, None)]
    assert runner.run_pages([lesson], tmp_path / 'work', Path(sys.executable)) == 1
