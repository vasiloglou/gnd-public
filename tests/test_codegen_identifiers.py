from __future__ import annotations

import ast
import json
import keyword
import re
import sys
from pathlib import Path

import pytest

from gnd.codegen.identifiers import (
    KEYWORD_SUFFIX,
    RESERVED_IDENTIFIERS,
    IdentifierError,
    module_name,
    python_symbol,
    symbol_table,
    tool_symbol,
)
from gnd.model import load_model

REPO_ROOT = Path(__file__).resolve().parents[1]
IDENTIFIERS_SRC = REPO_ROOT / 'src' / 'gnd' / 'codegen' / 'identifiers.py'
META_SCHEMA = REPO_ROOT / 'src' / 'gnd' / 'schema' / 'orm-meta.schema.json'
KEYWORDS_MODEL = REPO_ROOT / 'tests' / 'fixtures' / 'models' / 'keywords.orm.yaml'
ALL_KEYWORDS = tuple(keyword.kwlist) + tuple(keyword.softkwlist)

def _identifier_pattern() -> re.Pattern[str]:
    schema = json.loads(META_SCHEMA.read_text(encoding='utf-8'))
    return re.compile(schema['$defs']['identifier']['pattern'])

def test_the_keyword_fixture_is_a_valid_model_whose_ids_are_keywords() -> None:
    model = load_model(str(KEYWORDS_MODEL))
    object_ids = {str(entry['id']) for entry in model.object_types}
    fact_ids = {str(entry['id']) for entry in model.fact_types}
    role_names = {str(role['role_name']) for fact_type in model.fact_types for role in fact_type.get('roles') or []}
    assert {'class', 'lambda', 'pass', 'del'} <= object_ids
    assert {'import', 'global', 'yield'} <= fact_ids
    assert {'from', 'return', 'for', 'in', 'as', 'is'} <= role_names
    for name in object_ids | fact_ids | role_names:
        if name == 'type' and sys.version_info < (3, 12):
            assert python_symbol(name) == name
            continue
        assert keyword.iskeyword(name) or keyword.issoftkeyword(name), f'{name!r} in the keywords fixture is not a Python keyword — the fixture exists to be entirely hazardous'

def test_a_plain_identifier_passes_through_unchanged() -> None:
    assert python_symbol('employee') == 'employee'
    assert python_symbol('employee_has_name') == 'employee_has_name'

def test_a_hard_keyword_gets_the_pep8_trailing_underscore() -> None:
    assert python_symbol('import') == 'import' + KEYWORD_SUFFIX
    assert python_symbol('import') == 'import_'
    assert python_symbol('from') == 'from_'
    assert python_symbol('class') == 'class_'

def test_a_soft_keyword_is_sanitized_too() -> None:
    assert keyword.issoftkeyword('match') and (not keyword.iskeyword('match'))
    assert python_symbol('match') == 'match_'
    assert keyword.issoftkeyword('type') == (sys.version_info >= (3, 12))
    assert python_symbol('type') == ('type_' if keyword.issoftkeyword('type') else 'type')
    for word in keyword.softkwlist:
        assert python_symbol(word) == word + KEYWORD_SUFFIX

def test_a_name_the_emitted_module_itself_binds_is_sanitized() -> None:
    assert RESERVED_IDENTIFIERS, 'the reserved table is empty — it guards nothing'
    for reserved in RESERVED_IDENTIFIERS:
        assert python_symbol(reserved) == reserved + KEYWORD_SUFFIX, f'{reserved!r} is on the published reserved table but survives sanitization unchanged'

def test_every_keyword_maps_to_a_valid_non_keyword_symbol() -> None:
    assert len(ALL_KEYWORDS) > 30, f'the keyword sweep has only {len(ALL_KEYWORDS)} entries — it is not sweeping the stdlib keyword sets'
    for word in ALL_KEYWORDS:
        symbol = python_symbol(word)
        assert symbol.isidentifier(), f'{word!r} produced {symbol!r}, not an identifier'
        assert not keyword.iskeyword(symbol), f'{word!r} produced hard keyword {symbol!r}'
        assert not keyword.issoftkeyword(symbol), f'{word!r} produced soft keyword {symbol!r}'
        assert symbol not in RESERVED_IDENTIFIERS, f'{word!r} produced reserved name {symbol!r}'

def test_the_mapping_is_idempotent_on_its_own_output() -> None:
    for word in ALL_KEYWORDS + ('employee', 'import_', 'type_'):
        once = python_symbol(word)
        assert python_symbol(once) == once, f'{word!r}: {once!r} is not a fixed point'

def test_a_non_identifier_input_is_refused_rather_than_mangled() -> None:
    for bad in ('has space', '9lives', '', 'dash-ed'):
        with pytest.raises(IdentifierError):
            python_symbol(bad)

def test_a_sanitization_collision_raises_naming_both_model_ids() -> None:
    with pytest.raises(IdentifierError) as caught:
        symbol_table(['import', 'import_'], kind='fact type')
    message = str(caught.value)
    assert "'import'" in message, message
    assert "'import_'" in message, message
    assert "'import_'" not in message.replace("'import_'", ''), 'sanity: quoting is exact'

def test_distinct_ids_that_do_not_collide_build_a_table() -> None:
    table = symbol_table(['import', 'class', 'employee'], kind='fact type')
    assert table == {'import': 'import_', 'class': 'class_', 'employee': 'employee'}

def test_the_table_preserves_declaration_order() -> None:
    ids = ['yield', 'import', 'global']
    assert list(symbol_table(ids, kind='fact type')) == ids

def test_the_table_uses_the_symbol_function_it_is_given() -> None:
    table = symbol_table(['import'], kind='fact type', symbol=tool_symbol)
    assert table == {'import': tool_symbol('import')}

def test_tool_symbol_is_the_published_fact_type_mapping() -> None:
    assert tool_symbol('import') == 'import_'
    assert tool_symbol('employee_has_name') == 'employee_has_name'
    for fact_id in ('import', 'global', 'yield'):
        symbol = tool_symbol(fact_id)
        assert symbol.isidentifier() and (not keyword.iskeyword(symbol))

def test_tool_symbol_composes_python_symbol() -> None:
    for word in ALL_KEYWORDS:
        assert python_symbol(word) in tool_symbol(word)

def test_module_name_is_a_valid_module_identifier() -> None:
    assert module_name('full_vocabulary') == 'full_vocabulary'
    assert module_name('class') == 'class_'
    assert module_name('keywords') == 'keywords'

def test_no_python_keyword_is_hand_written_as_a_literal_in_the_module() -> None:
    source = IDENTIFIERS_SRC.read_text(encoding='utf-8')
    assert 'import keyword' in source
    assert 'keyword.iskeyword' in source and 'keyword.issoftkeyword' in source
    assert keyword.issoftkeyword(KEYWORD_SUFFIX), 'the exemption below is only justified while KEYWORD_SUFFIX is itself a soft keyword; if that stopped being true, drop the exemption'

    def hand_written_keywords(text: str) -> list[str]:
        return [node.value for node in ast.walk(ast.parse(text)) if isinstance(node, ast.Constant) and isinstance(node.value, str) and (node.value != KEYWORD_SUFFIX) and (keyword.iskeyword(node.value) or keyword.issoftkeyword(node.value))]
    constants = [node.value for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Constant) and isinstance(node.value, str)]
    assert constants, 'the AST walk found no string constants — it parsed nothing'
    assert hand_written_keywords('KWLIST = ["import", "class"]') == ['import', 'class'], 'the predicate does not catch a planted keyword list — it guards nothing'
    offenders = hand_written_keywords(source)
    assert not offenders, f'identifiers.py contains hand-written keyword literals {offenders}; the stdlib keyword module is the only permitted source of that set'

def test_module_name_folds_filename_space_characters() -> None:
    assert module_name('my-model') == 'my_model'
    assert module_name('v1.2-draft') == 'v1_2_draft'
    assert module_name('9lives').isidentifier()
    assert module_name('9lives').startswith('m_')
    for stem in ('my-model', 'v1.2-draft', '9lives', 'class', 'full_vocabulary'):
        symbol = module_name(stem)
        assert symbol.isidentifier(), f'{stem!r} produced {symbol!r}'
        assert not keyword.iskeyword(symbol)

def test_the_tables_are_module_level_data_with_rationale_comments() -> None:
    source = IDENTIFIERS_SRC.read_text(encoding='utf-8')
    for name in ('KEYWORD_SUFFIX', 'RESERVED_IDENTIFIERS'):
        assert f'\n{name} = ' in source or f'\n{name}: ' in source, f'{name} is not a module-level assignment'
        index = source.index(f'\n{name}')
        preamble = source[:index].rstrip('\n').rsplit('\n\n', 1)[-1]
        assert '#:' in preamble, f"{name} carries no `#:` rationale comment — projection.py:43's publish-the-table discipline is what makes the table reviewable"
