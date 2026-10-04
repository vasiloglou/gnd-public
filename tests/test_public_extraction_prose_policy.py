"""Current extraction prose routes and scope policy agree over public inputs."""
import re
from pathlib import Path

import pytest

from gnd.extraction_scope import fact_type_scope
from gnd.model import load_model

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS = REPO_ROOT / "src/gnd/skills"
MIXED_MODEL = REPO_ROOT / "tests/fixtures/v51-extraction-boundary/models/mixed.orm.yaml"
POPULATION_REFERENCE = 'gnd-orm-core/references/population-format.md'

SCOPE_DECLARATION = re.compile('included = `(?P<first>[^`]+)`, `(?P<second>[^`]+)`; excluded = `(?P<excluded>[^`]+)`')

POPULATION_ROUTE = '../gnd-orm-core/references/population-format.md#deterministic-document-extraction-covers'

CONTRACT_ROUTE = '../../gnd-orm-core/references/population-format.md#deterministic-document-extraction-covers'

def _declared_scope_classes(text: str) -> tuple[set[str], set[str]]:
    matches = list(SCOPE_DECLARATION.finditer(text))
    assert len(matches) == 1
    match = matches[0]
    return ({match['first'], match['second']}, {match['excluded']})

def _assert_prose_code_agree(scope: dict[str, str | None]) -> None:
    text = (SKILLS / POPULATION_REFERENCE).read_text(encoding='utf-8')
    included, excluded = _declared_scope_classes(text)
    model = load_model(MIXED_MODEL)
    for fact_type in model.fact_types:
        fact_type_id = str(fact_type['id'])
        rule = fact_type.get('derivation_rule')
        prose_class = 'structured-derived' if isinstance(rule, dict) else 'legacy-opaque' if isinstance(rule, str) else 'asserted'
        assert (scope[fact_type_id] is None) == (prose_class in included)
        assert (scope[fact_type_id] is not None) == (prose_class in excluded)

def test_normative_scope_classes_agree_with_the_policy_and_each_mutation_reds() -> None:
    scope = fact_type_scope(load_model(MIXED_MODEL))
    _assert_prose_code_agree(scope)
    for fact_type_id in ('book_listed', 'book_ranked', 'book_is_eligible'):
        mutated = dict(scope)
        mutated[fact_type_id] = 'flipped' if scope[fact_type_id] is None else None
        with pytest.raises(AssertionError):
            _assert_prose_code_agree(mutated)

def test_extraction_consequence_has_one_home_and_both_workflow_files_route() -> None:
    documents = {path.relative_to(SKILLS).as_posix(): path.read_text(encoding='utf-8') for path in SKILLS.rglob('*.md')}
    holders = [name for name, text in documents.items() if SCOPE_DECLARATION.search(text)]
    assert holders == [POPULATION_REFERENCE]
    assert POPULATION_ROUTE in documents['gnd-extract/SKILL.md']
    assert CONTRACT_ROUTE in documents['gnd-extract/references/extraction-contract.md']
    assert 'never\nemit a fact for a structured-derived fact type' in documents['gnd-extract/SKILL.md']

def test_extraction_skill_branches_on_the_applicability_reason() -> None:
    """Review finding 3: structured scope and unmatchable identity are distinct."""
    skill = (SKILLS / 'gnd-extract' / 'SKILL.md').read_text(encoding='utf-8')
    assert "Branch on the row's `reason`" in skill
    assert 'structured-derived scope reason means never extract that fact type' in skill
    assert 'reference-unmatchable reason' in skill
    assert 'Fact types marked inapplicable are ones the document had no way to name' not in skill
