from __future__ import annotations

import posixpath
import re
import shutil
import subprocess
import tomllib
from collections.abc import Iterator
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as metadata_version
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path

import pytest

from gnd import DEV_VERSION, DISTRIBUTION, resolve_version

EXPECTED_SKILL_FILE_COUNT = 65
EXPECTED_RELATIVE_LINK_COUNT = 211
EXPECTED_RELATIVE_LINKS = frozenset({('gnd-extract/SKILL.md', '../gnd-dev-session/references/judgment-contract.md'), ('gnd-extract/references/extraction-contract.md', '../../gnd-dev-session/references/judgment-contract.md'), ('gnd-orm-core/SKILL.md', '../gnd-dev-session/references/judgment-contract.md'), ('gnd-orm-core/references/population-format.md', '../../gnd-dev-session/references/judgment-contract.md'), ('gnd-orm-core/references/representation-format.md', '../../gnd-dev-session/references/judgment-contract.md'), ('gnd-render-doc/SKILL.md', '../gnd-dev-session/references/judgment-contract.md'), ('gnd-render-doc/references/rendering-contract.md', '../../gnd-dev-session/references/judgment-contract.md'), ('gnd-model-evolve/SKILL.md', '../gnd-orm-core/references/representation-format.md#repair-annotations'), ('gnd-model-from-text/SKILL.md', '../gnd-orm-core/references/representation-format.md#repair-annotations'), ('gnd-orm-core/references/representation-format.md', '../../gnd-dev-session/references/session-v7-contract.md'), ('gnd-extract/SKILL.md', '../gnd-export/SKILL.md'), ('gnd-render-doc/SKILL.md', '../gnd-export/SKILL.md'), ('gnd-solve/SKILL.md', '../gnd-export/SKILL.md'), ('gnd-export/SKILL.md', '../gnd-orm-core/SKILL.md'), ('gnd-export/SKILL.md', '../gnd-orm-core/references/milestone-record-format.md'), ('gnd-export/references/export-contract.md', '../SKILL.md'), ('gnd-export/references/witness-contract.md', '../SKILL.md'), ('gnd-orm-core/SKILL.md', '../gnd-export/SKILL.md'), ('gnd-adopt/SKILL.md', '../gnd-orm-core/references/representation-format.md#fixed-reference-populations-version-4'), ('gnd-codegen/SKILL.md', '../gnd-orm-core/references/representation-format.md#fixed-reference-populations-version-4'), ('gnd-conformance/SKILL.md', '../gnd-orm-core/references/representation-format.md#fixed-reference-populations-version-4'), ('gnd-extract/SKILL.md', '../gnd-orm-core/references/representation-format.md#fixed-reference-populations-version-4'), ('gnd-model-evolve/SKILL.md', '../gnd-orm-core/references/representation-format.md#fixed-reference-populations-version-4'), ('gnd-model-from-code/SKILL.md', '../gnd-orm-core/references/representation-format.md#fixed-reference-populations-version-4'), ('gnd-model-from-text/SKILL.md', '../gnd-orm-core/references/representation-format.md#fixed-reference-populations-version-4'), ('gnd-render-doc/SKILL.md', '../gnd-orm-core/references/representation-format.md#fixed-reference-populations-version-4'), ('gnd-adopt/SKILL.md', '../gnd-orm-core/references/representation-format.md#calendar-day-terms-v71'), ('gnd-codegen/SKILL.md', '../gnd-orm-core/references/representation-format.md#calendar-day-terms-v71'), ('gnd-conformance/SKILL.md', '../gnd-orm-core/references/representation-format.md#calendar-day-terms-v71'), ('gnd-extract/SKILL.md', '../gnd-orm-core/references/representation-format.md#calendar-day-terms-v71'), ('gnd-model-evolve/SKILL.md', '../gnd-orm-core/references/representation-format.md#calendar-day-terms-v71'), ('gnd-model-from-code/SKILL.md', '../gnd-orm-core/references/representation-format.md#calendar-day-terms-v71'), ('gnd-model-from-text/SKILL.md', '../gnd-orm-core/references/representation-format.md#calendar-day-terms-v71'), ('gnd-render-doc/SKILL.md', '../gnd-orm-core/references/representation-format.md#calendar-day-terms-v71'), ('gnd-adopt/SKILL.md', '../gnd-model-from-code/SKILL.md'), ('gnd-orm-core/SKILL.md', '../gnd-adopt/SKILL.md'), ('gnd-adopt/SKILL.md', '../gnd-orm-core/references/provenance-and-modality.md'), ('gnd-adopt/SKILL.md', '../gnd-orm-core/references/milestone-record-format.md'), ('gnd-adopt/SKILL.md', '../gnd-new-project/SKILL.md'), ('gnd-adopt/references/gsd-mapping.md', '../../gnd-orm-core/references/provenance-and-modality.md'), ('gnd-codegen/SKILL.md', '../gnd-conformance/SKILL.md'), ('gnd-codegen/SKILL.md', '../gnd-extract/SKILL.md'), ('gnd-codegen/SKILL.md', '../gnd-model-evolve/SKILL.md'), ('gnd-codegen/SKILL.md', '../gnd-model-from-text/SKILL.md'), ('gnd-codegen/SKILL.md', '../gnd-new-project/SKILL.md'), ('gnd-codegen/SKILL.md', '../gnd-orm-core/SKILL.md'), ('gnd-codegen/SKILL.md', '../gnd-orm-core/references/milestone-record-format.md'), ('gnd-codegen/SKILL.md', '../gnd-orm-core/references/population-format.md'), ('gnd-codegen/SKILL.md', '../gnd-render-doc/SKILL.md'), ('gnd-codegen/references/codegen-contract.md', '../../gnd-extract/references/extraction-contract.md'), ('gnd-codegen/references/codegen-contract.md', '../../gnd-orm-core/references/population-format.md'), ('gnd-codegen/references/codegen-contract.md', '../SKILL.md'), ('gnd-codegen/references/architecture-contract.md', '../SKILL.md'), ('gnd-conformance/SKILL.md', '../gnd-codegen/SKILL.md'), ('gnd-conformance/SKILL.md', '../gnd-extract/SKILL.md'), ('gnd-conformance/SKILL.md', '../gnd-model-evolve/SKILL.md'), ('gnd-conformance/SKILL.md', '../gnd-model-from-code/SKILL.md'), ('gnd-conformance/SKILL.md', '../gnd-model-from-text/SKILL.md'), ('gnd-conformance/SKILL.md', '../gnd-new-project/SKILL.md'), ('gnd-conformance/SKILL.md', '../gnd-orm-core/SKILL.md'), ('gnd-conformance/SKILL.md', '../gnd-orm-core/references/milestone-record-format.md'), ('gnd-conformance/SKILL.md', '../gnd-review-panel/SKILL.md'), ('gnd-conformance/references/conformance-contract.md', '../SKILL.md'), ('gnd-dev-session/SKILL.md', '../gnd-codegen/SKILL.md'), ('gnd-dev-session/SKILL.md', '../gnd-conformance/SKILL.md'), ('gnd-dev-session/SKILL.md', '../gnd-model-evolve/SKILL.md'), ('gnd-dev-session/SKILL.md', '../gnd-new-project/SKILL.md'), ('gnd-dev-session/SKILL.md', '../gnd-orm-core/SKILL.md'), ('gnd-dev-session/SKILL.md', '../gnd-orm-core/references/milestone-record-format.md'), ('gnd-dev-session/SKILL.md', '../gnd-orm-core/references/population-format.md'), ('gnd-dev-session/SKILL.md', '../gnd-orm-core/references/representation-format.md'), ('gnd-dev-session/SKILL.md', '../gnd-review-panel/SKILL.md'), ('gnd-extract/SKILL.md', '../gnd-model-from-text/SKILL.md'), ('gnd-extract/SKILL.md', '../gnd-new-project/SKILL.md'), ('gnd-extract/SKILL.md', '../gnd-orm-core/SKILL.md'), ('gnd-extract/SKILL.md', '../gnd-orm-core/references/milestone-record-format.md'), ('gnd-extract/SKILL.md', '../gnd-orm-core/references/population-format.md'), ('gnd-extract/SKILL.md', '../gnd-orm-core/references/population-format.md#deterministic-document-extraction-covers'), ('gnd-extract/SKILL.md', '../gnd-render-doc/SKILL.md'), ('gnd-extract/references/extraction-contract.md', '../../gnd-orm-core/references/population-format.md#deterministic-document-extraction-covers'), ('gnd-extract/references/extraction-contract.md', '../SKILL.md'), ('gnd-model-evolve/SKILL.md', '../gnd-conformance/references/conformance-contract.md'), ('gnd-model-evolve/SKILL.md', '../gnd-new-project/SKILL.md'), ('gnd-model-evolve/SKILL.md', '../gnd-orm-core/SKILL.md'), ('gnd-model-evolve/SKILL.md', '../gnd-orm-core/references/milestone-record-format.md'), ('gnd-model-evolve/SKILL.md', '../gnd-orm-core/references/provenance-and-modality.md'), ('gnd-model-evolve/references/evolution-contract.md', '../../gnd-orm-core/SKILL.md'), ('gnd-model-evolve/references/evolution-contract.md', '../../gnd-orm-core/references/provenance-and-modality.md'), ('gnd-model-evolve/references/evolution-contract.md', '../SKILL.md'), ('gnd-model-from-code/SKILL.md', '../gnd-new-project/SKILL.md'), ('gnd-model-from-code/SKILL.md', '../gnd-orm-core/SKILL.md'), ('gnd-model-from-code/SKILL.md', '../gnd-orm-core/references/milestone-record-format.md'), ('gnd-model-from-code/SKILL.md', '../gnd-orm-core/references/provenance-and-modality.md'), ('gnd-model-from-code/references/recovery-contract.md', '../../gnd-orm-core/SKILL.md'), ('gnd-model-from-code/references/recovery-contract.md', '../SKILL.md'), ('gnd-model-from-text/SKILL.md', '../gnd-model-evolve/SKILL.md'), ('gnd-model-from-text/SKILL.md', '../gnd-model-from-code/SKILL.md'), ('gnd-model-from-text/SKILL.md', '../gnd-new-project/SKILL.md'), ('gnd-model-from-text/SKILL.md', '../gnd-orm-core/SKILL.md'), ('gnd-model-from-text/SKILL.md', '../gnd-orm-core/references/constraint-inference.md'), ('gnd-model-from-text/SKILL.md', '../gnd-orm-core/references/constraint-reference.md'), ('gnd-model-from-text/SKILL.md', '../gnd-orm-core/references/halpin-posture.md'), ('gnd-model-from-text/SKILL.md', '../gnd-orm-core/references/milestone-record-format.md'), ('gnd-model-from-text/SKILL.md', '../gnd-orm-core/references/orm-meta.schema.json'), ('gnd-model-from-text/SKILL.md', '../gnd-orm-core/references/provenance-and-modality.md'), ('gnd-model-from-text/SKILL.md', '../gnd-orm-core/references/representation-format.md'), ('gnd-model-from-text/SKILL.md', '../gnd-orm-core/references/verbalization-patterns.md'), ('gnd-model-from-text/USAGE.md', '../gnd-orm-core/SKILL.md'), ('gnd-model-from-text/USAGE.md', '../gnd-orm-core/references/constraint-inference.md'), ('gnd-model-from-text/USAGE.md', '../gnd-orm-core/references/provenance-and-modality.md'), ('gnd-model-from-text/evals/README.md', '../examples/movie_catalog.dialogue.md'), ('gnd-model-from-text/references/csdp-workflow.md', '../../gnd-orm-core/references/constraint-inference.md'), ('gnd-model-from-text/references/csdp-workflow.md', '../../gnd-orm-core/references/constraint-reference.md'), ('gnd-model-from-text/references/csdp-workflow.md', '../../gnd-orm-core/references/halpin-posture.md'), ('gnd-model-from-text/references/csdp-workflow.md', '../../gnd-orm-core/references/provenance-and-modality.md'), ('gnd-model-from-text/references/csdp-workflow.md', '../../gnd-orm-core/references/representation-format.md'), ('gnd-model-from-text/references/csdp-workflow.md', '../../gnd-orm-core/references/verbalization-patterns.md'), ('gnd-model-from-text/references/dialogue-patterns.md', '../../gnd-orm-core/references/halpin-posture.md'), ('gnd-model-from-text/references/dialogue-patterns.md', '../../gnd-orm-core/references/provenance-and-modality.md'), ('gnd-new-project/SKILL.md', '../gnd-model-from-code/SKILL.md'), ('gnd-new-project/SKILL.md', '../gnd-model-from-text/SKILL.md'), ('gnd-new-project/SKILL.md', '../gnd-orm-core/references/milestone-record-format.md'), ('gnd-new-project/SKILL.md', '../gnd-orm-core/references/coverage-and-element-addressing.md'), ('gnd-new-project/SKILL.md', '../gnd-solve/SKILL.md'), ('gnd-orm-core/SKILL.md', '../gnd-codegen/SKILL.md'), ('gnd-orm-core/SKILL.md', '../gnd-conformance/SKILL.md'), ('gnd-orm-core/SKILL.md', '../gnd-dev-session/SKILL.md'), ('gnd-orm-core/SKILL.md', '../gnd-extract/SKILL.md'), ('gnd-orm-core/SKILL.md', '../gnd-model-evolve/SKILL.md'), ('gnd-orm-core/SKILL.md', '../gnd-model-from-code/SKILL.md'), ('gnd-orm-core/SKILL.md', '../gnd-model-from-text/SKILL.md'), ('gnd-orm-core/SKILL.md', '../gnd-new-project/SKILL.md'), ('gnd-orm-core/SKILL.md', '../gnd-render-doc/SKILL.md'), ('gnd-orm-core/SKILL.md', '../gnd-review-panel/SKILL.md'), ('gnd-orm-core/SKILL.md', '../gnd-review-panel-light/SKILL.md'), ('gnd-orm-core/SKILL.md', '../gnd-solve/SKILL.md'), ('gnd-orm-core/SKILL.md', '../gnd-update-review-panel/SKILL.md'), ('gnd-orm-core/references/milestone-record-format.md', '../../gnd-new-project/SKILL.md'), ('gnd-orm-core/references/milestone-record-format.md', '../../gnd-solve/SKILL.md'), ('gnd-render-doc/SKILL.md', '../gnd-extract/SKILL.md'), ('gnd-render-doc/SKILL.md', '../gnd-new-project/SKILL.md'), ('gnd-render-doc/SKILL.md', '../gnd-orm-core/SKILL.md'), ('gnd-render-doc/SKILL.md', '../gnd-orm-core/references/milestone-record-format.md'), ('gnd-render-doc/SKILL.md', '../gnd-orm-core/references/population-format.md'), ('gnd-render-doc/references/rendering-contract.md', '../SKILL.md'), ('gnd-review-panel/SKILL.md', '../gnd-conformance/SKILL.md'), ('gnd-review-panel/SKILL.md', '../gnd-model-from-text/SKILL.md'), ('gnd-review-panel/SKILL.md', '../gnd-new-project/SKILL.md'), ('gnd-review-panel/SKILL.md', '../gnd-orm-core/SKILL.md'), ('gnd-review-panel/SKILL.md', '../gnd-orm-core/references/milestone-record-format.md'), ('gnd-review-panel/SKILL.md', '../gnd-update-review-panel/SKILL.md'), ('gnd-review-panel-light/SKILL.md', '../gnd-review-panel/SKILL.md'), ('gnd-review-panel-light/SKILL.md', '../gnd-review-panel/references/review-contract.md'), ('gnd-review-panel-light/SKILL.md', '../gnd-orm-core/references/milestone-record-format.md'), ('gnd-review-panel/references/review-contract.md', '../../gnd-update-review-panel/SKILL.md'), ('gnd-review-panel/references/review-contract.md', '../SKILL.md'), ('gnd-solve/SKILL.md', '../gnd-codegen/SKILL.md'), ('gnd-solve/SKILL.md', '../gnd-conformance/SKILL.md'), ('gnd-solve/SKILL.md', '../gnd-dev-session/SKILL.md'), ('gnd-solve/SKILL.md', '../gnd-model-evolve/SKILL.md'), ('gnd-solve/SKILL.md', '../gnd-model-from-code/SKILL.md'), ('gnd-solve/SKILL.md', '../gnd-model-from-text/SKILL.md'), ('gnd-solve/SKILL.md', '../gnd-new-project/SKILL.md'), ('gnd-solve/SKILL.md', '../gnd-orm-core/SKILL.md'), ('gnd-solve/SKILL.md', '../gnd-orm-core/references/milestone-record-format.md'), ('gnd-solve/SKILL.md', '../gnd-review-panel/SKILL.md'), ('gnd-update-review-panel/SKILL.md', '../gnd-orm-core/references/milestone-record-format.md')})
EXPECTED_SKILL_NAMES = frozenset({'gnd-adopt', 'gnd-codegen', 'gnd-conformance', 'gnd-dev-session', 'gnd-extract', 'gnd-export', 'gnd-model-evolve', 'gnd-model-from-code', 'gnd-model-from-text', 'gnd-new-project', 'gnd-orm-core', 'gnd-render-doc', 'gnd-review-panel', 'gnd-review-panel-light', 'gnd-solve', 'gnd-update-review-panel'})
EXPECTED_SKILL_FILES = frozenset({'gnd-dev-session/references/judgment-contract.md', 'gnd-adopt/SKILL.md', 'gnd-adopt/migration.schema.json', 'gnd-adopt/references/gsd-environment-cleanup.md', 'gnd-adopt/references/gsd-mapping.md', 'gnd-adopt/scripts/verify_migration.py', 'gnd-codegen/SKILL.md', 'gnd-codegen/references/architecture-contract.md', 'gnd-codegen/references/codegen-contract.md', 'gnd-conformance/SKILL.md', 'gnd-conformance/references/conformance-contract.md', 'gnd-dev-session/SKILL.md', 'gnd-dev-session/references/session-v7-contract.md', 'gnd-export/SKILL.md', 'gnd-export/references/export-contract.md', 'gnd-export/references/witness-contract.md', 'gnd-export/references/witness.schema.json', 'gnd-extract/SKILL.md', 'gnd-extract/references/extraction-contract.md', 'gnd-model-evolve/SKILL.md', 'gnd-model-evolve/references/evolution-contract.md', 'gnd-model-from-code/SKILL.md', 'gnd-model-from-code/references/recovery-contract.md', 'gnd-model-from-text/SKILL.md', 'gnd-model-from-text/USAGE.md', 'gnd-model-from-text/evals/README.md', 'gnd-model-from-text/evals/cases.json', 'gnd-model-from-text/evals/expected/synthetic_good_user.orm.yaml', 'gnd-model-from-text/evals/fixtures/synthetic_good_user/README.md', 'gnd-model-from-text/evals/fixtures/synthetic_good_user/dialogue.md', 'gnd-model-from-text/evals/reviewability_checklist.md', 'gnd-model-from-text/examples/library_with_subtypes.dialogue.md', 'gnd-model-from-text/examples/library_with_subtypes.orm.yaml', 'gnd-model-from-text/examples/movie_catalog.dialogue.md', 'gnd-model-from-text/examples/movie_catalog.orm.yaml', 'gnd-model-from-text/examples/objectification_in_enrollment.dialogue.md', 'gnd-model-from-text/examples/objectification_in_enrollment.orm.yaml', 'gnd-model-from-text/examples/reference_scheme_elicitation.dialogue.md', 'gnd-model-from-text/examples/reference_scheme_elicitation.orm.yaml', 'gnd-model-from-text/references/csdp-workflow.md', 'gnd-model-from-text/references/dialogue-patterns.md', 'gnd-model-from-text/scripts/validate_model.py', 'gnd-new-project/SKILL.md', 'gnd-orm-core/SKILL.md', 'gnd-orm-core/references/constraint-inference.md', 'gnd-orm-core/references/coverage-and-element-addressing.md', 'gnd-orm-core/references/constraint-reference.md', 'gnd-orm-core/references/halpin-posture.md', 'gnd-orm-core/references/milestone-record-format.md', 'gnd-orm-core/references/orm-meta.schema.json', 'gnd-orm-core/references/population-format.md', 'gnd-orm-core/references/population.schema.json', 'gnd-orm-core/references/provenance-and-modality.md', 'gnd-orm-core/references/representation-format.md', 'gnd-orm-core/references/steps.schema.json', 'gnd-orm-core/references/verbalization-patterns.md', 'gnd-render-doc/SKILL.md', 'gnd-render-doc/references/rendering-contract.md', 'gnd-review-panel/SKILL.md', 'gnd-review-panel/references/review-contract.md', 'gnd-review-panel-light/SKILL.md', 'gnd-solve/SKILL.md', 'gnd-update-review-panel/SKILL.md', 'gnd-update-review-panel/agents/openai.yaml', 'gnd-update-review-panel/scripts/update_harnesses.py'})
FROZEN_BASE_DEPENDENCIES = {'jsonschema', 'pydantic', 'ruamel-yaml'}
PEP723_SIBLING_SCHEMA = 'gnd-orm-core/references/orm-meta.schema.json'
RELATIVE_LINK_RE = re.compile(b'\\]\\((\\.\\./[^)\\s]+)\\)')
REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / 'pyproject.toml'

def iter_skill_files(root: Traversable, prefix: str='') -> Iterator[tuple[str, Traversable]]:
    for entry in root.iterdir():
        rel = f'{prefix}{entry.name}'
        if entry.is_dir():
            yield from iter_skill_files(entry, f'{rel}/')
        else:
            yield (rel, entry)

def _skills_root() -> Traversable:
    return files('gnd') / 'skills'

def _read_pyproject() -> dict:
    return tomllib.loads(PYPROJECT.read_text(encoding='utf-8'))

def _normalize(requirement: str) -> str:
    name = re.split('[<>=!~;\\[\\s]', requirement.strip(), maxsplit=1)[0]
    return re.sub('[-_.]+', '-', name).lower()

def test_skills_resource_root_is_a_directory() -> None:
    root = _skills_root()
    assert root.is_dir(), "the packaged resource directory gnd/skills is absent — importlib.resources.files('gnd') / 'skills' is not a directory. The skill tree must live under src/gnd/skills/ so it ships inside the wheel and is visible identically from an editable checkout (D-04)."

def test_skill_resource_tree_carries_every_file() -> None:
    root = _skills_root()
    assert root.is_dir(), 'gnd/skills resource directory is absent (see the sibling test)'
    found = sorted((rel for rel, _ in iter_skill_files(root)))
    missing = sorted(EXPECTED_SKILL_FILES - set(found))
    extra = sorted(set(found) - EXPECTED_SKILL_FILES)
    assert not missing and (not extra), f'the packaged skill tree is not the pinned inventory.\n  missing ({len(missing)}): ' + ', '.join(missing) + f'\n  extra   ({len(extra)}): ' + ', '.join(extra) + '\nSet difference, not arithmetic: a dropped file and an unrelated added one cancel in a count and are both named here.'
    assert len(found) == EXPECTED_SKILL_FILE_COUNT, f'the packaged skill tree holds {len(found)} files, expected {EXPECTED_SKILL_FILE_COUNT}. A partial include is the failure that matters here. Found:\n  ' + '\n  '.join(found)
    assert len(EXPECTED_SKILL_FILES) == EXPECTED_SKILL_FILE_COUNT, f'the pinned inventory holds {len(EXPECTED_SKILL_FILES)} paths but EXPECTED_SKILL_FILE_COUNT is {EXPECTED_SKILL_FILE_COUNT}. The two literals describe the same tree and are updated as one decision; this assertion is what stops them from drifting apart silently.'

def test_the_packaged_tree_holds_exactly_the_fifteen_named_skills() -> None:
    root = _skills_root()
    assert root.is_dir(), 'gnd/skills resource directory is absent (see the sibling test)'
    names = {rel.split('/')[0] for rel, _ in iter_skill_files(root)}
    assert names == EXPECTED_SKILL_NAMES, f'packaged skills are {sorted(names)}, expected {sorted(EXPECTED_SKILL_NAMES)}.\n  missing: {sorted(EXPECTED_SKILL_NAMES - names)}\n  extra:   {sorted(names - EXPECTED_SKILL_NAMES)}'
    assert len(EXPECTED_SKILL_NAMES) == 16, 'the packaged surface is exactly fifteen skills; a sixteenth is a decision with a plan behind it, not an edit to this literal'

def test_every_relative_skill_link_resolves_inside_the_resource_tree() -> None:
    root = _skills_root()
    assert root.is_dir(), 'gnd/skills resource directory is absent (see the sibling test)'
    entries = {rel for rel, _ in iter_skill_files(root)}
    directories = set()
    for rel in entries:
        parts = rel.split('/')
        for depth in range(1, len(parts)):
            directories.add('/'.join(parts[:depth]))
    checked = 0
    edges: set[tuple[str, str]] = set()
    unresolved: list[str] = []
    for rel, resource in iter_skill_files(root):
        if not rel.endswith('.md'):
            continue
        parent = posixpath.dirname(rel)
        for match in RELATIVE_LINK_RE.finditer(resource.read_bytes()):
            target = match.group(1).decode('utf-8')
            checked += 1
            edges.add((rel, target))
            target_path = target.partition('#')[0]
            resolved = posixpath.normpath(posixpath.join(parent, target_path))
            if resolved not in entries and resolved not in directories:
                unresolved.append(f'{rel} -> {target} (resolved: {resolved})')
    assert not unresolved, 'cross-skill relative links point nowhere:\n  ' + '\n  '.join(unresolved)
    missing = sorted(EXPECTED_RELATIVE_LINKS - edges)
    extra = sorted(edges - EXPECTED_RELATIVE_LINKS)
    assert not missing and (not extra), f'the skill routing graph is not the pinned inventory.\n  missing ({len(missing)}): ' + ', '.join((f'{s} -> {t}' for s, t in missing)) + f'\n  extra   ({len(extra)}): ' + ', '.join((f'{s} -> {t}' for s, t in extra)) + '\nSet difference, not arithmetic: a removed route and an unrelated new one cancel in a count and are both named here. If the change is intentional, regenerate EXPECTED_RELATIVE_LINKS per its comment.'
    assert checked == EXPECTED_RELATIVE_LINK_COUNT, f'checked {checked} relative links, expected {EXPECTED_RELATIVE_LINK_COUNT}. These links are sibling-relative by design (D-07) and survive the tree move by construction. With the graph pinned as a set above, this count is the non-vacuity floor and the loose multiplicity guard: it moves when an existing route is mentioned more or fewer times.'

def test_pep723_validator_sibling_schema_ships() -> None:
    root = _skills_root()
    assert root.is_dir(), 'gnd/skills resource directory is absent (see the sibling test)'
    entries = {rel for rel, _ in iter_skill_files(root)}
    assert PEP723_SIBLING_SCHEMA in entries, f'{PEP723_SIBLING_SCHEMA} is missing from the packaged skill tree; gnd-model-from-text/scripts/validate_model.py resolves its meta-schema through that sibling path and would be broken for every installed user.'

def test_installed_version_matches_pyproject() -> None:
    declared = _read_pyproject()['project']['version']
    try:
        installed = metadata_version(DISTRIBUTION)
    except PackageNotFoundError:
        pytest.fail(f'distribution {DISTRIBUTION!r} has no installed metadata; run `uv sync` so the editable install matches the pyproject name (D-01).')
    assert installed == declared, f'installed metadata reports version {installed!r} but pyproject.toml declares {declared!r}. pyproject.toml is the only place a version number is written (D-02); re-sync the environment rather than adding a second literal.'

def test_console_script_reports_the_single_sourced_version() -> None:
    executable = shutil.which('gnd')
    if executable is None:
        pytest.skip('the `gnd` console script is not on PATH (run under `uv run`)')
    result = subprocess.run([executable, '--version'], capture_output=True, text=True, check=False)
    declared = _read_pyproject()['project']['version']
    assert result.returncode == 0, f"`gnd --version` exited {result.returncode}, expected 0. argparse's version action raises SystemExit(0), which is inside the normative band contract.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    assert declared in result.stdout, f'`gnd --version` printed {result.stdout.strip()!r}, which does not carry the pyproject version {declared!r}. The version has exactly one source (D-02) — do not add a literal to src/.'

def test_resolve_version_reports_an_unmistakable_string_when_uninstalled(monkeypatch: pytest.MonkeyPatch) -> None:

    def _raise(_name: str) -> str:
        raise PackageNotFoundError(DISTRIBUTION)
    monkeypatch.setattr('gnd.version', _raise)
    fallback = resolve_version()
    assert fallback == DEV_VERSION
    assert 'dev' in fallback, 'the development fallback must carry a `dev` marker a human cannot mistake for a release (D-02).'

def test_base_dependency_set_is_frozen() -> None:
    declared = {_normalize(dep) for dep in _read_pyproject()['project']['dependencies']}
    assert declared == FROZEN_BASE_DEPENDENCIES, f'base dependencies are {sorted(declared)}, expected {sorted(FROZEN_BASE_DEPENDENCIES)}. D-18 freezes the base install: a new runtime dependency goes behind an optional extra, and this test is the mechanical form of that policy. Changing it is a decision, not a fix.'

def test_faker_is_pinned_under_the_synth_extra_and_nowhere_in_the_base() -> None:
    pyproject = _read_pyproject()
    project = pyproject['project']
    base = {_normalize(dep) for dep in project.get('dependencies', [])}
    assert 'faker' not in base, f'faker leaked into [project.dependencies] {sorted(base)}; D-18 keeps the base install at jsonschema/pydantic/ruamel-yaml. The synth stack is opt-in — promoting faker to base is a decision, not a fix.'
    extras = project.get('optional-dependencies', {})
    synth = {_normalize(dep) for dep in extras.get('synth', [])}
    assert synth == {'faker'}, f"[project.optional-dependencies] synth is {sorted(synth)}, expected exactly {{'faker'}}. The extra carries the one package this phase installs and no more (polyfactory and hypothesis are refuted/deferred, D-17)."
    faker_pin = next(dep for dep in extras['synth'] if _normalize(dep) == 'faker')
    assert '40.36.0' in faker_pin, f'the synth extra pins {faker_pin!r}; the legitimacy gate cleared faker==40.36.0 specifically. A version bump is a re-clearance, not a fix.'
    dev_dependencies = pyproject.get('dependency-groups', {}).get('dev', [])
    dev_faker = [dep for dep in dev_dependencies if _normalize(dep) == 'faker']
    assert len(dev_faker) == 1 and '40.36.0' in dev_faker[0], '[dependency-groups] dev must pin faker==40.36.0 because the default test suite invokes the optional synth lane'

def test_the_extract_skill_and_its_contract_agree_on_the_parse_failure_state() -> None:
    root = _skills_root() / 'gnd-extract'
    sources = {'SKILL.md': (root / 'SKILL.md').read_text(encoding='utf-8'), 'references/extraction-contract.md': (root / 'references' / 'extraction-contract.md').read_text(encoding='utf-8')}
    refuted = re.compile('(?:run is|failure is)\\s*`?extraction:\\s*failed`?\\s*at exit 3', re.IGNORECASE)
    for name, text in sources.items():
        assert not refuted.search(text), f'{name} still claims a parse failure yields `extraction: failed` at exit 3. Measured behaviour is exit 3 with state `ran` — `failed` is reserved for sidecar problems (UAT 2, 2026-08-13).'
    keeps_state_ran = re.compile('state.{0,40}?(?:stay|remain|is|=)\\w*\\s*`?ran`?', re.IGNORECASE | re.DOTALL)
    for name, text in sources.items():
        assert keeps_state_ran.search(text), f'{name} no longer states that `extraction.state` stays `ran` on a parse failure. The fix for a wrong sentence is a right one, not silence — an agent that reads neither claim guesses.'

def test_every_packaged_skill_frontmatter_reads_back(tmp_path: Path) -> None:
    from gnd.exp.frontmatter import read_frontmatter
    root = _skills_root()
    documents = [(rel, resource) for rel, resource in iter_skill_files(root) if rel.endswith('/SKILL.md')]
    assert len(documents) >= 5, f'only {len(documents)} SKILL.md documents were found under the packaged tree; the walk is not reaching the skills and this guard is checking nothing'
    for rel, resource in documents:
        probe = tmp_path / rel.replace('/', '_')
        probe.write_bytes(resource.read_bytes())
        mapping, body = read_frontmatter(probe)
        assert sorted(mapping) == ['description', 'name'], f'{rel} declares frontmatter keys {sorted(mapping)}; the Agent Skills spec shape GND ships is exactly `name` and `description`'
        assert mapping['name'] == rel.split('/')[0], f"{rel} declares name {mapping['name']!r} but ships in directory {rel.split('/')[0]!r}; the spec requires they match or the skill is not discovered"
        assert body.strip(), f'{rel} has an empty body'

def _routing_text(rel: str) -> str:
    root = _skills_root()
    resource = root
    for part in rel.split('/'):
        resource = resource / part
    return re.sub('\\s+', ' ', resource.read_text(encoding='utf-8').replace('*', ''))
ROUTING_MATRIX: tuple[tuple[str, str, str, str], ...] = (('gnd-model-from-text/SKILL.md', '../gnd-model-evolve/SKILL.md', 'model .{0,30}already exists', 'unchanged.{0,80}(source|provenance).{0,200}D-12'), ('gnd-model-from-text/SKILL.md', '../gnd-model-from-code/SKILL.md', '(codebase|existing code)', 'one-time.{0,300}D-14'), ('gnd-codegen/SKILL.md', '../gnd-conformance/SKILL.md', 'drift', 'separate claim'), ('gnd-codegen/SKILL.md', '../gnd-model-evolve/SKILL.md', 'model.{0,40}(is wrong|must change|changing)', '[Nn]othing regenerates automatically'), ('gnd-conformance/SKILL.md', '../gnd-model-evolve/SKILL.md', 'model.{0,40}(has to change|must change|is what)', 'not permission to regenerate'), ('gnd-conformance/SKILL.md', '../gnd-model-from-code/SKILL.md', '(brownfield|never had a model)', 'drift and brownfield recovery are different'), ('gnd-orm-core/SKILL.md', '../gnd-model-evolve/SKILL.md', 'must change', '[Rr]outing only'), ('gnd-orm-core/SKILL.md', '../gnd-model-from-code/SKILL.md', 'existing codebase', 'D-14'), ('gnd-orm-core/SKILL.md', '../gnd-review-panel/SKILL.md', '(plan|experiment outcome)', 'advisory.{0,200}D-22'))

@pytest.mark.parametrize(('source', 'destination', 'trigger', 'boundary'), ROUTING_MATRIX, ids=[f"{src.split('/')[0]}->{dst.split('/')[1]}" for src, dst, _, _ in ROUTING_MATRIX])
def test_each_phase4_route_names_its_trigger_and_its_authority_boundary(source: str, destination: str, trigger: str, boundary: str) -> None:
    text = _routing_text(source)
    assert f']({destination})' in text, f'{source} does not link to {destination}. A capability that ships in the wheel and is named by no sibling is reachable only by a reader who already knew it existed.'
    assert re.search(trigger, text, re.IGNORECASE), f'{source} links to {destination} without naming when to take the route (expected to match {trigger!r}). A destination with no trigger is a see-also, and a see-also routes nobody.'
    assert re.search(boundary, text, re.IGNORECASE), f'{source} routes to {destination} without stating the authority boundary the handoff keeps (expected to match {boundary!r}). This is the half that reads as a caveat and gets trimmed: without it the route is indistinguishable from a promise that the destination runs itself.'

def test_gnd_orm_core_indexes_the_workflows_without_becoming_one() -> None:
    text = _routing_text('gnd-orm-core/SKILL.md')
    assert 'There are no workflow steps here' in text, 'gnd-orm-core dropped its references-only declaration. The workflow index is a list of destinations; the declaration is what keeps it one.'
    assert 'references-only library' in text
    for name in sorted(EXPECTED_SKILL_NAMES - {'gnd-orm-core'}):
        assert f'](../{name}/SKILL.md)' in text, f'the gnd-orm-core workflow index does not reach {name}. A reader choosing a workflow from this page would not learn it exists.'
    raw = (_skills_root() / 'gnd-orm-core' / 'SKILL.md').read_text(encoding='utf-8')
    headings = [line.strip() for line in raw.splitlines() if line.startswith('#')]
    procedural = [heading for heading in headings if re.match('#+\\s*(workflow|instructions|step\\b|steps\\b|how to)', heading, re.IGNORECASE) and (not re.match('#+\\s*workflow index\\b', heading, re.IGNORECASE))]
    assert not procedural, f"gnd-orm-core acquired procedural heading(s) {procedural}; it is a references-only library (D-07). 'Workflow index' is a list of destinations and is allowed; '## Workflow' is a procedure and is not."

def test_no_route_promises_automatic_regeneration_or_applied_fixes() -> None:
    denials = {'gnd-model-from-code/SKILL.md': 'one-time', 'gnd-conformance/SKILL.md': 'no route above installs a watcher', 'gnd-review-panel/SKILL.md': 'never applies a fix', 'gnd-review-panel-light/SKILL.md': 'never applies a fix', 'gnd-codegen/SKILL.md': 'no payload in GND presents them as one score', 'gnd-orm-core/SKILL.md': 'stay separate payloads', 'gnd-model-from-text/SKILL.md': '[Nn]either route hands over write authority'}
    for rel, pattern in denials.items():
        assert re.search(pattern, _routing_text(rel), re.IGNORECASE), f'{rel} no longer carries its required denial (expected to match {pattern!r}). Every Phase 4 handoff is a user-selected step, and the document that omits the denial is the one whose reader assumes otherwise.'
RECORD_CONTRACT = 'gnd-orm-core/references/milestone-record-format.md'
RECORD_ROUTES = {'gnd-export/SKILL.md': 'never touches git', 'gnd-codegen/SKILL.md': 'never touches git', 'gnd-conformance/SKILL.md': 'never touches git', 'gnd-dev-session/SKILL.md': 'never touches git', 'gnd-extract/SKILL.md': 'never touches git', 'gnd-model-evolve/SKILL.md': 'never touches git', 'gnd-model-from-code/SKILL.md': 'never touches git', 'gnd-model-from-text/SKILL.md': 'never touches git', 'gnd-new-project/SKILL.md': 'never touches git', 'gnd-render-doc/SKILL.md': 'never touches git', 'gnd-review-panel/SKILL.md': 'never touches git', 'gnd-review-panel-light/SKILL.md': 'never touches git', 'gnd-solve/SKILL.md': 'commits nothing itself', 'gnd-update-review-panel/SKILL.md': 'never touches git'}

@pytest.mark.parametrize(('source', 'denial'), sorted(RECORD_ROUTES.items()), ids=[src.split('/')[0] for src, _ in sorted(RECORD_ROUTES.items())])
def test_every_workflow_skill_routes_to_the_record_contract(source: str, denial: str) -> None:
    text = _routing_text(source)
    depth = '../' * source.count('/')
    assert f']({depth}{RECORD_CONTRACT})' in text, f'{source} does not link the milestone-record contract. The record shape and commit grammar have one home (D-07); a skill that restates or omits them is how a second home appears.'
    assert re.search(denial, text), f"{source} routes to the record contract without its authority denial (expected to match {denial!r}). The record and the commit are the driving agent's acts; the document that omits the denial is the one whose reader assumes gnd performs them."

def test_the_record_contract_binds_the_agent_and_not_the_cli() -> None:
    text = _routing_text(RECORD_CONTRACT)
    assert re.search('never binds the .?gnd.? CLI', text), 'the milestone-record contract no longer states that it binds the driving agent and never the gnd CLI.'
    assert 'never touches git' in text
    assert 'append-only' in text
