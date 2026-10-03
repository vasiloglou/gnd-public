from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {'streams': {'files': ['apply.exit.json', 'apply.stderr.txt', 'apply.stdout.txt'], 'skill_recipe_home': 'src/gnd/skills/gnd-model-evolve/SKILL.md'}, 'skill_edge': {'post_phase_tokens': {'src/gnd/skills/gnd-model-evolve/SKILL.md': ['apply.stdout.txt', 'apply.stderr.txt', 'apply.exit.json'], 'src/gnd/skills/gnd-model-evolve/references/evolution-contract.md': ['tracked_roster', 'expected_tracked_tree_sha256', 'evolution:old-pending-read-only'], 'src/gnd/skills/gnd-orm-core/references/coverage-and-element-addressing.md': ['sources.unbound', 'legacy-report-without-model-digest'], 'src/gnd/skills/gnd-orm-core/references/representation-format.md': ['report.schema.json', 'schema_version', 'model_digest']}, 'removed_claim': {'forbidden_phrases': ['it appears in no `CheckReport`, no `--format json` payload'], 'path': 'src/gnd/skills/gnd-orm-core/references/representation-format.md', 'reason': 'the home states that the model digest appears in no --format json payload; the approved v5/v6 wire makes that false'}}}


def test_the_evolution_skill_documents_the_retained_stream_recipe() -> None:
    """INTENDED RED. The workflow home must give the explicit redirection recipe
    to caller-owned paths outside the immutable proposal directory."""
    answer = EXPECTED['streams']
    text = (REPO_ROOT / answer['skill_recipe_home']).read_text(encoding='utf-8')
    for name in answer['files']:
        assert name in text, name


@pytest.mark.parametrize('path', sorted(EXPECTED['skill_edge']['post_phase_tokens']))
def test_each_phase_three_skill_home_carries_its_new_normative_tokens(path: str) -> None:
    """INTENDED RED. Prose and code must agree about the new wire."""
    text = (REPO_ROOT / path).read_text(encoding='utf-8')
    for token in EXPECTED['skill_edge']['post_phase_tokens'][path]:
        assert token in text, f'{path} does not name {token!r}'


def test_the_representation_home_no_longer_denies_the_report_model_digest() -> None:
    """INTENDED RED. Leaving the old claim would ship false normative prose."""
    answer = EXPECTED['skill_edge']['removed_claim']
    text = (REPO_ROOT / answer['path']).read_text(encoding='utf-8')
    assert 'in every version 5 or 6 payload' in text, "the digest's reach is v5/v6, not all JSON"
    surviving = [phrase for phrase in answer['forbidden_phrases'] if phrase in text]
    assert surviving == [], answer['reason']
