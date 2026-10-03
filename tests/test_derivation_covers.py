from __future__ import annotations

import json
from pathlib import Path

import pytest

from gnd import cli
from gnd.cli import main
from gnd.exp.frontmatter import render_frontmatter
from gnd.exp.spec import SpecError, read_spec

CORPUS = Path(__file__).parent / 'fixtures' / 'phase3-consumers'

def _init_arguments(root: Path, cover: str) -> list[str]:
    return ['exp', 'init', 'EXP-008-derivation-cover', '--out', str(root), '--kind', 'data-driven', '--title', 'Can the experiment claim its derivation obligation', '--question', 'Q1=Did the verifier reach the structured derivation?', '--covers', cover]

def test_cli_json_derivation_cover_round_trips_through_spec(tmp_path: Path) -> None:
    assert main(_init_arguments(tmp_path, json.dumps({'derivation': 'book_is_eligible'}))) == 0
    spec = read_spec(tmp_path / 'EXP-008-derivation-cover' / 'SPEC.md')
    assert [entry.model_dump(exclude_none=True) for entry in spec.covers] == [{'derivation': 'book_is_eligible'}]

@pytest.mark.parametrize(('cover', 'message'), (({}, 'exactly one'), ({'fact_type': 'book_is_eligible', 'derivation': 'book_is_eligible'}, 'exactly one'), ({'derivations': 'book_is_eligible'}, 'extra')), ids=('zero-keys', 'two-keys', 'unknown-key'))
def test_spec_refuses_every_non_singleton_cover_entry(tmp_path: Path, cover: dict[str, str], message: str) -> None:
    path = tmp_path / 'SPEC.md'
    path.write_text(render_frontmatter({'id': 'EXP-008-derivation-cover', 'kind': 'data-driven', 'title': 'Closed derivation claim', 'questions': [{'id': 'Q1', 'text': 'Was the derivation reached?'}], 'follows': [], 'covers': [cover]}, '# Derivation cover\n'), encoding='utf-8')
    with pytest.raises(SpecError, match=message):
        read_spec(path)

def test_cli_json_refuses_a_multi_key_cover_without_writing(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as caught:
        main(_init_arguments(tmp_path, json.dumps({'fact_type': 'book_is_eligible', 'derivation': 'book_is_eligible'})))
    assert caught.value.code == cli.EXIT_USAGE
    assert list(tmp_path.iterdir()) == []

def test_exp_init_help_names_the_derivation_address(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        main(['exp', 'init', '--help'])
    assert caught.value.code == 0
    assert 'derivation:<id>' in capsys.readouterr().out

def test_coverage_corroborates_a_derivation_claim_without_merging_fact_type(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(_init_arguments(tmp_path, json.dumps({'derivation': 'book_is_eligible'}))) == 0
    capsys.readouterr()
    assert main(['coverage', str(CORPUS / 'eligibility.orm.yaml'), '--experiments', str(tmp_path), '--check', str(CORPUS / 'check-v4.exact.payload.json'), '--format', 'json']) == 0
    payload = json.loads(capsys.readouterr().out)
    rows = {row['address']: row for row in payload['elements']}
    derivation = rows['derivation:book_is_eligible']
    assert derivation['status'] == 'corroborated'
    assert [claim['experiment'] for claim in derivation['claims']] == ['EXP-008-derivation-cover']
    assert {item['source'] for item in derivation['evidence']} == {'check'}
    fact_type = rows['fact_type:book_is_eligible']
    assert fact_type['status'] == 'unclaimed'
    assert fact_type['claims'] == []
